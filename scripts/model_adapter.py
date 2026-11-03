#!/usr/bin/env python3
"""Call an OpenAI-compatible model API and write predicted OpenFOAM fields.

This adapter is intentionally separate from benchmark_runner.py. The runner owns
case preparation and scoring; this file owns the model/API call.
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from prompt_metadata import read_prompt_document, render_runtime_paths


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[0]


@dataclass(frozen=True)
class ModelCallResult:
    text: str
    elapsed_seconds: float
    started_at: str
    finished_at: str
    token_usage: dict | None


def resolve_path(path_text: str, base: Path = ROOT) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    base_candidate = base / path
    if base_candidate.exists() or path_text.startswith(("datasets/", "predictions/", "results/", "config/")):
        return base_candidate
    return REPO_ROOT / path


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def natural_path_key(path: Path | str) -> tuple:
    """Sort numeric time-directory names chronologically instead of lexically."""
    text = path.as_posix() if isinstance(path, Path) else str(path)
    tokens = re.split(r"(\d+(?:\.\d+)?)", text)
    return tuple(
        (0, float(token)) if re.fullmatch(r"\d+(?:\.\d+)?", token) else (1, token)
        for token in tokens
        if token
    )


def sanitize_model_alias(name: str) -> str:
    alias = name.strip().lower()
    alias = re.sub(r"[-_]?\d{6,8}$", "", alias)
    alias = re.sub(r"[^a-z0-9]+", "", alias)
    return alias or "model"


def apply_case_paths(config: dict, prompt_path: Path) -> dict:
    updated = dict(config)
    alias = updated.get("model_alias") or sanitize_model_alias(updated.get("model_name", "model"))
    updated["model_alias"] = alias
    try:
        metadata, _ = read_prompt_document(prompt_path)
        updated.update(render_runtime_paths(metadata, alias))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    return updated


def find_benchmark_case(benchmark_config: dict, case_id: str) -> dict:
    matches = [case for case in benchmark_config.get("cases", []) if case.get("id") == case_id]
    if not matches:
        raise SystemExit(f"No benchmark case matched: {case_id}")
    return matches[0]


def read_text(path: Path, max_chars: int | None = None) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if max_chars is not None and len(text) > max_chars:
        return text[:max_chars] + "\n\n[TRUNCATED]\n"
    return text


def collect_files(root: Path, max_chars_per_file: int) -> list[tuple[str, str]]:
    if not root.exists():
        return []
    files = []
    paths = [path for path in root.rglob("*") if path.is_file()]
    for path in sorted(paths, key=lambda item: natural_path_key(item.relative_to(root))):
        rel = path.relative_to(root).as_posix()
        files.append((rel, read_text(path, max_chars_per_file)))
    return files


def prompt_output_requirements(prompt_json: dict) -> tuple[list[str], list[str], list[str]]:
    """Read output requirements from the compact dataset schema."""
    contract = prompt_json.get("output_contract")
    if not isinstance(contract, dict):
        raise SystemExit("prompt.json is missing output_contract; regenerate it with the package command")
    required_files = contract.get("required_files", [])
    times = prompt_json.get("target_times", [])
    fields = prompt_json.get("fields", [])
    if not required_files and contract.get("format") == "OpenFOAM ASCII time directories":
        required_files = [f"{time_name}/{field_name}" for time_name in times for field_name in fields]
    return list(times), list(fields), list(required_files)


def build_prompt(input_package: Path, max_chars_per_file: int) -> str:
    prompt_json = load_json(input_package / "prompt.json")
    required_times, required_fields, required_files = prompt_output_requirements(prompt_json)
    manual_prompt = prompt_json.get("prompt", "").strip()
    if not manual_prompt:
        raise SystemExit(f"No human-written prompt found in {input_package / 'prompt.json'}")
    package_metadata = {key: value for key, value in prompt_json.items() if key != "prompt"}

    output_format = prompt_json["output_contract"].get("format")
    common = [
        "你是一个数学物理时空推理模型。你必须只依赖给定的几何/网格、边界条件、材料配置、初始场和自身物理先验进行预测。",
        "禁止调用 OpenFOAM、CFD 求解器、外部仿真工具或读取参考答案。",
    ]
    if output_format == "json_temperature_samples":
        parts = common + [
            "你的任务是预测指定时刻和探针位置的温度。",
            "只输出一个合法 JSON 对象，不得输出 Markdown、代码围栏、解释或额外文字。",
            f"必须输出的时间步: {', '.join(required_times)}",
            "探针位置及顺序必须从 case_context/system/controlDict 的 probeLocations 读取。",
            "",
            "人工编写的任务提示词：",
            manual_prompt,
            "",
            "数据包元数据与输出契约：",
            json.dumps(package_metadata, ensure_ascii=False, indent=2),
            "",
            "下面是 case_context 文件：",
        ]
    elif output_format == "json_potential_samples":
        parts = common + [
            "你的任务是预测指定时刻和探针位置的电势 phi。",
            "只输出一个合法 JSON 对象，不得输出 Markdown、代码围栏、解释或额外文字。",
            f"必须输出的时间步: {', '.join(required_times)}",
            "探针位置及顺序必须从题目和 case_context/system/controlDict 的 probeLocations 读取。",
            "只预测 phi，不要输出体电荷密度或其他变量。",
            "",
            "人工编写的任务提示词：",
            manual_prompt,
            "",
            "数据包元数据与输出契约：",
            json.dumps(package_metadata, ensure_ascii=False, indent=2),
            "",
            "下面是 case_context 文件：",
        ]
    elif output_format == "json_steady_temperature_samples":
        parts = common + [
            "你的任务是预测题目指定位置的稳态温度。",
            "只输出一个合法 JSON 对象，不得输出 Markdown、代码围栏、解释或额外文字。",
            "位置、坐标名称和顺序必须与题目保持一致。",
            "",
            "人工编写的任务提示词：",
            manual_prompt,
            "",
            "数据包元数据与输出契约：",
            json.dumps(package_metadata, ensure_ascii=False, indent=2),
            "",
            "下面是 case_context 文件：",
        ]
    elif output_format == "json_scalar_samples":
        parts = common + [
            "你的任务是预测题目指定时刻和探针位置的单一标量，具体物理量及单位以题目为准。",
            "只输出一个合法 JSON 对象，不得输出 Markdown、代码围栏、解释或额外文字。",
            f"必须输出的时间步: {', '.join(required_times)}",
            "探针位置及顺序以题目为准；若随附 system/functions 或 system/controlDict 定义 probeLocations，应与其保持一致。",
            "",
            "人工编写的任务提示词：",
            manual_prompt,
            "",
            "数据包元数据与输出契约：",
            json.dumps(package_metadata, ensure_ascii=False, indent=2),
            "",
            "下面是 case_context 文件：",
        ]
    elif output_format == "json_flow_samples":
        parts = common + [
            "你的任务是预测指定时刻和探针位置的二维速度与压力。",
            "只输出一个合法 JSON 对象，不得输出 Markdown、代码围栏、解释或额外文字。",
            f"必须输出的时间步: {', '.join(required_times)}",
            "探针位置及顺序必须从 case_context/system/controlDict 的 probeLocations 读取。",
            "每个 U 元素必须是 [Ux, Uy]，不得输出 z 分量。",
            "",
            "人工编写的任务提示词：",
            manual_prompt,
            "",
            "数据包元数据与输出契约：",
            json.dumps(package_metadata, ensure_ascii=False, indent=2),
            "",
            "下面是 case_context 文件：",
        ]
    elif output_format == "json_compressible_flow_samples":
        parts = common + [
            "你的任务是预测指定时刻和位置的单组分可压缩流场。",
            "只输出一个合法 JSON 对象，不得输出 Markdown、代码围栏、解释或额外文字。",
            f"必须输出的时间步: {', '.join(required_times)}",
            "每个时间行必须包含 rho、U、p、T、Ma；每个 U 元素必须为 [Ux, Uy, Uz]。",
            "位置及顺序必须与题目和输出契约保持一致。",
            "",
            "人工编写的任务提示词：",
            manual_prompt,
            "",
            "数据包元数据与输出契约：",
            json.dumps(package_metadata, ensure_ascii=False, indent=2),
            "",
            "下面是 case_context 文件：",
        ]
    elif output_format == "json_reaction_diffusion_samples":
        parts = common + [
            "你的任务是预测一维有限速率化学反应—扩散过程的温度、压力、速度和组分质量分数。",
            "只输出一个合法 JSON 对象，不得输出 Markdown、代码围栏、解释或额外文字。",
            f"必须输出的时间步: {', '.join(required_times)}",
            "每个时间行必须包含 T、p、U、Y_CH4、Y_O2、Y_CO2、Y_H2O、Y_N2。",
            "每个 U 元素必须为 [Ux, Uy, Uz]；位置及顺序必须与题目和输出契约一致。",
            "",
            "人工编写的任务提示词：",
            manual_prompt,
            "",
            "数据包元数据与输出契约：",
            json.dumps(package_metadata, ensure_ascii=False, indent=2),
            "",
            "下面是 case_context 文件：",
        ]
    elif output_format == "json_velocity_samples":
        parts = common + [
            "你的任务是预测指定时刻、指定横向位置的流向速度。",
            "只输出一个合法 JSON 对象，不得输出 Markdown、代码围栏、解释或额外文字。",
            f"必须输出的时间步: {', '.join(required_times)}",
            "横向位置及顺序必须与题目保持一致。",
            "",
            "人工编写的任务提示词：",
            manual_prompt,
            "",
            "数据包元数据与输出契约：",
            json.dumps(package_metadata, ensure_ascii=False, indent=2),
            "",
            "下面是 case_context 文件：",
        ]
    else:
        parts = common + [
            "你的任务是预测后续 OpenFOAM ASCII 字段文件。",
            "",
            "必须输出文件内容，格式严格如下。每个文件一个代码块，代码块前一行写 FILE: <time>/<field>。",
            "示例：",
            "FILE: 0.5/U",
            "```foam",
            "/* OpenFOAM field content here */",
            "```",
            "",
            f"必须输出的时间步: {', '.join(required_times)}",
            f"必须输出的字段: {', '.join(required_fields)}",
            f"必须输出的文件: {', '.join(required_files)}",
            "",
            "人工编写的任务提示词：",
            manual_prompt,
            "",
            "数据包元数据与输出契约：",
            json.dumps(package_metadata, ensure_ascii=False, indent=2),
            "",
            "下面是 case_context 文件：",
        ]

    for rel, text in collect_files(input_package / "case_context", max_chars_per_file):
        parts.extend([f"\n--- case_context/{rel} ---", text])

    parts.append("\n下面是已知输入时间步字段：")
    for rel, text in collect_files(input_package / "inputs", max_chars_per_file):
        parts.extend([f"\n--- inputs/{rel} ---", text])

    if output_format in {
        "json_temperature_samples",
        "json_potential_samples",
        "json_steady_temperature_samples",
        "json_flow_samples",
        "json_compressible_flow_samples",
        "json_reaction_diffusion_samples",
        "json_scalar_samples",
        "json_velocity_samples",
    }:
        parts.extend(["", "再次强调：只输出 JSON 对象；不要调用求解器或输出参考答案来源。"])
    else:
        parts.extend(["", "再次强调：只输出预测文件代码块；不要输出求解器调用步骤；不要输出目标时间步参考解来源。"])
    return "\n".join(parts)


def extract_response_text(parsed: dict) -> str:
    if isinstance(parsed.get("output_text"), str):
        return parsed["output_text"]

    pieces: list[str] = []
    for item in parsed.get("output", []):
        if isinstance(item, dict):
            for content in item.get("content") or []:
                if isinstance(content, dict):
                    text = content.get("text")
                    if isinstance(text, str):
                        pieces.append(text)
    if pieces:
        return "".join(pieces)

    # Some OpenAI-compatible gateways return Chat Completions-shaped JSON
    # even when the request was sent to /responses.
    for choice in parsed.get("choices", []):
        if not isinstance(choice, dict):
            continue
        message = choice.get("message", {})
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            pieces.append(message["content"])
        elif isinstance(choice.get("text"), str):
            pieces.append(choice["text"])
    if pieces:
        return "".join(pieces)
    raise SystemExit("Responses API returned no text output")


def extract_sse_response_text(body: str) -> str:
    pieces: list[str] = []
    final_text = None
    final_response = None
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if not data or data == "[DONE]":
            continue
        try:
            event = json.loads(data)
        except json.JSONDecodeError:
            continue
        event_type = event.get("type", "")
        if event_type.endswith("output_text.delta") and isinstance(event.get("delta"), str):
            pieces.append(event["delta"])
        elif isinstance(event.get("delta"), dict):
            delta = event["delta"]
            for key in ("text", "content"):
                if isinstance(delta.get(key), str):
                    pieces.append(delta[key])
                    break
        elif event_type.endswith("output_text.done") and isinstance(event.get("text"), str):
            final_text = event["text"]
        elif event_type.endswith("completed") and isinstance(event.get("response"), dict):
            final_response = event["response"]

        # Compatibility fallback for gateways that emit Chat Completions
        # chunks from a Responses endpoint.
        for choice in event.get("choices", []):
            if not isinstance(choice, dict):
                continue
            delta = choice.get("delta", {})
            if isinstance(delta, dict) and isinstance(delta.get("content"), str):
                pieces.append(delta["content"])
            message = choice.get("message", {})
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                final_text = message["content"]
    if pieces:
        return "".join(pieces)
    if final_text is not None:
        return final_text
    if final_response is not None:
        return extract_response_text(final_response)

    # A few compatible gateways ignore stream=true and return one complete
    # JSON object with application/json instead of an SSE stream.
    stripped = body.strip()
    if stripped.startswith("{"):
        try:
            return extract_response_text(json.loads(stripped))
        except json.JSONDecodeError:
            pass
    raise SystemExit("Streaming Responses API returned no text output")


def extract_chat_sse_response_text(body: str) -> str:
    pieces: list[str] = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if not data or data == "[DONE]":
            continue
        try:
            event = json.loads(data)
        except json.JSONDecodeError:
            continue
        for choice in event.get("choices", []):
            delta = choice.get("delta", {})
            content = delta.get("content")
            if isinstance(content, str):
                pieces.append(content)
            message = choice.get("message", {})
            content = message.get("content")
            if isinstance(content, str):
                pieces.append(content)
    if pieces:
        return "".join(pieces)
    raise SystemExit("Streaming chat/completions API returned no text output")


def normalize_token_usage(usage: dict | None) -> dict | None:
    """Normalize Responses and Chat Completions usage names while preserving details."""
    if not isinstance(usage, dict):
        return None
    input_tokens = usage.get("input_tokens", usage.get("prompt_tokens"))
    output_tokens = usage.get("output_tokens", usage.get("completion_tokens"))
    total_tokens = usage.get("total_tokens")
    if total_tokens is None and isinstance(input_tokens, int) and isinstance(output_tokens, int):
        total_tokens = input_tokens + output_tokens
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "provider_usage": usage,
    }


def build_api_request(config: dict, prompt: str) -> tuple[str, dict]:
    api_base = config["api_base"].rstrip("/")
    api_protocol = config.get("api_protocol", config.get("api_type", "chat_completions"))
    system_prompt = "You predict physical fields or requested samples from provided OpenFOAM context. Do not call solvers."

    if api_protocol in {"responses", "responses_api"}:
        payload = {
            "model": config["model_name"],
            "stream": config.get("stream", False),
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}],
                },
            ],
        }
        if "temperature" in config:
            payload["temperature"] = config["temperature"]
        if "max_output_tokens" in config or "max_tokens" in config:
            payload["max_output_tokens"] = config.get("max_output_tokens", config.get("max_tokens"))
        if config.get("tools"):
            payload["tools"] = config["tools"]
        if isinstance(config.get("extra_body"), dict):
            payload.update(config["extra_body"])
        return f"{api_base}/responses", payload

    payload = {
        "model": config["model_name"],
        "max_tokens": config.get("max_tokens", 16000),
        "stream": config.get("stream", False),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    }
    if config.get("temperature", 0) is not None:
        payload["temperature"] = config.get("temperature", 0)
    if config.get("stream", False) and config.get("track_usage", True):
        payload["stream_options"] = {"include_usage": True}
    if isinstance(config.get("extra_body"), dict):
        payload.update(config["extra_body"])
    return f"{api_base}/chat/completions", payload


def required_output_files(config: dict) -> set[str]:
    input_package = resolve_path(config["input_package"])
    prompt_json = load_json(input_package / "prompt.json")
    _, _, required_files = prompt_output_requirements(prompt_json)
    return set(required_files)


def predicted_files_complete(text: str, required_files: set[str]) -> bool:
    if not required_files:
        return False
    return required_files.issubset(set(extract_predicted_files(text)))


def decode_sse_data(raw_line: bytes) -> dict | None:
    line = raw_line.decode("utf-8", errors="replace").strip()
    if not line.startswith("data:"):
        return None
    data = line.removeprefix("data:").strip()
    if not data or data == "[DONE]":
        return None
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def read_streaming_response(response, config: dict, api_protocol: str) -> tuple[str, dict | None]:
    raw_parts: list[str] = []
    text_parts: list[str] = []
    usage = None
    required_files = required_output_files(config) if config.get("stop_when_files_complete", True) else set()
    track_usage = config.get("track_usage", True)

    for raw_line in response:
        decoded_line = raw_line.decode("utf-8", errors="replace")
        raw_parts.append(decoded_line)
        event = decode_sse_data(raw_line)
        if not event:
            continue

        if api_protocol in {"responses", "responses_api"}:
            event_type = event.get("type", "")
            if event_type.endswith("output_text.delta") and isinstance(event.get("delta"), str):
                text_parts.append(event["delta"])
            response_payload = event.get("response")
            if isinstance(response_payload, dict) and isinstance(response_payload.get("usage"), dict):
                usage = response_payload["usage"]
        else:
            for choice in event.get("choices", []):
                delta = choice.get("delta", {})
                content = delta.get("content")
                if isinstance(content, str):
                    text_parts.append(content)

        if isinstance(event.get("usage"), dict):
            usage = event["usage"]

        candidate_text = "".join(text_parts)
        if required_files and not track_usage and predicted_files_complete(candidate_text, required_files):
            return candidate_text, None

    body = "".join(raw_parts)
    if text_parts:
        return "".join(text_parts), usage
    if api_protocol in {"responses", "responses_api"}:
        stripped = body.strip()
        if stripped.startswith("{"):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                pass
            else:
                if isinstance(parsed.get("usage"), dict):
                    usage = parsed["usage"]
                return extract_response_text(parsed), usage
        return extract_sse_response_text(body), usage
    return extract_chat_sse_response_text(body), usage


def call_openai_compatible(config: dict, prompt: str) -> ModelCallResult:
    api_key = config.get("api_key", "")
    api_key_env = config.get("api_key_env", "OPENAI_API_KEY")
    if not api_key:
        api_key = os.environ.get(api_key_env)
    if not api_key:
        raise SystemExit(f"No API key configured. Set 'api_key' in model_config.json or environment variable {api_key_env}")

    url, payload = build_api_request(config, prompt)
    data = json.dumps(payload).encode("utf-8")
    stream = config.get("stream", False)
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream" if stream else "application/json",
            "User-Agent": "LLMbenchmark/0.3 OpenAI-compatible-client",
        },
        method="POST",
    )
    api_protocol = config.get("api_protocol", config.get("api_type", "chat_completions"))
    started_at = datetime.now(timezone.utc).isoformat()
    started_timer = time.perf_counter()
    usage = None
    try:
        if config.get("disable_proxy", False):
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            response_context = opener.open(
                request, timeout=config.get("request_timeout_seconds", 600)
            )
        else:
            response_context = urllib.request.urlopen(
                request, timeout=config.get("request_timeout_seconds", 600)
            )
        with response_context as response:
            if stream:
                response_text, usage = read_streaming_response(response, config, api_protocol)
                body = None
            else:
                body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Model API HTTP error {exc.code}: {error_body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Model API request failed: {exc}") from exc
    except http.client.RemoteDisconnected as exc:
        raise SystemExit(
            "Model API connection closed before an HTTP response was received. "
            "The configured gateway or its upstream service disconnected the request; "
            "retry later or use a different API protocol/channel."
        ) from exc
    except TimeoutError as exc:
        raise SystemExit(f"Model API request timed out: {exc}") from exc

    if not config.get("stream", False):
        parsed = json.loads(body)
        usage = parsed.get("usage")
        if api_protocol in {"responses", "responses_api"}:
            response_text = extract_response_text(parsed)
        else:
            response_text = parsed["choices"][0]["message"]["content"]

    finished_at = datetime.now(timezone.utc).isoformat()
    return ModelCallResult(
        text=response_text,
        elapsed_seconds=time.perf_counter() - started_timer,
        started_at=started_at,
        finished_at=finished_at,
        token_usage=normalize_token_usage(usage),
    )


def extract_predicted_files(response_text: str) -> dict[str, str]:
    pattern = re.compile(
        r"FILE:\s*([^\n\r]+)\s*```(?:[A-Za-z0-9_+-]+)?\s*\n(.*?)```",
        flags=re.S,
    )
    files = {}
    for match in pattern.finditer(response_text):
        rel_path = match.group(1).strip()
        content = match.group(2)
        rel_path = rel_path.replace("\\", "/").lstrip("/")
        if ".." in Path(rel_path).parts:
            continue
        files[rel_path] = content.rstrip() + "\n"
    return files


def extract_json_answer(response_text: str) -> dict:
    text = response_text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.S | re.I)
    if fenced:
        text = fenced.group(1).strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        value = None
        for match in re.finditer(r"\{", text):
            try:
                candidate, _ = decoder.raw_decode(text[match.start():])
            except json.JSONDecodeError:
                continue
            if isinstance(candidate, dict):
                value = candidate
                break
        if value is None:
            raise SystemExit("Model response does not contain a valid JSON object")
    if not isinstance(value, dict):
        raise SystemExit("Model JSON response must be an object")
    return value


def write_prediction_files(files: dict[str, str], prediction_dir: Path) -> None:
    prediction_dir.mkdir(parents=True, exist_ok=True)
    for rel_path, content in files.items():
        target = prediction_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Call a model API for one benchmark input package.")
    parser.add_argument("--model-config", default="config/model_config.json", help="Path to model config JSON.")
    parser.add_argument("--case", required=True, help="Benchmark case id used to load paths from its prompt.md.")
    parser.add_argument("--config", default="config/benchmark_config.json", help="Benchmark config JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Build prompt and print summary without calling API.")
    parser.add_argument("--max-chars-per-file", type=int, default=200000, help="Prompt truncation limit per input file.")
    args = parser.parse_args()

    config_path = resolve_path(args.model_config)
    benchmark_config_path = resolve_path(args.config)
    benchmark_config = load_json(benchmark_config_path)
    case = find_benchmark_case(benchmark_config, args.case)
    prompt_path = resolve_path(case.get("prompt_file"))
    if not prompt_path.exists():
        raise SystemExit(f"Prompt file not found: {case.get('prompt_file')}")
    config = apply_case_paths(load_json(config_path), prompt_path)
    input_package = resolve_path(config["input_package"])
    prediction_dir = resolve_path(config["prediction_dir"])
    raw_response_path = resolve_path(config["raw_response_path"])
    run_metadata_path = resolve_path(config["run_metadata_path"])

    prompt = build_prompt(input_package, args.max_chars_per_file)
    prompt_json = load_json(input_package / "prompt.json")
    output_format = prompt_json.get("output_contract", {}).get("format")
    if args.dry_run:
        print(
            json.dumps(
                {
                    "model_config": str(config_path),
                    "case": args.case,
                    "prompt_file": str(prompt_path),
                    "input_package": str(input_package),
                    "prediction_dir": str(prediction_dir),
                    "run_metadata_path": str(run_metadata_path),
                    "prompt_chars": len(prompt),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    provider = config.get("provider", "openai_compatible")
    if provider != "openai_compatible":
        raise SystemExit(f"Unsupported provider: {provider}")

    call_result = call_openai_compatible(config, prompt)
    response_text = call_result.text
    raw_response_path.parent.mkdir(parents=True, exist_ok=True)
    raw_response_path.write_text(response_text, encoding="utf-8")

    json_output_formats = {
        "json_temperature_samples",
        "json_potential_samples",
        "json_steady_temperature_samples",
        "json_flow_samples",
        "json_compressible_flow_samples",
        "json_reaction_diffusion_samples",
        "json_scalar_samples",
        "json_velocity_samples",
    }
    if output_format in json_output_formats:
        answer = extract_json_answer(response_text)
        prediction_dir.mkdir(parents=True, exist_ok=True)
        answer_path = prediction_dir / "answer.json"
        answer_path.write_text(json.dumps(answer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        files = {"answer.json": answer_path.read_text(encoding="utf-8")}
    else:
        files = extract_predicted_files(response_text)
    required_files = required_output_files(config)
    run_metadata = {
        "model_name": config.get("model_name"),
        "model_alias": config.get("model_alias"),
        "input_package": str(input_package),
        "started_at_utc": call_result.started_at,
        "finished_at_utc": call_result.finished_at,
        "generation_elapsed_seconds": call_result.elapsed_seconds,
        "token_usage": call_result.token_usage,
        "token_usage_source": "provider_api" if call_result.token_usage is not None else "unavailable",
        "required_files": sorted(required_files),
        "written_files": sorted(files),
        "all_required_files_generated": required_files.issubset(files),
    }
    run_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    run_metadata_path.write_text(json.dumps(run_metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not files:
        raise SystemExit(
            f"No predicted files found in model response. Raw response saved to {raw_response_path}. "
            "Expected blocks like: FILE: 0.5/U followed by a fenced code block."
        )
    if output_format not in json_output_formats:
        write_prediction_files(files, prediction_dir)
    print(
        json.dumps(
            {
                "raw_response_path": str(raw_response_path),
                "prediction_dir": str(prediction_dir),
                "run_metadata_path": str(run_metadata_path),
                "generation_elapsed_seconds": call_result.elapsed_seconds,
                "token_usage": call_result.token_usage,
                "written_files": sorted(files),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

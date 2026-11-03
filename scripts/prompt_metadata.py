#!/usr/bin/env python3
"""Parse case-specific runtime paths from prompt.md front matter."""

from __future__ import annotations

from pathlib import Path


PATH_KEYS = ("input_package", "prediction_dir", "raw_response_path")


def read_prompt_document(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"Prompt is missing path front matter: {path}")

    try:
        closing_index = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError(f"Prompt front matter is not closed with '---': {path}") from exc

    metadata: dict[str, str] = {}
    for line in lines[1:closing_index]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Invalid prompt front-matter line in {path}: {line}")
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")

    missing = [key for key in PATH_KEYS if not metadata.get(key)]
    if missing:
        raise ValueError(f"Prompt front matter is missing {', '.join(missing)}: {path}")

    body = "\n".join(lines[closing_index + 1 :]).strip()
    if not body:
        raise ValueError(f"Prompt body is empty: {path}")
    return metadata, body


def render_runtime_paths(metadata: dict[str, str], model_alias: str) -> dict[str, str]:
    paths = {
        key: metadata[key].replace("{model_alias}", model_alias)
        for key in PATH_KEYS
    }
    unresolved = [key for key, value in paths.items() if "{" in value or "}" in value]
    if unresolved:
        raise ValueError(f"Unresolved path placeholder in: {', '.join(unresolved)}")

    raw_response = Path(paths["raw_response_path"])
    paths["run_metadata_path"] = (raw_response.parent / "run.json").as_posix()
    paths["eval_output_path"] = (raw_response.parent / "eval.json").as_posix()
    return paths

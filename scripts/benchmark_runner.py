#!/usr/bin/env python3
"""Prepare and evaluate OpenFOAM-based fluid prediction benchmark cases.

The runner intentionally keeps a small dependency footprint so it can run in a
plain OpenFOAM checkout. It supports three practical steps:

1. list: inspect configured cases.
2. prepare: export a model-facing prompt package with initial/time-step fields.
3. evaluate: compare model-predicted OpenFOAM ASCII fields against references.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from prompt_metadata import read_prompt_document, render_runtime_paths


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[0]


METRIC_DEFINITIONS = {
    "notation": (
        "Flatten all cells and components. Let prediction=p_i, reference=r_i, "
        "error=e_i=p_i-r_i, count=N, and means=p_bar/r_bar."
    ),
    "mae": "(1/N) * sum_i |p_i-r_i|",
    "rmse": "sqrt((1/N) * sum_i (p_i-r_i)^2)",
    "max_abs": "max_i |p_i-r_i|",
    "relative_l2": "sqrt(sum_i (p_i-r_i)^2) / sqrt(sum_i r_i^2)",
    "bias": "p_bar-r_bar",
    "centered_rmse": "sqrt((1/N) * sum_i (((p_i-p_bar)-(r_i-r_bar))^2))",
    "centered_relative_l2": (
        "sqrt(sum_i (((p_i-p_bar)-(r_i-r_bar))^2)) / "
        "sqrt(sum_i (r_i-r_bar)^2)"
    ),
    "prediction_l2": "sqrt(sum_i p_i^2)",
    "reference_l2": "sqrt(sum_i r_i^2)",
    "alpha_boundedness_violation_fraction": "count_i(p_i < -1e-9 or p_i > 1+1e-9) / N",
    "alpha_liquid_volume_abs_error": "|sum_i p_i - sum_i r_i| (cell-count sum; not cell-volume weighted)",
    "alpha_liquid_volume_relative_error": "|sum_i p_i - sum_i r_i| / |sum_i r_i|",
    "alpha_interface_cell_count_error": "|count_i(1e-6 < p_i < 1-1e-6) - count_i(1e-6 < r_i < 1-1e-6)|",
    "aggregate": "Arithmetic mean across all successfully evaluated time-field pairs.",
}


@dataclass(frozen=True)
class FieldData:
    values: list[list[float]]
    components: int
    uniform: bool


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def resolve_path(path_text: str | None, base: Path = ROOT) -> Path | None:
    if not path_text:
        return None
    path = Path(path_text)
    if path.is_absolute():
        return path
    if path_text.startswith("workbench/"):
        return REPO_ROOT / path
    base_candidate = base / path
    if base_candidate.exists():
        return base_candidate
    repo_candidate = REPO_ROOT / path
    if repo_candidate.exists() or path_text.startswith(("tutorials/", "applications/", "src/")):
        return repo_candidate
    return base_candidate


def load_config(path_text: str) -> dict:
    path = resolve_path(path_text) or (ROOT / "config/benchmark_config.json")
    return load_json(path)


def parse_csv_arg(value: str | None) -> list[str] | None:
    if value is None:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


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


def apply_case_model_paths(config: dict, case: dict) -> dict:
    updated = dict(config)
    alias = updated.get("model_alias") or sanitize_model_alias(updated.get("model_name", "model"))
    updated["model_alias"] = alias
    prompt_path = resolve_path(case.get("prompt_file"))
    if not prompt_path or not prompt_path.exists():
        raise SystemExit(f"Prompt file not found: {case.get('prompt_file')}")
    try:
        metadata, _ = read_prompt_document(prompt_path)
        updated.update(render_runtime_paths(metadata, alias))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    return updated


def case_with_overrides(
    case: dict,
    fields: list[str] | None = None,
    input_times: list[str] | None = None,
    target_times: list[str] | None = None,
) -> dict:
    updated = dict(case)
    if fields is not None:
        updated["fields"] = fields
    if input_times is not None:
        updated["input_times"] = input_times
    if target_times is not None:
        updated["target_times"] = target_times
    return updated


def iter_cases(config: dict, case_id: str | None = None) -> list[dict]:
    cases = config.get("cases", [])
    if case_id is None:
        return cases
    selected = [case for case in cases if case["id"] == case_id]
    if not selected:
        raise SystemExit(f"No benchmark case matched: {case_id}")
    return selected


def case_storage_path(case: dict) -> Path:
    """Return the category-aware relative storage path for a benchmark case."""
    return Path(case.get("storage_path", case["id"]))


def numeric_time_key(path: Path) -> tuple[int, float | str]:
    try:
        return (0, float(path.name))
    except ValueError:
        return (1, path.name)


def discover_times(case_dir: Path) -> list[str]:
    if not case_dir.exists():
        return []
    times = [
        path.name
        for path in case_dir.iterdir()
        if path.is_dir() and re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", path.name)
    ]
    return [Path(t).name for t in sorted((Path(t) for t in times), key=numeric_time_key)]


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def parse_number_list(text: str) -> list[float]:
    return [float(item) for item in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", text)]


def parse_uniform(value_text: str) -> FieldData:
    nums = parse_number_list(value_text)
    if not nums:
        raise ValueError("uniform internalField has no numeric value")
    if value_text.strip().startswith("("):
        return FieldData(values=[nums], components=len(nums), uniform=True)
    return FieldData(values=[[nums[0]]], components=1, uniform=True)


def parse_nonuniform(clean_text: str) -> FieldData:
    match = re.search(
        r"internalField\s+nonuniform\s+\S+\s+(\d+)\s*\((.*?)\)\s*;",
        clean_text,
        flags=re.S,
    )
    if not match:
        raise ValueError("unsupported nonuniform internalField format")
    expected_count = int(match.group(1))
    body = match.group(2)
    vectors = re.findall(r"\(([^()]+)\)", body)
    if vectors:
        values = [parse_number_list(vector) for vector in vectors]
        components = len(values[0]) if values else 0
    else:
        scalars = parse_number_list(body)
        values = [[value] for value in scalars]
        components = 1
    if len(values) != expected_count:
        raise ValueError(f"field entry count mismatch: expected {expected_count}, got {len(values)}")
    return FieldData(values=values, components=components, uniform=False)


def read_internal_field(path: Path) -> FieldData:
    clean_text = strip_comments(path.read_text(encoding="utf-8", errors="ignore"))
    if re.search(r"format\s+binary\s*;", clean_text):
        raise ValueError(
            f"{path} is an OpenFOAM binary field. Convert reference and prediction fields to ASCII "
            "before Python evaluation, for example by writing the case with 'writeFormat ascii' "
            "or using foamFormatConvert in an OpenFOAM shell."
        )
    uniform_match = re.search(r"internalField\s+uniform\s+(\([^;]+\)|[^;]+)\s*;", clean_text, flags=re.S)
    if uniform_match:
        value_text = uniform_match.group(1).strip()
        variable_match = re.fullmatch(r"\$([A-Za-z_][A-Za-z0-9_]*)", value_text)
        if variable_match:
            declaration = re.search(
                rf"(?m)^\s*{re.escape(variable_match.group(1))}\s+(\([^;]+\)|[^;]+)\s*;",
                clean_text,
            )
            if not declaration:
                raise ValueError(f"unresolved internalField variable {value_text}")
            value_text = declaration.group(1)
        return parse_uniform(value_text)
    if "internalField" in clean_text and "nonuniform" in clean_text:
        return parse_nonuniform(clean_text)
    raise ValueError(f"could not parse internalField from {path}")


def broadcast_values(a: FieldData, b: FieldData) -> tuple[list[list[float]], list[list[float]]]:
    if a.components != b.components:
        raise ValueError(f"component mismatch: {a.components} vs {b.components}")
    if len(a.values) == len(b.values):
        return a.values, b.values
    if len(a.values) == 1:
        return a.values * len(b.values), b.values
    if len(b.values) == 1:
        return a.values, b.values * len(a.values)
    raise ValueError(f"cell count mismatch: {len(a.values)} vs {len(b.values)}")


def flatten(values: Iterable[Iterable[float]]) -> list[float]:
    return [component for row in values for component in row]


def field_metrics(prediction: FieldData, reference: FieldData, field_name: str) -> dict:
    pred_values, ref_values = broadcast_values(prediction, reference)
    pred = flatten(pred_values)
    ref = flatten(ref_values)
    diffs = [p - r for p, r in zip(pred, ref)]
    abs_diffs = [abs(v) for v in diffs]
    mse = sum(v * v for v in diffs) / len(diffs)
    ref_l2 = math.sqrt(sum(v * v for v in ref))
    pred_l2 = math.sqrt(sum(v * v for v in pred))
    pred_mean = sum(pred) / len(pred)
    ref_mean = sum(ref) / len(ref)
    centered_pred = [v - pred_mean for v in pred]
    centered_ref = [v - ref_mean for v in ref]
    centered_diffs = [p - r for p, r in zip(centered_pred, centered_ref)]
    centered_ref_l2 = math.sqrt(sum(v * v for v in centered_ref))
    result = {
        "cells": len(pred_values),
        "components": prediction.components,
        "mae": sum(abs_diffs) / len(abs_diffs),
        "rmse": math.sqrt(mse),
        "max_abs": max(abs_diffs),
        "relative_l2": math.sqrt(sum(v * v for v in diffs)) / ref_l2 if ref_l2 else None,
        "bias": pred_mean - ref_mean,
        "centered_rmse": math.sqrt(sum(v * v for v in centered_diffs) / len(centered_diffs)),
        "centered_relative_l2": math.sqrt(sum(v * v for v in centered_diffs)) / centered_ref_l2
        if centered_ref_l2
        else None,
        "prediction_l2": pred_l2,
        "reference_l2": ref_l2,
    }
    if field_name.startswith("alpha"):
        pred_scalar = [row[0] for row in pred_values]
        ref_scalar = [row[0] for row in ref_values]
        result.update(
            {
                "boundedness_violation_fraction": sum(v < -1e-9 or v > 1 + 1e-9 for v in pred_scalar)
                / len(pred_scalar),
                "liquid_volume_abs_error": abs(sum(pred_scalar) - sum(ref_scalar)),
                "liquid_volume_relative_error": abs(sum(pred_scalar) - sum(ref_scalar))
                / abs(sum(ref_scalar))
                if sum(ref_scalar)
                else None,
                "interface_cell_count_error": abs(
                    sum(1 for v in pred_scalar if 1e-6 < v < 1 - 1e-6)
                    - sum(1 for v in ref_scalar if 1e-6 < v < 1 - 1e-6)
                ),
            }
        )
    return result


def case_summary(case: dict) -> dict:
    return {
        "id": case["id"],
        "title": case["title"],
        "category": case["category"],
        "solver": case.get("solver"),
        "standard_case_path": case.get("standard_case_path"),
        "difficulty": case["difficulty"],
        "input_times": case.get("input_times", []),
        "target_times": case.get("target_times", []),
        "fields": case.get("fields", []),
        "metrics": case.get("metrics", []),
        "prompt_file": case.get("prompt_file", ""),
        "notes": case.get("notes", ""),
    }


def command_list(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    summary = {
        "benchmark_name": config["benchmark_name"],
        "version": config["version"],
        "cases": [case_summary(case) for case in iter_cases(config, args.case)],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def read_prompt_text(path_text: str | None) -> str:
    path = resolve_path(path_text)
    if not path or not path.exists():
        raise SystemExit(f"Prompt file not found: {path_text}")
    try:
        _, body = read_prompt_document(path)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    return body


def copy_case_files(case: dict, source_case: Path, output_dir: Path) -> dict:
    fallback_case = resolve_path(case.get("template_case_path"))
    fields = list(dict.fromkeys(case.get("fields", []) + case.get("model_input_fields", [])))
    input_times = case.get("input_times", [])
    copied: dict[str, list[str]] = {}
    for time_name in input_times:
        for field_name in fields:
            source = source_case / time_name / field_name
            if not source.exists() and field_name == "alpha.water":
                source = source_case / time_name / "alpha.water.orig"
            if not source.exists() and fallback_case:
                source = fallback_case / time_name / field_name
                if not source.exists() and field_name == "alpha.water":
                    source = fallback_case / time_name / "alpha.water.orig"
            if source.exists():
                target = output_dir / "inputs" / time_name / field_name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                copied.setdefault(time_name, []).append(field_name)
    return copied


def copy_if_exists(source: Path, target_root: Path, relative_path: str) -> str | None:
    source_path = source / relative_path
    if not source_path.exists():
        return None
    target_path = target_root / relative_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)
    return relative_path


def copy_tree_if_exists(source: Path, target_root: Path, relative_path: str) -> list[str]:
    source_path = source / relative_path
    if not source_path.exists() or not source_path.is_dir():
        return []
    copied = []
    for child in source_path.rglob("*"):
        if child.is_file():
            child_relative = child.relative_to(source)
            target_path = target_root / child_relative
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(child, target_path)
            copied.append(str(child_relative))
    return copied


def copy_case_context(case: dict, source_case: Path, output_dir: Path) -> list[str]:
    fallback_case = resolve_path(case.get("template_case_path"))
    context_root = output_dir / "case_context"
    context_files = [
        "system/blockMeshDict",
        "system/controlDict",
        "system/fvSchemes",
        "system/fvSchemes.orig",
        "system/fvSolution",
        "system/setFieldsDict",
        "system/functions",
        "constant/physicalProperties",
        "constant/momentumTransport",
        "constant/momentumTransport.orig",
        "constant/dynamicMeshDict",
        "constant/chemistryProperties",
        "constant/combustionProperties",
        "constant/reactions",
        "constant/thermo.compressibleGas",
        "constant/phaseProperties",
        "constant/physicalProperties.air",
        "constant/physicalProperties.water",
        "constant/g",
    ]
    context_files.extend(case.get("extra_context_files", []))

    copied: list[str] = []
    for relative_path in context_files:
        copied_path = copy_if_exists(source_case, context_root, relative_path)
        if copied_path is None and fallback_case:
            copied_path = copy_if_exists(fallback_case, context_root, relative_path)
        if copied_path:
            copied.append(copied_path)

    if case.get("include_poly_mesh", True):
        copied.extend(copy_tree_if_exists(source_case, context_root, "constant/polyMesh"))
        if fallback_case:
            copied.extend(
                path
                for path in copy_tree_if_exists(fallback_case, context_root, "constant/polyMesh")
                if path not in copied
            )
    return sorted(set(copied))


def apply_model_input_policy(case: dict, output_dir: Path) -> list[str]:
    """Redact derived values only in the generated model-facing dataset copy."""
    policy = case.get("model_input_policy")
    if not policy:
        return []
    if policy != "derive_heat_flux":
        raise SystemExit(f"Unsupported model_input_policy for {case['id']}: {policy}")

    redacted: list[str] = []
    properties_path = output_dir / "case_context" / "constant" / "physicalProperties"
    if not properties_path.exists():
        raise SystemExit(
            f"Cannot apply derive_heat_flux policy for {case['id']}: "
            "case_context/constant/physicalProperties is missing"
        )
    properties_text = properties_path.read_text(encoding="utf-8")
    properties_text, dt_count = re.subn(
        r"(?m)^[ \t]*DT[ \t]+DT[ \t]+\[[^\]\n]+\][ \t]+[^;\n]+;[ \t]*$",
        "// DT value intentionally omitted from this model-facing copy.",
        properties_text,
    )
    if dt_count != 1:
        raise SystemExit(
            f"Expected exactly one DT entry to redact for {case['id']}, found {dt_count}"
        )
    properties_path.write_text(properties_text, encoding="utf-8")
    redacted.append("case_context/constant/physicalProperties:DT")

    input_paths = sorted((output_dir / "inputs").glob("*/*"), key=natural_path_key)
    gradient_files = 0
    gradient_values = 0
    for input_path in input_paths:
        if not input_path.is_file():
            continue
        input_text = input_path.read_text(encoding="utf-8")
        input_text, count = re.subn(
            r"(?m)^([ \t]*)gradient[ \t]+uniform[ \t]+[^;\n]+;[ \t]*$",
            r"\1// gradient value intentionally omitted from this model-facing copy.",
            input_text,
        )
        if count:
            input_path.write_text(input_text, encoding="utf-8")
            gradient_files += 1
            gradient_values += count

    expected_input_files = len(case.get("input_times", [])) * len(case.get("fields", []))
    if gradient_files != expected_input_files or gradient_values < gradient_files:
        raise SystemExit(
            f"Incomplete fixedGradient redaction for {case['id']}: "
            f"redacted {gradient_values} values in {gradient_files}/{expected_input_files} input files"
        )
    redacted.append(f"inputs/*/*:gradient ({gradient_values} values)")
    return redacted


def case_from_args(raw_case: dict, args: argparse.Namespace) -> dict:
    case = case_with_overrides(
        raw_case,
        fields=parse_csv_arg(getattr(args, "fields", None)),
        input_times=parse_csv_arg(getattr(args, "input_times", None)),
        target_times=parse_csv_arg(getattr(args, "target_times", None)),
    )
    if not case.get("fields"):
        raise SystemExit(f"No fields configured for {case['id']}")
    if not case.get("input_times") and case.get("reference_type") != "analytic":
        raise SystemExit(f"No input times configured for {case['id']}")
    if not case.get("target_times") and case.get("output_format") != "json_steady_temperature_samples":
        raise SystemExit(f"No target times configured for {case['id']}")
    overlap = sorted(
        set(case.get("input_times", [])) & set(case.get("target_times", [])),
        key=lambda value: float(value),
    )
    if overlap:
        raise SystemExit(
            f"Input and target times overlap for {case['id']}; this would leak reference answers: "
            f"{', '.join(overlap)}"
        )
    return case


def dataset_files(root: Path) -> list[str]:
    if not root.exists():
        return []
    files = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()]
    return sorted(files, key=natural_path_key)


def extract_case_data(case: dict, source_case: Path, output_dir: Path) -> dict:
    if not source_case.exists() or not source_case.is_dir():
        raise SystemExit(f"OpenFOAM source case not found: {source_case}")

    # These are generated directories. Clearing them prevents stale time steps or
    # fields from a previous configuration from leaking into the model input.
    for generated_name in ("inputs", "case_context"):
        generated_path = output_dir / generated_name
        if generated_path.exists():
            shutil.rmtree(generated_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    prompt_json_path = output_dir / "prompt.json"
    if prompt_json_path.exists():
        prompt_json_path.unlink()

    copied_inputs = copy_case_files(case, source_case, output_dir)
    copied_context = copy_case_context(case, source_case, output_dir)
    model_input_redactions = apply_model_input_policy(case, output_dir)
    missing_inputs = [
        f"{time_name}/{field_name}"
        for time_name in case.get("input_times", [])
        for field_name in case.get("fields", [])
        if field_name not in copied_inputs.get(time_name, [])
    ]
    if missing_inputs:
        raise SystemExit(
            f"Missing required model input fields in {source_case}: {', '.join(missing_inputs)}"
        )
    invalid_inputs = []
    for time_name in case.get("input_times", []):
        for field_name in case.get("fields", []):
            copied_path = output_dir / "inputs" / time_name / field_name
            try:
                if field_format(copied_path) != "ascii":
                    raise ValueError("field is not OpenFOAM ASCII")
                read_internal_field(copied_path)
            except Exception as exc:  # noqa: BLE001 - report every invalid model input.
                invalid_inputs.append(f"{time_name}/{field_name}: {exc}")
    if invalid_inputs:
        raise SystemExit("Invalid model input fields: " + "; ".join(invalid_inputs))
    return {
        "case_id": case["id"],
        "source_case": str(source_case),
        "output_dir": str(output_dir),
        "input_files": dataset_files(output_dir / "inputs"),
        "context_files": copied_context,
        "model_input_redactions": model_input_redactions,
    }


def package_case_prompt(config: dict, case: dict, output_dir: Path) -> dict:
    input_files = dataset_files(output_dir / "inputs")
    expected_inputs = {
        f"{time_name}/{field_name}"
        for time_name in case.get("input_times", [])
        for field_name in case.get("fields", [])
    }
    missing_inputs = sorted(expected_inputs.difference(input_files))
    if missing_inputs:
        raise SystemExit(
            f"Dataset inputs are incomplete for {case['id']}; run extract first. "
            f"Missing: {', '.join(missing_inputs)}"
        )

    target_times = case.get("target_times", [])
    fields = case.get("fields", [])
    output_format = case.get("output_format")
    json_samples = output_format in {
        "json_temperature_samples",
        "json_potential_samples",
        "json_steady_temperature_samples",
        "json_flow_samples",
        "json_compressible_flow_samples",
        "json_reaction_diffusion_samples",
        "json_scalar_samples",
        "json_velocity_samples",
    }
    required_files = (
        ["answer.json"]
        if json_samples
        else [f"{time_name}/{field_name}" for time_name in target_times for field_name in fields]
    )
    if output_format == "json_temperature_samples":
        output_contract = {
            "format": "json_temperature_samples",
            "required_files": required_files,
            "schema": {
                "case_id": "string",
                "points": [{"x": "number", "y": "number"}],
                "temperature_by_time": [{"time": "number", "values": ["number"]}],
            },
            "rule": (
                "Read probeLocations from system/controlDict and preserve their order. "
                "Return temperatures for every configured target time."
            ),
        }
    elif output_format == "json_potential_samples":
        output_contract = {
            "format": "json_potential_samples",
            "required_files": required_files,
            "schema": {
                "case_id": "string",
                "points": [{"x": "number", "y": "number", "z": "number"}],
                "potential_by_time": [{"time": "number", "values": ["number"]}],
            },
            "rule": (
                "Read probeLocations from system/controlDict and preserve their order. "
                "Return electrostatic potential phi for every configured target time."
            ),
        }
    elif output_format == "json_steady_temperature_samples":
        output_contract = {
            "format": "json_steady_temperature_samples",
            "required_files": required_files,
            "schema": {
                "case_id": "string",
                "points": [{"x/r/y/theta": "number"}],
                "temperature": ["number"],
            },
            "rule": "Preserve the stated point order and return one temperature for every point.",
        }
    elif output_format == "json_scalar_samples":
        output_contract = {
            "format": "json_scalar_samples",
            "required_files": required_files,
            "schema": {
                "case_id": "string",
                "points": ([{"x": "number", "y": "number", "z": "number"}]
                           if case.get("require_z_coordinate") else
                           [{"x": "number", "y": "number"}]),
                "scalar_by_time": [{"time": "number", "values": ["number"]}],
            },
            "rule": (
                "Preserve probe order from the question; verify against system/functions "
                "or system/controlDict when available. Return one scalar value for each "
                "point at every configured target time."
            ),
        }
    elif output_format == "json_flow_samples":
        output_contract = {
            "format": "json_flow_samples",
            "required_files": required_files,
            "schema": {
                "case_id": "string",
                "points": [{"x": "number", "y": "number"}],
                "flow_by_time": [
                    {
                        "time": "number",
                        "U": [["Ux number", "Uy number"]],
                        "p": ["number"],
                    }
                ],
            },
            "rule": (
                "Read probeLocations from system/controlDict and preserve their order. "
                "Return [Ux, Uy] and p for every point at every configured target time."
            ),
        }
    elif output_format == "json_compressible_flow_samples":
        output_contract = {
            "format": "json_compressible_flow_samples",
            "required_files": required_files,
            "schema": {
                "case_id": "string",
                "points": [{"x": "number", "y": "number", "z": "number"}],
                "flow_by_time": [{
                    "time": "number", "rho": ["number"],
                    "U": [["Ux number", "Uy number", "Uz number"]],
                    "p": ["number"], "T": ["number"], "Ma": ["number"],
                }],
            },
            "rule": (
                "Preserve the stated point/time order and return rho, [Ux,Uy,Uz], "
                "p, T and Ma for every point at every target time."
            ),
        }
    elif output_format == "json_reaction_diffusion_samples":
        output_contract = {
            "format": "json_reaction_diffusion_samples",
            "required_files": required_files,
            "schema": {
                "case_id": "string",
                "points": [{"x": "number", "y": "number", "z": "number"}],
                "state_by_time": [{
                    "time": "number", "T": ["number"], "p": ["number"],
                    "U": [["Ux number", "Uy number", "Uz number"]],
                    "Y_CH4": ["number"], "Y_O2": ["number"],
                    "Y_CO2": ["number"], "Y_H2O": ["number"], "Y_N2": ["number"],
                }],
            },
            "rule": (
                "Preserve point/time order and return T, p, [Ux,Uy,Uz] and all five "
                "named species mass fractions for every point and target time."
            ),
        }
    elif output_format == "json_velocity_samples":
        output_contract = {
            "format": "json_velocity_samples",
            "required_files": required_files,
            "schema": {
                "case_id": "string",
                "y": ["number"],
                "u": [{"time": "number", "values": ["number"]}],
            },
            "rule": (
                "Preserve the stated y-coordinate and time order. "
                "Return streamwise velocity u at every point and time."
            ),
        }
    else:
        output_contract = {
            "format": "OpenFOAM ASCII time directories",
            "directory_layout": "<prediction_dir>/<time>/<field>",
            "required_files": required_files,
            "rule": (
                "Use the same mesh, cell ordering, field dimensions, and boundary patch structure "
                "as the provided inputs and case_context."
            ),
        }
    payload = {
        "schema_version": "1.0",
        "benchmark_name": config["benchmark_name"],
        "benchmark_version": config["version"],
        "case_id": case["id"],
        "title": case["title"],
        "prompt": read_prompt_text(case.get("prompt_file")),
        "input_times": case.get("input_times", []),
        "target_times": target_times,
        "fields": fields,
        "input_files": input_files,
        "context_files": dataset_files(output_dir / "case_context"),
        "output_contract": output_contract,
    }
    if case.get("model_input_policy"):
        payload["model_input_policy"] = case["model_input_policy"]
    write_json(output_dir / "prompt.json", payload)
    return {
        "case_id": case["id"],
        "prompt_source": str(resolve_path(case.get("prompt_file"))),
        "prompt_json": str(output_dir / "prompt.json"),
        "required_files": required_files,
    }


def command_extract(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    extracted = []
    for raw_case in iter_cases(config, args.case):
        case = case_from_args(raw_case, args)
        source_case = resolve_path(args.source_dir or case.get("reference_case_path") or case.get("standard_case_path"))
        if source_case is None:
            raise SystemExit(f"No OpenFOAM source case configured for {case['id']}")
        output_dir = resolve_path(args.output_dir) / case_storage_path(case)
        extracted.append(extract_case_data(case, source_case, output_dir))
    print(json.dumps({"extracted": extracted}, indent=2, ensure_ascii=False))


def command_package(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    packaged = []
    for raw_case in iter_cases(config, args.case):
        case = case_from_args(raw_case, args)
        output_dir = resolve_path(args.output_dir) / case_storage_path(case)
        packaged.append(package_case_prompt(config, case, output_dir))
    print(json.dumps({"packaged": packaged}, indent=2, ensure_ascii=False))


def command_prepare(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    prepared = []
    for raw_case in iter_cases(config, args.case):
        case = case_from_args(raw_case, args)
        source_text = args.source_dir or case.get("reference_case_path") or case.get("standard_case_path")
        source_case = resolve_path(source_text)
        output_dir = resolve_path(args.output_dir) / case_storage_path(case)
        if source_case is None and case.get("reference_type") == "analytic":
            output_dir.mkdir(parents=True, exist_ok=True)
            prepared.append(
                {
                    "extract": {
                        "case_id": case["id"],
                        "skipped": True,
                        "reason": "analytic case has no OpenFOAM input files",
                    },
                    "package": package_case_prompt(config, case, output_dir),
                }
            )
            continue
        if source_case is None:
            raise SystemExit(f"No OpenFOAM source case configured for {case['id']}")
        prepared.append(
            {
                "extract": extract_case_data(case, source_case, output_dir),
                "package": package_case_prompt(config, case, output_dir),
            }
        )
    print(json.dumps({"prepared": prepared}, indent=2, ensure_ascii=False))


def field_format(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return "unreadable"
    match = re.search(r"format\s+(\w+)\s*;", text)
    return match.group(1) if match else "unknown"


def check_case_data(case: dict, source_dir: Path) -> dict:
    fields = case.get("fields", [])
    times = list(dict.fromkeys(case.get("input_times", []) + case.get("target_times", [])))
    entries = []
    ok = True
    for time_name in times:
        for field_name in fields:
            path = source_dir / time_name / field_name
            if not path.exists() and field_name == "alpha.water":
                path = source_dir / time_name / "alpha.water.orig"
            entry = {"time": time_name, "field": field_name, "path": str(path), "exists": path.exists()}
            if not path.exists():
                entry["status"] = "missing"
                ok = False
            else:
                fmt = field_format(path)
                entry["format"] = fmt
                if fmt != "ascii":
                    entry["status"] = "not_ascii"
                    ok = False
                else:
                    try:
                        parsed = read_internal_field(path)
                        entry.update(
                            {
                                "status": "ok",
                                "cells": len(parsed.values),
                                "components": parsed.components,
                                "uniform": parsed.uniform,
                            }
                        )
                    except Exception as exc:  # noqa: BLE001 - report all parse failures.
                        entry["status"] = "parse_error"
                        entry["error"] = str(exc)
                        ok = False
            entries.append(entry)
    return {
        "case": case_summary(case),
        "source_dir": str(source_dir),
        "ok": ok,
        "fields": entries,
    }


def command_check(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    cases = iter_cases(config, args.case)
    if len(cases) != 1:
        raise SystemExit("--case is required for check")
    case = case_with_overrides(
        cases[0],
        fields=parse_csv_arg(args.fields),
        input_times=parse_csv_arg(args.input_times),
        target_times=parse_csv_arg(args.target_times),
    )
    source_dir = resolve_path(args.source_dir or case.get("reference_case_path") or case.get("standard_case_path"))
    if source_dir is None:
        raise SystemExit("No source directory configured; pass --source-dir")
    print(json.dumps(check_case_data(case, source_dir), indent=2, ensure_ascii=False))


def evaluate_case(case: dict, prediction_dir: Path, reference_dir: Path) -> dict:
    fields = case.get("fields", [])
    target_times = case.get("target_times") or discover_times(reference_dir)
    field_results = []
    missing = []
    for time_name in target_times:
        for field_name in fields:
            pred_path = prediction_dir / time_name / field_name
            ref_path = reference_dir / time_name / field_name
            if not ref_path.exists() and field_name == "alpha.water":
                ref_path = reference_dir / time_name / "alpha.water.orig"
            if not pred_path.exists():
                missing.append({"time": time_name, "field": field_name, "side": "prediction", "path": str(pred_path)})
                continue
            if not ref_path.exists():
                missing.append({"time": time_name, "field": field_name, "side": "reference", "path": str(ref_path)})
                continue
            try:
                metrics = field_metrics(read_internal_field(pred_path), read_internal_field(ref_path), field_name)
                field_results.append({"time": time_name, "field": field_name, "metrics": metrics})
            except Exception as exc:  # noqa: BLE001 - surface parsing/evaluation failures in JSON.
                field_results.append({"time": time_name, "field": field_name, "error": str(exc)})

    valid = [entry["metrics"] for entry in field_results if "metrics" in entry]
    aggregate = {}
    if valid:
        for key in ("mae", "rmse", "max_abs", "relative_l2", "centered_rmse", "centered_relative_l2"):
            values = [metrics[key] for metrics in valid if metrics.get(key) is not None]
            aggregate[key] = sum(values) / len(values) if values else None
    return {
        "case": case_summary(case),
        "prediction_dir": str(prediction_dir),
        "reference_dir": str(reference_dir),
        "metric_definitions": METRIC_DEFINITIONS,
        "field_results": field_results,
        "missing": missing,
        "aggregate": aggregate,
    }


def evaluate_json_temperature_samples(case: dict, prediction_dir: Path) -> dict:
    prediction_path = prediction_dir / "answer.json"
    reference_path = resolve_path(case.get("reference_answer_path"))
    errors: list[str] = []
    field_results = []

    if reference_path is None or not reference_path.exists():
        raise SystemExit(f"JSON reference answer not found: {case.get('reference_answer_path')}")
    reference = load_json(reference_path)
    if not prediction_path.exists():
        return {
            "case": case_summary(case),
            "prediction_path": str(prediction_path),
            "reference_path": str(reference_path),
            "schema_compliance": False,
            "schema_errors": ["missing answer.json"],
            "field_results": [],
            "aggregate": {},
        }

    try:
        prediction = load_json(prediction_path)
    except Exception as exc:  # noqa: BLE001
        return {
            "case": case_summary(case),
            "prediction_path": str(prediction_path),
            "reference_path": str(reference_path),
            "schema_compliance": False,
            "schema_errors": [f"invalid JSON: {exc}"],
            "field_results": [],
            "aggregate": {},
        }

    if prediction.get("case_id") != reference.get("case_id"):
        errors.append("case_id mismatch")
    pred_points = prediction.get("points")
    ref_points = reference.get("points")
    if not isinstance(pred_points, list) or len(pred_points) != len(ref_points):
        errors.append("points length mismatch")
    else:
        for index, (pred_point, ref_point) in enumerate(zip(pred_points, ref_points)):
            try:
                coordinate_keys = tuple(key for key in ("x", "y", "z", "r") if key in ref_point)
                if not coordinate_keys or any(
                    abs(float(pred_point[key]) - float(ref_point[key])) > 1e-12
                    for key in coordinate_keys
                ):
                    errors.append(f"point {index} coordinate/order mismatch")
            except (KeyError, TypeError, ValueError):
                errors.append(f"point {index} is invalid")

    pred_rows = prediction.get("temperature_by_time")
    ref_rows = reference.get("temperature_by_time")
    if not isinstance(pred_rows, list) or len(pred_rows) != len(ref_rows):
        errors.append("temperature_by_time length mismatch")
    else:
        for index, (pred_row, ref_row) in enumerate(zip(pred_rows, ref_rows)):
            try:
                pred_time = float(pred_row["time"])
                ref_time = float(ref_row["time"])
                pred_values = [float(value) for value in pred_row["values"]]
                ref_values = [float(value) for value in ref_row["values"]]
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"time row {index} is invalid: {exc}")
                continue
            if abs(pred_time - ref_time) > 1e-12:
                errors.append(f"time row {index} order/value mismatch")
                continue
            if len(pred_values) != len(ref_values):
                errors.append(f"time {ref_time:g} value count mismatch")
                continue
            if not all(math.isfinite(value) for value in pred_values):
                errors.append(f"time {ref_time:g} contains non-finite values")
                continue
            metrics = field_metrics(
                FieldData([[value] for value in pred_values], 1, False),
                FieldData([[value] for value in ref_values], 1, False),
                "T",
            )
            field_results.append({"time": ref_time, "field": "T", "metrics": metrics})

    valid = [entry["metrics"] for entry in field_results]
    aggregate = {}
    if valid:
        for key in ("mae", "rmse", "max_abs", "relative_l2", "centered_rmse", "centered_relative_l2"):
            values = [metrics[key] for metrics in valid if metrics.get(key) is not None]
            aggregate[key] = sum(values) / len(values) if values else None
    return {
        "case": case_summary(case),
        "prediction_path": str(prediction_path),
        "reference_path": str(reference_path),
        "metric_definitions": METRIC_DEFINITIONS,
        "schema_compliance": not errors,
        "schema_errors": errors,
        "field_results": field_results,
        "aggregate": aggregate,
    }


def evaluate_json_potential_samples(case: dict, prediction_dir: Path) -> dict:
    prediction_path = prediction_dir / "answer.json"
    reference_path = resolve_path(case.get("reference_answer_path"))
    errors: list[str] = []
    field_results = []

    if reference_path is None or not reference_path.exists():
        raise SystemExit(f"JSON reference answer not found: {case.get('reference_answer_path')}")
    reference = load_json(reference_path)
    if not prediction_path.exists():
        return {
            "case": case_summary(case),
            "prediction_path": str(prediction_path),
            "reference_path": str(reference_path),
            "schema_compliance": False,
            "schema_errors": ["missing answer.json"],
            "field_results": [],
            "aggregate": {},
        }

    try:
        prediction = load_json(prediction_path)
    except Exception as exc:  # noqa: BLE001
        return {
            "case": case_summary(case),
            "prediction_path": str(prediction_path),
            "reference_path": str(reference_path),
            "schema_compliance": False,
            "schema_errors": [f"invalid JSON: {exc}"],
            "field_results": [],
            "aggregate": {},
        }

    if prediction.get("case_id") != reference.get("case_id"):
        errors.append("case_id mismatch")
    pred_points = prediction.get("points")
    ref_points = reference.get("points")
    if not isinstance(pred_points, list) or len(pred_points) != len(ref_points):
        errors.append("points length mismatch")
    else:
        for index, (pred_point, ref_point) in enumerate(zip(pred_points, ref_points)):
            try:
                if any(
                    abs(float(pred_point[key]) - float(ref_point[key])) > 1e-12
                    for key in ("x", "y", "z")
                ):
                    errors.append(f"point {index} coordinate/order mismatch")
            except (KeyError, TypeError, ValueError):
                errors.append(f"point {index} is invalid")

    pred_rows = prediction.get("potential_by_time")
    ref_rows = reference.get("potential_by_time")
    if not isinstance(pred_rows, list) or len(pred_rows) != len(ref_rows):
        errors.append("potential_by_time length mismatch")
    else:
        for index, (pred_row, ref_row) in enumerate(zip(pred_rows, ref_rows)):
            try:
                pred_time = float(pred_row["time"])
                ref_time = float(ref_row["time"])
                pred_values = [float(value) for value in pred_row["values"]]
                ref_values = [float(value) for value in ref_row["values"]]
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"time row {index} is invalid: {exc}")
                continue
            if abs(pred_time - ref_time) > 1e-12:
                errors.append(f"time row {index} order/value mismatch")
                continue
            if len(pred_values) != len(ref_values):
                errors.append(f"time {ref_time:g} value count mismatch")
                continue
            if not all(math.isfinite(value) for value in pred_values):
                errors.append(f"time {ref_time:g} contains non-finite values")
                continue
            metrics = field_metrics(
                FieldData([[value] for value in pred_values], 1, False),
                FieldData([[value] for value in ref_values], 1, False),
                "phi",
            )
            field_results.append({"time": ref_time, "field": "phi", "metrics": metrics})

    valid = [entry["metrics"] for entry in field_results]
    aggregate = {}
    if valid:
        for key in ("mae", "rmse", "max_abs", "relative_l2", "centered_rmse", "centered_relative_l2"):
            values = [metrics[key] for metrics in valid if metrics.get(key) is not None]
            aggregate[key] = sum(values) / len(values) if values else None
    return {
        "case": case_summary(case),
        "prediction_path": str(prediction_path),
        "reference_path": str(reference_path),
        "metric_definitions": METRIC_DEFINITIONS,
        "schema_compliance": not errors,
        "schema_errors": errors,
        "field_results": field_results,
        "aggregate": aggregate,
    }


def evaluate_json_steady_temperature_samples(case: dict, prediction_dir: Path) -> dict:
    prediction_path = prediction_dir / "answer.json"
    reference_path = resolve_path(case.get("reference_answer_path"))
    errors: list[str] = []
    field_results = []

    if reference_path is None or not reference_path.exists():
        raise SystemExit(f"JSON reference answer not found: {case.get('reference_answer_path')}")
    reference = load_json(reference_path)
    if not prediction_path.exists():
        return {
            "case": case_summary(case),
            "prediction_path": str(prediction_path),
            "reference_path": str(reference_path),
            "schema_compliance": False,
            "schema_errors": ["missing answer.json"],
            "field_results": [],
            "aggregate": {},
        }

    try:
        prediction = load_json(prediction_path)
    except Exception as exc:  # noqa: BLE001
        return {
            "case": case_summary(case),
            "prediction_path": str(prediction_path),
            "reference_path": str(reference_path),
            "schema_compliance": False,
            "schema_errors": [f"invalid JSON: {exc}"],
            "field_results": [],
            "aggregate": {},
        }

    if prediction.get("case_id") != reference.get("case_id"):
        errors.append("case_id mismatch")
    pred_points = prediction.get("points")
    ref_points = reference.get("points")
    if not isinstance(pred_points, list) or len(pred_points) != len(ref_points):
        errors.append("points length mismatch")
    else:
        for index, (pred_point, ref_point) in enumerate(zip(pred_points, ref_points)):
            try:
                coordinate_keys = tuple(key for key in ("x", "y", "z", "r", "theta") if key in ref_point)
                if not coordinate_keys or any(
                    abs(float(pred_point[key]) - float(ref_point[key])) > 1e-12
                    for key in coordinate_keys
                ):
                    errors.append(f"point {index} coordinate/order mismatch")
            except (KeyError, TypeError, ValueError):
                errors.append(f"point {index} is invalid")

    try:
        pred_values = [float(value) for value in prediction["temperature"]]
        ref_values = [float(value) for value in reference["temperature"]]
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"temperature is invalid: {exc}")
    else:
        if len(pred_values) != len(ref_values):
            errors.append("temperature value count mismatch")
        elif not all(math.isfinite(value) for value in pred_values):
            errors.append("temperature contains non-finite values")
        else:
            metrics = field_metrics(
                FieldData([[value] for value in pred_values], 1, False),
                FieldData([[value] for value in ref_values], 1, False),
                "T",
            )
            field_results.append({"field": "T", "metrics": metrics})

    aggregate = {}
    if field_results:
        metrics = field_results[0]["metrics"]
        aggregate = {
            key: metrics.get(key)
            for key in ("mae", "rmse", "max_abs", "relative_l2", "centered_rmse", "centered_relative_l2")
        }
    return {
        "case": case_summary(case),
        "prediction_path": str(prediction_path),
        "reference_path": str(reference_path),
        "metric_definitions": METRIC_DEFINITIONS,
        "schema_compliance": not errors,
        "schema_errors": errors,
        "field_results": field_results,
        "aggregate": aggregate,
    }


def evaluate_json_scalar_samples(case: dict, prediction_dir: Path) -> dict:
    prediction_path = prediction_dir / "answer.json"
    reference_path = resolve_path(case.get("reference_answer_path"))
    scalar_field = case.get("fields", ["scalar"])[0]
    errors: list[str] = []
    field_results = []

    if reference_path is None or not reference_path.exists():
        raise SystemExit(f"JSON reference answer not found: {case.get('reference_answer_path')}")
    reference = load_json(reference_path)
    if not prediction_path.exists():
        return {
            "case": case_summary(case),
            "prediction_path": str(prediction_path),
            "reference_path": str(reference_path),
            "schema_compliance": False,
            "schema_errors": ["missing answer.json"],
            "field_results": [],
            "aggregate": {},
        }

    try:
        prediction = load_json(prediction_path)
    except Exception as exc:  # noqa: BLE001
        return {
            "case": case_summary(case),
            "prediction_path": str(prediction_path),
            "reference_path": str(reference_path),
            "schema_compliance": False,
            "schema_errors": [f"invalid JSON: {exc}"],
            "field_results": [],
            "aggregate": {},
        }

    if prediction.get("case_id") != reference.get("case_id"):
        errors.append("case_id mismatch")
    pred_points = prediction.get("points")
    ref_points = reference.get("points")
    if not isinstance(pred_points, list) or len(pred_points) != len(ref_points):
        errors.append("points length mismatch")
    else:
        for index, (pred_point, ref_point) in enumerate(zip(pred_points, ref_points)):
            try:
                keys = ("x", "y", "z") if case.get("require_z_coordinate") else ("x", "y")
                if any(abs(float(pred_point[key]) - float(ref_point[key])) > 1e-12 for key in keys):
                    errors.append(f"point {index} coordinate/order mismatch")
            except (KeyError, TypeError, ValueError):
                errors.append(f"point {index} is invalid")

    pred_rows = prediction.get("scalar_by_time")
    ref_rows = reference.get("scalar_by_time")
    if not isinstance(pred_rows, list) or len(pred_rows) != len(ref_rows):
        errors.append("scalar_by_time length mismatch")
    else:
        for index, (pred_row, ref_row) in enumerate(zip(pred_rows, ref_rows)):
            try:
                pred_time = float(pred_row["time"])
                ref_time = float(ref_row["time"])
                pred_values = [float(value) for value in pred_row["values"]]
                ref_values = [float(value) for value in ref_row["values"]]
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"time row {index} is invalid: {exc}")
                continue
            if abs(pred_time - ref_time) > 1e-12:
                errors.append(f"time row {index} order/value mismatch")
                continue
            if len(pred_values) != len(ref_values):
                errors.append(f"time {ref_time:g} value count mismatch")
                continue
            if not all(math.isfinite(value) for value in pred_values):
                errors.append(f"time {ref_time:g} contains non-finite values")
                continue
            metrics = field_metrics(
                FieldData([[value] for value in pred_values], 1, False),
                FieldData([[value] for value in ref_values], 1, False),
                scalar_field,
            )
            field_results.append({"time": ref_time, "field": scalar_field, "metrics": metrics})

    valid = [entry["metrics"] for entry in field_results]
    aggregate = {}
    if valid:
        for key in ("mae", "rmse", "max_abs", "relative_l2", "centered_rmse", "centered_relative_l2"):
            values = [metrics[key] for metrics in valid if metrics.get(key) is not None]
            aggregate[key] = sum(values) / len(values) if values else None
    return {
        "case": case_summary(case),
        "prediction_path": str(prediction_path),
        "reference_path": str(reference_path),
        "metric_definitions": METRIC_DEFINITIONS,
        "schema_compliance": not errors,
        "schema_errors": errors,
        "field_results": field_results,
        "aggregate": aggregate,
    }


def evaluate_json_flow_samples(case: dict, prediction_dir: Path) -> dict:
    prediction_path = prediction_dir / "answer.json"
    reference_path = resolve_path(case.get("reference_answer_path"))
    errors: list[str] = []
    field_results = []

    if reference_path is None or not reference_path.exists():
        raise SystemExit(f"JSON reference answer not found: {case.get('reference_answer_path')}")
    reference = load_json(reference_path)
    if not prediction_path.exists():
        return {
            "case": case_summary(case),
            "prediction_path": str(prediction_path),
            "reference_path": str(reference_path),
            "schema_compliance": False,
            "schema_errors": ["missing answer.json"],
            "field_results": [],
            "aggregate_by_field": {},
        }

    try:
        prediction = load_json(prediction_path)
    except Exception as exc:  # noqa: BLE001
        return {
            "case": case_summary(case),
            "prediction_path": str(prediction_path),
            "reference_path": str(reference_path),
            "schema_compliance": False,
            "schema_errors": [f"invalid JSON: {exc}"],
            "field_results": [],
            "aggregate_by_field": {},
        }

    if prediction.get("case_id") != reference.get("case_id"):
        errors.append("case_id mismatch")
    pred_points = prediction.get("points")
    ref_points = reference.get("points")
    if not isinstance(pred_points, list) or len(pred_points) != len(ref_points):
        errors.append("points length mismatch")
    else:
        for index, (pred_point, ref_point) in enumerate(zip(pred_points, ref_points)):
            try:
                if any(abs(float(pred_point[key]) - float(ref_point[key])) > 1e-12 for key in ("x", "y")):
                    errors.append(f"point {index} coordinate/order mismatch")
            except (KeyError, TypeError, ValueError):
                errors.append(f"point {index} is invalid")

    pred_rows = prediction.get("flow_by_time")
    ref_rows = reference.get("flow_by_time")
    if not isinstance(pred_rows, list) or len(pred_rows) != len(ref_rows):
        errors.append("flow_by_time length mismatch")
    else:
        for index, (pred_row, ref_row) in enumerate(zip(pred_rows, ref_rows)):
            try:
                pred_time = float(pred_row["time"])
                ref_time = float(ref_row["time"])
                pred_u = [[float(component) for component in value] for value in pred_row["U"]]
                ref_u = [[float(component) for component in value] for value in ref_row["U"]]
                pred_p = [float(value) for value in pred_row["p"]]
                ref_p = [float(value) for value in ref_row["p"]]
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"time row {index} is invalid: {exc}")
                continue
            if abs(pred_time - ref_time) > 1e-12:
                errors.append(f"time row {index} order/value mismatch")
                continue
            if len(pred_u) != len(ref_u) or len(pred_u) != len(ref_points):
                errors.append(f"time {ref_time:g} U value count mismatch")
                continue
            if any(len(value) != 2 for value in pred_u):
                errors.append(f"time {ref_time:g} U entries must contain [Ux, Uy]")
                continue
            if len(pred_p) != len(ref_p) or len(pred_p) != len(ref_points):
                errors.append(f"time {ref_time:g} p value count mismatch")
                continue
            if not all(math.isfinite(value) for row in pred_u for value in row) or not all(
                math.isfinite(value) for value in pred_p
            ):
                errors.append(f"time {ref_time:g} contains non-finite values")
                continue
            u_metrics = field_metrics(
                FieldData(pred_u, 2, False), FieldData(ref_u, 2, False), "U"
            )
            p_metrics = field_metrics(
                FieldData([[value] for value in pred_p], 1, False),
                FieldData([[value] for value in ref_p], 1, False),
                "p",
            )
            field_results.extend(
                [
                    {"time": ref_time, "field": "U", "metrics": u_metrics},
                    {"time": ref_time, "field": "p", "metrics": p_metrics},
                ]
            )

    aggregate_by_field = {}
    for field_name in ("U", "p"):
        valid = [
            entry["metrics"] for entry in field_results if entry["field"] == field_name
        ]
        if not valid:
            continue
        aggregate_by_field[field_name] = {}
        for key in (
            "mae",
            "rmse",
            "max_abs",
            "relative_l2",
            "centered_rmse",
            "centered_relative_l2",
        ):
            values = [metrics[key] for metrics in valid if metrics.get(key) is not None]
            aggregate_by_field[field_name][key] = (
                sum(values) / len(values) if values else None
            )

    return {
        "case": case_summary(case),
        "prediction_path": str(prediction_path),
        "reference_path": str(reference_path),
        "metric_definitions": METRIC_DEFINITIONS,
        "schema_compliance": not errors,
        "schema_errors": errors,
        "field_results": field_results,
        "aggregate_by_field": aggregate_by_field,
    }


def evaluate_json_compressible_flow_samples(case: dict, prediction_dir: Path) -> dict:
    prediction_path = prediction_dir / "answer.json"
    reference_path = resolve_path(case.get("reference_answer_path"))
    errors: list[str] = []
    field_results = []
    scalar_fields = ("rho", "p", "T", "Ma")

    if reference_path is None or not reference_path.exists():
        raise SystemExit(f"JSON reference answer not found: {case.get('reference_answer_path')}")
    reference = load_json(reference_path)
    if not prediction_path.exists():
        return {
            "case": case_summary(case), "prediction_path": str(prediction_path),
            "reference_path": str(reference_path), "schema_compliance": False,
            "schema_errors": ["missing answer.json"], "field_results": [],
            "aggregate_by_field": {},
        }
    try:
        prediction = load_json(prediction_path)
    except Exception as exc:  # noqa: BLE001
        return {
            "case": case_summary(case), "prediction_path": str(prediction_path),
            "reference_path": str(reference_path), "schema_compliance": False,
            "schema_errors": [f"invalid JSON: {exc}"], "field_results": [],
            "aggregate_by_field": {},
        }

    if prediction.get("case_id") != reference.get("case_id"):
        errors.append("case_id mismatch")
    pred_points, ref_points = prediction.get("points"), reference.get("points")
    if not isinstance(pred_points, list) or len(pred_points) != len(ref_points):
        errors.append("points length mismatch")
    else:
        for index, (pred_point, ref_point) in enumerate(zip(pred_points, ref_points)):
            try:
                if any(abs(float(pred_point[key])-float(ref_point[key])) > 1e-12 for key in ("x", "y", "z")):
                    errors.append(f"point {index} coordinate/order mismatch")
            except (KeyError, TypeError, ValueError):
                errors.append(f"point {index} is invalid")

    pred_rows, ref_rows = prediction.get("flow_by_time"), reference.get("flow_by_time")
    if not isinstance(pred_rows, list) or len(pred_rows) != len(ref_rows):
        errors.append("flow_by_time length mismatch")
    else:
        for index, (pred_row, ref_row) in enumerate(zip(pred_rows, ref_rows)):
            try:
                pred_time, ref_time = float(pred_row["time"]), float(ref_row["time"])
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"time row {index} is invalid: {exc}")
                continue
            if abs(pred_time-ref_time) > 1e-12:
                errors.append(f"time row {index} order/value mismatch")
                continue
            parsed: dict[str, list[list[float]]] = {}
            try:
                parsed["U"] = [[float(component) for component in value] for value in pred_row["U"]]
                ref_u = [[float(component) for component in value] for value in ref_row["U"]]
                for name in scalar_fields:
                    parsed[name] = [[float(value)] for value in pred_row[name]]
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"time row {index} is invalid: {exc}")
                continue
            if len(parsed["U"]) != len(ref_u) or len(parsed["U"]) != len(ref_points):
                errors.append(f"time {ref_time:g} U value count mismatch")
                continue
            if any(len(value) != 3 for value in parsed["U"]):
                errors.append(f"time {ref_time:g} U entries must contain [Ux, Uy, Uz]")
                continue
            bad = False
            for name in scalar_fields:
                if len(parsed[name]) != len(ref_row[name]) or len(parsed[name]) != len(ref_points):
                    errors.append(f"time {ref_time:g} {name} value count mismatch")
                    bad = True
            if bad or not all(math.isfinite(value) for values in parsed.values() for row in values for value in row):
                if not bad:
                    errors.append(f"time {ref_time:g} contains non-finite values")
                continue
            field_results.append({
                "time": ref_time, "field": "U",
                "metrics": field_metrics(FieldData(parsed["U"], 3, False), FieldData(ref_u, 3, False), "U"),
            })
            for name in scalar_fields:
                ref_values = [[float(value)] for value in ref_row[name]]
                field_results.append({
                    "time": ref_time, "field": name,
                    "metrics": field_metrics(FieldData(parsed[name], 1, False), FieldData(ref_values, 1, False), name),
                })

    aggregate_by_field = {}
    for field_name in ("rho", "U", "p", "T", "Ma"):
        valid = [entry["metrics"] for entry in field_results if entry["field"] == field_name]
        if not valid:
            continue
        aggregate_by_field[field_name] = {}
        for key in ("mae", "rmse", "max_abs", "relative_l2", "centered_rmse", "centered_relative_l2"):
            values = [metrics[key] for metrics in valid if metrics.get(key) is not None]
            aggregate_by_field[field_name][key] = sum(values)/len(values) if values else None
    return {
        "case": case_summary(case), "prediction_path": str(prediction_path),
        "reference_path": str(reference_path), "metric_definitions": METRIC_DEFINITIONS,
        "schema_compliance": not errors, "schema_errors": errors,
        "field_results": field_results, "aggregate_by_field": aggregate_by_field,
    }


def evaluate_json_reaction_diffusion_samples(case: dict, prediction_dir: Path) -> dict:
    prediction_path = prediction_dir / "answer.json"
    reference_path = resolve_path(case.get("reference_answer_path"))
    scalar_fields = ("T", "p", "Y_CH4", "Y_O2", "Y_CO2", "Y_H2O", "Y_N2")
    errors: list[str] = []
    field_results = []
    if reference_path is None or not reference_path.exists():
        raise SystemExit(f"JSON reference answer not found: {case.get('reference_answer_path')}")
    reference = load_json(reference_path)
    if not prediction_path.exists():
        return {
            "case": case_summary(case), "prediction_path": str(prediction_path),
            "reference_path": str(reference_path), "schema_compliance": False,
            "schema_errors": ["missing answer.json"], "field_results": [], "aggregate_by_field": {},
        }
    try:
        prediction = load_json(prediction_path)
    except Exception as exc:  # noqa: BLE001
        return {
            "case": case_summary(case), "prediction_path": str(prediction_path),
            "reference_path": str(reference_path), "schema_compliance": False,
            "schema_errors": [f"invalid JSON: {exc}"], "field_results": [], "aggregate_by_field": {},
        }
    if prediction.get("case_id") != reference.get("case_id"):
        errors.append("case_id mismatch")
    pred_points, ref_points = prediction.get("points"), reference.get("points")
    if not isinstance(pred_points, list) or len(pred_points) != len(ref_points):
        errors.append("points length mismatch")
    else:
        for index, (pred_point, ref_point) in enumerate(zip(pred_points, ref_points)):
            try:
                if any(abs(float(pred_point[key])-float(ref_point[key])) > 1e-12 for key in ("x", "y", "z")):
                    errors.append(f"point {index} coordinate/order mismatch")
            except (KeyError, TypeError, ValueError):
                errors.append(f"point {index} is invalid")
    pred_rows, ref_rows = prediction.get("state_by_time"), reference.get("state_by_time")
    if not isinstance(pred_rows, list) or len(pred_rows) != len(ref_rows):
        errors.append("state_by_time length mismatch")
    else:
        for index, (pred_row, ref_row) in enumerate(zip(pred_rows, ref_rows)):
            try:
                pred_time, ref_time = float(pred_row["time"]), float(ref_row["time"])
                pred_u = [[float(component) for component in value] for value in pred_row["U"]]
                ref_u = [[float(component) for component in value] for value in ref_row["U"]]
                pred_scalars = {name: [float(value) for value in pred_row[name]] for name in scalar_fields}
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"time row {index} is invalid: {exc}")
                continue
            if abs(pred_time-ref_time) > 1e-12:
                errors.append(f"time row {index} order/value mismatch")
                continue
            if len(pred_u) != len(ref_u) or len(pred_u) != len(ref_points):
                errors.append(f"time {ref_time:g} U value count mismatch")
                continue
            if any(len(value) != 3 for value in pred_u):
                errors.append(f"time {ref_time:g} U entries must contain [Ux, Uy, Uz]")
                continue
            invalid = False
            for name in scalar_fields:
                if len(pred_scalars[name]) != len(ref_row[name]) or len(pred_scalars[name]) != len(ref_points):
                    errors.append(f"time {ref_time:g} {name} value count mismatch")
                    invalid = True
            finite = all(math.isfinite(value) for row in pred_u for value in row)
            finite = finite and all(math.isfinite(value) for values in pred_scalars.values() for value in values)
            if invalid or not finite:
                if not invalid:
                    errors.append(f"time {ref_time:g} contains non-finite values")
                continue
            field_results.append({
                "time": ref_time, "field": "U",
                "metrics": field_metrics(FieldData(pred_u, 3, False), FieldData(ref_u, 3, False), "U"),
            })
            for name in scalar_fields:
                field_results.append({
                    "time": ref_time, "field": name,
                    "metrics": field_metrics(
                        FieldData([[value] for value in pred_scalars[name]], 1, False),
                        FieldData([[float(value)] for value in ref_row[name]], 1, False), name,
                    ),
                })
    aggregate_by_field = {}
    for field_name in ("T", "p", "U", "Y_CH4", "Y_O2", "Y_CO2", "Y_H2O", "Y_N2"):
        valid = [entry["metrics"] for entry in field_results if entry["field"] == field_name]
        if not valid:
            continue
        aggregate_by_field[field_name] = {}
        for key in ("mae", "rmse", "max_abs", "relative_l2", "centered_rmse", "centered_relative_l2"):
            values = [metrics[key] for metrics in valid if metrics.get(key) is not None]
            aggregate_by_field[field_name][key] = sum(values)/len(values) if values else None
    return {
        "case": case_summary(case), "prediction_path": str(prediction_path),
        "reference_path": str(reference_path), "metric_definitions": METRIC_DEFINITIONS,
        "schema_compliance": not errors, "schema_errors": errors,
        "field_results": field_results, "aggregate_by_field": aggregate_by_field,
    }


def evaluate_json_velocity_samples(case: dict, prediction_dir: Path) -> dict:
    prediction_path = prediction_dir / "answer.json"
    reference_path = resolve_path(case.get("reference_answer_path"))
    errors: list[str] = []
    field_results = []

    if reference_path is None or not reference_path.exists():
        raise SystemExit(f"JSON reference answer not found: {case.get('reference_answer_path')}")
    reference = load_json(reference_path)
    if not prediction_path.exists():
        return {
            "case": case_summary(case),
            "prediction_path": str(prediction_path),
            "reference_path": str(reference_path),
            "schema_compliance": False,
            "schema_errors": ["missing answer.json"],
            "field_results": [],
            "aggregate": {},
        }

    try:
        prediction = load_json(prediction_path)
    except Exception as exc:  # noqa: BLE001
        return {
            "case": case_summary(case),
            "prediction_path": str(prediction_path),
            "reference_path": str(reference_path),
            "schema_compliance": False,
            "schema_errors": [f"invalid JSON: {exc}"],
            "field_results": [],
            "aggregate": {},
        }

    if prediction.get("case_id") != reference.get("case_id"):
        errors.append("case_id mismatch")
    try:
        pred_y = [float(value) for value in prediction["y"]]
        ref_y = [float(value) for value in reference["y"]]
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"y coordinates are invalid: {exc}")
        pred_y, ref_y = [], []
    if len(pred_y) != len(ref_y):
        errors.append("y coordinate count mismatch")
    elif any(abs(pred - ref) > 1e-12 for pred, ref in zip(pred_y, ref_y)):
        errors.append("y coordinate/order mismatch")

    pred_rows = prediction.get("u")
    ref_rows = reference.get("u")
    if not isinstance(pred_rows, list) or len(pred_rows) != len(ref_rows):
        errors.append("u row count mismatch")
    else:
        for index, (pred_row, ref_row) in enumerate(zip(pred_rows, ref_rows)):
            try:
                pred_time = float(pred_row["time"])
                ref_time = float(ref_row["time"])
                pred_values = [float(value) for value in pred_row["values"]]
                ref_values = [float(value) for value in ref_row["values"]]
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"time row {index} is invalid: {exc}")
                continue
            if abs(pred_time - ref_time) > 1e-12:
                errors.append(f"time row {index} order/value mismatch")
                continue
            if len(pred_values) != len(ref_values) or len(pred_values) != len(ref_y):
                errors.append(f"time {ref_time:g} velocity count mismatch")
                continue
            if not all(math.isfinite(value) for value in pred_values):
                errors.append(f"time {ref_time:g} contains non-finite values")
                continue
            metrics = field_metrics(
                FieldData([[value] for value in pred_values], 1, False),
                FieldData([[value] for value in ref_values], 1, False),
                "u",
            )
            field_results.append({"time": ref_time, "field": "u", "metrics": metrics})

    valid = [entry["metrics"] for entry in field_results]
    aggregate = {}
    if valid:
        for key in ("mae", "rmse", "max_abs", "relative_l2", "centered_rmse", "centered_relative_l2"):
            values = [metrics[key] for metrics in valid if metrics.get(key) is not None]
            aggregate[key] = sum(values) / len(values) if values else None
    return {
        "case": case_summary(case),
        "prediction_path": str(prediction_path),
        "reference_path": str(reference_path),
        "metric_definitions": METRIC_DEFINITIONS,
        "schema_compliance": not errors,
        "schema_errors": errors,
        "field_results": field_results,
        "aggregate": aggregate,
    }


def command_evaluate(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    cases = iter_cases(config, args.case)
    if len(cases) != 1:
        raise SystemExit("--case is required for evaluate")
    case = case_with_overrides(
        cases[0],
        fields=parse_csv_arg(args.fields),
        target_times=parse_csv_arg(args.target_times),
    )
    model_config = {}
    if args.model_config:
        model_config_path = resolve_path(args.model_config)
        if model_config_path is None:
            raise SystemExit(f"Model config not found: {args.model_config}")
        model_config = apply_case_model_paths(load_json(model_config_path), case)
    prediction_dir_text = args.prediction_dir or model_config.get("prediction_dir")
    prediction_dir = resolve_path(prediction_dir_text)
    if prediction_dir is None:
        raise SystemExit("--prediction-dir is required unless --model-config is provided")
    if case.get("output_format") == "json_temperature_samples":
        result = evaluate_json_temperature_samples(case, prediction_dir)
    elif case.get("output_format") == "json_potential_samples":
        result = evaluate_json_potential_samples(case, prediction_dir)
    elif case.get("output_format") == "json_steady_temperature_samples":
        result = evaluate_json_steady_temperature_samples(case, prediction_dir)
    elif case.get("output_format") == "json_scalar_samples":
        result = evaluate_json_scalar_samples(case, prediction_dir)
    elif case.get("output_format") == "json_flow_samples":
        result = evaluate_json_flow_samples(case, prediction_dir)
    elif case.get("output_format") == "json_compressible_flow_samples":
        result = evaluate_json_compressible_flow_samples(case, prediction_dir)
    elif case.get("output_format") == "json_reaction_diffusion_samples":
        result = evaluate_json_reaction_diffusion_samples(case, prediction_dir)
    elif case.get("output_format") == "json_velocity_samples":
        result = evaluate_json_velocity_samples(case, prediction_dir)
    else:
        reference_dir = resolve_path(args.reference_dir or case.get("reference_case_path") or case.get("standard_case_path"))
        if reference_dir is None:
            raise SystemExit("No reference directory configured; pass --reference-dir")
        result = evaluate_case(case, prediction_dir, reference_dir)
    if model_config:
        result["model"] = {
            "config": str(resolve_path(args.model_config)),
            "model_name": model_config.get("model_name"),
            "model_alias": model_config.get("model_alias"),
        }
        run_metadata_path = resolve_path(model_config.get("run_metadata_path"))
        if run_metadata_path and run_metadata_path.exists():
            result["generation"] = load_json(run_metadata_path)
    output_text = args.output or model_config.get("eval_output_path")
    if output_text:
        write_json(resolve_path(output_text), result)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fluid prediction benchmark workbench.")
    parser.add_argument("--config", default="config/benchmark_config.json", help="Path to benchmark config JSON.")
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List benchmark case metadata.")
    list_parser.add_argument("--case", default=None, help="Optional case id.")
    list_parser.set_defaults(func=command_list)

    extract_parser = subparsers.add_parser("extract", help="Extract model-visible inputs from an OpenFOAM case.")
    extract_parser.add_argument("--case", required=True, help="Case id.")
    extract_parser.add_argument("--source-dir", default=None, help="Override source OpenFOAM case directory.")
    extract_parser.add_argument("--input-times", default=None, help="Comma-separated input times, e.g. 0,0.1,0.2.")
    extract_parser.add_argument("--fields", default=None, help="Comma-separated fields, e.g. U,p,T.")
    extract_parser.add_argument("--output-dir", default="datasets", help="Generated dataset root directory.")
    extract_parser.set_defaults(func=command_extract)

    package_parser = subparsers.add_parser("package", help="Convert the human prompt into datasets/<case>/prompt.json.")
    package_parser.add_argument("--case", required=True, help="Case id.")
    package_parser.add_argument("--input-times", default=None, help="Comma-separated input times, e.g. 0,0.1,0.2.")
    package_parser.add_argument("--target-times", default=None, help="Comma-separated prediction times, e.g. 0.3,0.4.")
    package_parser.add_argument("--fields", default=None, help="Comma-separated fields, e.g. U,p,T.")
    package_parser.add_argument("--output-dir", default="datasets", help="Generated dataset root directory.")
    package_parser.set_defaults(func=command_package)

    prepare_parser = subparsers.add_parser("prepare", help="Run extract and package in one command.")
    prepare_parser.add_argument("--case", required=True, help="Case id.")
    prepare_parser.add_argument("--source-dir", default=None, help="Override source OpenFOAM case directory.")
    prepare_parser.add_argument("--input-times", default=None, help="Comma-separated input times, e.g. 0,0.1,0.2.")
    prepare_parser.add_argument("--target-times", default=None, help="Comma-separated target times, e.g. 0.5,0.6.")
    prepare_parser.add_argument("--fields", default=None, help="Comma-separated fields, e.g. U,p,T.")
    prepare_parser.add_argument("--output-dir", default="datasets", help="Output directory for prompt packages.")
    prepare_parser.set_defaults(func=command_prepare)

    check_parser = subparsers.add_parser("check", help="Check that benchmark fields exist and are ASCII-parseable.")
    check_parser.add_argument("--case", required=True, help="Case id.")
    check_parser.add_argument("--source-dir", default=None, help="Override source OpenFOAM case directory.")
    check_parser.add_argument("--input-times", default=None, help="Comma-separated input times, e.g. 0,0.1,0.2.")
    check_parser.add_argument("--target-times", default=None, help="Comma-separated target times, e.g. 0.5,0.6.")
    check_parser.add_argument("--fields", default=None, help="Comma-separated fields, e.g. U,p,T.")
    check_parser.set_defaults(func=command_check)

    eval_parser = subparsers.add_parser("evaluate", help="Evaluate predicted OpenFOAM fields.")
    eval_parser.add_argument("--case", required=True, help="Case id.")
    eval_parser.add_argument("--model-config", default=None, help="Model config JSON; derives prediction/output paths automatically.")
    eval_parser.add_argument("--prediction-dir", default=None, help="Directory containing predicted time folders.")
    eval_parser.add_argument("--reference-dir", default=None, help="Override reference OpenFOAM case directory.")
    eval_parser.add_argument("--target-times", default=None, help="Comma-separated target times, e.g. 0.5,0.6.")
    eval_parser.add_argument("--fields", default=None, help="Comma-separated fields, e.g. U,p,T.")
    eval_parser.add_argument("--output", default=None, help="Optional JSON output path.")
    eval_parser.set_defaults(func=command_evaluate)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command is None:
        args.command = "list"
        args.case = getattr(args, "case", None)
        command_list(args)
        return
    args.func(args)


if __name__ == "__main__":
    main()

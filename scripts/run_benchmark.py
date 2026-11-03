#!/usr/bin/env python3
"""Run one benchmark case end-to-end with one command.

Pipeline:
1. prepare model-facing input package
2. call the configured model
3. evaluate predicted OpenFOAM fields
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def add_optional(cmd: list[str], flag: str, value: str | None) -> None:
    if value:
        cmd.extend([flag, value])


def run_step(name: str, cmd: list[str]) -> None:
    print(flush=True)
    print(f"=== {name} ===", flush=True)
    print(" ".join(cmd), flush=True)
    completed = subprocess.run(cmd, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise SystemExit(f"{name} failed with exit code {completed.returncode}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run prepare -> model prediction -> evaluate for one benchmark case.")
    parser.add_argument("--case", default="heat_conduction_1", help="Benchmark case id.")
    parser.add_argument("--model-config", required=True, help="Model config JSON, e.g. config/models/deepseekv4flash.json.")
    parser.add_argument("--config", default="config/benchmark_config.json", help="Benchmark config JSON.")
    parser.add_argument("--source-dir", default=None, help="Override source/reference case for prepare.")
    parser.add_argument("--reference-dir", default=None, help="Override reference case for evaluate.")
    parser.add_argument("--input-times", default=None, help="Comma-separated input times for prepare.")
    parser.add_argument("--target-times", default=None, help="Comma-separated target times for prepare/evaluate.")
    parser.add_argument("--fields", default=None, help="Comma-separated field names for prepare/evaluate.")
    parser.add_argument("--output-dir", default="datasets", help="Prepare output root directory.")
    parser.add_argument("--max-chars-per-file", type=int, default=200000, help="Prompt truncation limit per input file.")
    parser.add_argument("--skip-prepare", action="store_true", help="Do not regenerate datasets/<case> before calling the model.")
    parser.add_argument("--skip-model", action="store_true", help="Do not call the model; only run prepare/evaluate as requested.")
    parser.add_argument("--skip-evaluate", action="store_true", help="Do not evaluate after model prediction.")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if not args.skip_prepare:
        prepare_cmd = [
            PYTHON,
            "scripts/benchmark_runner.py",
            "--config",
            args.config,
            "prepare",
            "--case",
            args.case,
            "--output-dir",
            args.output_dir,
        ]
        add_optional(prepare_cmd, "--source-dir", args.source_dir)
        add_optional(prepare_cmd, "--input-times", args.input_times)
        add_optional(prepare_cmd, "--target-times", args.target_times)
        add_optional(prepare_cmd, "--fields", args.fields)
        run_step("prepare input package", prepare_cmd)

    if not args.skip_model:
        model_cmd = [
            PYTHON,
            "scripts/model_adapter.py",
            "--model-config",
            args.model_config,
            "--case",
            args.case,
            "--config",
            args.config,
            "--max-chars-per-file",
            str(args.max_chars_per_file),
        ]
        run_step("call model", model_cmd)

    if not args.skip_evaluate:
        eval_cmd = [
            PYTHON,
            "scripts/benchmark_runner.py",
            "--config",
            args.config,
            "evaluate",
            "--case",
            args.case,
            "--model-config",
            args.model_config,
        ]
        add_optional(eval_cmd, "--reference-dir", args.reference_dir)
        add_optional(eval_cmd, "--target-times", args.target_times)
        add_optional(eval_cmd, "--fields", args.fields)
        run_step("evaluate prediction", eval_cmd)


if __name__ == "__main__":
    main()

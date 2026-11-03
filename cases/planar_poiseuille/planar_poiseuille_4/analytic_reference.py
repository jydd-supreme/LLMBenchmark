#!/usr/bin/env python3
"""Analytical reference evaluator for the five plane-Poiseuille questions."""

from __future__ import annotations

import argparse
import json
import math


NU = 0.1
A_FORWARD = 0.2
H = 1.0
PLUG_SPEED = 0.8


def steady_forward(y: float) -> float:
    return 1.0 - y * y


def odd_modes(y: float, t: float, coefficient) -> float:
    total = 0.0
    # Exponential damping makes 400 terms excessive for the requested t>0,
    # but it is useful for very early plug-flow snapshots.
    for n in range(400):
        odd = 2 * n + 1
        k = odd * math.pi / 2.0
        total += coefficient(n, odd) * math.cos(k * y) * math.exp(-NU * k * k * t)
    return total


def velocity(case_id: int, y: float, t: float) -> float:
    case_id = {20: 1, 21: 2, 22: 3, 23: 4, 24: 5}.get(case_id, case_id)
    if not -H <= y <= H:
        raise ValueError("y must lie in [-1, 1]")
    if t <= 0:
        raise ValueError("series evaluator requires t > 0")

    us = steady_forward(y)

    if case_id == 1:
        return us + odd_modes(
            y,
            t,
            lambda n, odd: -32.0 * ((-1.0) ** n) / (math.pi**3 * odd**3),
        )
    if case_id == 2:
        return us + 0.30 * math.cos(math.pi * y / 2.0) * math.exp(
            -(math.pi**2) * t / 40.0
        )
    if case_id == 3:
        return us + 0.40 * math.sin(math.pi * y) * math.exp(
            -(math.pi**2) * t / 10.0
        )
    if case_id == 4:
        return us + odd_modes(
            y,
            t,
            lambda n, odd: ((-1.0) ** n)
            * (3.2 / (math.pi * odd) - 32.0 / (math.pi**3 * odd**3)),
        )
    if case_id == 5:
        return -us + odd_modes(
            y,
            t,
            lambda n, odd: 64.0 * ((-1.0) ** n) / (math.pi**3 * odd**3),
        )
    raise ValueError("case_id must be one of 1, 2, 3, 4, 5")


def parse_floats(value: str) -> list[float]:
    return [float(item) for item in value.split(",")]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=int, required=True, choices=range(20, 25))
    parser.add_argument("--times", type=parse_floats, required=True)
    parser.add_argument(
        "--y",
        type=parse_floats,
        default=parse_floats("-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1"),
    )
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    args = parser.parse_args()

    rows = [
        {
            "time": t,
            "values": [velocity(args.case, y, t) for y in args.y],
        }
        for t in args.times
    ]
    if args.format == "json":
        result = {"case_id": "planar_poiseuille_4", "y": args.y, "u": rows}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("case,t,y,u")
        for row in rows:
            for y, u in zip(args.y, row["values"]):
                print(f"{args.case},{row['time']:.10g},{y:.10g},{u:.12g}")


if __name__ == "__main__":
    main()

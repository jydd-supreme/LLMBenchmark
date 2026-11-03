#!/usr/bin/env python3
"""Closed-form references for heat-conduction cases 25--34."""

import argparse
import json
import math


def line_points(key, values):
    return [{key: value} for value in values]


def solve(case):
    case_id = "heat_conduction_59"

    if case == 25:
        ri, ro, ti, to = 0.02, 0.08, 500.0, 300.0
        rs = [0.02, 0.025, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
        temperature = [ti + (to-ti)*math.log(r/ri)/math.log(ro/ri) for r in rs]
        return {"case_id": case_id, "points": line_points("r", rs), "temperature": temperature}

    if case == 26:
        ri, ro, ti, to = 0.03, 0.12, 600.0, 300.0
        rs = [0.03, 0.04, 0.05, 0.06, 0.075, 0.09, 0.105, 0.12]
        temperature = [to + (ti-to)*(1/r-1/ro)/(1/ri-1/ro) for r in rs]
        return {"case_id": case_id, "points": line_points("r", rs), "temperature": temperature}

    if case == 27:
        ri, ro, q, k, to = 0.02, 0.08, 50000.0, 20.0, 300.0
        rs = [0.02, 0.025, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
        temperature = [to + q*ri/k*math.log(ro/r) for r in rs]
        return {"case_id": case_id, "points": line_points("r", rs), "temperature": temperature}

    if case == 28:
        radius, qv, k, ts = 0.05, 2.0e6, 15.0, 300.0
        rs = [0.0, 0.005, 0.01, 0.02, 0.03, 0.04, 0.045, 0.05]
        temperature = [ts + qv*(radius**2-r**2)/(4*k) for r in rs]
        return {"case_id": case_id, "points": line_points("r", rs), "temperature": temperature}

    if case == 29:
        radius, qv, k, ts = 0.04, 1.5e6, 10.0, 310.0
        rs = [0.0, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04]
        temperature = [ts + qv*(radius**2-r**2)/(6*k) for r in rs]
        return {"case_id": case_id, "points": line_points("r", rs), "temperature": temperature}

    if case == 30:
        l1, l2, k1, k2, tl, tr = 0.03, 0.07, 10.0, 2.0, 500.0, 300.0
        heat_flux = (tl-tr)/(l1/k1+l2/k2)
        xs = [0.0, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10]
        temperature = [
            tl-heat_flux*x/k1 if x <= l1 else tl-heat_flux*l1/k1-heat_flux*(x-l1)/k2
            for x in xs
        ]
        return {"case_id": case_id, "points": line_points("x", xs), "temperature": temperature}

    if case == 31:
        ri, rm, ro, k1, k2, ti, to = 0.02, 0.04, 0.10, 15.0, 3.0, 500.0, 300.0
        c = (ti-to)/(math.log(rm/ri)/k1 + math.log(ro/rm)/k2)
        rs = [0.02, 0.025, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10]
        temperature = [
            ti-c*math.log(r/ri)/k1 if r <= rm else to+c*math.log(ro/r)/k2
            for r in rs
        ]
        return {"case_id": case_id, "points": line_points("r", rs), "temperature": temperature}

    if case == 32:
        points = [
            {"x": x, "y": y}
            for y in [0.1, 0.25, 0.4]
            for x in [0.1, 0.25, 0.5, 0.75, 0.9]
        ]
        temperature = [
            300.0 + 100.0*math.sin(math.pi*p["x"])*math.sinh(math.pi*p["y"])/math.sinh(math.pi*0.5)
            for p in points
        ]
        return {"case_id": case_id, "points": points, "temperature": temperature}

    if case == 33:
        thetas = [0.0, math.pi/6, math.pi/3, math.pi/2]
        points = [{"r": r, "theta": theta} for r in [0.0, 0.025, 0.05, 0.075, 0.1] for theta in thetas]
        temperature = [300.0 + 80.0*(p["r"]/0.1)**3*math.cos(3*p["theta"]) for p in points]
        return {"case_id": case_id, "points": points, "temperature": temperature}

    if case == 34:
        points = [
            {"x": x, "y": y}
            for y in [0.1, 0.2, 0.3, 0.4]
            for x in [0.25, 0.5, 0.75]
        ]
        decay_rate = 0.01*(math.pi**2 + (4*math.pi)**2)
        rows = []
        for t in [0.1, 0.5, 1.0, 2.0]:
            values = [
                300.0 + 100.0*math.sin(math.pi*p["x"])*math.sin(4*math.pi*p["y"])*math.exp(-decay_rate*t)
                for p in points
            ]
            rows.append({"time": t, "values": values})
        return {"case_id": case_id, "points": points, "temperature_by_time": rows}

    raise ValueError("case must be in 25..34")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=int, required=True, choices=range(25, 35))
    args = parser.parse_args()
    print(json.dumps(solve(args.case), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

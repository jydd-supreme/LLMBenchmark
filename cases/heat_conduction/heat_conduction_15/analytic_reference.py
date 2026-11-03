#!/usr/bin/env python3
"""Closed-form reference generator for one-dimensional heat cases 0--19."""

import argparse
import json
import math


DIRICHLET = {
    0: (573.0, 273.0, 273.0, 0.050, [0.3, 0.4, 0.5, 0.6]),
    1: (423.0, 283.0, 283.0, 0.020, [0.6, 0.7, 0.8, 0.9, 1.0]),
    2: (673.0, 293.0, 293.0, 0.035, [0.6, 0.7, 0.8, 0.9, 1.0]),
    3: (523.0, 303.0, 303.0, 0.075, [0.6, 0.7, 0.8, 0.9, 1.0]),
    4: (723.0, 313.0, 313.0, 0.100, [0.6, 0.7, 0.8, 0.9, 1.0]),
    5: (423.0, 423.0, 283.0, 0.020, [0.6, 0.7, 0.8, 0.9, 1.0]),
    6: (473.0, 473.0, 293.0, 0.035, [0.6, 0.7, 0.8, 0.9, 1.0]),
    7: (523.0, 523.0, 303.0, 0.050, [0.6, 0.7, 0.8, 0.9, 1.0]),
    8: (623.0, 623.0, 313.0, 0.075, [0.6, 0.7, 0.8, 0.9, 1.0]),
    9: (723.0, 723.0, 323.0, 0.100, [0.6, 0.7, 0.8, 0.9, 1.0]),
}

INTERNAL_SOURCE = {
    10: (0.25, 423.0, 283.0, 0.020),
    11: (0.35, 473.0, 293.0, 0.035),
    12: (0.45, 523.0, 303.0, 0.050),
    13: (0.60, 623.0, 313.0, 0.075),
    14: (0.75, 723.0, 323.0, 0.100),
}

FLUX = {
    15: (293.15, 2700.0, 900.0, 205.0, 200000.0, 0.0),
    16: (303.15, 8960.0, 385.0, 401.0, 0.0, 350000.0),
    17: (313.15, 2330.0, 700.0, 148.0, 500000.0, 0.0),
    18: (293.15, 2700.0, 900.0, 205.0, 150000.0, 250000.0),
    19: (303.15, 8960.0, 385.0, 401.0, 300000.0, 180000.0),
}


def case_id(number):
    return "heat_conduction_15"


def dirichlet_temperature(x, t, tl, tr, t0, alpha, terms=500):
    steady = tl + (tr-tl)*x
    transient = 0.0
    for n in range(1, terms+1):
        sign = (-1.0)**n
        coefficient = 2.0/(n*math.pi)*(
            (t0-tl)*(1.0-sign) + (tr-tl)*sign
        )
        transient += coefficient*math.sin(n*math.pi*x)*math.exp(-alpha*(n*math.pi)**2*t)
    return steady + transient


def segment_temperature(s, length, t, cold, hot, alpha, hot_at_right, terms=500):
    delta = hot-cold
    if hot_at_right:
        steady = cold + delta*s/length
        transient = sum(
            2*delta*((-1.0)**n)/(n*math.pi)
            * math.sin(n*math.pi*s/length)
            * math.exp(-alpha*(n*math.pi/length)**2*t)
            for n in range(1, terms+1)
        )
    else:
        steady = hot - delta*s/length
        transient = sum(
            -2*delta/(n*math.pi)
            * math.sin(n*math.pi*s/length)
            * math.exp(-alpha*(n*math.pi/length)**2*t)
            for n in range(1, terms+1)
        )
    return steady + transient


def internal_source_temperature(x, t, source_x, hot, cold, alpha):
    if abs(x-source_x) < 1e-14:
        return hot
    if x < source_x:
        return segment_temperature(x, source_x, t, cold, hot, alpha, True)
    return segment_temperature(x-source_x, 1-source_x, t, cold, hot, alpha, False)


def flux_temperature(x, t, t0, rho, cp, k, q_left, q_right, terms=500):
    length = 0.02
    alpha = k/(rho*cp)
    g_left, g_right = q_left/k, q_right/k
    g_total = g_left+g_right
    spatial = (
        g_total*x*x/(2*length) - g_left*x
        + length*(2*g_left-g_right)/6
    )
    transient = sum(
        -2*length*(g_left+((-1.0)**n)*g_right)/(n*n*math.pi**2)
        * math.cos(n*math.pi*x/length)
        * math.exp(-alpha*(n*math.pi/length)**2*t)
        for n in range(1, terms+1)
    )
    return t0 + alpha*g_total*t/length + spatial + transient


def solve(number):
    if number in DIRICHLET:
        tl, tr, t0, alpha, times = DIRICHLET[number]
        xs = [i/10 for i in range(11)]
        rows = [
            {"time": t, "values": [dirichlet_temperature(x,t,tl,tr,t0,alpha) for x in xs]}
            for t in times
        ]
    elif number in INTERNAL_SOURCE:
        source_x, hot, cold, alpha = INTERNAL_SOURCE[number]
        xs = sorted(set([i/10 for i in range(11)] + [source_x]))
        times = [0.6, 0.7, 0.8, 0.9, 1.0]
        rows = [
            {"time": t, "values": [internal_source_temperature(x,t,source_x,hot,cold,alpha) for x in xs]}
            for t in times
        ]
    elif number in FLUX:
        args = FLUX[number]
        xs = [0.002*i for i in range(11)]
        times = [0.6, 0.7, 0.8, 0.9, 1.0]
        rows = [
            {"time": t, "values": [flux_temperature(x,t,*args) for x in xs]}
            for t in times
        ]
    else:
        raise ValueError("case must be in 0..19")
    return {
        "case_id": case_id(number),
        "points": [{"x": x} for x in xs],
        "temperature_by_time": rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=int, required=True, choices=range(20))
    args = parser.parse_args()
    print(json.dumps(solve(args.case), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

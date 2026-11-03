#!/usr/bin/env python3
"""Analytic reference for problem 47."""
import json
import math

SPEC = json.loads('{"A": 140.0, "R": 0.05, "Tb": 300.0, "alpha": 8.436213991769547e-05, "category": "一维传热/球体径向模态", "cp": 900.0, "family": "sphere_sinc", "k": 205.0, "material": "aluminium", "number": 47, "rho": 2700.0, "times": [2, 8, 20, 50, 100]}')

def j0(value):
    total = term = 1.0
    for index in range(1, 80):
        term *= -(value * value / 4.0) / (index * index)
        total += term
        if abs(term) < 1.0e-16:
            break
    return total

def temp(x, time):
    s = SPEC
    a = s["alpha"]
    f = s["family"]
    if f == "fixed_equal_sine":
        lam = math.pi/s["L"]
        return s["Tb"] + s["A"]*math.sin(lam*x)*math.exp(-a*lam*lam*time)
    if f == "fixed_unequal_sine":
        lam = math.pi/s["L"]
        steady = s["Tl"] + (s["Tr"]-s["Tl"])*x/s["L"]
        return steady + s["A"]*math.sin(lam*x)*math.exp(-a*lam*lam*time)
    if f == "insulated_cosine":
        lam = math.pi/s["L"]
        return s["Tm"] + s["A"]*math.cos(lam*x)*math.exp(-a*lam*lam*time)
    if f == "mixed_half_sine":
        lam = math.pi/(2*s["L"])
        return s["Tb"] + s["A"]*math.sin(lam*x)*math.exp(-a*lam*lam*time)
    if f == "uniform_source":
        beta = s["qvol"]/(s["rho"]*s["cp"])
        steady = s["Tb"] + s["qvol"]*x*(s["L"]-x)/(2*s["k"])
        transient = 0.0
        for n in range(1, 600, 2):
            lam = n*math.pi/s["L"]
            coefficient = -4*beta*s["L"]**2/(a*math.pi**3*n**3)
            transient += coefficient*math.sin(lam*x)*math.exp(-a*lam*lam*time)
        return steady + transient
    if f == "sinusoidal_source":
        lam = math.pi/s["L"]
        return s["Tb"] + s["qvol"]/(s["k"]*lam*lam)*math.sin(lam*x)*(1-math.exp(-a*lam*lam*time))
    if f == "semi_infinite_step":
        return s["T0"] + (s["Ts"]-s["T0"])*math.erfc(x/(2*math.sqrt(a*time)))
    if f == "infinite_gaussian":
        variance = s["sigma"]**2 + 2*a*time
        return s["T0"] + s["A"]*s["sigma"]/math.sqrt(variance)*math.exp(-x*x/(2*variance))
    if f == "cylinder_bessel":
        lam = 2.404825557695773/s["R"]
        return s["Tb"] + s["A"]*j0(lam*x)*math.exp(-a*lam*lam*time)
    if f == "sphere_sinc":
        lam = math.pi/s["R"]
        shape = 1.0 if abs(x) < 1e-15 else math.sin(lam*x)/(lam*x)
        return s["Tb"] + s["A"]*shape*math.exp(-a*lam*lam*time)
    raise ValueError(f)

def positions():
    if "L" in SPEC:
        return [SPEC["L"]*i/10 for i in range(11)]
    if "depth" in SPEC:
        return [SPEC["depth"]*i/10 for i in range(11)]
    if "half_width" in SPEC:
        return [-SPEC["half_width"] + 2*SPEC["half_width"]*i/12 for i in range(13)]
    return [SPEC["R"]*i/10 for i in range(11)]

xs = positions()
result = {
    "case_id": "heat_conduction_48",
    "points": [{"x": x} for x in xs],
    "temperature_by_time": [
        {"time": t, "values": [temp(x, t) for x in xs]}
        for t in SPEC["times"]
    ],
}
print(json.dumps(result, ensure_ascii=False, indent=2))

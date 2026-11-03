#!/usr/bin/env python3
"""Analytic reference for planar Poiseuille problem 36."""
import json
import math

S = json.loads('{"accel": 0.5, "amplitude": 0.45, "category": "平面Poiseuille流/对称初始扰动", "family": "symmetric_mode", "h": 0.015, "mu": 0.072, "nu": 7.5e-05, "number": 36, "rho": 960.0, "times": [0.06, 0.15, 0.3, 0.75, 1.5, 3.0]}')

def series(y, time, amplitude):
    total = 0.0
    for index in range(400):
        odd = 2*index + 1
        wave = odd*math.pi/(2*S["h"])
        coefficient = 32*amplitude*((-1.0)**index)/(math.pi**3*odd**3)
        total += coefficient*math.cos(wave*y)*math.exp(-S["nu"]*wave*wave*time)
    return total

def profile(y, maximum):
    return maximum*(1-(y/S["h"])**2)

def velocity(y, time):
    f = S["family"]
    h, nu = S["h"], S["nu"]
    if f == "startup":
        maximum = S["accel"]*h*h/(2*nu)
        return profile(y, maximum)-series(y,time,maximum)
    if f == "decay":
        maximum = S["initial_accel"]*h*h/(2*nu)
        return series(y,time,maximum)
    if f == "reversal":
        old = S["initial_accel"]*h*h/(2*nu)
        reverse = S["reverse_accel"]*h*h/(2*nu)
        return profile(y,-reverse)+series(y,time,old+reverse)
    maximum = S["accel"]*h*h/(2*nu)
    if f == "symmetric_mode":
        wave = math.pi/(2*h)
        return profile(y,maximum)+S["amplitude"]*math.cos(wave*y)*math.exp(-nu*wave*wave*time)
    wave = math.pi/h
    return profile(y,maximum)+S["amplitude"]*math.sin(wave*y)*math.exp(-nu*wave*wave*time)

ys = [S["h"]*value for value in [-0.9,-0.7,-0.5,-0.3,-0.1,0,0.1,0.3,0.5,0.7,0.9]]
result = {
    "case_id": "planar_poiseuille_17",
    "y": ys,
    "u": [{"time":t,"values":[velocity(y,t) for y in ys]} for t in S["times"]],
}
print(json.dumps(result, ensure_ascii=False, indent=2))

#!/usr/bin/env python3
"""Analytic reference for planar Poiseuille problem 28."""
import json
import math

S = json.loads('{"category": "平面Poiseuille流/撤去压降衰减", "family": "decay", "h": 0.02, "initial_accel": 1.2, "mu": 0.13799999999999998, "nu": 0.00015, "number": 28, "rho": 920.0, "times": [0.0533333333, 0.1333333333, 0.2666666667, 0.6666666667, 1.3333333333, 2.6666666667]}')

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
    "case_id": "planar_poiseuille_9",
    "y": ys,
    "u": [{"time":t,"values":[velocity(y,t) for y in ys]} for t in S["times"]],
}
print(json.dumps(result, ensure_ascii=False, indent=2))

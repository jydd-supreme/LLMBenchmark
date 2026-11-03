---
input_package: datasets/compressible_flow/compressible_flow_16
prediction_dir: predictions/compressible_flow/compressible_flow_16/{model_alias}
raw_response_path: results/compressible_flow/compressible_flow_16/{model_alias}/response.txt
---

# 问题 16

考虑单组分、无化学反应的可压缩理想气体，仅考虑由所给OpenFOAM配置确定的质量、动量和总能量演化。

一只圆锥形固体沿管轴方向运动，周围气体起初静止。锥体运动挤压前方气体，在锥尖附近形成快速变化的压缩区；靠近锥体与远离锥体的探针受扰动的时间不同。

圆锥和远端随动边界沿x方向以 `150.0 m/s` 运动，初始气体静止；初始压力 `80000.0 Pa`、温度 `280.0 K`。

材料模型、几何、网格、全部初始条件与边界条件以随题提供的OpenFOAM文件为准。请预测下列固定空间位置在指定时刻的密度、速度、压力、温度和马赫数：

```text
points = [{"x":-0.007200000000000001,"y":0.0015,"z":0},{"x":-0.006500000000000001,"y":0.0012,"z":0},{"x":-0.0055,"y":0.0015,"z":0},{"x":-0.0045000000000000005,"y":0.0018000000000000002,"z":0},{"x":-0.003,"y":0.0022,"z":0},{"x":-0.002,"y":0.0022,"z":0},{"x":-0.001,"y":0.0022,"z":0},{"x":-0.006,"y":0.0023,"z":0}]
times = [5e-06,1e-05,1.5e-05,2e-05] s
```

只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。点和时间顺序必须与题目一致，每个数值至少保留8位有效数字：

```json
{"case_id":"compressible_flow_16","points":[{"x":0,"y":0,"z":0}],"flow_by_time":[{"time":5e-06,"rho":[0],"U":[[0,0,0]],"p":[0],"T":[0],"Ma":[0]}]}
```

必须输出全部位置与全部时刻。不得调用OpenFOAM、CFD求解器或读取标准答案。

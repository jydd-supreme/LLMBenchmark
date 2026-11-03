---
input_package: datasets/compressible_flow/compressible_flow_10
prediction_dir: predictions/compressible_flow/compressible_flow_10/{model_alias}
raw_response_path: results/compressible_flow/compressible_flow_10/{model_alias}/response.txt
---

# 问题 10

考虑单组分、无化学反应的可压缩理想气体，仅考虑由所给OpenFOAM配置确定的质量、动量和总能量演化。

超声速气流沿通道前进时遇到使流向发生偏折的斜壁。气流在转角附近受到压缩，斜向波系将上游和下游状态分开；同一 x 位置的上下探针可能位于波系的不同一侧。

归一化理想气体来流马赫数为 `3.5`，流动转折角为 `12.0 deg`。

材料模型、几何、网格、全部初始条件与边界条件以随题提供的OpenFOAM文件为准。请预测下列固定空间位置在指定时刻的密度、速度、压力、温度和马赫数：

```text
points = [{"x":0.4,"y":0.2,"z":0.05},{"x":0.4,"y":0.8,"z":0.05},{"x":1.0,"y":0.2,"z":0.05},{"x":1.0,"y":0.5,"z":0.05},{"x":1.0,"y":0.8,"z":0.05},{"x":2.0,"y":0.2,"z":0.05},{"x":2.0,"y":0.5,"z":0.05},{"x":2.0,"y":0.8,"z":0.05},{"x":3.0,"y":0.2,"z":0.05},{"x":3.0,"y":0.5,"z":0.05},{"x":3.0,"y":0.8,"z":0.05}]
times = [1,2,3,5,10] s
```

只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。点和时间顺序必须与题目一致，每个数值至少保留8位有效数字：

```json
{"case_id":"compressible_flow_10","points":[{"x":0,"y":0,"z":0}],"flow_by_time":[{"time":1,"rho":[0],"U":[[0,0,0]],"p":[0],"T":[0],"Ma":[0]}]}
```

必须输出全部位置与全部时刻。不得调用OpenFOAM、CFD求解器或读取标准答案。

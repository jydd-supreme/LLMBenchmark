---
input_package: datasets/compressible_flow/compressible_flow_15
prediction_dir: predictions/compressible_flow/compressible_flow_15/{model_alias}
raw_response_path: results/compressible_flow/compressible_flow_15/{model_alias}/response.txt
---

# 问题 15

考虑单组分、无化学反应的可压缩理想气体，仅考虑由所给OpenFOAM配置确定的质量、动量和总能量演化。

高速气体从入口进入具有倾斜壁面的进气扩压通道，流道截面沿程改变。壁面转折可能引起压缩波和激波，壁温还会影响近壁气体；沿程及不同壁面距离的探针用于区分这些区域。

入口速度 `900.0 m/s`，扩压板角度 `12.0 deg`，壁温 `320.0 K`，采用k-omega SST。

材料模型、几何、网格、全部初始条件与边界条件以随题提供的OpenFOAM文件为准。请预测下列固定空间位置在指定时刻的密度、速度、压力、温度和马赫数：

```text
points = [{"x":0.01,"y":0,"z":0.002},{"x":0.01,"y":0,"z":0.055},{"x":0.05,"y":0,"z":0.002},{"x":0.05,"y":0,"z":0.055},{"x":0.12,"y":0,"z":0.002},{"x":0.12,"y":0,"z":0.045},{"x":0.2,"y":0,"z":0.002},{"x":0.2,"y":0,"z":0.04},{"x":0.3,"y":0,"z":0.002},{"x":0.3,"y":0,"z":0.03},{"x":0.42,"y":0,"z":0.002},{"x":0.42,"y":0,"z":0.025}]
times = [0.0002,0.0004,0.0006,0.0008] s
```

只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。点和时间顺序必须与题目一致，每个数值至少保留8位有效数字：

```json
{"case_id":"compressible_flow_15","points":[{"x":0,"y":0,"z":0}],"flow_by_time":[{"time":0.0002,"rho":[0],"U":[[0,0,0]],"p":[0],"T":[0],"Ma":[0]}]}
```

必须输出全部位置与全部时刻。不得调用OpenFOAM、CFD求解器或读取标准答案。

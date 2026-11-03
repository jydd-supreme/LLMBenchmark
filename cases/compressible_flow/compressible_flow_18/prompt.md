---
input_package: datasets/compressible_flow/compressible_flow_18
prediction_dir: predictions/compressible_flow/compressible_flow_18/{model_alias}
raw_response_path: results/compressible_flow/compressible_flow_18/{model_alias}/response.txt
---

# 问题 18

考虑单组分、无化学反应的可压缩理想气体，仅考虑由所给OpenFOAM配置确定的质量、动量和总能量演化。

高压气体从小出口喷入压力较低的周围区域，形成向下游扩展的高速射流。射流与环境气体之间存在速度和压力差，膨胀与再压缩结构沿轴向发展；轴线上和偏离轴线的探针看到的状态可能不同。

射流入口压力 `220000.0 Pa`、温度 `260.0 K`、速度 `270.0 m/s`。

材料模型、几何、网格、全部初始条件与边界条件以随题提供的OpenFOAM文件为准。请预测下列固定空间位置在指定时刻的密度、速度、压力、温度和马赫数：

```text
points = [{"x":0.002,"y":0.001,"z":0},{"x":0.005,"y":0.001,"z":0},{"x":0.01,"y":0.001,"z":0},{"x":0.015,"y":0.001,"z":0},{"x":0.02,"y":0.001,"z":0},{"x":0.025,"y":0.001,"z":0},{"x":0.005,"y":0.004,"z":0},{"x":0.01,"y":0.004,"z":0},{"x":0.015,"y":0.004,"z":0},{"x":0.02,"y":0.004,"z":0},{"x":0.025,"y":0.004,"z":0},{"x":0.01,"y":0.008,"z":0},{"x":0.02,"y":0.008,"z":0}]
times = [5e-06,1e-05,1.5e-05,2e-05] s
```

只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。点和时间顺序必须与题目一致，每个数值至少保留8位有效数字：

```json
{"case_id":"compressible_flow_18","points":[{"x":0,"y":0,"z":0}],"flow_by_time":[{"time":5e-06,"rho":[0],"U":[[0,0,0]],"p":[0],"T":[0],"Ma":[0]}]}
```

必须输出全部位置与全部时刻。不得调用OpenFOAM、CFD求解器或读取标准答案。

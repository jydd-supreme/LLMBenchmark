---
input_package: datasets/compressible_flow/compressible_flow_3
prediction_dir: predictions/compressible_flow/compressible_flow_3/{model_alias}
raw_response_path: results/compressible_flow/compressible_flow_3/{model_alias}/response.txt
---

# 问题 3

考虑单组分、无化学反应的可压缩理想气体，仅考虑由所给OpenFOAM配置确定的质量、动量和总能量演化。

想象一根沿 x 方向的长直管，隔膜起初把左侧高压高温气体与右侧低压气体分开，两边起初都静止。隔膜在初始时刻移除后，高压侧向右膨胀，向右传播的压缩波、向左传播的稀疏波及中间的接触区使密度、速度、压强和温度出现不同的空间变化。

左右初态分别为 `(p,T,Ux)=(90000,320,80)` 和 `(12000,260,0)`，间断位置 `x=-0.5 m`；`mu=1.2e-05 Pa s`，`Pr=0.9`。

材料模型、几何、网格、全部初始条件与边界条件以随题提供的OpenFOAM文件为准。请预测下列固定空间位置在指定时刻的密度、速度、压力、温度和马赫数：

```text
points = [{"x":-3,"y":0,"z":0},{"x":-2,"y":0,"z":0},{"x":-1,"y":0,"z":0},{"x":-0.5,"y":0,"z":0},{"x":0,"y":0,"z":0},{"x":0.5,"y":0,"z":0},{"x":1,"y":0,"z":0},{"x":2,"y":0,"z":0},{"x":3,"y":0,"z":0}]
times = [0.001,0.003,0.005,0.007] s
```

只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。点和时间顺序必须与题目一致，每个数值至少保留8位有效数字：

```json
{"case_id":"compressible_flow_3","points":[{"x":0,"y":0,"z":0}],"flow_by_time":[{"time":0.001,"rho":[0],"U":[[0,0,0]],"p":[0],"T":[0],"Ma":[0]}]}
```

必须输出全部位置与全部时刻。不得调用OpenFOAM、CFD求解器或读取标准答案。

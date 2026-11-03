---
input_package: datasets/compressible_flow/compressible_flow_7
prediction_dir: predictions/compressible_flow/compressible_flow_7/{model_alias}
raw_response_path: results/compressible_flow/compressible_flow_7/{model_alias}/response.txt
---

# 问题 7

考虑单组分、无化学反应的可压缩理想气体，仅考虑由所给OpenFOAM配置确定的质量、动量和总能量演化。

超声速气流从左侧进入二维通道，下壁突然抬高形成一个朝向来流的台阶。气流被台阶迫使转向，台阶前后可能出现压缩波、激波与反射；贴近下壁和通道上部的探针会经历不同的变化。

归一化理想气体来流马赫数为 `3.5`，台阶高度为 `0.15 m`。

材料模型、几何、网格、全部初始条件与边界条件以随题提供的OpenFOAM文件为准。请预测下列固定空间位置在指定时刻的密度、速度、压力、温度和马赫数：

```text
points = [{"x":0.2,"y":0.1,"z":0},{"x":0.2,"y":0.5,"z":0},{"x":0.55,"y":0.1,"z":0},{"x":0.55,"y":0.7,"z":0},{"x":0.75,"y":0.35,"z":0},{"x":0.75,"y":0.7,"z":0},{"x":1.2,"y":0.35,"z":0},{"x":1.2,"y":0.7,"z":0},{"x":1.8,"y":0.35,"z":0},{"x":1.8,"y":0.7,"z":0},{"x":2.6,"y":0.35,"z":0},{"x":2.6,"y":0.7,"z":0}]
times = [0.2,0.4,0.6,0.8,1.0] s
```

只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。点和时间顺序必须与题目一致，每个数值至少保留8位有效数字：

```json
{"case_id":"compressible_flow_7","points":[{"x":0,"y":0,"z":0}],"flow_by_time":[{"time":0.2,"rho":[0],"U":[[0,0,0]],"p":[0],"T":[0],"Ma":[0]}]}
```

必须输出全部位置与全部时刻。不得调用OpenFOAM、CFD求解器或读取标准答案。

---
input_package: datasets/compressible_flow/compressible_flow_12
prediction_dir: predictions/compressible_flow/compressible_flow_12/{model_alias}
raw_response_path: results/compressible_flow/compressible_flow_12/{model_alias}/response.txt
---

# 问题 12

考虑单组分、无化学反应的可压缩理想气体，仅考虑由所给OpenFOAM配置确定的质量、动量和总能量演化。

超声速来流遇到伸入通道的楔形固体，必须绕开楔面。楔尖附近的压缩扰动向外传播，局部流速、压强和温度会随到楔面的距离而异；探针分布在楔前及楔后不同高度。

归一化理想气体来流马赫数为 `6.0`，楔角为 `20.0 deg`。

材料模型、几何、网格、全部初始条件与边界条件以随题提供的OpenFOAM文件为准。请预测下列固定空间位置在指定时刻的密度、速度、压力、温度和马赫数：

```text
points = [{"x":-0.1,"y":0.03,"z":0},{"x":-0.05,"y":0.1,"z":0},{"x":0.03,"y":0.03,"z":0},{"x":0.03,"y":0.1,"z":0},{"x":0.1,"y":0.06,"z":0},{"x":0.1,"y":0.12,"z":0},{"x":0.2,"y":0.1,"z":0},{"x":0.2,"y":0.13,"z":0},{"x":0.28,"y":0.125,"z":0},{"x":0.28,"y":0.145,"z":0}]
times = [0.04,0.08,0.12,0.16,0.2] s
```

只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。点和时间顺序必须与题目一致，每个数值至少保留8位有效数字：

```json
{"case_id":"compressible_flow_12","points":[{"x":0,"y":0,"z":0}],"flow_by_time":[{"time":0.04,"rho":[0],"U":[[0,0,0]],"p":[0],"T":[0],"Ma":[0]}]}
```

必须输出全部位置与全部时刻。不得调用OpenFOAM、CFD求解器或读取标准答案。

---
input_package: datasets/heat_conduction/heat_conduction_22
prediction_dir: predictions/heat_conduction/heat_conduction_22/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_22/{model_alias}/response.txt
---

# 问题 22

杆两端贴着温度相同的恒温环境，内部起初有一处平滑的高温隆起。热量从内部向两端传出，温度峰值逐渐降低；两端始终被固定在环境温度。

考虑常物性的均质固体，仅考虑一维瞬态热传导。物性参数为：

- `rho=7800 kg/m3`；
- `Cp=500 J/(kg K)`；
- `k=45 W/(m K)`；
- 热扩散率由上述物性确定；
- 长度：`L=0.08 m`；

- 初始温度：`T(x,0)=290+160 sin(pi x/L) K`；
- 两端从 `t=0` 起均保持 `290 K`。

忽略辐射、相变和接触热阻；除题目明确给出的体积热源外，不存在其他内热源。请根据相应的一维热传导模型计算：

```text
x = [0,0.008,0.016,0.024,0.032,0.04,0.048,0.056,0.064,0.072,0.08] m
t = [5,20,60,150,300] s
```

对于径向问题，输出中的 `x` 表示径向坐标 `r`。只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。每个温度至少保留8位有效数字，点和时间顺序必须与题目一致：

```json
{"case_id":"heat_conduction_22","points":[{"x":0}],"temperature_by_time":[{"time":5,"values":[0]}]}
```

示例不完整；必须输出全部位置和全部时刻。不得调用外部数值求解器或读取标准答案。

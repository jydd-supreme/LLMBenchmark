---
input_package: datasets/heat_conduction/heat_conduction_39
prediction_dir: predictions/heat_conduction/heat_conduction_39/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_39/{model_alias}/response.txt
---

# 问题 39

这是一块向内部延伸得足够远的固体，初态处处等温。从指定时刻起，表面突然被固定为更高温度；热影响从表面向内部逐渐渗透，足够远处在观测时间内仍接近初温。

考虑常物性的均质固体，仅考虑一维瞬态热传导。物性参数为：

- `rho=2700 kg/m3`；
- `Cp=900 J/(kg K)`；
- `k=205 W/(m K)`；
- 热扩散率由上述物性确定；


- `x>=0` 的半无限固体初始温度均匀为 `300 K`；
- 从 `t=0+` 起表面 `x=0` 突然保持为 `500 K`；
- 当 `x` 趋于无穷远时温度保持 `300 K`。

忽略辐射、相变和接触热阻；除题目明确给出的体积热源外，不存在其他内热源。请根据相应的一维热传导模型计算：

```text
x = [0,0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1] m
t = [10,30,60,120,300] s
```

对于径向问题，输出中的 `x` 表示径向坐标 `r`。只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。每个温度至少保留8位有效数字，点和时间顺序必须与题目一致：

```json
{"case_id":"heat_conduction_39","points":[{"x":0}],"temperature_by_time":[{"time":10,"values":[0]}]}
```

示例不完整；必须输出全部位置和全部时刻。不得调用外部数值求解器或读取标准答案。

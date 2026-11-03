---
input_package: datasets/heat_conduction/heat_conduction_42
prediction_dir: predictions/heat_conduction/heat_conduction_42/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_42/{model_alias}/response.txt
---

# 问题 42

把固体看成向左右无限延伸的一维介质，初始温度在原点附近呈局部高峰，远离原点则趋于同一背景温度。没有边界持续供热；热峰随时间降低并向两侧展宽。

考虑常物性的均质固体，仅考虑一维瞬态热传导。物性参数为：

- `rho=2700 kg/m3`；
- `Cp=900 J/(kg K)`；
- `k=205 W/(m K)`；
- 热扩散率由上述物性确定；


- 固体在 `-infinity<x<infinity` 上无限延伸；
- 初始温度：`T(x,0)=300+180 exp(-x^2/(2*0.012^2)) K`；
- 无边界热输入，远处温度趋于 `300 K`。

忽略辐射、相变和接触热阻；除题目明确给出的体积热源外，不存在其他内热源。请根据相应的一维热传导模型计算：

```text
x = [-0.06,-0.05,-0.04,-0.03,-0.02,-0.01,0,0.01,0.02,0.03,0.04,0.05,0.06] m
t = [2,8,20,50,100] s
```

对于径向问题，输出中的 `x` 表示径向坐标 `r`。只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。每个温度至少保留8位有效数字，点和时间顺序必须与题目一致：

```json
{"case_id":"heat_conduction_42","points":[{"x":0}],"temperature_by_time":[{"time":2,"values":[0]}]}
```

示例不完整；必须输出全部位置和全部时刻。不得调用外部数值求解器或读取标准答案。

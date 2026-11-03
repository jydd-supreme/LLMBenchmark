---
input_package: datasets/heat_conduction/heat_conduction_47
prediction_dir: predictions/heat_conduction/heat_conduction_47/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_47/{model_alias}/response.txt
---

# 问题 47

考察一根足够长的实心圆柱的横截面：沿轴向没有温度变化，只有中心到外表面的径向传热。中心附近初始较热，外圆周维持较低的恒温；温度分布随时间从外向内调整。

考虑常物性的均质固体，仅考虑一维瞬态热传导。物性参数为：

- `rho=8960 kg/m3`；
- `Cp=385 J/(kg K)`；
- `k=401 W/(m K)`；
- 热扩散率由上述物性确定；
- 外半径：`R=0.07 m`；

- 无限长实心圆柱仅发生径向导热，径向坐标记为 `x=r`；
- 初始温度：`T(r,0)=315+110 J0(2.4048255577 r/R) K`，`J0` 为第一类零阶Bessel函数；
- 中心满足径向对称条件，外表面 `r=R` 保持 `315 K`。

忽略辐射、相变和接触热阻；除题目明确给出的体积热源外，不存在其他内热源。请根据相应的一维热传导模型计算：

```text
x = [0,0.007,0.014,0.021,0.028,0.035,0.042,0.049,0.056,0.063,0.07] m
t = [2,10,30,80,160] s
```

对于径向问题，输出中的 `x` 表示径向坐标 `r`。只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。每个温度至少保留8位有效数字，点和时间顺序必须与题目一致：

```json
{"case_id":"heat_conduction_47","points":[{"x":0}],"temperature_by_time":[{"time":2,"values":[0]}]}
```

示例不完整；必须输出全部位置和全部时刻。不得调用外部数值求解器或读取标准答案。

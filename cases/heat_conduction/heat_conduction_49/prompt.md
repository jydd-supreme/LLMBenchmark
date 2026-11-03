---
input_package: datasets/heat_conduction/heat_conduction_49
prediction_dir: predictions/heat_conduction/heat_conduction_49/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_49/{model_alias}/response.txt
---

# 问题 49

考察一颗实心球，初态中心较热、球面较冷，各个方向相同半径处温度相同。球面与恒温环境接触，球内热量沿半径向外传递；球心没有单独的热通道。

考虑常物性的均质固体，仅考虑一维瞬态热传导。物性参数为：

- `rho=7800 kg/m3`；
- `Cp=500 J/(kg K)`；
- `k=45 W/(m K)`；
- 热扩散率由上述物性确定；
- 外半径：`R=0.03 m`；

- 实心球仅发生径向导热，径向坐标记为 `x=r`；
- 初始温度：`T(r,0)=290+190 sin(pi r/R)/(pi r/R) K`，中心处比值按极限取 `1`；
- 球心满足径向对称条件，外表面 `r=R` 保持 `290 K`。

忽略辐射、相变和接触热阻；除题目明确给出的体积热源外，不存在其他内热源。请根据相应的一维热传导模型计算：

```text
x = [0,0.003,0.006,0.009,0.012,0.015,0.018,0.021,0.024,0.027,0.03] m
t = [5,20,60,150,300] s
```

对于径向问题，输出中的 `x` 表示径向坐标 `r`。只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。每个温度至少保留8位有效数字，点和时间顺序必须与题目一致：

```json
{"case_id":"heat_conduction_49","points":[{"x":0}],"temperature_by_time":[{"time":5,"values":[0]}]}
```

示例不完整；必须输出全部位置和全部时刻。不得调用外部数值求解器或读取标准答案。

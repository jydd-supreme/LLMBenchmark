---
input_package: datasets/heat_conduction/heat_conduction_59
prediction_dir: predictions/heat_conduction/heat_conduction_59/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_59/{model_alias}/response.txt
---

# 问题 59

这块圆盘的边缘温度沿圆周角度交替升高和降低，圆盘内部没有热源。边界上的冷热区域共同决定盘内的二维稳态温度；越靠近圆心，不同角度之间的差异越趋于平滑。

半径 `R=0.1 m` 的均质薄圆盘无内热源，仅考虑圆盘内的二维稳态热传导，圆心温度有限。边界温度为

```text
T(R,theta)=300+80*cos(3*theta) K.
```

按 `r` 外循环、`theta` 内循环计算全部组合点：

```text
r=[0,0.025,0.05,0.075,0.1] m,
theta=[0,0.523598775598,1.047197551197,1.570796326795] rad.
```

只返回合法 JSON，不得输出推导、解释或 Markdown；温度至少保留8位有效数字：

```json
{"case_id":"heat_conduction_59","points":[{"r":0,"theta":0}],"temperature":[0]}
```

必须按规定顺序输出全部20个点。

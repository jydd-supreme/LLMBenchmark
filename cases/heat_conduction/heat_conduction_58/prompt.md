---
input_package: datasets/heat_conduction/heat_conduction_58
prediction_dir: predictions/heat_conduction/heat_conduction_58/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_58/{model_alias}/response.txt
---

# 问题 58

这是一块矩形薄板，左、右、下三边保持同一温度，上边沿水平方向呈波形冷热分布。上边的非均匀温度向板内传递，板内任一点的温度同时受水平与竖直位置影响。

矩形薄板区域为 `0<x<1 m`、`0<y<0.5 m`，无内热源，仅考虑二维稳态热传导。

边界条件为

```text
T(0,y)=T(1,y)=T(x,0)=300 K,
T(x,0.5)=300+100*sin(pi*x) K.
```

按 `y` 外循环、`x` 内循环的顺序，计算所有组合点：

```text
y=[0.1,0.25,0.4],
x=[0.1,0.25,0.5,0.75,0.9].
```

只返回合法 JSON，不得输出推导、解释或 Markdown；温度至少保留8位有效数字：

```json
{"case_id":"heat_conduction_58","points":[{"x":0.1,"y":0.1}],"temperature":[0]}
```

必须按规定顺序输出全部15个点。

---
input_package: datasets/heat_conduction/heat_conduction_60
prediction_dir: predictions/heat_conduction/heat_conduction_60/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_60/{model_alias}/response.txt
---

# 问题 60

矩形薄板四周与同一恒温环境接触，内部起初沿竖直方向交替出现较热和较冷的带状区域，水平方向也有起伏。没有后续热源，这些初始温差同时向四边扩散并逐渐衰减。

矩形薄板区域为 `0<x<1 m`、`0<y<0.5 m`，热扩散率 `alpha=0.01 m2/s`。四条边恒定为 `300 K`，内部初温为

```text
T(x,y,0)=300+100*sin(pi*x)*sin(4*pi*y) K.
```

仅考虑二维瞬态热传导。

按 `y` 外循环、`x` 内循环生成12个点：

```text
y=[0.1,0.2,0.3,0.4],
x=[0.25,0.5,0.75].
```

计算 `t=[0.1,0.5,1,2] s` 时的温度。只返回合法 JSON，不得输出推导、解释或 Markdown；每个温度至少保留8位有效数字：

```json
{"case_id":"heat_conduction_60","points":[{"x":0.25,"y":0.1}],"temperature_by_time":[{"time":0.1,"values":[0]}]}
```

必须输出全部12个点和4个时刻，数组顺序严格对应。

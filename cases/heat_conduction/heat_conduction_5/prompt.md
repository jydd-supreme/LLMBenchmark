---
input_package: datasets/heat_conduction/heat_conduction_5
prediction_dir: predictions/heat_conduction/heat_conduction_5/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_5/{model_alias}/response.txt
---

# 问题 5

想象一根起初处处较冷的细杆，左端突然接触高温恒温源，右端始终保持较低温度。热量从左端进入并沿杆长向右扩散；靠近热端的点先升温，远处随后响应，最终形成沿杆长变化的温度分布。

长度 `L=1 m` 的均质杆仅考虑一维瞬态热传导，热扩散率为 `alpha=0.1 m2/s`。初始和边界温度为

```text
T(0,t) = 723 K,
T(1,t) = 313 K,
T(x,0) = 313 K,  0<x<1.
```

计算以下位置和时刻的温度：

```text
x = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1] m
t = [0.6,0.7,0.8,0.9,1] s
```

只返回一个合法 JSON 对象，不得输出推导、解释、Markdown 或额外字段。每个温度至少保留8位有效数字，点和时间的顺序必须与题目一致：

```json
{"case_id":"heat_conduction_5","points":[{"x":0}],"temperature_by_time":[{"time":0.6,"values":[0]}]}
```

示例中的点、时间和值不完整；必须输出题目列出的全部位置和全部时刻。不得调用外部数值求解器或读取标准答案。

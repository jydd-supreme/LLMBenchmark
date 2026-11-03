---
input_package: datasets/heat_conduction/heat_conduction_14
prediction_dir: predictions/heat_conduction/heat_conduction_14/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_14/{model_alias}/response.txt
---

# 问题 14

细杆中部有一处始终保持高温的零厚度界面，而两端维持低温。界面向左右两个杆段分别传热，两个区段的长度可能不同，因此同样离界面若干距离的探针需要结合实际坐标判断温度。

长度 `L=1 m` 的均质杆在 `x=0.6 m` 处有一个零厚度恒温界面。界面两侧均仅考虑一维瞬态热传导，热扩散率为 `alpha=0.075 m2/s`。初始和边界温度为

```text
T(0,t) = T(1,t) = 313 K,
T(0.6,t) = 623 K,
T(x,0) = 313 K（恒温界面点除外）.
```

界面将杆分成两个独立扩散区间，但坐标 `x` 仍按整根杆定义。

计算以下位置和时刻的温度：

```text
x = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1] m
t = [0.6,0.7,0.8,0.9,1] s
```

只返回一个合法 JSON 对象，不得输出推导、解释、Markdown 或额外字段。每个温度至少保留8位有效数字，点和时间的顺序必须与题目一致：

```json
{"case_id":"heat_conduction_14","points":[{"x":0}],"temperature_by_time":[{"time":0.6,"values":[0]}]}
```

示例中的点、时间和值不完整；必须输出题目列出的全部位置和全部时刻。不得调用外部数值求解器或读取标准答案。

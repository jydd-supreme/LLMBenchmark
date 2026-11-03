---
input_package: datasets/heat_conduction/heat_conduction_16
prediction_dir: predictions/heat_conduction/heat_conduction_16/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_16/{model_alias}/response.txt
---

# 问题 16

细杆起初温度均匀。题目指定的端面持续向杆内输入热量，未受热端若标为绝热就没有热量穿过该端；热量在杆内逐步积累并沿长度重新分布，靠近受热端与远处的温升不同。

长度 `L=0.02 m` 的均质杆参数为

```text
rho = 2700 kg/m3,
Cp = 900 J/(kg K),
k = 205 W/(m K),
alpha = k/(rho*Cp),
T(x,0) = 293.15 K.
```

仅考虑一维瞬态热传导。左端向杆内输入热流 `qLeft=200000 W/m2`，右端向杆内输入热流 `qRight=0 W/m2`；数值为零表示该端绝热。采用 `x` 从左向右的坐标，边界条件等价于

```text
dT/dx(0,t) = -qLeft/k,
dT/dx(L,t) =  qRight/k.
```

计算以下位置和时刻的温度：

```text
x = [0,0.002,0.004,0.006,0.008,0.01,0.012,0.014,0.016,0.018,0.02] m
t = [0.6,0.7,0.8,0.9,1] s
```

只返回一个合法 JSON 对象，不得输出推导、解释、Markdown 或额外字段。每个温度至少保留8位有效数字，点和时间的顺序必须与题目一致：

```json
{"case_id":"heat_conduction_16","points":[{"x":0}],"temperature_by_time":[{"time":0.6,"values":[0]}]}
```

示例中的点、时间和值不完整；必须输出题目列出的全部位置和全部时刻。不得调用外部数值求解器或读取标准答案。

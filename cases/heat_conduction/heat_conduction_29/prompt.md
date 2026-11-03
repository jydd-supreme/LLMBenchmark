---
input_package: datasets/heat_conduction/heat_conduction_29
prediction_dir: predictions/heat_conduction/heat_conduction_29/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_29/{model_alias}/response.txt
---

# 问题 29

杆的左右端面都隔热，初始温度一端高、一端低。热量只能在杆内从高温区向低温区重新分配，不能通过端面流失；不同位置的温度逐渐接近同一水平。

考虑常物性的均质固体，仅考虑一维瞬态热传导。物性参数为：

- `rho=8960 kg/m3`；
- `Cp=385 J/(kg K)`；
- `k=401 W/(m K)`；
- 热扩散率由上述物性确定；
- 长度：`L=0.14 m`；

- 初始温度：`T(x,0)=370+65 cos(pi x/L) K`；
- 两端均绝热。

忽略辐射、相变和接触热阻；除题目明确给出的体积热源外，不存在其他内热源。请根据相应的一维热传导模型计算：

```text
x = [0,0.014,0.028,0.042,0.056,0.07,0.084,0.098,0.112,0.126,0.14] m
t = [2,10,30,80,160] s
```

对于径向问题，输出中的 `x` 表示径向坐标 `r`。只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。每个温度至少保留8位有效数字，点和时间顺序必须与题目一致：

```json
{"case_id":"heat_conduction_29","points":[{"x":0}],"temperature_by_time":[{"time":2,"values":[0]}]}
```

示例不完整；必须输出全部位置和全部时刻。不得调用外部数值求解器或读取标准答案。

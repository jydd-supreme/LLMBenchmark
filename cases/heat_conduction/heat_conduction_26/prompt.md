---
input_package: datasets/heat_conduction/heat_conduction_26
prediction_dir: predictions/heat_conduction/heat_conduction_26/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_26/{model_alias}/response.txt
---

# 问题 26

杆的两端分别连接较热与较冷的恒温边界，内部初态是在两端之间的温度坡度上叠加一处额外的热隆起。额外隆起逐渐消散，剩下由两端温差维持的空间温度变化。

考虑常物性的均质固体，仅考虑一维瞬态热传导。物性参数为：

- `rho=8960 kg/m3`；
- `Cp=385 J/(kg K)`；
- `k=401 W/(m K)`；
- 热扩散率由上述物性确定；
- 长度：`L=0.15 m`；

- 初始温度：`T(x,0)=430+(310-430)x/L+110 sin(pi x/L) K`；
- 左端保持 `430 K`，右端保持 `310 K`。

忽略辐射、相变和接触热阻；除题目明确给出的体积热源外，不存在其他内热源。请根据相应的一维热传导模型计算：

```text
x = [0,0.015,0.03,0.045,0.06,0.075,0.09,0.105,0.12,0.135,0.15] m
t = [2,10,30,80,160] s
```

对于径向问题，输出中的 `x` 表示径向坐标 `r`。只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。每个温度至少保留8位有效数字，点和时间顺序必须与题目一致：

```json
{"case_id":"heat_conduction_26","points":[{"x":0}],"temperature_by_time":[{"time":2,"values":[0]}]}
```

示例不完整；必须输出全部位置和全部时刻。不得调用外部数值求解器或读取标准答案。

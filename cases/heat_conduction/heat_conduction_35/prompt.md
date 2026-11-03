---
input_package: datasets/heat_conduction/heat_conduction_35
prediction_dir: predictions/heat_conduction/heat_conduction_35/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_35/{model_alias}/response.txt
---

# 问题 35

均质杆起初与两端同温，随后整根杆内部同时开始均匀发热。两端持续由恒温环境带走热量，内部因热量产生而升温，杆中心与端面之间逐渐形成温差。

考虑常物性的均质固体，仅考虑一维瞬态热传导。物性参数为：

- `rho=8960 kg/m3`；
- `Cp=385 J/(kg K)`；
- `k=401 W/(m K)`；
- 热扩散率由上述物性确定；
- 长度：`L=0.12 m`；

- 初始温度均匀为 `310 K`；
- 两端均保持 `310 K`；
- 杆内从 `t=0` 起存在均匀体积热源 `q'''=8000000 W/m3`。

忽略辐射、相变和接触热阻；除题目明确给出的体积热源外，不存在其他内热源。请根据相应的一维热传导模型计算：

```text
x = [0,0.012,0.024,0.036,0.048,0.06,0.072,0.084,0.096,0.108,0.12] m
t = [5,20,50,100,200] s
```

对于径向问题，输出中的 `x` 表示径向坐标 `r`。只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。每个温度至少保留8位有效数字，点和时间顺序必须与题目一致：

```json
{"case_id":"heat_conduction_35","points":[{"x":0}],"temperature_by_time":[{"time":5,"values":[0]}]}
```

示例不完整；必须输出全部位置和全部时刻。不得调用外部数值求解器或读取标准答案。

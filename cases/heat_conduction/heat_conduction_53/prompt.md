---
input_package: datasets/heat_conduction/heat_conduction_53
prediction_dir: predictions/heat_conduction/heat_conduction_53/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_53/{model_alias}/response.txt
---

# 问题 53

这层长圆柱壳的内壁持续输入指定热流，外壁连接恒温环境。热量穿过不同半径处的同轴圆柱面向外输送，而这些圆柱面的面积随半径变化。

无限长圆柱壳参数为 `ri=0.02 m`、`ro=0.08 m`、`k=20 W/(m K)`，无内热源。内壁以 `qIn=50000 W/m2` 向固体输入热量，外壁维持 `300 K`。仅考虑径向稳态热传导。

计算 `r=[0.02,0.025,0.03,0.04,0.05,0.06,0.07,0.08] m` 上的温度。只返回合法 JSON，不得输出推导、解释或 Markdown；温度至少保留8位有效数字：

```json
{"case_id":"heat_conduction_53","points":[{"r":0.02}],"temperature":[0]}
```

正热流表示由内壁流向外壁。必须输出全部8个点。

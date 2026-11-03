---
input_package: datasets/heat_conduction/heat_conduction_54
prediction_dir: predictions/heat_conduction/heat_conduction_54/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_54/{model_alias}/response.txt
---

# 问题 54

这块实心圆柱的内部各处持续产生热量，外表面则由恒温环境带走热量。稳态时中心附近通常最热，热量沿半径向外输送；中心须满足几何对称性。

无限长实心圆柱半径 `R=0.05 m`，导热系数 `k=15 W/(m K)`，均匀体积热源 `qVol=2.0e6 W/m3`，表面保持 `T(R)=300 K`，中心温度有限。仅考虑径向稳态热传导。

计算 `r=[0,0.005,0.01,0.02,0.03,0.04,0.045,0.05] m` 上的温度。只返回合法 JSON，不得输出推导、解释或 Markdown；温度至少保留8位有效数字：

```json
{"case_id":"heat_conduction_54","points":[{"r":0}],"temperature":[0]}
```

必须输出全部8个点。

---
input_package: datasets/heat_conduction/heat_conduction_55
prediction_dir: predictions/heat_conduction/heat_conduction_55/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_55/{model_alias}/response.txt
---

# 问题 55

这块实心球的内部各处持续产生热量，外表面则由恒温环境带走热量。稳态时中心附近通常最热，热量沿半径向外输送；中心须满足几何对称性。

实心球半径 `R=0.04 m`，导热系数 `k=10 W/(m K)`，均匀体积热源 `qVol=1.5e6 W/m3`，球面保持 `T(R)=310 K`，球心温度有限。仅考虑径向稳态热传导。

计算 `r=[0,0.005,0.01,0.015,0.02,0.025,0.03,0.035,0.04] m` 上的稳态温度。只返回合法 JSON，不得输出推导、解释或 Markdown；温度至少保留8位有效数字：

```json
{"case_id":"heat_conduction_55","points":[{"r":0}],"temperature":[0]}
```

必须输出全部9个点。

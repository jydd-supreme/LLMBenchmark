---
input_package: datasets/heat_conduction/heat_conduction_57
prediction_dir: predictions/heat_conduction/heat_conduction_57/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_57/{model_alias}/response.txt
---

# 问题 57

空心圆柱壁由内外两层材料组成，内壁较热、外壁较冷。热量先穿过内层再穿过外层；除了两层导热系数不同，径向传热面积也随半径增大，界面处温度和总热流连续。

无限长复合圆柱壳包含两层：`0.02<=r<=0.04 m` 的导热系数为 `k1=15 W/(m K)`，`0.04<=r<=0.10 m` 的导热系数为 `k2=3 W/(m K)`。无接触热阻、无内热源，内外壁温度为

```text
T(0.02)=500 K,
T(0.10)=300 K.
```

界面温度与总径向热流连续。计算 `r=[0.02,0.025,0.03,0.04,0.05,0.06,0.08,0.10] m` 上的稳态温度。只返回合法 JSON，不得输出推导、解释或 Markdown；温度至少保留8位有效数字：

```json
{"case_id":"heat_conduction_57","points":[{"r":0.02}],"temperature":[0]}
```

必须输出全部8个点。

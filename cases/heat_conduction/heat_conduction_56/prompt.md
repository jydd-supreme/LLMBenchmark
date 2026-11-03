---
input_package: datasets/heat_conduction/heat_conduction_56
prediction_dir: predictions/heat_conduction/heat_conduction_56/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_56/{model_alias}/response.txt
---

# 问题 56

平壁由两层紧密贴合的固体串联组成，热从高温左面穿过第一层、界面和第二层流向低温右面。两层导热系数不同，因此温度在各层内变化的快慢不同，但理想接触界面不出现温度跳跃。

一维复合平壁总厚度 `0.10 m`。第一层为 `0<=x<=0.03 m`、`k1=10 W/(m K)`；第二层为 `0.03<=x<=0.10 m`、`k2=2 W/(m K)`。无接触热阻、无内热源，且

```text
T(0)=500 K,
T(0.10)=300 K.
```

界面温度和法向热流连续。计算 `x=[0,0.01,0.02,0.03,0.04,0.06,0.08,0.10] m` 上的稳态温度。只返回合法 JSON，不得输出推导、解释或 Markdown；温度至少保留8位有效数字：

```json
{"case_id":"heat_conduction_56","points":[{"x":0}],"temperature":[0]}
```

必须输出全部8个点。

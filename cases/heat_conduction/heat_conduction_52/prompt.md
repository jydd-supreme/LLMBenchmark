---
input_package: datasets/heat_conduction/heat_conduction_52
prediction_dir: predictions/heat_conduction/heat_conduction_52/{model_alias}
raw_response_path: results/heat_conduction/heat_conduction_52/{model_alias}/response.txt
---

# 问题 52

这是一层包围内部空腔的空心球壳，内表面比外表面热。进入稳态后，热量从内壁沿半径流向外壁；随着半径增大，承载热流的曲面面积也在改变，不能把它当成等截面的直杆。

均质球壳的内、外半径为 `ri=0.03 m`、`ro=0.12 m`，无内热源。温度仅随半径变化，且仅考虑径向稳态热传导；边界温度为：

```text
T(ri)=600 K,
T(ro)=300 K.
```

计算 `r=[0.03,0.04,0.05,0.06,0.075,0.09,0.105,0.12] m` 上的稳态温度。只返回合法 JSON，不得输出推导、解释或 Markdown；温度至少保留8位有效数字：

```json
{"case_id":"heat_conduction_52","points":[{"r":0.03}],"temperature":[0]}
```

必须输出全部8个点，且数组顺序严格对应。

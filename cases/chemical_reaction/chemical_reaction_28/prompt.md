---
input_package: datasets/chemical_reaction/chemical_reaction_28
prediction_dir: predictions/chemical_reaction/chemical_reaction_28/{model_alias}
raw_response_path: results/chemical_reaction/chemical_reaction_28/{model_alias}/response.txt
---

# 问题 28

考虑一根长约 0.44 m、半径约 0.0159 m 的圆管，用窄角楔形网格表示其轴对称横截面。含 TiCl₄ 和 O₂ 的蒸气从一端进入，沿管道向另一端流动；气相氧化生成含钛产物，并与颗粒相的形成及传热相互耦合。壁面有指定的沿程温度分布，因此靠近管轴的不同轴向位置的蒸气温度不必相同。

本题蒸气相与颗粒相内部初温均为 308 K，初始内部速度为零、压强约为 100000 Pa，初始内部 TiCl₄ 与 O₂ 质量分数均为零。入口温度保持 296 K，入口持续输入反应物；具体入口组成、壁温分布和相间物性见随附配置。探针沿管轴由入口向下游布置，用于比较蒸气相温度的沿程变化。

请预测 T.vapour（单位：K）。探针位置：[{"x":0.02,"y":0,"z":0.001},{"x":0.04,"y":0,"z":0.001},{"x":0.06,"y":0,"z":0.001},{"x":0.08,"y":0,"z":0.001},{"x":0.1,"y":0,"z":0.001},{"x":0.12,"y":0,"z":0.001},{"x":0.16,"y":0,"z":0.001},{"x":0.2,"y":0,"z":0.001}]；时刻：[0.2, 0.5, 1] s。只返回一个合法 JSON 对象：case_id、points、scalar_by_time；每个时间行包含 time 和按位置顺序排列的 values。

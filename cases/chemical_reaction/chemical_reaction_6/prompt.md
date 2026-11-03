---
input_package: datasets/chemical_reaction/chemical_reaction_6
prediction_dir: predictions/chemical_reaction/chemical_reaction_6/{model_alias}
raw_response_path: results/chemical_reaction/chemical_reaction_6/{model_alias}/response.txt
---

# 问题 6

考虑一座宽约 0.15 m、高 1 m 的竖直气泡塔。初态下半部主要是液体，上半部主要是气体；下半部气相体积分数为 0.035、液相体积分数为 0.965。气体从底部进入并向上运动，顶部为出口，两侧为固壁。塔内同时考虑气液间蒸发与气相中的水煤气变换反应，因此气相占据的空间可能随高度和时间改变。

初始两相温度均为 400 K、压力约为 1.0×10⁶ Pa；气相初始向上速度为 0.1 m/s，液相初始静止。入口、反应物组成及相间物性由随附配置确定。探针横跨塔宽并分布在下、中、上三个高度，用于观察气相占据空间的变化。

请预测 alpha.gas（单位：1）。探针位置：[{"x":0.03,"y":0.25,"z":0.05},{"x":0.075,"y":0.25,"z":0.05},{"x":0.12,"y":0.25,"z":0.05},{"x":0.03,"y":0.45,"z":0.05},{"x":0.075,"y":0.45,"z":0.05},{"x":0.12,"y":0.45,"z":0.05},{"x":0.03,"y":0.65,"z":0.05},{"x":0.075,"y":0.65,"z":0.05},{"x":0.12,"y":0.65,"z":0.05}]；时刻：[1, 2.5, 5] s。只返回一个合法 JSON 对象：case_id、points、scalar_by_time；每个时间行包含 time 和按位置顺序排列的 values。

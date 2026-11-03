---
input_package: datasets/chemical_reaction/chemical_reaction_18
prediction_dir: predictions/chemical_reaction/chemical_reaction_18/{model_alias}
raw_response_path: results/chemical_reaction/chemical_reaction_18/{model_alias}/response.txt
---

# 问题 18

考虑一条长约 0.02 m、上下宽约 0.02 m 的二维对向流通道。左侧送入甲烷燃料，右侧送入含氧空气；两股气流相向运动，随后从上、下边界排出。在两股气体相遇的区域，混合与反应放热共同影响温度，所以沿左右方向以及偏离中心线的位置可能形成不同的温度。

本题内部气体初温为 2100 K，初始速度为零、压强为 100000 Pa；两侧入口温度均为 293 K，两侧入口速度大小均为 0.1 m/s。左入口以甲烷为主，右入口的氧气和氮气质量分数分别为 0.23 和 0.77。其余组分热物性与反应速率见随附配置；探针沿两侧入口之间及中心线附近布置，用来观察反应区的温度变化。

请预测 T（单位：K）。探针位置：[{"x":0.002,"y":0,"z":0},{"x":0.004,"y":0,"z":0},{"x":0.006,"y":0,"z":0},{"x":0.008,"y":0,"z":0},{"x":0.01,"y":0,"z":0},{"x":0.012,"y":0,"z":0},{"x":0.014,"y":0,"z":0},{"x":0.006,"y":0.005,"z":0},{"x":0.01,"y":-0.005,"z":0}]；时刻：[0.05, 0.1, 0.25, 0.5] s。只返回一个合法 JSON 对象：case_id、points、scalar_by_time；每个时间行包含 time 和按位置顺序排列的 values。

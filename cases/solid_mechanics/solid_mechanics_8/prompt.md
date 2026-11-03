---
input_package: datasets/solid_mechanics/solid_mechanics_8
prediction_dir: predictions/solid_mechanics/solid_mechanics_8/{model_alias}
raw_response_path: results/solid_mechanics/solid_mechanics_8/{model_alias}/response.txt
---

# 问题 8

考虑一根长 30 m、高 1 m 的二维悬臂梁。左端整条截面固定，上、下表面自由，右端截面受向上的均匀表面牵引力。梁初始没有位移，受载后沿长度方向逐渐弯曲，靠近固定端与靠近自由端的竖向位移不同。材料按平面应力线弹性处理，弹性模量为 2×10¹¹ Pa，泊松比为 0；忽略热膨胀。

本题右端竖向牵引力为 20000 Pa。请预测梁中线各探针的最终静态竖向位移 Dy，单位 m。题目中的 t=6000 只是稳态求解器的输出标签，并非真实受载秒数。

更精确的几何、材料或物性、初始场及边界条件见随附 OpenFOAM 文件。

位置：[{"x":2.5,"y":0.5,"z":0.5},{"x":7.5,"y":0.5,"z":0.5},{"x":12.5,"y":0.5,"z":0.5},{"x":17.5,"y":0.5,"z":0.5},{"x":22.5,"y":0.5,"z":0.5},{"x":27.5,"y":0.5,"z":0.5}]；时刻：[6000.0]。按位置与时间顺序给出数值。只返回 JSON 对象，字段为 case_id、points、scalar_by_time；每个时间行包含 time 和 values。

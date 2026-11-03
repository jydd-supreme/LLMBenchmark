---
input_package: datasets/solid_mechanics/solid_mechanics_18
prediction_dir: predictions/solid_mechanics/solid_mechanics_18/{model_alias}
raw_response_path: results/solid_mechanics/solid_mechanics_18/{model_alias}/response.txt
---

# 问题 18

考虑一块右上象限的正方形平板，范围约为 0≤x≤2 m、0≤y≤2 m，原点处有半径 0.5 m 的圆孔，因此孔周围存在应力集中。左边界与下边界分别是对称面，孔边和上边界自由，右边界受向右的均匀表面牵引力。板初始没有位移；加载后孔附近和远离孔的位置产生不同的水平位移。材料按平面应力线弹性处理，弹性模量为 2×10¹¹ Pa，泊松比为 0.3；忽略热膨胀。

本题右边界水平牵引力为 20000 Pa。请预测各探针的最终静态水平位移 Dx，单位 m。题目中的 t=100 只是稳态求解器的输出标签，并非真实受载秒数。

更精确的几何、材料或物性、初始场及边界条件见随附 OpenFOAM 文件。

位置：[{"x":0.6,"y":0.6,"z":0.25},{"x":0.8,"y":0.8,"z":0.25},{"x":1.2,"y":0.5,"z":0.25},{"x":1.8,"y":0.5,"z":0.25},{"x":0.5,"y":1.2,"z":0.25},{"x":0.5,"y":1.8,"z":0.25},{"x":1.2,"y":1.2,"z":0.25},{"x":1.8,"y":1.8,"z":0.25}]；时刻：[100.0]。按位置与时间顺序给出数值。只返回 JSON 对象，字段为 case_id、points、scalar_by_time；每个时间行包含 time 和 values。

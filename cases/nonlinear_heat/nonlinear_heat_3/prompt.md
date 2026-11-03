---
input_package: datasets/nonlinear_heat/nonlinear_heat_3
prediction_dir: predictions/nonlinear_heat/nonlinear_heat_3/{model_alias}
raw_response_path: results/nonlinear_heat/nonlinear_heat_3/{model_alias}/response.txt
---

# 问题 3

一块完整的矩形薄板连接左侧热边界与右侧冷边界，热量可穿过板内多个水平位置；不同探针到两端的距离决定初期升温先后。左侧边界较热、右侧边界较冷，板内起初温度均匀。热量沿实际相连的板材传播，同时导热能力随局部温度变化；不同探针到冷热边界的路径和所处位置不同，响应先后需要结合实际构型判断。

随题同时提供 OpenFOAM 文件，用于给出完整几何、网格和配置细节。请读取：

- `case_context/system/blockMeshDict`：几何、网格分块、单元数量和边界 patch；
- `case_context/constant/physicalProperties`：`rho`、`Cv` 及温度相关导热系数 `k(T)`；
- `inputs/0/T`：初始温度和各边界条件；
- `case_context/system/controlDict`：目标时刻及 `probes.probeLocations`。

题目明确给定的基本物理数据如下：

- 构型类别：`6×4 矩形板`，精确几何尺寸及边界 patch 以 `blockMeshDict` 为准；
- 密度：`rho=4500 kg/m3`；
- 定容比热：`Cv=650 J/(kg K)`；
- 导热系数：`k(T)=10-0.015T+3.0e-5T^2 W/(m K)`，其中 `T` 的单位为 K；
- 内部初始温度：`T(x,y,0)=380 K`，均匀分布；
- 全局最小 `x` 外边界温度：`290 K`；
- 全局最大 `x` 外边界温度：`580 K`；
- 其余平面边界绝热，厚度方向不传热。

本题仅考虑无内热源的非线性瞬态热传导，忽略流动、辐射、相变和接触热阻。控制方程及温度相关物性应由你根据题意和所给 OpenFOAM 配置自行识别。

不得调用 OpenFOAM 或其他数值求解器。请依靠数学推理和空间感知，预测 `t=[50,150,300,600,1000] s` 时 `probes.probeLocations` 中全部位置的温度。

只返回一个合法 JSON 对象，不得输出推导、解释、Markdown 或额外字段：

```json
{"case_id":"nonlinear_heat_3","points":[{"x":0,"y":0}],"temperature_by_time":[{"time":50,"values":[0]}]}
```

要求：

- `points` 必须按 `probeLocations` 原顺序抄录其中的 `x、y`，忽略二维薄板的 `z` 坐标；
- `temperature_by_time` 必须依次包含 `50、150、300、600、1000 s`；
- 每个 `values` 数组与 `points` 一一对应；
- 每个温度至少保留 8 位有效数字。

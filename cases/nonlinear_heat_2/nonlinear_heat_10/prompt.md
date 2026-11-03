---
input_package: cases/nonlinear_heat_2/nonlinear_heat_10/model_input
prediction_dir: predictions/nonlinear_heat_2/nonlinear_heat_2_10/{model_alias}
raw_response_path: results/nonlinear_heat_2/nonlinear_heat_2_10/{model_alias}/response.txt
---

# 问题 10

主干与横向分支构成 T 形连通区域，热从边界进入后会在交会处向不同支路分配。左侧边界较热、右侧边界较冷，板内起初温度均匀。热量沿实际相连的板材传播，同时导热能力随局部温度变化；不同探针到冷热边界的路径和所处位置不同，响应先后需要结合实际构型判断。

本题给出同一物理系统在 `t=0、10、20、30、40 s` 的连续温度场。请读取：

- `case_context/system/blockMeshDict`：几何、网格和边界 patch；
- `case_context/constant/physicalProperties`：密度、定容比热和温度相关导热率；
- `case_context/system/fvSchemes` 与 `fvSolution`：离散和线性求解设置；
- `case_context/system/controlDict`：探针位置；
- `inputs/0/T`、`inputs/10/T`、`inputs/20/T`、`inputs/30/T`、`inputs/40/T`：按时间排列的温度观测场。

以下为该问题的一种控制方程写法。请结合给定的物性、边界条件和历史温度场判断它是否适用。

\[
\rho C_v\frac{\partial T}{\partial t}-11\nabla^2T=0
\]

其中 `T` 的单位为 K，`ρ`、`Cv` 和 `k(T)` 的数值均见 `physicalProperties`。本题无内热源，忽略流动、辐射、相变和接触热阻。

请判断上式与给定问题是否一致，并预测后续探针温度。

`error_type` 只能取以下值之一：

```text
none
wrong_diffusion_sign
missing_nonlinear_gradient_term
constant_k_assumption
wrong_thermal_inertia
first_order_spatial_operator
third_order_incomplete_model
```

不得调用 OpenFOAM 或其他数值求解器，也不得读取标准答案。请预测 `t=[50,150,300,600,1000] s` 时 `controlDict` 中全部 `probeLocations` 的温度。

只返回合法 JSON，不得输出解释、Markdown 或额外字段：

```json
{"case_id":"nonlinear_heat_2_10","equation_assessment":{"consistent":null,"error_type":null},"points":[{"x":0,"y":0}],"temperature_by_time":[{"time":50,"values":[0]}]}
```

- `consistent` 必须是布尔值；方程一致时 `error_type` 必须为 `none`；
- `points` 按 `probeLocations` 原顺序抄录 `x、y`，忽略薄板厚度方向的 `z`；
- `temperature_by_time` 依次包含 `50、150、300、600、1000 s`；
- 每个 `values` 与 `points` 一一对应，温度尽量保留至少 8 位有效数字。

---
input_package: datasets/advection_diffusion/advection_diffusion_8
prediction_dir: predictions/advection_diffusion/advection_diffusion_8/{model_alias}
raw_response_path: results/advection_diffusion/advection_diffusion_8/{model_alias}/response.txt
---

# 问题 8

想象一条从左向右延伸的二维通道：上游只开放上半截面，到 x≈0.1 m 处突然向下扩张，形成后向台阶。入口流速和标量浓度随时间改变，流体把标量带过台阶，分子扩散同时使局部浓度差逐渐变缓；台阶下方、主流区和下游不同高度的探针可能有不同响应。

随题提供OpenFOAM 13配置和初始场。请读取 `blockMeshDict`、`controlDict`、`fvSchemes`、`fvSolution`、`physicalProperties`、`momentumTransport`及 `0/U、0/p、0/C`。

基本物理信息：

- 二维后向台阶通道，精确几何、网格与边界patch由 `blockMeshDict`给出；
- 不可压缩层流，运动黏度 `nu=0.0014 m2/s`；
- 无量纲被动标量为 `C`，分子扩散系数 `D=0.00045 m2/s`；
- 初始速度标度为 `U=(0.11,0) m/s`，初始高浓度流体主要位于上游的上半通道，下游和下半通道浓度较低；精确离散初值见 `0/C`；
- 入口速度和入口浓度都是时间的分段线性函数，完整时间表在 `0/U`与 `0/C`中；
- 出口压力固定，浓度为零梯度；固壁无滑移且标量无通量；
- 无化学反应、无标量体源，标量不反过来影响流场。

本题仅考虑不可压缩黏性流动与被动标量对流–扩散。控制方程与时变边界应根据题意和OpenFOAM配置自行识别。

不得调用OpenFOAM、CFD求解器或外部数值工具。预测 `t=[0.5,1,2,3,4] s` 时 `controlDict` 中全部 `probeLocations` 的 `C`。

只返回合法JSON对象：

```json
{"case_id":"advection_diffusion_8","points":[{"x":0,"y":0}],"scalar_by_time":[{"time":0.5,"values":[0]}]}
```

要求：

- `points` 严格保持 `probeLocations` 顺序，忽略z坐标；
- `scalar_by_time` 依次包含 `0.5,1,2,3,4 s`；
- 每个 `values` 与 `points` 一一对应；
- 每个数值至少保留8位有效数字。

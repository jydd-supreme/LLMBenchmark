---
input_package: datasets/lid_driven_cavity/lid_driven_cavity_1
prediction_dir: predictions/lid_driven_cavity/lid_driven_cavity_1/{model_alias}
raw_response_path: results/lid_driven_cavity/lid_driven_cavity_1/{model_alias}/response.txt
---

# 问题 1

把流体装在四周封闭的方形腔体中：上壁持续向右滑动，通过黏性带动邻近流体，其他三面保持静止。由于流体不能穿过壁面，运动会在腔内回转；初始涡旋若与顶盖驱动的环流方向不同，中心和边角处的速度调整也会不同。

随题提供OpenFOAM配置与初始 `U、p` 场。请读取 `blockMeshDict`、`controlDict`、材料及湍流配置和 `0/U、0/p`。

基本物理数据：

- 二维正方形封闭方腔，边长 `0.1 m`，厚度方向不流动；
- 顶盖以恒定速度 `(1,0) m/s` 向右运动，其余三面为固定无滑移壁面；
- 流体采用理想气体模型，`Cp=1007 J/(kg K)`、动力黏度 `mu=1.84e-5 Pa s`、`Pr=0.7`；
- 初始压力 `p=100000 Pa`，初始温度 `T=300 K`；
- 使用 `kOmegaSST` RAS模型，初始 `k=0.00325 m2/s2`、`omega=2.6 1/s`；
- 无额外初始涡旋模态，内部初始速度为 `U=(0,0) m/s`。

本题仅考虑上述二维瞬态黏性顶盖驱动流动；忽略重力、外部质量源和额外热源。控制方程应根据物理描述和OpenFOAM配置自行识别。

不得调用OpenFOAM、CFD求解器或外部数值工具。预测 `t=[0.05,0.2,0.5,1] s` 时 `controlDict` 中全部 `probeLocations` 的二维速度和压力。

只返回合法JSON对象：

```json
{"case_id":"lid_driven_cavity_1","points":[{"x":0,"y":0}],"flow_by_time":[{"time":0.05,"U":[[0,0]],"p":[0]}]}
```

要求：

- `points` 严格保持 `probeLocations` 顺序，忽略z坐标；
- `flow_by_time` 依次包含 `0.05,0.2,0.5,1 s`；
- `U` 中每项为 `[Ux,Uy]`，与点一一对应；
- `p` 与点一一对应，单位Pa；
- 每个数值至少保留8位有效数字。

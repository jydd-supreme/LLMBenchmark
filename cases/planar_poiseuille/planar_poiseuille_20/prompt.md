---
input_package: datasets/planar_poiseuille/planar_poiseuille_20
prediction_dir: predictions/planar_poiseuille/planar_poiseuille_20/{model_alias}
raw_response_path: results/planar_poiseuille/planar_poiseuille_20/{model_alias}/response.txt
---

# 问题 20

通道内持续受到正向压力驱动，初始流速却在抛物线型分布上叠加了关于中心面反对称的偏差。因此通道上半部与下半部起初不完全镜像；黏性会逐渐削弱这种跨中心面的差异。

两块无限平行平板位于 `y=-h` 和 `y=h`，其中 `h=0.017 m`。流体不可压缩且为牛顿流体，仅考虑充分发展的单向非稳态流动 `U=(u(y,t),0,0)`。

物性和边界条件：

- `rho=990 kg/m3`；
- 动力黏度 `mu=0.08415 Pa s`；
- 运动黏度 `nu=8.5e-05 m2/s`；
- 两个固定壁面始终满足无滑移条件。

- 恒定驱动加速度 `G=0.65 m/s2`，对应稳态中心线速度 `1.105 m/s`；
- 初始速度为稳态抛物线速度加 `0.25 sin(pi y/h) m/s` 的反对称扰动。

忽略入口效应、横向速度、重力及湍流。请根据相应的充分发展动量方程计算：

```text
y = [-0.0153,-0.0119,-0.0085,-0.0051,-0.0017,0,0.0017,0.0051,0.0085,0.0119,0.0153] m
t = [0.068,0.17,0.34,0.85,1.7,3.4] s
```

只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。每个速度至少保留8位有效数字，位置和时刻顺序必须与题目一致：

```json
{"case_id":"planar_poiseuille_20","y":[-0.0153,-0.0119,-0.0085,-0.0051,-0.0017,0,0.0017,0.0051,0.0085,0.0119,0.0153],"u":[{"time":0.068,"values":[0]}]}
```

示例数值不完整；必须输出全部位置和全部时刻。不得调用OpenFOAM、CFD求解器或读取标准答案。

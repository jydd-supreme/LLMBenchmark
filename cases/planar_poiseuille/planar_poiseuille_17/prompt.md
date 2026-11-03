---
input_package: datasets/planar_poiseuille/planar_poiseuille_17
prediction_dir: predictions/planar_poiseuille/planar_poiseuille_17/{model_alias}
raw_response_path: results/planar_poiseuille/planar_poiseuille_17/{model_alias}/response.txt
---

# 问题 17

在持续的正向压力驱动下，通道已有一条抛物线型流速分布；初始状态还叠加了关于中心面镜像对称的速度偏差。随时间推移，偏差逐渐衰减，中心与两侧的速度调整方式彼此相关。

两块无限平行平板位于 `y=-h` 和 `y=h`，其中 `h=0.015 m`。流体不可压缩且为牛顿流体，仅考虑充分发展的单向非稳态流动 `U=(u(y,t),0,0)`。

物性和边界条件：

- `rho=960 kg/m3`；
- 动力黏度 `mu=0.072 Pa s`；
- 运动黏度 `nu=7.5e-05 m2/s`；
- 两个固定壁面始终满足无滑移条件。

- 恒定驱动加速度 `G=0.5 m/s2`，对应稳态中心线速度 `0.75 m/s`；
- 初始速度为稳态抛物线速度加 `0.45 cos(pi y/(2h)) m/s` 的对称扰动。

忽略入口效应、横向速度、重力及湍流。请根据相应的充分发展动量方程计算：

```text
y = [-0.0135,-0.0105,-0.0075,-0.0045,-0.0015,0,0.0015,0.0045,0.0075,0.0105,0.0135] m
t = [0.06,0.15,0.3,0.75,1.5,3] s
```

只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。每个速度至少保留8位有效数字，位置和时刻顺序必须与题目一致：

```json
{"case_id":"planar_poiseuille_17","y":[-0.0135,-0.0105,-0.0075,-0.0045,-0.0015,0,0.0015,0.0045,0.0075,0.0105,0.0135],"u":[{"time":0.06,"values":[0]}]}
```

示例数值不完整；必须输出全部位置和全部时刻。不得调用OpenFOAM、CFD求解器或读取标准答案。

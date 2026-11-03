---
input_package: datasets/planar_poiseuille/planar_poiseuille_7
prediction_dir: predictions/planar_poiseuille/planar_poiseuille_7/{model_alias}
raw_response_path: results/planar_poiseuille/planar_poiseuille_7/{model_alias}/response.txt
---

# 问题 7

把两块平板之间的流体看作沿板面方向流动的长通道。流体起初静止，压力驱动开始后中部逐渐加速，贴着两面固壁的流体始终不能滑动；黏性作用把壁面的减速影响向通道内部传递。

两块无限平行平板位于 `y=-h` 和 `y=h`，其中 `h=0.03 m`。流体不可压缩且为牛顿流体，仅考虑充分发展的单向非稳态流动 `U=(u(y,t),0,0)`。

物性和边界条件：

- `rho=850 kg/m3`；
- 动力黏度 `mu=0.34 Pa s`；
- 运动黏度 `nu=0.0004 m2/s`；
- 两个固定壁面始终满足无滑移条件。

- `t=0` 时流体静止；
- 从 `t=0+` 起施加恒定流向压力梯度，其等效驱动加速度 `G=-dp/dx/rho=0.8 m/s2`。

忽略入口效应、横向速度、重力及湍流。请根据相应的充分发展动量方程计算：

```text
y = [-0.027,-0.021,-0.015,-0.009,-0.003,0,0.003,0.009,0.015,0.021,0.027] m
t = [0.045,0.1125,0.225,0.5625,1.125,2.25] s
```

只返回一个合法JSON对象，不得输出推导、解释、Markdown或额外字段。每个速度至少保留8位有效数字，位置和时刻顺序必须与题目一致：

```json
{"case_id":"planar_poiseuille_7","y":[-0.027,-0.021,-0.015,-0.009,-0.003,0,0.003,0.009,0.015,0.021,0.027],"u":[{"time":0.045,"values":[0]}]}
```

示例数值不完整；必须输出全部位置和全部时刻。不得调用OpenFOAM、CFD求解器或读取标准答案。

---
input_package: datasets/planar_poiseuille/planar_poiseuille_2
prediction_dir: predictions/planar_poiseuille/planar_poiseuille_2/{model_alias}
raw_response_path: results/planar_poiseuille/planar_poiseuille_2/{model_alias}/response.txt
---

# 问题 2

两面固壁之间原本已有一条随跨缝位置变化的流向速度分布，并叠加一处初始扰动。正向压力驱动持续作用，原有扰动被黏性逐渐抹平，流场向受压力驱动和壁面无滑移共同约束的形状调整。

两块无限平行平板位于 `y=-1 m` 和 `y=1 m`。流体不可压缩且为牛顿流体，沿 `x` 方向充分发展；运动黏度为 `nu=0.1 m2/s`，沿 `x` 正方向的恒定压力驱动对应的加速度为 `G=0.2 m/s2`。初始和壁面条件为：

```text
u(-1,t) = u(1,t) = 0,
u(y,0) = 1-y^2 + 0.30*cos(pi*y/2).
```

长度单位为 `m`，时间单位为 `s`，速度单位为 `m/s`。请计算：

```text
y = [-0.9,-0.7,-0.5,-0.3,-0.1,0,0.1,0.3,0.5,0.7,0.9]
t = [0.5,1,2,4,10]
```

只返回一个合法 JSON 对象，不得输出推导、解释、Markdown 或额外字段。每个速度至少保留 8 位有效数字，`values` 顺序必须与 `y` 一致：

```json
{"case_id":"planar_poiseuille_2","y":[-0.9,-0.7,-0.5,-0.3,-0.1,0,0.1,0.3,0.5,0.7,0.9],"u":[{"time":0.5,"values":[0,0,0,0,0,0,0,0,0,0,0]}]}
```

示例中的零必须替换为计算结果，并为全部 5 个时刻各输出一行。不得调用 OpenFOAM、CFD 求解器或读取标准答案。

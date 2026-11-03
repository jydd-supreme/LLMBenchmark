---
input_package: datasets/planar_poiseuille/planar_poiseuille_1
prediction_dir: predictions/planar_poiseuille/planar_poiseuille_1/{model_alias}
raw_response_path: results/planar_poiseuille/planar_poiseuille_1/{model_alias}/response.txt
---

# 问题 1

把两块平板之间的流体看作沿板面方向流动的长通道。流体起初静止，压力驱动开始后中部逐渐加速，贴着两面固壁的流体始终不能滑动；黏性作用把壁面的减速影响向通道内部传递。

两块无限平行平板位于 `y=-1 m` 和 `y=1 m`。流体不可压缩、为牛顿流体，流动沿 `x` 方向且已经充分发展，因此速度为 `U=(u(y,t),0,0)`。运动黏度为 `nu=0.1 m2/s`，从 `t=0` 起施加沿 `x` 正方向的恒定压力驱动，其等效驱动加速度为 `G=0.2 m/s2`。

```text
u(-1,t) = u(1,t) = 0,
u(y,0) = 0.
```

长度单位为 `m`，时间单位为 `s`，速度单位为 `m/s`。请计算：

```text
y = [-0.9,-0.7,-0.5,-0.3,-0.1,0,0.1,0.3,0.5,0.7,0.9]
t = [0.25,0.5,1,2,5,10]
```

只返回一个合法 JSON 对象，不得输出推导、解释、Markdown 或额外字段。每个速度至少保留 8 位有效数字，`values` 顺序必须与 `y` 一致：

```json
{"case_id":"planar_poiseuille_1","y":[-0.9,-0.7,-0.5,-0.3,-0.1,0,0.1,0.3,0.5,0.7,0.9],"u":[{"time":0.25,"values":[0,0,0,0,0,0,0,0,0,0,0]}]}
```

示例中的零必须替换为计算结果，并为全部 6 个时刻各输出一行。不得调用 OpenFOAM、CFD 求解器或读取标准答案。

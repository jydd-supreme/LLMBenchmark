---
input_package: datasets/planar_poiseuille/planar_poiseuille_4
prediction_dir: predictions/planar_poiseuille/planar_poiseuille_4/{model_alias}
raw_response_path: results/planar_poiseuille/planar_poiseuille_4/{model_alias}/response.txt
---

# 问题 4

平板间流体的内部一开始近似以相同速度前进，但两侧固壁从开始就保持静止。这使壁面附近迅速产生速度梯度；在持续压力驱动和黏性作用下，跨缝速度分布由初始平顶形态向弯曲形态转变。

两块无限平行平板位于 `y=-1 m` 和 `y=1 m`。流体不可压缩且为牛顿流体，沿 `x` 方向充分发展；运动黏度为 `nu=0.1 m2/s`，沿 `x` 正方向的恒定压力驱动对应的加速度为 `G=0.2 m/s2`。初始和壁面条件为：

```text
u(-1,t) = u(1,t) = 0,
u(y,0) = 0.8,  -1<y<1.
```

初始内部速度为 `0.8 m/s`，两个壁面始终为零速度。长度单位为 `m`，时间单位为 `s`，速度单位为 `m/s`。请计算：

```text
y = [-0.9,-0.7,-0.5,-0.3,-0.1,0,0.1,0.3,0.5,0.7,0.9]
t = [0.05,0.1,0.5,1,2,5,10]
```

只返回一个合法 JSON 对象，不得输出推导、解释、Markdown 或额外字段。每个速度至少保留 8 位有效数字，`values` 顺序必须与 `y` 一致：

```json
{"case_id":"planar_poiseuille_4","y":[-0.9,-0.7,-0.5,-0.3,-0.1,0,0.1,0.3,0.5,0.7,0.9],"u":[{"time":0.05,"values":[0,0,0,0,0,0,0,0,0,0,0]}]}
```

示例中的零必须替换为计算结果，并为全部 7 个时刻各输出一行。不得调用 OpenFOAM、CFD 求解器或读取标准答案。

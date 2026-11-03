---
input_package: datasets/planar_poiseuille/planar_poiseuille_5
prediction_dir: predictions/planar_poiseuille/planar_poiseuille_5/{model_alias}
raw_response_path: results/planar_poiseuille/planar_poiseuille_5/{model_alias}/response.txt
---

# 问题 5

流体原先受正向压力驱动，在通道中形成前进流动；随后驱动改为反向。反向作用先使原有速度减小，再可能改变流向，而靠壁处与中心处的反转时刻不必相同。

两块无限平行平板位于 `y=-1 m` 和 `y=1 m`。在 `t=0` 前流体处于正向稳态；从 `t=0` 开始驱动力反转。流体不可压缩且为牛顿流体，运动黏度为 `nu=0.1 m2/s`；反转后的等效驱动加速度为 `G=-0.2 m/s2`。初始和壁面条件为：

```text
u(-1,t) = u(1,t) = 0,
u(y,0) = 1-y^2.
```

长度单位为 `m`，时间单位为 `s`，速度单位为 `m/s`；负速度表示流动已经反向。请计算：

```text
y = [-0.9,-0.7,-0.5,-0.3,-0.1,0,0.1,0.3,0.5,0.7,0.9]
t = [0.5,2,2.75,2.94,5,10,20]
```

只返回一个合法 JSON 对象，不得输出推导、解释、Markdown 或额外字段。每个速度至少保留 8 位有效数字，不得删除负号或对速度取绝对值。`values` 顺序必须与 `y` 一致：

```json
{"case_id":"planar_poiseuille_5","y":[-0.9,-0.7,-0.5,-0.3,-0.1,0,0.1,0.3,0.5,0.7,0.9],"u":[{"time":0.5,"values":[0,0,0,0,0,0,0,0,0,0,0]}]}
```

示例中的零必须替换为计算结果，并为全部 7 个时刻各输出一行。不得调用 OpenFOAM、CFD 求解器或读取标准答案。

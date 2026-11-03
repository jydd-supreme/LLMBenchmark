---
input_package: datasets/advection_diffusion/advection_diffusion_32
prediction_dir: predictions/advection_diffusion/advection_diffusion_32/{model_alias}
raw_response_path: results/advection_diffusion/advection_diffusion_32/{model_alias}/response.txt
---

# 问题 32

二维矩形区域为 0≤x≤5 m、0≤y≤3 m。左边界中部 1≤y≤2 m 为入口，右边界下部 0≤y≤1 m 为出口，顶部 y=3 m 为开放边界，其余边界为无滑移固壁。
顶部边界可同时出现流入和流出。入口带入示踪剂，示踪剂随流体对流并扩散；顶部流入的外部流体也可能携带示踪剂。本题没有化学反应、标量体源、体积阻塞或热浮力反馈。

随题提供网格生成配置、物性、求解配置，以及 `0/U、0/p、0/C、0/k、0/omega、0/nut`。请同时读取 `system/functions` 中的标量输运与探针设置。

- 不可压缩非稳态流动，保留原教程的 k–ω SST RAS 湍流模型；这里不是层流题。
- 运动黏度 ν=1×10⁻⁵ m²/s；初始速度为零，k=0.001 m²/s²，omega=1 s⁻¹。nut 在计算中由湍流模型更新。
- 入口速度为 (1,0,0) m/s，保持恒定。
- 无量纲被动浓度为 C，初始整个区域 C=0。入口浓度采用分段线性插值，时间表为 (0 s, 0)、(0.2 s, 1)、(0.6 s, 1)、(0.8 s, 0)、(2 s, 0)。
- 有效标量扩散系数为 D_eff=1×(ν+ν_t)，单位 m²/s；ν_t 为随时空变化的湍流黏度。完整系数见 `system/functions`。
- 顶部采用 inletOutlet 浓度边界：流入时 C=0，流出时零梯度；出口和固壁的浓度均为零梯度。
- 出口运动学压力 p=0；顶部为 p0=0 的 totalPressure 与 pressureInletOutletVelocity 组合。p 的单位为 m²/s²。
- 保留原教程的规则网格，共 6000 个二维单元。经 extrudeMesh 后 z 范围为 −2～−1 m，所有探针位于 z=−1.5 m。精确边界和离散格式以配置为准。
- 探针按所在单元取值（cell），只要求以下 5 个时刻的结果，不需要预测全场。

不得调用 OpenFOAM、CFD 求解器或外部数值工具，也不得读取标准答案。请预测 t=[0.4,0.8,1.2,1.6,2] s 时 `system/functions` 中全部 12 个 probeLocations 的 C。

只返回合法 JSON 对象：

```json
{"case_id":"advection_diffusion_32","points":[{"x":0,"y":0}],"scalar_by_time":[{"time":0.4,"values":[0]}]}
```

- points 必须按 probeLocations 顺序列出真实的 x、y 坐标，忽略 z。
- scalar_by_time 依次包含 0.4、0.8、1.2、1.6、2 s；每个 values 必须包含与探针一一对应的 12 个数。
- 数值输出尽量保留至少 8 位有效数字；这只是输出格式要求，不代表数值参考具有同等精度。

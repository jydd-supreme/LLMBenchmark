# LLMbenchmark

面向大模型的数学物理空间—时间推理评测基准。存在解析解的题目直接以解析答案评分；无解析解的题目使用离线生成的 OpenFOAM 参考结果。模型测试期间不得调用外部求解器或读取标准答案。

## 案例与编号

案例 ID 在每个物理类别内从 1 连续编号：

| 类别 | 案例 ID | 数量 | 参考答案 |
|---|---|---:|---|
| 一维及复杂构型传热 | `heat_conduction_1`–`heat_conduction_60` | 60 | 解析解 |
| 平面 Poiseuille 流 | `planar_poiseuille_1`–`planar_poiseuille_20` | 20 | 解析解 |
| 非线性导热 | `nonlinear_heat_1`–`nonlinear_heat_30` | 30 | OpenFOAM |
| 顶盖驱动方腔 | `lid_driven_cavity_1`–`lid_driven_cavity_20` | 20 | OpenFOAM |
| 对流扩散 | `advection_diffusion_1`–`advection_diffusion_40` | 40 | OpenFOAM |
| 可压缩流与激波 | `compressible_flow_1`–`compressible_flow_20` | 20 | OpenFOAM 13 `shockFluid` |
| 瞬态静电与空间电荷迁移 | `electromagnetics_1`–`electromagnetics_25` | 25 | OpenFOAM 13 `electrostaticFoam` |
| 化学反应（气泡塔、对向火焰、二氧化钛合成） | `chemical_reaction_1`–`chemical_reaction_30` | 30 | OpenFOAM 13 数值解 |
| 声学 | `acoustics_1`–`acoustics_20` | 20 | OpenFOAM 数值解 |
| 固体力学 | `solid_mechanics_1`–`solid_mechanics_20` | 20 | OpenFOAM 数值解 |

当前配置共 285 道题。

旧 ID 与新 ID 的完整对应关系见 `config/case_id_map.json`。

## 目录结构

所有运行时目录采用相同的两级结构：`<category>/<case_id>`。

```text
cases/<category>/<case_id>/
datasets/<category>/<case_id>/
predictions/<category>/<case_id>/<model_alias>/
results/<category>/<case_id>/<model_alias>/
```

例如 `nonlinear_heat_30`：

```text
cases/nonlinear_heat/nonlinear_heat_30/prompt.md
datasets/nonlinear_heat/nonlinear_heat_30/prompt.json
predictions/nonlinear_heat/nonlinear_heat_30/example_model/answer.json
results/nonlinear_heat/nonlinear_heat_30/example_model/response.txt
results/nonlinear_heat/nonlinear_heat_30/example_model/run.json
results/nonlinear_heat/nonlinear_heat_30/example_model/eval.json
```

数值参考案例位于：

```text
openfoam_cases/nonlinear_heat/nonlinear_heat_<n>/
openfoam_cases/lid_driven_cavity/lid_driven_cavity_<n>/
openfoam_cases/advection_diffusion/advection_diffusion_<n>/
openfoam_cases/compressible_flow/compressible_flow_<n>/
openfoam_cases/electromagnetics/electromagnetics_<n>/
openfoam_cases/chemical_reaction/chemical_reaction_<n>/
openfoam_cases/acoustics/acoustics_<n>/
openfoam_cases/solid_mechanics/solid_mechanics_<n>/
```

## 单题测试

先复制 `config/models/example.json`，填写自己的模型 ID、API 地址及环境变量名；随后加载本地 `.env` 并执行评测：

```bash
cd <your-local-LLMBenchmark-path>
set -a
source .env
set +a

python3 scripts/run_benchmark.py \
  --case nonlinear_heat_30 \
  --model-config config/models/example.json
```

解析题也可直接执行相同流程，不需要 OpenFOAM 输入目录：

```bash
python3 scripts/run_benchmark.py \
  --case heat_conduction_1 \
  --model-config config/models/example.json
```

只验证路径与提示词，不调用 API：

```bash
python3 scripts/benchmark_runner.py prepare --case lid_driven_cavity_1
python3 scripts/model_adapter.py \
  --case lid_driven_cavity_1 \
  --model-config config/models/example.json \
  --dry-run
```

只评测已有预测：

```bash
python3 scripts/benchmark_runner.py evaluate \
  --case nonlinear_heat_30 \
  --model-config config/models/example.json
```

## 路径来源

每道题的 `prompt.md` 文件头显式定义模型运行路径：

```yaml
---
input_package: datasets/nonlinear_heat/nonlinear_heat_30
prediction_dir: predictions/nonlinear_heat/nonlinear_heat_30/{model_alias}
raw_response_path: results/nonlinear_heat/nonlinear_heat_30/{model_alias}/response.txt
---
```

`run.json` 和 `eval.json` 自动写入 `raw_response_path` 所在目录。配置文件中的 `storage_path` 则用于 `benchmark_runner.py prepare/package` 生成分类后的数据集路径。

## 标准答案隔离

- `cases/.../reference_answer.json` 是评分用标准答案，不写入模型输入包。
- `datasets/.../prompt.json`、`inputs/` 和 `case_context/` 是模型可见内容。
- 非线性传热、方腔和对流扩散题只向模型提供配置允许的网格、物性、初始场与边界条件。
- 可压缩流题为单组分、无化学反应，评分量为 `rho/U/p/T/Ma`；逐题数值与物理检查见 `validation_report.json`。
- 电磁学题采用带电圆导线附近的瞬态静电场与空间电荷迁移模型；每题只评分电势 `phi`，标准答案使用加密网格，并逐题保存粗细网格敏感性结果。
- `chemical_reaction_1`–`chemical_reaction_10` 由 `bubbleColumnEvaporatingReacting` 改编，仅改变初始气液体积分数，评分气相体积分数 `alpha.gas`。
- `chemical_reaction_11`–`chemical_reaction_20` 由 `counterFlowFlame2D` 改编，仅改变初始内部温度，评分温度 `T`（K）。
- `chemical_reaction_21`–`chemical_reaction_30` 由 `titaniaSynthesis` 改编，仅改变初始两相温度，评分蒸气相温度 `T.vapour`（K）。
- 三组均保留原型的网格、反应机理、热物性、边界条件和求解控制；逐题结果与组内不变量审核见 `cases/chemical_reaction/SUITE_VALIDATION.json`。参考答案是数值解，而非解析或实验真值；尚未逐题证明网格与时间步收敛，评分应考虑数值容差。
- 模型输出统一写入 `predictions/`，API 原始响应、token 使用量和评分写入 `results/`。

## 主要脚本

- `scripts/run_benchmark.py`：执行 `prepare → model → evaluate`。
- `scripts/benchmark_runner.py`：数据打包、检查和评分。
- `scripts/model_adapter.py`：构建模型输入、调用 API、保存预测和运行信息。
- `scripts/prompt_metadata.py`：读取题目路径元数据，供打包与模型调用使用。

模型密钥只应写入 `.env` 或环境变量，不要写入模型配置 JSON。


本公开快照只包含 OpenFOAM 初始场、物性、网格和求解配置；完整时间步输出、求解日志、模型配置及评测结果保留在本地。参考答案见 `cases/<category>/<case_id>/reference_answer.json`。

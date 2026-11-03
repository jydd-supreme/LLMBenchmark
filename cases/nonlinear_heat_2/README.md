# nonlinear_heat_2：候选方程批判与温度外推

本目录包含 30 道题，与 `cases/nonlinear_heat/nonlinear_heat_1` 至 `_30` 一一对应。原题是未显式给出 PDE 的中性物理基线；本题组额外给出五个历史温度场和一个可能正确、也可能错误的候选方程。

- 输入历史：0、10、20、30、40 s 的完整 T 场；
- 预测目标：50、150、300、600、1000 s 的原探针温度；
- 6 道候选方程正确；
- 24 道候选方程错误，六类错误各 4 道；
- 所有未来温度标准答案都来自原来的正确 OpenFOAM 物理模型；错误方程只作为干扰信息；
- `suite_manifest.json` 和 `reference_answer.json` 是隐藏评分资料，不得提供给被测模型。

每题只向模型提供 `model_input/prompt.json`、`model_input/inputs/` 和 `model_input/case_context/`。`suite_manifest.json` 记录配对关系与标签，`validation_report.json` 记录历史场复算验证。

评分示例：

```bash
python3 evaluate_suite.py /path/to/predictions
```

预测目录应包含 `nonlinear_heat_1/answer.json` 至 `nonlinear_heat_30/answer.json`。

模型运行应使用每题的 `model_input/` 目录；其中只有 `prompt.json`、`inputs/` 和 `case_context/`。题目根目录的标准答案及隐藏元数据只供离线评分，不可整体作为模型输入。

使用现有适配器检查单题输入（不调用模型 API）：

```bash
cd <your-local-LLMBenchmark-path>
python3 scripts/model_adapter.py --dry-run \
  --config cases/nonlinear_heat_2/adapter_config.json \
  --case nonlinear_heat_2_1 \
  --model-config config/models/gpt6.json
```

实际运行模型时去掉 `--dry-run`，然后使用本目录的 `evaluate_suite.py` 对结果评分。此次仅提供题组本地配置，不改全局 `benchmark_config.json`。

适配器生成的答案位于 `predictions/nonlinear_heat_2/nonlinear_heat_2_N/{model_alias}/answer.json`。使用适配器结果评分时，从仓库根目录运行：

```bash
python3 cases/nonlinear_heat_2/evaluate_suite.py predictions/nonlinear_heat_2 --model-alias gpt6p1sol
```

这里的 `gpt6p1sol` 与所用模型配置中的 `model_alias` 保持一致。若自行准备答案，也可沿用上面的 `nonlinear_heat_N/answer.json` 简单目录结构。

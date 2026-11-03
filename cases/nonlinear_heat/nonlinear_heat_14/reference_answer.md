# 问题 14 OpenFOAM 数值参考

本题的 `k(T)=32-0.028T` 使瞬态控制方程成为非线性扩散方程，不采用闭式解析答案。

标准答案由 OpenFOAM 13 的 `foamRun -solver solid` 计算，材料使用内置 `polynomialSolid` 模型；参考案例位于：

```text
openfoam_cases/nonlinear_heat_14
```

运行与提取：

```bash
cd openfoam_cases/nonlinear_heat_14
./Allrun
./extract_reference.py
```

提交仓库中的 `reference_answer.json` 是由上述探针输出直接生成的基准值。

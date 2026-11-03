# 问题0解析参考

令稳态线性解为 `Ts=TL+(TR-TL)x/L`，将 `T-Ts` 作正弦 Fourier 展开；每个第 n 模态按 `exp[-alpha*(n*pi/L)^2*t]` 衰减。

标准答案：`python3 analytic_reference.py --case 0`

# REPORT.md

## Summary（进行中，完成后更新为 ≤5 行终版）

- 会话开始：2026-08-29（环境：Claude Code 远程容器，4 核，scipy/sympy/sklearn 已装）
- 注：原计划新建仓库存放本目录，但 GitHub 集成无创建仓库权限（403），保守选择放入
  `experiment` 仓库 `claude/understand-requirements-oz3ayh` 分支的 `overnight/` 子目录。
  整个目录自包含，之后可原样迁移到新仓库。

---

## 任务日志（倒序追加在此行之下）

### T6 真实 surrogate 的 η^path 测量 — PASS（实证测量）
- 做了什么：breast_cancer / wine / digits(前 20 特征)，f = 决策树 held-out accuracy，
  f̃ = 5-fold CV accuracy，greedy on f̃ 轨迹上测 η^path，30 次划分，K=1..7。
  openml airline satisfaction 因网络受限跳过（已记录）。
- 结果：η^path 很大且重尾（K=7 中位数 43 / 60 / 371），L_K(η^path) 下界 vacuous（0.023/0.017/0.003）；
  但实际 ratio(K=7) 中位数 0.963/0.941/0.957，630 行最差 0.718。诊断脚本确认 η 爆炸由
  accuracy 量化尺度的近零增益主导（argmax 对的 d̃ 或 d 中位数恰为 1 个量化单位）。
  方向一致性不成立：17%-32% 候选对 d 与 d̃ 反号；29%-53% 的对 d ≤ 0（f 不单调）。
- 对论文的含义：不能讲"实测 η 小"，应讲 raw multiplicative 误差对 ML surrogate 过于悲观，
  为 additive-multiplicative / trimmed 误差变体提供直接动机。
- 复现：`python3 results/T6_eta_path.py`（约 5 分钟）、`results/T6_argmax_diagnostic.py`。
  数据 `results/T6_eta_path.csv`，图 `figures/T6_*.png`，详见 `results/T6_summary.md`。

### T3 Reduced LP 对偶证书与 K=3(+K=4) 闭式 [VERIFIED-SYMBOLIC]（作为 reduced LP 值）— PASS
- 结果：定义 q=(K−1)η/((K−1)η+1)，V_j(η)=1−q^j(1−(K−j)/(Kη))，分段点为整数 η=2..K，
  则 reduced LP 值在段 [K−j,K−j+1] 上恰为 V_j。
  K=3：[1,2] (16η+3)/(3(2η+1)²)；[2,3] 7/(3(2η+1))；[3,∞) 1/η。
  K=4：[1,2] (135η²+36η+4)/(4(3η+1)³)；[2,3] (21η+2)/(2(3η+1)²)；[3,4] 13/(4(3η+1))；[4,∞) 1/η。
- 验证：K=2,3,4 全部 9 段构造显式 primal 解与对偶证书，sympy 精确算术 + Sturm 根计数
  整段验证（duality gap ≤1.1e−16）；K=2 恰好收回 R4；R5 全表 Fraction 精确重现；
  60 点拟合流程 held-out 残差 ≤3.3e−16。一般 K 猜想 min_j V_j 在 K=2..6×41 点 max 偏差 8.9e−16
  [CONJECTURE]。这把 "ρ_K=1/η iff η≥K"（R5 conjecture）在 K≤4 的 reduced-LP 层面变成定理。
- Caveat：闭式=ρ_K 还依赖 R6 的 reduced=全格点（K≤4 已验，一般 K 是 [HAND-PROOF-UNREVIEWED] 下界）。
- 复现：`python3 results/T3_duals.py`、`results/T3_K3_closed_form.py`；
  详见 `results/T3_K3_closed_form.md`、`results/T3_duals.json`、`figures/T3_K3_pieces.png`。

### T1 基线复现 [VERIFIED-LP] — PASS
- 做了什么：运行 `code/check_explicit_instance.py` 与 `code/worst_case_lp.py` 的 worst_case()
  （K=2 n=4、K=3 n=6，single-element 误差，η_u=η_o=√η，η ∈ {1,1.5,2,2.5,3,4}）。
- 结果：explicit instance 6 组参数 ALL PASS；12 个 LP 值与 RESEARCH_STATE.md R5 全部一致（<1e-7）。
- 复现：`python3 results/T1_baseline.py`，输出 `results/T1_baseline.txt`。
- 下一步：T2。

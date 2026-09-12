# M0 — J5 闸门（TASKS8，2026-09-12）

## 0. 输入状态

TASKS8 声明的四个 J5 文件（INDEPENDENT_THEORY_AUDIT_2026-09-12.md、VERIFICATION_SUMMARY.md、
verify_audit.py、submodular_K4_exact_duals.json）**均未送达**：仓库（含远端分支）、experiment
镜像、会话 uploads 目录（files_1.zip 解包核实为第一晚引导包）都查过。详见
results/J5/MISSING_INPUTS.md。后果：
- verify_audit.py 的"四个 PASS"**无法确认**。按用户规则"M0 未通过的项目不改正文"，凡**只以**
  该脚本为据的采纳一律不做。实际影响见下节逐项裁定。
- J5 手证原文不可转录；能本地重构或本地 oracle 闭合的项目照做，来源标注
  "本地重构，规格转述自 TASKS8"。

## 1. 本地脚本清单复跑（TASKS8 指定的九个，逐一 timeout 1500s）

| 脚本 | 退出码 |
|---|---|
| results/N1_dual_certificate.py | 0 |
| results/N2_check.py | 0 |
| results/T5_symbolic.py | 0 |
| results/H_J3_gate_check.py | 0 |
| results/H_B_asymptotic.py --quick | 0 |
| results/L1_table.py | 0 |
| results/J2_core_oracles.py | 0 |
| results/H3_j2_recheck.py | 0 |
| results/H_E_ceiling_small_n.py | 0 |

**9/9 exit 0**。日志在会话 scratchpad（m0_*.log）；脚本本身在 results/ 可随时复跑。

## 2. 三个反例的独立有理复算（results/M0_counterexamples.py，ALL PASS）

规格取自 TASKS8 内联描述（J5 章节号沿其转述）：

1. **J5 §3 停止版反例** [VERIFIED-EXHAUSTIVE，Fraction]：两元素 modular 实例上，
   提前停止版 greedy（无正预测增益即停）在"已执行步 a_t 全为 1"的 run 上输出 ratio 1/2，
   而 L_2(1) = 3/4；同一实例上固定 K 步版 ratio = 1。结论：**保证只能对固定 K 步语义陈述**
   （或对停止版只给已执行步的乘积界）。
2. **J5 §11 n=4, K=2, η=3/2 反例** [VERIFIED-LP，36 个分支 LP + Fraction]：
   "查询全部 6 个 pair、按 f̃ 取 argmax"的算法（6 次 size-2 查询 ≤ nK = 8，**属于 𝒜_lin**）
   精确最坏值 = 2/3 = 1/η，严格大于 ρ_2(3/2) = 3/5。结论：cor:greedybudget 相关的
   "not aware of any algorithm in 𝒜_lin exceeding ρ_K" 与 greedy 类内最优猜想**必须加 n 量词**
   （n ≥ 4K⁵ 或 inf over n）：小 n 处 C(n,K) ≤ nK 时穷举本身属于 𝒜_lin 且在 η < K 严格超过 ρ_K。
3. **J5 §10 N∖{e} 攻击（K=4, τ=1, n=12, η=2）** [VERIFIED-SYMBOLIC，Fraction]：
   显式 hardness 族上 G(N∖{e}) 在 e ∈ O（(x,y)=(8,3)）与 e ∉ O（(7,4)）两类的值差
   恰为 a⁹/3 = 3359232/40353607 ≈ 0.0832 > 0（a = 6/7）。结论：该构造族**不能去掉查询大小限制**
   （与第九晚 P1 在 K=3 的确认一致）。

## 3. 闸门裁定（逐 M 项）

- **通过（可改正文）**：M1.1（固定 K 步统一，§3 反例确认）、M1.2/M1.4/M1.5（量词与定义卫生，
  自明修正）、M1.3（ρ_{n,K}，论证本地重构）、M2 全部十项（措辞收缩只会变保守；M2.3 由 §11
  反例确认为必需，M2.5 由 §10 反例确认）、M3.4（η=1、K=1 情形，本地 sympy 检查）、M4。
- **改道（本地 oracle 替代缺失文件）**：M3.2（ρ^sub_{8,4} 的 16 轨道有理对偶 JSON 未送达，
  已派 Opus 代理本地重建双侧证书；重建成功才改 rem:exact-gap，否则只做方向性收缩）。
- **不做（依赖缺失原文）**：M3.1 的"J5 §9 证明写入附录"（原文缺失，主代理限时 45 分钟尝试
  本地重构，失败则 T8 保持 [CONJECTURE] 并记录）；M3.3 的"J5 人工复核：已闭合"台账注记
  （无法核实审计内容，写入即虚构来源）。

以上裁定与理由同步进 REPORT（M5）。

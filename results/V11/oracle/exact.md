# V11 Q4 oracle 报告：thm:exact（台账 T6，正文 Theorem 1：ρ_K = min_j V_j）

脚本：`results/V11/oracle/exact.py`（一键运行 `python3 results/V11/oracle/exact.py`，全部通过时 exit 0）
日志：`results/V11/oracle/exact.log`
机器可读：`results/V11/oracle/exact.json`
复跑产物副本：`results/V11/oracle/reruns/`
本次运行：15 个 check 全 PASS，0 个 violation，exit code 0，用时 189.5 秒。

陈述来源 `results/V11/inputs/statement_exact.md`；路线甲材料来自 `paper/sections/appendix_proofs.tex` 的
`app:exact`（第 582 行起：reduced LP 即 eq:redlp、对偶乘子 eq:duals-jpos / eq:duals-jzero、attaining instances）
与 `app:validity`（第 2149 行起：四族不等式的有效性）；对应脚本 `results/N1_dual_certificate.py`、
`results/N2_check.py`、`code/reduced_lp.py`、`results/T3_duals.py`；台账卡 `THEOREM_LEDGER.md` 的 `## T6`。

记号：k₁ = (K−1)η + 1，q = (K−1)η/k₁，V_j(η) = 1 − q^j(1 − (K−j)/(Kη))。

独立路线：本脚本自带一个精确有理两阶段 simplex（`fractions.Fraction`，Dantzig 规则加 Bland 兜底），
直接解 `code/reduced_lp.py` 的**完整** LP（变量序、行序逐行转写，不做对称化归约，不做任何缩减）。
求解器内部不出现 V_j；V_j 只在解出之后用来比对。所有判定用 `Fraction` 或 sympy，浮点只出现在打印文本、
C6 这一项以及被复跑的两个既有脚本内部。种子固定（D1 = 20260918）。未修改任何既有仓库文件。

---

## 1. 查了什么，结果如何

| 编号 | 内容 | 状态标签 | 精确计数 |
|---|---|---|---|
| C0a | sympy 恒等式：V_0 = 1/η；相邻 V_j 的递推 V_{j+1} − V_j = q^j[(1 − (K−j)/(Kη)) − q(1 − (K−j−1)/(Kη))]，K = 2..8 | [VERIFIED-SYMBOLIC] PASS | 35 条恒等式，residual 全为 0 |
| C0b | 段上取最小：对 K = 2..8、每个 j、每个 i ≠ j，把 V_i − V_j 化成有理式后对分子做**精确实根隔离**（先除掉端点根 (η−lo)、(hi−η)，再用 `sp.count_roots` 确认段内无根，并在段中点取正号），于是 min_i V_i 在 [K−j, K−j+1] 上由 V_j 取到，分段点就是整数 2..K | [VERIFIED-SYMBOLIC] PASS | 168 个有序对 (i, j)，段内零根，全部符号为正 |
| C0c | ρ_K = 1/η 当且仅当 η ≥ K：η ≥ K 时 min_j V_j 精确等于 1/η，η < K 时严格小于 1/η | [VERIFIED-SYMBOLIC] PASS | 49 个精确点（K = 2..8 × 7 个 η，含 K−1/100、K、K+1/100） |
| C1 | 自写精确有理 simplex 解 `code/reduced_lp.py` 的完整 LP：K = 2..6，每个 K 取 20 个有理 η（含 η = 1、整数 2..K、η = K、K 以上的值 K+1/2、K+1、K+3/2、2K、2K+1/3、3K，以及每个段 [m, m+1] 的中点 m+1/2，其余用段内有理数补足），每个最优值与 min_j V_j 做 `Fraction` 相等判定 | [VERIFIED-LP]（精确有理） PASS | 100 个 LP，100/100 精确相等；最大 simplex 迭代数 186 |
| C2 | 每个最优点上的精确 primal-dual certificate，只对着 LP 数据本身核：primal x ≥ 0 且逐行满足 Ax ≤ b、c′x = min_j V_j；乘子 λ ≥ 0 且 A′λ + c ≥ 0、−b′λ = c′x。弱对偶因此把最优值钉死，不依赖求解器本身 | [VERIFIED-LP]（精确有理） PASS | 100 个证书，100/100 通过 |
| C3 | 陈述里印出的 K = 2, 3, 4 闭式：每段先用 sympy 对 V_j 做恒等式核对（residual 0），再把该段上的 20 个 η 的 LP 精确值与闭式代入值做 `Fraction` 相等判定 | [VERIFIED-SYMBOLIC + VERIFIED-LP] PASS | 9 个分段恒等式 + 60 个精确数值点 |
| C4 | 复跑 `results/N1_dual_certificate.py`（一般 K 的对偶证书，sympy） | [VERIFIED-SYMBOLIC] PASS | exit code 0，50.8 秒，`320/320 checks passed`，`OVERALL: PASS`，产物按字节还原 |
| C5 | 复跑 `results/N2_check.py`（每个 j 的 attaining instances，精确有理） | [VERIFIED-SYMBOLIC] PASS | exit code 0，16.0 秒，`TOTAL 480/480 PASS`，产物按字节还原 |
| C6 | 与 `code/reduced_lp.reduced` 的 scipy / HiGHS 浮点解交叉比对 | [VERIFIED-LP 浮点] PASS | 100 个点，最大 \|exact − float\| = 3.33e−16 |
| C7 | 路线甲的归约步（app:validity）在随机实例上的检查：D1 的每条 run 诱导的向量 (d_t, g_{t,i})（以 OPT 归一，O\* 取一个大小恰为 K 的最大化集）逐条满足 eq:redlp 的四族不等式 sum(t)、pred(t,i)、mono(t,i)、cons(t,i) | [VERIFIED-EXHAUSTIVE] PASS | 174,548 次约束检查，覆盖 6,878 条 run，0 条违反，最小 slack 为 0（出现在 pred(0,0)，即取等） |
| D1 | 2,400 个随机精确实例的反例搜索（见第 2 节） | [VERIFIED-EXHAUSTIVE] PASS | 2,400 实例 / 6,878 条 tie 全枚举 run / 4,419 次抽样被拒 / 0 violation |
| D2 | Figure 1 结构化实例（见第 3 节） | [VERIFIED-EXHAUSTIVE] PASS | 4 项（f 单调 submodular、OPT、surrogate A、surrogate B）全 PASS |

---

## 2. Criterion D：对陈述本身的反例搜索

随机实例的生成（种子 20260918）：

- f 的族：modular、coverage、coverage + modular 混合、两个 coverage 相加；权重是小分母有理数。
  每个抽样出来的 f 都在整个格点上精确验过单调与 submodular（不通过就丢弃并计入拒绝数）。
- n 在 [max(K,3), 7] 内随机，K 在 {2, 3} 内交替。
- surrogate f̃ 的三种模式：`scale`（f̃ = c·f，η = 1）、`perturb`（逐集合乘性扰动）、`indep`（独立再抽一个
  单调 submodular 函数当 f̃）。抽完之后**回头算实际的最小合法因子** η_u = max d/d̃、η_o = max d̃/d，
  η = η_u·η_o；若某处 d > 0 而 d̃ ≤ 0，或 d = 0 而 d̃ ≠ 0，则该 f̃ 不合法，丢弃。
- predictive greedy 跑满 K 步，**每一步的 tie 全部枚举**（分叉搜索），取所有 run 里 f 值最小的那条结算，
  即对抗 tie。判据：f(T)/OPT ≥ ρ_K(该实例的实际 η)，其中 ρ_K 由 min_j V_j 在该 η 上取值。

结果：2,400 个实例（K = 2 和 K = 3 各 1,200），6,878 条 run，**0 个 violation**。
最小 slack（最紧的一格）是 269/3168 ≈ 0.0849，出现在 K = 2、n = 4、modular、η = 288/17 ≈ 16.94，
ratio = 19/132 ≈ 0.1439，ρ_2 = 17/288 ≈ 0.0590。
把范围限到 η ≤ 2，最小 slack 是 35/316 ≈ 0.1108，出现在 K = 2、n = 4、η = 1，ratio = 68/79 ≈ 0.8608，
ρ_2(1) = 3/4。随机实例里没有取等的（D1_equality_instances = 0）；取等要靠 N2 的构造实例，见 C5。

---

## 3. Figure 1 结构化实例（HANDOFF_2026-09-18.md §7）

全部用有理数重算。N = {a, b, c}，K = 2，真值 f = (5, 9/2, 24/5, 19/2, 15/2, 7, 97/10)。

- f 单调 submodular，8 个集合全格点验过；OPT = f({a,b}) = 19/2。
- surrogate A = (9/2, 22/5, 132/25, 9, 69/10, 38/5, 46/5)：实际全局 η = 54/25 = 2.16（= η_u 27/16 × η_o 32/25，
  handoff 记的"约 2.16"对上）；greedy 唯一走出 {b, c}（无 tie，1 条 run）；ratio = 14/19 ≈ 0.7368（即 7/9.5，
  handoff 的 0.74）；ρ_2(54/25) = 25/54 ≈ 0.4630，ratio − ρ_2 = 281/1026 > 0；η^sel = 27/22 ≈ 1.2273（handoff 的 1.23）。
- surrogate B = (13/2, 16/5, 39/10, 247/20, 83/10, 26/5, 63/5)：实际全局 η = 1628/351 ≈ 4.6382（= 22/13 × 74/27，
  handoff 记的"约 4.6"对上）；greedy 唯一走出 {a, b}；ratio = 1；ρ_2(1628/351) = 351/1628 ≈ 0.2156，
  ratio − ρ_2 = 1277/1628 > 0；η^sel = 1（handoff 的 1.00）。
- 两条 ratio 都 ≥ 各自 η 处的 ρ_2，与定理一致；同时确认 B 的全局 η 比 A 大（4.64 > 2.16），
  与 §12 "图 1 不标 η、不能说边际误差小的赢" 的禁令一致。

---

## 4. Running example（K = 3, η = 3/2）

k₁ = 4，q = 3/4，(V_0, V_1, V_2) = (2/3, 7/12, 9/16)，argmin j = 2，η = 3/2 落在段 [K−j, K−j+1] = [1, 2]。
自写精确 simplex 在完整 reduced LP 上的最优值 = 9/16 = 0.5625 = min_j V_j，primal-dual certificate 通过。
陈述里 K = 3 在 [1,2] 上的闭式 (16η+3)/(3(2η+1)²) 代入得 27/48 = 9/16，三者精确一致。

---

## 5. FAILED 项

无。15 个 check 全 PASS，`violations` 为 0，exit code 0。

---

## 6. 本次 oracle 的范围与未覆盖处

- 本脚本独立确立的是：**reduced LP 的最优值精确等于 min_j V_j**，在 K = 2..6 × 20 个有理 η 共 100 个格点上
  用自写精确有理 simplex 加 primal-dual certificate 逐点确认；加上 C0b 的段上极小性与分段点（K = 2..8 符号）。
  一般 K、一般 η 的符号对偶证书是 N1（C4 复跑，320/320），不是本脚本重新推导的。
- 从 LP 最优值到 ρ_K 还要两步。(i) 归约方向（每条真实 run 诱导的向量落在 LP 可行域内，故 ρ_K ≥ LP 最优值）：
  本脚本用 C7 在 2,400 个随机实例的 6,878 条 run 上逐条核了四族不等式（174,548 次检查，0 违反），
  但 app:validity 里对一般实例的推导本身没有在这里重新做，仍以仓库既有的 R6 / J2 slack 证书为准。
  (ii) 可达方向（存在实例把 min_j V_j 取到，故 ρ_K ≤ min_j V_j）：由 C5 复跑的 N2（480/480）覆盖，
  本脚本没有独立重建那族实例。
- 因此 T6 的等号在本次 oracle 下的状态是：LP 侧 [VERIFIED-LP]（精确有理，本脚本）+ [VERIFIED-SYMBOLIC]（N1 复跑），
  可达侧 [VERIFIED-SYMBOLIC]（N2 复跑），归约侧在随机实例上 [VERIFIED-EXHAUSTIVE]，其一般性论证仍按台账保持原标签。
- C6 走 scipy / HiGHS 浮点，只作参照，标 [VERIFIED-LP 浮点]；本脚本自身的每个判定都是精确的。
- 复跑说明：N1 与 N2 会在 `results/` 下原地覆写自己的 JSON 产物，所以复跑前先存字节、复跑后把新产物拷进
  `results/V11/oracle/reruns/`、再把原文件写回并核对 sha256，三个 N2 产物与 N1 产物均按字节还原（json 的
  `reruns` 段记录了 before / after / restored）。N2 的三个产物两次运行按字节相同；N1 的 JSON 两次运行只差
  记录的耗时字段（`runtime_s` 与 17 条 part E 检查里的秒数），320 项检查内容完全一致。
  开发阶段曾先探跑过这两个脚本一次以估时，那一次在快照协议之前，已经把它们自己的 JSON 产物重写过一遍；
  脚本文件本身未改动，产物内容除耗时字段外与之前一致。

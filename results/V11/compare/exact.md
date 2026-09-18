# ROUTE-COMPARISON：thm:exact（ledger T6，正文 Theorem 1：rho_K = min_j V_j）

TASKS11 Q4，criterion B。本文件只做比对，不修改任何既有文件，未运行 git。

- **路线一（repo proof）**：`paper/sections/appendix_proofs.tex` 的
  `\subsection{The exact worst case}\label{app:exact}`（第 582 行起）与
  `\subsection{Validity of the reduced constraints}\label{app:validity}`（第 2149 行起），
  另用到 `\label{app:coherence}`（第 524 行，`lem:coherence`）。
  陈述与 n 量词在 `paper/sections/results.tex` 第 191 行（`thm:exact`）与第 208 行（`rem:exact-n`）。
  台账卡 `THEOREM_LEDGER.md` 的 `## T6`（副产品与禁止声称）与 `## T6b`（`prop:rigidity`）。
  依赖脚本：`results/N1_dual_certificate.py`、`results/N2_check.py`、`code/reduced_lp.py`、
  `results/T3_duals.py`、`results/T3_K3_closed_form.py`、`results/N3_K5_lattice.py`、
  `results/H3_j2_recheck.py`、`results/J2_core_oracles.py`。
- **路线二（blind derivation）**：`results/V11/route2/exact.md`，oracle 脚本
  `results/V11/route2/dual_certificate.py`、`symbolic_instance_identities.py`、
  `verify_instance_exact.py`、`lp_full_instance.py`。
- **本轮独立复算脚本**：`results/V11/compare/judge_exact_checks.py`（本文件新写，不 import 两条
  路线的任何脚本，全部对象按各自 write-up 重新实现；sympy 符号 + `fractions.Fraction`，
  float 只出现在最后一个 cross-check 打印块）。复算结果：

  | 块 | 内容 | 规模 | 结果 | 标签 |
  |---|---|---|---|---|
  | B1 | 路线二 dual (D) 可行性 + 目标值 `= V_j` | `K=2..7`，全部 `j`，符号 `eta` 限于各自 segment | 749 检查 0 失败 | [VERIFIED-SYMBOLIC] |
  | B2 | 路线一 `eq:duals-jpos/jzero` 的加权和恒等式 + 乘子非负 | `K=2..7`，全部 `j`，符号 `eta` | 525 检查 0 失败 | [VERIFIED-SYMBOLIC] |
  | B3 | 段结构（`V_i-V_{i+1}` 闭式、`c_j` 单峰、`V_K>=V_{K-1}`）与 `K=2,3,4` 闭式 | `K=2..8` | 76 检查 0 失败 | [VERIFIED-SYMBOLIC] |
  | B4 | 路线二 attaining instance 逐 `S` 逐 `e` 穷举 | `K=2,3,4`（12 个 `eta`）+ `K=5`（8 个 `eta`），含 29 个 `eta<K-j` 的格 | 131 例 0 失败 | [VERIFIED-EXHAUSTIVE] |
  | B5 | 路线一 `eq:vj-family` 逐 `S` 逐 `e` 穷举（split 取 `(eta,1)`） | `K=2,3,4` | 段内 44 例 0 失败；段外 19 例 19 失败（`mono`/`band`） | [VERIFIED-EXHAUSTIVE] |
  | B6 | 路线二给出的 trajectory 点对 (P) 的精确有理可行性与目标值 `=V_j` | `K=2..8`，全部 `j`，9 个 `eta` | 315 例 0 失败 | [VERIFIED-EXHAUSTIVE] |
  | B7 | LP 变体对照：`sum+pred+mono` vs `sum+cons+mono` vs 四族全上 | `K=2..5`，5 个 `eta`（HiGHS 浮点） | 三列分别等于 `L_K`、`rho_K`、`rho_K` | [VERIFIED-LP，旁证] |

---

## 1. Step 对应表

"路线一位置" 指 `app:exact` 的 paragraph 名、`app:validity` 的 lemma 名，或 `results.tex` 的
定理/remark。

| 路线二的步骤 | 路线一的对应位置 | 判定 |
|---|---|---|
| Step 1 归一化 `F_OPT=1`；用 `ftilde -> ftilde/eta_o` 把 band 归到 `(eta_u,eta_o)=(eta,1)` | `app:exact` 开头 "Throughout this subsection `K>=2`, `eta>=1`, `f(O*)=1`"；`definition1.md` 的 scaling 说明 | 对应，但取法不同：路线一全程保留一般 split（上界方向明写 "fix any split `eta_u eta_o = eta`"，脚本用 `sqrt(eta)`），路线二把 split 固定成 `(eta,1)`。两者在 verbatim Definition 1（`eta_u,eta_o>=1`）下都合法，见第 3 节 D3 |
| Step 2 Lemma A `M_t <= eta g_t`，并指出单用它只能到 `L_K(eta)` | `app:validity` 的 `lem:app-pred`（`pred(t,i)`，case (a)(b)(c)）；`L_K` 的部分是 `app:guarantee`（`prop:guarantee`），不在 `app:exact` 内 | 对应，逐字同构（路线二的链 `d_x <= eta_u dtilde_x <= eta_u dtilde_{e_t} <= eta g_t` 与 `lem:app-pred` case (b) 的链同序）。路线二额外给出 `L_3(2)=91/216 < 7/15` 的数值间隙说明，路线一未在此处给 |
| Step 3 Lemma B：`dtilde_o(S+e) <= dtilde_e(S+o)`，两侧套 band 得 `d_o(S+e) <= eta d_e(S+o)`，代入 `f` 的交换恒等式得 `m_{o,t} <= g_t + (1-1/eta) m_{o,t+1}` | `app:coherence` 的 exchange identity 与 Part (i)(ii)（`lem:coherence`），加 `app:validity` 的 `lem:app-cons`（`cons(t,i)`） | 对应，且是逐字同构：路线二的 (3) 就是 `lem:coherence` (i)（取 `e=e_t`、`e'=o`），(4) 就是 `cons(t,i)`。路线一在 `lem:app-cons` case (b) 把它写成三个非负项之和（J2 slack 分解），路线二写成两次 band 夹逼；等价 |
| Step 3 的边界情形（`o=e_t` 取等；`o in S^t` 两端为 0） | `lem:app-cons` case (c) 与 case (a)（zeroing convention） | 对应。路线一另把该 case 记为 "closes the gap this subsection exists to close"（R6 缺口），路线二未知此历史但覆盖了同样两个 case |
| Step 4 覆盖不等式 `1 <= f(S^t) + sum_i m_{i,t}` | `app:validity` 的 `lem:app-sum`（`sum(t)`） | 对应，逐字同构（同样的 telescoping 加逐项 submodularity 加 `f(S^t ∪ O*) >= f(O*)`） |
| Step 5 LP relaxation (P)：`(A_t)(B_t)(C_t)`，规模只依赖 `K`，`rho_K >= val(P)` 对一切 `n>=K` | `app:exact` 的 "The reduced linear program" 段（`eq:redlp` 的四族 `sum/pred/mono/cons`）加 `lem:app-relaxation` | **约束集不同**：路线二的 (P) 只有 `sum`、`cons`（聚合）与 `mono`（聚合），**不含 `pred`**；路线一的 `eq:redlp` 四族齐全且逐 `i` 不聚合。两者的 LP 最优值一致（B7 浮点旁证；B1+B6 给出精确证明：dual 给 `>=V_j`、trajectory 点给 `<=V_j`）。详见第 3 节 D1 |
| Step 6 聚合 `P_t=sum_i m_{i,t}`，并说明回代 `m_{i,t}=P_t/K` 不丢信息 | 路线一不聚合，只说 "the same for every index `i` by the symmetry of `eq:redlp` in `i`"（乘子对称） | 不同写法，同一内容。路线一在对偶侧用对称性，路线二在原始侧先聚合；本轮复算两侧都成立 |
| Step 7 dual 乘子 `z,w,y` 闭式（由 complementary slackness 反解），两个非负性给 segment 两端点 | `app:exact` 的 `eq:duals-jpos`/`eq:duals-jzero` 与其后的 "Nonnegativity" 段 | **不同证书**：路线一的支撑是 `sum + pred + cons`（`lambda_mono` 恒为 0），路线二的支撑是 `sum + cons + mono`（`pred` 完全不用）。两套乘子都独立复核通过（B1、B2）。端点机制一致：路线一 `lambda_S(j)>=0 <=> eta<=K-j+1`、`lambda_P(j)>=0 <=> eta>=K-j`；路线二 `y_j>=0 <=> eta<=K-j+1`、`w_j>=0 <=> eta>=K-j` |
| Step 8 dual 目标值 `sum_t y_t = V_j`，weak duality 给 `rho_K >= V_j` | `app:exact` 的 "(c) The constant equals `-V_j`" 与 "Conclusion of the lower bound" | 对应，同一结论。路线一把它写成加权和恒等式 `Sigma = sum_t d_t - V_j`（(a)(b)(c) 三族系数逐项核对），路线二用 `(Dg_0)` 取等加几何和；两条算路都通过本轮复算 |
| Step 9 段结构：`c_{j+1}>=c_j <=> eta<=K-j`，`j*=ceil(K-eta)` 截断，断点整数 `2..K`，`rho_K=1/eta` 当且仅当 `eta>=K` | `app:exact` 的 "Which `V_j` is smallest" 段（`V_i-V_{i+1}=q^i(K-i-eta)/(K eta k_1)`） | 对应，两式互为等价形（`V_i-V_{i+1}=c_{i+1}-c_i`），B3 逐式核对一致 |
| Step 9 的附注 `V_K-V_{K-1}=q^{K-1}(1/k_1-1/(K eta))>=0`，故加入 `j=K` 不改变 min | 路线一**不用** `V_K`；台账 T6 的禁止声称写 "`V_i-V_{i+1}` 索引 `i<=K-2`"（K6 修正），同一事实以 `U_K > V_{K-1}`（`app:tightness` 与 T6 副产品）出现 | 不同记法，同一事实：`V_K=1-q^K=U_K`，`eta>1` 时严格。路线二**没有违反**禁止声称（它没有对 `i=K-1` 用相邻差公式，而是单独算 `V_K-V_{K-1}`），但入稿时仍应保持路线一的记法 |
| Step 10 下界合并 `rho_K >= min_j V_j`，对一切 `n>=K` | `app:exact` 的 "Conclusion of the lower bound" 加 `lem:app-relaxation` | 对应 |
| Step 11 attaining `f`：`n=2K` 的 coverage function，atom 表 `a(i,s)=g_s/K`、`a(i,inf)=R_j/K`、`tau_t` | `app:exact` 的 `eq:vj-family` 中的 `f(S)=1-q^x(1-y/K)+z delta_j chi(y)`（`(x,z,y)` 的 counting function，`lem:app-count`） | **不同构造**：路线一是三块 counting function，head 元素彼此对称、monotone submodular 要靠九个二阶差分逐项核对且**需要 `eta>=K-j`**；路线二是 coverage function，head 元素 `e_s` 的测度 `g_s` 逐步递减、monotone submodular 自动成立且**不需要段条件**。B4/B5 复核：路线二的族在 29 个 `eta<K-j` 的格点仍然全部合法，路线一的 capped 族在同样的段外 19 个格点全部丢 monotonicity。见第 3 节 D2 |
| Step 12 attaining predictor `ftilde = f - (1-1/eta) max_i mu(A_{o_i} cap C(S))`，band 由 max 的次可加性得证 | `app:exact` 的 `eq:vj-family` 中的 `ftilde(S)=W(0)-q^x W(y)+z eta_o delta_j chi(y)` 与 "The error is exactly `(eta_u,eta_o)`" 段 | **不同构造**，同一效果。路线一逐比值列出三个取值并排序，声明误差恰为 `(eta_u,eta_o)`；路线二只证 band 成立（`0<=Delta beta<=d`），未声明"误差恰好等于"，但其构造实际两侧都取到（tail 步 `dtilde=d`，`o_i` 处 `dtilde=d/eta`），本轮 B4 顺带确认 |
| Step 13 `F_OPT=1`（任一 `K`-set `<= r/K+(1-r/K)[(1-R_j)+R_j/eta] <= 1`） | `app:exact` 的 "The optimum" 段（`z delta_j <= q^x (K-y)/K`） | 对应，两条不等式链结构相同（都用 `eta>=1` 与 tail 份额不超过未选 `o` 的份额）。路线一在此处**再次**用到 `z<=K-j<=eta`，路线二不需要 |
| Step 14 greedy 轨迹与 full tie（恒等式 `K+(eta-1)(K-1)=k_1`） | `app:exact` 的 "The per-step gain table" 与 "The greedy induction" 段（以及 `eq:W0-identity`） | 对应：两条路线的每一步都是 `e_t` 与全部 `o_i` 打平、未选的同类候选严格更小，adversary 取 `e_t`。所用的代数恒等式同一条（路线一记作 `W(0)-(K-1)eta_o/K=1/(K eta_u)`，路线二记作 `K+(eta-1)(K-1)=k_1`） |
| Step 15 `F_ALG=(1-R_j)+(K-j)R_j/(K eta)=V_j` | `app:exact` 的 `f(S^K)=1-q^j+(K-j)delta_j=V_j` display | 对应，逐字同构 |
| Step 16 合并 + `K=2,3,4` 闭式 + 以 `(f,ftilde)` 为变量的完整实例 LP 旁证（22 格点，浮点） | `app:exact` 末段与 `results.tex` 的定理闭式；旁证对应 `rem:app-status` 的 "agreement of `eq:redlp` with the full-lattice program has been checked for `K<=5` and at nineteen `(K,eta)` test points"（脚本 `results/N3_K5_lattice.py`） | 对应。闭式在 B3 中逐条核对与陈述一致；两条路线的 full-lattice 旁证都是浮点，都不作决定性依据 |
| §3 `K=3, eta=3/2` 数值走查（profile 表、实例 atom 表、dual 证书 `z=(7/32,7/24,1/3)`、`w=(0,0,1/9)`、`y=(7/32,7/32,1/8)`、`sum y=9/16`） | 路线一无逐格走查；最接近的是 `results/T3_K3_closed_form.py` 与台账 T6b 的 `K=3, eta=2` 两条轨迹例 | 路线二独有。本轮逐个有理数复算，全部一致 [VERIFIED-SYMBOLIC] |
| §5 空洞性检验（adversarial tie、恰好 `K` 步、single-element band 用在非轨迹状态、`f` 的 monotone submodular、`ftilde` 无结构假设、deterministic） | `app:exact` 的 "The role of the ties" 段、`app:validity` 的 `rem:app-rulers`（哪族容得下 `etasel`/`etatr`）与 `rem:app-census`（哪族消耗哪条假设） | 对应且覆盖面相当。路线二的 "single-element 用在 `(S^t ∪ {o}, e_t)` 这个非轨迹状态" 与 `rem:app-rulers` 对 `cons` 的结论逐字一致 |
| §5 的 [FAILED] 记录：把 `ftilde` 限制成 density 形式（`mu/eta <= mutilde <= mu`）在 `j>=2` 不可行 | 路线一无对应条目；最接近的是 T7/`rem:exact-gap`（submodular surrogate 下的 `rho^sub`）与 `results/N2_check.py` Part G（"ftilde 单调但不 submodular"） | 路线二独有。本轮未复算该 [FAILED]（time-box），保留其自标状态 |

### 路线一中路线二未覆盖的内容

| 路线一的步骤 | 路线二的状态 |
|---|---|
| `rem:exact-n`（`results.tex` 第 208 行）：`rho_{n,K}=rho_{2K,K}` 对**每个固定** `n>=2K`，由 restriction（限制到 `T ∪ O*`）+ padding（补零元素）给出，台账 T6 的 M1 条目记 [HAND-PROOF-UNREVIEWED] | **未覆盖**。路线二把 `rho_K` 读作 `inf_{n>=K} rho_{n,K}`（它自己在 §5 第 4 条标为"追加的读法假设"），只给 "下界对一切 `n>=K` + 上界在 `n=2K` 取到"，没有 restriction/padding 论证，因此对固定 `n>2K` 的 `rho_{n,K}` 无结论。这是本轮唯一的量词差异，见第 2 节 |
| `app:validity` 的 `|O*|<K` 记账（"if `|O*|<K`, set `g_{t,i}=0` for the unused indices"） | **未覆盖**。路线二按 `assumptions.md` 取 `O*={o_1..o_K}` 为一个最优 `K`-set，未讨论最优集更小的情形（monotone `f` 下可补齐，路线二未写这一句） |
| `app:exact` 的 "The error is exactly `(eta_u,eta_o)`"：实例的误差不只被 `eta` 界住，而是恰好坐在 band 两侧 | **未明写**（其构造实际满足，B4 顺带确认）。写作时若要保留 "not merely bounded by `eta`" 这句，仍以路线一为准 |
| `app:exact` 的 "The role of the ties" 后半：严格偏好下的极限变体（`eta'<eta` 放进 `f`，比值 `V_j(eta') -> V_j(eta)`），以及 K6 caveat（段左端点的有理反例 `K=3, j=1, eta=2, eta'=19/10`，一个后期 `O` 增益变成 `-1/72`） | **未覆盖**。路线二只给 "tie 偏向 `O*` 则同一实例比值变 1"（本轮独立确认成立），没有严格偏好的极限版本 |
| `app:exact` 的 Roadmap 段与 `app:rigidity`（`prop:rigidity`，台账 T6b）：最坏轨迹的刚性、断点读作 active-constraint switch | **未覆盖**（不在被证陈述内） |
| 台账 T6 副产品 "下界证书中单调约束乘子恒为零" | **路线二不具备**：它的证书恰恰用 `mono`（`w_t>0`，`t>=j`）而不用 `pred`。两条证书都可行、目标值同为 `V_j`（B1、B2），说明该 LP 的对偶最优面不唯一；这条副产品仍只对路线一的证书成立 |
| `app:validity` 的 `rem:app-status`：反向（每个可行点都可实现）**不声称** | 路线二 §5 第 3 条有同样的自我限制，措辞一致 |
| 路线一的 oracle 覆盖面：`N1` 对 `(K,j,t,i)` 一般符号（modulo 一次有限分支枚举）加 `K=2..10` 暴力；`N2` 480/480 加 `K<=6` 全格点 | 路线二的 oracle 只做到 `K=2..7`（dual，逐 `K` 符号）与 `K<=5`（实例穷举）。本轮复算与路线二同量级，未能把一般 `K` 闭合 |

---

## 2. 量词比对

被证陈述（`results/V11/inputs/statement_exact.md`，与 `results.tex` 第 191 行逐字一致）本身只带
`K>=2`、`eta>=1`、adversarial tie 三个量词，`n` 不在陈述里。

| 量词 | 路线一 | 路线二 | 是否一致 |
|---|---|---|---|
| `K` | `K>=2` 整数全称（`app:exact` 首行） | `K>=2` 整数全称，并补一句 `K=1` 时公式仍给 `1/eta`、只是断点集合为空 | 一致（路线二的 `K=1` 注与 HANDOFF §3 "at `K=1` every bound equals `1/eta`" 同向） |
| `eta` | `eta>=1` 全称；`eta=1` 允许（`app:exact` 的 `j=K-1` 段按连续性处理 `eta->1`） | `eta in [1,infty)` 全称；`eta=1` 单列（`theta=0`），`eta=infty` 明确排除 | 一致 |
| `f` | 一切 monotone submodular、`f(empty)=0`；`f(O*)=1` 归一化 | 同；并补 `F_OPT=0` 按 `assumptions.md` 平凡 | 一致 |
| `ftilde` | 一切满足 Definition 1 的集合函数，band 在全部 `(S,e)` 上；不要求 submodular（`rem:app-census`、`N2_check.py` Part G） | 同，并显式写出 "全部 `2^n·n` 个 `(S,e)`"、"不要求 submodular" | 一致 |
| 算法与 tie | predictive greedy，恰好 `K` 步，adversarial tie | 同，且逐条做空洞性检验 | 一致 |
| `j` | `0<=j<=K-1`；禁止用 `V_K`（台账 T6） | `0<=j<=K-1`，另证加入 `j=K` 不改变 min | 实质一致（记法差别，见第 1 节表） |
| `n` | `rem:exact-n`：`rho_{n,K}=rho_{2K,K}` 对**每个** `n>=2K`，`rho_K` 记这个公共值 | `rho_K := inf_{n>=K} rho_{n,K}`（自标为追加的读法假设）；下界对一切 `n>=K`，上界在 `n=2K` 取到 | **不一致**。路线一有"对每个固定 `n>=2K` 取同值"这条全称量词，路线二没有（它只给 inf） |

结论：`quantifier_match = false`，唯一的差异项是 `n`。两条路线在 `n=2K` 上的取值一致，且路线二的 inf
读法与路线一的公共值在 `n>=2K` 上相同，所以差异是覆盖面差异，不是矛盾。

---

## 3. 分歧清单（divergences）

- **D1（LP 约束集与对偶支撑）**。路线一的 `eq:redlp` 有四族 `sum/pred/mono/cons` 且逐 `i`，其证书支撑是
  `sum+pred+cons`，`lambda_mono` 恒为 0；路线二的 (P) 只有 `sum+cons+mono` 的聚合版，其证书支撑是
  `sum+cons+mono`，完全不用 `pred`。两套乘子本轮都独立符号复核通过（B1 749 检查、B2 525 检查，各 0 失败），
  LP 值一致（B7 浮点：`sum+pred+mono` 给 `L_K`，`sum+cons+mono` 与四族全上都给 `rho_K`）。
  含义：`cons` 一族足以决定精确值，`pred` 在 `cons` 面前是冗余的（`cons` 加 submodularity 蕴含 `pred`，
  路线二 Step 3 末尾明写）。台账 T6 的副产品句（"单调约束乘子恒为零"）只对路线一的证书成立。
- **D2（attaining 族）**。路线一 `eq:vj-family` 是 counting function，capped 变体 `chi(y)=[y<K]` 只在
  `eta>=K-j` 上 monotone submodular，路线一并据此写 "This is the only place where the segment
  condition is consumed, and it is where the breakpoints come from"；路线二是 coverage function，
  对一切 `eta>=1` 与一切 `j` 都合法（B4：29 个段外格点全过；B5：路线一 capped 族在段外 19 个格点全丢
  monotonicity）。两者不矛盾（段外的 `V_j` 不是 min，用不上），但路线一那句叙述是 route-specific：
  `N2_check.py` 自己的 uncapped 变体（`chi==1`）已记 "monotone submodular for every `eta>=1`, no side
  condition"，与路线二同向。断点的来源在路线二里只出自 `min_j` 的比较（Step 9），不出自实例合法性。
- **D3（`eta_u,eta_o` 的拆分）**。路线一全程保留一般 split 并声明实例误差恰为 `(eta_u,eta_o)`；路线二归一到
  `(eta,1)`。verbatim Definition 1 允许 `eta_o=1`，convention B 更宽，所以两者都合法；本轮 B5 用
  `(eta,1)` 跑路线一的族也全过，说明该差别不影响结论。
- **D4（`n` 量词）**。见第 2 节末行：路线一 `rem:exact-n`（每个 `n>=2K`，restriction + padding，
  [HAND-PROOF-UNREVIEWED]）vs 路线二 `inf_{n>=K}` 读法。
- **D5（tie 的空洞性处理）**。路线一另有严格偏好的极限变体与 K6 段左端点反例；路线二只给 tie 偏向 `O*`
  时比值变 1（本轮独立确认对其族成立）。路线二没有触碰路线一那条 caveat。
- **D6（附带结论）**。路线一有 `prop:rigidity`（T6b）与 "`U_K > V_{K-1}` 对 `eta>1`" 的副产品；路线二没有
  刚性结论，但以 `V_K-V_{K-1}=q^{K-1}(1/k_1-1/(K eta))` 独立重现了后者（`eta>1` 时严格为正，`eta=1` 时为零），
  与台账 T6 副产品一致。
- **D7（数值走查）**。路线二有 `K=3, eta=3/2` 的完整有理走查（profile、atom 表、dual 证书、`L_3` 间隙），
  路线一在附录里没有对应段落。

**路线二与路线一没有互相矛盾的步骤。** 本轮对路线一的独立复核（B2、B5）也没有发现可以举出的错误：
`eq:duals-jpos/jzero` 的加权和恒等式与非负性在 `K=2..7` 全部 `j` 上成立，`eq:vj-family` 在段内
`K=2,3,4` 的全部格点上合法且给出 `V_j`，段外失效与路线一自己的说明一致。

---

## 4. 路线二的 gap 与追加假设（route-two gaps）

1. **一般 `K` 的 dual 可行性未闭合**。路线二的证书按 `K` 逐个符号验证，覆盖 `K=2..7`（本轮 B1 独立复跑，
   749 检查 0 失败）；对任意 `K` 的统一论证是手写的 complementary slackness 反解，状态
   [HAND-PROOF-UNREVIEWED]。路线一在这一点上更强：`N1_dual_certificate.py` 号称对 `(K,j,t,i)` 一般符号
   （modulo 一次有限分支枚举）加 `K=2..10` 暴力，320/320。
2. **一般 `K` 的实例合法性未闭合**。逐 `S` 逐 `e` 穷举只到 `K=5`（本轮 B4 复跑到 `K=5`，131 例 0 失败）；
   `K>=6` 是手写论证，状态 [HAND-PROOF-UNREVIEWED]。补充观察：路线二的 band 论证（`beta` 是 `K` 个单调
   函数的逐点极大，增量不超过 `mu(A_x \ C(S))=d_x(S)`）与 monotone submodular（coverage）在一般 `K` 上
   都是两三行，比路线一的九个二阶差分更短，但仍未经 oracle 闭合。
3. **LP relaxation 的紧性不是独立证的**，由 Step 11-15 的实例闭合；`lp_full_instance.py` 的完整
   `(f,ftilde)` LP 是浮点旁证。这一条与路线一的 `rem:app-status` 同样限度，不构成差异。
4. **追加的读法假设**：`rho_K` 读作 `inf_{n>=K} rho_{n,K}`。若原文的 `rho_K` 指某个固定的 `n`，路线二的上界
   方向需要该 `n>=2K`；路线一的 `rem:exact-n` 正是补上这一步的（其本身也是 [HAND-PROOF-UNREVIEWED]）。
5. **ground set 规模的最小性未处理**：`n<2K` 是否也能达到同值、`rho_{n,K}` 对小 `n` 的形状，路线二无结论。
   路线一同样没有 `n<2K` 的结论（`thm:ceiling` 的 `n<2K` 分支是另一条陈述）。
6. **`|O*|<K` 的记账未写**（路线一 `app:validity` 写了）。在 `assumptions.md` 的 "`O*` 是最优 `K`-set"
   约定下无实质影响。
7. **density 形式 predictor 的 [FAILED] 条目未经 oracle**：路线二给出失败不等式
   （head 步 `t<j-1` 处 `lambda_t g_t (K-1) >= sum_{s>t} lambda_s g_s + lambda_inf R_j` 在
   `lambda in [1/eta,1]` 内无解）但没有脚本；本轮 time-box 内未复算，维持其自标状态。
8. **"只用 Lemma A 的最好界是 `L_K`" 这句在路线二里是断言加一个数值例子**，不是证明。本轮 B7 以浮点 LP
   在 `K=2..5`、5 个 `eta` 上复核该断言成立（`sum+pred+mono` 的 LP 值逐点等于 `L_K`），标 [VERIFIED-LP]，
   仍不是一般 `K` 的证明。

---

## 5. 判定

- **结论一致**：两条路线得到同一个 `rho_K(eta)=min_{0<=j<=K-1} V_j(eta)`，同一段结构（`V_j` 在
  `[K-j,K-j+1]` 上取到，断点整数 `2..K`，`rho_K=1/eta` 当且仅当 `eta>=K`），`K=2,3,4` 的闭式与陈述逐字一致
  （B3 符号核对）。
- **路线二无未改正的错误**：本轮把它的每一步都重算了一遍（B1、B3、B4、B6 与 §3 走查的每个有理数），
  没有发现错误；它的下界证书与上界实例都通过独立实现的 oracle。
- **量词不完全重合**：差异只在 `n`（第 2 节）。
- **路线一无可举出的错误**（B2、B5）。

**verdict：B-PASS-with-different-route。** 同一结论，但两条路线的两个关键对象不同：
下界用的对偶支撑不同（路线一 `sum+pred+cons`，路线二 `sum+cons+mono`），上界用的 attaining 族不同
（路线一 counting function 且需要段条件，路线二 coverage function 且不需要）。两者互为独立确认，
对 `thm:exact` 的可信度是加强而不是削弱；入稿仍以路线一为准，并保留 `rem:exact-n` 的 `n` 量词，
因为路线二没有覆盖它。

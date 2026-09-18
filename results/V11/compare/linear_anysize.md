# ROUTE-COMPARISON：thm:linear-anysize（ledger T10d / J7；paper 中为 Proposition）

V11 Q8 判据 B。本文件是比对裁判的报告，不修改任何既有文件。

- **route one（仓库路线）**：`paper/sections/appendix_proofs.tex` subsection `app:hardness-anysize`
  （约 1985–2150 行）＋ `results/J7/linear_anysize.md` ＋ `THEOREM_LEDGER.md` 的 `## T10d`；
  脚本 `results/J7_symbolic.py`（148 项）、`results/J7_grid_check.py`（99 configs ＋ 对抗模拟）、
  `results/J7_fragment_checks.py`（F3 反例）、`results/J7_bound18_check.py`。
  陈述本体在 `paper/sections/results.tex` 884–905 行。
- **route two（盲审路线）**：`results/V11/route2/linear_anysize.md`（只读 `results/V11/inputs/` 下
  definition1 / assumptions / notation / statement_linear_anysize / anysize_template 五个文件）。
- **裁判自备 oracle**：`results/V11/compare/judge_linear_anysize_checks.py`（新文件，可一键复跑；
  不 import 两条路线的任何脚本；全部判定用 sympy 或 `fractions.Fraction`，float 只出现在打印里）。

结论先行：**B-PASS-with-different-route**。主链完全对上，两处走了不同的证明路线，
一处内部约定（构造里的 `j`）在整数 eta 上确实不同因而 `W_K` 是两个不同的函数（两者都仍满足
陈述的三段不等式），另有一处 route two 的附带断言可被精确反驳（见 §4 的 E1）。

---

## 1. 判据速览

| 项 | 判定 |
| --- | --- |
| 同一结论 | 是（三段链 rho_K <= alpha_lin <= min{1/eta, W_K} <= min{1/eta, rho_K + 1/(K(e^{K-1}-K-1))}，以及 eta >= K 时两端坍缩为 1/eta） |
| 量词完全一致 | 否（见 §3，共 8 条差异，其中 1 条可证地改变 W_K 的取值） |
| route two 是否有额外假设 / gap / error | 有：1 条可精确反驳的 error（D5 的 `alpha_{K+1} = 1`）、2 条 added assumption、6 条自报 gap（见 §4） |
| route one 是否有被 route two 推翻的步骤 | 无。route two 未与 route one 的任何一步冲突 |
| verdict | **B-PASS-with-different-route** |

---

## 2. 步骤对应表

route one 的步骤编号是本裁判为比对而加的（附录原文不编号）；route two 的编号用其原文编号。

### 2.1 route two 的每一步 -> route one 的对应步

| route two | 内容 | route one 对应 | 关系与证据 |
| --- | --- | --- | --- |
| L1 | predictive greedy 属于 A_n（<= K(n+1) 次 query、集合大小 <= K、deterministic、输出 K 个元素），故 alpha_n >= rho_K | R11「the lower bound being Theorem~\ref{thm:exact}」 | **route two 更细**。route one 只引用 thm:exact，不写 greedy 落在该算法类里的核对；route two 把预算、集合大小、确定性、输出大小逐条对上 A_n 的定义 [HAND-PROOF-UNREVIEWED] |
| L2 | alpha_n 关于 n 非增（补 null element，Definition 1 的 zero-pattern 保证 band 成立），单调有界故极限存在 | **无对应**（different route：route one 直接把 alpha_lin 写成 lim 而不论证极限存在） | **route two 新增**。论证方向正确：把 inf 限制到「n 上实例的 null-element 延拓」这一子族即得 alpha_{n+1} <= alpha_n [HAND-PROOF-UNREVIEWED] |
| U1 | modular hard family：w_e = 1/K on O、1/(eta K) off O，tilde f = \|S\|/(eta K)，(eta_u, eta_o) = (eta, 1)，F_OPT = 1 | R12 = `app:ceiling` 的 construction：f_O(S) = c(\|S∩B\|/eta_o + eta_u\|S∩O\|)，tilde f = c\|S\| | **同一族**。route two 的族是 route one 的 eta_o = 1、c = 1/(eta K) 特例。注意 route one 的 1/eta 分支不在 `app:hardness-anysize` 里，而在 `app:ceiling`（thm:ceiling）；route two 独立重造了它 |
| U2 | tilde f 只依赖 \|S\| 故零泄漏，E_O[f(T)] <= 1/eta + K/n，令 n -> infinity 得 alpha_lin <= 1/eta | R12 的 deterministic 段（n >= 2K 时取 O ⊆ N\T，直接得 <= 1/eta，无 K/n 项） | **different route，route one 更强**。route two 用平均论证得到 1/eta + K/n，只在极限下够用；route one 用「T 固定 ⟹ 存在与 T 不交的 K-set」得到 n >= 2K 上的精确 1/eta |
| U3 | 与 U2 取 min | 陈述本身的 min{1/eta, W_K} | 对应 |
| U4 | randomized 按 Yao 方向（分布上取期望再交换）归约到 deterministic | 陈述的 parenthetical「randomized algorithms measured in expectation」＋ `app:ceiling` 的 randomized 段 | 对应；route two 写出了交换步骤 [HAND-PROOF-UNREVIEWED] |
| C1 | 两类计数函数 monotone submodular 的 (a)-(d) 格点判据，及其到 (M1)(M2)(M3) 的翻译 | R6 的一句「These one-dimensional facts yield every monotonicity and diminishing-returns inequality of F on the count grid」 | **route two 更细**。route one 把这一步压成一句话；route two 写出四条格点不等式与三条序列条件，并另在脚本里逐格直接验 F 本身 |
| C2 | band 的四类边表格，band 完全由 (M1)(M2)(M3) 推出，不产生新约束；zero-pattern 随之成立 | R7 的「the same four-edge-class table as in Appendix~\ref{app:greedybudget}」 | **同一张表**。逐行核对一致：x 方向 y=0 行 ΔH = Δr + (eta-1)Δa（route one 记作 p_x + (eta-1)u_x），其余三行比值为 1 或 eta。裁判独立复验 [VERIFIED-EXHAUSTIVE]（B1） |
| C3 | H(x+1,0) = H(x,1) 在每个 size 上成立；closing step 上等价于 a_{t*} = 0 | R8 ＋ R6 的 a_x - a_{x+1} = g_{x+1}/eta 与 r_{t*} = g_{t*} | **同一事实**，写法不同：route one 把 design equation 写成 r_{t*} = g_{t*}，route two 写成 a_{t*} = 0；由 a = r - g 二者相同 [VERIFIED-SYMBOLIC] |
| C4 | design equation 解出 d(m) = (nu^m - K)/(K Theta(m))，Theta(t) = eta nu^t - t - eta > 0；恒等式 (3.4) | R3 ＋ R4：d = (nu^m/K - 1)/B_m，B_m = eta(nu^m - 1) - m，以及 d - 1/(K eta) = (m - eta(K-1))/(K eta B_m) | **完全相同的量**：A1「Theta == B_m」、A2「d_route2 == d_route1」、A3「(3.4) 恒成立」均 [VERIFIED-SYMBOLIC]。Theta > 0 的证法不同：route one 用 eta(nu^m - 1) >= eta m(nu-1) > m，route two 用 psi(eta) = eta ln nu > 1 与 Theta' > 0；两者都成立 |
| C5 | admissibility 精确归约为 (A) m >= eta(K-1)、(B) m d <= 1、(C) (m+1) d >= 1 | R6 的 legality 清单：d ∈ [1/(m+1), 1/m]（＝(B)＋(C)）、d > 1/(K eta)（＝(A)）、junction p_{j-1} >= D、K g_x >= r_x | **等价条件集**，但方向不同：route one 只证**充分**（这些条件成立故族合法），route two 还逐条论证**必要**（每条 admissibility 都归到这三条）。K g >= r 一项：route one 用 plateau 上凹且在 ell = m 处取 (K-1) r_{t*} >= 0，route two 用 chi(u) 的 concavity 化为 nu^m(K eta - m) >= K eta；A8 证明两者是同一不等式 [VERIFIED-SYMBOLIC] |
| C6 | Psi_2(t) = 1 - (t+1) d(t)，m 取第一个非正整数点；(i) 存在性、(ii) (C)、(iii) (A) 严格、(iv) (B) 用 (3.5) ＋ 极小性反证 | R1：Psi_1(t) = (K eta - t - 1) nu^t - K(eta-1)，m = min{z >= 1 : Psi_1(z) <= 0}；(B) 由 R4 的第二恒等式 1/m - d = nu Psi_1(m-1)/(K m B_m) 与极小性一行得出 | **同一个 m，不同的判别式与不同的 (B) 证法**。A6：Psi_2(t) = Psi_1(t)/(K Theta(t))，Theta > 0 故同号、同第一非正点 [VERIFIED-SYMBOLIC]。**different route**：route one 的 Psi_1 让极小性直接给出 m d(m) <= 1；route two 的 Psi_2 只给出 m d(m-1) < 1，故必须补 (3.5) 恒等式（A7 [VERIFIED-SYMBOLIC]）＋ zeta 单调性反证。两条都成立，route one 更短 |
| C7 | location bounds eta(K-1) < m < K eta | R2：同一对界，右半由 Psi_1(K eta - 1) = -K(eta-1) < 0，左半由 nu^{eta(K-1)} > e^{K-1} > K | **相同结论，different route**：route two 的右半由 (B) ＋ C5 第 8 条得 K eta - m > 0，左半由 (3.4) ＋ k_1 <= K eta 得 Psi_2(t) > 0 for t <= eta(K-1) |
| C8 | W_K = F(K,0) = 1 - q^j(1 - (K-j)d)；W_K - rho_K = q^j(K-j)(d - 1/(K eta)) | R10 前半：W_K = 1 - Q + (K-j)Q d，gap 恒等式 (17) | **公式逐字相同**（Q = q^j）。但 j 的取法不同，见 §3 的 (Q7) |
| C9 | gap < 1/(K(e^{K-1}-K-1))：用 q^j <= 1、K - j <= **K**、m - eta(K-1) < eta、Theta(m) > eta(h^{K-1}-K-1)，再补 L1（Padé 型 psi - 1 > 1/(2eta-1)）、L2、L3 | R10 后半：用 K - j <= **eta**、Q <= 1、m - eta(K-1) < eta、nu^m > e^{K-1}，三行收尾 | **different route**。route one 的 j 公式蕴含 K - j = ceil(eta) - 1 <= eta（clamp 到 K-1 时 K-j = 1 <= eta，clamp 到 0 时 eta > K = K-j），故一步到位；route two 因换了 j 的约定只能用 K - j <= K，多付出一个解析引理链。裁判精确复验：两种 j 下 gap 都严格落在界内 [VERIFIED-EXHAUSTIVE]（D1，2352 configs，e 用有理上界 2719/1000 使判定保守） |
| C10 | (P1) 每个 size 上 H(x+1,0) = H(x,1)；(P2) x >= t* 后 H 恒为 C；(P3) 泄漏必须 y >= 2 且 x <= t*-1，故 \|S\| <= t*+K-1 | R8：同 (P1)(P2)；泄漏条件写成 y >= 2 且 \|S\| <= t*+**K** | **同向，route two 更紧一格**。route one 只用 x > t* 饱和；route two 注意到 a_{t*} = 0 使 x = t* 的 y >= 1 切片也平坦。裁判复验 P1/P2/P3 与 \|S\| <= t*+K-1 [VERIFIED-EXHAUSTIVE]（B1）。两者不冲突 |
| D1 | instance distribution：O 均匀随机 K-subset | R5 ＋ R9 的「For a uniformly random K-set O」 | 对应 |
| D2 | reference oracle tilde f_0(S) = sigma(\|S\|)/eta_u，泄漏的定义，L = t*+K-1 < K(eta+2) | R8/R9 隐含同一 reference（G 只依赖 \|S\|），常数写作 t*+K | 对应；route two 把常数显式写成与 n 无关 |
| D3 | 固定路径归纳 ＋ union bound：Pr[E] <= c n K · C(K,2) L(L-1)/(n(n-1)) + K^2/n = O(K^5(eta+2)^2/n) -> 0，得 alpha_lin <= W_K | R9：单查询泄漏概率 <= K^2(t*+K)^2/(2n^2)，cnK 次累计 <= c K^3(t*+K)^2/(2n) -> 0，「canonical-transcript induction 与 averaging 同 app:hardness」 | **同一论证，route two 写全**。route one 把 transcript 归纳外包给 `app:hardness`；route two 就地写出归纳与 T ∩ O 项。量级一致（t*+K <= K(eta+2) 时 K^3(t*+K)^2 = O(K^5(eta+2)^2)）。两者都 [HAND-PROOF-UNREVIEWED] |
| D4 | 预算敏感性：union bound 需 Q = o(n^2)；Q = C(n,K) 时算法可枚举定位 O | R15「Beyond the linear budget」：Q <= n^2/(2K^2(t*+K)^2) 仍是 candidate bound（ledger T12）；指数 2 在 48 个配置上有 two-constraint 证书；two-sided band 恰在 tau = 1 且 n > K(t*+1) 时可行 | **route two 只覆盖定性部分**。route one 的 tau >= 2 不可行证书与 two-sided band 结论在 route two 中无对应（route two 也没有声称） |
| D5 | n -> infinity 不可去：n = K+1 时用 K+1 次 complement query 分离唯一 B 元素并恢复 O，ratio = 1；**于是 alpha_{K+1} = 1 > W_K** | R17（附录注释与 ledger T10d）：n < K + t* 时 reverse greedy 在该族上读出 O 并达到 ratio 恰为 1，故「no finite-n `<= W_K` statement holds wholesale」 | **同一现象，不同见证，且 route two 多走了一步错**。两者都只证明了「该 hard family 在有限 n 上不再给出 <= W_K」；route two 进一步写下 alpha_{K+1} = 1，这句可被精确反驳（§4 E1）。route one 的措辞停在「该族上 ratio = 1」，没有这一步 |
| D6 | eta >= K 时 beta_j 关于 j 非增（beta_{j+1}/beta_j <= 1 ⟺ eta >= K - j），故 rho_K = V_0 = 1/eta，全链坍缩 | 陈述的「For eta >= K both ends equal 1/eta」，依据 thm:exact 的 plateau（`appendix_proofs.tex` 793–825、1429 行：j = 0，min_i V_i = V_0 = 1/eta） | **同一结论**；route two 把 beta 的单调性判据独立推了一遍，与 route one 引用的 thm:exact plateau 一致 |
| D7 | 合并 | 附录的收尾句「This proves Proposition~\ref{thm:linear-anysize}」 | 对应 |
| §5.1 | K = 3、eta = 3/2 的全表走查：j = 2, m = 4, d = 13/58, t* = 6, W_3 = 523/928, rho_3 = 9/16, gap = 1/928 | 附录与 `results/J7/linear_anysize.md` 的同一算例：m = 4, d = 13/58, W_3(3/2) = 523/928 = 9/16 + 1/928；J7 文件另给 Psi_1(3) = 12 > 0、B_4 = 116 | **逐格相同**。裁判把 route two 的 8 行 r/g/a/F/H 表逐项精确复算，全部命中 [VERIFIED-EXHAUSTIVE]（B3） |
| §5.2 | K = 2 的 probe 概率算例（route two 自标 [FAILED]，因为 `ProbeLottery` 不在其五个 input 文件中） | **无对应**：`ProbeLottery` 属于 J8（`results/V11/inputs/statement_probelottery.md`），与本命题无关 | **越界项，与本判据无关**。route two 已把它隔离（明说 K = 2 不在定理范围、不用它下任何结论），不影响主链 |
| §5.3 | 62208 格 PASS1 ＋ 350 格 PASS2 有理穷举 0 失败；gap/界最大比 0.2018（K=6, eta=6） | `results/J7_symbolic.py`（148 项）、`results/J7_grid_check.py`（99 configs）、`results/J7_bound18_check.py` | **独立网格，结论一致**。裁判自建第三套网格（2352 configs，K = 3..10）复现同一结论，route two 的 j 下最大比 0.2155（K=10, eta=10），route one 的 j 下 0.2146 [VERIFIED-EXHAUSTIVE]（D1） |

### 2.2 route one 中 route two 未覆盖的步骤

| route one 步 | 内容 | route two 覆盖情况 |
| --- | --- | --- |
| R13 | night-4 截断规则 m = ceil(K eta) - 1 的反驳：K = 3、eta = 667/500 时该公式给 m = 4，得 r_{t*} = -151089222203006/81950355825200625 < 0（`results/J7_fragment_checks.py`） | **未覆盖**，也不需要：route two 从未见过旧规则，它的 Psi_2 直接给出 m = 3 的那一类正确取值 |
| R14 | S12：Psi 规则与 argmax_m 的 excess slope 在 303 个精确点一致，并有结构恒等式（d(z) 在 Psi(z-1) >= 0 时升、Psi(z) <= 0 时降） | **未覆盖**。route two 没有做「Psi 规则 ＝ 最优 m」这一层对照，只证明了它给出的 m 是 admissible 的 |
| R15 | 超线性预算段：Q <= n^2/(2K^2(t*+K)^2)；t*+K <= (2+eta)K+1；tau >= 2 在 48 个配置上由 two-constraint 证书不可行；two-sided band 恰在 tau = 1 且 n > K(t*+1) 可行 | **部分覆盖**（D4 只有 Q = o(n^2) 这一句） |
| R16 | 渐近：eta = 2 时 excess 在 K = 4,8,16,32 为 3.2e-4、5.9e-7、4.5e-12、5.2e-22；W_K(eta) -> 1 - e^{-1/eta}；链 L_K <= V_j <= W_K < U_K | **未覆盖**，route two 在其 gap 清单第 9 条自报未做 |
| R7 末句 | 「both split endpoints attained on positive-gain edges at x = 0 ⟹ the smallest admissible error factors are exactly (eta_u, eta_o)」（族的误差标定是紧的） | **未覆盖**。route two 的 C2 表说明每类边的比值为 1 或 eta（端点被取到），但没有把它上升为「(eta_u, eta_o) 是最小可行误差因子」这一标定断言 |
| R12 的 attainment 方向 | `app:ceiling` 的 matching upper bound：穷举搜索 hat S 达到 1/eta（1/eta 这个天花板是可达的） | **未覆盖**，route two 只需要 1/eta 作上界，没有做可达性 |

> 关于任务书里 thm:ceiling / prop:valueacc / J8 的三条附加指令：它们按陈述分派，与
> thm:linear-anysize 无关。本判据中唯一与 `app:ceiling` 相关的接触点是 route one 的 1/eta 分支
> 来源（表中 U1/U2 行已注明）；`appendix_model_proofs.tex`、`J8_claude_spotcheck.py`、
> `HANDOFF_ADDENDUM_2026-09-18.md` 的 C 节与本命题无交集，本文件不对它们下判断。

---

## 3. 量词比对

两条路线在**陈述层面**的量词一致：K >= 3 整数；eta > 1 实数；两者先固定再令 n -> infinity；
deterministic 算法，randomized 按自身随机性取期望；O(nK) 次 query；query 大小任意；
输出 \|T\| <= K；实例为 monotone submodular f ＋ error product <= eta；alpha_lin 是 n -> infinity 的极限；
eta >= K 时两端等于 1/eta。以下是**只出现在一侧**的量词。

只在 route two 出现（route one 留作隐含或写在别处）：

- **(Q1) n >= K 与极限存在性。** route two 定义 alpha_n 时明写 n >= K，并用 alpha_n 关于 n 非增
  ＋ 有下界 rho_K 论证 lim 存在（步骤 L2）。route one 直接写 lim，没有这一步。
- **(Q2) 预算常数 c 与 n 无关。** route two 明写「存在与 n 无关的常数 c（可依赖 K, eta）使 query 数 <= c n K」，
  并在 D4 指出论证实际只需 Q = o(n^2)，以及 c 若能随 n 增长到 Theta(n) 则论证失效。
  route one 的 O(nK) 写法蕴含这一点但未把 c 的允许依赖写明。
- **(Q3) tie breaking 由 adversary 打破。** 在 `assumptions.md`（＝ paper 的 predictive greedy 段）里，
  不在 Proposition 的句子里；route two 把它提到量词表。
- **(Q4) F_OPT = 0 的平凡约定。** 在 `model.tex`，不在 Proposition 句子里；route two 提到量词表。
- **(Q5) band 是 single-element 版、S 跑遍全部 2^N、并含 zero-pattern（d_e(S) = 0 ⟺ tilde d_e(S) = 0）。**
  route one 在 `def:eta` 里，Proposition 只写「error product at most eta」；route two 逐条复述。
  核对 `paper/sections/model.tex` 23–32 行，route two 的复述与 Definition 1 逐字相符。
- **(Q6) ratio 约定 alpha ∈ (0,1]、F_ALG >= alpha F_OPT、越大越好。** 在 `notation.md`；route two 提到量词表。

只在 route one 出现：

- **(Q7) 构造内部的 j 的取法（改变 W_K 的取值）。** route one 用显式公式
  `j = max{0, min{K-1, K+1-ceil(eta)}}`；route two 用「rho_K = min_j V_j 的 argmin，并列时取最小的 j」。
  template 只写「the active segment index of rho_K = min_j V_j」，并列时未定义，两读法都合规。
  **两者在整数 eta（2 <= eta <= K）上必然不同**，且恰好 j_route1 = j_route2 + 1；
  此时 V_{j} = V_{j+1}（rho_K 相同），但 W_K 不同，且 **W_route1 < W_route2 严格**。
  [VERIFIED-EXHAUSTIVE]（C1，K = 3..14、12 组分母、eta <= 25，共 39456 configs，
  不匹配项全部且仅出现在整数 eta 上，形状无一例外；C2 在 528 个格点上进一步确认
  m 与 rho_K 永远一致、j 不同处 W_route1 < W_route2 严格）。例：K = 3、eta = 2 时
  j_route1 = 2、W = 2003/4275 = 0.468538…；j_route2 = 1、W = 403/855 = 0.471345…；
  rho_3(2) = V_1 = V_2 = 7/15 = 0.466666…（两个 j 都是 argmin，故 rho_K 相同）。
  后果：两条路线的 `W_K` 是**两个不同的函数**（在非整数 eta 上重合，在整数 eta 上 route two 的更大），
  但两者都是合法实例族的值，故 alpha_lin <= W 对两者都成立，三段链对两者都成立
  [VERIFIED-EXHAUSTIVE]（B2、D1）。paper 里的 W_K 指的是 route one 的那一个。
- **(Q8) 族的误差标定是紧的：「the smallest admissible error factors are exactly (eta_u, eta_o)」。**
  route two 没有给出对应量词（它只验证 band 成立并指出每类边的比值取到 1 与 eta）。

因此 `quantifier_match = false`：(Q7) 是可证的实质差异，(Q1)(Q2)(Q5) 是 route two 的显式化补足，
(Q8) 是 route one 独有。

---

## 4. route two 的额外假设、gap 与 error

裁判自己重算了 route two 的每一处计算，结果如下。

### 4.1 可精确反驳的 error（1 条）

- **[FAILED] 步骤 D5 第 1 点的句子「alpha_{K+1} = 1」。**
  route two 正确地论证了：在第 3 节的 hard family 上，n = K+1 时 K+1 次 complement query
  S_e = N\{e} 足以分离唯一的 B 元素（H(1,K-1) = C - eta a_1/(K-1) != C = H(0,K)，因 a_1 > 0），
  从而在**该族的实例上**达到 ratio 1。但 alpha_{K+1} 是对 I_{K+1}(K,eta) **全体**实例取 inf 再对算法取 sup，
  单个族上的 ratio 1 不足以给出 alpha_{K+1} = 1。反驳用 route two **自己的** U1 族即可：
  n = K+1 时 tilde f = \|S\|/(eta K) 与 O 无关，deterministic 算法的输出 T 固定，\|T\| <= K，
  而 \|B\| = 1 迫使 \|T ∩ O\| >= \|T\| - 1，adversary 取使交集最小的 O，得
  `alpha_{K+1}(K,eta) <= k_1/(K eta) = (eta(K-1)+1)/(K eta) < 1`（eta > 1 时严格）。
  例：K = 3、eta = 3/2 时上界为 8/9；K = 5、eta = 3 时为 13/15。
  [VERIFIED-EXHAUSTIVE]（E1，K = 3..7 × eta ∈ {3/2, 2, 5/2, 3, 7/2}，全部命中 k_1/(K eta) 且 < 1）。
  **影响范围**：该句属于「n -> infinity 这个量词不可去」的空洞性检验，不进入定理链；
  去掉这句之后 D5 的其余两点（T ∩ O 项为 Theta(K^2/n)；alpha_n 非增故有限 n 的 alpha_n 可严格大于 alpha_lin）
  仍成立，结论（n -> infinity 不可去）不受影响。
- **顺带记录一个两条路线共有的弱点（不计入 route two 独有）**：两条路线都只证明了
  「该 hard family 在有限 n 上不再给出 <= W_K」，都没有给出「alpha_n > W_K 在某个有限 n 上成立」的证明
  （那需要一个在 I_n 全体实例上超过 W_K 的算法）。route one 的附录措辞
  「no finite-n `<= W_K` statement holds wholesale」与 ledger T10d 的「有限 n 的 `<= W` 为假」
  之间也有同样的落差。建议按 route one 附录的措辞为准，ledger 那一行的强读法宜收缩。
  状态 [HAND-PROOF-UNREVIEWED]。

### 4.2 added assumption（2 条，route two 自报，裁判确认）

1. **j 的并列取法**（见 (Q7)）。route two 取最小 argmin，route one 用显式公式。
   route two 自己说明 gap 界只用 q^j <= 1 与 K - j <= K，故结论不变。这一点裁判确认为正确，
   代价是必须补 L1/L2/L3 那条解析链（route one 因 K - j <= eta 而不需要）。
2. **rho_K(eta) = min_{0<=j<=K-1} V_j(eta) 被当作已知**（`notation.md` 归给 thm:exact，route two 未独立证明）。
   L1、C8、D6 依赖它。route one 同样依赖 thm:exact。这是两条路线共同的外部依赖，不是 route two 独有的缺口。

### 4.3 route two 自报的 gap（6 条，裁判逐条评估）

1. **`ProbeLottery` 未定义 ⟹ §5.2 记 [FAILED]。** 与本命题无关（属 J8）。**不计为本判据的 gap**。
2. **C1 的等价性（(a)-(d) ⟺ (M1)(M2)(M3)）只有叙述没有完整证明。** route one 在这一点上更弱
   （整段压成一句），且两条路线的网格脚本都是直接对 F 逐格验，不依赖该等价性。**不影响结论**。
3. **L2/L3 的解析证明分 K >= 4 与 K = 3 两条路，端点极限的 epsilon 细节未写。**
   裁判精确复核了这条链：
   - L1（Padé 型）：phi(z) = -ln(1-z) - 2z/(2-z)，phi'(z) = 1/(1-z) - 4/(2-z)^2 = z^2/((1-z)(2-z)^2) > 0，
     phi(0) = 0，故 z = 1/eta 给出 psi(eta) - 1 > 1/(2eta-1)。裁判逐步复核了这两行代数
     （(2-z)^2 - 4(1-z) = z^2），结论一致；该项的符号确认由 route two 自己的 `check_analytic_bound.py`
     承担，本判据脚本未重复，状态沿用 [VERIFIED-SYMBOLIC]。
   - L2 的 K >= 4 分支：ln(eta/K) + (K-1)/(2eta) 在 eta = (K-1)/2 取驻点，二阶导 (K-1-eta)/eta^3 > 0 故为极小，
     值 1 + ln((K-1)/(2K)) 关于 K 递增，K = 4 时为 1 + ln(3/8) > 0（等价于 e > 8/3）。驻点 (K-1)/2 ∈ (1, K) 对 K >= 4 成立。
   - L2 的 K = 3 分支：ln(eta/3) + 2/(2eta-1)，驻点方程 4eta^2 - 8eta + 1 = 0 的正根 eta = 1 + sqrt(3)/2 ≈ 1.866，
     二阶导在该点为正，值 ln((2+sqrt3)/6) + sqrt3 - 1 ≈ 0.2572 > 0；端点 eta -> 1+ 给 2 - ln 3 ≈ 0.901 > 0，
     eta -> 3- 给 2/5 = 0.4 > 0。**端点无问题，route two 的这条 gap 是过度保守的自陈。**
     状态仍记 [HAND-PROOF-UNREVIEWED]（手证，无符号 oracle 覆盖整条链），但最终不等式本身
     已由 D1 在 2352 个精确格点上独立确认。
4. **alpha_n 的 sup 是否可达、c 对 K/eta 的依赖未细究。** 与 route one 同等程度地未处理。**不影响结论**。
5. **只给 alpha_lin <= W_K，未构造达到 W_K 的算法。** 定理本身只声称 <=，route one 亦然。**不是 gap**。
6. **1/eta 与 W_K 两个分支用了两个独立的 hard family 而未合成为一族。** route one 也是两族
   （`app:ceiling` 给 1/eta，`app:hardness-anysize` 给 W_K）。**与 route one 一致，不是差异**。
7. **未验证 W_K 关于 eta 的单调性、K -> infinity 的渐近。** 对应 route one 的 R16，route one 有而 route two 无。
   **计为 route two 相对 route one 的缺口，但不在定理陈述之内**。
8. **隔离说明**：route two 记录了收尾时对 `results/V11/route2/` 执行过一次 `ls`，看到其他盲审路线的文件名，
   未打开任何一个。裁判无法独立核实这一点，按其自报记录在案。

### 4.4 裁判独立复算的结论（脚本 `judge_linear_anysize_checks.py`）

| 块 | 内容 | 结果 |
| --- | --- | --- |
| A1–A8 | 两条路线的 d、Theta/B_m、Psi 规则、(3.4)、route one 的两条恒等式、route two 的 (3.5)、chi(m) 与 1 - m d 的同分子性 | 全部 residual = 0 [VERIFIED-SYMBOLIC] |
| B1 | route two 的 j 下族的合法性：monotone、submodular（含 cross/DR）、0 <= F <= 1、F(0,K) = 1、F(0,0) = H(0,0) = 0、逐边 band、zero pattern、P1/P2/P3、(A)(B)(C)、location bounds、泄漏 size <= t*+K-1 | 575 configs（K = 3..7，eta 有理 <= 6），0 失败 [VERIFIED-EXHAUSTIVE] |
| B2 | 同一族改用 route one 的 j 亦合法 | 575 configs，0 失败 [VERIFIED-EXHAUSTIVE] |
| B3 | route two §5.1 的 8 行 r/g/a 表与 W_3 = 523/928、gap = 1/928、H(1,2) = 23/24、H(3,0) = 37/48 | 逐项命中 [VERIFIED-EXHAUSTIVE] |
| C1–C2 | j 的差异形状；两条路线的 m 与 rho_K 永远一致 | C1：39456 configs（K = 3..14、eta <= 25），差异仅在整数 eta 且恒为 j_route1 = j_route2 + 1；C2：528 configs（K = 3..8、eta <= 9），m 与 rho_K 全一致，j 不同处 W_route1 < W_route2 严格 [VERIFIED-EXHAUSTIVE] |
| D1 | 0 <= W_K - rho_K < 1/(K(e^{K-1}-K-1))，两种 j 都验，e 用有理上界 2719/1000（判定保守） | 2352 configs（K = 3..10、eta <= 15），0 失败；最大比 route two 0.2155（K=10, eta=10）、route one 0.2146（K=10, eta=101/10） [VERIFIED-EXHAUSTIVE] |
| E1 | route two D5 的 alpha_{K+1} = 1 | 反驳成立，上界恒为 k_1/(K eta) < 1 [VERIFIED-EXHAUSTIVE] |

另外，route one 的 `results/J7_bound18_check.py` 本次亲跑：`configs: 99 / ALL PASS`，exit 0，
与 ledger T10d 的记载一致。

---

## 5. route one 是否有被 route two 推翻的步骤

没有。逐项核对：

- Psi 判别式：形式不同但同号同 m（A6）。不构成冲突。
- d、Theta/B_m、(3.4)、W_K 与 gap 的闭式：逐字相同（A1–A3、C8 行）。
- admissibility：route two 的 (A)(B)(C) 与 route one 的 d ∈ [1/(m+1), 1/m] ∧ d > 1/(K eta) 等价。
- 泄漏范围：route two 的 \|S\| <= t*+K-1 比 route one 的 \|S\| <= t*+K **更紧**，是加强不是反驳。
- j：两读法都合规（template 未定义并列），route one 的读法给出更小的 W_K，故 route one 的陈述更强而非有误。
- 1/eta 分支：route two 的族是 route one `app:ceiling` 族的特例，结论一致；route one 的 n >= 2K 版本更强。

唯一值得记入 review 的是 §4.1 末尾的共有弱点（ledger T10d「有限 n 的 `<= W` 为假」这一行的强读法
超出了模拟所支持的范围），这不是 route two 推翻 route one，而是两条路线共同的措辞收缩建议。

---

## 6. 判定

- `consistent = false`。两条路线到达同一结论（三段链 ＋ eta >= K 坍缩），但 route two 含一条未修正的
  错误断言（D5 的 alpha_{K+1} = 1，[FAILED]，见 §4.1）。该错误位于量词必要性说明中，不进入定理链。
- `quantifier_match = false`。差异见 §3：(Q7) 的 j 约定可证地改变 W_K 的取值；
  (Q1)(Q2)(Q5)(Q3)(Q4)(Q6) 是 route two 的显式化补足；(Q8) 是 route one 独有。
- **verdict = B-PASS-with-different-route**。主链的每一步在 route one 中都有对应；
  C6(iv) 的 (B) 证法、C7 的右半、C9 的 gap 收尾、U2 的 1/eta 论证走的是不同路线，
  全部独立成立；route two 另补了 route one 没有的 L2（极限存在性）与 D3 的显式 transcript 归纳。
  唯一的 error 局限在一句附带断言上，且其所属小节的结论（n -> infinity 不可去）本身不受影响。

复跑方式与本次亲跑输出（exit 0）：

```
$ python3 results/V11/compare/judge_linear_anysize_checks.py
[A] symbolic identities (sympy)
  PASS  A1 Theta(m) == B_m
  PASS  A2 d_route2 == d_route1
  PASS  A3 (3.4) d - 1/(K eta) = (m - eta(K-1))/(K eta Theta)
  PASS  A4 route one id1  d - 1/(m+1) = -Psi1(m)/(K(m+1)B_m)
  PASS  A5 route one id2  1/m - d = nu Psi1(m-1)/(K m B_m)
  PASS  A6 Psi2(t) == Psi1(t)/(K Theta(t))  (same sign, same m) | ratio=1
  PASS  A7 route two (3.5) s Theta(m-1) - (s-1) Theta(m) = nu^m(K eta - m) - K eta
  PASS  A8 chi(m) and 1 - m d share the numerator ... (up to the positive factor K-1)
[B] exhaustive legality of the route-two family (575 configs)
  PASS  B1 monotone submodular + band + zero pattern + P1/P2/P3 + (A)(B)(C) + location bounds
           + leak size <= t*+K-1
      largest observed leak size minus t*: 5 (K=7 eta=2)
  PASS  B2 the same family with route one's j is legal too
  PASS  B3 route two section 5.1 table (K=3, eta=3/2) reproduces exactly
[C] the two j conventions (39456 + 528 configs)
  PASS  C1 j differs exactly at integer eta in [2,K], always j_route1 = j_route2 + 1
      mismatching configs: 1080 of 39456; example (3, '2', 2, 1)
  PASS  C2 m and rho_K always agree; where j differs, W_route1 < W_route2 strictly
      example: K=3 eta=2  j1=2 j2=1  W1=2003/4275  W2=403/855
[D] exact gap bound, e replaced by 2719/1000 (2352 configs, both j)
  PASS  D1 0 <= W_K - rho_K < 1/(K(e^{K-1}-K-1)) for both j conventions
      r1 largest gap/bound ratio 0.214603 at K=10 eta=101/10
      r2 largest gap/bound ratio 0.215519 at K=10 eta=10
[E] route two step D5, the sentence alpha_{K+1} = 1
  PASS  E1 on route two's U1 family at n=K+1 every deterministic algorithm is capped at
           k_1/(K eta) < 1, so alpha_{K+1} = 1 is false

all judge checks passed (block E confirms the route-two D5 sentence is refuted)
```

（block E 的 PASS 表示「该反驳成立」，即 route two 的那句断言为 [FAILED]。）

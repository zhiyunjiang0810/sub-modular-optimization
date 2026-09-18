# V11 Q1 oracle 报告：prop:necessity（台账 T1，别名 prop:nobound）

复现命令：`python3 results/V11/oracle/nobound.py`（exit 0 当且仅当全部检查通过）。
本次运行：exit 0，13 项检查全 PASS，0 FAILED，耗时 32.4 秒。
产物：`results/V11/oracle/nobound.py`、`nobound.log`（全部输出）、`nobound.json`（机器可读）。
全部判定用 `fractions.Fraction` 或 sympy，float 只出现在打印文本里。随机种子固定：D 主循环 20260918，子抽样 11。

## 1. 被测陈述与两个构造

陈述（`results/V11/inputs/statement_nobound.md`）：不假设 eta 上界时，对任意 deterministic algorithm、任意 n >= 2K，存在 (f, ftilde) 使输出 T 满足 f(T) <= K/(n-K) f(O\*)。

两个 route-one 构造都已按原文实现：

- 构造 A（`paper/sections/appendix_model_proofs.tex`，2026-09-18 交付未接线）：ftilde(S) = |S|，delta = K/(n-K)，f(S) = |S ∩ O| + delta |S \ O|，eta = 1/delta = (n-K)/K。
- 构造 B（`paper/sections/appendix_proofs.tex`，subsection `app:necessity`，约第 81 行）：ftilde(S) = |S|，gamma = K^2/(n(n-K))，f_O(S) = |S ∩ O| + gamma |S \ O|，eta = 1/gamma = n(n-K)/K^2。

两者是同一单参数族 f_delta(S) = |S ∩ O| + delta |S \ O| 的两个 delta 取值。脚本在 delta ∈ {K/(n-K), K^2/(n(n-K)), 1/2, 1/5, 1/50}、K = 1..4、n = 2K..12 上跑同一套 oracle，共 32 个 (K, n) 格点、160 个 instance。

## 2. Criterion C：oracle 结果（逐项）

| 编号 | 检查内容 | 状态 | 计数 |
|---|---|---|---|
| C0 | sympy 关系式：delta - gamma = K/n；n(n-K) - K^2 在 n = 2K+m 处等于 K^2 + 3Km + m^2；K/n + gamma = delta；1/delta = (n-K)/K；1/gamma = n(n-K)/K^2 | PASS [VERIFIED-SYMBOLIC] | 5 个 residual 全为 0 |
| C1 | instance validity：f(∅) = 0、monotone、submodular（local exchange 形式全枚举；n <= 8 再加 diminishing-returns 形式） | PASS [VERIFIED-EXHAUSTIVE] | 160 instance，162140 个子集，896560 次单调检查，2288035 次 submodularity 检查，453630 次 DR 检查 |
| C2 | Definition 1 的 band 成立，且最小可行因子恰为 eta_u = 1、eta_o = 1/delta（两端都被取到），并满足 d = 0 当且仅当 dtilde = 0 | PASS [VERIFIED-EXHAUSTIVE] | 896560 个 (S, e) pair |
| C3 | OPT = f(O) = K（全子集枚举与 count lattice 枚举两条路给同一值） | PASS [VERIFIED-EXHAUSTIVE] | 160 instance |
| C4/C5 | 算法类型 1（predictive greedy on ftilde，adversarial ties）与类型 2（对 ftilde 在所有 K-set 上穷举 argmax，adversarial ties）：输出与 O 不交，且 f(T) <= delta OPT | PASS [VERIFIED-EXHAUSTIVE] | 320 次算法运行；每个 instance 的 K-set 全平局（例：K = 3, n = 9 时 20 个 K-set 同值，greedy 用 27 次 query，穷举用 84 次） |
| C6 | 算法类型 3（任意固定输出 T，\|T\| <= K）：对每个 T 重建不交的 O，f(T) <= delta OPT | PASS [VERIFIED-EXHAUSTIVE] | 18240 个固定输出，其中 11450 个取等号（\|T\| = K） |
| C7 | n >= 2K 时每个 \|T\| <= K 都存在不交的 K-set O | PASS [VERIFIED-EXHAUSTIVE] | 3648 个输出 |
| C8 | n = 2K-1 的反面样例：满额输出 T 与任何 K-set O 必相交，构造的结论不可达 | PASS（记录见下） | 12 个 case，12 个都不可达 |
| C9（附加） | app:necessity 的 randomized 平均步：O 取 uniform random K-set 时 E_O[f_O(T)]/OPT <= K/(n-K)（对全部 C(n,K) 个 O 精确求和） | PASS [VERIFIED-EXHAUSTIVE] | 2290 个 O 求和项 |
| C10 | K = 3、eta = 3/2 running example，并记录该固定 eta 下陈述常数 K/(n-K) 的成立范围 | PASS [VERIFIED-EXHAUSTIVE] | n ∈ {6, 7, 8, 12} |

worst slack（Criterion C，所有算法输出）：0，即界在 \|T\| = K 时处处取等号；ratio f(T)/OPT = delta。记录到的极端参数是 K = 1, n = 2, delta = 1（ratio 1，界也是 1）。

## 3. Criterion D：对陈述本身的反例搜索

- 随机 deterministic algorithm 数量：2400（要求 >= 2000）。三类各 800：
  1. `fixed_set`：随机固定输出集合，\|T\| <= K；
  2. `rule_on_answers`：随机生成的确定性规则，先对 ftilde 做 1..6 次真实 query，再由答案向量决定输出（因为 ftilde(S) = |S| 与 O 无关，答案恒定，输出落为固定集合，这正是证明用的 reduction，脚本是执行它而不是假设它）；
  3. `greedy_tiebreak`：predictive greedy 配固定随机 tie-break 顺序。
- 参数范围：K ∈ 1..4，n ∈ 2K..12，delta = K/(n-K)。
- 每个 trial 验证：f(T) <= K/(n-K) OPT；OPT = f(O) = K；误差恰为 eta = (n-K)/K 且两端取到（eta_u = 1，eta_o = (n-K)/K）；f 在 count lattice 上 normalized、monotone、submodular。另有 214 个 trial 做了全子集层面的重扫（2^n 个子集重建 f、重算 band 与 OPT），与 count lattice 结果逐项一致。
- violations：0。eta 不符：0。
- 界取等号（slack = 0）的 trial：1502 / 2400。
- worst slack：0，例如 kind = rule_on_answers、K = 1、n = 11、\|T\| = 1、delta = 1/10、eta = 10、f(T) = 1/10 = 界。
- worst ratio f(T)/OPT：1，出现在 K = 3、n = 6（n = 2K，delta = 1，界本身就是 1，不 binding）。

结构化 case：

| case | 结果 |
|---|---|
| n = 2K（K = 1..4）：delta = 1，eta = 1，界 = 1 | PASS，界以等号成立，此时构造不损失任何东西，陈述在该端点是平凡的 |
| K = 1，n = 2..12，全部 \|T\| <= 1 的输出（88 个） | PASS，f(T) = 1/(n-1) = delta，正好等于界 |
| 每个 K 的最小 n（n = 2K），全部输出穷举（219 个） | PASS，max ratio 均为 1，界不 binding |
| 全局最小 instance K = 1, n = 2 | PASS，delta = 1，eta = 1，K/(n-K) = 1 |

## 4. K = 3、eta = 3/2 running example（三行）

K = 3，delta = 1/eta = 2/3，O = {0,1,2}，T = {3,4,5}：f(O) = 3 = OPT，f(T) = 3 · 2/3 = 2，ratio 2/3 = 1/eta，eta_u = 1、eta_o = 3/2 两端都取到。
n = 6 时陈述常数 K/(n-K) = 1，n = 7 时 3/4，都 >= 2/3，故 f(T) <= K/(n-K) OPT 成立。
n = 8 时 K/(n-K) = 3/5 < 2/3，n = 12 时 1/3 < 2/3：固定 eta = 3/2 的实例给不出陈述常数，陈述在大 n 处用的是它自己的 delta = K/(n-K)（对应 eta = (n-K)/K > 3/2）。

## 5. n = 2K-1 记录（C8 明细）

固定满额输出 T（\|T\| = K），n = 2K-1 时 N \ T 只剩 K-1 个元素，任何 K-set O 与 T 至少交 1 个元素（forced overlap = 2K - n = 1）。此时对所有 O 取最好（最小）比值仍严格大于 delta：

| K | n | delta | min over O 的 f(T)/OPT | 与 delta 比较 |
|---|---|---|---|---|
| 2 | 3 | 1/2 | 3/4 | 3/4 > 1/2，不可达 |
| 3 | 5 | 1/2 | 2/3 | 2/3 > 1/2，不可达 |
| 4 | 7 | 1/2 | 5/8 | 5/8 > 1/2，不可达 |
| 1 | 1 | 1/2 | 1 | 1 > 1/2，不可达 |

一般形式：最好情况是 |T ∩ O| = 1，f(T)/OPT = (1 + delta(K-1))/K，它大于 delta 当且仅当 delta < 1。delta = 1/5、1/50 的 12 个 case 同样全部不可达（见 nobound.json 的 `n_equals_2K_minus_1`）。所以 n >= 2K 这个前提在构造里是实质性的，不是修饰。

## 6. 两个构造的比较（顺便记录，不进正文）

C0 给出 delta - gamma = K/n > 0，故 gamma 版的界 gamma 严格强于陈述常数 K/(n-K)，差一个因子 K/n；gamma <= 1 等价于 n(n-K) >= K^2，在 n = 2K+m 处展开为 K^2 + 3Km + m^2 >= 0，对 n >= 2K 恒成立，这正是 O 保持最优所需。C9 确认 gamma 的取法目的：uniform random O 下 K/n + gamma = K/(n-K)，即 randomized 版恰好落到陈述常数上。两版在 Q1 全部检查下都通过；`results/V11/notes.md` 里"保留 delta 版"的建议与此一致，因为 delta 版直接匹配陈述常数，gamma 版的额外强度只在 randomized 段用得上。

## 7. 复跑的既有脚本

- `results/M0_counterexamples.py`：exit code 0，9 条 PASS，0 条 FAIL，输出末行 `ALL PASS`，耗时约 0.5 秒。该脚本不写任何文件，未被修改。它覆盖 J5 三个反例（含 n = 4, K = 2 的 modular witness），与本次 T1 的 modular 族相邻，作交叉核对。
- `results/J2_core_oracles.py` 等：未复跑，理由是它会覆写已有的 `results/J2_core_oracles.json`，而本次任务禁止改动既有仓库文件。此项记录在 nobound.json 的 `reruns` 字段。

## 8. 状态标签与边界

- 构造 A、B 的 instance 合法性、band 与最小因子、OPT、三类算法的输出界：[VERIFIED-EXHAUSTIVE]（K = 1..4，n = 2K..12，5 个 delta，全子集枚举）。
- delta 与 gamma 的代数关系、randomized 平均恒等式：[VERIFIED-SYMBOLIC]（sympy，residual 为 0）。
- 陈述的量词"任意 deterministic algorithm、arbitrary query access"：oracle 只能覆盖有限多个算法（本次 2400 + 320 个）。"ftilde 的答案与 O 无关，故 transcript 与输出在 f 选定前已固定"这一步在脚本里是按每个被实现算法逐个执行并核对的，不是对全部算法的证明。该归约步维持 [HAND-PROOF-UNREVIEWED]，是本卡唯一未被 oracle 覆盖的环节。
- 无 [FAILED] 项。无违反。

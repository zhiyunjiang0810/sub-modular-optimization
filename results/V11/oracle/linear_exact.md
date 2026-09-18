# V11 oracle 报告：thm:linear-exact（台账 T10c，来源 J6，正文 Theorem 2）

一键复跑：`python3 results/V11/oracle/linear_exact.py`，exit 0 当且仅当全部检查通过。
输出：`results/V11/oracle/linear_exact.log`（全文）、`linear_exact.json`（机器可读）、本文件。
本次运行：29 项检查，0 FAILED，0 violations，16.5 秒，seed 20260918。
全部判定用 `fractions.Fraction` 或 sympy，浮点只出现在括号里的打印值。
没有修改任何仓库既有文件；三个 Q4 脚本用 subprocess 原样复跑。

被检验的陈述（`results/V11/inputs/statement_linear_exact.md`）：K ≥ 2、η > 1、n ≥ 4K⁵，
𝒜_lin = 确定性、≤ nK 次 f̃ 查询、每次查询集合大小 ≤ K、输出 ≤ K 元素；
则 sup_{A∈𝒜_lin} inf_{(f,f̃)} f(A)/OPT = ρ_K(η)，在每个这样的 n 上精确，无渐近。

---

## 一、Criterion C（oracle）

### C1–C3 既有脚本复跑（不修改）

| 脚本 | exit code | 用时 | 关键计数 |
|---|---|---|---|
| `results/Q4_gpt_check.py` | 0 | 2.2 s | `13 symbolic identities: PASS`；`configs=159, edges=111032, DR=207842, balanced=2441` |
| `results/Q4_symbolic_ineq.py` | 0 | 0.5 s | 34 条分支不等式全部 PASS，末行 `ALL PASS` |
| `results/Q4_indep_check.py` | 0 | 8.5 s | `configs checked: 111`，末行 `ALL PASS` |

状态 [VERIFIED-SYMBOLIC]（前两项）与 [VERIFIED-LP 精确有理]（第三项的穷举电池）。
这三项复现的是**族的合法性**（monotone、submodular、band 四类边、归一化、两端校准、
刚性轨迹、F(K,0) = ρ_K），不是 transcript 装配。

### C4 计数链（精确有理 + sympy）[VERIFIED-SYMBOLIC]

逐步验证，11 条全 PASS：

- (a) 固定一对元素同时落入 O 的概率 = C(n−2,K−2)/C(n,K) = K(K−1)/(n(n−1))；
  并用 32 组 (n,K)（n = 4..10）的精确有理穷举交叉核对。
- (b) (K/n)² − K(K−1)/(n(n−1)) = K(n−K)/(n²(n−1)) ≥ 0（K ≤ n），
  故 Pr[|S ∩ O| ≥ 2] ≤ C(K,2)·K(K−1)/(n(n−1)) ≤ C(K,2)(K/n)²。
- (c) 对 nK 次查询取 union：宽松式 = K⁴(K−1)/(2n) ≤ K⁵/(2n)（slack 恰为 K⁴/(2n)）；
  紧式 = K³(K−1)²/(2(n−1))。
- (d) 输出与 O 相交：对 ≤ K 个输出元素取 union，每个落入 O 的概率 K/n，合计 ≤ K²/n。
- (e) 在 n = 4K⁵ 处总量恰为 1/8 − 1/(8K) + 1/(4K³)；粗放读法 1/8 + 1/(4K³)，
  由 1/32 − 1/(4K³) = (K³−8)/(32K³) ≥ 0（K ≥ 2）得 ≤ 1/8 + 1/32 = **5/32 < 1**。
  K = 2..12 的精确值另行列出，例如 K=2, n=128 得 5/32；K=3, n=972 得 29/216；
  K=4, n=4096 得 33/256。紧式在同样的 n 上严格更小（K=2: 255/4064；K=3: 6803/104868）。

### C5 使计数链给出失败概率 < 1 的最小 n [VERIFIED-EXHAUSTIVE + VERIFIED-SYMBOLIC]

两种读法给出两个不同的门槛，K = 2..12 全部逐个精确核对（同时验证 n−1 处不成立）：

- **陈述里写的宽松链** K⁵/(2n) + K²/n < 1 ⟺ n > K⁵/2 + K²，
  最小 n = ⌊K⁵/2 + K²⌋ + 1。K=2: 21；K=3: 131；K=4: 529；K=5: 1588；K=6: 3925。
- **保留 K(K−1)/(n(n−1)) 的紧链** K³(K−1)²/(2(n−1)) + K²/n < 1，
  等价于二次式 n² − (A+B+1)n + B > 0，A = K³(K−1)²/2，B = K²。其较大根落在
  (A+B, A+B+1) 内（因 0 < B < A+B+1），所以最小整数 n 恰为 **A + B + 1 = K³(K−1)²/2 + K² + 1**。
  K=2: 9（handoff 数字 8）；K=3: 64（63）；K=4: 305（304）；K=5: 1026（1025）；K=6: 2737（2736）。

结论（对 handoff 的回答）：handoff 里的 K³(K−1)²/2 + K² **是紧链的严格门槛本身，
不是可取的最小 n**；可取的最小 n 恰比它大 1。写成 "n > K³(K−1)²/2 + K²" 才与链一致。
另外这条链只需要 n 超过一个 K⁵ 量级（甚至 K⁵/2 量级）的数，
所以定理里的 n ≥ 4K⁵ 是充分条件而不是链的最紧输出；4K⁵ 的作用是把总量压到 5/32 这个
有余量的常数上。二次式的根位置那一步标 [HAND-PROOF-UNREVIEWED]（逐 K 的结论是穷举验证的）。

### C6 随机版 ε_n [VERIFIED-SYMBOLIC]

ε_n = K²/n + K⁵/(2n) 与计数链的总量逐项相同；在 n = 4K⁵ 处 ε_n = 1/8 + 1/(4K³) ≤ 5/32。
也就是说随机版的 ε_n 就是同一条链，没有额外损失。

### C7 自写族实现的格点合法性 [VERIFIED-EXHAUSTIVE]

按公式（k1、q、j、Q、δ、C、r_x、h_x、F、H、Ĥ）另写一份实现，在 D 用到的 4 个 (K,η)
乘 2 个极端 split 上逐点检查：8 组 config、392 条边、608 次 DR 比较、48 个 balanced 状态，
全 PASS。逐项含：F(0,0) = H(0,0) = 0、F(0,K) = 1、0 ≤ F ≤ 1、所有一阶差分非负、
所有二阶差分非正、band ΔF/η_u ≤ Δf̃ ≤ η_o ΔF 在四类边上成立、x = 0 处两个 split 端点都达到、
刚性轨迹（d_t 与剩余 O 元素的真实边际）、G(x,y) = Ĝ_{x+y}（x+y ≤ K, y ≤ 1）、
以及 **size > K 处的泄漏确实存在**（8 组全部检出），这正是该族只声称 small-set 不可区分的原因。

---

## 二、Criterion D（对陈述本身的反例搜索）

参数：K ∈ {2,3}，η ∈ {3/2, 2}，n = 128 与 256（K=2，4K⁵ = 128）、972 与 1944（K=3，4K⁵ = 972）。
对手流程：先用 canonical oracle S ↦ Ĥ_{|S|}/η_u 跑出算法的固定 transcript 与输出 T₀，
再**显式搜索**隐藏集 O（与 T₀ 不交、与每个被查询集合至多交 1 个元素；先按冲突图度数做确定性
贪心，失败再做 seeded 随机重启），最后把算法**重放**到真实实例上，核对 transcript 与输出未变，
再用精确有理算 f(T)/OPT。8 个 (K,η,n) 全部找到合法 O，重放全部一致。

### D1 结构化候选（56 个 case，0 违反）

| 候选 | 是否在 𝒜_lin | 结果 |
|---|---|---|
| predictive greedy | 是（例：K=3,n=1944 用 5830 次，集合 ≤ 3） | 全部 ratio = ρ_K，slack 0 |
| top-(K+1) shortlist 再按 f̃ 选最好 K 子集 | 是（n + K + 1 次） | 全部 ratio = ρ_K，slack 0 |
| greedy 加一轮 swap pass | 查询大小 ≤ K，但次数 nK + K(n−K) ≈ 2nK **超出 nK 预算**（已记录） | 全部 ratio = ρ_K，slack 0 |
| random-permutation greedy（3 个 seed） | 是 | 全部 ratio = ρ_K，slack 0 |
| max(forward greedy, backward/deletion greedy) | **否**：backward 需要大小至多 n−1 的查询 | 见下 |

每个 (K,η,n) 的 ρ_K：K=2,η=3/2 是 3/5；K=2,η=2 是 1/2；K=3,η=3/2 是 9/16；K=3,η=2 是 7/15。
所有在类候选的 ratio 都恰等于对应的 ρ_K，最坏 slack ρ_K − ratio = 0，没有任何 ratio 超过 ρ_K。

关于 backward greedy 的记录（按要求点名）：deletion greedy 从全集出发，查询集合大小达到 n−1，
因此不在 𝒜_lin 内，canonical small-set transcript 论证对它不适用。把它直接放到真实实例上跑
（count grid 模拟，ties 按算法自己的"最小下标"规则，O 的下标位置由对手选，试了 8 种放置：
最低、最高、6 个 seeded 随机）：把 O 放在最低下标时 max(forward, backward) 拿到 ratio = 1 = OPT；
但对手可以选到另一种放置，使 ratio 恰回落到 ρ_K（8 个 config 全部如此）。所以在这个族上，
超出大小限制的候选没有真正超过 ρ_K，超过的只是那条论证路径：它的比值依赖 O 的下标放置，
而 small-set 情形下计数链给出的是与放置无关的结论。这条记录不构成对任意大小查询的任何声称，
任意大小的最优值仍 [OPEN]（台账 T12）。

### D2 500 个随机确定性策略（0 违反）

每个策略 = 一串随机查询集合（数量随机取到 min(nK, 256)，每个集合大小随机取 1..K）
加一条只依赖答案向量的固定输出规则（三选一：在被查询的 K-集合里取答案最大者；
按包含该元素的集合的答案和取前 K；用答案向量的哈希做 seeded 选取）。
8 个 config 各 62 个（第一个 66 个），合计 500。
结果：`no_O = 0`（每次都找到合法 O）、`replay_mismatch = 0`、`violations = 0`。
全部 ratio ≤ ρ_K，最小 slack ρ_K − ratio = 0（在 K=2, η=3/2, n=128 处 ratio = 3/5 = ρ_2(3/2)）。

---

## 三、K = 3, η = 3/2 running example（三行以内）

k1 = 4，q = 3/4，j = 2，Q = 9/16，δ = 1/8，C = 4/3；Ĥ = 0, 1/3, 7/12, 37/48；ρ_3(3/2) = 9/16。
F(3,0) = 9/16 = ρ_3，F(0,3) = 1 = OPT；size > K 的泄漏：H(6,0) = 61/48 ≠ 4/3 = H(5,1)。
n ≥ 4K⁵ = 972；宽松链最小 n = 131，紧链最小 n = 64（handoff 数字 63 是严格门槛，非最小 n）。

---

## 四、FAILED 与仍未被 oracle 覆盖的部分

本次没有 FAILED 项，0 个 violation。需要说明的边界：

1. **transcript 归纳与两次平均仍是手写的**。C4/C5 只验证了计数链的代数，D1/D2 只验证了
   有限多个具体算法（56 个结构化 case 加 500 个随机策略）在该族上落在 ρ_K 以下。
   有限计算不能遍历所有自适应确定性算法，所以装配步骤（count-grid → 集合函数的 DR 链接、
   canonical transcript 归纳、随机版两次平均）状态仍是 [HAND-PROOF-UNREVIEWED，来源 J6]，
   与台账 T10c 一致，本次不升级。
2. **"greedy 加一轮 swap pass" 超出 nK 预算**（约 2nK 次），已在 JSON 的 `within_budget`
   字段记录；它仍满足 |S| ≤ K，对手依然找到了合法 O，比值仍是 ρ_K。
   若要把它算进类内，需要把 union bound 的项数从 nK 换成实际次数，
   在 n ≥ 4K⁵ 处仍 < 1（2×1/8 + 1/32 = 9/32）。
3. **C5c′ 关于二次式根位置的一般 K 论证**标 [HAND-PROOF-UNREVIEWED]；逐 K 的结论
   （K = 2..12）是精确穷举的。
4. D 的对手搜索用了固定 seed 的随机重启；每次都先由确定性的按度数贪心成功，所以结论不依赖随机数。

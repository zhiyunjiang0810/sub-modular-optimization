# V11 oracle 报告：thm:linear-anysize（台账 T10d，来源 J7，正文 Proposition）

一键复跑：`python3 results/V11/oracle/linear_anysize.py`，exit 0 当且仅当全部检查通过。
输出：`results/V11/oracle/linear_anysize.log`（全文）、`linear_anysize.json`（机器可读）、本文件。
本次运行：**28 项检查，0 FAILED，0 violations，38.9 秒，seed 20260918**；
D 部分 63 个 structured case + 300 个 random strategy。
全部判定用 `fractions.Fraction` 或 sympy，浮点只出现在括号里的打印值。
没有修改任何仓库既有文件：四个 J7 脚本用 subprocess 原样复跑，
其中 `results/J7_symbolic.py` 会重写自己的 `results/J7_symbolic.json`，
脚本在复跑前后取 sha256 并在有变化时按备份还原（本次 sha256 前后相同，
`14307741cd75d8f6...`，未触发还原；只有 mtime 变化，内容逐字节不变）。

被检验的陈述（`results/V11/inputs/statement_linear_anysize.md`）：K ≥ 3、η > 1，
α_lin(K,η) 为确定性、O(nK) 次**任意大小** f̃ 查询、输出 ≤ K 元素的算法类在 n → ∞ 时的
最优最坏近似比（randomized 按期望），则

    ρ_K(η) ≤ α_lin(K,η) ≤ min{1/η, W_K(η)} ≤ min{1/η, ρ_K(η) + 1/(K(e^{K−1}−K−1))}。

路线一材料（只读，不作为 oracle）：`paper/sections/appendix_proofs.tex` 的
`app:hardness-anysize`（约 1987 行）、`results/J7/linear_anysize.md`、台账 `THEOREM_LEDGER.md` 的
`## T10d`。

---

## 一、Criterion C（oracle）

### C1–C4 既有脚本复跑（不修改，只记录 exit code 与关键计数）

| 编号 | 脚本 | exit code | 用时 | 关键计数（取自其 stdout） |
|---|---|---|---|---|
| C1 | `results/J7_symbolic.py` | **0** | 15.6 s | `PASS 116` + `EXACT 15` + `ASSEMBLY 17` = **148 项**；`FAILED items: none` |
| C2 | `results/J7_grid_check.py` | **0** | 6.0 s | `configs: 99`；`ALL PASS`（含 K=3 三个 η、n = 8..12 的 adversarial simulation 段） |
| C3 | `results/J7_fragment_checks.py` | **0** | 0.3 s | `ALL PASS`（Part 1 F3 反例、Part 2 gap 形状、Part 3 any-size 模拟） |
| C4 | `results/J7_bound18_check.py` | **0** | 0.0 s | `configs: 99`；`ALL PASS`（e 用有理上界，判定精确） |

四个脚本的 stdout 里 FAIL 行数均为 0。C1 的 148 项内部分级：116 项 sympy 恒等式/符号判号
[VERIFIED-SYMBOLIC]、15 项精确有理有限验证 [VERIFIED-LP 精确有理]、17 项 ASSEMBLY
（经典初等不等式与归纳装配）按 J7 原样仍记 [HAND-PROOF-UNREVIEWED]，本次未升级。

### C5 F3 反例的独立精确复算（K = 3，η = 667/500）[VERIFIED-EXHAUSTIVE]

9 项全 PASS。j = 2；旧规则 m = ⌈Kη⌉ − 1 = 4（Kη = 2001/500，⌈·⌉ = 5）；
Ψ 规则给 m = 3，因为 Ψ(2) = 2502/167 > 0 而 Ψ(3) = −4073296/4657463 ≤ 0。
旧规则下

    r_{t*} = −151089222203006/81950355825200625 ≈ −1.8436676776e−3 < 0，

与附录所引的分数逐位相同（两种读法，直接斜率 D(m) 与 excess 读法 max{Q/(Kη), D(m)}，
给出同一个精确分数）。Ψ 规则下 r_{t*} = g_{t*} = 20664743922357/157947123981500 ≥ 0，
收尾合法；plateau 斜率的真实 argmax 也是 m = 3（D(3) = 0.250903569740 > D(4) = 0.250871183525）。
结论：旧截断规则在此参数上给出负的 O-marginal，单调性失败，Ψ 规则修复之。

### C6 running example（K = 3，η = 3/2）[VERIFIED-EXHAUSTIVE]

j = 2，m = 4，t* = 6，q = 3/4，ν = 3，Q = 9/16，B_m = 116，d = 13/58，D = 117/928，C = 4/3。
W_3(3/2) = F(3,0) = **523/928 = 9/16 + 1/928**，ρ_3(3/2) = **9/16**，gap = **1/928** ≈ 1.078e−3。
523/928 ≈ 0.563577586 < 2/3 = 1/η，即该 K-集上界严格低于 unconditional ceiling。

### C7 自写 count-grid 合法性电池（三个 D 配置）[VERIFIED-EXHAUSTIVE]

族按 `results/J7/linear_anysize.md` 的 (4)(6)(9)(10) 重新转写，不 import
`results/J7_grid_check.py`。每个配置检查：归一化 F(0,0) = 0、F(0,K) = 1、H(0,0) = 0，
0 ≤ F ≤ 1，所有一阶差 ≥ 0，三类二阶差 ≤ 0，band ΔF ≤ ΔH ≤ ηΔF 且两个校准端点在 x = 0
达到，any-size profile **H(x+1,0) = H(x,1) 对一切 x**，x > t* 全饱和，
leak 特征（J7 (15)：H 与 size profile 不同的格点必有 y ≥ 2 且 x ≤ t*），
F(K,0) = W_K 与 gap 恒等式 (17)。

| K | η | j | m | t* | 格点 | 边 | 二阶差 | leak 格点 | W_K | ρ_K | gap | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 3/2 | 2 | 4 | 6 | 48 | 80 | 130 | 10 | 523/928 | 9/16 | 1/928 | 0 |
| 3 | 2 | 2 | 5 | 7 | 52 | 87 | 142 | 12 | 2003/4275 | 7/15 | 8/4275 | 0 |
| 3 | 667/500 | 2 | 3 | 5 | 44 | 73 | 118 | 8 | 286046512059143/473841371944500 | 1521500/2522667 | 257841809143/473841371944500 | 0 |

### C8 自写精确 sweep（99 组配置，1089 条断言）[VERIFIED-EXHAUSTIVE]

与 `results/J7_bound18_check.py` 同一张网格（K = 3..12，每个 K 十个 η），但为独立实现，
每组 11 条断言全部通过：(5) η(K−1) < m < Kη；B_m > 0；(7a)(7b) 两条 d-恒等式与
1/(m+1) ≤ d ≤ 1/m；(8) d − 1/(Kη) = (m−η(K−1))/(KηB_m) > 0；(17) gap 恒等式；
(18) 0 < W_K − ρ_K < 1/(K(e^{K−1}−K−1))，其中 e 换成精确有理**上界** 2718281829/10⁹，
使右端成为有理下界，判定保持精确；r_{t*} = g_{t*} ≥ 0；ν^m > e^{K−1}（同一有理上界）。
(18) 最紧的一格是 K = 12、η = 25/2，gap/bound ≈ 0.2126，仍有五倍余量。

### C9 两条 d-恒等式的 sympy 交叉验证 [VERIFIED-SYMBOLIC]

用 η = 1 + u（u > 0）、ν = η/(η−1)、Nm 代表 ν^m 的编码，sympy `simplify` 把
(7a)、(7b)、(8) 三式的残差都化为 0。注：若把 ν 当作与 η 无关的自由符号，(7b) 的残差是
(−ην + η + ν)/(m(−N_mη + η + m))，其分子恰在 ν = η/(η−1) 时为零；这条恒等式依赖 ν 的定义，
已在脚本注释与本行记录。

---

## 二、Criterion D（对陈述本身的反例搜索）

实例按 `results/J7/linear_anysize.md` 的公式自写（不 import 仓库脚本），全部精确有理。
ground set 大小 n，隐藏 K-集 O，f(S) = F(|S \ O|, |S ∩ O|)，预测量 H = η_u f̃；
f(O) = 1，故 ratio = F(|T \ O|, |T ∩ O|)。K = 3，η ∈ {3/2, 2, 667/500}，n = 8..14。
三个 η 的 t* 分别是 6、7、5，故 K + t* = 9、10、8。

### D1 structured（63 个 case，adversarial tie，精确 count-grid DP）

forward predictive greedy、reverse（deletion）greedy、max(forward, reverse) 三种，
tie 全部由 adversary 按最小化终值来打破。由于族在固定 O 的置换下对称，这些值与 O 的位置无关，
即已经是对所有 placement 的最坏值。

| η | W_K(η) | n < K+t* 的 n | 该区 fwd | 该区 rev | n ≥ K+t* 的 n | 该区 fwd = rev = max |
|---|---|---|---|---|---|---|
| 3/2 | 523/928 ≈ 0.563577586 | 8 | = W | **1**（leak） | 9..14 | = W（恰好取等） |
| 2 | 2003/4275 ≈ 0.468538012 | 8, 9 | = W | **1**（leak） | 10..14 | = W（恰好取等） |
| 667/500 | ≈ 0.603675679 | 无 | 不适用 | 不适用 | 8..14 | = W（恰好取等） |

- n ≥ K + t*：21 个 (η,n) 格，每格三个候选，**全部 ratio ≤ W_K(η)**，且都恰好取等，
  worst slack ratio − W = **0**（例如 η = 3/2、n = 9、forward greedy，ratio = W = 523/928）。
- n < K + t*：3 个格（η = 3/2 的 n = 8；η = 2 的 n = 8, 9），**reverse greedy 的 ratio 恰为 1**，
  复现了台账 T10d 的 must-not-claim：有限 n 的 "≤ W_K" 读法为假，
  陈述里的 n → ∞ 量词不能去掉。这三格的 forward greedy 仍 = W。
- 量词附注：这些 n 上的 reverse greedy 本身已超出 O(nK) 预算，
  查询数 Σ_{s=K+1}^{n} s 分别是 30、30、39，而 nK = 24、24、27；
  一般地 reverse greedy 是 Θ(n²) 次查询，固定 K 时不属于线性查询类。
  所以这条 must-not-claim 约束的是**族在有限 n 的性质**，而不是定理所辖算法类里出现了反例。

### D2 random strategies（300 个，任意大小查询）

每个 strategy = 一串随机查询集合（数量在 1..nK 之间随机，每个集合大小在 1..n 之间随机，
即真正的 arbitrary size）+ 一条只读答案向量的固定输出规则（四种：最优被查 K-集、
按答案质量排序取前 K、按同尺寸答案落差排序取前 K、答案向量哈希驱动的固定选取）。
对每个 strategy，adversary 被给足权力：**枚举全部 C(n,K) 个 O placement**，
逐个重放该 strategy 并取 ratio 的最小值。

- 总数 300；n ≥ K+t* 的 leak-free 区 **252** 个，n < K+t* 的 leak 区 48 个。
- leak-free 区：**0 个 violation**，adversary-min ratio 的最大值在每个 (η,n) 格上都恰好等于
  W_K(η)，worst slack ratio − W = **0**。
- leak 区 48 个：0 个超过 W。随机非自适应 strategy 没有利用泄漏，
  adversary 总能找到与输出不交的 O。这一区不作为 PASS/FAIL 判据，只记录。

### D 汇总

- violations：**0**。
- worst slack（leak-free 区，ratio − W_K）：D1 为 0（K=3, η=3/2, n=9, forward greedy，
  ratio = W = 523/928），D2 为 0（K=3, η=3/2, n=9, rule 1, 1 次查询，
  adversary-min ratio = W = 523/928）。上界处处取等，没有任何候选越过 W_K。
- leak 区的最坏值：ratio = 1（reverse greedy，η = 3/2 的 n = 8 与 η = 2 的 n = 8, 9），
  相对 W 的超出量分别为 405/928 与 2272/4275，按上文量词附注记为预期现象。

---

## 三、状态与未声称项

- C1–C4 复跑结论沿用各脚本自身的标签：[VERIFIED-SYMBOLIC]（C1 的 116 项）、
  [VERIFIED-LP 精确有理]（C1 的 15 项、C2、C4）、[HAND-PROOF-UNREVIEWED]（C1 的 17 项 ASSEMBLY）。
- C5–C8 为本 oracle 自写，[VERIFIED-EXHAUSTIVE]（精确有理，无浮点判定）；
  C9 [VERIFIED-SYMBOLIC]。
- D1、D2 [VERIFIED-EXHAUSTIVE]（精确有理；D2 的 adversary 为全枚举，不是抽样）。
- 本 oracle **没有**覆盖、因而仍是 [HAND-PROOF-UNREVIEWED，来源 J7] 的部分：
  count grid 到集合函数的提升、单次查询泄漏概率 ≤ K²(t*+K)²/(2n²) 与 cnK 次的累积界
  (16)、canonical-transcript 归纳、平均论证，以及定理的下界方向（引用 thm:exact）。
  这些是解析/组合论证，不是本次可 oracle 化的对象。
- 本 oracle **不支持**的声称：α_lin = ρ_K（指数小项未消）；有限 n 的 "≤ W_K"（D1 已给出
  ratio = 1 的反例行）；K = 2 情形（(18) 右端在 K = 2 时 e−3 < 0，无内容）；
  把 D 部分 n = 8..14 的结果读成对 n → ∞ 陈述的证明或证伪（n 太小，
  泄漏界 cK³(t*+K)²/(2n) 在该区间远大于 1，这一区间只能做 sanity check）。
- 时间盒：无 sub-step 超时，全流程 38.9 秒。

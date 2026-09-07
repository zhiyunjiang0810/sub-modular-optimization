# H-E: n < 2K 时无限算力确定性天花板的精确形式

任务来源 TASKS6.md §H-E。脚本 `results/H_E_ceiling_small_n.py`，数据 `results/H_E_ceiling_small_n.json`。
一键复现：`cd results && timeout 1800 python3 H_E_ceiling_small_n.py`（全程约 5 秒）。
本文件不改 .tex，不改 THEOREM_LEDGER.md；T8 卡片的建议改法见最后一节。

## 0. 结论（headline）

记 m0 = max(0, 2K − n)（输出集合与任何 K-set 之间被迫的最小 overlap）。

    C(n, K, eta) = K / ( m0 + (K − m0) eta )

对 K ≤ n < 2K 即

    C(n, K, eta) = K / ( (2K − n) + (n − K) eta )
                 = 1 / ( (1 − lam) eta + lam ),      lam = m0/K = (2K − n)/K,

也就是 1/eta 与 1 之间按 lam 的 harmonic interpolation。n ≥ 2K 时 m0 = 0，公式退化为
T8 现有的 1/eta；n = K 时 m0 = K，公式给出 1，与"只有一个 K-set 可选"一致。

状态拆开写：

| 断言 | 状态 |
| --- | --- |
| 对称 f̃ 族的 adversary LP 值 = K/(m + (K−m) eta)（逐 m），K ∈ {2,3,4}, n ∈ {K+1..2K}, eta ∈ {1.5,2,3} | [VERIFIED-LP]（n < 2K 的 48 个 (n,K,eta,m) 点，另加 n = 2K 的 36 个 sanity 点，共 84 点，最大误差 3.34e-16） |
| 上界方向（任何 deterministic 算法在该族上 ≤ C）与下界方向（该族内 LP 值 ≥ C）的手写论证 | [HAND-PROOF-UNREVIEWED]，两侧配平，见 §3 |
| 达到 C 的 witness 实例（modular f，exact Fraction 验证 band、O 取到 max、比值 = 闭式） | [VERIFIED-SYMBOLIC]（6 个点用 Fraction 精确检验） |
| 闭式中的单调性与极限恒等式（对 m、对输出大小 s、m=0 给 1/eta、m=K 给 1、harmonic 形式） | [VERIFIED-SYMBOLIC]（sympy） |
| exhaustive search over predicted values 在 n < 2K 的精确最坏值 = C（f̃ 自由的 LP-B） | [VERIFIED-LP]（18 个 (n,K,eta) 点全部相等） |
| 由此 "C 就是 n < 2K 的精确 deterministic unbounded-query 最优值"，在网格上成立 | [VERIFIED-LP] at grid；一般 (n,K,eta) 为 [CONJECTURE] |
| exhaustive search 在一般 n < 2K 优于 1/eta 的手写证明 | [FAILED]，卡点见 §5 |

## 1. 设置

Ground set N = {0,...,n−1}，K ≤ n < 2K。

Adversary 用经典的 uninformative prediction：f̃(S) = b·|S|。所有 single-element predicted gain
都等于 b，任何 deterministic 算法（不限查询次数、不限查询集合大小）在 f̃ 上的 transcript 与
真实 f 无关，因此输出是一个事先固定的集合 S_out。relabeling 保持 f̃ 不变且把任一 K-set 映到
任一 K-set，所以 S_out = {0,...,K−1} 是 w.l.o.g.；输出大小 |S_out| < K 的情形见 §6。

Definition 1（single-element 版，eta_u = max d/d̃, eta_o = max d̃/d）在 d̃_e(A) ≡ b 时退化成
真实边际增益上的一个两端 box：

    b / eta_o  ≤  d_e(A)  ≤  b · eta_u      对所有 A 和 e ∉ A。

**LP-A（adversary LP / 天花板 LP）**：变量是 f(A)（A ⊆ N，共 2^n 个）与标量 b。

    min f(S_out)
    s.t.  f(empty) = 0；submodularity（相邻形式 d_e(A ∪ {e'}) ≤ d_e(A)）；monotone；
          b/eta_o ≤ d_e(A) ≤ b·eta_u（上面的 box）；b ≥ 0；
          f(A) ≤ 1 对所有 |A| ≤ K；  f(O_m) = 1，

O_m 是一个 overlap |O_m ∩ S_out| = m 的 canonical K-set（取 S_out 的前 m 个元素加 S_out 外的
K − m 个元素，要求 m ≥ 2K − n）。"哪个 K-set 取到 max"用枚举 m 实现：S_out 的 stabiliser 把
同一 m 的所有 K-set 互相映到，所以每个 m 一个代表就够。Adversary 的值 = min over
m ∈ {m0, ..., K}。

b 必须是变量而不是常数：目标是比值 f(S_out)/max_{|A|≤K} f(A)，对 f 的正数缩放不变，
normalization "max = 1" 已经用掉了 f 的尺度，f̃ 的尺度就必须放开（把 b 钉死会让 LP 无解或
人为抬高值，脚本里可用 `fix_b` 复现这一点）。

**LP-B（算法侧）**：变量是 f 与 f̃（各 2^n 个），约束是 f monotone submodular、双边 band、
f̃(Ŝ) ≥ f̃(A) 对所有 |A| ≤ K（即 Ŝ = argmax_{|A|≤K} f̃(A)，tie 由 adversary 打破，Ŝ = {0..K−1}
w.l.o.g.），同样的 normalization；目标 min f(Ŝ)。它给出 exhaustive search over predicted values
在 overlap 类型 m 下的精确最坏值。注意 LP-B 的 f̃ 不限制为对称，也不限制为 submodular（D1）。

方向要分清：LP-A 是"某一个 adversary 族"给出的**上界**（任何确定性算法都不超过它），
LP-B 是"某一个算法"给出的**下界**（存在算法达到它）。两者相等时精确值被夹住。

## 2. 逐点数值（eta_u = eta_o = sqrt(eta)，per (n, K, eta, m)）

LP-A 与闭式 K/(m + (K−m) eta) 的差在下表全部 48 个点上 ≤ 3.4e-16（连 n = 2K 的 sanity 点共
84 个点，最大误差 3.34e-16）。LP-B 列是同一 (n,K,eta,m) 下
exhaustive search 的精确最坏值。

| K | n | eta | m | LP-A | K/(m+(K−m)eta) | LP-B (exhaustive) |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 3 | 1.5 | 1 (m0) | 0.800000000 | 4/5 | 0.800000000 |
| 2 | 3 | 1.5 | 2 | 1.000000000 | 1 | 1.000000000 |
| 2 | 3 | 2 | 1 (m0) | 0.666666667 | 2/3 | 0.666666667 |
| 2 | 3 | 2 | 2 | 1.000000000 | 1 | 1.000000000 |
| 2 | 3 | 3 | 1 (m0) | 0.500000000 | 1/2 | 0.500000000 |
| 2 | 3 | 3 | 2 | 1.000000000 | 1 | 1.000000000 |
| 3 | 4 | 1.5 | 2 (m0) | 0.857142857 | 6/7 | 0.857142857 |
| 3 | 4 | 1.5 | 3 | 1.000000000 | 1 | 1.000000000 |
| 3 | 4 | 2 | 2 (m0) | 0.750000000 | 3/4 | 0.750000000 |
| 3 | 4 | 2 | 3 | 1.000000000 | 1 | 1.000000000 |
| 3 | 4 | 3 | 2 (m0) | 0.600000000 | 3/5 | 0.600000000 |
| 3 | 4 | 3 | 3 | 1.000000000 | 1 | 1.000000000 |
| 3 | 5 | 1.5 | 1 (m0) | 0.750000000 | 3/4 | 0.750000000 |
| 3 | 5 | 1.5 | 2 | 0.857142857 | 6/7 | 0.857142857 |
| 3 | 5 | 1.5 | 3 | 1.000000000 | 1 | 1.000000000 |
| 3 | 5 | 2 | 1 (m0) | 0.600000000 | 3/5 | 0.600000000 |
| 3 | 5 | 2 | 2 | 0.750000000 | 3/4 | 0.750000000 |
| 3 | 5 | 2 | 3 | 1.000000000 | 1 | 1.000000000 |
| 3 | 5 | 3 | 1 (m0) | 0.428571429 | 3/7 | 0.428571429 |
| 3 | 5 | 3 | 2 | 0.600000000 | 3/5 | 0.600000000 |
| 3 | 5 | 3 | 3 | 1.000000000 | 1 | 1.000000000 |
| 4 | 5 | 1.5 | 3 (m0) | 0.888888889 | 8/9 | 0.888888889 |
| 4 | 5 | 1.5 | 4 | 1.000000000 | 1 | 1.000000000 |
| 4 | 5 | 2 | 3 (m0) | 0.800000000 | 4/5 | 0.800000000 |
| 4 | 5 | 2 | 4 | 1.000000000 | 1 | 1.000000000 |
| 4 | 5 | 3 | 3 (m0) | 0.666666667 | 2/3 | 0.666666667 |
| 4 | 5 | 3 | 4 | 1.000000000 | 1 | 1.000000000 |
| 4 | 6 | 1.5 | 2 (m0) | 0.800000000 | 4/5 | 0.800000000 |
| 4 | 6 | 1.5 | 3 | 0.888888889 | 8/9 | 0.888888889 |
| 4 | 6 | 1.5 | 4 | 1.000000000 | 1 | 1.000000000 |
| 4 | 6 | 2 | 2 (m0) | 0.666666667 | 2/3 | 0.666666667 |
| 4 | 6 | 2 | 3 | 0.800000000 | 4/5 | 0.800000000 |
| 4 | 6 | 2 | 4 | 1.000000000 | 1 | 1.000000000 |
| 4 | 6 | 3 | 2 (m0) | 0.500000000 | 1/2 | 0.500000000 |
| 4 | 6 | 3 | 3 | 0.666666667 | 2/3 | 0.666666667 |
| 4 | 6 | 3 | 4 | 1.000000000 | 1 | 1.000000000 |
| 4 | 7 | 1.5 | 1 (m0) | 0.727272727 | 8/11 | 0.727272727 |
| 4 | 7 | 1.5 | 2 | 0.800000000 | 4/5 | 0.800000000 |
| 4 | 7 | 1.5 | 3 | 0.888888889 | 8/9 | 0.888888889 |
| 4 | 7 | 1.5 | 4 | 1.000000000 | 1 | 1.000000000 |
| 4 | 7 | 2 | 1 (m0) | 0.571428571 | 4/7 | 0.571428571 |
| 4 | 7 | 2 | 2 | 0.666666667 | 2/3 | 0.666666667 |
| 4 | 7 | 2 | 3 | 0.800000000 | 4/5 | 0.800000000 |
| 4 | 7 | 2 | 4 | 1.000000000 | 1 | 1.000000000 |
| 4 | 7 | 3 | 1 (m0) | 0.400000000 | 2/5 | 0.400000000 |
| 4 | 7 | 3 | 2 | 0.500000000 | 1/2 | 0.500000000 |
| 4 | 7 | 3 | 3 | 0.666666667 | 2/3 | 0.666666667 |
| 4 | 7 | 3 | 4 | 1.000000000 | 1 | 1.000000000 |

按 (n, K, eta) 取 min（min 总在 m = m0 取到，因为闭式对 m 严格递增，sympy 检查
d/dm 的分子 = K(eta − 1) > 0）：

| K | n | eta | m0 | 天花板 C（LP-A min） | 精确值 | 1/eta | C 相对 1/eta 的提升 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 3 | 1.5 | 1 | 0.800000000 | 4/5 | 0.666667 | +0.133333 |
| 2 | 3 | 2 | 1 | 0.666666667 | 2/3 | 0.500000 | +0.166667 |
| 2 | 3 | 3 | 1 | 0.500000000 | 1/2 | 0.333333 | +0.166667 |
| 3 | 4 | 1.5 | 2 | 0.857142857 | 6/7 | 0.666667 | +0.190476 |
| 3 | 4 | 2 | 2 | 0.750000000 | 3/4 | 0.500000 | +0.250000 |
| 3 | 4 | 3 | 2 | 0.600000000 | 3/5 | 0.333333 | +0.266667 |
| 3 | 5 | 1.5 | 1 | 0.750000000 | 3/4 | 0.666667 | +0.083333 |
| 3 | 5 | 2 | 1 | 0.600000000 | 3/5 | 0.500000 | +0.100000 |
| 3 | 5 | 3 | 1 | 0.428571429 | 3/7 | 0.333333 | +0.095238 |
| 4 | 5 | 1.5 | 3 | 0.888888889 | 8/9 | 0.666667 | +0.222222 |
| 4 | 5 | 2 | 3 | 0.800000000 | 4/5 | 0.500000 | +0.300000 |
| 4 | 5 | 3 | 3 | 0.666666667 | 2/3 | 0.333333 | +0.333333 |
| 4 | 6 | 1.5 | 2 | 0.800000000 | 4/5 | 0.666667 | +0.133333 |
| 4 | 6 | 2 | 2 | 0.666666667 | 2/3 | 0.500000 | +0.166667 |
| 4 | 6 | 3 | 2 | 0.500000000 | 1/2 | 0.333333 | +0.166667 |
| 4 | 7 | 1.5 | 1 | 0.727272727 | 8/11 | 0.666667 | +0.060606 |
| 4 | 7 | 2 | 1 | 0.571428571 | 4/7 | 0.500000 | +0.071429 |
| 4 | 7 | 3 | 1 | 0.400000000 | 2/5 | 0.333333 | +0.066667 |

Sanity row：n = 2K（K = 2,3,4，同样三个 eta，共 9 个 (n,K,eta) 组合）LP-A 给出 1/eta，与 T8 现有陈述一致
（脚本里作为 sanity 行跑了，见 JSON 的 `lpA` 中 n = 2K 的行）。

闭式与 1/eta 的差（sympy 化简）：C − 1/eta = m(eta − 1) / (eta (K eta − m eta + m))，
eta > 1 且 m ≥ 1 时严格为正。

## 3. 两侧手写论证（[HAND-PROOF-UNREVIEWED]，被上面的 LP 数值配平）

先做 §1 的尺度归一：把 f 换成 g = (eta_o / b) f，box 变成 1 ≤ d^g_e(A) ≤ eta_u eta_o = eta，
比值目标不变。以下写 1 和 eta 就是这个归一后的 box。

**下界（adversary 达不到更低）**：设 O 是 max K-set，I = S_out ∩ O，|I| = m，x = f(I)。
沿 I 到 S_out 的链，每步增益 ≥ 1，得 f(S_out) ≥ x + (K − m)。沿 I 到 O 的链用 submodularity，
f(O) ≤ x + sum_{e ∈ O\I} d_e(I) ≤ x + (K − m) eta。又 x ≥ m（∅ 到 I 每步 ≥ 1）。于是

    f(S_out)/f(O) ≥ (x + K − m) / (x + (K − m) eta) ≥ K / (m + (K − m) eta),

第二步因为该式对 x 单调不减（sympy：d/dx 的分子 = (K − m)(eta − 1) ≥ 0），在 x = m 取最小。

**上界（adversary 达得到）**：取 modular f，权重 eta 给 O\S_out 的 K − m 个元素，权重 1 给其余
所有元素。则 f(S_out) = K，f(O) = m + (K − m) eta，而任何 K-set 至多含这 K − m 个重元素，
所以 O 确实取到 max（|N \ S_out| = n − K ≥ K − m 保证 O 存在）。比值恰为
K/(m + (K − m) eta)。gains 只取 1 和 eta 两个值，归一回去就是 1/sqrt(eta) 与 sqrt(eta)，
两端都被取到，因此 error 恰为 (eta_u, eta_o)，与 T8 构造的"误差恰为 (eta_u, eta_o)"同款。
这个 witness 在 6 个 (K, n, eta) 点上用 Fraction 精确验证（band、O 取 max、比值 = 闭式）
[VERIFIED-SYMBOLIC]。

**对 m 取 min**：闭式对 m 严格递增，adversary 取 m = m0 = max(0, 2K − n)，得到 §0 的 C。
m0 是被迫的：|S_out| = |O| = K 且 |N| = n 给出 |S_out ∩ O| ≥ 2K − n。

**空洞性检验**：去掉 "deterministic" 结论不成立（randomized 见 §7）；去掉 "n < 2K" 公式退化成
1/eta，即 T8 现有内容；去掉 "unbounded query" 不改这里的任何一步（构造对查询次数没有假设），
所以正文里不要把这条写成 query-complexity 结果。

## 4. split 依赖性检查（eta_u, eta_o 的分法）

Definition 1 允许任意 (eta_u, eta_o) 的分法。T0 卡片把"值只依赖乘积"标为 LP 观察加一行
scaling 论证。对**本族**（f̃ = b|S|，b 自由）这一行是完整的：band 退化成
b/eta_o ≤ d_e(A) ≤ b·eta_u，令 g = (eta_o/b) f 得 1 ≤ d^g ≤ eta_u eta_o，与分法无关；
目标是比值，对 g 的正数缩放不变。

数值确认（4 个点、每点 4 种分法，全部相同，spread ≤ 1.1e-16）：

| K | n | eta | (sqrt,sqrt) | (eta,1) | (1,eta) | (eta/1.25, 1.25) |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | 5 | 2 | 0.600000000 | 0.600000000 | 0.600000000 | 0.600000000 |
| 3 | 4 | 3 | 0.600000000 | 0.600000000 | 0.600000000 | 0.600000000 |
| 4 | 6 | 1.5 | 0.800000000 | 0.800000000 | 0.800000000 | 0.800000000 |
| 2 | 3 | 3 | 0.500000000 | 0.500000000 | 0.500000000 | 0.500000000 |

第三种写法（把 band 换成它的 split-free 后果：变量 L, U，L ≤ d_e(A) ≤ U，U ≤ eta·L）在同样
4 个点给出同样的值，说明这个消元是等价的而不是巧合。

**这个检查确立了什么、没确立什么**：确立的是"在 f̃ = b|S| 的对称族里，LP-A 的值只依赖
eta = eta_u eta_o"，这有 §4 第一段的完整 scaling 论证加 LP 数值双证。**没有**确立 Definition 1
在一般 f̃ 下 "只依赖乘积"（T0 禁止声称的那一条）：一般 f̃ 的尺度不能自由缩放掉，
LP-B（f̃ 自由）没有做 split 扫描，本次不涉及。

## 5. 算法侧（matching upper bound），只说能支持的

T8 现有的 converse 是：exhaustive search over predicted values 在**任何**实例上 ≥ f(O*)/eta，
证明只用了 f̃(S) ≤ eta_o f(S)、f̃(S) ≥ f(S)/eta_u 与 argmax。这条在 n < 2K 仍然成立，但
1/eta 在 n < 2K 已经不是正确的 benchmark：C > 1/eta。

LP-B 的结果：在全部 18 个 (n, K, eta) 点上，exhaustive search 的精确最坏值**恰好等于**
LP-A 的天花板 C，而且逐 m 也相等（见 §2 表最后一列）。所以在网格上

    n < 2K 的 deterministic unbounded-query 精确最优值 = C(n, K, eta)，由 exhaustive search 达到。

状态：[VERIFIED-LP] at grid（K ≤ 4, n ≤ 7, eta ∈ {1.5, 2, 3}）；一般 (n, K, eta) 是
[CONJECTURE]。

**手写证明的卡点 [FAILED]**。自然的两步分解走不通：

- (P1) 沿 I = Ŝ ∩ O* 分链，f̃(Ŝ) ≤ f̃(I) + eta_o (f(Ŝ) − f(I))，f̃(O*) ≥ f̃(I) + (f(O*) − f(I))/eta_u，
  配合 f̃(Ŝ) ≥ f̃(O*) 得 **f(Ŝ) ≥ f(I) + (f(O*) − f(I))/eta**。这一步是干净的，
  且已经比 1/eta 严格好（只要 f(I) > 0）。[HAND-PROOF-UNREVIEWED]
- (P2) 要从 (P1) 推出 C，等价于需要 **f(I) ≥ m/(m + (K − m) eta) · f(O*)**（代数等价，已核对）。
- 但 LP-B 直接对 f(I) 取 min 的结果是 **0**（脚本 `objective="I"`，除 m = K 外所有点都是 0）。
  也就是说 (P2) 作为独立引理是假的：存在满足全部约束的实例使 f(Ŝ ∩ O*) = 0，此时 f(Ŝ) 仍然
  ≥ C（因为该实例并不是 f(Ŝ) 的最坏点）。两个目标在不同的顶点取到，所以 C 不能由
  (P1) + (P2) 逐步得到，必须联合处理。

也就是说，"exhaustive search 在 n < 2K 达到 C"目前只有 LP 证据，没有手写证明；下一步应该走
项目里 N1 的老流程：取 LP-B 在 m = m0 处的 dual multipliers，看哪些 argmax 约束
（Ŝ 对哪些 K-set 的比较）进入支撑集，再据此拼 inequality。本次时间预算内没做。

**因此正文里目前只能写**：(a) 上界 C 对任何确定性算法成立（§3 有手写证明加 LP）；
(b) 已知的可达保证是 1/eta（T8 原有，对所有 n 成立）；(c) 在 K ≤ 4, n ≤ 7 的网格上
exhaustive search 恰好达到 C [VERIFIED-LP]，一般情形 [CONJECTURE]。不要写成 "exhaustive
search achieves the exact optimum for n < 2K"。

## 6. 输出集合大小的检查

算法可以输出 |S_out| = s < K。对每个 s，被迫 overlap 是 m_s = max(0, s + K − n)，把 §3 的
论证照抄一遍得 s/(m_s + (K − m_s) eta)。LP 逐 s 枚举全部 K-set 作为 O（不用对称性缩减）的
结果与之一致，且对 s 递增（sympy：d/ds 的分子 = K + n(eta − 1) > 0），所以输出满 K 个元素
对算法最优，§1 的 w.l.o.g. 成立 [VERIFIED-LP]：

| K | n | eta | s=1 | s=2 | s=3 | s=4 |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | 5 | 2 | 0.166666667 | 0.333333333 | 0.600000000 | |
| 3 | 4 | 2 | 0.166666667 | 0.400000000 | 0.750000000 | |
| 4 | 6 | 2 | 0.125000000 | 0.250000000 | 0.428571429 | 0.666666667 |

## 7. 未涉及 / 仍然 OPEN

- **randomized 版**：本次只做 deterministic。T8 的 randomized 上界 (1 − K/n)/eta + K/n 的推导
  对任何 n 都成立（O 均匀随机、与随机串独立），n < 2K 时它给出的数比 C 松，例如
  K = 3, n = 5, eta = 2 时是 0.8 而 C = 0.6，两者不矛盾（randomized 值 ∈ [C, 0.8]），但
  randomized 在 n < 2K 的精确值仍然 [OPEN]。
- **eta 网格**：只做了 {1.5, 2, 3}，都 > 1。eta = 1 时闭式给 C = K/K = 1，与"预测无误差时
  exhaustive 找到最优"一致，但没跑 LP 确认。
- **K ≥ 5**：n ≤ 9 的全格点 LP（2^9 = 512 变量）应该还跑得动，本次没跑。
- LP-B 的 split 扫描（f̃ 自由时值是否只依赖乘积）没做，见 §4 末。

## 8. 建议的 THEOREM_LEDGER.md T8 卡片改法（本文件不改台账，请人工确认后落台账再改 .tex）

在 T8 卡片里，把"禁止声称"第一条 `n<2K 时的值（[OPEN]，明晚 E 项）` 替换为下面三行，
其余各行不动：

```
- n<2K（H-E）：对称 f̃=b|S| 族给出的天花板为 C(n,K,η)=K/(m0+(K−m0)η)，m0=max(0,2K−n)
  =1/((1−λ)η+λ)，λ=m0/K；n≥2K 时退化为 1/η。逐 overlap 类型 m 的值为 K/(m+(K−m)η)，对 m 递增。
  状态：[VERIFIED-LP]（K∈{2,3,4}, n∈{K+1..2K}, η∈{1.5,2,3}，84 点，其中 n<2K 的 48 点，误差 ≤3.4e-16，
  results/H_E_ceiling_small_n.py）+ 两侧手写论证 [HAND-PROOF-UNREVIEWED] + witness 的
  Fraction 精确验证 [VERIFIED-SYMBOLIC]。输出大小 s<K 更差（s/(m_s+(K−m_s)η) 对 s 递增）。
- 禁止声称：C 由某个算法达到（exhaustive search 在 K≤4, n≤7 网格上恰好达到 C 是
  [VERIFIED-LP] at grid，一般情形 [CONJECTURE]，手写证明卡在 f(Ŝ∩O*) 可以为 0，
  两步分解失效，见 results/H_E_ceiling_small_n.md §5）；C 是 randomized 的值（randomized
  在 n<2K 仍 [OPEN]，(1−K/n)/η+K/n 只是上界且在 n<2K 比 C 松）；"值只依赖 η_uη_o" 推广到
  一般 f̃（§4 的 scaling 论证只对 f̃=b|S| 这一族成立）。
```

同时 T8 的陈述行可以把 `n ≥ 2K` 改成 `n ≥ 2K（一般 n 的天花板见下一行的 C(n,K,η)）`，
但 .tex 里的 thm:ceiling 建议**先不改陈述**，只在 Theorem 后的说明句里把
"the exact ceiling for n<2K is open" 换成一句带状态标签的话，例如：

> For n<2K the same construction gives the sharper ceiling K/((2K−n)+(n−K)\eta), which is
> attained by exhaustive search in the LP-verified range K\le4, n\le7 (Conjecture for general
> parameters).

（措辞按 K9 的规矩：比较的是 worst-case guarantee，不写 "any algorithm is the same"。）

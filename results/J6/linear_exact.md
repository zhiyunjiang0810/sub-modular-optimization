# J6 — 同预算类（查询集合大小 ≤ K）的精确 hardness：α*_{n,K}(η) = ρ_K(η)

来源：GPT 对 GPT_PROMPT_LINEAR_EXACT.md 的回答，2026-09-13，只读仓库快照 1832e26e；GPT 未交付文件，本文件由 Claude 从对话逐字转录（数学内容未改动，仅加本段说明与状态行）。
状态：[HAND-PROOF-UNREVIEWED，来源 J6]；GPT 自报 13 项符号恒等式 [VERIFIED-SYMBOLIC]，159 组有理参数（111,032 条边、207,842 次 DR 比较、2,441 个 balanced 状态）精确检查通过。Claude 已手推关键步骤（拼接不等式、Cq=η(K−1)/K、四类边比值、截断三区间、值 = V_j）。升级条件：results/ 自写 sympy 独立验证 + 作者复核。
应用：闭合 cor:greedybudget 的夹逼区间；greedy 在 𝒜_lin（≤ nK 次查询、每次 |S| ≤ K）内精确最优，n ≥ 4K^5。

---

**目标可以闭合，而且可以加强为：对每个 n ≥ 4K^5，确定性算法在该查询预算类内的最优最坏比已经精确等于 ρ_K(η)，无需取 n → ∞。**

关键是只要求大小 ≤ K 的集合满足 (b)。下面的构造允许较大集合上的 y = 1 查询泄漏信息，从而避开 N4 的长程约束。

## §1 闭式：F, G 与参数

### 1.1 Parameters

Fix K ≥ 2, η > 1, η_u, η_o ≥ 1, η_u η_o = η. Set

k_1 = (K−1)η + 1,   q = (K−1)η / k_1,

and choose j = max{0, K − ⌊η⌋}. Thus 0 ≤ j ≤ K−1, and

K − j ≤ η.   (1)

Define Q = q^j, δ = Q/(Kη), C = k_1/K, [z]_+ = max{z, 0}.

For every integer x ≥ 0, define two residual sequences:

r_x = q^x (0 ≤ x ≤ j);  r_x = [Q − (x−j)δ]_+ (x ≥ j).   (2)

h_x = ((K−1)/K) q^x (0 ≤ x ≤ j);  h_x = [((K−1)/K) Q − (x−j)δ]_+ (x ≥ j).   (3)

The two definitions agree at x = j.

Let N = B ⊔ O, |O| = K, |B| = n−K. For S ⊆ N write x = |S∩B|, y = |S∩O|, c_y = (K−y)/(K−1) (1 ≤ y ≤ K).

### 1.2 The true objective

F(x,y) = 1 − r_x (y = 0);  F(x,y) = 1 − c_y h_x (1 ≤ y ≤ K).   (4)

### 1.3 The predictor

Scaled predictor H = η_u G:

H(x,0) = C − r_x − (η−1) h_x;  H(x,y) = C − η c_y h_x (1 ≤ y ≤ K);  G(x,y) = H(x,y)/η_u.   (5)

These formulas define the entire set functions, including all sets larger than K.

### 1.4 Analytic tail extension

Truncation thresholds α = j + (K−1)η, β = j + Kη.   (6)

For integer x ≥ α, h_x = 0, so F(x,y) = 1 and G(x,y) = C/η_u for every y ≥ 1. For integer x ≥ β both residuals vanish, so F(x,y) = 1, G(x,y) = C/η_u for every y.   (7)

Thus T = ⌈j + Kη⌉ is a valid saturation threshold. Positive parts handle noninteger thresholds. There is no requirement that T ≤ n − K.

## §2 对 (a)(b)(c) 的证明

### 2.1 Residual inequalities

p_x = r_x − r_{x+1}, s_x = h_x − h_{x+1}.   (8)

Claims: p_x ≥ s_x ≥ 0, p_{x+1} ≤ p_x, s_{x+1} ≤ s_x   (9);  and r_x − h_x ≥ h_x/(K−1) ≥ 0   (10).

Proof of (9). For x < j: p_x = q^x/k_1, s_x = ((K−1)/K) q^x/k_1, nonnegative and decreasing. For x ≥ j: p_x = min{δ, r_x}, s_x = min{δ, h_x}   (11); since r_x ≥ h_x ≥ 0 this gives p_x ≥ s_x ≥ 0, each nonincreasing. If j ≥ 1, at the junction p_{j−1} = Q/(q k_1) = Q/((K−1)η) ≥ δ and s_{j−1} = ((K−1)/K)·Q/(q k_1) = δ   (12), so neither sequence increases at the junction.

Proof of (10). For x ≤ j equality: r_x − h_x = q^x/K = h_x/(K−1). For x ≥ j put z = (x−j)δ, A = ((K−1)/K)Q. If 0 ≤ z ≤ A: (r_x − h_x) − h_x/(K−1) = z/(K−1) ≥ 0   (13). If A ≤ z ≤ Q: h_x = 0 and r_x − h_x = Q − z ≥ 0. If z ≥ Q both are zero. ∎

### 2.2 Monotonicity, submodularity, normalization of F

Δ_x F(x,0) = p_x;  Δ_x F(x,y) = c_y s_x (1 ≤ y ≤ K)   (14)
Δ_y F(x,0) = r_x − h_x;  Δ_y F(x,y) = h_x/(K−1) (1 ≤ y < K)   (15)

Nonnegative by (9)–(10). Diminishing returns: x-marginals decrease with x (p, s nonincreasing) and with y (p_x ≥ s_x, then decreasing c_y); the first y-marginal decreases with x since (r_x − h_x) − (r_{x+1} − h_{x+1}) = p_x − s_x ≥ 0; later y-marginals decrease with x since h_x decreases; y-marginals decrease with y by (10) and are then constant. Adjacent count-grid comparisons imply DR for the set function by chaining single-element additions. Hence F is monotone submodular, F(0,0) = 0, F(0,K) = 1, 0 ≤ F ≤ 1 on the grid (16), so O is optimal with OPT = 1.

### 2.3 Edge classes and exact calibration

| Edge class | ΔF | ΔH = η_u ΔG |
|---|---|---|
| B-edge, y = 0 | p_x | p_x + (η−1)s_x |
| B-edge, 1 ≤ y ≤ K | c_y s_x | η c_y s_x |
| O-edge, y = 0 | r_x − h_x | r_x − h_x |
| O-edge, 1 ≤ y < K | h_x/(K−1) | η h_x/(K−1) |

Since 0 ≤ s_x ≤ p_x, p_x ≤ p_x + (η−1)s_x ≤ η p_x; the other classes directly. Thus ΔF ≤ ΔH ≤ η ΔF, i.e. ΔF/η_u ≤ ΔG ≤ η_o ΔF   (17). Ratios (18): (1 + (η−1)s_x/p_x)/η_u; η_o; 1/η_u; η_o. Both extrema attained on positive edges at x = 0: (G(0,1)−G(0,0))/(F(0,1)−F(0,0)) = 1/η_u and (G(0,2)−G(0,1))/(F(0,2)−F(0,1)) = η_o   (19), so the actual factors are exactly (η_u, η_o). Zero-gain edges have ΔH = ΔG = 0. H(0,0) = C − 1 − (η−1)(K−1)/K = 0, so G(∅) = 0. This proves (a).

### 2.4 Indistinguishability and the rigid greedy trajectory

No truncation on the trajectory: (K−j)δ ≤ ηδ = Q/K ≤ ((K−1)/K)Q   (20).

Define for 0 ≤ s ≤ K: Ĥ_s = C(1 − q^s) (s ≤ j); Ĥ_s = C(1−Q) + η(s−j)δ (j ≤ s ≤ K)   (21); Ĝ_s = Ĥ_s/η_u.

For y = 0: H(x,0) = Ĥ_x (0 ≤ x ≤ K). For y = 1, x < j: H(x,1) = C − η((K−1)/K)q^x = C(1 − q^{x+1}) = Ĥ_{x+1}   (22), using Cq = η(K−1)/K. For j ≤ x ≤ K−1: H(x,1) − H(x,0) = Q/K = ηδ, hence H(x,1) = Ĥ_{x+1}   (23). Therefore

G(x,y) = Ĝ_{x+y} whenever x + y ≤ K, y ≤ 1.   (24)

This proves (b). At every state (t,0), G(t+1,0) = G(t,1): all remaining B-elements and all O-elements have identical predicted marginal gains; with adversarial ties and n ≥ 2K greedy selects K elements of B. True selected gains d_t = q^t/k_1 (t < j), q^j/(Kη) (j ≤ t < K)   (25); every remaining optimal element has true marginal g_{t,i} = r_t − h_t = q^{min(t,j)}/K   (26); the common predicted marginal at step t is q^{min(t,j)}/(Kη_u)   (27).

### 2.5 Value, dependence on n, integer breakpoints

For every K-set T ⊆ B: F(T)/F(O) = F(K,0) = 1 − Q + (K−j)δ = V_j(η)   (28).
V_{j+1}(η) − V_j(η) = q^j(η − K + j)/(Kη k_1)   (29), so j = max{0, K − ⌊η⌋} is a minimizer; at integer η = m (2 ≤ m ≤ K) the branches j = K−m and j = K−m+1 tie. Hence

F(T)/F(O) = ρ_K(η) for every n ≥ 2K and every disjoint K-set T.   (30)

Thus (c) holds with ρ_K^{(n)}(η) ≡ ρ_K(η); no residual approximation error.

### 2.6 Why this does not contradict the N4/F3 excess

N4 requires all y ≤ 1 states of all sizes to be canonical; its fixed-K limit is V_j plus a positive excess (e.g. K=4, η=2: W_4(2) = 38065/84721 = 22/49 + 27/84721 > ρ_4(2)). This construction only guarantees (24); e.g. K=3, η=3/2, j=2 gives H(6,0) = 61/48 ≠ H(5,1) = 4/3   (31). It therefore neither proves the legality of the original F3 formula nor any arbitrary-size-query hardness; it solves the size-≤K target.

## §3 Theorem (exact optimality at the greedy query budget) — [HAND-PROOF-UNREVIEWED]

Let K ≥ 2, η > 1, n ≥ 4K^5. Consider deterministic algorithms that access only G, make at most nK value queries, query only sets of cardinality ≤ K, and return a set of cardinality ≤ K. For every such algorithm 𝒜 and every split η_u η_o = η there is an instance with normalized monotone submodular F, predictor G, actual single-element factors exactly (η_u, η_o), such that F(𝒜^G)/OPT ≤ ρ_K(η)   (32). Combined with the exact predictive-greedy guarantee,

sup_𝒜 inf_{(F,G)} F(𝒜^G)/OPT = ρ_K(η)   (33)

for this deterministic query class.

Proof. Use the family (2)–(5) indexed by the hidden K-set O. Run 𝒜 against the canonical oracle S ↦ Ĝ_{|S|} (|S| ≤ K); this fixes queries S_1..S_Q (Q ≤ nK) and output T_0 independently of O. Choose O uniformly among K-subsets. Pr(|S_i ∩ O| ≥ 2) ≤ C(K,2)(K/n)^2; Pr(T_0 ∩ O ≠ ∅) ≤ K^2/n. Hence Pr[∃i: |S_i∩O| ≥ 2 or T_0∩O ≠ ∅] ≤ nK·C(K,2)(K/n)^2 + K^2/n ≤ K^5/(2n) + K^2/n ≤ 1/8 + 1/32 = 5/32 < 1   (34). Fix O outside the bad event. By induction over queries the actual execution agrees with the canonical execution (identical previous answers imply the same next query, and (24) supplies the same answer), so the output is T_0, disjoint from O; monotonicity and (30) give F(T_0) ≤ F(K,0) = ρ_K(η); OPT = 1. Predictive greedy uses Σ_{t=0}^{K−1}(n−t) = nK − K(K−1)/2 ≤ nK queries of size ≤ K and supplies the opposite inequality. ∎

Randomized corollary: for every randomized algorithm with the same restrictions there is a single instance with E[F(𝒜^G)]/OPT ≤ ρ_K(η) + K/n + K^5/(2n)   (35) (fix the seed, use its canonical transcript; on the agreement event F(T_0) ≤ ρ_K + |T_0∩O|/K since each O-element has singleton value 1/K and submodularity bounds its marginal by 1/K; on failure F ≤ 1; average over O then over the seed). The randomized class matches asymptotically for fixed K, η as n → ∞; no exact finite-n claim.

## §4 复算脚本（GPT 原样；H 始终表示 η_u G）

```python
from fractions import Fraction as R
from math import ceil
import sympy as sp

# ---------- General symbolic branch identities ----------
K, E, Q, z, y = sp.symbols("K E Q z y", positive=True)
p, s, r, h = sp.symbols("p s r h", real=True)
j = sp.symbols("j", integer=True, nonnegative=True)

k1 = (K - 1) * E + 1
q = (K - 1) * E / k1
D = Q / (K * E)
A = Q * (K - 1) / K
C = k1 / K

identities = [
    D - (K - 1) / K * Q / (q * k1),
    (K - 1) / K * Q / (q * k1) - D,
    C - Q - (E - 1) * Q * (K - 1) / K - C * (1 - Q),
    C - E * Q * (K - 1) / K - C * (1 - q * Q),
    C - (Q - z) - (E - 1) * (A - z) - (C * (1 - Q) + E * z),
    C - E * (A - z) - (C * (1 - Q) + E * (z + D)),
    (Q - z) - (A - z) - (A - z) / (K - 1) - z / (K - 1),
    (C - (r - p) - (E - 1) * (h - s)) - (C - r - (E - 1) * h) - (p + (E - 1) * s),
    (C - E * h) - (C - r - (E - 1) * h) - (r - h),
    (C - E * (K - y) * (h - s) / (K - 1)) - (C - E * (K - y) * h / (K - 1)) - E * (K - y) * s / (K - 1),
    (C - E * (K - y - 1) * h / (K - 1)) - (C - E * (K - y) * h / (K - 1)) - E * h / (K - 1),
    1 - Q + (K - j) * D - (1 - Q * (1 - (K - j) / (K * E))),
    (1 - q * Q * (1 - (K - j - 1) / (K * E))) - (1 - Q * (1 - (K - j) / (K * E))) - Q * (E - K + j) / (K * E * k1),
]
assert all(sp.cancel(expr) == 0 for expr in identities)
print("13 symbolic identities: PASS")

# ---------- Exact finite-parameter checks ----------
counts = dict(configs=0, edges=0, DR=0, balanced=0)
for k in range(2, 13):
    etas = sorted({R(1001, 1000), R(5, 4), R(3, 2), R(7, 4), R(2), R(9, 4), R(5, 2), R(3),
                   R(k) - R(1, 3), R(k), R(k) + R(1, 3), R(k + 1)})
    for e in etas:
        js = {max(0, k - e.numerator // e.denominator)}
        if e.denominator == 1 and 2 <= e <= k:
            js.add(k - int(e) + 1)
        for jj in js:
            counts["configs"] += 1
            kk = (k - 1) * e + 1
            qq = (k - 1) * e / kk
            Qj = qq ** jj
            delta = Qj / (k * e)
            const = kk / k
            end = jj + ceil(k * e) + 2

            def values(x, y):
                if x <= jj:
                    r = qq ** x
                    h = R(k - 1, k) * r
                else:
                    zz = (x - jj) * delta
                    r = max(R(0), Qj - zz)
                    h = max(R(0), R(k - 1, k) * Qj - zz)
                if y == 0:
                    return 1 - r, const - r - (e - 1) * h
                c = R(k - y, k - 1)
                return 1 - c * h, const - e * c * h

            tab = {(x, y): values(x, y) for x in range(end + 1) for y in range(k + 1)}
            assert tab[0, 0] == (0, 0)
            assert tab[0, k][0] == 1
            assert all(0 <= f <= 1 for f, H in tab.values())
            for x in range(end + 1):
                for y in range(k + 1):
                    for dx, dy in [(1, 0), (0, 1)]:
                        xx, yy = x + dx, y + dy
                        if xx > end or yy > k:
                            continue
                        df = tab[xx, yy][0] - tab[x, y][0]
                        dH = tab[xx, yy][1] - tab[x, y][1]
                        assert 0 <= df <= dH <= e * df
                        counts["edges"] += 1
                        for sx, sy in [(1, 0), (0, 1)]:
                            if xx + sx > end or yy + sy > k:
                                continue
                            df2 = tab[xx + sx, yy + sy][0] - tab[x + sx, y + sy][0]
                            assert df >= df2
                            counts["DR"] += 1
                    if x + y <= k and y <= 1:
                        assert tab[x, y][1] == tab[x + y, 0][1]
                        counts["balanced"] += 1
            for t in range(k):
                df = tab[t + 1, 0][0] - tab[t, 0][0]
                assert df == (qq ** t / kk if t < jj else delta)
                assert tab[t, 1][0] - tab[t, 0][0] == qq ** min(t, jj) / k
                assert tab[t + 1, 0][1] == tab[t, 1][1]
            rho = min(1 - qq ** a * (1 - R(k - a, k) / e) for a in range(k))
            assert tab[k, 0][0] == rho
            assert tab[0, 1][1] == tab[0, 1][0]
            assert tab[0, 2][1] - tab[0, 1][1] == e * (tab[0, 2][0] - tab[0, 1][0])
print(counts)
# GPT reported: configs=159, edges=111032, DR=207842, balanced=2441
```

证据范围：一般参数的符号运算核对各分支恒等式；截断处的非负性、分支覆盖和全局 submodularity 由 §2.1–2.2 的证明承担，不能仅由有限循环推出。

## §5 GPT 三句话总评

这个双残差截断构造满足全部 (a)(b)(c)，并精确实现所要求的刚性轨迹，比值对 n ≥ 2K 恒等于 ρ_K(η)。结合已有 transcript 论证，可将 T10b 升级为 n ≥ 4K^5 时确定性 greedy 查询预算类的精确最优性，而随机类得到固定 K 下的渐近精确最优性。它依赖查询大小限制，主动放弃较大集合上的 y ≤ 1 不可区分性，因此不能用于声称任意大小查询下的同样结论。

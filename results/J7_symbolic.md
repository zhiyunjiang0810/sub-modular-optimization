# J7 独立符号验证报告：results/J7/linear_anysize.md 的全部恒等式与不等式

脚本：`results/J7_symbolic.py`（`python3 results/J7_symbolic.py`，约 18 秒，exit 0 当且仅当没有 FAILED）
数据：`results/J7_symbolic.json`（逐项状态、key identity 字符串、S8 分支表、S12 sweep 表）
对象：`results/J7/linear_anysize.md`（来源状态 [HAND-PROOF-UNREVIEWED，来源 J7]，其自报的 8 项符号恒等式在本次验证中不作为前提使用）

本次统计：148 个条目，其中 sympy 恒等式或 sympy assumption engine 判定的符号不等式 116 项，精确有理数有限验证 15 项，未被 oracle 判定而显式登记为 assembly 的 17 项，FAILED 0 项。

## 0. 摘要

- J7 构造合法性所依赖的**全部代数恒等式**（(7) 两式、(8)、(11)、(12)、(13)、(14)、(17)，以及 3.3 节四类边的 ΔF/ΔH 表）在一般 (K, η, m, j) 上由 sympy 逐项确认为恒等于零，状态 [VERIFIED-SYMBOLIC]。
- 全部符号不等式在把 domain 编码成"符号可见"形式后（K = 3 + w，η = 1 + u，q^x / q^j / ν^m / ν^l / ν^(−t) 用正符号代入，case 假设用带符号 slack 代入）由 assumption engine 判定，状态 [VERIFIED-SYMBOLIC]。
- 剩下 17 项是显式登记的 assembly：classical analytic facts（(1+1/u)^(u+1) > e、e^(K−1) > K、Bernoulli、幂函数单调性）与 integer/logic assembly（归纳法原理、凹函数单交叉、ceiling 分类、两条 replacement lemma 的串联等）。它们的每个代数成分都已符号确认，缺的是把成分接起来的那一步，状态 [HAND-PROOF-UNREVIEWED]。
- 本次把原本较重的三条 assembly 收紧成了单句残留：K g ≥ r 的平台段由 chord 恒等式（S6.7a）归约到唯一一条初等不等式 m(ν^l − 1) ≤ l(ν^m − 1)（0 ≤ l ≤ m 整数），并对 7 个有理 ν 与 l ≤ m ≤ 40 做了精确验证（S6.7e）；g ≥ 0 的平台段由闭式 g_{j+l} = r_T + (ηD − Q/K)ν^l(ν^(m−l) − 1) 归约到 ν^(m−l) ≥ 1（S8.22a/b）；a ≥ 0 由 telescoping 恒等式 a_{j+l} = Σ_{i=l+1}^{m} g_{j+i}/η 归约到"有限个非负数之和非负"（S8.24a）。
- S12：Ψ 规则 m = min{z ≥ 1 : Ψ(z) ≤ 0} 与 D(m) 的直接 argmax 在 303 个精确有理网格点（K = 3..12）上**无一例不一致**；另外给出了两条符号恒等式（S12.0a/S12.0b）解释为什么二者必然一致（d(z) 关于 z 单峰，峰值位置正是 Ψ 首次变号处）。
- 附带得到的转录交叉验证：J7 第 4 节引用的 old rule 在 K = 3, η = 667/500 处的 r_T = −151089222203006/81950355825200625，本管线独立算出的值与之逐位相同（S11.8）。

## 1. 方法与 domain encoding

house style 参照 `results/Q4_symbolic_ineq.py` 与 `results/Q2_symbolic.py`：

| 对象 | 编码 |
|---|---|
| K ≥ 3 | `K = 3 + w`, `w >= 0`（只需 K ≥ 2 的条目用 `K2 = 2 + w2`） |
| η > 1 | `eta = 1 + u`, `u > 0`；ν = η/(η−1) = (1+u)/u，assumption engine 可判定 log(ν) > 0 |
| q^x, q^j, ν^m, ν^l, ν^(−t) | 正符号 `P, Q, Nm, Nl, NT` |
| Ψ(m) ≤ 0（m 的定义） | 代入 `Psi(m) = -s0`, `s0 >= 0` |
| Ψ(m−1) ≥ 0（m 的极小性） | 代入 `Psi(m-1) = s1`, `s1 >= 0` |
| B_m > 0 | 代入 `bp > 0`，并单独由 Bernoulli 确认 |
| m > η(K−1)（S1(a)） | 代入 `m = eta(K-1) + sgap`, `sgap > 0` |
| m < Kη（S1(b)） | 代入 `m = K eta - sc`, `sc > 0` |
| ν^m > e^(K−1) | 代入 `Nm = exp(K-1) + s3`, `s3 > 0` |
| ⌈η⌉ | 代入 `ceil(eta) = eta + 1 - zb`, `zb > 0`（即只用到 ⌈η⌉ < η + 1；η 为整数时 zb = 1） |

状态词汇：`PASS` = sympy 恒等式或 assumption engine 判定的符号不等式 → [VERIFIED-SYMBOLIC]；`EXACT` = 精确有理数（Fraction）有限验证，判定中不出现 float → [VERIFIED-LP]；`ASSEMBLY` = 显式登记但本脚本未用 oracle 判定的一步 → [HAND-PROOF-UNREVIEWED]；`FAIL` = 未建立并记录原因。

## 2. 逐项状态表 S1 至 S12

| 检查 | 内容 | 条目数 | 状态 |
|---|---|---|---|
| S1 | φ(t) = ν^(−t)Ψ(t) 的结构、φ'' < 0、φ(0) = K−1、两处根位置、η(K−1) < m < Kη | 24 PASS / 1 EXACT / 5 ASSEMBLY | [VERIFIED-SYMBOLIC] + [HAND-PROOF-UNREVIEWED] 残留 |
| S2 | J7 (7)：d − 1/(m+1) = −Ψ(m)/(K(m+1)B_m)，1/m − d = νΨ(m−1)/(KmB_m)，B_m > 0，1/(m+1) ≤ d ≤ 1/m | 8 PASS / 2 ASSEMBLY | [VERIFIED-SYMBOLIC] + 残留 |
| S3 | J7 (8)：d − 1/(Kη) = (m − η(K−1))/(KηB_m) > 0 | 2 PASS | [VERIFIED-SYMBOLIC] |
| S4 | J7 (11)：r_T = g_T 恒等，r_T = Q(1−md)，r_T ≥ 0 ⟺ d ≤ 1/m，r_T ≤ D ⟺ d ≥ 1/(m+1) | 6 PASS | [VERIFIED-SYMBOLIC] |
| S5 | J7 (12) 逐段（几何段、线性段含 junction、收尾步、饱和段）与递推 g_{x+1} = ν(g_x − D)；J7 (14) 与 (12) 的代数等价 | 9 PASS | [VERIFIED-SYMBOLIC] |
| S6 | J7 (13) 恒等、二阶差分 = −(ν−1)²ν^l K(ηD − Q/K)、端点 0 与 (K−1)r_T、几何段与饱和段取等、chord 归约与残留不等式的精确验证 | 12 PASS / 1 EXACT / 1 ASSEMBLY | [VERIFIED-SYMBOLIC] + [VERIFIED-LP] + 残留 |
| S7 | junction 不等式 p_{j−1} = Q/((K−1)η) ≥ D | 4 PASS | [VERIFIED-SYMBOLIC] |
| S8 | 3.3 节四类边的 ΔF/ΔH 表、band、monotone/DR 归约到 R1..R6，逐分支 | 34 PASS / 2 ASSEMBLY | [VERIFIED-SYMBOLIC] + 残留 |
| S9 | W_K = F(K,0)（需 K ≤ T）、J7 (17) 的恒等与正号 | 4 PASS / 1 ASSEMBLY | [VERIFIED-SYMBOLIC] + 残留 |
| S10 | J7 (18) 的逐步链：K−j ≤ η 的三分支、Q ≤ 1、m−η(K−1) < η、B_m > η(e^(K−1)−1−K)、e^(K−1) > K+1、收尾算术 | 11 PASS / 5 ASSEMBLY | [VERIFIED-SYMBOLIC] + 残留 |
| S11 | K=3, η=3/2 与 K=3, η=667/500 两行例子（精确有理数），含全 (x,y) 网格合法性与 J7 第 4 节引用值的复算 | 8 EXACT | [VERIFIED-LP] |
| S12 | Ψ 规则与 argmax D(m) 在 303 个精确有理点上的一致性；单峰性的两条符号恒等式；10 组配置的全网格合法性电池 | 2 PASS / 5 EXACT / 1 ASSEMBLY | [VERIFIED-SYMBOLIC] + [VERIFIED-LP] + 残留 |

（S6 的 12 PASS 含 S6.7a 至 S6.7d 四条 chord 归约恒等式；S8 的 34 PASS 含 S8.22a/b 与 S8.24a 三条本次新增的闭式归约。）

细节（逐条 id、statement、certificate）见 `results/J7_symbolic.json` 的 `checks` 字段。几处值得单独记录的：

- S1.3：φ''(t) = −K(η−1)(ln ν)² ν^(−t)，assumption engine 判定严格为负（ν = 1 + 1/u > 1 使 (ln ν)² > 0），故 φ 严格凹，[VERIFIED-SYMBOLIC]。
- S1.6：φ(η(K−1)) = (η−1)(1 − Kν^(−η(K−1)))，恒等式确认，与 J7 转录一致。
- S1.26：Ψ(Kη−1) = −K(η−1)，恒等式确认。
- S2.5：把 Bernoulli 写成 ν^m = 1 + m(ν−1) + e (e ≥ 0) 后，B_m = m/(η−1) + ηe，正号由 assumption engine 直接判定。这条比 J7 附注里的"η(ν−1) = ν，减 1 得 1/(η−1)"更直接。
- S5.8：H(x+1,0) = H(x,1) 在代入 a_x = a_{x+1} + g_{x+1}/η 与 r_{x+1} = a_{x+1} + g_{x+1} 后恒等于零，即 (14) ⟺ (12)，与 J7 附录的转录核对记录一致。
- S12.0a/S12.0b：d(m) − d(m−1) = r_T(m)/(ηB_{m−1})，d(m) − r_T(m) = (η−1)B_{m+1}(d(m) − d(m+1))。这两条恒等式把"Ψ 规则 = argmax"从有限 sweep 提升为一个只差单峰性收尾的结构性解释。

## 3. S8 逐分支归约表

四类边（3.3 节表格）在一般符号下确认为恒等式：

| 边 | ΔF | ΔH | 状态 |
|---|---|---|---|
| x 方向, y = 0 | p_x | p_x + (η−1)u_x | [VERIFIED-SYMBOLIC] (S8.1, S8.2) |
| x 方向, y ≥ 1 | ((K−y)/(K−1)) u_x | η ΔF | [VERIFIED-SYMBOLIC] (S8.3, S8.4) |
| y 方向, y = 0 | g_x | g_x | [VERIFIED-SYMBOLIC] (S8.5, S8.6) |
| y 方向, y ≥ 1 | a_x/(K−1) | η ΔF | [VERIFIED-SYMBOLIC] (S8.7, S8.8) |

band ΔF ≤ ΔH ≤ ηΔF 按类归约：class 1 归约为 u_x ≥ 0 与 p_x ≥ u_x；class 2、4（ΔH = ηΔF）归约为 ΔF ≥ 0；class 3（ΔH = ΔF = g_x）归约为 g_x ≥ 0。monotone 与 DR 归约为同一组量：x 方向二阶差分给出 p、u 非增；y 方向二阶差分给出 (K g_x − r_x)/(K−1) ≥ 0（S8.13）；混合二阶差分给出 g 非增（S8.14）与 p_x ≥ u_x（S8.15）。

于是全部条件归约为 R1 至 R6，逐分支状态：

| 归约后的不等式 | 分支 | 状态 | 证书 |
|---|---|---|---|
| R1 g_x ≥ 0 | 几何段 x ≤ j | [VERIFIED-SYMBOLIC] | g = q^x/K > 0 |
| R1 g_x ≥ 0 | 平台段 j < x ≤ T | [HAND-PROOF-UNREVIEWED]（残留已收紧） | 闭式 g_{j+l} = r_T + (ηD − Q/K)ν^l(ν^(m−l) − 1)（S8.22a），符号由 assumption engine 判定（S8.22b），残留只剩 ν^(m−l) ≥ 1 |
| R1 g_x ≥ 0 | 饱和段 x > T | [VERIFIED-SYMBOLIC] | g = 0 |
| R2 g 非增 | 几何段 | [VERIFIED-SYMBOLIC] | S8.17/S8.18，差为 q^x(1−q)/K |
| R2 g 非增 | junction j−1 → j | [VERIFIED-SYMBOLIC] | S8.21，0 < q < 1 |
| R2 g 非增 | 平台段 | [VERIFIED-SYMBOLIC] | S8.19/S8.20，差为 (ηD − Q/K)ν^l(ν−1) ≥ 0，用 S3 |
| R2 g 非增 | 收尾 T → T+1 | [VERIFIED-SYMBOLIC] | g_T = r_T ≥ 0（S4） |
| R3 a_x ≥ 0 且非增 | 全部 | [HAND-PROOF-UNREVIEWED]（残留已收紧） | 非增来自 u ≥ 0；非负用 telescoping 恒等式 a_{j+l} = Σ_{i=l+1}^{m} g_{j+i}/η（S8.24a），残留只剩"有限个非负数之和非负" |
| R4 u_x ≥ 0 且非增 | 全部 | [VERIFIED-SYMBOLIC] | u_x = g_{x+1}/η（S5）+ R1 + R2 |
| R5 p_x ≥ u_x | 几何段 | [VERIFIED-SYMBOLIC] | S8.25/S8.26，gap = q^x/(K k_1) |
| R5 p_x ≥ u_x | 平台段 | [VERIFIED-SYMBOLIC] | S8.27/S8.28，= (ηD − Q/K)ν^(l+1)/η ≥ 0 |
| R5 p_x ≥ u_x | 收尾/饱和 | [VERIFIED-SYMBOLIC] | p_T − u_T = r_T ≥ 0 |
| R5 p 非增 | 几何段 | [VERIFIED-SYMBOLIC] | p_x = q^x/k_1 递减 |
| R5 p 非增 | junction j−1 → j | [VERIFIED-SYMBOLIC] | S7：p_{j−1} = Q/((K−1)η) ≥ D |
| R5 p 非增 | 平台段 | [VERIFIED-SYMBOLIC] | 常数 D |
| R5 p 非增 | 收尾 T−1 → T | [VERIFIED-SYMBOLIC] | D ≥ r_T（S4.4，⟺ d ≥ 1/(m+1)） |
| R5 p 非增 | T → T+1 | [VERIFIED-SYMBOLIC] | r_T ≥ 0（S4.5，⟺ d ≤ 1/m） |
| R6 K g_x ≥ r_x | 几何段 | [VERIFIED-SYMBOLIC] | 取等（S6.8） |
| R6 K g_x ≥ r_x | 平台段 | [HAND-PROOF-UNREVIEWED]（残留已收紧） | chord 恒等式（S6.7a/b）+ 符号判定（S6.7c），残留只剩 m(ν^l − 1) ≤ l(ν^m − 1)（0 ≤ l ≤ m 整数），已在 7 个有理 ν 上精确验证（S6.7e） |
| R6 K g_x ≥ r_x | 饱和段 | [VERIFIED-SYMBOLIC] | 0 = 0 |

额外确认：H(0,0) = C − 1 − (η−1)(K−1)/K = 0（S8.32），F(0,0) = 0、F(x,K) = 1、F ≤ 1、H 单调（由 ΔH ≥ ΔF ≥ 0 得到）（S8.33）。

## 4. 仍为 hand-proof 的步骤（17 项，[HAND-PROOF-UNREVIEWED]）

分四类。每一项的代数成分都已符号确认，未被 oracle 判定的只是把成分接起来的那一步。

**(a) classical analytic facts（4 项）**

1. S1.17：(1 + 1/u)^(u+1) > e（u > 0）。sympy 确认的成分：h(u) = (u+1)ln(1+1/u) − 1 的导数恒等式 h'(u) = ln(1+1/u) − 1/u（S1.9）、lim_{u→∞} h(u) = 0（S1.10）、d/dx[x − ln(1+x)] = x/(1+x) > 0 且在 x = 0 取 0（S1.11/S1.12）；另一条路线用 artanh：(1+y)/(1−y) 在 y = 1/(2u+1) 处等于 1 + 1/u（S1.13）、d/dy[artanh(y) − y] = y²/(1−y²) > 0（S1.14/S1.15）、若 ln(1+1/u) > 2/(2u+1) 则 (u+1)ln(1+1/u) − 1 > 1/(2u+1) > 0（S1.16）。sympy 不判定 `(log(1+1/u) - 1/u).is_negative`（返回 None），因此"f(0) = 0 且 f' > 0 ⟹ f > 0"这一步是引用的经典结论。补充 oracle：u = 1..60 的整数点上用精确有理数与 E 比较，全部成立（S1.18，[VERIFIED-LP]）。
2. S1.23：e^(K−1) > K（整数 K ≥ 2）与 e^(K−1) > K+1（整数 K ≥ 3）。base（E > 2、E² > 4）与 induction step（K(e−1) − 1 > 0、K(e−1) + e − 2 > 0）都由 sympy 判定（S1.19 至 S1.22），缺的是归纳法原理本身。
3. S2.9：Bernoulli ν^m ≥ 1 + m(ν−1)（整数 m ≥ 1）。base R_1 = 0 与 step R_{m+1} = νR_m + m(ν−1)² ≥ 0 都由 sympy 确认（S2.7/S2.8），缺的是归纳法原理。
4. S10.6：Q = q^j ≤ 1（整数 j ≥ 0）。0 < q < 1 由 sympy 判定（S10.5），缺的是幂单调性。同类的还有 S1.25 中 s ↦ s^(K−1) 的单调性与 S10.11 中 t ↦ ν^t 的单调性。

**(b) integer / logic assembly（6 项）**

5. S1.25：ν^(η(K−1)) = (ν^η)^(K−1) > e^(K−1) > K。恒等式 S1.7 与两个不等式都已确认，缺中间一步的幂单调性。
6. S1.28：J7 (5)，η(K−1) < m < Kη。用 φ 严格凹（S1.3）+ φ(0) = K−1 > 0（S1.4/S1.5）得到唯一正根 t*，sign Ψ = sign φ（S1.1）+ φ(η(K−1)) > 0（S1.24）+ Ψ(Kη−1) < 0（S1.26/S1.27）把 t* 夹住，m = ⌈t*⌉。"严格凹且在 0 处为正 ⟹ 单交叉"这一步是 assembly。
7. S1.30：m ≥ K。来自 m > η(K−1) > K−1（S1.29）与 m 是整数。
8. S2.10：J7 (7) 的最终形式 1/(m+1) ≤ d ≤ 1/m，把 S2.1 至 S2.6 串起来。
9. S9.2：K ≤ T = j + m（W_K = F(K,0) 不需要在 x = K 之前截断），来自 S1.30 与 j ≥ 0；同时用 j ≤ K−1 < K。
10. S10.4：K − j ≤ η 的三分支。unclamped 分支（K − j = ⌈η⌉ − 1）、上钳位分支（j = K−1，K − j = 1 ≤ η）、下钳位分支（j = 0，⌈η⌉ ≥ K+1 故 η > K）各自的符号由 sympy 判定（S10.1 至 S10.3），缺的是 ceiling 的分类讨论本身。

**(c) 凹性到内部整点（1 项，残留已收紧为一条初等不等式）**

11. S6.7：平台段 K g_x ≥ r_x。sympy 确认：(13) 的闭式恒等（S6.1）、l 方向二阶差分 = −(ν−1)²ν^l K(ηD − Q/K)（S6.2）、ηD − Q/K = Q(m − η(K−1))/(K B_m) ≥ 0（S6.3/S6.4，用 S3）、l = 0 处为 0（S6.5）、l = m 处为 (K−1)r_T ≥ 0（S6.6 + S4.5）。J7 3.3 节第 5 条用的是"凹函数在区间两端非负 ⟹ 区间内（含整点）非负"。本次把它换成了 chord 恒等式：K g_{j+l} − r_{j+l} = (l/m)(K−1)r_T + K(ηD − Q/K)[(l/m)(ν^m − 1) − (ν^l − 1)]（S6.7a/S6.7b），其符号由 assumption engine 判定（S6.7c）。于是残留精确地只剩一条初等不等式：对整数 0 ≤ l ≤ m 与 ν > 1，m(ν^l − 1) ≤ l(ν^m − 1)，等价于"递增序列 ν^i 的前 l 项平均不超过前 m 项平均"（求和形式由 S6.7d 确认）。补充 oracle：7 个有理 ν 与所有 0 ≤ l ≤ m ≤ 40 精确验证通过（S6.7e，[VERIFIED-LP]）。

**(d) 单调序列与链式放缩（6 项）**

12. S8.22：R1 平台段 g_x ≥ 0。本次改为闭式 g_{j+l} = r_T + (ηD − Q/K)ν^l(ν^(m−l) − 1)（S8.22a），符号由 assumption engine 判定（S8.22b），残留只剩 ν^(m−l) ≥ 1（幂单调性，(a) 第 4 条同类）。
13. S8.24：R3 a_x ≥ 0 且非增。非增来自 u ≥ 0；非负改用 telescoping 恒等式 a_{j+l} = Σ_{i=l+1}^{m} g_{j+i}/η（S8.24a，sympy 的几何求和闭式，用 ν/(ν−1) = η），残留只剩"有限个非负数之和非负"。
14. S10.11：ν^m > e^(K−1)，用 m > η(K−1) 与 ν > 1 的幂单调性。
15. S10.12：e^(K−1) − K − 1 > 0（K ≥ 3），即 (a) 第 2 条在 K ≥ 3 的形式。
16. S10.16：J7 (18) 的最终串联。两条 replacement lemma（分子放大 S10.13、分母缩小 S10.14）与收尾算术 η·1·η/(Kη·ηX) = 1/(KX)（S10.15）都由 sympy 判定，缺的是把它们按顺序接到 (17) 上的那一步。
17. S12.0c：argmax_z d(z) = m。两条局部恒等式（S12.0a/S12.0b）与 Ψ 的单交叉给出 d 先非降后非增，"单峰 ⟹ argmax 在峰点"是 assembly；有限验证见 S12（303 点全部一致）。

## 5. S12 sweep 结果

网格：K = 3..12；每个 K 的 η 取 segment midpoints（c + 1/2）、near-integer（c ± 1/100）、小 frac(Kη) corner（(a ± 1/1000)/K，a ∈ {K+1, K+2, 2K, 3K−1}）、η 接近 1（101/100、1001/1000）、j = 0 区间（K ± 1/100、K + 1/2、K + 3/2），并显式包含 667/500 与 2001/1000。共 303 个精确有理点，全部判定用 Fraction，无 float。

| 项目 | 结果 |
|---|---|
| Ψ 规则 m 与 argmax_m D(m) 一致 | 303/303，无一例不一致（S12.1） |
| Ψ 规则族可行（r_T ≥ 0） | 303/303（S12.2） |
| j = max{0, min{K−1, K+1−⌈η⌉}} 达到 min_t V_t | 303/303（S12.3） |
| 0 < W_K − ρ_K < 1/(K(e^(K−1)−K−1)) | 303/303（S12.4） |
| 全 (x,y) 网格合法性电池（range、monotone、band、三个 DR 二阶差分、y ≤ 1 的 O-independence、normalization、W_K = F(K,0)） | 10 组配置，0 violation（S12.5） |

说明：S12.4 里 rational 与 exp(K−1) 的比较由 sympy 的精确常数比较完成（内部按需提高精度判号），本报告把它计为 [VERIFIED-LP] 而不是纯符号判定。

例子行（S11，全部 [VERIFIED-LP]）：K = 3, η = 3/2 得 Ψ(3) = 12 > 0、Ψ(4) = −42 < 0、m = 4、B_4 = 116、d = 13/58、j = 2、Q = 9/16、D = 117/928、W_3 = 523/928 = 9/16 + 1/928、ρ_3 = 9/16，与 J7 (2) 与例子段逐位一致；K = 3, η = 667/500 得 Ψ 规则 m = 3、old rule ⌈Kη⌉−1 = 4、old rule 的 r_T = −151089222203006/81950355825200625 < 0（与 J7 第 4 节引用值逐位相同）、Ψ 规则的 r_T > 0 且全网格合法。

## 6. 结论：J7 的构造合法性现在处于什么状态

**可以说的**：在"count grid (x, y) 上给定的 F 与 H = η_u G 是否满足 J7 3.3 节列出的合法性清单"这个范围内，J7 的构造合法性的**代数部分**已经由本管线独立符号验证，不依赖来源自报的结果。具体地：(7)、(8)、(11)、(12)、(13)、(14)、(17) 全部作为一般 (K, η, m, j) 的恒等式成立；四类边的 ΔF/ΔH 表成立；monotone、DR、band 归约到 R1 至 R6 后，每个分支要么是恒等式，要么是 assumption engine 在编码后的 domain 上判定的符号。J7 (18) 的每一步放缩单独判定通过。截断规则 m 的定义与 D(m) 的 argmax 在 303 个精确有理点上一致，并有两条局部恒等式给出结构性解释。

**不能说的**：整体合法性**尚未**是全符号闭合的，残留正是第 4 节列的 17 项 [HAND-PROOF-UNREVIEWED]。收紧之后，其中带实质数学内容的只剩两条：
- (1 + 1/u)^(u+1) > e（经典结论，sympy 在本管线中不判定 `log(1+1/u) - 1/u` 的符号；已用 u = 1..60 的整数点精确验证补强）；
- m(ν^l − 1) ≤ l(ν^m − 1)（整数 0 ≤ l ≤ m，ν > 1），即 K g ≥ r 在平台段的唯一残留（已用 7 个有理 ν、l ≤ m ≤ 40 精确验证补强）。
其余 15 项是归纳法原理、幂与指数的单调性（含 ν^(m−l) ≥ 1、Q = q^j ≤ 1）、"有限个非负数之和非负"、凹函数单交叉、ceiling 分类、以及把已判定的放缩按顺序串起来这类 assembly。

**本次验证覆盖不到的部分**（仍按来源状态 [HAND-PROOF-UNREVIEWED]，不因本文件升级）：
1. 从 count grid 函数到 ground set 上真实 set function 的 lift（本脚本只在 (x, y) 网格上验证，没有验证 x = |S \ O|, y = |S ∩ O| 的对称化构造在集合层面同样 submodular、monotone）；
2. J7 3.4 节的 any-size 论证：泄漏集合的刻画 (15)、单次查询泄漏概率 ≤ K²(T+K)²/(2n²) 与 cnK 次累计 (16)、canonical-transcript 归纳与平均论证；
3. ρ_K(η) 本身等于 predictive greedy 精确最坏比这一事实（本脚本只把 ρ_K 取作 V_j，并在 sweep 上核对 V_j = min_t V_t）；
4. (1) 的下界方向 ρ_K ≤ α_lin。

因此 J7 的结论 (1)、(18) 目前的合适状态是：**构造合法性的代数与符号部分 [VERIFIED-SYMBOLIC]（本文件），构造到定理的其余环节 [HAND-PROOF-UNREVIEWED]**。要继续清残留，剩下的两条实质项都是标准教科书结论（(1+1/u)^(u+1) > e；递增序列的前缀平均递增），建议的处理是在正文里显式引用而不是重新推导；其余 15 项（归纳法、幂单调性、有限非负和、单交叉、ceiling 分类、放缩串联）属于可由作者复核一次即可关闭的 assembly，本文件已把每一项的代数成分逐条列出，复核时只需核对接口而不必重推代数。

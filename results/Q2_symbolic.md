# Q2 一般 K 符号验证报告 (TASKS10)

脚本: `results/Q2_symbolic.py`(`python3 results/Q2_symbolic.py`,约 7 秒,exit 0 当且仅当无 FAILED)
数据: `results/Q2_symbolic.json`(104 条 check + 48 点 exact-rational sweep 表)
被验证对象: `results/Q1_closed_form.py :: build_closed_form()`

## 0. 状态总表

| 检查 | 内容 | 状态 |
|---|---|---|
| C0 | 本脚本重新推导的分支表达式 vs 交付的 Piecewise(转写守卫) | [VERIFIED-SYMBOLIC] |
| C1 | F 单调: Delta_x F >= 0, Delta_y F >= 0,逐分支 | [VERIFIED-SYMBOLIC] |
| C2 | F submodular: 三个二阶差分 <= 0,逐分支含 x=j、x=T 两个 junction | [VERIFIED-SYMBOLIC] |
| C3 | 单元素 band (eta_u, eta_o) = (eta, 1),四类边 + 极值边清单 | [VERIFIED-SYMBOLIC] |
| C4 | O-independence(y <= 1)与 Ghat 三个 phase 的相容性 | [VERIFIED-SYMBOLIC] |
| C5 | 归一化 F(0,0)=0, F(0,K)=1, F <= 1,目标值 F(K,0) | [VERIFIED-SYMBOLIC] |
| C6 | 卡点: E(m) = D(m) - D_base 的符号、阈值 m_c、sweep | [VERIFIED-SYMBOLIC],其中 m* 的取值规则为 [CONJECTURE] |
| C7 | 整数 eta 处 V_j 的段切换 | [VERIFIED-SYMBOLIC] |
| C8 | 上述分支分析的全 2D 网格 exact-rational 交叉验证(18 组) | [VERIFIED-SYMBOLIC] |

无 FAILED 项。两条 CONJECTURE 都在 C6,都只涉及 argmax 位置 m*,不涉及闭式本身的 feasibility。

有效参数域(本任务全部结论的前提): K >= 3 整数, 2 <= j <= K-1 整数, eta 严格落在 (K-j, K-j+1) 内
(因此 eta > 1), n >= 2K, X = n - K, split (eta_u, eta_o) = (eta, 1), balanced region y <= 1。

## 1. 记号与本报告新得到的结构恒等式

k1 = eta(K-1)+1, q = (K-1)eta/k1 = 1 - 1/k1, nu = eta/(eta-1), B(m) = eta(nu^m - 1) - m,
D_base = q^j/(K eta), D(m) = q^j (nu^m/K - 1)/B(m), T = j+m, r_T = r(T) = q^j - m D。

序列层记号: d(x) = r(x) - r(x+1), e(x) = g(x+1) - g(x), a(x) = r(x) - g(x), E = D - D_base。

C1/C2/C3 的整套分支分析都被下面这条恒等式拉平,它在每一个分支与两个 junction 上分别由 sympy 确认
(check id `C1.ID.geo` / `C1.ID.junc` / `C1.ID.tail` / `C1.ID.close` / `C1.ID.sat`):

> **master identity**  a(x) - a(x+1) = g(x+1)/eta,对所有 x >= 0 成立。

由它直接得到(`C1.consequence`, `C5.Fform`):

- F(x, y) = 1 - a(x)(K-y)/(K-1) 对 y >= 1;特别 F(x,K) = 1 对所有 x。
- Delta_x F(x,0) = d(x);  Delta_x F(x,y) = (K-y) g(x+1) / (eta (K-1)) 对 y >= 1。
- Delta_y F(x,0) = g(x);  Delta_y F(x,y) = a(x)/(K-1) 对 y >= 1。
- g(x) - d(x) = (eta-1) g(x+1)/eta(`C3.e1.lo`)。

于是二维网格上的全部 LP 约束都退化成 r, g 两个一维序列上的 6 个条件:
r 非增且凸, g 非负且非增, a = r-g >= 0, K g - r >= 0。

## 2. C0 转写守卫 [VERIFIED-SYMBOLIC]

逐分支比对交付的 Piecewise(r 的两段与 x > T 的 0 段, g 同, F 的 y=0 与 y>=1 两段, D(m), D_base,
objective, V_j),全部化零;另外把本脚本的 exact Fraction 序列与 `Q1_closed_form.instantiate()`
在 (K,eta,n) = (3,3/2,24), (4,5/2,32), (5,7/2,40) 上逐格比对,max |diff| = 0(`C0.numeric`)。

注: 交付的 Piecewise 里 r 的第二段写作 `x <= T`,与本报告的 j < x <= T 一致。

## 3. C1 单调性 [VERIFIED-SYMBOLIC]

| 边类 | Delta F 的闭式 | 归约成的不等式 | 证书 | 是否取等 |
|---|---|---|---|---|
| x-edge, y=0, x < j | d(x) = q^x/k1 | q > 0, k1 > 0 | `C1.dx.geo` | 从不取等 |
| x-edge, y=0, j <= x < T | d(x) = D | D >= D_base > 0 | 定义 | 从不取等 |
| x-edge, y=0, x = T | d(T) = r_T | r_T >= 0,等价于 D(m) >= D(m-1) | `C6.ID.rT_local` | r_T = 0 时取等 |
| x-edge, y=0, x > T | 0 | 平凡 | `C1.dx.sat` | 恒取等 |
| x-edge, y >= 1 | (K-y) g(x+1)/(eta(K-1)) | g >= 0 | master identity + `C1.g.nonneg` | y=K 或 g(x+1)=0 |
| y-edge, y=0 -> 1 | g(x) | g(x) >= 0 | `C1.g.nonneg` | x > T |
| y-edge, y >= 1 | a(x)/(K-1) | a = r-g >= 0 | a 非增 + a(T)=0 | x >= T |

g >= 0 的证书链: 在 x <= j 上 g = q^x/K > 0;在 tail 上 g 非增(`C2.g.tail`,需 E >= 0)且末端
g(T) = r(T) = r_T >= 0;x > T 上 g = 0。NO-TAIL regime 下 g 在 x >= j 上恒等于 q^j/K。
a >= 0 的证书链: master identity 给出 a 非增(因 g >= 0),TAIL 末端 a(T) = r_T - g_T = 0
(D(m) 的定义,`C2.def.Dm`);NO-TAIL 下 a(X) = r(X) - q^j/K >= 0 由 X - j <= eta(K-1) 给出。

## 4. C2 submodularity [VERIFIED-SYMBOLIC]

### Delta_x^2 F <= 0(y = 0 层,即 d 非增)

| 位置 | 归约成的不等式 | 证书 | 取等 |
|---|---|---|---|
| x+2 <= j | d(x+1) = q d(x), q < 1 | `C2.dxx.geo` | 否 |
| junction x = j-1 | **D <= q^(j-1)/k1 = q^j/((K-1) eta)** | NO-TAIL: D_base = q^j/(K eta) 严格更小;TAIL: D <= q^j/m 且 m > eta(K-1) | 否 |
| tail 内部 | d == D 常数 | `C2.dxx.tailint` | **恒取等** |
| junction x = T-1 | **r_T <= D**,等价于 D(m) >= D(m+1) | `C6.ID.dT_local` | 否(一般) |
| x = T | 0 <= r_T | `C2.dxx.sat` | r_T = 0 |

junction x = T-1 这一条只在 T < X(closing edge T -> T+1 落在网格内)时才是约束;当 argmax 被网格
宽度截断到 m = X - j 时 T = X,该边不存在,条件自动 vacuous。K=8, j=6, eta=5/2, n=32 正是这种情形
(`results/Q2_grid_check.log` 中 m=18, T=24=X)。

### Delta_x^2 F <= 0(y >= 1 层)与 Delta_x Delta_y F <= 0

两者都归约为 g 非增(前者是 (K-y)/(eta(K-1)) 乘 (g(x+2)-g(x+1)),后者在 y=0 层就是 e(x),
在 y >= 1 层是 -g(x+1)/(eta(K-1)))。

| 位置 | e(x) = g(x+1)-g(x) 的闭式 | 归约 | 取等 |
|---|---|---|---|
| x < j | -q^x(1-q)/K | q < 1 | 否 |
| j <= x < T(含 junction x=j) | -eta E nu^(x-j) (nu-1) | **E = D - D_base >= 0** | **E = 0 时恒取等(NO-TAIL)** |
| x = T | -r_T | r_T >= 0 | r_T = 0 |
| x > T | 0 | 平凡 | 恒取等 |

### Delta_y^2 F <= 0

y >= 1 层恒为 0(F 关于 y 仿射,`C2.dyy.y1`,**恒取等**)。y = 0 层归约为 K g(x) - r(x) >= 0:

| 位置 | K g - r 的闭式 | 归约 | 取等 |
|---|---|---|---|
| x <= j | 0 | 恒等式 `C2.dyy.geo` | **整段恒取等** |
| j < x <= T | h(i) = i D - K eta E (nu^i - 1), i = x-j | h 在 i 上 concave(`C2.dyy.concave`,需 E >= 0),h(0)=0, h(m) = (K-1) r_T >= 0(`C2.dyy.endpoints`),故 h(i) >= ((m-i)h(0) + i h(m))/m >= 0 | i=0 |
| x > T | 0 | 平凡 | 恒取等 |

## 5. C3 单元素 band [VERIFIED-SYMBOLIC]

split (eta_u, eta_o) = (eta, 1),要求每条边满足 dF/eta <= dG <= dF。

| 边类 | dF | dG | 下端条件 | 上端条件 | 极值 |
|---|---|---|---|---|---|
| x-edge, y=0 | d(x) | g(x)/eta | d(x) <= g(x),即 (eta-1)g(x+1)/eta >= 0 | g(x) <= eta d(x) | 见下 |
| x-edge, y=1 | d+e = g(x+1)/eta | Ghat(x+2)-Ghat(x+1) = g(x+1)/eta | dF >= 0 | **恒等,上端 tight** | eta_o = 1 |
| y-edge, y=0->1 | g(x) | g(x)/eta | **恒等,下端 tight** | g >= 0, eta >= 1 | eta_u = eta |
| y-edge, y >= 1 | a(x)/(K-1) | 同 dF(G_unbal 规则) | dF >= 0 | **恒等,上端 tight** | eta_o = 1 |
| x-edge, y >= 2 | (K-y)g(x+1)/(eta(K-1)) | g(x+1)/eta + dF(x,y) - dF(x,1) = dF(x,y) | dF >= 0 | **恒等,上端 tight** | eta_o = 1 |

x-edge y=0 的上端条件逐分支:

| 位置 | eta d - g 的闭式 | 归约 | 取等 |
|---|---|---|---|
| x < j | q^x (eta-1)/(K k1) | eta > 1 | 否;比值 dG/dF = k1/(K eta) 落在 (1/eta, 1) 内部 |
| j <= x < T | eta E nu^(x-j) | E >= 0 | **E = 0 即 NO-TAIL 时恒取等** |
| x = T | (eta-1) r_T | eta > 1, r_T >= 0 | r_T = 0 |
| x > T | 0 | 平凡 | 退化 0 <= 0 <= 0 |

y >= 2 的 x-edge 之所以也恰好上端 tight,是因为 G_unbal 规则里的 Ghat 步长 g(x+1)/eta 与
dF(x,1) 相等(master identity),两者相消后 dG = dF(x,y) 精确成立(`C3.e4.x`)。

### 极值边清单(extreme-edge inventory,TASKS10 要求)

- 下端 dG = dF/eta(实现 eta_u = eta): **每一条 y=0 -> y=1 的 y-edge**;以及 y=0 层的 closing
  x-edge x = T(那里 g(T) = d(T) = r_T)。
- 上端 dG = dF(实现 eta_o = 1): **每一条 y=1 层的 x-edge**;**y >= 2 区域的全部边**(x 与 y 方向);
  在 NO-TAIL regime 下还包括 y=0 层全部 x >= j 的 x-edge。
- 严格内部(两端都不取): y=0 层 x < j 的 x-edge,比值恒为 k1/(K eta)。

因此 band 预算被恰好用满: eta_u = eta 与 eta_o = 1 都被实际达到,乘积恰为 eta,不是 < eta。

## 6. C4 O-independence 与 Ghat 的 phase 相容性 [VERIFIED-SYMBOLIC]

- y <= 1 上 G(x,y) = Ghat(x+y) 是构造性的(只依赖 |S| = x+y),y >= 2 的规则在 y=1 处退化为
  Ghat(x+1),两种写法在重叠处一致,G 良定义(`C4.Oindep`)。
- phase1(j+1) = phase2(s=j+1)(M=0),phase2(T+1) = phase3:`C4.junc12`, `C4.junc23` 化零。
- Ghat 的步长在每个 phase 与两个 junction 上都等于 g(s)/eta:`C4.step.ph1`(s < j)、
  `C4.step.junc`(s = j)、`C4.step.cross`(s = j+1,跨 phase)、`C4.step.ph2`(phase 2 内部,
  以 W = nu^M 为自由正符号)、`C4.step.ph3`(饱和段步长 0)。
- 由此 Ghat 非降(步长 = g/eta >= 0),这正是 C3 里那三类边的 band 检验所需要的输入。

## 7. C5 归一化与目标值 [VERIFIED-SYMBOLIC]

- F(0,0) = 1 - r(0) = 0;F(0,K) = 1 - 1 + 1/K + (K-1)(1-1/K)/(K-1) = 1;并且 F(x,K) = 1 对所有 x。
- F(x,y) <= 1: y=0 层归约为 r(x) >= 0;y >= 1 层由 F = 1 - a(x)(K-y)/(K-1) 归约为 a(x) >= 0。
  结论对全网格成立,不只是 x+y <= K。
- F(K,0) = 1 - r(K) = 1 - q^j + (K-j) D,前提 j <= K <= T。K <= T 是自动的: NO-TAIL 下 T = +oo;
  TAIL 下 m >= m_c > eta(K-1) >= eta > K-j。
- D = D_base 时目标值恰为 V_j(`C5.obj.Vj`);一般地 objective = V_j + (K-j) E(`C5.obj.excess`)。

## 8. C6 卡点分析

### (c) 分母正性 [VERIFIED-SYMBOLIC]

B(m) = eta(nu^m - 1) - m > 0 对所有整数 m >= 1 与 eta > 1。证书: Bernoulli 不等式
nu^m >= 1 + m(nu-1) 的归纳步被 sympy 化零(`C6.bern.step`: nu^(m+1)-1-(m+1)(nu-1) =
nu[nu^m-1-m(nu-1)] + m(nu-1)^2),代入后 B(m) >= eta m (nu-1) - m = m/(eta-1) > 0
(`C6.bern.bound`)。48 个 sweep 点上另有 exact-rational 复核。

### (a) D(1) < D_base [VERIFIED-SYMBOLIC]

D(1) = q^j (K - eta(K-1))/K(`C6.D1.form`,与任务给的手算一致),并且

> D(1) - D_base = - q^j (eta(K-1) - 1)(eta - 1) / (K eta)  < 0  对 eta > 1, K >= 2

(`C6.D1.sign`)。所以 staircase 绝不从 m = 1 开始。

### (b) E(m) 的精确符号 [VERIFIED-SYMBOLIC]

任务预期 N(m) 是"指数 + 线性"的 convex 函数。实际上通分之后 nu^m 项精确抵消:

> **E(m) = D(m) - D_base = q^j (m - eta(K-1)) / (K eta B(m))**    (`C6.E.form`)

分子里只剩线性项。由 q^j, K, eta, B(m) > 0 得

> **sign E(m) = sign(m - eta(K-1))**,即 **E(m) > 0 当且仅当 m > eta(K-1)**  (`C6.E.sign`)

阈值 **m_c = min{m >= 1: D(m) > D_base} = floor(eta(K-1)) + 1**,首个 staircase 台阶在
**n_c = K + j + m_c**(`C6.mc`;48/48 sweep 点上 brute-force 的 m_c 与该公式逐点相等)。

关于 m -> oo: lim D(m) = D_base 确实成立,但 E(m) ~ q^j m /(K eta^2 nu^m) 是从**上方**趋于 0
(m > eta(K-1) 之后恒正),所以 sup_m D(m) 在**有限** m* 处取到,excess 不是极限现象而是中段现象
(`C6.limit`)。

局部最优与两个 junction 条件的等价(这是 C2 两条 junction 不等式的最终证书):

> **D(m) - D(m-1) = r_T / (eta B(m-1))**,故 r_T >= 0 当且仅当 D(m) >= D(m-1)  (`C6.ID.rT_local`)
> **D(m) - r_T = (eta-1) B(m+1) (D(m) - D(m+1))**,故 d(T) = r_T <= D 当且仅当 D(m) >= D(m+1)  (`C6.ID.dT_local`)

也就是说,闭式在**任何**使 D 取到可用范围内最大值的 m 处自动满足 C2 的两条 junction 不等式。
这解释了为什么 `params()` 用直接 argmax 选 m 就够,不需要额外的 feasibility 侧条件。

由 `C6.ID.dT_local` 还得到 m* 的判定式(`C6.ID.step_sign`):

> D(m) >= D(m+1) 当且仅当 nu^m (eta K - 1 - m) <= K(eta-1)

### m* 的取值规则 [CONJECTURE] + 对既有猜想的反例

- 规则 **m* = min{m >= 1: nu^m (eta K - 1 - m) <= K(eta-1)}**,并且 m* <= ceil(eta K) - 1。
  上式的等价性是 [VERIFIED-SYMBOLIC];"第一个局部极大即全局极大"用的是 nu^m (eta K-1-m) 关于实
  变量 m 的单峰性(导数 nu^m[L(eta K-1-m) - 1] 只变号一次,L = ln nu)加上 m=1 处
  2 eta (K-1) > K,这一段是手写论证,oracle 只在 sweep 上确认(48/48 点 D(m) 严格增到 m* 再非增)。
  故整体标 [CONJECTURE]。
- **N4/Q1 继承的 [CONJECTURE] m* = ceil(eta K) - 1 在本 sweep 上被反例推翻**(exact rational):

| K | eta | j | eta*K | 真 argmax m* | ceil(eta K)-1 |
|---|---|---|---|---|---|
| 5 | 2001/1000 | 3 | 10.005 | 9 | 10 |
| 5 | 20001/10000 | 3 | 10.0005 | 9 | 10 |
| 8 | 40001/10000 | 4 | 32.0008 | 31 | 32 |
| 6 | 25001/10000 | 4 | 15.0006 | 14 | 15 |

  失效条件是 frac(eta K) 足够小(此时 m = ceil(eta K)-2 处已经满足判定式)。这只影响"用 m* 预测
  saturation onset n = K + j + m*"这类推断,不影响闭式本身: `params()` 与 `Q2_grid_check.py` 都用
  直接 argmax。`Q2_indep_nsweep.py` 的 `W_exact` 搜到 mstar+3,在这些点上仍能取到真 argmax,但其
  P4b/P4c 里用 T = j + ceil(eta K) - 1 定位 onset 的那几行在该区域会偏一格。

### sweep 结果(48 点,全部 exact rational,`Q2_symbolic.json: sweep_C6b`)

K in {3,4,5,8,13,21},j in {2, floor(K/2), K-1} 与 2 <= j <= K-1 的交,eta 取 K-j+1/100、
K-j+1/2、K-j+99/100,外加 6 个 frac(eta K) 接近 0 的 stress 点。每点核对:

- m_c = floor(eta(K-1)) + 1: 48/48 与 brute-force 一致;
- E(m*) > 0 且 W = V_j + (K-j)E(m*) > V_j: 48/48;
- r_T >= 0 与 d(T) <= D: 48/48;
- **m_c > K - j: 48/48**;
- j = K+1-ceil(eta) 且 V_j = rho_K = min_t V_t: 48/48;
- n = 2K 处闭式值 = V_j: 48/48;
- D(m) 关于 m 单峰、B(m) > 0: 48/48;
- 在 n = 2K、n = n_c、n = K+T、n = K+T+2 四个网格宽度上,C1/C2/C3/C5 的序列层条件全部成立。

## 9. C7 段切换 [VERIFIED-SYMBOLIC]

V_j(eta) = 1 - q^j(1 - (K-j)/(K eta))。sympy 确认两条:

> **V_j(K-j) = V_{j+1}(K-j)**(`C7.switch`),**V_j(K-j+1) = V_{j-1}(K-j+1)**(`C7.switch2`)

即段 j 的定义域 (K-j, K-j+1) 的两个端点分别与相邻段的值相接,rho_K = min_t V_t 在整数 eta 处连续,
active index 在那里切换。n = 2K regime 的闭式值就是 V_j(C6 的 m_c > K-j),所以两段在端点处给出
同一个 n = 2K 值。

## 10. C8 全 2D 网格交叉验证 [VERIFIED-SYMBOLIC]

对 (K,j,eta) in {(3,2,3/2), (3,2,19/10), (4,2,5/2), (4,3,3/2), (5,3,5/2), (5,4,3/2)},
在 n = 2K(NO-TAIL)、n = K+T(saturation onset)、n = K+T+3 三个宽度上,用本脚本自己的序列重建
F、Ghat、G,逐边检查 monotone、submodular(三个二阶差分)、band(两端)、F <= 1、O-independence、
归一化: 18/18 组 0 violation。这条与既有的 `results/Q2_grid_check.py`(K <= 8 全格点)独立但一致。

## 11. 卡点

**TASKS10 前提 (c) 不成立的确切位置与不等式。**

前提 (c) 要求 rho_K^{(n)} 在 n -> oo 时趋于 rho_K = min_j V_j。对本族(relaxed-F LP 顶点,split
(eta,1),balanced region y <= 1)这不成立,原因是:

1. LP 值 = 1 - q^j + (K-j) D,而 D = max(D_base, max_{1 <= m <= X-j} D(m)),X = n-K
   (`C5.obj`, `C5.obj.excess`)。
2. **卡住的不等式是 E(m) = D(m) - D_base > 0,它精确等价于 m > eta(K-1)**,因为

   > E(m) = q^j (m - eta(K-1)) / (K eta (eta(nu^m - 1) - m)),分母恒正

   所以 **m_c = floor(eta(K-1)) + 1**,首个台阶出现在 **n_c = K + j + m_c**。
3. 于是对 X >= j + m_c(即 n >= n_c)LP 值严格超过 V_j,并且随 n 非降,最终饱和在
   **W = V_j + (K-j) max_m E(m) > V_j**。这与 (c) 要求的"降到 V_j"方向相反。
   数值侧已由 [VERIFIED-LP] 的 `results/Q2_indep_nsweep.py` 独立确认(P1 到 P4)。
4. 有效参数范围: 2 <= j <= K-1, eta in (K-j, K-j+1), K >= 3, n >= 2K。j <= 1(eta > K-1)不在本次
   验证范围内,`Q1_closed_form.py` 的 note 3 已标其为 upper bound only。

**为什么 n = 2K 仍然恰好给出 V_j。** 在 n = 2K 时 X = K,可用的 tail 长度只有 m in 1..K-j。而

> m_c > eta(K-1) >= eta > K-j

(第一步是 m_c 的定义,第二步用 K >= 2,第三步用域条件 eta > K-j),所以 **m_c > K-j 恒成立**,
没有任何可用的 m 能触发 excess,D = D_base,值恰为 V_j。该不等式的状态: 在给定域上是
[VERIFIED-SYMBOLIC](三步都是域条件的直接后果,`C6.mc_gt_Kj`),并在 48/48 个 sweep 点上
exact-rational 复核通过。更一般地,**NO-TAIL regime 的精确刻画是 X - j <= eta(K-1)**,
即 n <= n_c - 1(`C6.regime`)。

**这对 TASKS10 路线意味着什么。** 前提 (b)(O-independence)与合法性在本族上是成立的(C1 到 C5
全部 [VERIFIED-SYMBOLIC]),失效的只有 (c) 这一条,且失效是单向的: 该族给出的 hardness 上界是
W(n),满足 rho_K = W(2K) <= W(n) <= W(oo) = V_j + (K-j)max_m E(m)。也就是说,这条构造能给出的
n -> oo 上界比 rho_K **弱**(数值更大),夹逼区间闭不上;要闭合就必须换族(例如让 O-independence
只在更小的区域成立,或放弃 y <= 1 的 balanced 定义),或者接受一个随 n 增大的上界。

## 12. 复现

```
python3 results/Q2_symbolic.py          # 全量,约 7 秒,exit 0
python3 results/Q2_symbolic.py quick    # 缩减 sweep
```

输出 `results/Q2_symbolic.json`: `status`(C0..C8)、`checks`(104 条,每条含 id / status /
statement / certificate)、`key_identities`(本报告引用的全部恒等式的字符串形式)、
`sweep_C6b`(48 行,每行含 m_c、m*、r_T、V_j、W、n_c、n_sat 与 fail 列表)。

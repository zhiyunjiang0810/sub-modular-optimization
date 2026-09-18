# ROUTE-TWO 盲证：thm:exact（$\rho_K(\eta)=\min_j V_j(\eta)$）

本文件是对 `results/V11/inputs/statement_exact.md` 的独立重证。只使用
`definition1.md`、`assumptions.md`、`notation.md` 三个输入文件里的定义与标准数学，
没有查阅论文正文、台账或任何既有证明。所有可复现脚本在
`/home/user/sub-modular-optimization/results/V11/route2/` 下。

---

## 1. 陈述复述（逐量词展开）

**记号**（取自 assumptions.md / notation.md，未改动）：
ground set $N$，$|N|=n$；$f:2^N\to\mathbb R_{\ge0}$ monotone submodular，$f(\emptyset)=0$；
cardinality budget $K$，$1\le K\le n$；predictor $\tilde f:2^N\to\mathbb R$，$\tilde f(\emptyset)=0$；
$d_e(S)=f(S\cup\{e\})-f(S)$，$\tilde d_e(S)=\tilde f(S\cup\{e\})-\tilde f(S)$。
$k_1=(K-1)\eta+1$，$q=(K-1)\eta/k_1=1-1/k_1$，
$$V_j(\eta)=1-q^{\,j}\Bigl(1-\frac{K-j}{K\eta}\Bigr),\qquad 0\le j\le K-1 .$$

**被证命题（我的措辞）。** 固定整数 $K\ge 2$ 与实数 $\eta\in[1,\infty)$。
定义
$$\rho_K(\eta)\;=\;\inf\Bigl\{\ \tfrac{f(S^K)}{F^{\mathrm{OPT}}}\ \Bigr\}$$
其中 inf 遍历一切满足下列条件的四元组 $(n,N,f,\tilde f)$ 与一切 tie-breaking 选择：

- **(Q1) 存在量词 $n$**：对每个整数 $n\ge K$ 各取一次，$\rho_K$ 是对 $n$ 取 inf（即
  $\rho_K=\inf_{n\ge K}\rho_{n,K}$）。下界方向对**任意** $n\ge K$ 成立；上界方向我给出的
  attaining instance 用 $n=2K$，因此 inf 在 $n=2K$ 处已经取到。
- **(Q2) 全称量词 $f$**：对一切 monotone submodular $f$ 且 $f(\emptyset)=0$；$F^{\mathrm{OPT}}=\max_{|T|=K}f(T)$；
  若 $F^{\mathrm{OPT}}=0$，按 assumptions.md 的约定该比值平凡成立，下面一律设 $F^{\mathrm{OPT}}=1$（齐次性，见 Step 1）。
- **(Q3) 全称量词 $\tilde f$**：对一切满足 Definition 1（def:eta）的 $\tilde f$，即存在
  $\eta_u,\eta_o\ge1$，$\eta_u\eta_o=\eta$，使得**对一切** $S\subseteq N$ 与**一切** $e\notin S$ 都有
  $d_e(S)/\eta_u\le\tilde d_e(S)\le\eta_o d_e(S)$。这是 single-element、multiplicative 版本，
  band 在全部 $2^n\cdot n$ 个 $(S,e)$ 上成立，不只在 greedy 轨迹上。
- **(Q4) 算法**：predictive greedy，deterministic 单步贪心，$t=0,\dots,K-1$ 每步取
  $\arg\max_{e\notin S^t}\tilde d_e(S^t)$；query 只落在 $\tilde f$ 上，query size 为单元素
  （每步只比较 $|S^t|+1$ 大小的集合值差）；**恰好执行 $K$ 步**，即使某步最大预测增益为 $0$ 也要选。
- **(Q5) tie breaking**：$\arg\max$ 非唯一时由 adversary 选择（adversarial ties）。这条**不是空洞的**：
  下面 Step 11 至 Step 15 的 attaining instance 在**每一步**都是 $e_t$ 与全部 $o_i$ 预测增益严格相等的
  full tie，若把 tie 改成任何偏向 $O^\ast$ 的规则，同一实例的比值变成 $1$。
- **(Q6) $\eta$ 的定义域**：$\eta\in[1,\infty)$。$\eta\ge1$ 由 Definition 1 的 $\eta_u,\eta_o\ge1$ 强制；
  $\eta=1$ 允许（此时 $\tilde f$ 与 $f$ 的单元素增益逐点相等）。$\eta=\infty$ 不在域内。
- **(Q7) $K$ 的定义域**：$K\ge2$ 整数。$K=1$ 时公式仍给出 $V_0=1/\eta$ 且结论正确，
  但“断点是整数 $2,\dots,K$”这一句在 $K=1$ 退化为空集，所以 $K\ge2$ 是陈述卫生所需，
  不是数学内容所需（空洞性检验记录见 §5）。

**结论。**
$$\rho_K(\eta)=\min_{0\le j\le K-1}V_j(\eta),$$
且 $\min$ 在 $j^\ast(\eta)=\min\{K-1,\max\{0,\lceil K-\eta\rceil\}\}$ 处取到；
等价地 $V_j$ 在 $\eta\in[K-j,K-j+1]$ 上是 minimizer（$j=0$ 时区间为 $[K,\infty)$），
断点是整数 $2,3,\dots,K$。特别地 $\rho_K(\eta)=1/\eta$ 当且仅当 $\eta\ge K$。
$K\in\{2,3,4\}$ 的闭式见 Step 16。

---

## 2. 推导

约定：$S^0=\emptyset$，$S^{t+1}=S^t\cup\{e_t\}$，$g_t=d_{e_t}(S^t)$，
$O=O^\ast=\{o_1,\dots,o_K\}$ 是一个最优 $K$-set，
$m_{i,t}=d_{o_i}(S^t)$ 若 $o_i\notin S^t$，否则 $m_{i,t}:=0$。
$R_t=F^{\mathrm{OPT}}-f(S^t)$，$\theta=1-1/\eta\in[0,1)$。

### Step 1（归一化与 band 的重标定）[HAND-PROOF-UNREVIEWED]
用到：assumptions.md（$F^{\mathrm{OPT}}=0$ 平凡）、definition1.md 的 scaling 说明。
比值 $f(S^K)/F^{\mathrm{OPT}}$ 在 $f\mapsto cf$ 下不变，故设 $F^{\mathrm{OPT}}=1$。
又 predictive greedy 的 $\arg\max$ 在 $\tilde f\mapsto\tilde f/\eta_o$ 下不变，而 band
$d/\eta_u\le\tilde d\le\eta_o d$ 变为 $d/(\eta_u\eta_o)\le\tilde d\le d$。
因此**不失一般性**取 $\eta_u=\eta,\ \eta_o=1$，band 写作
$$d_e(S)/\eta\ \le\ \tilde d_e(S)\ \le\ d_e(S)\qquad\forall S,\ \forall e\notin S. \tag{1}$$
（这一步只用于化简书写；下界方向的推导只用 $\eta_u\eta_o=\eta$，不依赖此归一化。）

### Step 2（逐步选择误差，Lemma A）[HAND-PROOF-UNREVIEWED]
用到：Step 1 的 (1)、Q4 的 $\arg\max$、Definition 1。
对任意 $x\notin S^t$，
$$d_x(S^t)\ \overset{(1)}{\le}\ \eta_u\tilde d_x(S^t)\ \overset{\arg\max}{\le}\ \eta_u\tilde d_{e_t}(S^t)\ \overset{(1)}{\le}\ \eta_u\eta_o\,g_t=\eta\,g_t. \tag{2}$$
即 $M_t:=\max_{x\notin S^t}d_x(S^t)\le\eta g_t$。这正是 def:etasel 里 $\etasel\le\eta$ 的内容，
也是 Goundan–Schulz 意义下 $\alpha$-approximate incremental oracle，$\alpha=\eta$。
**注意：只用 (2) 得到的最好界是 $L_K(\eta)=1-(1-\frac1{K\eta})^K$，它严格小于 $\rho_K$**
（例：$K=3,\eta=2$，$L_3=91/216\approx0.4213 < 7/15=\rho_3$），
所以 (2) 不足以定出精确值，必须引入 Step 3。

### Step 3（两元素一致性，Lemma B；本证明的关键）[HAND-PROOF-UNREVIEWED]
用到：Q4 的 $\arg\max$、Definition 1 的 band 在 $(S^t\cup\{o\},e_t)$ 与 $(S^{t+1},o)$ 两处、
$\tilde f$ 是集合函数（两条链到同一集合给同一值）、$f$ 的同一恒等式。

设 $o\notin S^{t+1}$，写 $S=S^t$，$e=e_t$。因为 $\tilde f$ 是集合函数，
$$\tilde f(S\cup\{e,o\})=\tilde f(S\cup e)+\tilde d_o(S\cup e)=\tilde f(S\cup o)+\tilde d_e(S\cup o).$$
greedy 在 $S$ 处选 $e$ 给出 $\tilde d_e(S)\ge\tilde d_o(S)$，即 $\tilde f(S\cup e)\ge\tilde f(S\cup o)$。
两式相减得
$$\tilde d_o(S\cup e)\ \le\ \tilde d_e(S\cup o).$$
再对左端用 band 下界、对右端用 band 上界：
$$\frac{d_o(S\cup e)}{\eta_u}\le\tilde d_o(S\cup e)\le\tilde d_e(S\cup o)\le\eta_o\,d_e(S\cup o)
\quad\Longrightarrow\quad d_o(S\cup e)\ \le\ \eta\,d_e(S\cup o). \tag{3}$$
而 $f$ 自身的两条链给出恒等式（无不等号）
$$d_e(S\cup o)=d_e(S)+d_o(S\cup e)-d_o(S).$$
代入 (3)，用 $m_{o,t}=d_o(S^t)$、$m_{o,t+1}=d_o(S^{t+1})$、$g_t=d_e(S)$：
$$m_{o,t+1}\le\eta\bigl(g_t+m_{o,t+1}-m_{o,t}\bigr)
\iff \boxed{\,m_{o,t}\ \le\ g_t+\theta\,m_{o,t+1}\,},\qquad \theta=1-\tfrac1\eta. \tag{4}$$
**(4) 蕴含 (2)**：由 submodularity $m_{o,t+1}\le m_{o,t}$ 代入 (4) 得 $m_{o,t}\le\eta g_t$。
所以 (4) 是比 Lemma A 严格更强的逐步约束，它是 $k_1=(K-1)\eta+1$ 出现的唯一来源。

边界情形（用到 monotonicity）：若 $o=e_t$ 则 $m_{o,t}=g_t$，$m_{o,t+1}=0$，(4) 取等；
若 $o\in S^t$ 则两端皆 $0\le g_t$。故 (4) 对一切 $o\in O$、一切 $0\le t\le K-1$ 成立。

### Step 4（覆盖不等式）[HAND-PROOF-UNREVIEWED]
用到：$f$ 的 monotone + submodular、$F^{\mathrm{OPT}}=1$。
$$1=f(O)\le f(O\cup S^t)\le f(S^t)+\!\!\sum_{o\in O\setminus S^t}\!\!d_o(S^t)
= f(S^t)+\sum_{i=1}^{K}m_{i,t}. \tag{5}$$
（第二个不等号是 submodularity 的标准逐元素展开；$m_{i,t}=0$ 的约定使求和范围可写成全部 $i$。）

### Step 5（run 的 LP relaxation）[HAND-PROOF-UNREVIEWED]
用到：Step 3 的 (4)、Step 4 的 (5)、submodularity $m_{i,t+1}\le m_{i,t}$、monotonicity $g_t\ge0$。
任一 run 的数据 $(g_t)_{t<K}$、$(m_{i,t})_{t\le K}$ 是下列 LP 的可行点，且
$f(S^K)=\sum_{t<K}g_t$（telescoping，$f(\emptyset)=0$）：
$$
\textbf{(P)}\quad
\min\ \sum_{t=0}^{K-1}g_t
\ \ \text{s.t.}\ \
\begin{cases}
\text{(A}_t)\ \sum_{s<t}g_s+\sum_i m_{i,t}\ \ge\ 1, & 0\le t\le K-1,\\[2pt]
\text{(B}_t)\ K\,g_t+\theta\sum_i m_{i,t+1}-\sum_i m_{i,t}\ \ge\ 0, & 0\le t\le K-1,\\[2pt]
\text{(C}_t)\ \sum_i m_{i,t}-\sum_i m_{i,t+1}\ \ge\ 0, & 0\le t\le K-1,\\[2pt]
g\ge0,\ m\ge0 .
\end{cases}
$$
（(B$_t$) 是 (4) 对 $i$ 求和；对 $i$ 求和不丢信息：给定聚合量 $P_t=\sum_i m_{i,t}$ 的可行解，
令 $m_{i,t}=P_t/K$ 即还原逐 $i$ 的 (4) 与单调性。）因此
$$\rho_K(\eta)\ \ge\ \mathrm{val}(\textbf{P}). \tag{6}$$
注意 (P) 的规模只依赖 $K$，与 $n$ 无关，所以 (6) 对一切 $n\ge K$ 一致成立。

### Step 6（对称化 / 聚合变量）[HAND-PROOF-UNREVIEWED]
令 $P_t=\sum_i m_{i,t}$，$t=0,\dots,K$。(P) 即
$$\min\sum_t g_t\ \text{ s.t. }\ \text{(A}_t)\ \sum_{s<t}g_s+P_t\ge1,\ \
\text{(B}_t)\ Kg_t+\theta P_{t+1}-P_t\ge0,\ \ \text{(C}_t)\ P_t-P_{t+1}\ge0,\ \ g,P\ge0 .$$

### Step 7（dual multipliers）[VERIFIED-SYMBOLIC]
对偶（(A$_t$)↔$y_t$，(B$_t$)↔$z_t$，(C$_t$)↔$w_t$，$t=0,\dots,K-1$）：
$$
\textbf{(D)}\quad \max\ \sum_t y_t \ \ \text{s.t.}\ \
\begin{cases}
(\mathrm{Dg}_t)\ \sum_{t'>t}y_{t'}+K z_t\le1,\\
(\mathrm{DP}_t)\ y_t-z_t+\theta z_{t-1}+w_t-w_{t-1}\le0,& 0\le t\le K-1,\\
(\mathrm{DP}_K)\ \theta z_{K-1}-w_{K-1}\le0,\\
y,z,w\ge0,\quad z_{-1}=w_{-1}=0 .
\end{cases}
$$
对每个 $j$ 与 $\eta$ 属于其 segment $[K-j,K-j+1]$（$j=0$ 时 $[K,\infty)$），取
$$
z_t=\frac1K\ (t\ge j),\qquad
z_{j-1}=\frac{K\eta-K+j}{K\,k_1},\qquad
z_t=q^{\,j-1-t}z_{j-1}\ (0\le t\le j-1),
$$
$$
w_t=0\ (t<j),\qquad w_t=\frac{\theta}{K}-\frac{K-1-t}{K\eta}\ (t\ge j),\qquad
y_t=z_t-\theta z_{t-1}-w_t+w_{t-1}.
$$
这是由 complementary slackness 反解出来的（(A$_t$) 在 $t\le j$ 紧、(B$_t$) 全紧、(C$_t$) 在 $t\ge j$ 紧）。
两个非负性恰好给出 segment 的两个端点：
$$w_j=\frac{\eta-(K-j)}{K\eta}\ \ge0\iff \eta\ge K-j,\qquad
y_j=\frac{(K-j+1)-\eta}{k_1}\ \ge0\iff \eta\le K-j+1 .$$
**oracle：** `dual_certificate.py` 用 sympy 以符号 $\eta$ 验证了 $K=2,\dots,7$、全部 $j$：
所有 $(\mathrm{Dg}_t)$、$(\mathrm{DP}_t)$、$(\mathrm{DP}_K)$ 与 $y,z,w\ge0$ 在各自 segment 上无违反。

### Step 8（dual objective $=V_j$）[VERIFIED-SYMBOLIC]
上述取法下 $\sum_{t}y_t=V_j(\eta)$。手算路径：$j\ge1$ 时 $(\mathrm{Dg}_0)$ 取等给
$\sum_t y_t=1-(K-1)z_0$，而 $z_0=q^{\,j-1}z_{j-1}$，代入并用 $\frac{K-1}{k_1}=\frac q\eta$ 得
$$\sum_t y_t=1-\frac{q^{\,j}(K\eta-K+j)}{K\eta}=1-q^{\,j}\Bigl(1-\frac{K-j}{K\eta}\Bigr)=V_j .$$
$j=0$ 时直接 $y_0=1/\eta=V_0$，$y_t=0\ (t\ge1)$。
**oracle：** 同 `dual_certificate.py`，$K=2,\dots,7$ 全部 $j$ 符号恒等式为真。
由 weak duality 与 (6)：
$$\rho_K(\eta)\ \ge\ \mathrm{val}(\textbf{P})\ \ge\ V_j(\eta)\quad\text{对该 segment 的 }j. \tag{7}$$

### Step 9（哪个 $j$ 最小：段结构）[VERIFIED-SYMBOLIC]
令 $c_j=q^{\,j}\bigl(1-\frac{K-j}{K\eta}\bigr)$，则 $V_j=1-c_j$，最小化 $V_j$ 等价于最大化 $c_j$。
直接计算
$$c_{j+1}\ge c_j\iff q\bigl(K\eta-K+j+1\bigr)\ge K\eta-K+j\iff q\,k_1\ge K\eta-K+j\iff \eta\le K-j .$$
故 $c_j$ 关于 $j$ 先增后减，最大值在 $j^\ast=\lceil K-\eta\rceil$（截断到 $[0,K-1]$）处，
即 $V_j$ 在 $\eta\in[K-j,K-j+1]$ 上是 minimizer，断点为整数 $2,\dots,K$。
又 $V_K-V_{K-1}=q^{K-1}\bigl(\frac1{k_1}-\frac1{K\eta}\bigr)\ge0$（因 $k_1\le K\eta$），
所以把 $j=K$ 加进来也不改变 $\min$，$j$ 的范围 $0\le j\le K-1$ 是充分的。
$\eta\ge K$ 时 $j^\ast=0$、$V_0=1/\eta$；$\eta<K$ 时 $c_1>c_0$ 严格，故 $\rho_K<1/\eta$，
于是“$\rho_K=1/\eta$ **当且仅当** $\eta\ge K$”。
**oracle：** `dual_certificate.py` 的 `check_argmin` 对 $K=2,\dots,6$ 符号验证
$(c_{j+1}-c_j)/(K-j-\eta)$ 在 $\eta\ge1$ 上恒正。

### Step 10（下界方向小结）[HAND-PROOF-UNREVIEWED + VERIFIED-SYMBOLIC 的证书]
对给定 $(K,\eta)$ 取 $j=j^\ast(\eta)$，由 (7) 与 Step 9：
$$\rho_K(\eta)\ \ge\ \min_{0\le j\le K-1}V_j(\eta)\qquad\text{对一切 }n\ge K. \tag{8}$$
链条依赖：Step 3 (4) → Step 4 (5) → Step 5 (P) → Step 7/8 证书 → Step 9 段选择。

### Step 11（attaining instance 的 $f$）[HAND-PROOF-UNREVIEWED，K≤5 为 VERIFIED-EXHAUSTIVE]
固定 $j\in\{0,\dots,K-1\}$。令
$$R_0=1,\quad g_t=\frac{R_t}{k_1}\ (t<j),\quad g_t=\frac{R_j}{K\eta}\ (t\ge j),\quad R_{t+1}=R_t-g_t,$$
于是 $R_t=q^{\,t}$ 对 $t\le j$。ground set $N=\{e_0,\dots,e_{K-1}\}\cup\{o_1,\dots,o_K\}$，$n=2K$。
$f$ 取为下列 atom 系统的 coverage function（测度 $\mu$，coverage function 自动 monotone submodular）：

| atom | 测度 | 被哪些元素覆盖 |
|---|---|---|
| $a(i,s)$，$1\le i\le K$，$0\le s<j$ | $g_s/K$ | $o_i$ 与 $e_s$ |
| $a(i,\infty)$，$1\le i\le K$ | $R_j/K$ | 只有 $o_i$ |
| $\tau_t$，$j\le t\le K-1$ | $g_t=R_j/(K\eta)$ | 只有 $e_t$ |

于是 $A_{o_i}$ 两两不交、测度各 $1/K$；head 元素 $e_t\ (t<j)$ 的集合 $A_{e_t}=\bigcup_i a(i,t)$ 测度 $g_t$，
完全落在 $\Omega_O=\bigcup_iA_{o_i}$ 内；tail 元素 $e_t\ (t\ge j)$ 的集合是私有的 $\tau_t$。
直接计算：$f(O)=1$；$f(S^t)=\sum_{s<t}g_s=1-R_t$；
$d_{o_i}(S^t)=R_t/K\ (t\le j)$，$=R_j/K\ (t>j)$；$d_{e_t}(S^t)=g_t$。

### Step 12（attaining predictor $\tilde f$，闭式）[HAND-PROOF-UNREVIEWED，K≤5 为 VERIFIED-EXHAUSTIVE]
令 $C(S)=\bigcup_{x\in S}A_x$，$\beta(S)=\max_{1\le i\le K}\mu\bigl(A_{o_i}\cap C(S)\bigr)$，取
$$\boxed{\ \tilde f(S)\ =\ f(S)\ -\ \Bigl(1-\frac1\eta\Bigr)\,\beta(S)\ }\qquad(\eta_u=\eta,\ \eta_o=1).$$
**band 成立**：写 $\Lambda=f-\beta$，则 $\tilde f=\frac1\eta f+\theta\Lambda$，故只需
$0\le\Lambda_x(S)\le d_x(S)$，即 $0\le\beta(S\cup x)-\beta(S)\le d_x(S)$。左边由 $\beta$ 单调；
右边因为 $\beta$ 是 $K$ 个单调函数 $\beta_i(S)=\mu(A_{o_i}\cap C(S))$ 的逐点极大，故
$$\beta(S\cup x)-\beta(S)\le\max_i\bigl[\beta_i(S\cup x)-\beta_i(S)\bigr]
=\max_i\mu\bigl(A_{o_i}\cap A_x\setminus C(S)\bigr)\le\mu\bigl(A_x\setminus C(S)\bigr)=d_x(S).$$
（最后一步用 $A_{o_i}$ 两两不交。）这对**一切** $S$ 与 $x\notin S$ 成立，符合 Q3 的全称量词，
并自动满足 Definition 1 的 “$d_e(S)=0\Rightarrow\tilde d_e(S)=0$”。
$\tilde f$ 不必 submodular，Definition 1 与 assumptions.md 也没有要求它 submodular。

**轨迹上的取值。** $\beta(S^t)=\frac1K\sum_{s<\min(t,j)}g_s$，于是
$$\Lambda_{e_t}(S^t)=\tfrac{K-1}{K}g_t\ (t<j),\qquad \Lambda_{e_t}(S^t)=g_t\ (t\ge j),\qquad
\Lambda_{o_i}(S^t)=0\ \ \forall t,i .$$

### Step 13（$F^{\mathrm{OPT}}=1$）[HAND-PROOF-UNREVIEWED，K≤5 为 VERIFIED-EXHAUSTIVE]
设 $|T|=K$，其中 $r$ 个来自 $O$、若干 head、$p$ 个 tail（$p\le K-r$）。则
$$f(T)\le\underbrace{\frac rK}_{\text{被选中的 }A_{o_i}}
+\underbrace{\frac{K-r}{K}\sum_{s<j}g_s}_{\text{head 只能吃未选 }o\text{ 的份额}}
+\underbrace{p\,\frac{R_j}{K\eta}}_{\text{tail 私有}}
\le \frac rK+\Bigl(1-\frac rK\Bigr)\Bigl[(1-R_j)+\frac{R_j}{\eta}\Bigr]\le1,$$
最后一步用 $\eta\ge1\Rightarrow(1-R_j)+R_j/\eta\le1$。结合 $f(O)=1$ 得 $F^{\mathrm{OPT}}=1$。

### Step 14（greedy 轨迹与 ties）[HAND-PROOF-UNREVIEWED，K≤5 为 VERIFIED-EXHAUSTIVE]
用 $\tilde d_x(S^t)=\frac{d_x(S^t)}{\eta}+\theta\Lambda_x(S^t)$ 与 Step 12 的轨迹值：

- head 步 $t<j$：$\tilde d_{e_t}(S^t)=\frac{g_t}{\eta}+\theta\frac{K-1}{K}g_t
  =\frac{g_t\,[\,K+(\eta-1)(K-1)\,]}{K\eta}=\frac{g_t\,k_1}{K\eta}=\frac{R_t}{K\eta}$
  （用到恒等式 $K+(\eta-1)(K-1)=k_1$ 与 $g_t=R_t/k_1$）；
  而 $\tilde d_{o_i}(S^t)=\frac{m_t}{\eta}=\frac{R_t}{K\eta}$。**两者相等，是 tie。**
  尚未选的 head $e_u\ (u>t)$ 给 $\frac{g_u k_1}{K\eta}\le\frac{g_tk_1}{K\eta}$（$g$ 在 head 上递减）；
  tail $e_u$ 给 $\frac{g_u}{\eta}+\theta g_u=g_u=\frac{R_j}{K\eta}\le\frac{R_t}{K\eta}$。
- tail 步 $t\ge j$：$\tilde d_{e_t}(S^t)=g_t=\frac{R_j}{K\eta}$，
  $\tilde d_{o_i}(S^t)=\frac{R_j/K}{\eta}=\frac{R_j}{K\eta}$，其它 tail 同值。**又是 tie。**

因此在 adversarial tie breaking 下 greedy 依次选 $e_0,\dots,e_{K-1}$，恰好 $K$ 步（Q4/Q5）。
反之若 tie 偏向 $O^\ast$，同一实例给比值 $1$，故 Q5 这个限定词非空。

### Step 15（$F^{\mathrm{ALG}}=V_j$）[VERIFIED-SYMBOLIC + VERIFIED-EXHAUSTIVE]
$$F^{\mathrm{ALG}}=\sum_{t<K}g_t=(1-R_j)+(K-j)\frac{R_j}{K\eta}
=1-q^{\,j}\Bigl(1-\frac{K-j}{K\eta}\Bigr)=V_j(\eta).$$
**oracle：** `symbolic_instance_identities.py` 对 $K=2,\dots,8$、全部 $j$、符号 $\eta$ 验证
$\sum_t g_t=V_j$ 与 Step 14 用到的三个恒等式；
`verify_instance_exact.py` 用 `fractions.Fraction` 对 $K=2,3,4$（$\eta\in\{1,\frac54,\frac32,2,\frac94,\frac52,3,\frac72,4,\frac92,5,6\}$、
全部 $j$）与 $K=5$（8 个 $\eta$）逐 $S$、逐 $e$ 穷举验证 monotonicity、submodularity、
band (1)、zero-preservation、greedy trace、$f(O)=1$、$F^{\mathrm{OPT}}=1$、$F^{\mathrm{ALG}}=V_j$，全部通过。

### Step 16（合并）[结论标签见下]
由 Step 10 的 (8) 与 Step 11–15（取 $j=j^\ast(\eta)$）得
$$\rho_K(\eta)=\min_{0\le j\le K-1}V_j(\eta),$$
$V_{j}$ 的 segment 与断点由 Step 9 给出。展开闭式（`dual_certificate.py` 的 `closed_forms`，
sympy 因式化）：
$$\rho_2=\min\Bigl\{\tfrac1\eta,\ \tfrac{3}{2(\eta+1)}\Bigr\};$$
$$\rho_3=\frac{16\eta+3}{3(2\eta+1)^2},\quad \frac{7}{3(2\eta+1)},\quad \frac1\eta
\qquad\text{分别在 }[1,2],[2,3],[3,\infty);$$
$$\rho_4=\frac{135\eta^2+36\eta+4}{4(3\eta+1)^3},\quad\frac{21\eta+2}{2(3\eta+1)^2},
\quad\frac{13}{4(3\eta+1)},\quad\frac1\eta
\qquad\text{分别在 }[1,2],[2,3],[3,4],[4,\infty).$$
与被证陈述逐字一致。

**独立交叉验证（不依赖上面的结构猜测）**：`lp_full_instance.py` 把
“$f$ monotone submodular + $\tilde f$ 满足 band + greedy 的 $\arg\max$ 不等式 +
$f(O)=1$ 且一切 $K$-set $\le1$”整体写成一个以 $\bigl(f(S),\tilde f(S)\bigr)_{S\subseteq N}$ 为变量的
线性规划（$n=2K$），最小化 $f(S^K)$。结果（HiGHS，浮点）：
$K=2$（7 个 $\eta$）、$K=3$（7 个 $\eta$）、$K=4$（8 个 $\eta$）共 22 个格点，
LP 最优值与 $\min_jV_j$ 的差均在 $3\times10^{-16}$ 以内。[VERIFIED-LP]
（这一步是浮点的，只作旁证；决定性结论由 Step 7/8 的符号证书与 Step 15 的有理穷举承担。）

---

## 3. 数值走查：$K=3$，$\eta=3/2$

（任务里的括注“ProbeLottery 用 $K=2$”不适用于 thm:exact，此处按 $K=3,\eta=3/2$ 走查。）

$k_1=2\cdot\frac32+1=4$，$q=\frac{3}{4}$，$\theta=\frac13$，
$j^\ast=\lceil K-\eta\rceil=\lceil 1.5\rceil=2$，$\eta=\frac32\in[K-j,K-j+1]=[1,2]$ ✓。

**profile（全部有理）**

| $t$ | $R_t$ | $g_t$ | $m_t=d_{o_i}(S^t)$ | $f(S^t)$ | $\tilde d_{e_t}(S^t)=\tilde d_{o_i}(S^t)$ |
|---|---|---|---|---|---|
| 0 | $1$ | $1/4$ | $1/3$ | $0$ | $2/9$ |
| 1 | $3/4$ | $3/16$ | $1/4$ | $1/4$ | $1/6$ |
| 2 | $9/16$ | $1/8$ | $3/16$ | $7/16$ | $1/8$ |

$t=0,1$ 是 head（$g_t=R_t/4$），$t=2$ 是 tail（$g_2=R_2/(K\eta)=\frac{9/16}{9/2}=\frac18$）。
$$F^{\mathrm{ALG}}=\tfrac14+\tfrac3{16}+\tfrac18=\tfrac9{16},\qquad
V_2=1-\Bigl(\tfrac34\Bigr)^2\Bigl(1-\tfrac{1}{3\cdot 3/2}\Bigr)=1-\tfrac9{16}\cdot\tfrac79=\tfrac9{16},$$
闭式核对 $\frac{16\eta+3}{3(2\eta+1)^2}=\frac{27}{48}=\frac9{16}$ ✓。
$\min_jV_j$：$V_0=\frac23$，$V_1=\frac{7}{3\cdot4}=\frac7{12}$，$V_2=\frac9{16}$，最小者确为 $V_2$ ✓。

**实例（$n=6$）**：$\mu(A_{o_i})=\frac13$，其中 $a(i,0)=\frac1{12}$、$a(i,1)=\frac1{16}$、$a(i,\infty)=\frac3{16}$
（和 $=\frac{4+3+9}{48}=\frac13$ ✓）；$A_{e_0}=\{a(i,0)\}_i$ 测度 $\frac14$，
$A_{e_1}=\{a(i,1)\}_i$ 测度 $\frac3{16}$，$\tau_2$ 测度 $\frac18$。
predictor：$\tilde f=f-\frac13\beta$，$\beta(\emptyset)=0$，$\beta(S^1)=\frac1{12}$，$\beta(S^2)=\frac7{48}$。
核对 $\tilde d_{e_0}(\emptyset)=\frac14-\frac13\cdot\frac1{12}=\frac29$，
band 区间 $[\frac14/\frac32,\frac14]=[\frac16,\frac14]\ni\frac29$ ✓；
$\tilde d_{o_i}(\emptyset)=\frac13-\frac13\cdot\frac13=\frac29$，band 区间 $[\frac29,\frac13]$ 的**下端** ✓，两者相等即 tie。

**dual 证书（$j=2$）**
$$z=(z_0,z_1,z_2)=\Bigl(\tfrac7{32},\ \tfrac7{24},\ \tfrac13\Bigr),\quad
w=(0,0,\tfrac19),\quad y=\Bigl(\tfrac7{32},\ \tfrac7{32},\ \tfrac18\Bigr).$$
可行性核对：$(\mathrm{Dg}_0)$：$y_1+y_2+3z_0=\frac7{32}+\frac18+\frac{21}{32}=1$ ✓；
$(\mathrm{Dg}_1)$：$y_2+3z_1=\frac18+\frac78=1$ ✓；$(\mathrm{Dg}_2)$：$3z_2=1$ ✓；
$(\mathrm{DP}_3)$：$\theta z_2=\frac19=w_2$ ✓；$y,z,w\ge0$ ✓（$w_2=\frac{\eta-(K-j)}{K\eta}=\frac{1/2}{9/2}=\frac19$，
$y_2=\frac{(K-j+1)-\eta}{k_1}=\frac{1/2}{4}=\frac18$）。
目标值 $\sum y_t=\frac7{32}+\frac7{32}+\frac18=\frac{18}{32}=\frac9{16}=F^{\mathrm{ALG}}$，primal 与 dual 相等，
$\rho_3(3/2)=\frac9{16}$。

**Lemma A 与 Lemma B 的差距（说明为什么需要 Step 3）**：
若只用 (2)（即只有 $m_{i,t}\le\eta g_t$），LP 的最优值是
$L_3(3/2)=1-\bigl(1-\frac{1}{K\eta}\bigr)^K=1-\bigl(\frac79\bigr)^3=\frac{386}{729}\approx0.5295$，
严格小于真值 $\frac9{16}=0.5625$，所以 Lemma A 单独不够。
加上 (4) 之后，head 的剩余量递推率从 $\frac1{K\eta}=\frac29$ 收紧到 $\frac1{k_1}=\frac14$
（$R_{t+1}=qR_t$，$q=\frac34$），才得到正确值。

---

## 4. 复现脚本

| 文件 | 作用 | 标签 |
|---|---|---|
| `dual_certificate.py` | sympy 符号验证 dual 可行性、目标值 $=V_j$、$c_j$ 的单峰性、$K\le4$ 闭式 | [VERIFIED-SYMBOLIC] |
| `symbolic_instance_identities.py` | 符号验证实例族的 5 个恒等式（$K=2..8$，全部 $j$） | [VERIFIED-SYMBOLIC] |
| `verify_instance_exact.py` | `Fraction` 逐 $S$ 逐 $e$ 穷举验证实例族（$K=2..5$） | [VERIFIED-EXHAUSTIVE] |
| `lp_full_instance.py` | 以 $(f,\tilde f)$ 为变量的完整实例 LP，独立复核 $\rho_K$（浮点） | [VERIFIED-LP] |
| `instance_family.py` | 实例族构造 + 给定 $f$ 时 predictor 的可行性 LP（中间产物） | [VERIFIED-LP] |
| `extract_instance.py` | 从完整 LP 最优解读出轨迹 profile（用于发现构造） | 诊断脚本 |

---

## 5. 未闭合的步骤 / 追加的假设 / 空洞性检验

1. **一般 $K$ 的 dual 可行性没有 oracle 闭合。** Step 7/8 的证书对每个固定 $K$ 由 sympy 符号验证
   （$K=2,\dots,7$，符号 $\eta$，全部 $j$）。对任意 $K$ 的统一论证是手写的
   （complementary slackness 反解 + 两个端点不等式），状态 [HAND-PROOF-UNREVIEWED]。
   我没有写出对 $K$ 的归纳并让 oracle 确认。
2. **一般 $K$ 的实例合法性没有 oracle 闭合。** Step 11–14 的 band 与 greedy 论证是手写的
   （$\beta$ 是 $K$ 个单调函数的极大、$A_{o_i}$ 两两不交），逐 $S$ 逐 $e$ 的穷举只做到 $K=5$
   （$n=10$，$2^{10}$ 个子集）。$K\ge6$ 的实例合法性状态为 [HAND-PROOF-UNREVIEWED]。
3. **LP relaxation 的紧性不是我证的，而是被实例闭合的。** Step 5 的 (P) 只是必要条件的集合；
   我没有独立论证“(P) 没有遗漏任何有效不等式”。结论之所以成立，是因为 Step 11–15 的实例
   把 (P) 的最优值实现了出来。`lp_full_instance.py` 的完整 $(f,\tilde f)$ LP 是浮点旁证
   （22 个格点，误差 $\le3\times10^{-16}$），不作为决定性依据。
4. **ground set 规模的最小性未处理。** 我只证 $n=2K$ **足够**（attaining instances 用 $n=2K$，
   $K$ 个 $O^\ast$ 元素与 $K$ 个 greedy 元素互不相同）。
   是否存在 $n<2K$ 的实例达到同一值、以及 $\rho_{n,K}$ 对小 $n$ 的形状，本文件没有结论。
   陈述里的 $\rho_K$ 我读作 $\inf_{n\ge K}\rho_{n,K}$；若原文的 $\rho_K$ 指某个固定的 $n$，
   上界方向需要该 $n\ge2K$。**这是我为读通陈述而追加的一条读法假设。**
5. **$\eta_u,\eta_o$ 的拆分。** Step 1 用 $\tilde f\mapsto\tilde f/\eta_o$ 把 band 归一到
   $(\eta_u,\eta_o)=(\eta,1)$。在 definition1.md 的 verbatim 版本下 $\eta_o=1$ 合法（$\ge1$），
   所以不需要 convention B。若某处要求 $\eta_o>1$ 严格，实例可整体乘常数后仍合法。
6. **边界与退化情形。** $\eta=1$：$\theta=0$，(4) 退化为 $m_{o,t}\le g_t$，实例族给
   $V_{K-1}=1-(1-\frac1K)^{K-1}(1-\frac1K)=1-(1-\frac1K)^K$，与 $L_K(1)=U_K(1)$ 一致，已在
   $K=2,3,4,5$ 有理穷举通过。$K=1$：公式给 $1/\eta$ 且正确，但断点集合为空，故陈述用 $K\ge2$。
   $\eta$ 恰在整数断点：两个 $V_j$ 相等，两套 dual 证书都可行（$w_j=0$ 或 $y_j=0$），无矛盾。
7. **空洞性检验（CLAUDE.md 要求，逐个限定词）。**
   - *adversarial tie breaking*：非空。去掉它（例如偏向 $O^\ast$ 的确定性 tie 规则），
     Step 14 的实例比值变 $1$；我的实例在**每一步**都是 full tie，所以整个上界方向依赖这个词。
   - *恰好 $K$ 步*：非空。assumptions.md 已记载提前停止会掉到 $1/2$ 级别；我的实例在
     tail 步的预测增益为正，所以“$K$ 步”在这里不吃紧，但 $j=0$ 段的实例里 head 为空、
     全部增益来自 tail，若允许提前停止则比值可以更差，结论会改变。
   - *single-element error*：非空。(3) 用到了 band 在 $(S^t\cup\{o\},e_t)$ 这个**非轨迹**状态上的上界；
     只在 greedy 轨迹状态上成立的 $\eta^{\mathrm{path}}$ 版本推不出 (4)。
   - *monotone submodular $f$*：非空。Step 4 的 (5) 与 Step 3 的 $m_{o,t+1}\le m_{o,t}$ 都要它。
   - *$\tilde f$ 无结构假设*：非空且是本证明的必要条件。Step 12 的 $\tilde f=f-\theta\beta$
     不是 submodular（$\beta$ 取 max）；我尝试过把 $\tilde f$ 限制为 coverage function
     （density 形式 $\tilde\mu\in[\mu/\eta,\mu]$），可以手算出在 $j\ge2$ 时**不可行**
     （head 步要求 $R_{t+1}\le R_j$，对 $t<j-1$ 不成立），所以“$\tilde f$ 只需是集合函数”这个
     宽松度在上界方向是吃紧的。若把 $\tilde f$ 限制为 submodular，本文件的上界不适用。[FAILED
     的是 density 形式的 predictor 构造，具体失败不等式：head 步 $t<j-1$ 处
     $\lambda_tg_t(K-1)\ge\sum_{s>t}\lambda_sg_s+\lambda_\infty R_j$ 在 $\lambda\in[1/\eta,1]$ 内无解。]
   - *deterministic*：陈述未出现该词，我也没有引入随机化；predictive greedy 除 tie 外确定。

---

## 6. 读过的文件

- `/home/user/sub-modular-optimization/results/V11/inputs/definition1.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/assumptions.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/notation.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/statement_exact.md`

（隔离纪律：除上述四个文件外，没有打开、grep、列出或搜索仓库中任何其他文件；
`/home/user/sub-modular-optimization/CLAUDE.md` 由会话环境自动注入，非我主动读取。
没有使用 web search，没有运行 git，新写文件全部位于 `results/V11/route2/`。）

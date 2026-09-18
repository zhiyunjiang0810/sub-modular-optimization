# ROUTE-TWO 盲审独立推导：thm:linear-anysize（T10d / J7）

本文件是 route-two blind prover 的独立推导。作者只读了本目录 `inputs/` 下的五个文件（清单见
第 5 节），没有读附录、没有读 ledger、没有联网、没有跑 git。所有决策性算术用
`fractions.Fraction` 或 sympy 精确完成，float 只出现在打印里。可复跑脚本放在
`results/V11/route2/`：

| 脚本 | 作用 |
| --- | --- |
| `check_symbolic.py` | 恒等式 S1–S8（sympy） |
| `check_selection.py` | 选择引理 S9（sympy） |
| `check_family.py` | 单格精确审计（Fraction） |
| `run_grid.py` | 两遍网格穷举（62208 + 350 格） |
| `check_leakage.py` | 泄漏结构 P1–P4 |
| `check_analytic_bound.py` | 解析子引理 A1–A4 |
| `check_misc.py` | $n=K+1$ 见证 M1、$\beta$ 单调性 M2 |

---

## 1. 陈述的复述（逐个量词）

用我自己的话把 thm:linear-anysize 重写一遍，把每个量词写到明处。

**固定的参数。** 一个整数 $K$，满足 $K\ge3$；一个实数 $\eta$，满足 $\eta>1$。两者都是先固定、
再让 $n\to\infty$ 的；$K$ 不随 $n$ 变，$\eta$ 也不随 $n$ 变。

**实例类 $\mathcal I_n(K,\eta)$。** 对每个整数 $n\ge K$，$\mathcal I_n(K,\eta)$ 是所有满足下列条件的
三元组 $(N,f,\tilde f)$ 的集合：

* $N$ 是 ground set，$|N|=n$；
* $f:2^N\to\mathbb R_{\ge0}$ monotone submodular，$f(\emptyset)=0$（assumptions.md）；
* $\tilde f:2^N\to\mathbb R$，$\tilde f(\emptyset)=0$，并且**存在** $\eta_u,\eta_o>0$ 使得
  $\eta_u\eta_o\le\eta$ 且对**所有** $S\subseteq N$ 和**所有** $e\notin S$ 有
  $d_e(S)/\eta_u\le\tilde d_e(S)\le\eta_o\,d_e(S)$（definition1.md，convention B；
  这里 single-element 版本，$S$ 跑遍全部 $2^N$，不只是 greedy 轨迹）。
  “error product at most $\eta$” 即 $\eta_u\eta_o\le\eta$。
* 由 Definition 1，$d_e(S)=0$ 当且仅当 $\tilde d_e(S)=0$。

**算法类 $\mathcal A_n$。** 存在常数 $c$（与 $n$ 无关，可依赖 $K,\eta$），使得算法是 deterministic 的，
在任何实例上最多发出 $c\,nK$ 次 query；每次 query 是一个**任意大小**的集合 $S\subseteq N$（$|S|$ 从
$0$ 到 $n$ 都允许，这是与 single-element / bounded-size 版本的唯一区别），oracle 返回
$\tilde f(S)$；算法只能看到 $\tilde f$，永远看不到 $f$（assumptions.md）。query 是 adaptive 的：
第 $i$ 次 query 可以任意依赖前 $i-1$ 次的返回值。算法最终输出一个集合
$T\subseteq N$，$|T|\le K$（注意是 at most $K$，不是 exactly $K$）。

**比值约定。** $F^{\mathrm{OPT}}=\max_{|S|\le K}f(S)=f(O^\ast)$；ratio
$\alpha\in(0,1]$ 满足 $f(T)\ge\alpha F^{\mathrm{OPT}}$，越大越好（notation.md）。当
$F^{\mathrm{OPT}}=0$ 时该实例的 ratio 按 assumptions.md 约定平凡成立。

**被定义的量。**
$$\alpha_n(K,\eta)\;=\;\sup_{A\in\mathcal A_n}\ \inf_{I\in\mathcal I_n(K,\eta)}\ \frac{f(A(I))}{F^{\mathrm{OPT}}(I)},
\qquad
\alpha_{\mathrm{lin}}(K,\eta)\;=\;\lim_{n\to\infty}\alpha_n(K,\eta).$$
randomized 算法按自身随机性取期望来度量，即把 $f(A(I))$ 换成
$\mathbb E_{\text{coins}}[f(A(I))]$；下文第 2.6 步说明这不改变上界。

**$\rho_K(\eta)$。** predictive greedy（在 $\tilde f$ 上跑 single-step greedy，恰好执行 $K$ 步，
worst-case 语句里 ties 由 adversary 打破，assumptions.md）在 error level $\eta$ 上的精确
worst-case ratio。它对所有 $n$ 取 inf，因此与 $n$ 无关。由 notation.md，
$\rho_K(\eta)=\min_{0\le j\le K-1}V_j(\eta)$，其中
$k_1=(K-1)\eta+1$，$q=(K-1)\eta/k_1$，$V_j(\eta)=1-q^{j}\bigl(1-\tfrac{K-j}{K\eta}\bigr)$。

**待证的链。** 对所有 $K\ge3$、所有 $\eta>1$：
$$\rho_K(\eta)\;\le\;\alpha_{\mathrm{lin}}(K,\eta)\;\le\;\min\Bigl\{\tfrac1\eta,\;W_K(\eta)\Bigr\}
\;\le\;\min\Bigl\{\tfrac1\eta,\;\rho_K(\eta)+\tfrac{1}{K(e^{K-1}-K-1)}\Bigr\},$$
其中 $W_K(\eta)$ 是下面第 3 节构造出来的显式常数；并且当 $\eta\ge K$ 时两端都等于 $1/\eta$。

**空洞性检验（CLAUDE.md 第 11 节要求）。** 逐个限定词：
(i) `deterministic` 不可删，但删掉后结论不变（第 2.6 步：随机算法按期望度量时同一上界成立），
所以它只是把 $\alpha_{\mathrm{lin}}$ 的定义写窄，不影响真值；
(ii) `arbitrary size` 不可删：这正是与 single-element 版本的区别，删掉后上界还成立但定理失去内容，
换成对立面（限制 $|S|\le K$）则第 3 节的 $t^\ast$-truncation 变成不必要；
(iii) `$O(nK)$` 不可删：第 4.4 步给出 $Q=o(n^2)$ 才够，$Q=\binom nK$ 时结论假；
(iv) `$n\to\infty$` 不可删，见第 4.5 步；
(v) `at most $K$` 不可删：输出更大集合时 $F(x,0)$ 可以超过 $W_K$；
(vi) `$K\ge3$` 用在 $e^{K-1}>K+1$ 和第 3.9 步的 $K=3$ 边界算例；
(vii) `$\eta>1$` 用在 $\nu=\eta/(\eta-1)$ 有限，且用在 $m>\eta(K-1)$ 的严格性。

---

## 2. 推导（编号步骤）

### 2.0 记号

$k_1=(K-1)\eta+1$，$q=(K-1)\eta/k_1\in(0,1)$，$\nu=\eta/(\eta-1)>1$，
$\psi(\eta)=\eta\ln\nu$，$h(\eta)=\nu^{\eta}=e^{\psi(\eta)}$。

---

### 2.1 步骤 L1（下界，$\rho_K\le\alpha_{\mathrm{lin}}$）

predictive greedy 属于 $\mathcal A_n$：第 $t$ 步（$t=0,\dots,K-1$）对每个 $e\notin S^t$ 查
$\tilde f(S^t\cup\{e\})$，再查一次 $\tilde f(S^t)$，共 $\le K(n+1)\le 2nK$ 次 query（$n\ge1$），
每次 query 的集合大小 $\le K$，所以也是合法的 arbitrary-size 算法；它 deterministic（tie-breaking
规则固定，worst case 下由 adversary 选最差的那条规则），恰好输出 $K$ 个元素，满足 $|T|\le K$。
用的是：assumptions.md 中 predictive greedy 的定义 + $\mathcal A_n$ 的定义。
**状态 [HAND-PROOF-UNREVIEWED]。**

由 $\rho_K(\eta)$ 的定义（assumptions.md：“Its exact worst-case ratio at error level $\eta$”），
对每个 $n\ge K$ 和每个 $I\in\mathcal I_n(K,\eta)$ 都有
$f(S^{\mathrm{greedy}})\ge\rho_K(\eta)F^{\mathrm{OPT}}$，故 $\alpha_n\ge\rho_K(\eta)$。

### 2.2 步骤 L2（极限存在）

$\alpha_n$ 关于 $n$ 非增：给定 $n$ 上的实例 $I$，加入一个 null element $e^\ast$（对所有 $S$ 有
$d_{e^\ast}(S)=0$，从而 Definition 1 强制 $\tilde d_{e^\ast}(S)=0$，band 自动成立，$f$ 仍
monotone submodular），得到 $n+1$ 上的实例，其 $F^{\mathrm{OPT}}$ 不变；任何 $n+1$ 上的算法
限制到这类实例上给出 $n$ 上的算法且 query 预算不增。故 $\alpha_{n+1}\le\alpha_n$。
配合 $\rho_K(\eta)\le\alpha_n\le1$（步骤 L1），单调有界数列收敛，
$\alpha_{\mathrm{lin}}=\lim_n\alpha_n$ 存在且 $\ge\rho_K(\eta)$。
用的是：步骤 L1 + Definition 1 的 zero-pattern 条款。**状态 [HAND-PROOF-UNREVIEWED]。**

### 2.3 步骤 U1（上界 $1/\eta$，modular hard family）

取 $N$ 任意，$|N|=n$；$O\subseteq N$ 是均匀随机的 $K$-subset（这是一个 instance distribution，
不是算法的随机性）。定义 modular
$$f(S)=\sum_{e\in S}w_e,\qquad w_e=\begin{cases}1/K,&e\in O,\\ 1/(\eta K),&e\notin O,\end{cases}
\qquad \tilde f(S)=\frac{|S|}{\eta K}.$$
$f$ modular 故 submodular，$w_e>0$ 故 monotone，$f(\emptyset)=0$，$\tilde f(\emptyset)=0$。
边际增益：$d_e(S)=w_e$，$\tilde d_e(S)=1/(\eta K)$。取 $\eta_u=\eta,\eta_o=1$：
$e\in O$ 时 $d_e/\eta_u=1/(\eta K)=\tilde d_e\le\eta_o d_e$；$e\notin O$ 时三者相等。
error product $=\eta$。没有零增益，zero-pattern 条款平凡成立。
$F^{\mathrm{OPT}}=f(O)=1$。
用的是：Definition 1（convention B）+ assumptions.md。**状态 [HAND-PROOF-UNREVIEWED]。**

### 2.4 步骤 U2（$1/\eta$ 的信息论论证）

$\tilde f(S)=|S|/(\eta K)$ 只依赖 $|S|$，与 $O$ 完全无关，因此任意大小的 query 一个 bit 都不泄漏。
deterministic 算法在这一族上的 query 序列和输出 $T$ 是**固定的**（与 $O$ 无关），$|T|\le K$。于是
$$f(T)=\frac{|T\cap O|}{K}+\frac{|T|-|T\cap O|}{\eta K}\le\frac1\eta+\frac{|T\cap O|}{K},
\qquad \mathbb E_O|T\cap O|=\frac{|T|\,K}{n}\le\frac{K^2}{n}.$$
故 $\mathbb E_O[f(T)]\le 1/\eta+K/n$。既然存在一个实例其值不超过期望值，
$\alpha_n\le 1/\eta+K/n$，令 $n\to\infty$ 得 $\alpha_{\mathrm{lin}}\le1/\eta$。
用的是：步骤 U1。**状态 [HAND-PROOF-UNREVIEWED]。**

### 2.5 步骤 U3（$W_K$ 上界的位置）

第 3 节构造第二族，给出 $\alpha_{\mathrm{lin}}\le W_K(\eta)$。与步骤 U2 合并得
$\alpha_{\mathrm{lin}}\le\min\{1/\eta,W_K\}$。

### 2.6 步骤 U4（randomized）

上面两族都是**实例分布**上的论证：对任意 deterministic $A$，
$\mathbb E_{I}[f(A(I))/F^{\mathrm{OPT}}]\le B$。randomized 算法 $A_r$ 是 deterministic 算法上的
分布，于是 $\mathbb E_I\mathbb E_{\text{coins}}[\cdot]=\mathbb E_{\text{coins}}\mathbb E_I[\cdot]\le B$，
故存在实例使 $\mathbb E_{\text{coins}}[\cdot]\le B$。这就是 Yao 方向的直接使用，不需要 minimax 定理。
用的是：步骤 U2、U3 的分布形式。**状态 [HAND-PROOF-UNREVIEWED]。**

---

## 3. 第二族：admissibility、$\Psi$、location bounds、$W_K$ 与 gap 界

本节按 `anysize_template.md` 给的 shape 走，未知量是整数 $m\ge1$ 与实数 $d>0$。

### 3.1 步骤 C1（两类计数函数的 monotone submodular 判据）

$F$ 只依赖 $(x,y)=(|S\cap B|,|S\cap O|)$。对这种 set function，monotone submodular 等价于在
count grid 上：
(a) $\Delta_xF\ge0$，$\Delta_yF\ge0$；
(b) $\Delta_xF(x+1,y)\le\Delta_xF(x,y)$；
(c) $\Delta_yF(x,y+1)\le\Delta_yF(x,y)$；
(d) $\Delta_xF(x,y+1)\le\Delta_xF(x,y)$（cross / DR 条件）。
这是把 diminishing returns $d_e(S)\ge d_e(S')$（$S\subseteq S'$）沿两个方向逐格展开的标准
等价形式。**状态 [HAND-PROOF-UNREVIEWED]**，并在 `check_family.py` 中对每个格点直接验
(a)–(d)（不依赖该等价性，直接对 $F$ 本身验），**[VERIFIED-EXHAUSTIVE]**。

代入模板：
$$\Delta_xF(x,0)=r_x-r_{x+1},\quad \Delta_xF(x,y)=c_y(a_x-a_{x+1})\ (y\ge1),$$
$$\Delta_yF(x,0)=g_x,\quad \Delta_yF(x,y)=\tfrac{a_x}{K-1}\ (y\ge1).$$
于是 (a)–(d) 化为三条序列条件：
* **(M1)** $r$ 非增、convex、$r_x\ge0$（并 $r_0=1$ 给出 $0\le F\le1$）；
* **(M2)** $a$ 非增、convex、$a_x\ge0$；
* **(M3)** $g$ 非增，且 $g_x\ge\frac{a_x}{K-1}$，后者等价于 $K g_x\ge r_x$。

（(d) 在 $y=0\to1$ 上恰好等价于 $g$ 非增；在 $y\ge1$ 上由 $c_y$ 递减 + $a$ 非增自动成立。）

### 3.2 步骤 C2（band 自动成立）

在 count grid 的每条边上（$H=\eta_u\tilde f$，band 写成 $\Delta F\le\Delta H\le\eta\Delta F$）：

| 边 | $\Delta F$ | $\Delta H$ | 结论 |
| --- | --- | --- | --- |
| $x\to x+1$，$y=0$ | $\Delta r$ | $\Delta r+(\eta-1)\Delta a$ | $\ge\Delta F\iff\Delta a\ge0$；$\le\eta\Delta F\iff\Delta g\ge0$ |
| $(x,0)\to(x,1)$ | $g_x$ | $g_x$ | 比值 $1$，只需 $g_x\ge0$ |
| $x\to x+1$，$y\ge1$ | $c_y\Delta a$ | $\eta c_y\Delta a$ | 比值恰为 $\eta$ |
| $y\to y+1$，$y\ge1$ | $a_x/(K-1)$ | $\eta a_x/(K-1)$ | 比值恰为 $\eta$ |

其中 $\Delta r=\Delta a+\Delta g$。所以 band **完全由 (M1)(M2)(M3) 推出**，不产生新约束；
包括 closing step $x=t^\ast\to t^\ast+1$（那里 $\Delta a=0$，$\Delta H=\Delta F=r_{t^\ast}$）。
Definition 1 的 zero-pattern（$\Delta H=0\iff\Delta F=0$）也随之成立：第一行由
$0\le\Delta a\le\Delta r$ 给出，其余三行成比例。
用的是：步骤 C1 + definition1.md。**状态 [VERIFIED-SYMBOLIC]**（`check_symbolic.py`）
+ **[VERIFIED-EXHAUSTIVE]**（`check_family.py`，逐边有理数验证）。

### 3.3 步骤 C3（global size-profile property，以及它逼出 $a_{t^\ast}=0$）

**命题。** 对每个 $x\ge0$，$H(x+1,0)=H(x,1)$，即只要 $|S\cap O|\le1$，$\tilde f(S)$ 只依赖 $|S|$；
**在每个 size 上**都成立，不只是小集合。

把两边展开，$H(x+1,0)=H(x,1)$ 等价于
$$\eta r_{x+1}-(\eta-1)g_{x+1}=\eta r_x-\eta g_x.\tag{3.1}$$
逐段验证（`check_symbolic.py` 项 S1，全部化简为 $0$）：
* $x+1\le j$（geometric 段）：左边 $=q^{x+1}\bigl(\eta-\frac{\eta-1}{K}\bigr)=q^{x+1}\frac{k_1}{K}
  =q^{x}\frac{qk_1}{K}=q^x\frac{(K-1)\eta}{K}$，右边同；
* $x=j$（junction）：用 $(\eta-1)\nu=\eta$，两边都化为 $\eta Q(1-\tfrac1K)$；
* $j<x$、$x+1\le t^\ast$（plateau 段）：用 $(\eta-1)\nu^{u+1}=\eta\nu^{u}$，差为 $0$；
* $x>t^\ast$：两边都是 $0$。
* **closing step $x=t^\ast$**：左边 $=0$（$r_{t^\ast+1}=g_{t^\ast+1}=0$），右边 $=\eta a_{t^\ast}$。
  于是 (3.1) 在这里成立**当且仅当**
  $$\boxed{a_{t^\ast}=0}\tag{3.2}$$

这就是 truncation 处唯一的新约束，并且它是**必须**的：若 $a_{t^\ast}>0$，则
$H(t^\ast+1,0)\ne H(t^\ast,1)$，一个大小为 $t^\ast+1$ 的 query 就能区分 $|S\cap O|=0$ 与 $=1$，
从而以 $\Theta(K/n)$ 的概率（而不是 $\Theta(K^2/n^2)$）泄漏，$O(nK)$ 次 query 的 union bound 失效。
用的是：模板定义 + definition1.md。**状态 [VERIFIED-SYMBOLIC]。**

### 3.4 步骤 C4（design equation，解出 $d=d(m)$）

把 (3.2) 写开，$D=Qd$，$u=x-j$，$a_{j+u}=Q\bigl[1-ud-\eta d+(\eta d-\tfrac1K)\nu^{u}\bigr]$，
令 $u=m$ 得
$$1-md-\eta d+\Bigl(\eta d-\frac1K\Bigr)\nu^{m}=0
\;\Longleftrightarrow\;
d=d(m)=\frac{\nu^{m}-K}{K\bigl(\eta\nu^{m}-m-\eta\bigr)}.\tag{3.3}$$
记 $\Theta(t)=\eta\nu^{t}-t-\eta$。

**$\Theta(t)>0$ for $t>0$：** $\Theta(0)=0$，$\Theta'(t)=\eta\nu^{t}\ln\nu-1=\psi(\eta)\nu^{t}-1$，
而 $\psi(\eta)=\eta\ln\frac{\eta}{\eta-1}=-\eta\ln(1-\tfrac1\eta)>\eta\cdot\tfrac1\eta=1$
（用 $-\ln(1-z)>z$，$z\in(0,1)$），故 $\Theta'>0$。

**一个恒等式（后面反复用）：**
$$d(m)-\frac1{K\eta}=\frac{m-\eta(K-1)}{K\eta\,\Theta(m)}.\tag{3.4}$$
所以 $d(m)\ge\frac1{K\eta}\iff m\ge\eta(K-1)$。
用的是：步骤 C3。**状态 [VERIFIED-SYMBOLIC]**（S2、S3）。

### 3.5 步骤 C5（admissibility 归约到三条）

逐条把 (M1)(M2)(M3) 翻译成 $(m,d)$ 上的不等式。

1. **$r$ 在 $x=j$ 的 convexity**（仅当 $j\ge1$）：$-D\ge-\,q^{j-1}(1-q)$，即
   $d\le\frac{1-q}{q}=\frac1{(K-1)\eta}$（用 $1-q=1/k_1$，$qk_1=(K-1)\eta$）。
2. **$r_{t^\ast}\ge0$**：$md\le1$。
3. **$r$ 在 closing step 的 convexity**：$r_{t^\ast}\le D$，即 $(m+1)d\ge1$。
4. **$a$ 在 $x=j$ 的 convexity**（仅当 $j\ge1$）：
   $a_{j+1}-a_j=Q\frac{d-1/K}{\eta-1}$，$a_j-a_{j-1}=-\frac{Q}{K\eta}$，
   条件 $a_{j+1}-a_j\ge a_j-a_{j-1}$ 等价于 $d\ge\frac1{K\eta}$。
5. **$a$ 在 plateau 上 convex**：二阶差分 $=A\nu^{u}(\nu-1)^2$，$A=Q(\eta d-\tfrac1K)$，
   等价于 $d\ge\frac1{K\eta}$（与 4 同）。
6. **$g$ 在 $x=j$ 非增**：$g_{j+1}\le g_j=Q/K$ 等价于 $\eta D\ge Q/K$，即 $d\ge\frac1{K\eta}$（与 4 同）。
   plateau 上 $g_{j+u}=\eta D-A\nu^{u}$ 在 $A\ge0$ 时递减；closing 处 $g_{t^\ast}=r_{t^\ast}\ge0$。
7. **$a$ 非增**：由 convexity，只需最后一个 increment $\le0$。
   $a_{j+u+1}-a_{j+u}=Q\bigl[-d+\frac{(\eta d-1/K)\nu^{u}}{\eta-1}\bigr]$，取 $u=m-1$ 并代入 (3.3)
   的 $(\eta d-\tfrac1K)\nu^m=md+\eta d-1$，条件化为 $md\le1$（与 2 同）。
8. **$Kg_x\ge r_x$**：$x\le j$ 时取等号。plateau 上，令
   $\chi(u)=ud-(K\eta d-1)(\nu^{u}-1)$，则 $Kg-r=Q\chi(u)$。$\chi$ 关于 $u$ concave（因
   $K\eta d-1\ge0$），$\chi(0)=0$，故 $\chi\ge0$ on $[0,m]$ 等价于 $\chi(m)\ge0$。代入 (3.3) 后
   $$\chi(m)\ge0\iff \nu^{m}(K\eta-m)\ge K\eta\iff md\le1 .$$
   （最后一步与 2 是**同一个**不等式；`check_symbolic.py` 项 S5 把两者的分子都化为
   $\nu^m(K\eta-m)-K\eta$。）
9. **$a_x\ge0$、$0\le F\le1$、$F(0,K)=1$**：$a$ 非增（第 7 条）+ $a_{t^\ast}=0$ 给出 $a\ge0$；
   $r_0=1$、$a_0=\frac{K-1}{K}<1$、$c_y\le1$ 给出 $0\le F\le1$；$c_K=0$ 给出 $F(x,K)=1$，
   特别 $F(0,K)=1$，即 $F^{\mathrm{OPT}}=1$。

**归约结论。** 全部 admissibility 等价于
$$\textbf{(A)}\ m\ge\eta(K-1),\qquad \textbf{(B)}\ md(m)\le1,\qquad \textbf{(C)}\ (m+1)d(m)\ge1 .$$
第 1 条被 (A)+(B) 蕴含：$d\le1/m$ 且 $m\ge\eta(K-1)$ 给出 $d\le\frac1{\eta(K-1)}$。
用的是：步骤 C1、C2、C4。**状态 [VERIFIED-SYMBOLIC]**（S4、S5、S6）
+ **[VERIFIED-EXHAUSTIVE]**（`run_grid.py`，62208+350 格全过）。

### 3.6 步骤 C6（$\Psi$ 判据）

**定义**
$$\Psi(t)\;=\;1-(t+1)\,d(t),\qquad t\in\mathbb Z_{\ge1},$$
并取 $m$ 为 **$\Psi$ 的第一个非正整数点**，即 $m=\min\{t\ge1:\Psi(t)\le0\}$。

**(i) $m$ 存在且有限。** $d(t)\to\frac1{K\eta}>0$（(3.4)，分子线性、分母指数），故
$(t+1)d(t)\to\infty$。

**(ii) $m$ 满足 (C)。** 由定义。

**(iii) $m$ 满足 (A)，而且是严格的 $m>\eta(K-1)$。**
若 $t<\eta(K-1)$，由 (3.4) 有 $d(t)<\frac1{K\eta}$，于是
$(t+1)d(t)<\frac{t+1}{K\eta}<\frac{\eta(K-1)+1}{K\eta}=\frac{k_1}{K\eta}\le1$（因 $\eta\ge1$），
即 $\Psi(t)>0$。若 $t=\eta(K-1)$ 恰为整数，则 $d(t)=\frac1{K\eta}$ 且
$\Psi(t)=1-\frac{k_1}{K\eta}>0$（因 $\eta>1$ 给出 $k_1<K\eta$）。两种情形都不是非正点，
所以 $m>\eta(K-1)$。特别地 $m>K-1$，故 $m\ge K$，$t^\ast=j+m\ge K$。

**(iv) $m$ 满足 (B)。** 这是本推导里唯一需要技巧的一步。记
$\zeta(t)=\frac{t-\eta(K-1)}{\Theta(t)}$，则 $d(t)=\frac1{K\eta}(1+\zeta(t))$。令 $s=m-\eta(K-1)>0$。
因 $\Theta(m),\Theta(m-1)>0$，
$$\zeta(m)\le\zeta(m-1)\iff s\,\Theta(m-1)-(s-1)\Theta(m)\le0 .$$
把左端展开并用 $m-s=\eta(K-1)$、$\nu-1=\frac1{\eta-1}$ 化简，恰好得到
$$s\,\Theta(m-1)-(s-1)\Theta(m)\;=\;\nu^{m}(K\eta-m)-K\eta. \tag{3.5}$$
（`check_selection.py` 项 S9，residual $=0$。）
现在反证：设 (B) 不成立，即 $md(m)>1$。由步骤 C5 第 8 条的等价，
$\nu^{m}(K\eta-m)<K\eta$，由 (3.5) 得 $\zeta(m)<\zeta(m-1)$，即 $d(m)<d(m-1)$。
另一方面 $m\ge K\ge3\ge2$，由 $m$ 的极小性 $\Psi(m-1)>0$，即 $m\,d(m-1)<1$。于是
$$m\,d(m)\;<\;m\,d(m-1)\;<\;1,$$
与 $md(m)>1$ 矛盾。故 (B) 成立。
用的是：步骤 C4、C5。**状态 [VERIFIED-SYMBOLIC]**（(3.5) 是 sympy 恒等式）
+ 反证部分 **[HAND-PROOF-UNREVIEWED]**，并在 62208 格上 **[VERIFIED-EXHAUSTIVE]**。

### 3.7 步骤 C7（location bounds）

$$\eta(K-1)\;<\;m\;<\;K\eta .$$
左半由步骤 C6(iii)。右半：由 (B) 与步骤 C5 第 8 条，$\nu^{m}(K\eta-m)\ge K\eta>0$，
而 $\nu^m>0$，故 $K\eta-m>0$。（更粗的写法：$m\le1/d$ 且 $d>\frac1{K\eta}$。）
区间 $(\eta(K-1),K\eta)$ 长度为 $\eta>1$，所以它总含整数，这与步骤 C6(i) 的存在性一致。
**状态 [HAND-PROOF-UNREVIEWED]** + **[VERIFIED-EXHAUSTIVE]**。

### 3.8 步骤 C8（$W_K$ 与 $W_K-\rho_K$ 的闭式）

取模板中的 $j$ 为 $\rho_K=\min_{0\le j\le K-1}V_j$ 的 argmin（若有并列取最小的 $j$）。
由步骤 C7，$j\le K-1<K\le t^\ast$，故 $K$ 落在 plateau 段：
$$r_K=Q-(K-j)D=q^{j}\bigl(1-(K-j)d\bigr),\qquad
\boxed{\,W_K(\eta)=F(K,0)=1-q^{j}\bigl(1-(K-j)d\bigr)\,}$$
与 $V_j=1-q^{j}\bigl(1-\frac{K-j}{K\eta}\bigr)$ 相减：
$$\boxed{\,W_K(\eta)-\rho_K(\eta)=q^{j}\,(K-j)\Bigl(d-\frac1{K\eta}\Bigr)
=\frac{q^{j}(K-j)\bigl(m-\eta(K-1)\bigr)}{K\eta\,\Theta(m)}\;\ge 0\,}\tag{3.6}$$
用的是：notation.md 的 $V_j$ 与 $\rho_K=\min_jV_j$，步骤 C4 的 (3.4)。
**状态 [VERIFIED-SYMBOLIC]**（S8）+ **[VERIFIED-EXHAUSTIVE]**。

### 3.9 步骤 C9（指数小的 gap 界）

**目标：** $W_K-\rho_K<\dfrac{1}{K\bigl(e^{K-1}-K-1\bigr)}$，$K\ge3$，$\eta>1$。

(a) $q<1$ 给出 $q^{j}\le1$；$j\ge0$ 给出 $K-j\le K$；步骤 C7 给出 $m-\eta(K-1)<\eta$。

(b) 步骤 C7 的 $m>\eta(K-1)$ 与 $m<K\eta$ 给出
$$\Theta(m)=\eta\nu^{m}-m-\eta>\eta\,\nu^{\eta(K-1)}-K\eta-\eta=\eta\bigl(h^{K-1}-K-1\bigr),
\qquad h=\nu^{\eta}=e^{\psi(\eta)} .$$

(c) 代入 (3.6)：
$$W_K-\rho_K<\frac{K\cdot\eta}{K\eta\cdot\eta\bigl(h^{K-1}-K-1\bigr)}=\frac{1}{\eta\bigl(h^{K-1}-K-1\bigr)} .$$

(d) 只需 **L3**：$\eta\bigl(h^{K-1}-K-1\bigr)\ge K\bigl(e^{K-1}-K-1\bigr)$。注意
$\psi(\eta)>1$（步骤 C4）给出 $h>e$，又 $e^{K-1}>K+1$ 对 $K\ge3$ 成立（$e^2=7.389>4$，
左端增长更快），故两边括号都是正的。
* **情形 $\eta\ge K$：** $h^{K-1}-K-1\ge e^{K-1}-K-1$ 且 $\eta\ge K$，直接得证。
* **情形 $\eta<K$：** $\eta(h^{K-1}-K-1)=\eta h^{K-1}-\eta(K+1)>\eta h^{K-1}-K(K+1)$，
  因此只需 **L2**：$\eta\,h^{K-1}\ge K\,e^{K-1}$，即
  $$\ln\frac\eta K+(K-1)\bigl(\psi(\eta)-1\bigr)\ \ge\ 0 .$$

(e) **L1（Padé 型下界）：** 对 $z\in(0,1)$，$\phi(z)=-\ln(1-z)-\frac{2z}{2-z}$ 满足 $\phi(0)=0$ 且
$$\phi'(z)=\frac1{1-z}-\frac{4}{(2-z)^2}=\frac{z^2}{(1-z)(2-z)^2}>0 ,$$
故 $\phi>0$。取 $z=1/\eta$ 得 $\ln\frac{\eta}{\eta-1}>\frac{2}{2\eta-1}$，即
$$\psi(\eta)-1>\frac{1}{2\eta-1}\ \Bigl(\ge\frac{1}{2\eta}\Bigr).$$

(f) **L2 的证明：**
* $K\ge4$：$\ln\frac\eta K+\frac{K-1}{2\eta}$ 在 $\eta=\frac{K-1}2$ 取最小值
  $1+\ln\frac{K-1}{2K}\ge1+\ln\frac38=0.01917>0$（$\frac{K-1}{2K}$ 关于 $K$ 递增，$K=4$ 时为 $3/8$）。
* $K=3$：用 (e) 的更强形式，$\ln\frac\eta3+\frac{2}{2\eta-1}$ 在 $4\eta^2-8\eta+1=0$ 的正根
  $\eta=1+\frac{\sqrt3}{2}$ 处取最小值 $\ln\frac{2+\sqrt3}{6}+\sqrt3-1=0.25725>0$。

于是 L3 成立，代回 (c) 得到目标不等式，且不等号是严格的（(a) 中 $m-\eta(K-1)<\eta$ 已严格）。
用的是：步骤 C7、C8。**状态 [HAND-PROOF-UNREVIEWED]**（L1 的 $\phi'$ 化简
**[VERIFIED-SYMBOLIC]**；L2、L3 在 $K=3..60$、$\eta$ 用 golden-section 求最小值上
**[VERIFIED-EXHAUSTIVE]**，L2 的最小值恒 $\approx0.31\sim0.36$，L3 在 $K=3$ 时最小值 $11.86>0$）。

**数量级说明。** 网格上 $(W_K-\rho_K)\big/\frac{1}{K(e^{K-1}-K-1)}$ 的最大值是
$0.2018$（$K=6,\eta=6,m=35,j=0$），即这个界在被检查的范围内有约 $5$ 倍余量，不是紧的。

### 3.10 步骤 C10（global size-profile property 的完整陈述）

综合步骤 C3 与 $a_x=0$（$x\ge t^\ast$）：

* **(P1)** 对每个 $x\ge0$：$H(x+1,0)=H(x,1)$。所以存在单变量函数 $\sigma$ 使得
  $|S\cap O|\le1\Rightarrow \tilde f(S)=\sigma(|S|)/\eta_u$，**在所有 size 上**成立，包括 $|S|$ 与 $n$
  同阶的巨大 query。
* **(P2)** 对 $x\ge t^\ast$ 与任意 $y$：$a_x=0$，故 $H(x,y)=C$（$y\ge1$）；对 $x>t^\ast$ 还有
  $r_x=0$，故 $H(x,0)=C$。即一旦 $|S\cap B|\ge t^\ast$，surrogate 就完全平坦。
* **(P3)** 由 (P1)(P2)，$H(x,y)\ne\sigma(x+y)$ 只可能在 $y\ge2$ 且 $x\le t^\ast-1$ 时发生，
  于是泄漏 query 必满足 $|S|\le t^\ast+K-1$。

**状态 [VERIFIED-SYMBOLIC]**（P1）+ **[VERIFIED-EXHAUSTIVE]**（`check_leakage.py`，
$K=3..7$、$\eta\in(1,5]$ 的有理网格上 P1/P2/P3 全过，且最大泄漏 size 从未超过 $t^\ast+K-1$）。

---

## 4. $O(nK)$ 任意大小 query 的泄漏界

### 4.1 步骤 D1（实例分布）

$N=B\sqcup O$，$O$ 是 $N$ 的均匀随机 $K$-subset，$B=N\setminus O$；$f,\tilde f$ 按模板用
$(x,y)=(|S\cap B|,|S\cap O|)$ 定义，$(m,d)$ 按第 3 节选。由步骤 C5、C2，这是
$\mathcal I_n(K,\eta)$ 的合法成员，且 $F^{\mathrm{OPT}}=F(0,K)=1$。

### 4.2 步骤 D2（reference oracle 与“泄漏”的定义）

令 reference surrogate $\tilde f_0(S)=\sigma(|S|)/\eta_u$（步骤 C10(P1) 中的 $\sigma$）。称 query $S$
**泄漏**，若 $\tilde f(S)\ne\tilde f_0(S)$。由步骤 C10(P3)，$S$ 泄漏蕴含
$$|S\cap O|\ge2\quad\text{且}\quad |S\cap B|\le t^\ast-1 ,$$
于是 $|S|\le t^\ast+K-1$。记 $L=t^\ast+K-1$。由步骤 C7，
$$t^\ast=j+m<(K-1)+K\eta,\qquad L<K(\eta+2).$$
这是一个**与 $n$ 无关的常数**（$K,\eta$ 固定）。

### 4.3 步骤 D3（固定路径 + union bound）

固定 deterministic $A\in\mathcal A_n$。把 $A$ 跑在 $\tilde f_0$ 上：因为 $\tilde f_0$ 与 $O$ 无关，
$A$ 产生一列**固定的** query $S_1,\dots,S_Q$（$Q\le cnK$）与一个**固定的**输出 $T$，$|T|\le K$。
设事件
$$\mathcal E=\{\exists i\le Q:\ S_i\ \text{泄漏}\}\cup\{T\cap O\ne\emptyset\}.$$
在 $\mathcal E^c$ 上，$A$ 在真实实例上得到与在 $\tilde f_0$ 上逐步相同的返回值（归纳：前 $i-1$ 步相同
则第 $i$ 个 query 是同一个 $S_i$，而 $S_i$ 不泄漏），故输出同一个 $T$，且 $T\subseteq B$，于是
$$f(T)=F(|T|,0)=1-r_{|T|}\le1-r_K=W_K$$
（用 $r$ 非增与 $|T|\le K$，步骤 C5）。

**概率。** 对固定的 $S$，$|S|=s$：
$$\Pr[\,|S\cap O|\ge2\,]\le\binom K2\frac{s(s-1)}{n(n-1)} .$$
（对 $O$ 中每一对元素用一次，两者同时落进 $S$ 的概率是 $\frac{s}{n}\cdot\frac{s-1}{n-1}$，再 union。）
只有 $s\le L$ 的 query 可能泄漏，故
$$\Pr[\mathcal E]\ \le\ Q\binom K2\frac{L(L-1)}{n(n-1)}+\frac{|T|\,K}{n}
\ \le\ \frac{c\,nK\cdot K^2L^2}{2\,n(n-1)}+\frac{K^2}{n}
\ =\ O\!\Bigl(\frac{K^3L^2}{n}\Bigr)=O\!\Bigl(\frac{K^5(\eta+2)^2}{n}\Bigr)\xrightarrow[n\to\infty]{}0 .$$

**期望值。** $f\le1$，故
$$\mathbb E_O[f(T_A)]\le W_K+\Pr[\mathcal E]\;=\;W_K+O(1/n).$$
于是 $\alpha_n\le W_K+O(1/n)$，令 $n\to\infty$ 得 $\alpha_{\mathrm{lin}}\le W_K$。
用的是：步骤 C10、C5、D2。**状态 [HAND-PROOF-UNREVIEWED]**（概率部分是标准计数；
结构部分 P1/P2/P3 已 **[VERIFIED-EXHAUSTIVE]**）。

### 4.4 步骤 D4（哪些 query 能泄漏，为什么 $O(nK)$ 这个预算重要）

* **不能泄漏的：** 任何 $|S\cap O|\le1$ 的 query，不论多大（(P1)）；任何 $|S\cap B|\ge t^\ast$ 的
  query，不论 $|S\cap O|$ 多大（(P2)）。特别地，$|S|>t^\ast+K-1$ 的 query 一定属于后者，
  所以“任意大小”这个额外能力**只在常数多个 size 上**有用。这正是 truncation 参数
  $t^\ast$ 的作用：它把 surrogate 在 $B$ 方向上提前压平。
* **能泄漏的：** 只有 $|S\cap O|\ge2$ 且 $|S\cap B|<t^\ast$ 的 query，概率 $O(K^2L^2/n^2)$。
* **预算敏感性：** union bound 需要 $Q\cdot O(K^2L^2/n^2)=o(1)$，即 $Q=o(n^2)$（$K,\eta$ 固定）。
  $O(nK)$ 满足；但 $Q=\binom nK$ 不满足，此时算法可以枚举所有 $K$-subset，找出使
  $\tilde f$ 偏离 $\sigma$ 的那些，从而定位 $O$ 并输出它，ratio 达到 $1$。所以
  $\alpha_{\mathrm{lin}}\le W_K$ 依赖 query 预算的多项式阶，不只是“多项式”。
  **状态 [HAND-PROOF-UNREVIEWED]**（这是对 quantifier 的必要性说明，不是主定理的一部分）。

### 4.5 步骤 D5（为什么 $n\to\infty$ 不能去掉）

上界形式是 $\alpha_n\le W_K+\Pr[\mathcal E]$，而 $\Pr[\mathcal E]=\Theta(1/n)$ 在固定 $n$ 时是常数，
不是 $0$。三个具体理由：

1. **小 $n$ 时预算足以穷举，上界直接为假。** $\mathcal A_n$ 里的常数 $c$ 允许依赖 $K,\eta$，
   所以在固定的小 $n$ 上它可以大到让算法查遍全部 $2^n$ 个子集。取 $n=K+1$，此时 $|B|=1$，
   算法对每个 $e\in N$ 查一次 $S_e=N\setminus\{e\}$（共 $K+1$ 次 query，$|S_e|=K$）：
   $$e\in O\Rightarrow(x,y)=(1,K-1),\quad H=C-\frac{\eta\,a_1}{K-1};\qquad
     e\in B\Rightarrow(x,y)=(0,K),\quad H=C .$$
   因 $1<t^\ast$ 给出 $a_1>0$，两个值不同，算法因此唯一确定那个 $B$ 元素，从而恢复
   $O=N\setminus B$ 并输出它，ratio $=1$。于是 $\alpha_{K+1}=1>W_K$，
   不等式 $\alpha_n\le W_K$ 在 $n=K+1$ 上为假。
2. **$T\cap O\ne\emptyset$ 项不可去。** 即使不泄漏，随机输出的 $K$ 个元素碰到 $O$ 的概率是
   $\Theta(K^2/n)$，这一项只在极限下消失。
3. **定义本身。** $\alpha_n$ 关于 $n$ 非增（步骤 L2），$\alpha_{\mathrm{lin}}$ 是它的下确界；
   任何有限 $n$ 的 $\alpha_n$ 都可能严格大于 $\alpha_{\mathrm{lin}}$，把 $\lim$ 换成“对所有 $n$”
   会把陈述变成更强、并且（由第 1 点）为假的命题。

**状态 [HAND-PROOF-UNREVIEWED]** + 第 1 点的分离见证 **[VERIFIED-EXHAUSTIVE]**
（`check_misc.py` 项 M1，$K=3..7$ 各算例 $H(1,K-1)\ne H(0,K)$ 全部成立；
$K=3,\eta=3/2$ 时 $H(1,2)=\frac{23}{24}\ne\frac43=H(0,3)$，另有泄漏见证
$H(1,2)=\frac{23}{24}\ne\sigma(3)=H(3,0)=\frac{37}{48}$，见第 5.1 节表）。

### 4.6 步骤 D6（$\eta\ge K$ 时两端相等）

**引理。** 记 $\beta_j=q^{j}\bigl(1-\frac{K-j}{K\eta}\bigr)$，则 $V_j=1-\beta_j$，且
$$\frac{\beta_{j+1}}{\beta_j}\le1\iff K\eta-K+j\ \ge\ qk_1=(K-1)\eta\iff \eta\ge K-j .$$
（推导：$\frac{\beta_{j+1}}{\beta_j}=q\frac{z+1}{z}$，$z=K\eta-K+j$；$q(z+1)\le z\iff q\le z(1-q)=z/k_1$。）

* $j=0$ 时 $\beta_0=1-\frac1\eta$，故 $V_0=\frac1\eta$ **恒成立**，于是 $\rho_K\le\frac1\eta$ 恒成立。
* 若 $\eta\ge K$，则对所有 $0\le j\le K-1$ 有 $\eta\ge K\ge K-j$，故 $\beta$ 关于 $j$ 非增，
  $\beta_j\le\beta_0$，$V_j\ge V_0$，于是 $\rho_K(\eta)=V_0=\frac1\eta$，且 argmin 取 $j=0$。
* 此时 $\min\{\frac1\eta,W_K\}\le\frac1\eta=\rho_K\le\alpha_{\mathrm{lin}}\le\min\{\frac1\eta,W_K\}$，
  故全链坍缩为等式，两端都是 $\frac1\eta$。（顺带：$W_K\ge\rho_K=\frac1\eta$ 由 (3.6) 的非负性。）

用的是：notation.md 的 $V_j$、步骤 C8、L1、U2。
**状态 [HAND-PROOF-UNREVIEWED]** + **[VERIFIED-EXHAUSTIVE]**（`run_grid.py` 对每个
$\eta\ge K$ 的格点验 $\rho_K=1/\eta$，62208 格全过）。

### 4.7 步骤 D7（合并）

L1 + L2 给左端；U2 + D3 给中间；C9 给右端；D6 给 $\eta\ge K$ 的坍缩。定理的三段不等式成立。

---

## 5. 数值走查

### 5.1 $K=3$，$\eta=3/2$（主算例，全部有理数精确）

$k_1=4$，$q=\frac34$，$\nu=3$，$C=\frac43$，$\eta(K-1)=3$，$K\eta=\frac92$。

$V_0=\frac23$，$V_1=\frac7{12}$，$V_2=\frac9{16}$，故 $\rho_3(\tfrac32)=\frac9{16}=0.5625$，$j=2$，$Q=q^2=\frac9{16}$。

$\Psi$ 判据（步骤 C6）：

| $t$ | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- |
| $d(t)$ | $0$ | $\frac15$ | $\frac29$ | $\frac{13}{58}$ |
| $\Psi(t)=1-(t+1)d(t)$ | $1$ | $\frac25$ | $\frac19$ | $-\frac{7}{58}$ |

第一个非正点是 $t=4$，故 $m=4$，$d=\frac{13}{58}$，$D=Qd=\frac{117}{928}$，$t^\ast=j+m=6$。

admissibility：(A) $4>3$ ✓；(B) $md=\frac{26}{29}\le1$ ✓（等价形式
$\nu^m(K\eta-m)=81\cdot\frac12=\frac{81}2\ge\frac92=K\eta$ ✓）；(C) $(m+1)d=\frac{65}{58}\ge1$ ✓。
location bounds：$3<4<4.5$ ✓。

序列与 $F,H$（$c_1=1,c_2=\frac12,c_3=0$）：

| $x$ | $r_x$ | $g_x$ | $a_x$ | $F(x,0)$ | $F(x,1)$ | $F(x,2)$ | $F(x,3)$ | $H(x,0)$ | $H(x,1)$ | $H(x,2)$ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | $1$ | $\frac13$ | $\frac23$ | $0$ | $\frac13$ | $\frac23$ | $1$ | $0$ | $\frac13$ | $\frac56$ |
| 1 | $\frac34$ | $\frac14$ | $\frac12$ | $\frac14$ | $\frac12$ | $\frac34$ | $1$ | $\frac13$ | $\frac7{12}$ | $\frac{23}{24}$ |
| 2 | $\frac9{16}$ | $\frac3{16}$ | $\frac38$ | $\frac7{16}$ | $\frac58$ | $\frac{13}{16}$ | $1$ | $\frac7{12}$ | $\frac{37}{48}$ | $\frac{101}{96}$ |
| 3 | $\frac{405}{928}$ | $\frac{171}{928}$ | $\frac{117}{464}$ | $\frac{523}{928}$ | $\frac{347}{464}$ | $\frac{811}{928}$ | $1$ | $\frac{37}{48}$ | $\frac{2659}{2784}$ | $\frac{6371}{5568}$ |
| 4 | $\frac9{29}$ | $\frac{81}{464}$ | $\frac{63}{464}$ | $\frac{20}{29}$ | $\frac{401}{464}$ | $\frac{865}{928}$ | $1$ | $\frac{2659}{2784}$ | $\frac{3145}{2784}$ | $\frac{6857}{5568}$ |
| 5 | $\frac{171}{928}$ | $\frac{135}{928}$ | $\frac9{232}$ | $\frac{757}{928}$ | $\frac{223}{232}$ | $\frac{455}{464}$ | $1$ | $\frac{3145}{2784}$ | $\frac{1775}{1392}$ | $\frac{3631}{2784}$ |
| 6 $(=t^\ast)$ | $\frac{27}{464}$ | $\frac{27}{464}$ | $0$ | $\frac{437}{464}$ | $1$ | $1$ | $1$ | $\frac{1775}{1392}$ | $\frac43$ | $\frac43$ |
| 7 | $0$ | $0$ | $0$ | $1$ | $1$ | $1$ | $1$ | $\frac43$ | $\frac43$ | $\frac43$ |

读表可见：$a_6=0$（design equation (3.2)）；$H(x+1,0)=H(x,1)$ 逐行成立
（$\frac13,\frac7{12},\frac{37}{48},\frac{2659}{2784},\dots$）；$x\ge7$ 后 $H\equiv C=\frac43$（(P2)）；
$H(1,2)=\frac{23}{24}\ne\sigma(3)=H(3,0)=\frac{37}{48}$，这是一个**泄漏** query 的显式见证。

结果：
$$W_3(\tfrac32)=F(3,0)=\frac{523}{928}=0.5635776\ldots,\qquad
W_3-\rho_3=\frac{523}{928}-\frac9{16}=\frac1{928}=0.00107759\ldots$$
校验 (3.6)：$q^{j}(K-j)\bigl(d-\frac1{K\eta}\bigr)=\frac9{16}\cdot1\cdot\bigl(\frac{13}{58}-\frac29\bigr)=\frac1{928}$ ✓。
指数界：$\frac{1}{K(e^{K-1}-K-1)}=\frac{1}{3(e^{2}-4)}=0.098356\ldots$，而 $\frac1{928}=0.001078$，
余量约 $91$ 倍 ✓。
最终 $\min\{\frac1\eta,W_3\}=\min\{\frac23,\frac{523}{928}\}=\frac{523}{928}$，于是
$$\frac9{16}\le\alpha_{\mathrm{lin}}(3,\tfrac32)\le\frac{523}{928}\le\frac9{16}+\frac1{3(e^2-4)} .$$
区间宽度 $\frac1{928}\approx1.08\times10^{-3}$。

### 5.2 $K=2$ 的 probe 算例（“ProbeLottery item”）

`ProbeLottery` 这个名字在我被允许读的五个文件里没有出现（见第 7 节的 gap 记录）。我按最接近的
读法执行：把它当作第 4 节“哪些 query 能泄漏 / 抽中隐藏对的概率”这一项，并在 $K=2$ 上给出数字。

$K=2$ 时 $O=\{o_1,o_2\}$ 只有一对，$\binom K2=1$，泄漏事件就是 $O\subseteq S$：
$$\Pr[\,O\subseteq S\,]=\frac{s(s-1)}{n(n-1)},\qquad s=|S| .$$
这就是“抽奖”的中奖概率：一次 probe 相当于买 $\binom s2$ 张彩票，奖池有 $\binom n2$ 张。
取 $s=6$（一个与 $n$ 无关的常数 size，量级同第 4.2 节的 $L$）：

| $n$ | $\Pr[O\subseteq S]$ | 数值 |
| --- | --- | --- |
| $10^3$ | $1/33300$ | $3.003\times10^{-5}$ |
| $10^4$ | $1/3333000$ | $3.000\times10^{-7}$ |
| $10^6$ | $1/33333300000$ | $3.000\times10^{-11}$ |

$Q=c\,nK=2cn$ 次 probe 的 union bound 是 $2cn\cdot\frac{s(s-1)}{n(n-1)}=\Theta(1/n)\to0$。
对照 $K=3$、$L=10$、$c=4$：$n=10^3$ 时 union bound $\approx3.24$（无信息），
$n=10^6$ 时 $\approx3.24\times10^{-3}$（有信息）。这两个数字量化了第 4.5 节“$n\to\infty$ 不能去掉”。

注意 $K=2$ 不在定理的 $K\ge3$ 范围内，这里只用它演示 probe 的概率计算，不用它下任何关于
$W_K$ 或 gap 界的结论。

### 5.3 网格穷举结果

`run_grid.py`：

* PASS 1（便宜检查：(A)(B)(C)、location bounds、(3.6)、指数界、$\eta\ge K$ 时 $\rho_K=1/\eta$、
  key lemma 在 $\eta(K-1)$ 为整数时的有理验证）：$K=3..14$，
  $\eta\in\{a/b: b\in\{1,2,3,4,5,6,8,10,12,16,20,50,200\},\,1<a/b\le25\}$，
  共 **62208 格，0 失败**。
* PASS 2（加上整张 count grid 的 monotone submodular、逐边 band、zero-pattern、(P1)(P2)）：
  $K=3..7$，$\eta\in\{a/b: b\in\{1,2,3,4,5,8\},\,1<a/b\le6\}$，共 **350 格，0 失败**。
* $(W_K-\rho_K)\big/\frac{1}{K(e^{K-1}-K-1)}$ 的最大值 $=0.2018$（$K=6,\eta=6$）。

`check_leakage.py`：$K=3..7$、$\eta\in(1,5]$ 有理网格上 P1/P2/P3 **0 失败**。

---

## 6. 没有闭合的步骤 / 额外加的假设

1. **[GAP] `ProbeLottery` 未定义。** 该词不在我被允许读的五个文件中。我按“probe 抽中隐藏对的
   概率”这一读法在 $K=2$ 上给了数字（第 5.2 节）。若它在真正的附录里指某个具体算法，则第 5.2 节
   与它无关，需要重做。**状态 [FAILED]**（就“按原意复现 ProbeLottery”这一子项而言）。
2. **[ADDED ASSUMPTION] $j$ 取 $\rho_K=\min_jV_j$ 的 argmin。** 模板只说 $j$ 是
   “the active segment index of $\rho_K=\min_jV_j$”。并列时我取最小的 $j$。若真正的附录取
   另一个约定，(3.6) 中的 $q^{j}(K-j)$ 会变，但界 (c) 只用了 $q^j\le1,K-j\le K$，结论不变。
3. **[ADDED ASSUMPTION] $\rho_K(\eta)=\min_{0\le j\le K-1}V_j(\eta)$ 被当作已知。**
   notation.md 把它写成 Theorem~\ref{thm:exact} 的内容，我没有独立证明它；步骤 L1/C8/D6 依赖它。
   若该式本身有误，$W_K-\rho_K$ 的闭式随之失效（$W_K$ 的构造与上界论证不受影响）。
   **状态 [HAND-PROOF-UNREVIEWED，依赖外部]。**
4. **[GAP] 两类计数函数的 monotone submodular 判据（步骤 C1 的等价性）** 我只给了叙述，
   没有写完整证明；不过 `check_family.py` 是直接对 $F$ 本身逐格验 (a)–(d) 的，所以网格结论
   不依赖这条等价性，只有“(M1)(M2)(M3) 是充要条件”这句话依赖它。
5. **[GAP] L2/L3 的解析证明只在 $K\ge4$ 走 $\frac{K-1}{2\eta}$、$K=3$ 走 $\frac{2}{2\eta-1}$ 两条路。**
   两条路都已算到底（第 3.9(f) 节），但我没有写出 $\phi$ 在端点的极限论证的完整 $\epsilon$-细节；
   数值上 $K=3..60$ 全过，最小值 $\approx0.31$，余量充足。**状态 [HAND-PROOF-UNREVIEWED]。**
6. **[GAP] $\alpha_n$ 的 sup 是否可达、$\mathcal A_n$ 中 $O(nK)$ 的常数 $c$ 与 $K,\eta$ 的依赖**
   没有细究。步骤 D3 的 union bound 对任意固定 $c$ 都是 $O(c/n)$，所以 $c$ 允许依赖 $K,\eta$
   但不允许依赖 $n$。若 $c$ 允许随 $n$ 增长到 $\Theta(n)$（即 $Q=\Theta(n^2K)$），我的论证失效。
7. **[GAP] $W_K$ 与真实 $\alpha_{\mathrm{lin}}$ 的差。** 本推导只给出 $\alpha_{\mathrm{lin}}\le W_K$；
   我没有构造达到 $W_K$ 的算法，所以 $W_K$ 是否紧未知。定理也只声称 $\le$。
8. **[GAP] 上界链中 $\min\{1/\eta,W_K\}$ 的两族没有合成为一族。** 我用了两个独立的 hard family
   （第 2.3 节的 modular 族与第 3 节的族），分别给 $1/\eta$ 和 $W_K$，再取 $\min$。这是合法的
   （上界取 min），但若附录用单一族同时给出两者，构造会不同。
9. **未做的检查：** 我没有验证 $W_K$ 关于 $\eta$ 的单调性、$K\to\infty$ 的渐近，也没有验证
   $W_K\le1/\eta$ 是否在某些 $(K,\eta)$ 上成立（网格上 $K=3,\eta=3/2$ 时 $W_3<1/\eta$，
   $\eta\ge K$ 时 $W_K\ge1/\eta$，两种情况都出现过，所以 $\min$ 两个分支都是活的）。

---

## 7. 读过的文件

只读了这五个（没有 grep、没有 list、没有打开仓库中任何其他文件，没有联网，没有跑 git）：

1. `/home/user/sub-modular-optimization/results/V11/inputs/definition1.md`
2. `/home/user/sub-modular-optimization/results/V11/inputs/assumptions.md`
3. `/home/user/sub-modular-optimization/results/V11/inputs/notation.md`
4. `/home/user/sub-modular-optimization/results/V11/inputs/statement_linear_anysize.md`
5. `/home/user/sub-modular-optimization/results/V11/inputs/anysize_template.md`

**隔离说明（据实记录）：** 在收尾做文件卫生检查时对 `results/V11/route2/` 执行了一次 `ls`，
该目录里存在其他盲审路线留下的 `.md` 与 `.py` 文件名。我没有打开、没有 grep、没有读取其中
任何一个，本文件的全部内容只来自上面五个 input 文件与我自己的脚本输出。

写入的新文件（全部在 `results/V11/route2/` 下，没有修改仓库任何既有文件）：
`linear_anysize.md`、`check_symbolic.py`、`check_selection.py`、`check_family.py`、
`run_grid.py`、`check_leakage.py`、`check_analytic_bound.py`、`check_misc.py`。

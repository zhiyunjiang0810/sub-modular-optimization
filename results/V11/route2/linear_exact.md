# ROUTE-TWO 盲证：thm:linear-exact（T10c / J6，Theorem 2）

盲证条件：本文件只使用 `results/V11/inputs/` 下的四个输入文件（见第 5 节）与标准数学。没有读取
`paper/`、`THEOREM_LEDGER.md`、`RESEARCH_STATE.md`、`REPORT.md`、任何 `HANDOFF*`、任何 J6/J8 证明稿，
也没有使用 web search 或 git。用户消息里附带的两个 HANDOFF 与 appendix/spotcheck 附件同样没有打开：
路线二的价值在于独立性，读了就失效；这是保守选择，记录在此。

所有脚本在 `results/V11/route2/` 下，可一键复跑：

- `q6_route2_checks.py`：$\rho_K,L_K,U_K$ 的精确有理数表与 sympy 恒等式。
- `q6_route2_lp_scipy.py`：predictive greedy 自身最坏比的 LP。
- `q6_route2_lp_hard.py`：hardness 族的 LP（输出存 `q6_lp_log.txt`，数值存 `q6_lp_values.json`）。

约定：判定用精确算术（`fractions.Fraction` / sympy），float 只出现在 LP 求解与打印。每条数学断言带状态标签。

---

## 1. 陈述复述（逐量词展开）

用我自己的话把 thm:linear-exact 重写为量词完全展开的形式。记 $N$ 为 ground set，$|N|=n$。

**输入量词（全称）**

- (Q1) $K$ 是整数，$K\ge2$。$K=1$ 被排除（$K=1$ 时 greedy 单步即最优结构，$V_j$ 的分段退化）。
- (Q2) $\eta$ 是实数，$\eta>1$。严格不等号：$\eta=1$ 时 $\rho_K(1)=L_K(1)$，构造中"好元素与坏元素同带宽"
  的自由度消失（第 3.4 节反面结果在 $\eta=1$ 退化）。
- (Q3) $n$ 是整数且 $n\ge 4K^5$。是"每一个这样的 $n$"，不是"充分大的 $n$"，所以确定性部分没有
  asymptotics in $n$；也没有 asymptotics in $K$（常数 $4$ 与指数 $5$ 显式）。
- (Q4) 算法类 $\mathcal A_{\mathrm{lin}}$：**deterministic**；对 $\tilde f$ 做**至多 $nK$ 次查询**；
  **每次查询的集合大小 $\le K$**；**输出集合大小 $\le K$**。查询可以 adaptive（第 $i$ 次查询可依赖前
  $i-1$ 次的返回值）。算法**不能**查询 $f$，$\tilde f$ 是唯一可查询对象（assumptions.md）。
- (Q5) 成员性：predictive greedy 用 $Kn-K(K-1)/2=\sum_{t=0}^{K-1}(n-t)$ 次查询，每次查询集合大小
  $t+1\le K$，输出大小 $K$，故 $\in\mathcal A_{\mathrm{lin}}$（$Kn-K(K-1)/2\le nK$）。
- (Q6) 对每个 $A\in\mathcal A_{\mathrm{lin}}$，以及**每一个指定的 split** $\eta_u,\eta_o\ge1$ 且
  $\eta_u\eta_o=\eta$。split 是被 adversary 之外的人指定的，构造必须适配任意 split。

**输出量词（存在）**

- (Q7) 存在实例 $(f,\tilde f)$：$f:2^N\to\mathbb R_{\ge0}$ monotone submodular、$f(\emptyset)=0$；
  $\tilde f:2^N\to\mathbb R$、$\tilde f(\emptyset)=0$；且 $(f,\tilde f)$ 在 Definition~\ref{def:eta}
  意义下的**最小可容许 error factors 恰好是 $(\eta_u,\eta_o)$**（不是"至多"，是"恰好"：两侧都要紧）。
- (Q8) 在该实例上 $A$ 的输出 $T$（$|T|\le K$）满足 $f(T)/f(O^\ast)\le\rho_K(\eta)$，其中 $O^\ast$ 是
  某个最优 $K$-set，$f(O^\ast)=F^{\mathrm{OPT}}$。约定 $f(O^\ast)=0$ 时比值命题平凡成立。
- (Q9) 与 thm:exact（保证侧，对每个 error $\le\eta$ 的实例成立）合并得
  $\sup_{A\in\mathcal A_{\mathrm{lin}}}\inf_{(f,\tilde f)}f(A^{\tilde f})/f(O^\ast)=\rho_K(\eta)$。
- (Q10) 随机化部分：对每个与 (Q4) 同预算的 randomized 算法，存在一个 error 恰为 $\eta$ 的实例，使
  $\mathbb E[f(T)/f(O^\ast)]\le\rho_K(\eta)+\varepsilon_n$，$\varepsilon_n=K^2/n+K^5/(2n)$。期望只对
  **算法自身的随机性**取；实例是固定的（先固定实例，再跑算法）。随机类只给渐近匹配（$n\to\infty$，$K$ 固定），
  不声称有限 $n$ 的精确等式。

**tie breaking 与步数**：assumptions.md 规定所有 worst-case 陈述用 adversarial tie-breaking，
predictive greedy 恒执行 $K$ 步（预测增益为零的步也照选）。这两条只影响 (Q5) 与 (Q9) 的保证侧；
hardness 侧（Q6–Q8）对任意 $A$ 成立，不需要 tie-breaking 约定。

**$\rho_K$ 与 $\eta$ 的定义域**（notation.md）：
$$k_1=(K-1)\eta+1,\qquad q=\frac{(K-1)\eta}{k_1},\qquad
V_j(\eta)=1-q^{\,j}\Bigl(1-\frac{K-j}{K\eta}\Bigr),\qquad
\rho_K(\eta)=\min_{0\le j\le K}V_j(\eta).$$
$j$ 的取值范围 notation.md 未写死，我按 $j\in\{0,1,\dots,K\}$ 读（第 4.1 节给出理由：$j$ 是"落在
$O^\ast$ 内的步数"，取值只能是 $0..K$）。另记
$L_K(x)=1-(1-\frac1{xK})^K$，$U_K(\eta)=1-(1-\frac1{\eta(K-1)+1})^K$。

**[VERIFIED-SYMBOLIC]** $V_0(\eta)=1/\eta$ 与 $V_K(\eta)=U_K(\eta)$ 是恒等式（sympy，
`q6_route2_checks.py`）。**[VERIFIED-EXHAUSTIVE]** 在 $K=2..6$、$\eta\in\{1,6/5,3/2,2,3,5\}$ 的
30 个格点上 $L_K\le\rho_K\le U_K$ 全部成立（精确有理数），且 $\eta=1$ 时三者相等。

---

## 2. 预备：两条结构引理

### 引理 A（count grid 到 set function）[HAND-PROOF-UNREVIEWED]

设 $N=B_1\uplus\cdots\uplus B_m$ 是一个划分，$c(S)=(|S\cap B_1|,\dots,|S\cap B_m|)$，
$\Phi:\prod_i\{0,\dots,|B_i|\}\to\mathbb R_{\ge0}$ 满足 $\Phi(\mathbf 0)=0$ 且

- (A1) 单调：$\Phi(x+e_i)\ge\Phi(x)$；
- (A2) 网格上的 diminishing returns：$x\le y$（逐坐标）$\Rightarrow$
  $\Phi(x+e_i)-\Phi(x)\ \ge\ \Phi(y+e_i)-\Phi(y)$ 对每个 $i$。

则 $f(S)=\Phi(c(S))$ 是 monotone submodular 且 $f(\emptyset)=0$。

*推导*：$S\subseteq T$，$e\notin T$，$e\in B_i$。则 $c(S)\le c(T)$，$c(S\cup e)=c(S)+e_i$，
$c(T\cup e)=c(T)+e_i$。由 (A2)，$d_e(S)=\Phi(c(S)+e_i)-\Phi(c(S))\ge\Phi(c(T)+e_i)-\Phi(c(T))=d_e(T)$，
这正是 submodularity 的 diminishing-returns 刻画；(A1) 给 monotone；$\Phi(\mathbf 0)=0$ 给 $f(\emptyset)=0$。
用到的前提：只有 (A1)(A2) 与划分的存在性，不需要 $\Phi$ 可分离或凹。

注：引理 A 对 $\tilde f$ **不**要求任何东西。Definition 1 只要求 $\tilde f$ 是集合函数、$\tilde f(\emptyset)=0$、
band 成立；$\tilde f$ 不必 monotone、不必 submodular。第 3 节的构造利用了这一点。

### 引理 B（band 的逐点性与两个推论）[HAND-PROOF-UNREVIEWED]

Definition 1 的 band $d_e(S)/\eta_u\le\tilde d_e(S)\le\eta_o d_e(S)$ 等价于
$$\tilde d_e(S)/\eta_o\ \le\ d_e(S)\ \le\ \eta_u\,\tilde d_e(S).$$

- (B1) **同一集合、同一预测值的两个元素**：若 $\tilde d_e(S)=\tilde d_{e'}(S)$，则
  $d_e(S)\le\eta\,d_{e'}(S)$，$\eta=\eta_u\eta_o$。这是 band 唯一能产生的"跨元素"约束。
- (B2) **选择误差**：若 $\tilde d_{e_t}(S^t)\ge\tilde d_o(S^t)$（greedy 或任何"取预测最大"的一步），则
  $d_o(S^t)\le\eta_u\tilde d_o(S^t)\le\eta_u\tilde d_{e_t}(S^t)\le\eta_u\eta_o d_{e_t}(S^t)=\eta g_t$。
  即 Definition (selection error) 的 $a_t\le\eta$，$\etasel\le\eta$。
- (B3) **$\tilde f$ 的一致性耦合**：$\tilde d$ 不是自由的实数族，而必须来自一个集合函数。对任意
  $S$ 与 $e\ne e'$，
  $$\tilde d_e(S)+\tilde d_{e'}(S\cup e)=\tilde f(S\cup\{e,e'\})-\tilde f(S)=\tilde d_{e'}(S)+\tilde d_e(S\cup e'),$$
  于是 band 在四个位置同时生效。**(B3) 是本定理与 $L_K$ 之间差距的来源**（第 4.2 节）。

---

## 3. 硬族：构造思想

### 3.1 目标

要对**任意** $A\in\mathcal A_{\mathrm{lin}}$ 生效，硬族必须让"查询 $\tilde f$"这件事本身没有信息量，
再让 $A$ 的输出落到低值集合上。所以要找一个族 $\{(f_\pi,\tilde f_\pi)\}_{\pi}$，$\pi$ 取遍隐藏结构，使得

- (P1) 只要 $A$ 的查询"看不见"$\pi$，所有 $\tilde f_\pi$ 在这些查询上返回相同的值（canonical transcript）；
- (P2) 能"看见"$\pi$ 的查询很少，可以用 union bound 数掉；
- (P3) 对看不见 $\pi$ 的那些 $\pi$，$f_\pi(T)/f_\pi(O^\ast)\le\rho_K(\eta)$。

### 3.2 硬族在 size $\le K$ 的集合上必须具备的性质

**关键性质**：$\tilde f_\pi$ 必须对"至多含 1 个 $\pi$-元素"的集合完全盲，而在"含 $\ge2$ 个 $\pi$-元素"的
集合上可以任意。记 $O^\ast=\pi$（$|\pi|=K$），称满足
$$\tilde f_\pi(S)=\varphi(|S|)\quad\text{当 }|S\cap\pi|\le1 \tag{$\ast$}$$
的 predictor 为 **1-blind predictor**（$\tau=2$：要"看见"必须一次查询里装进 $\ge2$ 个隐藏元素）。

为什么必须是 $\tau=2$ 而不是更强的对称性（$\tau=1$，即 $\tilde f$ 完全由 $|S|$ 决定）？因为完全对称的
predictor 把硬度卡死在 $1/\eta=V_0$ 上：

**反面结果 R1（count-only predictor 的天花板）[HAND-PROOF-UNREVIEWED + VERIFIED-LP]**
若 $\tilde f(S)=\varphi(|S|)$ 对所有 $S$ 成立，则对任意与 $O^\ast$ 不交的 $K$-set $T=\{b_0,\dots,b_{K-1}\}$
与任意 $O^\ast=\{o_0,\dots,o_{K-1}\}$，
$$f(T)\ \ge\ \frac1\eta f(O^\ast).$$
*推导*：设 $O_{<t}=\{o_0,\dots,o_{t-1}\}$。在集合 $O_{<t}$（大小 $t$）上，$b_t$ 与 $o_t$ 的预测增益都等于
$\varphi(t+1)-\varphi(t)$，由 (B1) 得 $d_{b_t}(O_{<t})\ge d_{o_t}(O_{<t})/\eta$。求和
$\sum_t d_{o_t}(O_{<t})=f(O^\ast)$，故 $\sum_t d_{b_t}(O_{<t})\ge f(O^\ast)/\eta$。（把左端换成
$f(T)=\sum_t d_{b_t}(T_{<t})$ 需要一步比较，这一步我没有闭合成手证，见第 6 节 GAP-1；
LP 直接给出了结论。）
*LP 证据*：`q6_route2_lp_hard.py` 段 [B]，$\eta=3/2$：$K=2,m=6$ count-only 的 all-T 最优值
$=0.666666667=1/\eta$；$K=3,m=6$ 同样 $=1/\eta$；"$K$ 个 block、每块藏一个好元素、predictor
block-symmetric"的变体也是 $1/\eta$。由于 $\rho_3(3/2)=0.5625<2/3$，**完全对称族无法达到 $\rho_K$**。
段 [D]：$\tau=3$ 的 2-blind predictor 同样回到 $2/3$。所以 $\tau=2$ 是唯一可用的盲度。

**正面结果 R2（1-blind 族达到 $\rho_K$）[VERIFIED-LP]**
$\eta=3/2$，1-blind predictor（$\tau=2$）：

| $K$ | $m$ | per-T | all-T | avg-T | all-T（$f$ 也是 count-grid） | $\rho_K$ |
|---|---|---|---|---|---|---|
| 3 | 7 | 0.562500000 | 0.562500000 | 0.562500000 | 0.562500000 | $9/16=0.5625$ |
| 2 | 7 | 0.600000000 | 0.610000000 | 0.610000000 | 0.610000000 | $3/5=0.6$ |

三个 split $(\eta_u,\eta_o)\in\{(1,\frac32),(\frac32,1),(\sqrt{3/2},\sqrt{3/2})\}$ 给出相同的值，
与 (Q6) 的"任意 split"一致（最坏值只依赖 $\eta$）。$K=2$ 的 all-T/avg-T 差 $0.01$，见 GAP-2。

### 3.3 显式构造（$H(K,\eta,n,\eta_u,\eta_o)$）

- ground set $N$，$|N|=n$；隐藏结构 $\pi\subseteq N$，$|\pi|=K$，取遍所有 $\binom nK$ 个 $K$-子集。
- $f_\pi(S)=\Phi(|S\cap\pi|,\ |S\setminus\pi|)$，$\Phi$ 满足引理 A 的 (A1)(A2)（两坐标 count grid）。
- $\tilde f_\pi(S)=\widetilde\Phi(|S\cap\pi|,\ |S\setminus\pi|)$，并要求 **1-blind 条件**
  $\widetilde\Phi(0,s)=\widetilde\Phi(1,s-1)=\varphi(s)$ 对所有 $s$；$a\ge2$ 时 $\widetilde\Phi(a,b)$ 自由。
- band 对指定 split $(\eta_u,\eta_o)$ 在**所有** $S\subseteq N$、$e\notin S$ 上成立（不只是 $|S|\le K$；
  这一条是 Definition 1 的要求，构造时必须把 $b$ 一直取到 $n-K$）。
- $O^\ast=\pi$，$f_\pi(O^\ast)=\Phi(K,0)$ 归一化为 $1$；要求 $\Phi(a,b)\le1$ 对所有 $a+b=K$。
- 目标：$\Phi(0,K)\le\rho_K(\eta)$（$T$ 与 $\pi$ 不交时 $f_\pi(T)=\Phi(0,K)$）。

$\Phi,\widetilde\Phi$ 的存在性在 $K=2,3$、$\eta=3/2$ 由 LP 给出（R2 表的最后一列即"$f$ 也是 count-grid"
的情形）。一般 $(K,\eta)$ 的存在性我没有闭合（GAP-3）。

### 3.4 为什么 1-blind 能突破 $1/\eta$（机制说明）[HAND-PROOF-UNREVIEWED]

R1 的证明用的是"在含 $\le1$ 个好元素的状态上，好元素与坏元素预测增益相同"。1-blind 恰好把这个论证
截断在链的第二步：链 $\emptyset\to\{o_0\}\to\{o_0,o_1\}\to\cdots$ 从第二步起状态已含 $\ge2$ 个好元素
（含 $1$ 个好元素的状态加一个好元素得到的集合含 $2$ 个），$\widetilde\Phi$ 在那里自由，band 不再把
$d_{o_t}$ 压到坏元素增益的 $\eta$ 倍以内。于是 $f(O^\ast)$ 可以比"$K$ 个坏元素"大得多，而算法在只看见
$\varphi(|S|)$ 的情况下无法定位 $\pi$。

---

## 4. 值等于 $\rho_K$ 的理由

### 4.1 $V_j$ 的组合含义 [HAND-PROOF-UNREVIEWED]

对任意一步 $t$（状态 $S^t$，gap$_t=f(O^\ast)-f(S^t)$，$g_t=d_{e_t}(S^t)$），由 submodularity
$f(O^\ast)\le f(S^t)+\sum_{o\in O^\ast\setminus S^t}d_o(S^t)$ 与 (B2)：

- (i) 若 $e_t\in O^\ast$：其中一项是 $d_{e_t}(S^t)=g_t$，其余至多 $K-1$ 项各 $\le\eta g_t$，故
  $\text{gap}_t\le\bigl((K-1)\eta+1\bigr)g_t=k_1g_t$，即 $g_t\ge\text{gap}_t/k_1$，
  gap 收缩因子 $q=(K-1)\eta/k_1$。
- (ii) 若 $e_t\notin O^\ast$：$K$ 项各 $\le\eta g_t$，故 $g_t\ge\text{gap}_t/(K\eta)$。

设一条运行里恰有 $j$ 步属于 (i)，$K-j$ 步属于 (ii)。把 (i) 的 $j$ 步放在前面并取等号，gap 变为
$q^{\,j}$（归一化 $f(O^\ast)=1$）；其后 $K-j$ 步取**平坦**增益 $q^{\,j}/(K\eta)$（即所有 (ii) 步都在
状态 $S^j$ 处的约束上取等号，而不是各自在自己的 gap 上取等号）。总值
$$1-q^{\,j}+(K-j)\frac{q^{\,j}}{K\eta}=1-q^{\,j}\Bigl(1-\frac{K-j}{K\eta}\Bigr)=V_j(\eta).$$
$j$ 只能取 $0..K$，故 $\rho_K=\min_{0\le j\le K}V_j$。$j=0$ 给 $1/\eta$（与 R1 的天花板同值），
$j=K$ 给 $U_K$（显式实例族的值）。**[VERIFIED-SYMBOLIC]** 这两个端点恒等式已用 sympy 确认。

### 4.2 为什么 (ii) 的增益是平坦的而不是逐步收缩的（$L_K$ 不可达）

若 (ii) 的每一步都在自己的 gap 上取等号，总值会是 $L_K(\eta)=1-(1-\frac1{K\eta})^K<\rho_K$。
这条 profile 不可行，原因是引理 B 的 (B3)：$\tilde f$ 必须是集合函数。

**$K=2$ 的精确反例（$\eta=3/2$，与 split 无关）[HAND-PROOF-UNREVIEWED，精确有理算术]**
设 $O^\ast=\{o_1,o_2\}$，$f(O^\ast)=1$，运行取 $e_0,e_1\notin O^\ast$，并按 $L_2$ profile 取等号：
$g_0=\frac1{2\eta}=\frac13$，于是 $d_{o_i}(\emptyset)=\eta g_0=\frac12$（两项之和恰为 $1$，故各项被逼到
$\frac12$）；gap$_1=\frac23$，$g_1=\frac{2/3}{2\eta}=\frac29$，$d_{o_i}(\{e_0\})=\eta g_1=\frac13$。
由此 $f(\{e_0,o_1\})=\frac13+\frac13=\frac23$，$f(\{o_1\})=\frac12$，所以
$$d_{e_0}(\{o_1\})=\tfrac23-\tfrac12=\tfrac16 .$$
另一方面 greedy 在 $\emptyset$ 选 $e_0$ 要求 $\tilde f(e_0)\ge\tilde f(o_1)$，band 给
$\tilde f(e_0)\le\eta_o/3$ 与 $\tilde f(o_1)\ge\frac1{2\eta_u}=\eta_o/3$，故两者都被逼成 $\eta_o/3$；
在 $\{e_0\}$ 选 $e_1$ 同样把 $\tilde d_{o_1}(\{e_0\})$ 逼成 $\frac29\eta_o$，于是
$\tilde f(\{e_0,o_1\})=\frac13\eta_o+\frac29\eta_o=\frac59\eta_o$。用 (B3) 换一个顺序：
$$\tilde d_{e_0}(\{o_1\})=\tilde f(\{e_0,o_1\})-\tilde f(\{o_1\})=\tfrac59\eta_o-\tfrac13\eta_o=\tfrac29\eta_o,$$
band 上界 $\tilde d_{e_0}(\{o_1\})\le\eta_o d_{e_0}(\{o_1\})$ 要求 $d_{e_0}(\{o_1\})\ge\frac29$。
与上面的 $\frac16<\frac29$ 矛盾。$\eta_o$ 在两侧约掉，所以矛盾与 split 无关。
**[VERIFIED-LP]** 同一结论的独立确认：`q6_route2_lp_scipy.py` 在 $m=4,5$、两个 split 下给出
predictive greedy 的精确最坏比 $0.6=\rho_2(3/2)>5/9=L_2(3/2)$；$K=3,m=6$ 给出
$0.5625=\rho_3(3/2)>386/729=L_3(3/2)$。两个 LP 的最优解都把 $O^\ast$ 放在与运行轨迹**不交**的位置，
这正是 hardness 需要的形态。

*保留*：LP 的值是"在 $|N|=m$ 上的精确最坏比"，最坏比对 $m$ 单调不增，我只算到 $m=6,7$。
$m\to n$ 不再下降这一点由 thm:exact 的保证侧给出，而 thm:exact 是**外部输入**（notation.md 只给了它的
公式，我没有重证它）。

### 4.3 与算法类的衔接

R2 的 per-T 列说明：存在 1-blind 实例使得某个与 $\pi$ 不交的 $K$-set 的值恰为 $\rho_K$；all-T 列说明
（$K=3$）**所有**与 $\pi$ 不交的 $K$-set 的值同时 $\le\rho_K$。确定性论证只需要 per-T（adversary 在看到
canonical $T$ 之后再选 $\pi$ 与坏元素的对齐方式）；随机化论证需要 avg-T（见第 5.3 节与 GAP-2）。

---

## 5. 定理的推导（编号步骤）

固定 $K\ge2$，$\eta>1$，$n\ge4K^5$，split $(\eta_u,\eta_o)$，以及 $A\in\mathcal A_{\mathrm{lin}}$。

**S1（基实例）** 取第 3.3 节的 $(\Phi,\widetilde\Phi)$，满足引理 A 的 (A1)(A2)、1-blind 条件
$(\ast)$、band（对指定 split、对所有 $S$）、$\Phi(K,0)=1$、$\Phi(a,b)\le1$（$a+b=K$）、
$\Phi(0,K)\le\rho_K(\eta)$。
*用到*：引理 A；R2（$K=2,3$，$\eta=3/2$ 的 LP 存在性）；一般 $(K,\eta)$ 为 GAP-3。
状态：$K\in\{2,3\},\eta=3/2$ **[VERIFIED-LP]**；一般情形 **[CONJECTURE]**。

**S2（族）** 对每个 $K$-子集 $\pi\subseteq N$ 定义 $f_\pi(S)=\Phi(|S\cap\pi|,|S\setminus\pi|)$，
$\tilde f_\pi(S)=\widetilde\Phi(|S\cap\pi|,|S\setminus\pi|)$。由引理 A，每个 $f_\pi$ monotone submodular、
$f_\pi(\emptyset)=0$；由 S1 的 band 条件，每个 $(f_\pi,\tilde f_\pi)$ 的 error 在 $(\eta_u,\eta_o)$ 之内。
*用到*：引理 A；S1。**[HAND-PROOF-UNREVIEWED]**

**S3（canonical transcript induction）** 设 $\varphi(s)=\widetilde\Phi(0,s)$，并设"generic predictor"
为 $\tilde f_{\mathrm{gen}}(S)=\varphi(|S|)$。对固定的 deterministic $A$，令
$Q_1,\dots,Q_R$（$R\le nK$）与输出 $T$ 为 $A$ 在 $\tilde f_{\mathrm{gen}}$ 上的查询序列与输出（**canonical
transcript**，与 $\pi$ 无关）。断言：若 $|Q_i\cap\pi|\le1$ 对所有 $i\le R$ 成立，则 $A$ 在
$\tilde f_\pi$ 上的运行与 canonical transcript 逐字相同，输出也是 $T$。
*推导*（对 $i$ 归纳）：$i=1$ 时 $Q_1$ 由 $A$ 的确定性决定，与 predictor 无关；由 $(\ast)$，
$\tilde f_\pi(Q_1)=\varphi(|Q_1|)=\tilde f_{\mathrm{gen}}(Q_1)$。设前 $i-1$ 次查询与返回值都相同，则 $A$
的内部状态相同，故第 $i$ 次查询同为 $Q_i$，再由 $(\ast)$ 返回值相同。归纳完成；$T$ 是状态的函数，故相同。
*用到*：$A$ deterministic（Q4）；1-blind 条件 $(\ast)$；查询大小 $\le K$ 只在 S4 的计数里用到。
**[HAND-PROOF-UNREVIEWED]**

**S4（union bound 与显式常数）** 对均匀随机的 $K$-子集 $\pi$：

- (a) **可见事件** $\mathrm{Vis}=\{\exists i:|Q_i\cap\pi|\ge2\}$。每个 $Q_i$ 大小 $\le K$，含 $\binom K2$
  个 pair；一个固定 pair 被含入 $\pi$ 的概率是 $\binom{n-2}{K-2}/\binom nK=\frac{K(K-1)}{n(n-1)}$。故
  $$\Pr[\mathrm{Vis}]\ \le\ nK\cdot\binom K2\cdot\frac{K(K-1)}{n(n-1)}
   =\frac{K^3(K-1)^2}{2(n-1)}\ \le\ \frac{K^5}{2n},$$
  最后一步等价于 $n(K-1)^2\le(n-1)K^2$，即 $K^2\le n(2K-1)$，在 $n\ge K\ge2$ 时成立。
- (b) **命中事件** $\mathrm{Hit}=\{T\cap\pi\ne\emptyset\}$。$\Pr[e\in\pi]=K/n$，$|T|\le K$，故
  $\Pr[\mathrm{Hit}]\le K^2/n$。
- (c) $\Pr[\mathrm{Vis}\cup\mathrm{Hit}]\le K^2/n+K^5/(2n)=\varepsilon_n$。当 $n\ge4K^5$ 时
  $K^5/(2n)\le\frac18$ 且 $K^2/n\le\frac1{4K^3}\le\frac1{32}$，故 $\varepsilon_n\le\frac5{32}<1$。

*用到*：查询次数 $\le nK$、查询大小 $\le K$、输出大小 $\le K$（Q4）；$n\ge4K^5$（Q3）；S3 的 canonical
transcript（$Q_i$ 与 $T$ 在概率空间里是**常量**，这是 union bound 可用的前提）。
**[HAND-PROOF-UNREVIEWED]**（纯计数，可复核）

**S5（确定性结论）** 由 S4(c)，存在 $\pi^\ast$ 同时满足：所有 $Q_i$ 与 $\pi^\ast$ 至多交一个元素，
且 $T\cap\pi^\ast=\emptyset$。由 S3，$A$ 在 $(f_{\pi^\ast},\tilde f_{\pi^\ast})$ 上输出 $T$；由 S1，
$$\frac{f_{\pi^\ast}(T)}{f_{\pi^\ast}(O^\ast)}=\frac{\Phi(0,|T|)}{\Phi(K,0)}\le\Phi(0,K)\le\rho_K(\eta).$$
（$|T|\le K$ 时用 $\Phi$ 的单调性。）*用到*：S1、S3、S4。**[HAND-PROOF-UNREVIEWED]**

**S6（校准到恰好 $(\eta_u,\eta_o)$）** 令 $\eta_u^{\min}=\max_{S,e}d_e(S)/\tilde d_e(S)$，
$\eta_o^{\min}=\max_{S,e}\tilde d_e(S)/d_e(S)$（约定 $0/0=1$）。构造里把 $\widetilde\Phi$ 的整体尺度选成
在某个 $(S,e)$ 上 $d_e(S)=\eta_u\tilde d_e(S)$ 取等号，同时在另一个 $(S',e')$ 上
$\tilde d_{e'}(S')=\eta_o d_{e'}(S')$ 取等号；由 scaling（definition1.md convention B：
$\tilde f\mapsto c\tilde f$ 把 $(\eta_u,\eta_o)$ 变成 $(c\eta_u,\eta_o/c)$ 而 $\eta$ 不变），只要族在某个
状态上的真实增益比恰为 $\eta$，就能对**任意**指定 split 同时把两侧做紧。
*用到*：Definition 1 convention B 的 scaling 性质；构造里存在"增益比恰为 $\eta$"的位置。
状态：**[HAND-PROOF-UNREVIEWED]**；LP 侧的间接证据是三个 split 给出相同的最坏值（R2 表），
但"最小可容许因子恰为 $(\eta_u,\eta_o)$"这一等式本身我没有用 oracle 逐点核验（GAP-4）。

**S7（匹配）** 保证侧 thm:exact（每个 error $\le\eta$ 的实例上 predictive greedy $\ge\rho_K$）是外部输入。
与 S5 合并得 $\sup_A\inf_{(f,\tilde f)}=\rho_K(\eta)$，上确界由 predictive greedy 取到（Q5 的成员性）。
*用到*：thm:exact（**未在本文件重证**）；S5；Q5。**[HAND-PROOF-UNREVIEWED，依赖外部定理]**

**S8（randomized averaging）** 设 $A$ 随机、预算同 (Q4)，随机性由 seed $\omega$ 决定；对每个固定 $\omega$，
$A_\omega$ 是确定性算法，有自己的 canonical transcript 与输出 $T_\omega$。取 $\pi$ 均匀随机且与 $\omega$
独立，则
$$\mathbb E_{\pi,\omega}\Bigl[\frac{f_\pi(T_\omega)}{f_\pi(O^\ast)}\Bigr]
\le\mathbb E_\omega\Bigl[\Pr_\pi[\mathrm{Vis}\cup\mathrm{Hit}]\cdot1
+\Pr_\pi[\text{good}]\cdot\overline\rho\Bigr]\le\overline\rho+\varepsilon_n,$$
其中 $\overline\rho=\max_{T}\ \mathbb E_\pi[\,f_\pi(T)\mid T\cap\pi=\emptyset,\ \text{invisible}\,]$ 是
"轨道平均"（用了 $f_\pi(T)/f_\pi(O^\ast)\le1$ 处理坏事件）。再由 Fubini，存在一个 $\pi^\ast$ 使
$\mathbb E_\omega[\,\cdot\,]\le\overline\rho+\varepsilon_n$，把它固定成实例即得 (Q10)。
需要 $\overline\rho\le\rho_K$：这是 R2 表的 **avg-T** 列。$K=3$ 成立（$=0.5625$），
$K=2$ 给 $0.61>0.6$（GAP-2）。
*用到*：S3（对每个 seed）、S4 的两个计数、$f/f(O^\ast)\le1$、avg-T 值。
**[VERIFIED-LP for $K=3,\eta=3/2$; 其余 CONJECTURE]**

**S9（三个 assembly step 的前提清单）**

| assembly step | 内容 | 用到的前提 | 状态 |
|---|---|---|---|
| count grid $\to$ set function | 引理 A | 划分存在；$\Phi$ 的 (A1)(A2)；与 $\tilde f$ 无关 | [HAND-PROOF-UNREVIEWED] |
| canonical transcript induction | S3 | $A$ deterministic；1-blind $(\ast)$；查询返回值只经由 $\tilde f$ | [HAND-PROOF-UNREVIEWED] |
| randomized averaging | S8 | S3 对每个 seed 成立；$\pi\perp\omega$；S4 的两项计数；$f(T)\le f(O^\ast)$；avg-T $\le\rho_K$ | [VERIFIED-LP ($K=3$)] / [CONJECTURE] |

---

## 6. 数值走查

### 6.1 $K=3$，$\eta=3/2$

$k_1=(K-1)\eta+1=4$，$q=3/4$。

| $j$ | $V_j$ | 小数 | 含义 |
|---|---|---|---|
| 0 | $2/3$ | 0.666667 | 全部步落在 $O^\ast$ 之外；$=1/\eta$，也是对称 predictor 的天花板 (R1) |
| 1 | $7/12$ | 0.583333 | 1 步落在 $O^\ast$ 内 |
| 2 | $9/16$ | **0.562500** | $j^\ast=2$，$\rho_3(3/2)=9/16$ |
| 3 | $37/64$ | 0.578125 | $=U_3(3/2)$ |

$L_3(3/2)=386/729\approx0.529492<9/16<37/64=U_3(3/2)$ **[VERIFIED-EXHAUSTIVE]**。

预算与常数：$n\ge4K^5=972$；predictive greedy 用 $Kn-K(K-1)/2=3n-3=2913$ 次查询 $\le nK=2916$。
在 $n=972$：
$\Pr[\mathrm{Vis}]\le K^3(K-1)^2/(2(n-1))=108/1942\approx0.055613\le K^5/(2n)=1/8$；
$\Pr[\mathrm{Hit}]\le K^2/n=9/972=1/108\approx0.009259$；
$\varepsilon_{972}=1/108+1/8=29/216\approx0.134259<1$，故 S5 的 $\pi^\ast$ 存在。
LP 侧：$m=7$、三个 split 下 1-blind 族的 per-T / all-T / avg-T 全部等于 $0.5625=\rho_3(3/2)$
**[VERIFIED-LP]**；而 count-only 与 block-symmetric 族只能到 $0.666667$ **[VERIFIED-LP]**。

### 6.2 $K=2$（ProbeLottery 项）

*说明*：任务里"ProbeLottery"这个名字在我可读的四个输入文件中没有定义（它出现在任务文本而非
statement/definition/assumption/notation 里）。保守读法：它指 thm:linear-exact 的**随机化条款**
（probe = 对 $\tilde f$ 的查询，lottery = 对隐藏 $\pi$ 的抽签），因此这里做 $K=2$ 的随机化走查。
若 ProbeLottery 实为某个具体随机算法，本节的结论仍然适用于它，因为 S8 对**任意**同预算随机算法成立。

$k_1=\eta+1=5/2$，$q=\eta/k_1=3/5$；$V_0=2/3$，$V_1=3/5$，$V_2=16/25=0.64$；
$\rho_2(3/2)=3/5$，$j^\ast=1$；$L_2(3/2)=5/9\approx0.5556$，$U_2(3/2)=16/25$。
（端点核对：$\rho_2(1)=3/4=L_2(1)$，与 assumptions.md 里"two-element instance drives it to ratio
$1/2$ against $L_2(1)=3/4$"的数字一致 **[VERIFIED-EXHAUSTIVE]**。）

$n\ge4K^5=128$；$\varepsilon_{128}=K^2/n+K^5/(2n)=4/128+32/256=1/32+1/8=5/32=0.15625$；
精确 union bound $\Pr[\mathrm{Vis}]\le K^3(K-1)^2/(2(n-1))=8/254\approx0.0315$，
$\Pr[\mathrm{Hit}]\le4/128=0.03125$，和 $\approx0.0627<1$，S5 的 $\pi^\ast$ 存在。

随机化走查：$A$ 随机，seed $\omega$；对每个 $\omega$ 有 canonical $T_\omega$（$|T_\omega|\le2$）。
$\pi$ 均匀取 $\binom n2$ 个 pair 之一。坏事件概率 $\le5/32$（在 $n=128$）；好事件下
$\mathbb E[f_\pi(T_\omega)]$ 等于 1-blind 族的轨道平均 avg-T $=0.61$（LP，$m=5..9$ 稳定）
**[VERIFIED-LP]**，而不是 $\rho_2=0.6$。于是我的族给出
$\mathbb E\le0.61+\varepsilon_n$，比陈述里的 $0.6+\varepsilon_n$ 弱 $0.01$。只有当
$\varepsilon_n=20/n\ge0.01$，即 $n\le2000$ 时，两者不冲突；$n>2000$ 时我的构造达不到陈述（GAP-2）。
确定性条款在 $K=2$ 不受影响：per-T $=0.600000000$ **[VERIFIED-LP]**。

---

## 7. 没有闭合的步骤 / 额外添加的假设

- **GAP-1（R1 的手证缺一步）**：R1 的链式论证给出 $\sum_t d_{b_t}(O_{<t})\ge f(O^\ast)/\eta$，
  要得到 $f(T)=\sum_t d_{b_t}(T_{<t})\ge f(O^\ast)/\eta$ 还需比较两条链上的增益，我没有闭合。
  结论本身由 LP 在 $K=2,3$、$\eta=3/2$ 上确认。状态：结论 [VERIFIED-LP]，一般证明 [FAILED]
  （失败点：$T_{<t}$ 与 $O_{<t}$ 不可比，submodularity 不直接给出所需方向）。
- **GAP-2（$K=2$ 的轨道平均）**：1-blind 族的 avg-T 在 $K=2,\eta=3/2$ 是 $0.61$，
  严格大于 $\rho_2=0.6$；$m=5,\dots,9$ 与三个 split 上都稳定。确定性条款不受影响（per-T $=0.6$），
  随机化条款在 $n>2000$ 处我的族达不到 $\rho_2+\varepsilon_n$。可能的出路（未验证）：
  (a) 存在比 1-blind 更好的族；(b) $K=2$ 需要单独处理；(c) 陈述的随机化条款对小 $K$ 需要额外余项。
  状态：[FAILED]（我的构造在 $K=2$ 的随机化条款上，$\eta=3/2$，$n>2000$）。
- **GAP-3（一般 $(K,\eta)$ 的基实例）**：S1 里 $(\Phi,\widetilde\Phi)$ 的存在性只在
  $K\in\{2,3\},\eta=3/2$ 用 LP 确认。一般 $K$、一般 $\eta>1$ 的显式 $\Phi$ 我没有写出，也没有证明
  $\Phi(0,K)=\rho_K(\eta)$ 可达。状态：[CONJECTURE]。
- **GAP-4（校准的紧性）**：S6 只给了论证思路，没有对构造逐点核验"最小可容许因子恰好是
  $(\eta_u,\eta_o)$"。LP 只保证 band 以 $(\eta_u,\eta_o)$ 成立（即 error **至多**），
  不保证**恰好**。状态：[HAND-PROOF-UNREVIEWED]。
- **GAP-5（band 在大集合上的延拓）**：Definition 1 对**所有** $S\subseteq N$ 生效，包括 $|S|>K$。
  LP 只覆盖 $m\le7$ 的全格；$n$ 很大时 $\Phi(a,b)$ 在 $b$ 一直到 $n-K$ 的区间上如何保持 (A2) 与 band，
  我没有写出显式延拓（自然做法是让两坐标的增益在 $b$ 大时按同一几何率衰减，从而带宽保持 $\le\eta$）。
  状态：[CONJECTURE]。
- **GAP-6（thm:exact 未重证）**：S7 的保证侧、以及"LP 在小 $m$ 上的值不会随 $m\to n$ 继续下降"，
  都依赖 thm:exact。notation.md 只给了 $\rho_K=\min_jV_j$ 的公式。路线二不重证它。状态：外部输入。
- **GAP-7（$V_j$ 的 $j$ 取值范围）**：notation.md 未写明 $j$ 的范围，我按 $0\le j\le K$ 读，
  理由见 4.1（$j$ = 落在 $O^\ast$ 内的步数）。若原文的范围不同，$\rho_K$ 的数值会变。状态：读法假设。
- **添加的假设（ProbeLottery）**：第 6.2 节的说明。状态：读法假设。
- **未做的检验**：我没有核验 $\rho_K$ 在 $\eta\in(1,\infty)$ 上的单调性、$K=2$ 之外的端点行为、
  以及 $\varepsilon_n$ 里两个常数是否可以改进（我的计数给出的精确上界是
  $K^2/n$ 与 $K^3(K-1)^2/(2(n-1))$，后者严格小于 $K^5/(2n)$）。

### 空洞性检验（对陈述里的限定词逐个做）

| 限定词 | 去掉/取反会怎样 | 结论 |
|---|---|---|
| deterministic | 去掉后 S3 的归纳失效（查询序列不再是常量），只能走 S8 的平均，得到 $+\varepsilon_n$ | 载重，必须保留 |
| 至多 $nK$ 次查询 | 换成 $n^2$ 次：S4(a) 的 union bound 变成 $n^2\cdot K^2/2\cdot K^2/n^2=K^4/2\ge1$，论证失效 | 载重 |
| 每次查询大小 $\le K$ | 允许大集合查询时，一次查询可含 $\ge2$ 个隐藏元素的概率大增，S4(a) 失效 | 载重 |
| 输出大小 $\le K$ | 只用在 S4(b) 的 $|T|\le K$ 与 $\rho_K$ 的定义里 | 载重 |
| $n\ge4K^5$ | 用于 $\varepsilon_n<1$（确定性存在性）。若只要 $\varepsilon_n<1$，$n>K^2+K^5/2$ 足够，$4K^5$ 有余量 | 载重但不紧 |
| 最小因子**恰好** $(\eta_u,\eta_o)$ | 换成"至多"，命题变弱但仍非平凡；"恰好"排除了用更大 $\eta$ 的实例充数 | 载重（GAP-4 未核验） |
| no asymptotics in $n$ or $K$ | 确定性条款确实对每个 $n\ge4K^5$ 成立（常数显式）；随机化条款则**是**渐近的 | 表述正确，但两条款的强度不同，需并列说明 |

---

## 8. 读过的文件

只读了以下四个（无其他任何仓库文件、无网络）：

1. `/home/user/sub-modular-optimization/results/V11/inputs/definition1.md`
2. `/home/user/sub-modular-optimization/results/V11/inputs/assumptions.md`
3. `/home/user/sub-modular-optimization/results/V11/inputs/notation.md`
4. `/home/user/sub-modular-optimization/results/V11/inputs/statement_linear_exact.md`

另：`/home/user/sub-modular-optimization/CLAUDE.md` 由 session 自动载入（house rules），非本人主动打开。

写出的文件（全部在 `results/V11/route2/`，未修改任何既有文件）：
`linear_exact.md`、`q6_route2_checks.py`、`q6_route2_lp_scipy.py`、`q6_route2_lp_hard.py`、
`q6_route2_lp_k2.py`（sympy exact-LP 尝试，见下）、`q6_lp_log.txt`、`q6_lp_values.json`。

`q6_route2_lp_k2.py` 用 `sympy.solvers.simplex.lpmin` 做精确有理 LP，在 $O^\ast$ 与轨迹不交时抛
`UnboundedLPError`；我用一个显式可行解（模函数 $f=\tilde f=|S|/2$）精确核验了该 LP 可行，
因此这是求解器行为而非不可行，已改用 scipy/HiGHS，结论在 $K=2,3$ 上与手算一致。状态：[FAILED]（精确有理
求解器路径），[VERIFIED-LP]（浮点 HiGHS 路径，值都是 $0.6$、$0.5625$、$2/3$、$0.61$ 这类短有理数）。

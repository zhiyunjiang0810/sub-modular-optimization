# ROUTE-TWO 盲审推导：thm:hardness（台账 T10，论文 Theorem 3；TASKS11 Q7）

本文件是在隔离条件下对 thm:hardness 的独立推导。只读取了
`results/V11/inputs/` 下的四个输入文件（清单见第 5 节），没有读取论文正文、
台账、附录或任何其他实现。所有数学断言带状态标签。符号/穷举检查脚本：
`results/V11/route2/q7_verify_hardness.py`（可一键复跑，精确有理数）。

一句话结论：statement 的**值公式** $H_{K,\tau}(\eta)=L_K(\bar\theta)$、
$\bar\theta\ge1\iff\eta\ge\frac{K-1}{K-\tau}$、$K\to\infty$ 极限、以及
$(\eta_u,\eta_o)$ 任意劈分的 rescaling，四项我都能独立闭合（前三项有 oracle）。
**隐藏引理的门槛条件 $n\ge4K^{c+2}$ 与随机化附加项 $\varepsilon_n$ 的第二项，
我的推导给不出**：我得到的充分条件是 $n\ge4K^{2\tau}$（在 $c=0,\tau=1$ 时两者
恰好都是 $4K^2$，$c>0$ 时 stated 条件比我需要的弱），而我得到的附加项是
level-$\tau$ 的 union bound $\frac{K^{2\tau}}{\tau!\,n^{\tau-c}}$，
statement 里显示的是 level-$(\tau+1)$ 的 $\frac{K^{2\tau+2}}{(\tau+1)!\,n^{\tau+1-c}}$
（严格更小）。细节见第 4 节。

---

## 1. 陈述复述（逐个量词写全）

### 1.1 固定的对象与顺序

按 `assumptions.md`：ground set $N$，$|N|=n$；monotone submodular
$f:2^N\to\mathbb R_{\ge0}$，$f(\emptyset)=0$；cardinality budget $K$，$1\le K\le n$；
算法**不能**求值 $f$，只能查询 predictor $\tilde f$（$\tilde f(\emptyset)=0$）；
$d_e(S)=f(S\cup\{e\})-f(S)$，$\tilde d_e(S)=\tilde f(S\cup\{e\})-\tilde f(S)$；
$O^\ast$ 是一个最优 $K$-set，$F^{\mathrm{OPT}}=f(O^\ast)$；比值约定
$\alpha\in(0,1]$，$F^{\mathrm{ALG}}\ge\alpha F^{\mathrm{OPT}}$，越大越好。

量词顺序（这是整条定理的骨架，顺序不可交换）：

1. **对所有**实数 $c\ge0$。由 $c$ 定义 $\tau:=\lceil c\rceil+1$（整数 $c$ 时
   $\tau=c+1$；一般地 $\tau-c\ge1$，且 $\tau\ge1$）。
2. **对所有**整数 $K,n$ 与实数 $\eta$，满足
   $K>\tau$、$n\ge4K^{c+2}$、$\eta>1$ 且 $\eta\ge\frac{K-1}{K-\tau}$
   （后者等价于 $\bar\theta\ge1$，见 Step 2）。注意 $K>\tau$ 是让 $K-\tau\ge1$、
   使 $\frac{K-1}{K-\tau}$ 有定义且为正的必要条件。
3. **对所有**确定性（deterministic）算法 $\mathcal A$，它对 $\tilde f$ 的查询
   **至多 $n^c$ 次**（$Q:=n^c$），**每次查询的集合大小至多 $K$**，
   输出 $T$ 且 $|T|\le K$。算法是 adaptive 的（第 $i$ 次查询可依赖前 $i-1$ 个回答），
   但不是随机的。
4. **存在**一个 instance $(f,\tilde f)$：$f$ monotone submodular（$f(\emptyset)=0$），
   $\tilde f$ 是 predictor，且 $(f,\tilde f)$ 在 Definition~\ref{def:eta} 意义下
   **最小可行 error factors 的乘积恰好等于 $\eta$**（是 "exactly"，不是 "at most"；
   即 $\inf\{\eta_u\eta_o:\ \text{band 成立}\}=\eta$ 且 inf 取到）。
5. 使得 $\mathcal A$ 在该 instance 上的输出 $T$ 满足
   $$\frac{f(T)}{f(O^\ast)}\ \le\ H_{K,\tau}(\eta):=1-\Bigl(1-\frac1{\eta(K-\tau)+1}\Bigr)^{K}=L_K(\bar\theta).$$

### 1.2 附带的三条从句

6. **劈分**：对任何预先指定的 $(\eta_u,\eta_o)$ 且 $\eta_u\eta_o=\eta$，都存在
   同一族的一个 rescaling 实现该劈分（$\eta$ 不变）。
7. **随机化**：对所有随机算法（同样至多 $n^c$ 次查询、每次集合大小 $\le K$），
   同一 bound 在**期望**意义下成立，允许一个 additive
   $\varepsilon_n=\frac Kn+\frac{K^{2\tau+2}}{(\tau+1)!\,n^{\tau+1-c}}$；
   期望是对算法的内部随机性取的（Yao 意义下也可以读成：对 instance 分布取期望）。
8. **渐近**：$K\to\infty$、$\tau,\theta$ 固定时 $K\delta(\theta)\to\tau-1/\theta$；
   $c,\eta$ 固定时 $H_{K,\tau}(\eta)\to1-e^{-1/\eta}$。

### 1.3 定义域与约定（逐项）

- $\eta$ 的定义域：$\eta>1$（严格），且 $\eta\ge\frac{K-1}{K-\tau}$。
  当 $\tau=1$ 时 $\frac{K-1}{K-1}=1$，第二个约束被 $\eta>1$ 吞掉；
  当 $\tau\ge2$ 时第二个约束是真约束（数值见第 3 节）。
- $K$ 的定义域：整数，$\tau<K\le n$。
- $\eta_u,\eta_o$：按 `definition1.md` convention B，$\eta_u,\eta_o>0$ 且
  $\eta=\eta_u\eta_o\ge1$；没有结论依赖劈分。
- **tie breaking**：`assumptions.md` 规定所有 worst-case 陈述里 ties 被 adversarially
  打破。本定理的 statement 里算法是任意确定性算法（不是 greedy），
  所以 tie breaking 不在算法一侧出现；它只在下面这个意义上被用到：
  adversary 可以在给 predictor 赋值时把"并列"往对自己有利的一边推
  （Step 7 的 oblivious 回答就是最极端的版本）。**我的推导不需要 tie-breaking 假设**，
  这是一个可以做空洞性检验的限定词，见第 4.6 节。
- $|T|\le K$（不是 $=K$）：monotone $f$ 下补满到 $K$ 只会变好，所以 $\le$ 与 $=$
  对上界陈述等价（Step 9）。

---

## 2. 推导（编号步骤，每步注明所用假设/前置步骤）

记号：$\beta:=\dfrac{1}{\eta(K-\tau)+1}$，$\bar\theta:=\dfrac{\eta(K-\tau)+1}{K}$，
于是 $\beta=\dfrac1{\bar\theta K}$。归一化 $f(O^\ast)=1$（`assumptions.md` 说
$f(O^\ast)=0$ 时比值陈述平凡成立，所以可设 $f(O^\ast)>0$ 并按它缩放；
缩放不改变 $d/\tilde d$ 的比值，因此不改变 $\eta$）。

### Step 1（代数恒等式：$H=L_K(\bar\theta)$）[VERIFIED-SYMBOLIC]

`notation.md` 给 $L_K(x)=1-\bigl(1-\frac1{xK}\bigr)^K$。代入 $x=\bar\theta$：
$\frac1{\bar\theta K}=\frac1{\eta(K-\tau)+1}=\beta$，故
$L_K(\bar\theta)=1-(1-\beta)^K=H_{K,\tau}(\eta)$。
sympy 化简差为 $0$（脚本 C1）。依据：`notation.md` 的 $L_K$ 定义 + 代数。

### Step 2（$\bar\theta\ge1$ 与 $\eta\ge\frac{K-1}{K-\tau}$ 等价）[VERIFIED-SYMBOLIC]

$K>\tau\Rightarrow K-\tau>0$，于是
$\bar\theta\ge1\iff\eta(K-\tau)+1\ge K\iff\eta(K-\tau)\ge K-1\iff\eta\ge\frac{K-1}{K-\tau}$。
sympy：$[\eta(K-\tau)+1-K]-(K-\tau)[\eta-\frac{K-1}{K-\tau}]\equiv0$（脚本 C2）。
依据：statement 的 $K>\tau$ 假设。
**这条解释了 statement 里那句 "so that $\bar\theta\ge1$"**：它不是额外条件，
就是 $\eta\ge\frac{K-1}{K-\tau}$ 的改写。
含义：$\bar\theta\ge1$ 保证 $\beta\le1/K$，即每一步至多吃掉剩余量的 $1/K$，
这正是 $L_K$ 作为 guarantee curve 的合法参数域（$L_K$ 的自变量是 error level，需 $\ge1$）。

### Step 3（一致性：$H_{K,\tau}(\eta)\ge L_K(\eta)$）[VERIFIED-EXHAUSTIVE]

$\tau\ge1,\eta\ge1\Rightarrow\eta\tau\ge1\Rightarrow\eta(K-\tau)+1\le\eta K
\Rightarrow\beta\ge\frac1{\eta K}\Rightarrow H\ge L_K(\eta)$。
穷举：$K\in[2,12]$，$\tau\in[1,K)$，$\eta\in\{1,\frac54,\dots,10\}$（有理数网格，
只取满足 $\bar\theta\ge1$ 的格点），$H<L_K(\eta)$ 的反例个数 $=0$（脚本 C3）。
这是必需的 sanity check：hardness 上界不能低于已知 guarantee，否则两条结果互相矛盾。
依据：Step 1 + `notation.md` 的 $L_K$。

### Step 4（硬族必须长什么样：oblivious window）[HAND-PROOF-UNREVIEWED]

从 statement 本身反推构造的形状。算法只能碰 $\tilde f$，而 $f$ 的取值（比值的分子分母）
完全由 adversary 在事后决定。要让**任何** $n^c$ 次查询的确定性算法都失败，
必须让查询序列本身不携带关于 $O^\ast$ 的信息。做法唯一：

- (a) 取一个 hidden set $O^\ast\subseteq N$，$|O^\ast|=K$；
- (b) 取一个 **oblivious**（只依赖 $|S|$ 的）函数 $\Psi:\{0,1,\dots,K\}\to\mathbb R_{\ge0}$，
  令 $\tilde f(S)=\Psi(|S|)$ **在 window 内**
  $$\mathcal W_\tau:=\{S\subseteq N:\ |S|\le K,\ |S\cap O^\ast|\le\tau-1\}$$
  成立；window 外 $\tilde f$ 可以随 $f$ 走（那里 error 取 $1$，不影响全局 $\eta$）。

**为什么必须是 window 而不是全域。** 若要求 $\tilde f\equiv\Psi(|S|)$ 对所有 $|S|\le K$
成立，则对任意 $S$ 与 $e,e'\notin S$ 都有 $\tilde d_e(S)=\tilde d_{e'}(S)$，
于是 Definition~\ref{def:eta} 的 band 强制
$$\frac{\max\{d_e(S),d_{e'}(S)\}}{\min\{d_e(S),d_{e'}(S)\}}\le\eta_u\eta_o=\eta
\qquad(\ast)$$
（把 $d_e/\eta_u\le\tilde d\le\eta_o d_e$ 与同样的 $e'$ 不等式两两相除即得；
这是 Step 4 的核心不等式，下面反复用）。取 $S$ 使得 $|S\cap O^\ast|=K-1$：
剩下那个 $o\in O^\ast\setminus S$ 的 $d_o(S)$ 是"最后一块必需品"，
而一个 dummy 在同一 $S$ 上的增益可以被 adversary 压到任意小，$(\ast)$ 会被违反。
所以 oblivious 只能在**离 $O^\ast$ 足够远**的区域成立，
"足够远"的度量就是 balancedness margin $\tau$：$|S\cap O^\ast|\le\tau-1$。
> 状态：这一步是"必须长成这样"的启发式论证（necessity 的方向我没有严格闭合，
> 只闭合了 "全域 oblivious 不可行"）。标 [HAND-PROOF-UNREVIEWED]。

### Step 5（$(\ast)$：band 把 hidden/dummy 的真增益比锁在 $\eta$ 内）[HAND-PROOF-UNREVIEWED]

设 $S\in\mathcal W_\tau$，$e,e'\notin S$，且 $S\cup\{e\},S\cup\{e'\}$ 仍在 window 内，
则 $\tilde d_e(S)=\Psi(|S|+1)-\Psi(|S|)=\tilde d_{e'}(S)=:w$。由 Definition~\ref{def:eta}
（convention B 下同形）：$d_e(S)/\eta_u\le w\le\eta_o d_e(S)$ 与
$d_{e'}(S)/\eta_u\le w\le\eta_o d_{e'}(S)$。于是
$d_e(S)\le\eta_u w\le\eta_u\eta_o d_{e'}(S)=\eta\,d_{e'}(S)$，对称地反过来也成立，
即 $(\ast)$。**这是 $\eta$ 唯一进入构造的入口**：$\eta$ 不限制算法的行为，
它限制 adversary 能把 hidden 元素和 dummy 元素的真增益拉开多远。
依据：Definition~\ref{def:eta} / convention B（`definition1.md`）+ Step 4 的 (b)。

### Step 6（每步能吃到的剩余比例 $\ge\beta$，"$\eta(K-\tau)+1$" 的来历）[HAND-PROOF-UNREVIEWED]

设算法在某个 window 内状态 $S$，记剩余量
$R(S):=f(O^\ast\cup S)-f(S)$。由 $f$ monotone 得 $R(S)\ge f(O^\ast)-f(S)=1-f(S)$；
由 submodular 得 telescoping 上界
$$R(S)\ \le\ \sum_{o\in O^\ast\setminus S}d_o(S).\qquad(\dagger)$$
（$(\dagger)$ 是 submodularity 的标准推论：把 $O^\ast\setminus S$ 逐个加入，
每一步的增益被在更小集合 $S$ 上的增益上界。）

现在数 $(\dagger)$ 右边的项数与每项大小。窗口允许算法最多握住 $\tau-1$ 个
$O^\ast$ 元素，所以**临界状态**是 $|S\cap O^\ast|=\tau-1$，此时
$|O^\ast\setminus S|=K-\tau+1$。设算法这一步选中的元素真增益为 $g$。把
$O^\ast\setminus S$ 的 $K-\tau+1$ 项分成两类：

- 其中一项记作当前这一步实际吃到的那一个（或与它并列的那一个），贡献恰好 $g$；
- 其余 $K-\tau$ 项，每一项由 Step 5 的 $(\ast)$ 受限于 $\eta g$。

于是
$$R(S)\ \le\ (K-\tau)\cdot\eta g+1\cdot g=\bigl(\eta(K-\tau)+1\bigr)g,
\qquad\text{即}\qquad g\ \ge\ \beta\,R(S).\qquad(\ddagger)$$
**这就是 $\eta(K-\tau)+1$ 的组合意义**：$K-\tau$ 个"被 band 放大 $\eta$ 倍的
hidden 元素" + $1$ 个"当前这一步本身"。
与 `notation.md` 里 $U_K(\eta)=1-(1-\frac1{\eta(K-1)+1})^K$ 对照：
$U_K$ 是 $\tau=1$ 的同一个计数（$K-1$ 个 + 当前 $1$ 个），
hardness 族把"免费漏掉的元素"从 $1$ 个放宽到 $\tau$ 个，于是 $K-1\rightsquigarrow K-\tau$。
依据：monotone + submodular（`assumptions.md`）+ Step 5 + Step 4 的 window 定义。

### Step 7（$K$ 步几何衰减 → $1-(1-\beta)^K$）[HAND-PROOF-UNREVIEWED]

令 $S^0=\emptyset\subseteq\ldots\subseteq S^K=T$ 是算法输出的任一 $K$ 步填充顺序，
$R_t:=R(S^t)$，$g_t:=f(S^{t+1})-f(S^t)$。$(\ddagger)$ 给 $g_t\ge\beta R_t$；
又 $R_{t+1}=R_t-g_t$（由 $R$ 的定义与 $f$ 的 telescoping，$f(O^\ast\cup S)$ 在
$S\subseteq O^\ast\cup S$ 下的变化被吸收），于是
$$R_{t+1}\le(1-\beta)R_t\ \Longrightarrow\ R_K\le(1-\beta)^K R_0=(1-\beta)^K,$$
$$f(T)=1-R_K\ \ge\ 1-(1-\beta)^K=H_{K,\tau}(\eta).$$
注意方向：**这是 guarantee 方向的不等式**（"每步至少吃 $\beta$ 比例"）。
Hardness 族的作用是把 $(\dagger)(\ddagger)$ 的每一个不等号都**取等**：
adversary 把 $f$ 造成使得 window 内每一步恰好吃到 $\beta R_t$、
且窗口内任何 $K$ 元集合都达不到更多。于是
$$\max\{f(T):\ |T|\le K,\ |T\cap O^\ast|\le\tau-1\}=1-(1-\beta)^K=H_{K,\tau}(\eta).$$
这就是 statement 里 $H=L_K(\bar\theta)$ 的结构性解释：
**hardness 值 = guarantee curve 在有效 error $\bar\theta=\frac{\eta(K-\tau)+1}{K}$ 处的取值**，
有效 error 比真实 error $\eta$ 小（$\bar\theta\le\eta\iff\eta\tau\ge1$，Step 3），
差额正是被 $\tau$ 个"免费"元素吃掉的部分。
> 状态：ratio $r=1-\beta$ 的几何衰减与终值 $1-(1-\beta)^K$ 我能写清楚；
> **"存在这样一个取等的 monotone submodular $f$" 我没有构造出来**（见 4.1）。
> 因此 Step 7 只能标 [HAND-PROOF-UNREVIEWED]，且带一个未闭合的存在性缺口。

### Step 8（隐藏引理：$n^c$ 次查询的 union bound）[HAND-PROOF-UNREVIEWED]

算法是确定性的，且我们对 window 内的一切查询都用 oblivious 的 $\Psi(|S|)$ 回答。
于是**回答序列与 $O^\ast$ 无关**，从而**查询序列 $S_1,\dots,S_Q$（$Q=n^c$）
是一个与 $O^\ast$ 无关的固定序列**（这一步用到 deterministic；随机化见 Step 11）。
剩下只需证明：存在一个 $K$-set $O^\ast$ 使得所有查询都落在 window 内，
即 $|S_i\cap O^\ast|\le\tau-1\ \forall i$。用概率方法，取 $O^\ast$ 在所有
$K$-subsets 上均匀随机：

1. 固定 $i$ 与一个 $\tau$-subset $A\subseteq S_i$。因为 $K\le n$，
   $$\Pr[A\subseteq O^\ast]=\frac{K(K-1)\cdots(K-\tau+1)}{n(n-1)\cdots(n-\tau+1)}
   \le\Bigl(\frac Kn\Bigr)^{\tau}$$
   （逐项 $\frac{K-i}{n-i}\le\frac Kn$）。
2. $|S_i|\le K$（**这里用到"每次查询集合大小 $\le K$"这个量词**），
   所以 $S_i$ 内的 $\tau$-subset 至多 $\binom{K}{\tau}\le\frac{K^\tau}{\tau!}$ 个，
   union bound 给
   $$\Pr\bigl[|S_i\cap O^\ast|\ge\tau\bigr]\le\frac{K^{\tau}}{\tau!}\Bigl(\frac Kn\Bigr)^{\tau}
   =\frac{K^{2\tau}}{\tau!\,n^{\tau}}.$$
3. 对 $Q=n^c$ 次查询再 union：
   $$\Pr\bigl[\exists i:\ |S_i\cap O^\ast|\ge\tau\bigr]\ \le\
   \frac{K^{2\tau}}{\tau!\,n^{\tau-c}}=:P_\tau(n).\qquad(\S)$$
4. 只要 $P_\tau(n)<1$，就存在一个 $O^\ast$ 使所有查询留在 window 内，
   Step 7 的值上界随即适用于该 $O^\ast$。

**我得到的充分条件。** 由 $\tau=\lceil c\rceil+1\ge c+1$ 得 $\tau-c\ge1$，故
$n^{\tau-c}\ge n$，于是
$$n\ \ge\ 4K^{2\tau}\ \Longrightarrow\ P_\tau(n)\le\frac{K^{2\tau}}{\tau!\,n}\le\frac1{4\,\tau!}\le\frac14<1 .$$
**与 statement 的 $n\ge4K^{c+2}$ 的关系。** 在 $c=0$（$\tau=1$）时
$4K^{2\tau}=4K^2=4K^{c+2}$，**完全一致**，而且常数 $4$ 正好把 $(\S)$ 压到 $1/4$
（数值见第 3 节）。$c>0$ 时 $2\tau=2\lceil c\rceil+2>c+2$，stated 条件严格更弱：
把 $n=4K^{c+2}$（整数 $c$，$\tau=c+1$）代回 $(\S)$ 得（脚本 C5）
$$P_\tau\bigl(4K^{c+2}\bigr)=\frac{K^{2c+2}}{(c+1)!\cdot4K^{c+2}}=\frac{K^{c}}{4\,(c+1)!},$$
它 $<1$ 当且仅当 $K^c<4(c+1)!$，即 $c=1$ 时 $K<8$、$c=2$ 时 $K\le4$。
所以 **stated 的 $n\ge4K^{c+2}$ 不足以让我这条 union bound 收敛**，
除非还有我看不到的更省的计数。记为 GAP-1（第 4 节）。

### Step 9（从 window 上界到输出比值）[HAND-PROOF-UNREVIEWED]

算法输出 $T$，$|T|\le K$。由 Step 8 选定的 $O^\ast$，所有被查询过的集合都在 window 内。
要把 $T$ 也放进 window，需要 $|T\cap O^\ast|\le\tau-1$。
若 $T$ 本身被查询过，直接由 Step 8 得到；若 $T$ 未被查询过（确定性算法完全可以
输出一个没查过的集合），则需要在 Step 8 的 union bound 里把 $T$ 也算作一次"查询"，
即用 $Q+1\le n^c+1$ 代替 $Q$。这只把 $(\S)$ 放大到 $\frac{K^{2\tau}(1+n^{-c})}{\tau!\,n^{\tau-c}}$，
在 $n\ge4K^{2\tau}$ 下仍 $<1$（$\tau\ge1$ 时富余足够）。
于是 $T\in\mathcal W_\tau$，Step 7 给 $f(T)\le H_{K,\tau}(\eta)\cdot f(O^\ast)$。
$|T|\le K$ 而非 $=K$：$f$ monotone，补满只会增大 $f(T)$，所以对 $|T|=K$ 证上界即可。
依据：Step 7 + Step 8 + `assumptions.md` 的 monotone。

### Step 10（error 恰好 $=\eta$ 与任意劈分）[HAND-PROOF-UNREVIEWED]（劈分部分可独立闭合）

"最小可行 error factors 之积恰好 $\eta$" 需要两件事：
(i) 上界：window 内由 Step 5 的构造，band 处处以 $\eta$ 成立，window 外取 $\tilde f=f$
（error $1$）；(ii) 下界：存在某个 $(S,e),(S,e')$ 使 $(\ast)$ 取等，
即真增益比恰为 $\eta$。(ii) 要求 Step 7 的构造在临界状态上把 $\eta$ 用满
（这与 $(\ddagger)$ 取等是同一个要求）。我没有显式构造，故 (ii) 未闭合。

**劈分从句可以独立闭合**（只用 `definition1.md`）：convention B 明确
"multiplying $\tilde f$ by $c>0$ maps $(\eta_u,\eta_o)\to(c\eta_u,\eta_o/c)$ and leaves
$\eta$ unchanged"。设已实现的最小劈分为 $(\eta_u^0,\eta_o^0)$，$\eta_u^0\eta_o^0=\eta$，
给定目标 $(\eta_u,\eta_o)$ 且 $\eta_u\eta_o=\eta$，取缩放因子
$$\kappa=\frac{\eta_u}{\eta_u^0}\ \Longrightarrow\
(\kappa\eta_u^0,\ \eta_o^0/\kappa)=\Bigl(\eta_u,\ \frac{\eta_u^0\eta_o^0}{\eta_u}\Bigr)
=\Bigl(\eta_u,\frac{\eta}{\eta_u}\Bigr)=(\eta_u,\eta_o).$$
即"任何预先指定的劈分都由一次 rescaling 实现"，且 $f$ 与算法行为不变
（$\tilde f\mapsto\kappa\tilde f$ 不改变 $\arg\max\tilde d$，也不改变算法能区分的信息，
因为它是全局常数倍）。**注意**：这一步依赖 convention B 允许 $\eta_u<1$ 或 $\eta_o<1$；
`definition1.md` 里 verbatim 的论文文本把两个因子都下界在 $1$，那时只有
$\eta_u\in[1,\eta]$ 的劈分可实现。这是一个量词依赖，记为 GAP-4。

### Step 11（随机化与 $\varepsilon_n$）[HAND-PROOF-UNREVIEWED / 部分 FAILED]

随机算法时 Step 8 的"查询序列与 $O^\ast$ 无关"仍然成立（我们的回答仍是 oblivious 的
$\Psi(|S|)$，与 $O^\ast$ 无关），但查询序列现在依赖算法的随机带 $r$。
标准做法（Yao）：固定 $O^\ast$ 的均匀分布，对 $(r,O^\ast)$ 取联合期望。
记 bad event $B=\{\exists i:|S_i\cap O^\ast|\ge\tau\}\cup\{|T\cap O^\ast|\ge\tau\}$。
对每个固定的 $r$，Step 8 的计算逐字成立，故 $\Pr_{O^\ast}[B\mid r]\le P_\tau(n)+\frac{K^{2\tau}}{\tau!n^\tau}$，
取期望后同界。在 $B^c$ 上 Step 9 给 $f(T)/f(O^\ast)\le H$；在 $B$ 上比值至多 $1$。
于是
$$\mathbb E\Bigl[\frac{f(T)}{f(O^\ast)}\Bigr]\ \le\ H_{K,\tau}(\eta)+\Pr[B]
\ \le\ H_{K,\tau}(\eta)+\underbrace{\frac{K^{2\tau}}{\tau!\,n^{\tau-c}}\Bigl(1+n^{-c}\Bigr)}_{=:\ \varepsilon_n^{\text{(mine)}}\ \text{的主项}} .$$

把我的 $\varepsilon_n^{\text{(mine)}}$ 与 statement 的
$\varepsilon_n=\frac Kn+\frac{K^{2\tau+2}}{(\tau+1)!\,n^{\tau+1-c}}$ 对照（脚本 C5）：

- statement 的第二项**逐字等于我的 $(\S)$ 在 level $\tau+1$ 处的值**：
  $n^c\binom{K}{\tau+1}(K/n)^{\tau+1}\le\frac{K^{2\tau+2}}{(\tau+1)!\,n^{\tau+1-c}}$，
  sympy 差为 $0$。也就是说 statement 的随机化项对应的是
  $\Pr[\exists i:|S_i\cap O^\ast|\ge\tau+1]$，**比我需要的 level-$\tau$ 事件严格小**：
  两者之比 $\frac{P_\tau}{P_{\tau+1}}=\frac{(\tau+1)n}{K^2}\gg1$。
- 第一项 $\frac Kn$ 我只能给出一个**猜测性**的来源：$\frac Kn=\Pr[e\in O^\ast]$
  （单个固定元素落进随机 $K$-set 的概率），像是"输出集合的单个元素偶然命中"
  这一项的代价；但从 statement 本身我推不出它，也推不出为什么是 $K/n$ 而不是 $K^2/n$
  （$\mathbb E|T\cap O^\ast|\le K^2/n$）。

**结论（诚实版）**：$\varepsilon_n$ **as displayed 不从我的论证得出**；
我的论证给出的是 $\frac Kn+\frac{K^{2\tau}}{\tau!\,n^{\tau-c}}$
（即把显示式里的 $\tau+1$ 换回 $\tau$），它比 displayed 版本大。
两者在 $n\to\infty$ 时都 $\to0$（因 $\tau-c\ge1$），所以定性结论不受影响，
但**常数与指数不一致**。记为 GAP-2/GAP-3。

### Step 12（渐近）[VERIFIED-SYMBOLIC / 部分无法检验]

$c,\eta$ 固定、$K\to\infty$（$\tau$ 随之固定）时
$$H_{K,\tau}(\eta)=1-\Bigl(1-\frac1{\eta(K-\tau)+1}\Bigr)^{K},\qquad
K\ln\Bigl(1-\frac1{\eta(K-\tau)+1}\Bigr)\longrightarrow-\frac1\eta,$$
故 $H\to1-e^{-1/\eta}$。sympy `limit` 直接给 $1-e^{-1/\eta}$，
与目标之差化简为 $0$（脚本 C4）。
另一条 "$K\delta(\theta)\to\tau-1/\theta$"：**$\delta(\theta)$ 与 $\theta$ 的定义
不在我的四个输入文件里**（`notation.md` 只说 $a_\theta,\delta(\theta),\Psi,\bar\theta$
是 hardness-family parameters，没给公式）。因此这一条我无法检验，记为 GAP-5。
可以说的只是：若 $\delta$ 与 $\bar\theta$ 的关系是
$\bar\theta=\frac{\eta(K-\tau)+1}{K}$ 这一类"$\theta$ 减去 $O(1/K)$ 修正"的形式，
则 $K\delta\to\tau-1/\theta$ 与 $K\bigl(\theta-\bar\theta\bigr)$ 的展开同阶：
取 $\theta=\eta$ 时 $K(\eta-\bar\theta)=K\eta-\eta(K-\tau)-1=\eta\tau-1$，
与 $\tau-1/\theta$ 只差一个 $\theta=\eta$ 的乘因子（$\eta\tau-1=\eta(\tau-1/\eta)$）。
这是**一致性的强提示，不是验证**，标 [CONJECTURE]。

---

## 3. 数值走查（精确有理数，脚本 C6）

### 3.1 $K=3$，$\eta=3/2$

先确定哪些 $\tau$ 合法。$K>\tau\Rightarrow\tau\in\{1,2\}$；
$\tau=\lceil c\rceil+1$，故 $\tau=1\Leftrightarrow c=0$，$\tau=2\Leftrightarrow c\in(0,1]$。

- $\tau=2$（$c\in(0,1]$）：要求 $\eta\ge\frac{K-1}{K-\tau}=\frac{2}{1}=2$，
  但 $\eta=3/2<2$，**假设不满足**（脚本 C6 返回 False）。所以 $K=3,\eta=3/2$ 只有
  $\tau=1$ 一格可走。这本身是一个有用的观察：$\tau\ge2$ 时
  $\eta\ge\frac{K-1}{K-\tau}$ 是真约束，小 $K$ 下把 $\eta$ 逼得很高。
- $\tau=1$（$c=0$，即算法只允许 $n^0=1$ 次查询）：
  - $\beta=\dfrac1{\eta(K-\tau)+1}=\dfrac1{\frac32\cdot2+1}=\dfrac14$，
    $\bar\theta=\dfrac{\eta(K-\tau)+1}{K}=\dfrac43\ \ge1$ ✓。
  - 几何衰减（Step 7），$r=1-\beta=3/4$：
    $$R_0=1,\quad R_1=\tfrac34,\quad R_2=\tfrac9{16},\quad R_3=\tfrac{27}{64},$$
    $$f(T)=1-R_3=\tfrac{37}{64}=0.578125=H_{3,1}(3/2).$$
  - 交叉检查 Step 1：$L_3(4/3)=1-\bigl(1-\frac1{(4/3)\cdot3}\bigr)^3=1-(3/4)^3=\frac{37}{64}$ ✓。
  - 交叉检查 Step 3：$L_3(3/2)=1-(1-\frac1{4.5})^3=1-(7/9)^3=\frac{386}{729}\approx0.5295
    \le\frac{37}{64}$ ✓（hardness 值高于 guarantee，无矛盾）。
  - 门槛：$n\ge4K^{c+2}=4\cdot3^2=36$。此时 Step 8 的 union bound
    $$P_1(36)=n^{0}\binom31\frac Kn=3\cdot\frac3{36}=\frac14<1\ \checkmark$$
    （$c=0$ 时 stated 条件与我的 $4K^{2\tau}=4K^2=36$ 恰好相同，常数 $4$ 把概率压到 $1/4$）。
  - $\varepsilon_n$ 在 $n=36$：displayed $=\frac3{36}+\frac{3^4}{2!\cdot36^2}=\frac{11}{96}\approx0.1146$；
    我的版本 $=\frac3{36}+\frac{3^2}{1!\cdot36}=\frac13\approx0.3333$。
    注意 $H+\frac13=0.911<1$，所以即使用我的（更大的）附加项，$n=36$ 这一格仍然非平凡。

### 3.2 $K=2$（对应 "ProbeLottery item"）

**说明**：`ProbeLottery` 这个名字没有出现在我的四个输入文件里（既不在 statement，
也不在 notation table），所以我无法按它的定义走查。保守处理：我把 $K=2$ 这一格
当作定理本身在 $K=2$ 的实例化来算，并把"ProbeLottery 未定义"记入第 4 节。

$K=2\Rightarrow\tau=1\Rightarrow c=0$（$\tau<K=2$ 只剩 $\tau=1$）。
$\eta\ge\frac{K-1}{K-\tau}=\frac11=1$，被 $\eta>1$ 吞掉，故任何 $\eta>1$ 都合法。
一般式：
$$\beta=\frac1{\eta+1},\qquad
H_{2,1}(\eta)=1-\Bigl(\frac{\eta}{\eta+1}\Bigr)^{2},\qquad
\bar\theta=\frac{\eta+1}{2}.$$
取 $\eta=3/2$：$\beta=2/5$，$r=3/5$，$R_0=1,R_1=3/5,R_2=9/25$，
$$f(T)=1-\tfrac9{25}=\tfrac{16}{25}=0.64=H_{2,1}(3/2),\qquad \bar\theta=\tfrac54,$$
$L_2(3/2)=1-(1-\frac13)^2=\frac59\approx0.5556\le0.64$ ✓。
门槛 $n\ge4K^2=16$，union bound $\binom21\cdot\frac2{16}=\frac14<1$ ✓。
$\varepsilon_{16}$：displayed $=\frac2{16}+\frac{2^4}{2\cdot16^2}=\frac5{32}\approx0.156$；
我的 $=\frac2{16}+\frac{2^2}{16}=\frac38=0.375$。
**独立交叉检查**：`assumptions.md` 提到 $L_2(1)=3/4$；脚本算 $L_2(1)=1-(1-\frac12)^2=\frac34$ ✓，
说明我对 `notation.md` 里 $L_K$ 的读法与论文一致。

---

## 4. 未闭合的步骤 / 我不得不添加的假设

按严重程度排列。

### GAP-1（门槛条件不一致）[FAILED]

**具体不等式**：Step 8 的 $(\S)$，$P_\tau(n)=\frac{K^{2\tau}}{\tau!\,n^{\tau-c}}<1$。
**参数**：整数 $c\ge1$，$\tau=c+1$，$n=4K^{c+2}$（statement 的门槛）。
代入得 $P_\tau=\frac{K^{c}}{4(c+1)!}$，$<1$ 当且仅当 $K^c<4(c+1)!$：
$c=1$ 时需 $K<8$，$c=2$ 时需 $K\le4$，$c=3$ 时需 $K^3<96$ 即 $K\le4$。
在 $c\ge1$ 且 $K$ 大时，stated 的 $n\ge4K^{c+2}$ **不足以**让我的 union bound $<1$。
我能闭合的充分条件是 $n\ge4K^{2\tau}$（此时 $P_\tau\le\frac1{4\tau!}\le\frac14$），
它在 $c=0,\tau=1$ 时与 stated 条件**完全相同**（$4K^2$）。
**我没有找到更省的计数**：把 $\binom{K}{\tau}$ 换成任何我试过的更紧写法
（$\binom{K}{\tau}\binom{n-\tau}{K-\tau}/\binom nK$、按 disjoint block 取候选 $O^\ast$、
按元素而非 $\tau$-subset 做 union）都得到同阶的 $K^{2\tau}/n^{\tau-c}$，
指数 $2\tau$ 无法降到 $c+2$（$c>0$ 时 $2\tau=2\lceil c\rceil+2>c+2$）。
**保守处理**：我在本文件里用 $n\ge4K^{2\tau}$ 走完 Step 8/9，并明确标注
这与 statement 的 $n\ge4K^{c+2}$ 不同。若论文另有更省的隐藏引理，这是需要人类核对的第一处。

### GAP-2（$\varepsilon_n$ 第二项的 level 错位）[FAILED]

**具体项**：$\frac{K^{2\tau+2}}{(\tau+1)!\,n^{\tau+1-c}}$。
它逐字等于 level-$(\tau+1)$ 的 union bound
$n^c\binom{K}{\tau+1}(K/n)^{\tau+1}$ 的松弛（sympy 差为 $0$）。
但 Step 9 的值上界要求排除的是 level-$\tau$ 事件 $|S\cap O^\ast|\ge\tau$
（window 定义为 $|S\cap O^\ast|\le\tau-1$），其概率是
$\frac{K^{2\tau}}{\tau!\,n^{\tau-c}}$，比 displayed 项大 $\frac{(\tau+1)n}{K^2}$ 倍。
两种可能（我无法从 statement 区分）：(a) 论文的 window 实际定义为
$|S\cap O^\ast|\le\tau$（而不是 $\le\tau-1$），此时 level-$(\tau+1)$ 才是 bad event，
但那样 Step 6 的计数应变成 $K-\tau-1$ 项乘 $\eta$ 加 $1$，
给出 $\eta(K-\tau-1)+1$ 而不是 $\eta(K-\tau)+1$，与 $H$ 的公式冲突；
(b) displayed 的 $\varepsilon_n$ 里有 off-by-one。
**保守处理**：我采用 window $=\{|S\cap O^\ast|\le\tau-1\}$（因为它与 $H$ 的
$\eta(K-\tau)+1$ 自洽，见 Step 6），并报告我得到的是
$\varepsilon_n^{\text{(mine)}}=\frac Kn+\frac{K^{2\tau}}{\tau!\,n^{\tau-c}}$。
**因此：statement 里 as displayed 的 $\varepsilon_n$ 不从我的论证得出。**

### GAP-3（$\varepsilon_n$ 第一项 $K/n$ 来源不明）[CONJECTURE]

我能给的最好解释是 $\frac Kn=\Pr[\text{固定元素}\in O^\ast]$。
但我的 Step 11 里，"输出集合 $T$ 未被查询过"这件事已经被吸收进
$Q\to Q+1$ 的重新 union（代价是 $(\S)$ 乘 $(1+n^{-c})$，不是加 $K/n$）。
我推不出为什么恰是 $K/n$（而非 $K^2/n=\mathbb E|T\cap O^\ast|$ 的上界）。
未闭合。

### GAP-4（"error 恰好 $=\eta$" 的下界方向 + 劈分的 convention 依赖）[HAND-PROOF-UNREVIEWED]

Step 10 的 (i)（band 以 $\eta$ 成立）我能说清；(ii)（最小可行乘积**恰好**是 $\eta$，
不是更小）要求构造在某个 $(S,e,e')$ 上把 $(\ast)$ 用满，
这依赖我没有写出的显式 $f$（见 GAP-6）。
另外：劈分从句在 `definition1.md` 的 **convention B** 下成立（允许 $\eta_u<1$）；
在同文件 verbatim 的论文文本（$\eta_u,\eta_o\ge1$）下，只有 $\eta_u\in[1,\eta]$
的劈分可实现，"any prescribed split" 需要读成 convention B。这是一个量词依赖，
建议在定理里点明用的是哪一种 convention。

### GAP-5（$\delta(\theta)$、$\theta$、$a_\theta$、$\Psi$ 未定义）[无法检验]

statement 最后一句 "$K\delta(\theta)\to\tau-1/\theta$" 用到 $\delta(\cdot)$ 和 $\theta$，
`notation.md` 只把它们列为 "hardness-family parameters (Section~\ref{sec:hardness})"，
没有给公式；我的四个输入文件里没有定义。因此该渐近式我**无法检验**。
第 12 步给了一条一致性提示（$K(\eta-\bar\theta)=\eta\tau-1=\eta(\tau-1/\eta)$），
标 [CONJECTURE]。
**输入包缺失项**：$\delta(\theta)$、$a_\theta$、$\Psi$、$\theta$ 的定义，
以及 $\bar\theta$ 的独立定义（我是从 $H=L_K(\bar\theta)$ **反解**出
$\bar\theta=\frac{\eta(K-\tau)+1}{K}$ 的，这是自洽的读法，但不是从定义得到的）。

### GAP-6（显式硬族的存在性没有构造出来）[HAND-PROOF-UNREVIEWED]

Step 7 里"存在 monotone submodular $f$ 使 window 内最优值**恰好**
$1-(1-\beta)^K$、同时 $f(O^\ast)=1$" 我没有构造出来。
我试过的最自然的两个候选都不行，记录下来供人类判断：
1. **等分 coverage**：$\Omega$ 分成 $K$ 等份，$o_i$ 盖第 $i$ 份，每个 dummy 独立盖每份的
   $\beta$ 比例。此时 window 内握 $\tau-1$ 个 $o$ 加 $K-\tau+1$ 个 dummy 的值是
   $\frac{\tau-1}{K}+\frac{K-\tau+1}{K}\bigl(1-(1-\beta)^{K-\tau+1}\bigr)$，
   **不是** $1-(1-\beta)^K$ 的形状；而且在 $|S\cap O^\ast|=\tau-1$ 处
   $(\ast)$ 的比值是 $\frac1{\beta(K-\tau+1)}$，取等给
   $\beta=\frac1{\eta(K-\tau+1)}<\frac1{\eta(K-\tau)+1}$，
   即这个族比 statement **更强**（$H$ 更小），说明它不满足某条我漏掉的约束
   （多半是 window 边界 $j=\tau-1\to\tau$ 上 $\tilde f$ 的可拼接性）。
2. **纯 nested dummy**：dummy 逐个吃剩余的 $\beta$。此时全局 $(\dagger)$ 只给
   $1\le K\eta\beta$，即 $\beta\ge\frac1{\eta K}$，得到的是 $L_K(\eta)$ 而不是 $H$。
结论：$K-\tau$ 与 "+1" 的正确来源应该是 window **边界**上
$\tilde f$ 必须同时满足 window 内 oblivious 与 window 外 band 这两侧的拼接约束；
我在 Step 6 里用"$K-\tau$ 项乘 $\eta$ 加当前 $1$ 项"给出的计数与公式**完全吻合**，
但这个计数我只能作为 heuristic 交出，没有显式 $f$ 支撑。**这是本次推导最大的缺口。**

### 4.6 限定词的空洞性检验（CLAUDE.md 要求）

- **deterministic**：去掉后陈述改变。确定性是 Step 8 里"查询序列与 $O^\ast$ 无关"的唯一
  依据；随机化要走 Yao 并付 $\varepsilon_n$。**非空洞，必须保留。**
- **each on a set of size at most $K$**：去掉后 Step 8 第 2 点的 $\binom{|S|}{\tau}\le\binom K\tau$
  失效，一次 $|S|=n/2$ 的查询就能定位 $O^\ast$。**非空洞。**
- **$n\ge4K^{c+2}$**：去掉后 union bound 无法 $<1$（而且见 GAP-1，它在 $c>0$ 时本身就不够）。
  **非空洞但数值待核。**
- **$K>\tau$**：去掉后 $K-\tau\le0$，$\frac{K-1}{K-\tau}$ 无定义或为负，$\beta$ 可能 $>1$。
  **非空洞。**
- **$\eta>1$（严格）**：在 $\tau=1$ 时它就是 $\bar\theta\ge1$；$\eta=1$ 时
  $H_{K,1}(1)=1-(1-\frac1K)^K=L_K(1)$，公式仍有意义，所以"严格"这一条在 $\tau=1$ 时
  **接近空洞**（只排除一个端点）；在 $\tau\ge2$ 时它被更强的 $\eta\ge\frac{K-1}{K-\tau}>1$ 吞掉，
  **完全空洞，可删**（建议只写 $\eta\ge\max\{1,\frac{K-1}{K-\tau}\}$）。
- **adversarial tie breaking**：本定理里算法是任意确定性算法，不是 greedy，
  我的推导**没有用到**这条。它在 `assumptions.md` 里是全局约定，
  但对 thm:hardness 而言看不出作用点。**疑似空洞，建议在本定理处说明它是否被用到。**
- **"smallest admissible error factors ... exactly $\eta$"**：把 "exactly" 换成 "at most"，
  陈述变弱（"at most $\eta$" 的 instance 可能实际 error 远小于 $\eta$，
  那样 hardness 就不是在 error level $\eta$ 上的）。**非空洞，且是 GAP-4 的来源。**

---

## 5. 读过的文件

只读了以下四个（无其他文件、无 web、无 git、无 grep）：

1. `/home/user/sub-modular-optimization/results/V11/inputs/definition1.md`
2. `/home/user/sub-modular-optimization/results/V11/inputs/assumptions.md`
3. `/home/user/sub-modular-optimization/results/V11/inputs/notation.md`
4. `/home/user/sub-modular-optimization/results/V11/inputs/statement_hardness.md`

另写入（不算读取）：
- `/home/user/sub-modular-optimization/results/V11/route2/q7_verify_hardness.py`（本文件的 oracle 脚本）
- `/home/user/sub-modular-optimization/results/V11/route2/hardness.md`（本文件）

复跑方式：`cd /home/user/sub-modular-optimization/results/V11/route2 && timeout 600 python3 q7_verify_hardness.py`。
脚本全部用 `sympy.Rational` / `fractions.Fraction`，float 只出现在打印里。

## 6. 状态汇总表

| 断言 | 状态 |
|---|---|
| $H_{K,\tau}(\eta)=L_K(\bar\theta)$，$\bar\theta=\frac{\eta(K-\tau)+1}{K}$ | [VERIFIED-SYMBOLIC] |
| $\bar\theta\ge1\iff\eta\ge\frac{K-1}{K-\tau}$（$K>\tau$） | [VERIFIED-SYMBOLIC] |
| $H_{K,\tau}(\eta)\ge L_K(\eta)$（一致性） | [VERIFIED-EXHAUSTIVE]（有理网格 $K\le12$） |
| $H_{K,\tau}(\eta)\to1-e^{-1/\eta}$ | [VERIFIED-SYMBOLIC] |
| displayed $\varepsilon_n$ 第二项 $=$ level-$(\tau+1)$ union bound | [VERIFIED-SYMBOLIC] |
| $K$ 步几何衰减，ratio $1-\beta$，$\beta=\frac1{\eta(K-\tau)+1}$ | [HAND-PROOF-UNREVIEWED] |
| $\eta(K-\tau)+1$ 的组合计数（$K-\tau$ 项 $\times\eta$ + 当前 $1$ 项） | [HAND-PROOF-UNREVIEWED] |
| union bound 给出 $n\ge4K^{2\tau}$ 充分 | [HAND-PROOF-UNREVIEWED] |
| statement 的 $n\ge4K^{c+2}$ 对 $c\ge1$、$K$ 大时充分 | [FAILED]（反例参数见 GAP-1） |
| displayed $\varepsilon_n$ 从本推导得出 | [FAILED]（level 错位，见 GAP-2） |
| 任意劈分 $\eta_u\eta_o=\eta$ 由 rescaling 实现（convention B） | [HAND-PROOF-UNREVIEWED]（推导完整，依赖 convention B） |
| 显式硬族 $f$ 的存在性 | [FAILED]（未构造，见 GAP-6） |
| $K\delta(\theta)\to\tau-1/\theta$ | 无法检验（GAP-5，定义缺失） |

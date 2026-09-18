# ROUTE-TWO 盲证：thm:ceiling（deterministic ceiling, all ground-set sizes）

本文件是对 `results/V11/inputs/statement_ceiling.md` 中所述命题的独立重新推导。
只使用 `definition1.md` / `assumptions.md` / `notation.md` 三个输入文件里的定义与约定，
以及标准数学。没有查阅仓库中任何其它文件，没有使用 web search，没有运行 git。

所有可复现脚本在本目录下：

| 脚本 | 作用 | 状态标签 |
|---|---|---|
| `verify_ceiling.py` | 主验证（符号恒等式 + 两族紧实例的有理精确检验 + 400 个随机 coverage 实例上逐条检验证明的每一步） | `[VERIFIED-SYMBOLIC]` `[VERIFIED-EXHAUSTIVE]` |
| `lp_perinstance.py` | 逐实例界的最坏值 LP（探索用，浮点仅用于打印） | `[VERIFIED-LP]` |
| `lp_families.py` | 判定哪几族约束是必需的（用于定位证明骨架） | `[VERIFIED-LP]` |
| `lp_dual.py` | 取 LP 对偶乘子，反推证明结构（探索用） | 探索脚本 |
| `check_candidate.py` | 一个反例候选：它满足所有"成对"必要条件却无相容 predictor，用来说明证明不能只用成对不等式 | `[VERIFIED-LP]` |

---

## 1. 陈述复述（连同全部 quantifier）

### 1.1 固定的对象与域

- ground set $N$，$|N|=n$；monotone submodular $f:2^N\to\mathbb R_{\ge0}$，$f(\emptyset)=0$；
  cardinality budget $K$。取值域：陈述里写 $2\le K\le n$（`assumptions.md` 的全局约定是 $1\le K\le n$；
  见 §5 关于 $K\ge2$ 是否必要的检验）。
- algorithm 不能 evaluate $f$，只能 query $\tilde f:2^N\to\mathbb R$，$\tilde f(\emptyset)=0$。
- $d_e(S)=f(S\cup\{e\})-f(S)$，$\tilde d_e(S)=\tilde f(S\cup\{e\})-\tilde f(S)$。
- prediction error（Definition 1）：$\forall S\subseteq N,\ \forall e\notin S$，
  $d_e(S)/\eta_u\le\tilde d_e(S)\le\eta_o\,d_e(S)$；scalar error $\eta=\eta_u\eta_o$。
  本陈述取 $\eta_u,\eta_o\ge1$，故 $\eta\ge1$。Definition 1 同时强制
  $d_e(S)=0\Leftrightarrow\tilde d_e(S)=0$，且所有 predicted gain 非负（于是 $\tilde f$ monotone）。
- $O^\ast$：一个 optimal $K$-set，$F^{\mathrm{OPT}}=f(O^\ast)$。approximation ratio 约定
  $\alpha\in(0,1]$，$F^{\mathrm{ALG}}\ge\alpha F^{\mathrm{OPT}}$。
- 若 $f(O^\ast)=0$，按 `assumptions.md`，所有 ratio 陈述平凡成立。

### 1.2 上界方向（ceiling）

> 对**每一个** deterministic algorithm $\mathcal A$（对 $\tilde f$ 有 **arbitrary query access**，
> 即 query 数目与形式都不受限；输出 $T$ 满足 $|T|\le K$），
> 以及**每一对** $\eta_u,\eta_o\ge1$，
> **存在**一对 $(f,\tilde f)$，其 error **恰好**是 $(\eta_u,\eta_o)$（两侧都取到等号，不只是"至多"），
> 使得 $\mathcal A$ 在该实例上的输出 $T$ 满足
> $$f(T)\;\le\;C^\ast_{n,K}(\eta)\,f(O^\ast),\qquad
>   C^\ast_{n,K}(\eta)=\frac{K}{K+(\eta-1)\min\{K,\,n-K\}} .$$

量词顺序是 $\forall\mathcal A\ \forall(\eta_u,\eta_o)\ \exists(f,\tilde f)$：实例可以依赖算法，
这正是 deterministic 这个限定词的落点（见 §4）。

### 1.3 下界方向（attainment，逐实例形式）

> 设 $S$ 是在**全部** $K$-subsets 上 maximize $\tilde f$ 的集合（即 exhaustive search over
> predicted values，query size $=\binom{n}{K}$，$|S|=K$）。
> 则**在每一个实例上**、对**每一个** optimal $K$-set $O^\ast$、以及**每一个** maximizer $S$
> （即 tie 以对抗方式打破也成立）：
> $$f(S)\;\ge\;\frac{K}{K+(\eta-1)\,|O^\ast\setminus S|}\,f(O^\ast)\;\ge\;C^\ast_{n,K}(\eta)\,f(O^\ast).$$

两侧合起来说明 $C^\ast_{n,K}(\eta)$ 是 deterministic、任意 query 数下的**精确** ceiling，
且对每个 $n$ 都由 exhaustive search 达到。

### 1.4 两个分支的闭式

$\min\{K,n-K\}=n-K$ 当且仅当 $n\le 2K$，此时
$\frac{K}{K+(\eta-1)(n-K)}=\frac{K}{(2K-n)+(n-K)\eta}$；
$\min\{K,n-K\}=K$ 当 $n\ge2K$，此时 $\frac{K}{K+(\eta-1)K}=1/\eta$。
两式在 $n=2K$ 处相等（都等于 $1/\eta$）。`[VERIFIED-SYMBOLIC]`（`verify_ceiling.py` 段 A：
sympy `simplify` 得 0）

---

## 2. 完整推导

记号：$C=S\cap O^\ast$，$j=|O^\ast\setminus S|$，$\Delta_s=d_s(S\setminus\{s\})$（$s\in S$），
$m=\min_{s\in S}\Delta_s$，$\theta=1-1/\eta\in[0,1)$。

### 2.0 预备引理

**L0（chain bound）.** 对 $W\subseteq A$，沿任意一条从 $W$ 到 $A$ 的 chain 逐项套用
Definition 1，得 $\frac1{\eta_u}\bigl(f(A)-f(W)\bigr)\le\tilde f(A)-\tilde f(W)\le\eta_o\bigl(f(A)-f(W)\bigr)$。
取 $W=\emptyset$ 得 $f(A)/\eta_u\le\tilde f(A)\le\eta_o f(A)$。
依据：Definition 1；$\tilde f$ 是良定义的 set function（各 chain 之和一致）。`[HAND-PROOF-UNREVIEWED]`

**L1（归一化）.** 令 $\hat f=\tilde f/\eta_o$。则 $\hat d_e(A)=\tilde d_e(A)/\eta_o\in[d_e(A)/\eta,\ d_e(A)]$，
且 $\hat f$ 与 $\tilde f$ 在 $K$-subsets 上的 argmax 完全相同（$\eta_o>0$）。
故在 §2.2 的 converse 里可以无损地假设 $\eta_u=\eta,\ \eta_o=1$，即
$$d_e(A)/\eta\ \le\ \tilde d_e(A)\ \le\ d_e(A).$$
依据：Definition 1 convention B 的 scaling 一段（$(\eta_u,\eta_o)\mapsto(c\eta_u,\eta_o/c)$，$\eta$ 不变）。
`[HAND-PROOF-UNREVIEWED]`

**L2（剩余函数 $r$）.** 在 L1 的归一化下令 $r=f-\tilde f$。则 $r(\emptyset)=0$，且对一切 $A,e\notin A$：
$$0\ \le\ r(A\cup\{e\})-r(A)=d_e(A)-\tilde d_e(A)\ \le\ \Bigl(1-\tfrac1\eta\Bigr)d_e(A)=\theta\,d_e(A).$$
左端非负说明 $r$ 是 monotone set function（$W\subseteq A\Rightarrow r(W)\le r(A)$），
右端沿 chain 相加给出 $r(A)-r(W)\le\theta\bigl(f(A)-f(W)\bigr)$。
依据：L1 + Definition 1 的两侧。`[HAND-PROOF-UNREVIEWED]`

### 2.1 上界方向：对每个 deterministic algorithm 的 adversary 实例

**U1（构造）.** 置 $h=\min\{K,\,n-K\}$。predictor 取**与实例无关**的
$$\tilde f(A)=|A| \qquad(\text{于是 }\tilde d_e(A)=1\ \text{恒成立},\ \tilde f(\emptyset)=0).$$
对任一 $h$-subset $H\subseteq N$ 定义 modular 目标
$$f_H(A)=\eta_u\,|A\cap H|+\tfrac1{\eta_o}\,|A\setminus H| .$$
$f_H$ 是 modular、monotone、submodular，$f_H(\emptyset)=0$。依据：modular 函数的定义与权重非负
（$\eta_u\ge1>0$，$1/\eta_o>0$）。

**U2（band 恰好是 $(\eta_u,\eta_o)$）.** $d_e(A)=\eta_u$（$e\in H$）或 $1/\eta_o$（$e\notin H$），$\tilde d_e(A)=1$。
- $e\in H$：$d_e/\eta_u=1=\tilde d_e$（下侧取等，$\eta_u$ 被取到）且 $\tilde d_e=1\le\eta_o\eta_u=\eta$（上侧成立）。
- $e\notin H$：$\tilde d_e=1=\eta_o\cdot\frac1{\eta_o}$（上侧取等，$\eta_o$ 被取到）且 $d_e/\eta_u=\frac1{\eta}\le1$（下侧成立）。

故只要 $1\le h\le n-1$，error 就**恰好**是 $(\eta_u,\eta_o)$。依据：U1 + Definition 1。
`[VERIFIED-EXHAUSTIVE]`（`verify_ceiling.py` 段 B 对 $2\le n\le 8$、$1\le K\le n$、四组
$(\eta_u,\eta_o)$ 用 `Fraction` 逐个 marginal 精确检验 band 可行且两侧都取到）

**U3（determinism 的落点）.** $\tilde f$ 与 $H$ 无关，因此 $\mathcal A$ 的整条 query transcript
以及输出 $T$ 对族 $\{(f_H,\tilde f)\}_H$ 中的每个成员完全相同。于是 adversary 可以**先**读出 $T$、
**后**挑 $H$。依据：$\mathcal A$ deterministic，且它只能 query $\tilde f$（`assumptions.md`）。

**U4（藏开 $T$）.** $|T|\le K$ 给出 $|N\setminus T|\ge n-K\ge h$，故存在 $H\subseteq N\setminus T$，$|H|=h$。
取这个 $H$，则 $T\cap H=\emptyset$，于是 $f_H(T)=|T|/\eta_o\le K/\eta_o$。依据：U3 + $h=\min\{K,n-K\}\le n-K$。

**U5（OPT 值）.** $f_H$ 是 modular，权重只有 $\eta_u$（$h$ 个）与 $1/\eta_o$（$n-h$ 个），且
$\eta_u\ge1/\eta_o$（等价于 $\eta\ge1$）。又 $h\le K\le n$，故 optimal $K$-set 取全部 $H$ 加上
$K-h$ 个轻元素：$f_H(O^\ast)=h\eta_u+(K-h)/\eta_o$。依据：U1 + $\eta\ge1$。

**U6（比值）.** 由 U4、U5：
$$\frac{f_H(T)}{f_H(O^\ast)}\ \le\ \frac{K/\eta_o}{h\eta_u+(K-h)/\eta_o}
=\frac{K}{h\,\eta_u\eta_o+K-h}=\frac{K}{K+(\eta-1)h}=C^\ast_{n,K}(\eta).$$
依据：U4、U5、$\eta=\eta_u\eta_o$。`[VERIFIED-SYMBOLIC]`（段 A 的 A3）+
`[VERIFIED-EXHAUSTIVE]`（段 B：上式在整张网格上按有理数逐格取等）

**U7（边界情形 $n=K$）.** 此时 $h=0$，$C^\ast=1$，$O^\ast=N$，任何 $|T|\le K$ 都有 $f(T)\le f(N)=f(O^\ast)$，
结论平凡成立；为满足"error 恰好 $(\eta_u,\eta_o)$"，取 $H$ 为任意单元素（$U2$ 的两侧仍都取到，因为
$1\le1\le n-1$ 需要 $n\ge2$，而 $n=K\ge2$）。依据：monotonicity of $f$ + U2。

**小结 I.** 对每个 deterministic $\mathcal A$、每对 $\eta_u,\eta_o\ge1$，存在 error 恰为
$(\eta_u,\eta_o)$ 的 $(f,\tilde f)$ 使 $f(T)\le C^\ast_{n,K}(\eta)f(O^\ast)$。
`[HAND-PROOF-UNREVIEWED]`（构造本身 `[VERIFIED-EXHAUSTIVE]`）

### 2.2 下界方向：exhaustive search 的逐实例保证

设 $S$ 是 $\tilde f$ 在全部 $K$-subsets 上的一个 maximizer（$|S|=K$），$O^\ast$ 是任一 $K$-set（optimality
在下面**没有被用到**，见 §5 的量词检验），$j=|O^\ast\setminus S|$。按 L1 归一化，$\theta=1-1/\eta$，$r=f-\tilde f$ 如 L2。

**C1（主不等式 J）.**
$$f(O^\ast)-f(S)\ \le\ \theta\,\bigl[f(S\cup O^\ast)-f(S)\bigr].$$
推导（三步，每步注明依据）：
1. $|O^\ast|=K$，故 $O^\ast$ 是竞争者，$\tilde f(S)\ge\tilde f(O^\ast)$，即
   $f(S)-r(S)\ge f(O^\ast)-r(O^\ast)$，即 $f(O^\ast)-f(S)\le r(O^\ast)-r(S)$。
   依据：$S$ 的 maximality。
2. $O^\ast\subseteq S\cup O^\ast$ 且 $r$ monotone（L2 左端），故 $r(O^\ast)\le r(S\cup O^\ast)$。
3. 沿 $S\to S\cup O^\ast$ 的 chain 用 L2 右端：$r(S\cup O^\ast)-r(S)\le\theta[f(S\cup O^\ast)-f(S)]$。

串起来即得 (J)。注意这一步**只**用到 $\tilde f(S)\ge\tilde f(O^\ast)$ 这一条 maximality，
以及 $r$ 的单调性（即 Definition 1 的上侧）与 band 的下侧。
`[HAND-PROOF-UNREVIEWED]` + `[VERIFIED-EXHAUSTIVE]`（段 D 在 400 个随机 coverage 实例上逐条核对 (J)）

> 备注：只用"成对"的推论（即对每个 $K$-set $A$ 分别得到
> $f(A)\le f(A\cap S)+\eta[f(S)-f(A\cap S)]$）**不足以**得到本定理；
> `check_candidate.py` 给出一个 $n=4,K=3,\eta=2$ 的 monotone submodular $f$，
> 它满足全部成对推论、$O^\ast$ 也确实 optimal、比值 $5/7<3/4$，但不存在与之相容的 $\tilde f$
> （LP infeasible）。(J) 之所以更强，是因为它把 $r(S)$ 这一个公共量同时用在两个方向上。
> `[VERIFIED-LP]`

**C2（submodular 展开）.** 设 $O^\ast\setminus S=\{o_1,\dots,o_j\}$，则
$$f(S\cup O^\ast)-f(S)=\sum_{i=1}^{j}d_{o_i}\bigl(S\cup\{o_1,\dots,o_{i-1}\}\bigr)\ \le\ \sum_{i=1}^{j}d_{o_i}(S).$$
依据：telescoping + submodularity（base set 变大时 marginal 不增）。

**C3（swap 不等式）.** 对每个 $s\in S$ 与每个 $o\notin S$：
$$d_o(S)\ \le\ d_o(S\setminus\{s\})\ \le\ \eta\,\Delta_s .$$
推导：$S\setminus\{s\}\cup\{o\}$ 是 $K$-set，故 $\tilde f(S)\ge\tilde f(S\setminus\{s\}\cup\{o\})$，
两边减去 $\tilde f(S\setminus\{s\})$ 得 $\tilde d_s(S\setminus\{s\})\ge\tilde d_o(S\setminus\{s\})$；
再用归一化 band 的两侧：$\Delta_s\ge\tilde d_s(S\setminus\{s\})\ge\tilde d_o(S\setminus\{s\})\ge d_o(S\setminus\{s\})/\eta$。
第一个 $\le$ 是 submodularity（$S\setminus\{s\}\subseteq S$）。
依据：$S$ 的 maximality（single swap）+ Definition 1 + submodularity。
`[HAND-PROOF-UNREVIEWED]` + `[VERIFIED-EXHAUSTIVE]`（段 D）

**C4（$m\le f(S)/K$）.** 把 $S=\{s_1,\dots,s_K\}$ 排序，$S_i=\{s_1,\dots,s_i\}$，则
$S_{i-1}\subseteq S\setminus\{s_i\}$，由 submodularity $\Delta_{s_i}\le d_{s_i}(S_{i-1})$，于是
$$\sum_{s\in S}\Delta_s\ \le\ \sum_{i=1}^{K}d_{s_i}(S_{i-1})=f(S)-f(\emptyset)=f(S),$$
从而 $m=\min_s\Delta_s\le f(S)/K$。依据：submodularity + $f(\emptyset)=0$。
`[HAND-PROOF-UNREVIEWED]` + `[VERIFIED-EXHAUSTIVE]`（段 D）

**C5（合并）.** 由 C3（对所有 $s$ 取最紧的一个）得 $d_o(S)\le\eta m$；代入 C2：
$$f(S\cup O^\ast)-f(S)\ \le\ j\,\eta\,m\ \overset{\text{C4}}{\le}\ \frac{j\,\eta}{K}\,f(S).$$
代入 (J)，并用 $\theta\eta=\eta-1$：
$$f(O^\ast)-f(S)\ \le\ \theta\cdot\frac{j\eta}{K}f(S)=\frac{(\eta-1)j}{K}\,f(S),$$
即
$$f(O^\ast)\ \le\ \frac{K+(\eta-1)j}{K}\,f(S)
\qquad\Longleftrightarrow\qquad
f(S)\ \ge\ \frac{K}{K+(\eta-1)\,|O^\ast\setminus S|}\,f(O^\ast). \tag{$\ast$}$$
依据：C1、C2、C3、C4。`[HAND-PROOF-UNREVIEWED]` + `[VERIFIED-EXHAUSTIVE]`（段 D：
400 个随机 coverage 实例，对**每一个** $\tilde f$-maximizer $S$ 与**每一个** optimal $O^\ast$ 都成立）
+ `[VERIFIED-LP]`（`lp_perinstance.py`：在 $n\in\{3,4,5\}$、$K\in\{2,3\}$、$\eta\in\{3/2,2,3\}$、
$0\le j\le\min\{K,n-K\}$ 的每一格上，最坏值 LP 的最优值与 $(\ast)$ 右端**相等**，即 $(\ast)$ 不可改进）

**C6（从逐实例形式到 $C^\ast_{n,K}$）.** $O^\ast\setminus S\subseteq N\setminus S$ 且 $|N\setminus S|=n-K$，
又 $|O^\ast\setminus S|\le|O^\ast|=K$，故
$$j\ \le\ \min\{K,\ n-K\}.$$
由于 $\eta\ge1$，$x\mapsto\frac{K}{K+(\eta-1)x}$ 关于 $x$ 不增，于是 $(\ast)$ 的右端
$\ge\frac{K}{K+(\eta-1)\min\{K,n-K\}}=C^\ast_{n,K}(\eta)$。
这也是 $n$ 唯一进入结论的地方。依据：集合计数 + 单调性。

**C7（紧性，说明 $C^\ast$ 不可再降）.** 对每个 $0\le j\le\min\{K,n-K\}$：取 modular $f$，
$S$ 的 $K$ 个元素权重 $1$，另取 $j$ 个元素权重 $\eta$，其余权重 $0$；取
$\tilde d$ 为：$S$ 的元素走 band 上侧（$\tilde w=\eta_o$），那 $j$ 个重元素走 band 下侧
（$\tilde w=\eta/\eta_u=\eta_o$）。于是所有元素的 predicted weight 相同，$S$ 是一个 maximizer
（tie 按对抗方式打破时合法），$O^\ast$ 由 $j$ 个重元素加 $K-j$ 个 $S$ 中元素组成，
$$\frac{f(S)}{f(O^\ast)}=\frac{K}{j\eta+(K-j)}=\frac{K}{K+(\eta-1)j}.$$
取 $j=\min\{K,n-K\}$ 即得 $C^\ast_{n,K}$。`[VERIFIED-EXHAUSTIVE]`（段 C：$2\le n\le8$，
$2\le K\le n$，$\eta\in\{3/2,2,3\}$，全部 $j$，有理精确，且 $S$ 的 maximality 与 $O^\ast$ 的 optimality
都用穷举核对）
若要求 maximizer 唯一，把 $S$ 的权重改成 $1+\epsilon$ 即可，比值随 $\epsilon\downarrow0$ 趋于同一极限；
即在唯一 maximizer 的意义下界是"渐近紧"，在对抗 tie-breaking 下是"精确紧"。

**小结 II.** exhaustive search over predicted values 在每个实例上给出 $(\ast)$，从而给出
$C^\ast_{n,K}(\eta)$；与小结 I 合起来，$C^\ast_{n,K}(\eta)$ 是 deterministic、query 数不受限时的精确 ceiling。

---

## 3. 数值走查

### 3.1 $K=3$，$\eta=3/2$（取 $\eta_u=3/2,\ \eta_o=1$）

| $n$ | $h=\min\{K,n-K\}$ | $C^\ast_{n,3}(3/2)$ | 分支 |
|---|---|---|---|
| 3 | 0 | $3/3=1$ | $n=K$，平凡 |
| 4 | 1 | $\dfrac{3}{3+\frac12\cdot1}=\dfrac{6}{7}\approx0.857$ | $K\le n<2K$：$\frac{3}{(6-4)+1\cdot\frac32}=\frac{3}{7/2}$ |
| 5 | 2 | $\dfrac{3}{3+\frac12\cdot2}=\dfrac34$ | $K\le n<2K$：$\frac{3}{(6-5)+2\cdot\frac32}=\frac34$ |
| 6 | 3 | $\dfrac{3}{3+\frac12\cdot3}=\dfrac23=1/\eta$ | $n=2K$，两支相等 |
| $\ge6$ | 3 | $2/3$ | $n\ge2K$ |

**$n=6$ 的 adversary 实例（U1）**：$\tilde f(A)=|A|$；算法读完 $\tilde f$ 后输出某个 $T$，$|T|\le3$；
adversary 取 $H\subseteq N\setminus T$，$|H|=3$，权重 $3/2$，其余三个元素权重 $1$。
则 $f(T)=|T|\cdot1\le3$，$f(O^\ast)=3\cdot\frac32=\frac92$，比值 $\le\frac{3}{9/2}=\frac23=1/\eta$。
band：重元素 $d/\eta_u=\frac{3/2}{3/2}=1=\tilde d$（下侧取等），轻元素 $\eta_o d=1=\tilde d$（上侧取等），
error 恰好 $(3/2,1)$。

**$n=4$ 的 adversary 实例**：$h=1$，一个重元素权重 $3/2$，三个轻元素权重 $1$；$T$ 必须是三个轻元素
（adversary 把重元素藏在 $T$ 外），$f(T)=3$，$f(O^\ast)=\frac32+2=\frac72$，比值 $\frac{3}{7/2}=\frac67$。

**逐实例形式（$n=5$，$K=3$）**：$j=|O^\ast\setminus S|$ 只能取 $0,1,2$：
$j=0$ 给 $1$，$j=1$ 给 $\frac{3}{3.5}=\frac67$，$j=2$ 给 $\frac{3}{4}$。
对应的紧实例（C7，$j=2$）：$S$ 的三个元素权重 $1$，另两个元素权重 $\frac32$，
$\tilde w$ 全部等于 $1$，$S$ 是（对抗 tie-breaking 下的）maximizer，
$O^\ast=\{$两个重元素$\}\cup\{S$ 中任一元素$\}$，$f(O^\ast)=3+1=4$，$f(S)=3$，比值 $3/4$。

**证明链在该实例上的数值**：$\Delta_s=1$ 对所有 $s\in S$，$m=1=f(S)/K=3/3$（C4 取等）；
$d_o(S)=\frac32=\eta m$（C3 取等）；$f(S\cup O^\ast)-f(S)=2\cdot\frac32=3=j\eta m$（C2 取等）；
$\theta=1-\frac23=\frac13$，(J) 右端 $=\frac13\cdot3=1=f(O^\ast)-f(S)$（C1 取等）。
四步同时取等，这解释了为什么界是精确的。

### 3.2 $K=2$（最小可取 budget）

任务描述里"$K=2$ 用于 ProbeLottery item"这一条在本陈述里无对应项：thm:ceiling 的陈述中
没有 ProbeLottery（也没有任何 randomized subroutine）。按保守处理，这里仍给出 $K=2$ 的走查。

$K=2$、$\eta=3/2$：$n=2$ 时 $h=0$，$C^\ast=1$；$n=3$ 时 $h=1$，$C^\ast=\frac{2}{2+\frac12}=\frac45$；
$n\ge4$ 时 $h=2$，$C^\ast=\frac{2}{2+1}=\frac23=1/\eta$。
$n=4$ 的 adversary 实例：两个重元素（权重 $3/2$）藏在 $T$ 外，两个轻元素（权重 $1$）；
$f(T)=2$，$f(O^\ast)=3$，比值 $2/3$。
$K=2$、$\eta=2$、$n=3$：$C^\ast=\frac{2}{2+1}=\frac23$；紧实例为权重 $(1,1,2)$、$\tilde w\equiv1$，
$S=\{$两个轻元素$\}$，$f(S)=2$，$f(O^\ast)=2+1=3$。

---

## 4. randomized algorithm 会变成什么，以及 fixed random string 是不是陈述的一部分

**(a) 陈述里没有 random string。** 1.2 的量词是"对每个 deterministic algorithm"，
实例在算法之后被选出（U3）。陈述中不含随机性，也不含"固定随机串"这一前置量词。

**(b) 把 deterministic 换成 randomized 会怎样。** 设 $\mathcal A$ 用随机串 $R$。对**每个固定的** $R$，
$\mathcal A_R$ 是 deterministic，于是 §2.1 给出实例 $(f_{H(R)},\tilde f)$ 满足上界。
但 $H$ 依赖 $R$，所以只能得到"先固定 $R$、再选实例"的版本，也就是把定理逐串应用一遍，
并**不**蕴涵"存在一个实例使得对随机串取期望后仍不超过 $C^\ast$"。因此，
若要在陈述中加"fixed random string"，它必须写成量词顺序 $\forall R\ \exists(f,\tilde f)$，
这与把定理应用到 $\mathcal A_R$ 是同一件事，不是更强的结论。

**(c) 对同一族做 Yao 会得到什么。** U1 的族里所有实例共享同一个 $\tilde f$，
所以算法的输出分布与 $H$ 独立。取 $H$ 在全部 $h$-subsets 上均匀：对任意固定的 $|T|\le K$，
$$\mathbb E_H\bigl[f_H(T)\bigr]=|T|\Bigl(\tfrac hn\eta_u+\bigl(1-\tfrac hn\bigr)\tfrac1{\eta_o}\Bigr)
\ \le\ K\Bigl(\tfrac hn\eta_u+\tfrac{n-h}{n}\tfrac1{\eta_o}\Bigr),$$
（关于 $|T|$ 单调不减，因为 $\eta_u\ge1/\eta_o$），于是存在某个 $H$ 使得
$$\frac{\mathbb E\bigl[f_H(T)\bigr]}{f_H(O^\ast)}\ \le\
\frac{K\bigl(n+(\eta-1)h\bigr)}{n\bigl(K+(\eta-1)h\bigr)}
= C^\ast_{n,K}(\eta)\cdot\frac{n+(\eta-1)h}{n},\qquad h=\min\{K,n-K\}.$$
`[VERIFIED-SYMBOLIC]`（段 E）
放大因子 $\frac{n+(\eta-1)h}{n}>1$（只要 $\eta>1,h\ge1$），所以**这一族给不出 $C^\ast$ 级别的
randomized ceiling**。具体地，$n\ge2K$ 时该值为 $\frac1\eta+\frac{K(\eta-1)}{n\eta}$，
在 $K$ 固定、$n\to\infty$ 时才趋于 $1/\eta$。
直观原因：$\tilde f$ 完全无信息时，均匀随机的 $K$-set 平均能抓到 $\frac hn$ 比例的重元素，
而 deterministic 算法被 adversary 一个不剩地躲开。

**(d) 结论（用于量词审计）.** "deterministic" 是**非空洞**的限定词：
去掉它，1.2 的结论在上面这一族上不再成立（差一个 $\frac{n+(\eta-1)h}{n}$ 因子）。
至于真正的 randomized ceiling 是否仍等于 $C^\ast_{n,K}$，本次盲证的输入文件不足以判定，
记为 GAP（§5）。下界方向（§2.2）不受影响：exhaustive search 本身是 deterministic，
所以 $C^\ast$ 对 randomized 算法类同样是可达的。

---

## 5. 未能闭合的步骤、额外假设与量词检验

**(G1) randomized ceiling 的精确值：未闭合。** §4(c) 只给出 $C^\ast\cdot\frac{n+(\eta-1)h}{n}$
这一个 randomized 上界（来自 U1 那一族）。是否存在另一族把 randomized ceiling 压回 $C^\ast$，
或者 randomized 算法是否确实能超过 $C^\ast$，本文件不作判断。`[CONJECTURE]` 不下；标 GAP。

**(G2) "error 恰好 $(\eta_u,\eta_o)$" 在 $n=K$ 时。** $h=0$ 时 U1 的重元素集为空，两侧不能同时取到，
需要像 U7 那样换一个实例（该情形下结论本身平凡）。这是陈述里 $\min\{K,n-K\}$ 在 $n=K$ 退化为 $0$
的直接后果，不是证明缺口，但正文若写"该实例即为所需"需要加一句 $n>K$ 的限定。

**(G3) 添加的约定（保守选择，已记录理由）。**
1. 把"arbitrary query access"理解为：算法的输出是 $\tilde f$ 这个**函数**的确定性函数
   （value query、adaptive query、甚至读出整张表都允许）。这是最强的读法，使 U3 成立；
   任何更弱的 query model 都是它的子类，结论照样成立。
2. 把"output of size at most $K$"理解为 $|T|\le K$ 且 $T\subseteq N$。
3. `definition1.md` 的 verbatim 版把两个因子都 floor 在 $1$，convention B 允许 $\eta_u,\eta_o>0$。
   本陈述写 $\eta_u,\eta_o\ge1$，U1/U2 只用到 $\eta_u>0,\eta_o>0,\eta\ge1$，两种读法都覆盖。
4. §2.2 用 L1 先把 band 归一化成 $[d/\eta,\,d]$。合法性由 convention B 的 scaling 一段保证。

**(G4) 量词空洞性检验（CLAUDE.md 第"空洞性检验"节）。**

| 限定词 | 去掉/取反后会怎样 | 结论 |
|---|---|---|
| deterministic | 见 §4：同一族只给出 $C^\ast\cdot\frac{n+(\eta-1)h}{n}$，结论变假 | 必须保留，且正文需一句话说明变在哪 |
| arbitrary query access | 换成受限 query 只会让 ceiling 更低（上界方向更容易），但会让"attains the ceiling"一句失真（attainment 用了 $\binom nK$ 次 query） | 保留；建议在 attainment 处点明 query size $\binom nK$ |
| output of size at most $K$ | 允许 $|T|>K$ 时取 $T=N$ 即得 $f(T)\ge f(O^\ast)$，结论变假 | 必须保留 |
| error **exactly** $(\eta_u,\eta_o)$ | 换成"at most"会让上界变弱（adversary 可用更好的 predictor 逃避） | 保留；U2 已验证可实现 |
| $2\le K$ | $K=1$ 时上界构造与 converse 推导逐字成立（$h=\min\{1,n-1\}$；$n\ge2$ 时 $C^\ast_{n,1}=1/\eta$） `[VERIFIED-EXHAUSTIVE]`（本目录 K=1 网格检验） | $K\ge2$ 对**本命题**不是必需的；若保留应说明是为了与主文其它结果对齐 |
| "for every optimal $K$-set $O^\ast$" 中的 optimal | §2.2 的推导从未使用 $O^\ast$ 的 optimality：$(\ast)$ 对**任意** $K$-set $O^\ast$ 成立 `[VERIFIED-LP]`（`lp_families.py`：把 $f$-optimality 约束整族删掉，LP 最优值不变） | optimality 只在把 $f(O^\ast)$ 读作 $F^{\mathrm{OPT}}$ 时需要；$(\ast)$ 本身可以陈述得更强 |
| tie breaking（$S$ 是"一个" maximizer） | $(\ast)$ 对每一个 maximizer 都成立，对抗 tie-breaking 无影响 `[VERIFIED-EXHAUSTIVE]`（段 D 遍历全部 maximizer） | 保留"a set $S$ maximizing"即可 |
| $\min\{K,n-K\}$ | 这是 $j\le\min\{K,n-K\}$（C6）的直接来源；换成 $K$ 会在 $n<2K$ 时给出错误（过小）的 ceiling | 必需 |

**(G5) 需要人类判断的一点。** §2.2 的 (J) 用的是"$\tilde f(S)\ge\tilde f(O^\ast)$ 这一条 + $r$ 的单调性"，
而 C3 另外用到 single-swap maximality。`lp_families.py` 显示：只保留
{single swaps} $\cup$ {$O^\ast$} 这两族 $\tilde f$-maximality 约束，LP 最优值就已经等于 $(\ast)$；
只保留其中一族则不够（例如 $n=6,K=3,j=3,\eta=2$：只用 single swaps 得 $0.4286<0.5$）。
这说明正文若想把 attainment 推广到"只做 single swap 的 local search"，需要另行处理，
`[FAILED]` 的具体位置是：单靠 single-swap 族，$n=6,K=3,\eta=2,j=3$ 的最坏值为 $3/7$ 而非 $1/2$。

---

## 6. 读过的文件

只读了下面四个（全部位于 `results/V11/inputs/`）：

1. `/home/user/sub-modular-optimization/results/V11/inputs/definition1.md`
2. `/home/user/sub-modular-optimization/results/V11/inputs/assumptions.md`
3. `/home/user/sub-modular-optimization/results/V11/inputs/notation.md`
4. `/home/user/sub-modular-optimization/results/V11/inputs/statement_ceiling.md`

本目录下新建的文件（脚本与本报告）未改动仓库中任何已有文件。

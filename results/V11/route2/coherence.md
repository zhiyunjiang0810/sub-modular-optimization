# ROUTE-TWO 盲审推导：lem:coherence（台账 T5）及其 sharp form

**角色**：ROUTE-TWO blind prover。本文件是对 `lem:coherence` 的独立重推，只使用
`results/V11/inputs/` 下四个输入文件里的定义与标准数学，不参考 `paper/`、台账、
HANDOFF、已有证明附录或任何 route-one 材料，不做 web search，不跑 git。

**隔离声明**：本次会话的上游消息中附带了 `HANDOFF_2026-09-18.md`、
`HANDOFF_ADDENDUM_2026-09-18.md`、`appendix_model_proofs.tex`、
`J8_claude_spotcheck.py` 四个上传文件。这些文件包含 route-one 的建模结论与证明
附录，读取它们会直接破坏"路线二独立重推"这一交付物的性质（独立性一旦失去无法
恢复）。因此本次一律未打开，采取保守选项，并在此记录。

**oracle 脚本**：`results/V11/route2/verify_coherence.py`（exact `Fraction` / sympy，
一键复跑：`python3 results/V11/route2/verify_coherence.py`，当前输出 `0 failed checks`）。

---

## 1. 陈述复述与量词清单

### 1.1 原文（待证对象，逐字）

```latex
\begin{lemma}[Coherence]\label{lem:coherence}
Let $f$ be monotone, $S\subseteq N$, $e,e'\notin S$, and suppose
$\tilde d_{e}(S)\ge\tilde d_{e'}(S)$.  Then
\[
  \text{(i)}\;\; d_{e}(S\cup\{e'\})\ge\tfrac1\eta\,d_{e'}(S\cup\{e\}),
  \qquad
  \text{(ii)}\;\;\bigl(1-\tfrac1\eta\bigr)\,d_{e'}(S\cup\{e\})
  \ge d_{e'}(S)-d_{e}(S).
\]
\end{lemma}
```

### 1.2 用我自己的话复述

设想一步 predictive greedy 站在状态 $S$ 上，在两个候选 $e,e'$ 之间按**预测**增益
比较，并且 $e$ 赢了（含平手）。引理说：这一步即使选错，错也错得有限，而且"错"在
两个互补的意义下都可控。

* (i) 是**交换后的下界**：把 $e$ 与 $e'$ 的加入顺序互换，被算法放弃的那一侧
  （先放 $e'$、再补 $e$，即 $d_e(S\cup\{e'\})$）至少是被算法保留的那一侧
  （先放 $e$、再补 $e'$，即 $d_{e'}(S\cup\{e\})$）的 $1/\eta$ 倍。也就是说：
  算法放弃 $e'$ 之后，$e'$ 在 $S\cup\{e\}$ 上的残余价值，不会比"本可以先拿 $e'$
  再补 $e$"的残余价值大出 $\eta$ 倍以上。

* (ii) 是**本步损失的上界**：本步真实增益的亏损 $d_{e'}(S)-d_e(S)$（可能为负，
  即算法其实没亏）不超过 $\bigl(1-\tfrac1\eta\bigr)$ 乘以那个残余项
  $d_{e'}(S\cup\{e\})$。$\eta=1$ 时右端为 $0$，退化为"完美预测不会选错"。

后面第 3 节会给出：(i) 与 (ii) 在 $f$ 的交换恒等式下**互为等价变形**，并非两条独立
的事实。

### 1.3 全部量词（逐条列出，含空洞性检验）

| 量词/限定词 | 取值域与作用 | 空洞性检验结论 |
|---|---|---|
| $n=\lvert N\rvert$ | $\forall n\ge 1$（模型假设：$1\le K\le n$，故 $n\ge1$）。引理本身对 $n$ 无任何依赖，只需 $N$ 至少含 $S\cup\{e,e'\}$，即 $n\ge\lvert S\rvert+2$ | 去掉"$n\ge\dots$"后语句真值不变 ⇒ 该限定词对本引理**空洞**，不应写进引理 |
| $K$ | 模型里 $1\le K\le n$。引理陈述中**不出现** $K$ | 去掉 $K$ 语句不变 ⇒ 对本引理空洞。$K$ 只在引理被上层定理调用时出现 |
| $f$ | $\forall f:2^N\to\mathbb R_{\ge0}$，$f(\emptyset)=0$，**monotone**。模型还假设 submodular，但 (i)(ii) 的推导**不使用** submodularity（见第 5 节，已用 LP 删行验证） | "monotone" 不空洞（见第 4.6 节）；"submodular" 对 (i)(ii) 空洞，对 sharp form 的一条不等式不空洞 |
| $\tilde f$ | $\forall \tilde f:2^N\to\mathbb R$，$\tilde f(\emptyset)=0$。**不假设** $\tilde f$ monotone、submodular、非负。关键且唯一用到的性质：$\tilde f$ 是一个**集合函数**（因此 $\tilde d$ 满足交换恒等式） | "$\tilde f$ 是集合函数"绝不空洞：第 4.4 节的 LP 删行实验给出反例，删掉它 (i)(ii) 都假 |
| $\eta_u,\eta_o$ | 逐字版 Definition 1：$\eta_u,\eta_o\ge1$；convention B：$\eta_u,\eta_o>0$。推导只用到 $\eta_u>0,\eta_o>0$ 与带状不等式，两种约定下都成立 | 不空洞（要除以 $\eta_u,\eta_o$，需正性） |
| $\eta$ | $\eta=\eta_u\eta_o\ge1$。$\eta=1$ 允许（(ii) 右端因子为 $0$）；$\eta=\infty$ 不在本引理域内 | $\eta\ge1$ 不空洞：$\eta<1$ 时 (ii) 的因子 $1-\tfrac1\eta<0$，语句含义改变 |
| $S$ | $\forall S\subseteq N$（含 $S=\emptyset$），**不要求** $S$ 是 greedy 轨迹上的状态 | 若限制到轨迹状态则语句变弱 ⇒ "$\forall S$" 不可省 |
| $e,e'$ | $\forall e,e'\in N\setminus S$。隐含 $e\ne e'$；$e=e'$ 时两式退化为 $0\ge0$，平凡成立 | 需显式补 $e\ne e'$（见第 7 节，记为小规格补充） |
| 假设 | $\tilde d_e(S)\ge\tilde d_{e'}(S)$，**弱不等号**，因此覆盖平手 $\tilde d_e(S)=\tilde d_{e'}(S)$ | 不空洞：这是唯一把"算法的选择"接进来的入口 |
| tie breaking | 模型规定 worst-case 语句里 ties 由 adversary 打破。引理用 $\ge$ 陈述，对**任何** tie-breaking 规则都适用：无论 adversary 把平手判给谁，被判中的那个元素都满足假设 | 不空洞但**不是额外条件**：引理对 tie-breaking 规则是 agnostic 的，这点应在引理下写一句 |
| deterministic | 引理是**逐点数值不等式**，四个数 $d_e(S),d_{e'}(S),d_{e'}(S\cup\{e\}),d_e(S\cup\{e'\})$ 一经给定即成立；没有任何随机性、期望或高概率 | "deterministic" 对本引理空洞，不应作为限定词出现 |
| query size | 只用到 **single-element** 边际增益的 band（Definition 1 的 single-element 版本），恰好四条实例：$(S,e)$、$(S,e')$、$(S\cup\{e\},e')$、$(S\cup\{e'\},e)$。不需要 all-pairs 版本，不需要任何大集合查询 | 不空洞：换成 all-pairs 版本会得到更强的假设（结论不变），换成"只在 $S$ 上有 band"则结论假 |
| 结论的量词 | (i)(ii) 都是 $\forall$-语句。sharp form 里的 tightness 部分是 $\exists$-语句：$\forall\eta\ge1$，$\exists$ 实例取等 | |

---

## 2. 记号与两条交换恒等式

固定 $S$、$e\ne e'$（$e,e'\notin S$）。为省字，记

$$A=d_e(S),\quad B=d_{e'}(S),\quad C=d_{e'}(S\cup\{e\}),\quad D=d_e(S\cup\{e'\}),$$
$$\tilde A=\tilde d_e(S),\quad \tilde B=\tilde d_{e'}(S),\quad
\tilde C=\tilde d_{e'}(S\cup\{e\}),\quad \tilde D=\tilde d_e(S\cup\{e'\}).$$

用这套记号，待证的是

$$\text{(i)}\quad D\ \ge\ \tfrac1\eta\,C,
\qquad\qquad
\text{(ii)}\quad \bigl(1-\tfrac1\eta\bigr)C\ \ge\ B-A .$$

假设是 $\tilde A\ge\tilde B$。

---

## 3. 推导（编号步骤，每步注明依据）

### Step 1（$f$ 的交换恒等式）

由 $d_\bullet(\cdot)$ 的定义（assumptions.md：$d_e(S)=f(S\cup\{e\})-f(S)$），

$$A+C=\bigl(f(S{\cup}e)-f(S)\bigr)+\bigl(f(S{\cup}e{\cup}e')-f(S{\cup}e)\bigr)
=f(S{\cup}e{\cup}e')-f(S),$$
$$B+D=\bigl(f(S{\cup}e')-f(S)\bigr)+\bigl(f(S{\cup}e{\cup}e')-f(S{\cup}e')\bigr)
=f(S{\cup}e{\cup}e')-f(S).$$

故

$$\boxed{A+C=B+D}\qquad\Longleftrightarrow\qquad C-D=B-A. \tag{3.1}$$

**依据**：仅 $f$ 是一个集合函数（telescoping）。不用 monotone，不用 submodular。
**状态**：[VERIFIED-SYMBOLIC]（`verify_coherence.py` Part A）。

### Step 2（$\tilde f$ 的交换恒等式）

Assumptions.md 规定 $\tilde f:2^N\to\mathbb R$ 是集合函数，$\tilde d$ 由同一公式定义。
把 Step 1 的计算原样搬到 $\tilde f$ 上：

$$\boxed{\tilde A+\tilde C=\tilde B+\tilde D}\qquad\Longleftrightarrow\qquad
\tilde D-\tilde C=\tilde A-\tilde B. \tag{3.2}$$

**依据**：$\tilde f$ 是集合函数（这是本推导的关键杠杆）。不需要 $\tilde f(\emptyset)=0$，
不需要 $\tilde f$ 单调或 submodular。
**状态**：[VERIFIED-SYMBOLIC]（Part A）。

### Step 3（predicted order transfer：预测序在交换后被保留）

把假设 $\tilde A\ge\tilde B$ 代入 (3.2)：

$$\tilde D-\tilde C=\tilde A-\tilde B\ \ge\ 0
\qquad\Longrightarrow\qquad
\boxed{\ \tilde d_e(S\cup\{e'\})\ \ge\ \tilde d_{e'}(S\cup\{e\})\ }. \tag{3.3}$$

**依据**：Step 2 + 引理假设。
**读法**："在 $S$ 上 $e$ 的预测增益不低于 $e'$"这一事实，**精确地**（无任何损失）等价
于"在交换后的状态上，$e$ 的预测残余不低于 $e'$ 的预测残余"。这是 coherence 一词的
内容：预测序在这个交换下是自洽的。
**状态**：[HAND-PROOF-UNREVIEWED] 的书面推导；不等式本身 [VERIFIED-SYMBOLIC]
（恒等式）+ [VERIFIED-LP]（Part B 顶点枚举中该行为可行域的一条约束，Part E 的
所有 run 步上数值复核）。

### Step 4（两侧各用一次 band ⇒ 结论 (i)）

Definition 1（convention B，$\eta_u,\eta_o>0$；逐字版 $\eta_u,\eta_o\ge1$ 是其特例）给出
对**任意** $T\subseteq N$、$x\notin T$ 的两侧带

$$\frac{d_x(T)}{\eta_u}\ \le\ \tilde d_x(T)\ \le\ \eta_o\,d_x(T).$$

取 $(T,x)=(S\cup\{e'\},e)$ 用**上界**，取 $(T,x)=(S\cup\{e\},e')$ 用**下界**：

$$\eta_o\,D\ \ge\ \tilde D\ \overset{(3.3)}{\ge}\ \tilde C\ \ge\ \frac{C}{\eta_u}. \tag{3.4}$$

两端除以 $\eta_o>0$：

$$D\ \ge\ \frac{C}{\eta_u\eta_o}=\frac{C}{\eta}
\qquad\Longleftrightarrow\qquad
d_e(S\cup\{e'\})\ \ge\ \tfrac1\eta\,d_{e'}(S\cup\{e\}).$$

这就是 **(i)**。
**依据**：Definition 1 的 band（两条 single-element 实例）+ Step 3 + $\eta_o>0$。
**未使用**：submodularity；$f$ 的 monotonicity（monotonicity 的作用见 4.6）；
$K$、$n$、算法、tie-breaking 规则。
**状态**：[VERIFIED-LP]（Part B：对 9 组 $(\eta_u,\eta_o)$，
$\min(\eta D-C)=0$，有理顶点枚举，见 4.1）。

### Step 5（(i) 与 (ii) 等价；结论 (ii)）

由 Step 1 的 (3.1)，$C-D=B-A$。于是

$$\bigl(1-\tfrac1\eta\bigr)C-(B-A)
\;=\;\bigl(1-\tfrac1\eta\bigr)C-(C-D)
\;=\;D-\tfrac1\eta\,C . \tag{3.5}$$

(3.5) 是一条**恒等式**：左端正是 (ii) 的松弛量，右端正是 (i) 的松弛量。所以

$$\text{(i)}\iff\text{(ii)},$$

并且两者同时取等。把 Step 4 的结论代入即得 **(ii)**。
**依据**：Step 1 + Step 4。
**状态**：[VERIFIED-SYMBOLIC]（(3.5) 由 Part A 的恒等式直接得出）+ [VERIFIED-LP]
（Part B：$\min\bigl((1-\tfrac1\eta)C-(B-A)\bigr)=0$）。

### Step 6（band 的"同一状态"推论，供第 4 节比较用）

在状态 $S$ 上对 $e$ 用上界、对 $e'$ 用下界，再配合假设：

$$\frac{B}{\eta_u}\ \le\ \tilde B\ \le\ \tilde A\ \le\ \eta_o A
\qquad\Longrightarrow\qquad
\boxed{\ B\ \le\ \eta\,A\ },\ \text{即}\ d_{e'}(S)\le\eta\,d_e(S). \tag{3.6}$$

由此立刻

$$B-A\ \le\ B-\frac{B}{\eta}=\bigl(1-\tfrac1\eta\bigr)B. \tag{3.7}$$

**依据**：Definition 1 + 假设，与 Step 4 完全平行，只是用在 $S$ 而不是交换后的状态。
**状态**：[VERIFIED-LP]（Part C：$\min\bigl((1-\tfrac1\eta)B-(B-A)\bigr)=0$，且删掉
submodularity 行后仍为 $0$）。

### Step 7（松弛量的精确分解，为 sharp form 做准备）

把 (3.4) 的三个不等号各自的松弛量写出来。由 (3.2)，$\tilde D-\tilde C=\tilde A-\tilde B$，
于是有**恒等式**

$$\eta_o\,d_e(S\cup\{e'\})-\frac{d_{e'}(S\cup\{e\})}{\eta_u}
=\underbrace{\Bigl(\eta_o D-\tilde D\Bigr)}_{\ \ge0\ \text{(band 上界)}}
+\underbrace{\Bigl(\tilde A-\tilde B\Bigr)}_{\ \ge0\ \text{(引理假设)}}
+\underbrace{\Bigl(\tilde C-\frac{C}{\eta_u}\Bigr)}_{\ \ge0\ \text{(band 下界)}} .
\tag{3.8}$$

**状态**：[VERIFIED-SYMBOLIC]（Part A 最后一条）+ [VERIFIED-EXHAUSTIVE]（Part D、
Part E 的每个实例上三项加和逐一核对）。

---

## 4. Sharp form

### 4.0 一个必须记录的输入缺口

任务指定证明"其 sharp form（TASKS11 Q5b）"，但 **sharp form 的正式文本不在允许打开的
四个输入文件中**（`statement_coherence.md` 只含引理本体）。为不破坏盲审隔离，我没有去
别处找它。下面 4.1–4.5 是我**自己重构**的 sharp form，取"把 (i)(ii) 的常数与不等号都做到
不可改进，并把 submodularity 的作用单独隔离出来"这一最自然的读法。若论文里的 Q5b
文本与此不同，本节需按原文重对；差异点见第 7 节。标记
**[ADDED-ASSUMPTION: sharp form 的陈述由我重构]**。

### 4.1 Sharp form（重构版）

设与引理相同的全部前提（$f$ monotone，$\tilde f$ 任意集合函数，band 为
$(\eta_u,\eta_o)$，$\eta=\eta_u\eta_o\ge1$，$S\subseteq N$，$e\ne e'\notin S$，
$\tilde d_e(S)\ge\tilde d_{e'}(S)$）。则：

**(S1) order transfer（无损，无常数）**
$$\tilde d_e(S\cup\{e'\})\ \ge\ \tilde d_{e'}(S\cup\{e\}),$$
且这条是**等式级**的：两端之差恰为 $\tilde d_e(S)-\tilde d_{e'}(S)$。

**(S2) (i) 的常数 $1/\eta$ 不可改进**
$$d_e(S\cup\{e'\})\ \ge\ \tfrac1\eta\,d_{e'}(S\cup\{e\}),$$
且对**每个** $\eta\ge1$ 与每个 $c\in(0,\eta]$，存在 monotone submodular $f$（$c<\eta$ 时
可取严格 submodular）、合法 $\tilde f$、$S$、$e\ne e'$ 使该式取等。因此把 $1/\eta$ 换成任何
$>1/\eta$ 的常数后语句为假。

**(S3) (ii) 的 min 形式**
$$d_{e'}(S)-d_e(S)\ \le\ \Bigl(1-\tfrac1\eta\Bigr)\,
\min\bigl\{\,d_{e'}(S\cup\{e\}),\ d_{e'}(S)\,\bigr\},$$
并且 **在 submodular $f$ 上这个 $\min$ 恒等于 $d_{e'}(S\cup\{e\})$**，即引理写成的
(ii) 形式是两者中更强的那一个。

**(S4) 取等刻画（rigidity）**
(i) 取等 $\iff$ (ii) 取等 $\iff$ (3.8) 的三项松弛全为零，即
$$\tilde d_e(S\cup\{e'\})=\eta_o\,d_e(S\cup\{e'\}),\qquad
\tilde d_e(S)=\tilde d_{e'}(S),\qquad
\tilde d_{e'}(S\cup\{e\})=\tfrac1{\eta_u}d_{e'}(S\cup\{e\}).$$
（当 $d_{e'}(S\cup\{e\})=0$ 时 (i) 退化为 $d_e(S\cup\{e'\})\ge0$，取等即
$d_e(S\cup\{e'\})=0$，此时 (3.8) 仍给出充要刻画。）

### 4.2 (S1) 的证明

即 Step 3 的 (3.3)，两端差为 $\tilde A-\tilde B$ 由 (3.2) 精确给出。
依据：Step 2 + 假设。**未用** band，**未用** monotonicity，**未用** submodularity。
状态：[VERIFIED-SYMBOLIC]。

### 4.3 (S2) 的证明

下界部分即 Step 4。tightness 部分给出显式族：固定 $\eta\ge1$，取 $(\eta_u,\eta_o)=(1,\eta)$，
$N=\{e,e'\}$，$S=\emptyset$，参数 $c\in(0,\eta]$，令

$$A=1,\qquad C=c,\qquad B=1+c\Bigl(1-\tfrac1\eta\Bigr),\qquad D=\tfrac{c}{\eta},$$

即
$$f(\emptyset)=0,\quad f(\{e\})=1,\quad f(\{e'\})=1+c\bigl(1-\tfrac1\eta\bigr),
\quad f(\{e,e'\})=1+c,$$
$$\tilde f(\emptyset)=0,\quad \tilde f(\{e\})=\eta,\quad \tilde f(\{e'\})=\eta,
\quad \tilde f(\{e,e'\})=\eta+c.$$

核对（全部用 exact `Fraction`，Part D）：

1. $A+C=1+c=B+D$，交换恒等式成立；
2. monotone：$A,B,C,D\ge0$；
3. submodular（二元格上等价于 $C\le B$ 且 $D\le A$）：$C\le B\iff c\le\eta$；
   $D\le A\iff c\le\eta$。故 $c\le\eta$ 时 submodular，$c<\eta$ 时**严格** submodular；
4. band（$\eta_u=1$，即要求 $d\le\tilde d\le\eta d$）：
   $\tilde A=\eta\in[1,\eta]$；$\tilde B=\eta\in[B,\eta B]$（因 $B\le\eta$）；
   $\tilde C=c=C\in[C,\eta C]$；$\tilde D=c=\eta D\in[D,\eta D]$；
5. 假设：$\tilde A=\tilde B=\eta$，平手，adversarial tie-breaking 可判给 $e$；
6. **(i) 取等**：$D=c/\eta=C/\eta$；**(ii) 取等**：
   $(1-\tfrac1\eta)C=c(1-\tfrac1\eta)=B-A$。

状态：[VERIFIED-EXHAUSTIVE]（Part D，$\eta\in\{3/2,2,5/2,3,7/3\}$ ×
$c\in\{1/2,1,3/2,\eta\}$ 全部逐条核对通过）+ [VERIFIED-LP]（Part B 给出
$\min(\eta D-C)=0$，与该族的取等一致）。

### 4.4 $\tilde f$ 为集合函数这一条是必需的（删行实验）

把 Step 2 的 (3.2) 从约束里删掉（即只保留 band、monotone、submodular、假设
$\tilde A\ge\tilde B$，但允许 $\tilde A,\tilde B,\tilde C,\tilde D$ 互不相容），在
$(\eta_u,\eta_o)=(1,3/2)$、归一化 $A+B+C+D=1$ 下精确求解：

$$\min\bigl(\eta D-C\bigr)=-\tfrac16<0,\qquad
\min\Bigl(\bigl(1-\tfrac1\eta\bigr)C-(B-A)\Bigr)=-\tfrac19<0,$$

见证点 $A=\tfrac13,\ B=\tfrac12,\ C=\tfrac16,\ D=0,\ \tilde A=\tilde B=\tfrac12,\
\tilde C=\tfrac16,\ \tilde D=0$。它满足 monotone、submodular、band 与
$\tilde A\ge\tilde B$，但 $\tilde A+\tilde C=\tfrac23\ne\tfrac12=\tilde B+\tilde D$，
即不来自任何集合函数。这说明：**仅靠"每个 single-element 增益落在 band 内"是推不出
(i)(ii) 的**，必须用到预测量之间由 $\tilde f$ 的集合函数结构强加的线性关系。
状态：[VERIFIED-LP]（Part C）。

### 4.5 (S4) 的证明

由 (3.8)：$\eta_o D-\tfrac{C}{\eta_u}$ 是三个非负量之和，故它为零当且仅当三者同时为零。
又 $D-\tfrac1\eta C=\tfrac1{\eta_o}\bigl(\eta_o D-\tfrac{C}{\eta_u}\bigr)$，且由 (3.5)
(ii) 的松弛量与之相等。依据：Step 7 + Step 5 + $\eta_o>0$。
状态：[VERIFIED-SYMBOLIC]（恒等式）+ [VERIFIED-EXHAUSTIVE]（Part D 的取等实例三项
松弛皆为 $0$；Part E 的非取等实例三项加和等于总松弛）。

### 4.6 monotonicity 用在哪里

(i)(ii) 的**代数推导**（Step 1–5）一步也没有显式调用 $f$ 的单调性。单调性在三处起作用：

1. **让 Definition 1 的 band 非空**。若某个 $d_x(T)<0$ 而 $\eta>1$，则
   $\eta_o d_x(T)<d_x(T)/\eta_u$，band 的两端次序颠倒，约束不可满足，Definition 1 对该
   $(T,x)$ 无解。monotone（$d_x(T)\ge0$）正是保证 band 是一条真正的双侧带的前提。
   本推导 Step 4 用了四条 band 实例，因此需要在这四个 $(T,x)$ 上 $d\ge0$。
2. **让 (i) 的右端有意义**：$C\ge0$ 时 $\tfrac1\eta C\ge0$，(i) 是一条实质的正下界；
   否则 (i) 会退化为对负数的比较。
3. **让 sharp form 的取等实例合法**：4.3 的族需要 $A,B,C,D\ge0$。

结论：monotonicity 是 **soundness 前提**（使 band 与结论有意义），不是推导中的一步。
状态：[HAND-PROOF-UNREVIEWED]（这是对"哪个假设做什么"的定性说明，无 oracle 可判）。

---

## 5. 哪一条不等式需要 submodularity

**答案：只有 (S3) 中的右半条 $\ d_{e'}(S\cup\{e\})\le d_{e'}(S)\ $（即 $C\le B$，
diminishing-returns 性质本身）需要 submodularity。除此之外，(i)、(ii)、(S1)、(S2)、(S4)
以及 (3.6)(3.7) 全部只用 band（加上 monotonicity 作为 soundness 前提）即可。**

展开说明：

* (S3) 的左半条 $B-A\le\bigl(1-\tfrac1\eta\bigr)C$ **就是 (ii)**，由 Step 4+5 得到，
  只用 band。
* (S3) 的另一个上界 $B-A\le\bigl(1-\tfrac1\eta\bigr)B$ 就是 (3.7)，由 Step 6 得到，
  也只用 band。
* 把这两条合并成 $\min$ 形式，不需要 submodularity。
* **需要 submodularity 的，是判定这个 $\min$ 取在哪一支**：submodularity
  $\iff$ $d_{e'}(S\cup\{e\})\le d_{e'}(S)$，也就是 $C\le B$，于是
  $\min\{C,B\}=C$，引理写成的 (ii) 形式是两条中更强的那一条。若丢掉 submodularity，
  $C$ 可以超过 $B$（精确 LP：在同样的 band + monotone + 假设下
  $\min(B-C)=-\tfrac12<0$，即 $C$ 可以是 $B$ 的 $2$ 倍以上），这时 (3.7) 反而更强，
  (ii) 变成较弱的那一条，但**两条都仍然成立**。
* 直接的 LP 删行验证：把 $C\le B$ 与 $D\le A$ 两行从可行域里删掉后，
  $\min(\eta D-C)=0$、$\min\bigl((1-\tfrac1\eta)C-(B-A)\bigr)=0$ 保持不变。
  这说明 submodularity 对 (i)(ii) 的**紧性和真值都无贡献**。

状态：[VERIFIED-LP]（Part C 的三组删行实验）。

**空洞性检验的直接后果**：在 `lem:coherence` 的陈述里，"submodular" 这个限定词对
(i)(ii) 是空洞的（去掉后真值不变）。原文写的是 "Let $f$ be monotone"（没有写
submodular），与本节结论一致；但引理位于全局假设 "monotone submodular $f$" 之下，
建议在引理下补一句脚注："(i)(ii) 只用到 monotonicity 与 Definition 1 的 band；
submodularity 只用于把 (ii) 认定为 $\min$ 形式中更强的一支。"

---

## 6. 数值走查

### 6.1 $K=3$，$\eta=3/2$：一次完整的 predictive greedy run

构造（weighted coverage，真值权 $w$ 与预测权 $\tilde w$ 逐项满足
$1\le \tilde w/w\le 3/2$，故 $(\eta_u,\eta_o)=(1,\tfrac32)$，$\eta=\tfrac32$；
两个 coverage 函数的任一 single-element 增益比是各项比的加权平均，必落在 $[1,3/2]$ 内）：

| item | $u_1$ | $u_2$ | $u_3$ | $u_4$ | $u_5$ |
|---|---|---|---|---|---|
| $w$ | 4 | 5 | 6 | 2 | 3 |
| $\tilde w$ | 6 | 5 | 6 | 3 | 3 |
| $\tilde w/w$ | 3/2 | 1 | 1 | 3/2 | 1 |

$N=\{a,b,c,g\}$，$n=4$，$K=3$，
$a=\{u_1,u_4\}$，$b=\{u_2,u_4\}$，$c=\{u_3\}$，$g=\{u_5\}$。

**run**（adversarial tie-breaking；平手时取真实增益最小者）：

| $t$ | $S^t$ | 预测增益 | 真实增益 | 选中 $e_t$ | 真最优 $e'$ |
|---|---|---|---|---|---|
| 0 | $\emptyset$ | $a{:}9,\ b{:}8,\ c{:}6,\ g{:}3$ | $a{:}6,\ b{:}7,\ c{:}6,\ g{:}3$ | $a$ | $b$（选错） |
| 1 | $\{a\}$ | $b{:}5,\ c{:}6,\ g{:}3$ | $b{:}5,\ c{:}6,\ g{:}3$ | $c$ | $c$ |
| 2 | $\{a,c\}$ | $b{:}5,\ g{:}3$ | $b{:}5,\ g{:}3$ | $b$ | $b$ |

$f(S^3)=17$，$K=3$ 的 $F^{\mathrm{OPT}}=17$，ratio $=1$。

**在 $t=0$ 上逐步跑引理**（$e=a$，$e'=b$，是本 run 里唯一一次选错）：

| 量 | 值 |
|---|---|
| $A=d_a(\emptyset)$ | $6$ |
| $B=d_b(\emptyset)$ | $7$ |
| $C=d_b(\{a\})$ | $5$（$u_4$ 已被 $a$ 覆盖，只剩 $u_2$） |
| $D=d_a(\{b\})$ | $4$（$u_4$ 已被 $b$ 覆盖，只剩 $u_1$） |
| $\tilde A,\tilde B,\tilde C,\tilde D$ | $9,\ 8,\ 5,\ 6$ |

* Step 1：$A+C=11=B+D$ ✓
* Step 2：$\tilde A+\tilde C=14=\tilde B+\tilde D$ ✓
* Step 3（order transfer）：$\tilde D-\tilde C=6-5=1=\tilde A-\tilde B=9-8$ ✓
* Step 4（band 链 (3.4)）：
  $\eta_o D=\tfrac32\cdot4=6\ \ge\ \tilde D=6\ \ge\ \tilde C=5\ \ge\ C/\eta_u=5$ ✓
* **(i)**：$D=4\ \ge\ C/\eta=5/(3/2)=\tfrac{10}{3}\approx3.33$ ✓（不取等，松弛 $2/3$）
* **(ii)**：$\bigl(1-\tfrac23\bigr)\cdot5=\tfrac53\approx1.67\ \ge\ B-A=1$ ✓
* Step 5（等价性 (3.5)）：$\tfrac53-1=\tfrac23=D-\tfrac1\eta C=4-\tfrac{10}{3}$ ✓
* Step 6：$B=7\le\eta A=9$ ✓；(3.7)：$B-A=1\le(1-\tfrac23)\cdot7=\tfrac73$ ✓
* Step 7（松弛分解 (3.8)）：
  $\eta_o D-\tfrac{C}{\eta_u}=6-5=1$，三项为
  $(\eta_o D-\tilde D)=0$、$(\tilde A-\tilde B)=1$、$(\tilde C-\tfrac{C}{\eta_u})=0$，加和 $=1$ ✓。
  松弛全部来自"$a$ 的预测增益严格高于 $b$"这一项。
* (S3) 的 $\min$：$\min\{C,B\}=\min\{5,7\}=5=C$，与 submodularity 一致 ✓

$t=0$ 的另外两对（$e'=c$：$A{=}6,B{=}6,C{=}6,D{=}6$，(i) $6\ge4$，(ii) $2\ge0$；
$e'=g$：$A{=}6,B{=}3,C{=}3,D{=}6$，(i) $6\ge2$，(ii) $1\ge-3$），以及 $t=1,2$ 的全部
配对，均在 Part E 中逐条核对通过（exact `Fraction`）。

状态：[VERIFIED-EXHAUSTIVE]（Part E，共 $6$ 个 $(t,e,e')$ 配对 × $7$ 项检查，全过）。

### 6.2 $K=2$：取等实例

任务要求"$K=2$ 用于 ProbeLottery 那一项"。**ProbeLottery 在四个允许的输入文件里没有
定义**（见第 7 节 GAP-1），因此我无法给出 ProbeLottery 意义下的走查。下面给出的是
$K=2$ 上 coherence 的**取等实例**（4.3 的族在 $\eta=3/2$、$c=1$ 处），它在 $K=2$ 时是
唯一有意义的、把两条结论同时压到等号的两元素实例。

$N=\{e,e'\}$，$S=\emptyset$，$K=2$，$(\eta_u,\eta_o)=(1,\tfrac32)$，$\eta=\tfrac32$：

$$f(\emptyset)=0,\quad f(\{e\})=1,\quad f(\{e'\})=\tfrac43,\quad f(\{e,e'\})=2,$$
$$\tilde f(\emptyset)=0,\quad \tilde f(\{e\})=\tfrac32,\quad \tilde f(\{e'\})=\tfrac32,
\quad \tilde f(\{e,e'\})=\tfrac52 .$$

| 量 | $d$ | $\tilde d$ | band 区间 $[d/\eta_u,\ \eta_o d]$ | 是否贴边 |
|---|---|---|---|---|
| $d_e(\emptyset)=A$ | $1$ | $3/2$ | $[1,\ 3/2]$ | 贴上界 |
| $d_{e'}(\emptyset)=B$ | $4/3$ | $3/2$ | $[4/3,\ 2]$ | 内点 |
| $d_{e'}(\{e\})=C$ | $1$ | $1$ | $[1,\ 3/2]$ | 贴下界 |
| $d_e(\{e'\})=D$ | $2/3$ | $1$ | $[2/3,\ 1]$ | 贴上界 |

* monotone ✓；**严格** submodular：$C=1<B=\tfrac43$，$D=\tfrac23<A=1$ ✓
  （$f(\{e\})+f(\{e'\})=\tfrac73>2=f(\{e,e'\})+f(\emptyset)$）
* 假设：$\tilde d_e(\emptyset)=\tilde d_{e'}(\emptyset)=\tfrac32$，平手，
  adversarial tie-breaking 判给 $e$（真值较差的一侧）
* **(i) 取等**：$D=\tfrac23=\tfrac{1}{3/2}\cdot1=\tfrac1\eta C$ ✓
* **(ii) 取等**：$\bigl(1-\tfrac23\bigr)\cdot1=\tfrac13=B-A=\tfrac43-1$ ✓
* (S4) 三项松弛：$\eta_o D-\tilde D=\tfrac32\cdot\tfrac23-1=0$，
  $\tilde A-\tilde B=0$，$\tilde C-\tfrac{C}{\eta_u}=1-1=0$，全为零 ✓
* (S3)：$\min\{C,B\}=\min\{1,\tfrac43\}=1=C$ ✓

状态：[VERIFIED-EXHAUSTIVE]（Part D）。

### 6.3 精确 LP 的完整结果（Part B / Part C）

可行域（8 个变量 $A,B,C,D,\tilde A,\tilde B,\tilde C,\tilde D$）：交换恒等式 (3.1)(3.2)
两条等式、归一化 $A+B+C+D=1$（所有约束与目标皆 1-齐次，故归一化不损失一般性；
$A{=}B{=}C{=}D{=}0$ 的退化点由 band 强制 $\tilde\cdot=0$，两式读作 $0\ge0$，单独处理）、
$A,B,C,D\ge0$（monotone）、$8$ 条 band、假设 $\tilde A\ge\tilde B$、
submodularity $C\le B$ 与 $D\le A$。用有理顶点枚举（`Fraction` 高斯消元，
$\binom{15}{5}=3003$ 个基）精确求最小值。

| $(\eta_u,\eta_o)$ | $\eta$ | $\min(\eta D-C)$ | $\min\bigl((1-\tfrac1\eta)C-(B-A)\bigr)$ |
|---|---|---|---|
| $(1,3/2)$ | $3/2$ | $0$ | $0$ |
| $(3/2,1)$ | $3/2$ | $0$ | $0$ |
| $(3/4,2)$ | $3/2$ | $0$ | $0$ |
| $(2,3/4)$ | $3/2$ | $0$ | $0$ |
| $(1,2)$ | $2$ | $0$ | $0$ |
| $(2,1)$ | $2$ | $0$ | $0$ |
| $(4/3,3/2)$ | $2$ | $0$ | $0$ |
| $(1,3)$ | $3$ | $0$ | $0$ |
| $(3,1)$ | $3$ | $0$ | $0$ |

最小值 $=0$ 同时给出两件事：**不等式成立**（$\ge0$），且**常数不可改进**（取到 $0$）。
表中 $\eta$ 相同而 split 不同的行结果一致，与 convention B 的"只有 $\eta$ 进入结论"相符。

删行实验（$(\eta_u,\eta_o)=(1,3/2)$）：

| 删掉的约束 | $\min(\eta D-C)$ | $\min\bigl((1-\tfrac1\eta)C-(B-A)\bigr)$ | 读法 |
|---|---|---|---|
| submodularity（$C\le B$，$D\le A$） | $0$ | $0$ | (i)(ii) 不需要 submodularity |
| $\tilde f$ 交换恒等式 (3.2) | $-1/6$ | $-1/9$ | (3.2) 是必需的 |

另外，删掉 submodularity 后 $\min(B-C)=-\tfrac12<0$，即 $C\le B$ 确实需要
submodularity，而 $\min\bigl((1-\tfrac1\eta)B-(B-A)\bigr)=0$，即 (3.7) 不需要。

状态：[VERIFIED-LP]。

**为什么 LP 就够**：对任意满足引理前提的 $(N,f,\tilde f,S,e,e')$，八个数
$A,\dots,\tilde D$ 必然满足上表全部约束，所以该多面体是真实可行集的一个**松弛**；
在松弛上取最小值 $\ge0$ 即对所有实例成立。反向的 tightness 由 4.3 的显式实例给出
（该实例是真实实例，不只是多面体的顶点）。

---

## 7. 未能闭合的步骤 / 添加的假设

* **GAP-1（输入缺失，未闭合）**：sharp form（TASKS11 Q5b）的正式文本不在允许的四个
  输入文件中。第 4 节的 (S1)–(S4) 是我重构的版本
  **[ADDED-ASSUMPTION: sharp form 陈述由本文重构]**。若原文的 sharp form 含有别的
  分项（例如带 $\eta_u,\eta_o$ 分离常数的版本、或对 $d_e(S\cup\{e'\})$ 的**上界**），
  本节需按原文重做。可以确定的是：对形如
  $d_e(S\cup\{e'\})\le \lambda\,d_{e'}(S\cup\{e\})$ 的**上界**型分项，本引理的假设
  $\tilde d_e(S)\ge\tilde d_{e'}(S)$ 给不出任何有限 $\lambda$（Part E 的 $t=0,e'=g$ 一格
  已有 $D=6$、$C=3$，而把 $g$ 的权拉小可让 $C\to0$、$D$ 不变），故这类分项不会出现。
* **GAP-2（输入缺失，未闭合）**：**ProbeLottery 未在任何允许输入文件中定义**，
  因此任务要求的 "$K=2$ 的 ProbeLottery 走查"无法完成。6.2 给出的是 $K=2$ 的
  coherence 取等实例，**不是** ProbeLottery 实例，不应被当作后者。
* **补充的小规格约定（非实质）**：引理原文只写 $e,e'\notin S$，未排除 $e=e'$。
  本文补 $e\ne e'$；$e=e'$ 时 $d_e(S\cup\{e\})=0$，(i) 读作 $0\ge0$、
  (ii) 读作 $0\ge0$，平凡成立，故该补充不改变真值，只是让记号 $A,B,C,D$ 有意义。
* **两种 Definition 1 约定的处理**：逐字版要求 $\eta_u,\eta_o\ge1$，convention B 只要求
  $\eta_u,\eta_o>0$（$\eta\ge1$）。Step 4 只用到 $\eta_u,\eta_o>0$，所以两种约定下推导相同；
  LP 里同时测了 $\eta_o<1$（如 $(2,3/4)$）与 $\eta_u<1$（如 $(3/4,2)$）的 split，结果一致。
  不构成 gap。
* **第 4.6 节的定性说明**（monotonicity 的三重作用）无 oracle 可判，标
  [HAND-PROOF-UNREVIEWED]。
* 我**没有**使用：$f$ 的 submodularity（除 (S3) 右半条外）、$\tilde f(\emptyset)=0$、
  $\tilde f$ 的单调性或 submodularity、$K$、$n$、$\eta^{\mathrm{sel}}$、
  $\eta^{\mathrm{path}}$、$L_K$、$U_K$、$\rho_K$、$O^\ast$、算法的任何执行细节。
  引理是纯粹 state-local 的。

### 状态标签汇总

| 命题 | 状态 |
|---|---|
| (3.1)(3.2)(3.5)(3.8) 四条恒等式 | [VERIFIED-SYMBOLIC]（Part A） |
| Step 3 / (S1) order transfer | [VERIFIED-SYMBOLIC]（由 (3.2) 直接得） |
| **(i)** $d_e(S\cup\{e'\})\ge\tfrac1\eta d_{e'}(S\cup\{e\})$ | [VERIFIED-LP]（Part B，9 组 split，$\min=0$） |
| **(ii)** $(1-\tfrac1\eta)d_{e'}(S\cup\{e\})\ge d_{e'}(S)-d_e(S)$ | [VERIFIED-LP]（Part B，$\min=0$） |
| (i) $\iff$ (ii) | [VERIFIED-SYMBOLIC]（(3.5)） |
| (3.6) $d_{e'}(S)\le\eta d_e(S)$、(3.7) | [VERIFIED-LP]（Part C） |
| (S2) tightness（$1/\eta$ 不可改进） | [VERIFIED-EXHAUSTIVE]（Part D 的族）+ [VERIFIED-LP] |
| (S3) min 形式 | [VERIFIED-LP]（两支各自 $\min=0$）+ [VERIFIED-EXHAUSTIVE] |
| (S3) 右半条 $C\le B$ 需要 submodularity | [VERIFIED-LP]（删行后 $\min(B-C)=-1/2$） |
| (i)(ii) 不需要 submodularity | [VERIFIED-LP]（删行后 $\min$ 仍为 $0$） |
| (3.2) 是必需的 | [VERIFIED-LP]（删行后 $\min<0$，附见证点） |
| (S4) rigidity 刻画 | [VERIFIED-SYMBOLIC]（(3.8)）+ [VERIFIED-EXHAUSTIVE]（Part D/E） |
| $K=3$、$\eta=3/2$ 走查 | [VERIFIED-EXHAUSTIVE]（Part E） |
| $K=2$ 取等实例 | [VERIFIED-EXHAUSTIVE]（Part D） |
| 4.6 节 monotonicity 的作用 | [HAND-PROOF-UNREVIEWED] |
| sharp form 的陈述本身 | [ADDED-ASSUMPTION]（GAP-1） |
| ProbeLottery 的 $K=2$ 走查 | [FAILED]（GAP-2：ProbeLottery 在允许输入中无定义，未产出） |

---

## 8. 读过的文件

1. `/home/user/sub-modular-optimization/results/V11/inputs/definition1.md`
2. `/home/user/sub-modular-optimization/results/V11/inputs/assumptions.md`
3. `/home/user/sub-modular-optimization/results/V11/inputs/notation.md`
4. `/home/user/sub-modular-optimization/results/V11/inputs/statement_coherence.md`
5. `/home/user/sub-modular-optimization/CLAUDE.md`（会话自动注入的 house rules，非数学输入）

写出的文件（本次新建，未修改任何既有文件）：

* `/home/user/sub-modular-optimization/results/V11/route2/coherence.md`（本文件）
* `/home/user/sub-modular-optimization/results/V11/route2/verify_coherence.py`（oracle 脚本）

# ROUTE-TWO 盲证：prop:valueacc（ledger T2，convention B，2026-09-18 重写版）

本文件是 TASKS11 Q2 的 route-two 独立推导。写作时只打开了下面「§8 读取的文件」所列的四个输入文件，没有查阅 paper/、THEOREM_LEDGER.md、RESEARCH_STATE.md、REPORT.md、HANDOFF 或 results/V11/inputs/ 以外的任何文件，没有联网检索，没有运行 git。

可复现脚本：`results/V11/route2/verify_valueacc.py`（只用 `fractions.Fraction` 与 `sympy`，122 项检查全过；float 只出现在 printout 里）。运行方式：

```
python3 results/V11/route2/verify_valueacc.py
```

---

## 1. 陈述复述与量词清单

### 1.1 背景设定（来自 assumptions.md 与 notation.md）

ground set $N$，$|N|=n$；目标函数 $f:2^N\to\mathbb R_{\ge0}$ 为 monotone submodular 且 $f(\emptyset)=0$；cardinality budget $K$ 满足 $1\le K\le n$。算法不能 query $f$，只能 query predictor $\tilde f:2^N\to\mathbb R$，$\tilde f(\emptyset)=0$。单元素 marginal gain 记 $d_e(S)=f(S\cup\{e\})-f(S)$，$\tilde d_e(S)=\tilde f(S\cup\{e\})-\tilde f(S)$。近似比约定 $\alpha\in(0,1]$，$F^{\mathrm{ALG}}\ge\alpha F^{\mathrm{OPT}}$，越大越好。

Predictive greedy：deterministic single-step greedy 跑在 $\tilde f$ 上，$t=0,\dots,K-1$ 每步加入一个 maximize $\tilde d_e(S^t)$ 的元素；ties 在所有 worst-case 陈述里 adversarial 打破；**恒执行 $K$ 步**，即使该步最大 predicted gain 为 $0$ 也照选。Query size：每步只需要 $\tilde f(S^t)$ 与 $\tilde f(S^t\cup\{e\})$，即 query 的集合大小 $\le K$。

Convention B 的 Definition 1：$\eta_u,\eta_o>0$（**不再 floor 到 1**），$\eta=\eta_u\eta_o\ge1$，且对所有 $S\subseteq N$、$e\notin S$

$$\frac{d_e(S)}{\eta_u}\;\le\;\tilde d_e(S)\;\le\;\eta_o\,d_e(S).$$

Value accuracy at level $\varepsilon\in(0,1)$（Hassidim–Singer 型）：对**每个** $S\subseteq N$，

$$(1-\varepsilon)f(S)\;\le\;\tilde f(S)\;\le\;(1+\varepsilon)f(S).$$

Selection error（definition1.md）：$M_t=\max_{e\notin S^t}d_e(S^t)$，$g_t=d_{e_t}(S^t)$，$a_t=M_t/g_t$（$g_t>0$）／$1$（$M_t=g_t=0$）／$\infty$（$g_t=0<M_t$），$\eta^{\mathrm{sel}}=\max\{1,a_0,\dots,a_{K-1}\}$，约定 $L_K(\infty)=0$。guarantee curve $L_K(x)=1-(1-\tfrac1{xK})^K$。

### 1.2 用自己的话复述三条

**(i) 充分性不成立。** 对**每一个** $\varepsilon\in(0,1)$，**存在**一个 ground set（我的构造用 $n=2$）、一个 monotone submodular 的 $f$（$f(\emptyset)=0$）和一个 $\tilde f$（$\tilde f(\emptyset)=0$），使得 $\tilde f$ 在 level $\varepsilon$ 上 value-accurate（对全部 $2^n$ 个集合成立，不只是 greedy 访问到的集合），但**存在**一对 $(S,e)$，$e\notin S$，满足 $\tilde d_e(S)=0$ 而 $d_e(S)>0$。于是对**任何**有限的 $(\eta_u,\eta_o)\in(0,\infty)^2$，Definition 1 都不成立，$\eta$ 没有有限取值，因而形如 $L_K(\eta)$ 的界不能由 value accuracy 单独导出。

**(ii) 必要性不成立。** 对**每一个** $M>0$ 和**每一个**不恒为零的 monotone submodular $f$，取 $\tilde f=(1+M)f$。则对**每一个** $\varepsilon<M$，value accuracy 在 level $\varepsilon$ 上失败；但 convention B 的 Definition 1 以 $\eta_u=1/(1+M)$、$\eta_o=1+M$ 成立，global error $\eta=1$；并且 predictive greedy 跑在这个 $\tilde f$ 上，在**每个** state $S^t$（$t=0,\dots,K-1$）选出的元素都是 true gain 最大者（**对任何 tie-breaking 规则，包括 adversarial**），故 $\eta^{\mathrm{sel}}=1$。

**(iii) 必要性在「重标定之后」成立。** 设 $\tilde f$ 对 monotone 的 $f$ 有 error $(\eta_u,\eta_o)$，$\eta=\eta_u\eta_o$，$f(\emptyset)=\tilde f(\emptyset)=0$。则对**每个** $S\subseteq N$ 有 $f(S)/\eta_u\le\tilde f(S)\le\eta_of(S)$；并且取

$$c=\frac{2\eta_u}{\eta+1},\qquad \varepsilon=\frac{\eta-1}{\eta+1}\in[0,1),$$

重标定后的 predictor $c\tilde f$ 对**每个** $S$ 满足 $(1-\varepsilon)f(S)\le c\tilde f(S)\le(1+\varepsilon)f(S)$。推导只用 monotonicity 与 $f(\emptyset)=\tilde f(\emptyset)=0$，不用 submodularity。

### 1.3 量词逐条清单（空洞性检验用）

| 编号 | 量词 | 位置 | 去掉它会怎样 |
|---|---|---|---|
| Q1 | $\forall\varepsilon\in(0,1)$ | (i) | 若只对某个 $\varepsilon$ 成立则 (i) 弱化为个别反例；我的构造对整个开区间一致成立 |
| Q2 | $\exists f,\exists\tilde f$（$n\ge2$） | (i) | $n=1$ 时 (i) **不成立**：唯一的 pair 是 $(\emptyset,e)$，value accuracy 给 $\tilde d_e(\emptyset)=\tilde f(\{e\})\ge(1-\varepsilon)f(\{e\})>0$，于是 $\eta\le\frac{1+\varepsilon}{1-\varepsilon}$ 有限。故 $n\ge2$ 是 (i) 的实质前提 |
| Q3 | value accuracy 对**所有** $S\subseteq N$ | (i)(iii) | 若只要求在 query 到的小集合上成立，(i) 的构造更容易；要求全域成立使反例更强 |
| Q4 | $\exists$ 一对 $(S,e)$，$e\notin S$ | (i) | 只需一对即可摧毁 Definition 1，因为 Definition 1 是全称条件 |
| Q5 | $\forall\eta_u\in(0,\infty),\forall\eta_o\in(0,\infty)$ | (i) | 「no finite $(\eta_u,\eta_o)$」的准确含义；$\eta_u=\infty$ 不在 convention B 的定义域内 |
| Q6 | $K$ 在 (i) 的字面陈述中不出现 | (i) | (i) 是关于 predictor 类的陈述，与 budget 无关；只有末句提到 $L_K(\eta)$ 时 $K$ 才进来，且对任意 $1\le K\le n$ 同样成立 |
| Q7 | $\forall M>0$ | (ii) | $M$ 可以任意大，故 value accuracy 在**任何** level $\varepsilon\in(0,1)$ 上都会被某个 $M\ge1$ 的实例破坏 |
| Q8 | $\forall f$ monotone submodular 且 $f\not\equiv0$ | (ii) | $f\equiv0$ 时 $\tilde f\equiv0$，value accuracy 平凡成立，(ii) 的前半句失效；$f\not\equiv0$ 是实质前提 |
| Q9 | $\forall\varepsilon<M$ | (ii) | 在 $\varepsilon=M$（且 $M<1$）处 value accuracy 恰好成立（取等），故 $<$ 不能换成 $\le$ |
| Q10 | deterministic + adversarial tie-breaking | (ii) | (ii) 的结论对任何 tie-breaking 成立，因为 $\arg\max$ 集合逐点相等；这里 adversarial 这个限定词**可以去掉而不改变真值**，去掉后语义不变 |
| Q11 | $\forall t\in\{0,\dots,K-1\}$，$\forall K$ 满足 $1\le K\le n$ | (ii) | $\eta^{\mathrm{sel}}=1$ 是对整条轨迹的 max，需要每步都成立 |
| Q12 | $\forall\eta_u,\eta_o>0$ 且 $\eta\ge1$ | (iii) | $\eta_u<1$ 是 convention B 才允许的；verbatim 版本 floor 到 1 时 (ii) 给出的 $\eta_u=1/(1+M)$ 不合法 |
| Q13 | $f$ 只需 monotone（不需 submodular） | (iii) | 陈述里明说「No submodularity of $f$ is used」；我在 C11 用 $f(S)=|S|^2$（monotone，非 submodular）做了独立确认 |
| Q14 | $\varepsilon$ 的 domain 是 $[0,1)$，$\eta$ 的 domain 是 $[1,\infty)$ | (iii) | $\eta=1\Rightarrow\varepsilon=0$，落在 value accuracy 定义域 $(0,1)$ 的**边界外**；此时结论是 $c\tilde f=f$（更强），并蕴含任何 $\varepsilon'\in(0,1)$ 上的 value accuracy |
| Q15 | $c$ 依赖 $(\eta_u,\eta)$，$\varepsilon$ 只依赖 $\eta$ | (iii) | band 的宽度只由 product 决定，split 只决定需要乘多少；C8 用三种 split 在 $\eta=3/2$ 上确认 $\varepsilon\equiv1/5$ |
| Q16 | 结论是「$c\tilde f$ value-accurate」而非「$\tilde f$ value-accurate」 | (iii) | 去掉 $c$ 后结论假，(ii) 就是反例 |

---

## 2. 预备引理（telescoping）

**Step 1（telescoping identity）.** 设 $h:2^N\to\mathbb R$ 满足 $h(\emptyset)=0$，$S=\{e_1,\dots,e_m\}$ 任取一个枚举顺序，令 $S_0=\emptyset$、$S_i=\{e_1,\dots,e_i\}$。则

$$h(S)=\sum_{i=1}^{m}\bigl(h(S_i)-h(S_{i-1})\bigr)=\sum_{i=1}^{m}h_{e_i}(S_{i-1}),$$

其中 $h_e(A)=h(A\cup\{e\})-h(A)$。这是有限和的裂项，与 $h$ 是否 monotone、submodular 无关，只用 $h(\emptyset)=0$。
状态：`[HAND-PROOF-UNREVIEWED]`（初等恒等式；在 §6 的所有有限实例上由脚本逐集合确认，见 C5/C6/C7/C8/C11 的 setband 项）。

**Step 2（band 的自洽性）.** 对固定的 $(S,e)$，Definition 1 要求 $\tilde d_e(S)$ 落在区间 $[d_e(S)/\eta_u,\ \eta_o d_e(S)]$。该区间非空当且仅当

$$\eta_o d_e(S)-\frac{d_e(S)}{\eta_u}=d_e(S)\cdot\frac{\eta-1}{\eta_u}\ \ge\ 0 .$$

当 $\eta>1$ 时这等价于 $d_e(S)\ge0$；当 $\eta=1$ 时区间退化为单点 $\eta_od_e(S)$。所以 Definition 1 在 $\eta>1$ 时已经强制 $f$ monotone；在下文里 monotonicity **仅**通过 $d_e(S)\ge0$（以及由此得到的 $f(S)\ge f(\emptyset)=0$）起作用。
状态：`[VERIFIED-SYMBOLIC]`（脚本 C10a/C10b）。

---

## 3. (i) 的推导：value accuracy 不充分

### 3.1 构造 Instance A

**Step 3（构造）.** 固定 $\varepsilon\in(0,1)$。取 $N=\{1,2\}$（$n=2$；若需要更大的 $n$，追加任意多个 weight 为 $0$ 的 dummy 元素，monotone submodular 与下面所有等式都不变）。令 $f$ 为 modular：

$$f(S)=\mathbb 1[1\in S]+\varepsilon\cdot\mathbb 1[2\in S],$$

即 $f(\emptyset)=0,\ f(\{1\})=1,\ f(\{2\})=\varepsilon,\ f(\{1,2\})=1+\varepsilon$。定义 predictor

$$\tilde f(\emptyset)=0,\quad \tilde f(\{1\})=1,\quad \tilde f(\{2\})=\varepsilon,\quad \tilde f(\{1,2\})=1 .$$

**Step 4（$f$ 合法）.** modular 函数是 submodular 且（weights 非负）monotone，$f(\emptyset)=0$，$f\ge0$。
依据：Step 3 的定义。状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C5，对全部 $2^2$ 个集合与全部 $(S,T,e)$ 三元组穷举 monotone 与 diminishing returns）。

**Step 5（value accuracy 成立）.** 逐集合验：
- $S=\emptyset$：$0\le0\le0$。
- $S=\{1\}$：$\tilde f/f=1\in[1-\varepsilon,1+\varepsilon]$。
- $S=\{2\}$：$\tilde f/f=1\in[1-\varepsilon,1+\varepsilon]$。
- $S=\{1,2\}$：下侧需 $(1-\varepsilon)(1+\varepsilon)=1-\varepsilon^2\le1$，成立；上侧需 $1\le(1+\varepsilon)^2$，成立。

故 $\tilde f$ 在 level $\varepsilon$ 上 value-accurate。
依据：Step 3 的数值 + $\varepsilon\in(0,1)$。状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C5，$\varepsilon\in\{1/100,1/5,1/2,9/10\}$ 用 `Fraction` 精确验算）。

**Step 6（marginal gain 被抹平）.** 取 $S=\{1\}$、$e=2$：

$$d_2(\{1\})=f(\{1,2\})-f(\{1\})=\varepsilon>0,\qquad
\tilde d_2(\{1\})=\tilde f(\{1,2\})-\tilde f(\{1\})=1-1=0 .$$

依据：Step 3。状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C5 的 witness 输出，例如 $\varepsilon=1/5$ 时 witness 为 $([1],2,\tfrac15,0)$）。

**Step 7（不存在有限的 $(\eta_u,\eta_o)$）.** 设存在 $\eta_u,\eta_o\in(0,\infty)$ 使 Definition 1 成立。把它用在 Step 6 的 pair 上，下侧给

$$\frac{\varepsilon}{\eta_u}\le\tilde d_2(\{1\})=0 .$$

但 $\varepsilon>0$、$\eta_u>0$ 蕴含 $\varepsilon/\eta_u>0$，矛盾。故对任何有限的 $\eta_u$（从而对任何有限的 $\eta=\eta_u\eta_o$）Definition 1 都失败。
依据：Step 6 + convention B 的 Definition 1 + Q5 的量词。状态：`[HAND-PROOF-UNREVIEWED]`（一行不等式；其前提 Step 5、Step 6 是 `[VERIFIED-EXHAUSTIVE]`）。

注：这正是 definition1.md 里「$d_e(S)=0$ forces $\tilde d_e(S)=0$」那句话的逆否用法，convention B 还额外要求「$\tilde d_e(S)=0$ exactly when $d_e(S)=0$」，Step 6 违反的是后一半。

**Step 8（$L_K(\eta)$ 不可用）.** $L_K$ 的自变量按 notation.md 是一个数 $x$；由 Step 7，对 Instance A 不存在有限的 $\eta$ 可代入。若按 definition1.md 的约定把不可达的 error 记为 $\infty$，则 $L_K(\infty)=0$，界平凡。因此 value accuracy 单独不能产出任何非平凡的 $L_K(\eta)$ 型保证。
依据：Step 7 + notation.md 的 $L_K$ 定义 + definition1.md 的 $L_K(\infty)=0$ 约定。状态：`[HAND-PROOF-UNREVIEWED]`。

**Step 9（重标定救不回来）.** 对任何 $c>0$，$c\tilde f$ 的 marginal gain 是 $c\tilde d_e(S)$，在 Step 6 的 pair 上仍为 $0$，故 Step 7 的矛盾原样保留。并且 $\arg\max_e c\tilde d_e(S)=\arg\max_e\tilde d_e(S)$，predictive greedy 的运行轨迹与 $\eta^{\mathrm{sel}}$ 完全不变。所以 (i) 的失败不是 (ii)(iii) 那种 scale artifact。
依据：Step 6 + $c>0$。状态：`[HAND-PROOF-UNREVIEWED]`。

### 3.2 Instance B：把 (i) 加强到 $\eta^{\mathrm{sel}}=\infty$

Instance A 摧毁的是 Definition 1 的**假设**。下面这个实例进一步说明：value-accurate 的 predictor 可以让 predictive greedy 的一步选中 true gain 为 $0$ 的元素，而当时存在严格更好的候选，于是 selection error 也无穷。这一段是我加的加强，不是 (i) 的字面内容。

**Step 10（构造 Instance B）.** $N=\{1,2,3\}$，$K=2$，参数 $\varepsilon\in(0,1)$、$\delta>0$。取 coverage 型

$$f(S)=\mathbb 1[S\cap\{1,2\}\ne\emptyset]+\delta\cdot\mathbb 1[3\in S]$$

（元素 $1,2$ 覆盖同一个 weight 为 $1$ 的 item，元素 $3$ 覆盖一个 weight 为 $\delta$ 的独立 item），故 monotone submodular，$f(\emptyset)=0$。predictor：

$$\tilde f(\emptyset)=0,\ \ \tilde f(\{1\})=\tilde f(\{2\})=1-\varepsilon,\ \ \tilde f(\{3\})=(1+\varepsilon)\delta,$$
$$\tilde f(\{1,2\})=1+\varepsilon,\ \ \tilde f(\{1,3\})=\tilde f(\{2,3\})=(1-\varepsilon)(1+\delta),\ \ \tilde f(\{1,2,3\})=(1+\varepsilon)(1+\delta).$$

每个集合的 $\tilde f/f$ 都在 $\{1-\varepsilon,1,1+\varepsilon\}$ 里，故 value accuracy 成立。
状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C6，四组 $(\varepsilon,\delta)$ 全部 $2^3$ 个集合精确验算；同时确认所有 $\tilde d_e(S)\ge0$，即 predictor 不产生负 predicted gain）。

**Step 11（greedy 的两步）.** 条件

$$(1+\varepsilon)\delta\le1-\varepsilon\quad(\text{step }0),\qquad (1-\varepsilon)\delta\le2\varepsilon\quad(\text{step }1)$$

下（等号处用 adversarial tie-breaking）：
- $t=0$：$\tilde d_1(\emptyset)=\tilde d_2(\emptyset)=1-\varepsilon$，$\tilde d_3(\emptyset)=(1+\varepsilon)\delta$，adversary 选 $\{1,2\}$ 中一个，设为 $1$。
- $t=1$：$\tilde d_2(\{1\})=(1+\varepsilon)-(1-\varepsilon)=2\varepsilon$，$\tilde d_3(\{1\})=(1-\varepsilon)(1+\delta)-(1-\varepsilon)=(1-\varepsilon)\delta$。由第二个条件 greedy 选 $2$。

终态 $S^2=\{1,2\}$，$f(S^2)=1$；而 $F^{\mathrm{OPT}}=f(\{1,3\})=1+\delta$。ratio $=1/(1+\delta)$。
状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C6 用 DFS 枚举所有 argmax-consistent 的 tie 打破方式并取最坏，$\varepsilon=1/5,\delta=1/2$ 得 ratio $=2/3$）。

**Step 12（$\eta^{\mathrm{sel}}=\infty$）.** 在 $t=1$：$M_1=\max\{d_2(\{1\}),d_3(\{1\})\}=\max\{0,\delta\}=\delta>0$，而 $g_1=d_2(\{1\})=0$。按 definition1.md 的第三种情形 $a_1=\infty$，故 $\eta^{\mathrm{sel}}=\infty$，$L_K(\eta^{\mathrm{sel}})=L_K(\infty)=0$。
依据：Step 11 + selection error 的定义。状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C6）。

**Step 13（Instance B 违反 band 的哪一侧）.** 脚本的诊断输出显示，Instance B 里不存在 $\tilde d=0<d$ 的 pair，违反的是**上**侧：例如 $\varepsilon=1/5,\delta=1/2$ 时 $d_2(\{1\})=0$ 而 $\tilde d_2(\{1\})=2/5>0=\eta_o\cdot0$。所以 Instance A 与 Instance B 分工明确：A 给 (i) 的字面结论（下侧被破坏），B 给 $\eta^{\mathrm{sel}}=\infty$ 的加强（上侧被破坏）。两者都说明 value accuracy 不蕴含 Definition 1。
状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C6 的 band-violation 诊断项）。

### 3.3 (i) 末句的准确读法（重要）

我把「no bound of the form $L_K(\eta)$ follows from value accuracy alone」证成的是**非蕴含**命题：

> 不存在函数 $\eta:(0,1)\to[1,\infty)$，使得「$\tilde f$ 在 level $\varepsilon$ value-accurate」蕴含「$\tilde f$ 满足 Definition 1 且 global error $\le\eta(\varepsilon)$」。

它由 Step 7 直接得到（对 Instance A，**任何**有限值都不行）。

我**没有**证成下面这个更强的、容易被误读进去的命题：

> 对每个 $\varepsilon$ 与每个 $\eta$，存在 level $\varepsilon$ value-accurate 的实例使 predictive greedy 的 ratio 严格低于 $L_K(\eta)$。

反向的数值信息：在 $\varepsilon=1/5$ 上，Instance B 族能达到的最坏 ratio 是 $(1-\varepsilon)/(1+\varepsilon)=2/3$（见 Step 14），而 (iii) 对应的 $\eta=3/2$ 给 $L_2(3/2)=1-(1-\tfrac13)^2=5/9\approx0.5556<2/3$。也就是说这一族**没有**在数值上击穿 $L_2(3/2)$。我另外尝试把 Instance B 推广到 $K$ 个 decoy（$B=\{b_1,\dots,b_K\}$ 共享一个 unit item，$G=\{g_1,\dots,g_K\}$ 各占一个 $\delta$ item，predictor 取 $\tilde f(S)=u(|S\cap B|)+(1-\varepsilon)\delta|S\cap G|$，$u$ 从 $1-\varepsilon$ 线性升到 $1+\varepsilon$），发现每步可骗取的 fake gain 是 $2\varepsilon/(K-1)$，于是可容忍的 $\delta\le 2\varepsilon/((K-1)(1-\varepsilon))$，总损失 $(K-1)\delta\le2\varepsilon/(1-\varepsilon)$ 与 $K$ 无关：value band 的总宽度 $2\varepsilon f(S)$ 是一个**总预算**而不是每步预算。因此「value accuracy 是否本身蕴含某种乘性保证」不是我这次能闭合的问题，记入 §7 的未闭合清单。

**Step 14（Instance B 族的最坏 ratio）.** 令 $\delta^\star(\varepsilon)=\min\bigl\{\tfrac{1-\varepsilon}{1+\varepsilon},\ \tfrac{2\varepsilon}{1-\varepsilon}\bigr\}$。两个约束的交点由 $2\varepsilon(1+\varepsilon)=(1-\varepsilon)^2$ 即 $\varepsilon^2+4\varepsilon-1=0$ 给出，正根 $\varepsilon_0=\sqrt5-2\approx0.2360$。于是

$$\text{ratio}=\frac{1}{1+\delta^\star(\varepsilon)}=\begin{cases}\dfrac{1-\varepsilon}{1+\varepsilon}, & 0<\varepsilon\le\varepsilon_0,\\[2mm] \dfrac{1+\varepsilon}{2}, & \varepsilon_0\le\varepsilon<1.\end{cases}$$

状态：`[HAND-PROOF-UNREVIEWED]`（两端点在 $\varepsilon=\varepsilon_0$ 处同值 $\tfrac{\sqrt5-1}{2}\approx0.618$，脚本在 $\varepsilon\in\{1/10,1/8,1/5\}$ 上确认了第一支）。

---

## 4. (ii) 的推导：value accuracy 不必要

设 $M>0$，$f$ monotone submodular、$f(\emptyset)=0$、$f\not\equiv0$，$\tilde f=(1+M)f$。注意 $\tilde f(\emptyset)=0$ 自动成立。

**Step 15（Definition 1 以等号成立）.** 对任意 $S$、$e\notin S$，

$$\tilde d_e(S)=\tilde f(S\cup\{e\})-\tilde f(S)=(1+M)\bigl(f(S\cup\{e\})-f(S)\bigr)=(1+M)\,d_e(S).$$

取 $\eta_o=1+M$：上侧 $\tilde d_e(S)=\eta_od_e(S)\le\eta_od_e(S)$，取等。取 $\eta_u=1/(1+M)$：下侧 $d_e(S)/\eta_u=(1+M)d_e(S)=\tilde d_e(S)$，取等。两个因子都 $>0$，符合 convention B 的定义域。
依据：$\tilde f$ 的定义 + convention B 的 Definition 1。状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C7，$M\in\{1/100,1/2,3\}$，$n=4$ 的 weighted coverage $f$，全部 $(S,e)$ pair）。

**Step 16（$\eta=1$）.** $\eta=\eta_u\eta_o=\frac{1}{1+M}\cdot(1+M)=1$，满足 convention B 要求的 $\eta\ge1$（取边界）。
状态：`[VERIFIED-SYMBOLIC]`（脚本 C9a）。

**Step 17（convention B 是必需的）.** verbatim 版 Definition 1 要求 $\eta_u,\eta_o\ge1$，此时 $\eta_u=1/(1+M)<1$ 不合法，可用的最小合法对是 $(\eta_u,\eta_o)=(1,1+M)$，给出 $\eta=1+M>1$，(ii) 的「$\eta=1$」结论就失效。所以 (ii) 的 punchline 恰恰依赖 convention B 取消 floor 这一改动。
依据：definition1.md 的 verbatim 段与 convention B 段的对照。状态：`[HAND-PROOF-UNREVIEWED]`。

**Step 18（value accuracy 在每个 $\varepsilon<M$ 失败）.** 由 $f\not\equiv0$ 与 $f\ge0$，存在 $S^\dagger$ 使 $f(S^\dagger)>0$。则

$$\tilde f(S^\dagger)=(1+M)f(S^\dagger)>(1+\varepsilon)f(S^\dagger)\quad\Longleftrightarrow\quad M>\varepsilon,$$

上侧被违反。故对每个 $\varepsilon\in(0,M)\cap(0,1)$ value accuracy 失败。（在 $\varepsilon=M$ 且 $M<1$ 处上侧取等、下侧 $(1-M)f\le(1+M)f$ 显然，value accuracy 恰好成立，所以 Q9 里的严格不等号不可放宽。）取 $M\ge1$ 即得：存在 predictor 在**任何** level $\varepsilon\in(0,1)$ 上都不 value-accurate 却有 $\eta=1$。
依据：$f\not\equiv0$（Q8）+ Step 15。状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C7 在 $\varepsilon\in\{M/2,\,0.99M,\,M\}$ 上确认前两者失败、第三者成立）。

**Step 19（argmax 保持）.** 映射 $x\mapsto(1+M)x$ 在 $\mathbb R$ 上严格单调递增（$1+M>0$）。对固定 state $S^t$，候选集合都是同一个 $\{e:e\notin S^t\}$，故

$$\arg\max_{e\notin S^t}\tilde d_e(S^t)=\arg\max_{e\notin S^t}d_e(S^t)\quad(\text{作为集合相等}).$$

因此无论 tie 如何打破（包括 adversarial），被选中的 $e_t$ 必落在 true gain 的 argmax 里，即 $g_t=M_t$。
依据：Step 15 + 严格单调性。状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C7 对全部 $2^4$ 个 state 逐一比较两个 argmax 集合）。

**Step 20（$\eta^{\mathrm{sel}}=1$）.** 对每个 $t$：若 $g_t>0$，则 $a_t=M_t/g_t=1$；若 $M_t=g_t=0$，则按定义 $a_t=1$；第三种情形 $g_t=0<M_t$ 由 Step 19 排除（$g_t=M_t$）。故 $\eta^{\mathrm{sel}}=\max\{1,1,\dots,1\}=1$，对每个 $1\le K\le n$ 成立。相应地 $L_K(\eta^{\mathrm{sel}})=L_K(1)=1-(1-1/K)^K\ge1-e^{-1}$。
依据：Step 19 + selection error 定义的三分情形 + monotonicity 给出的 $M_t\ge0$。状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C7 对 $K=1,2,3,4$ 枚举全部 tie 打破方式，均得 $\eta^{\mathrm{sel}}=1$，且终值与直接在 $f$ 上跑 greedy 的最坏终值逐点相等）。

**Step 21（(ii) 的结论形式）.** (i)+(ii) 合起来：value accuracy 既不是 predictive greedy 有保证的充分条件（Step 7/8），也不是必要条件（Step 18 + Step 20）。

---

## 5. (iii) 的推导：重标定后必要性恢复

设 $\tilde f$ 对 monotone 的 $f$ 有 error $(\eta_u,\eta_o)$，$\eta=\eta_u\eta_o\ge1$，$f(\emptyset)=\tilde f(\emptyset)=0$。

**Step 22（set-level band）.** 固定 $S=\{e_1,\dots,e_m\}$ 与任一枚举顺序，$S_i$ 如 Step 1。对 $f$ 与 $\tilde f$ 分别用 Step 1（两者都在 $\emptyset$ 取 $0$）：

$$f(S)=\sum_{i=1}^m d_{e_i}(S_{i-1}),\qquad \tilde f(S)=\sum_{i=1}^m \tilde d_{e_i}(S_{i-1}).$$

对每一项用 Definition 1（$e_i\notin S_{i-1}$ 成立，因为枚举无重复）：$d_{e_i}(S_{i-1})/\eta_u\le\tilde d_{e_i}(S_{i-1})\le\eta_o d_{e_i}(S_{i-1})$。逐项求和（有限和，不等式可加）：

$$\boxed{\ \frac{f(S)}{\eta_u}\ \le\ \tilde f(S)\ \le\ \eta_o\,f(S)\ }\qquad\forall S\subseteq N .$$

**用到了什么**：Step 1 的裂项（只需 $f(\emptyset)=\tilde f(\emptyset)=0$）、Definition 1 的逐 pair band、以及 $\eta_u>0$ 使 $1/\eta_u$ 有意义。**没有用到** submodularity；也没有用到 $d_{e_i}\ge0$，因为不等式是逐项相加而不是逐项取绝对值。monotonicity 只在 Step 2 的意义上起作用（保证 band 非空、保证 $f(S)\ge0$ 从而 $(1\pm\varepsilon)f(S)$ 是常规的相对带）。求和结果与枚举顺序无关，因为左右两端都不依赖顺序。
状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C8 的 setband 项，三种 split；C11 在 monotone 非 submodular 的 $f(S)=|S|^2$ 上对 $4\times2^3$ 个 in-band predictor 逐一确认）。

**Step 23（把 $c$ 与 $\varepsilon$ 解出来，而不是猜出来）.** 要求存在 $c>0$ 与尽可能小的 $\varepsilon$ 使 $c\tilde f$ 在 level $\varepsilon$ value-accurate。把 Step 22 乘以 $c>0$：

$$\frac{c}{\eta_u}f(S)\ \le\ c\tilde f(S)\ \le\ c\,\eta_o f(S).$$

由于（对 $f(S)>0$ 的 $S$）这两端是能被 band 取到的最紧边界，充分条件即

$$\frac{c}{\eta_u}\ \ge\ 1-\varepsilon\qquad\text{且}\qquad c\,\eta_o\ \le\ 1+\varepsilon .$$

等价地 $\varepsilon\ge\max\{\,\underbrace{1-c/\eta_u}_{=:A(c)},\ \underbrace{c\eta_o-1}_{=:B(c)}\,\}$。$A$ 关于 $c$ 严格递减（导数 $-1/\eta_u<0$），$B$ 严格递增（导数 $\eta_o>0$），故 $\max\{A,B\}$ 是 $c$ 的严格拟凸函数，最小值在 $A(c)=B(c)$ 处取到：

$$1-\frac{c}{\eta_u}=c\eta_o-1\ \Longrightarrow\ c\Bigl(\eta_o+\frac1{\eta_u}\Bigr)=2\ \Longrightarrow\ c=\frac{2}{\eta_o+1/\eta_u}=\frac{2\eta_u}{\eta_u\eta_o+1}=\frac{2\eta_u}{\eta+1},$$

对应的最小 level

$$\varepsilon=B(c)=\frac{2\eta_u\eta_o}{\eta+1}-1=\frac{2\eta-(\eta+1)}{\eta+1}=\frac{\eta-1}{\eta+1}.$$

依据：Step 22 + 一元极小化。状态：`[VERIFIED-SYMBOLIC]`（脚本 C3a–C3d：sympy 解出的平衡点与 $c$ 恒等，平衡值与 $\varepsilon$ 恒等，两个单调性由导数确认）。

**Step 24（代回验证，两侧都取等）.**

$$\frac{c}{\eta_u}=\frac{2}{\eta+1}=1-\frac{\eta-1}{\eta+1}=1-\varepsilon,\qquad
c\,\eta_o=\frac{2\eta_u\eta_o}{\eta+1}=\frac{2\eta}{\eta+1}=1+\frac{\eta-1}{\eta+1}=1+\varepsilon .$$

代入 Step 22 得对每个 $S\subseteq N$

$$(1-\varepsilon)f(S)=\frac{c}{\eta_u}f(S)\ \le\ c\tilde f(S)\ \le\ c\eta_of(S)=(1+\varepsilon)f(S).$$

状态：`[VERIFIED-SYMBOLIC]`（脚本 C1a/C1b，$\eta_u,\eta_o$ 为正号符号量，两式化简后恒为 $0$）。

**Step 25（$\varepsilon$ 的取值范围）.** $\varepsilon(\eta)=\frac{\eta-1}{\eta+1}$ 在 $\eta\ge1$ 上：$\varepsilon(1)=0$；$\varepsilon'(\eta)=\frac{2}{(\eta+1)^2}>0$ 严格递增；$\lim_{\eta\to\infty}\varepsilon=1$ 且对每个有限 $\eta$ 有 $\varepsilon<1$。故 $\varepsilon\in[0,1)$，与陈述一致。边界情形 $\eta=1$：$\varepsilon=0$，Step 24 给 $c\tilde f(S)=f(S)$ 对每个 $S$ 成立（$c\tilde f$ 与 $f$ 逐点相等），这比 value accuracy 强，且蕴含任何 level $\varepsilon'\in(0,1)$ 上的 value accuracy；因为 value accuracy 的定义域是 $(0,1)$，这个端点需要单独说明（Q14）。
状态：`[VERIFIED-SYMBOLIC]`（脚本 C2a–C2d）。

**Step 26（重标定后的两个因子）.** 由 $c\tilde d_e(S)\ge c\,d_e(S)/\eta_u=d_e(S)/(\eta_u/c)$ 与 $c\tilde d_e(S)\le c\eta_od_e(S)$，$c\tilde f$ 的 error 因子是

$$(\eta_u',\eta_o')=\Bigl(\frac{\eta_u}{c},\ c\eta_o\Bigr)=\Bigl(\frac{\eta+1}{2},\ \frac{2\eta}{\eta+1}\Bigr)=\Bigl(\frac{1}{1-\varepsilon},\ 1+\varepsilon\Bigr),\qquad \eta_u'\eta_o'=\eta .$$

也就是说 $c$ 的作用是把 band 摆正成 $[(1-\varepsilon)d,\ (1+\varepsilon)d]$，然后 Step 1 的裂项把逐 pair 的对称 band 直接抬成集合层面的对称 band。这是 (iii) 的另一种等价叙述。
状态：`[VERIFIED-SYMBOLIC]`（脚本 C4a–C4d）。

**Step 27（$c$ 与 $\varepsilon$ 在最坏情形下不可改进）.** 这是我加的补充命题（不在 (iii) 的字面内容里）。取 $N=\{1,2\}$、$f(S)=|S|$、$\tilde f(\emptyset)=0$、$\tilde f(\{1\})=1/\eta_u$、$\tilde f(\{2\})=\eta_o$、$\tilde f(\{1,2\})=1/\eta_u+\eta_o$。逐 pair 检查：$\tilde d_1(\emptyset)=1/\eta_u$（下侧取等），$\tilde d_2(\{1\})=\eta_o$（上侧取等），$\tilde d_2(\emptyset)=\eta_o$（上侧取等），$\tilde d_1(\{2\})=1/\eta_u$（下侧取等），全部合法。对任何 $c'>0$，$S=\{1\}$ 的下侧要求 $c'/\eta_u\ge1-\varepsilon'$，$S=\{2\}$ 的上侧要求 $c'\eta_o\le1+\varepsilon'$，正是 Step 23 的两条约束，故最小可行 level 恰为 $\varepsilon=(\eta-1)/(\eta+1)$，唯一最优 scale 恰为 $c=2\eta_u/(\eta+1)$。
状态：`[VERIFIED-SYMBOLIC]` + `[VERIFIED-EXHAUSTIVE]`（脚本 C3 给最优化部分，C8 在 $\eta=3/2$ 的具体实例上确认上下两侧同时取等，故该实例上 $\varepsilon=1/5$ 无法降低）。

**Step 28（(iii) 只用了什么）.** 按陈述要求明确列出：
1. **monotonicity of $f$**：只通过 $d_e(S)\ge0$ 使用（Step 2），保证 Definition 1 的 band 非空（$\eta>1$ 时这是强制的）并保证 $f(S)\ge0$。Step 22–Step 24 的代数链条本身与 $d_e(S)$ 的符号无关。
2. **$f(\emptyset)=\tilde f(\emptyset)=0$**：Step 1 裂项的锚点，两个函数都要在 $\emptyset$ 取 $0$，否则 set-level band 里会多出一个常数偏移。
3. **Definition 1 的逐 pair band**（convention B，$\eta_u,\eta_o>0$）。
4. **不需要 submodularity**：Step 22 的求和对任意集合函数成立。独立佐证：`[VERIFIED-EXHAUSTIVE]` 脚本 C11 在 $f(S)=|S|^2$（monotone，穷举确认非 submodular）上对 $4$ 组 $(\eta_u,\eta_o)$ × $2^3$ 种 in-band predictor，全部满足 set-level band 与 $c\tilde f$ 的 value accuracy。
5. **不需要 $K$、不需要 greedy、不需要 adversarial tie-breaking**：(iii) 是关于函数对 $(f,\tilde f)$ 的陈述，对所有 $2^n$ 个集合成立，与算法无关。

---

## 6. 数值 walk-through

### 6.1 (iii) 在 $K=3$、$\eta=3/2$

取 $\eta=3/2$，则

$$\varepsilon=\frac{\eta-1}{\eta+1}=\frac{1/2}{5/2}=\frac15,\qquad c=\frac{2\eta_u}{\eta+1}=\frac{2\eta_u}{5/2}=\frac{4\eta_u}{5}.$$

实例：$N=\{1,2,3\}$，$K=3$，$f$ modular，weights $w=(3,2,1)$。三种 split 都给同一个 $\varepsilon=1/5$：

| split $(\eta_u,\eta_o)$ | $c$ | $\tilde f$ 的 weights | $c\tilde f(\{1\})$ vs $[0.8\cdot3,\,1.2\cdot3]$ | $c\tilde f(\{2,3\})$ vs $[0.8\cdot3,\,1.2\cdot3]$ |
|---|---|---|---|---|
| $(1,\tfrac32)$ | $4/5$ | $(9/2,\,2,\,1)$ | $18/5=3.6$，上侧取等 | $12/5=2.4$，下侧取等 |
| $(\tfrac32,1)$ | $6/5$ | $(3,\,4/3,\,2/3)$ | $18/5=3.6$，上侧取等 | $12/5=2.4$，下侧取等 |
| $(\tfrac34,2)$ | $3/5$ | $(6,\,8/3,\,4/3)$ | $18/5=3.6$，上侧取等 | $12/5=2.4$，下侧取等 |

（三行的 predictor 都取「元素 $1$ 乘 $\eta_o$、元素 $2,3$ 除以 $\eta_u$」，故上下两侧同时被取到；$f(\{2,3\})=3$，带为 $[\tfrac45\cdot3,\tfrac65\cdot3]=[2.4,3.6]$。）

第一行逐集合展开（$\eta_u=1,\eta_o=3/2,c=4/5$，predictor 把元素 $1$ 放大 $3/2$、元素 $2,3$ 保持不变）：

| $S$ | $f(S)$ | $\tilde f(S)$ | $f/\eta_u=f$ | $\eta_of=\tfrac32f$ | $c\tilde f(S)$ | $[(1-\varepsilon)f,(1+\varepsilon)f]=[\tfrac45f,\tfrac65f]$ |
|---|---|---|---|---|---|---|
| $\emptyset$ | $0$ | $0$ | $0$ | $0$ | $0$ | $[0,0]$ |
| $\{1\}$ | $3$ | $9/2$ | $3$ | $9/2$ | $18/5$ | $[12/5,\,18/5]$ 上端取等 |
| $\{2\}$ | $2$ | $2$ | $2$ | $3$ | $8/5$ | $[8/5,\,12/5]$ 下端取等 |
| $\{3\}$ | $1$ | $1$ | $1$ | $3/2$ | $4/5$ | $[4/5,\,6/5]$ 下端取等 |
| $\{1,2\}$ | $5$ | $13/2$ | $5$ | $15/2$ | $26/5$ | $[4,\,6]$ |
| $\{1,3\}$ | $4$ | $11/2$ | $4$ | $6$ | $22/5$ | $[16/5,\,24/5]$ |
| $\{2,3\}$ | $3$ | $3$ | $3$ | $9/2$ | $12/5$ | $[12/5,\,18/5]$ 下端取等 |
| $\{1,2,3\}$ | $6$ | $15/2$ | $6$ | $9$ | $6$ | $[24/5,\,36/5]$ |

上下两侧都被取到（$\{1\}$ 取上端，$\{2\},\{3\},\{2,3\}$ 取下端），故在这个实例上 $\varepsilon=1/5$ 不能降低（Step 27）。
状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C8）。

### 6.2 (ii) 在 $K=3$

取 $M=1/2$，$\tilde f=\tfrac32f$，$(\eta_u,\eta_o)=(2/3,3/2)$，$\eta=1$。实例：$N=\{1,2,3,4\}$，coverage，$\mathrm{cov}(1)=\{a,b\}$，$\mathrm{cov}(2)=\{b,c\}$，$\mathrm{cov}(3)=\{c,d\}$，$\mathrm{cov}(4)=\{d\}$，weights $w_a=3,w_b=1,w_c=2,w_d=1$，故 $f(\{1\})=4,f(\{2\})=3,f(\{3\})=3,f(\{4\})=1$。

$K=3$ 的运行（predicted gain 全部是 true gain 的 $3/2$ 倍，argmax 逐点相同）：

| $t$ | $S^t$ | true gains $d_e(S^t)$ | predicted gains $\tilde d_e(S^t)$ | 选中 | $M_t$ | $g_t$ | $a_t$ |
|---|---|---|---|---|---|---|---|
| $0$ | $\emptyset$ | $1{:}4,\ 2{:}3,\ 3{:}3,\ 4{:}1$ | $6,\ 9/2,\ 9/2,\ 3/2$ | $1$ | $4$ | $4$ | $1$ |
| $1$ | $\{1\}$ | $2{:}2,\ 3{:}3,\ 4{:}1$ | $3,\ 9/2,\ 3/2$ | $3$ | $3$ | $3$ | $1$ |
| $2$ | $\{1,3\}$ | $2{:}0,\ 4{:}0$ | $0,\ 0$ | $2$（adversarial） | $0$ | $0$ | $1$ |

$\eta^{\mathrm{sel}}=\max\{1,1,1,1\}=1$，终值 $f(\{1,2,3\})=7=F^{\mathrm{OPT}}$。第 $t=2$ 步正是 definition1.md 的 $M_t=g_t=0$ 情形（算法恒执行 $K$ 步，该步 predicted gain 为 $0$ 仍然选）。value accuracy 方面：$\tilde f(\{1\})=6>(1+\varepsilon)\cdot4$ 当且仅当 $\varepsilon<1/2=M$，故每个 $\varepsilon<1/2$ 都失败。
交叉验证（Step 25 与 (ii) 的一致性）：$\eta=1\Rightarrow\varepsilon=0$ 且 $c=2\eta_u/(\eta+1)=2\cdot\tfrac23/2=\tfrac23$，而 $c\tilde f=\tfrac23\cdot\tfrac32f=f$，逐点相等，与 Step 25 的端点结论吻合。
状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C7、C9c）。

### 6.3 (i) 在 $K=2$

（本 proposition 不含 ProbeLottery item；任务模板里「$K=2$ for the ProbeLottery item」在此处无对应对象，故把 $K=2$ 用于 (i) 的 greedy walk-through，理由记在 §7。）

取 $\varepsilon=1/5$。

**Instance A**（$n=2$，与 $K$ 无关）：$f=(0,1,\tfrac15,\tfrac65)$ 于 $(\emptyset,\{1\},\{2\},\{1,2\})$，$\tilde f=(0,1,\tfrac15,1)$。value accuracy：$\{1,2\}$ 处需 $\tfrac45\cdot\tfrac65=\tfrac{24}{25}\le1\le\tfrac65\cdot\tfrac65=\tfrac{36}{25}$，成立。关键 pair：$d_2(\{1\})=\tfrac15>0$ 而 $\tilde d_2(\{1\})=0$，于是下侧要求 $\tfrac15/\eta_u\le0$，对任何 $\eta_u>0$ 不可能。

**Instance B**（$n=3$，$K=2$，$\delta=\delta^\star(1/5)=\tfrac{2\varepsilon}{1-\varepsilon}=\tfrac12$）：

| $S$ | $\emptyset$ | $\{1\}$ | $\{2\}$ | $\{3\}$ | $\{1,2\}$ | $\{1,3\}$ | $\{2,3\}$ | $\{1,2,3\}$ |
|---|---|---|---|---|---|---|---|---|
| $f$ | $0$ | $1$ | $1$ | $1/2$ | $1$ | $3/2$ | $3/2$ | $3/2$ |
| $\tilde f$ | $0$ | $4/5$ | $4/5$ | $3/5$ | $6/5$ | $6/5$ | $6/5$ | $9/5$ |
| $\tilde f/f$ | – | $4/5$ | $4/5$ | $6/5$ | $6/5$ | $4/5$ | $4/5$ | $6/5$ |

全部落在 $[4/5,6/5]=[1-\varepsilon,1+\varepsilon]$，value accuracy 成立。运行：
- $t=0$：$\tilde d_1(\emptyset)=\tilde d_2(\emptyset)=4/5$，$\tilde d_3(\emptyset)=3/5$，选 $1$。
- $t=1$：$\tilde d_2(\{1\})=6/5-4/5=2/5$，$\tilde d_3(\{1\})=6/5-4/5=2/5$，adversarial tie 选 $2$。
- 终态 $\{1,2\}$，$f=1$；$F^{\mathrm{OPT}}=f(\{1,3\})=3/2$；ratio $=2/3=(1-\varepsilon)/(1+\varepsilon)$。
- $t=1$ 的 selection error：$M_1=\max\{d_2(\{1\}),d_3(\{1\})\}=\max\{0,\tfrac12\}=\tfrac12>0$，$g_1=0$，故 $a_1=\infty$，$\eta^{\mathrm{sel}}=\infty$，$L_2(\infty)=0$。

对照：$L_2(3/2)=1-(1-\tfrac13)^2=\tfrac59\approx0.5556$，$L_2(1)=1-(1-\tfrac12)^2=\tfrac34$，$L_3(3/2)=1-(\tfrac79)^3=\tfrac{386}{729}\approx0.5295$，$L_3(1)=1-(\tfrac23)^3=\tfrac{19}{27}\approx0.7037$。本实例 ratio $2/3$ 高于 $L_2(3/2)$，故它摧毁的是 Definition 1 的**假设**与 $\eta^{\mathrm{sel}}$，不是某个具体 $L_K$ 数值（见 §3.3）。
状态：`[VERIFIED-EXHAUSTIVE]`（脚本 C5、C6）。

---

## 7. 未闭合项、加入的假设、与输入文件的出入

**G1（加入的实质前提，(i)）**：(i) 的字面陈述没有写 $n\ge2$，但 $n=1$ 时 (i) 为假（Q2 已给出一行论证）。我按「选保守选项」的规则把构造放在 $n=2$（可用 weight $0$ 的 dummy 元素扩到任意 $n\ge2$），并把 $n\ge2$ 明确列为前提。状态：`[HAND-PROOF-UNREVIEWED]`（$n=1$ 的反向论证）。

**G2（(i) 末句的强度）**：我证成的是非蕴含（不存在有限 $\eta$），**没有**证成「value accuracy 下 greedy 的 ratio 可以低于任意给定的 $L_K(\eta)$」。我的 $K$ 步推广尝试显示 value band 的总宽度 $2\varepsilon f(S)$ 是总预算而非每步预算，Instance B 族在 $K=2$、$\varepsilon=1/5$ 处的最坏 ratio $2/3$ 高于 $L_2(3/2)=5/9$。**开放问题**：value accuracy at level $\varepsilon$ 本身是否蕴含某个 $\varepsilon,K$ 的乘性保证（形如 $\rho\ge\phi(\varepsilon,K)>0$），以及该保证与 $L_K\bigl(\tfrac{1+\varepsilon}{1-\varepsilon}\bigr)$ 的关系。状态：`[CONJECTURE]`（两个方向都无证明；时间盒到点，未继续）。

**G3（definition1.md 的 scaling 方向与 (ii) 不自洽）**：definition1.md 的 convention B 段写「multiplying $\tilde f$ by $c>0$ maps $(\eta_u,\eta_o)\to(c\eta_u,\eta_o/c)$」。按 Definition 1 直接计算：$c\tilde d\ge c\,d/\eta_u=d/(\eta_u/c)$ 且 $c\tilde d\le(c\eta_o)d$，故正确的映射是 $(\eta_u,\eta_o)\to(\eta_u/c,\ c\eta_o)$，两个因子的位置与文件所写相反。检验：(ii) 里 $\tilde f=(1+M)f$ 是 $f$（其 $(\eta_u,\eta_o)=(1,1)$）乘以 $c=1+M$，(ii) 给出的答案是 $(\tfrac1{1+M},1+M)$，与我的映射一致，与文件所写的 $(c\cdot1,1/c)=(1+M,\tfrac1{1+M})$ 相反。product $\eta$ 在两种写法下都不变，所以这条对本 proposition 的三条结论没有影响，但 definition1.md 那一句本身需要修正。状态：`[VERIFIED-SYMBOLIC]`（脚本 C4，以及 C9c 的一致性交叉验证）。**这是本次盲证发现的唯一一处输入文件内部不一致，建议回写。**

**G4（verbatim Definition 1 与 convention B 的张力）**：verbatim 段写「$\eta_u,\eta_o\ge1$」以及「all predicted gains are nonnegative」。Instance B 的 predictor 满足 $\tilde d_e(S)\ge0$（脚本已确认），但 Instance A 与 Instance B 都不满足 band，这不构成矛盾；只是提醒 (ii) 的 $\eta=1$ 结论严格依赖 convention B 取消 floor（Step 17）。状态：`[HAND-PROOF-UNREVIEWED]`。

**G5（(iii) 里 monotonicity 的实际用途）**：陈述说「No submodularity of $f$ is used in (iii)」，但没说 monotonicity 用在哪里。我的推导显示代数链条（Step 22–24）与 $d_e(S)$ 的符号无关，monotonicity 只用于 Step 2 的 band 自洽与 $f(S)\ge0$。若把 (iii) 中的 monotone 换成任意集合函数，Step 22–24 的**不等式链仍然成立**，只是当 $\eta>1$ 且某个 $d_e(S)<0$ 时 Definition 1 的前提本身空洞。按「空洞性检验」，monotone 这个限定词**不能删**，但它的作用需要在正文或脚注里用一句话说清：它保证 band 非空、保证 $(1\pm\varepsilon)f(S)$ 是围绕非负数的相对带。状态：`[VERIFIED-SYMBOLIC]`（C10）+ `[VERIFIED-EXHAUSTIVE]`（C11 的非 submodular 实例）。

**G6（任务模板里的 ProbeLottery 条目）**：任务要求「(3) 数值 walk-through 在 $K=3,\eta=3/2$，ProbeLottery item 用 $K=2$」。prop:valueacc 的三条里没有 ProbeLottery 这个对象（statement_valueacc.md 通篇没有该词）。我按保守处理：不去别的文件查它是什么（违反隔离要求），把 $K=2$ 用在 (i) 的 greedy walk-through 上（(i) 的 Instance B 本来就需要 $K=2$），并在此记录该条目在本 proposition 下无对应物。

**G7（时间盒）**：G2 的 $K$ 步推广尝试在约 20 分钟后停止，按规则记录状态并继续，没有继续追问。

**没有发现的问题**：(i)(ii)(iii) 三条的字面陈述（在 G1 的 $n\ge2$ 补充之后）与我的独立推导逐条吻合，$c=2\eta_u/(\eta+1)$ 与 $\varepsilon=(\eta-1)/(\eta+1)$ 是我从极小化问题解出来的，与陈述给的常数完全相同，且在最坏情形下不可改进（Step 27）。

---

## 8. 状态标签汇总

| 结论 | 状态 | 依据 |
|---|---|---|
| (i) Instance A 是 monotone submodular 且 value-accurate | `[VERIFIED-EXHAUSTIVE]` | C5，$\varepsilon\in\{1/100,1/5,1/2,9/10\}$，`Fraction` |
| (i) 存在 $(S,e)$：$\tilde d=0<d$ | `[VERIFIED-EXHAUSTIVE]` | C5 |
| (i) 不存在有限 $(\eta_u,\eta_o)$ | `[HAND-PROOF-UNREVIEWED]` | Step 7（一行），前提已 oracle 确认 |
| (i) 加强：存在 value-accurate 实例使 $\eta^{\mathrm{sel}}=\infty$ | `[VERIFIED-EXHAUSTIVE]` | C6，全部 tie 打破方式枚举 |
| (i) 重标定救不回来 | `[HAND-PROOF-UNREVIEWED]` | Step 9 |
| (i) 末句「no $L_K(\eta)$ bound」按非蕴含读 | `[HAND-PROOF-UNREVIEWED]` | Step 8 + §3.3 |
| (i) 强版本（ratio 可低于任意 $L_K(\eta)$） | `[CONJECTURE]` | 未证；G2 |
| (ii) band 以等号成立，$\eta=1$ | `[VERIFIED-EXHAUSTIVE]` + `[VERIFIED-SYMBOLIC]` | C7, C9a |
| (ii) value accuracy 在每个 $\varepsilon<M$ 失败 | `[VERIFIED-EXHAUSTIVE]` | C7 |
| (ii) argmax 保持，$\eta^{\mathrm{sel}}=1$ | `[VERIFIED-EXHAUSTIVE]` | C7，$K=1,2,3,4$ |
| (iii) set-level band | `[VERIFIED-EXHAUSTIVE]` | C8, C11 |
| (iii) $c,\varepsilon$ 的解出与代回 | `[VERIFIED-SYMBOLIC]` | C1, C3 |
| (iii) $\varepsilon\in[0,1)$ 与端点 | `[VERIFIED-SYMBOLIC]` | C2 |
| (iii) 重标定后因子 $(\tfrac1{1-\varepsilon},1+\varepsilon)$ | `[VERIFIED-SYMBOLIC]` | C4 |
| (iii) $c,\varepsilon$ 最坏情形不可改进 | `[VERIFIED-SYMBOLIC]` + `[VERIFIED-EXHAUSTIVE]` | C3, C8 |
| (iii) 不用 submodularity | `[VERIFIED-EXHAUSTIVE]` | C11，$f(S)=|S|^2$ |
| definition1.md 的 scaling 映射方向写反 | `[VERIFIED-SYMBOLIC]` | C4 + C9c |

脚本总计 122 项检查，全部通过，无 `[FAILED]` 项。

---

## 9. 读取的文件

盲证过程中只打开了以下四个文件（绝对路径）：

1. `/home/user/sub-modular-optimization/results/V11/inputs/definition1.md`
2. `/home/user/sub-modular-optimization/results/V11/inputs/assumptions.md`
3. `/home/user/sub-modular-optimization/results/V11/inputs/notation.md`
4. `/home/user/sub-modular-optimization/results/V11/inputs/statement_valueacc.md`

以及 `/home/user/sub-modular-optimization/CLAUDE.md`（由 harness 自动注入上下文，非主动打开）。本次新建的文件只有 `results/V11/route2/valueacc.md` 与 `results/V11/route2/verify_valueacc.py`，没有修改仓库中任何既有文件，没有运行 git。

# ROUTE-TWO 独立推导：prop:necessity（no bound, no guarantee），TASKS11 Q1 / ledger T1

本文件是 blind route-two 推导。只使用 `results/V11/inputs/` 下四个输入文件中的定义，其余仓库内容未打开。所有数值判定用 `fractions.Fraction` 或 sympy 精确算术，浮点仅出现在打印里。可复现脚本：`results/V11/route2/verify_nobound.py`。

---

## 1. 陈述复述（每个量词显式写出）

原文（`statement_nobound.md`）：

```latex
If no upper bound on $\eta$ is assumed, then for every deterministic algorithm with
arbitrary query access to $\tilde f$ and every $n\ge2K$ there are pairs $(f,\tilde f)$
on which the output $T$ satisfies $f(T)\le\tfrac{K}{n-K}\,f(O^{\ast})$.
Consequently no constant worst-case ratio is achievable without an error assumption.
```

我的复述（量词逐条列出）：

- **(Q1) 预先固定的参数**：整数 $K\ge1$ 与整数 $n$，满足 $n\ge 2K$（由 `assumptions.md` 还有 $1\le K\le n$，$n\ge 2K$ 蕴含之）。$N$ 是 $|N|=n$ 的 ground set。
- **(Q2) 全称，算法**：对**每一个** deterministic algorithm $\mathcal A$。deterministic 的含义：$\mathcal A$ 不使用内部随机性，其 query 序列与最终输出是已收到的 oracle 回答的确定函数。
- **(Q3) 全称，query 能力**：$\mathcal A$ 对 $\tilde f$ 有 **arbitrary query access**。本推导采用最强解释：$\mathcal A$ 可以做任意多次（含 $2^{n}$ 次，即读遍整张值表）、任意自适应的 query，query 的形式也不限于 value query；极限情形是直接把整个函数 $\tilde f$ 作为输入交给 $\mathcal A$。$\mathcal A$ 另外免费知道 $n$、$K$、以及下面构造的整个 instance family 的描述。$\mathcal A$ **不能** query $f$（`assumptions.md`：the algorithm cannot evaluate $f$）。
- **(Q4) 输出的 query size / 可行性**：输出 $T\subseteq N$ 必须满足 cardinality budget，即 $|T|\le K$。
- **(Q5) 存在，instance**：**存在** pair $(f,\tilde f)$，其中 $f:2^{N}\to\mathbb R_{\ge0}$ monotone submodular 且 $f(\emptyset)=0$，$\tilde f:2^{N}\to\mathbb R$ 且 $\tilde f(\emptyset)=0$，$(f,\tilde f)$ 满足 Definition 1（convention B）中的 marginal-gain error 条件，误差参数 $(\eta_u,\eta_o)$ 有限但**不受任何预先给定的上界约束**，$\eta=\eta_u\eta_o\ge1$。
- **(Q6) 结论**：在该 instance 上 $\mathcal A$ 的输出 $T$ 满足 $f(T)\le\frac{K}{n-K}f(O^{\ast})$，其中 $O^{\ast}$ 是 $f$ 的一个 optimal $K$-set，$F^{\mathrm{OPT}}=f(O^{\ast})$。
- **(Q7) $\eta$ 与 $K$ 的定义域**：$K\in\mathbb Z_{\ge1}$；$\eta_u,\eta_o>0$ 且 $\eta=\eta_u\eta_o\ge1$（convention B）。本构造给出的 $\eta$ 依赖 $n,K$，见第 5 节。
- **(Q8) tie breaking**：本命题针对 arbitrary deterministic algorithm，不涉及 greedy 的 tie breaking；若把 $\mathcal A$ 特化为 predictive greedy，则本构造需要 **adversarial tie breaking**（见第 8 节 Step 11），这与 `assumptions.md` 中 "ties broken adversarially in all worst-case statements" 一致。
- **(Q9) 结论的第二句**：对固定的 $K$，令 $n\to\infty$，$\frac{K}{n-K}\to0$，故不存在与 $n$ 无关的常数 $\alpha\in(0,1]$ 使某个 deterministic algorithm 在所有（无 $\eta$ 上界的）instance 上达到 $F^{\mathrm{ALG}}\ge\alpha F^{\mathrm{OPT}}$。

**量词的作用次序（关键）**：$\forall\mathcal A\ \forall(n,K:n\ge2K)\ \exists(f,\tilde f)$。instance 在算法之后选取，因此 adversary 可以先算出 $\mathcal A$ 的输出再挑 $f$。这一点是整个证明的杠杆。

---

## 2. 构造（instance family）

固定 $n\ge 2K\ge2$。令

$$w\;=\;\frac{K}{n-K}\;\in(0,1],$$

（$n\ge2K$ 保证 $n-K\ge K\ge1$，故 $0<w\le1$；$w=1$ 当且仅当 $n=2K$。）

对每个 $A\subseteq N$ 且 $|A|=K$，定义

$$f_A(S)\;=\;|S\cap A|\;+\;w\,|S\setminus A|\;=\;\sum_{e\in S}w_e,\qquad
w_e=\begin{cases}1,&e\in A,\\[2pt] w,&e\notin A.\end{cases}$$

**唯一的 predictor**（对整个 family 共用一个，与 $A$ 无关）：

$$\tilde f(S)\;=\;|S|.$$

Instance family：$\mathcal F_{n,K}=\{(f_A,\tilde f):A\subseteq N,\ |A|=K\}$，共 $\binom nK$ 个 pair。

直观：$A$ 外的 $n-K$ 个元素合计质量 $(n-K)\cdot\frac{K}{n-K}=K=f_A(A)$，即"坏元素整体"与"好集合"等重，但被摊薄到 $n-K$ 个元素上；predictor 把所有元素看成完全一样，因此不携带关于 $A$ 的任何信息。

---

## 3. 逐步推导

> 状态约定见 CLAUDE.md。每步末尾给出依据（输入文件的哪条假设，或前面哪一步）。

**Step 1（$f_A$ 合法）** $f_A$ 是 nonnegative modular function，$f_A(\emptyset)=0$，且对一切 $S$ 与 $e\notin S$ 有 $d_e(S)=w_e>0$，故 monotone；对 $S\subseteq T$ 与 $e\notin T$ 有 $d_e(S)=w_e=d_e(T)$，diminishing returns 以等号成立，故 submodular。于是 $f_A$ 满足 `assumptions.md` 对 objective 的全部要求。
依据：`assumptions.md`（monotone submodular，$f(\emptyset)=0$，$f\ge0$）。
状态：[VERIFIED-EXHAUSTIVE]（脚本 C2a，全格点 $2^{n}$ 上逐对检查 monotone 与 submodular，$K\le3$，$2K\le n\le8$）。

**Step 2（$\tilde f$ 合法）** $\tilde f(S)=|S|$ 满足 $\tilde f(\emptyset)=0$，且 $\tilde f:2^N\to\mathbb R$。`assumptions.md` 对 predictor 只要求这两点；附带地 $\tilde f$ 本身也是 monotone modular，因此即便额外要求 predictor 为 monotone submodular，构造依然成立。
依据：`assumptions.md`、`notation.md`（$\tilde f$ 是唯一可 query 的对象）。
状态：[VERIFIED-EXHAUSTIVE]（脚本 C2c 一并检查）。

**Step 3（Definition 1 的 support 条件）** 对一切 $S,e\notin S$：$\tilde d_e(S)=1>0$ 且 $d_e(S)=w_e>0$。故 "$d_e(S)=0\iff\tilde d_e(S)=0$" 成立（两侧都不发生）。
依据：`definition1.md`（verbatim 段的 "In particular $d_e(S)=0$ forces $\tilde d_e(S)=0$"；convention B 段的 "forces $\tilde d_e(S)=0$ exactly when $d_e(S)=0$"）。
状态：[VERIFIED-EXHAUSTIVE]（脚本 `eta_factors` 中的 support 一致性检查）。

**Step 4（误差参数的精确值）** Definition 1 要求 $d_e(S)/\eta_u\le\tilde d_e(S)\le\eta_o\,d_e(S)$。代入 $d_e(S)=w_e$、$\tilde d_e(S)=1$：条件等价于对一切 $e$ 有 $w_e\le\eta_u$ 且 $1\le \eta_o w_e$，即

$$\eta_u\;\ge\;\max_e w_e=1,\qquad \eta_o\;\ge\;\frac1{\min_e w_e}=\frac1w=\frac{n-K}{K}.$$

最小取法 $(\eta_u,\eta_o)=\bigl(1,\frac{n-K}{K}\bigr)$，于是

$$\boxed{\ \eta\;=\;\eta_u\eta_o\;=\;\frac{n-K}{K}\ }$$

（convention B 的 scaling：把 $\tilde f$ 乘以 $c>0$ 得 $(\eta_u,\eta_o)\to(c\eta_u,\eta_o/c)$ 这一形式的重排，$\eta$ 不变；例如取 $\tilde f(S)=\sqrt w\,|S|$ 得对称分裂 $\eta_u=\eta_o=\sqrt{(n-K)/K}$。）
依据：`definition1.md`（Definition 1 与 convention B 的 scaling 段）+ Step 1、Step 2。
状态：[VERIFIED-EXHAUSTIVE]（脚本 C2c：在全格点上取 $\max_{S,e}d/\tilde d$ 与 $\max_{S,e}\tilde d/d$，结果恰为 $(1,(n-K)/K)$）。

**Step 5（$O^{\ast}=A$，$F^{\mathrm{OPT}}=K$）** $f_A$ modular，故 $\max_{|S|\le K}f_A(S)$ 由最大的 $K$ 个权重给出。因 $w\le1$，$A$ 是一个 optimal $K$-set，$f_A(O^{\ast})=f_A(A)=K>0$。（$n=2K$ 时 $w=1$，所有 $K$-set 同为最优，$F^{\mathrm{OPT}}=K$ 不变。）由 $f_A(O^\ast)>0$，`assumptions.md` 中"$f(O^\ast)=0$ 时 ratio 陈述平凡成立"的旁路不被触发，比值有实质内容。
依据：Step 1 + `assumptions.md`（$O^{\ast}$ 为 optimal $K$-set 的约定）。
状态：[VERIFIED-EXHAUSTIVE]（脚本 C2b）。

**Step 6（transcript 与 $A$ 无关）** family $\mathcal F_{n,K}$ 中所有 pair 共用同一个 $\tilde f$。$\mathcal A$ 只能 query $\tilde f$（不能 query $f$），且 $\mathcal A$ 是 deterministic：其第一个 query 由 $(n,K)$ 决定，第 $i$ 个 query 由前 $i-1$ 个回答决定，而这些回答只取决于 $\tilde f$。归纳可得：对 family 中任意两个 instance，$\mathcal A$ 的完整 query/answer transcript 逐字相同。
依据：`assumptions.md`（the algorithm cannot evaluate $f$）+ (Q2) deterministic + (Q3) query 只作用于 $\tilde f$。
状态：[HAND-PROOF-UNREVIEWED]（这是 information-theoretic 的一步，无 oracle 可直接检验；但其结论被 Step 7 的量化方式完全吸收，见下）。

**Step 7（输出是一个固定集合）** 由 Step 6，$\mathcal A$ 在 family 上输出同一个集合 $T=T(\tilde f)\subseteq N$，且 $|T|\le K$。注意 $T$ 不依赖于 $A$。
依据：Step 6 + (Q4)。
状态：[HAND-PROOF-UNREVIEWED]。**规避办法**：下面 Step 8-Step 10 对**一切** $T$ 且 $|T|\le K$ 逐个验证结论，因此无论 Step 6-7 把 $T$ 定成什么，结论都成立；脚本正是按"对所有 $T$"穷举的，这使 Step 6-7 只承担"把 adversary 的选择推到 $T$ 之后"的逻辑作用。

**Step 8（存在与 $T$ 不交的 $A$；这是 $n\ge2K$ 唯一被用到的地方）** $|N\setminus T|=n-|T|\ge n-K\ge K$，故可取 $A\subseteq N\setminus T$，$|A|=K$，即 $A\cap T=\emptyset$。
依据：(Q1) $n\ge2K$ + Step 7 的 $|T|\le K$。
状态：[VERIFIED-EXHAUSTIVE]（脚本 C2d 对所有 $T$ 取 $\min_A$，实现上就取到了这种 $A$）。

**Step 9（该 instance 上的算法值）** 取 Step 8 的 $A$，令 $f=f_A$。则 $|T\cap A|=0$，

$$f_A(T)\;=\;0+w\,|T|\;=\;\frac{K}{n-K}\,|T|\;\le\;\frac{K}{n-K}\,K .$$

依据：第 2 节的定义 + Step 8 + $|T|\le K$。
状态：[VERIFIED-EXHAUSTIVE]（脚本 C2d）。

**Step 10（结论）** 结合 Step 5 的 $f_A(O^{\ast})=K$：

$$f_A(T)\;\le\;\frac{K}{n-K}\cdot K\;=\;\frac{K}{n-K}\,f_A(O^{\ast}).$$

即 pair $(f_A,\tilde f)$ 正是命题所要的 pair，其误差为 $\eta=\frac{n-K}{K}$（Step 4），有限但随 $n$ 增长而无界，因此只有在"不假设 $\eta$ 的上界"时该 family 才被允许。$\blacksquare$（对固定 $n,K$ 的主断言）
依据：Step 5 + Step 9。
状态：[VERIFIED-EXHAUSTIVE]（$K\le3$，$2K\le n\le8$，所有 $|T|\le K$ 穷举，脚本 C2d；$\max_T\min_A$ 的比值恰等于 $\frac{K}{n-K}$，见第 7 节表格）+ 一般 $(n,K)$ 的代数推导 [HAND-PROOF-UNREVIEWED]。

**Step 11（第二句：no constant ratio）** 设某 deterministic algorithm $\mathcal A$ 声称对一切满足 `assumptions.md` 且 Definition 1 有限误差的 pair 都有 $f(T)\ge\alpha f(O^{\ast})$，$\alpha\in(0,1]$ 为常数（与 $n$ 无关）。固定 $K$，取 $n>K+K/\alpha$，则 $\frac{K}{n-K}<\alpha$，与 Step 10 矛盾。故不存在这样的常数 $\alpha$。
依据：Step 10 + (Q9)。
状态：[HAND-PROOF-UNREVIEWED]（纯逻辑步骤，无需 oracle）。

**Step 11'（若 $\mathcal A$ 特化为 predictive greedy）** 在 $\tilde f(S)=|S|$ 上每一步所有候选的 $\tilde d_e(S^t)=1$ 全部并列。按 `assumptions.md` 的 adversarial tie breaking，可让 $K$ 步全部选在 $N\setminus A$ 中（Step 8 保证这样的 $A$ 存在），得到与 Step 9 相同的 $f(T)=wK$。此时 selection error（`definition1.md` 的 def:etasel）为 $a_t=M_t/g_t=1/w=\frac{n-K}{K}$（对每个 $t$，因为 $M_t=1$ 由 $A$ 中未选元素达到，$g_t=w$），即 $\etasel=\frac{n-K}{K}=\eta$。
依据：`assumptions.md`（predictive greedy 定义与 adversarial ties）+ `definition1.md`（def:etasel）。
状态：[HAND-PROOF-UNREVIEWED]（手算 $a_t$；未单独写 oracle 脚本，但 $M_t,g_t$ 的取值由 modular 结构直接给出）。

---

## 4. 更强的版本（把比值压到任意小）与为什么命题只写 $\frac{K}{n-K}$

把第 2 节中的 $w$ 换成任意 $\epsilon\in(0,1]$，记 $f^{\epsilon}_A(S)=|S\cap A|+\epsilon|S\setminus A|$。Step 1-Step 10 逐字不变，得

$$f^{\epsilon}_A(T)\;\le\;\epsilon\,f^{\epsilon}_A(O^{\ast}),\qquad \eta(\epsilon)=\frac1\epsilon .$$

即：对**任意** $\epsilon>0$，都存在满足全部 assumption（除 $\eta$ 的上界外）的 pair 使 ratio $\le\epsilon$。命题中的 $\frac{K}{n-K}$ 是"$\epsilon=w$ 这一特定平衡取法"的值，其意义在于：它是使 $A$ 外元素总质量恰好等于 $f(O^{\ast})$ 的取法，并且它把所需误差压到该 family 里的最小值

$$\eta=\frac{n-K}{K}=\frac1{\text{ratio}},$$

即 **ratio $=1/\eta$**。换言之，命题的 $\frac{K}{n-K}$ 形式把"坏结果"与"所需误差"绑在一起：要在 $n$ 个元素上得到 ratio $\frac{K}{n-K}$，误差只需 $\frac{n-K}{K}$；要得到任意小的 ratio $\epsilon$，误差必须是 $1/\epsilon$。这正是"no bound on $\eta$"这一前提不可去的定量刻画。
状态：[VERIFIED-EXHAUSTIVE]（$\epsilon=w$ 的情形即 C2；一般 $\epsilon$ 的代数与 $\epsilon=w$ 完全同型，[HAND-PROOF-UNREVIEWED]）。

**空洞性检验（CLAUDE.md 第"空洞性检验"节）**，逐个限定词：

| 限定词 | 去掉/取反后 | 变化 |
|---|---|---|
| deterministic | 见第 6 节 | 变。worst-case 逐点结论变成期望结论，且所需 $\eta$ 从 $\frac{n-K}{K}$ 升到 $\frac{n(n-K)}{K^2}$。限定词非空洞。 |
| arbitrary query access | 换成 poly-query | 不变（本证明不用 query 数；用 arbitrary 是把陈述做强）。该限定词只在"强化"意义上有内容，不可删但应理解为"even with unbounded queries"。 |
| $n\ge2K$ | 换成 $n<2K$ | 变。Step 8 失效，构造给不出比 $\frac{2K-n}{K}$ 更小的比值（第 9 节，[VERIFIED-EXHAUSTIVE] C5）。 |
| no upper bound on $\eta$ | 假设 $\eta\le\eta_0$ | 变。family 中 ratio $=1/\eta\ge1/\eta_0$，构造不再能把比值压到 0。 |
| monotone submodular | 去掉 | 不变（本构造用 modular $f$，是 submodular 的特例，因此 hardness 不来自 $f$ 的复杂性，而完全来自 predictor 不含信息）。这一点值得在正文里说一句。 |

---

## 5. 本 instance 的误差 $\eta$（命题要求明确回答）

| 版本 | $f$ 的非最优权重 | $(\eta_u,\eta_o)$（最小取法） | $\eta$ | 得到的界 |
|---|---|---|---|---|
| 主构造（deterministic，worst case） | $w=\frac{K}{n-K}$ | $\bigl(1,\frac{n-K}{K}\bigr)$ | $\frac{n-K}{K}$ | $f(T)\le\frac{K}{n-K}f(O^\ast)$，等号可取 |
| 任意小比值版 | $\epsilon\in(0,1]$ | $(1,1/\epsilon)$ | $1/\epsilon$ | $f(T)\le\epsilon f(O^\ast)$ |
| randomized 版（第 6 节） | $\epsilon=\frac{K^2}{n(n-K)}$ | $\bigl(1,\frac{n(n-K)}{K^2}\bigr)$ | $\frac{n(n-K)}{K^2}$ | $\mathbb E[f(T)]\le\frac{K}{n-K}f(O^\ast)$ |

三行的 $\eta$ 都有限，都随 $n\to\infty$ 发散；这正是"if no upper bound on $\eta$ is assumed"这一前提被用到的地方，也是命题第二句成立的机制。
状态：[VERIFIED-EXHAUSTIVE]（三行的 $(\eta_u,\eta_o)$ 均由脚本在全格点上重新计算得到，C2c 与 C3）。

---

## 6. randomized algorithm 会怎样（命题要求明确回答）

设 $\mathcal A$ 是 randomized，内部随机种子 $R$ 与 instance 独立。由于 family 共用同一个 $\tilde f$，Step 6 的论证给出：对固定的 $R$，transcript 与 $A$ 无关，故输出 $T=T(R)$ 是一个与 $A$ **独立**的随机集合，$|T|\le K$。

取 $A$ 在所有 $K$-subset 上均匀随机，取 $\epsilon=\frac{K^2}{n(n-K)}$（注意 $\epsilon\le\frac{K}{n}\le1$），$f=f^{\epsilon}_A$。对任意固定的 $T$，$\mathbb E_A|T\cap A|=|T|\cdot\frac Kn$，于是

$$\mathbb E_{A,R}\bigl[f^{\epsilon}_A(T)\bigr]
=\mathbb E\bigl[|T\cap A|\bigr]+\epsilon\,\mathbb E\bigl[|T\setminus A|\bigr]
\le \frac{K|T|}{n}+\epsilon|T|
\le \frac{K^2}{n}+\epsilon K
= K\Bigl(\frac Kn+\frac{K^2}{n(n-K)}\Bigr)
= K\cdot\frac{K}{n-K},$$

最后一步用恒等式 $\frac Kn+\frac{K^2}{n(n-K)}=\frac{K}{n-K}$（[VERIFIED-SYMBOLIC]，脚本 C1）。由于 $f^{\epsilon}_A(O^{\ast})=K$ 对每个 $A$ 都成立，平均值论证给出：**存在**一个固定的 $A$（因而一个固定的 pair $(f^{\epsilon}_A,\tilde f)$）使

$$\mathbb E_R\bigl[f^{\epsilon}_A(T)\bigr]\;\le\;\frac{K}{n-K}\,f^{\epsilon}_A(O^{\ast}),\qquad \eta=\frac{n(n-K)}{K^2}.$$

结论：**randomized 不改变命题的界，只改变两件事**：(i) 结论从逐点 worst-case 变成对算法内部随机性的期望（Yao 型陈述）；(ii) 所需误差从 $\frac{n-K}{K}$ 升到 $\frac{n(n-K)}{K^2}$，因为 randomized 算法可以靠均匀随机挑 $T$ 白拿到 $\frac Kn$ 这一份 overlap，必须用更小的 $\epsilon$ 把它压回去。两种情形下 $\frac{K}{n-K}\to0$（$n\to\infty$），故 "no constant worst-case ratio" 对 randomized algorithm 同样成立（以期望意义）。

进一步说明界的形状：任何 randomized 算法（哪怕完全忽略 predictor，均匀随机输出 $K$ 个元素）在上述 family 上都能拿到 $\mathbb E[f(T)]\ge\frac{K^2}{n}$，即 ratio $\ge\frac Kn$。所以在这一 family 上 randomized 的真实量级是 $\Theta(K/n)$，命题的 $\frac{K}{n-K}$ 与之只差一个 $\le2$ 的因子（$n\ge2K$ 时 $\frac{K}{n-K}\le\frac{2K}{n}$）。
状态：不等式链 [VERIFIED-EXHAUSTIVE]（脚本 C3：对 $K\le3$、$2K\le n\le8$ 的所有 $T$ 精确计算 $\mathrm{avg}_A$，均 $\le\frac{K}{n-K}$）；核心恒等式 [VERIFIED-SYMBOLIC]（C1）；一般 $(n,K)$ 的推导 [HAND-PROOF-UNREVIEWED]。

---

## 7. 数值走查

### 7.1 $K=3$，$\eta=3/2$（命题要求的参数）

$\eta=\frac32$ 对应 $w=\frac1\eta=\frac23$。要让该 instance 证成命题的界，需要 $\frac23\le\frac{K}{n-K}=\frac{3}{n-3}$，即 $n\le7.5$，故 $n\in\{6,7\}$（且 $n\ge2K=6$）。

取 $n=7$，$N=\{1,\dots,7\}$，$K=3$，$w=\frac23$：

- predictor $\tilde f(S)=|S|$，与 $A$ 无关；deterministic $\mathcal A$ 无论做多少 query，输出是一个固定的 $T$，设 $T=\{1,2,3\}$。
- adversary 取 $A=\{4,5,6\}\subseteq N\setminus T$（$|N\setminus T|=4\ge3=K$，Step 8）。
- $f_A(O^{\ast})=f_A(A)=3$。
- $f_A(T)=0+\frac23\cdot3=2$。
- ratio $=\frac23\approx0.6667\le\frac{K}{n-K}=\frac34=0.75$。命题的界成立（有余量）。
- 误差核对：$d_e(S)\in\{1,\frac23\}$，$\tilde d_e(S)=1$，故 $\eta_u=1$，$\eta_o=\frac32$，$\eta=\frac32$。
- 若 $\mathcal A$ 是 predictive greedy：每步 7 个（或剩余的）候选 $\tilde d$ 全部并列为 1，adversarial tie breaking 依次选 $1,2,3$；$\etasel=\max_t M_t/g_t=1/(2/3)=\frac32$。

**注意**：同一个 $\eta=\frac32$ 在 $n=8$ 时**不足以**证成界：ratio 仍是 $\frac23$，但 $\frac{K}{n-K}=\frac35=0.6<\frac23$。此时必须把 $w$ 降到 $\frac35$，即 $\eta$ 升到 $\frac53$。这正是"$\eta$ 必须随 $n$ 增长"的具体体现。
状态：[VERIFIED-EXHAUSTIVE]（脚本 C4，逐 $n$ 打印 certifies 标志，$n\le7$ 为 True，$n\ge8$ 为 False）。

### 7.2 平衡取法的精确最坏值（脚本 C2d 输出，节选）

| $n$ | $K$ | $\eta=\frac{n-K}{K}$ | $\max_{|T|\le K}\min_{A}\frac{f_A(T)}{f_A(O^\ast)}$ | 命题的界 $\frac{K}{n-K}$ |
|---|---|---|---|---|
| 6 | 3 | $1$ | $1$ | $1$（平凡） |
| 7 | 3 | $4/3$ | $3/4$ | $3/4$ |
| 8 | 3 | $5/3$ | $3/5$ | $3/5$ |
| 6 | 2 | $2$ | $1/2$ | $1/2$ |
| 8 | 2 | $3$ | $1/3$ | $1/3$ |
| 8 | 1 | $7$ | $1/7$ | $1/7$ |

即在平衡取法下命题的界被**等号**达到：这一 family 恰好打到 $\frac{K}{n-K}$，不多不少。

### 7.3 randomized 走查（$K=3$，$n=8$）

$\epsilon=\frac{K^2}{n(n-K)}=\frac{9}{40}$，$\eta=\frac{40}{9}\approx4.444$。对任意 $|T|=3$：

$$\mathrm{avg}_A\frac{f^{\epsilon}_A(T)}{K}=\frac Kn+\epsilon\Bigl(1-\frac Kn\Bigr)=\frac38+\frac9{40}\cdot\frac58=\frac{33}{64}\approx0.5156\;\le\;\frac{K}{n-K}=\frac35 .$$

（脚本给出的精确最坏值就是 $\frac{33}{64}$；粗放上界 $\frac Kn+\epsilon=\frac{24}{40}=\frac35$ 正好等于界。）
状态：[VERIFIED-EXHAUSTIVE]（C3）。

### 7.4 ProbeLottery（$K=2$）

任务模板要求"$K=2$ 时做 ProbeLottery 项"。四个输入文件（`definition1.md`、`assumptions.md`、`notation.md`、`statement_nobound.md`）中**没有**任何名为 ProbeLottery 的对象、定义或记号，`notation.md` 的记号表里也没有。按 STRICT ISOLATION 规则我不能去别处查它的定义，按"不提问、选保守项"的规则，我**跳过**该小项并在此记录。作为替代，第 7.2 节已给出 $K=2$ 的精确穷举（$n=4,5,6,7,8$，比值分别为 $1,\frac23,\frac12,\frac25,\frac13$，逐个等于 $\frac{K}{n-K}$）。
状态：[FAILED]（未执行；原因：ProbeLottery 未在允许阅读的输入文件中定义，不是本 statement 的一部分）。

---

## 8. $n\ge2K$ 在哪里被用到，$n<2K$ 会怎样

$n\ge2K$ 只在 **Step 8** 用到一次：保证 $|N\setminus T|=n-|T|\ge n-K\ge K$，从而存在与 $T$ 完全不交的 $K$-set $A$。

若 $n<2K$，任何 $|T|=K$ 与任何 $|A|=K$ 必有 $|T\cap A|\ge 2K-n>0$，于是对本 family（无论 $w$ 多小）

$$\frac{f_A(T)}{f_A(O^{\ast})}\;\ge\;\frac{|T\cap A|}{K}\;\ge\;\frac{2K-n}{K}\;>\;0 .$$

因此该构造在 $n<2K$ 时**不能**把比值压到 0，$n\ge2K$ 是本证明路线的真实需求，不是装饰。
状态：[VERIFIED-EXHAUSTIVE]（脚本 C5，$2\le K\le4$、$K\le n<2K$）。

需要说明的是：这只表明**本构造**失效，并不表明 $n<2K$ 时存在好算法。后者需要另外的论证，本文件不做断言。
状态：[CONJECTURE] 不做；此处只记录为 open。

---

## 9. 无法闭合的步骤 / 额外加入的假设

1. **Step 6-7（transcript 与 $A$ 无关）**：[HAND-PROOF-UNREVIEWED]。这是对"deterministic algorithm with arbitrary query access"的形式化归纳论证，没有 oracle 可以直接检验（它是关于计算模型的陈述，不是关于数的陈述）。**缓解措施**：Step 8-10 与所有脚本检查都是对**一切** $T$（$|T|\le K$）取全称的，所以即便有人对 Step 6-7 的模型形式化持不同意见，只要承认"算法的输出是一个 $|T|\le K$ 的集合且与 $A$ 无关"，结论即成立。
2. **加入的假设（明确记录）**：$|T|\le K$。`statement_nobound.md` 只写 "the output $T$"，没有写 $|T|\le K$。我按 `assumptions.md` 的 cardinality budget $K$ 把输出解释为可行解。若允许 $|T|>K$，命题在字面上不成立（取 $T=N$ 即得 $f(T)>f(O^\ast)$）。这是**保守但必要**的读法。
3. **加入的解释**："arbitrary query access" 我取为无限制（可读完整张值表）。这只会让结论更强，不会削弱它；但若原文本意是"多项式次 value query"，本证明依然覆盖该情形。
4. **一般 $(n,K)$ 的代数**：脚本只穷举了 $K\le3$、$n\le8$（randomized 部分同）。一般参数下的 Step 4、Step 9、Step 10、第 6 节不等式链均为手写代数，标 [HAND-PROOF-UNREVIEWED]；每一步都是单行代数，但按 CLAUDE.md 规则不写 "proved"。
5. **Step 11'（$\etasel=\frac{n-K}{K}$）**：手算，未写独立脚本，标 [HAND-PROOF-UNREVIEWED]。
6. **ProbeLottery（$K=2$）小项**：未执行，见 7.4，标 [FAILED]（缺定义）。
7. **$n<2K$ 的一般下界**：未尝试，记为 open（第 8 节末）。
8. **与论文中 $\rho_K(\eta)$、$L_K$、$U_K$ 的关系**：本 route-two 推导不涉及，也未查看任何相关文件；此处不做任何比较断言。

---

## 10. 读过的文件

- `/home/user/sub-modular-optimization/results/V11/inputs/definition1.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/assumptions.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/notation.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/statement_nobound.md`

未打开、未 grep、未列出仓库中任何其他文件；未使用 web search；未运行 git。

新建文件（仅在 `results/V11/route2/` 下）：
- `/home/user/sub-modular-optimization/results/V11/route2/verify_nobound.py`（可复现脚本，`python3 results/V11/route2/verify_nobound.py`，运行时间 < 30s，结尾打印 `ALL CHECKS PASS (exact arithmetic).`）
- `/home/user/sub-modular-optimization/results/V11/route2/nobound.md`（本文件）

---

## 11. 一句话总结

对任意 deterministic algorithm，令 predictor 为与 instance 无关的 $\tilde f(S)=|S|$，令 $f_A(S)=|S\cap A|+\frac{K}{n-K}|S\setminus A|$ 并在算法输出 $T$ 之后选 $A\subseteq N\setminus T$（$n\ge2K$ 保证可选），即得 $f_A(T)=\frac{K}{n-K}f_A(O^{\ast})$，该 instance 的误差为 $\eta=\frac{n-K}{K}$，随 $n$ 无界；randomized 算法在期望意义下同样受制于 $\frac{K}{n-K}$，代价是误差升至 $\frac{n(n-K)}{K^2}$。

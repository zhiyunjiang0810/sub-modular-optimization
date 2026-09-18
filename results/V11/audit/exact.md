# 量词审计（criteria A 与 E）：thm:exact / 台账 T6（TASKS11 Q4，正文 Theorem 1）

本文件只做两件事：A 项逐量词比对正文环境与台账卡；E 项建立量词审计表，把陈述里的每个量词与形容词
落到路线甲证明的具体位置，落不上的记 GAP。

范围与纪律：不修改任何已有文件，不运行 git。本文件自身的算术用 sympy 精确核对（结果见 §5），
浮点只出现在打印里。状态标签按 CLAUDE.md：[VERIFIED-SYMBOLIC] [VERIFIED-LP] [VERIFIED-EXHAUSTIVE]
[HAND-PROOF-UNREVIEWED] [CONJECTURE] [FAILED]。读过的文件见 §6。

按 HANDOFF_ADDENDUM 的 B.1，本条目在正文里编号为 Theorem 1，label 不改，environment 仍是 `theorem`。
这与 `results/V11/statements.md` 第 173 行的元数据行一致，本审计不涉及该项改动。

---

## 1. Criterion A：正文陈述与台账陈述的逐量词比对

### 1.1 三段原文

正文：`paper/sections/results.tex` 第 191 至 207 行，environment `theorem`，label `thm:exact`，
标题 "Exact worst-case ratio of predictive greedy"。环境之前第 183 至 190 行是记号段
（$k_1=(K-1)\eta+1$、$q=(K-1)\eta/k_1$、$V_j(\eta)=1-q^{j}(1-\frac{K-j}{K\eta})$，$0\le j\le K-1$），
环境之后第 208 至 215 行是 `rem:exact-n`（ground-set size）。

矩阵输入：`results/V11/statements.md` 第 183 至 201 行的 LaTeX 块与
`results/V11/inputs/statement_exact.md` 第 6 至 22 行。两者与正文 environment 逐字符相同
（diff 结果：statements.md 与 statement_exact.md 完全一致；与 results.tex 的差别只有 markdown 的
围栏行与正文下一行的 `\begin{remark}[Ground-set size]`）。

台账：`THEOREM_LEDGER.md` 第 92 至 106 行，卡 `## T6 thm:exact`。卡的"陈述"行（第 94 行）为：

> K ≥ 2, η ≥ 1，adversarial tie：ρ_K(η)=min_{0≤j≤K−1} V_j(η)，V_j=1−q^j(1−(K−j)/(Kη))，
> q=(K−1)η/((K−1)η+1)；段 [K−j,K−j+1] 上由 V_j 取到，[K,∞) 上 V_0=1/η；分段点整数 2..K；
> ρ_K=1/η ⇔ η ≥ K。K=2,3,4 显式闭式见正文。

卡里另有独立条目：n 量词（第 98 至 102 行，M1）"ρ_{n,K}(η) = 固定 ground set 大小 n 的精确最坏比；
n ≥ 2K 时 ρ_{n,K} = ρ_{2K,K} = ρ_K"，以及注意项"原界对有限 K 严格不紧必须限定 η > 1"。

### 1.2 逐项对照

| 量词 / 形容词 | 正文（results.tex 191-207） | 台账（T6 陈述行） | 判定 |
|---|---|---|---|
| ∀ $K\ge2$ | "For every $K\ge2$" | "K ≥ 2" | 一致 |
| ∀ $\eta\ge1$ | "and $\eta\ge1$" | "η ≥ 1" | 一致 |
| 形容词 under adversarial tie breaking | 有，作为前件修饰整句 | "adversarial tie" | 一致 |
| 主结论 $\rho_K(\eta)=\min_{0\le j\le K-1}V_j(\eta)$ | 有，含指标范围 $0\le j\le K-1$ | 有，含 0≤j≤K−1 | 一致 |
| $V_j$ 与 $q$、$k_1$ 的定义 | 在环境**之外**（第 183 至 190 行的记号段） | 写进陈述行本身 | 位置差异，见 N1 |
| 分段：minimum attained by $V_j$ on $\eta\in[K-j,K-j+1]$ | 有 | "段 [K−j,K−j+1] 上由 V_j 取到" | 一致 |
| $j=0$ 分支：$V_0=1/\eta$ on $[K,\infty)$ | 有（括号内） | "[K,∞) 上 V_0=1/η" | 一致 |
| 分段点为整数 $2,\dots,K$ | "so the breakpoints are the integers $2,\dots,K$" | "分段点整数 2..K" | 一致 |
| 充要形式 $\rho_K=1/\eta$ **exactly when** $\eta\ge K$ | 有（"exactly when"） | "ρ_K=1/η ⇔ η ≥ K" | 一致 |
| $K\in\{2,3,4\}$ 闭式与各自的段 | 逐式写出，并标出 $[1,2],[2,3],[3,\infty)$ 等 | "K=2,3,4 显式闭式见正文"（指针） | 一致（指针，见 N3） |
| ground-set size $n$ | 环境内**不出现**；紧随其后的 `rem:exact-n` 给 $n\ge2K$ | 陈述行内**不出现**；卡里另起一条给 n ≥ 2K | 一致（两边都放在陈述之外），见 N2 |
| deterministic / randomized | 两边都不出现（predictive greedy 本身是确定性算法，tie 由 adversary 解） | 同 | 一致 |
| 查询次数、查询集合大小（$\le nK$、$|S|\le K$ 之类） | 两边都不出现（本条目不是查询类结果） | 同 | 一致 |
| expectation 量词 | 两边都不出现 | 同 | 一致 |
| fixed $K$ steps、$f(\emptyset)=0$、OPT>0 | 两边都不出现，继承 model.tex 与 assumptions.md | 同 | 一致（隐含量词进 E 表） |
| $\eta>1$ 的限定（"原界对有限 K 严格不紧"） | 不出现（该断言不在本陈述里） | 卡里作为"注意"项 | 一致（不是陈述内容），见 N4 |

### 1.3 A_diffs

逐量词、逐形容词、逐定义域比对的两张清单**完全重合**：上表没有任何一行落在"差异"。
因此 **A_match = true**。

下面四条是位置与呈现层面的记录，不属于量词清单，故不计入 A_match：

- **N1（定义的位置）**：正文把 $k_1$、$q$、$V_j$ 放在 environment 之外的记号段，环境体内出现的
  $V_j$ 是外部定义；台账陈述行把三个定义写在同一行内。矩阵若只抄 environment 体，$V_j$ 无定义。
  建议矩阵栏同时带上 results.tex 第 183 至 190 行，本审计不改文件。
- **N2（n 量词的载体）**：两边都把 n 放在陈述之外，正文用 `rem:exact-n`，台账用单独条目。
  两者内容一致（restriction 加 padding，$\rho_{n,K}=\rho_{2K,K}$ 对每个 $n\ge2K$），状态也一致
  （[HAND-PROOF-UNREVIEWED]，本地重构，J5 §13 原文未送达）。这不是 A 项差异，但它是 E 表的
  GAP-1（见 §2.1）。
- **N3（闭式的呈现）**：台账用指针"见正文"，正文逐式写出。内容一致，本审计对 $K=2,3,4$ 的九个
  分段闭式做了独立符号核对，全部等于对应的 $V_j$（§5 第 4、5 条，[VERIFIED-SYMBOLIC]）。
- **N4（$\eta>1$ 注意项）**：台账卡第 93 行的"原界对有限 K 严格不紧必须限定 η > 1"是 must-not-claim，
  约束的是 `rem:exact-gap` 一类的措辞，不是 thm:exact 的量词。正文对应处在 results.tex 第 371 行起的
  `rem:exact-gap`，那里写的是 $U_K>V_{K-1}$ for every $\eta>1$，限定已带上。

---

## 2. Criterion E：量词审计表（落到路线甲）

路线甲 = `paper/sections/appendix_proofs.tex` 的
`\subsection{The exact worst case (Theorem~\ref{thm:exact})}\label{app:exact}`（第 582 至 1012 行）
加它所消费的 `\subsection{Validity of the reduced constraints}\label{app:validity}`（第 2149 至 2347 行），
数据来源 `results/N1_dual_certificate.md`（对偶乘子）与 `results/N2_instances.md`（达到实例），
脚本 `results/N1_dual_certificate.py`、`results/N2_check.py`、`code/reduced_lp.py`、`results/T3_duals.py`。

app:exact 的段落锚点（行号）：`\paragraph{Roadmap.}`（584）、`\paragraph{The reduced linear program.}`（609）、
`\paragraph{Lower bound: greedy is never worse than $\min_jV_j$.}`（632）、其内 `\emph{Nonnegativity.}`（663）、
`\emph{The weighted-sum identity.}`（679）、`\emph{(a)}`（704）、`\emph{(b)}`（749）、`\emph{(c)}`（773）、
`\emph{Conclusion of the lower bound.}`（796）、`\emph{Which $V_j$ is smallest.}`（806）；
`\paragraph{Upper bound: the value $V_j$ is attained.}`（835）、其内 `\emph{Marginal gains.}`（862）、
`\emph{Monotonicity and submodularity of $f$.}`（885）、`\emph{The error is exactly $(\eta_u,\eta_o)$.}`（910）、
`\emph{The optimum.}`（931）、`\emph{The per-step gain table.}`（938）、`\emph{The greedy induction.}`（961）、
`\emph{The role of the ties.}`（986）。

状态列：**OK** = 路线甲有明确处理；**OK(隐含)** = 有处理但无独立句子；**部分** = 有处理但缺一步或缺定义；
**GAP** = 路线甲没有对应位置；**N/A** = 本陈述没有这个量词。

| 量词 / 形容词 | 处理位置（file + paragraph） | 状态 |
|---|---|---|
| 1. ∀ $K\ge2$（定义域下端） | app:exact 第 602 行 "Throughout this subsection $K\ge2$, $\eta\ge1$, $f(O^{\ast})=1$"；实际消费点在第 607 行 "Note $k_1\ge K\ge2$, so $q\in(0,1)$"（下界的几何求和与上界的 $q^j\le q^x$ 都要 $q\in(0,1)$） | OK |
| 2. ∀ $\eta\ge1$（定义域） | 同第 602 行；消费点三处：app:validity `lem:app-pred` case (c)（第 2233 行 "$d_t\ge d_t/\eta$, which holds because $d_t\ge0$ and $\eta\ge1$"）；app:exact `\emph{The error is exactly ...}`（910）里的排序 $1/\eta_u\le k_1/(K\eta_u)\le\eta_o$ 用 $k_1-K=(K-1)(\eta-1)\ge0$ 与 $K\eta-k_1=\eta-1\ge0$；`\emph{Nonnegativity.}`（663）对 $\eta-1$ 作分母的段落 | OK |
| 3. 形容词 under adversarial tie breaking | 上界侧 `\emph{The greedy induction.}`（961）"Adversarial tie breaking picks an element of $C$" 与 "the step is a tie and the adversary picks an element of $P$"；`\emph{The role of the ties.}`（986）"Every one of the $K$ steps above is a tie with an element of $O$, so adversarial tie breaking is load bearing"；正文 `rem:rigidity-ties`（results.tex 第 347 行）"This is why adversarial tie breaking is a hypothesis of Theorem~\ref{thm:exact} and not a convenience" | OK |
| 4. tie 在下界方向不被使用（形容词的作用范围） | 下界侧 app:validity 的四个 lemma 只用 $e_t\in\arg\max$，不依赖 argmax 如何解 tie（`lem:app-pred` case (b) 第 2224 行 "the second by the greedy choice"） | OK(隐含)（未写成句子，但四个证明里无 tie 假设） |
| 5. $\min_{0\le j\le K-1}$ 的指标范围 | `\emph{Which $V_j$ is smallest.}`（806）：相邻差 $V_i-V_{i+1}=q^i(K-i-\eta)/(K\eta k_1)$ 只对 $0\le i\le K-2$ 写（第 807 行注释记录 K6 修正：$i=K-1$ 会引用未定义的 $V_K$） | OK |
| 6. $V_j$、$q$、$k_1$ 的定义（环境外导入） | app:exact 第 603 至 606 行重述同一组定义，与 results.tex 第 183 至 190 行逐字一致 | OK |
| 7. "the minimum is attained by $V_j$ on $[K-j,K-j+1]$" | `\emph{Which $V_j$ is smallest.}`（806）末段："the sign of $K-i-\eta$ is nonnegative for $i\le j-1$ and nonpositive for $i\ge j$ ... $\min_iV_i=V_j$ there, and neighbouring segments agree at the integer endpoints" | OK（相邻差恒等式 [VERIFIED-SYMBOLIC]，§5 第 1 条；另见 results/N1_dual_certificate.py Part D） |
| 8. 段的左端 $\eta\ge K-j$ | 上界侧 `\emph{Monotonicity and submodularity of $f$.}`（885）："$\Delta_Of\ge0\iff\eta q^{x-j}\ge z$ ... because $z\le K-j\le\eta$ by the standing assumption $\eta\ge K-j$. This is the only place where the segment condition is consumed, and it is where the breakpoints come from" | OK |
| 9. 段的右端 $\eta\le K-j+1$ | 只在下界侧用：`\emph{Nonnegativity.}`（663）"the segment condition $\eta\le K-j+1$ is exactly $K-j+1-\eta\ge0$"，即 $\lambda_S(j)\ge0$ | OK（并记录：上界侧不需要右端，`\paragraph{Upper bound}` 第 836 行只写 "$\eta$ with $\eta\ge K-j$"；两侧的定义域不对称，合起来仍覆盖每个 $\eta\ge1$） |
| 10. $j=0$ 分支与 $V_0=1/\eta$ on $[K,\infty)$ | 下界侧 `\eqref{eq:duals-jzero}`（第 651 至 659 行）单列 $j=0$ 的乘子；`\emph{(c)}`（773）末 "For $j=0$ the sum is the single term $\lambda_S(0)=1/\eta$, and $V_0=1/\eta$"；`\emph{Which $V_j$ is smallest.}` 末句 "At $\eta\ge K$ the active index is $j=0$ and $\min_iV_i=V_0=1/\eta$" | OK |
| 11. 分段点恰为整数 $2,\dots,K$ | 同第 7 行的符号分析；正文 `rem:rigidity-breakpoints`（results.tex 第 311 行起）给出乘子层面的解释（$\lambda_P(j)$ 在左端点消失、$\lambda_S(j)$ 在右端点消失） | OK |
| 12. "$\rho_K=1/\eta$ **exactly when** $\eta\ge K$" 的充分方向（$\eta\ge K\Rightarrow$） | 第 10 行同两处 | OK |
| 13. 同一句的必要方向（$\eta<K\Rightarrow\rho_K<1/\eta$） | 路线甲**没有写出这一行**。它是 `\emph{Which $V_j$ is smallest.}` 的相邻差在 $i=0$ 的特例：$V_0-V_1=(K-\eta)/(K\eta k_1)>0$ 当 $\eta<K$ | **部分**：恒等式已在附录，结论句缺一行。本审计独立核对 $V_0-V_1=(K-\eta)/(K\eta k_1)$，$K=2..8$ [VERIFIED-SYMBOLIC]（§5 第 3 条）；oracle 侧 `results/V11/oracle/exact.log` 的 C0c 对 $K=2..8$、49 个精确点报 "strict inequality below K" [VERIFIED-SYMBOLIC] |
| 14. $K\in\{2,3,4\}$ 闭式与各自的段 | app:exact 第 826 至 833 行 "The closed forms displayed in Theorem~\ref{thm:exact} for $K\in\{2,3,4\}$ are the specializations of $\min_jV_j$"，并算了 $K=3$、$j=2$ 一例；脚本 `results/T3_K3_closed_form.py` | OK（$K=3$ 三段与 $K=4$ 四段共九式本审计全部独立核对，[VERIFIED-SYMBOLIC]，§5 第 4、5 条） |
| 15. 隐含：构造所需的 ground-set 大小 | 上界侧 `\paragraph{Upper bound}`（835）"Partition a ground set of $n=2K$ elements into $C$（$|C|=j$）, $P$（$|P|=K-j$）, $O$（$|O|=K$）"；`results/N2_instances.md` §0 同 | OK（构造侧本身），但陈述层见第 16 行 |
| 16. 隐含：陈述里的 $n$ 量词 | thm:exact 环境内没有 $n$；`\rho_K` 在 `paper/sections/model.tex` 第 78 行的定义句也没有 $n$；补位的是 `rem:exact-n`（results.tex 第 208 至 215 行）的 restriction 加 padding，$\rho_{n,K}=\rho_{2K,K}$ for every $n\ge2K$ | **GAP-1**：路线甲的 app:exact 内没有任何段落处理 $n$；`rem:exact-n` 是正文里的 remark，状态 [HAND-PROOF-UNREVIEWED]（results.tex 第 216 至 220 行的注释写明"LOCAL reconstruction"，J5 §13 原文未送达），数值支持 [VERIFIED-LP]（`results/L2_linear_candidates.py` gates，$K=2$、$n\in\{4,5,6\}$ 与 $K=3$、$n\in\{6,7\}$）。$K\le n<2K$ 不在覆盖范围内 |
| 17. 下界方向对 $n$ 的无关性 | reduced LP（`code/reduced_lp.py`，变量只有 $d_t$ 与 $g_{t,i}$）完全不含 $n$；app:validity 的四个 lemma 对任意 ground set 成立 | OK（这也是 GAP-1 只影响上界方向的原因） |
| 18. 隐含：$\rho_K$ 这个量本身的定义（对哪些对象取 worst case） | `model.tex` 第 70 至 78 行只有一句 "Its exact worst-case ratio at error level $\eta$ is written $\rho_K(\eta)$"；逐量词展开（对 $n$、$f$、$\tilde f$、tie 的取法）只在 `results/V11/route2/exact.md` §1 的 Q1 至 Q6 里写出，那是路线二 | **部分**：路线甲没有把 $\rho_K$ 的定义展开成量词串，读者要自己补 "inf over instances and tie-breaks"。与 GAP-1 同源 |
| 19. 隐含：normalization $f(\emptyset)=0$ 与 $\tilde f(\emptyset)=0$ | app:validity 第 2168 行 "let $f$ be monotone submodular with $f(\emptyset)=0$, let $\tilde f$ be an arbitrary set function with $\tilde f(\emptyset)=0$"；telescoping $\sum_{t<K}d_t=f(S^K)$ 用到它（`lem:app-relaxation` 第 2300 行）；构造侧 app:exact 第 859 行 "$f(\emptyset)=1-1=0$ and $\tilde f(\emptyset)=W(0)-W(0)=0$" | OK |
| 20. 隐含：OPT > 0 | app:exact 第 602 行与 app:validity 第 2172 行都直接取 $f(O^{\ast})=1$（归一化）；$f(O^{\ast})=0$ 的情形由 `model.tex` 第 15 至 16 行的约定"every ratio statement is read as holding trivially"承担 | OK(隐含)（路线甲无句子，属模型层继承；构造侧 $f(O)=1>0$ 自动满足） |
| 21. 隐含：$O^{\ast}$ 确实是最优 $K$-集 | 上界侧 `\emph{The optimum.}`（931）"for every $S$ with $|S|\le K$ one has $f(S)\le1$ ... So $f(O^{\ast})=1$ with $O^{\ast}=O$"；下界侧 app:validity 第 2172 行 "Fix an optimal set $O^{\ast}=\{o_1,\dots,o_K\}$" | OK |
| 22. 隐含：$|O^{\ast}|<K$ 的退化情形 | app:validity 第 2173 行 "(if $|O^{\ast}|<K$, set $g_{t,i}=0$ for the unused indices; every case (a) below covers them)" | OK |
| 23. 隐含：$f$ monotone submodular | 下界侧 app:validity `lem:app-sum`（2198，submodularity 加 monotonicity）、`lem:app-mono`（2239，diminishing returns）、`lem:app-sign`（2190，monotonicity）；`rem:app-census`（2330）逐族列出各自消费的假设；上界侧 `\emph{Monotonicity and submodularity of $f$.}`（885）九个二阶差分加 `lem:app-count` | OK（构造侧九个二阶差分 [VERIFIED-SYMBOLIC]，`results/N2_check.py` Part 4；$K\le6$ 全格点 [VERIFIED-LP]，Part 2） |
| 24. 隐含：$\tilde f$ 不必 submodular（只需 band 与 $\tilde f(\emptyset)=0$） | app:validity 第 2168 行 "an arbitrary set function"；`rem:app-census`（2330）末句 "No family uses submodularity of $\tilde f$"；构造侧 app:exact 第 884 行注释 "ftilde is monotone but not submodular (Part G)" | OK |
| 25. 隐含：拆分 $(\eta_u,\eta_o)$ 与乘积 $\eta$ | 下界侧四条约束只含 $\eta$（`\eqref{eq:redlp}`，第 618 至 630 行）；上界侧 `\paragraph{Upper bound}`（835）"fix **any** split $\eta_u\eta_o=\eta$ with $\eta_u,\eta_o\ge1$"，`\emph{The error is exactly $(\eta_u,\eta_o)$.}`（910）证明两个因子都被取到；model.tex 的 `lem:scaling`（第 44 至 56 行）给类意义的不变性 | OK（达到方向对每个拆分成立，强于陈述所需） |
| 26. 形容词 "error **exactly** $(\eta_u,\eta_o)$"（只在上界侧出现，不在陈述里） | app:exact 第 910 行起有构造侧的论证（三个比值 $1/\eta_u\le k_1/(K\eta_u)\le\eta_o$，外两个取到）；但 `def:eta`（model.tex 第 23 至 32 行）只定义 "error **at most** $(\eta_u,\eta_o)$"，全文没有 "exactly" 的定义句 | **部分（定义缺口，与 `results/V11/audit/ceiling.md` 第 7 行同源）**：对 thm:exact 不是承重项，"at most" 已足够支撑 $\rho_K\le V_j$；记录以便统一处理 |
| 27. 隐含：$\eta=1$ 与乘子里的 $\eta-1$ 分母 | `\emph{Nonnegativity.}`（663）末段处理 $j=K-1$（段 $[1,2]$）：$\lambda_C(K-1)$ 定义为 0，$\lambda_P(K-1)$ 由约分定为 $1/K$，"So \eqref{eq:duals-jpos} has no singularity on any segment"；`\emph{(a)}`（704）末段用 $\eta\to1$ 的连续性把恒等式延到 $\eta=1$ | OK（本审计另核 $\min_jV_j(1)=1-(1-1/K)^K=L_K(1)$，$K=2..8$ [VERIFIED-SYMBOLIC]，§5 第 7 条，与台账"η=1 时 ρ_K(1)=L_K(1)"一致） |
| 28. 隐含：固定 $K$ 步（不提前停） | model.tex 第 70 至 74 行 "The run always executes exactly $K$ steps"；下界侧 reduced LP 的变量就是 $d_0,\dots,d_{K-1}$（第 610 至 617 行）；上界侧 `\emph{The greedy induction.}`（961）跑满 $K$ 步，并证明第 $t\ge j$ 步一定有可选的 $P$ 元素（"which is available because $t-j<K-j=|P|$"） | OK |
| 29. 隐含：$|S|\le K$（可行性）与 OPT 的定义 | `\emph{The optimum.}`（931）对 $|S|\le K$ 取 max；model.tex 的 problem definition | OK |
| 30. 隐含：tie-breaking 约定与 $e_t\in O^{\ast}$（zeroing convention） | app:validity 第 2176 至 2188 行的 zeroing convention 与三分情形 (a)(b)(c)，四个 lemma 每个都单独处理 case (c)（`lem:app-pred` 2233、`lem:app-mono` 2248、`lem:app-cons` 2285） | OK（这一段的 bookkeeping 状态 [HAND-PROOF-UNREVIEWED]，见第 32 行） |
| 31. 隐含：mono 族乘子恒为 0 | 第 660 至 662 行 "All multipliers of the family $\mathrm{mono}$ are $0$: the lower bound does not use that the optimal gains decrease along the run"；`results/N1_dual_certificate.py` Corollary A（删掉 mono 行不改 LP 值） | OK |
| 32. 隐含：每个 run 给出 LP 可行点（relaxation 方向），反向不声称 | `lem:app-relaxation`（2291）与 `rem:app-status`（2306）"The reverse direction ... is not claimed here; the attaining instances of Appendix~\ref{app:exact} supply what the theorem needs instead" | OK（逻辑闭合：$\rho_K\ge\mathrm{LP}\ge V_j$ 加实例 $\rho_K\le V_j$）。状态：slack 恒等式 [VERIFIED-SYMBOLIC]（`results/H3_j2_recheck.py`、`results/J2_core_oracles.py`），周边 bookkeeping [HAND-PROOF-UNREVIEWED] |
| 33. 隐含：哪条约束吃哪把尺子（$\eta$ 对 $\eta^{\mathrm{tr}}$、$\eta^{\mathrm{sel}}$） | `rem:app-rulers`（2315）末句 "the exact value of Theorem~\ref{thm:exact} is stated for the global $\eta$"；台账 T6 的"禁止声称"条同 | OK |
| 34. deterministic / randomized 量词、fixed random string | 陈述里没有随机算法子句；predictive greedy 是确定性算法，唯一的非确定性是 tie，由 adversary 解（model.tex 第 70 至 71 行） | **N/A**（本条目无随机段落，故也没有"fixed random string"或 expectation 量词要审） |
| 35. 查询预算与查询集合大小（$\le nK$、$|S|\le K$、arbitrary query access） | 陈述里没有这些形容词；它们属于 T10c（thm:linear-exact）与 T8（thm:ceiling） | **N/A** |

### 2.1 GAP 汇总

- **GAP-1（唯一的真 GAP）：$n$ 量词在路线甲的 app:exact 里没有落点。** 陈述与台账都把它放在陈述之外
  （正文 `rem:exact-n`、台账单列条目），而 app:exact 的上界构造固定用 $n=2K$，下界的 reduced LP 不含 $n$。
  从"某个 $n=2K$ 的实例"到"每个 $n\ge2K$ 的 $\rho_{n,K}$"这一步只由 `rem:exact-n` 的两句话
  （restriction 到 $T\cup O^{\ast}$、padding 零增益元素）承担，状态 [HAND-PROOF-UNREVIEWED]，
  且正文注释自述是本地重构。$K\le n<2K$ 完全不在覆盖内。
  保守处理：不动正文，只记录；矩阵里本条目的 n 量词应标成"陈述外 remark，未复核"。
- **部分-1（表第 13 行）**："exactly when $\eta\ge K$" 的必要方向（$\eta<K$ 时严格小于 $1/\eta$）
  在路线甲没有写出的结论句，虽然它是同一段相邻差恒等式在 $i=0$ 的一行推论。
  证据充分（§5 第 3 条 [VERIFIED-SYMBOLIC]；oracle C0c [VERIFIED-SYMBOLIC]），缺的只是一句话。
- **部分-2（表第 18 行）**：$\rho_K$ 的定义在 model.tex 只有一句，没有展开成量词串；路线甲沿用它。
  逐量词展开只存在于路线二 `results/V11/route2/exact.md` §1。
- **部分-3（表第 26 行）**："error exactly $(\eta_u,\eta_o)$" 在 model.tex 没有定义句（`def:eta` 只有
  "at most"）。与 `results/V11/audit/ceiling.md` 的同名缺口是同一条，应一并处理。
  对 thm:exact 不承重。
- 次要记录（不计入 GAP）：表第 4、20 行是 OK(隐含)；表第 9 行记录了两个方向对段端点的定义域不对称
  （上界只要左端 $\eta\ge K-j$，右端只在下界的 $\lambda_S(j)\ge0$ 里用），两侧合起来仍覆盖 $\eta\ge1$ 的全部；
  表第 30、32 行的 bookkeeping 状态仍是 [HAND-PROOF-UNREVIEWED]。

---

## 3. TASKS11 的两个条件问题

两个都不适用于本条目，按要求明确记录：

- **"fixed random string" 量词是否在陈述里**：这是 thm:ceiling（T8）的专项问题。thm:exact 没有随机
  段落，陈述与台账都不含 randomized 子句，见 E 表第 34 行。thm:ceiling 的答案在
  `results/V11/audit/ceiling.md` §3（结论：不在陈述里，且这是正确的取法）。
- **$n\ge4K^5$ 能否收紧到约 $K^3(K-1)^2/2+K^2$**：这是 thm:linear-exact（T10c）的专项问题，
  依赖 `app:greedybudget` 的计数链（`paper/sections/appendix_proofs.tex` 第 1701 行起），
  与 thm:exact 的 $n$ 量词（GAP-1 里的 $n\ge2K$）无关。本文件不回答该问题，也没有读那条计数链。

---

## 4. 与路线二、oracle 的对照（只作参照，不计入 E 表）

- 路线二 `results/V11/route2/exact.md` §1 把 $\rho_K$ 的定义展开成 Q1 至 Q6 六个量词，其中 Q1 明写
  "下界方向对任意 $n\ge K$ 成立；上界方向的 attaining instance 用 $n=2K$，因此 inf 在 $n=2K$ 处取到"。
  注意这与正文的口径不同：路线二把 $\rho_K$ 定义成对 $n$ 取 inf，正文定义成 $n\ge2K$ 的公共值。
  两者在 $n\ge2K$ 上一致，在 $K\le n<2K$ 上不一致（那里 $\rho_{n,K}$ 更大）。这一条并入 GAP-1 记录。
- oracle `results/V11/oracle/exact.log` 的七项全 PASS：C0a（$V_j$ 闭式恒等式，$K=2..8$，35 条）、
  C0b（段上 $V_j=\min_iV_i$，168 个有序对，无内部根）、C0c（$\rho_K=1/\eta\iff\eta\ge K$，含 $\eta<K$ 的
  严格不等号）、C1（精确有理 simplex 复跑 `code/reduced_lp.py`，100 个 LP）、C2（逐点 primal-dual 证书）、
  C3（$K=2,3,4$ 印刷闭式）、C6（与浮点 scipy 交叉核对，最大偏差 3.33e-16）。
  该目录缺 `exact.md`（其余条目都有），只有 `.py/.log/.json`。记录，不补。

---

## 5. 本文件自身算术的核对

临时脚本（不入库，位于本次会话的 scratchpad）用 sympy 与 `fractions.Fraction` 做了九条精确核对，
residual 全为 0，状态 [VERIFIED-SYMBOLIC]（第 6 条为 [VERIFIED-EXHAUSTIVE]，有理网格穷举）：

1. $V_i-V_{i+1}=q^i(K-i-\eta)/(K\eta k_1)$，$K=2..8$，$0\le i\le K-2$；
2. $V_0=1/\eta$，$K=2..8$；
3. $V_0-V_1=(K-\eta)/(K\eta k_1)$，$K=2..8$（E 表第 13 行的一行推论）；
4. $K=3$ 的三个印刷闭式分别等于 $V_2,V_1,V_0$（段 $[1,2],[2,3],[3,\infty)$）；
5. $K=4$ 的四个印刷闭式分别等于 $V_3,V_2,V_1,V_0$（段 $[1,2],[2,3],[3,4],[4,\infty)$）；
6. $K=2..6$、$\eta$ 取 $[1,K+2]$ 内的四分之一有理网格，最小化指标与段规则一致，无反例；
7. $\min_jV_j(1)=1-(1-1/K)^K=L_K(1)$，$K=2..8$；
8. 上界实例的输出值 $1-q^j+(K-j)q^j/(K\eta)=V_j$，$K=2..8$、$0\le j\le K-1$；
9. 恒等式 `eq:W0-identity`：$W(0)-(K-1)\eta_o/K=1/(K\eta_u)$（符号 $K,\eta_u,\eta_o$）。

更强的证据不由本文件产生：一般 $K$ 对偶证书见 `results/N1_dual_certificate.py`（320/320 PASS），
达到实例见 `results/N2_check.py`（480/480 PASS），精确有理 LP 见 `results/V11/oracle/exact.py`。
路线甲的装配（app:validity 的 zeroing convention、三分情形、`lem:app-relaxation`，以及 `rem:exact-n`
的 restriction 加 padding）仍是 [HAND-PROOF-UNREVIEWED]。

---

## 6. 读过的文件

- `results/V11/statements.md`（第 171 至 201 行，T6 段）
- `results/V11/inputs/statement_exact.md`、`results/V11/inputs/definition1.md`、`results/V11/inputs/assumptions.md`
- `THEOREM_LEDGER.md`（第 92 至 123 行，卡 `## T6` 与 `## T6b`）
- `paper/sections/results.tex`（第 150 至 400 行，含 `sec:exact`、`thm:exact`、`rem:exact-n`、`prop:rigidity`、
  `rem:rigidity-breakpoints`、`rem:rigidity-ties`、`rem:exact-gap`）
- `paper/sections/model.tex`（第 1 至 110 行）
- `paper/sections/appendix_proofs.tex`（第 582 至 1012 行 `app:exact`；第 2149 至 2347 行 `app:validity`）
- `results/N1_dual_certificate.py`、`results/N1_dual_certificate.md`（§0）
- `results/N2_check.py`（文件头与 Part 清单）、`results/N2_instances.md`（§0）
- `code/reduced_lp.py`、`results/T3_duals.py`（文件头与行序约定）
- `results/V11/oracle/exact.log`、`results/V11/route2/exact.md`（§1，仅作对照）
- `HANDOFF_2026-09-18.md`（§3、§4）、`HANDOFF_ADDENDUM_2026-09-18.md`（A、B 节）
- `results/V11/audit/ceiling.md`（格式与同源缺口对照）

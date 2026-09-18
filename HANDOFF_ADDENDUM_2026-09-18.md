# HANDOFF ADDENDUM 2026-09-18（晚）

附在 HANDOFF_2026-09-18.md 之后。新对话读完主文件再读这份。本文件里的决定覆盖主文件中与之冲突的内容。

---

## A. 写作风格（最高优先级，每次出草稿前重读）

Cici 的口味只有一条：短句，用词准，不说废话。具体到可执行：

1. 每句一个意思。超过 25 个词就拆。
2. 主语写实。不用 it、this、the latter、the former 指代前文。
3. 先答案后理由。每节前两句：第一句是这节回答的问题，第二句是答案。
4. 先数字后符号。每条定理后面给 running example 的数（$K=3$，$\eta=3/2$）。
5. 禁用的句式：in the sense in which；in the terms of；the observation that X approximates the Y it approximates；as well as … also；it is worth noting；note that；we remark that。
6. 禁用的词：elementary、trivial（用 simple）；genuinely、honestly；robust（描述我们的算法时）；bridges the gap；novel；unconditional（用 regardless of the number of queries）。
7. brief 的"必含"项不是逐条塞进正文的清单。能合并的合并，能进附录的进附录，能删的删。
8. 正文不出现状态标签、仓库行号、label 名。
9. 全文一个比喻：price。information price、efficiency price、the price of the error。不用 cost。
10. 每段一行源码。公式为省空间用 \( \) 行内，除非必须独立成行。
11. 写完自己读一遍。任何一句需要读两遍才懂，重写。
12. 不给三个版本让她选。她定了的事直接执行。没定的事只给一个建议加一句理由。

对照样本：3.1 节的重写版（本文件 §C）是目标风格。新对话 9-18 下午那版 3.1 是反面样本，内容对、写法糊。

---

## B. 主文件之后新定的事

1. thm:ceiling 降为 Proposition，标题 "Upper bound for unbounded queries"。label 不改。正文定理重编号：Theorem 1 = thm:exact（$\rho_K$ 精确值），Theorem 2 = thm:linear-exact（J6），Theorem 3 = thm:hardness。任意大小查询的结果仍是 Proposition。
2. 降级理由（写进正文，说在审稿人前面）：达到方向是 Horel–Singer 引言的观察加 Prop 2(iii)（$\epsilon=(\eta-1)/(\eta+1)$ 代入 $\frac{1-\epsilon}{1+\epsilon}=1/\eta$）；上界方向是值空间的标准构造换成边际增益度量。两个方向各三行。
3. Proposition 只陈述 $n\ge2K$，$K\ge1$。$K\le n<2K$ 的精确值 $K/((2K-n)+(n-K)\eta)$ 与逐实例式进附录 remark。达到方向的状态是 [HAND-PROOF-UNREVIEWED, J5 套 A]，不是 [CONJECTURE]，主文件 §4 写旧了。随机段落进附录。
4. 贡献列表保留信息价格这一条，参照点语气：we record the information price $1/\eta$, which every later bound is measured against; both directions are simple once the error is measured on marginal gains。
5. "value accuracy is not sufficient" 必须限定。对不限查询的算法它是假的（穷举拿 $\frac{1-\epsilon}{1+\epsilon}$）。只能说：value accuracy 不给 $\eta$ 上界；对 predictive greedy 不够（Horel–Singer 的 $\epsilon<1/K$ 阈值，proposition 编号待核）。落点三处：Model 的 Prop 2 读法句；intro 第 13 句前加 for predictive greedy；Prop 2 标题改成 "Value accuracy is neither sufficient nor necessary for predictive greedy"。
6. 转述 Horel–Singer 和 Hassidim–Singer 的不可能性必须带 with polynomially many queries（HS：fewer than exponentially-many queries）。intro 第 6 句同。
7. Singer–Vondrák 2015（NeurIPS 28，pp. 3204–3212，官方元数据）进 related work 第一组，半句，读正文前不写查询限定。
8. Model 的 Prop 2 读法句定稿：
   Proposition~\ref{prop:nobound} says that no guarantee independent of the error exists. Proposition~\ref{prop:valueacc} says that value accuracy does not bound the marginal-gain error (i), so no guarantee in $\eta$ follows from value accuracy, and that predictive greedy does not need value accuracy (ii); a bounded marginal-gain error implies value accuracy up to scale (iii), but not conversely. The marginal-gain condition is therefore the stronger one, and it is the condition predictive greedy responds to. Definition~\ref{def:eta} is the only assumption on the surrogate in the rest of the paper. Proofs of both propositions are in Appendix~\ref{app:model}.
9. Prop 1 陈述里 "satisfying the remaining assumptions of this section" 改成 "satisfying every assumption of this section except a bound on $\eta$"。
10. 附录 app:model 已写（outputs/appendix_model_proofs.tex）：Prop 1 用 $\tilde f(S)=|S|$ 加模函数 $f(S)=|S\cap O|+\delta|S\setminus O|$，$\delta=K/(n-K)$，$\eta=1/\delta$；remark 说任意 $\delta$ 成立故退化速度至少 $1/\eta$。Prop 2 (i) 两元素构造 $f(\{a,b\})=1+\epsilon$、$\tilde f(\{a,b\})=1$；(ii) 一行；(iii) 链求和加缩放。末尾 remark 记路线乙。状态：Prop 2(iii) 已由 Cici 读过并经随机 oracle（96 个合法 surrogate，零违反）核过，可标 [HAND-PROOF-REVIEWED] + [VERIFIED-EXHAUSTIVE (random)]；其余 [HAND-PROOF-UNREVIEWED]，Cici 待读。要与台账 T1 的构造对齐，二者只留一个。
11. 3.1 正文达到方向用路线乙（引 Horel–Singer 加 Prop 2(iii)），附录用路线甲（三行自足）。
12. 多项式查询那一档在小 $K$ 时不比 $1/\eta$ 紧：$K=3$、$\eta=3/2$、$c=1$ 时 $H_{3,2}=0.784>0.667$，$K=5$ 才降到 $0.634$。第 5 节写成 $\min\{H_{K,\tau}(\eta),1/\eta\}$；四档梯子的展示例子用 $K\ge5$，或在 $K=3$ 那行填 $1/\eta$ 并注明 $H$ 不 binding。
13. predictive greedy 不是新算法。写法定稿在 Model 的 Algorithm 段。intro 第 9 句同步。只有 ProbeLottery 可以写 we construct。
14. GS 2007 的 setting 与我们不同：他们 $f$ 已知、近似在"找最大"一步（计算原因）；我们 $f$ 不可见、对 $\tilde f$ 精确取 argmax（信息原因）。Definition 1 蕴含每步是 GS 意义的 $1/\eta$-approximate step，故其定理黑箱可用。这句放第 4 节 Prop 3 处。bib 键 goundan2007revisiting（Optimization Online 2007/08/1740）。
15. 图 1 气泡文字定稿：左 "Surrogate $A$ is within 10% of $f$, $B$ within 30%. Which one should greedy trust?"；右 "The surrogate with 30% error reached the optimum; the one with 10% error did not."

---

## C. 3.1 节目标风格样本（Cici 认可的写法，内容以此为准）

\subsection{What can any algorithm guarantee?}\label{sec:ceiling}

Suppose an algorithm may query the surrogate as often as it likes but never sees $f$. How much of $\mathrm{OPT}$ can it guarantee when the marginal-gain error is $\eta$? The answer is $1/\eta$, and it is exact.

[Proposition thm:ceiling 陈述]

Both directions take three lines. For the upper bound, give the algorithm $\tilde f(S)=c|S|$. This surrogate says nothing about $f$, so the algorithm's queries and its output $T$ are fixed before $f$ is chosen. Pick a $K$-set $O$ disjoint from $T$, which exists since $n\ge2K$, and let $f$ be modular with weight $c\eta_u$ on $O$ and $c/\eta_o$ elsewhere. Definition~\ref{def:eta} holds with both factors attained, $f(O)=cK\eta_u$, and $f(T)\le cK/\eta_o=f(O)/\eta$. For the lower bound, add the elements of any set one at a time and apply the band to each step; this gives $f(S)/\eta_u\le\tilde f(S)\le\eta_o f(S)$ for every $S$. A set $\hat S$ maximizing $\tilde f$ therefore satisfies $f(\hat S)\ge\tilde f(\hat S)/\eta_o\ge\tilde f(O^{\ast})/\eta_o\ge f(O^{\ast})/\eta$. Neither direction uses anything about $\tilde f$ beyond the band. With $K=3$ and $\eta=3/2$, the adversary gives $f(T)=3$ against $f(O)=9/2$, the ratio $2/3=1/\eta$.

The lower bound is not new. \citet{horel2016maximization} note that a maximizer of a function within $1\pm\epsilon$ of $f$ is a $\frac{1-\epsilon}{1+\epsilon}$-approximation for $f$; by Proposition~\ref{prop:valueacc}(iii) with $\epsilon=(\eta-1)/(\eta+1)$ this is $1/\eta$. The upper bound is the value-space adversary of that line with the error measured on marginal gains.

We record the result because everything after it is measured against it. The factor $1/\eta$ is paid by every deterministic algorithm, however many queries it makes, and it is recovered by an algorithm that uses nothing but the band. It is the price of the error itself; only a better surrogate reduces it. At $\eta=1$ it equals $1$: with marginal gains correct up to scale, unlimited queries recover the optimum. As $\eta\to\infty$ it tends to $0$, and with no bound on $\eta$ Proposition~\ref{prop:nobound} rules out every constant. Optimization from samples \citep{balkanski2017limitations}, whose guarantees bound values on most sets and leave marginal gains free, sits at this end of the curve.

Two refinements are in Appendix~\ref{app:ceiling}. The same construction bounds randomized algorithms by $(1-\frac Kn)\frac1\eta+\frac Kn$ in expectation; their exact value is open. For $K\le n<2K$ every $K$-set shares at least $2K-n$ elements with $O^{\ast}$, and the exact deterministic value is $K/((2K-n)+(n-K)\eta)$.

This is a statement about information, not computation: exhaustive search evaluates $\binom nK$ predicted sets. Section~\ref{sec:exact} asks how far below $1/\eta$ predictive greedy sits, and Section~\ref{sec:hardness} what polynomial budgets can reach.

---

## D. 两个对话的分工

- 旧对话（有完整决策链）：判断、红队、措辞准不准、与已定决策的一致性。
- 新对话（读过仓库）：Claude Code 任务包、附录转录、复核清单、brief、行号与 label。
- 任何一方新定的事，当天写进 addendum，另一方同步。

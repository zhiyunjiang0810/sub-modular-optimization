# 量词审计（criteria A 与 E）：thm:ceiling / 台账 T8（TASKS11 Q3）

本文件只做两件事：A 项逐量词比对正文环境与台账卡；E 项建立量词审计表，把陈述里的每个量词与形容词
落到路线甲证明的具体位置，落不上的记 GAP。

范围与纪律：不修改任何已有文件，不运行 git。本文件自身的算术用 sympy 精确核对（脚本见 §6），
浮点只出现在打印里。状态标签按 CLAUDE.md：[VERIFIED-SYMBOLIC] [VERIFIED-LP] [VERIFIED-EXHAUSTIVE]
[HAND-PROOF-UNREVIEWED] [CONJECTURE] [FAILED]。读过的文件见 §7。

按 HANDOFF_ADDENDUM 的 B.1 与 B.3，本条目已降为 Proposition，标题 "Upper bound for unbounded
queries"，label 不改；正文只留 $n\ge2K$，$K\le n<2K$ 的精确值进附录 remark；随机段落进附录。
**这三项改动在正文里只做了第一项**，见 A 项差异 D1、D6、D7。

---

## 1. Criterion A：正文陈述与台账陈述的逐量词比对

### 1.1 三段原文

正文（`paper/sections/results.tex` 第 441 至 463 行，environment `proposition`，label `thm:ceiling`）：

```latex
\begin{proposition}[Upper bound for unbounded queries]
\label{thm:ceiling}
Let $2\le K\le n$.  For every deterministic algorithm with arbitrary query
access to $\tilde f$ and output of size at most $K$, and every
$\eta_u,\eta_o\ge1$, there is a pair $(f,\tilde f)$ with error exactly
$(\eta_u,\eta_o)$ on which the output $T$ satisfies
$f(T)\le C^{*}_{n,K}(\eta)\,f(O^{\ast})$, where
\[
  C^{*}_{n,K}(\eta)\;=\;\frac{K}{K+(\eta-1)\min\{K,\,n-K\}}
  \;=\;\begin{cases}
    \dfrac{K}{(2K-n)+(n-K)\eta}, & K\le n\le2K,\\[6pt]
    1/\eta, & n\ge2K.
  \end{cases}
\]
Conversely, a set $S$ maximizing $\tilde f$ over all $K$-subsets satisfies,
on every instance and for every optimal $K$-set $O^{\ast}$,
\[
  f(S)\;\ge\;\frac{K}{K+(\eta-1)\,|O^{\ast}\setminus S|}\,f(O^{\ast})
  \;\ge\;C^{*}_{n,K}(\eta)\,f(O^{\ast}),
\]
so exhaustive search over predicted values attains the ceiling for every
$n$.
\end{proposition}
```

正文紧随其后、在 environment 之外的一段（第 464 至 473 行）：随机算法上界
$\mathbb E[f(T)]\le((1-\frac Kn)\frac1\eta+\frac Kn)f(O^{\ast})$（$n\ge2K$，"there is a fixed pair"，
"expectation over the algorithm's randomness"，并声明这只是上界不是精确随机值），加 $n=3$、$K=2$、
$\eta=3$ 的反例与 randomized minimax 仍 open。

台账（`THEOREM_LEDGER.md` 第 162 至 204 行，卡 `## T8 thm:ceiling`）。卡里有两段：
散文陈述（"台账陈述（逐字）"）与 LaTeX 块（`results/V11/statements.md` 第 72 至 120 行的
"正文陈述（逐字，LaTeX）"）。LaTeX 块与正文逐字符相同，只差 environment 与标题：
台账用 `\begin{theorem}[Deterministic ceiling, all ground-set sizes]`。
散文陈述为：2 ≤ K ≤ n，确定性、任意查询次数与大小、输出 ≤ K；minimax 值
C*_{n,K}(η) = K/(K+(η−1)·min{K, n−K})；上界侧对每个确定性算法存在实例（f̃ = b|S| 加 modular 高低权 f，
任意拆分实际误差两端恰取到，n=K 用混合高低权校准）；下界侧穷举 argmax_{|T|=K} f̃ 在每个实例上 ≥ C*，
并有更强的逐实例式 f(S)/f(O) ≥ K/(K+(η−1)|O∖S|)，无最小重叠假设。随机版在卡里单列一条。

### 1.2 逐项对照

| 量词 / 形容词 | 正文 | 台账 | 判定 |
|---|---|---|---|
| 定义域 $2\le K\le n$ | 有 | 有（散文与 LaTeX 块都有） | 一致 |
| ∀ deterministic algorithm | 有 | 有 | 一致 |
| 形容词 arbitrary query access to $\tilde f$ | 有，在陈述内修饰被全称的算法 | 有，"任意查询次数与大小" | 一致（措辞差异见 D3） |
| 形容词 output of size at most $K$ | 有 | 有，"输出 ≤ K" | 一致 |
| ∀ $\eta_u,\eta_o\ge1$（拆分全称） | 有，与算法并列的第二个全称 | LaTeX 块有；散文里降级为上界侧括号内的说明"任意拆分" | 一致（位置差异见 D4） |
| ∃ pair $(f,\tilde f)$，在算法之后 | 有 | 有（"对每个确定性算法存在实例"） | 一致 |
| 形容词 error exactly $(\eta_u,\eta_o)$ | 有 | 有（"实际误差两端恰取到"） | 一致（"exactly" 无定义，见 E 表第 7 行） |
| 结论 $f(T)\le C^{*}_{n,K}(\eta)f(O^{\ast})$ 与两分支 | 有 | 有 | 一致（分支恒等式 [VERIFIED-SYMBOLIC]，§6） |
| 逆向：$S$ maximizing $\tilde f$ over all $K$-subsets | 有（"all $K$-subsets"，即 $|S|=K$） | 有（argmax_{|T|=K}） | 一致 |
| 逆向的 on every instance | 有 | 有（"在每个实例上"） | 一致 |
| 逆向的 for every optimal $K$-set $O^{\ast}$ | 有 | 散文写 "f(S)/f(O)"，未显式写"对每个最优解" | **差异 D2** |
| 逐实例式 $K/(K+(\eta-1)|O^{\ast}\setminus S|)$ | 有 | 有 | 一致 |
| 无最小重叠假设 | 未写（由逐实例式蕴含） | 显式写出 | 一致（蕴含关系，不记差异） |
| environment 与标题 | `proposition`，"Upper bound for unbounded queries" | `theorem`，"Deterministic ceiling, all ground-set sizes"；`statements.md` 元数据行也写 `theorem` | **差异 D1** |
| minimax 用词 | 不出现 | 散文称 "minimax 值" | **差异 D5** |
| 随机上界 $(1-\frac Kn)\frac1\eta+\frac Kn$ | 在 environment 之外的正文段 | 卡里单列一条 | 一致（两边都在陈述之外；位置问题见 D6） |
| 随机段的量词"逐算法固定实例、对算法随机性取期望" | 有 | 有（"逐算法固定实例量词"） | 一致 |
| 随机段的 "fixed random string" | **不出现** | 不出现 | 一致（并且这是正确的取法，见 §3） |
| $n\ge2K$ 与 $K\le n<2K$ 的分工 | 合并在一个 Proposition 里 | 卡里合并，`statements.md` 另给 "TASKS11 要求的拆分读法" | **差异 D7**（相对 addendum B.3 的目标形态） |

### 1.3 A_diffs（差异清单）

- **D1（environment 与标题）**：正文是 `proposition` + "Upper bound for unbounded queries"；
  台账 LaTeX 块与 `results/V11/statements.md` 第 74 行的元数据行仍写 `theorem` +
  "Deterministic ceiling, all ground-set sizes"。这是 addendum B.1 的降级尚未回写台账。
  数学内容不受影响，但矩阵里两栏取自不同来源时会不一致。
- **D2（逆向的 $O^{\ast}$ 全称）**：正文写 "for every optimal $K$-set $O^{\ast}$"；台账散文只写
  f(S)/f(O)，没有把"对每个最优 K-集"提成全称。路线甲的证明对任取的最优 $O$ 成立（附录
  "The unified per-instance guarantee" 段第一句 "let $O$ be an optimal $K$-set"），所以正文强、台账弱，
  方向安全，但两边不同字。
- **D3（查询的形容词范围）**：台账写"任意查询次数与大小"，两项；正文只写 "arbitrary query access to
  $\tilde f$"，没有点出"任意大小的集合查询"。两者意图相同，正文的措辞把"大小"留给读者推断。
- **D4（拆分全称的位置）**：正文把 $\forall\eta_u,\eta_o\ge1$ 与 $\forall$ 算法并列写在前件；台账散文把它
  放进上界侧构造的括号里。LaTeX 块无此差异。两个全称可交换，判定为位置差异。
- **D5（minimax 用词）**：台账散文称 C* 为 "minimax 值"，正文不用这个词，只分两个方向陈述。
  两个方向合起来确实给出确定性 minimax 值，所以不是内容差异；但台账同卡的"禁止声称"条明确
  C* 不是随机 minimax 值，正文不使用该词更安全。
- **D6（随机段落的位置）**：addendum B.3 要求随机段落进附录，正文第 464 至 473 行仍在主文。
  与台账不冲突（台账也单列），记为待办差异。
- **D7（$n$ 区间的分工）**：addendum B.3 要求 Proposition 只陈述 $n\ge2K$、$K\ge1$，
  $K\le n<2K$ 的精确值与逐实例式进附录 remark。正文与台账都仍是 $2\le K\le n$ 的统一陈述。
  连带后果：正文的 $K\ge2$ 与附录 app:ceiling 开头固定的 $K\ge1$ 不一致（见 E 表第 1 行）。

**A_match = false**（有 D1 至 D7 七项；其中 D1、D6、D7 是与已定决策的偏差，D2 至 D5 是措辞与位置差异）。
若只比对台账 LaTeX 块与正文环境体（去掉 environment 名与标题），二者逐字符相同。

---

## 2. Criterion E：量词审计表（落到路线甲）

路线甲 = `paper/sections/appendix_proofs.tex` 的 `\subsection{The ceiling ...}\label{app:ceiling}`
（第 1211 至 1372 行）加 `results/J5_hardcore/J5_ceiling_proof.md`。
段落锚点：`\paragraph{The construction.}`（1219）、`\paragraph{Deterministic algorithms.}`（1237）、
`\paragraph{Randomized algorithms.}`（1246）、`\paragraph{The matching upper bound by exhaustive
search.}`（1258）、`\paragraph{The unified per-instance guarantee.}`（1277，内含 Step 1/2/3 与
式 `eq:ceiling-slack`）、`\paragraph{The matching adversary for every $n>K$.}`（1341）、
`\paragraph{Scope.}`（1353）。

状态列的含义：**OK** = 路线甲有明确处理；**OK(隐含)** = 有处理但未写成独立句子；
**GAP** = 路线甲没有对应位置。

| 量词 / 形容词 | 处理位置（file + paragraph） | 状态 |
|---|---|---|
| 1. 定义域下端 $K\ge2$ | app:ceiling 开头 "Fix $\eta_u,\eta_o\ge1$, $K\ge1$, $n\ge2K$"（1217）只要 $K\ge1$；J5 §1 用 $2\le K\le n$；Step 1 的交换对 $K=1$ 同样成立 | **GAP（方向相反）**：陈述比证明更强，$K\ge2$ 在路线甲无处使用。oracle C1b 对 $K=1$、$n=2..10$ 单独跑过 [VERIFIED-EXHAUSTIVE]，无违反 |
| 2. 定义域上端 $K\le n$ | app:ceiling "The matching adversary for every $n>K$" 段末句处理 $n=K$（输出整个 ground set，比值 1，端点用混合高低权校准）；J5 §4 末段同 | OK |
| 3. ∀ deterministic algorithm | app:ceiling "Deterministic algorithms" 段首句 "The transcript of a deterministic algorithm querying $\tilde f$ is the same for every $O$"；"The matching adversary" 段 "its transcript and output are fixed" | OK |
| 4. arbitrary query access（次数与大小都不限） | 同上两段：$\tilde f(S)=c|S|$ 与 $\tilde f(T)=b|T|$ 不依赖 $O$，故任意多次、任意大小的查询都不透露信息 | OK（"大小"未点名，与 D3 对应） |
| 5. output of size at most $K$ | app:ceiling "Deterministic algorithms" 段 "its output $T$, $|T|\le K$"；"The matching adversary" 段 "Complete the output to a $K$-set $S$ if necessary ... a smaller output is only worse"；J5 §4 "原算法若输出更小的集合，其真实价值不超过 f(S)" | OK |
| 6. ∀ $\eta_u,\eta_o\ge1$（任意拆分） | app:ceiling "The construction" 段：gains 为 $c/\eta_o$（$B$ 上）与 $c\eta_u$（$O$ 上），"the error is exactly $(\eta_u,\eta_o)$ with both factors attained"；"The matching adversary" 段 "the single-element and all-pairs errors equal the prescribed split exactly" | OK |
| 7. error **exactly** $(\eta_u,\eta_o)$（"exactly" 这个词本身） | 构造侧有（两个因子都取到，并用 modular 性把 all-pairs 也压成两值的加权平均）；但 `paper/sections/model.tex` 的 Definition~\ref{def:eta}（第 23 至 32 行）只定义 "error **at most** $(\eta_u,\eta_o)$"，"exactly" 在全文没有定义句 | **GAP（定义缺口）**：需一句"最小可行因子恰为 $(\eta_u,\eta_o)$"的约定。oracle C1 对 186 个实例精确算最小因子并核对 [VERIFIED-EXHAUSTIVE] |
| 8. ∃ pair $(f,\tilde f)$ 在算法之后（量词顺序） | app:ceiling "Deterministic algorithms" 段 "is fixed before $O$ is chosen" | OK |
| 9. 分支 $n\ge2K$，值 $1/\eta$ | app:ceiling "Deterministic algorithms" 段的显示式 $f_O(T)/f_O(O^{\ast})\le 1/(\eta_u\eta_o)$ | OK |
| 10. 分支 $K\le n\le2K$，值 $K/((2K-n)+(n-K)\eta)$ | app:ceiling "The matching adversary for every $n>K$" 段：$a_0=\min\{K,n-K\}$，$f(S)/f(O)=K/(K+(\eta-1)a_0)$；J5 §4 同式 | OK（两分支与 $\min$ 形式的恒等 [VERIFIED-SYMBOLIC]，§6） |
| 11. $f(O^{\ast})$ 是最优值（$O^{\ast}$ 真的最优） | app:ceiling "The construction" 段末 "Since $\eta_u\ge1\ge1/\eta_o$, the $K$ largest coefficients are those of $O$ and $f_O(O^{\ast})=f_O(O)=c\eta_uK$" | OK |
| 12. 逆向：$S$ maximizing $\tilde f$ over all $K$-subsets | app:ceiling "The unified per-instance guarantee" 段 "let $S$ maximize $\tilde f$ over all sets of size **exactly** $K$（the band makes $\tilde f$ monotone, so completing a smaller predicted maximizer to size $K$ loses nothing）" | OK（但同一 subsection 的 "The matching upper bound by exhaustive search" 段用的是 "size **at most** $K$" 的 $\hat S$，两段口径不同，靠 band 单调性弥合，正文陈述取 $K$-subsets 与前者一致） |
| 13. 逆向：on every instance | 同上段：除模型假设外对实例无限制；J5 §2 "无需假设 S 与 O 恰好最小重叠" | OK |
| 14. 逆向：for every optimal $K$-set $O^{\ast}$ | 同上段 "let $O$ be an optimal $K$-set"（任取，故为全称）；式 (1) 对该 $O$ 成立 | OK(隐含)（未写 "for every"，但 $O$ 任取） |
| 15. 逐实例式 $K/(K+(\eta-1)a)$，$a=|O^{\ast}\setminus S|$ | app:ceiling Step 3 的显示式与 `eq:ceiling-slack`；J5 §2 式 (1)、§3 式 (7) | OK（式 (7) [VERIFIED-SYMBOLIC]，§6 与 results/J5_hardcore/J5_hardcore_oracles.py） |
| 16. 从逐实例式到 $C^{*}_{n,K}$ 的一步（$a\le\min\{K,n-K\}$） | app:ceiling Step 3 末 "$a\le\min\{K,n-K\}$ then gives $C^{*}_{n,K}$" | OK |
| 17. 需要**全部** $aK$ 次交换比较（不是 one-swap） | app:ceiling Step 1 "Summing over all $aK$ pairs $(b,s)$" 与 "The deletion side ranges over all $K$ elements of $S$, intersection included"；Scope 段重申 | OK |
| 18. 构造所需的 ground set 大小 | $n\ge2K$ 分支：app:ceiling "Deterministic algorithms" 段 "With $n\ge2K$ there is a $K$-set $O\subseteq N\setminus T$"；$K<n<2K$ 分支：只需 $n>K$（"The matching adversary" 段）；$n=K$：同段末句 | OK |
| 19. tie-breaking（argmax 不唯一时取哪个 $S$） | 无专门句子。Step 1 只用 "the predicted optimality of $S$"，对**任一** maximizer 都成立，故对抗性取 tie 也覆盖 | OK(隐含)。oracle C2 显式取"对抗 tie 下最差的 f̃-argmax K-集"，2,200 个实例 0 违反 [VERIFIED-EXHAUSTIVE] |
| 20. normalization $f(\emptyset)=\tilde f(\emptyset)=0$ | app:ceiling "The matching upper bound by exhaustive search" 段的望远镜从 $S_0=\emptyset$ 起，必须要 $f(\emptyset)=\tilde f(\emptyset)=0$；模型假设在 model.tex 第 9 至 14 行。构造侧 $f_O(\emptyset)=0$ 明写 | OK（app:ceiling 未重述该假设，属模型层继承） |
| 21. $f$ monotone submodular | Step 1 用 diminishing returns（$d_b(S)\le d_b(S\setminus\{s\})$）与 $Z-A\le D$；构造侧 "modular with positive coefficients, hence monotone and submodular" | OK |
| 22. $\tilde f$ 无结构假设（不必 submodular） | app:ceiling Step 2 末 "the algorithm need not have queried the union, and $\tilde f$ need not be submodular" | OK |
| 23. $\mathrm{OPT}>0$ | app:ceiling 未提。model.tex 第 15 至 16 行 "when $f(O^{\ast})=0$ every ratio statement is read as holding trivially"；J5 §1 "以 $f(O)>0$ 的实例定义近似比" | OK(隐含)（模型层有约定，路线甲正文无句子；构造侧 $f_O(O^{\ast})=c\eta_uK>0$ 自动满足） |
| 24. 拆分 $(\eta_u,\eta_o)$ 与乘积 $\eta$ 的关系 | Step 1 用 $\eta_u$ 与 $\eta$，Step 2 用 $\eta_u,\eta_o$ 两侧耦合，结论只含乘积；构造侧两个因子分别取到；model.tex 的 lem:scaling（第 44 至 56 行）给类意义的不变性 | OK |
| 25. 随机段：∀ randomized algorithm，∃ fixed pair | app:ceiling "Randomized algorithms" 段 + 末句 "$\min_O\le\mathbb E_O$ turns this into a statement about one instance" | OK |
| 26. 随机段：expectation over the algorithm's randomness | 同段。但计算把 $m=|T|$ 当定值写（"writing $m=|T|\le K$"），而随机算法的 $|T|$ 一般是随机变量；严格写法是先对固定随机串做确定性计算再对随机串求期望 | **GAP（部分）**：缺"条件于随机串"这一步的句子。结论不受影响（把 $m$ 换成 $\mathbb E[m]\le K$ 即可，且系数对 $m$ 单调），但路线甲没有写出来。标 [HAND-PROOF-UNREVIEWED] |
| 27. 随机段：又一次 error exactly $(\eta_u,\eta_o)$ | 沿用 "The construction" 段的同一构造 | OK |
| 28. 随机段：只是上界，不是精确随机值 | app:ceiling Scope 段的 $n=3$、$K=2$、$\eta=3$ 反例与 "the randomized minimax value remains open"；J5 §5 末段 | OK |
| 29. "fixed random string" 量词 | 只在 app:ceiling "Randomized algorithms" 段作为独立性说明出现（"independent of the random string"），**不在陈述里**；台账"禁止声称"条明确不得说随机算法逐种子满足确定性界 | OK（见 §3 的专门回答） |
| 30. 逆向方向的算法身份（存在算法，不是任意算法） | app:ceiling Scope 段首句 "The lower-bound quantifier is: there exists an algorithm (exhaustive search) that guarantees $C^{*}_{n,K}$ on every instance"；J5 §1 末段与 §5 | OK |
| 31. 穷举非多项式查询，不改 hardness 的适用范围 | app:ceiling Scope 段 "Exhaustive search evaluates $\binom nK$ predicted sets; nothing here produces a polynomial-query algorithm" | OK |

### 2.1 GAP 汇总

1. **$K\ge2$ 在路线甲无处使用**（表第 1 行）。陈述的定义域比证明需要的窄。按 addendum B.3 的目标形态
   （$K\ge1$、$n\ge2K$）这条会自动消失。保守处理：不动正文，只记录。
2. **"error exactly" 缺定义**（表第 7 行）。Definition~\ref{def:eta} 只有 "at most"。建议在 model.tex
   加一句约定（"exactly" = 满足带的最小可行因子对恰为 $(\eta_u,\eta_o)$），或在 app:ceiling 的
   "The construction" 段把"两个因子都被某个单元素增益取到"的口径写成定义句。本审计不改文件。
3. **随机段缺"条件于随机串"的一步**（表第 26 行）。$m=|T|$ 被当作定值。
4. 次要（不记入 GAP，只记录）：表第 12 行两段的 $\hat S$ 口径不同（"at most $K$" 与 "exactly $K$"）；
   表第 14、19、20、23 行是 OK(隐含)，即成立但无独立句子。

---

## 3. thm:ceiling 的专项回答："fixed random string" 量词在陈述里吗

**不在。** 正文第 464 至 473 行的随机段落写的是：对每个随机算法与每个 $n\ge2K$，**存在一个固定的**
$(f,\tilde f)$，使得**对算法随机性取期望**后 $\mathbb E[f(T)]\le((1-\frac Kn)\frac1\eta+\frac Kn)f(O^{\ast})$。
量词顺序是 ∀ 算法、∃ 固定实例、对随机串取期望。"fixed random string" 这个短语只出现在附录
app:ceiling 的 "Randomized algorithms" 段，作用是说明 $O$ 的均匀抽取与算法随机串独立。

这个取法是对的，理由两条：

- 若把 "fixed random string" 写进陈述，等于声称逐种子成立，那是假的：台账 T8 的"禁止声称（M4 追加）"
  条与 app:ceiling 的 Scope 段都给了反例（$n=3$、$K=2$、$\eta=3$，确定性值 $1/2$，而均匀随机二元集
  的期望至少 $\frac23 f(N)$）。
- 陈述里真正需要的是"先固定实例、再对随机性取期望"这一顺序，正文的 "there is a fixed pair ...
  the expectation over the algorithm's randomness" 已经把它写死。

配套的一条缺口在 §2.1 第 3 条：附录的平均化把 $|T|$ 当定值，没有写"先条件于随机串"。
状态 [HAND-PROOF-UNREVIEWED]。

（TASKS11 里 thm:linear-exact 的 $n\ge4K^5$ 收紧问题属于另一个条目，不在本文件范围。）

---

## 4. 与路线乙的关系（只作对照，不计入 E 表）

路线乙覆盖的是 $n\ge2K$ 的**达到方向**，来源两处：
`paper/sections/appendix_model_proofs.tex` 末尾 remark（第 51 行起）与 `HANDOFF_ADDENDUM_2026-09-18.md`
的 C 节。它用 Prop 2(iii) 把 marginal-gain band 换算成 value accuracy：取 $\epsilon=(\eta-1)/(\eta+1)$ 得
$\frac{1-\epsilon}{1+\epsilon}=1/\eta$ [VERIFIED-SYMBOLIC]（§6），再引 Horel 与 Singer 的观察。
对照表：

- E 表第 12 至 16 行（达到方向的量词）在路线乙里由 Prop 2(iii) 的 `eq:valueband`
  （$f(S)/\eta_u\le\tilde f(S)\le\eta_o f(S)$，对**所有** $S$）与"rescaling 不改变 $\tilde f$ 的 maximizer"两句承担。
- 路线乙**不覆盖**逐实例式 $K/(K+(\eta-1)a)$，也不覆盖 $K\le n<2K$：它只给全局的 $1/\eta$。
  故 E 表第 10、15 行仍只有路线甲一个出处。
- 路线乙的 Prop 2(iii) 在 `results/V11/statements.md` 的 T2 卡里带 "$\eta_o<2$" 的定义域限制，
  而 `appendix_model_proofs.tex` 的版本先乘 $c=2\eta_u/(\eta+1)$ 再落到 $\epsilon\in[0,1)$，没有该限制。
  两个版本不一致。这条属于 prop:valueacc 条目，这里只记录它会影响路线乙在大 $\eta_o$ 时是否可引用。
- 路线乙的对手侧（addendum §C 的三行）与路线甲 "The construction" 段是同一构造（权重 $c\eta_u$ 在 $O$ 上、
  $c/\eta_o$ 在别处），不是独立第二证明。

---

## 5. 与本审计相邻的两条记录（不改文件，仅记录）

- `paper/sections/appendix_proofs.tex` 的 Scope 段（第 1353 行起）用了 addendum A.6 与 CLAUDE.md 第 8 条
  同时禁用的那个副词去修饰 "The randomized value is ... different"。措辞问题，不影响数学。
- 正文第 464 至 473 行的随机段落与 $K\le n<2K$ 分支按 addendum B.3 应移入附录（A 项差异 D6、D7）。

---

## 6. 本文件自身算术的核对

脚本（临时目录，不入库）对以下 8 条做了 sympy 精确核对，residual 全为 0，状态 [VERIFIED-SYMBOLIC]：

1. $K/(K+(\eta-1)(n-K))=K/((2K-n)+(n-K)\eta)$；
2. $K/(K+(\eta-1)K)=1/\eta$；
3. 两分支在 $n=2K$ 处相接；
4. slack 恒等式 (7)：$(1+\frac{(\eta-1)a}{K})A-B=E+\gamma H+\frac\gamma KJ+\frac{\gamma\eta a}{K}T$；
5. 对手比值 $\frac{Kc/\eta_o}{a_0\eta_uc+(K-a_0)c/\eta_o}=\frac{K}{K+(\eta-1)a_0}$；
6. $n\ge2K$ 且 $T\cap O=\emptyset$ 时 $\frac{cK/\eta_o}{c\eta_uK}=1/\eta$；
7. Horel 与 Singer 的换算 $\frac{1-\epsilon}{1+\epsilon}=1/\eta$，$\epsilon=(\eta-1)/(\eta+1)$；
8. 随机常数 $\frac{m(1-K/n)/\eta_o+\eta_umK/n}{\eta_uK}$ 在 $m=K$ 处等于 $(1-\frac Kn)\frac1\eta+\frac Kn$。

更强的数值与穷举证据不由本文件产生，见 `results/V11/oracle/ceiling.md`（9 个 check 全 PASS，
3,544 个随机实例 0 违反）与 `results/J5_hardcore/J5_hardcore_oracles.py`。
路线甲的一般装配（交换求和、望远镜、minimax 量词）仍是 [HAND-PROOF-UNREVIEWED，来源 J5 套 A]。

---

## 7. 读过的文件

- `results/V11/statements.md`（第 72 至 120 行，T8 段）
- `results/V11/inputs/statement_ceiling.md`
- `results/V11/inputs/definition1.md`、`results/V11/inputs/assumptions.md`
- `THEOREM_LEDGER.md`（第 162 至 204 行，卡 `## T8`）
- `paper/sections/results.tex`（第 439 至 473 行；另见第 554、620、854 行的引用点）
- `paper/sections/model.tex`（第 1 至 120 行）
- `paper/sections/appendix_proofs.tex`（第 1211 至 1372 行，`app:ceiling`）
- `paper/sections/appendix_model_proofs.tex`（全文，末尾 remark 为路线乙）
- `results/J5_hardcore/J5_ceiling_proof.md`（全文）
- `HANDOFF_2026-09-18.md`（第 70 行）、`HANDOFF_ADDENDUM_2026-09-18.md`（A、B、C 节）
- `results/V11/oracle/ceiling.md`（对照用）
- `results/V11/audit/nobound.md`（格式对照）

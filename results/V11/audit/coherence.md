# 量词审计（criteria A 与 E）：lem:coherence / 台账 T5 与其 sharp form（TASKS11 Q5b）

本文件只做两件事：A 项逐量词比对正文环境与台账卡，E 项建立量词审计表并把每个量词落到路线一证明的具体位置。
不修改任何已有文件，不运行 git。本文件自带的算术用 fractions.Fraction 与 sympy，浮点只出现在打印里。
状态标签按 CLAUDE.md：[VERIFIED-SYMBOLIC] [VERIFIED-LP] [VERIFIED-EXHAUSTIVE] [HAND-PROOF-UNREVIEWED] [CONJECTURE] [FAILED]。

路线一材料（本审计逐行读过的部分）：

- `paper/sections/appendix_proofs.tex` 的 subsection `app:coherence`（第 524 至 579 行）。三个 paragraph 标签依次为
  The exchange identity（第 532 行）、Part (i)（第 547 行）、Part (ii)（第 560 行）；第 529 至 530 行是假设行，
  第 576 至 579 行是收尾句。下文简称 app:coherence 的"交换恒等式段"、"(i) 段"、"(ii) 段"。
- 正文 `paper/sections/results.tex` 的 subsection `sec:coherence`（第 136 至 175 行）：lemma 环境在第 138 至 147 行，
  sharp form 的散文段在第 153 至 166 行。
- sharp form 的下游使用与证书：`appendix_proofs.tex` 的 `app:validity`（`lem:app-mono` 第 2239 至 2252 行、
  `lem:app-cons` 第 2253 至 2290 行、`rem:app-rulers` 第 2315 至 2328 行、`rem:app-census` 第 2330 至 2338 行）
  与 `app:rigidity` 的 Step 7（第 1138 至 1156 行）。
- oracle：`results/H_J3_gate_check.py`（item 1 的 sharp form 等价性）与 `results/J2_core_oracles.py`
  （`symbolic_core` 的 R6 pred / R6 cons 三项非负 slack 恒等式，第 42 至 46 行）。

读过的文件全表见 §8。

---

## 1. Criterion A：正文陈述与台账陈述的逐量词比对

### 1.1 两段原文

正文（`results.tex` 第 138 至 147 行，environment `lemma`，label `lem:coherence`；与
`results/V11/statements.md` 第 159 至 170 行、`results/V11/inputs/statement_coherence.md` 第 6 至 15 行三处逐字一致。
本项没有 convention B 改写版，正文与输入包给的是同一段 LaTeX）：

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

台账（`THEOREM_LEDGER.md` 卡 `## T5 lem:coherence`，陈述字段）：

> 陈述：f 单调，S⊆N，e,e'∉S，d̃_e(S) ≥ d̃_{e'}(S)。则 (i) d_e(S∪{e'}) ≥ d_{e'}(S∪{e})/η；(ii) (1−1/η) d_{e'}(S∪{e}) ≥ d_{e'}(S)−d_e(S)。

台账卡的其余字段（状态、sharp form 附注、禁止声称）不属于陈述字段，不计入 A 比对；sharp form 单独在 §1.4 比，
禁止声称字段的一处状态名问题记在 §5 的 N3。

### 1.2 逐项对照

| 量词 / 形容词 | 正文 | 台账 | 判定 |
|---|---|---|---|
| f monotone | 有，"Let $f$ be monotone" | 有，"f 单调" | 一致 |
| f submodular | 无 | 无 | 一致（共同省略；sharp form 第二式需要它，见 §1.4 与 E 表第 2 行） |
| f 的 normalization f(∅)=0 | 无 | 无 | 一致（共同省略，本引理不需要，见 E 表第 3 行） |
| S 的全称 "for every $S\subseteq N$" | 有，"$S\subseteq N$"，无 \|S\| 限制 | 有，"S⊆N"，无 \|S\| 限制 | 一致 |
| e, e' 的位置限定 e,e' ∉ S | 有 | 有 | 一致 |
| e ≠ e' | 无 | 无 | 一致（共同省略；路线一明写了它，见 GAP-2） |
| 假设 d̃_e(S) ≥ d̃_{e'}(S)（弱不等号，允许打平） | 有 | 有 | 一致 |
| 结论 (i) 的式子与方向 | 有，$d_e(S\cup\{e'\})\ge\tfrac1\eta d_{e'}(S\cup\{e\})$ | 有，d_e(S∪{e'}) ≥ d_{e'}(S∪{e})/η | 一致（写法 1/η 前置与后除同义） |
| 结论 (ii) 的式子与方向 | 有 | 有 | 一致 |
| η 的定义域（η ≥ 1）与 (η_u,η_o) 的拆分 | 未写（继承 `def:eta`，`model.tex` 第 23 至 32 行） | 未写 | 一致（共同省略，见 E 表第 15、16 行） |
| 只用全局 η，不用 η^sel / η^tr | 陈述里只出现 η | 陈述里只出现 η | 一致（限制写在两边各自的非陈述字段） |
| K 的定义域 / K ≥ 2 | 无（本引理不出现 K） | 无 | 一致 |
| n、ground set 大小 | 无 | 无 | 一致（共同省略，见 GAP-3） |
| OPT > 0 | 无（本引理不是比值陈述） | 无 | 一致 |
| deterministic / randomized | 无 | 无 | 一致（本陈述不量化算法类） |
| fixed random string / expectation over what | 无 | 无 | 一致（本陈述无随机条款） |
| arbitrary query access、至多 nK 次查询、\|S\| ≤ K | 无 | 无 | 一致（本陈述无查询量词） |
| adversarial ties、固定 K 步 | 无 | 无 | 一致（本引理不依赖 run 的 tie 规则，见 E 表第 11 行） |
| error "exactly" 还是 "at most" | 不出现 (η_u,η_o)，只用 η | 同 | 一致（读法由 `def:eta` 的 "error at most" 决定） |

### 1.3 A_diffs

**空**。正文 lemma 环境与台账陈述字段逐量词重合，没有一条量词、定义域限制或形容词只出现在一边。

**A_match = true**。

### 1.4 sharp form 的附加比对（Q5b 指定的对象）

正文（`results.tex` 第 153 至 166 行，散文段，不是独立环境）：

> Part (ii) has a sharp form that is the starting point of the proof of the next theorem. Let $e$ be the element the
> predictor prefers at $S$ and $e'$ a competing candidate, and write $d=d_e(S)$ ..., $g=d_{e'}(S)$ ... and
> $h=d_{e'}(S\cup\{e\})$ ...; then (ii), combined with submodularity of $f$, reads
> $d-\frac g\eta\ge(1-\frac1\eta)(g-h)\ge0$. ... In particular, for $\eta>1$ a step with $d=g/\eta$ forces $h=g$.

台账（T5 卡的 sharp form 项）：

> Sharp form（H-J3 采纳）：d − g/η ≥ (1−1/η)(g−h) ≥ 0，其中 d=d_e(S)、g=d_{e'}(S)、h=d_{e'}(S∪{e})；
> 第一个不等号是 (ii) 的等价改写 [VERIFIED-SYMBOLIC，results/H_J3_gate_check.py]，第二个另用 f 的 submodularity。
> 推论：η>1 且 d=g/η 时必有 h=g。作为 lemma 的 sharp form 陈述，不另立新定理。

| 项 | 正文 | 台账 | 判定 |
|---|---|---|---|
| 记号 d=d_e(S)、g=d_{e'}(S)、h=d_{e'}(S∪{e}) | 有，三个都有 | 有，三个都有 | 一致 |
| 链 d − g/η ≥ (1−1/η)(g−h) ≥ 0 | 有 | 有 | 一致 |
| 第一个不等号 = (ii) 的等价改写 | 有（"(ii) ... reads"） | 有 | 一致 |
| 第二个不等号需要 f 的 submodularity | 有（"combined with submodularity of $f$"） | 有 | 一致 |
| 第二个不等号还需要 η ≥ 1 | 排版文本里没有，只在第 168 至 172 行的注释里 | 陈述里没有 | 一致（共同省略，由 `def:eta` 继承，见 E 表第 16 行） |
| 推论 η>1 且 d=g/η ⟹ h=g | 有 | 有 | 一致 |
| 假设的表述方式 | 散文："$e$ 是 predictor 在 $S$ 处偏好的元素，$e'$ 是竞争候选" | 继承陈述字段的 d̃_e(S) ≥ d̃_{e'}(S) | 同一关系的两种写法，记为 N1，不计差异 |
| 不另立新定理 | 正文确实放在 subsection 内，无 theorem 环境 | 明写"不另立新定理" | 一致（台账是指令，正文是执行） |

sharp form 一侧同样没有只出现在一边的量词，所以 A_match 不因它改变。

---

## 2. Criterion E：量词审计表

表内"处理位置"一律给 file 加段落标签或可检索的原文片段。状态取值：覆盖（路线一有明写的一句）、隐式（路线一用到
但没有一句建立或点名）、不需要（本证明不用这个条件）、不适用（陈述里没有这个量词）、GAP。

| 量词 / 形容词 | 处理位置（file + 段落） | 状态 |
|---|---|---|
| 1. f monotone | `appendix_proofs.tex` app:coherence 全段（第 524 至 579 行）不出现 monotone、monotonicity 或 $d\ge0$ 的任何一次使用；`model.tex` 第 9 至 10 行的全局假设与 `def:eta`（第 23 至 32 行）"all predicted gains are nonnegative" | **GAP-1**（陈述里的假设，路线一未用） |
| 2. f submodular（陈述无，sharp form 第二式需要） | `results.tex` 第 155 至 160 行 "combined with submodularity of $f$"；附录里对应的一行是 `lem:app-mono`（第 2239 至 2252 行）"by submodularity in its diminishing-returns form" | 覆盖（但不在 app:coherence 内，见 GAP-4） |
| 3. f 的 normalization f(∅)=0 | 本证明不使用（全部量都是差分）；`model.tex` 第 9 至 10 行 | 不需要 |
| 4. f̃ 是定义在全部子集上的集合函数（交换恒等式的唯一依据） | app:coherence 交换恒等式段第 540 行 "This uses nothing but the definition of a set function." | 覆盖 |
| 5. f̃(∅)=0、f̃ 的结构假设（submodular 与否） | 本证明不使用；`model.tex` 第 12 行；`rem:app-census` 第 2336 至 2338 行 "No family uses submodularity of $\tilde f$" | 不需要 |
| 6. 全称 "for every $S\subseteq N$"，无 \|S\| ≤ K−1 限制 | app:coherence 第 529 行 "Let $S\subseteq N$"；应用处才把 S 取成 run state（`lem:app-cons` 第 2253 至 2290 行的 S^t） | 覆盖 |
| 7. e, e' ∉ S | app:coherence 第 529 行 "$e,e'\notin S$" | 覆盖 |
| 8. e ≠ e' | app:coherence 第 529 行明写 "with $e\ne e'$"；`lem:app-cons` 第 2287 至 2289 行记录 case (c) 因此不调用本引理。正文与台账陈述都没有这个限定 | **GAP-2**（路线一有，陈述侧缺） |
| 9. ground set 需满足 \|N \ S\| ≥ 2（否则陈述空洞） | 无一处说明；`model.tex` 第 15 行只有 1 ≤ K ≤ n | **GAP-3**（空洞性，轻） |
| 10. 假设 d̃_e(S) ≥ d̃_{e'}(S)，弱不等号 | app:coherence 第 529 至 530 行 "assume $\tilde d_{e}(S)\ge\tilde d_{e'}(S)$"；用在 \eqref{eq:coh-pred} 的减法（第 540 至 545 行） | 覆盖 |
| 11. tie-breaking（adversarial ties） | 本引理不需要：假设是弱不等号，打平也成立。应用处由 greedy choice 提供，`lem:app-cons` 第 2274 至 2276 行 "because $o_i$ is eligible at step $t$ and $e_t$ was chosen"；tie 规则本身在 `model.tex` 第 70 至 71 行 | 不需要 |
| 12. band 在离轨状态 S∪{e'} 上成立（全局 η 的关键） | app:coherence (i) 段第 557 行 "the third by the upper band at $(S\cup\{e'\},e)$"；`rem:app-rulers` 第 2315 至 2328 行点名这是 η^sel / η^tr 不够用的原因 | 覆盖 |
| 13. band 在状态 S∪{e}（run 的下一个 state）上成立 | app:coherence (i) 段第 556 行 "the first inequality by the lower band at $(S\cup\{e\},e')$" | 覆盖 |
| 14. 拆分 (η_u, η_o) 与乘积 η 的关系 | app:coherence (i) 段的三步链 $\eta_u\cdot\eta_o=\eta$（第 551 至 554 行）；class 层面的缩放不变在 `model.tex` `lem:scaling`（第 44 至 54 行） | 覆盖 |
| 15. η_u, η_o > 0（把不等号两边乘 η_u 所需） | 无一句点名；`def:eta`（`model.tex` 第 24 行）写 η_u,η_o ≥ 1，convention B（`results/V11/inputs/definition1.md`）放宽到 >0，两种约定下链条都成立 | 隐式 |
| 16. η ≥ 1（保 1−1/η ≥ 0） | app:coherence (ii) 段第 573 至 574 行 "Only $\eta\ge1$ is used beyond the bands, and only to keep the factor $1-\tfrac1\eta$ nonnegative when the inequality is applied later." | 覆盖 |
| 17. 结论 (i) | app:coherence (i) 段第 547 至 559 行 | 覆盖 |
| 18. 结论 (ii) | app:coherence (ii) 段第 560 至 574 行 | 覆盖 |
| 19. sharp form 第一式 d − g/η ≥ (1−1/η)(g−h) | `results.tex` 第 153 至 166 行；oracle `results/H_J3_gate_check.py` item 1（本次复跑 PASS）；`app:rigidity` Step 7 第 1143 至 1149 行按此形改写两条约束。app:coherence 内没有这一式 | 覆盖（[VERIFIED-SYMBOLIC]） |
| 20. sharp form 第二式 (1−1/η)(g−h) ≥ 0 | `results.tex` 第 155 至 160 行的 "combined with submodularity of $f$"；附录侧由 `lem:app-mono`（第 2239 至 2252 行）与 η ≥ 1 拼出，`app:rigidity` 第 1146 至 1148 行写成 "$g-h\ge0$" | **GAP-4**（无一处把两个部件合起来证 sharp form） |
| 21. sharp form 的记号绑到一个 greedy step（d 是选中的真增益，g、h 是竞争者的前后增益） | `results.tex` 第 155 至 160 行；`app:rigidity` Step 7 第 1142 至 1143 行 "Write $d=d_{K-1}$, $g=g_{K-1,i}$ and $h=g_{K,i}$" | 覆盖 |
| 22. 推论：η>1 且 d=g/η ⟹ h=g | `results.tex` 第 165 至 166 行；`app:rigidity` Step 7 第 1151 至 1152 行 "since $\eta>1$ the two displays leave $h=g$" | 覆盖 |
| 23. (ii) 的三项非负 slack 分解（证书形式） | `lem:app-cons` 第 2265 至 2276 行的恒等式与三个 brace；oracle `results/J2_core_oracles.py` 第 43 至 46 行 'R6 cons nonnegative-slack identity' | 覆盖（[VERIFIED-SYMBOLIC]） |
| 24. (i) 的三项非负 slack 分解 | `app:rigidity` 第 1176 至 1184 行（pred 的 slack 分解，三个 brace）；oracle `results/J2_core_oracles.py` 第 42 至 43 行 'R6 pred nonnegative-slack identity' | 覆盖（[VERIFIED-SYMBOLIC]） |
| 25. 全局 η 不可换成 η^sel 或 η^tr | `rem:app-rulers` 第 2319 至 2325 行；`results.tex` 第 173 至 175 行的 Scope 注释 | 覆盖 |
| 26. OPT > 0 / f(O\*) > 0 | 本引理不是比值陈述，不涉及 | 不适用 |
| 27. K ≥ 2、K 的定义域、固定 K 步、早停变体 | 本引理不出现 K；应用处 t ≤ K−1（`lem:app-cons` 的 for every t,i） | 不适用 |
| 28. \|S\| ≤ K、至多 nK 次查询、arbitrary query access | 陈述无查询量词，证明不使用 | 不适用 |
| 29. deterministic / randomized、fixed random string、expectation over what | 陈述无随机条款，无期望，无算法类量词 | 不适用 |
| 30. error "exactly" 还是 "at most" | `def:eta`（`model.tex` 第 23 至 25 行）措辞是 "error at most $(\eta_u,\eta_o)$"；app:coherence 全程按 at most 使用（两侧都是不等号，不假设取等） | 覆盖 |

合计 30 行：覆盖 17 行，隐式 1 行，不需要 3 行，不适用 5 行，GAP 4 行。

### 2.1 模板附带问题（本项不适用，逐条记录理由）

- "thm:ceiling 的 fixed random string 量词是否在陈述里"：本项是 lem:coherence，陈述无随机段落，问题不适用。
  该问题属另一项，已在 `results/V11/audit/ceiling.md` 处理，本文件不重复也不复制其结论。
- "thm:linear-exact 的 n ≥ 4K^5 能否紧到约 K^3(K−1)^2/2 + K^2"：`app:greedybudget` 从 `appendix_proofs.tex`
  第 1703 行起，全段不引用 `lem:coherence`（`lem:coherence` 的全部引用位置是 `results.tex` 第 138、240 行与
  `appendix_proofs.tex` 第 524、586、1143、2277、2287、2321、2335 行，无一条落在 app:greedybudget 区间内）。
  本项与那条 counting chain 没有引用关系，不作判断，以免与负责该项的审计重复或冲突。

---

## 3. GAP 清单

四条，按保守口径列出。判定标准：路线一 app:coherence 里没有一句建立、点名或使用该条件，即使它在别处可补。
四条都不动摇 (i)(ii) 的真值（§4 的 oracle 结果支持这一点），三条是"补一句话"的量级，GAP-4 是"补一段"的量级。

- **GAP-1（中）f monotone 这条假设在路线一未被使用**。app:coherence 的三段（交换恒等式、(i)、(ii)）没有一处调用
  单调性：交换恒等式只用集合函数的定义，(i) 只把 band 串起来，(ii) 只用 f 的交换恒等式加 (i)。按 CLAUDE.md 的空洞性检验，
  把 "monotone" 去掉后两条结论的推导逐字不变。反向关系是：`def:eta` 在 η > 1 时强制每个 d_e(S) ≥ 0（§4 第 3 项），
  也就是说 Definition 1 本身蕴含 f 单调，陈述里的 "Let $f$ be monotone" 是全局模型假设的重述，不是本引理额外要的东西。
  保守处理：不建议删掉正文里的 "monotone"（它让 sharp form 里 g、h ≥ 0 的读法自然，也与全文假设一致），
  建议在 app:coherence 加一句说明它用在哪里或不用在哪里。状态 [HAND-PROOF-UNREVIEWED]，不影响真值。
- **GAP-2（中）e ≠ e' 在陈述侧缺失**。app:coherence 第 529 行的假设行明写 "with $e\ne e'$"，正文 lemma 环境与台账
  陈述字段都只写 "e,e'∉S"。e = e' 时 (i) 的左端 $d_e(S\cup\{e'\})$ 是把 e 加进已含 e 的集合，按记号表不成立，
  所以这是陈述读不通而不是陈述为假。`lem:app-cons` 第 2287 至 2289 行已经把这条限定当作既有条件使用
  （"Lemma~\ref{lem:coherence}, which requires $e\ne e'$, is not invoked in this case, which is what closes the gap
  this subsection exists to close"），可见下游依赖它。建议：正文与台账的陈述都补 $e\ne e'$。这是四条里唯一
  下游已经明确依赖、而陈述没写的。状态 [HAND-PROOF-UNREVIEWED]。
- **GAP-3（轻）ground set 的大小要求 \|N \ S\| ≥ 2**。陈述对 S 全称，但只有当 S 之外至少有两个不同元素时才有可谈的
  (e,e')；`model.tex` 第 15 行只给 1 ≤ K ≤ n。这是空洞性而不是错误：\|N \ S\| ≤ 1 时假设的前件无法满足，陈述空真。
  建议不改正文，只在审计里记一句。状态记录项。
- **GAP-4（中）sharp form 在附录里没有独立的证明段**。sharp form 只在正文 `results.tex` 第 153 至 166 行以散文出现，
  理由分散在三处：第一个不等号的等价性由 `results/H_J3_gate_check.py` item 1 的 sympy 担保（正文第 168 至 172 行的
  注释指向它，但注释不排版）；第二个不等号的两个部件是 `lem:app-mono`（submodularity）与 η ≥ 1，它们在
  `app:validity` 里各自为 reduced LP 的约束服务，不是为 sharp form 写的；`app:rigidity` Step 7 第 1143 至 1149 行
  把两条约束"rearranged as the sharp form"来用，属于使用而不是建立。app:coherence 全段没有 sharp form 的任何一行。
  后果：读者在附录里找不到 sharp form 的证明。建议在 app:coherence 末尾加三行（(ii) 的移项 加 g ≥ h 加 η ≥ 1），
  不新增编号对象，与台账"不另立新定理"一致。状态 [HAND-PROOF-UNREVIEWED]。

---

## 4. 本文件自身算术的核对（exact arithmetic）

用 sympy 与 fractions.Fraction，浮点只在打印。脚本放在会话 scratchpad（不在仓库里新增脚本文件），内容如下，可直接重跑：

```python
from fractions import Fraction as F
from itertools import product
import sympy as sp

# 1. sharp form 第一式与 (ii) 的等价
d, g, h, eta = sp.symbols('d g h eta', positive=True)
sharp = (d - g/eta) - (1 - 1/eta)*(g - h)
coh2  = (1 - 1/eta)*h - (g - d)
sp.simplify(sharp - coh2)                      # -> 0

# 2. (i) 与 (ii) 的三项非负 slack 分解（(ii) 的一式即 J2 的 R6 cons）
eu, eo = sp.symbols('eta_u eta_o', positive=True)
X, Y, xt, yt = sp.symbols('X Y xt yt', real=True)      # X=d_e(S u e'), Y=d_e'(S u e)
lhs_i = X - Y/(eu*eo)
rhs_i = (eo*X - xt)/eo + (xt - yt)/eo + (eu*yt - Y)/(eu*eo)
sp.simplify(lhs_i - rhs_i)                     # -> 0
dd, gg, hh, P, Q, R = sp.symbols('dd gg hh P Q R', real=True)
lhs_ii = (1 - 1/(eu*eo))*hh - gg + dd
rhs_ii = (eo*(dd+hh-gg) - (P+R-Q))/eo + (P-Q)/eo + (eu*R-hh)/(eu*eo)
sp.simplify(lhs_ii - rhs_ii)                   # -> 0

# 3. band 的可行性反过来强制 d >= 0
dv = sp.symbols('dv', real=True)
sp.factor(sp.simplify(eo*dv - dv/eu))          # -> dv*(eta_o*eta_u - 1)/eta_u

# 4. 四集合表的有理穷举（gains 取 0,1/2,...,3；五组 (eta_u, eta_o)）
# 5. 去掉 submodularity 后 sharp form 第二式失效的有理实例
# 6. K=3, eta=3/2 的取等示例
```

结果：

- sharp form 第一式与 (ii) 的移项恒等，残差 0。与 `results/H_J3_gate_check.py` item 1 一致；本次复跑该脚本，
  9 项全部 PASS（含 2,480 次 facet LP，最大坐标偏差 3.94e-15），退出码 0。[VERIFIED-SYMBOLIC]
- (i) 的 slack 分解 $X-\frac{Y}{\eta_u\eta_o}=\frac{\eta_oX-\tilde x}{\eta_o}+\frac{\tilde x-\tilde y}{\eta_o}
  +\frac{\eta_u\tilde y-Y}{\eta_u\eta_o}$ 与 (ii) 的六符号分解都恒等于零。三项的非负性依次来自
  $(S\cup\{e'\},e)$ 的上带、假设 d̃_e(S) ≥ d̃_{e'}(S)（经预测侧交换恒等式搬运）、$(S\cup\{e\},e')$ 的下带。
  这与 `J2_core_oracles.py` 的 R6 pred / R6 cons 两条恒等式是同一件事，本文件独立重推一次。[VERIFIED-SYMBOLIC]
- band 可行性：$\eta_od-\frac{d}{\eta_u}=\frac{d(\eta_u\eta_o-1)}{\eta_u}$，所以 η > 1 时 Definition 1 在
  $(S,e)$ 处可满足当且仅当 $d_e(S)\ge0$。即 Definition 1 对全部 (S,e) 成立就蕴含 f 单调。这是 GAP-1 的依据。[VERIFIED-SYMBOLIC]
- 有理穷举：四个集合 S、S∪{e}、S∪{e'}、S∪{e,e'} 上的真增益与预测增益取 0,1/2,…,3 的格点，
  (η_u,η_o) 取 (1,3/2)、(3/2,1)、(5/4,6/5)、(1,1)、(2,2)，并施加 band、假设与两侧的交换恒等式，
  共 9,484 个可行表，(i) 与 (ii) 各 0 次违反。[VERIFIED-EXHAUSTIVE（格点）]
- submodularity 的作用被隔离出来：取 d=1、g=1/2、h=1（f 单调但不 submodular，因为 h > g），
  band 取 (η_u,η_o)=(3/2,1) 即 η=3/2。此时 (ii) 成立（左端 1/3 ≥ 右端 −1/2），第一式也成立（d−g/η=2/3），
  但 sharp form 的尾项 (1−1/η)(g−h)=−1/6 < 0，链条的第二个不等号失效。
  所以 (i)(ii) 不需要 submodularity，sharp form 的第二式需要。[VERIFIED-EXHAUSTIVE（单实例，有理）]
- running example（K=3，η=3/2）：η>1 且 d=g/η 的取等情形。取 g=1，则 d=2/3，(ii) 给
  (1−1/η)h ≥ g−d=1/3，即 h ≥ 1；submodularity 给 h ≤ g=1；两边夹出 h=g=1，正是正文第 165 至 166 行的推论。[VERIFIED-SYMBOLIC]

这些核对覆盖 (i)(ii) 的证书形式、sharp form 两个不等号各自的依赖、以及 GAP-1 的依据。
它们不覆盖 app:coherence 的散文推理顺序本身，后者仍是 [HAND-PROOF-UNREVIEWED]，与附录第 576 行的收尾句
"No script checks the computations of this proof." 一致。

---

## 5. 记录项（不计入 A_diffs，也不计入 GAP）

- **N1 措辞**：正文 sharp form 段把假设写成"$e$ 是 predictor 在 $S$ 处偏好的元素、$e'$ 是竞争候选"，台账沿用
  陈述字段的 d̃_e(S) ≥ d̃_{e'}(S)。定冠词 "the element the predictor prefers" 在应用处就是 greedy 的 argmax，
  argmax 蕴含对每个竞争者的逐对不等式，所以正文的读法是引理的特例，不把引理改窄也不与之冲突。不计为差异。
- **N2 台账状态字段**：T5 卡写"两行证明（f̃(S∪{e,e'}) 两种展开）"。路线一实际是三段：f̃ 的交换恒等式、(i) 的三步 band 链、
  f 的交换恒等式加 (i)。两行是压缩说法，不影响陈述。
- **N3 台账禁止声称字段的状态名**：T5 卡写"对 η^sel 或 η^tr 成立（它用到离轨状态 S∪{e} 的误差带，必须全局 η）"。
  禁令本身与路线一一致，但理由里的状态名应是 **S∪{e'}**：app:coherence (i) 段第 557 行的第三步上带就在
  $(S\cup\{e'\},e)$，而 S∪{e} 在 run 里正是下一个 run state（η^tr 覆盖它）。`rem:app-rulers` 第 2321 至 2322 行
  写的也是 "the band at the state $S^{t}\cup\{o_i\}$, which is off the greedy trajectory"，即 S∪{e'} 一侧。
  建议只改台账卡的这一处状态名，不改禁令。`results/V11/oracle/coherence.md` 的 D4a 节独立得到同一处更正。
- **N4 正文状态注释与排版文本**：sharp form 需要的 η ≥ 1 只写在 `results.tex` 第 168 至 172 行的注释里
  （"the second is g >= h, which is submodularity of f, together with eta >= 1"），注释不进 PDF。
  按 HANDOFF ADDENDUM §A 第 8 条"正文不出现状态标签、仓库行号、label 名"，不建议把注释内容原样搬进正文；
  GAP-4 的三行附录补丁可以同时把 η ≥ 1 说清楚。
- **N5 convention B 的影响**：`results/V11/inputs/definition1.md` 记录正文 `def:eta` 把两个因子都下取整到 1，
  convention B 放宽到 η_u,η_o > 0。app:coherence 的链条只用到 η_u, η_o > 0 与 band 本身，两种约定下逐字成立，
  本项不因 convention 改写产生第二个版本的陈述。

---

## 6. 结论

- **A_match = true，A_diffs 为空**。`results.tex` 第 138 至 147 行的 lemma 环境与 `THEOREM_LEDGER.md` T5 卡的陈述字段
  逐量词重合；Q5b 指定的 sharp form 一侧（正文第 153 至 166 行对台账 sharp form 项）同样没有只出现在一边的量词。
  两边共同省略的四项（f submodular、f(∅)=0、e ≠ e'、η ≥ 1）在 E 表与 GAP 清单里各自有行，不算 A 差异。
- **Criterion E**：30 行。覆盖 17 行，隐式 1 行（η_u,η_o > 0），不需要 3 行，不适用 5 行，GAP 4 行
  （GAP-1 f monotone 未被路线一使用；GAP-2 e ≠ e' 陈述侧缺失；GAP-3 \|N \ S\| ≥ 2 的空洞性；GAP-4 sharp form
  在附录里没有独立证明段）。四条都不影响 (i)(ii) 的真值，GAP-2 是唯一下游已明确依赖而陈述没写的一条。
- 引理整体的状态维持 [HAND-PROOF-UNREVIEWED]（app:coherence 的散文推理无脚本）；本文件把 sharp form 第一式的等价性、
  (i)(ii) 的三项非负 slack 分解、band 蕴含单调性、以及 submodularity 在 sharp form 第二式中的必要性升为
  [VERIFIED-SYMBOLIC] / [VERIFIED-EXHAUSTIVE（格点）]。

---

## 7. 状态标签小结

| 对象 | 标签 |
|---|---|
| sharp form 第一式 ≡ (ii) 的移项（自推 加 复跑 `H_J3_gate_check.py` item 1，9/9 PASS） | [VERIFIED-SYMBOLIC] |
| (i) 的三项非负 slack 分解（自推；对应 `J2_core_oracles.py` 的 R6 pred） | [VERIFIED-SYMBOLIC] |
| (ii) 的三项非负 slack 分解（自推；对应 `J2_core_oracles.py` 的 R6 cons 与 `lem:app-cons`） | [VERIFIED-SYMBOLIC] |
| Definition 1 在 η > 1 时强制 d_e(S) ≥ 0（GAP-1 的依据） | [VERIFIED-SYMBOLIC] |
| (i)(ii) 在四集合有理格点上无违反（9,484 个可行表，0 violation） | [VERIFIED-EXHAUSTIVE（格点）] |
| sharp form 第二式在去掉 submodularity 后失效（d=1、g=1/2、h=1、η=3/2，尾项 −1/6） | [VERIFIED-EXHAUSTIVE（单实例，有理）] |
| app:coherence 的三段散文推理（交换恒等式、(i) 的 band 链、(ii) 的代入） | [HAND-PROOF-UNREVIEWED] |
| sharp form 作为一个整体在附录里的证明 | [HAND-PROOF-UNREVIEWED]（GAP-4：附录里没有这一段） |
| 引理整体 | [HAND-PROOF-UNREVIEWED] |

---

## 8. 读过的文件

路线一与陈述侧：

- `paper/sections/results.tex`（第 125 至 250 行：sec:coherence 的 lemma 环境、sharp form 段、两处状态注释，
  以及第 240 至 243 行 sharp form 作为 thm:exact 证明起点的那句）
- `paper/sections/appendix_proofs.tex`（第 520 至 600 行 app:coherence 与其后 app:exact 的 roadmap；
  第 1130 至 1200 行 app:rigidity Step 7 与 pred slack 分解；第 2225 至 2348 行 app:validity 的
  lem:app-mono、lem:app-cons、rem:app-rulers、rem:app-census 与收尾；第 1703 行 app:greedybudget 的起始标签）
- `paper/sections/model.tex`（第 9 至 16 行全局假设、第 23 至 32 行 def:eta、第 33 至 54 行 lem:scaling、
  第 70 至 116 行 predictive greedy 与 def:etasel、第 117 至 126 行 η^tr）
- `THEOREM_LEDGER.md`（T5 卡全文；相邻的 T3、T4、T6、T6b 卡用于确认 sharp form 的下游去向）
- `results/V11/statements.md`（T5 段）、`results/V11/inputs/statement_coherence.md`、
  `results/V11/inputs/definition1.md`、`results/V11/inputs/assumptions.md`、`results/V11/inputs/notation.md`

oracle 与参照：

- `results/H_J3_gate_check.py`（读 header 与 item 1 至 4 的实现；本次完整复跑，9/9 PASS，退出码 0）
- `results/J2_core_oracles.py`（读 `symbolic_core` 的 R6 pred / R6 cons 两条恒等式与 slack 最小化的说明）
- `results/V11/audit/guarantee.md`（只为对齐本系列审计文件的格式与口径）
- `results/V11/oracle/coherence.md`（只为 §5 N3 的交叉印证与避免重复，不引用其结论作为本文件的依据）
- `results/V11/notes.md`、`CLAUDE.md`、`HANDOFF_2026-09-18.md`、`HANDOFF_ADDENDUM_2026-09-18.md`

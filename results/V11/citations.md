# V11 引用核验 (citations verification)

生成日期: 2026-09-18
方法: 实际 fetch 源 PDF / 落地页, 本地抽取文本后逐句核对。凡未能从实际 fetch 到的来源中定位者, 一律标 NOT FOUND, 不猜测编号。

---

## 事实 1 (Fact 1): Goundan & Schulz, greedy + alpha-approximate incremental oracle 的定理编号

- **待核事实**: 论文引用写的是 "Theorem 1" —— 即在 alpha-approximate incremental oracle 下, greedy 在 uniform matroid 上给出 1 - (1 - 1/(alpha*k))^k >= 1 - e^{-1/alpha} 型保证的那条编号定理。
- **来源 URL (已实际 fetch)**:
  - https://optimization-online.org/wp-content/uploads/2007/08/1740.pdf (全文 PDF, 25 页, 本地抽取文本核对)
  - https://optimization-online.org/2007/08/1740/ (落地页, 核对题名与年份)
- **原文引用 (verbatim, 第 8 页, Section 3.1 "Greedy Algorithm for fS|FU" 之后)**:

  > "Theorem 1. If zg is the value of the Greedy Algorithm for fS|FU , then
  > zopt / zg <= (αk)^k / ((αk)^k − (αk − 1)^k) <= e^{1/α} / (e^{1/α} − 1)."

  配套的 greedy 算法定义 (同页 Step 2):

  > "Select an element ei ∈ E \ Si−1 for which α ρei(Si−1) ≥ max_{e∈E\Si−1} ρe(Si−1) using an α-approximate incremental oracle."

  证明结尾同时给出正向形式:

  > "zg = Σ_{i=1}^{k} ρi ≥ ((αk)^k − (αk − 1)^k) / (αk)^k · zopt"

  这正是 1 - (1 - 1/(αk))^k >= 1 - e^{-1/α} 的等价写法 (取倒数形式)。
- **说明 (nuance)**: 原文以 **比值 zopt/zg 的上界** 形式陈述, 上界为 e^{1/α}/(e^{1/α}−1); 我们论文中以 **近似比 1 - e^{-1/α}** 的形式引用, 二者等价 (1 - e^{-1/α} = (e^{1/α}−1)/e^{1/α})。引用时若写 "1 - e^{-1/α}" 建议注明 "equivalently/in ratio form", 以免与原文字面不符。原文中定理编号 K 用的是小写 k, 我们论文用 K, 属记号差异。
- **另注**: Theorem 2 (locally greedy, partition matroid) 与 Theorem 3 (general independence systems, 1/(αM+1) 型) 是不同结论, 不要混引。
- **状态**: **FOUND** —— "Theorem 1" 正确, 无需修正。

---

## 事实 2 (Fact 2): Horel & Singer, (1-eps)/(1+eps) 观察的确切位置, 以及 greedy 阈值 eps < 1/k 的命题编号

- **待核事实 (a)**: 引言中 "某函数 F 在 f 的 1 ± eps 之内, 则 F 的极大化者对 f 是 (1-eps)/(1+eps)-approximation" 这一观察的确切 section/paragraph。
- **待核事实 (b)**: 给出 greedy 阈值 eps < 1/k 的 proposition/theorem 编号 (早先简报写的是 Proposition 6, 需验证)。
- **来源 URL (已实际 fetch)**:
  - https://proceedings.neurips.cc/paper_files/paper/2016/file/81c8727c62e800be708dbf37c4695dff-Paper.pdf (全文 PDF, 9 页 + 附录, 本地抽取文本核对)
  - https://proceedings.neurips.cc/paper/2016/hash/81c8727c62e800be708dbf37c4695dff-Abstract.html (落地页, 核对题名与会议)

### (a) 位置: Section 1 (Introduction), 小标题段落 "Optimization of approximate submodularity" (第 2 页), 该段最后第三句, 紧接在 1.1 "Overview of the results" 之前

- **原文引用 (verbatim)**:

  > "Note that if there exists an α-approximation algorithm for the problem of maximizing an ε-approximate submodular function F , then this algorithm is a α(1−ε)/(1+ε)-approximation algorithm for the original submodular function f."

  该句带脚注 1:

  > "Observe that for an approximately submodular function F , there exists many submodular functions f of which it is an approximation. All such submodular functions f are called representatives of F . The conversion between an approximation guarantee for F and an approximation guarantee for a representative f of F holds for any choice of the representative."

  同页 (1) 式给出 eps-approximately submodular 的定义:

  > "(1−ε)f(S) ≤ F (S) ≤ (1 +ε)f(S)."
- **说明**: 原文写的是一般的 α(1−ε)/(1+ε); 我们论文引用的 "极大化者是 (1-ε)/(1+ε)-approximation" 是 α = 1 的特例, 与原文一致但并非逐字。建议引用时写 "a special case (α = 1) of the observation in Horel and Singer (2016), Section 1"。
- **状态**: **FOUND** (位置 = Section 1 Introduction, "Optimization of approximate submodularity" 段)。

### (b) 编号: 阈值 eps ~ 1/k 涉及两条不同结论, 需区分

- **正向保证 (greedy 在 eps <= 1/k 时仍有常数近似) = Theorem 5**, 原文 Section 3.1 "Greedy algorithm" 引言句与定理:

  > "Running the same algorithm for an ε-approximately submodular function results in a constant approximation ratio when ε ≤ 1/k."

  > "Theorem 5. Let F be an ε-approximately submodular function, then the set S returned by the greedy algorithm satisfies: F (S) ≥ 1/(1 + 4kε) · (1−ε)^2 · (1 − ((1−ε)/(1+ε))^{2k} (1 − 1/k)^k) ..."

  Section 1.1 概述中对应表述:

  > "In the general case of monotone submodular functions we show that the greedy algorithm achieves a (1−1/e−O(δ)) approximation ratio when ε = δ/k (Theorem 5)."

- **紧性 / 阈值不可超越 (eps = 1/k 是 greedy 的临界) = Proposition 6**:

  > "The following proposition shows that ε = 1/k is tight for the greedy algorithm, and that this is the case even for additive functions."

  > "Proposition 6. For any β > 0, there exists an ε-approximately additive function with ε = Ω(1/k^{1−β}) for which the Greedy algorithm has non-constant approximation ratio."

  Section 1.1 概述:

  > "Furthermore, this bound is tight: given a 1/k^{1−β}-approximately submodular function, the greedy algorithm no longer provides a constant factor approximation guarantee (Proposition 6)."

- **状态**: **FOUND**, 但 **早先简报的 "Proposition 6" 只在紧性含义下正确**。若我们的句子表述为 "greedy 在 eps < 1/k 时仍有常数保证", 正确编号是 **Theorem 5**; 若表述为 "eps = 1/k 是 greedy 的紧阈值 / 超过即失效", 才是 **Proposition 6**。请据正文措辞择一, 或同时引 (Theorem 5 与 Proposition 6)。
- **矩阵约束的类比结论是 Theorem 7, 有界曲率的是 Proposition 8, 勿混引。**

---

## 事实 3 (Fact 3): 两篇文献的确切题名与出处

### 3.1 goundan2007revisiting
- **确切题名 (PDF 首页与落地页一致)**: "Revisiting the Greedy Approach to Submodular Set Function Maximization"
- **作者**: Pranava R. Goundan (Analytics Operations Engineering); Andreas S. Schulz (MIT Sloan School of Management)
- **出处 (落地页给出的引用格式)**: "Working Paper, Massachusetts Institute of Technology, 2007"; Optimization Online 提交日期 2007 年 8 月 1 日, preprint 编号 1740
- **来源 URL**: https://optimization-online.org/2007/08/1740/ ; https://optimization-online.org/wp-content/uploads/2007/08/1740.pdf
- **状态**: **FOUND**

### 3.2 horel2016maximization
- **确切题名 (NeurIPS 落地页与 PDF 一致)**: "Maximization of Approximately Submodular Functions"
- **作者**: Thibaut Horel, Yaron Singer
- **出处**: Advances in Neural Information Processing Systems 29 (NIPS 2016)
- **来源 URL**: https://proceedings.neurips.cc/paper/2016/hash/81c8727c62e800be708dbf37c4695dff-Abstract.html
- **页码 3045--3053**: NeurIPS 落地页未显示页码, 我们未从实际 fetch 的来源中核到该页码区间。
- **状态**: 题名/作者/会议 **FOUND**; 页码 `3045--3053` **[CITATION-NEEDS-VERIFICATION]** (未从实际 fetch 的来源证实, 不据猜测改动)。

---

## paper/references.bib 一致性检查

检查文件: `/home/user/sub-modular-optimization/paper/references.bib` (第 53-61 行, 第 68-75 行)。

### goundan2007revisiting (第 53-61 行)
| 字段 | bib 现值 | 来源核对 | 判定 |
|---|---|---|---|
| author | Goundan, Pranava R. and Schulz, Andreas S. | 一致 | OK |
| title | Revisiting the greedy approach to submodular set function maximization | 原文为 Title Case: "Revisiting the Greedy Approach to Submodular Set Function Maximization" | **轻微不一致**: 大小写。BibTeX 样式会自行降格, 但建议加保护括号 `{G}reedy` 等, 或整体保留小写并在 style 允许下不改。不影响可检索性。 |
| institution | Massachusetts Institute of Technology | 与落地页 "Working Paper, Massachusetts Institute of Technology, 2007" 一致 | OK |
| year | 2007 | 提交日 2007-08-01 | OK |
| type | Working paper | 与落地页用词一致 | OK |
| note | Optimization Online preprint 1740 | 与 URL 中编号 1740 一致 | OK |
| url | https://optimization-online.org/2007/08/1740/ | 可访问 | OK |

结论: 无实质性错误, 仅题名大小写与原文不同。

### horel2016maximization (第 68-75 行)
| 字段 | bib 现值 | 来源核对 | 判定 |
|---|---|---|---|
| author | Horel, Thibaut and Singer, Yaron | 一致 | OK |
| title | Maximization of approximately submodular functions | 原文 Title Case: "Maximization of Approximately Submodular Functions" | **轻微不一致**: 大小写, 同上 |
| booktitle | Advances in Neural Information Processing Systems 29 ({NIPS} 2016) | 落地页写作 "Advances in Neural Information Processing Systems 29 (NIPS 2016)" | OK |
| pages | 3045--3053 | 未从实际 fetch 的来源证实 | **[CITATION-NEEDS-VERIFICATION]** |
| year | 2016 | 一致 | OK |
| url | proceedings.neurips.cc/paper/2016/hash/81c8727c62e800be708dbf37c4695dff-Abstract.html | 可访问, 指向正确论文 | OK |

结论: 无实质性错误; `pages` 字段待核。

---

## 对正文引用措辞的建议 (不改文件, 仅记录)

1. Goundan-Schulz 的 "Theorem 1" 编号正确, 但原文是比值上界形式, 建议在正文写 "Theorem 1 (stated there as a bound on zopt/zg)" 或直接引用等价的 1 - (1 - 1/(αK))^K 形式并注明等价。
2. Horel-Singer 的 (1-ε)/(1+ε) 观察, 应定位到 "Section 1, paragraph 'Optimization of approximate submodularity'", 且注明是原文 α(1−ε)/(1+ε) 在 α = 1 的特例。
3. Horel-Singer 的 greedy 阈值: 正向保证引 **Theorem 5**, 紧性引 **Proposition 6**。早先简报单写 Proposition 6, 若正文句意为正向保证则需改为 Theorem 5。

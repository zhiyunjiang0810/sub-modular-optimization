# 量词审计（criteria A 与 E）：thm:hardness / 台账 T10（TASKS11 Q7，正文 Theorem 3）

本文件只做两件事：A 项逐量词比对正文 environment 与台账卡的陈述行；E 项建立量词审计表，
把陈述里的每个量词与形容词落到路线甲证明（`app:hardness`）的具体位置，落不上的记 GAP。
TASKS11 给本条目没有专项问题（"fixed random string" 问题属 thm:ceiling，计数链收紧问题属
thm:linear-exact），§3 只记与本条目相邻、审计中确认过的两件事。

范围与纪律：不修改任何已有文件，不运行 git。本文件自身的算术用 sympy 与 `fractions.Fraction`
精确核对（结果见 §5），浮点只出现在打印里。状态标签按 CLAUDE.md：[VERIFIED-SYMBOLIC]
[VERIFIED-LP] [VERIFIED-EXHAUSTIVE] [HAND-PROOF-UNREVIEWED] [CONJECTURE] [FAILED]。
读过的文件见 §6。

---

## 1. Criterion A：正文陈述与台账陈述的逐量词比对

### 1.1 三份原文

正文：`paper/sections/results.tex` 第 587 至 611 行，environment `theorem`，label `thm:hardness`，
标题 "Bounded-query hardness, deterministic"。环境之前第 552 至 586 行是 `sec:hardness` 的引导段
（定义 $a_\theta,A_\theta,B_\theta,\delta(\theta),\Psi(\theta),\bar\theta$ 与被取代的 $\Phi,\hat\eta$），
之后第 612 至 664 行是 "Three scope notes"，第 665 至 693 行是 `rem:hardness-chain`，
第 694 行起是 `rem:hardness-pins`。

矩阵输入：`results/V11/statements.md` 第 278 至 316 行的 LaTeX 块与
`results/V11/inputs/statement_hardness.md` 第 6 至 30 行。两者与正文 environment **逐字符相同**
（本次用 python 做全等比较，两项均为 True，§5 第 9 条）。因此 A 项的实质比对对象是正文
environment 对台账卡的中文陈述行。

台账：`THEOREM_LEDGER.md` 第 230 至 247 行，卡 `## T10 thm:hardness`。其中"陈述"行是第 231 行
（单行），另有"状态"（232）、"副产品"（233）、"禁止声称"（234 至 236）、"第九晚注 P0/P1"
（237 至 241）、"禁止声称 M4 追加"（242 至 243）、"禁止声称 第九晚追加"（244 至 246）五组，
A 项只比对"陈述"行。

### 1.2 逐项对照

| 量词 / 形容词 | 正文（results.tex 587-611） | 台账（T10 陈述行 231） | 判定 |
|---|---|---|---|
| $c\ge0$ 实数 | "Let $c\ge0$ be real" | "c ≥ 0 实数" | 一致 |
| $\tau=\lceil c\rceil+1$ | "put $\tau=\lceil c\rceil+1$, which equals $c+1$ at integer $c$" | "τ=⌈c⌉+1" | **差异 D1**（整数 c 的等式只在正文） |
| $K>\tau$ | "Let the integers $K>\tau$" | "K>τ" | **差异 D2**（"the integers" 只在正文，见下） |
| $n\ge4K^{c+2}$ | "$n\ge4K^{c+2}$" | "n ≥ 4K^{c+2}" | 一致 |
| $\eta>1$ | "the real $\eta>1$" | "η>1" | 一致 |
| $\eta\ge(K-1)/(K-\tau)$ | "with $\eta\ge\tfrac{K-1}{K-\tau}$ ... so that $\bar\theta\ge1$" | "η ≥ (K−1)/(K−τ)" | 一致（正文多写等价形式 $\bar\theta\ge1$） |
| $\bar\theta$ 的定义 | 不在 environment 内（第 571 行引导段给 $\bar\theta=\Psi^{-1}(\eta)=(\eta(K-\tau)+1)/K$） | "θ̄=(η(K−τ)+1)/K" 写在陈述行内 | **差异 D3**（定义位置不同） |
| 参数被"固定" | "be fixed" | 无对应词 | 计入 D3（同一处，不另计） |
| ∀ deterministic algorithm | "For every deterministic algorithm" | "任意确定性算法" | 一致 |
| 查询次数 $\le n^{c}$ | "making at most $n^{c}$ queries to $\tilde f$" | "≤n^c 次 ... f̃ 查询" | 一致 |
| 每次查询集合大小 $\le K$ | "each on a set of size at most $K$" | "每次集合大小 ≤K" | 一致 |
| 输出集合大小 $\le K$ | 作为结论里对 $T$ 的插入语 "the output $T$ (of size at most $K$)" | 作为算法类的限定 "输出 ≤K 元素" | **差异 D4**（同一限制，作用域位置不同） |
| ∃ instance $(f,\tilde f)$（在 ∀ 算法之后） | "there is an instance $(f,\tilde f)$" | "存在 ... 的实例" | 一致（量词顺序同） |
| $f$ monotone submodular | "with monotone submodular $f$" | 无 | **差异 D5** |
| 误差"恰为"$\eta$ | "whose **smallest admissible** error factors in Definition~\ref{def:eta} have product **exactly** $\eta$" | "实际误差恰为 η" | **差异 D6**（"smallest admissible" 与 Definition 1 指针只在正文） |
| 结论式 | $f(T)/f(O^{\ast})\le H_{K,\tau}(\eta):=1-(1-\frac1{\eta(K-\tau)+1})^{K}=L_K(\bar\theta)$ | 同式 | 一致 |
| 任意给定拆分 $\eta_u\eta_o=\eta$ | "Any prescribed split $\eta_u\eta_o=\eta$ of that error is realized by the rescaling of Appendix~\ref{app:hardness}" | 无 | **差异 D7** |
| 随机版：∀ randomized ∃ instance | "For randomized algorithms the same bound holds in expectation" | "随机版加 ε_n" | **差异 D8**（两边都没写量词顺序，正文另有 "in expectation" 一词） |
| 随机版：expectation 的对象 | 不写（只写 "in expectation"） | 不写 | 一致（两边都缺，见 E 表第 26 行） |
| 随机版：$\varepsilon_n$ 的值 | $\varepsilon_n=\frac Kn+\frac{K^{2\tau+2}}{(\tau+1)!\,n^{\tau+1-c}}$ | ε_n=K/n+K^{2τ+2}/((τ+1)! n^{τ+1−c}) | 一致 |
| 随机版：整数 $c$ 的形式 | "which for integer $c$ reads $\tfrac Kn+\tfrac{K^{2c+4}}{(c+2)!\,n^{2}}$" | 无 | **差异 D9** |
| 两条极限 | "As $K\to\infty$ with $\tau$ and $\theta$ fixed, $K\delta(\theta)\to\tau-1/\theta$; with $c$ and $\eta$ fixed, $H_{K,\tau}(\eta)\to1-e^{-1/\eta}$" | 无 | **差异 D10** |
| adversarial ties / fixed $K$ steps / $|S|\le K$ 之外的查询大小 | 不出现 | 不出现 | 一致（见 E 表第 32 至 34 行） |
| $f(\emptyset)=0$、$\tilde f(\emptyset)=0$、OPT > 0、$1\le K\le n$ | 不出现（继承 `model.tex` 第 9 至 17 行） | 不出现 | 一致 |

### 1.3 A_diffs

**A_match = false**，共 10 条差异：

- **D1（整数 c 的等式）**：正文写 "$\tau=\lceil c\rceil+1$, which equals $c+1$ at integer $c$"，
  台账只写 "τ=⌈c⌉+1"。这半句承重：附录第 1603 至 1605 行说明计数一步用的是 $\tau$ 的整数性，
  正文的这半句是读者把 $\tau$ 读回 $c+1$ 的唯一许可；台账的"禁止声称"组也没有替代句。
- **D2（K 与 n 的整数性）**：正文写 "Let the integers $K>\tau$ and $n\ge4K^{c+2}$"，台账陈述行不写。
  $1\le K\le n$ 的整数约定在 `model.tex` 第 15 行，台账靠继承，内容不冲突，按 A 项规则记为差异。
- **D3（$\bar\theta$ 的定义位置）**：台账把 $\bar\theta=(\eta(K-\tau)+1)/K$ 写在陈述行内；正文的
  environment 内只出现 $\bar\theta\ge1$ 与结论式右端的 $L_K(\bar\theta)$，定义在第 571 行的引导段。
  单读 environment 时 $\bar\theta$ 是未绑定符号，这是呈现层差异，不是内容分歧。
- **D4（输出大小的作用域）**：正文把 "(of size at most $K$)" 放在结论里修饰 $T$，台账把"输出 ≤K 元素"
  放在算法类的限定里。附录第 1607 至 1609 行是台账读法（"return a set of size at most $K$"），
  且该限制在证明里被用了两次（见 E 表第 15 行），所以台账的位置与证明一致，正文的插入语读法更弱。
- **D5（monotone submodular）**：正文写 "with monotone submodular $f$"，台账陈述行没有这四个词。
  构造侧由附录第 1570 至 1590 行与 `lem:app-count` 承担，台账"状态"行也不提；按 A 项规则记为差异。
- **D6（smallest admissible）**：正文写 "smallest admissible error factors in Definition~\ref{def:eta}
  have product exactly $\eta$"，台账写"实际误差恰为 η"。两者指同一件事（$\eta^{\mathrm{act}}=\theta AB$），
  但台账缺"最小可行因子"这层措辞，而这正是台账"禁止声称"第一条（旧 $\Phi$ 校准的 "error exactly η"）
  要防的坑，陈述行自身没有写出防线。
- **D7（拆分子句）**：正文有 "Any prescribed split $\eta_u\eta_o=\eta$ ... is realized by the rescaling"，
  台账陈述行完全没有拆分量词。附录第 1560 至 1569 行有对应段（$\beta=\eta_o/(\sqrt\theta A)$）。
  对照：同类卡 T10c 的陈述行是写了拆分量词的，本卡没有。
- **D8（随机版的量词顺序与 "in expectation"）**：正文写 "For randomized algorithms the same bound holds
  in expectation up to an additive ..."，台账写"随机版加 ε_n"。两边都没有写成"对任意随机算法存在实例"，
  也都没有写期望对什么取（附录第 1639 至 1657 行取的是 random seed $r$ 与均匀 $O$ 的两次平均）。
  正文比台账多 "in expectation" 一词，记为差异；两边共同缺的部分记在 E 表第 26、27 行。
- **D9（整数 c 的 $\varepsilon_n$ 形式）**：正文多一句 "which for integer $c$ reads
  $K/n+K^{2c+4}/((c+2)!\,n^{2})$"，台账无。该式是 $\tau=c+1$ 的代入，附录无单列位置（E 表第 29 行）。
- **D10（两条极限）**：正文末句的两条极限（$K\delta(\theta)\to\tau-1/\theta$ 与
  $H_{K,\tau}(\eta)\to1-e^{-1/\eta}$）在台账陈述行里完全没有。第一条还引入了 environment 内未量化的
  符号 $\theta$（设计参数，定义在第 552 至 560 行的引导段），见 E 表第 30 行。

不计入 A_diffs 的呈现差异一条：台账用一行中文流水句，正文用 environment 加三条 scope notes；
scope notes（$\varepsilon_n$ 不自动消失、查询大小是查询模型条件、$\min\{H,1/\eta\}$ 的合并）
在台账里分散在"禁止声称"组第 234 至 236 行，内容对应，位置不同。

---

## 2. Criterion E：量词审计表（落到路线甲）

路线甲 = `paper/sections/appendix_proofs.tex` 的
`\subsection{Bounded-query hardness (Theorem~\ref{thm:hardness})}` `\label{app:hardness}`
（第 1461 至 1699 行），段落锚点：
`\paragraph{The family.}`（1497）、`\paragraph{Every edge of the count grid.}`（1517）、
`\paragraph{A prescribed split of the error.}`（1560）、
`\paragraph{The true objective and its optimum.}`（1570）、`\paragraph{Counting.}`（1591）、
`\paragraph{The canonical transcript, and the deterministic statement.}`（1606）、
`\paragraph{Randomized algorithms, by averaging.}`（1638）、
`\paragraph{Calibration, comparison with the symmetric band, and the limit.}`（1658）。
第 1492 至 1496 行是 "information-theoretic" 一词的用法声明。
被引用的辅助引理：`lem:app-count`（同文件第 53 至 74 行，counting functions）。
脚本：`results/J2_core_oracles.py`（`hardness_fraction_grid` 第 223 至 269 行、
`calibration_comparison` 第 272 至 289 行、`symbolic_core` 第 29 行起）、
`results/H3_j2_recheck.py`（第 4 项：边表极值与闭式对照；第 5 项：新旧校准表）。

状态列：**OK** = 路线甲有明确处理；**OK(隐含)** = 有处理但无独立句子；**部分** = 有处理但缺一步
或缺定义；**GAP(陈述层)** = 路线甲有，陈述里缺该量词；**GAP** = 路线甲没有对应位置；
**N/A** = 本陈述没有这个量词。

| 量词 / 形容词 | 处理位置（file + paragraph） | 状态 |
|---|---|---|
| 1. $c\ge0$ 实数 | app:hardness `Counting.`（1591）末句第 1603 至 1605 行 "The integrality of $\tau$ enters at this step, which is the reason for $\tau=\lceil c\rceil+1$ rather than $\tau=c+1$ at real $c$"；$c$ 本身只通过 $Q=n^{c}$ 与指数 $\tau+1-c$ 进入 | OK |
| 2. $\tau=\lceil c\rceil+1$ 整数 | `The family.` 第 1498 行 "Fix integers $1\le\tau<K<n$"；整数性的消费点是 `Counting.` 的 $\binom{K}{\tau+1}$ 与 $(\tau+1)!$ | OK |
| 3. $K>\tau$ | 第 1498 行同句；消费点是 $A_\theta=a^{\tau}K/(K-\tau)$ 与 $G_O$ 第二支的 $\frac{K-y}{K-\tau}$（$K=\tau$ 时分母为 0），以及第 1548 至 1550 行 "both are attained on actual edges because $n>K$ and $1\le\tau<K$" | OK |
| 4. $K\ge2$（隐含） | 由 $K>\tau\ge1$ 得；第 1498 行。陈述与台账都不单列 $K\ge2$ | OK(隐含) |
| 5. $K$、$n$ 为整数 | 第 1498 行 "Fix integers"；`model.tex` 第 15 行 $1\le K\le n$ | OK |
| 6. $n\ge4K^{c+2}$ | `The canonical transcript ...` 第 1618 至 1624 行 "Under $n\ge4K^{c+2}$ the first term is at most $\frac{K^{c(c+1-\tau)}}{(\tau+1)!\,4^{\tau+1-c}}\le\frac1{16(\tau+1)!}\le\frac1{32}$"，第二项 $K^{2}/n\le1/(4K^{c})\le1/4$，合计 $\le9/32$ | OK（充分非必要，§5 第 6 条精确复核） |
| 7. 基础集大小 $n>K$（构造所需，隐含） | 第 1498 行 "$1\le\tau<K<n$"；第 1538 至 1539 行 "the table is the same for all $n>K$"。陈述只写 $n\ge4K^{c+2}$，而 $4K^{c+2}\ge4K^{2}>K$，故 $n>K$ 是推论 | OK(隐含) |
| 8. 计数里的 $n\ge K$ | `Counting.` 第 1595 至 1597 行 "since $(K-i)n\le K(n-i)$ for $n\ge K$" | OK |
| 9. $\eta>1$（严格） | 路线甲**没有任何一步消费严格性**：族只要求 $\theta\ge1$，$a=1-1/(\theta K)\in(0,1)$ 在 $\theta=1$ 仍成立，$\eta=(K-1)/(K-\tau)$ 时 $\bar\theta=1$ 合法（§5 第 8 条）。删去严格性后陈述在 $\eta=(K-1)/(K-\tau)$ 处仍真 | **部分**（形容词是充分设定，非承重） |
| 10. $\eta\ge(K-1)/(K-\tau)$（等价 $\bar\theta\ge1$） | `The family.` 第 1498 行 "a real $\theta\ge1$" + `Calibration ...` 第 1659 行 $\theta=\bar\theta=\Psi^{-1}(\eta)$；等价性 §5 第 4 条 [VERIFIED-SYMBOLIC] | OK |
| 11. $\bar\theta$ 的定义 | results.tex 第 571 行（引导段）；app:hardness 第 1659 行重述 | OK（environment 内未绑定，见 D3） |
| 12. ∀ deterministic algorithm | `The canonical transcript ...` 第 1607 行 "Let $\mathcal A$ be deterministic"；确定性的消费点在第 1627 至 1630 行的归纳 "determinism makes the $i$th query equal to $S_i$" | OK |
| 13. 至多 $n^{c}$ 次查询 | 同段第 1607 至 1608 行 $Q=n^{c}$；消费点是第 1613 至 1617 行把单查询界乘 $Q$ 得 $n^{\tau+1-c}$ | OK |
| 14. 每次查询 $|S|\le K$ | `Counting.` 第 1592 行 "For a fixed $S$ with $|S|\le K$" 与 $\binom{K}{\tau+1}$ 的上界（只在这里消费；$G_O$ 的第一支对任意大小的 balanced 集合都等于 $\hat G(|S|)$） | OK |
| 15. 输出 $|T|\le K$ | `The canonical transcript ...` 第 1607 至 1609 行 "return a set of size at most $K$"，消费两次：$\Pr[T_0\cap O\ne\emptyset]\le|T_0|K/n\le K^{2}/n$（第 1612 行）与 `The true objective ...` 第 1588 至 1590 行 $1-a^{|T|}\le1-a^{K}$ | OK |
| 16. 算法只查 $\tilde f$，查不到 $f$ | `model.tex` 第 11 至 13 行；app:hardness 第 1610 行把 $\mathcal A$ 跑在 canonical oracle $S\mapsto\hat G(|S|)$ 上 | OK |
| 17. ∃ instance（顺序在 ∀ 算法之后） | `The canonical transcript ...` 第 1625 至 1627 行 "at least one $K$-set $O$ makes every canonical query balanced and misses $T_0$; fix such an $O$"；顺序的说明在第 1633 至 1637 行 "The order of the two arguments matters ..." | OK |
| 18. $f$ monotone submodular | `The true objective and its optimum.` 第 1571 至 1583 行（一阶差分非负、二阶差分非正）+ `lem:app-count`（第 53 至 74 行） | OK |
| 19. $f$ normalized，$f(\emptyset)=0$ | 同段第 1583 行 "makes $F_O$ a normalized monotone submodular function"；$F_O(0,0)=0$ 未单列，§5 第 2 条精确核对 | OK(隐含) |
| 20. $\tilde f(\emptyset)=0$ 与预测增益非负 | app:hardness 无单列句；$G_O(0,0)=0$ 与所有边 $r>0$ 由边表隐含（`model.tex` 第 12 行要求 $\tilde f(\emptyset)=0$，Definition 1 要求预测增益非负），§5 第 1、2 条精确核对 | OK(隐含) |
| 21. $d_e(S)=0\Rightarrow\tilde d_e(S)=0$（Definition 1） | `Every edge of the count grid.` 第 1533 至 1535 行 "An $x$-edge starting at $y=K$ has zero true and zero predicted gain, and no $y$-edge starts at $y=K$" | OK |
| 22. 误差因子是"最小可行"且被取到 | 同段第 1547 至 1550 行 "the largest and the smallest values of $r$ over the whole grid are $A$ and $1/(\theta B)$, and both are attained on actual edges" | OK |
| 23. 两个因子 $\ge1$（Definition 1 的要求） | 同段第 1547 行 "Since $A\ge1$ and $B\ge1$" 与第 1558 行 "both factors are at least $1$"，$A\ge1$ 即 $a^{\tau}\ge1-\tau/K$（Bernoulli）未写出 | **部分**（断言无论证；§5 第 1 条对 140 组参数精确核对 [VERIFIED-EXHAUSTIVE 有限参数]） |
| 24. 误差乘积"恰为 $\eta$" | `Every edge ...` 第 1551 至 1557 行 $\eta^{\mathrm{act}}=\theta AB=\Psi(\theta)$ + `Calibration ...` 第 1659 至 1660 行 "makes the pair's error exactly $\eta$" | OK |
| 25. 任意给定拆分 $\eta_u\eta_o=\eta$ | `A prescribed split of the error.` 第 1560 至 1569 行（$\beta=\eta_o/(\sqrt\theta A)$，canonical profile 同乘 $\beta$ 仍只依赖 $|S|$，故不泄漏 $O$） | OK |
| 26. 随机版：期望对什么取 | 陈述只写 "in expectation"；路线甲 `Randomized algorithms, by averaging.` 第 1639 行 "Fix the random seed $r$" 与第 1652 至 1657 行的两次平均（对 $r$ 与对均匀 $O$，再用 $\min_O\le\mathbb E_O$）说明是对算法自身 random seed 取期望 | **GAP(陈述层)**（证明有，陈述与台账都没写） |
| 27. 随机版：∀ 随机算法 ∃ 实例，且该实例误差仍恰为 $\eta$ | 路线甲同段给出单个 $O$（对所有 seed 统一）；族与校准不变故误差仍恰为 $\eta$。陈述只写 "the same bound holds"，未写量词顺序，也未重述误差校准 | **GAP(陈述层)** |
| 28. $\varepsilon_n=K/n+K^{2\tau+2}/((\tau+1)!\,n^{\tau+1-c})$ | 同段：中间项 $|T_0^{(r)}\cap O|/K$ 对均匀 $O$ 平均得 $\le K/n$，$\mathbf 1[E_r^{c}]$ 项用 `Counting.` 的查询并集界（注意确定性显示式里的第二项是 $K^{2}/n$，随机版因除以 $K$ 变成 $K/n$，两者一致） | OK |
| 29. 整数 $c$ 的形式 $K/n+K^{2c+4}/((c+2)!\,n^{2})$ | 附录无单列位置；由 $\tau=c+1$ 代入得（$2\tau+2=2c+4$、$\tau+1-c=2$）。results.tex 第 613 至 616 行的 scope note 用同一代入给出 $1/(16(c+2)!)$ | **部分**（纯代入，§5 第 7 条精确核对） |
| 30. $K\to\infty$、$\tau$ 与 $\theta$ 固定：$K\delta(\theta)\to\tau-1/\theta$ | `Calibration ...` 第 1681 至 1683 行 $\delta(\theta)=AB-1=(\tau-1/\theta)/(K-\tau)$。符号 $\theta$ 在 environment 内未量化（定义在 results.tex 第 552 至 560 行的引导段），且与陈述其余部分用的 $\bar\theta$ 不是同一个量 | **部分**（数学有处理，陈述层符号未绑定） |
| 31. $c$ 与 $\eta$ 固定：$H_{K,\tau}(\eta)\to1-e^{-1/\eta}$ | 同段第 1683 至 1685 行 "$K/(\eta(K-\tau)+1)\to1/\eta$ and $H_{K,\tau}(\eta)\to1-e^{-1/\eta}$" | OK |
| 32. adversarial ties | 本陈述无此形容词（`model.tex` 第 70 至 72 行是 predictive greedy 的属性）。路线甲对应的隐含要求是：算法的下一步查询是已收到答案的确定函数，这由第 12 行的 determinism 承担 | N/A（隐含要求已由 determinism 覆盖） |
| 33. fixed $K$ steps | 本陈述无此形容词；算法类只限查询次数、查询大小与输出大小 | N/A |
| 34. arbitrary query access / 至多 $nK$ 次查询 | 本陈述无（任意大小查询版本是 `app:hardness-anysize`，$\le nK$ 版本是 `thm:linear-exact`）。results.tex 第 657 至 663 行的空洞性检验注释对这两个方向各给一句 | N/A |
| 35. 结论只用乘积 $\eta$、不用拆分 | `lem:scaling`（`model.tex` 第 45 至 57 行，band 类意义）+ 第 25 行的显式 rescaling；`model.tex` 第 60 至 63 行注明读预测**值**的算法不被 run-invariance 覆盖，hardness 用显式 rescaling 处理拆分 | OK |
| 36. 恒等式 $H_{K,\tau}(\eta)=L_K(\bar\theta)$ | `Calibration ...` 第 1660 至 1664 行；[VERIFIED-SYMBOLIC]（`results/J2_core_oracles.py`，§5 第 3 条独立复核） | OK |
| 37. $\tau=1$ 时 $H_{K,1}=U_K$（台账副产品，正文 `rem:hardness-chain`） | results.tex 第 665 至 693 行；代入 $\tau=1$ 一行 | OK（不在陈述内，列出以备比对） |
| 38. $O^{\ast}=O$ 且 OPT > 0 | `The true objective and its optimum.` 第 1584 至 1587 行 $\max_{|S|\le K}F_O(S)=F_O(O)=\theta^{-1/2}>0$；`model.tex` 第 15 至 17 行另有 OPT = 0 的平凡约定 | OK |

### 2.1 GAP 清单

- **GAP(陈述层) 1（行 26）**：随机版的期望没有写明对什么取。路线甲取的是算法自身 random seed
  与均匀 $O$ 的两次平均，最终给出一个**固定实例**上关于 seed 的期望；陈述与台账陈述行都只写
  "in expectation" / "随机版加 ε_n"。对照：同族的 T10b、T10c 卡写的是 $\mathbb E_{\mathrm{seed}}$。
- **GAP(陈述层) 2（行 27）**：随机版没有写"对任意随机算法存在实例"的量词顺序，也没有重述该实例的
  误差仍恰为 $\eta$。两处都由路线甲给出，陈述层缺。

无 route-one GAP：E 表 38 行里没有一行在 `app:hardness` 完全找不到落点。三行标 **部分**
（行 9 的 $\eta>1$ 严格性、行 23 的 $A\ge1,B\ge1$、行 29 的整数 $c$ 代入、行 30 的 $\theta$ 未绑定，
共四行），理由逐行写在表内。

---

## 3. 两条与本条目相邻、审计中确认过的事（不改文件，仅记录）

1. **状态分解**与台账一致：边表、极值因子、$\Psi(\theta)=(\theta K-1)/(K-\tau)$、二阶差分、
   校准恒等式与两条极限是 [VERIFIED-SYMBOLIC] + [VERIFIED-LP]（`results/J2_core_oracles.py`：
   $K=2..12$、每个整数 $\tau=1..K-1$、$\theta\in\{1,6/5,2,4\}$ 的精确有理 count grid）；
   计数界、canonical transcript 归纳与两次平均是 [HAND-PROOF-UNREVIEWED]，
   附录第 1694 至 1699 行与台账第 232 行都写明不升级。本审计不改动任何标签。
2. **有限参数下 $H_{K,\tau}$ 可超过 $1/\eta$**：$\eta=2$、$c=2$（$\tau=3$）、$K=8$ 时
   $H=1-(10/11)^{8}=114358881/214358881\approx0.5335>1/2$（§5 第 5 条精确复核），
   与 results.tex 第 619 至 623 行的 scope note 及台账第 235 行的"禁止声称"一致：
   本定理的内容是与 $L_K$ 的渐近吻合，不是逐点改进；两个上界按 $\min\{H_{K,\tau}(\eta),1/\eta\}$ 合并。

---

## 4. 空洞性检验（CLAUDE.md 第二晚规则）逐个形容词

| 形容词 | 去掉或换成对立面后 | 判定 |
|---|---|---|
| deterministic | 陈述变为随机版，结论差一个加性 $\varepsilon_n$（正文同句给出） | 承重，保留 |
| 每次查询 $|S|\le K$ | 预算含义变，常数不变（附录 1592 行是唯一消费点）；任意大小版本另见 `app:hardness-anysize` | 承重（改变类而非常数），正文第 657 至 663 行的注释已写清 |
| 至多 $n^{c}$ 次 | 去掉预算就回到 `thm:ceiling` 的 $1/\eta$，常数不同 | 承重，保留 |
| monotone submodular $f$ | 去掉则实例出模型 | 承重，保留 |
| 误差"恰为 $\eta$"（对"至多 $\eta$"） | 至多 $\eta$ 是更弱的实例要求，会让 hardness 更容易而结论更弱；恰为 $\eta$ 是被校准取到的 | 承重，保留 |
| $\eta>1$ 严格 | 在 $\eta=(K-1)/(K-\tau)$（$\tau=1$ 时即 $\eta=1$）处路线甲仍给出同一结论 | **不承重**（E 表行 9），本审计不建议改动正文，只记录 |
| "the integers"（$K$、$n$） | 与 `model.tex` 重复 | 呈现层，保留无害 |

---

## 5. 本文件自身算术的核对

临时脚本（不入库，位于本次会话的 scratchpad
`hardness_audit_checks.py`）用 sympy 与 `fractions.Fraction` 做了 9 组精确核对，
全部 PASS，无 FAILED：

1. **边表极值与实际误差** [VERIFIED-EXHAUSTIVE 有限参数]：自写一份 $F_O$、$G_O$ 实现
   （$K=2..8$ × 每个整数 $\tau=1..K-1$ × $\theta\in\{1,3/2,2,7/3,4\}$ 共 140 组，$x$ 取到 $K+3$），
   逐边精确有理核对 $\max r=A$、$\min r=1/(\theta B)$、$\theta AB=(\theta K-1)/(K-\tau)$、
   $\theta A^{2}\ge1$ 与 $\theta B^{2}\ge1$（即 $\sqrt\theta A\ge1$、$\sqrt\theta B\ge1$）、
   真增益非负、零真增益边的预测增益为零。与 `results/J2_core_oracles.py` 的
   $K=2..12$、$\theta\in\{1,6/5,2,4\}$ 网格结论一致（本次为独立实现，未 import 该脚本）。
2. **合法性** [VERIFIED-EXHAUSTIVE 有限参数]：同 140 组参数上 $\bar F$ 的三类二阶差分 $\le0$，
   且 $\bar F(0,0)=G_O(0,0)=0$（支持 E 表行 18 至 20）。
3. **最优解与断开输出的值** [VERIFIED-EXHAUSTIVE 有限参数]：$\max_{x+y\le K}\bar F=\bar F(0,K)=1$，
   $\bar F(K,0)=1-a^{K}$（支持 E 表行 15、38）。
4. **校准** [VERIFIED-SYMBOLIC]：$\Psi(\bar\theta)=\eta$ 与
   $L_K(\bar\theta)=1-(1-\frac1{\eta(K-\tau)+1})^{K}=H_{K,\tau}(\eta)$ 的 sympy 残差为 0；
   并在 $K=2..11$、$\tau=1..K-1$、7 个 $\eta$ 上精确核对
   $\bar\theta\ge1\iff\eta\ge(K-1)/(K-\tau)$。
5. **不交叉与有限参数越界** [VERIFIED-SYMBOLIC + VERIFIED-EXHAUSTIVE]：$\eta\tau\ge1$ 时
   $\bar\theta\le\eta$ 且 $H_{K,\tau}(\eta)\ge L_K(\eta)$（$K=2..11$ 全部整数 $\tau$、4 个 $\eta$）；
   $H_{8,3}(2)=114358881/214358881>1/2$。
6. **计数算术** [VERIFIED-SYMBOLIC + VERIFIED-EXHAUSTIVE]：指数恒等式
   $2\tau+2-(c+2)(\tau+1-c)=c(c+1-\tau)$ 的 sympy 残差为 0；整数 $c=0,1,2,3$、
   $K=\tau+1..14$、$n=4K^{c+2}$ 处精确有理核对第一项 $\le1/32$、第二项 $\le1/4$、合计恰 $\le9/32<1/2$
   （最坏总和取到 $9/32$）；实数 $c\in\{1/2,3/2,7/3\}$ 处核对 $K$ 的指数 $c(c+1-\tau)\le0$。
7. **$\varepsilon_n$ 的端点值** [VERIFIED-EXHAUSTIVE 有限参数]：$n=4K^{c+2}$、整数 $c$ 时
   $\varepsilon_n$ 的第二项恰为 $1/(16(c+2)!)$，与 results.tex 第 613 至 616 行相同（$c=0..3$、$K$ 到 11）。
8. **随机版的逐点不等式** [VERIFIED-EXHAUSTIVE 有限参数]：$x\le K$ 时
   $1-a^{x}(1-y/K)\le1-a^{K}+y/K$ 在 140 组参数 × 全部 $(x,y)$ 上成立（支持 E 表行 28）；
   并核对 $\eta=(K-1)/(K-\tau)$ 时 $\bar\theta=1$、$a\in(0,1)$（支持 E 表行 9）。
9. **三份陈述文本的全等比较**：`paper/sections/results.tex` 第 587 至 611 行的 environment 与
   `results/V11/statements.md`、`results/V11/inputs/statement_hardness.md` 的 LaTeX 块
   逐字符相同（两项均为 True）。

---

## 6. 读过的文件

- `paper/sections/results.tex`（第 500 至 760 行，含 `sec:hardness` 引导段、`thm:hardness`、
  三条 scope notes、`rem:hardness-chain`、`rem:hardness-pins`）
- `paper/sections/appendix_proofs.tex`（`app:hardness` 第 1461 至 1699 行；`lem:app-count` 第 53 至 74 行；
  `app:greedybudget` 开头第 1701 至 1720 行只作邻接对照）
- `paper/sections/model.tex`（第 1 至 100 行：全局设定、`def:eta`、`lem:scaling`、predictive greedy 的固定 $K$ 步与 tie 约定）
- `THEOREM_LEDGER.md`（卡 `## T10` 第 230 至 247 行；邻接卡 T10b 第 248 至 289 行、T10c 第 290 至 330 行、
  T10d 第 331 至 368 行、T11 第 369 行起，只作量词写法对照）
- `results/V11/statements.md`（第 278 至 316 行）
- `results/V11/inputs/statement_hardness.md`（全文 31 行）
- `results/J2_core_oracles.py`（`hardness_fraction_grid`、`calibration_comparison`、`symbolic_core`）
- `results/H3_j2_recheck.py`（第 4、5 项的独立复核）
- `results/V11/audit/linear_exact.md`、`results/V11/audit/ceiling.md`（只为对齐本文件格式）
- `CLAUDE.md`（状态标签与空洞性检验规则）

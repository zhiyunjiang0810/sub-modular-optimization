# 量词审计（criteria A 与 E）：J8 ProbeLottery（Proposition；证明文件未送达，TASKS11 Q9）

本文件只做两件事：A 项把"矩阵里将要出现的陈述"与台账卡、正文 environment 逐量词比对；
E 项建立量词审计表，把陈述里的每个量词与形容词（含隐含项）落到路线一（route 1）证明材料的
具体位置，落不上的记 GAP。

本条目的特殊之处：**路线一对 J8 是整体 GAP**。`results/J8/probe_lottery.md`（含不等式 (3)、
(8)–(12)）未送达（`results/V11/MISSING_INPUTS.md` 已记）。仓库里与 J8 有关的全部材料只有三项：
`results/J8/J8_claude_spotcheck.py`（算法的完整实现）、`results/J8/J8_claude_spotcheck_run.log`
（紧实例 3/5 + 1/2048，400 个随机 coverage 实例 0 违反）、`HANDOFF_2026-09-18.md` §4 第 77 行
（速查陈述）。因此 E 表里凡属"不等式怎么得出"的行一律 GAP，只有"算法层面的可核对事实"
（查询次数、查询集合大小、输出集合大小、期望的取法、缩放不变性）能落到具体行号。

范围与纪律：不修改任何已有仓库文件，不运行 git。本文件自身的算术用 `fractions.Fraction`
精确复核，脚本在 scratchpad（未入库），代码片段内联在 §4 以便重跑；浮点只出现在打印里。
状态标签按 CLAUDE.md：[VERIFIED-SYMBOLIC] [VERIFIED-LP] [VERIFIED-EXHAUSTIVE]
[HAND-PROOF-UNREVIEWED] [CONJECTURE] [FAILED]。读过的文件见 §5。

---

## 1. Criterion A：陈述三方比对

### 1.1 三份原文位置

- **矩阵陈述**：`results/V11/statements.md` 第 377 至 391 行（标题行写明"陈述来源
  HANDOFF_2026-09-18 §4；证明文件未送达"），与 `results/V11/inputs/statement_probelottery.md`
  第 6 至 17 行（命题）加第 21 至 38 行（算法五步与查询记账）。两份的命题正文逐字符相同
  （逐行 diff 只差首尾各一个空行，§4 第 5 条）。
- **台账**：`THEOREM_LEDGER.md` **没有 J8 卡**。全文卡号只有 T0 至 T15，且全文检索
  `Probe`、`lottery`、`9n`、`400000`、`2048` 零命中。与 J8 最近的卡是 T10c
  （`thm:linear-exact`，第 290 至 330 行），它的"禁止声称"行不涉及 J8。
- **正文**：`paper/sections/results.tex` **没有 ProbeLottery environment**。全 `paper/` 目录检索
  `Probe`、`lottery` 零命中；`REPORT.md`、`RESEARCH_STATE.md` 同样零命中。正文里与该陈述
  相关的只有 `thm:linear-exact`（第 756 至 789 行）的随机子句和它的空洞性检验注释
  （第 805 行起），以及 `rem:hardness-leak`（第 732 至 745 行）关于 size cap 的说明。

### 1.2 判定

A 项要求"每个量词在两边以相同 scope 出现"。台账侧与正文侧的量词集合都是**空集**，
矩阵侧是一段完整的命题，两个列表不可能重合。

**A_match = false。**

### 1.3 A_diffs（逐条）

decisive（决定 A_match 的两条）：

- **D0 正文缺失**：`paper/sections/results.tex` 无任何 ProbeLottery environment，正文侧没有
  可比对的量词。矩阵陈述若进矩阵，"正文环境"一栏只能填"未入正文"。
- **D1 台账缺失**：`THEOREM_LEDGER.md` 无 J8 卡。按维护规则"任何定理陈述改动，先改本文件
  对应卡，再改 .tex"，J8 目前连第一步都没有。矩阵的"台账卡"一栏只能填 GAP。

矩阵陈述与 `HANDOFF_2026-09-18.md` §4 第 77 行速查陈述的差（这是唯一可做的实质比对）：

- **D2 矩阵新增五项量词**：handoff 只写"$K=2,\eta=3/2$，随机算法，$\le 9n$ 次、$|S|\le5$，
  每个实例 $\mathbb E[F]/\mathrm{OPT}\ge 3/5+1/400000$"。矩阵陈述另加：输出集合大小恰为 2；
  $f$ monotone submodular；$f(\emptyset)=0$；Definition 1 的任意拆分 $\eta_u\eta_o=3/2$
  以及"rescale 后 $d_e(S)\le\tilde d_e(S)\le\frac32 d_e(S)$"；expectation 只对算法自身随机性。
  这五项都是正确方向的补全，但都没有来源文件背书。
- **D3 ground set 下界两边都没有**：矩阵与 handoff 都不写 $n\ge n_0$，连 $n\ge 2K=4$ 都没有。
  算法的形容词 "each on a set of size at most 5" 在 $n<5$ 时仍为真但不可达
  （实测 $n=2$ maxsize 2、$n=3$ maxsize 3、$n\ge5$ maxsize 5，§4 第 2 条）。
- **D4 OPT > 0 两边都没有**：比值 $\mathbb E[f(T)]/\mathrm{OPT}$ 在 $\mathrm{OPT}=0$ 时无定义；
  脚本第 83 行直接相除，未排除该实例类。
- **D5 tie-breaking 方向不一致**：算法描述第 23 行写 "argmax returns the first maximiser"
  （固定顺序），而 `paper/sections/model.tex` 与 `HANDOFF` §8 给 predictive greedy 的约定是
  "breaks ties adversarially"。命题里没有 tie 量词，因此"每个实例"是否对所有 tie-break 顺序
  成立，两边都未陈述。
- **D6 必要性子句把分离全部归给 size cap**：矩阵陈述末句说这证明
  "the query-size restriction $|S|\le K$ of the linear-budget optimality theorem is necessary
  for randomized algorithms with budget $\frac92 nK$"。`thm:linear-exact` 的类
  （`results.tex` 第 761 至 764 行）是"at most $nK$ queries, each on a set of size at most $K$"。
  ProbeLottery 同时放松了两件事：集合大小 $2\to5$，预算 $nK\to 9n=\frac92\,nK$（$K=2$）。
  陈述只归因于前者。
- **D7 必要性子句缺 $n$ 的下界**：`thm:linear-exact` 的随机子句（`results.tex` 第 781 至 789 行）
  只给 $\mathbb E\le\rho_K(\eta)+\varepsilon_n$，$\varepsilon_n=K^2/n+K^5/(2n)$；$K=2$ 时
  $\varepsilon_n=20/n$。要让 $1/400000$ 的超出成为真正的分离，需要 $20/n<1/400000$，即
  $n>8\times10^6$。两边都不写这个量词。[VERIFIED-SYMBOLIC 算术，§4 第 3 条]
- **D8 误差量词的方向**：矩阵写 "error at most $\eta=3/2$"，handoff 写 "$\eta=3/2$"。
  "at most" 隐含结论对更小误差也成立，这个单调性两边都未陈述也未证。
- **D9 命题的常数与算法的常数脱节**：$\mathrm{EPS}=1/10000$、$127/128$、$1/1024$、扩展轮数 4、
  $|B|\le5$ 只出现在算法描述里，命题里只出现 $1/400000$；二者的关系没有出处（不等式
  (3)、(8)–(12) 未送达）。实测紧实例的余量是 $1/2048$，约为 $1/400000$ 的 195 倍
  （$400000/2048=3125/16=195.3125$）。

---

## 2. Criterion E：量词审计表

"where handled" 一栏给文件加行号或可辨识的引用短语。路线一的证明文件缺失，所以只有算法层面
的行能落地；凡是需要不等式的行都记 GAP。

| 量词 / 形容词 | where handled（file + 段落/行号） | status |
|---|---|---|
| "There is a randomized algorithm"（存在量词，算法侧见证） | `results/J8/J8_claude_spotcheck.py` 第 12 至 50 行 `probe_lottery`（五步与输出分布完整） | 已落地（算法存在，保证未证） |
| $K=2$ 固定 | 算法本身硬编码成对输出（第 46 至 48 行的 $P_0$、$\{v,z_v\}$、$\{b,v\}$ 全是 2-集） | 已落地（形式），推广到 $K\ge3$ 是 handoff 第 77 行的 [OPEN] |
| $\eta=3/2$ 固定 | 紧实例 `tight_instance` 第 55 行 `K, eta = 2, R(3, 2)`；随机族第 81 行 `Gs = Fs + Fp/2`（保证 $d_F\le d_G\le\frac32 d_F$） | GAP（只有两族有限实例，没有"为何 3/2"的论证） |
| "error at most $\eta$"：Definition 1 的 band，对所有 $S$ 与 $e\notin S$ 双向 | 无。脚本只构造满足 band 的实例，不显示 band 的全称量词如何进入不等式 | **GAP** |
| 拆分 $(\eta_u,\eta_o)$ 任意，只有乘积 $\eta$ 起作用 | 脚本第 62 行注释 "eta_u = 1, so G = H" 只覆盖一个端点；算法对正缩放不变（我方 600 组比对 0 不一致，§4 第 1 条）故"任意拆分"可化归到该端点 | 部分 GAP（缩放不变性是我方补的，不在任何送达文件里） |
| "at most $9n$ queries" | 脚本第 20 行计数、第 87 行 `assert nq <= 9*n`；`J8_claude_spotcheck_run.log` 四行（$n=6,8,12,20$）；我方在"全平局"实例上 $n=2..39$ 得 queries $=9n-24$（$n\ge10$），§4 第 2 条 | 已落地（有限 $n$ [VERIFIED-EXHAUSTIVE]），一般 $n$ 的书面算术推导 GAP |
| "each on a set of size at most $5$" | 脚本第 21 行 `maxsize` 追踪、第 87 行 `assert ms <= 5`；来源是第 37 行的 4 轮上限（$|B|\le5$） | 已落地 |
| "outputs a set of size $2$" | 脚本第 46 至 48 行分布只含三类 2-集；我方 2000 实例全部 $|T|=2$ | 已落地 [VERIFIED-EXHAUSTIVE 有限] |
| "on every instance $(f,\tilde f)$"（全称量词） | 无。只有 400（原脚本）+ 2000（我方）随机 coverage 实例与一个紧族 | **GAP** |
| $f$ monotone submodular | 无证明。脚本用 weighted coverage（结构上 submodular）与 count-grid 族 | **GAP** |
| $f(\emptyset)=0$（normalization） | 脚本第 79 行 `if S else R(0)`；命题里 normalization 在哪一步被用到无出处 | **GAP** |
| $\mathrm{OPT}>0$（隐含） | 无。脚本第 83 行直接除 OPT，未排除 $\mathrm{OPT}=0$ | **GAP** |
| 结论常数 $3/5+1/400000$ | 无。不等式 (3)、(8)–(12) 未送达；紧实例实测 $3/5+1/2048$（log 四行） | **GAP** |
| "the expectation over the algorithm's own randomness only" | 脚本第 46 至 49 行给出显式分布并 `assert sum(dist.values()) == 1`，第 68、85 行按分布加权求期望（不是采样），故期望在实现层是精确的 | 部分 GAP（"实例先于随机串固定"这一层量词无出处） |
| fixed random string / Yao 方向的量词 | 无。命题只写 expectation，不写固定随机串后的确定性化 | **GAP**（与 D7 的比较需要同一量词顺序） |
| adversarial ties | 无。算法描述第 23 行固定 "first maximiser"；命题不含 tie 量词。我方对紧族随机打乱顺序 22×40 组，最坏仍 $3/5+1/2048$ | **GAP**（有限证据支持，陈述未写） |
| ground set 大小 $n$ 的隐含要求 | 无。命题无 $n$ 下界；pool 与 4 轮扩展在 $n<5$ 时退化（maxsize 随 $n$ 降） | **GAP** |
| $K\ge2$ 要求 | 命题固定 $K=2$，自动满足 | 不适用（本命题无此量词） |
| $\mathrm{EPS}=1/10000$ 的容差及其尺度 | 只在算法描述第 24、28 行；第二个测试用 $\mathrm{EPS}\cdot M$（$M$ 是 singleton 最大值）而不是 $\mathrm{EPS}\cdot p$，尺度不一致，无出处说明 | **GAP** |
| 引用的 $\rho_2(3/2)=3/5$ | `paper/sections/results.tex` 第 191 至 207 行 `thm:exact` 与台账 T6（第 92 至 106 行）；我方按 $V_j$ 公式精确复算 $\min\{V_0,V_1\}=\min\{2/3,3/5\}=3/5$ | 已落地 [VERIFIED-SYMBOLIC 算术] |
| 必要性子句里的 "budget $\frac92 nK$" 与 size cap 的归因 | `results.tex` 第 761 至 764 行给出 $\mathcal A_{\mathrm{lin}}$ 的两个限制；本陈述同时放松两者（D6） | **GAP** |
| 必要性子句与随机子句 $\rho_K+\varepsilon_n$ 的量化比较 | `results.tex` 第 781 至 789 行给 $\varepsilon_n=K^2/n+K^5/(2n)$；$K=2$ 需 $n>8\times10^6$（D7） | **GAP**（陈述里无此 $n$ 下界） |
| 确定性版本、$K\ge3$ | `HANDOFF_2026-09-18.md` 第 77 行明写 [OPEN] | 范围说明，非本命题量词 |

GAP 汇总见 §6 的 gaps 列表。

---

## 3. TASKS11 给本条目附带的两条专项问题

这两条问题的主体分别属于 `thm:ceiling` 与 `thm:linear-exact` 两个条目，本条目按指令一并回答。

### 3.1 `thm:ceiling` 的随机段落是否含 "fixed random string" 量词

**不含。** `paper/sections/results.tex` 的 proposition environment 是第 441 至 463 行；随机内容
不在 environment 内，而是紧随其后的正文散文第 464 至 475 行，原句是
"For every randomized algorithm and $n\ge2K$ there is a fixed pair, again with error exactly
$(\eta_u,\eta_o)$, on which the expectation over the algorithm's randomness satisfies …"。

- 写出来的量词是"实例先固定、期望对算法随机性取"，这是比 Yao 式更强也更干净的顺序。
- "fixed random string"（固定随机串后算法确定性化）这一中间量词没有出现在陈述里。它作为**证明
  步骤**存在：第 480 至 482 行的状态注释把 "the randomized $K/n$ averaging" 标为
  [HAND-PROOF-UNREVIEWED, source J5 batch A]，`app:ceiling`（`appendix_proofs.tex` 第 1211 行起）
  承担该步。
- 结论：陈述层面无需该量词；审计只需记"证明步骤里的固定随机串化未被 oracle 覆盖"。

### 3.2 `app:greedybudget` 的计数链能否把 $n\ge4K^5$ 收紧到约 $K^3(K-1)^2/2+K^2$

**按原文字面：不能，只能到 $K^4(K-1)+2K^2$。补两处（都不改动式子的正确性）之后：能，且阈值
恰好是 $K^3(K-1)^2/2+K^2$。** 不改任何文本，以下只是复算。

计数链原文（`paper/sections/appendix_proofs.tex` 第 1835 至 1856 行，paragraph
"Counting at the budget $Q=nK$."）：

```
Pr[R subset O] = K(K-1)/(n(n-1)) = (K/n)^2 - K(n-K)/(n^2(n-1)) <= (K/n)^2
nK * C(K,2) * (K/n)^2 + Pr[T_0 cap O != empty] <= K^4(K-1)/(2n) + K^2/n <= K^5/(2n) + K^2/n
"Under n >= 4K^5 the first term is at most 1/8 and the second is at most 1/(4K^3) <= 1/32,
 so the total is at most 5/32 < 1/2"
```

(a) 原文字面（放缩到 $(K/n)^2$，并要求失败概率 $<1/2$）：
$\frac{K^4(K-1)}{2n}+\frac{K^2}{n}<\frac12 \iff n>K^4(K-1)+2K^2$。
逐 $K$ 的最小 $n$：$K=2$ 得 25，$K=3$ 得 181，$K=4$ 得 801，$K=5$ 得 2551。
（对照 $4K^5$：128、972、4096、12500。）

(b) 要得到 $K^3(K-1)^2/2+K^2$ 需要两处改动，两处都在原文的推导里已经现成：

1. 保留精确值 $\Pr[R\subseteq O]=\frac{K(K-1)}{n(n-1)}$，不放大到 $(K/n)^2$。原文第 1841 至 1845 行
   已经先算出精确值再放大，所以这一步不需要新论证。每次查询的失败概率变成
   $\binom K2\cdot\frac{K(K-1)}{n(n-1)}=\frac{K^2(K-1)^2}{2n(n-1)}$，乘以 $Q=nK$ 得
   $\frac{K^3(K-1)^2}{2(n-1)}$。
2. 把判据 $<\frac12$ 换成 $<1$。存在性只需坏事件概率小于 1（"some $K$-set $O$ makes every
   canonical query balanced and misses $T_0$"），$\frac12$ 是原文取的余量，不是必需。

此时条件是 $\frac{K^3(K-1)^2}{2(n-1)}+\frac{K^2}{n}<1$，逐 $K$ 精确求最小 $n$
（`fractions.Fraction`，§4 第 4 条）：

| $K$ | $4K^5$（原文） | (a) 原文字面的最小 $n$ | (b) 两处改动后的最小 $n$ | $K^3(K-1)^2/2+K^2$ |
|---|---|---|---|---|
| 2 | 128 | 25 | 9 | 8 |
| 3 | 972 | 181 | 64 | 63 |
| 4 | 4096 | 801 | 305 | 304 |
| 5 | 12500 | 2551 | 1026 | 1025 |
| 6 | 31104 | 6553 | 2737 | 2736 |
| 10 | 400000 | 90201 | 40601 | 40600 |
| 13 | 1485172 | 343071 | 158354 | 158353 |

(b) 列恰为 $\lfloor K^3(K-1)^2/2+K^2\rfloor+1$，$K=2..13$ 全部吻合，即 handoff 第 74 行
"可紧到约 $K^3(K-1)^2/2+K^2$" 的来源就是这两处改动。[VERIFIED-SYMBOLIC 算术]

三条附带说明（写进矩阵时要一起带）：
- 收紧只动计数链。transcript induction（第 1857 行起）、两次平均、count-grid 到集合函数的接线
  仍是 [HAND-PROOF-UNREVIEWED]，收紧不改变它们的状态。
- 第 1877 至 1879 行 "The only property of the budget that the computation uses is
  $Q\le n^2/(4K^4)$, which $Q=nK$ satisfies exactly when $n\ge4K^5$" 这句要跟着改，否则与新阈值
  不一致。
- 随机子句的 $\varepsilon_n=K^2/n+K^5/(2n)$（`results.tex` 第 786 行）用的是同一条放缩，收紧后
  第二项应为 $K^3(K-1)^2/(2n)$ 量级；本审计不改文本，只记录连带处。
- $n\ge2K$ 在上表每个 $K$ 处都被 (b) 列自动满足。

---

## 4. 本文件用到的 oracle 记录（脚本在 scratchpad，未入库）

原脚本 `results/J8/J8_claude_spotcheck.py` 原样复跑，exit 0，输出与
`results/J8/J8_claude_spotcheck_run.log` 逐字符一致（紧实例 $n=6,8,12,20$ 均得
$\mathbb E[F]=6149/10240=3/5+1/2048$，queries $\le 9n$，maxsize 5；400 随机实例 0 违反，
最差比 4/5）。

1. **缩放不变性**（支撑 E 表"任意拆分"行）：对 200 个随机 coverage 实例，把 oracle 乘以
   $7/3$、$1/1000$、$10^6$ 各跑一遍，输出分布与原分布逐键比较，**600 组 0 不一致**。
   [VERIFIED-EXHAUSTIVE 有限]
2. **查询次数与集合大小**（支撑 E 表两行）：取"全平局"modular 实例 $g(S)=|S|$（使 pool $C$ 取到
   全集，扩展轮工作量最大），$n=2..39$：$n\ge10$ 时 queries $=9n-24$，比值最大 $109/13\approx8.385$，
   maxsize 在 $n\ge5$ 时为 5、$n=3$ 时为 3、$n=2$ 时为 2，输出集合大小恒为 2。
   [VERIFIED-EXHAUSTIVE 有限]
3. **D7 的阈值**：$K=2$ 时 $\varepsilon_n=K^2/n+K^5/(2n)=4/n+16/n=20/n$；$20/n<1/400000
   \iff n>8\,000\,000$。[VERIFIED-SYMBOLIC 算术]
4. **§3.2 的阈值表**：
   ```python
   from fractions import Fraction as R
   paper = lambda n,K: R(K**4*(K-1),2*n) + R(K**2,n)          # 原文字面
   exact = lambda n,K: R(n*K)*R(K*(K-1),2)*R(K*(K-1),n*(n-1)) + R(K**2,n)
   def minimal_n(f,K,bound):
       n = 2*K
       while not f(n,K) < bound: n += 1
       return n
   for K in range(2,14):
       print(K, 4*K**5, minimal_n(paper,K,R(1,2)), minimal_n(exact,K,R(1)),
             R(K**3*(K-1)**2,2)+K**2)
   ```
   [VERIFIED-SYMBOLIC 算术]
5. **两份陈述文本比对**：`statements.md` 第 379 至 391 行与
   `inputs/statement_probelottery.md` 第 6 至 18 行逐行 diff，只差首尾各一个空行。
6. **红队（补充有限证据，不构成验证）**：2000 个随机 coverage 实例（$n=3..10$，随机 tie-break
   顺序，$\mathrm{OPT}=0$ 跳过），0 违反 $3/5+1/400000$，最差比 $74/83\approx0.8916$；
   紧族 $n=4..25$ 各 40 次随机打乱 tie-break 顺序，最坏仍为 $3/5+1/2048$。
   [VERIFIED-EXHAUSTIVE 有限]。有限测试只能证伪，不能确立一般结论。

---

## 5. 读过的文件

- `results/V11/statements.md`（第 377 至 391 行）
- `results/V11/inputs/statement_probelottery.md`
- `results/V11/MISSING_INPUTS.md`
- `THEOREM_LEDGER.md`（全文检索 + T6、T10c、T10d、T12 各卡）
- `paper/sections/results.tex`（第 441 至 500 行、第 694 至 830 行、第 884 行起；全文检索 Probe/lottery）
- `paper/sections/appendix_proofs.tex`（第 1703 至 1890 行 `app:greedybudget`；label 索引）
- `results/J8/J8_claude_spotcheck.py`、`results/J8/J8_claude_spotcheck_run.log`
- `HANDOFF_2026-09-18.md`（§3、§4 第 77 行、§8）、`HANDOFF_ADDENDUM_2026-09-18.md`（§B）
- `CLAUDE.md`

---

## 6. 结论与 GAP 清单

- **A_match = false**，决定性原因是台账无 J8 卡、正文无 J8 environment（D0、D1）。
  其余七条（D2 至 D9）是矩阵陈述与 handoff 速查陈述之间的差，其中 D6、D7 是实质性的：
  必要性子句把分离归因于 size cap 一项，而算法同时把预算放大 4.5 倍，并且与
  `thm:linear-exact` 随机子句的分离只在 $n>8\times10^6$ 时成立。
- **路线一整体 GAP**：证明文件未送达，E 表里 12 行记 GAP。可落地的只有算法层面的五项事实
  （存在性见证、$\le9n$ 次、$|S|\le5$、输出大小 2、期望按显式分布取）加一项引用
  （$\rho_2(3/2)=3/5$）。
- 整条结果的状态建议维持 [HAND-PROOF-UNREVIEWED]，并在矩阵里注明"证明文件未送达，
  只有实现与有限实例证据"。不写 proved / we show。

# ROUTE-COMPARISON：prop:necessity / prop:nobound（TASKS11 Q1，criterion B，ledger T1）

判定：**B-PASS**。两条路线到达同一结论；route two 的每一条数值断言经本判官用 exact arithmetic 独立复算后成立，未发现未修正的错误；route two 也没有与 route one 的任何步骤相冲突的断言。

本文件的所有复核脚本：`/tmp/claude-0/-home-user/09d7d9a5-0b14-54a1-894a-d76a6d641333/scratchpad/judge_nobound.py`（fractions.Fraction + sympy，浮点只出现在打印里）。另外重跑了 route two 自带脚本 `/home/user/sub-modular-optimization/results/V11/route2/verify_nobound.py`，结尾打印 `ALL CHECKS PASS (exact arithmetic).`，exit 0。

---

## 0. 被比对的三份材料

| 代号 | 文件 | 构造 | 覆盖范围 | 是否进入编译 |
|---|---|---|---|---|
| 甲1 | `/home/user/sub-modular-optimization/paper/sections/appendix_proofs.tex`，subsection `app:necessity`（第 80 行起） | $\gamma=\dfrac{K^2}{n(n-K)}$，$\tilde f(S)=|S|$，$f_O(S)=|S\cap O|+\gamma|S\setminus O|$ | deterministic **与** randomized，一个 $\gamma$ 统一两种情形 | 是（`paper/main.tex:108` 有 `\input{sections/appendix_proofs}`） |
| 甲2 | `/home/user/sub-modular-optimization/paper/sections/appendix_model_proofs.tex`，subsection `prop:nobound`（第 6 行起，2026-09-18 交付） | $\delta=\dfrac{K}{n-K}$，$\tilde f(S)=|S|$，$f(S)=|S\cap O|+\delta|S\setminus O|$ | 仅 deterministic，外加 remark：任意 $\delta\in(0,1]$ 均可，故退化速度至少 $1/\eta$ | 否（unwired；仓库内与上传件 byte-identical，已 diff 确认） |
| 乙 | `/home/user/sub-modular-optimization/results/V11/route2/nobound.md` | 主构造 $w=\dfrac{K}{n-K}$（= 甲2 的 $\delta$）；randomized 节改取 $\epsilon=\dfrac{K^2}{n(n-K)}$（= 甲1 的 $\gamma$） | deterministic + randomized + 任意 $\epsilon$ 的推广 + predictive greedy 特化 | 不适用 |

关键观察：route one 本身就是**两个互不相同的构造**，ledger 与 HANDOFF_ADDENDUM 第 40 行已记录"要与台账 T1 的构造对齐，二者只留一个"。route two 并非第三条路线，它**恰好是甲1 与甲2 的并集**：deterministic 段逐字对应甲2，randomized 段逐字对应甲1，并额外给出把两者串起来的单参数族 $\epsilon\in(0,1]$（甲2 的 remark 给出同一族，但未把 randomized 取值代进去）。

---

## 1. 步骤对应表（route two 的每一步 → route one）

| 乙 的步骤 | 乙的内容 | 甲中的对应 | 对应关系 | 本判官复核 |
|---|---|---|---|---|
| Step 1 | $f_A(S)=|S\cap A|+w|S\setminus A|$ 是 nonnegative modular，$f(\emptyset)=0$，monotone（$d_e=w_e>0$），submodular（DR 取等号） | 甲2 第 15 行 "The function $f$ is modular, hence normalized, monotone and submodular"；甲1 "$f_O$ is modular with coefficients in $\{1,\gamma\}\subseteq(0,1]$, so it is monotone and submodular" | 完全一致，只有 $w$ 与 $\gamma$ 的取值不同 | 全格点逐对 DR 检查，$K\le3$、$2K\le n\le8$ 全部通过 [VERIFIED-EXHAUSTIVE]（judge C-A） |
| Step 2 | $\tilde f(S)=|S|$，$\tilde f(\emptyset)=0$；附带说明它本身也是 monotone modular | 甲2 第 9 行 "Let the surrogate be the modular function $\tilde f(S)=|S|$. It is normalized and can be evaluated on any set."；甲1 同式 | 一致。乙多写了"即便额外要求 predictor 为 monotone submodular 构造仍成立"这一句，甲两版都没写 | [VERIFIED-EXHAUSTIVE]（judge C-A） |
| Step 3 | Definition 1 的 support 条件：$\tilde d_e=1>0$ 且 $d_e=w_e>0$，两侧都不为零 | 甲1、甲2 均未单独写这一步（甲2 直接跳到 $\eta_u,\eta_o$） | 乙**多出一步**（补全 Definition 1 的 "forces $\tilde d_e=0$ exactly when $d_e=0$" 这一条款的检查）。不是分歧，是 route two 更细 | [VERIFIED-EXHAUSTIVE]（judge C-A） |
| Step 4 | $\eta_u\ge\max_e w_e=1$，$\eta_o\ge 1/w$；最小取法 $(1,\frac{n-K}{K})$，$\eta=\frac{n-K}{K}$ | 甲2 第 15 行："Definition~\ref{def:eta} holds with $\eta_u=1$ and $\eta_o=1/\delta$, that is, with the finite error $\eta=1/\delta=(n-K)/K$" | 逐字一致 | 全格点重算 $\max_{S,e}d/\tilde d$ 与 $\max_{S,e}\tilde d/d$，得 $(1,(n-K)/K)$ [VERIFIED-EXHAUSTIVE]（judge C-A） |
| Step 5 | $f_A$ modular 且 $w\le1$，故 $O^\ast=A$、$F^{\mathrm{OPT}}=K>0$；并注明 $f(O^\ast)>0$ 使 `assumptions.md` 的平凡旁路不触发 | 甲1："$\max_{|S|\le K}f_O(S)=f_O(O)=K$, because $\gamma\le1$ makes the $K$ largest modular coefficients exactly those of $O$"；甲2："$\mathrm{OPT}\ge f(O)=K$" | 一致。乙比甲1 更严谨一点：$n=2K$ 时 $w=1$，所有 $K$-set 同为最优，甲1 的"exactly those of $O$"在 $\gamma=1$ 时会失准（对甲1 的 $\gamma$ 而言 $\gamma<1$ 恒成立，故甲1 无实际问题） | [VERIFIED-EXHAUSTIVE]（judge C-A，逐 instance 用 top-$K$ 权重重算 OPT） |
| Step 6 | family 共用一个 $\tilde f$、算法不能 query $f$、deterministic，归纳得 transcript 与 $A$ 无关 | 甲2 第 9 行："Its values do not depend on $f$, so every answer the algorithm receives is determined before $f$ is chosen"；甲1："$\tilde f$ does not depend on $O$, so the whole query transcript of $\mathcal A$ ... are the same for every $O$" | 同一论证，同样只有手写归纳 | 无 oracle 可查（计算模型断言）[HAND-PROOF-UNREVIEWED]，两条路线状态相同 |
| Step 7 | 输出是一个与 $A$ 无关的固定集合 $T$，$|T|\le K$ | 甲2："hence the output $T$, with $|T|\le K$, is a fixed set determined by the algorithm alone"；甲1："its output $T$ with $|T|\le K$" | 逐字一致，**包括 $|T|\le K$ 这一条**。乙把它标为"额外加入的假设"，但甲两版同样在 statement 文本之外补了这一条，所以这不是乙独有的加项 | 同上 |
| Step 8 | $|N\setminus T|\ge n-K\ge K$，取 $A\subseteq N\setminus T$，$|A|=K$；$n\ge2K$ 只在此处用到 | 甲2："Choose a set $O\subseteq N\setminus T$ with $|O|=K$, which exists because $n\ge2K$"；甲1："Since $n\ge2K$ and $|T|\le K$, a $K$-set $O\subseteq N\setminus T$ exists" | 一致。乙额外断言"这是 $n\ge2K$ 唯一被用到的地方"，甲1 的 LaTeX 注释与之相左，见第 4 节分歧 D3 | [VERIFIED-EXHAUSTIVE]（judge C-A：$\max_T\min_A$ 的最优 $A$ 正是不交的那个） |
| Step 9 | $f_A(T)=w|T|\le wK=\frac{K^2}{n-K}$ | 甲2 第 17 行："$f(T)=\delta|T|\le\delta K$" | 逐字一致 | [VERIFIED-EXHAUSTIVE]（judge C-A） |
| Step 10 | $f_A(T)\le\frac{K}{n-K}f_A(O^\ast)$，$\eta=\frac{n-K}{K}$ | 甲2："Hence $f(T)\le\delta\cdot\mathrm{OPT}=\tfrac{K}{n-K}\cdot\mathrm{OPT}$" | 逐字一致（等号可取）。甲1 走另一条：$\frac{\gamma|T|}{K}\le\gamma=\frac{K^2}{n(n-K)}\le\frac{K}{n-K}$，结论**更强**（差一个因子 $K/n$），但所用 $\eta$ 也更大 | $\max_{|T|\le K}\min_A$ 精确等于 $\frac{K}{n-K}$，$K\le3$、$2K\le n\le8$ 全格点 [VERIFIED-EXHAUSTIVE]；甲1 的 $\gamma\le K/(n-K)$ 等价于 $K/n\le1$，全参数成立 [VERIFIED-SYMBOLIC]（judge C-B） |
| Step 11 | 固定 $K$ 取 $n>K+K/\alpha$ 得 $\frac{K}{n-K}<\alpha$，故无常数 worst-case ratio | 甲2 的 remark 第 21 行（任意 $\delta$ 版）；甲1 段末 "Letting $n\to\infty$ with $K$ fixed drives the right side to $0$" | 一致。甲2 的 remark 走的是 $\delta\to0$，乙走的是 $n\to\infty$，两者都能得出该句，且乙第 4 节把 $\delta\to0$ 版本也写了 | 纯逻辑，无 oracle [HAND-PROOF-UNREVIEWED]，两路线同状态 |
| Step 11' | 特化为 predictive greedy：$\tilde d$ 全部并列，adversarial tie breaking 把 $K$ 步全放在 $N\setminus A$，$\eta^{\mathrm{sel}}=1/w=\frac{n-K}{K}$ | **甲中没有对应步骤**（甲1、甲2 对本命题都不提 greedy、不提 tie breaking） | route two 独有（different route，理由：本命题针对 arbitrary deterministic algorithm，greedy 只是其中一个实例，甲选择不写这条特化） | $M_t=1$、$g_t=w$、$a_t=1/w$ 由 modular 结构直接给出；乙未写独立脚本 [HAND-PROOF-UNREVIEWED]，本判官照手算核对通过（$w=2/3$ 时 $a_t=3/2$），但同样不升级状态标签 |
| §4 推广 | $w\to\epsilon\in(0,1]$ 得 ratio $\le\epsilon$、$\eta=1/\epsilon$；$\frac{K}{n-K}$ 是使 $A$ 外总质量 $=f(O^\ast)$ 的平衡取法，满足 ratio $=1/\eta$ | 甲2 的 remark 第 21 行："The same construction with any $\delta\in(0,1]$ gives $f(T)\le\delta\cdot\mathrm{OPT}$ with $\eta=1/\delta$ ... the guarantee of every algorithm degrades at least as fast as $1/\eta$" | 逐字一致 | $\epsilon=w$ 的情形 [VERIFIED-EXHAUSTIVE]；一般 $\epsilon$ 同型代数 [HAND-PROOF-UNREVIEWED]，两路线同状态 |
| §5 误差表 | 三行 $(\eta_u,\eta_o)$：主构造 $(1,\frac{n-K}{K})$；任意小比值版 $(1,1/\epsilon)$；randomized 版 $(1,\frac{n(n-K)}{K^2})$ | 甲2 给第一行；甲1 给第三行（$\eta=1/\gamma=n(n-K)/K^2$） | 三行合起来恰好覆盖甲1 与甲2 各自的取值，没有第四个取值 | 三行全部重算 [VERIFIED-EXHAUSTIVE]（judge C-A、C-B） |
| §6 randomized | $T$ 与均匀随机的 $A$ 独立；取 $\epsilon=\frac{K^2}{n(n-K)}$，$\mathbb E[f(T)]/K\le\frac Kn+\epsilon=\frac{K}{n-K}$；平均值论证给出固定 pair；$\eta$ 升到 $\frac{n(n-K)}{K^2}$ | 甲1 的 "Randomized algorithms" 段：hypergeometric mean $\mathbb E|T\cap O|=\mathbb E|T|\cdot K/n\le K^2/n$，$f_O(T)\le|T\cap O|+\gamma K$，同一恒等式链，$\min_O\le\mathbb E_O$ | **逐字一致**，连恒等式 $\frac Kn+\frac{K^2}{n(n-K)}=\frac{K}{n-K}$ 都相同 | 恒等式 [VERIFIED-SYMBOLIC]（judge C-D：sympy simplify 得 0）；$K\le3$、$2K\le n\le8$ 的 $\max_T\mathrm{avg}_A$ 全部 $\le\frac{K}{n-K}$ [VERIFIED-EXHAUSTIVE]（judge C-E + route two 脚本 C3） |
| §6 尾段 | 任何 randomized 算法在该 family 上至少拿到 $\frac Kn$，故真实量级 $\Theta(K/n)$，与 $\frac{K}{n-K}$ 相差 $\le2$ 倍 | **甲中没有**（甲1 只给上界，不讨论该 family 上的 randomized 下界） | route two 独有（是对甲1 界的紧性讨论，不是反驳） | $\frac{K}{n-K}\le\frac{2K}{n}\iff n\ge2K$ [VERIFIED-EXHAUSTIVE]（judge C-I，$K\le3$、$n\le8$）；下界 $\mathbb E\ge K^2/n$ 由 $\mathbb E|T\cap A|=K^2/n$ 直接给出 [HAND-PROOF-UNREVIEWED] |
| §7.1 走查 | $\eta=3/2$（$w=2/3$）时该 instance 证成界当且仅当 $n\le7.5$，故 $n\in\{6,7\}$ | 甲中无数值走查 | route two 独有 | $2/3\le 3/(n-3)\iff n\le7.5$；逐 $n$ 复算 $n=6,7$ True、$n=8,9$ False [VERIFIED-EXHAUSTIVE]（judge C-F，与 route two 脚本 C4 一致） |
| §7.2 表 | $\max_{|T|\le K}\min_A$ 的精确值逐格等于 $\frac{K}{n-K}$（6 格） | 甲中无 | route two 独有（说明甲2 的界是被等号达到的，不是宽松估计） | 6 格全部复算命中，另补齐 $K\le3$、$2K\le n\le8$ 共 15 格 [VERIFIED-EXHAUSTIVE]（judge C-A） |
| §7.3 走查 | $n=8,K=3$：$\epsilon=9/40$，$\eta=40/9$，精确最坏 $\mathrm{avg}_A=33/64$，粗放上界 $\frac Kn+\epsilon=\frac35$ 正好等于界 | 甲中无数值走查 | route two 独有 | 精确重算得 $33/64$，$33/64\le3/5$，$\frac38+\frac9{40}=\frac35$ [VERIFIED-EXHAUSTIVE]（judge C-E） |
| §7.4 ProbeLottery | 未执行，记 [FAILED]（输入包中无定义），以 $K=2$ 精确穷举替代 | 不适用 | 见第 5 节 gap G4 | $K=2$、$n=4..8$ 的比值 $1,\frac23,\frac12,\frac25,\frac13$ 逐个复算命中 [VERIFIED-EXHAUSTIVE]（judge C-A） |
| §8 $n<2K$ | 任意 $|T|=K$、$|A|=K$ 必有 $|T\cap A|\ge2K-n$，故 ratio $\ge\frac{2K-n}{K}>0$，构造失效 | 甲中无（甲只声明 $n\ge2K$ 时存在不交的 $O$，不讨论反向） | route two 独有（空洞性检验条目） | $2\le K\le4$、$K\le n<2K$ 逐格复算，$\max_T\min_A\ge\frac{2K-n}{K}$ 全部成立 [VERIFIED-EXHAUSTIVE]（judge C-H） |

### 1b. Route one 有而 route two 未覆盖的步骤

| 甲的步骤 | 出处 | route two 是否覆盖 | 说明 |
|---|---|---|---|
| $\gamma\le1$ 的论证 "$n\ge2K$ gives $n(n-K)\ge2K\cdot K>K^2$" | 甲1 | 未逐字覆盖 | 乙对自己的 $w=K/(n-K)$ 证 $w\le1$（由 $n-K\ge K$），是同一件事的另一个取值。本判官复核：甲1 的蕴含方向正确（充分），$K\ge1$ 时 $2K^2>K^2$ [VERIFIED-SYMBOLIC] |
| 附录级约定 "instances are normalized so that $f(O^\ast)=1$ whenever a ratio is computed" | 甲1 文件头（第 48 行附近） | 未覆盖 | 乙不做归一化，直接用 $f(O^\ast)=K$。两者等价（比值不变），但归一化约定只在甲1 出现 |
| $\mathrm{OPT}\ge f(O)=K$（用 $\ge$ 而非 $=$） | 甲2 第 17 行 | 乙用 $O^\ast=A$、$f(O^\ast)=K$（等号） | 甲2 的 $\ge$ 对结论足够（$\delta>0$），乙的等号更强且已被穷举确认，无冲突 |
| 与 `thm:ceiling` 的衔接句 "Proposition~\ref{thm:ceiling} shows that this rate is exact" | 甲2 remark | 未覆盖（乙 §9 第 8 条明确声明不做任何与 $\rho_K,L_K,U_K$ 的比较） | STRICT ISOLATION 的直接后果，不是缺陷 |
| results.tex 第 32-37 行注释：随机版"no constant is derived here and none is claimed (ledger T1)" | route one 的正文注释 | 乙 §6 给出了常数 | 见第 4 节分歧 D4（这是 route one 内部的不一致，乙站在甲1 一边） |

---

## 2. 结论是否相同

相同。两条路线都到达

$$f(T)\;\le\;\frac{K}{n-K}\,f(O^{\ast}),$$

对每一个 deterministic algorithm、每一个 $n\ge2K$，由 adversary 在看到 $T$ 之后选取的 pair $(f,\tilde f)$ 上成立，且该 pair 的 $\eta$ 有限但随 $n$ 无界，由此推出第二句"无常数 worst-case ratio"。

两条路线还都给出了 randomized 版本（乙 §6 与甲1 的 randomized 段），常数相同、$\eta$ 相同、论证步骤相同。

---

## 3. 量词比对

### 3.1 一致的量词（load-bearing，逐条命中）

| 量词 | 乙 | 甲1 | 甲2 |
|---|---|---|---|
| 整数 $K\ge1$、整数 $n\ge2K$ 预先固定 | Q1 | "Fix $K\ge1$ and $n\ge2K$" | "Fix ... $n\ge2K$" |
| $\forall$ deterministic algorithm | Q2 | 有（"Deterministic algorithms" 段） | "Fix a deterministic algorithm" |
| arbitrary query access to $\tilde f$，不能 query $f$ | Q3 | "arbitrary query access to $\tilde f$" | 同（"can be evaluated on any set"，$f$ 不可 query） |
| 输出可行性 $|T|\le K$ | Q4 | "its output $T$ with $|T|\le K$" | "the output $T$, with $|T|\le K$" |
| $\exists$ pair：$f$ monotone submodular、$f(\emptyset)=0$、$\tilde f(\emptyset)=0$、满足 Definition 1、$\eta$ 有限且无预设上界 | Q5 | "The pair is admissible and has finite error" | "satisfies every assumption of Section~\ref{sec:model}; only the value of $\eta$ is dictated by the adversary" |
| 结论式与 $f(O^\ast)=K>0$ | Q6 | 有 | 有 |
| 次序 $\forall\mathcal A\ \forall(n,K)\ \exists(f,\tilde f)$，instance 在算法之后选 | Q7 次序段 | 有（$O$ 在 $T$ 之后选） | 有 |
| randomized：$T$ 与 $O$ 独立、对内部随机性取期望、存在固定 pair | 有（§6） | 有（randomized 段） | 无 |

### 3.2 只在一边出现的量词（quantifier_match = false 的全部理由）

1. **[只在乙] tie breaking / predictive greedy 特化（乙 Q8 与 Step 11'）**：乙声明"若把 $\mathcal A$ 特化为 predictive greedy，则本构造需要 adversarial tie breaking，此时 $\eta^{\mathrm{sel}}=(n-K)/K$"。甲1、甲2 对本命题完全不提 greedy、不提 tie breaking。这是乙多出来的限定词，不影响主结论（主结论对 arbitrary deterministic algorithm 成立，greedy 只是其中之一）。
2. **[只在乙] convention B 的参数域（乙 Q7）**：乙显式写 $\eta_u,\eta_o>0$、$\eta=\eta_u\eta_o\ge1$（convention B）。甲1、甲2 只给出具体取值 $(\eta_u,\eta_o)=(1,1/\gamma)$ 或 $(1,1/\delta)$，不写参数域。注意两个构造给出的 $\eta_u=1$ 同时满足 verbatim Definition 1 的 $\eta_u,\eta_o\ge1$ 与 convention B 的 $\eta_u,\eta_o>0$，所以这条差异不改变任何一条结论的适用范围。
3. **[只在乙] arbitrary query access 的最强解释显式化（乙 Q3 的括注）**：乙写明"可读完整张值表、免费知道 $n,K$ 与 family 描述"。甲1、甲2 只写 "arbitrary query access"，其 transcript 论证隐含同一解释。这是显式化，不是加强或削弱。
4. **[只在甲1] 附录级归一化约定 $f(O^\ast)=1$**：乙不归一化。比值层面等价。
5. **[只在甲1] randomized 量词**；**[只在甲2] 无 randomized**：route one 的两个文件彼此在这一条上不一致，乙与甲1 一致。

因此：主命题的全部 load-bearing 量词两边逐条命中；`quantifier_match` 之所以记 false，只因为上面 5 条辅助限定词在两边的出现情况不同，没有一条会改变结论或其适用范围。

---

## 4. 分歧清单（divergences）

**D1（构造常数不同，route one 内部即有分歧）**：甲1 用 $\gamma=K^2/(n(n-K))$，甲2 用 $\delta=K/(n-K)$，乙的 deterministic 段取 $\delta$、randomized 段取 $\gamma$。三者都到达 statement 的界。差别在于同一 family 里的自由参数取值：甲1 的 deterministic 结论更强（比值 $\gamma=\frac Kn\cdot\frac{K}{n-K}$，比 statement 的界小一个因子 $K/n$），代价是所需 $\eta=n(n-K)/K^2$ 更大；甲2 与乙的 deterministic 取法把界**等号**达到，所需 $\eta=(n-K)/K$ 是该 family 中能证成该界的最小值。复核：$\gamma\le K/(n-K)\iff K/n\le1$，全参数成立 [VERIFIED-SYMBOLIC]；$\max_{|T|\le K}\min_A$ 在 $\delta$ 取法下精确等于 $K/(n-K)$，$K\le3$、$2K\le n\le8$ 全格点 [VERIFIED-EXHAUSTIVE]（judge C-A、C-B）。**这不是矛盾**，是同一 family 的两个参数点，乙 §4 已把两者统一进 $\epsilon\in(0,1]$ 的单参数族。HANDOFF_ADDENDUM 第 40 行已要求"二者只留一个"，本比对不改变该要求，只补一句：若只留一个，留甲2/乙的 $\delta$ 取法会使 deterministic 陈述的 $\eta$ 最小，但 randomized 段仍必须用 $\gamma$，因此两个常数在同一个证明里是各司其职的，甲1 用一个 $\gamma$ 统一两段的写法在 deterministic 侧是宽松的。

**D2（$\eta$ 的取值随之不同）**：同一个 statement 的界，甲1 的 instance 有 $\eta=n(n-K)/K^2$，甲2 与乙的 instance 有 $\eta=(n-K)/K$。若正文要引用"证成该界所需的误差"，两个数字不可混用。[VERIFIED-EXHAUSTIVE]（judge C-A、C-B）。

**D3（$n\ge2K$ 的作用，甲1 的注释与乙冲突）**：甲1 第 138 行附近的 LaTeX 注释写 "n >= 2K is exactly what makes gamma <= 1, which is what keeps O optimal"。乙 §8 断言 $n\ge2K$ 唯一被用到的地方是 Step 8（存在与 $T$ 不交的 $A$）。本判官复核支持乙：$\gamma\le1$ 等价于 $n(n-K)\ge K^2$，即 $n\ge K(1+\sqrt5)/2\approx1.618K$，**严格弱于** $n\ge2K$；显式反例（精确有理算术）$K=3,n=5<6=2K$ 时 $\gamma=9/10\le1$，$K=4,n=7$ 时 $\gamma=16/21\le1$，$K=5,n=9$ 时 $\gamma=25/36\le1$ [VERIFIED-EXHAUSTIVE + VERIFIED-SYMBOLIC]（judge C-C）。所以甲1 注释里的 "exactly" 说法不成立：$n\ge2K$ 对 $\gamma\le1$ 是充分不必要，它在证明里真正不可替代的作用是 Step 8 的不交性。甲1 的**可见正文**只写 "where $\gamma\le1$ because $n\ge2K$ gives $n(n-K)\ge2K\cdot K>K^2$"，这是一个正确的充分性蕴含，不受影响；出问题的只是那条注释。建议修正该注释，不需要动正文。

**D4（randomized 常数的 route one 内部不一致）**：`paper/sections/results.tex` 第 32-37 行的注释与 ledger T1 都写"随机版 ... 本文未给常数，不声称"，但甲1 的 randomized 段**已经给出常数** $K/(n-K)$，并给了完整的 hypergeometric + averaging 论证。乙 §6 与甲1 一致（同常数、同 $\eta$、同论证）。这是 route one 内部三处（results.tex 注释 / ledger T1 / appendix_proofs.tex 正文）的口径不一致，需要人类裁决：要么把 ledger T1 与 results.tex 注释更新为"随机版常数 $K/(n-K)$，$\eta=n(n-K)/K^2$，见 app:necessity"，要么把甲1 的 randomized 段降级为 remark。恒等式本身 [VERIFIED-SYMBOLIC]（judge C-D）。

**D5（label 不一致）**：同一命题在 `results.tex`/`appendix_proofs.tex` 里叫 `prop:necessity`，在 `appendix_model_proofs.tex` 里叫 `prop:nobound`，ledger 卡叫 T1 prop:nobound。`appendix_model_proofs.tex` 未被 `main.tex` `\input`，所以目前不产生编译错误；一旦接入，`\ref{prop:nobound}` 会成为 undefined reference。这是文档工程层面的分歧，不是数学分歧。

**D6（乙内部的一处方向性笔误，非载荷）**：乙 Step 4 的括注写 "把 $\tilde f$ 乘以 $c>0$ 得 $(\eta_u,\eta_o)\to(c\eta_u,\eta_o/c)$"，随后举例 "$\tilde f(S)=\sqrt w|S|$ 得 $\eta_u=\eta_o=\sqrt{(n-K)/K}$"。这两句彼此不相容：从定义 $d_e/\eta_u\le\tilde d_e\le\eta_o d_e$ 出发，$\tilde f\to c\tilde f$ 的正确映射是 $(\eta_u,\eta_o)\to(\eta_u/c,\,c\eta_o)$。复核（$K=3,n=7$，$w=3/4$，$c=\sqrt w$）：从头重算得 $(\eta_u,\eta_o)=(2\sqrt3/3,2\sqrt3/3)$，正确映射给出同值，乙引用的映射给出 $(\sqrt3/2,\,8\sqrt3/9)$，不匹配；两种写法的乘积都等于 $4/3$ [VERIFIED-SYMBOLIC]（judge C-G）。**归属**：该映射式是乙从输入包 `results/V11/inputs/definition1.md` 的 convention B 段逐字抄来的（该段又来自 HANDOFF_2026-09-18 第 3 节），所以这是输入文件里的方向性笔误，乙照抄且自己的举例用的是正确方向。由于命题只用到 $\eta=\eta_u\eta_o$ 的不变性，而不变性两种写法都成立，这条不影响任何结论。建议顺手修 `definition1.md` 与 HANDOFF 第 3 节的该句（本判官不修改任何既有文件）。

---

## 5. Route two 的 gap 与加入的假设（route2_gaps）

**G1（模型层手写步骤）**：Step 6-7，"deterministic + arbitrary query access $\Rightarrow$ transcript 与 $A$ 无关、输出是固定集合"。[HAND-PROOF-UNREVIEWED]，无 oracle 可直接检验。**route one 有完全相同的 gap**（甲1、甲2 用的是同一句话），所以这不是 route two 相对 route one 的缺口。乙的缓解措施有效：Step 8-10 与全部脚本对一切 $|T|\le K$ 取全称，故任何"输出是一个 $|T|\le K$ 的、与 $A$ 无关的集合"的形式化都落在已检查范围内。

**G2（加入的假设：$|T|\le K$）**：statement 原文只写 "the output $T$"。乙按 `assumptions.md` 的 cardinality budget 补上 $|T|\le K$，并指出若允许 $|T|>K$ 则命题字面不成立（取 $T=N$）。**route one 的两个文件同样补了这一条**（甲2："the output $T$, with $|T|\le K$"；甲1："its output $T$ with $|T|\le K$"），所以这是 statement 文本的缺项，不是 route two 独有的加项。建议在 `results.tex` 的命题里补一句"输出满足 $|T|\le K$"，否则三份材料都在证一个比字面更强的读法。

**G3（参数范围）**：乙的穷举只覆盖 $K\le3$、$2K\le n\le8$（randomized 同）。一般 $(n,K)$ 的 Step 4/9/10 与 §6 不等式链是手写单行代数 [HAND-PROOF-UNREVIEWED]。本判官在同一范围内独立重算全部命中，另用 sympy 对 $\frac Kn+\frac{K^2}{n(n-K)}=\frac{K}{n-K}$ 与 $\gamma\le K/(n-K)$ 做了全参数符号确认 [VERIFIED-SYMBOLIC]，把 §6 的关键恒等式与 D1 的比较从有限参数升级为全参数。剩余仍为有限参数的：Step 4 的 $(\eta_u,\eta_o)$ 最小取法、Step 10 的等号可达性。

**G4（ProbeLottery $K=2$ 小项未执行）**：[FAILED]，原因是输入包四个文件中没有 ProbeLottery 的定义，STRICT ISOLATION 禁止外查。本判官确认：`results/V11/inputs/` 下确有 `statement_probelottery.md`，但它不在 route two 被允许阅读的四个文件（`definition1.md`、`assumptions.md`、`notation.md`、`statement_nobound.md`）之内，而且 ProbeLottery 与 prop:nobound 无逻辑关系（它属于 J8 那条线）。乙的处理（跳过 + 记录 + 用 $K=2$ 精确穷举替代）是保守且正确的选择，该 [FAILED] 不构成 prop:nobound 的缺口。

**G5（Step 11' 无独立脚本）**：$\eta^{\mathrm{sel}}=(n-K)/K$ 为手算，[HAND-PROOF-UNREVIEWED]。本判官按 `def:etasel` 复核 $M_t=1$、$g_t=w$、$a_t=1/w$ 通过，但按 CLAUDE.md 不升级标签。该项是 route two 独有的附加内容，route one 不含，因此它既不是缺口也不是分歧，只是未被 oracle 覆盖的增量。

**G6（$n<2K$ 的一般下界未做）**：乙只证明本构造在 $n<2K$ 失效（[VERIFIED-EXHAUSTIVE]），不对"是否存在好算法"作任何断言，记为 open。route one 同样不涉及。

**未发现的项**：没有发现 route two 的任何计算错误、任何与 route one 相冲突的断言，也没有发现 route two 对 route one 任一步骤的反驳。D6 是唯一的笔误，其来源在输入文件，且不载荷。

---

## 6. 判定

- **结论一致性**：是。两条路线同结论、同界、同 $\eta$ 的量级解释；randomized 段逐字同构。
- **route two 是否有加入的假设 / gap / 错误**：有一条加入的假设（$|T|\le K$，但 route one 同样加），三条 [HAND-PROOF-UNREVIEWED]（G1、G3 剩余项、G5），一条 [FAILED] 小项（G4，与本命题无关），一条非载荷笔误（D6，源自输入文件）。没有影响结论的错误。
- **route one 是否有被 route two 反驳的步骤**：可见正文没有。被反驳的是甲1 的一条 LaTeX **注释**（D3，"$n\ge2K$ is exactly what makes $\gamma\le1$"），本判官用精确有理反例确认该注释不成立。另有 route one 内部的口径不一致 D4、label 不一致 D5，需要人类裁决，但都不是数学错误。
- **verdict：B-PASS**（route two 与 route one 的同一条路线，deterministic 段 = 甲2，randomized 段 = 甲1，全部数值断言经独立 exact arithmetic 复核通过）。

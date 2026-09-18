# ROUTE-COMPARISON 裁定：prop:valueacc（ledger T2，convention B，2026-09-18 重写版）

TASKS11 Q2，criterion B。本文件比对 route one（仓库证明）与 route two（盲证 `results/V11/route2/valueacc.md`），
给出逐步对应表、判定、分歧清单与 route-two 未闭合项。本次只新建了
`results/V11/compare/valueacc.md` 与 `results/V11/compare/judge_valueacc_checks.py`，没有修改任何既有文件，没有运行 git。

**判定：B-PASS**（同一结论、同一常数；route two 无未修正的错误；量词清单不一致但差异全部指向 route one 更弱）。

裁定方自己的复核脚本（独立于 route two 的脚本重写，只用 `fractions.Fraction` 与 `sympy`，float 只出现在 printout）：

```
python3 results/V11/compare/judge_valueacc_checks.py     # 120+ 项，TOTAL FAILURES: 0
python3 results/V11/route2/verify_valueacc.py            # route two 自带脚本，passed: 122  failed: 0
```

---

## 0. 三份 route-one 文本的定位（先说清比对对象）

| 记号 | 文件与位置 | 约定 | 覆盖内容 |
|---|---|---|---|
| R1B | `paper/sections/appendix_model_proofs.tex` L24–L52，`\subsection{Proof of Proposition~\ref{prop:valueacc}}` | convention B | (i) 实例与 $\eta=\infty$；(ii) value accuracy 失败 + $(\eta_u,\eta_o)=(\tfrac1{1+M},1+M)$、$\eta=1$；(iii) 链求和 + $c=2\eta_u/(\eta+1)$、$\varepsilon=(\eta-1)/(\eta+1)$；末尾 Remark 接 Horel–Singer 给 thm:ceiling 的第二证明 |
| R1A | `paper/sections/appendix_proofs.tex` L143–L216，`\label{app:valueacc}` | **旧约定**（$\eta_u,\eta_o\ge1$，(iii) 的 level 是 $\max\{1-1/\eta_u,\eta_o-1\}$，带 $\eta_o<2$ 前提） | (i) 另一个实例；(ii) 含 **argmax 保持与 $\eta^{\mathrm{sel}}=1$**；(iii) 旧 level，无 rescaling |
| 台账 | `THEOREM_LEDGER.md` L47–L67「## T2」 | convention B | 陈述与禁止声称；矩阵以 `results/V11/inputs/statement_valueacc.md` 为准 |

按任务要求，route two 的比对基准是 **R1B**；R1A 只用于确认「(ii) 的 $\eta^{\mathrm{sel}}$ 分句在仓库里有没有证明」以及旧 level 的归档形态。
结论：**statement 的 (ii) 里「predictive greedy 每步选真增益最大者（$\eta^{\mathrm{sel}}=1$）」这一分句在 R1B 中缺失**，只在 R1A 中有（论证与约定无关，可平移）。这是本次比对最实质的一条分歧，方向是 route one 弱于 route two。

---

## 1. 步骤对应表（route two 每一步 → route one）

对应关系分四类：`=` 同一论证；`≈` 同一论证但实例/写法不同；`+` route two 新增（route one 无对应）；`⊂` route one 有但更弱。

| route two 步 | 内容 | route one 对应 | 类别 | 说明 |
|---|---|---|---|---|
| Step 1 | telescoping identity（$h(\emptyset)=0$，任一枚举顺序） | R1B (iii) 的 $f(S)=\sum d_{e_i}(S_{i-1})$、$\tilde f(S)=\sum\tilde d_{e_i}(S_{i-1})$；R1A (iii)「summing the telescoping along any fixed enumeration」 | `=` | 两边都是初等裂项，都只用 $\emptyset$ 处取 0 |
| Step 2 | band 自洽性：上端减下端 $=d\cdot\frac{\eta-1}{\eta_u}$；$\eta>1$ 时非空 $\iff d\ge0$ | 无 | `+` | route one 未做 band 非空性分析；这一步是 route two 给 monotonicity 定位的依据（见 §3 的 D8） |
| Step 3–5 | (i) Instance A：$N=\{1,2\}$，$f$ modular weights $(1,\varepsilon)$，$\tilde f=(0,1,\varepsilon,1)$；逐集合验 value accuracy | R1B (i)：$f=(0,1,1,1+\varepsilon)$，$\tilde f\equiv1$（非空集） | `≈` | **实例不同、机制相同**（都让 $\tilde f$ 在第二步增益上被抹平）。两个实例我都独立验过 value accuracy 与 monotone submodular（judge 脚本 §A、§A'）。R1A 用第三个实例 $f=(0,1,\tfrac{2\varepsilon}{1-\varepsilon},\tfrac{1+\varepsilon}{1-\varepsilon})$，同样合法（judge 脚本 §A''） |
| Step 6 | $d_2(\{1\})=\varepsilon>0$，$\tilde d_2(\{1\})=0$ | R1B (i) 的 $\tilde d_b(\{a\})=0$ 而 $d_b(\{a\})=\varepsilon>0$ | `=` | 同一 witness 类型 |
| Step 7 | 下侧给 $\varepsilon/\eta_u\le0$，与 $\eta_u>0$ 矛盾，故无有限 $(\eta_u,\eta_o)$ | R1B (i)「no finite $\eta_u$ satisfies ...; that is, $\eta=\infty$」 | `=` | 一行不等式，两边一致 |
| Step 8 | $L_K(\eta)$ 无自变量可代；按 $L_K(\infty)=0$ 约定界平凡 | R1B **无**；R1A (i) 末句「every bound of the form $L_K(\eta)$ is vacuous for it」 | `⊂` | R1B 停在 $\eta=\infty$，没有把 statement 的末句写出来。两条路线对末句的读法一致（非蕴含），见 §4 的 G2 |
| Step 9 | 重标定救不回来：$c\tilde d=0$ 不变，argmax 与轨迹不变 | 无（R1B 的末尾 Remark 里有同型的「rescaling does not change the maximizer」，但用途是 thm:ceiling） | `+` | route two 的补充，封住「(i) 是不是 scale artifact」这个口子 |
| Step 10–13 | (i) 加强 Instance B：$n=3$、$K=2$ coverage，value-accurate 而 $\eta^{\mathrm{sel}}=\infty$；并诊断 A 破下侧、B 破上侧 | 无 | `+` | 超出 statement 字面内容；我复核通过（judge 脚本 §C，四组 $(\varepsilon,\delta)$，穷举全部 tie 打破） |
| Step 14 | Instance B 族最坏 ratio $=(1-\varepsilon)/(1+\varepsilon)$（$\varepsilon\le\sqrt5-2$）或 $(1+\varepsilon)/2$ | 无 | `+` | 我用 sympy 独立确认两支公式、交点 $\varepsilon_0=\sqrt5-2$ 与交点值 $(\sqrt5-1)/2$（judge 脚本 §D） |
| Step 15–16 | (ii) $\tilde d_e(S)=(1+M)d_e(S)$，band 两侧同时取等，$(\eta_u,\eta_o)=(\tfrac1{1+M},1+M)$，$\eta=1$ | R1B (ii) 同句 | `=` | 逐字同构 |
| Step 17 | convention B 取消 floor 是 (ii) 的 $\eta=1$ 所必需；verbatim 版最小合法对给 $\eta=1+M$ | 无（信息在 `definition1.md` 末段与台账 T2） | `+` | 属于「约定层」的说明，R1B 的证明正文不提 |
| Step 18 | $f\not\equiv0$ 给出 $f(S^\dagger)>0$；$(1+M)f>(1+\varepsilon)f\iff M>\varepsilon$；$\varepsilon=M$ 且 $M<1$ 时恰好成立 | R1B (ii)「For every nonempty $S$ with $f(S)>0$ ... value-accurate at no level below $M$」 | `≈` | R1B 把 $f\not\equiv0$ 藏在「with $f(S)>0$」里，未显式列为前提；$\varepsilon=M$ 的边界 R1B、R1A 都没写 |
| Step 19–20 | argmax 集合逐点相等 $\Rightarrow g_t=M_t\Rightarrow a_t=1\Rightarrow\eta^{\mathrm{sel}}=1$（含 $M_t=g_t=0$ 的第二种情形） | **R1B 无**；R1A (ii)「the maximizers ... are the same set of elements ... giving $\etasel=1$」 | `⊂` | **R1B 缺这一整段**，而 statement (ii) 明写该分句。R1A 的版本只处理「positive chosen gain」的步，未显式处理 $M_t=g_t=0$ 的步；route two 两种情形都处理 |
| Step 21 | (i)+(ii) 合成「既不充分也不必要」 | statement 标题句 | `=` | 合成句，无新内容 |
| Step 22 | (iii) set-level band：逐项套 band 后相加，得 $f(S)/\eta_u\le\tilde f(S)\le\eta_of(S)$ | R1B (iii) 的 eq:valueband | `=` | **但理由不同**：R1B 写「all terms are nonnegative because $f$ is monotone; summing gives」，route two 指出逐项相加不需要符号条件。见 §3 的 D8 |
| Step 23 | 把 $c$ 与 $\varepsilon$ 作为极小化问题解出（$A(c)=1-c/\eta_u$ 递减、$B(c)=c\eta_o-1$ 递增，平衡点） | 无（R1B 直接「Now set $\varepsilon=\ldots$ and $c=\ldots$」） | `+` | route two 把常数**解出来**而不是验证给定值，结果与 R1B 的常数逐字相同（我用 sympy 解同一方程复核，judge 脚本 §G） |
| Step 24 | 代回：$c/\eta_u=2/(\eta+1)=1-\varepsilon$，$c\eta_o=2\eta/(\eta+1)=1+\varepsilon$ | R1B (iii) 同句 | `=` | 逐字同构 |
| Step 25 | $\varepsilon(1)=0$，$\varepsilon'=2/(\eta+1)^2>0$，$\lim=1$，故 $\varepsilon\in[0,1)$；$\eta=1$ 时 $c\tilde f=f$ | R1B (iii) 括号句「For $\eta=1$ this reads $c\tilde f=f$; for $\eta>1$ the level lies in $(0,1)$」 | `≈` | 同结论；route two 多给单调性与极限，并点明 $\varepsilon=0$ 落在 value accuracy 定义域 $(0,1)$ 之外 |
| Step 26 | 重标定后因子 $(\eta_u/c,\ c\eta_o)=(\tfrac1{1-\varepsilon},1+\varepsilon)$，product 仍为 $\eta$ | 无（`definition1.md` 有一句方向相反的 scaling 规则） | `+` | 这一步直接暴露了输入文件的方向错误，见 §3 的 D9 |
| Step 27 | $(c,\varepsilon)$ 在最坏情形下唯一最优（$n=2$、$f=|S|$、两侧各被一个集合取等） | 无 | `+` | 我独立确认该实例合法且两侧同时取等（judge 脚本 §I，三种 split） |
| Step 28 | (iii) 前提清单：monotonicity 只经 $d\ge0$；$f(\emptyset)=\tilde f(\emptyset)=0$；不需 submodularity；不需 $K$/greedy/tie-breaking | R1B 的 Remark 首句「uses only that $f$ is monotone and that both functions vanish on the empty set; it does not use submodularity」 | `≈` | 同结论，route two 多一层「monotonicity 具体用在哪」的定位 |
| §6.1 | $K=3$、$\eta=3/2$ 的三种 split 数值表 | 无 | `+` | 全表我逐格复核（judge 脚本 §J），$c\in\{4/5,6/5,3/5\}$、$\varepsilon\equiv1/5$、上下两侧各被取到 |
| §6.2 | $K=3$、$M=1/2$ 的 coverage 逐步表，$\eta^{\mathrm{sel}}=1$ | 无 | `+` | 复核通过（judge 脚本 §K）：singletons $(4,3,3,1)$、$d_\cdot(\{1\})=(2,3,1)$、$f(\{1,3\})=7=\mathrm{OPT}$、$t=2$ 两个增益为 0 |
| §6.3 | $K=2$ 的 Instance A/B 有理数表 | 无 | `+` | 复核通过（judge 脚本 §A、§C） |

### 1.1 route one 有而 route two 未覆盖的步骤

| route one 步 | 内容 | route two 是否覆盖 | 判断 |
|---|---|---|---|
| R1B (i) 的 padding 句 | 「Any number of further elements with zero marginal gain under both $f$ and $\tilde f$ may be added to reach a prescribed $n$」 | 覆盖（route two Step 3 用 weight 0 的 dummy 元素） | 无分歧 |
| R1B (i) 的 submodularity 检查写法 | 显式写 $d_a(\{b\})=d_b(\{a\})=\varepsilon\le1=d_a(\emptyset)$ | 覆盖（route two 用 modular $\Rightarrow$ submodular） | 无分歧 |
| R1B 末尾 Remark | (iii) + Horel–Singer 的 $\alpha\frac{1-\varepsilon}{1+\varepsilon}$ 观察 $\Rightarrow$ thm:ceiling 的 attainment 第二证明（$\frac{1-\varepsilon}{1+\varepsilon}=1/\eta$） | **未覆盖** | 不是 prop:valueacc 的内容，route two 处于隔离状态无法看到 `horel2016` 的观察。判为「超出陈述范围，不计入 gap」。补记一条可复核的等式：$\varepsilon=\frac{\eta-1}{\eta+1}\Rightarrow\frac{1-\varepsilon}{1+\varepsilon}=\frac{2/(\eta+1)}{2\eta/(\eta+1)}=\frac1\eta$，与 route two Step 24 的两个等式是同一组，故 route two 的材料足以支撑该 Remark |
| R1A (ii) 的 $\eta^{\mathrm{sel}}=1$ | argmax 保持 $\Rightarrow\etasel=1$，并引 prop:guarantee 认证 $L_K(1)$ | 覆盖且更细（Step 19–20 补了 $M_t=g_t=0$ 的情形与「对每个 $K$」） | route two 更强 |
| R1A (iii) 的旧 level | $\max\{1-1/\eta_u,\eta_o-1\}$，带 $\eta_o<2$ 前提，无 rescaling | 未覆盖（按任务要求不比对旧约定） | 归档项，不计入 gap |

---

## 2. 结论与量词是否一致

**结论一致。** (i)(ii)(iii) 三条的结论句、常数 $c=2\eta_u/(\eta+1)$、level $\varepsilon=(\eta-1)/(\eta+1)$、区间 $[0,1)$、(ii) 的 $(\eta_u,\eta_o)=(\tfrac1{1+M},1+M)$ 与 $\eta=1$，route two 与 R1B 逐字相同。route two 的 $(c,\varepsilon)$ 是从极小化问题解出来的，不是抄的，这一点提高了独立性。

**量词不一致（`quantifier_match = false`）。** 差异全部是「route two 有、route one 无」，没有反向的一条。逐条列在 §3。

---

## 3. 分歧清单（divergences）

按「在一条路线中出现、在另一条中缺席」列出。D1–D7 是量词层面，D8–D10 是论证层面。

- **D1（量词，route two 有／R1B 无）(i) 的 $n\ge2$。** statement 与 R1B 都没写 $n\ge2$，但 $n=1$ 时 (i) 为假：唯一 pair 是 $(\emptyset,e)$，value accuracy 给 $\tilde f(\{e\})\ge(1-\varepsilon)f(\{e\})>0$（当 $f(\{e\})>0$），于是 $\eta\le\frac{1+\varepsilon}{1-\varepsilon}$ 有限；$f(\{e\})=0$ 时 value accuracy 逼出 $\tilde f(\{e\})=0$，band 平凡成立。R1B 的构造本身就在 $n=2$ 上并用 padding 扩到任意 $n$，所以这是**两条路线共有的隐含前提**，route two 把它显式化。状态 `[HAND-PROOF-UNREVIEWED]`（$n=1$ 的反向一行论证）。建议：陈述里补「$n\ge2$」或「$|N|\ge2$」。
- **D2（量词，route two 有／R1B 无）(i) 末句的 $L_K(\eta)$ 与其中的 $K$。** R1B 的证明停在 $\eta=\infty$，没有写 statement 的末句；R1A 有一句「every bound of the form $L_K(\eta)$ is vacuous」。route two 的 Step 8 + §3.3 把它明确读成**非蕴含**（不存在函数 $\varepsilon\mapsto\eta(\varepsilon)$ 使 value accuracy 蕴含有限 $\eta$），并对任意 $1\le K\le n$ 成立。两条路线的读法一致，只是 R1B 没写。
- **D3（量词，route two 有／R1B 无）(ii) 的「$f$ 不恒为零」。** statement 写了，R1B 的证明把它藏在「for every nonempty $S$ with $f(S)>0$」里，没有显式作为前提；$f\equiv0$ 时前半句为假。
- **D4（量词，route two 有／R1B 无）(ii) 的 $\varepsilon=M$ 边界。** $M<1$ 时 value accuracy 在 $\varepsilon=M$ 处恰好成立（上侧取等），故 statement 里的严格号「$\varepsilon<M$」不可放宽成 $\le$。R1B、R1A 都未提。我独立确认（judge 脚本 §F，$M\in\{1/100,1/2\}$ 上 $\varepsilon=M$ 时 value accuracy 成立，$\varepsilon\in\{M/2,0.99M\}$ 时失败）。
- **D5（量词，route two 有／R1B 无）(ii) 的 $\eta^{\mathrm{sel}}=1$ 全套量词。** 对每个 $t\in\{0,\dots,K-1\}$、每个 $1\le K\le n$、任何 tie-breaking（adversarial 这个限定词在此可删而真值不变，因为 argmax 集合逐点相等）。**R1B 完全没有这一段**，statement (ii) 却明写。R1A 有 argmax 保持的论证但只覆盖「positive chosen gain」的步，未显式处理 $M_t=g_t=0$ 给 $a_t=1$ 的步。route two 两种情形都处理，并穷举 $K=1,2,3,4$ 的全部 tie 打破方式确认。**这一条是本次比对里 route one 唯一的实质缺口**，建议回写 R1B。
- **D6（量词，route two 有／R1B 无）(iii) 的 $\eta_u,\eta_o>0$ 与 $\eta\ge1$ 的定义域，以及「convention B 取消 floor 是 (ii) 的前提」。** R1B 的 (iii) 只写「Let $\tilde f$ have marginal-gain error $\eta=\eta_u\eta_o$」，$\varepsilon\in[0,1)$ 实际要求 $\eta\ge1$。route two 的 Q12 + Step 17 把这两件事挑明。
- **D7（量词，route two 有／R1B 无）(iii) 的 split 不变性。** $c$ 依赖 $(\eta_u,\eta)$，$\varepsilon$ 只依赖 $\eta$；band 宽度由 product 决定，split 只决定 scale。R1B 的公式里隐含，但没有作为一句话写出；route two 用三种 split（$(1,\tfrac32),(\tfrac32,1),(\tfrac34,2)$）在 $\eta=3/2$ 上确认 $\varepsilon\equiv1/5$。
- **D8（论证，两条路线对 monotonicity 的定位不同）。** R1B (iii) 写「and all terms are nonnegative because $f$ is monotone; summing gives」，把逐项求和挂在非负性上；route two Step 22 指出有限多条不等式逐项相加与符号无关，monotonicity 只在两处起作用：Step 2 的 band 非空（$\eta>1$ 时 Definition 1 本身强制 $d_e(S)\ge0$）与 $f(S)\ge0$ 使 $(1\pm\varepsilon)f(S)$ 是围绕非负数的相对带。**这不是矛盾**，R1B 那半句是多余而非错误（$L_i\le x_i\le U_i\Rightarrow\sum L_i\le\sum x_i\le\sum U_i$ 对任意实数成立）。按空洞性检验，(iii) 里的 monotone 不能删，但需要一句话说清它用在哪；建议把 R1B 的这半句改写。
- **D9（输入文件缺陷，route two 发现，我复核确认）`definition1.md` 的 scaling 方向写反。** 文件 convention B 段写「multiplying $\tilde f$ by $c>0$ maps $(\eta_u,\eta_o)\to(c\eta_u,\eta_o/c)$」，直接计算给 $c\tilde d\ge c\,d/\eta_u=d/(\eta_u/c)$ 与 $c\tilde d\le(c\eta_o)d$，正确映射是 $(\eta_u,\eta_o)\to(\eta_u/c,\ c\eta_o)$。判决性检验：$f$ 自身的因子是 $(1,1)$，$\tilde f=(1+M)f$ 即 $c=1+M$，(ii) 与 R1B 给的答案是 $(\tfrac1{1+M},1+M)$，与正确映射一致，与文件所写的 $(1+M,\tfrac1{1+M})$ 相反（后者会要求 $\tilde d\le d/(1+M)$，与 $\tilde d=(1+M)d$ 直接冲突）。状态 `[VERIFIED-SYMBOLIC]`（judge 脚本 §L）。**波及范围**：同一句话也出现在 `HANDOFF_2026-09-18.md` §3 L54；`paper/sections` 的 Model 散文写的是方向无关的「moves $\eta_u,\eta_o$ by reciprocal factors」，未受影响；product $\eta$ 在两种写法下都不变，故 prop:valueacc 的三条结论不受影响。建议回写这两处。
- **D10（覆盖面，R1B 有／route two 无）末尾 Remark 的 Horel–Singer 接续。** 见 §1.1；判为超出陈述范围，不计入 route-two gap。route two 的 Step 24 已给出该 Remark 所需的全部等式。

---

## 4. route-two 未闭合项（route2 gaps）

route two 自报 G1–G7，我逐条核过，重排如下（G1、G3 已在 §3 作为 D1、D9 处理，不重复计为 gap）。

- **R2-G1（读法降级，已在文件内明说）(i) 末句只证成非蕴含。** route two 没有证成「value accuracy 下 ratio 可低于任意给定的 $L_K(\eta)$」；其 Instance B 族在 $\varepsilon=1/5,K=2$ 的最坏 ratio 是 $2/3$，高于 $L_2(3/2)=5/9$（我复核两数均正确）。**裁定：这不是缺陷，而是正确的保守读法。** 台账 T2 的禁止声称条与 `HANDOFF_ADDENDUM_2026-09-18.md` §B 第 5 条恰好要求这个读法：「value accuracy is not sufficient」必须限定到 predictive greedy，因为对不限查询的算法它是假的（穷举拿 $\frac{1-\varepsilon}{1+\varepsilon}$）。route two 在隔离状态下独立到达了同一保守结论。
- **R2-G2（真正的未闭合项，`[CONJECTURE]`）「value accuracy at level $\varepsilon$ 本身是否蕴含某个 $\phi(\varepsilon,K)>0$ 的乘性保证」。** route two 的 $K$ 步推广尝试显示 value band 的总宽度 $2\varepsilon f(S)$ 是**总预算**而非每步预算（每步可骗 $2\varepsilon/(K-1)$，总损失上界与 $K$ 无关），时间盒约 20 分钟后停止。**裁定：合理停止，不影响 (i) 的字面结论。** 需要注意的是这个问题在仓库语境下是**算法相关**的：对不限查询的算法答案是肯定的（$\frac{1-\varepsilon}{1+\varepsilon}$，addendum §B5 与 R1B 末尾 Remark）；对 predictive greedy 仍开放。route two 因隔离看不到前者，其问题表述没有区分算法类，建议入库时补一句限定。
- **R2-G3（未覆盖，不计缺陷）Instance B 族之外的最坏性。** Step 14 只给出该**族内**的最坏 ratio，没有声称是所有 value-accurate 实例上的最坏值，文件也没有越界声称。状态 `[HAND-PROOF-UNREVIEWED]`；我复核了两支公式、交点与三个格点的分支归属，全部正确。
- **R2-G4（措辞层）verbatim Definition 1 与 convention B 的张力。** route two 的 G4 记录正确，无遗留问题。
- **R2-G5（回写建议，非缺陷）(iii) 里 monotonicity 的用途需要一句话说清。** 与 D8 同一件事，route two 的定位正确。
- **R2-G6（模板条目无对应物）ProbeLottery。** 任务模板要求「$K=2$ for the ProbeLottery item」，但 prop:valueacc 三条里没有 ProbeLottery 这个对象（`statement_valueacc.md` 全文无该词，它属于 J8 那条命题）。route two 按隔离要求没有去别处查证，改把 $K=2$ 用在 (i) 的 walk-through 上并记录。**裁定：处理得当。**
- **R2-G7（时间盒）** 记录完整，符合房规。

**route two 无未修正的计算错误。** 我重写的独立脚本覆盖 route two 的全部数值与符号断言（两个 (i) 实例 + 旧附录实例、Instance B 的四组参数与全部 tie 打破、Step 14 的两支与交点、四个 $L_K$ 数值、(ii) 的三个 $M$ 与 $K=1..4$、(iii) 的符号恒等与极小化、$|S|^2$ 非 submodular 上的 set-level band、Step 27 的紧实例、§6.1 与 §6.2 的逐格数值、scaling 方向），**0 项 FAILED**。route two 自带脚本 122/0 也复跑通过。

---

## 5. route two 是否与 route one 的某一步矛盾

**没有矛盾。** 逐项核对结果：

1. (i) 的实例不同但都合法，两个实例我都验过 monotone submodular 与 level-$\varepsilon$ value accuracy；两者破坏的是 Definition 1 的同一侧（下侧，$\tilde d=0<d$）。
2. (ii) 逐字同构；route two 多出的 $\eta^{\mathrm{sel}}=1$ 段与 R1A 的对应段同向、更细。
3. (iii) 的链求和、$c$、$\varepsilon$、代回、$\eta=1$ 端点全部同构；唯一差别是 D8 的 monotonicity 定位，route two 的分析更细，R1B 的多余半句不构成错误。
4. route two 指出的 `definition1.md` 方向错误（D9）指向**输入文件**，不指向 R1B 的证明；R1B 的 (ii) 恰好与正确方向一致。

---

## 6. 不适用的任务模板条目

- **thm:ceiling 的 route「yi」/「jia」对比（$n\ge2K$ attainment 方向）**：本次判定对象是 prop:valueacc，不是 thm:ceiling，故不执行。仅记录一条与本命题相关的事实：R1B 末尾 Remark 用 prop:valueacc(iii) 加 Horel–Singer 的观察给出 attainment 的第二条路径，其所需等式 $\frac{1-\varepsilon}{1+\varepsilon}=\frac1\eta$（在 $\varepsilon=\frac{\eta-1}{\eta+1}$ 处）由 route two 的 Step 24 独立提供，两条路线在这一点上相容。该 Remark 本身是否构成完整证明，留给 thm:ceiling 的比对任务判定。
- **J8 的 route-one GAP 与 `results/J8/J8_claude_spotcheck.py` 数值**：同样不属于本命题，不执行。
- **ProbeLottery 的 $K=2$ walk-through**：见 R2-G6，本命题下无对应对象。

---

## 7. 状态标签汇总（本比对文件自身的断言）

| 断言 | 状态 | 依据 |
|---|---|---|
| route two 的 Instance A（三种 $\varepsilon$ 以上）monotone submodular 且 value-accurate，witness $\tilde d=0<d$ | `[VERIFIED-EXHAUSTIVE]` | judge 脚本 §A，$\varepsilon\in\{1/100,1/5,1/2,9/10,99/100\}$ |
| R1B 的 (i) 实例同样合法 | `[VERIFIED-EXHAUSTIVE]` | judge 脚本 §A' |
| R1A（旧附录）的 (i) 实例同样合法 | `[VERIFIED-EXHAUSTIVE]` | judge 脚本 §A'' |
| Instance B：value-accurate、$\eta^{\mathrm{sel}}=\infty$、只破上侧、ratio $=1/(1+\delta)$ | `[VERIFIED-EXHAUSTIVE]` | judge 脚本 §C，四组参数，穷举全部 argmax-consistent tie 打破 |
| Step 14 两支公式、交点 $\sqrt5-2$、交点值 $(\sqrt5-1)/2$ | `[VERIFIED-SYMBOLIC]` | judge 脚本 §D |
| $L_2(3/2)=5/9$、$L_2(1)=3/4$、$L_3(3/2)=386/729$、$L_3(1)=19/27$、$2/3>5/9$ | `[VERIFIED-EXHAUSTIVE]` | judge 脚本 §E |
| (ii) band 两侧取等、$\eta=1$、argmax 集合逐点相等、$\eta^{\mathrm{sel}}=1$（$K=1..4$ 全 tie 打破）、$\varepsilon=M$ 边界 | `[VERIFIED-EXHAUSTIVE]` | judge 脚本 §F，$M\in\{1/100,1/2,3\}$ |
| (iii) $c/\eta_u=1-\varepsilon$、$c\eta_o=1+\varepsilon$、极小化解出 $c$、$\varepsilon\in[0,1)$、$(\eta_u/c)(c\eta_o)=\eta$、band 宽度 $d(\eta-1)/\eta_u$ | `[VERIFIED-SYMBOLIC]` | judge 脚本 §G |
| (iii) set-level band 与 $c\tilde f$ 的 value accuracy 在 monotone 非 submodular 的 $f=|S|^2$ 上成立 | `[VERIFIED-EXHAUSTIVE]` | judge 脚本 §H，四组 $(\eta_u,\eta_o)$ × $2^3$ 个 in-band predictor |
| Step 27 紧实例合法且两侧同时取等 | `[VERIFIED-EXHAUSTIVE]` | judge 脚本 §I，三种 split |
| §6.1 与 §6.2 的逐格数值 | `[VERIFIED-EXHAUSTIVE]` | judge 脚本 §J、§K |
| `definition1.md` 的 scaling 映射方向写反，正确映射为 $(\eta_u/c,\ c\eta_o)$ | `[VERIFIED-SYMBOLIC]` | judge 脚本 §L，并用 (ii) 交叉检验 |
| R1B 缺 (ii) 的 $\eta^{\mathrm{sel}}=1$ 分句 | `[HAND-PROOF-UNREVIEWED]`（文本比对结论，非数学断言） | `appendix_model_proofs.tex` L35 的段落全文 |
| (i) 在 $n=1$ 时为假 | `[HAND-PROOF-UNREVIEWED]` | 一行论证，见 D1 |
| 「value accuracy 是否蕴含 predictive greedy 的某个 $\phi(\varepsilon,K)>0$」 | `[CONJECTURE]` | 两条路线都未闭合；不限查询算法的版本另有答案（addendum §B5） |

---

## 8. 判定与建议动作

**verdict = B-PASS。** `consistent = true`（同一结论、同一常数，route two 无未修正错误）；`quantifier_match = false`（差异见 §3 的 D1–D7，全部方向是 route one 更弱）。

建议动作（本次不执行，交给 V11-Q10 的回写任务）：

1. `results/V11/inputs/definition1.md` 与 `HANDOFF_2026-09-18.md` §3 L54 的 scaling 映射改为 $(\eta_u,\eta_o)\to(\eta_u/c,\ c\eta_o)$（D9）。
2. `paper/sections/appendix_model_proofs.tex` 的 (ii) 补回 argmax 保持与 $\eta^{\mathrm{sel}}=1$ 一段（可从 `app:valueacc` 平移，论证与约定无关），并补 $M_t=g_t=0$ 的情形（D5）。
3. 同文件 (iii) 的「all terms are nonnegative because $f$ is monotone」改写成 monotonicity 的真实用途（band 非空与 $f(S)\ge0$），或直接删去该半句（D8）。
4. (i) 的陈述补 $n\ge2$（或在证明里点明 $n=1$ 为假），(ii) 的证明显式引用「$f\not\equiv0$」（D1、D3）。
5. (ii) 加一句 $\varepsilon=M$ 的边界说明，支持严格号（D4）。

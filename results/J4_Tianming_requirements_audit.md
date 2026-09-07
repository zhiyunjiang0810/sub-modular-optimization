# J4：目前的理论是否满足 Tianming 的要求？

2026-09-07。核对对象：上传的 `TIANMING_REQUIREMENTS_CHECK (1).md`，以及 GitHub 提交 [`3006b9024017180689c19bf5a49d09ff9bf10029`](https://github.com/zhiyunjiang0810/sub-modular-optimization/commit/3006b9024017180689c19bf5a49d09ff9bf10029) 的论文源码。J3 另按此前交付的证明结构草稿核对。

**判断：第 1 条的 greedy tightness、第 2 条的删除 R-step、第 4 条的 single-step 分析改进，已有实质回应。第 3 条有两个明确结果，但只能按算法范围分别判定，不能笼统写成“任何算法都不能比 greedy 更好”。**

现在最强的主贡献是：在明确的全局边际误差模型下，给出 greedy 的精确有限 K 最坏值，并解释通常的逐步误差分析为什么不能达到这个值。受限查询的 hardness 提供渐近呼应。它们可以支撑一条清楚的理论主线，但尚未完成一般查询模型下的有限 K 算法最优性刻画。

## 1. 如何判定“满足”

清单明确说原话是“尽量用当时的原话或关键词”，并另外列了作者的解释。此次把这两部分分开处理：作者对要求的解释不能自动当作 Tianming 本人的完整要求。尤其是 `O(n)K`，材料无法确定表示 `O(nK)` 还是 `O(n^K)`；第 5 节分别回答。

核对采用三层证据：当前论文实际写了什么；已有一般论证及其逻辑连接；符号或有限实例验证覆盖什么。沿用项目状态标签：`[VERIFIED-SYMBOLIC]` 指恒等式，`[VERIFIED-LP]` 包括有限精确穷举，`[HAND-PROOF-UNREVIEWED]` 保留给没有一般 oracle 的手工装配。后一个标签本身不表示已经发现错误，也不能与缺少一般证明的猜想混为一谈。

| 要求及其范围 | 核对结论 | 当前落点 |
|---|---|---|
| 对每个 K 给 greedy 的达到实例 | 满足，须说明误差度量与参数域 | Theorem 7：selection / trajectory error；Theorem 9：global error |
| 给出 greedy 在原全局误差模型下的精确答案 | 满足，已有下界证书与达到构造的完整对应 | Theorem 9，附录 exact / validity / instances |
| 删除 R-step 算法、理论与对应实验 | 完成 | 活跃论文源码未发现残留；穷举结论保留在 Theorem 11 |
| 不限查询的确定性算法上界 | 满足，且是可达到的最优保证 | Theorem 11：1/η，n≥2K |
| 多项式次、每次大小≤K 的查询上界 | 在定理列出的参数范围内满足 | Theorem 13：校准后的 H，以及随机版附加项 |
| 任意大小、任意固定多项式查询预算的匹配上界 | 未完成 | F3 预算受限，且一般 K 的构造证明仍缺 |
| 有限 K、与 greedy 相同预算下的算法最优性或更好算法 | 一般情形未完成 | 1≤η<K 时，现有结果未闭合这条前沿 |
| single-step 分析改进 | 满足；J3 结构解释尚未进正文 | Lemma 8 + Theorem 9；J3 有可审阅的一般手推 |

当前版本并非仅仅收录了 J2 报告。`model.tex` 已修正有害零步，`appendix_proofs.tex` 已加入 coherence 非负 slack 证书，Theorem 13 已换成实际误差乘积的闭式校准，查询类包含 greedy 的限制也已进入正文。J3 刚性命题未出现在该提交中。以上均按当前源码确认，而非沿用旧 REVIEW_BRIEF 或 RESEARCH_STATE 的状态。

## 2. 要求 1：tightness 已有回应，但两把尺必须分开

### 2.1 Theorem 7 确实逐 K 取到经典界

当前定理范围为 K≥2、â>1、对抗 tie。取两个大小为 K 的块 B、O，令

\[
a=1-\frac{1}{\hat aK},\qquad
F(x,y)=1-a^x(1-y/K).
\]

沿 greedy 的 `(x,y)=(t,0)` 轨迹，B 与 O 的预测增益都为 `a^t/(âK)`；真实增益分别为 `a^t/(âK)` 与 `a^t/K`。所以每一步 selection error 都是 â，trajectory error 的两个因子为 â、1，输出值为

\[
\eta^{\mathrm{sel}}=\eta^{\mathrm{tr}}=\hat a,
\qquad \frac{f(B)}{f(O)}=1-a^K=L_K(\hat a).
\]

所有选中增益均为正，J2 新增的零步分支不会改变这个达到实例。最优值为 1，真实目标的单调性、submodularity 与预测误差由附录的完整边际表承担。原 T5 / F2 的检查以及当前附录逐步式相互吻合。

**但它的全局误差为 `(Kâ−1)/(K−1)>â`。** 因此 Theorem 7 不能被表述为原全局 L_K(η) 的逐 K tightness。这一点当前正文已区分。

### 2.2 Theorem 9 给出更实质的全局答案

令

\[
k_1=(K-1)\eta+1,\quad q=\frac{(K-1)\eta}{k_1},\quad
V_j=1-q^j\left(1-\frac{K-j}{K\eta}\right).
\]

Theorem 9 的结论是

\[
\rho_K(\eta)=\min_{0\le j\le K-1}V_j(\eta).
\]

核对两个方向时，关键连接都在：

1. 任意实际 run 产生 reduced-LP 可行点。greedy 选中最优元素时，后续对应 g 置零；consistency 此时是 `0≥0`。一般候选的 coherence slack 已写成三项非负量，其中一项使用离轨状态的上误差带。
2. 分段显式非负乘子把这些约束配成 `Σd_t−V_j`，给出所有实际 run 的下界。η=1 使用取消奇点后的分支；相邻分支差的索引已改为 `0≤i≤K−2`。
3. 每一段有三块显式实例达到 V_j，补上反方向。无需证明“每一个 reduced-LP 可行点都能实现”，也不需要事先假定任意 run 与最优集不相交。

J2 已有独立 slack 分解、1,536 个全格点约束检查、456 个有理对偶检查，并复跑原 N1 的 320 项和 N2 的 480 项。当前采纳后的证明与这条证据链相符。一般归约与分类装配仍按仓库规则保留手证标签；此次没有发现推翻主定理两个方向的缺口。

清单中的“原界对每个有限 K 严格不紧”必须补 `η>1`。在 η=1，预测器等于真实函数，且

\[
\rho_K(1)=L_K(1)=1-(1-1/K)^K.
\]

对于 η>1，coherence 解释了严格改进：若经典递推每一步同时取等，就需要每个最优元素满足 `g_{t,i}=ηd_t`；coherence 与 submodularity 又迫使这些边际在下一步不下降，而取等的 coverage 要求它们的总和随剩余最优值下降。两者冲突。结合 Theorem 9 的达到性，得到有限 K 的严格差距。此处一般等号推理保留 `[HAND-PROOF-UNREVIEWED]`，J4 另以 325 组精确参数检查边界与严格性。

### 2.3 不能把 NWF 的“greedy tight”自动扩成所有算法最优

NWF 1978 的公开摘要明确描述 greedy 的有限 K 保证及逐 K 达到。另一篇 Nemhauser–Wolsey 1978 讨论 partial enumeration 加 greedy，并把算法保证与计算预算联系起来。二者对应不同问题，清单把它们放进同一条解释，容易提高或混淆验收标准。[NWF 1978](https://link.springer.com/article/10.1007/BF01588971)，[NW 1978](https://pubsonline.informs.org/doi/abs/10.1287/moor.3.3.177?journalCode=moor)。

因此：**Tianming 若要的是 greedy 的 tight bound，已经有实质答案；若另要有限 K 的“最优算法对预算的精确权衡”，还不能判定完成。**

## 3. 要求 2：R-step 删除完成

核对 `main.tex` 的实际输入文件、理论、正文实验及附录实验，并排除 LaTeX 注释后，R-step / lookahead / multi-step / pair-greedy 均无活跃文本命中。旧研究文件与注释里保存历史结果，不构成重新放进论文。

保留的穷举结论正确。全局单元素带沿同一条链求和给

\[
f(S)/\eta_u\le\tilde f(S)\le\eta_of(S).
\]

取 `Ŝ∈argmax_{|S|≤K} f̃(S)`，则

\[
f(\hat S)\ge\frac{\tilde f(\hat S)}{\eta_o}
\ge\frac{\tilde f(O^*)}{\eta_o}
\ge\frac{f(O^*)}{\eta_u\eta_o}.
\]

有限误差还保证 f̃ 单调，所以枚举恰好 K 个元素的集合即可。这部分保留在 Theorem 11 中，与删除 R-step 技术没有冲突。

R12 的 K=4 数值结果不能升级为一般 K/R 定律，也不应作为“删除工作完成”的证明或论文新增贡献。

## 4. 要求 3：已经满足哪两层，仍缺哪一层

### 4.1 Theorem 11：不限查询的确定性最优保证是 1/η

构造

\[
\tilde f(S)=b|S|,\qquad
f_O(S)=b\left(\frac{|S\setminus O|}{\eta_o}+\eta_u|S\cap O|\right),\quad b>0.
\]

所有 O 产生相同预测器；任意确定性算法的输出 T 因此先被固定。n≥2K 时可选择与 T 不相交的 K 集合 O，令该算法的比值至多 1/η。

误差恰好正确：O 外的预测/真实比是 η_o，O 内是 1/η_u，两端均达到。这里 all-pairs 指从 A 到 A∪B 的增益。任意这样的比值是对应单元素比值的加权平均，且单元素对包含在 all-pairs 中，所以两个最大误差因子仍恰为 `(η_u,η_o)`。

与穷举下界合起来，这给出了 **n≥2K、不限查询、确定性算法** 的精确 minimax 保证。量词是“对每个算法存在一个坏实例”，并非每个算法都具有该保证。

随机算法得到的是

\[
\frac{1-K/n}{\eta}+\frac Kn.
\]

先对均匀隐藏 O 取平均，再使用最小值不超过平均值，能选出一个固定 O；无需让 O 随随机种子改变。该上界在有限 n 下大于 1/η，一般不能把它也称为随机算法的精确最优值。

此次新增 `[VERIFIED-LP：精确穷举]`：20 个 `(n,K,η_u,η_o)` 构造，253,220 个非零 all-pairs 增益检查，1,928 个隐藏最优集/输出大小的平均检查，全部通过。平均公式另有 `[VERIFIED-SYMBOLIC]`。一般算法的不可区分性装配仍保留手证标签。

### 4.2 Theorem 13：受限查询的渐近回答是成立的适用方向

当前主文已经使用

\[
\eta_{\mathrm{act}}=\frac{\theta K-1}{K-\tau},\quad
\bar\theta=\frac{\eta(K-\tau)+1}{K},\quad
H_{K,\tau}(\eta)=1-\left(1-\frac1{\eta(K-\tau)+1}\right)^K.
\]

适用条件也已写明：固定实数 c≥0，`τ=⌈c⌉+1`，K>τ，`n≥4K^(c+2)`，η>1 且 `η≥(K−1)/(K−τ)`；最多 n^c 次对 f̃ 的查询，每次集合大小≤K，输出大小≤K。

我重新沿正文核对了 adaptive transcript 的顺序：先让算法面对只依赖集合大小的 canonical oracle，固定查询及输出；再随机选 O，对这些固定查询作并集界；最后逐步归纳真实回答与 canonical 回答相同。当前文本使用的是这个顺序，没有直接把依赖 O 的真实自适应查询当成独立集合。

四类边穷尽误差方向，当前校准也支持任意指定的误差拆分。计数部分给出坏事件概率至多 9/32，足以选择确定性坏实例。随机版先固定随机种子，对 O 平均，再对种子平均，得到同一个 O 的期望界。一般计数与归纳已有可审阅手推；按项目规则仍保留 `[HAND-PROOF-UNREVIEWED]`，与 F3 缺少一般构造论证的情况不同。J4 补查 1,638 个精确超几何概率，均不超过所用并集上界。

这一结果的三个实质范围是：

- **查询大小限制属于模型条件。** “多项式时间算法”通常仍可查询大集合；查询预算有限也不限制查询之间可用多少计算，二者不能直接替换。
- **不能排除有限 K 的改进。** 固定 c、η，H 的极限是 `1−exp(−1/η)`。这排除的是所述查询类在极限常数上的统一改进，容许有限 K 或低阶项的改进。
- **greedy 必须在比较类中。** 它最多使用 `Kn−K(K−1)/2` 次查询。`nK≤n^c` 足够，例如整数 c≥2。当前 remark 已修正，不能再对 c=0 的一查询类声称 greedy 达到类最优。

H 也不是在每个有限参数点都优于已有的 1/η 天花板。例如 η=2、c=2，K=8 时 H≈0.533493，大于 0.5；K=16 时 H≈0.453295，小于 0.5。比较确定性保证时可合并成 `min{H,1/η}`。称其 non-trivial 应说明是渐近匹配或落在更强的有限参数区间。

随机版还需保留 ε_n：只取 `K→∞` 并不自动使正文给出的附加项消失。整数 c 且 `n=4K^(c+2)` 时，其第二项恰为 `1/[16(c+2)!]`。若要从该显示上界直接得到相同随机渐近常数，需要选择使 ε_n→0 的 n(K)，例如 `n≥4K^(c+3)`。这不破坏允许 n 足够大的最坏情况论证，但极限的量词应写清。

### 4.3 F3 不能用来宣布一般查询版本已经完成

当前附录把 F3 写为任意大小查询的补充 theorem，但结尾同时明确承认：j、m* 的一般闭式无证明；构造的单调性、submodularity 与归一化只有有限参数穷举，没有一般 K 的推导；随机版另用一个尚未核查的构造不等式。

因此这里的欠缺不只是“普通概率推理没有代码检查”。**一般参数下的合法坏实例尚没有完整论证，故不能把 F3 按已完成的一般定理计入验收。** 它保留为有价值的构造方向与有限证据。

即使补上该证明，它目前的预算上限也只是

\[
Q\le\frac{n^2}{2K^2(t^*+K)^2},
\]

约为 `n²/((2+η)²K⁴)`，没有覆盖任意固定多项式指数。附录把它进一步写成 `n^(2−o(1))` 时还需要限制 K、η 相对 n 的增长；不能在所有参数 regime 下省略 K⁴。

清单的“指数 2 是该构造族内在上限”也应注明一般证书的覆盖范围。当前附件所引的 48 组不可行性检查，不能单独证明一切参数、一切该族扩展均不可行。这不是对问题本身的查询复杂度上限。

## 5. “某个算法比 greedy 好”应如何回答

这里清单的总结过于简略。**现有穷举算法已经在 1≤η<K 时，严格改善 greedy 的最坏情况保证。**

由相邻分支式

\[
V_0-V_1=\frac{K-\eta}{K\eta k_1}>0\quad(\eta<K),
\]

有 `ρ_K≤V_1<V_0=1/η`。例如：

| K | η | greedy 的精确最坏保证 | 穷举的最坏保证 |
|---|---|---|---|
| 3 | 1 | 19/27 | 1 |
| 3 | 3/2 | 9/16 | 2/3 |
| 3 | 2 | 7/15 | 1/2 |
| 3 | 3 | 1/3 | 1/3 |

这比较最坏情况保证，并不表示穷举输出在每个实例上都拥有更大的真实 f 值。

因此 `O(n)K` 的两种解释，答案明显不同：

| Tianming 的原意 | 现在能回答什么 |
|---|---|
| 允许 O(n^K) 级别的穷举 | 已有更强算法保证，且 n≥2K 时达到不限查询确定性最优值 1/η；算法思路简单，不能仅凭此保证理论新颖性 |
| 要求 O(nK) 或与 greedy 相当的查询预算 | 一般有限 K 的更好算法或最优性尚未解决；现有受限查询定理只提供渐近结论 |

枚举所需预测值查询数是 `binom(n,K)`，总实现还包含枚举和表示集合的开销。固定 K 时它关于 n 是多项式；K 作为增长参数时，它不属于指数独立于 K 的统一多项式预算。Theorem 13 的固定 c、K>⌈c⌉+1 条件也正好阻止把该 hardness 套在完整穷举上。

在 η≥K 时，greedy 的 ρ_K=1/η，所以它达到不限查询的确定性最优保证。应写成这句话，不能写“greedy、穷举与任何算法相同”，更不能借此声称有限 n 的随机算法也被锁定在 1/η。

## 6. 要求 4 与 J3：分析已有改进，刚性论证可以继续采用

### 6.1 Sharp form 的逻辑核对

记 d 为选中元素当前真实增益，g 为另一个未选元素的当前增益，h 为加入选中元素后的增益。Coherence (ii) 等价于

\[
d-\frac g\eta\ge\left(1-\frac1\eta\right)(g-h).
\]

再用真实 f 的 submodularity，得到

\[
\boxed{d-\frac g\eta\ge\left(1-\frac1\eta\right)(g-h)\ge0.}
\]

第一段是原 (ii) 的等价改写；第二段还用了 submodularity，并非只靠 coherence。Coherence 本身只需要全局单元素误差带及预测值来自同一个 set function，不使用预测器 submodularity。其证明确实访问 `S∪{o}` 的离轨状态，所以不能换成纯 selection / trajectory error。

在 η>1 时，若 `d=g/η`，就必须 `h=g`：当前误选已经损失到误差带允许的极限，就不能同时再削弱该竞争元素未来的边际。这是对现有证明机制很有解释力的提炼；其等价改写不宜另行包装成独立新定理。

### 6.2 J3 的一般规模递推没有发现逻辑断点

J3 讨论非断点：`η∈(K−j,K−j+1)`、1≤j≤K−1，或 j=0、η>K。归一化 OPT=1。逐步核对如下。

1. 当前一般对偶的正权重恰好覆盖 coverage 的 t=0,…,j，consistency 的 t=0,…,K−2，以及 prediction 的 t=j,…,K−1，每个最优元素都受约束。
2. 若输出达到 V_j，非负加权 slack 总和为零，所有正权重对应约束取等。
3. t<j 时，相邻 coverage 等式与 consistency 求和给 `(1−1/η)r_{t+1}=r_t−Kd_t`；联立 `r_{t+1}=r_t−d_t`，得到 `d_t=r_t/k_1`、`r_{t+1}=qr_t`。
4. t=j 时，逐元素 prediction 等式和 coverage 共同给 `g_{j,i}=q^j/K`、`d_j=q^j/(Kη)`。此处产生对称性，无需提前假设最优元素对称。
5. 后期 prediction 与 consistency 等式迫使 g 冻结、d 恒定。早期再用逐元素 consistency 向后回推。最后 t=K−1 的 consistency 乘子虽为零，约束仍有效；结合 prediction 等号与 mono，依然得到 `g_{K,i}=g_{K−1,i}`。

相应轨迹量为

\[
d_t=\begin{cases}q^t/k_1,&t<j,\\q^j/(K\eta),&t\ge j,\end{cases}
\qquad g_{t,i}=q^{\min(t,j)}/K\quad(0\le t\le K).
\]

这条一般手推可继续作为结构引理草稿使用；此次复核未发现将有限 LP 错推广到一般 K 的归纳跳步。沿用 `[HAND-PROOF-UNREVIEWED]` 标记其互补松弛与归纳装配，递推恒等式已有 `[VERIFIED-SYMBOLIC]`。J3 原有 40 个最优面、2,480 次坐标极值 LP 支持有限范围的唯一性，此次没有重复运行这些检查。

边界要保留：不涵盖整数断点；不唯一确定整对函数；不控制所有候选元素的边际。K=3、η=2 的两条不同最优增益序列已经说明断点不能直接沿用唯一性。

**J3 尚未写入当前 GitHub 正文，不影响“single-step 分析已经改进”的判断，但影响“正文已展示结构深度”的判断。** 最有价值的后续写作是把 sharp form、两阶段等号轨迹及断点的对偶退化连起来，让精确公式的来源更容易看见。

## 7. 归属核对与仍需同步的文字

Goundan–Schulz 2007 第 7 页 Step 2 使用 `α·chosen marginal≥maximum marginal`，Theorem 1 给出与 L_K(α) 等价的保证。因此 `α=η^sel` 同向，当前 Proposition 5 的归属处理正确。当前 model、results、related 都已明确归属，没有把该经典下界直接列为新结果。[GS 2007 原文](https://optimization-online.org/wp-content/uploads/2007/08/1740.pdf)。

还有少量文字不能据此算作全部完成：

- `notation_table.tex` 仍写 `τ=c+1`，而主定理允许实数 c，应改为 `τ=⌈c⌉+1`；增加正文一句“整数时相等”不会自动修正表格的一般定义。
- `related.tex` 把有限 K 的经典界紧接着称为 polynomial-query “unimprovable”，需要限定到渐近常数；NW 1978 的 partial enumeration 本来就展示了有限 K 的预算与保证权衡。其 “matching bounded-query obstruction” 也宜明确为 asymptotically matching。[NW 1978](https://pubsonline.informs.org/doi/abs/10.1287/moor.3.3.177?journalCode=moor)。
- 主文件的摘要、引言、结论仍以占位或注释为主。注释中的旧校准和较宽叙事不能作为现行定理的验收依据，正式写入时应按本文的算法范围同步。
- F3 的一般结论应在完成构造证明后再作为 theorem 计入贡献；目前应让读者明确看见它的未完成状态，而非由一个 theorem 环境承担过强印象。

## 8. 建议怎样向 Tianming 汇报，以及下一步优先级

可以准确地汇报：

> 我们已经完成了 global marginal-error 模型下 greedy 的精确有限 K 最坏值，并有显式达到实例与一般下界证书；R-step 已删，single-step 分析通过 coherence 得到实质改进。对任意确定性算法，不限查询时的最优保证是 1/η；对固定多项式查询预算、每次大小≤K 的算法，已有渐近匹配的 hardness。任意大小查询的一般多项式版本，以及有限 K 的同预算算法最优性，仍未完成。若允许 O(n^K) 枚举，则 1≤η<K 时已有严格优于 greedy 的最坏保证。我们还需确认您所说的 O(n)K 指哪一种复杂度。

最值得投入的三件事依次是：

1. **把 exact characterization 的证明结构写进主线。** 采用 J3 的 sharp form 与两阶段刚性解释，并保留非断点范围。这直接提高已有核心结果的解释力。
2. **明确第 3 条的验收目标。** 允许枚举时答案已很清楚；若要一般多项式、任意大小查询，缺的是实质 hardness；若要同预算有限 K 的改进，缺的是算法或更紧上界。这三种任务不能相互代替。
3. **处理 F3 的一般证明状态及少量范围措辞。** 先保证主贡献建立在已闭合的证据链上，再决定是否为补充定理投入新研究时间。

我的研究判断是：目前已有一套值得集中呈现的理论结果。其力度来自精确答案、coherence 限制和等号结构；第 3 条尚未解决的更广问题应清楚列出，不需要把它们全部完成才承认已有进展，也不能用已有进展把它们覆盖掉。

## 9. 复核证据与范围

本次新增脚本 `J4_requirements_oracles.py`，输出 JSON 与日志。结果：7 项符号恒等式、253,220 个 all-pairs 增益检查、1,928 个隐藏最优集平均检查、325 组界比较、1,638 个超几何计数检查，全部通过。有限检查只覆盖标明范围，不认证所有自适应算法。

`J4_source_audit.json` 记录固定提交、17 份源码/审查文件的 Git blob 校验、来源 URL、R-step 活跃文本扫描及已采纳状态。对源码作内容与逻辑核对；本次没有重新编译或对 GitHub PDF 做视觉审阅，也没有重新开展实验审计。

一般主证明复用 J2 已完成的证书检查，并读取仓库 H3 的独立复核及采纳后的正文。J3 的等号推理本次重新手工检查，有限 LP 证据复用此前交付。没有改动论文正文或向 GitHub 推送。

主要证据位置：[当前结果与定理](https://github.com/zhiyunjiang0810/sub-modular-optimization/blob/3006b9024017180689c19bf5a49d09ff9bf10029/paper/sections/results.tex)，[当前模型与误差定义](https://github.com/zhiyunjiang0810/sub-modular-optimization/blob/3006b9024017180689c19bf5a49d09ff9bf10029/paper/sections/model.tex)，[当前附录证明及 F3 缺口说明](https://github.com/zhiyunjiang0810/sub-modular-optimization/blob/3006b9024017180689c19bf5a49d09ff9bf10029/paper/sections/appendix_proofs.tex)，[H3 对 J2 的独立复核](https://github.com/zhiyunjiang0810/sub-modular-optimization/blob/3006b9024017180689c19bf5a49d09ff9bf10029/results/H3_j2_assessment.md)。

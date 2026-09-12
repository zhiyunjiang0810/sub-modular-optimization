# Independent theory audit

审计对象：2026-09-11 dossier，以及仓库 main 的固定快照 [`6ea1ab859409e95654015346bd214d8fea46daef`](https://github.com/zhiyunjiang0810/sub-modular-optimization/tree/6ea1ab859409e95654015346bd214d8fea46daef)，提交时间 2026-09-11 10:36:57 UTC。核对了 35 页 `paper/main.pdf`、相应 TeX、THEOREM_LEDGER 和下述脚本。以下 § 编号对应 dossier；括号内另列 PDF 的编号。

**总判断：主定理 §6 的证明闭合，§7 的一般规模刚性证明也闭合；§10–§11 的 hardness 在明写的查询大小、预算和参数范围内成立。没有发现推翻这些核心结果的反例。** 但 dossier 与论文的算法定义不完全一致，若干“精确”标签超过实际证据，§11 的候选算法总结和最优性措辞需要收缩，§13 原有的一个论证方向错误。不能把这些问题解释成“只是审稿人没看懂”。

本审计还得到两项实质进展：

- **§9 的一般小 n 确定性 minimax 值可以闭合。** 下文给出穷举达到 C(n,K,η) 的完整补集损失证明，避开原先失败的交集分解。
- **§13 的 K=4, η=3/2 点已有真正的有理数下界证书。** 本次覆盖全部最优集类型，精确验证 16 份对偶证书，证明该点最坏值为 23/41，并可推广到所有 n≥8。

状态标签只描述证据类型，不代替数学判断。对原标为 [HAND-PROOF-UNREVIEWED] 的步骤，我会明确说明本次是否已人工闭合；人工证明不需要再等待某个“oracle”才能成为证明，也不能因此改称形式化机器证明。新给出的手证宜先按原约定登记为 [HAND-PROOF-UNREVIEWED]、注明来源并由作者复核；这与我在此给出的“已证”判断并不矛盾。

复核范围：N1 对偶脚本 320/320、N2 实例脚本 480/480、T5 tightness 脚本、H_J3 的 2,480 个 LP、H_B `--quick`、L1、J2_core、H3_j2、H_E 均成功重跑。**未复核**：L2/L2R/H_F 的全部分支搜索没有重新跑完；检查了代码、搜索输出和证书验证方式。J4 所称 253,220 次 all-pairs 检查的原始独立脚本未取得，因此该计数未复核。F3、R-step、additive-band 的全部实验亦未重跑。下文不把这些既有计数当成本次独立验证。

## §0 — 模型、量词和三把尺子

**判断：基本模型成立；定义必须补齐，缩放引理应改写。**

1. 明写 n≥K≥1，并在定义 ratio、归一化 OPT=1 时排除 OPT=0，或约定该情形 ratio=1。f≡0 时优化不等式平凡，但 f(T)/OPT 和误差比值中的 0/0 不能不作定义。η^tr 的两个因子应分别写成包含 1 的最大值；零/零边不参与比值，空轨迹的最大值取 1。

2. **区分 prescribed band 和 actual minimal factors。** 建议先定义类别

   \[
   \mathcal F(\eta_u,\eta_o)=\{(f,\tilde f):d/\eta_u\le\tilde d\le\eta_o d\},
   \]

   再定义最小因子为 max{1,sup d/\tilde d} 和 max{1,sup \tilde d/d}。不能把“属于这个类别”和“两个端点均被取到”混用。

3. **Lemma 0′ 的任意缩放句子，按实际最小因子解释是假的。** 取任意非零 modular f，令 \tilde f=2f。最小因子是 (1,2)；缩放 c=1/2 后为 (1,1)，并非声称的 (2,1)。缩放 c=2 又会把形式表达式变成 (1/2,4)，落出因子≥1 的定义域。正确版本是：对于两个合法的预设因子对、且乘积相同，取 c=η_u/η'_u，则 \tilde f↦c\tilde f 给出两个 **band 类别** 的双射，保留 greedy 的 argmax。因此按“误差至多”的类别定义的 greedy 最坏值只依赖乘积。§6 的逐 split 饱和实例另外证明 exact-error 类达到相同最坏值。不要用一次不加限定的缩放替代这两件事。[HAND-PROOF-UNREVIEWED：上述修正版已人工核对。]

4. ρ_K 必须说明 n 的量词。最清楚的写法是先定义 ρ_{n,K}，然后证明 n≥2K 时相同；否则写成对所有 n 的 infimum。不能在 §9 讨论固定小 n、到 §11 又无说明地换成 infimum over n。

5. **dossier 的 greedy 提前停止，PDF 的 greedy 固定执行 K 步。** PDF `model.tex` 的定义及 Proposition 5 都使用 S^K；dossier 用 K*。有限全局误差下两者的目标值相同，因为提前停止已经最优；离开全局误差模型时不同，直接影响 §3 的 per-run certificate，见该节反例。

6. “arbitrary set function”在这里指不额外要求 submodularity。有限误差已经强制 \tilde f 单调且与 f 有相同的零边际位置。应把这一强结构写进模型动机。尤其本文没有学习复杂度定理，也没有从训练误差推出全局 marginal band 的定理。

## §1 — 无误差上界则无统一保证（T1；PDF Proposition 3）

**判断：确定性结论已证；随机版本的陈述需要补上期望。**

附录 B.1 已把 dossier 的 ε→0 草图替换为 γ=K²/[n(n−K)]，得到 E[ratio]≤K/n+γ=K/(n−K)，账目正确。这个手证已闭合，不需要穷举查询策略。[HAND-PROOF-UNREVIEWED：本次人工复核通过。]

PDF Proposition 3 和 dossier 的“for every algorithm … output T satisfies …”没有明确把随机算法改成期望。若读成对每个随机种子成立，就是错误：均匀随机输出 K-set 的算法以正概率输出 O*；n>2K 时该输出的 ratio=1>K/(n−K)。请分成 deterministic 和 E_seed 两句，实例在随机种子之前固定。

“no constant”应解释为没有对 n/K 一致的常数，不是每个固定 n,K 都没有正保证。确定性在允许无限误差时甚至可被迫输出零值；随机情况下均匀 K-set 有 K/n 的一般基线。因此现在这个较弱的 K/(n−K) 数字主要是为了把两个版本写在一起，建议压缩本命题，不要当贡献。

这个命题也不证明“有限的全局乘性 marginal band 是任何保证的必要条件”。它只排除完全没有关联假设的整个实例类；保持候选排序等其他假设也能保证 greedy 的表现。

## §2 — Value accuracy（T2；PDF Proposition 4）

**判断：(i)–(iii) 的数学内容成立；标题和解释需要限定“不充分”的对象。**

- (i) 给出的 f 确实 modular，四个集合的 value band 均成立，d_b({a})=2ε/(1−ε)>0 而预测边际为零。证明的是 **value accuracy 不蕴含有限 marginal error**，不是“value accuracy 对任何算法都不给保证”。例如穷举最大化 \tilde f 总能保证 (1−ε)/(1+ε)。Horel–Singer 也给出小 ε 区域的正面结果，不能概括为全面不可能。[Horel–Singer, 2016](https://thibaut.horel.org/mas.pdf)
- (ii) 缩放保持选择次序的论证正确。它证明不需要小的 value error 来保证良好选择；它不证明全局 η 变小，也不证明 greedy 一般返回 OPT。
- (iii) telescoping 正确，但 max{1−1/η_u,η_o−1} 可能≥1，而本节此前只定义 ε∈(0,1)。把 value-band 定义扩展到 ε≥0，或给 (iii) 加“若此值<1”。例如 η_o=3 时该值=2，不能继续称其落在已定义的 ε∈(0,1) 类中。

建议保持引理/命题级背景地位；不要把它们包装成预测框架新颖性的主要证据。原 [HAND-PROOF-UNREVIEWED] 的简单手证本次均已核对。

PDF Proposition 4 前的解释 “the bound has to be on marginal gains rather than values” 超过了本命题所证内容。应改为“value accuracy need not imply the marginal-gain assumptions used in our bounds”，否则会与上述穷举保证及小 ε 的已知正面结果冲突。

## §3 — GS 保证和逐次运行证书（T3；PDF Proposition 5）

**判断：PDF 的固定 K 步版本已证；dossier 的提前停止版本，若仅假设有限 η^sel，陈述为假。**

反例：K=2、N={1,2,3,4}，

\[
f(S)=|S\cap\{1,2\}|,\qquad \tilde f(S)=\min\{1,f(S)\}.
\]

两个函数都单调 submodular。greedy 先选 1，随后所有预测边际为零而停止。唯一执行的步骤有 M_0=g_0=1，故 dossier 的 η^sel=1；但 f(T)/OPT=1/2<L_2(1)=3/4。停止检查没有被记为“harmful zero step”，所以原来的 ∞ 修补没有覆盖它。附带 `verify_audit.py` 用有理数重现此例。

正确版本任选其一：

1. 如当前 PDF，定义执行 K 步，零预测边际也继续选；
2. 对停止版要求 K*=K 或 M_{K*}=0；
3. 只对已经执行的 m=K* 步给出

   \[
   f(S^m)\ge\left[1-\prod_{t<m}\left(1-\frac1{Ka_t}\right)\right]\mathrm{OPT}.
   \]

   若只保留最大误差，则指数是 m：1−(1−1/(Kη^sel))^m，不能换成 L_K。

**这个反例不推翻有限全局误差下的主线，也不推翻当前 PDF 明写 T=S^K 的 Proposition 5。** 它推翻的是 dossier 停止规则与离模型 per-run 证书拼在一起后的版本。实验实现必须明确遵守哪一个算法。

固定 K 步时，正增益、benign zero、harmful zero 三类已穷尽；逐步乘积界也成立。dossier 残差最后一行漏写乘子 OPT，除非在本节提前声明 OPT=1。归属 GS 正确，α=η^sel 的方向也正确；有限 K 的递推已存在于其证明中。[Goundan–Schulz, Theorem 1 and proof](https://optimization-online.org/wp-content/uploads/2007/08/1740.pdf) 不应计入新贡献。

## §4 — Selection/trajectory tightness（T4；PDF Theorem 7）

**判断：已证。** T5 完整脚本成功重跑；一般 K 的 greedy 归纳没有剩余逻辑缺口：在 (t,0)，B 与 O 的预测边际相等，B 尚未耗尽且增益严格为正，故 adversarial tie 可维持 y=0 到第 K 步。η^sel=η^tr=â 的计算正确。[VERIFIED-SYMBOLIC；归纳本次人工核对。]

边界：K=1 被明确排除，不是假定后漏证；可另用两个 modular 元素补上 1/â 的紧性。â=1 时当前公式仍合法并退化为经典例子，可把 â>1 扩成 â≥1，或明确经典端点另引 NWF。不能据此声称全局误差 η=â：实际全局乘积 (âK−1)/(K−1) 更大。

建议把实例族写作 \mathcal U_K(â)，不要与标量 U_K(η) 混用同一符号。两者的参数需要校准后才可比较。保留 adversarial tie 的定理即可；strict-preference 的端点极限需要另证，不能从内部点扰动直接推出。

## §5 — Coherence 与 sharp form（T5；PDF Lemma 8）

**判断：已证，是主线中真正有辨识度的结构性步骤。**

交换恒等式确实来自同一个集合函数 \tilde f 的两条路径。上下 band 与 greedy comparison 的三项非负 slack 分解正确；sharp form 的第一个不等式只是重排，第二个才使用 f 的 submodularity。η>1、d=g/η 推出 h=g；η=1 时不能作该推论，因为系数消失。H_J3 与 H3_j2 重跑通过。[VERIFIED-SYMBOLIC；一般交换论证已人工核对。]

PDF Lemma 8 的独立陈述宜加“under Definition 1”。e≠e′ 可写明；若允许相等，两条结论都退化为 0≥0，但附录的交换证明只处理不同元素，需要一句说明。

这是全局一致的 value oracle 相比逐步 approximate incremental oracle 的额外约束。应围绕这个区别说明新意，而不是只说“我们改了误差度量”。不过，本审计核对的是与 GS 的区别，不等于证明所有历史文献中均无相同观察。

## §6 — 精确 greedy 最坏值（T6；PDF Theorem 9）

**判断：已证。建议将“一般 K 装配尚未审查”改为“本次独立审计已人工闭合”，保留 [VERIFIED-SYMBOLIC] 的准确范围。**

### §6.1 有效约束

置零没有漏洞。对 coherence 约束分三类：尚未选择且不同于 e_t 时用 §5；o_i=e_t 时 g_{t,i}=d_t、g_{t+1,i}=0，两端都是零；已经选择时 g_{t,i}=g_{t+1,i}=0，约束为 0≥−d_t。最后一种一般不是“等号”。dossier 的“equality of both sides≤0”应换成这三句；附录 B.13 已正确区分。

(C) 的 telescoping 与单调性使用正确，不要求 S^t 与 O* 不交。有限 band 下提前停止已经达到 OPT，可把后续 d、g、r 全部补零；四类约束仍成立。或者如 PDF 直接分析 K 步算法。故 §16 问题 1 不构成主定理缺口。

删去 (M) 的 LP 行不会破坏该下界证书，但不能删去 f 的单调性假设；也不能在 §7 的末状态证明中省略 (M)。

### §6.2 对偶证书

我逐项核对了附录 B.6 的 nonnegativity、g 系数、d 系数和常数项。分类 t=0、1≤t≤j−1、t=j、j+1≤t≤K−1、t=K，加上 j=0 特例，穷尽全部坐标；空区间无需另作归纳。d 系数以 t=j−1 为基例向下递推，闭合。

闭区间端点没有负乘子。唯一表面奇点是 j=K−1、η=1：应按已写的消去式定义 λ_P(K−1)=1/K、λ_coh(K−1)=0，而不是直接计算 0/0。源文件随后用连续性处理该端点，合法。K=2 的 worked example 系数和常数项亦正确。

N1 重跑 **320/320 PASS**。这加上有限分类的人工核对，已经是一般 K 的证明；无需把一个穷尽分类永久留作未完成任务。

### §6.3 显式实例

N2 重跑 **480/480 PASS**。当前论文用 capped family，并明确 η≥K−j；其危险边只有 y=K−1 的 O 增益，ηq^{x−j}≥z 由 x≤j、z≤K−j≤η 保证。该条件不能从 capped family 的全参数陈述中省略。未 capped 版本可放宽范围，但不要混用两个公式。

两阶段 greedy 归纳、OPT=1、误差端点达到和输出 V_j 均闭合。实际误差严格为给定 split 的结论来自端点见证，不是有限精度计算“看起来相等”。

附录“这是断点的来源”的解释应收缩：capped family 的可行性边界碰巧在这里；决定最小分支的是 V_i−V_{i+1} 的符号，uncapped family 在更大范围仍合法。§6.3 中“j=0 是 §10 的 modular 实例”也是错误引用：应指 §9 的对称 modular 天花板实例；§10 的 F 一般不是 modular。

### §6.4 定理范围

η=1、整数 η、零增益与 adversarial tie 均有合法处理。K=1 可单列 ρ_1=1/η，不应把 K≥2 的 q/k_1 论证原样套过去。对于固定 n<K 或 K>n，现定义没有意义，应在 §0 排除。

新增 must-not-claim：不能把“完整数值 LP 与 reduced LP 一致”本身称为一般 K 证明；一般证明是有效性＋对偶＋可实现实例。也不能把 adversarial-tie 下的 attained minimum 自动称作任何 tie-breaking 算法的 attained minimum。

## §7 — 最坏轨迹刚性（T6b；PDF Proposition 10）

**判断：已证，包括一般 K；dossier 对最后一步的摘要省略了必要约束。**

内部区间的正支撑确实为 coverage t≤j、coherence t≤K−2、prediction t≥j；j=0、j=K−1 的空段也正确。前向残差递推、t=j 的对称性推导、冻结段和向后逐坐标回推都不预设最优边际对称。H_J3 重跑的 **40 个面、2,480 个 LP，最大偏差 3.94×10^−15** 与公式一致。[VERIFIED-SYMBOLIC]＋[VERIFIED-LP]，一般互补松弛证明已人工核对。

**末状态不能只用 (P)+(M)。** 还必须用乘子为零但仍有效的末步 (S)：

\[
0=d-g/\eta\ge(1-1/\eta)(g-h)\ge0.
\]

η>1 才推出 h=g。PDF 附录 B.7 Step 7 完整写了这一步，因此这是 dossier 的省略，不是论文的残留缺口。

注意两个记号系统：PDF λ_S 是 sum/coverage 的乘子；dossier 的约束 (S) 却表示 coherence。右端点消失的 (K−j+1−η)/k_1 是 **coverage** 乘子，不能解释成 coherence(j) 消失。例如 K=3,j=1,η=3 时 coherence(j) 的乘子为 1/6，仍正。

断点处两条 7/15 轨迹正确；唯一性不能延伸。当前“仅约束所选增益与固定 O* 的边际”的范围正确。近等号 slack≤ε/λ 是有效的逐约束结论，不是全轨迹距离界，尤其不能在退化端点声称统一稳定性。

## §8 — 渐近和 K 单调性（T9；PDF Corollary 16）

**判断：(a)–(c) 已证，均依赖 §6；有一项验证来源写错。**

H_B `--quick` 与 L1 成功重跑。c(η)、d(η,⌊η⌋)、c 的极大点、ρ_K−L_K 的一阶项及 U_K−ρ_K 的二阶项没有发现算术错误。[VERIFIED-SYMBOLIC，conditional on §6。]

§16 问题 4 的尾界成立：对 x>1，逐项用 1/i≤1/3（i≥3）得到

\[
-\log(1-1/x)\le 1/x+1/(2x^2)+1/[3x^2(x-1)].
\]

变量变换 s=t/(1+t) 覆盖 [0,1)，m=⌊η⌋≥1、K≥m+1 的域没有遗漏；重跑得到分子 84 项、无负系数、常数 14，分母 165 项、无负系数，结合原分母各因子为正，严格正性闭合。平台首次下降使用 K=m+1>η；整数 η 取左端 s=0，已经包含。故不必继续把 tail bound 留成未解决技术步骤。

**证据来源更正：** dossier 称“Richardson from reduced LP, K=50..800”。`H_B_asymptotic.md` §1 与脚本明确写大 K 外推使用闭式、Fraction 和 mpmath；LP 只是另行对拍，不能说 K=800 的 LP 独立确认了展开。本次也只跑 `--quick`，没有重做大 K LP。

轻微笔误：(a) 的 L_K、U_K 两端趋于 1−e^−1/η，不是 e^−1/η。统一 O 常数、η 随 K 增长、凸性及单实例 ratio 的 K 单调性均不由本节推出。

## §9 — 信息论天花板及小 n 的完整闭合（T8；PDF Theorem 14）

**判断：n≥2K 的确定性最优值与随机上界已证；小 n 的 [CONJECTURE]/[OPEN] 可以用以下一般证明解决。**

原 n≥2K 手证正确。若输出大小 s<K，f(T)=cs/η_o 和 E|T∩O|=sK/n，不能写成等于 cK/η_o 或 K²/n，但所需不等式仍成立。c 应取正。随机量词为“对每个随机算法，存在一个固定实例，使种子期望满足界”；不是给每个种子重新选 O。[HAND-PROOF-UNREVIEWED：本次已人工核对。]

### 新的一般达到证明

令 K≤n≤2K、ℓ=n−K。穷举输出一个大小恰为 K 的 \tilde f 最大集合 T；有限 band 使 \tilde f 单调，所以从 ≤K 的最大集合补足到 K 不损失保证。令 R=N\T，R*=N\O*，并定义删除损失

\[
h(A)=f(N)-f(N\setminus A),\qquad
\tilde h(A)=\tilde f(N)-\tilde f(N\setminus A).
\]

**Step 1：h 是 normalized monotone supermodular，且其边际满足同一误差带。** 对 e∉A，

\[
h(A\cup\{e\})-h(A)=d_e(N\setminus(A\cup\{e\})).
\]

因此从空集 telescoping 后 h(A)/η_u≤\tilde h(A)≤η_o h(A)。R 最小化大小 ℓ 的 \tilde h，所以

\[
h(R)\le\eta_u\tilde h(R)\le\eta_u\tilde h(R^*)\le\eta h(R^*).\tag{9.1}
\]

**Step 2：h(R*)≤(ℓ/K)f(T)。** ℓ=0 时 T=N，结论直接为 1；以下设 1≤ℓ≤K。从 T 均匀选大小 ℓ 的 A。R* 是所有 ℓ-set 中 h 的最小者，故

\[
h(R^*)\le\mathbb E h(A)\le\frac{\ell}{K}h(T)
\le\frac{\ell}{K}f(T).\tag{9.2}
\]

中间一步是 supermodular averaging：若 a_s 是 T 的均匀 s-subset 上 h 的平均值，则 a_{s+1}−a_s 非减（在随机排列前缀上用 increasing marginal returns），a_0=0，故 a_ℓ/ℓ≤a_K/K。最后一步由 R∩T=∅、R∪T=N 及 supermodularity 得 h(R)+h(T)≤h(N)=f(N)，从而 h(T)≤f(N)−h(R)=f(T)。

**Step 3：配平。** 不需要除以 h(R*)，因此它为零的情形也覆盖：

\[
\begin{aligned}
f(O^*)&=f(T)+h(R)-h(R^*)\\
&\le f(T)+(\eta-1)h(R^*)\\
&\le\left(1+\frac{\ell}{K}(\eta-1)\right)f(T).
\end{aligned}
\]

所以穷举保证

\[
\boxed{\frac{f(T)}{\mathrm{OPT}}\ge
\frac{K}{K+(n-K)(\eta-1)}
=\frac{K}{(2K-n)+(n-K)\eta}.}\tag{9.3}
\]

### Matching hardness 与边界

对确定性算法使用 \tilde f(S)=c|S|。先固定它的输出并补足为 K-set T。令 N\T 的 ℓ 个元素真权重为 cη_u，T 的元素真权重为 c/η_o。最优解选全部 ℓ 个高权重元素及 K−ℓ 个低权重元素，输出 ratio 恰为 (9.3)；若原算法输出不足 K，ratio 只会更低。n>K 时两端点都达到，因此任意合法 split 的实际误差也恰好满足要求。

至此，对 **预设 band 类、固定 n,K、确定性算法、任意查询数量及大小**，

\[
\boxed{\alpha^*_{\rm det}(n,K,\eta)=
\begin{cases}
\displaystyle\frac{K}{(2K-n)+(n-K)\eta},&K\le n\le2K,\\[2mm]
1/\eta,&n\ge2K.
\end{cases}}\tag{9.4}
\]

n=K 给 1；n=2K 两支相接；η=1 给 1。n=K=1 时若坚持“两个最小因子都严格大于 1 且均饱和”，实例类可能为空，故总定理应以 prescribed bands 表述，另陈述非退化参数的 exact-error witness。

这个证明解决了 §16 问题 5：**达到算法就是穷举；恰好 K 个元素是一个可以免费保证的输出规范。** 原交集 f(T∩O*) 可能为零的障碍真实存在，但不是定理的障碍。没有借用那个错误中间断言。

新手证建议先登记 [HAND-PROOF-UNREVIEWED] 并请作者独立核对；本审计的数学判断为已证。原 H_E 的 18 个算法侧 LP 已重跑通过，附带 verifier 也精确检查了上述中间不等式的实例，但一般性来自证明，不来自有限网格。随机 minimax 仍为 [OPEN]；不能把 (9.4) 用作随机算法的固定 n 上界。

## §10 — 有界大小查询 hardness（T10；PDF Theorem 17）

**判断：在原文假设内已证。** J2_core 和 H3_j2 的边表与校准检查重跑通过；canonical transcript 及两次平均本次人工闭合。[VERIFIED-SYMBOLIC]＋已复核的一般手证。

先固定 canonical transcript，再对随机 O 作 union bound，这个顺序正确。适应性没有破坏独立性：只需对固定的 canonical queries 计数，再用相同历史迫使实际第 i 次查询相同。算法的查询上限需对每个 seed/合法执行成立；只限制期望查询数不是同一陈述。

令 p_bad 为查询失败概率，在 n≥4K^{c+2} 下

\[
p_{\rm bad}\le\frac{K^{c(c+1-\tau)}}{4^{\tau+1-c}(\tau+1)!}\le1/32,
\]

因为 τ=⌈c⌉+1≥c+1；输出相交概率≤K²/n≤1/4，常数充分。没有必要把这条有限分类的初等计算继续留作疑点。

随机版 K/n 是正确的，来源不是 P(T_0∩O≠∅)，而是 |T_0∩O|/K 的期望。附录的点态式

\[
\mathrm{ratio}\le H_{K,\tau}+|T_0^{(r)}\cap O|/K+\mathbf1[E_r^c]
\]

足以换序平均得到一个固定 O。固定 K、c 时 n→∞，ε_n→0；若 K 也增长必须另给增长条件。n≥4K^{c+3} 是固定 c 下的充分条件。

η≥(K−1)/(K−τ) 是 θ≥1 的真实适用条件；不能写成“每个 η>1、每个 K>τ”都直接成立。固定 η>1、固定 c 后，足够大的 K 会满足它。η=1 的一般 n^c 查询渐近最优性不能直接引用本定理，需要另接精确 oracle 的结果。

**必须突出 query-size 限制。** 当前 hard family 在精确 value-oracle 模型下被 n+1 个大集合查询识别：

\[
G(N)=1,\qquad
G(N\setminus\{e\})=
\begin{cases}
1,&e\notin O,\\
1-a^{n-K+\tau}/(K-\tau),&e\in O.
\end{cases}
\]

逐个查询 N\{e} 就识别 O，并输出最优解。差值很小不影响精确 oracle 下的反例。**这不反驳原定理；它证明当前构造不能支持取消查询大小限制的推广。** 当 K≥2 时 n+1≤nK，因而这一限制对“greedy 同预算”叙事尤其重要。

H_{8,3}(2)=1−(10/11)^8≈0.53349262>1/2 的例子正确。min{H,1/η} 只可直接用于确定性；随机版本需取其对应随机上界的 min。

## §11 — Greedy 同预算类与候选算法（T10b/T11；PDF Corollary 20）

**判断：天花板和 O(K^−2) 间隙已证；一般有限 K 最优性仍未证；候选总结必须改。**

### 同预算天花板

τ=1 的计数正确：查询失败≤K^5/(2n)，输出相交≤K²/n；n≥4K^5、K≥2 时总和≤1/8+1/32。L1 已重跑通过。结合 §6、§9 得到的是

\[
\rho_K\le\alpha^*_{\mathcal A_{lin}}\le\min\{U_K,1/\eta\}.
\]

不是已经解出了 α*。**PDF Corollary 20 的标题 “Optimality within the greedy query budget” 过强**，建议改为 “An upper bound within the greedy query budget” 或 “Near-optimality within the greedy query budget”。正文随后承认 open，不会自动消除标题造成的误导。

固定 η>1 的二阶间隙公式正确；c′ 的整数连续性也正确。但 min 上界不总等于 U_K。只有在固定 η、足够大的 K 时，U_K<1/η，才能把区间宽度直接写作 U_K−ρ_K。η≥K 时区间宽度是 0，虽然 U_K−ρ_K 仍可能正。随机版在 n=4K^5、K→∞ 时 ε_n 的第二项为 1/8，不能自动消失；n/K^5→∞ 才让该项消失。

**η=1 可补回此 corollary。** τ=1 时 θ=1、F=G，边表与 canonical transcript 仍合法，且 U_K(1)=ρ_K(1)。因此对于 n≥4K^5、size≤K 的 nK 查询类，η=1 也有精确最优性；不必把它留作空白。K=1 可由查询所有 singleton 与 §9 单独解决。

### 固定 n 的量词不能省

若把 conjecture 写成“对所有固定 n≥2K，greedy 在 nK 预算内最优”，它已被反驳：K=2,n=4,η=3/2 时，穷举全部 6 个二元集合只需 6≤nK=8 次查询，保证 2/3；greedy 的精确保证为 3/5。差为 1/15。这个反例不触犯 n≥4K^5 的原 corollary，但要求 conjecture 明写其 large-n 范围，或明确它是对 n 取 infimum 的算法族问题。

一般 n^c 类的适用条件应是 nK≤n^c，而不是统一禁止 c<2。例如 c=3/2 且 n≥4K^{7/2} 已包含 greedy。“单查询可被逼到 0”只讨论 c=0，不能证明 c=1 的一般最优值。保留实际包含关系及固定 c、η、联合增长条件即可。

### 三个候选的证据

1. **PE_1 不是所定义的线性查询算法。** 对每个 singleton start 再跑 greedy 的直接最坏查询量是 O(n²K)，没有给出保证≤nK 的实现。它也不是“所有结果不超过 greedy”：dossier 自己给出 K=3,n=6,η=3/2 的 19/29>9/16，差 43/464。它可以说明真实值不可用于最终选优的困难，但不是对整个 \mathcal A_lin 的排除证据。
2. shortlist 的算法确实落在所述预算类，给出的数值是有限范围 [VERIFIED-LP]；一般闭式仍为 [CONJECTURE]，不能由逐位匹配升级。
3. swap pass 超过 nK；其行为还必须固定是按顺序接受每次弱改进，还是每个位置只接受第一次、是否拒绝 tie。`L2_linear_candidates.py` 把 accept/reject 两支都写成非严格不等式，实际分析的是 adversarial choices at ties，不能泛称所有“one swap pass”。

**“精确分数值”标签有实质证据缺口。** `L2R_finish_k3n7.py` 278–284 行先把浮点 LP 最优值 rationalize，再标作 exact；JSON 明写 “1e-9 pruning/LP tolerance”。286 行的 consistency check 也是浮点，293 行只在候选优于 ρ_3 时才调用 exact_witness。因此 31/51、37/69 的输出不是双向有理数最优证书。H_F 的搜索同样用 1e−9 比较剪枝。完整遍历离散分支不等于每个连续 LP 都精确求解；仅有可行实例也只能证明上界，不能证明最坏值恰好等于该分数。

正确标法是 **[VERIFIED-LP：有限参数、浮点求解，未在本次完整重跑]**；精确等式须补每个相关分支/剪枝节点的有理数对偶或带向外舍入的可靠下界，以及最优分支的精确可行见证。当前数据足以作为计算证据，不能写成“严格 STOC 意义下逐格精确最优”。

## §12 — 任意大小查询（T12）

**判断：保持 [OPEN]/[CONJECTURE]，不是定理。** 已检查论文对本节的限定；没有独立复跑 F3，也没有取得一般参数合法性和随机平均中所需的不等式证明。48 个有限参数不能推出一般 switching-index 公式，更不能推出 arbitrary polynomial queries 的结论。

建议正文只用一句说明 unrestricted-size query optimum 尚未解决。附录若保留，应把 conjectural statement、已验证范围和失败步骤分开；“candidate construction removes the cap”也应理解为目标，而非已完成结果。§10 的 N\{e} 攻击应作为新构造必须通过的第一项检查。

## §13 — Submodular surrogate（T7；PDF Remark 13）

**判断：一般 W_m 上界实例可由简短手证闭合；一般 matching lower bound 仍 [OPEN]。dossier 用实例证明 U_K 失效的理由不成立，但其结论现在可以在一个点精确修复。**

### 一般上界实例

检查 `H_C_submodular_surrogate.md` §6 的公式。令 D=1+(η−1)r^m、c=cut(S)，则

\[
c_{max}=(1-r^m)/D,\quad
1-c_{max}=\eta r^m/D,\quad
A_0-\eta_o c_{max}=\eta_o r^m/D.
\]

两函数的 mixed second differences 为 −d_t/K 或 −η_o d_t/K，其余相应二阶差为零，因此 submodularity 对一般参数成立。上述端点确保 O 边际非负；早期 B 边际为 d_t(1−y/K)，后期为 d_t。O 边际比

\[
R(c)=\eta_o\frac{1/D-c}{1-c}
\]

非增，最小值是 1/η_u，B 比值为 η_o。每个 singleton 真值≤1/K，submodularity 给所有 |S|≤K 的 f(S)≤1，O 达到 1。逐步 predicted tie 和求和得到 W_m。故这一上界不必仅以“410/410”支撑；一般手证已闭合。m=0 与 η=1 都包含。

### 原来失效的逻辑与本次修复

“存在实例 ratio=W>U”不能证明 worst-case ratio>U：infimum≤W，与≤U 并不矛盾。`H_C_submodular_surrogate.md` §6 第 3 点及 dossier 的 “instance-backed” 因而是错误论证方向。K=4 起原材料部分 LP 又只固定不相交 O，不能自动替代所有 optimal-set overlap 类型的下界。

**本次补了真正的下界。** 固定 K=4,n=8,η_u=1,η_o=3/2，把 greedy 序列重标为 0,1,2,3。未选元素可任意置换，所以 O* 与这四个位置的交集有 2^4=16 个代表类型，覆盖全部 70 个四元最优集。为每类求出对偶后，独立用 Fraction 精确检查：乘子符号、全部变量系数等式、目标常数。16 个对偶下界都≥23/41，不相交类恰为 23/41；上面的 m=2 实例给出相等方向。因此

\[
\rho^{sub}_{8,4}(3/2)=23/41,
\qquad 23/41-U_4(3/2)=5463/600281>0.
\]

证据是 **[VERIFIED-SYMBOLIC：有理数证书恒等式]＋[VERIFIED-EXHAUSTIVE：全部 16 个轨道代表]**。`submodular_K4_exact_duals.json` 和不依赖 solver 的 `verify_audit.py` 随报告交付；后者还精确验证了匹配实例的完整格点、误差、OPT 与 greedy 轨迹。

### n 的范围可以扩大，但不能只靠 padding 的一个方向

对 greedy 的最坏值，任意运行都可限制到 T∪O*，大小≤2K：所有已选元素仍存在，greedy 比较仍成立，restriction 保留两函数的 submodularity 与 band，O* 仍最优。再加零 dummy 至 2K 个元素。反方向，把 2K 元素实例 padding 到任意 n≥2K。故在 prescribed-band、adversarial-tie 模型中

\[
\rho^{sub}_{n,K}=\rho^{sub}_{2K,K}\quad(n\ge2K).
\]

因此上面的精确 K=4 点也对所有 n≥8 成立；一般 W_m 上界亦可 padding 到这些 n。dossier 的“不能说任何 n≠2K 的结果”过于保守，应改成“不能未经 restriction＋padding 证明便宣称 n 无关；n<2K 另论”。

仍不得声称一般 ρ_K^sub=min_m W_m、所有 η 都严格改善、或给出该模型的一般渐近最优值。一个修复后的精确点不等于一般 matching lower bound。

## §14 — R-step 与 additive band（T13/T14）

**判断：有限 R=2 LP 仅保留 [VERIFIED-LP，未复核]；additive 保证的代数正确，tightness 范围需收缩。**

“K=4 的三个点相等，hence fixed R 不改变极限”这一推理不成立。若要保留极限句，可给真正证明：固定 η>1 和 R、K 是 R 的倍数时，对最优集中 R 元素的随机子集平均得到每个 batch 至少覆盖 R/K 的 residual；band 给出 L_{K/R}(η) 下界。该算法只有 O(Kn^R) 个、大小≤K 的查询，取适当固定 c、再用 §10 的大 n hardness 得到同一极限。非整除的尾块应明确处理。这是新的证明拼接，不是三格 LP 的推论；没有必要为其保留完整 R-step 主章节。

对 additive band，greedy 比较给

\[
d_{chosen}\ge M_t/\eta-2\varepsilon/\eta_o.
\]

解 affine residual recurrence 后恰得 L_K(η)(OPT−2Kη_u ε)，系数方向正确。若提前停止，需加相应零步处理；若右端负，保证只是平凡界。所谓“ε term tight in the LP”必须列出算法、K,n、η、ε 范围及双向证书，不能升级成任意参数的 tight theorem。单元素 additive ε 逐链会累积 |B|ε，不能把本节的 additive all-pairs 版本当作 §0 纯乘性 telescoping 的同义改写。

## §15 — 实验使用的一致性（T15）

**判断：当前分母方向和 coverage 任务的资格区分正确；需同步 §3 的停止规则，并收缩“learned surrogate 已得到认证”的表述。**

greedy-on-f≤OPT，因此图中 f(T)/f(greedy_f) 是真实 approximation ratio 的上估计。这些点落在理论下界以上，不能独立验证理论下界，因为真实 ratio 可能更低。人工构造、真实 OPT 已知的实例才承担相应校验角色。

H3_j2 重跑确认 E2 的 16 条 K=30 轨迹含 harmful zero steps，对固定步数 η^sel=∞、certificate=0 的处理正确。是否有未记入的提前停止需按实现另查，不能只根据已执行步的表格排除 §3 反例。

只有 hindsight f 可查询仍不够：计算 η^sel 需要每个已访问状态的全部候选真边际，不是只记录选中元素的增益。当前文字允许 hindsight 查询，可以成立；但它不是 prediction-only 算法在线计算的证书。

论文中满足理论结构的 E2 surrogate 是观察子图上的 coverage；真正 learned 的 feature-selection 目标不在 monotone-submodular 模型内。故实验支持“误差诊断＋一个结构合法任务”，尚未证明一般学习方法会产生满足全局 marginal band 的预测器。不要把 diagnostics 或平均预测精度用于背书这一全局假设。ρ_K 只能画在正确的全局误差轴上，这一禁令应保留。

## §16 — 八个重点问题的直接回答

| 问题 | 独立结论 |
|---|---|
| 1. (S) 的最优元素置零；早停 (C) | 正确。按三类逐项检查；有限 band 早停最优，补零。离模型 η^sel 早停证书另有 §3 反例。 |
| 2. 一般 K dual、闭端点、t split | 闭合。η=1 的 0/0 需用已给的消去定义；所有坐标类别穷尽。N1 320/320 重跑。 |
| 3. (S) 正支撑及末步 locking | 内部区间正支撑正确；末步需要有效 (S)+(M)+tight (P)。PDF 已写，dossier 摘要漏 (S)。 |
| 4. 单调性 tail bound 与整数 | 正确，已人工证明尾界并重跑正系数证书；整数对应 s=0，首降单独成立。 |
| 5. 小 n 达到性及输出 K | 已在 §9 给一般补集损失证明；穷举输出恰 K 可免费规范化；确定性 C 完全闭合，随机仍开放。 |
| 6. transcript、常数、ε 量词 | 闭合；固定 canonical queries 后 union bound，实例独立于 seed。联合极限需 n 随 K 足够快增长。 |
| 7. 跨结果一致性 | L≤ρ≤U=H_{K,1} 正确；一般 H≥U；U、H 不总≤1/η。大误差 plateau 与穷举/预算类界一致。 |
| 8. 标签是否过度声称 | 是：L2/L2R 的“精确分数”；candidate 算法预算/总结；Corollary 20 标题；§13 原错误方向。§6–§8 的一般手证则已经能够闭合，不必永久降格。 |

应追加 must-not-claim：随机算法逐种子满足确定性界；由停止前 η^sel 得 L_K；任意 c<2 都不含 greedy；所有 n 上 greedy 同预算最优；PE_1 属于 nK 类；浮点分支穷尽等于精确有理最优；存在高 ratio 实例证明 worst-case 下界；小查询 hardness 已解决 unrestricted query optimum；本论文证明了 learned predictors 满足全局误差假设。

## ICLR oral 标准下的贡献与叙事

**真正值得做主线的是 §5→§6→§7，以及 §11 对同预算改进空间的限制。** §5 识别“同一个预测集合函数”带来的跨状态约束；§6 给出每个有限 K 的精确答案与达到实例；§7 解释达到等号为什么必须有两阶段结构。这个组合超过了单纯重述 GS。§10–§11 让精细 greedy 分析与“其他算法能好多少”建立了联系，但结论必须一直带着查询大小限制。

§9 现在可以升级为所有固定 n 的确定性信息论 characterization，证明短、结构清楚，值得保留。§3–§4 是读者进入问题的基线与标尺校准，不能各自算一个主要创新。§8 的二阶差距解释 §11 有用；c(η) 在何处最大、长 Richardson 表、逐格失败候选、R-step 和大段历史修复记录应移出正文。§12 未闭合的方向、§13 一般 lower bound 及 additive 实验适合 future work/附录。

建议叙事顺序：**oracle 模型与经典基线 → coherence → exact greedy 与 equality structure → 全信息 minimax → bounded-size nK-query near-optimality → 模型的未解决范围。** 两个“不必要/不充分”命题压缩处理，避免读者前半篇仍以为贡献只是换误差指标。

最可能被攻击的三处：

1. **结构假设与学习场景的距离。** 全局乘性边际带强制零边际位置完全一致；当前合法实验又主要是 coverage proxy。需要解释这一模型为何值得研究，而不是暗示通常的预测准确性自然蕴含它。
2. **其他算法的上界范围。** 当前答案只覆盖 bounded-size queries；同预算类的一般有限 K 最优值还留 O(K^−2) 区间，且 small-n conjecture 可能因量词不清直接为假。审稿人会先看这些限定是否进入摘要、标题和 theorem statement。
3. **证明证据的可靠性。** 核心一般定理已有真正证明，应展示它们；候选算法的浮点“exact”与 dossier/台账/源文件不一致反而削弱可信度。不能用“数千测试全过”替代一个缺失的下界方向。

我的评价是：**已具备一篇有实质内容的理论论文的核心，但目前不能据此判断达到了 oral 强度。** 有限 K 的精确结构和近最优预算界有价值；主要渐近常数仍是经典常数，且强模型假设和 query-size 限制压缩了影响范围。口径严谨是必要条件，不能单独制造 oral 级分量。

### 最值得再做的一个结果

优先解决 **任意大小查询下的多项式查询最优常数**：证明仍为 1−e^−1/η，或给出大集合查询算法严格打破它。两种答案都比继续验证几十个小 LP 点更有分量，也直接回答导师的“在整个框架下任何算法能做到多好”。

若走 hardness：可尝试隐藏分区的 symmetry-gap blow-up，让 canonical surrogate 在所有查询大小对应的 overlap 集中带内不可区分，再用浓缩与 transcript。真正难点是同时保持 f 的 submodularity、同一个 \tilde f 的可积性、全域 marginal band 的端点校准，以及 N\{e} 附近的合法性。当前 saturating construction 的零边际会泄漏 O，必须先消除这个泄漏；value-noise 的 smoothing 不能不经边际分析便照搬。这个建议是证法方向，**不是已有证明或成功概率保证**。

若这个方向短期不能闭合，宁可明确保留它为主要开放问题，也不要用“all polynomial-query algorithms”概括 §10。本次补全的小 n minimax 已经增加了一个完整结论，但不足以替代上述访问模型缺口。

## Severity 分级

### 严重

- **§3 / T3：** dossier 的停止版 η^sel 证书存在 1/2<3/4 的反例；PDF 固定 K 步版不受影响。必须统一算法与实验定义。
- **§11 / T11：** 浮点求解、容差剪枝与 rationalize 不能支持精确有理最优值；“三个线性预算候选均不超过 greedy”的总括同时违反预算分类和 PE_1 已列数值。
- **§11 / T10b：** 最优性标题与一般有限 K conjecture 必须带范围；若声称所有固定 n，K=2,n=4 的穷举反例直接否定它。
- **§13 / T7：** 用坏实例给 worst-case 下界的方向错误。本次已在 K=4,η=3/2 点以精确对偶修复，但一般 matching lower bound 仍开放。
- **§10–§12：** 若摘要或口头叙事去掉 query-size 限制，就是实质过度声称；原定理本身没有被反驳。

### 中等

- **§0 / Lemma 0′：** actual factors 与 prescribed band 的缩放混用；ρ_K 缺 n 量词；OPT=0 与空/零比值约定不全。
- **§1 / T1：** 随机版本漏期望；no-constant 的参数增长范围不明确。
- **§8 / T9：** 把由闭式作的 Richardson 外推说成大 K reduced-LP 独立验证。
- **§11：** c<2 的统一排除不正确；随机联合极限和 min{U,1/η} 的生效范围必须明写。
- **§14：** 三个有限点不能推出 R-step 极限；additive tightness 尚无一般参数证据。
- **§15：** 学习实验、合法理论任务、离线证书和全局 band 的支持关系需明确，避免将 diagnostics 当作模型验证。

### 轻微

- **§2：** (iii) 的 ε 可能超出此前定义域。
- **§3、§6、§7：** 残差漏 OPT、j=0 引用错节、置零等号摘要不准确、末步漏写有效 coherence、两套 S/C 记号互换。
- **§4、§8：** 实例族与 U_K 标量同名，K=1/â=1 可补；极限句漏 1−。
- **版本管理：** THEOREM_LEDGER 的 T9 同时保留旧的 monotonicity [OPEN] 和后来的已证记录；历史结果文档也有过时“唯一缺口”等句。应给每卡一个最终状态，历史另存。PDF 当前还显示 “Published as a conference paper at ICLR 2027”，来自 `main.tex` 的 `\iclrfinalcopy`；它是已知模板开关，提交前必须去掉，不能作为事实陈述。

## 给导师的三句话

核心 exact-greedy 定理、一般 K 刚性和带明确查询大小限制的 hardness 已通过独立证明检查，贡献已经超过 GS 的经典近似 greedy 保证。当前最大的风险是停止版证书、浮点“精确”标签及有限预算最优性范围的过度声称；本次还补出了所有小 n 的确定性 minimax 证明，并为 submodular-surrogate 的一个关键点提供了精确对偶证书。若目标是 ICLR oral，下一项最有分量的工作是解决任意大小查询的算法上界或给出突破，而不是继续扩充小规模 LP 表格。

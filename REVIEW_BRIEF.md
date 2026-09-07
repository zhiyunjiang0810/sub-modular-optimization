# REVIEW_BRIEF.md — 联合审查交接文档（写给零上下文的外部审查者）

写作日期 2026-09-07。本文档自足：不需要读过仓库任何其他文件即可开始审查。
读完本文档后，审查所需的原文位置与复现脚本在第 8、9 节。

---

## 1. 前因：这个项目是什么

一篇理论论文的改稿：**submodular maximization with predictions**。原稿投过
TPAMI（原文完整保存在 `legacy/tpami_submission/`），被审稿人指出若干实质问题
（近似比方向写反、一个号称 robustness 的引理并无证明、误差度量的动机不足等，
清单在 `RESEARCH_STATE.md` 的"已知的论文错误"节）。现在目标是 ICLR 2027，
论文骨架已装配完成（`paper/main.pdf`，27 页，编译 0 错误），abstract 与
introduction 留白待人写，其余各节有实质内容。

改稿不是修修补补：理论主干在六个通宵会话里全部重做并大幅加强。本文档
第 4 节逐条列出现有定理、证明方法与验证状态。

**最重要的工作规则**（`CLAUDE.md`，审查时请按同一标准执行）：任何数学断言
的状态由 oracle 决定，不由信心决定。可用 oracle 三种：数值 LP/穷举
（scipy）、符号恒等式（sympy）、小实例全格点穷举。状态标签体系：

- `[VERIFIED-LP]`：数值 LP 或穷举确认，附一键复现脚本；
- `[VERIFIED-SYMBOLIC]`：sympy 符号恒等式确认，附脚本；
- `[HAND-PROOF-UNREVIEWED]`：有手写证明但无 oracle，**这是审查的主攻对象**；
- `[CONJECTURE]`：数值支持但无证明；
- `[FAILED]`：尝试过不成立或未完成。

标签写在 .tex 源码注释与 results/ 的 md 文件里；PDF 正文不显示标签（这本身
是一个已被内部审稿记录的问题，见第 7 节）。

## 2. 模型与记号（论文 Section 2，`paper/sections/model.tex`）

- 基础问题：ground set $N$，$|N|=n$；monotone submodular $f:2^N\to\mathbb R_{\ge0}$，
  $f(\emptyset)=0$；基数预算 $K$；目标 $\max_{|S|\le K} f(S)$。
- **关键模型设定：算法不能查询 $f$，只能查询一个 predictor $\tilde f$**
  （$\tilde f(\emptyset)=0$，除此之外无任何结构假设，这是定案 D1）。
- 边际增益 $d_e(S)=f(S\cup\{e\})-f(S)$，预测增益 $\tilde d_e(S)$ 同理。
- **误差模型（Definition 1）**：$\tilde f$ 有 (single-element, multiplicative)
  误差至多 $(\eta_u,\eta_o)$，若对所有 $S$ 与 $e\notin S$：
  $d_e(S)/\eta_u \le \tilde d_e(S) \le \eta_o\, d_e(S)$。标量误差
  $\eta=\eta_u\eta_o$。注意这蕴含 $d=0 \Leftrightarrow \tilde d=0$ 且预测增益非负。
- 近似比约定：$\alpha\in(0,1]$，$F^{ALG}\ge\alpha F^{OPT}$，越大越好。
- **Predictive greedy**：在 $\tilde f$ 上跑的单步贪心，每步加一个最大化
  $\tilde d_e(S^t)$ 的元素；所有 worst-case 陈述里 tie 由对抗方打破。
  其在误差水平 $\eta$ 下的精确最坏比记 $\rho_K(\eta)$。
- **两个逐 run 的误差**（比全局 $\eta$ 细）：
  - selection error $\eta^{\mathrm{sel}}$（Definition 2）：一次运行中，
    $\max\{\max_{e\notin S^t} d_e(S^t)/d_{e_t}(S^t) : t<K,\ d_{e_t}(S^t)>0\}$，
    即"每一步选的元素比当步最优真实增益差多少倍"，只对正增益步取。
    事后（$f$ 可观测时）可测，这是论文的 certificate 叙事根基。
  - trajectory error $\eta^{\mathrm{tr}}$：把 Definition 1 限制在这次运行
    访问过的状态上。
  - 链：$\eta^{\mathrm{sel}} \le \eta^{\mathrm{tr}} \le \eta$ 对每次运行成立
    （两行手证）。
- 三条曲线：
  - $L_K(x) = 1-(1-\frac1{xK})^K$：保证曲线；
  - $U_K(\eta) = 1-(1-\frac1{\eta(K-1)+1})^K$：旧显式实例族达到的值；
  - $\rho_K(\eta) = \min_{0\le j\le K-1} V_j(\eta)$：精确最坏值，其中
    $k_1=(K-1)\eta+1$，$q=(K-1)\eta/k_1$，
    $V_j(\eta)=1-q^j(1-\frac{K-j}{K\eta})$。
- 两个定案的建模决定（改动全文措辞的依据）：
  - **D1**：主模型对 $\tilde f$ 不作 submodular 假设；"$\tilde f$ 也
    submodular"只以一条 remark 出现（该变体最坏值在 $\eta<K-1$ 严格变大）。
  - **D2**：$L_K$ 保证降格为 Proposition 并归属 Goundan & Schulz (2007,
    Theorem 1)（"essentially due to"措辞，证明入附录标 included for
    completeness）；全文对该结果禁写 "we prove/show"。背景：GS 的
    $\alpha$-approximate incremental oracle 取 $\alpha=\eta^{\mathrm{sel}}$
    时其 Theorem 1 就是 $L_K$ 界（注意第四晚曾把方向写反为 $1/\eta^{\mathrm{sel}}$，
    F6 审计改正，审查时请独立核对 GS 原文 p.7）。

## 3. 后果：论文的四个承重位（story）

1. **模型**：$f$ 不可查询、只能查 $\tilde f$；乘性单元素增益误差；必须有
   误差上界（否则任何算法无常数比）；且上界必须落在增益上而非取值上
   （value accuracy neither sufficient nor necessary）。
2. **保证即证书**：经典 $L_K$ 界（归属 GS）在逐 run 可测的
   $\eta^{\mathrm{sel}}$ 处成立，事后测得的 $\eta^{\mathrm{sel}}$ 就是该次
   运行的 certificate；实验按此读数。
3. **精确最坏值**：$\rho_K(\eta)=\min_j V_j(\eta)$，两个方向都到证书级
   （显式对偶乘子 + 显式达到实例），严格低于旧族 $U_K$。
4. **Hardness**：$n^c$ 次、每次大小 $\le K$ 的查询预算内，确定性算法不能
   超过 $L_K(\hat\eta)$；与保证合起来把该查询类的最优渐近钉在
   $1-e^{-1/\eta}$（$K\to\infty$）。

## 4. 定理清单：陈述、证明方法、验证状态

以下编号按当前 `paper/main.pdf`（27 页版）。正文在
`paper/sections/results.tex`，证明在 `paper/sections/appendix_proofs.tex`
（附录 B，标签 `app:*`）。

### 4.1 Proposition 3（No bound, no guarantee，`prop:necessity`）
- 陈述：不设 $\eta$ 上界时，对任何算法（任意查询权）与 $n\ge2K$，存在
  $(f,\tilde f)$ 使输出 $T$ 满足 $f(T)\le\frac{K}{n-K}f(O^*)$。
- 方法：对称 predictor 构造（把所有单元素预测值抹平），averaging 论证覆盖
  randomized；$\gamma=K^2/(n(n-K))$ 的选取恰好使 randomized 界等于
  $K/(n-K)$，$n\ge2K$ 恰好保证 $\gamma\le1$。
- 状态：`[HAND-PROOF-UNREVIEWED]`，无脚本。证明 `app:necessity`（约 1 页）。

### 4.2 Proposition 4（Value accuracy neither sufficient nor necessary，`prop:valueacc`）
- 陈述（三部分）：(i) 对每个 $\varepsilon\in(0,1)$ 存在 monotone submodular
  $f$ 与 value-accurate（Hassidim–Singer 的 $\varepsilon$-erroneous 意义）
  的 $\tilde f$，使某处 $d_e(S)>0$ 而 $\tilde d_e(S)=0$，故 Definition 1 的
  任何有限 $(\eta_u,\eta_o)$ 都不成立；(ii) $\tilde f=(1+M)f$ 在所有
  $\varepsilon<M$ 处不 value-accurate，但 $\eta^{\mathrm{sel}}=1$，保证满额
  适用；(iii) 反向：$(\eta_u,\eta_o)$ 误差蕴含 value accuracy 到
  $\max\{1-1/\eta_u,\eta_o-1\}$。
- 来源与方法：(i)(iii) 是 TPAMI 原稿 Lemma 2/3 的重述（(iii) 原稿用
  all-pairs 的 $d_\emptyset(S)$，重写为单元素定义沿枚举 telescoping）；
  (ii) 是本次新增的两行 scaling 观察。
- 状态：`[HAND-PROOF-UNREVIEWED]`，无脚本。证明 `app:valueacc`。

### 4.3 Proposition 5（$L_K$ 保证，`prop:guarantee`）★有已知漏洞
- 陈述：predictive greedy 一次 selection error 为 $\eta^{\mathrm{sel}}$ 的
  运行满足 $f(T)\ge L_K(\eta^{\mathrm{sel}})f(O^*)\ge(1-e^{-1/\eta^{\mathrm{sel}}})f(O^*)$；
  同界对 $\eta^{\mathrm{tr}}$、$\eta$ 成立且有序。
- 方法：标准 greedy 分析（覆盖/averaging + 展开），D2 归属 GS 2007。
  证明 `app:guarantee`，四步，标注 included for completeness。
- 状态：`[HAND-PROOF-UNREVIEWED]`。**已知漏洞（内部对抗审稿 G5 的严重第 1
  条，最优先审查项）**：Definition 2 把非正增益步排除在
  $\eta^{\mathrm{sel}}$ 之外，而附录证明对非正步的处理暗用了全局
  Definition 1（它不是本 Proposition 的前提）。经验证据：对全部 12,057 行
  实验数据重算，63 个 run 有 ratio $< L_K(\eta^{\mathrm{sel}})$，全部满足
  frac_steps_nonpos $>0$，其中 38 个在 $\eta^{\mathrm{sel}}=1.0$；最坏一例
  sport_coverage $K=4$，ratio 0.4153 对 $L_4(1)=0.6836$。三个候选修法
  （加 Definition 1 前提 / 重定义 $\eta^{\mathrm{sel}}$ 把非正步计入 /
  只对全正步 run 声明 certificate）尚未定夺。**请独立判断哪个修法在数学上
  最小且不破坏 certificate 叙事。**

### 4.4 Theorem 6（Per-K tightness，`thm:tightness`）
- 陈述：对每个 $K\ge2$、$\hat a>1$，存在 $2K$ 元素实例使对抗-tie 运行的
  $\eta^{\mathrm{sel}}=\eta^{\mathrm{tr}}=\hat a$ 且输出值恰为
  $L_K(\hat a)f(O^*)$（保证在该族上对每个 K 取等，不只渐近）。
- 方法：显式实例族 + greedy 归纳。附录 `app:tightness` 八步全写
  （族的闭式、四条 ratio 恒等式逐项展开、单调性与全部二阶差分、误差计算
  $\eta_o=R$、$\eta_u=\hat a$、OPT、tie 归纳、$U_K$ 重参数化）。
- 状态：族的恒等式 `[VERIFIED-SYMBOLIC 一般 K]`
  （`results/T5_symbolic.py`，105/105）；全格点数值 $K\le6$
  （`code/check_explicit_instance.py`）；$\eta^{\mathrm{sel}}=\hat a$
  `[VERIFIED-LP K=2..8, â∈{1.5,2}]`（`results/F2_etasel_tight.py`）；
  组装成文的手写证明 `[HAND-PROOF-UNREVIEWED]`。
- 已知弱点（G5）：达到值依赖每步全员 tie（$2K-t$ 个候选全平），是
  tie-breaking artifact；无 strict-preference 变体（Theorem 8 有）。

### 4.5 Lemma 7（Coherence lemma，`lem:coherence`）
- 陈述：$\tilde d_e(S)\ge\tilde d_{e'}(S)$ 时的两条交换不等式
  （(i) $d_e(S\cup\{e'\})\ge\frac1\eta d_{e'}(S\cup\{e\})$；
  (ii) $(1-\frac1\eta)d_{e'}(S\cup\{e\})\ge d_{e'}(S)-d_e(S)$）。
- 方法：$\tilde f(S\cup\{e,e'\})-\tilde f(S)$ 按两个顺序展开 + 误差带。
  `app:coherence`。原名 consistency lemma，因与 LAA 术语撞名改名
  （GLOSSARY）。
- 状态：`[HAND-PROOF-UNREVIEWED]`，无脚本。

### 4.6 Theorem 8（精确最坏值 $\rho_K=\min_j V_j$，`thm:exact`）★论文主定理
- 陈述：对每个 $K\ge2$、$\eta\ge1$、对抗 tie，
  $\rho_K(\eta)=\min_{0\le j\le K-1}V_j(\eta)$；分段结构：$V_j$ 在
  $\eta\in[K-j,K-j+1]$ 上取 min（$V_0=1/\eta$ 于 $[K,\infty)$），断点是
  整数 $2..K$；$\rho_K=1/\eta \iff \eta\ge K$；$K=2,3,4$ 有显式分段闭式。
- 证明结构（三块，状态各异，审查时请分开对待）：
  1. **$\ge$ 方向（greedy 不会更差）**：对一个 reduced factor-revealing LP
     给出一般 $K$ 的显式对偶乘子（两段各一族 $\lambda$），非负性论证
     （含 $j=K-1$、$\eta=1$ 的可去奇点），加权求和恒等式的系数配平全部
     手写展开（$g$ 系数五种情形、$d$ 系数向下归纳用 $q-1=-1/k_1$、常数项
     几何和 + $M+(K-j)=K\eta$）。状态：`[VERIFIED-SYMBOLIC 一般 K，模有限
     分支枚举]`，`results/N1_dual_certificate.py` 320/320；成文手证
     `app:exact` 前半。**mono 约束的乘子恒为 0**（即对偶证书不用单调性
     约束），这是个可疑但已验证的事实，值得审查者留意。
  2. **从任意实例到 reduced LP 的归约有效性**：四族有效不等式（R6），
     其中 case (c)（$e_t\in O^*$）是当初缺口所在。状态：
     `[HAND-PROOF-UNREVIEWED]`，无 oracle（只有"归约后的 LP 与全格点 LP
     数值相等"这一间接证据，$K\le5$）。成文 `app:validity`（约 2 页，
     由 `results/F2_R6_validity.tex` 整合）。**这是主定理下界唯一悬空的
     一步，第二优先审查项。** 关键 remark：cons 约束用的是离轨 band，
     因此精确值只对全局 $\eta$ 陈述，$L_K$ 才能对 $\eta^{\mathrm{sel}}$
     陈述（两把尺子并存的原因，务必读 `rem:app-rulers`）。
  3. **$\le$ 方向（值可达）**：对每个 $j$ 的显式三块实例
     C($j$)+P($K-j$)+O($K$)：$f=1-q^x(1-y/K)+z\delta_j\chi(y)$，
     $\tilde f=W(0)-q^xW(y)+z\eta_o\delta_j\chi(y)$，其中
     $\delta_j=q^j/(K\eta)$，$W(0)=k_1/(K\eta_u)$，$W(y)=(K-y)\eta_o/K$。
     机制：$\tilde f$ 把每步候选压成与 O 打平（tie 承重），greedy 被对抗
     tie 拖着走出值 $V_j$。状态：`[VERIFIED-SYMBOLIC 一般 K，模同一枚举
     约定]`，`results/N2_check.py` 480/480（含 $K\le6$ 全格点、$K\le8$
     精确 Fraction、strict-tie 变体极限）。成文 `app:exact` 后半
     （含逐步增益表）+ `app:instances`。
- 附带已证事实：$L_K\le\min_j V_j$（reduced LP 约束集包含 $L_K$ 分析用的
  全部约束，故值不减，F0）；$U_K-V_{K-1}=q^{K-1}(\eta-1)/(K\eta k_1)>0$
  `[VERIFIED-SYMBOLIC]`（旧族严格非最优）。
- 实例的 $\tilde f$ monotone 但**不** submodular（D1 的动机）。

### 4.7 Remark 9（`rem:exact-gap`，含 D1 的 submodular-surrogate 变体）
- 若要求 $\tilde f$ 也 submodular，最坏值在 $\eta<K-1$ 严格变大：
  $K=3,\eta=1.5$ 时 $9/16\to19/33$（`[VERIFIED-LP + 实例验证器确认可达]`，
  `results/F4_submodular_ftilde.md`；另有 $K=4,\eta=2$: $22/49\to23/50$）。
  general characterization 留 open。闭式猜想
  $\rho_K^{sub}=\min_m W_m$，$W_m=(K-m r^m)/(K(1+(\eta-1)r^m))$，
  $r=1-1/K$，76/76 点吻合，`[CONJECTURE]`，按 D1 不进正文。

### 4.8 Theorem 10（$1/\eta$ ceiling，`thm:ceiling`）
- 陈述：任意查询权的确定性算法存在误差恰 $(\eta_u,\eta_o)$ 的实例使
  $f(T)\le f(O^*)/\eta$；randomized 版 $(1-\frac Kn)\frac1\eta+\frac Kn$；
  反向：在预测值上穷举所有 $K$-子集达到 $f(\hat S)\ge f(O^*)/\eta$。
- 方法：modular 对称构造 + averaging；穷举反向界用 telescoped band。
  `app:ceiling`。randomized 常数在第五晚由推导补齐（此前草稿未查验）。
- 状态：`[HAND-PROOF-UNREVIEWED]`，无脚本。

### 4.9 Corollary 11（渐近，`cor:limit`）
- 陈述：固定 $\eta$，$L_K(\eta)$ 与 $\rho_K(\eta)$ 都 $\to 1-e^{-1/\eta}$
  （$K\to\infty$）；**单调性只对 $L_K$ 声明**。
- 注意：原稿曾写"monotonically within each segment"对两者；$\rho_K$ 的
  单调性无证明（minimizing index 随 $K$ 移动），只有数值支持
  `[CONJECTURE]`，第五晚集成时已保守地从可见陈述中删去。
- 状态：$L_K$ 部分初等；$\rho_K$ 极限由闭式
  `[VERIFIED-SYMBOLIC，results/T3_K3_closed_form.py]`。`app:asymptotics`。

### 4.10 Theorem 12（Bounded-query hardness，`thm:hardness`）★第三优先审查项
- 陈述：固定 $c\ge0$，$\tau=c+1$，$K\ge2\tau$，$\eta>1$ 满足 $\Phi(1)\le\eta$
  （充分条件 $K\ge\tau(1+\frac2{\ln\eta})$），$\hat\eta=\Phi^{-1}(\eta)$，
  $n\ge4K^{c+2}$。任何至多 $n^c$ 次查询、每次查询集合大小 $\le K$ 的确定性
  算法，存在 monotone submodular $f$、单元素误差恰 $\eta$ 的实例使
  $f(T)\le L_K(\hat\eta)f(O^*)$。randomized 加 additive
  $\varepsilon_n=\frac Kn+\frac{K^{2c+4}}{(c+2)!\,n^2}$。渐近
  $K\delta(\eta)\to\max\{2\tau(1-\frac1\eta),\frac{2(\tau-1)}\eta\}$，
  $L_K(\hat\eta)\to1-e^{-1/\eta}$。
  其中 $a_\theta=1-\frac1{\theta K}$，
  $1+\delta(\theta)=\max\{a_\theta^{\tau}\frac K{K-\tau},a_\theta^{1-\tau}\}^2$，
  $\Phi(\theta)=\theta(1+\delta(\theta))$。
- 方法（`app:hardness`，六步，全文来源 `results/N5_bounded_query_hardness.tex`）：
  隐藏最优集 O + hypergeometric concentration（并集界）、transcript 归纳的
  valuation 引理、$\delta$ 的四条边界情形、$\Phi$ 可逆性、averaging（明确
  不冒称 Yao minimax）。"information-theoretic" 的含义在首次出现处声明
  （只数查询、无复杂度假设）。
- 状态分解：装配 `[HAND-PROOF-UNREVIEWED]`；$\delta$ 闭式在 40 个有限点
  `[VERIFIED-LP]`（`results/N5_delta_at_etahat.py`），一般 $(K,\tau,\eta)$
  `[CONJECTURE]`，**而它出现在定理陈述里**（G5 严重条目）；渐近
  `[VERIFIED-SYMBOLIC 15/15]`（`results/N5_asymptotics.py`）。
- 历史教训（增强审查动机）：第一晚 T2 曾得出单支 $\delta$ 闭式，第二晚 N5
  发现它不完整（第二支来自 $y$ 方向 balanced 边，第一支占优 iff
  $\eta\ge2-1/\tau$；分歧点 $(K,\eta,\tau)=(4,1.2,2)$ 用独立 LP 复核
  LP=0.595568=第二支）。即：**这一族闭式已经错过一次**。
- 相关未入文材料：任意大小查询的变体定理草稿（$Q=O(n^2/((2+\eta)^2K^4))$，
  指数 2 是该族内在上限），在 `results/F3_hardness_full.tex`，未进 paper。

### 4.11 Remark 13（`rem:hardness-pins`）
- 与 Proposition 5 合并读出"查询类最优渐近钉在 $1-e^{-1/\eta}$"；有限 $K$
  下两曲线间 $O(c/K)$ 缺口 open。已知瑕疵（G5 中等条目）：其中
  "$K$ evaluations of $\tilde f$ per step" 的说法不对（每步是 $\Theta(n)$
  次、全程 $\Theta(nK)$），$c=1$ 时的对照句需要修。

## 5. 证明方法论汇总（审查者需要知道的技术框架）

1. **Factor-revealing / reduced LP**：把"greedy 在误差 $\eta$ 下最坏能多差"
   写成对增益序列的 LP；变量是各步各类增益，约束来自 submodularity、
   monotonicity、误差带（cons）与 R6 有效不等式。$\rho_K$ 的下界=该 LP 的
   显式对偶可行解（certificate 级），上界=显式实例。**归约有效性（任意
   实例的轨迹都满足 reduced LP 的约束）是唯一手证步**。
2. **符号验证的含义**："一般 $K$ `[VERIFIED-SYMBOLIC]` 模有限分支枚举"指：
   恒等式对符号 $K,\eta$ 用 sympy 验证，但 min/max 的分支选取按有限分类
   枚举后逐支验证；审查者应检查分支分类是否穷尽。
3. **Hardness 的三件套**：隐藏 O + concentration（查询集合与 O 的交集落在
   hypergeometric 集中带）+ valuation（在集中带内所有查询答案与 O 无关）
   + averaging。查询大小 $\le K$ 是承重限定词（任意大小见 F3 草稿）。
4. **空洞性检验**（`CLAUDE.md` 第二晚起）：定理陈述里每个限定词做删除/取反
   替换测试；GLOSSARY 列了易空词（tight 必须指明三义之一、any algorithm
   必须指明算法类、robust 全库禁用、information-theoretic 首用须定义）。
   审查时同样适用。
5. **实验作为理论 oracle**：E4 把 Theorem 6/8 的构造实例喂进与真实实验
   完全相同的管线，19/19 实现理论值到 $10^{-10}$ 量级；G5 又独立重算了
   全部 headline 宏与 CSV 一致。数字不是审查重点，但 G5 用 CSV 反算出
   Proposition 5 的反例（见 4.3），说明数据可以攻击定理。

## 6. 实验一段话（背景即可，非审查重点）

三族任务按"离模型距离"排谱：E1 feature selection（学出的 surrogate，
CV 准确率预测 held-out 准确率）、E2 influence maximization（部分观测图，
one-hop coverage，观测概率 $p$ 可调出单调的 $p$-$\eta^{\mathrm{sel}}$
曲线）、E3 extractive summarization（启发式 surrogate，真目标 ROUGE-1 F
自身有 2.14% submodular 违反与 7.12% monotone 违反，作为 out-of-model
诚实报告）；E4 构造实例贴线。主图：真实任务的 (η^sel, ratio) 散点悬在
$\rho_K/L_K$ 曲线上方。所有正文数字由脚本生成宏（`sections/numbers.tex`，
94+ 宏，硬打数字审计为 0）。OPT 代理：分母用 greedy-on-f；breast_cancer
$K\le5$ 穷举显示该代理只把 ratio 抬高约 1.8%。

## 7. 已知弱点清单（内部对抗审稿 G5 已发现的，请勿重复劳动，请深挖）

完整报告 `results/G5_review.md`（749 行，严重 6 / 中等 16 / 轻微 10）。
严重条目摘要：
1. Proposition 5 对含非正步 run 失效（63 行 CSV 反例，见 4.3）；
2. Theorem 8 的 $\ge$ 方向压在无 oracle 的 `app:validity` 手证上；
3. Theorem 12 陈述内嵌 `[CONJECTURE]` 的 $\delta$ 闭式；
4. D2 之后 novelty 需要 intro 立位（算法、保证、误差度量都归属 GS 2007）；
5. Theorem 6 是全员 tie 的 artifact，无 strict 变体；
6. 状态标签在 PDF 不可见，与 statements 的措辞冲突。
中等条目里审查者最该接手的：Prop 3 缺 deterministic/randomized 限定词；
Remark 13 的每步查询数错误；$1/\eta$ ceiling 与 hardness 界的表面矛盾
（调和只在注释里）；$\alpha$ 在 model.tex 里 20 行内两个相反约定；
all-pairs error 用而未定义；打印的 $\eta^{\mathrm{sel}}$ 中位数与打印的
$L_K/\rho_K$ 互算有第三位小数差（界在未舍入中位数上算）。

**给联合审查者的具体请求**（按价值排序）：
1. 逐行审 `app:validity`（R6 四族不等式，尤其 case (c)）：这是主定理
   唯一悬空步，找出反例或给出独立证明都极有价值；
2. 审 Proposition 5 的非正步漏洞的三个修法，判断哪个最小且自洽，并检查
   修法对 Theorem 6（tightness 在同一定义下）与实验 certificate 叙事的
   连锁影响；
3. 攻击 $\delta$ 闭式的一般性（4.10）：给出第三支存在的反例，或证明两支
   穷尽；`results/N5_delta_at_etahat.py` 可改造成搜索器；
4. 核对 GS 2007 Theorem 1 的原文与我们 $\alpha=\eta^{\mathrm{sel}}$ 的
   实例化是否逐字成立（该方向已错过一次）；
5. `app:exact` 下界的系数配平（4.6 之 1）虽有 sympy 复核，但成文的手写
   展开是新写的，值得抽查 $t=j$ 分支。

## 8. 文件地图

```
paper/main.tex                     主文件（ICLR 2027 模板，主 PDF = paper/main.pdf）
paper/sections/model.tex           Section 2（模型，Definition 1/2）
paper/sections/results.tex         Section 4（定理陈述，含全部状态注释）
paper/sections/appendix_proofs.tex 附录 B（全部证明，标签 app:*，1400+ 行）
paper/sections/related.tex         Section 3（related work，29 条核验引用）
paper/sections/experiments.tex     Section 5 + appendix_experiments.tex 附录 C
paper/references.bib               29 条，每条过四步核验（F6 + H1）
RESEARCH_STATE.md                  逐晚研究状态 R1-R14 + 修正记录（中文）
GLOSSARY.md                        术语表 + 禁用词 + 撞名处理（中文）
REPORT.md                          逐晚工作报告，顶部是最新 summary（中文）
results/G5_review.md               内部对抗审稿报告（最重要的先行审查材料）
results/G1_pagebudget.md           页数预算与附录逐节页数
results/H1_bib_crosscheck.md       与 TPAMI 版的文献交叉验证
legacy/tpami_submission/           TPAMI 原稿全文（对照用；含作者信息，勿外传）
```

## 9. 关键复现脚本（一键，python3，依赖 numpy/scipy/sympy/pandas）

```
results/N1_dual_certificate.py     Theorem 8 下界对偶证书（320 检查）
results/N2_check.py                Theorem 8 上界实例（480 检查）
results/T5_symbolic.py             Theorem 6 族的恒等式（105 检查）
results/F2_etasel_tight.py         Theorem 6 的 eta^sel = a-hat（K=2..8）
results/T3_K3_closed_form.py       K=3 闭式与渐近恒等式
results/N5_delta_at_etahat.py      Theorem 12 delta 闭式 40 点 LP 对照
results/N5_asymptotics.py          Theorem 12 渐近（sympy 15 恒等式）
results/G3_gen_numbers.py          全部正文实验数字宏的再生成
results/G3_number_audit.py         正文硬打数字审计（应为 0 违规）
code/worst_case_lp.py 等 code/*    第一晚冻结的基线 LP（勿改，可 import）
```

编译：`cd paper && pdflatex main && bibtex main && pdflatex main && pdflatex main`，
应得 0 error、0 undefined reference。

## 10. 一段话给审查者定调

这篇论文的信誉体系是"每个断言的状态由 oracle 决定"。审查时请沿用同一
标准：不要因为论证读起来顺就升格一个 `[HAND-PROOF-UNREVIEWED]`；发现
问题时优先构造可运行的反例脚本（放 results/，命名带你的任务号）；指控
数字错误必须附与 CSV 对照的计算。三个最值得火力集中的点按序：
`app:validity`、Proposition 5 的非正步漏洞、Theorem 12 的 $\delta$ 闭式
一般性。

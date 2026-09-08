# REPORT.md

## Summary（第七晚：问题 B 收口，台账已同步）

- L1-L4 全部完成，无 FAILED：正文新增 cor:greedybudget（台账新卡 T10b 先行）+ rem:greedybudget + 附录 app:greedybudget + results/L1_table.csv；L2 两个线性预算候选的精确 LP（Opus 代理，五道闸门我本地重跑 exit 0）；L3 open-problem 段草稿（results/L3_openproblem.tex，未接入 main，conclusion 由人写）+ sandwich 图 paper 版（figures/sandwich_paper.pdf）；台账 T10b 新卡 + T11 追加 L2 行。编译 35 页 0 错误 0 未定义引用（results/L4_compile.log），审计 342 literals 0 违规。
- **最重要结果**：greedy 预算类 𝒜_lin（≤nK 次、size ≤K 查询）在误差 η 的天花板 ≤ min{U_K(η), 1/η}（τ=1 计数按预算 nK 重做，n ≥ 4K⁵ 显式条件，计数链 [VERIFIED-SYMBOLIC]，装配沿 app:hardness 保持 [HAND-PROOF-UNREVIEWED]）；与 ρ_K 的差 = c'(η)/K² + O(1/K³)，c'(η)=e^{−1/η}⌊η⌋(2η−⌊η⌋−1)/(2η²) 连续且 η>1 时为正（[VERIFIED-SYMBOLIC conditional on thm:exact]，K≤400 数值贴合）；η ≥ K 时 greedy 恰达类天花板。
- **L2 结论**：36/40 跑完的配置无一超过 ρ_K（"严格优于"规程未触发）；候选 A（top-(K+1) shortlist）全线塌到单元素保证量级；候选 B（greedy+单轮 swap）在 n=2K 恰持平 ρ_K、更大 n 严格劣于；与 H-F 的 PE_1 对照，n=2K 处无"小 n 超越"。K=3,n=7 的 η∈{1.25,1.5} 两格分支定界未穷尽 [OPEN]（incumbent 是上界，不是超越证据）。
- **最需人类判断**：conclusion 是否吸收 L3_openproblem.tex 草稿（含唯一允许的断言 "we conjecture predictive greedy is worst-case optimal within 𝒜_lin"）与 sandwich 图；K=3,n=7 两格 [OPEN] 是否值得再算（md §5.1 有三条提速建议）。
- 保守决定与逐项对照见下节"第七晚任务明细"（ε_n 按 TASKS7 取 K²/n+K⁵/(2n)（装配实际给 K/n）；候选 B 预算 2nK−K² 超出 Q=nK 的记账已进 T11 禁止声称）。

## 第七晚任务明细（L1-L4，2026-09-08）

- **L1**：先写台账卡 T10b 再落 .tex（用户指令顺序）。计数重做：单查询对概率 K(K−1)/(n(n−1)) ≤ (K/n)²（slack K(n−K)/(n²(n−1))）、Q=nK 并集 ≤ K⁵/(2n)、输出相交 ≤ K²/n、n ≥ 4K⁵ ⇒ 总失败 ≤ 5/32 < 1/2，全部 sympy（results/L1_table.py §1）；U_K−V_{K−1} 恒等式因 sympy 不并符号指数改为两步分解验证（1−1/k₁=q + 括号项）。gap 级数：U_K 与 V_{K−m} 的 1/K 系数同为 c(η)（故 K·gap→0），1/K² 系数差 c'(η)，整数 η 处两支同值 e^{−1/η}(η−1)/(2η)。表 35 行（K∈{2,3,4,5,8,10,20}×η∈{1.25,1.5,2,3,5}）。附录注明同一算术覆盖任意 Q ≤ n²/(4K⁴)。
- **L2**（Opus 代理，1.5h）：全格点 LP + 决策分支枚举 + 五道闸门（冻结 worst_case_lp 复现 ρ_K 20/20 偏差 ≤5.6e−16；O-对称归约、拆分不变性、叶子计数、greedy 轨迹 WLOG）+ 40/40 instance-rebuild 一致性。我重跑 gates 模式确认 exit 0。额外发现（均入 md/T11）：swap 严格比较的 ε-余量研究（下确界不变，inf 非 min）；候选 A 闭式猜想 1/((K−1)η+1) 与 1/(Kη)；候选 B 预算 2nK−K²。交付 results/L2_linear_candidates.{py,json,md}。
- **L3**：sandwich 图两面板（K=8 区间 + log-log 宽度贴 c'/K² 渐近，最小有效字号 7.07pt ≥ 7pt，results/L3_sandwich_fig.py）；open-problem 段按 TASKS7 清单逐项落实（三个数 0.4216/0.4242/0.5 来自 L1_table.csv 精确值；候选句在 L2 出结果后按实际结论填写，占位期不预设方向）；wrapper 编译测试 0 错误（results/L3_compile.log，wrapper 已删，citation warning 是 wrapper 无 bibtex 所致）。接入 main 时四个字面数字需转 numbers.tex 宏（文件头有提案宏名）。
- **L4**：台账 T10b/T11 + 表头日期；编译（results/L4_compile.log）；审计 0 违规；push + experiment 镜像同步。

- 全部完成：K1-K7（前日）+ K9（J4 六项措辞与范围修正，F3 降为 candidate bound 段落）+ H-J3（sharp form、prop:rigidity 刚性命题、断点 active-constraint-switch remark、app:rigidity 逐步证明；闸门由自写 results/H_J3_gate_check.py 全过，2,480 LP 偏差 4e-15，J3 原脚本未交付已记录）+ 四个硬核探针 H-F/H-B/H-E/H-C。全文 34 页编译 0 错误 0 未定义引用（results/H_final_compile.log），数字审计 311 literals 0 违规。
- **三个新硬核结果**：H-B 的 c(η)=e^{−1/η}(2η−1)/(2η²) 非分段闭式 + ρ_K 关于 K 非增的证明闭合（conditional on thm:exact，cor:limit 单调子句已按台账恢复）；H-E 的 n<2K 精确天花板 K/((2K−n)+(n−K)η)（84 点 LP，thm:ceiling 后已加句）；H-C 的一般 K 双 submodular 实例族把 ρ_K^sub ≤ min_m W_m 升为定论（410/410），下界仍 [CONJECTURE] 且卡点已定位。
- **最需人类判断（H-F 发现）**：partial enumeration PE_1 在 n=2K 严格优于 greedy，但 n≥7 起在 η∈{2,2.5} **严格劣于** greedy（按 f̃ 选终点的损失超过枚举收益，NW 1978 的有限 K 改进不能搬入预测模型）；这是 greedy 有限 K 最优性的正面证据（R=1,K=3,n≤8），建议进 open problem 段并回 Tianming 的 O(n)K 问题。
- **台账已同步**：THEOREM_LEDGER.md 逐卡更新 T4/T5/T6/T6b(新)/T7/T8/T9/T11 + 表头；每卡状态标签与 results/ 脚本一一对应；本晚全部陈述改动先改卡后改 .tex。TASKS_J2.md 依旧缺失（按 H3 计划执行）；J3/J4 的 oracle 脚本未交付，闸门与数值以自写脚本替代（H_J3_gate_check.py；J4 的 253,220/1,928/325/1,638 检查无法本地复跑，只据其报告引用并注明）。
- H 系列唯一 FAILED：H-C 的 W_m 对偶证书（卡点：路径变量 LP 加自然 f̃-submodular 割后仍收在 min_j V_j，42/42，需换聚合变量）；H-E 的 LP-B 手证、H-F 的一个 branch_both 交叉检查超时也已如实记卡点。contribution (iv) 要点沿用 J2 采纳日的清单，另加一条：intro 可引用 rem:exhaustive-vs-greedy 与 H-F 作为"greedy 在同预算类内最优"的证据链。

## Summary（J2 采纳日：K1-K7 全部完成）

- 外部审查 J2（GPT）的六项发现经 H3 独立复核后全部落实进正文，K1-K7 无 FAILED：η^sel 换逐步定义（有害零步 ∞）、E2 证书连锁重算、主图拆两幅、R6 slack 证书入附录、hardness 重校准为 H_{K,τ}、P2 小修全清。编译 0 错误 0 未定义引用，30 页（results/K7_compile.log）；数字审计 0 违规。
- **最重要的变化**：thm:hardness 换为更强更简的 H_{K,τ}(η)=1−(1−1/(η(K−τ)+1))^K（实际误差乘积校准，无反函数分支）；τ=1（c=0）时 H=U_K，四曲线成链 L_K ≤ ρ_K ≤ U_K = H_{K,1}；app:validity 关键步升级 [VERIFIED-SYMBOLIC]。
- **最需人类判断**：contribution (iv) 的 intro 承重位要按下节"contribution (iv) 需相应改写的要点"重写（查询类最优性现在限定 c≥2 的类）；E2 证书叙事新增 16 条 ∞ 轨迹的表述已定稿，如嫌重可再压。
- 注意：TASKS_J2.md 在仓库、上传目录与 J2 包中均不存在；本日按 results/H3_j2_assessment.md 的 P0-P2 计划 + 用户四点补充执行（用户称两者一致）。若该文件后续出现且规格有差异，按差异补做。
- 逐项改动的 J2 章节对照与复核结果在下面"J2 采纳日明细"，全部 commit 已 push（82f50cf 等 5 个），experiment 镜像已同步。

## J2 采纳日明细（K1-K7，2026-09-07）

每项注明【J2 章节 | 复核结果】。复核 = results/H3_j2_recheck.py（我的独立实现，ALL PASS）+ J2 双脚本本环境重跑 all_passed。

- **K1**【J2 §4 | 三元素反例独立复算成立】def:etasel 换逐步 a_t（正常步 M_t/g_t、良性零步 1、有害零步 ∞，L_K(∞)=0）；prop:guarantee 无条件化，η^tr/η 替换句加有限 band 前提；app:guarantee Step 2 重写（不再暗用全局 band）、Step 4 补零步情形、新增 stepwise product bound remark（[HAND-PROOF-UNREVIEWED]，J1 1,905 轨迹精确算术支持）；GS α=η^sel 三方一致（F6、J2、原文 p.7）。**补充点 1 完成**：U_K 族在新定义下 η^sel=η^tr=â 逐位不变，14/14（results/K1_etasel_newdef_check.py），无零步。
- **K2**【J2 §8 | 225/16/711/30416/5952 五个计数全部独立复算吻合】E2 有害零步轨迹 η^sel=∞：K=30 中位 η^sel 4.3→4.5、certified bound 0.207→0.199、p-η 单调网络 4→3（facebook_government p=0.5 半数 run 覆盖为 ∞，该 cell 中位 ∞）；E1/E3 全部改称 finite-step diagnostic（E1 也出模型：711/720 前缀见负候选边际）；OPT 代理方向两处 + 表注三条修正；"structurally zero" 注释删除。宏由 results/G3_gen_numbers.py 重生成，审计 199 literals 0 violations。
- **K3**【J2 §5 | 两把尺反例全枚举复算成立】**补充点 3 完成**：主图拆两幅。η^sel 轴（figures/money_plot）只画 L_K + 三族散点，16 条 ∞ E2 runs 面板注记不画点；全局 η 轴新图（figures/eta_global_plot）ρ_{3,5,8} + V_j 贴线 + U_K 悬上方；aux p-η 图按 ∞ cell 重绘（results/K3_split_figs.py，字号 ≥7pt）。
- **K4**【J2 §2 | 两条 slack 恒等式 sympy 独立验证 + 1,536 格点】cons case (b) 的三项非负证书写入 app:validity，恒等式 [VERIFIED-SYMBOLIC]，记账部分保持 [HAND-PROOF-UNREVIEWED]；thm:exact ≥ 方向状态注释同步。G5 严重第 2 条正面了结。
- **K5**【J2 §6-7 | 边表极值与 η_act=(θK−1)/(K−τ) 暴力枚举复核 + 新旧校准表 4 行复算】**补充点 2 完成**：thm:hardness 换 H_{K,τ} 版（实际误差恰 η、任意拆分可达，Ψ 闭式逆无分支，randomized ε_n 在整数 c 处还原旧式）；新增 rem:hardness-chain（c=0：H_{K,1}=U_K，链 L_K ≤ ρ_K ≤ U_K，注意 τ=⌈c⌉+1 下 τ=1 ⟺ c=0）；rem:hardness-pins 限定包含 greedy 的类（nK≤n^c，整数 c≥2）+ c=0 反例 + 间隙 O((c+1)/K)；app:hardness 重写（四行边表穷尽、β 缩放、概率装配按用户要求保持 [HAND-PROOF-UNREVIEWED] 未升级）；F3 任意大小查询定理入附录 app:hardness-anysize（约 1 页，状态标签原样保留，含 [CONJECTURE]/[EXACT] 边界）。notation 表的 Φ/η̂ 以"superseded 校准"身份保留定义，旧 N5_delta 脚本口径问题在附录注明。
- **K6**【J2 §3/§9 | 端点反例与 U_3(1.5)=37/64>19/33 复核】rem:exact-gap 收缩（η=1 两模型重合；"strictly improves" 限定到已验证点位；U_K 句改为"上界证明不再适用"）；V_i 索引 0..K−2；严格扰动端点 caveat（K=3,j=1,η=2,η'=19/10 失单调性）与补法草图入注释。
- **K7**：本节 + D3 记录（RESEARCH_STATE/GLOSSARY）+ REVIEW_BRIEF 顶部加时效注记。

## contribution (iv) 需相应改写的要点（供人类改 intro，正文未动）

intro 注释块的第 4 承重位（hardness position）按 K5 后的定理需要这样改：

1. 陈述换名换形：不再是 "no deterministic algorithm with n^c queries of size at most K beats L_K(η̂)"，而是 "…beats H_{K,τ}(η) = 1−(1−1/(η(K−τ)+1))^K，τ=⌈c⌉+1"；不再需要 Φ 反函数与假设 (H)，前提改为 η ≥ (K−1)/(K−τ)。
2. **"pins the bounded-query optimum to 1−e^{−1/η}" 必须限定查询类包含 greedy**：nK ≤ n^c（例如整数 c≥2、K≤n）。小 c 不成立（c=0 有单查询 ratio=0 反例）。写法建议："for every query class rich enough to contain greedy (n^c queries with c ≥ 2), the optimum at error η is pinned to 1−e^{−1/η} asymptotically in K"。
3. 有限 K 间隙写 O((c+1)/K)，不写 O(c/K)。
4. 新卖点可加一句：τ=1 时 hardness 曲线恰是旧显式族值 U_K，于是 L_K ≤ ρ_K ≤ U_K = H_{K,1} 四条曲线在一条链上（图 2 的 U_K 方框悬在 ρ_K 上方就是这条链的可视化）。
5. 第 2 承重位（certificate）同步微调：η^sel 是逐步定义（有害零步 ∞），certificate 只对模型内目标声明；实验三族一分为二（E2 证书 / E1、E3 诊断）。
6. （第七晚新增）第 4 承重位可再加一句收口：在 greedy 自己的预算类 𝒜_lin（nK 次 size ≤K 查询）内，天花板收紧到 min{U_K, 1/η}（cor:greedybudget，τ=1 常数），与 ρ_K 只差 c'(η)/K²+O(1/K³)；η ≥ K 时 greedy 恰达类天花板。措辞注意：有限 K、1<η<K 的类内最优性仍是 open（T10b/T11 禁止声称），intro 只能说 "within O(1/K²) of optimal in its own budget class"，不能说 optimal。

## Summary（第五晚：装配全文骨架）

- 全部完成，无 FAILED：G0 落实 D1/D2；G1 全文骨架；G2 附录逐行证明（约 14 页）；G3 experiments/related 正文 + 94 个数字宏（审计 0 手打数字）；G4 breast_cancer K=5 穷举 OPT（median 0.982）+ airline 保守 OPT 下估（≤0.33% 改进）；G5 对抗审稿；G6 投稿卫生（双盲干净、statements 按模板、图字号 ≥7pt）。
- **明早先看三个文件**：`paper/main.pdf`（25 页，0 错误 0 未定义引用，abstract/intro 留待人写，注释里有一句话故事、四个承重位与 A/B hook 草稿）；`results/G1_pagebudget.md`（逐节页数 vs 9 页预算 + 压缩点）；`results/G5_review.md`（严重 6 / 中等 16 / 轻微 10，附"明早先修三条"）。
- **最需人类拍板（G5 第 1 条，严重）**：prop:guarantee 对含非正步的 run 失效（12,057 行里 63 行 ratio < L_K(η^sel)，其中 38 行 η^sel=1.0；证据在 G5 报告）。修法三选一：给命题补 Definition 1 的全局前提 / 重定义 η^sel 把非正步计入 / 证书叙事只对全正步 run 声明并在表格用 n_steps_nonpos 列过滤。
- 其余严重项：Theorem 8 的 ≥ 方向压在 app:validity 手证步上（无 oracle）；Theorem 12 陈述内嵌 δ 闭式 [CONJECTURE]；状态标签只在源码注释、PDF 不可见，与 statements 的措辞冲突；D2 之后 novelty 要靠 intro 的四个承重位立住。
- 硬规则守住：每个 .tex 改动后全文在 ICLR 2027 模板编译通过、日志入 results/（G0/G1/G2/G3/G23/G4/G6_compile.log）；实验数字全部走 numbers.tex 宏；G5 子代理只读；每任务单独 commit 并已全部 push。

## 第五晚任务明细（G0-G7）

- G0：results.tex 的 Theorem 6 → Proposition + GS 归属句；D1 remark 定稿措辞（9/16→19/33，characterization left open，W_m 只留注释）；RESEARCH_STATE/GLOSSARY 追加 D1、D2 与日期。
- G1：main.tex 重构为完整骨架（model 拆出为 sections/model.tex，notation 表移附录 A，related/experiments/conclusion 挂 stub 后由 G3/人类填）；results/G1_pagebudget.md 落盘。
- G2（Opus 代理）：appendix_proofs.tex 186 行 → 1351 行；对偶乘子显式公式与消项逐步写出、三块实例逐步增益表、R6 validity（F2）整合；每个证明尾注 machine-checked 指针（如实，无脚本的写明无）；诚实缺口以注释保留（cor:limit 的 ρ_K 单调子句已保守删除，只对 L_K 保留）。
- G3（Opus 代理）：experiments.tex（三族谱系 + p-η 段 + E3 边界外段 + E4 贴线段）、related.tex（四组各三句 + 邻线，23 条核验引用全用上，η_AB 脚注）、G3_gen_numbers.py → numbers.tex（94 宏，字节级确定性）、G3_number_audit 0 违规。
- G4（Opus 代理）：K=5 穷举 1,744,360 次评估 18.5 分钟，K≤4 与 F1 逐位一致 [VERIFIED-EXHAUSTIVE]；airline 下估按方向如实写入附录（sanity check only）；宏与附录已由主代理集成。
- G5（只读 Opus 代理）：results/G5_review.md（749 行）；数字指控均附 CSV 复算证据，29 个头条宏全部对上；PROJECT_INSTRUCTIONS 不存在已记录，用 RESEARCH_STATE 替代。
- G6：双盲扫描零命中；statements 改 \subsection* 并加 link-withheld 占位；四图 paper 版重出（results/G6_paper_figs.py），缩放后最小 7.1-8.4pt；checklist 与明早 TODO 在 results/G6_submission_checklist.md（删 \iclrfinalcopy、Anonymous GitHub、notation 表 overfull）。
- G7：本 summary；全部 commit 已 push；experiment 镜像已同步。

## Summary（第四晚：修补、收尾、写作物料）

- 全部 PASS：F0 记号定稿；F1 实验修补（6/6）；F2 理论卫生（两悬案落地）；F5 写作物料（6 页模板编译干净）；F6 引用（23/23 四步核验入库）；F3 hardness 再攻（交付齐全，原目标如实 FAILED 但得到任意大小查询、Q=O(n²) 的定理草稿）；F4 submodular f̃（建模悬案有了答案）。
- 三个改变认知的结果：F4 证实要求 f̃ submodular 时最坏值在 η<K−1 严格变大（9/16→19/33，新闭式 min_m W_m [CONJECTURE]，U_K 失效）；F3 发现真带是过强形式化（大查询自动 O-无关），但查询预算指数内在卡在 2；F2 判定 (5,4) 为真实差异（N4 闭式隐含 F(x,K)≡1）。
- 两处修正：GS 2007 的 α 方向（=η^sel 非 1/η^sel，GLOSSARY+正文已改，Theorem 6 措辞降为 "in the terminology of GS"）；E2 的 η^path 中位数 71.7→284（去截断）。
- 最需人类拍板：论文采用哪个 surrogate 模型（f̃ 是否要求 submodular——决定 ρ_K 一整章怎么写）；以及 Theorem 6 归属措辞的最终口径。
- 硬规则全守：23 条引用全过四步核验才入 .bib；所有 .tex 在 ICLR 2027 模板下编译通过（日志在 results/F*_compile.log、F5_paper_compile.log）。

## Summary（实验之夜）

- 全部 PASS：E0 管线；E4 最坏实例 oracle（19/19 差 ≤1e-10）；E1 feature selection；E2 IM（240 轨迹无降规模）；E3 摘要；E5 主图；E6 汇总。无任务级 FAIL，无人工扰动 oracle。
- 主图故事成立（figures/money_plot）：三个真实任务的 (η^sel, ratio) 散点整体悬在 ρ_K/L_K 曲线上方，E4 构造实例精确贴线；E2 的 p-η 单调曲线是"何时重要"的展品（η 升 87× 时 ratio 只掉到 0.88）。
- 关键方法结论（E1）：η^path 的认证下界在真实数据上几乎无信息量（0.02-0.10），**论文主用 η^sel**（下界 0.2-0.5 有信息量且实测 ratio 更高）。
- 诚实记录：E1 发现 held-out acc 非 submodular 使纯 CELF 轨迹偏离精确 argmax（已改逐步精确并留反面证据）；E2 的 viol=0 是结构性的；E3 本地缺 sport/tech 参考摘要，HF 回填经 99/100 逐 token 验证并入库。
- 最需人类判断：论文实验节的三任务谱系措辞（学出的 surrogate ≈完美 / 观测残缺 单调可控 / 启发式+边界外 掉到 0.6-0.7），表格草稿 results/EXP_table.tex，差异清单在 results/EXP_SUMMARY.md。

## Summary（第二晚）

- 全部 PASS：N0 术语表/规则；N1 一般 K 对偶证书；N2 显式 V_j 实例；N3 K=5 验证；N4 hardness 解析化；N5 有界查询定理草稿；N6 加性误差模型。无任务级 FAIL。
- 头条：**ρ_K(η) = min_j V_j(η) 两个方向都到证书级**（N1 对偶 + N2 实例，均一般 K 符号验证），只剩 R6 有效不等式一步手证；N4 进一步表明 poly-query 技术的 n→∞ 极限恰是这同一闭式（修正第一晚"贴 U_K"的解读）。
- 两处对第一晚结论的修正已同步进文档：δ 闭式是 max 双支形式（N5，分歧点经独立 LP 复核）；relaxF 的 n=8K 数值未收敛（N4）。
- 最需人类判断：N2 实例的 f̃ 单调但不 submodular（R7 同病）——若模型要求 f̃ 也 submodular，全部上界实例失效，ρ_K 可能变大，这是建模决定；其次是 N6 的混合误差模型在量化尺度 ε 下对大多数真实数据行不可行，论文实证叙事需按 md 中的读法措辞。
- 复现：每个数字有一键脚本（results/N*_*.py，主会话全部复跑过）；第一晚 summary 存档在下方。

## Summary（第一晚，存档）

- 全部 PASS：T1 基线一致；T2 hardness；T3 闭式；T4 lookahead；T5 符号化；T6 实证；T7 定理草稿。无 FAIL（仅 T2 的 4 个超大 LP 超时跳过，已记录）。
- 最重要发现：R9 候选在真 balanced 定义下有结构性不可行证书（F 在 y=K 处平坦 vs Ĝ 递增，任意 n/δ/τ 都救不了）；放开 F 后 LP 值贴 U_K、K→∞ → 1−e^{−1/η}，且 y≤τ 下最小 δ 有精确闭式 1+δ=(a^τK/(K−τ))²。（注：两处解读已被第二晚 N4/N5 修正，见上。）
- 意外收获：T3 得到 K=3、K=4 分段闭式 + 一般 K 猜想 min_j V_j（符号对偶证书）；T4 发现 pair greedy 在 K=4 恰等于 ρ_2(η)；T5 把 R7 升级为一般 K [VERIFIED-SYMBOLIC]。
- 最需人类判断（当晚）：论文 hardness 一节怎么讲——第二晚 N4/N5 已给出答案的主体。

---

## 任务日志（倒序追加在此行之下）

### ——— 第四晚（TASKS4.md）———

### F7 收尾 — PASS
- REPORT 顶部换为第四晚 summary；RESEARCH_STATE 追加"第四晚 F1-F4"更新块；
  results.tex 的 F4 占位 remark 已按结果定稿并重编译；文件清单 results/F7_file_inventory.md；
  全部推送 + experiment 镜像同步。

### F4 submodular f̃ 约束下的最坏值 — PASS（回答了第二晚的建模悬案）
- **要求 f̃ submodular 会改变最坏值**：η < K−1 区严格变大（K=3,η=1.5: 9/16→19/33；
  K=4,η=1.5: 1447/2662→23/41；K=4,η=2: 22/49→23/50），η ≥ K−1 区不变。9 主点 + K=5 三点
  的 LP 最优解全部经独立验证器确认为真实例（f 单调 submodular、f̃ submodular、误差恰达、
  greedy 轨迹、比值=LP 值）——变大是可达的，不是松弛 [VERIFIED-LP]。
  主会话在分歧点 (3,1.5) 复跑精确吻合。
- 新闭式猜想 ρ_K^sub = min_m W_m（W_m=(K−m r^m)/(K(1+(η−1)r^m))，r=1−1/K；与 V_j 同构，
  衰减率 q→r），76/76 LP 点偏差 ≤4.4e-16 [CONJECTURE]；渐近极限比 1−e^{−1/η} 高 ~10%。
- U_K 在新模型**失效**为上界 [VERIFIED-LP]（R7 的 f̃ 也不 submodular）；L_K 仍是下界但更松。
  N2 族 0/72 submodular（违反量 O(1)）。若论文采用 submodular surrogate 模型，
  R7/U_K 全部陈述需重写——这是最需人类拍板的建模决定，remark 素材已备
  （results/F4_submodular_ftilde.md，明确禁写 "more robust"）。
- 诚实边界：闭式无对偶证书无一般 K；K=5 只解不相交 O（上界，但实例可达）；n=2K 充分性
  K≥4 为 [CONJECTURE]；只测 √η 拆分。复现 results/F4_submodular_ftilde.py（约 12 分钟）。

### F1 实验修补 — PASS（6/6，主会话核对新列与行数）
- ROUGE 核对：自实现与 rouge-score 在 90 篇 × 1,624 个候选上**逐项精确 0 差**（原因：这批文本
  无下划线/重音字符，两个 tokenizer 逐 token 相同；café/Zürich 负控制证明装置灵敏 0.05-0.13）。
  未改 f、未因 ROUGE 重跑 E3。venv 安装（系统 pip 因 Debian setuptools 补丁失败，非网络）。
- E2 η^path 去截断：4 图 240 轨迹全量重算（artist 31.5 分钟 < 40 上限，无图 n/a）。
  K=30 合并中位数 71.7→284（artist 200→1407）；断言 ratio/η^sel/viol 7,200 行逐行不变、
  pairs 文件逐字节相同。顺带更正 E2_notes 旧错："d≤0 出现 0 次"实为 16/240 条 run 各 1 步
  （用旧文件复核确认非本次改动引入）。
- statistics.py 写死非正步策略 + 新列 n_steps_nonpos/frac_steps_nonpos；E1-E4 全部重生成，
  旧列 0 处不同（E1 完整重跑 905 秒；rebuild-from-pairs 因 10 位舍入无法逐位重建，脚本改为
  拒绝写盘并如实记录）。
- OPT 代理：breast_cancer 暴力枚举到 K=4（K=5 估 74 分钟超预算，诚实降级）：
  f(greedy^f)/OPT 中位 0.9823（min 0.9554），greedy^f̃/OPT 0.9464。airline K=7 仍未测。
- EXP_table.tex 重生成（含新列与固定两句表注；旧表本超宽 465pt，新表 393.7pt 无 Overfull）；
  E5 全部图重出。详见 results/F1_fixes.md。

### F3 Hardness 全版本再攻 — PASS（交付齐全；原目标"任意多项式次查询"如实 FAILED）
- flatness 判定：N4 的 F(x,K)≡1 确实平坦且 x>T 整片饱和，但 R11(b) 证书不适用（Ĝ 同时饱和）。
  τ=1 真带下 **δ 恰为 0 iff n > K(T+1)**（门槛闭式 12/12 命中 [CONJECTURE]；任务指定的 n=8K
  恰好全在门槛之下——此前真带检查都在错误一侧）。τ≥2 对任意 n/δ 不可行（连 y≤τ 也一样），
  普适 2 约束 IIS 证书 240/240 与独立图论判据等价（主会话复跑 cert：252/252 PASS）。
- **意外正面结果**：N4 的 G 在 x>T 上自动 O-无关（[EXACT] 12/12），泄露集合全部满足
  |S∩O|≥2 且 |S|≤T+K——真带是过强的形式化，大查询不需要 concentration。由此得到
  **任意大小查询**的 hardness 定理草稿（results/F3_hardness_full.tex，模板下编译 2 页 0 错误）：
  预算 Q = O(n²/((2+η)²K⁴))，常数贴 ρ_K^LP。**指数卡在 2 是该族内在上限**，正文必须显式限定。
- 控制实验：F 也放开时真带 72/72 可行 δ=0，值与 y≤τ 逐点相等——障碍是 N4 显式闭式非真带本身；
  relaxF 值随 τ 单调退化，τ*=⌈K/η⌉ 处撞 1/η [CONJECTURE 8 行 7 中]。
- 诚实边界：定理装配步骤全 [HAND-PROOF-UNREVIEWED]；(12,3) 一行 HiGHS >20 分钟 SKIP；
  全部网格 LP、√η 拆分。数据 results/F3_delta_table.csv（309 行）、详见 F3_summary.md。

### F6 引用核验与 .bib — PASS（23/23 入库，0 未过）
- paper/references.bib：23 条全部过四步核验（9 条定位到定理/章节号，14 条 PASS*——存在性/
  字段/版本全验、陈述定位到摘要级，audit 里逐条注明）；模板 .bst 下编译 0 警告。
- 三个重要发现：(i) **Goundan-Schulz 2007 是 MIT working paper（无会议/期刊版）**，其 Theorem 1
  逐字就是本文 L_K 界，且 α 约定为 α = η^sel（**GLOSSARY 此前写反为 1/η^sel，已修**；
  论文 Theorem 6 措辞降为 "in the terminology of GS"，不得写 we prove——需人类确认）；
  (ii) Bhawalkar et al. 2025 存在但主题是 noisy oracle 非 LAA，不能放 LAA 段；
  (iii) SNAP email-Eu-core 官方规定引用是两条（Yin KDD'17 + Leskovec TKDD'07），均入库；
  GEMSEC 出处是 ASONAM 2019。Horel-Singer vs Hassidim-Singer 已确认为两篇（原稿错引成立），
  另有第三篇 Singer-Hassidim NeurIPS 2018 需防混淆。
- results.tex 的引用键已对齐（goundan2007revisiting），paper 重编译 0 未定义引用。
- 详见 results/F6_citation_audit.md。

### F5 写作物料 — PASS（6 页，模板下编译干净）
- paper/sections/results.tex（理论九节正式陈述，每条带状态标签注释与验证脚本指针，
  逐词过空洞性检验：无 robust、无裸 tight、全称句带限定）；appendix_proofs.tex（证明骨架，
  sympy 验证处逐一注明 verified symbolically）；notation_table.tex；statements.tex
  （AI use + reproducibility 如实草稿）；figures/captions.tex（主图+三辅图）。
- paper/main.tex 组装编译：pdflatex+bibtex+pdflatex×2 全过，0 LaTeX 错误、0 未定义引用/交叉引用，
  日志 results/F5_paper_compile.log。GS 归属修正已进正文。

### F2 理论卫生 — PASS（两个悬案落地）
- **(5,4) 判定为真实差异**：N4 闭式隐含多加了 F(x,K)≡1；LP 只要求 |S|≤K 处 F≤1，最优解用
  F(x,K)=1+xε（ε=1.755e-4）。精确二进有理可行点证明 LP ≤ 0.2474903831 < 闭式 0.2474906885；
  加回该约束后 LP 精确回到闭式（≤5.6e-17）。触发条件（为何仅 K=5）仍开放，已如实记录。
  [VERIFIED-LP 精确有理]，results/F2_54_exact.py（主会话复跑退出码 0）。
- R6 有效不等式手证 results/F2_R6_validity.tex [HAND-PROOF-UNREVIEWED]，含 b_t ∈ O 情形；
  模板下编译通过（results/F2_compile.log）。重要 remark：cons 约束用到离轨状态的 band，
  故 reduced LP 精确值只对全局 η 成立，而 L_K（只用 sum+pred）可对 η^sel 陈述——
  这解释了三把尺子的层级，正文已按此写。
- η^sel 紧性：U_K 实例 K=2..8×â∈{1.5,2} 上 η^sel=η^path=â 全 PASS（量化口径差异已注明），
  R7 已追加一行。[VERIFIED-LP]，results/F2_etasel_tight.py（主会话复跑退出码 0）。

### F0 状态同步与记号定稿 — PASS
- RESEARCH_STATE 追加 R14（实验之夜四段，含 OPT 代理注记）；L_K ≤ min_j V_j 升级 [PROVED]
  （约束包含关系一行论证）；GLOSSARY 加记号定稿/η^sel 出处/引用四步核验三条；paper/macros.tex。

### ——— 实验之夜（TASKS_EXP.md）———

### E6 汇总与写作物料 — PASS
- results/EXP_SUMMARY.md（每任务一段 + 与原稿实验的差异清单：删扰动 oracle、全量 airline、
  GBC→决策树、图数据替代、删 R-step、统一三量）；results/EXP_table.tex（booktabs 表格草稿，
  含 E4 贴线行与 OPT 代理注记）。

### E5 主图与辅助图 — PASS
- figures/money_plot.png/.pdf（K=5/K=30 双列，log-η 轴到 500，超界点数标注）；
  aux_eta_sel_by_K（三任务箱线）、aux_p_vs_eta（IM 的 p-η 单调曲线，log-y）、
  aux_d_dtilde_scatter（(d,d̃) 散点带 η=2 带，违例集中近零增益）。
- 复现：python3 results/E5_money_plot.py（读 E1-E4 的统一行 CSV，缺失文件显式跳过）。

### E1 Feature selection（学出来的 surrogate）— PASS
- 设定：airline 全量 25,375 行（不再 sample 1000；n_test=5,075，ε=1.97e-4）+ breast_cancer/wine/
  digits20；f = 决策树 held-out acc（修正旧脚本的 GBC 不一致），f̃ = train 上 5-fold CV；
  K=1..7 × 30 seeds；840 统一行 + 15,330 (d,d̃) 对，无 NaN（主会话复核）。
- **信息隔离是结构性的**：f̃ 构造自只接收 (X_train,y_train) 的工厂，__slots__ 无法挂 test 属性，
  闭包断言 + 内存共享断言 + 行为探针（打乱 y_test 后 f̃ 逐位不变而 f 大跌）四层全过。
  旧 oracle 的信息泄露与人工扰动从结构上排除。
- 结果（K=7 中位数）：ratio 0.999(airline)/0.955/0.944/0.959；η^sel 1.55/2.0/1.38/2.9；
  认证下界 L_7(η^sel) 0.49/0.40/0.54/0.30——有信息量；而 η^path 10-52，L_7(η^path) 仅
  0.02-0.10 几乎无信息量。**论文应主用 η^sel，这是本任务最重要的一条方法结论。**
- 基线（论文 Fig.1 替代）：airline 上 greedy-on-f̃ 每个 K 都不劣于 SelectKBest/RFE/MI/ExtraTrees
  的最好者（K=7: 0.9458 vs 0.9367），距 greedy-on-f 仅 0.002；breast_cancer 上互有胜负（如实报告）。
- 重要管线发现：held-out accuracy 非 submodular，纯 CELF 轨迹与精确 argmax 每 7 步只有 2-3 步
  一致——真值 greedy 已改为逐步精确 argmax 并断言，CELF 轨迹的 ratio 存 E1_diagnostics.csv
  作反面证据。OPT 代理的高估幅度用小例暴力枚举量化（wine K=7: f(greedy^f)/OPT 中位 0.972）。
- GBC seed0 稳健性核对：结论不变且略好；digits20 的 GBC 因单轨迹 >20 分钟按原则 5 跳过并注明。
- 复现：python3 results/E1_run.py（约 32 分钟分块）；详见 results/E1_notes.md。

### E2 Influence maximization（部分观测图 surrogate）— PASS（无降规模、无截断、全 240 轨迹）
- 设定：一跳覆盖；f̃ = 观测图（每边保留概率 p ∈ {0.3,0.5,0.8} × 20 种子）上同公式；
  K=1..30；替代图 facebook_{artist(50,515 全图), politician, government} + email_eu_core
  （原 Twitter/reddit 丢失，INVENTORY 有记录）。artist 单 run 实测 3.4 秒，无需节点截断。
- 主结果：p-η 单调关系干净（"何时重要"展品）——p 0.8→0.3 时 η^sel 中位数升 3.2×(artist)
  到 87×(government)，但 ratio 只从 ~0.99 掉到 0.88-0.96；认证下界 L_30(η^sel) 从 0.573
  掉到 0.008，真实实例比 worst-case 界乐观约两个数量级。η^sel 增长集中在前 5 步；尾重
  （artist p=0.3 max 456），须用分位数。对照：degree(观测图度数) 0.66-0.89、random 0.06-0.54，
  均逊于预测式 greedy。
- 方法学两点如实记录：viol=0 是结构性的（两个覆盖函数增益恒非负，这把尺子在 E2 无信息量）；
  facebook 三图 (d,d̃) 只落盘每步 top-50 候选，η^path 因此系统性下估（截断偏差已单独量化
  E2_truncation_check.csv；E5 用 η^sel 作横轴不受影响）。ratio>1 占 1.3%（OPT 代理上估所致）。
- 验证：真图 lazy CELF vs 全扫描逐步差 0；增量覆盖 vs Graph.coverage 差 0；轨迹逐元素相同
  （E2_validation.txt；主会话核对行数 7200 与中位数表一致）。
- 复现：python3 results/E2_run.py（支持 --dataset --p 分块）；数据 E2_rows.csv、E2_baselines.csv、
  E2_p_eta.csv；详见 results/E2_notes.md。

### E3 Text summarization（启发式 surrogate）— PASS
- 设定：BBC 三类各 100 篇，f = ROUGE-1 F（自实现，选择均记录），f̃ ∈ {coverage(α=0.25),
  diversity(farthest-first 聚类), facility-location(tf 余弦)}，全部不看参考摘要；K=3..7；
  无随机性，确定性两次运行 MD5 一致；11 秒全量。4,377 统一行 + 91,683 (d,d̃) 对落盘。
- 数据问题（诚实处理）：本地 Summaries 只有 business 类（原 zip 即缺 sport/tech；INVENTORY
  早先误写"各 5 类目"，已订正）。sport/tech 参考摘要由 HuggingFace 同源 CSV 精确回填，
  business 上 99/100 篇逐 token 一致验证可信度；回填 CSV 已入库 data/raw/（离线可复现，
  主会话改脚本优先读本地并复跑确认）。
- 结果（K=5 中位数）：ratio coverage 0.712 / diversity 0.662 / facility 0.628；
  η^sel 中位数 3.5 / 9.9 / 9.3（尾极重，须用分位数汇报）；最好 surrogate = coverage。
- "模型边界外"实测而非断言：穷举 70,560 个三元组，ROUGE-1 F 的 submodular 违反 2.14%、
  单调违反 7.12%（三个 f̃ 均 0 违反）；被选步 d ≤ 0 占 12-19%，方向违反 12-17%。
  CELF 在非 submodular f 上 K=6/7 有 ~1% 文章略差（≤0.026），如实记录未修正。
- 复现：python3 results/E3_run.py（主会话复跑退出码 0）；详见 results/E3_notes.md、E3_summary.json。

### E4 最坏实例的数值实现 — PASS（管线 oracle 建立）
- N2 的 V_j 实例（K∈{3,5,8}×每段一个 η，16 个）与 U_K 实例（â=2，3 个）全部通过实验管线
  （CachedSetFunction + CELF lazy greedy，不是符号验证）：realized ratio 与理论差 ≤1.1e-16。
- 发现并修复一个真实管线问题：最坏实例每步预测增益是精确 tie，浮点噪声 ~1e-16 会翻转
  对抗 tie 方向。给 lazy_greedy 加可选 quantize 参数（增益四舍五入到 1e-10 后比较，
  tie_key 决定方向），仅 E4 启用，真实数据任务不启用（已在代码注释与脚本头注明）。
- 三把尺子在最坏实例上的读数：V_j 实例 η^sel = η 精确成立，η^path(1e-9) = η；U_K 实例两者 = â。
  viol_sign_pct 全 0。
- 复现：python3 results/E4_worst_instances.py（约 1 分钟，退出码 0）；
  数据 results/E4_worst_case.csv、E4_rows.csv（统一行格式）。

### E0 环境盘点与共享管线 — PASS
- src/im_graph.py（图类 + 有向/无向边表加载 + 观测图边抽样 + 一跳覆盖 + CELF lazy greedy +
  真值最大增益扫描）、src/statistics.py（η^sel、η^path(ε)、ratio、统一行格式、L_K）。
  SubModular.ipynb 缺失（INVENTORY 已记录），模块从头实现；按规定不含 R-step 与 error-oracle 代码。
- 冒烟测试：lazy greedy 与朴素 greedy 逐步一致；观测图抽样种子确定性。
- 数据盘点更新进 data/INVENTORY.md（E0 期望清单逐项状态；原 Twitter/reddit/Facebook 图缺失，
  E2 使用替代图；下载 fallback 未触发）。

### ——— 第二晚（TASKS2.md）———

### N6 加性修正的误差模型 — PASS（理论紧 + 实证半正半负，全部诚实落盘）
- 理论 [HAND-PROOF-UNREVIEWED + LP oracle]：模型 d/η_u − ε ≤ d̃ ≤ η_o·d + ε 下
  F^PG ≥ L_K(η)·(OPT − 2Kη_u·ε)；关键结构：ε 只与 η_u 相乘（回代发生在被选元素上）。
- LP 检验超预期：16/16 无违反且发现 **LP(ε) = ρ_K(η)·max(0, 1−2Kη_u·ε) 精确成立**
  （29 点残差 ≤2.8e-16，覆盖 K=2,3,4 与三种误差拆分）[CONJECTURE N6-C1]——
  即推导的 ε 部分是紧的，唯一松弛就是 ε=0 时已有的 ρ_K − L_K。ε* = OPT/(2Kη_u) 只依赖 η_u（已验证）。
- 实证 trimmed 重测（1260 行）：η^path 大幅下降（K=7 中位数 43→4.8、60→5.5、371→17.9）但
  下界在 K ≥ 5 仍实质 vacuous（数值 0.009-0.074 vs 实测 ratio 0.94-0.96；wine 转负）；
  **实质进步在 K=3 的 ε 优化认证下界**：0.286/0.439（breast_cancer/digits20，比 T6 好 10-31 倍），wine 例外。
- 重要负面结果：任务规定的 ε（1-2 个量化单位）下混合模型对 1110/1260 行不可行
  （存在 d>0 且 d̃<−ε 的对）；使可行的最小 ε 中位数 3-12.6 个单位。additive_bound 的正确读法
  已在 md 中写明。s10 的 10 行"违反"全部是前提失配（f(∅)≠0、oracle greedy 非 OPT），非定理反例。
- 复现：N6_additive_lp.py（11 秒）、N6_eta_trimmed.py（247 秒），主会话复跑均退出码 0；
  详见 results/N6_additive_model.md、N6_eta_trimmed.csv、figures/N6_*.png。
- 未做（[FAILED] 子项）：结合 N1 "mono 乘子恒为 0" 检查加性项能否绕开 monotonicity（时间用尽）。

### N5 有界查询版 hardness 定理草稿 — PASS（含对 T2 结论 1 的实质修正）
- results/N5_bounded_query_hardness.tex：concentration 引理（并集界 + 超几何，n ≥ 4K^{c+2}）、
  取值引理、确定性定理 + 随机化推论（只用平均论证，不冒称 Yao minimax），每步状态标签，
  第 6 节逐词空洞性检验 V1-V17（删 adaptive；poly-query/查询大小≤K/K≥2τ/(H)/η>1 为承重限定词；
  all-pairs 版标 open；全文不写 tight）。
- **修正 T2 结论 1**：δ 闭式完整形式是 1+δ = max{a^τK/(K−τ), a^{1−τ}}²，第二支来自 y 方向
  balanced 边，第一支占优 iff η ≥ 2−1/τ。第一晚测试点全在第一支区所以未暴露。
  Oracle：N5_delta_at_etahat.py 40 点 + 主会话在分歧点 (4,1.2,2) 用第一晚网格 LP 独立复核
  （LP=0.595568=第二支）。已同步修正 RESEARCH_STATE R11(a) 与 T2_summary。
- 定理需两处结构性修改：加假设 (H) η̂ ≥ 1（充分条件 K ≥ τ(1+2/ln η)）；η̂ 用 Φ(θ)=θ(1+δ(θ))
  的不动点定义（δ 对 η 不再单调）。sympy 15/15：δ→0（首阶 2τ(1−1/η)/K）、L_K(η̂) → 1−e^{−1/η} 等。
- 诚实边界：max 闭式一般 (K,τ,η) 仍 [CONJECTURE]，τ 只测 {1,2}（c ∈ {0,1}）；F 固定非最优
  （N4 的最优 (F,G) 代入会更强但只测 τ=1，列为下一步）；有限 K 下本定理弱于 greedy 侧曲线，
  内容是渐近的。主会话复跑两个脚本均退出码 0。

### N2 中间 j 的可实现实例 [VERIFIED-SYMBOLIC 一般 K，模分支枚举] — PASS（R10 升级为精确最坏值）
- 对每个 j（0 ≤ j ≤ K）构造显式 (f, f̃)：三类元素 C(j)+P(K−j)+O(K)，
  f = 1 − q^x(1−y/K) + zδ_jχ(y)，f̃ = W(0) − q^xW(y) + zδ̃χ(y)（W(0)=k1/(Kη_u)，W(y)=(K−y)η_o/K，
  δ_j=q^j/(Kη)）。机制：f̃ 把每步候选压成 O 真实增益/η_u，每步与 O 打平（tie 对抗承重）。
- j=0 退化为 R2 modular 实例；j=K 与 R7/U_K 逐点相同；中间 j 全新。取 j*(η) 即 ρ_K ≤ min_j V_j。
- 验证：480/480（主会话复跑退出码 0）：44 条一般 K 符号 + K=2..6 全格点 + K=2..8 精确 Fraction
  + R5 表 25 点重现 + 与 K=2 witness 逐元素一致 + strict tie 变体极限。
- **净结论：ρ_K(η) = min_j V_j(η) 两个方向都到证书级**（≤ 方向 N2 实例；≥ 方向 N1 对偶证书），
  仅剩 R6 有效不等式那一步 [HAND-PROOF-UNREVIEWED]。
- 最需人类判断（N2 caveat 3）：f̃ 单调但不 submodular（与 R7 同病）；若模型要求 f̃ 也 submodular，
  ρ_K 可能变大，现有全部上界实例失效，这是建模层面的决定。

### N4 Hardness 的解析化 [VERIFIED-SYMBOLIC 一般 (K,η) + VERIFIED-LP 42 组精确有理] — PASS
- **修正 T2 结论 3 的解读**：relaxF LP 值对 n 未收敛（T2 用的 n=8K 不够大）；n→∞ 极限
  逐点等于 y≤τ 定义下的值，而后者 = **ρ_K^LP = min_j V_j（R10 闭式），严格小于 U_K**。
  超额项衰减极快（η=2: K=4/8/16/32 为 3.2e-4/5.9e-7/4.4e-12/5.2e-22）。
  两条研究线合流：poly-query 技术的极限恰是 greedy 最坏比闭式。
- 拿到 LP 最优 (F,G) 完整显式公式：相位 1（x ≤ j）逐字是 R7/U_K 实例（a=q=1−1/(η(K−1)+1)）；
  相位 2（j < x ≤ T）是 coherence lemma R3(ii) 处处取等的常数增量尾巴，g_T=r_T 处闭合；
  D 与 value 的闭式见 results/N4_hardness_construction.md。
- T2 的 (8,3) 意外观察获解释：X=n−K 太小放不下相位 2 尾巴，长程约束族 L 消失，值掉回 V_j。
- 紧约束 100% 落入 8 个族（K=3..6 全覆盖）：A-D 精确复现 reduced LP 的四类约束；
  族 L（穿过非平衡行的长程链）是 reduced LP 没有的，正是有限 n 超额项来源。
- 诚实边界：j、m* 索引闭式 [CONJECTURE]（264 点）；η > K−1 时闭式仅可行非最优；
  (5,4) 一个点差 3.2e-7 未查明；显式构造只对 y≤τ 可行，真 balanced 定义仍需 N5 的
  concentration 论证；只测 τ=1、√η 拆分。
- 复现：N4_check.py（42 组精确有理可行性，主会话复跑退出码 0）、N4_symbolic.py（19/19，
  主会话复跑退出码 0）、N4_duals.py、N4_figures.py；图 figures/N4_*.png。

### N3 R6 在 K=5 的验证 [VERIFIED-LP] — PASS
- n=10 全格点 LP（2048 变量 × 38435 行）与 reduced(5,η) 在 η ∈ {1.5,2,3,4.5} 完全一致
  （≤1.7e-16），且都等于 R10 闭式 min_j V_j；四个值为干净有理数 6389/12005、1597/3645、
  269/845、21/95，段号 j=4,3,2,1 与分段吻合。R6 的"上界=reduced"由 K≤4 扩到 K≤5。
- 关键自检：同一构造器在 n=6,K=3 枚举全部 20 个 O 与 code/worst_case_lp.py 逐位一致（diff=0）。
- O 类型扫描（η=1.5,2 全部 6 类）：值随 |O∩greedy| 严格递增，不相交类型确为 argmin。
- 支持 R5 猜想：η=4.5 < K=5 时 21/95 < 1/4.5。
- 复现：python3 results/N3_K5_lattice.py（约 17 分钟；主会话核对 CSV 与日志后跳过整体复跑，
  理由：脚本自带 n=6 对已验证代码的逐位等价自检）。caveats：每类型只解一个 O（对称性依据）、
  只测 single-element √η 拆分、n=2K。

### N1 一般 K 的对偶证书 [VERIFIED-SYMBOLIC] — PASS（R10 下界方向升级为一般 K 定理级）
- 全部乘子写成 (K,η,j) 显式公式（记 M = Kη−(K−j)）：段 j≥1 上 y_sum(0)=−q^{j−1}M/(Kk1)、
  y_sum(t)=−q^{j−1−t}M/k1²（1≤t≤j−1）、y_sum(j)=(η−(K−j+1))/k1、y_cons(t≤j−1)=−q^{j−1−t}M/(Kk1)、
  y_cons(t≥j)=−(K−1−t)/(K(η−1))、y_pred(t≥j)=−(η−(K−t))/(K(η−1))、y_mono≡0；j=0 段沿用 T3。
- 验证：符号 (K,j,t,i) 全自由的三条恒等式（对偶可行等式、段内非正性的盒上正性证书、bᵀy=V_j）
  + K=2..10 共 54 段的独立暴力符号 LP 复核 + 与第一晚 58 个乘子逐个比对 0 不符。
  320/320 PASS，主会话复跑确认（60 秒，退出码 0）。唯一非 oracle 步骤是 t 分支的有限枚举（组合记账）。
- 重要副产品：(i) mono 乘子恒为 0，下界证明不需要 monotonicity（删 mono 行 LP 值不变，双验证）；
  (ii) U_K − V_{K−1} = q^{K−1}(η−1)/(Kηk1) > 0 [VERIFIED-SYMBOLIC]，R7 实例族达不到 V_{K−1}，
  证紧需要新实例（正是 N2）；(iii) V_i−V_{i+1} 恒等式给出整数分段点的直接证明。
- 诚实边界：reduced LP 值 = 真实 ρ_K 仍依赖 R6（[HAND-PROOF-UNREVIEWED] + K≤4 有限点）；
  L_K ≤ min_j V_j 仅数值支持 [CONJECTURE]；两个 scipy 对偶退化点已如实列出（非反例）。
- 复现：python3 results/N1_dual_certificate.py；详见 results/N1_dual_certificate.md/.json。

### N0 术语表与规则更新 — PASS
- GLOSSARY.md 建立（13 个词条，含任务规定的 8 个必含术语：近似比方向、consistency 撞名改称
  coherence lemma、tight 三义、any algorithm 三范围、robust 禁用、η 与 Agarwal-Balkanski 撞名、
  information-theoretic、deterministic vs randomized 下界）。
- CLAUDE.md 末尾新增"空洞性检验"规则；RESEARCH_STATE.md 追加 R10-R13（各带状态标签）、
  R7 升级注记、R3 更名、已知论文错误新增"Section 1.1 近似比定义方向写反"。
- results/T7_theorems.tex 的 Lemma B 同步改名 Coherence。代码内部约束标识 cons(t) 不动
  （属脚本内部命名，改动会破坏第一晚脚本的可复现性，保守处理并在 GLOSSARY 注明）。

### T7 定理陈述与证明草稿 — PASS
- `results/T7_theorems.tex`：Theorem A（trajectory-tight，L_K(η^path) 下界 + U_K 逐 K 紧，
  紧性现为一般 K [VERIFIED-SYMBOLIC]）、Lemma B（consistency，[HAND-PROOF-UNREVIEWED]）、
  Theorem C（K=2 精确，min{1/η, 3/(2(η+1))}）+ K=3,4 闭式 remark（[VERIFIED-SYMBOLIC]
  作为 reduced LP 值）、Theorem D（1/η ceiling + 穷举匹配，[HAND-PROOF-UNREVIEWED]）、
  Corollary E（weak submodularity，γ 版本，Das–Kempe [CITATION-NEEDS-VERIFICATION]）。
- 每条定理的状态标签与复现脚本以 LaTeX 注释内联；需人工检查的证明步骤已逐一标注。

### T5 显式实例 U_K 的符号验证 [VERIFIED-SYMBOLIC 一般 K] — PASS
- 105/105 检查通过（35 项一般 K 符号 + 70 项 K=2..8 具体符号），运行 4 秒，主会话复跑确认。
- 关键技巧：p=a^x、Q=a^dx 参数化把全部断言化为有理函数恒等式，无符号指数，
  故 R7 的 5 个 item（四类比值、单调+submodular、G(x,K)=1、tie 恒等式、η 与 U_K 重参数化）
  全部一般 K 符号验证。额外收获：all-pairs 误差 η_u=â、η_o=aK/(K−1) 也一般 K 符号可证。
- 剩两个平凡手工步骤（论文一句话）：greedy 轨迹 y=0 的一行归纳（K=2..8 已显式符号模拟）；
  参数化忠实性（a∈(0,1) 已符号证）。R7 升级为 [VERIFIED-SYMBOLIC]。
- 复现：`python3 results/T5_symbolic.py`（退出码 0 当且仅当全过），输出 T5_symbolic.txt/json。

### T4 R=2 lookahead 的精确最坏值 [VERIFIED-LP] — PASS
- K=4 pair greedy（all-pairs 误差，tie 对抗）的 LP 精确最坏值：η=1.5: 3/5，η=2: 1/2，
  η=3: 1/3，与 K=2 闭式 ρ_2(η)=min{1/η, 3/(2(η+1))} 吻合到 3.3e-16；n=8 与 n=9 完全一致。
  即 2-lookahead 把 K=4 曲线精确抬到 K'=K/2 的 single-step 曲线 [一般 K 为 CONJECTURE]。
- 公平对照：single-step 在 all-pairs 误差下与 R5 single-element 值一致（0.543576, 22/49, 13/40）。
  改善 +0.056/+0.051/+0.008，随 η 增大消失；η ≥ K/2 = 2 时 pair 已达 R2 普适上界 1/η。
- 论文 R-step 下界 1−(1−1/(2η))² 成立但不紧（差 0.03~0.06）。若 ρ_{K/R} 对应关系成立，
  由 R8 得常数 R 的 lookahead 不改变 1−e^{−1/η} 渐近极限，收益是有限 K 效应。
- 复现：`python3 results/T4_pair_greedy_lp.py full|n9|smoke`；对称性检查 T4_symmetry_check.py
  （70 个 O 的 LP 值只依赖类型，PASS）；数据 T4_pair_vs_single.csv/json。

### T2 Poly-query hardness 构造（R9）的数值验证 — PASS（结论对 R9 是"否定 + 修复路线"）
- 结论 1 [VERIFIED-LP 有限实例]：y ≤ τ 定义下候选可行，最小 δ 有精确闭式
  1+δ = (a^τK/(K−τ))²（全格点 4 组 (n,K) × 网格 K ≤ 32 全部吻合，δ = O(τ/K) → 0）。
- 结论 2 [VERIFIED-LP + 结构性证书]：真正的 balanced 定义 |y−K|S|/n| ≤ τ 下，
  R9 候选对任意 δ 不可行。证书：balanced 的 S ⊇ O 加 B 元素时 Δ_e F = 0（F 在 y=K 处
  x 方向平坦）但 Ĝ 严格递增。证书对一切 n 存在，换 τ/n/δ 都救不了，必须改 F。
  这否定了 R9 的未解决问题（对该候选 F）。
- 结论 3 [VERIFIED-LP 有限实例]：放开 F 后（步骤 5）两种定义都可行；技术能证到的
  hardness 值贴着 U_K(η)，K→∞ 收敛到 1 − e^{−1/η}（K ≤ 24，n ≤ 192）。有限 K 时
  该技术不能把 hardness 压到 L_K 以下。LP 最优 F 的形状（Ĝ 大集合处饱和）已导出为
  解析化候选（results/T2_relaxF_solution_example.json）。
- 方法学：约束对 B/O 内置换协变，LP 可对称化到 (x,y) 网格（全格点 crosscheck 全 PASS，
  含 relaxF 模式的独立全格点核对，6/6 精确相等）。
- 复现：results/T2_hardness_lp.py（全格点）、T2_hardness_grid.py（网格三模式）、
  T2_relaxF_lattice_check.py、T2_figures.py；数据 T2_table.csv、T2_grid_*.csv；
  图 figures/T2_delta_vs_K.png、T2_relaxF_ratio.png；详见 results/T2_summary.md。

### T6 真实 surrogate 的 η^path 测量 — PASS（实证测量）
- 做了什么：breast_cancer / wine / digits(前 20 特征)，f = 决策树 held-out accuracy，
  f̃ = 5-fold CV accuracy，greedy on f̃ 轨迹上测 η^path，30 次划分，K=1..7。
  openml airline satisfaction 因网络受限跳过（已记录）。
- 结果：η^path 很大且重尾（K=7 中位数 43 / 60 / 371），L_K(η^path) 下界 vacuous（0.023/0.017/0.003）；
  但实际 ratio(K=7) 中位数 0.963/0.941/0.957，630 行最差 0.718。诊断脚本确认 η 爆炸由
  accuracy 量化尺度的近零增益主导（argmax 对的 d̃ 或 d 中位数恰为 1 个量化单位）。
  方向一致性不成立：17%-32% 候选对 d 与 d̃ 反号；29%-53% 的对 d ≤ 0（f 不单调）。
- 对论文的含义：不能讲"实测 η 小"，应讲 raw multiplicative 误差对 ML surrogate 过于悲观，
  为 additive-multiplicative / trimmed 误差变体提供直接动机。
- 复现：`python3 results/T6_eta_path.py`（约 5 分钟）、`results/T6_argmax_diagnostic.py`。
  数据 `results/T6_eta_path.csv`，图 `figures/T6_*.png`，详见 `results/T6_summary.md`。

### T3 Reduced LP 对偶证书与 K=3(+K=4) 闭式 [VERIFIED-SYMBOLIC]（作为 reduced LP 值）— PASS
- 结果：定义 q=(K−1)η/((K−1)η+1)，V_j(η)=1−q^j(1−(K−j)/(Kη))，分段点为整数 η=2..K，
  则 reduced LP 值在段 [K−j,K−j+1] 上恰为 V_j。
  K=3：[1,2] (16η+3)/(3(2η+1)²)；[2,3] 7/(3(2η+1))；[3,∞) 1/η。
  K=4：[1,2] (135η²+36η+4)/(4(3η+1)³)；[2,3] (21η+2)/(2(3η+1)²)；[3,4] 13/(4(3η+1))；[4,∞) 1/η。
- 验证：K=2,3,4 全部 9 段构造显式 primal 解与对偶证书，sympy 精确算术 + Sturm 根计数
  整段验证（duality gap ≤1.1e−16）；K=2 恰好收回 R4；R5 全表 Fraction 精确重现；
  60 点拟合流程 held-out 残差 ≤3.3e−16。一般 K 猜想 min_j V_j 在 K=2..6×41 点 max 偏差 8.9e−16
  [CONJECTURE]。这把 "ρ_K=1/η iff η≥K"（R5 conjecture）在 K≤4 的 reduced-LP 层面变成定理。
- Caveat：闭式=ρ_K 还依赖 R6 的 reduced=全格点（K≤4 已验，一般 K 是 [HAND-PROOF-UNREVIEWED] 下界）。
- 复现：`python3 results/T3_duals.py`、`results/T3_K3_closed_form.py`；
  详见 `results/T3_K3_closed_form.md`、`results/T3_duals.json`、`figures/T3_K3_pieces.png`。

### T1 基线复现 [VERIFIED-LP] — PASS
- 做了什么：运行 `code/check_explicit_instance.py` 与 `code/worst_case_lp.py` 的 worst_case()
  （K=2 n=4、K=3 n=6，single-element 误差，η_u=η_o=√η，η ∈ {1,1.5,2,2.5,3,4}）。
- 结果：explicit instance 6 组参数 ALL PASS；12 个 LP 值与 RESEARCH_STATE.md R5 全部一致（<1e-7）。
- 复现：`python3 results/T1_baseline.py`，输出 `results/T1_baseline.txt`。
- 下一步：T2。

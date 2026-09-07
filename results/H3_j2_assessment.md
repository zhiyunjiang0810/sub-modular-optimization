# H3_j2_assessment.md — 对外部审查 J2（GPT/Codex）的复核裁定（2026-09-07）

输入：results/J2_review.md、results/J2_hardness_repair.tex、J2 复现包（脚本与
证据 CSV 已并入 results/，见文末清单）。复核方式：(1) 在本环境原样重跑 J2 的
两个 oracle 脚本；(2) 用我自己的独立实现重算其关键声称
（results/H3_j2_recheck.py，全部 PASS，独立于 J2 代码）。

## 总裁定

J2 的质量很高：**六项主要发现全部复核成立**，其中两项是给我们送分的
（R6 证书、hardness 更强闭式），四项是必须修的真实错误。个别措辞我有保留
（见"保留意见"）。建议按本文末的顺序采纳。

## 逐项裁定（按 J2 章节）

### §2 R6 归约的显式 slack 证书 — 成立，重大正面收获
- 我用 sympy 独立验证了 case (b) 的两条配平恒等式（consistency 与
  prediction 各拆成三个非负项：离轨上带、greedy、下带），恒等式精确成立；
  case (c) consistency slack 恒为零、case (a) 退化为 d_t>=0 也对。
- J2 的 1,536 个全格点 LP 用真实 lattice 变量最小化待审约束的 slack，
  设计上避开了循环论证，本环境复跑 all_passed。
- **意义：app:validity 这一步（主定理 >= 方向唯一悬空的手证）可以升级**：
  恒等式部分 [VERIFIED-SYMBOLIC]，非负性逐项来自模型前提。这是 G5 严重
  第 2 条的正面了结。证书同时精确解释了为什么 cons 约束必须用全局 band
  （第一项用的是离轨状态 S∪{o} 的上带），与 rem:app-rulers 的既有 caveat
  一致，不需要改主定理的陈述口径。

### §4 selection error 的重定义 — 成立，采纳其修法
- 三元素 modular 反例我独立复算：greedy 依预测选 (e3,e1)，ratio=1/2，
  旧定义 eta_sel=1 而 L_2(1)=3/4，反例成立。它比 G5 的 63 行 CSV 证据更
  干净（modular、无 tie、无非 submodular 干扰）。
- J2 推荐的修法（逐步 a_t：正常步取 M_t/g_t，良性零步 M_t=g_t=0 取 1，
  有害零步 g_t=0<M_t 取无穷、L_K(∞)=0）就是我们三个候选修法中
  "重定义"的精细版。它保留事后可测的 certificate 叙事、保留链
  eta_sel<=eta_tr<=eta（有限全局带下有害零步不可能发生）、保留
  Theorem 7 tightness 族的取等。**我同意这是三选一里最优的**，
  比"加 Definition 1 前提"好（那会让证书需要不可检查的全局前提）。
- 附带的逐步乘积界 1-∏(1-1/(K a_t)) 是合理的补充，J1 有 1,905 条轨迹
  精确检查；一般装配保持 [HAND-PROOF-UNREVIEWED]，采纳时按此标注。
- GS 2007 方向 alpha=eta_sel 再次确认（第三方独立读原文，与 F6 一致）。

### §5 两把尺反例（rho 不是 selection-error 包络）— 成立，图注必修
- 我全枚举 16 个子集独立复算：f、f̃ 均 monotone submodular，C 与 O 之间
  无 tie（只有 C 类内对称 tie），greedy 选满 C，
  eta_sel=2、eta_tr=6、eta=27/2，ratio=7/16=L_2(2) < rho_2(2)=1/2。
- 结论：主图把 rho_K 画在 eta_sel 横轴上只能作"另一误差类的参照线"，
  不能叫这张图的 worst-case envelope；caption 的 "Real tasks sit far
  above the worst-case curves" 也因 63 行 L 违例而不成立。G5 的
  "70 行低于 rho 曲线"不是合法违例计数，这点 J2 与 G5 判断一致。

### §6 hardness 校准 — 成立，建议采纳其更强闭式
- 我独立暴力枚举 count grid 全部边（5 组 (K,tau,theta)，含大 x）：
  边比值极值恰为 A 与 1/(theta B)，无第三支；实际最小误差乘积
  eta_act = theta A B = (theta K-1)/(K-tau) 精确成立。
- 由此确认两件事：(1) 我们的 delta 闭式 [CONJECTURE] 问题以更强形式
  了结（四行边表穷尽）；(2) 原 Theorem 12 的 "error exactly eta" 在
  Phi 校准下不成立（witness 实际误差 theta A B < Phi(theta)，例
  (K,tau,theta)=(4,1,4)：实际 5 < Phi=25/4），这是真实缺口。
- 新校准 H_{K,tau}(eta) = 1-(1-1/(eta(K-tau)+1))^K = L_K(thetabar)，
  我数值复算 J2 表格 4 行全部吻合，且新界严格不弱于旧反函数界、
  仍 >= L_K(eta)（自洽）。tau=1 时 H = U_K(eta)，与旧显式族值重合，
  是一个漂亮的 sanity check。beta 缩放解决误差拆分。
  J2_hardness_repair.tex 可作为 app:hardness 的替换稿基础；其概率/
  transcript 装配自标 [HAND-PROOF-UNREVIEWED]，采纳时保持该标签。
- 附带修正确认：tau 需取整数（ceil(c)+1）；Phi 导数排版有 1/K 笔误；
  N5_delta 脚本用的是旧显式 etahat 而非 Phi^{-1}（不能当作现行定理的
  直接验证），这条对我们此前的验证口径是一个真实的降级提醒。

### §7 查询类最优性（rem:hardness-pins）— 成立，比 G5 的版本更深
- c=0 单查询反例逻辑我核对无误（藏两元素在 Q∪T 外，输出比 0，误差 2）；
  J2 对 n=16,K=2 的 18,769 个组合逐一构造了 witness。
- 结论：Remark 不只是"每步 K 次查询"的笔误（G5 已发现），而是
  "pinned optimum" 对小 c 直接为假：该类要容纳 greedy 需要
  nK <= n^c（如整数 c>=2）。有限间隙应写 O((c+1)/K)。

### §8 实验复算 — 全部成立
- 63 行 L 违例与 G5 一致；**E1 也在模型外**（711/720 前缀观察到负真实
  候选边际）是新发现，E1 的 "median run certifies" 用语必须撤回。
- E2 的 16 个有害零步、225 个受影响 K>=2 前缀：我独立从 E2_rows.csv
  复算得完全相同的 225/16；采样对的 30,416（真0预正）与 5,952
  （真正预0）两计数我也逐一复算吻合。G3_gen_numbers.py 里
  "structurally zero" 注释确实错误（viol=0 是覆盖值的结构保证，
  边际零点不对齐不在其内），需删。
- **OPT 代理方向措辞**：experiments.tex 第 69、94 行把分母称作
  "upper-estimate proxy for the optimum"，方向反了：greedy-on-f 是可行
  解，其值是 OPT 的下估，故 ratio 是真实比的上估。附录 app:exp-opt 的
  同类句子方向是对的，正文两处必修。

### §9 rem:exact-gap 两处收缩 — 成立
- eta=1 时 Definition 1 强制 f̃=f，两模型重合，"strictly improves for
  eta<K-1" 至少须排除 eta=1，且一般区间只能按 LP 点位陈述。
- "so U_K is no longer an upper bound" 是推理跳跃：实例失效不等于上界
  失效，且 K=3, eta=1.5 处 19/33 < 37/64=U_3(1.5)，U_K 在该点仍是上界。
  两处都是 D1 定稿措辞里的缺陷，需要人拍板改法（TASKS5 指定过原措辞）。

## 保留意见（对 J2 的三点 qualification）

1. J2 建议"G5 的相关措辞也应一起纠正"：G5_review.md 是存档的审稿产物，
   不改档案，只在采纳记录里注明其两处误判（rho 违例计数、tie 定性）。
2. J2 的新 hardness 定理与 selection-error 新定义均含
   [HAND-PROOF-UNREVIEWED] 装配段；采纳它们是"替换更强的草稿"而非
   "定理已证"，状态标签制度不变。
3. J2 对 branch 分界的历史归因（brief/RESEARCH_STATE 旧措辞 vs N5 文本）
   与我们的记录一致，无需额外动作。

## 建议采纳顺序（下一个工作块）

1. **P0** 换 def:etasel（J2 的 a_t 逐步定义 + L_K(∞)=0），修
   prop:guarantee 附录证明的零步段与 GS 对应句；同步 Theorem 7 陈述核对。
2. **P0** 实验层连锁：E2 的 225 个前缀 eta_sel 改 ∞ 并重算宏；撤回
   E1/E3 的模型内 certificate 用语（改 empirical diagnostic）；修正文
   两处 OPT 代理方向；重画主图（rho 曲线语义标注或移除）与 caption；
   删 "structurally zero" 注释。
3. **P1** 把 J2 §2 的 slack 证书写进 app:validity，状态升级为
   恒等式 [VERIFIED-SYMBOLIC] + 前提逐项非负。
4. **P1** 用 J2_hardness_repair.tex 重做 app:hardness 与 thm:hardness
   （eta_act 校准、整数 tau、查询类最优性范围、O((c+1)/K)）。
5. **P2** rem:exact-gap 两处收缩；V_i 索引 0<=i<=K-2；严格扰动端点补法；
   N5 导数笔误；REVIEW_BRIEF/RESEARCH_STATE 同步。

## 本次复核的产物

- results/H3_j2_recheck.py：独立重算脚本（sympy 恒等式 ×2、三元素反例、
  两把尺实例全枚举、hardness 边极值暴力枚举 ×5 组、新旧校准表 4 行、
  E2 前缀计数），全部 PASS，退出码 0。
- J2 包并入：results/J2_review.md、J2_core_oracles.{py,json,log}、
  J2_extra_audit.{py,json,log}、J2_hardness_repair.tex、
  J2_bound_violations.csv、J2_selection_diagnostics.csv（若含）、
  J2_E2_zero_step_evidence.csv、J2_original_N{1,2,5_delta}.log、
  J1_independent_audit.py、J1_oracle_output.json。
- 本环境复跑：J2_core_oracles 6.7 秒 all_passed=true；J2_extra_audit
  all_passed=true。

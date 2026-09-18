# V11 顺便发现（不进正文）

（按 TASKS11 禁止项：任何"顺便发现"记这里，不新增理论。）

- Q0：正文里 T1 的 label 是 `prop:necessity`（TASKS11 称 prop:nobound）；两者指同一命题，
  矩阵用正文 label 并注明别名。
- Q0：`Theorem~\ref{thm:ceiling}` 在正文与附录共出现 5 处（results.tex 3、appendix_proofs.tex 2）；
  thm:ceiling 目前是 theorem 环境。TASKS11 Q10 的 grep 判据要求 0 处，即 thm:ceiling 应作
  Proposition 引用；这是环境名/引用措辞的表现层变化，不改数学内容，Q10 处理并记录。
- Q0（输入到齐后）：appendix_model_proofs.tex 用 label `prop:nobound`、`app:model` 与 bib 键 `horel2016`，
  正文现用 `prop:necessity`、`app:necessity`、`horel2016maximization`；接线需改这三处（未做，见
  MISSING_INPUTS.md 落库决定）。
- Q0：Prop 1 两个构造：台账/app:necessity 用 γ = K²/(n(n−K))（η = 1/γ = n(n−K)/K²），
  appendix_model_proofs 用 δ = K/(n−K)（η = (n−K)/K，恰匹配陈述界）。两者 Q1 都验；
  建议保留 δ 版（直接匹配陈述、任意 δ 推广），γ 版随 app:model 接线时删除（作者操作）。
- Q0：J8 的算法有 EPS = 1/10000 的池阈值与 8 个 secondary 集合、127/128 与 1/1024 概率；
  期望下界 3/5 + 1/400000 与紧实例值 3/5 + 1/2048 的关系（1/2048 = 195.3125/400000）待 Q9 复核。
- Q1–Q8 工作流的 12 条顺便发现（η^tr 方案二下须按乘积截断；thm:linear-anysize 的 limit 未证存在；
  J8 盲审 II-b 缺口；thm:exact 另一组对偶支撑；J6 small-set-only 机制盲审到不了；hardness 路线二只到
  n ≥ 4K^{2τ}；thm:ceiling K ≥ 2 无用；prop:necessity |T| ≤ K；prop:valueacc n ≥ 2 与 f 不恒零；
  cor:limit K 下端；引文 Theorem 5 vs Proposition 6；盲审提示模板噪声）逐条见
  results/V11/VERIFICATION_MATRIX.md "重点发现"一节，此处不重复。
- Q1–Q8：两个 oracle 代理复跑旧脚本时改写了 results/J2_core_oracles.json 与 results/N1_dual_certificate.json
  的耗时字段（内容不变），已 `git checkout` 还原；V11 自己的产出全部在 results/V11/ 下。
- Q11（J9 盲审，不进正文）：路线二独立给出条件定理"若有限可行性问题 (P_{K,η})（count grid +
  truncation m = 3(K−1)，f 依赖 T 与 O）可解，则任意大小查询、≤ cnK 次的确定性算法在
  n ≥ 4cK⁵(K+2)² 上比值 ≤ ρ_K"，并用 LP 确认 K=2..7 可解、K=2,3,4 精确有理实例；同时独立确认
  T-independent count-grid 族的 excess 严格为正（与第十晚 W 结论一致）。一般 K 闭式未闭合。
  全部只作 J9 原文到达后的比对材料。

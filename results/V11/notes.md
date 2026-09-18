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
- Q11（J9 盲审，不进正文）：路线二独立给出条件定理"若有限可行性问题 (P_{K,η})（count grid +
  truncation m = 3(K−1)，f 依赖 T 与 O）可解，则任意大小查询、≤ cnK 次的确定性算法在
  n ≥ 4cK⁵(K+2)² 上比值 ≤ ρ_K"，并用 LP 确认 K=2..7 可解、K=2,3,4 精确有理实例；同时独立确认
  T-independent count-grid 族的 excess 严格为正（与第十晚 W 结论一致）。一般 K 闭式未闭合。
  全部只作 J9 原文到达后的比对材料。

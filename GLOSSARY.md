# GLOSSARY.md — 术语表（本文含义 vs 文献中的其他含义）

每行一个术语。写论文和报告时遇到左列术语，按"本文含义"使用；与文献撞名的，按"注意"列处理。

| 术语 | 本文含义 | 文献中的其他含义 / 注意 |
|---|---|---|
| approximation ratio α | α ∈ (0,1]，F^ALG/F^OPT ≥ α，越大越好 | 不少文献用 c ≥ 1（OPT/ALG ≤ c）。**原稿 Section 1.1 写成 "OPT ≤ α·A" 方向反了，需修**（已列入 RESEARCH_STATE 已知错误） |
| consistency | 只用 LAA 文献含义：预测完美（η=1）时算法达到的比值（与 robustness 成对出现） | 与第一晚的 "consistency lemma"（R3）撞名。**R3 在本仓库和论文中一律改称 coherence lemma**，本仓库文档已改（代码内约束标识 cons(t) 不动，属脚本内部命名） |
| coherence lemma | R3 的交换恒等式引理（原名 consistency lemma），见 RESEARCH_STATE R3 | 更名原因见上行 |
| tight | 必须指明三义之一：(a) 对 greedy 紧：存在实例使 predictive greedy 恰达该界（R7/U_K、N2）；(b) 渐近紧：K→∞ 上下界同极限（L_K 与 U_K → 1−e^{−1/η}）；(c) 绝对紧：无任何算法能更好（R2 的 1/η 在 η ≥ K 时） | 论文中裸写 "tight" 一律视为未完成句，改写或删除 |
| any algorithm | 必须指明范围之一：(i) 无限算力+任意多查询：信息论对抗论证（R2）；(ii) poly-query：隐藏 O + concentration（R9/R11/N5）；(iii) poly-time：需复杂度假设，本文不涉及 | 三者的证明方式与结论强度不同，混用即空洞 |
| robust / robustness | LAA 含义：η → ∞ 时仍保有的最坏比值 | **原稿 Lemma 1 声称的 robustness 证明不存在，该词在本仓库禁用**，除非附带 oracle 支撑的具体陈述 |
| η | 本文：η = η_u·η_o，乘性单元素（或 all-pairs）误差，η_u = max d/d̃，η_o = max d̃/d | 与 Agarwal–Balkanski 的 η [CITATION-NEEDS-VERIFICATION] 撞名（他们的定义不同）；引用该文时把他们的记号改写为 η_AB 或明确加脚注 |
| η^path | 只在 greedy 轨迹状态上取 max 的误差（R1、R13/T6） | 是本文自造术语，首次出现时必须定义 |
| information-theoretic | 下界只依赖查询数/可得信息，不依赖任何复杂度假设（R2、poly-query hardness 均属此类） | 文献中有时指熵/编码论证；本文用前者含义并在首次出现时说明 |
| deterministic vs randomized 下界 | R2：确定性算法对固定构造成立（≤ 1/η）；随机算法需把 O 均匀随机化，得 ≤ (1−K/n)/η + K/n；poly-query 版对随机算法用 Yao 原理（N5） | 声明任何下界时必须写明适用的算法类别，缺省即空洞 |
| ρ_K(η) | single-step predictive greedy 在 tie 对抗打破下的精确最坏比 | 与 R10 的 ρ_K^LP（reduced LP 值）区分：两者相等目前只在 K ≤ 4 的有限点 [VERIFIED-LP] |
| balanced（查询/集合） | 隐藏 O 的 hardness 论证里 y = \|S∩O\| 落在 hypergeometric 集中带内的集合；两种形式化：y ≤ τ 与 \|y − K\|S\|/n\| ≤ τ（R11 表明两者结论截然不同） | 使用时必须写明取哪种定义 |

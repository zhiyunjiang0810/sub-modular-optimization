# CLAUDE.md — 通宵研究会话规则

你在协助一篇理论论文（submodular maximization with predictions）的 ICLR 改稿。当前已确立的结果在 `RESEARCH_STATE.md`，今晚任务在 `TASKS.md`。已验证的代码在 `code/`。

## 最重要的一条

你容易写出自洽但错误的证明。所以：**任何数学断言的状态由 oracle 决定，不由你的信心决定。** 可用的 oracle 有三种：LP/数值（scipy），符号验证（sympy），穷举（小实例全格点）。没有 oracle 确认的断言，一律标 `[HAND-PROOF-UNREVIEWED]` 或 `[CONJECTURE]`，不准写 "proved"、"we show"、"it follows"。

状态标签（写报告和代码注释时必须使用）：
- `[VERIFIED-LP]` 数值 LP/穷举确认，附可复现脚本
- `[VERIFIED-SYMBOLIC]` sympy 符号恒等式确认，附脚本
- `[HAND-PROOF-UNREVIEWED]` 有手写证明但无 oracle
- `[CONJECTURE]` 数值支持但无证明
- `[FAILED]` 尝试过但不成立或未完成，写明原因

## 工作纪律

1. 每个任务开始前读 `RESEARCH_STATE.md` 对应条目；不要重新发现已确立的结果，直接复用 `code/` 里的函数。
2. 每个数值结论必须有一个脚本能一键复现，放在 `results/` 下，文件名含任务编号。数据存 JSON/CSV，图存 PNG。
3. 每完成一个任务或每 60 分钟，`git add -A && git commit -m "T<n>: <一句话>"`，并在 `REPORT.md` 追加一段：做了什么、结果、状态标签、失败原因、下一步。
4. 单个任务时间预算见 `TASKS.md`。卡住超过 45 分钟：记录到 `REPORT.md`，跳到下一任务，不要死磕。
5. 不修改 `code/` 里的已验证文件。新代码写新文件，可以 import 旧文件。
6. 所有长命令加 `timeout`。全格点 LP 在 n ≥ 12 时可能很慢，先用小 n 试。
7. 不引用你不确定存在的文献。需要提文献时写 `[CITATION-NEEDS-VERIFICATION]`。
8. 报告用中文，术语和公式保留英文。不用 em dash，不用 "genuinely/honestly"。
9. 网络可能受限。数据集优先用 sklearn 内置；下载失败就记录并用替代。
10. 早上人类会先读 `REPORT.md` 的开头。所以 `REPORT.md` 顶部维护一个 5 行以内的 summary：哪些任务 PASS、哪些 FAIL、最重要的一个发现、最需要人类判断的一个问题。

## 数学约定（与论文一致）

- 近似比 α ∈ (0,1]，越大越好：F^ALG/F^OPT ≥ α。
- 单元素边际增益 d_e(S) = f(S∪{e}) − f(S)，预测 d̃_e(S)。
- 误差 η_u = max d/d̃，η_o = max d̃/d，η = η_u·η_o。默认 single-element 版本（max over 所有 S 和单个 e）；all-pairs 版本 max over 所有 A,B。
- Path error η^path：只对 greedy 轨迹状态 S^t 取 max。
- ρ_K(η)：single-step predictive greedy 在 tie 对抗打破下的精确最坏比。
- L_K(η) = 1 − (1 − 1/(ηK))^K（论文 Theorem 6 下界）。
- U_K(η) = 1 − (1 − 1/(η(K−1)+1))^K（显式实例上界）。

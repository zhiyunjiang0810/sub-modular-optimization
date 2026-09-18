# V11 输入送达记录（Q0，2026-09-18）

## 送达时间线

- 指令到达时下列输入在仓库（origin/main 全部历史）、mirror、uploads 均不存在；
  Q0 盘点后当次会话内经 uploads 送达并落库：
  - HANDOFF_2026-09-18.md → 仓库根目录
  - HANDOFF_ADDENDUM_2026-09-18.md → 仓库根目录
  - appendix_model_proofs.tex → paper/sections/appendix_model_proofs.tex（**未 \input**，见下）
  - J8_claude_spotcheck.py → results/J8/J8_claude_spotcheck.py（原样运行 exit 0，
    results/J8/J8_claude_spotcheck_run.log：紧实例 E[F] = 3/5 + 1/2048 于 n=6,8,12,20，
    400 个随机 coverage 实例 0 违反，最差 4/5）

## 仍缺失

| 输入 | TASKS11 引用处 | 处理 |
|---|---|---|
| results/J8/probe_lottery.md（J8 证明：不等式 (3)、(8)–(12)） | Q9 | 未送达。算法本身由 spot-check 脚本完整给出（四步 + 分布 127/128、1/1024×8），故 Q9 的 C（实现 + 紧实例 + 2000 随机实例）、B（盲审只看算法描述与陈述）、E 可做；"(3)、(8)–(12) 各给精确 LP 对偶证书或 sympy 证明"无法做（不等式文本未知），记 GAP |
| TASKS10 Q5 | Q0 | 仓库的 TASKS10.md 只有 Q0–Q4，从未有 Q5；等价工作即本次 Q9 |
| Horel–Singer、Goundan–Schulz 原文 | Q5、Q10 citations.md | 仓库无原文；尝试网络定位，失败则写 NOT FOUND |

## 落库决定与理由（保守）

- appendix_model_proofs.tex 使用 label `prop:nobound`、`app:model` 与 bib 键 `horel2016`，而正文用
  `prop:necessity`、`app:necessity`、`horel2016maximization`。TASKS11 规定 \label 不动、不改正文陈述，
  故本次**不 \input** 该文件（避免未定义引用与重复 label），只作为 Q1/Q2 的路线一材料并做验证；
  接线与 app:necessity 的 γ 构造删除留给作者（矩阵给出建议与需要改的三处引用）。
- T2(ii)(iii) 按 addendum §B 改写进台账（TASKS11 Q0 明确授权），正文 prop:valueacc 文本不动。
- Definition 1 方案二作为盲审输入的主定义（HANDOFF §3 原文），正文 model.tex 仍是 ≥1 约定，不动。

## Q11（J9）追加

| 输入 | 引用处 | 处理 |
|---|---|---|
| results/J9/j9_proof.md（GPT 任意大小查询确定性 matching 证明） | Q11 | 未送达；见 results/J9/MISSING_INPUT.md。已做 C1 内联不等式与盲审路线二；C2–C4、D、E、比对与 T10e 待文件 |

# J6/J7 交叉核对闸门（Q4 后续日）

## 0. 送达时间线

- 指令到达时 results/J6/、results/J7/ 在两个仓库的全部远端分支、mirror、
  uploads、全盘文件系统均不存在（逐项搜索记录于本会话）。按 M0 夜确立的
  缺失输入规则（results/J5/MISSING_INPUTS.md）先做可独立复算的部分:
  J7 引用的 F3 反例（K=3, eta=667/500）精确复算、W - rho_K 衰减形状、
  替身族对抗模拟（results/J7_fragment_checks.py, exit 0）。
- 随后两个文件经 uploads 送达，已落到指令位置 results/J6/linear_exact.md
  与 results/J7/linear_anysize.md。两份均为 Claude 对 GPT 会话的逐字转录
  （转录说明在各自文件头部）；GPT 本身未交付任何脚本文件，J6 内嵌一段
  复算脚本，J7 没有附带脚本（其文件头如实说明）。

## 1. J6 的处理（=Q4 已处理的构造）

J6 的数学内容与本会话早晨以 chat 交付并按 TASKS10 Q4 全套处理的
双残差截断构造逐字一致（同 13 项恒等式、同电池计数
159/111,032/207,842/2,441、同定理陈述）。核对方式:

- 内嵌脚本提取后原样运行: 13 identities PASS + 计数逐位一致
  （results/J6_script_run.log, exit 0）。与 Q4 当日保存的
  results/Q4_gpt_check.py 为同一脚本（仅空白重排）。
- 指令要求的其余 J6 验证在 Q4 会话均已完成并 commit:
  自写 sympy 管线复核 13 恒等式 + 34 条三截断区间分支不等式
  （results/Q4_symbolic_ineq.py [VERIFIED-SYMBOLIC]）、K <= 12 有理数
  全格点（脚本自带电池 K∈[2,12] + 自写独立实现 K <= 13,
  results/Q4_indep_check.py 111 组 [VERIFIED-LP]）、small-set-only LP
  对账 18/18（results/Q4_smallset_lp.py）。
- 台账卡 T10c 已在 Q4 会话建立（先卡后文），thm:linear-exact 已入正文。
  本日只需把来源标注从 "Q4 外部并行审计" 具体化为
  "J6（results/J6/linear_exact.md）"，见台账注记。不重复建卡。

## 2. J7 的验证链（新内容: 任意大小查询的线性类）

J7 主张: alpha_lin(K,eta) <= min{1/eta, rho_K + 1/(K(e^{K-1}-K-1))}
（K >= 3，n -> infinity 的类最优值），更紧的 W_K(eta)；修正截断规则
m = min{z >= 1: Psi(z) <= 0}，Psi(t) = (K eta - t - 1)nu^t - K(eta-1)；
并指出 F3 原 m 公式非法的精确反例。

- 附带脚本: 无（GPT 未交付）。改为全部自写:
- F3 反例复算 [VERIFIED-LP 精确有理]: K=3, eta=667/500 时旧规则
  m = ceil(eta K) - 1 = 4 给 r_{t*} = -151089222203006/81950355825200625
  < 0（单调性失败），真 argmax = 3，修正规则给 3，argmax 处族可行
  （results/J7_fragment_checks.py Part 1）。J7 文中引用的分数逐位一致。
- 自写全格点电池 [VERIFIED-LP 精确有理]: 99 组（K=3..12，全部 j 域含
  j <= 1 与 j = 0，角点 eta），J7 公式直接转写（不经由 Q1 代码）:
  归一化、单调 + submodular、band 与双端点校准、任意大小关键性质
  H(x+1,0) = H(x,1) 对一切 x、x > T 全饱和、值 = W 闭式、gap 恒等式
  (17) 精确且为正、泄漏状态恰在 {y >= 2, x <= T} 内。ALL PASS
  （results/J7_grid_check.py + .log）。
- 对抗模拟 [VERIFIED-LP 精确有理]: K=3, eta in {3/2, 667/500, 2},
  n = 8..12，对抗 tie 的前向 greedy、反向 greedy（删除式，查询大小
  到 n，属任意大小类）、max(前向, 反向):
  - n >= K+T: 全部 <= W（且恰 = W）。
  - n < K+T: 反向 greedy 经泄漏区（此时全集大小 <= T+K）精确找回 O，
    比值恰为 1。这不与 J7 矛盾（其 (15) 泄漏集合刻画恰好允许此事，
    定理量词是 n -> infinity），但给出一条 must-not-claim:
    **J7 定理不能读成有限 n 的 "<= W"**；已写入 T10d 卡。
  指令原文要求 "n=8..12 确认比值 <= W_K"；按字面在 n < K+T 的 3 个
  格子不成立，成立的正确不变量如上。保守处理记录: 该 3 格测的是
  J7 未主张的有限 n 性质，J7 自身的主张（渐近 + 泄漏刻画）反而被
  这 3 格正面确认；已如实分开记录，不作为 J7 的验证失败。
- 一般 K 符号管线（自写，Opus 代理起草 + 主会话亲跑闸门）:
  results/J7_symbolic.py / .md / .json，覆盖 Psi/phi 结构与根定位
  (5)、(7)(8) 恒等式与符号、(11) r_T = g_T 与 0 <= r_T <= D、(12)/(14)
  全段、(13) 凹性论证、拼接不等式、单调/DR/band 归约、值与 gap (17)、
  (18) 的逐步链、示例行、Psi 规则对 argmax 的有限交叉核对。
  状态见该 md（本文件不预写其结论）。

## 3. 采纳决定（闸门裁定）

- J6: 已采纳（Q4 会话，T10c + thm:linear-exact）；本日补来源标注。
- J7: 待符号管线闸门（亲跑 exit 0 且无 FAILED 项）通过后采纳:
  T10d 新卡先行，thm:linear-anysize 入正文，app:hardness-anysize 的
  candidate-bound 段落按指令删除并替换为转录的构造与证明
  （[VERIFIED-SYMBOLIC 合法性] + [HAND-PROOF-UNREVIEWED 装配，来源 J7]），
  open-problem 草稿与 sandwich 图更新。任一失败则记录并停在正文之外。

## 4. 复现清单

- python3 results/J6_script_run 的来源: results/J6/linear_exact.md 内嵌
  脚本（提取后运行，日志 results/J6_script_run.log）
- python3 results/J7_fragment_checks.py   (exit 0)
- python3 results/J7_grid_check.py        (exit 0)
- python3 results/J7_symbolic.py          (状态见其输出)
- Q4 会话既有: Q4_gpt_check.py, Q4_indep_check.py, Q4_symbolic_ineq.py,
  Q4_smallset_lp.py（均 exit 0）

## 5. 补充送达（J7 spot-check）

- results/J7/J7_claude_spotcheck.py 后续经 uploads 送达（Claude chat 侧的
  spot-check；其头部自述"非 TASKS10 Q4 要求的独立 sympy 管线，不改任何
  标签"，按此处理，标签体系不变）。
- 原样运行 exit 0（results/J7_claude_spotcheck_run.log）：恒等式
  (7a)(7b)(8)(12) 全零；71 组精确网格（K=3..8）、20,924 条边、37,850 次
  DR、1,606 个全域剖面状态全过；(18) 用 float e（我们的
  J7_bound18_check.py 已有精确版，互为补充）。
- 数值对账：K=3, η=3/2 行（j=2, m=4, Q=9/16, D=117/928, W=523/928,
  gap=1/928, Ψ(3)=12）与我们的管线逐位一致；η=667/500 的 m=3 对旧规则 4
  一致；其打印的 r_T = g_T = 20664743922357/157947123981500 与我们
  builder 的值逐位一致（本会话现算核对）。
- 结论：三条独立实现（J7_grid_check、J7_symbolic、spot-check）在全部
  重叠点位一致；无新增采纳事项。

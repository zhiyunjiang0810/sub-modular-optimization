# results/J8/V11 — TASKS11 Q9（J8 ProbeLottery）产出索引

TASKS11 要求 Q9 的结果进 results/J8/。本目录是 results/V11 工作流中 J8 一项的四个角色产出的副本
（原件仍在 results/V11/{oracle,route2,compare,audit}/probelottery.*，矩阵行 "J8 ProbeLottery"）。

| 文件 | 角色 | 内容 |
|---|---|---|
| probelottery_oracle.py / .log / .json / .md | C + D（oracle 与反例搜索） | 独立重实现 ProbeLottery（只按 statement 文件的算法描述，不 import spot-check 脚本）；紧实例 K=2, η=3/2 双残差族 n ∈ {6,...,12,20} 恰 E[f] = 3/5 + 1/2048；2100 个随机合法实例 0 违反，全局最差即紧实例 6149/10240；算法 contract（≤ 9n 次查询、每次 \|S\| ≤ 5、输出 2-集、分布总质量 1）；C5 子进程复跑 results/J8/J8_claude_spotcheck.py exit 0；G1 不等式 (3)、(8)–(12) 的 LP 对偶证书 GAP（证明文件 results/J8/probe_lottery.md 未送达）。运行：`python3 results/J8/V11/probelottery_oracle.py`（exit 0；与原件相同的相对路径深度） |
| probelottery_route2_blind.md + J8_route2_*.py | B 路线二（盲审 Opus 子代理） | 只读 results/V11/inputs/{definition1,assumptions,notation,statement_probelottery}.md；独立推导 PARTIAL：情形 II-b（o_1、o_2 都进 pool 且四轮 extension 全被其他元素占据）只得 E ≥ (3/5 − 1.5625e−6)·OPT，比目标 3/5 + 2.5e−6 差 4.1e−6；未找到反例 |
| probelottery_compare.md + judge_probelottery_*.py | B 比对（判定人） | 路线一不存在（证明文件未送达），故 B-MISSING；紧实例两路线不同（J6 族 vs n=4 coverage）；II-b 缺口复核 |
| probelottery_audit.md | A + E（陈述逐字 + 量词审计） | 正文无 ProbeLottery 环境、台账无卡，A 无法比对；E 表：η=3/2 固定无论证、任意拆分只覆盖乘积、"≤ 9n" 与 "\|S\| ≤ 5" 由实现给出 |

最终标签：**[VERIFIED-ORACLE-ONLY]**（C/D 全过，路线一缺失）。不可原样写进正文；证明文件送达后补 (3)、(8)–(12) 的对偶证书并重定标签。

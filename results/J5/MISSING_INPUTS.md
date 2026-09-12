# results/J5/ 输入缺失记录（2026-09-12）

TASKS8.md 声明的四个输入文件在执行开始时均未到达：
- INDEPENDENT_THEORY_AUDIT_2026-09-12.md
- VERIFICATION_SUMMARY.md
- verify_audit.py
- submodular_K4_exact_duals.json

已检查位置：本仓库（含全部远端分支）、experiment 镜像仓库、会话 uploads 目录
（其中 files_1.zip 经解包核实为第一晚的引导包，非 J5）。先例：TASKS_J2.md 缺失日
（REPORT "J2 采纳日" 节）。

处理原则（保守，已记录进 REPORT）：
1. M0 闸门中 TASKS8 内联给出完整规格的项目照常独立复算（三个反例、本地脚本清单）。
2. verify_audit.py 的四个 PASS 无法确认：凡只以它为据的采纳一律不做。
3. J5 新手证的"移植/转录"不做（原文缺失）；能由本地 oracle 或本地重构闭合的，
   标注来源为"本地重构，规格转述自 TASKS8"，不标"来源 J5 原文"。
4. "J5 人工复核：已闭合"类注记不写入台账（无法核实其内容）。
若 J5 文件后续到达且与本晚处理有出入，按差异补做。

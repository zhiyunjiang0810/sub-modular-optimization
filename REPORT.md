# REPORT.md

## Summary（进行中，完成后更新为 ≤5 行终版）

- 会话开始：2026-08-29（环境：Claude Code 远程容器，4 核，scipy/sympy/sklearn 已装）
- 注：原计划新建仓库存放本目录，但 GitHub 集成无创建仓库权限（403），保守选择放入
  `experiment` 仓库 `claude/understand-requirements-oz3ayh` 分支的 `overnight/` 子目录。
  整个目录自包含，之后可原样迁移到新仓库。

---

## 任务日志（倒序追加在此行之下）

### T1 基线复现 [VERIFIED-LP] — PASS
- 做了什么：运行 `code/check_explicit_instance.py` 与 `code/worst_case_lp.py` 的 worst_case()
  （K=2 n=4、K=3 n=6，single-element 误差，η_u=η_o=√η，η ∈ {1,1.5,2,2.5,3,4}）。
- 结果：explicit instance 6 组参数 ALL PASS；12 个 LP 值与 RESEARCH_STATE.md R5 全部一致（<1e-7）。
- 复现：`python3 results/T1_baseline.py`，输出 `results/T1_baseline.txt`。
- 下一步：T2。

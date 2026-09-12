# J5H1 — J5 硬核审查包闸门（2026-09-12，J5 文件到齐当晚）

## 0. 输入到齐与 M 夜对账

此前第八晚（TASKS8/M0-M5）执行时 J5 的四个文件未送达（results/J5/MISSING_INPUTS.md）。本晚全部到齐：
- results/J5/：INDEPENDENT_THEORY_AUDIT_2026-09-12.md、VERIFICATION_SUMMARY.md、verify_audit.py、
  submodular_K4_exact_duals.json
- results/J5_hardcore/：J5_hardcore_audit.md、J5_ceiling_proof.md、J5_variant_certificates.md、
  J5_hardcore_oracles.{py,json,log}、J5_source_manifest.json

按 MISSING_INPUTS.md 的约定逐项对账（差异极小，M 夜按 TASKS8 转述执行的项目与原文一致）：
- M0 三个反例：与审计原文 §3/§10/§11 规格一致（§3 反例 J5 用 f=|S∩{1,2}|、f̃=min{1,f}，
  与 M0 的两元素 modular 构造等价，结论相同）。
- M1 的 lem:scaling、ρ_{n,K}、随机量词、valueacc 定义域：与审计 §0/§1/§2 的要求一致，无需返工。
- M3.1 当时 FAILED 的 n<2K 达到方向：本晚 J5H2 按 J5_ceiling_proof.md 原文转录（其证明走
  交换求和 + 并集误差耦合，正是绕开 f(S∩O) 卡点的路线；审计报告另有一份补集损失 h-supermodular
  证明，二者结论一致，附录采用 hardcore 包的交换版本，slack 恒等式 (7)(8)(9) 有符号 oracle）。
- M3.2 的本地对偶重建：与 J5 的 submodular_K4_exact_duals.json 双方独立、同值 23/41、同 16 轨道；
  verify_audit.py 本晚跑通，J5 侧证书成立。两套证书互为独立复核。

## 1. 闸门结果（全部通过）

- `cd results/J5_hardcore && python3 J5_hardcore_oracles.py --output-dir reproduced`：**exit 0，
  ALL PASS，30.46 秒**。覆盖：14 项符号恒等式（H-E 三种 slack 分解、H-B 展开/单调性、H-C 端点/分支）；
  H-B 正性证书（分子 84 项、分母 165 项全非负）；H-E 52 个独立全格点 LP + 24 个 modular 实例
  37,056 个 all-pairs 增量精确核验；H-C 56 个实例（121,344 边、262,144 方块）+ 16 类精确有理对偶
  （最小 23/41 > U_4 = 8080/14641）；PE₁ 128 子集完整有理反例（4/9，greedy 5/9）+ 补零扩展检查。
  **14 项恒等式与 52 个 LP 的通过条件满足。**
- `cd results/J5 && python3 verify_audit.py`：**exit 0，5 项 PASS**（16 轨道精确对偶、匹配 witness、
  23/41 − U_4 = 5463/600281 > 0、停止版反例 1/2 < 3/4、小 n minimax 证明的补集损失不等式实例核验）。

## 2. 本晚六项的执行依据（章节指针）

- J5H2（ceiling 统一）：J5_ceiling_proof.md 全文（陈述 §1、逐实例式 (1)、三步 §2、slack (7)(8)(9) §3、
  对手构造 §4、量词五条 §5、随机反例 n=3,K=2,η=3）。
- J5H3（PE₁）：J5_variant_certificates.md §4-§5（两表重建、七条轨迹、4/9 < 7/15 < 5/9、补零扩展）；
  审计 §七（收紧四句话、NWF 引用规范）。
- J5H4（W_m）：J5_variant_certificates.md §1（精确定义、band 端点、W_m 推导）与 §1.4（β_m）；
  审计 §六（不宜称 q 换 r）。
- J5H5（asymptotics 迁移）：审计 §四（展开、单调性证书、"装配未同步"裁定）。
- J5H6（H_F 修复）：审计 §七 第 5 点（非零 solver status 一律当 inf 会把数值失败当不可行剪枝；
  只对确认 infeasible 剪枝，其余 UNKNOWN；无证据表明已报告表格触发过该问题，重跑以确认）。

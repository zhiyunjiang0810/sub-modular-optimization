# H-J3 整合记录：把 J3 的结构化证明写进论文

日期 2026-09-07。任务 TASKS6.md 的 H-J3。输入是 `results/J3_proof_structure.md`（外部 J3 笔记）与
`results/H_J3_gate_check.py`（我方独立实现的闸门脚本）。台账依据 THEOREM_LEDGER.md 的 T5、T6、T6b 三张卡，
本次未改动台账。允许编辑的文件：`paper/sections/results.tex`、`paper/sections/appendix_proofs.tex`，
以及新建本文件。未执行任何 git 命令。

---

## 1. 闸门复跑结果

`python3 results/H_J3_gate_check.py`，exit 0，全部 PASS：

| 项 | 内容 | 状态 |
|---|---|---|
| 1 | sharp form `d − g/η ≥ (1−1/η)(g−h)` 与 coherence (ii) `(1−1/η)h ≥ g−d` 代数等价 | [VERIFIED-SYMBOLIC] |
| 2 | 相邻分支差 `V_i − V_{i+1} = q^i (K−i−η)/(K η k_1)` | [VERIFIED-SYMBOLIC] |
| 3 | 递推 `γ r' = r − K d`、`r' = r − d` ⇒ `d = r/k_1`、`r' = q r` | [VERIFIED-SYMBOLIC] |
| 4 | K=3, η=2 的两条最优 chosen-gain 序列 `(1/5, 2/15, 2/15)`、`(1/5, 4/25, 8/75)`，均和 `7/15 = V_1(2) = V_2(2)` | [VERIFIED-SYMBOLIC 精确有理数] |
| 5 | 40 个最优面（K=2..6，每个 j，η = K−j+1/4 与 K−j+3/4）上固定目标值为精确有理 `V_j` 后，对 reduced LP 的每个坐标分别求最小、最大，共 2,480 次 LP；所有坐标区间塌缩到两阶段序列 | [VERIFIED-LP]，最大坐标偏差 **3.94e-15** |

脚本没有向 LP 加 `g_{t,i} = g_{t,i'}` 的对称约束，也没有只读某一个最优解，所以第 5 项支持的是**有限最优面上的唯一性**。

---

## 2. 加在哪里、加了什么

### 2.1 `paper/sections/results.tex`

**(a) block 5，`lem:coherence` 之后（不新立定理，照台账 T5）**

在 lemma 与其状态注释之后加一段：一个 display

```
d − g/η ≥ (1 − 1/η)(g − h) ≥ 0,   d = d_e(S), g = d_{e'}(S), h = d_{e'}(S ∪ {e})
```

加两句解释（左端是选中增益超出误差带下限的余量，中间项是这一步对竞争者后续增益的削弱，两种损害不能同时取极端；
η > 1 且 d = g/η 时必有 h = g）。状态注释写明：第一个不等号是 (ii) 的等价改写
[VERIFIED-SYMBOLIC, `results/H_J3_gate_check.py` item 1]，第二个用 f 的 submodularity（g ≥ h）与 η ≥ 1；
并注明它和 lemma 一样只对全局 η 成立，不可用 η^sel / η^tr（台账 T5 的禁止声称）。

**(b) block 6，`thm:exact` 与其状态注释之后：证明主线段落（H-J3 第 5 项，J3 §5 顺序）**

`\paragraph{How the two directions fit together.}` 共 5 句，顺序为：sharp form 限制"当前损失 + 未来损失"同时取极端 →
两阶段候选轨迹（几何段 `q^t/k_1` + 冻结段，第 j 步切换）→ 一般对偶下界（四族约束的固定非负组合恒等于
`Σ_t d_t − V_j`）与达到实例 → `prop:rigidity` 把同一组合反过来读 → 断点是承重乘子消失的地方。
引用了 `lem:coherence`、`prop:rigidity`、`app:exact`、`rem:rigidity-breakpoints`。

**(c) 新命题 `prop:rigidity`（`\begin{proposition}[Structure of worst-case runs]`）**

位置：`thm:exact` 状态注释与证明主线段落之后，`rem:exact-gap` 之前。陈述逐字对齐台账 T6b：
K ≥ 2；η ∈ (K−j, K−j+1) 且 1 ≤ j ≤ K−1，或 j = 0 且 η > K；f(O*) = 1；若 adversarial-tie run 达到
ρ_K(η) = V_j(η)，则 `d_t = q^t/k_1 (t<j)`、`q^j/(Kη) (t≥j)`，`g_{t,i} = q^{min(t,j)}/K (0 ≤ t ≤ K)`。
命题前加了一句把 `d_t`、`g_{t,i}` 定义清楚（正文此前没有 reduced-LP 记号）。

命题后紧跟台账的三句范围句：只约束选中增益与最优元素沿轨迹的边际；不确定 (f, f̃)，也不约束未选候选的边际；
由 g 全正与置零约定，此类 run 与所固定的 O* 不交。

状态注释按台账 T6b 分三段：递推恒等式 [VERIFIED-SYMBOLIC]、40 面 / 2,480 LP 的唯一性 [VERIFIED-LP]
（均 `results/H_J3_gate_check.py`）、从互补松弛到任意规模实际轨迹的装配 [HAND-PROOF-UNREVIEWED] 且注明
**不得升级**。并列出禁止声称：唯一性延伸到整数断点、约束全体候选的最大真实边际、"phase transition" 措辞。

**(d) 两条 remark**

- `rem:rigidity-breakpoints`（Breakpoints as an active-constraint switch）：
  `λ_P(j) = (η−(K−j))/(K(η−1))` 在段左端点消失、`λ_S(j) = (K−j+1−η)/k_1` 在段右端点消失，
  所以整数 η 处被强制的约束更少，命题的论证不适用；K=3, η=2 的两条序列都和 `7/15`，唯一性不跨过断点。
  全文用 **active-constraint switch**，没有出现"相变 / phase transition"。
- `rem:rigidity-ties`（Ties, and what near-equality forces）：
  cons(t,i) 与 pred(t,i) 的 slack 各自分解成三个非负项，中间项都是 `(d̃_{e_t}(S^t) − d̃_{o_i}(S^t))/η_o`；
  命题把两个 slack 都置零（前者 t ≤ K−2，后者 t = K−1），故每步 P = Q，即每步与最优元素的预测增益打平，
  这解释了为什么 adversarial tie 是 `thm:exact` 的前提而不是方便设定。第二半：输出为 `V_j + ε` 时，
  对每个正乘子有 `0 ≤ slack_r ≤ ε/λ_r`；明确写成"逐 run 可检查的推论"，并写明不升级为统一稳定性定理
  （需要处理递推误差累计、K 增长、以及 η 逼近断点时乘子退化）。

### 2.2 `paper/sections/appendix_proofs.tex`

**(a) `app:exact` 开头加 roadmap 段（3 句）**，顺序与正文一致（sharp form → 两阶段形状 → 对偶下界与达到实例 →
`app:rigidity` 反读 → 断点）；明确说系数配平、实例增益表、四族约束的 validity 放在后面读。
**没有重排任何已有证明**，只插入这一段指路文字。

**(b) 新子节 `\subsection{Structure of the attaining runs (Proposition~\ref{prop:rigidity})}`，label `app:rigidity`**，
紧接在 `app:exact` 之后、`app:ceiling` 之前。按 J3 §2.1 用论文记号逐步写出：

1. **Step 1 正乘子支撑**：段内部有 M > 0、q ∈ (0,1)、η > 1，从 `\eqref{eq:duals-jpos}`、`\eqref{eq:duals-jzero}`
   逐条读出 `λ_S(t) > 0 ⇔ 0 ≤ t ≤ j`、`λ_C(t) > 0 ⇔ 0 ≤ t ≤ K−2`、`λ_P(t) > 0 ⇔ j ≤ t ≤ K−1`、mono 乘子全零。
   （J3 只断言这个支撑，没有给符号核对；这里补了。）
2. **Step 2 零加权 slack 和 ⇒ 每个被支撑的约束取等**，并点明零乘子的约束（sum(t), t>j；cons(K−1,i)；全部 mono）
   仍然有效但未被强制，Step 7 会以不等式的形式用到其中两条。
3. **Step 3 早期递推（t < j）**：相邻两个 coverage 等式 + 对 i 求和的 consistency 等式给出 `γ r_{t+1} = r_t − K d_t`，
   与 `r_{t+1} = r_t − d_t` 联立得 `d_t = r_t/k_1`、`r_{t+1} = q r_t`，由 r_0 = 1 得 `r_t = q^t`、`d_t = q^t/k_1`。
4. **Step 4 t = j 的切换**：prediction 对每个 i 取等给 `g_{j,i} = η d_j`，coverage 取等给 `Σ_i g_{j,i} = q^j`，
   故 `d_j = q^j/(Kη)`、`g_{j,i} = q^j/K`。明写"对称性是结论而非假设"（LP 对每个 i 分开处理）。
5. **Step 5 冻结段（j ≤ t ≤ K−2）**：prediction 取等 + consistency 取等 ⇒ `d_{t+1} = d_t`、`g_{t+1,i} = g_{t,i}`。
6. **Step 6 向后回推（t < j）**：`g_{t,i} = d_t + γ g_{t+1,i}`，用 `K + (K−1)(η−1) = k_1` 得 `g_{t,i} = q^t/K`，逐个 i。
7. **Step 7 末步锁定**：`λ_C(K−1) = 0`，故 cons(K−1,i) 未被强制，但仍成立；把 cons(K−1,i) 与 mono(K−1,i) 写成
   sharp form 的两个不等式，配上 prediction 取等 `d = g/η` 与 η > 1，得到 `g_{K,i} = g_{K−1,i} = q^j/K`。
   附一致性检查：`Σ_t d_t = V_j`，且 `app:exact` 的增益表说明达到实例正好走这条轨迹。
8. **范围段**：由 `g_{K,i} > 0` 与置零约定推出与 O* 不交；强调 `app:validity` 的归约仍须允许选中最优元素；
   不确定 (f, f̃)；不约束未选候选，特别是 `def:etasel` 用到的"状态上最大真实边际"不在结论内；整数 η 处论证停在 Step 1。
9. **两个后果**：写出 pred(t,i) slack 的三项非负分解（与 `lem:app-cons` 的分解同型），由此得 P = Q；以及
   `slack_r ≤ ε/λ_r`，并说明未做关于 η、K 的统一陈述。
10. **收尾的诚实机器检查行**：点名 `results/H_J3_gate_check.py`（递推、Step 7 的改写、两条 K=3 序列、
    40 个最优面 2,480 次 LP、最大偏差约 4e-15、无对称约束），并明写"没有脚本检查把 Step 1–7 装配成任意规模
    run 的陈述"。按该文件既有约定，正文不出现状态标签，标签写在注释里。

---

## 3. 保留为 [HAND-PROOF-UNREVIEWED] 的部分（不得升级）

- 从互补松弛到**任意 K** 的实际轨迹的整个归纳装配（`app:rigidity` Step 1–7 的串联）。有限证据只到 K = 2..6、
  每段两个 η；一般 K 靠手写归纳。
- `rem:rigidity-ties` 中"每个被支撑的 slack 为零 ⇒ 每步与最优元素 tie（P = Q）"这一步的装配；
  两个三项分解本身有符号 oracle（`H3_j2_recheck.py`、`J2_core_oracles.py`，K4 已采纳），装配没有。
- `app:exact` 原有的对偶证书与达到实例的状态未改动（[VERIFIED-SYMBOLIC modulo 有限分支枚举] + 装配未复核）。

未做且明确不做的升级：不把 `slack_r ≤ ε/λ_r` 升级为 uniform stability theorem；不把唯一性延伸到整数断点；
不声称约束了全体候选的最大真实边际。

---

## 4. 偏差说明（重要）

**J3 笔记自带的 oracle 脚本 `results/J3_structure_oracles.py` 从未交付。** J3 笔记 §2.3 与结尾的复现说明
（"`python3 results/J3_structure_oracles.py`，相关 JSON 和日志随包提供"）在本仓库没有对应文件。因此：

- 本次所有 40 面 / 2,480 次 LP、递推恒等式、两条 K=3 序列的引用，一律指向**我方独立实现**
  `results/H_J3_gate_check.py`；论文注释里凡是本该引用 J3 脚本的位置，都写明了 J3 脚本未交付这一事实
  （`results.tex` 两处状态注释、`appendix_proofs.tex` 的 `app:rigidity` 头部注释）。
- 我方脚本是照 J3 §2.3 描述的实验设计重写的（同样的 K 范围、同样的每段两个 η、同样固定目标值后逐坐标求极值），
  数值结论一致（最大偏差 3.94e-15，J3 报的是约 4.5e-15），但**这不是对 J3 数字的复现验证**，只是同一设计的独立复算。

## 5. J3 笔记不足、由本次补齐或如实标注之处

1. **正乘子支撑只有断言，没有符号核对。** J3 §2.1 直接给出三族支撑区间。本次在 `app:rigidity` Step 1 里
   从 `\eqref{eq:duals-jpos}`、`\eqref{eq:duals-jzero}` 逐条核对了符号，并指出这里正是段内部（开区间）被消耗的地方。
2. **末步论证过简。** J3 §2.1 末句只说"末步 prediction 取等，再结合 mono 与第 1 节的不等式"。本次写全：
   cons(K−1,i) 改写成 sharp form、mono(K−1,i) 给 `g − h ≥ 0`、prediction 取等给 `d = g/η`，再用 η > 1 得 h = g；
   并说明这条 consistency 约束虽然乘子为零但仍然有效。
3. **j = 0 的退化情形 J3 未单独交代。** 本次在 Step 3（区间为空）与 Step 4（`r_0 = 1 = q^0`）里显式处理。
4. **J3 没有说明"达到 run 是否存在"。** 本次在 Step 7 末尾加了一致性检查：`app:exact` 的 `\eqref{eq:vj-family}`
   实例的增益表正好等于该轨迹，所以被强制的轨迹确实可实现。这是我们补的，不是 J3 的内容。
5. **J3 §4 的近等号推论没有给常数。** 如实保留为逐 run 可检查的推论，并在正文写明升级需要什么
   （递推误差累计、K 增长、断点附近乘子退化），没有虚构统一界。
6. **`ρ_K = V_j` 在开区间上唯一取到最小值这件事** J3 没有证；它已经在 `app:exact` 的相邻差符号讨论里，
   本次直接引用，未重复。
7. **一般 K 的唯一性仍无 oracle。** J3 §2.3 自己也说"一般规模结论仍由 §2.1 的手工装配承担"，本次照此标注。

另外记录一处越界观察（未改，不在本任务编辑授权内）：`results.tex` 的 `rem:etasel-measurable` 里有一个
"reports honestly"，与 CLAUDE.md 第 8 条对报告用词的要求撞车；属既有正文，本次不动。

---

## 6. 编译

在 `paper/` 下按要求执行（从不编译默认 jobname）：

```
pdflatex -interaction=nonstopmode -jobname=main_hj3 main.tex
bibtex main_hj3
pdflatex -interaction=nonstopmode -jobname=main_hj3 main.tex
pdflatex -interaction=nonstopmode -jobname=main_hj3 main.tex
```

日志：`results/H_J3_compile.log`。最后一遍 pdflatex：**0 个 `!` 错误、0 个 undefined reference、
0 个 undefined citation、0 个 multiply-defined label**，输出 `main_hj3.pdf`，34 页。
Overfull hbox 仅 1 处（`main.tex` 第 8–44 行的 abstract 占位块），与改动前的 `main.log` 完全相同，本次没有新增。

新 label 及其位置（来自 `main_hj3.aux`）：

| label | 类型 | 编号 / 位置 |
|---|---|---|
| `prop:rigidity` | Proposition | 10（正文第 4 页） |
| `rem:rigidity-breakpoints` | Remark | 11（正文第 5 页） |
| `rem:rigidity-ties` | Remark | 12（正文第 5 页） |
| `app:rigidity` | 附录子节 | B.7（第 23 页） |

数字审计：`python3 results/G3_number_audit.py` → `total 290 literals, 0 violations`
（新增的 `1/5`、`2/15`、`7/15` 等都在 math mode，属该脚本的 theory-const 类）。

---

## 7. 与台账的对应

| 台账卡 | 落到 .tex 的位置 |
|---|---|
| T5（sharp form 行） | `results.tex` block 5，`lem:coherence` 之后的 display 与两句；不另立定理 |
| T6（新增禁止声称） | `prop:rigidity` 状态注释与 `rem:rigidity-breakpoints` 正文 |
| T6b（刚性命题 + 附属 remarks + 范围 + 状态分裂） | `prop:rigidity`、其后的范围句、`rem:rigidity-breakpoints`、`rem:rigidity-ties`、附录 `app:rigidity` |

台账文件本次未修改（按任务要求）。

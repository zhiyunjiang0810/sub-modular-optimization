# G1_pagebudget.md — 骨架页数实测与 9 页预算（第五晚 G1）

测量方法：main.aux 中各 section label 的起始页码（pdflatex+bibtex+pdflatex×2，
0 错误 0 未定义引用，日志 results/G1_compile.log）。当前 main.pdf 共 6 页
（正文 1-3，references 3-4，附录 4-6）。intro/related/experiments/conclusion
为占位 stub，其实测长度为 0，下表"预计"列为 G3/人类填入后的估计。

## 逐节实测 vs 预算

| 节 | 起始页 | 实测长度（页） | 预算（页） | 预计填满后 | 备注 |
|---|---|---|---|---|---|
| 1 Introduction | 1 | 0（占位） | 1.5 | 1.5 | 人类明早写；注释里有四个承重位清单与 A/B hook 草稿 |
| 2 Model & preliminaries | 1 | ~0.55 | 1.0 | ~0.7 | 从 results.tex 抽出；notation 表移到附录 A（理由：模型预算 1 页放不下整表） |
| 3 Related work | 1 | 0（占位） | 0.75 | ~0.75 | G3 写：4 组 × 3 句 + 2 条邻线 |
| 4 Theoretical results | 1 | ~2.2 | 3.5 | ~2.6-3.0 | 9 个块、2 条 remark；暂有余量 |
| 5 Experiments | 3 | 0（占位） | 1.75 | ~1.75-2.2 | G3 写：主图+表+三族叙事，最易超 |
| 6 Conclusion | 3 | 0（占位） | 0.25 | 0.25 | 占位注释里有候选内容 |
| Statements（不计页） | 3 | ~0.5 | 0 | ~0.5 | 模板规定不计入页数（G6 复核位置） |
| 附录 A notation | 4 | ~0.3 | - | ~0.3 | |
| 附录 B proofs | 4 | ~2.2 | - | ~7-9 | G2 重写后会大幅增长（U_K 2-3 页 + ρ_K 上下界各 2 页） |
| 附录 C 实验补充 | 6 | 0（占位） | - | ~1-2 | G3 填 |

预算合计 1.5+1+0.75+3.5+1.75+0.25 = 8.75 页，留 0.25 页缓冲。

## 当前/预计超支最大的三处与可压缩点

1. **Section 5 Experiments（预算 1.75，预计最高 2.2）**：主图（约 0.35 页）+
   EXP 表（约 0.3 页）+ 三族叙事 + E3/E2 各一段。压缩点：表只留合并行（全表下
   沉附录 C）；三张辅图全部进附录 C；E3 边界外发现与 E2 p-η 段各压到 3 句。
2. **Section 4 Theory（预算 3.5，当前 2.2 但 G3 会加过渡句）**：压缩点：
   thm:exact 里 K=2,3,4 闭式清单下沉附录；rem:hardness-pins 并入 conclusion；
   subsection 4.1（necessity）并入 4.2 开头一句话；cor:limit 并入 4.5 末尾。
3. **Section 1 Intro（预算 1.5，四个承重位 + hook 都要放）**：压缩点：贡献
   用行文不用 bullet 列表；hook 的 A/B 例子只保留两句，细节移到 Section 2。

## 结构决定（G1，保守方案与理由）

- notation 表移附录 A：模型节预算 1 页，表占 0.3+ 页放不下；正文以一句话指向。
- figures/captions.tex 不再编入 main（caption 草稿供 G3 采用后废弃）。
- \iclrfinalcopy 暂留（草稿显示页眉）；投稿前删除即匿名（G6 checklist 项）。
- results.tex 保留文件名（theory 节），模型块拆到 sections/model.tex；
  G3 的数字审计范围相应为 experiments.tex + results.tex + model.tex。

## 附录页数（G2 完成后由 G2 追加）

测量方法与 G1 一致：`paper/main_g2.aux` 中各 `app:` label 的起始页码（独立
jobname `main_g2`，pdflatex → bibtex → pdflatex ×3，**0 错误、0 未定义引用**，
日志 `results/G2_compile.log`）。粒度是**整页**（label 只记录起始页），所以
"长度"列 = 下一小节起始页 − 本小节起始页，误差 ±1 页；`0` 表示与下一小节同页。
测量时刻的 main_g2.pdf 共 25 页（正文 1-6，statements/references 7-8，
附录 A notation 9，附录 B proofs 9-23，附录 C experiments 23-25）。
注意：正文部分此时已被并行任务填入 experiments 图表，intro/related 仍是占位，
所以附录起始页会随人类写完正文而后移；下表的**长度**列不受影响。

### 附录 B（proofs）逐小节页数

| 小节 | label | 起始页 | 长度（页） | 内容与来源 |
|---|---|---|---|---|
| B 开头 | `app:proofs` | 9 | 0（与 B.1 同页） | 三条全局约定 + counting-function 引理 |
| B.1 | `app:necessity` | 9 | 1 | γ = K²/(n(n−K)) 构造，deterministic + randomized 两支 |
| B.2 | `app:guarantee` | 10 | 1 | L_K 的四步（覆盖、非正步、展开、三把尺子），D2 措辞 |
| B.3 | `app:tightness` | 11 | 2 | U_K 族八步：闭式、四条 ratio、单调 submodular、误差、OPT、greedy 归纳、η^sel=η^tr=â、η 重参数化 |
| B.4 | `app:coherence` | 13 | 1 | 两序展开 + 两条误差带链 |
| B.5 | `app:exact` | 14 | 4 | 下界 p.14-16（对偶乘子、非负性、三族系数恒等式、argmin_j），上界 p.16-18（三块实例、逐步增益表、greedy 归纳、tie 的必要性） |
| B.6 | `app:ceiling` | 18 | 1 | modular 构造 + 随机化平均 + exhaustive search 反向界 |
| B.7 | `app:asymptotics` | 19 | 0（与 B.8 同页） | 两个极限；单调性缺口见下 |
| B.8 | `app:hardness` | 19 | 2 | concentration / valuation / δ 的四条边 / Φ 可逆与装配 / 平均化 / K→∞ |
| B.9 | `app:validity` | 21 | 2 | 四族有效不等式逐条（含 e_t ∈ O* 的 case (c)）+ 三条 remark |
| B.10 | `app:instances` | 23 | 0（与附录 C 同页） | 实验用实例指回 B.3 / B.5 |
| **附录 B 合计** | | **9** | **约 14** | G1 预计 7-9 页，实际偏高 5 页 |

### 与 G1 预算的偏差、原因与可压缩点

- **偏差**：G1 行"附录 B proofs 预计 ~7-9 页"，实测约 14 页。原因是 G2 的任务
  要求把"verified symbolically"换成逐行论证：TASKS5 G2 给 app:tightness 定的
  就是 2-3 页、ρ_K 上下界各约 2 页、app:validity 约 2 页，四项合计已 8.5 页，
  其余七个小节 5.5 页。**附录不计入正文 9 页预算**（G1 的预算表只统计正文
  1-6 节），所以这不占用正文余量。
- 若人类仍想压缩附录，按"删掉后读者最不受损"排序的三个可压缩点：
  1. **B.5 下界的系数恒等式 (a)（约 0.8 页）**：四个分支的展开可压成两个分支
     加一句"其余两支同法"，代价是 referee 需自己补 t = j 那支的配平。
  2. **B.9 的三条 remark（约 0.4 页）**：`rem:app-rulers` 必须留（它解释为什么
     L_K 用 η^sel 而精确值用全局 η），`rem:app-census` 可删。
  3. **B.3 Step 8 与 B.4（各约 0.3 页）**：Step 8 的 U_K 重参数化可并入
     `rem:exact-gap` 的一句话；coherence 的两序展开可缩到三行。
- 反向提示：**不要**压缩 B.5 上界的逐步增益表与 B.9 的 case (c)。前者是唯一
  能让读者自行复算 V_j 的地方，后者正是 R6 当初被标记的缺口所在。

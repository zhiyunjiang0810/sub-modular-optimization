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

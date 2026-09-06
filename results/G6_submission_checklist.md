# G6_submission_checklist.md — 投稿卫生检查（第五晚 G6）

编译状态：pdflatex+bibtex+pdflatex×2 全部 0 错误 0 未定义引用（日志
results/G6_compile.log）。

## 1. 双盲检查

- [x] 正文与附录 grep 扫描（zhiyun/jiang/gmail/github.com/gitlab/acknowledg/
  thank/仓库名）：除模板自带的 dlbook_notation 注释链接外零命中。
- [x] \author{Anonymous}。
- [x] 无致谢段。
- [x] repo 链接位置已写占位："anonymous repository accompanying this
  submission (link withheld in this draft; an anonymized link is to be
  added at submission time)"（sections/statements.tex）。
- [ ] **TODO（人类，投稿前）**：删除 main.tex 里的 \iclrfinalcopy（当前留着
  是为了草稿显示页眉；删掉即进入匿名 submission 模式）。
- [ ] **TODO（人类，投稿前）**：把仓库通过 Anonymous GitHub（或 OpenReview
  supplementary zip）匿名化，替换 statements.tex 里的占位句。
  注意仓库内 REPORT/RESEARCH_STATE 等中文工作文件不应进 supplementary；
  建议只打包 code/、src/、results/ 的脚本与 CSV、data/INVENTORY.md。
- [ ] **硬规则（H1 追加，2026-09-06）：任何匿名化产物必须排除 legacy/ 目录**。
  legacy/tpami_submission/ 是 TPAMI 版原稿全文，legacy/Submodular_ICLR.zip 是
  其原始包，内含作者姓名、作者照片（images/*.jpg/png）、IEEE 传记与可识别
  仓库信息；任何一件进入 Anonymous GitHub 或 supplementary zip 即当场破盲。
  同理 REPORT.md、RESEARCH_STATE.md、GLOSSARY.md、TASKS*.md 也不入包。

## 2. Statements 位置与计页（模板要求核对）

- 模板原文（iclr2027_conference.tex 397-435 行）：AI use statement
  **required**、不计页；Ethics statement recommended、不计页；
  Reproducibility statement recommended、不计页；位置均为 main text 末尾、
  references 之前。
- [x] statements.tex 已改为 \subsection*（与模板一致），置于 conclusion 之后、
  \bibliography 之前（main.tex 顺序即是）。
- [x] AI use statement 按模板句式重写（used for / reviewed / take
  responsibility 三要素齐全），内容如实（口径与 REPORT.md 一致；re-ran
  claim 留了注释提醒人类按实际情况校准）。
- [x] Ethics statement：recommended-only，本文无人类被试/敏感数据（公开
  数据集），保守决定为暂不写；如需可加三句版（数据均公开、无隐私、无
  可预见滥用面）。
- [x] 页数规则：初投正文严格 9 页（模板 131 行），citations 不限页。当前
  conclusion 结束于第 6 页（intro/related 为占位），人类写满 intro 1.5 页
  后预计 8.5-9.0 页，见 results/G1_pagebudget.md。

## 3. 图字号（缩放后 ≥ 7pt）

E5 原图在 \textwidth 缩放后最小有效字号约 5.4-5.8pt，不达标；已用
results/G6_paper_figs.py 重出 paper 版四图并替换 paper/figures/ 下同名
PDF（E5 原件 figures/ 下不动）。逐图核算（名义最小字号 × 版面缩放比）：

| 图 | 画布宽 | 名义最小字号 | 嵌入宽度 | 有效字号 | 判定 |
|---|---|---|---|---|---|
| money_plot（图 1） | 7.0in | 9pt | \textwidth | 7.1pt | 达标 |
| aux_eta_sel_by_K（附录） | 7.2in | 11pt | \textwidth | 8.4pt | 达标 |
| aux_p_vs_eta（附录） | 4.2in | 10pt | 0.66\textwidth | 8.6pt | 达标 |
| aux_d_dtilde_scatter（附录） | 4.2in | 10pt | 0.62\textwidth | 8.1pt | 达标 |

主图布局目检通过（曲线标签移入 caption，与 "pts beyond" 注记的重叠已消）。

## 4. 其他卫生项

- [x] 数字审计：experiments.tex 非宏数字字面量 0 个（results/G3_number_audit.md）。
- [x] 引用：23 条全部过 F6 四步核验；bibtex 0 warning。
- [ ] 遗留 overfull hbox 1 处（notation_table.tex，93pt）：**TODO** 人类定稿
  时把该表列宽调窄或换行（不影响编译，双栏审稿观感问题）。
- [ ] \iclrfinalcopy 删除后需重查页眉与行号显示（submission 模式带行号）。
- [ ] G5 审稿报告（results/G5_review.md）里的 严重 级条目在明早优先处理。

# F6 引用核验审计（四步核验）

任务：TASKS4.md F6。规则见 GLOSSARY.md 第 21 行（引用四步核验）。
核验日期：2026-09-01。核验人：F6 子任务（自动核验 + 人工复核待做）。
核验工具：DBLP 官方 JSON API（`https://dblp.org/search/publ/api`）、出版方页面
（PMLR、NeurIPS proceedings、ACL Anthology、Project Euclid、Optimization Online、SNAP）、
arXiv 摘要页、Semantic Scholar Graph API。对 Goundan–Schulz、Horel–Singer、Das–Kempe、
Kempe–Kleinberg–Tardos、Balcan–Harvey 五篇另外下载了公开 PDF 并抽取正文文本以定位定理号
（Goundan–Schulz 的 PDF 用空口令 RC4 标准安全处理器解密后抽取）。

四步：
1. **存在性**：DBLP / 出版方 / arXiv / 数据集官方页的 URL。
2. **支持陈述定位**：本文引它支持什么陈述 + 原文定理号/定义号/页码。无法从公开来源定位到
   定理号的写"仅条目级，定理号待人工"。
3. **字段核对**：author 全名、venue 正式名、year、volume/number/pages 逐项对出版方或 DBLP。
4. **版本选择理由**：会议 vs 期刊 vs 预印本，选支持陈述的版本。

**结论标记**：
- `PASS` = 四步全过，且第 (2) 步定位到**原文定理号/定义号**，或（正文逐字句）到具体小节，
  或（数据集）到官方数据页的指定引用栏。
- `PASS*` = 存在性、字段、版本三步全过，第 (2) 步只到摘要/标题级（有逐字陈述但无定理号），
  定理号待人工补。仍可进 .bib。
- `[CITATION-NEEDS-VERIFICATION]` = 第 (1) 或 (3) 步失败（含网络不可达），**不进 .bib**，只在本文件记录。

---

## 主表（每篇一行）

| # | bibkey | (1) 存在性 URL | (2) 支持的陈述 + 定位 | (3) 字段核对 | (4) 版本理由 | 结论 |
|---|---|---|---|---|---|---|
| 1 | `nemhauser1978analysis` | https://doi.org/10.1007/BF01588971 （DBLP `journals/mp/NemhauserWF78`） | 经典 greedy 在 cardinality 约束下的 $1-(1-1/K)^K \ge 1-1/e$。**仅条目级**：Springer 403、S2 摘要被出版方屏蔽，定理号未从公开源确认。旁证：Kempe et al. 2003 的 THEOREM 2.1 明确把该陈述归于其参考文献 [23] = 本文 | George L. Nemhauser / Laurence A. Wolsey / Marshall L. Fisher；Mathematical Programming；1978；14(1):265–294 — 与 DBLP、Semantic Scholar 一致 | 只有期刊版；Part II（Math. Prog. Study 8）是另一篇，不用 | PASS* |
| 2 | `nemhauser1978best` | https://doi.org/10.1287/moor.3.3.177 （DBLP `journals/mor/NemhauserW78`） | "在 value-oracle 模型下，多项式次查询的算法不能优于 $1-1/e$"（本文 related work 的 best-algorithms 上界句）。**仅条目级**，定理号待人工（INFORMS 403，S2 摘要被屏蔽） | George L. Nemhauser / Laurence A. Wolsey；Mathematics of Operations Research；1978；3(3):177–188 — DBLP 与 S2 一致 | 只有期刊版 | PASS* |
| 3 | `feige1998threshold` | https://doi.org/10.1145/285055.285059 （DBLP `journals/jacm/Feige98`） | set cover 的 $\ln n$ 近似阈值：对任意 $\varepsilon>0$，除非 NP $\subseteq$ DTIME$(n^{O(\log\log n)})$，否则不能近似到 $(1-\varepsilon)\ln n$。定位：论文主定理（标题即该陈述）；公开 PDF 见 courses.cs.duke.edu/spring07/cps296.2/papers/p634-feige.pdf | Uriel Feige；Journal of the ACM；1998；45(4):634–652 | JACM 1998 是终版；STOC 1996 是 preliminary version（314–318），不用 | PASS |
| 4 | `goundan2007revisiting` | https://optimization-online.org/2007/08/1740/ （PDF: .../wp-content/uploads/2007/08/1740.pdf） | $\eta^{\mathrm{sel}}$ 的出处 + 本文 Theorem 6 的经典对应物。定位：**Section 3, Theorem 1（p. 7）**，见下方"重要发现 A"的逐字记录 | Pranava R. Goundan / Andreas S. Schulz；MIT working paper；2007；无卷期页码（工作论文） | **无期刊/会议版**：DBLP 无收录，检索只有 Optimization Online 的 e-print。已用官方页 + 全文 PDF 双重确认 | PASS |
| 5 | `horel2016maximization` | https://proceedings.neurips.cc/paper/2016/hash/81c8727c62e800be708dbf37c4695dff-Abstract.html （DBLP `conf/nips/HorelS16`） | $\varepsilon$-approximately submodular 下的 poly-query 下界。定位：**Theorem 3**（Section 2）；Intro 概述句："given access to an $(1-n^{-1/2+\delta})$-approximately submodular function, no algorithm can obtain an approximation ratio better than $O(1/n^{\delta})$ using polynomially many queries (Theorem 3)" | Thibaut Horel / Yaron Singer；NIPS 2016；3045–3053 | 会议版是正式出版版；arXiv:2411.10949 是 2024 年补挂的同名 e-print，不用 | PASS |
| 6 | `hassidim2017submodular` | https://proceedings.mlr.press/v65/hassidim17a.html （DBLP `conf/colt/HassidimS17`） | noisy oracle 下的**正面**结果（对足够大的 $k$ 可任意逼近 $1-1/e$）。定位：摘要级（PMLR 摘要明确此陈述）；定理号待人工 | Avinatan Hassidim / Yaron Singer；Proceedings of the 2017 Conference on Learning Theory；PMLR vol. 65；1069–1122；editors Kale & Shamir — 直接取自 PMLR 页的 BibTeX | COLT 2017（PMLR v65）是正式版；arXiv:1601.03095 (2016) 是预印本 | PASS* |
| 7 | `das2011submodular` | https://icml.cc/2011/papers/542_icmlpaper.pdf （DBLP `conf/icml/DasK11`） | submodularity ratio $\gamma$ 的定义与弱 submodular 下的 greedy 保证。定位：**Definition 2.3（Submodularity Ratio），Section 2.1**；**Theorem 3.2**：$R^2_{Z,S^{FR}} \ge (1-e^{-\gamma_{S^{FR},k}})\cdot \mathrm{OPT}$ | Abhimanyu Das / David Kempe；ICML 2011；1057–1064 | ICML 2011 会议版；arXiv:1102.3975 是同年预印本 | PASS |
| 8 | `elenberg2018restricted` | https://doi.org/10.1214/17-AOS1679 （Project Euclid 期刊页） | restricted strong convexity $\Rightarrow$ 弱 submodular，greedy 在一般目标下仍有常数因子保证。定位：摘要级；定理号待人工 | Ethan R. Elenberg / Rajiv Khanna / Alexandros G. Dimakis / Sahand Negahban；The Annals of Statistics；2018；46(6B):3539–3568 — 取自 Project Euclid | **期刊终版**（Ann. Statist. 2018），不用 arXiv:1612.00804 (2016)，因为要引的是完整定理体系 | PASS* |
| 9 | `balkanski2016power` | https://proceedings.neurips.cc/paper/2016/hash/c8758b517083196f05ac29810b924aca-Abstract.html （DBLP `conf/nips/BalkanskiRS16`） | optimization from samples 的**正面**结果：bounded curvature $c$ 下有 $(1-c)/(1+c-c^2)$ 近似且最优。定位：摘要级 | Eric Balkanski / Aviad Rubinstein / Yaron Singer；NIPS 2016；4017–4025 | 只有会议版 | PASS* |
| 10 | `balkanski2017limitations` | https://doi.org/10.1145/3055399.3055406 （DBLP `conf/stoc/BalkanskiRS17`） | optimization from samples 的**负面**结果：即使 coverage function 可学，poly 样本下也无常数因子近似。定位：摘要级 | Eric Balkanski / Aviad Rubinstein / Yaron Singer；STOC 2017；1016–1027 | 任务要求 2016 与 2017 两篇分开。2017 选 **STOC 会议版**（原始出处、与 2016 NIPS 平行）；JACM 2022 版（69(3):21:1–21:33）存在，若正文改引期刊版需替换本条 | PASS* |
| 11 | `rosenfeld2018learning` | https://proceedings.mlr.press/v80/rosenfeld18a.html （DBLP `conf/icml/RosenfeldBGS18`） | 学到的 surrogate 直接优化会退化：摘要原文 "recent negative results show that optimizing learned surrogates of submodular functions can result in arbitrarily bad approximations of the true optimum"；正面结果为 optimizable $\Leftrightarrow$ learnable 的等价刻画。定位：摘要级 | Nir Rosenfeld / Eric Balkanski / Amir Globerson / Yaron Singer；ICML 2018；PMLR vol. 80；**4374–4383**（PMLR 官方 BibTeX）。**注意 DBLP 记 4371–4380，与出版方冲突，以 PMLR 为准** | ICML 2018（PMLR v80）唯一版本 | PASS* |
| 12 | `bhawalkar2025unified` | http://papers.nips.cc/paper_files/paper/2025/hash/f3064f7a0ca2328ecb41a3aef6177d68-Abstract-Conference.html （DBLP `conf/nips/BhawalkarCFLL25`；arXiv:2510.21128） | **主题与任务提示不同，见"重要发现 C"**：persistent noisy value oracle 下的统一 meta-algorithm（monotone+matroid 得 $1-1/e$；non-monotone+matroid 得 $1/e$；无约束 non-monotone 得 $1/2$），**不是** learning-augmented。定位：摘要级 | Kshipra Bhawalkar / Yang Cai / Zhe Feng / Christopher Liaw / Tao Lin；NeurIPS 2025 | NeurIPS 2025 正式版；arXiv:2510.21128 为同一篇预印本。**pages 字段：NeurIPS 2025 proceedings 页与 DBLP 均未给页码，故 .bib 不写 pages**（缺字段而非错字段） | PASS* |
| 13 | `agarwal2024learning` | http://papers.nips.cc/paper_files/paper/2024/hash/19cdab1dee61d55158cf106244ceab08-Abstract-Conference.html （DBLP `conf/nips/AgarwalB24`；arXiv:2311.13006） | LAA + submodular 的最近工作；**η 撞名**（见"重要发现 D"）。定位：摘要级——dynamic monotone submodular maximization 的 $1/2-\varepsilon$ 期望近似，摊还更新时间依赖预测误差 | Arpit Agarwal / Eric Balkanski；NeurIPS 2024 | NeurIPS 2024 会议版；arXiv:2311.13006 (2023) 为预印本。proceedings 页与 DBLP 均无页码，.bib 不写 pages | PASS* |
| 14 | `cohenaddad2024learning` | http://papers.nips.cc/paper_files/paper/2024/hash/2db08b94565c0d582cc53de6cee5fd47-Abstract-Conference.html （DBLP `conf/nips/Cohen-AddadOGLP24`） | **主题查明**：用带噪预测绕过 max-cut 与 CSP 最大化版本的**近似难度**（计算壁垒），区别于 online LAA 绕过信息壁垒。定位：摘要原文 "noisy predictions about the optimal solution can be used to break classical hardness results for maximization problems such as the max-cut problem" | Vincent Cohen-Addad / Tommaso d'Orsi / Anupam Gupta / Euiwoong Lee / Debmalya Panigrahi；NeurIPS 2024 | NeurIPS 2024；proceedings 与 DBLP 均无页码，.bib 不写 pages | PASS* |
| 15 | `balcan2018submodular` | https://doi.org/10.1137/120888909 （DBLP `journals/siamcomp/BalcanH18`；arXiv:1008.2159） | "学 submodular 函数难"。定位：**Introduction §1.2（arXiv v3 正文逐字）**："we show that every algorithm for PMAC-learning monotone, submodular functions under arbitrary distributions must have approximation factor $\tilde\Omega(n^{1/3})$, even for constant $\varepsilon$ and $\delta$, and even if the functions are matroid rank functions"；配套上界 $O(n^{1/2})$。定理号待人工（PDF 的定理环境标号未能可靠抽出） | Maria-Florina Balcan / Nicholas J. A. Harvey；SIAM Journal on Computing；2018；47(3):703–754 | **选 SICOMP 2018**：STOC 2011（793–802）是 extended abstract，$\tilde\Omega(n^{1/3})$ 下界的完整构造在期刊版 | PASS |
| 16 | `mirzasoleiman2015lazier` | https://doi.org/10.1609/aaai.v29i1.9486 （DBLP `conf/aaai/MirzasoleimanBK15`） | 随机化 greedy 的 $(1-1/e-\varepsilon)$ 保证与线性时间。定位：摘要逐字 "our randomized algorithm, STOCHASTIC-GREEDY, can achieve a $(1-1/e-\varepsilon)$ approximation guarantee, in expectation"；定理号待人工 | Baharan Mirzasoleiman / Ashwinkumar Badanidiyuru / Amin Karbasi / Jan Vondrák / Andreas Krause；AAAI 2015；1812–1818。**任务提示"AAAI?"已确认为 AAAI** | AAAI 2015 会议版；arXiv:1409.7938 (2014) 为预印本 | PASS* |
| 17 | `purohit2018improving` | https://proceedings.neurips.cc/paper/2018/hash/73a427badebe0e32caa2e1fc7530b7f3-Abstract.html （DBLP `conf/nips/PurohitSK18`） | LAA 的 consistency/robustness 范式（ski rental、non-clairvoyant scheduling）。定位：摘要逐字 "improve with better predictions, but do not degrade much if the predictions are poor" | Manish Purohit / Zoya Svitkina / Ravi Kumar；NeurIPS 2018；9684–9693 | NeurIPS 2018 会议版；arXiv:2407.17712 (2024) 是补挂 e-print | PASS* |
| 18 | `lykouris2021competitive` | https://doi.org/10.1145/3447579 （DBLP `journals/jacm/LykourisV21`） | LAA caching：竞争比随 oracle 误差下降且被 $O(\log k)$ 封顶。定位：ICML 版摘要逐字 "a competitive ratio that both (i) decreases as the oracle's error decreases, and (ii) is always capped by $O(\log k)$"；定理号待人工 | Thodoris Lykouris / Sergei Vassilvitskii；Journal of the ACM；2021；68(4):24:1–24:25 | **选 JACM 2021 期刊版**。ICML 2018 版页码在两个官方源冲突（DBLP 3302–3311 vs PMLR 3296–3305），且 PMLR 的 BibTeX 把第二作者拼成 "Vassilvtiskii"，故不入 .bib；JACM 版无此问题且为终版 | PASS* |
| 19 | `kempe2003maximizing` | https://doi.org/10.1145/956750.956769 （DBLP `conf/kdd/KempeKT03`） | influence maximization 作为 monotone submodular 最大化的应用。定位：**THEOREM 2.1**（引 Nemhauser et al. 的 $(1-1/e)$ greedy 保证）、**THEOREM 2.2**（Independent Cascade 的影响函数 submodular）、**THEOREM 2.5**（Linear Threshold 同理）。逐字取自 kdd03-inf.pdf | David Kempe / Jon Kleinberg / Éva Tardos；KDD 2003；137–146 | **选 KDD 2003**（任务指定，且是原始出处）；Theory of Computing 11:105–147 (2015) 是期刊版，如正文需要完整证明可换 | PASS |
| 20 | `lin2011class` | https://aclanthology.org/P11-1052/ （DBLP `conf/acl/LinB11`） | submodular document summarization（E3 实验的目标函数出处）。定位：论文主题级（ACL Anthology 页未挂摘要） | Hui Lin / Jeff Bilmes；Proceedings of the 49th Annual Meeting of the ACL: HLT；2011；510–520；Portland, Oregon, USA — 取自 ACL Anthology 官方 BibTeX | ACL 2011 唯一版本 | PASS* |
| 21 | `rozemberczki2019gemsec` | https://doi.org/10.1145/3341161.3342890 （DBLP `conf/asunam/RozemberczkiDSS19`；SNAP: https://snap.stanford.edu/data/gemsec-Facebook.html） | E2 的三个替代图数据出处。定位：SNAP gemsec-Facebook 页把本文列为**指定引用**；页上 politician 5,908/41,729、government 7,057/89,455、artist 50,515/819,306，与 `results/E2_notes.md` 第 28–30 行完全一致 | Benedek Rozemberczki / Ryan Davies / Rik Sarkar / Charles Sutton；ASONAM 2019；65–72。**任务提示"CIKM/ASONAM?"已确认为 ASONAM（IEEE/ACM）** | ASONAM 2019 会议版；arXiv:1802.03997 (2018) 为预印本 | PASS |
| 22 | `leskovec2007graph` | https://doi.org/10.1145/1217299.1217301 （DBLP `journals/tkdd/LeskovecKF07`；SNAP: https://snap.stanford.edu/data/email-Eu-core.html） | email-Eu-core 数据出处之一。定位：SNAP 页 "Source" 栏明确列出本文 | Jure Leskovec / Jon Kleinberg / Christos Faloutsos；ACM Transactions on Knowledge Discovery from Data；2007；1(1):2（article number 2，非页码区间） | TKDD 期刊版（SNAP 指定形式） | PASS |
| 23 | `yin2017local` | https://doi.org/10.1145/3097983.3098069 （DBLP `conf/kdd/YinBLG17`；同上 SNAP 页） | email-Eu-core 数据出处之二。定位：SNAP 页 "Source" 栏与 Leskovec et al. 2007 **并列**，两条都要引 | Hao Yin / Austin R. Benson / Jure Leskovec / David F. Gleich；KDD 2017；555–564 | KDD 2017 会议版 | PASS |

---

## 重要发现

### A. Goundan–Schulz 2007 的正式出处与 Theorem 1 的逐字内容

**正式出处**：Pranava R. Goundan and Andreas S. Schulz, *Revisiting the Greedy Approach to
Submodular Set Function Maximization*, **Working paper, Massachusetts Institute of Technology,
2007**，公开于 Optimization Online（preprint 1740，2007-08-01 提交）。
**它没有会议或期刊版**：DBLP 对 `Goundan Schulz` 的检索返回 0 条；只在 Optimization Online 有官方页。
因此 .bib 用 `@techreport`（`type = {Working paper}`，`institution = {Massachusetts Institute of Technology}`，
`note` 记 preprint 编号）。ICLR 模板的 .bst 支持 `techreport`，编译无警告。

从解密后的 PDF 抽取的正文（Section 3 "Generalized Results over Uniform Matroids"，p. 7）：

- **greedy 步的定义**（$\alpha$-approximate incremental oracle）：
  "Select an element $e_i \in E \setminus S_{i-1}$ for which $\alpha\,\rho_{e_i}(S_{i-1}) \ge
  \max_{e \in E\setminus S_{i-1}} \rho_e(S_{i-1})$ using an $\alpha$-approximate incremental oracle."
- **Theorem 1**：
  $$\frac{z_{\mathrm{opt}}}{z_g} \;\le\; \frac{(\alpha k)^k}{(\alpha k)^k - (\alpha k - 1)^k}
  \;\le\; \frac{e^{1/\alpha}}{e^{1/\alpha}-1}.$$
  等价地 $z_g/z_{\mathrm{opt}} \ge 1 - \left(1 - \frac{1}{\alpha k}\right)^k \ge 1 - e^{-1/\alpha}$。
- 其后一句："For the case when $\alpha = 1$, the result is precisely that of Nemhauser et al. (1978)
  and therefore tight."

**两条需要人类判断的后果**：

1. **GLOSSARY.md 第 20 行的方向写反了。** 该行写 "α-approximate incremental oracle 的参数
   $\alpha = 1/\eta^{\mathrm{sel}}$"。但按 Goundan–Schulz 自己的约定（$\alpha\rho_{e_i} \ge \max_e \rho_e$，
   即 $\alpha \ge 1$），代入其 Theorem 1 得到的正是 $1-(1-1/(\alpha k))^k$，与本文
   $L_K(\eta) = 1-(1-1/(\eta K))^K$ 逐字相同。所以对应关系是 **$\alpha = \eta^{\mathrm{sel}}$**，
   不是 $1/\eta^{\mathrm{sel}}$。建议 F0/F5 把该行改掉。
2. **本文的 Theorem 6（RESEARCH_STATE R1）在数学上就是 Goundan–Schulz Theorem 1 的实例化。**
   RESEARCH_STATE R1 已写"本质上是 (1/η)-approximate greedy 的经典分析（Goundan–Schulz 2007
   [CITATION-NEEDS-VERIFICATION]）"——本次核验把这个标记解除，并且确认对应是**逐字相同**而非"本质上"。
   正文措辞必须相应下调，建议写成：
   > Restated in the terminology of \citet{goundan2007revisiting}, predictive greedy queries an
   > $\eta^{\mathrm{sel}}$-approximate incremental oracle, and Theorem~1 of that paper gives
   > $1-(1-1/(\eta^{\mathrm{sel}}K))^K$. Our contribution is not this bound but the characterization
   > of when it is attained (Section~...).
   不得写 "we prove"、"our new lower bound"。这是本晚最需要人类拍板的一处。

### B. Horel–Singer 2016 vs Hassidim–Singer 2017（原稿引用错误的确认）

RESEARCH_STATE.md"已知的论文错误"第 3 条得到独立确认，两篇是不同的文献、不同的方向：

- **Horel & Singer, NIPS 2016, pp. 3045–3053**，*Maximization of Approximately Submodular Functions*。
  **负面结果**：Theorem 3 给出 poly-query 下界（$\varepsilon$ 大于约 $n^{-1/2}$ 时任何算法的近似比
  不优于 $O(n^{-\delta})$）。这才是原稿要引的那篇。
- **Hassidim & Singer, COLT 2017, PMLR 65:1069–1122**，*Submodular Optimization under Noise*。
  **正面结果**：i.i.d. 噪声下对足够大的 $k$ 可任意逼近 $1-1/e$；摘要同时明说 adversarial noise
  下没有 non-trivial guarantee。
- 另外，同两位作者还有 Singer & Hassidim, *Optimization for Approximate Submodularity*,
  NeurIPS 2018, pp. 394–405（作者序相反）。改稿时不要与上面两篇混淆。

### C. Bhawalkar et al. 2025 存在，但主题不是 learning-augmented

任务清单第 11 条的提示是"learning-augmented submodular?"。**核验结果：不是。**
该文是 *A Unified Approach to Submodular Maximization Under Noise*（Kshipra Bhawalkar, Yang Cai,
Zhe Feng, Christopher Liaw, Tao Lin），NeurIPS 2025（arXiv:2510.21128），处理的是
**persistent noisy value oracle**（同一集合重复查询返回同一值），给出一个把任意 "robust"
精确算法转成抗噪算法的 meta-algorithm。它属于本文 related work 的**噪声 oracle**一支，
和 Horel–Singer / Hassidim–Singer 同组，**不能**放进 LAA 一段。它对 monotone + matroid
拿到 $1-1/e$，改进了 Huang et al. (2022) 的 $(1-1/e)/2$。

### D. Agarwal–Balkanski 2024 的 η 撞名（GLOSSARY 第 13 行）确认

他们的 $\eta$ 是**计数型**误差："the number of elements that are not inserted and deleted within
$w$ time steps of their predicted insertion and deletion times"（arXiv:2311.13006 摘要）。
本文的 $\eta = \eta_u\eta_o$ 是**乘性**边际增益误差。两者量纲、取值范围、单调方向都不同。
GLOSSARY 第 13 行的处理（引用该文时改写为 $\eta_{\mathrm{AB}}$ 或加脚注）成立且**必须执行**，
否则读者会把 $\eta \to \infty$ 的 robustness 讨论错读成他们的设定。

### E. SNAP email-Eu-core 的规定引用是**两条**

`https://snap.stanford.edu/data/email-Eu-core.html` 的 "Source" 栏并列列出：
1. Hao Yin, Austin R. Benson, Jure Leskovec, David F. Gleich. *Local Higher-order Graph Clustering.*
   KDD 2017, pp. 555–564.
2. Jure Leskovec, Jon Kleinberg, Christos Faloutsos. *Graph Evolution: Densification and Shrinking
   Diameters.* ACM TKDD 1(1), 2007.

两条都已入 .bib。E2 用的是 1,005 节点 / 25,571 边的版本，与 SNAP 页与
`results/E2_notes.md` 第 27 行一致。正文数据小节应同时 cite 两条。

---

## 出版方与 DBLP 冲突的字段（已按出版方裁定，记录备查）

| 条目 | DBLP | 出版方 | 采用 | 理由 |
|---|---|---|---|---|
| Rosenfeld et al. 2018 | pages 4371–4380 | PMLR v80 官方 BibTeX: 4374–4383 | 出版方 | PMLR 是 ICML 2018 的出版方，其页面自带 BibTeX 为准 |
| Lykouris–Vassilvitskii ICML 2018 | pages 3302–3311 | PMLR v80: 3296–3305（且作者拼作 "Vassilvtiskii"） | **两者都不采**，改引 JACM 2021 | 冲突未解，且期刊版是终版 |

---

## 未入 .bib 的版本（不是失败，是版本选择）

以下条目**存在且已核验**，但按第 (4) 步没有选中，故不写进 `paper/references.bib`。
若正文改写后需要它们，直接补入即可，不需要重新核验存在性。

- Feige 1998 的 STOC 1996 preliminary version（pp. 314–318，doi 10.1145/237814.237977）。
- Horel & Singer 的 arXiv:2411.10949（2024 年补挂的 e-print）。
- Hassidim & Singer 的 arXiv:1601.03095（2016 预印本）。
- Singer & Hassidim, *Optimization for Approximate Submodularity*, NeurIPS 2018, 394–405（另一篇，未用）。
- Das & Kempe 的 arXiv:1102.3975。
- Elenberg et al. 的 arXiv:1612.00804。
- Balkanski, Rubinstein & Singer, *The Limitations of Optimization from Samples*, **JACM 69(3):21:1–21:33, 2022**
  （期刊版；本次选 STOC 2017）。
- Balcan & Harvey, *Learning Submodular Functions*, **STOC 2011, 793–802**（extended abstract；本次选 SICOMP 2018）。
- Lykouris & Vassilvitskii, ICML 2018 版（页码冲突，见上表）。
- Kempe, Kleinberg & Tardos, *Theory of Computing* 11:105–147, 2015（期刊版；本次选 KDD 2003）。
- Mirzasoleiman et al. 的 arXiv:1409.7938。
- Rozemberczki et al. 的 arXiv:1802.03997。
- Purohit, Svitkina & Kumar 的 arXiv:2407.17712。
- Agarwal & Balkanski 的 arXiv:2311.13006。
- Nemhauser, Wolsey & Fisher, *An analysis of approximations ... — II*（Math. Programming Study 8, 1978；另一篇）。

---

## 统计

- 待核验组数：**21 组**（任务清单）→ 展开为 **23 条**参考文献
  （Balkanski–Rubinstein–Singer 拆为 2016 与 2017 两条；SNAP email-Eu-core 的规定引用是 2 条）。
- **通过：23 篇**（`PASS` 9 篇 + `PASS*` 14 篇），全部写入 `paper/references.bib`。
- **待验：0 篇**。本轮没有条目因存在性或字段问题被拒。
- **第 (2) 步达到 `PASS` 级（定理号/定义号、正文小节逐字、或官方数据页指定引用）的 9 篇**：
  Feige 1998、Goundan–Schulz 2007（Thm 1）、Horel–Singer 2016（Thm 3）、Das–Kempe 2011（Def 2.3 + Thm 3.2）、
  Balcan–Harvey 2018（§1.2 逐字）、Kempe–Kleinberg–Tardos 2003（Thm 2.1/2.2/2.5）、
  Rozemberczki et al. 2019、Leskovec et al. 2007、Yin et al. 2017（后三条为数据集官方页指定引用）。
- **陈述定位只到摘要/条目级、定理号待人工的：14 篇**，其中两篇（Nemhauser–Wolsey–Fisher 1978、
  Nemhauser–Wolsey 1978）是因为 Springer 与 INFORMS 对本环境返回 HTTP 403、Semantic Scholar
  的摘要被出版方屏蔽。人工在有机构订阅的机器上补定理号即可，**不影响这两条现在进 .bib**
  （存在性、字段、版本三步都已过）。

### 编译验证

在临时目录用模板的 `.sty` + `.bst` 做了 `pdflatex → bibtex → pdflatex ×2` 全流程测试
（23 条全部 `\citep`，另加一个 `\citet{goundan2007revisiting}`）：

- `t.blg`：`You've used 23 entries`，**warning$ -- 0**，无 "empty ... in" 之类字段告警。
- `t.log`：0 处 `Citation ... undefined`，无 LaTeX warning/error。
- 重音（`{\'E}va Tardos`、`Vondr{\'a}k`）与 `@techreport` 均正确渲染；模板未加载 `inputenc`，
  所以 .bib 一律用 7-bit LaTeX 重音命令，不要改成 UTF-8 字符。

（测试在 scratchpad 中进行，`paper/` 下除 `references.bib` 外没有被写入任何文件。）

---

## 交给下一个任务的动作项

1. **bibkey 不一致，`paper/main.tex` 现在编译有 1 条 undefined citation。**
   `paper/sections/results.tex:58` 写的是 `\citep{goundan2007}`，本文件产出的 .bib 用的是
   TASKS4.md F6 指定的 firstauthor+year 风格 key `goundan2007revisiting`。
   `paper/main.blg` 有 `Warning--I didn't find a database entry for "goundan2007"`，
   `paper/main.log:417` 有对应的 natbib warning。
   修法：把 `sections/results.tex:58` 的 `goundan2007` 改成 `goundan2007revisiting`。
   （F6 的写入范围限定在 `paper/references.bib` 与 `results/F6_*`，所以这里只记录不改。
   .bib 里不放同一篇文献的第二个 key，避免参考文献表出现重复条目。）
2. **GLOSSARY.md 第 20 行的 $\alpha = 1/\eta^{\mathrm{sel}}$ 要改成 $\alpha = \eta^{\mathrm{sel}}$**，
   理由见"重要发现 A"第 1 点。
3. **RESEARCH_STATE.md R1 的 `[CITATION-NEEDS-VERIFICATION]` 标记可以去掉**，
   同时把"本质上是"改成更强的措辞（逐字相同），见"重要发现 A"第 2 点。
4. **RESEARCH_STATE.md"已知的论文错误"第 3 条已独立确认**（见"重要发现 B"），可标为已核实。

---

## 对 [CITATION-NEEDS-VERIFICATION] 条目的正文写法

本轮没有产生这类条目。但改稿过程中若要新引一篇尚未走完四步核验的文献，按下面的写法处理，
**不得**先写进 `references.bib`：

```latex
% 正文里：不写 \citep，改写成带标记的文字，并在同一行留 TODO 注释。
The same phenomenon has been reported for streaming submodular maximization
[CITATION-NEEDS-VERIFICATION: author?, venue?, year?].
% TODO(F6): 四步核验后替换为 \citep{key}；未过核验则整句删除或改为不带引用的限定句。
```

三条约束：

1. 标记必须写在正文可见处（不是只写在 `%` 注释里），这样编译出的 PDF 里能一眼看见，
   人工复核不会漏。
2. 带 `[CITATION-NEEDS-VERIFICATION]` 的句子不得作为任何定理、贡献列表或摘要中陈述的依据；
   只能出现在 related work 的叙述句里。
3. 提交前必须清零：要么补完四步核验换成 `\citep{...}`，要么删句。可用
   `grep -rn "CITATION-NEEDS-VERIFICATION" paper/` 检查。

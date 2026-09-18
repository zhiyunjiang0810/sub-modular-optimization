# VERIFICATION_MATRIX (V11, 2026-09-18)

标准：A 陈述逐字（台账 vs 正文量词比对）；B 两条独立推导（路线一仓库证明，路线二盲审 Opus 子代理，只给 Definition 1 方案二、模型假设、陈述、记号表）；
C oracle（sympy 恒等式、有理格点精确不等式、穷举合法性、精确 LP/对偶）；D 陈述反例搜索（随机 ≥ 2000 + 结构化）；E 量词审计表。
标签规则：五项全过 [VERIFIED-CROSS]；B 或 E 有 GAP [HAND-PROOF-UNREVIEWED]；C 或 D 失败 [FAILED]；C 过 B 缺 [VERIFIED-ORACLE-ONLY]。
每行细节：results/V11/route2/<key>.md（路线二）、oracle/<key>.{py,log,json,md}（C/D）、audit/<key>.md（A/E）、compare/<key>.md（B 比对）。

| label | 正文编号 | 陈述原文 | 路线一位置 | 路线二结论一致? (B) | oracle 项目与结果 (C) | 反例搜索 (D) | 量词审计 (E) | 最终标签 | 裁定理由 | 可写进正文的精确表述 | K=3, η=3/2 数字走读 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| prop:necessity (alias prop:nobound) | Prop 1 | 逐字见下方明细 §prop:necessity (alias prop:nobound)（源 statements.md） | app:necessity + appendix_model_proofs.tex (unwired) | B-PASS; consistent=True, quantifiers=False; divergences: D1 构造常数：route one 内部即有两个构造，appendix_proofs.tex app:necessity 用 gamma=K^2/(n(n-K))，appendix_model_proofs.tex 用 delta=K/(n-K)；route two 的 deterministic 段取 delta（= 甲2），randomized 段取 gamma（= 甲1）。三者都到达 statement 的界；gamma <= K/(n-K) 等价于 K/n <= 1，全参数成立 [VERIFIED-SYMBOLIC]，故甲1 的 deterministic 结论更强一个因子 K/n，但 ...; route-2 gaps: G1 Step 6-7（deterministic + arbitrary query access 导致 transcript 与 A 无关、输出为固定集合）[HAND-PROOF-UNREVIEWED]，无 oracle 可检验。route  ... | C0 symbolic relations between the two constructions (sympy): PASS; C1 instance validity of both constructions (f(empty)=0, monotone, submodular): PASS; C2 Definition 1 band; smallest admissible factors eta_u=1, eta_o=1/delta, both attained: PASS; C3 OPT = f(O) = K: PASS; C4/C5 predictive greedy (adversarial ties) and exhaustive argmax of ftilde over K-sets (adversarial ties): PASS; C6 arbitrary fixed output T with /T/ <= K: PASS; C7 existence of a disjoint K-set O for every output when n >= 2K:  ... | random 2400, structured 4, violations 0, worst worst slack = 0 (bound attained with equality), reached in 1502 of 2400 trials, e.g. kind=rule_on_answers, K=1, n=11, /T ... | A_match=False; A_diffs: D1: 形容词 'arbitrary query access to $\tilde f$' 在正文 prop:necessity 环境内修饰被全称的算法，台账 T1 把它放在陈述字段之外的独立'前提'字段；作用范围相同，陈述文本不重合。; D2: 正文第二句 'Consequently no constant worst-case ratio is achievable without an error assumption.' 不在台账 T1 的陈述字段里，只以中文出现在卡标题'无误差假设则 ...; GAP: GAP-1（陈述层）：/T/ ≤ K 未写，正文与台账都只写 'the output T'；字面上若允许 /T/ > K，取 T = N 即得 f(T) > f(O*)，命题不成立。证明里两份路线一材料都用到该条件。; GAP-2 ... | **[HAND-PROOF-UNREVIEWED]** | C 11 项 PASS（160 实例精确穷举、18240 个固定输出、两个构造）；D 2400 随机算法 0 违反；B-PASS（路线二加了 /T/ ≤ K 读法）；E GAP：/T/ ≤ K、'no constant' 的量词、addendum B.9 措辞未落实、query 模型未定义。GAP 全是陈述层措辞，证明无缺口。 | Let K >= 1 and n >= 2K. For every deterministic algorithm with arbitrary query access to the surrogate whose output T has /T/ <= K, there is a pair (f, f~) with f monotone submodular, f(empty) = f~(empty) = 0, satisfying every assumption of Section 2 except a bound on eta (its error is finite, eta = (n-K)/K), on which f(T) <= (K/(n-K)) OPT. Consequently, for fixed K, no worst-case ratio bounded away from 0 uniformly in n holds without a bound on eta. | K = 3, delta = 1/eta = 2/3, O = {0,1,2}, T = {3,4,5}: f(O) = 3 = OPT, f(T) = 3 * 2/3 = 2, ratio 2/3 = 1/eta, with eta_u = 1 and eta_o = 3/2 both attained. n = 6: statement constant K/(n-K) = 1; n = 7: 3/4. Both are >= 2/3, so f(T) <= K/(n-K) * OPT holds. n = 8: 3/5 < 2/3 and n = 12: 1/3 < 2/3, so a  ... |
| prop:valueacc | Prop 2 | 逐字见下方明细 §prop:valueacc（源 statements.md） | appendix_model_proofs.tex (convention B) + app:valueacc (old) | B-PASS; consistent=True, quantifiers=False; divergences: D1 (i) 的 n>=2：statement 与 route one 都未写，route two 显式补为前提并给出 n=1 时 (i) 为假的一行论证（value accuracy 逼出 eta<=(1+eps)/(1-eps) 有限）。两条路线的构造实际都在 n=2 上，属共有隐含前提。[HAND-PROOF-UNREVIEWED]; D2 (i) 末句的 L_K(eta) 分句：convention-B 证明 appendix_model_proofs.tex 停在 eta=infinity，没有写这一句；旧附录 app:valueacc 有「every bound of the fo ...; route-2 gaps: R2-G1 (i) 末句只证成非蕴含（不存在有限 eta），没有证成「ratio 可低于任意给定 L_K(eta)」；Instance B 族在 eps=1/5,K=2 的最坏 ratio 2/3 高于 L_2(3/2)=5/9。裁定：这是正确的 ... | C1 (i) two-element construction, eps in {1/10, 1/2, 9/10}, base n=2: PASS; C1 (i) padded to n=6 with 4 zero-gain elements: PASS; C1b cross-check of the OLD appendix app:valueacc (i) instance: PASS; C2a (ii) sympy in M: smallest factors and eta=1: PASS; C2b (ii) numeric exact recheck, 200 random monotone submodular f with random rational M: PASS; C3a (iii) sympy identities c/eta_u = 1-eps and c*eta_o = 1+eps: PASS; C3b (iii) domain eps in [0,1): PASS; C4 (iii) 2200 random LEGAL surrogates, actual ... | random 6597, structured 7, violations 0, worst worst slack = 0 (tight, never negative). Over all 2200 legal surrogates x 57840 subsets, min over S of min(c*ftilde(S) - ... | A_match=False; A_diffs: D1 标题限定: 台账按 addendum §B 第5条改成 "Value accuracy is neither sufficient nor necessary for predictive greedy"; 正文 results.tex 的 proposition 标题仍是无限定版 "…neither sufficient nor necessary"。; D2 (ii) 的 η 结论: 台账写 "Definition 1 以 η_u=1/(1+M)、η_o=1+M 成立, 全局 η=1" ...; GAP: G1 陈述层: (i) 缺 n ≥ 2。n=1 时 (i) 为假（唯一 pair 是 (∅,e), value accuracy 给 f̃({e}) ≥ (1−ε)f({e})>0, 于是 η ≤ (1+ε)/(1−ε) 有限）。 ... | **[HAND-PROOF-UNREVIEWED]** | C 16 项 PASS（含 2200 个合法 surrogate × 57840 子集的 (iii)）；D 6597 次 0 违反；B-PASS；E GAP：(i) 缺 n ≥ 2，(ii) 缺 f 不恒零，正文仍旧约定。(iii) 单独看五项全过且 addendum 记 Cici 已读，可标 [HAND-PROOF-REVIEWED]+[VERIFIED-EXHAUSTIVE]。 | (i) For every eps in (0,1) and every n >= 2 there are a monotone submodular f with f(empty) = 0 and a surrogate f~ with f~(empty) = 0, value-accurate at level eps, whose marginal gain vanishes at a pair (S, e) with d_e(S) > 0; hence no finite (eta_u, eta_o) of Definition 1 exists for f~, and value accuracy alone yields no bound of the form L_K(eta). (ii) For every M > 0 and every monotone submodular f not identically zero, f~ = (1+M) f is value-accurate at no level eps < M, yet satisfies Definition 1 with (eta_u, eta_o) = (1/(1+M), 1+M), so eta = 1, and predictive greedy on f~ picks at every s ... | K = 3, eta = 3/2: (eta_u, eta_o) = (1, 3/2), eps = (eta-1)/(eta+1) = 1/5, c = 2 eta_u/(eta+1) = 4/5. Modular instance n = 4, weights (1,1,1,1), predicted factors (1, 3/2, 1, 3/2); on the 3-set S = {0,1,2}: f(S) = 3, ftilde(S) = 7/2, c ftilde(S) = 14/5. Band: (1-eps) f(S) = 12/5 <= 14/5 <= 18/5 = (1+ ... |
| thm:ceiling | Proposition (upper bound for unbounded queries) | 逐字见下方明细 §thm:ceiling（源 statements.md） | app:ceiling + J5_ceiling_proof.md; route yi: appendix_model_proofs remark | B-PASS; consistent=True, quantifiers=False; divergences: D1 构造摆法：路线一把重权放在 N\S（n-K 个元素），路线二只放 h=min{K,n-K} 个；比值恒等 [VERIFIED-SYMBOLIC]，无实质差别; D2 C1 的推法：路线一用 X<=Y 加两条链的 band（J5 式 (6)），路线二引入残差 r=f-ftilde 并用其单调性加 L1 归一化；代数上恒等; D3 C4 的取法：路线一求和（R=sum_s r_s <= A），路线二取最小（m <= f(S)/K）；最终界相同; D4 紧性：路线二给出逐 j 的紧实例族 C7（(*) 对每个 j 不可改进），路线一只在最坏 j 处给紧性；判定人 LP 复核支持路线二的更强说法 ...; route-2 gaps: RG1 randomized ceiling 的精确值未定：路线二只从 U1 那一族得 C*·(n+(eta-1)h)/n；同一开口在路线一也是 OPEN，故不构成路线二相对路线一的欠缺; RG2 n=K 时 error 两侧不能同时取等：路线二 ... | C0 sympy identities (C* two branches, slack identity (7), E decomposition (8), single-exchange decomposition (9), Horel-Singer eps substitution, adversary ratio forms): PASS; C1 (a) n >= 2K adversary exactness, K = 2..4, n = 2K..10, 14 rational splits: PASS; C1b (a) same adversary check for K = 1, run separately, n = 2..10: PASS; C2 (b) attainment on random exact instances, n >= 2K, n <= 7, K <= 3: PASS; C3 (c) adversary direction against three algorithm types: PASS; C4 rerun of results/J5_hardc ... | random 3544, structured 5, violations 0, worst Worst slack is 0 everywhere, i.e. the inequalities are tight at several points and never violated. Attainment side, per- ... | A_match=False; A_diffs: D1 environment 与标题：正文是 proposition + "Upper bound for unbounded queries"（addendum B.1 的降级），台账 LaTeX 块与 results/V11/statements.md 第 74 行元数据仍写 theorem + "Deterministic ceiling, all ground-set sizes"。数学内容不变，但矩阵两栏来源不一致。; D2 逆向方向的 O* 全称：正文写 "for every opt ...; GAP: K>=2：陈述的定义域比路线甲需要的窄，app:ceiling 只固定 K>=1，K>=2 在证明里无处使用（oracle C1b 对 K=1 全过）；按 addendum B.3 的目标形态会自动消失; error exactl ... | **[HAND-PROOF-UNREVIEWED]** | C 8 项 PASS（含 J5 hardcore 复跑：恒等式 (7)(8)(9)、52 LP、24 对手实例）；D 3544 次 0 违反；B-PASS（n<2K 交换论证被盲审独立复推）；E GAP：K ≥ 2 无用（应 K ≥ 1）、'exactly' 无定义、随机段缺条件于随机串一步。 | Let K >= 1 and n >= 2K, and let eta_u, eta_o > 0 with eta_u eta_o = eta >= 1. (a) For every deterministic algorithm with arbitrary query access to f~ that outputs a set T with /T/ <= K, there is a pair (f, f~) with f monotone submodular, f(empty) = f~(empty) = 0, whose smallest admissible factors are exactly (eta_u, eta_o), on which f(T) <= OPT/eta. (b) On every instance satisfying Definition 1 with product eta, a K-set S maximizing f~ over all K-subsets satisfies f(S) >= K/(K + (eta-1)/O* minus S/) OPT >= OPT/eta for every optimal K-set O*. Hence the optimal worst-case ratio of deterministic  ... | K=3, eta=3/2, n=6 adversary (c=1, split (3/2,1)): f(O)=9/2, f(T)=3, ratio 2/3 = 1/eta. n=5 (=2K-1) adversary: f(S)=3, f(O)=4, ratio 3/4 = C*_{5,3}(3/2). Per-instance form at a=/O*\S/=0,1,2,3: 1, 6/7, 3/4, 2/3. |
| prop:guarantee | Prop 3 | 逐字见下方明细 §prop:guarantee（源 statements.md） | app:guarantee | B-PASS; consistent=True, quantifiers=False; divergences: D1 量词域差异（唯一实质性量词分歧）：route1 用 def:eta verbatim，eta_u,eta_o >= 1；route2 的 Q9 写 convention B，eta_u,eta_o > 0 且乘积 >= 1。; D2 由 D1 派生、可复算的瑕疵：route2 Step 12 把 eta^tr 的两个因子各自截断到 1，Step 14 默认全局因子同样逐因子截断。verbatim 约定下自洽，convention B 下不成立：取 f̃=2f，全局 (eta_u,eta_o)=(1/2,2)、eta=1，而逐因子截断的 eta^tr=max(1,1/2)*max(1,2) ...; route-2 gaps: [ASSUMPTION-ADDED] eta^tr 的形式定义（Step 12）。route1 无公式故不可证伪；未闭合项是：若论文采用 convention B，该定义须改成乘积层面截断。; [ASSUMPTION-ADDED] 全零轨迹时截断 ... | C0 sympy identities on L_K [VERIFIED-SYMBOLIC]: PASS; C1 random exact instances: f(T) >= L_K(eta^sel) OPT and the ordering [VERIFIED-EXHAUSTIVE]: PASS; C2 Step-1 covering r_t <= K M_t and the contraction [VERIFIED-EXHAUSTIVE]: PASS; C3 auxiliary rem:app-product per-step product bound [VERIFIED-EXHAUSTIVE]: PASS; C4 legal band implies finite eta^sel [VERIFIED-EXHAUSTIVE]: PASS; C5 U_K exact tightness of L_K under eta^sel [VERIFIED-EXHAUSTIVE]: PASS; C6 rerun results/F2_etasel_tight.py [VERIFIED-L ... | random 3000, structured 5, violations 0, worst "Worst slack over all runs is 0, i.e. equality, attained on 790 of the 9064 C1 checks (trivial ones such as K=1, eta^sel ... | A_match=False; A_diffs: D1: normalization f(empty)=0 appears only in the paper statement (results.tex line 80 'Let $f$ be monotone submodular with $f(\emptyset)=0$'); the ledger T3 statement field (THEOREM_LEDGER.md line 70) writes only 'f 单调 submodular'. It is load-bearing ...; GAP: GAP-1 (light): normalization f(empty)=0 is used implicitly at app:guarantee Step 3 ('With $r_0=f(O^{\ast})$') and i ... | **[HAND-PROOF-UNREVIEWED]** | C 8 项 PASS（3000 随机 run；F2_etasel_tight、T5_symbolic 复跑）；D 0 违反；B-PASS；E 轻 GAP：f(∅)=0 与 r_t ≥ 0 在附录隐式使用。B 比对新发现方案二下 η^tr 的定义须按乘积截断（见重点发现 1）。 | Let f be monotone submodular with f(empty) = 0, O* an optimal K-set, and T = S^K the output of a K-step run of predictive greedy with selection error eta^sel (per-step factors a_t, eta^sel = max{1, a_t}, L_K(infinity) = 0). Then f(T) >= L_K(eta^sel) OPT >= (1 - e^{-1/eta^sel}) OPT with L_K(x) = 1 - (1 - 1/(xK))^K. If f~ satisfies Definition 1 with product eta, the same bound holds with eta^sel replaced by eta^tr (the band restricted to the run's states, with the truncation at 1 applied to the product of the two factors) or by eta, and L_K(eta^sel) >= L_K(eta^tr) >= L_K(eta). | "K = 3, U_3 family with ahat = 3/2 (n = 6, OPT = 1): the three steps have a_t = 3/2 each, so eta^sel = eta^tr = 3/2 and f(T) = 386/729 = L_3(3/2) ≈ 0.5295, exact equality.\nThe same instance has global eta = (3·3/2 − 1)/2 = 7/4 with L_3(7/4) = 4348/9261 ≈ 0.4695, so the three rulers read 386/729 = 3 ... |
| lem:coherence | Lemma | 逐字见下方明细 §lem:coherence（源 statements.md） | app:coherence + H_J3_gate_check.py | B-GAP (route two incomplete); consistent=True, quantifiers=False; divergences: D1 sharp form 是两个不同的命题：路线一（results.tex 153-167 行 + 台账 T5）的 sharp form 是 d - g/eta >= (1-1/eta)(g-h) >= 0（d=d_e(S), g=d_{e'}(S), h=d_{e'}(S+e)），第一个不等号是 (ii) 的恒等改写，第二个用 submodularity 加 eta>=1，并带推论 eta>1 且 d=g/eta ⇒ h=g；路线二第 4 节的 (S1) order transfer、(S2) 常数 1/eta 不可改进、(S3) min 形式、(S4) 取等刻画是自行重构的另一组命题。两 ...; route-2 gaps: GAP-A 未产出路线一的 sharp form 链 d - g/eta >= (1-1/eta)(g-h) >= 0（路线二自报 GAP-1，标 [ADDED-ASSUMPTION]）。可一行闭合：第 ... | C0 own sympy derivation of the slack decompositions: PASS; C1 random exact instances: parts (i), (ii) and the sharp form: PASS; C2 three-term nonnegative decomposition on every triple: PASS; C3 rerun results/H_J3_gate_check.py: PASS; C4 rerun results/J2_core_oracles.py, coherence part: PASS; C5 running example K=3 eta=3/2 exact worst-case trajectory: PASS | random 3468, structured 6, violations 0, worst Worst slack of (ii) (= slack of (i) = slack of the sharp-form first inequality) is 0, i.e. equality is attained: 29,398  ... | A_match=True; A_diffs: none; GAP: GAP-1 (medium): the hypothesis 'f monotone' is never used by route one. app:coherence (appendix_proofs.tex 524-579) proves the exchange identity from the set-function definition, (i) by chaining the bands, and (ii) from f's exchange identity plus (i); deleting 'monotone' leaves the derivation word f ... | **[HAND-PROOF-UNREVIEWED]** | C 6 项 PASS（自写 slack 分解 + H_J3/J2 复跑）；D 3468 三元组 0 违反；A 逐字一致；B：引理本体路线二完整一致，sharp form 链不在盲审输入里由判定人一行闭合（B-GAP 形式上）；E GAP（中）：'f monotone' 前提在证明中未使用（空洞性检验）。一行修订即可升 [VERIFIED-CROSS]。 | Let f~ satisfy Definition 1 with product eta for a set function f, let S be a subset of N and e, e' not in S with d~_e(S) >= d~_{e'}(S). Then (i) d_e(S + e') >= d_{e'}(S + e)/eta and (ii) (1 - 1/eta) d_{e'}(S + e) >= d_{e'}(S) - d_e(S). If moreover f is submodular, with d = d_e(S), g = d_{e'}(S), h = d_{e'}(S + e): d - g/eta >= (1 - 1/eta)(g - h) >= 0, and eta > 1 with d = g/eta forces h = g. The band is used at the off-run state S + e, so the lemma holds for the global eta only (not for eta^sel or eta^tr). (The hypothesis 'f monotone' is not used by the proof.) | K = 3, eta = 3/2: k_1 = 4, q = 3/4, j = 2; trajectory d_t = (1/4, 3/16, 1/8), optimum-element marginals g_t = (1/3, 1/4, 3/16, 3/16), sum d_t = 9/16 = V_2(3/2) = rho_3(3/2). Sharp form step by step: t=0, d - g/eta = 1/4 - 2/9 = 1/36 = (1-1/eta)(g-h) = (1/3)(1/3 - 1/4); t=1, 1/48 = (1/3)(1/4 - 3/16); ... |
| thm:exact | Theorem 1 | 逐字见下方明细 §thm:exact（源 statements.md） | app:exact + app:validity | B-PASS-with-different-route; consistent=True, quantifiers=False; divergences: D1 LP 约束集与对偶支撑不同：路线一 eq:redlp 有四族 sum/pred/mono/cons 且逐 i，其证书支撑是 sum+pred+cons（lambda_mono 恒为 0）；路线二的 (P) 只有聚合的 sum+cons+mono，完全不用 pred，且 mono 乘子 w_t>0（t>=j）。两套证书本轮均独立符号复核通过（749 与 525 检查，0 失败），LP 值一致（HiGHS 浮点：sum+pred+mono 给 L_K，sum+cons+mono 与四族全上都给 rho_K）。台账 T6 的副产品句『下界证书中单调约束乘子恒为零』只对路线一成立。; D2 at ...; route-2 gaps: 一般 K 的 dual 可行性未闭合：逐 K 符号验证只覆盖 K=2..7（本轮独立复跑 749 检查 0 失败），任意 K 的统一论证是手写的 complementary slackness 反解，[H ... | C0a sympy identities for V_j (K=2..8): PASS; C0b V_j = min_i V_i on segment [K-j, K-j+1], breakpoints are the integers 2..K: PASS; C0c rho_K = 1/eta exactly when eta >= K: PASS; C1 own exact rational simplex on the full LP of code/reduced_lp.py equals min_j V_j: PASS; C2 exact primal-dual certificate at every optimum: PASS; C3 closed forms printed in the statement for K=2,3,4: PASS; C4 rerun results/N1_dual_certificate.py: PASS; C5 rerun results/N2_check.py: PASS; C6 cross-check against float sc ... | random 2400, structured 5, violations 0, worst Worst (tightest) D1 slack f(T)/OPT - rho_K(eta) = 269/3168 = 0.0849 at K=2, n=4, modular f, independent-surrogate mode,  ... | A_match=True; A_diffs: [无量词差异] 逐量词比对（K>=2；eta>=1；adversarial tie breaking；min over 0<=j<=K-1；段 [K-j,K-j+1] 上由 V_j 取到；j=0 时 V_0=1/eta on [K,infty)；分段点整数 2..K；rho_K=1/eta exactly when eta>=K；K=2,3,4 闭式及其分段）两张清单完全重合，故 A_match=true。statements.md 第 183-201 行、inputs/statement_ex ...; GAP: GAP-1（唯一真 GAP，E 表第 16 行）：n 量词在路线甲的 app:exact 内没有落点。上界构造固定 n=2K，下界 reduced LP 不含 n；从 n=2K 的实例到每个 n>=2K 的 rho_{n,K} 只由 ... | **[HAND-PROOF-UNREVIEWED]** | C 10 项 PASS（自写精确有理 simplex K=2..6 × 20 个 η 逐点 = min_j V_j；N1/N2 复跑；四族有效性）；D 2400 随机实例 0 违反 + 图 1 实例复核；A 逐字一致；B-PASS（不同路线：另一组对偶支撑）；E GAP-1：n 量词只靠 rem:exact-n（restriction + padding）[HAND-PROOF-UNREVIEWE ... | For every K >= 2, every eta >= 1 and every n >= 2K, the exact worst-case ratio of K-step predictive greedy under adversarial tie breaking, over all instances on n elements with f monotone submodular, f(empty) = 0, and f~ satisfying Definition 1 with product at most eta, is rho_K(eta) = min_{0 <= j <= K-1} V_j(eta), V_j = 1 - q^j (1 - (K-j)/(K eta)), q = (K-1) eta/((K-1) eta + 1); the minimum is V_j on eta in [K-j, K-j+1] (V_0 = 1/eta on [K, infinity)), the breakpoints are the integers 2, ..., K, and rho_K(eta) = 1/eta exactly when eta >= K. (The independence of n for n >= 2K rests on restricti ... | K = 3, eta = 3/2: k1 = 4, q = 3/4, (V_0, V_1, V_2) = (2/3, 7/12, 9/16), argmin j = 2, and eta = 3/2 lies in the segment [K-j, K-j+1] = [1, 2]. The own exact rational simplex on the full reduced LP returns 9/16 = 0.5625 = min_j V_j, and its primal-dual certificate verifies exactly. The printed K = 3  ... |
| cor:limit | Corollary | 逐字见下方明细 §cor:limit（源 statements.md） | app:asymptotics | B-PASS-with-different-route; consistent=True, quantifiers=False; divergences: D1 rho_K 极限的路径不同：路线一（app:asymptotics 第 1380-1391 行）直接展开 active branch V_{K-floor(eta)}，逐项算 j/k1 -> 1/eta 与 1-floor(eta)/(K eta) -> 1；路线二 Step 11 改用 squeeze，下界是它新增的一致上界 h_K(j) <= e^{-1/eta}（Step 7，路线一无对应步骤），上界是 U_K。结论相同; D2 单调性的正性证书不同：路线一用尾界 -log(1-1/x) <= 1/x+1/(2x^2)+1/(3x^2(x-1)) 加坐标变换 s=t/(1+t) 后 ...; route-2 gaps: A1（已由本判定闭合）追加读法：notation.md 未给 min_j V_j 的 j 范围，路线二取 {0,...,K}，仓库是 {0,...,K-1}。exact rational 复核 min_{ ... | C0 rerun results/H_B_asymptotic.py: PASS; C1 sympy limit L_K(eta) -> 1 - e^{-1/eta}: PASS; C2 sympy limit V_{K-floor(eta)}(eta) -> 1 - e^{-1/eta}: PASS; C3 sympy series rho_K = 1 - e^{-1/eta} + c(eta)/K + O(1/K^2): PASS; C3b exact bracketing of the 1/K^2 remainder: PASS; C4 monotonicity of rho_K in K, exact rationals: PASS; C5 monotonicity of L_K in K, exact rationals: PASS; C6 limit approached from above, exact: PASS; C7 closed-form consistency (conditional on thm:exact / T6): PASS | random 18000, structured 8, violations 0, worst Monotonicity: the largest (least negative) strict difference over D1+D2 is rho_{K+1} - rho_K = -6.378052e-08 at eta = 66 ... | A_match=False; A_diffs: D2 (U_K): 台账陈述行写 "L_K、ρ_K、U_K → 1−e^{−1/η}"，正文 corollary 环境（results.tex 523-529）只讲 L_K 与 ρ_K；U_K 在正文只出现在环境之后第 533 行，且只作为 1/K 系数，没有极限断言。; D3 (L_K 单调性): 正文有 "L_K is monotone in K"，台账 T9 卡（206-209 陈述行，以及全卡）完全没有 L_K 的单调子句；且正文的 monotone 没有方向，附录 1378-1380  ...; GAP: GAP-1（K 的定义域）：陈述、台账 T9 卡、路线甲三处都没写 K 的下端。ρ_K 闭式只对 K ≥ 2 成立（thm:exact，results.tex 192）；1 ≤ η < 2 时 ⌊η⌋=1，平台子句只覆盖 K=1、 ... | **[HAND-PROOF-UNREVIEWED]** | C 9 项 PASS（H_B 复跑；sympy 极限与级数；精确差分 K ≤ 200）；D 18000 个 (K,η) 点 0 违反；B-PASS（不同路线）；E GAP：K 下端与 ρ_1 的出处、n 量词、'monotone' 无方向。全部 conditional on thm:exact。 | Fix eta >= 1. As K -> infinity, L_K(eta) increases to 1 - e^{-1/eta} and rho_K(eta) -> 1 - e^{-1/eta}. For K >= 2, rho_K(eta) is non-increasing in K: it equals 1/eta for 2 <= K <= floor(eta) and is strictly decreasing in K for K >= max{2, floor(eta)}, so the limit is approached from above. Quantitatively rho_K(eta) = 1 - e^{-1/eta} + c(eta)/K + O(1/K^2) with c(eta) = e^{-1/eta}(2 eta - 1)/(2 eta^2). (Every statement about rho_K is conditional on Theorem thm:exact and on n >= 2K.) | K = 3, eta = 3/2: m = floor(eta) = 1, k_1 = 4, q = 3/4, j* = 2, so rho_3 = V_2 = 9/16 = 0.5625, with L_3 = 386/729 = 0.529492 and U_3 = 37/64 = 0.578125 (sandwich holds). rho_4 = 1447/2662 = 0.543576, so rho_4 - rho_3 = -403/21296 = -0.018924 < 0 (strict decrease, no plateau since floor(eta) = 1). T ... |
| thm:linear-exact | Theorem 2 | 逐字见下方明细 §thm:linear-exact（源 statements.md） | app:greedybudget + results/J6/linear_exact.md | B-GAP (route two incomplete); consistent=False, quantifiers=False; divergences: D1 (substantive): route two's 1-blind condition (*) has no size cap ("for all s"), route one requires small-set indistinguishability only on /S/ <= K with /S cap O/ <= 1 and states explicitly that the predictor leaks on larger sets (K=3, eta=3/2: H(6,0)=61/48 vs H(5,1)=4/3). My count-grid LP shows r ...; route-2 gaps: GAP-1 (self-reported, [FAILED]): R1's hand proof misses the comparison between the two gain chains;  ... | C1 rerun results/Q4_gpt_check.py (13 identities + 159-config battery): PASS; C2 rerun results/Q4_symbolic_ineq.py (34 branch inequalities): PASS; C3 rerun results/Q4_indep_check.py (111 configs): PASS; C4 counting chain in exact rationals (11 sub-checks): PASS; C5 smallest n with chain total < 1, both readings, exact: PASS; C6 randomized clause eps_n = K^2/n + K^5/(2n): PASS; C7 own re-implementation of the double-residual family, count-grid legality on the D configurations: PASS | random 500, structured 40, violations 0, worst Worst slack rho_K - ratio = 0 (exactly zero, never negative) across all 56 structured cases and all 500 random strategie ... | A_match=False; A_diffs: D1 normalization: ledger states 'f 单调 submodular 归一化' (normalized); the results.tex environment says only 'monotone submodular f', f(emptyset)=0 is inherited from model.tex line 9 and never written in the statement; D2 error-factor wording: ledger sa ...; GAP: GAP-1: the domain of the inf in the sup-inf identity is written nowhere. results.tex 756-789 and THEOREM_LEDGER.md  ... | **[HAND-PROOF-UNREVIEWED]** | C 7 项 PASS（Q4 三脚本复跑 13 恒等式/159 电池/34 分支/111 组；计数链精确；自写重实现）；D 500 随机策略 + 56 结构化 0 违反；B-GAP：盲审走全大小 size-only 路线撞上强制超额，未复现 small-set-only 机制，判定人复核路线一正确；E GAP：sup-inf 的实例类未命名、归一化与'single-element'措辞。 | Let K >= 2, eta > 1 and n >= 4K^5. Let A_lin be the class of deterministic algorithms that make at most nK queries to f~, each on a set of size at most K, and output a set of size at most K; predictive greedy belongs to it. For every A in A_lin and every eta_u, eta_o > 0 with eta_u eta_o = eta there is an instance on n elements with f monotone submodular, f(empty) = f~(empty) = 0, whose smallest admissible factors are exactly (eta_u, eta_o), on which f(T)/OPT <= rho_K(eta). Hence, over instances on n elements with monotone submodular normalized f and error product at most eta, sup_{A in A_lin} ... | K=3, eta=3/2: k1 = 4, q = 3/4, j = 2, Q = 9/16, delta = 1/8, C = 4/3, Hhat = (0, 1/3, 7/12, 37/48), rho_3(3/2) = 9/16. F(3,0) = 9/16 = rho_3 and F(0,3) = 1 = OPT; the leak above size K is H(6,0) = 61/48 versus H(5,1) = 4/3. n >= 4K^5 = 972; the loose chain first gives failure probability < 1 at n =  ... |
| thm:hardness | Theorem 3 | 逐字见下方明细 §thm:hardness（源 statements.md） | app:hardness | B-GAP (route two incomplete); consistent=False, quantifiers=False; divergences: D1 window 门限：route2 取 W_tau={/S∩O*/<=tau-1}，route1 的 G_O oblivious 分支是 y<=tau、bad event 是 /S∩O/>tau。D2/D3 全部由此派生。; D2 门槛：route2 自己的充分条件是 n>=4K^{2tau}（c=0,tau=1 时与 statement 的 4K^2 相同）；route1 在 n>=4K^{c+2} 下用 level-(tau+1) 计数得总失败概率 <=9/32（本轮 c=0..3、K<=29 逐点精确复算最坏为 9/32）。route1 条件严格更弱，两者不矛盾。; D3 eps_n ...; route-2 gaps: G1 (=GAP-6, [FAILED])：显式硬族 f 未构造，route2 自称最大缺口。route1 给出 F_O/G_O，本轮在 (n,K,tau,eta)=(6,3,1,3/2),(7,3, ... | C1 rerun results/J2_core_oracles.py: PASS; C2 rerun results/H3_j2_recheck.py: PASS; C3 exact error product theta*A*B = (theta K - 1)/(K - tau): PASS; C4 exact rational table min{H_{K,tau}(eta), 1/eta}: PASS; C5 the tau=2, eta=3/2 column expectation: PASS; C6 identity H_{K,1}(eta) = U_K(eta): PASS; C7 limit H_{K,tau}(eta) -> 1 - e^{-1/eta}: PASS; C8 calibration thetabar = (eta(K-tau)+1)/K: PASS | random 2000, structured 6, violations 0, worst No violation and no slack on any equality: the error product eta_u*eta_o = rmax/rmin, the value F(K,0)/F(0,K) = H_{K,tau ... | A_match=False; A_diffs: D1 tau 的整数 c 等式：正文 "tau=ceil(c)+1, which equals c+1 at integer c"，台账陈述行只有 "τ=⌈c⌉+1"；该半句承重（app:hardness 第 1603 至 1605 行的整数性消费点）; D2 K 与 n 的整数性：正文 "Let the integers K>tau and n>=4K^{c+2}"，台账陈述行不写（靠 model.tex 第 15 行继承）; D3 thetabar 的定义位置：台账把 θ̄=(η(K−τ)+ ...; GAP: GAP(陈述层) 1：随机版的期望没有写明对什么取。路线甲（app:hardness 第 1639、1652 至 1657 行）取的是算法自身 random seed 与均匀 O 的两次平均，最终给出固定实例上关于 seed 的期 ... | **[HAND-PROOF-UNREVIEWED]** | C 8 项 PASS（J2/H3 复跑；非 binding 表：K=3,4 τ=2 η=3/2 不 binding，K ≥ 5 binding；H_{K,1}=U_K；极限）；D 2000 随机参数 0 违反；B-GAP：路线二未构造硬族且其 union bound 需 n ≥ 4K^{2τ}，判定人精确复算路线一在 n ≥ 4K^{c+2} 下失败概率 ≤ 9/32；E GAP：随机版期望对什么 ... | Let c >= 0 be real, tau = ceil(c) + 1, let K > tau and n >= 4K^{c+2} be integers, and let eta > 1 satisfy eta >= (K-1)/(K-tau). For every deterministic algorithm making at most n^c queries to f~, each on a set of size at most K, and outputting a set of size at most K, there is an instance with f monotone submodular, f(empty) = f~(empty) = 0, whose smallest admissible error factors have product exactly eta, on which f(T)/OPT <= H_{K,tau}(eta) = 1 - (1 - 1/(eta(K-tau)+1))^K; any prescribed split is realized by rescaling. For every randomized algorithm with the same budget there is a fixed instan ... | thetabar = (3/2*2+1)/3 = 4/3, a = 1 - 1/(thetabar*K) = 3/4, A = a*K/(K-1) = 9/8, B = a^0 = 1, thetabar*A*B = 3/2 = eta (eta_o^2 = 27/16, eta_u^2 = 4/3). H_{3,1}(3/2) = 1 - (3/4)^3 = 37/64 = 0.578125 = U_3(3/2) = L_3(4/3), and this is exactly the ratio Fbar(3,0)/Fbar(0,3) attained by the balanced out ... |
| thm:linear-anysize | Proposition (J7) | 逐字见下方明细 §thm:linear-anysize（源 statements.md） | app:hardness-anysize + results/J7/linear_anysize.md | B-PASS-with-different-route; consistent=False, quantifiers=False; divergences: j 约定（实质差异，改变 W_K 的取值）：route one 用显式公式 j = max{0, min{K-1, K+1-ceil(eta)}}；route two 用「rho_K = min_j V_j 的 argmin，并列取最小 j」。template 在并列时未定义，两读法都合规。二者恰在整数 eta（2 <= eta <= K）上不同，且恒有 j_route1 = j_route2 + 1；此时 rho_K 相同但 W_K 不同，且 W_route1 < W_route2 严格。例 K=3, eta=2：W_route1 = 2003/4275，W_route2 = 403/855 ...; route-2 gaps: [FAILED] 步骤 D5 第 1 点的句子「alpha_{K+1} = 1」是错的。route two 只证明了在第 3 节的 hard family 上 n = K+1 时算法可达 ratio 1 ... | C1 rerun results/J7_symbolic.py: PASS; C2 rerun results/J7_grid_check.py: PASS; C3 rerun results/J7_fragment_checks.py: PASS; C4 rerun results/J7_bound18_check.py: PASS; C5 F3 counterexample reproduced independently (K = 3, eta = 667/500): PASS; C6 running example K = 3, eta = 3/2: PASS; C7 own count-grid legality battery on the three D configurations: PASS; C8 own exact sweep of (5),(6),(7),(8),(17),(18) on 99 configurations: PASS; C9 sympy cross-check of the d-identities (7a), (7b), (8): PASS; ... | random 300, structured 21, violations 0, worst "Leak-free regime (n >= K + t*): worst slack ratio - W_K(eta) = 0, attained everywhere, i.e. the ceiling W_K is met with ... | A_match=False; A_diffs: D0 environment name: results.tex 884 uses \begin{proposition}, while the ledger card title and results/V11/statements.md line 319 metadata plus the LaTeX blocks in statements.md and inputs/statement_linear_anysize.md all use \begin{theorem}; apart fr ...; GAP: GAP-1 existence of the limit: the statement defines alpha_lin as the limit as n -> infinity, but the route-one mate ... | **[HAND-PROOF-UNREVIEWED]** | C 9 项 PASS（J7 四脚本复跑 148/99/F3 反例/(18)；自写电池；n < K+t* 反向 greedy 恰达 1 复现）；D 300 随机任意大小策略 0 违反；B-PASS-with-different-route 但路线二含一句错误（α_{K+1} = 1，判定人反驳）且整数 η 处 j 约定不同（路线一的 j 给更小的 W_K，两者都合法）；E GAP-1：'limit' ... | Let K >= 3, eta > 1 and c >= 1, and for each n let alpha_n denote the optimal worst-case ratio of deterministic algorithms that make at most c n K queries to f~ of arbitrary size and output a set of size at most K, over instances on n elements with monotone submodular normalized f and error product at most eta. Then rho_K(eta) <= alpha_n for every n >= 2K, and limsup_{n -> infinity} alpha_n <= min{1/eta, W_K(eta)}, where W_K(eta) (the value of the explicit family of the appendix, with j = max{0, min{K-1, K+1-ceil(eta)}} and the Psi truncation rule) satisfies 0 < W_K(eta) - rho_K(eta) < 1/(K(e^ ... | "K = 3, eta = 3/2: j = 2, m = 4 (Psi rule), t* = 6, q = 3/4, nu = 3, Q = 9/16, B_m = 116, d = 13/58, D = 117/928, C = 4/3.\nW_3(3/2) = F(3,0) = 523/928 = 9/16 + 1/928 (0.563577586), rho_3(3/2) = 9/16 (0.5625), gap = 1/928 (1.078e-3), and 523/928 < 2/3 = 1/eta.\nD at this eta: K + t* = 9, so n = 8 is ... |
| J8 ProbeLottery | Proposition (J8) | 逐字见下方明细 §J8 ProbeLottery（源 statements.md） | GAP: proof file undelivered; results/J8/J8_claude_spotcheck.py | B-MISSING (no route one); consistent=False, quantifiers=False; divergences: D1 路线一不存在：results/J8/probe_lottery.md 与不等式 (3),(8)-(12) 未交付，仓库只有 J8_claude_spotcheck.py + run.log + HANDOFF 2026-09-18 section 4 的一行状态，criterion B 的对偶证书无法组装; D2 紧实例不同：路线一用 J6 double-residual 族 (n=6,8,12,20，/C/=5,7,11,19，r=4，max query size 5) 取到 3/5+1/2048；路线二自造 n=4 coverage 实例 (/C/=2，r=2，max query s ...; route-2 gaps: G1 主缺口，情形 II-b 未闭合 [FAILED]：需要 o_1,o_2 在 pool C 内且 eps < 4.0945e-6 时四轮 extension 至少一轮取到某个 o_i。挡路必要条件 (3/ ... | C1 tight instance (K=2, eta=3/2 double-residual family, j=1), n in {6,8,12,20} plus 7,9,10,11: PASS; C1b 紧实例合法性（f 单调 submodular + band）: PASS; C2 随机合法实例（K=2, eta=3/2, n=8..12，三族）: PASS; C3 结构化案例（eta=1 的 n=4,5；紧实例 n=6..12；E4 的两个实例族在 K=2, eta=3/2）: PASS; C4 算法 contract（输出集大小 2、总质量 1、queries <= 9n、被查询集合大小 <= 5）: PASS; C5 复跑 results/J8/J8_claude_spotcheck.py（子进程，不修改不 import）: PASS; G1 路线甲：不等式 (3)、(8)-(12) 的 LP 对偶证书: GAP | random 2100, structured 8, violations 0, worst 全局最差比值 6149/10240 = 3/5 + 1/2048 ≈ 0.60048828，来自紧实例本身（n = 8，B 优先的 tie order，anchors = [0,1,6,2,3]，E = 6149/10240，OPT = 1 ... | A_match=False; A_diffs: D0 正文缺失：paper/sections/results.tex 无任何 ProbeLottery environment（全 paper/ 目录检索 Probe、lottery 零命中），正文侧量词集合为空集; D1 台账缺失：THEOREM_LEDGER.md 无 J8 卡（卡号只有 T0 至 T15，全文检索 Probe/lottery/9n/400000/2048 零命中），台账侧量词集合为空集；两个列表不可能重合，故 A_match = false; D2 矩阵陈述比 HANDOF ...; GAP: eta = 3/2 固定：无为何 3/2 的论证，只有两族有限实例; error at most eta：Definition 1 band 的全称量词如何进入不等式无出处; 拆分 (eta_u, eta_o) 任意：只覆盖 et ... | **[VERIFIED-ORACLE-ONLY]** | C：紧实例恰 3/5 + 1/2048（n = 6..12）、2100 个随机合法实例 0 违反且最差恰为紧实例、算法 contract（≤ 9n 次、/S/ ≤ 5、输出 2-集）全过；路线一缺失（证明文件未送达，对偶证书 GAP）；盲审 PARTIAL（II-b 一格差 4.1e−6 未闭合）；台账无卡、正文无环境。不可原样写进正文。 | Cannot be written into the paper on the repository's evidence: the proof is undelivered. Claim as delivered: for K = 2 and eta = 3/2, the randomized algorithm ProbeLottery (as implemented in results/J8/J8_claude_spotcheck.py) makes at most 9n queries, each on a set of size at most 5, outputs a 2-set, and on every instance with f monotone submodular, f(empty) = 0, and f~ satisfying Definition 1 with product 3/2 satisfies E_seed[f(T)] >= (3/5 + 1/400000) OPT; hence the query-size restriction of Theorem thm:linear-exact is necessary for randomized algorithms with budget (9/2) n K. Evidence: tight ... | K = 3、eta = 3/2 不在本命题范围内（命题只声称 K = 2，K >= 3 与确定性版本仍 [OPEN]），下面是对照值。 k1 = 4，q = 3/4，V_0 = 2/3、V_1 = 7/12、V_2 = 9/16，故 rho_3(3/2) = 9/16 = 0.5625，信息价格 1/eta = 2/3。 对应 K = 2：rho_2(3/2) = 3/5，ProbeLottery 在紧实例取 6149/10240 = 3/5 + 1/2048，声称 bound 为 3/5 + 1/400000。 |

## 逐条明细（主表各列的未截断版本；陈述原文逐字取自 statements.md）

### prop:necessity (alias prop:nobound) (Prop 1) — 最终标签 **[HAND-PROOF-UNREVIEWED]**

**陈述原文**

#### T1 prop:nobound (paper label prop:necessity)

- 正文环境: `proposition`, label `prop:necessity`
- 台账卡: ## T1 prop:nobound — 无误差假设则无常数保证

##### 台账陈述（逐字）

- 陈述（M1 量词校正）：不假设 η 上界时，对任意**确定性**算法、任意 n ≥ 2K，存在 (f,f̃) 使输出 T 满足
  f(T) ≤ K/(n−K)·f(O*)。

##### 正文陈述（逐字，LaTeX）

```latex
\begin{proposition}[No bound, no guarantee]\label{prop:necessity}
If no upper bound on $\eta$ is assumed, then for every deterministic
algorithm with
arbitrary query access to $\tilde f$ and every $n\ge2K$ there are pairs
$(f,\tilde f)$ on which the output $T$ satisfies
$f(T)\le\tfrac{K}{n-K}\,f(O^{\ast})$.  Consequently no constant worst-case
ratio is achievable without an error assumption.
\end{proposition}
```

**路线一位置**: app:necessity + appendix_model_proofs.tex (unwired)

**B 路线二比对**: B-PASS; consistent=True, quantifiers=False; divergences: D1 构造常数：route one 内部即有两个构造，appendix_proofs.tex app:necessity 用 gamma=K^2/(n(n-K))，appendix_model_proofs.tex 用 delta=K/(n-K)；route two 的 deterministic 段取 delta（= 甲2），randomized 段取 gamma（= 甲1）。三者都到达 statement 的界；gamma <= K/(n-K) 等价于 K/n <= 1，全参数成立 [VERIFIED-SYMBOLIC]，故甲1 的 deterministic 结论更强一个因子 K/n，但 ...; route-2 gaps: G1 Step 6-7（deterministic + arbitrary query access 导致 transcript 与 A 无关、输出为固定集合）[HAND-PROOF-UNREVIEWED]，无 oracle 可检验。route one 两个文件用的是同一句话，故这不是 route two 相对 route one 的缺口；route two 的缓解（Step 8-10 与全部脚本对一切 /T/<=K 取全称）有效。; G2 加入的假设 /T/ <= K：statement 原文只写 the output T。route two 按 assumptions.md 的 cardi ...

**C oracle**: C0 symbolic relations between the two constructions (sympy): PASS; C1 instance validity of both constructions (f(empty)=0, monotone, submodular): PASS; C2 Definition 1 band; smallest admissible factors eta_u=1, eta_o=1/delta, both attained: PASS; C3 OPT = f(O) = K: PASS; C4/C5 predictive greedy (adversarial ties) and exhaustive argmax of ftilde over K-sets (adversarial ties): PASS; C6 arbitrary fixed output T with |T| <= K: PASS; C7 existence of a disjoint K-set O for every output when n >= 2K: PASS; C8 n = 2K-1 exhibit (where the argument fails): PASS; C9 (extra) randomized averaging step of app:necessity with gamma: PASS; C10 running example K = 3, eta = 3/2: PASS; Quantifier 'every deterministic algorithm with arbitrary query access': GAP

**D 反例搜索**: random 2400, structured 4, violations 0, worst worst slack = 0 (bound attained with equality), reached in 1502 of 2400 trials, e.g. kind=rule_on_answers, K=1, n=11, /T ...

**E 量词审计**: A_match=False; A_diffs: D1: 形容词 'arbitrary query access to $\tilde f$' 在正文 prop:necessity 环境内修饰被全称的算法，台账 T1 把它放在陈述字段之外的独立'前提'字段；作用范围相同，陈述文本不重合。; D2: 正文第二句 'Consequently no constant worst-case ratio is achievable without an error assumption.' 不在台账 T1 的陈述字段里，只以中文出现在卡标题'无误差假设则 ...; GAP: GAP-1（陈述层）：/T/ ≤ K 未写，正文与台账都只写 'the output T'；字面上若允许 /T/ > K，取 T = N 即得 f(T) > f(O*)，命题不成立。证明里两份路线一材料都用到该条件。; GAP-2（陈述层）：第二句 'no constant worst-case ratio' 的量词（固定 K、n→∞，或'对任意 δ ∈ (0,1]'）未写；证明里有（appendix_proofs.tex 'Letting $n\to\infty$ with $K$ fixed'）。; GAP-3（陈述层）：pair 满足'除 η 上界外全部模型假设'的措辞未写，HANDOF ...

**裁定理由**: C 11 项 PASS（160 实例精确穷举、18240 个固定输出、两个构造）；D 2400 随机算法 0 违反；B-PASS（路线二加了 |T| ≤ K 读法）；E GAP：|T| ≤ K、'no constant' 的量词、addendum B.9 措辞未落实、query 模型未定义。GAP 全是陈述层措辞，证明无缺口。

**可写进正文的精确表述**: Let K >= 1 and n >= 2K. For every deterministic algorithm with arbitrary query access to the surrogate whose output T has |T| <= K, there is a pair (f, f~) with f monotone submodular, f(empty) = f~(empty) = 0, satisfying every assumption of Section 2 except a bound on eta (its error is finite, eta = (n-K)/K), on which f(T) <= (K/(n-K)) OPT. Consequently, for fixed K, no worst-case ratio bounded away from 0 uniformly in n holds without a bound on eta.

**K=3, η=3/2 走读**: K = 3, delta = 1/eta = 2/3, O = {0,1,2}, T = {3,4,5}: f(O) = 3 = OPT, f(T) = 3 * 2/3 = 2, ratio 2/3 = 1/eta, with eta_u = 1 and eta_o = 3/2 both attained. n = 6: statement constant K/(n-K) = 1; n = 7: 3/4. Both are >= 2/3, so f(T) <= K/(n-K) * OPT holds. n = 8: 3/5 < 2/3 and n = 12: 1/3 < 2/3, so a fixed eta = 3/2 instance no longer reaches the statement constant; there the statement uses its own delta = K/(n-K), i.e. eta = (n-K)/K.

### prop:valueacc (Prop 2) — 最终标签 **[HAND-PROOF-UNREVIEWED]**

**陈述原文**

#### T2 prop:valueacc

- 正文环境: `proposition`, label `prop:valueacc`
- 台账卡: ## T2 prop:valueacc — value accuracy 既不充分也不必要（H1 恢复；2026-09-18 方案二改写，待验证）

##### 台账陈述（逐字）

- 陈述（方案二）：(i) ∀ε∈(0,1) 存在单调 submodular f 与 value-accurate at level ε 的 f̃，某处
  d̃_e(S)=0 而 d_e(S)>0，故 Definition 1 的 (η_u,η_o) 无限，value accuracy 单独不给任何 L_K(η) 界；
  (ii) ∀M>0、∀不恒零的单调 submodular f，f̃=(1+M)f 在任何 ε<M 下不 value-accurate，但
  Definition 1 以 η_u=1/(1+M)、η_o=1+M 成立，**全局 η=1**（且 predictive greedy 每步选真增益最大者，
  η^sel=1）；
  (iii) 任意误差 (η_u,η_o)、η=η_uη_o 的 f̃：沿链求和得 f(S)/η_u ≤ f̃(S) ≤ η_o f(S) ∀S；取
  c = 2η_u/(η+1) 则 (1−ε)f ≤ c f̃ ≤ (1+ε)f，ε=(η−1)/(η+1) ∈ [0,1)，即**存在正缩放使 f̃
  value-accurate at level (η−1)/(η+1)**；无 η_o<2 前提；只用 f 单调与 f(∅)=f̃(∅)=0，不用 submodularity。

##### 正文陈述（逐字，LaTeX）

```latex
\begin{proposition}[Value accuracy is neither sufficient nor necessary]
\label{prop:valueacc}\mbox{}
\begin{itemize}
\item[(i)] For every $\varepsilon\in(0,1)$ there are a monotone submodular
$f$ and a predictor $\tilde f$, value-accurate at level $\varepsilon$, with
$\tilde d_e(S)=0$ at a pair where $d_e(S)>0$; hence no
$(\eta_u,\eta_o)$ of Definition~\ref{def:eta} is finite for $\tilde f$, and
no bound of the form $L_K(\eta)$ follows from value accuracy alone.
\item[(ii)] For every $M>0$ and every monotone submodular $f$ not
identically zero, the predictor $\tilde f=(1+M)f$ fails value accuracy at
every level $\varepsilon<M$, yet predictive greedy on $\tilde f$ picks at
every state an element of maximum true gain, so $\etasel=1$ and the full
guarantee of Proposition~\ref{prop:guarantee} applies to the run.
\item[(iii)] Conversely, every predictor with error at most
$(\eta_u,\eta_o)$ for a nonnegative $f$ is value-accurate at level
$\max\{1-1/\eta_u,\ \eta_o-1\}$, provided that this value is below $1$
(that is, $\eta_o<2$), so that it lies in the domain of the definition
above.
\end{itemize}
\end{proposition}
```

#### T2 方案二改写后的陈述（2026-09-18，台账已改，正文未改；矩阵以此为准）

Convention B of Definition 1: $\eta_u,\eta_o>0$, $\eta=\eta_u\eta_o\ge1$, and for all $S$ and $e\notin S$:
$d_e(S)/\eta_u\le\tilde d_e(S)\le\eta_o\,d_e(S)$ (so $d_e(S)=0$ forces $\tilde d_e(S)=0$).
Value accuracy at level $\varepsilon\in(0,1)$ (Hassidim--Singer): $(1-\varepsilon)f(S)\le\tilde f(S)\le(1+\varepsilon)f(S)$ for every $S$.

**Proposition (Value accuracy is neither sufficient nor necessary for predictive greedy).**
(i) For every $\varepsilon\in(0,1)$ there are a monotone submodular $f$ with $f(\emptyset)=0$ and a
predictor $\tilde f$ with $\tilde f(\emptyset)=0$, value-accurate at level $\varepsilon$, with
$\tilde d_e(S)=0$ at a pair $(S,e)$ where $d_e(S)>0$; hence no finite $(\eta_u,\eta_o)$ of Definition 1
exists for $\tilde f$, and no bound of the form $L_K(\eta)$ follows from value accuracy alone.
(ii) For every $M>0$ and every monotone submodular $f$ not identically zero, the predictor
$\tilde f=(1+M)f$ fails value accuracy at every level $\varepsilon<M$, yet Definition 1 holds with
$\eta_u=1/(1+M)$ and $\eta_o=1+M$, so its global error is $\eta=1$; predictive greedy on $\tilde f$
picks at every state an element of maximum true gain ($\eta^{\mathrm{sel}}=1$).
(iii) Let $\tilde f$ have error $(\eta_u,\eta_o)$ with $\eta=\eta_u\eta_o$ for a monotone $f$ with
$f(\emptyset)=\tilde f(\emptyset)=0$. Then $f(S)/\eta_u\le\tilde f(S)\le\eta_o f(S)$ for every $S$, and
with $c=2\eta_u/(\eta+1)$ and $\varepsilon=(\eta-1)/(\eta+1)\in[0,1)$ the rescaled predictor $c\tilde f$
is value-accurate at level $\varepsilon$: $(1-\varepsilon)f(S)\le c\tilde f(S)\le(1+\varepsilon)f(S)$ for
all $S$. No submodularity of $f$ is used in (iii).

**路线一位置**: appendix_model_proofs.tex (convention B) + app:valueacc (old)

**B 路线二比对**: B-PASS; consistent=True, quantifiers=False; divergences: D1 (i) 的 n>=2：statement 与 route one 都未写，route two 显式补为前提并给出 n=1 时 (i) 为假的一行论证（value accuracy 逼出 eta<=(1+eps)/(1-eps) 有限）。两条路线的构造实际都在 n=2 上，属共有隐含前提。[HAND-PROOF-UNREVIEWED]; D2 (i) 末句的 L_K(eta) 分句：convention-B 证明 appendix_model_proofs.tex 停在 eta=infinity，没有写这一句；旧附录 app:valueacc 有「every bound of the fo ...; route-2 gaps: R2-G1 (i) 末句只证成非蕴含（不存在有限 eta），没有证成「ratio 可低于任意给定 L_K(eta)」；Instance B 族在 eps=1/5,K=2 的最坏 ratio 2/3 高于 L_2(3/2)=5/9。裁定：这是正确的保守读法，与台账 T2 禁止声称条及 HANDOFF_ADDENDUM §B5 要求一致，不是缺陷。; R2-G2 [CONJECTURE] 未闭合：value accuracy at level eps 本身是否蕴含某个 phi(eps,K)>0 的乘性保证。route two 的 K 步推广显示 value band 总宽度 2*eps*f(S)  ...

**C oracle**: C1 (i) two-element construction, eps in {1/10, 1/2, 9/10}, base n=2: PASS; C1 (i) padded to n=6 with 4 zero-gain elements: PASS; C1b cross-check of the OLD appendix app:valueacc (i) instance: PASS; C2a (ii) sympy in M: smallest factors and eta=1: PASS; C2b (ii) numeric exact recheck, 200 random monotone submodular f with random rational M: PASS; C3a (iii) sympy identities c/eta_u = 1-eps and c*eta_o = 1+eps: PASS; C3b (iii) domain eps in [0,1): PASS; C4 (iii) 2200 random LEGAL surrogates, actual smallest factors: PASS; C4b (iii) on monotone f that FAILS submodularity (the statement's 'no submodularity is used in (iii)'): PASS; C5a structured: eta = 1 (ftilde = c0 f): PASS; C5b structured: very large eta: PASS; C5c structured: f with zero-gain elements: PASS; C6 scaling invariance of eta and of the (iii) constant: PASS; C7a old-convention comparison (appendix_proofs.tex app:valueacc): PASS; C7b rerun of the existing repo script results/M1_checks.py: PASS; RE running example K = 3, eta = 3/2: PASS; (i) closing clause 'no bound of the form L_K(eta) follows from value accuracy alone': GAP; Prior 96-surrogate oracle referenced in HANDOFF_ADDENDUM section B item 10: SKIPPED

**D 反例搜索**: random 6597, structured 7, violations 0, worst worst slack = 0 (tight, never negative). Over all 2200 legal surrogates x 57840 subsets, min over S of min(c*ftilde(S) - ...

**E 量词审计**: A_match=False; A_diffs: D1 标题限定: 台账按 addendum §B 第5条改成 "Value accuracy is neither sufficient nor necessary for predictive greedy"; 正文 results.tex 的 proposition 标题仍是无限定版 "…neither sufficient nor necessary"。; D2 (ii) 的 η 结论: 台账写 "Definition 1 以 η_u=1/(1+M)、η_o=1+M 成立, 全局 η=1" ...; GAP: G1 陈述层: (i) 缺 n ≥ 2。n=1 时 (i) 为假（唯一 pair 是 (∅,e), value accuracy 给 f̃({e}) ≥ (1−ε)f({e})>0, 于是 η ≤ (1+ε)/(1−ε) 有限）。甲 只给向上 padding, 乙 连 padding 句都没有。; G2 甲 (i) 缺 "no bound of the form L_K(η) follows" 那一句（只有乙有）。; G3 甲 (ii) 未声明 f 不恒零, 只用 "For every nonempty S with f(S)>0" 绕过; f ≡ 0 时 (ii) 前半句失效。; G4 甲  ...

**裁定理由**: C 16 项 PASS（含 2200 个合法 surrogate × 57840 子集的 (iii)）；D 6597 次 0 违反；B-PASS；E GAP：(i) 缺 n ≥ 2，(ii) 缺 f 不恒零，正文仍旧约定。(iii) 单独看五项全过且 addendum 记 Cici 已读，可标 [HAND-PROOF-REVIEWED]+[VERIFIED-EXHAUSTIVE]。

**可写进正文的精确表述**: (i) For every eps in (0,1) and every n >= 2 there are a monotone submodular f with f(empty) = 0 and a surrogate f~ with f~(empty) = 0, value-accurate at level eps, whose marginal gain vanishes at a pair (S, e) with d_e(S) > 0; hence no finite (eta_u, eta_o) of Definition 1 exists for f~, and value accuracy alone yields no bound of the form L_K(eta). (ii) For every M > 0 and every monotone submodular f not identically zero, f~ = (1+M) f is value-accurate at no level eps < M, yet satisfies Definition 1 with (eta_u, eta_o) = (1/(1+M), 1+M), so eta = 1, and predictive greedy on f~ picks at every step an element of maximum true gain. (iii) If f~ satisfies Definition 1 with (eta_u, eta_o), eta = eta_u eta_o, for a monotone f with f(empty) = f~(empty) = 0, then f(S)/eta_u <= f~(S) <= eta_o f(S) for every S, and c f~ with c = 2 eta_u/(eta+1) is value-accurate at level (eta-1)/(eta+1); submodularity is not used.

**K=3, η=3/2 走读**: K = 3, eta = 3/2: (eta_u, eta_o) = (1, 3/2), eps = (eta-1)/(eta+1) = 1/5, c = 2 eta_u/(eta+1) = 4/5. Modular instance n = 4, weights (1,1,1,1), predicted factors (1, 3/2, 1, 3/2); on the 3-set S = {0,1,2}: f(S) = 3, ftilde(S) = 7/2, c ftilde(S) = 14/5. Band: (1-eps) f(S) = 12/5 <= 14/5 <= 18/5 = (1+eps) f(S); and (1-eps)/(1+eps) = 2/3 = 1/eta.

### thm:ceiling (Proposition (upper bound for unbounded queries)) — 最终标签 **[HAND-PROOF-UNREVIEWED]**

**陈述原文**

#### T8 thm:ceiling

- 正文环境: `theorem`, label `thm:ceiling`
- 台账卡: ## T8 thm:ceiling — 确定性天花板，统一到全部 ground-set 大小（J5H2 重写）

##### 台账陈述（逐字）

- 统一陈述（来源 J5 套 A，results/J5_hardcore/J5_ceiling_proof.md）：2 ≤ K ≤ n，确定性、任意查询
  次数与大小、输出 ≤ K。minimax 值 **C*_{n,K}(η) = K/(K+(η−1)·min{K, n−K})**
  （K ≤ n ≤ 2K 时 = K/((2K−n)+(n−K)η)，n ≥ 2K 时 = 1/η）。
  上界侧：对每个确定性算法存在实例（f̃ = b|S| 线性预测 + modular 高低权 f，任意拆分 (η_u,η_o)
  实际误差两端恰取到；n=K 时输出全集比值 1，端点校准用混合高低权）。
  下界侧（**达到**）：穷举 argmax_{|T|=K} f̃ 在每个实例上 ≥ C*，且有更强的**逐实例式**
  f(S)/f(O) ≥ K/(K+(η−1)|O∖S|)（重叠越多越强，无最小重叠假设）。

##### 正文陈述（逐字，LaTeX）

```latex
\begin{theorem}[Deterministic ceiling, all ground-set sizes]
\label{thm:ceiling}
Let $2\le K\le n$.  For every deterministic algorithm with arbitrary query
access to $\tilde f$ and output of size at most $K$, and every
$\eta_u,\eta_o\ge1$, there is a pair $(f,\tilde f)$ with error exactly
$(\eta_u,\eta_o)$ on which the output $T$ satisfies
$f(T)\le C^{*}_{n,K}(\eta)\,f(O^{\ast})$, where
\[
  C^{*}_{n,K}(\eta)\;=\;\frac{K}{K+(\eta-1)\min\{K,\,n-K\}}
  \;=\;\begin{cases}
    \dfrac{K}{(2K-n)+(n-K)\eta}, & K\le n\le2K,\\[6pt]
    1/\eta, & n\ge2K.
  \end{cases}
\]
Conversely, a set $S$ maximizing $\tilde f$ over all $K$-subsets satisfies,
on every instance and for every optimal $K$-set $O^{\ast}$,
\[
  f(S)\;\ge\;\frac{K}{K+(\eta-1)\,|O^{\ast}\setminus S|}\,f(O^{\ast})
  \;\ge\;C^{*}_{n,K}(\eta)\,f(O^{\ast}),
\]
so exhaustive search over predicted values attains the ceiling for every
$n$.
\end{theorem}
```

##### TASKS11 要求的拆分读法（同一陈述，两个 n 区间）

- n >= 2K（Proposition 读法）: C*_{n,K}(eta) = 1/eta；对手侧对每个确定性算法存在实例使 f(T) <= f(O*)/eta；达到侧穷举 argmax f~ 满足 f(S) >= f(O*)/eta。
- K <= n < 2K（remark 读法）: C*_{n,K}(eta) = K/((2K-n)+(n-K)eta)；逐实例式 f(S) >= K/(K+(eta-1)|O*\S|) f(O*)。

**路线一位置**: app:ceiling + J5_ceiling_proof.md; route yi: appendix_model_proofs remark

**B 路线二比对**: B-PASS; consistent=True, quantifiers=False; divergences: D1 构造摆法：路线一把重权放在 N\S（n-K 个元素），路线二只放 h=min{K,n-K} 个；比值恒等 [VERIFIED-SYMBOLIC]，无实质差别; D2 C1 的推法：路线一用 X<=Y 加两条链的 band（J5 式 (6)），路线二引入残差 r=f-ftilde 并用其单调性加 L1 归一化；代数上恒等; D3 C4 的取法：路线一求和（R=sum_s r_s <= A），路线二取最小（m <= f(S)/K）；最终界相同; D4 紧性：路线二给出逐 j 的紧实例族 C7（(*) 对每个 j 不可改进），路线一只在最坏 j 处给紧性；判定人 LP 复核支持路线二的更强说法 ...; route-2 gaps: RG1 randomized ceiling 的精确值未定：路线二只从 U1 那一族得 C*·(n+(eta-1)h)/n；同一开口在路线一也是 OPEN，故不构成路线二相对路线一的欠缺; RG2 n=K 时 error 两侧不能同时取等：路线二在 U7 里已自行闭合（改取单元素 H），与路线一 J5 §4 末段修法一致；只剩一条正文措辞提醒（若写该实例即为所需需加 n>K）; RG3 四条添加的读法（arbitrary query access 取最强读法、/T/<=K、eta_u/eta_o 的域、L1 归一化）；全部保守，全部不改变结论; RG4 任务描述里 K=2 用于 ProbeLo ...

**C oracle**: C0 sympy identities (C* two branches, slack identity (7), E decomposition (8), single-exchange decomposition (9), Horel-Singer eps substitution, adversary ratio forms): PASS; C1 (a) n >= 2K adversary exactness, K = 2..4, n = 2K..10, 14 rational splits: PASS; C1b (a) same adversary check for K = 1, run separately, n = 2..10: PASS; C2 (b) attainment on random exact instances, n >= 2K, n <= 7, K <= 3: PASS; C3 (c) adversary direction against three algorithm types: PASS; C4 rerun of results/J5_hardcore/J5_hardcore_oracles.py --output-dir results/V11/oracle/j5_reproduced: PASS; C5 random exact instances with n = K..2K-1, K = 2..4: PASS; C6 app:ceiling adversary for K <= n < 2K has ratio exactly K/(K+(eta-1)min{K,n-K}): PASS

**D 反例搜索**: random 3544, structured 5, violations 0, worst Worst slack is 0 everywhere, i.e. the inequalities are tight at several points and never violated. Attainment side, per- ...

**E 量词审计**: A_match=False; A_diffs: D1 environment 与标题：正文是 proposition + "Upper bound for unbounded queries"（addendum B.1 的降级），台账 LaTeX 块与 results/V11/statements.md 第 74 行元数据仍写 theorem + "Deterministic ceiling, all ground-set sizes"。数学内容不变，但矩阵两栏来源不一致。; D2 逆向方向的 O* 全称：正文写 "for every opt ...; GAP: K>=2：陈述的定义域比路线甲需要的窄，app:ceiling 只固定 K>=1，K>=2 在证明里无处使用（oracle C1b 对 K=1 全过）；按 addendum B.3 的目标形态会自动消失; error exactly (η_u,η_o)：'exactly' 在 model.tex 的 Definition def:eta 里没有定义（只定义 'at most'），全文无约定句；需一句'最小可行因子对恰为 (η_u,η_o)'; 随机段的 expectation 量词：app:ceiling 'Randomized algorithms' 把 m=/T/ 当定值，缺'条件于随机串 ...

**裁定理由**: C 8 项 PASS（含 J5 hardcore 复跑：恒等式 (7)(8)(9)、52 LP、24 对手实例）；D 3544 次 0 违反；B-PASS（n<2K 交换论证被盲审独立复推）；E GAP：K ≥ 2 无用（应 K ≥ 1）、'exactly' 无定义、随机段缺条件于随机串一步。

**可写进正文的精确表述**: Let K >= 1 and n >= 2K, and let eta_u, eta_o > 0 with eta_u eta_o = eta >= 1. (a) For every deterministic algorithm with arbitrary query access to f~ that outputs a set T with |T| <= K, there is a pair (f, f~) with f monotone submodular, f(empty) = f~(empty) = 0, whose smallest admissible factors are exactly (eta_u, eta_o), on which f(T) <= OPT/eta. (b) On every instance satisfying Definition 1 with product eta, a K-set S maximizing f~ over all K-subsets satisfies f(S) >= K/(K + (eta-1)|O* minus S|) OPT >= OPT/eta for every optimal K-set O*. Hence the optimal worst-case ratio of deterministic algorithms with unbounded queries is exactly 1/eta. (Appendix remark: for K <= n < 2K the exact deterministic value is K/((2K-n) + (n-K) eta), attained by the same maximizer; for randomized algorithms and n >= 2K, for every algorithm there is a fixed pair on which E_seed[f(T)] <= ((1-K/n)/eta + K/n) OPT, an upper bound only.)

**K=3, η=3/2 走读**: K=3, eta=3/2, n=6 adversary (c=1, split (3/2,1)): f(O)=9/2, f(T)=3, ratio 2/3 = 1/eta. n=5 (=2K-1) adversary: f(S)=3, f(O)=4, ratio 3/4 = C*_{5,3}(3/2). Per-instance form at a=|O*\S|=0,1,2,3: 1, 6/7, 3/4, 2/3.

### prop:guarantee (Prop 3) — 最终标签 **[HAND-PROOF-UNREVIEWED]**

**陈述原文**

#### T3 prop:guarantee

- 正文环境: `proposition`, label `prop:guarantee`
- 台账卡: ## T3 prop:guarantee — predictive greedy 的保证（D2：归属 GS）

##### 台账陈述（逐字）

- 陈述（K1 后）：f 单调 submodular；run 的选择误差 η^sel（新定义：a_t=M_t/g_t，M_t=g_t=0 取 1，g_t=0<M_t 取 ∞，η^sel=max{1,a_t}，L_K(∞)=0）。则 f(T) ≥ L_K(η^sel) f(O*) ≥ (1−e^{−1/η^sel}) f(O*)，L_K(x)=1−(1−1/(xK))^K。同一界对 η^tr、η 成立。

##### 正文陈述（逐字，LaTeX）

```latex
\begin{proposition}[Guarantee of predictive greedy]\label{prop:guarantee}
Let $f$ be monotone submodular with $f(\emptyset)=0$ and let $T=S^{K}$ be the
output of a run of predictive greedy whose selection error is $\etasel$
(Definition~\ref{def:etasel}, with $L_K(\infty)=0$).
Then, with $L_K(x)=1-(1-\tfrac1{xK})^{K}$,
\[
  f(T)\;\ge\;L_K(\etasel)\,f(O^{\ast})
  \;\ge\;\bigl(1-e^{-1/\etasel}\bigr)f(O^{\ast}).
\]
If moreover the predictor has finite error $(\eta_u,\eta_o)$, the same bound
holds with $\etasel$ replaced by $\etatr$ or by $\eta$, and the three bounds
are ordered $L_K(\etasel)\ge L_K(\etatr)\ge L_K(\eta)$.
\end{proposition}
```

**路线一位置**: app:guarantee

**B 路线二比对**: B-PASS; consistent=True, quantifiers=False; divergences: D1 量词域差异（唯一实质性量词分歧）：route1 用 def:eta verbatim，eta_u,eta_o >= 1；route2 的 Q9 写 convention B，eta_u,eta_o > 0 且乘积 >= 1。; D2 由 D1 派生、可复算的瑕疵：route2 Step 12 把 eta^tr 的两个因子各自截断到 1，Step 14 默认全局因子同样逐因子截断。verbatim 约定下自洽，convention B 下不成立：取 f̃=2f，全局 (eta_u,eta_o)=(1/2,2)、eta=1，而逐因子截断的 eta^tr=max(1,1/2)*max(1,2) ...; route-2 gaps: [ASSUMPTION-ADDED] eta^tr 的形式定义（Step 12）。route1 无公式故不可证伪；未闭合项是：若论文采用 convention B，该定义须改成乘积层面截断。; [ASSUMPTION-ADDED] 全零轨迹时截断到 1 的方向判断有误：route2 称其为保守方向，但该方向只对 eta^sel<=eta^tr 成立，对 eta^tr<=eta 不成立（f̃=2f 反例）。这是本轮为 route2 新发现的 gap，route2 自己未识别。; rem:app-product 未推导：route2 未给逐步乘积界 1-prod(1-1/(K a_t))，也未给提 ...

**C oracle**: C0 sympy identities on L_K [VERIFIED-SYMBOLIC]: PASS; C1 random exact instances: f(T) >= L_K(eta^sel) OPT and the ordering [VERIFIED-EXHAUSTIVE]: PASS; C2 Step-1 covering r_t <= K M_t and the contraction [VERIFIED-EXHAUSTIVE]: PASS; C3 auxiliary rem:app-product per-step product bound [VERIFIED-EXHAUSTIVE]: PASS; C4 legal band implies finite eta^sel [VERIFIED-EXHAUSTIVE]: PASS; C5 U_K exact tightness of L_K under eta^sel [VERIFIED-EXHAUSTIVE]: PASS; C6 rerun results/F2_etasel_tight.py [VERIFIED-LP 浮点]: PASS; C7 rerun results/T5_symbolic.py [VERIFIED-SYMBOLIC]: PASS

**D 反例搜索**: random 3000, structured 5, violations 0, worst "Worst slack over all runs is 0, i.e. equality, attained on 790 of the 9064 C1 checks (trivial ones such as K=1, eta^sel ...

**E 量词审计**: A_match=False; A_diffs: D1: normalization f(empty)=0 appears only in the paper statement (results.tex line 80 'Let $f$ be monotone submodular with $f(\emptyset)=0$'); the ledger T3 statement field (THEOREM_LEDGER.md line 70) writes only 'f 单调 submodular'. It is load-bearing ...; GAP: GAP-1 (light): normalization f(empty)=0 is used implicitly at app:guarantee Step 3 ('With $r_0=f(O^{\ast})$') and is never named; fix is one clause in Step 3. Does not affect the truth of the statement.; GAP-2 (light): r_t >= 0 (equivalently f(S^t) <= f(O*), from /S^t/=t<=K and optimality of O* over ...

**裁定理由**: C 8 项 PASS（3000 随机 run；F2_etasel_tight、T5_symbolic 复跑）；D 0 违反；B-PASS；E 轻 GAP：f(∅)=0 与 r_t ≥ 0 在附录隐式使用。B 比对新发现方案二下 η^tr 的定义须按乘积截断（见重点发现 1）。

**可写进正文的精确表述**: Let f be monotone submodular with f(empty) = 0, O* an optimal K-set, and T = S^K the output of a K-step run of predictive greedy with selection error eta^sel (per-step factors a_t, eta^sel = max{1, a_t}, L_K(infinity) = 0). Then f(T) >= L_K(eta^sel) OPT >= (1 - e^{-1/eta^sel}) OPT with L_K(x) = 1 - (1 - 1/(xK))^K. If f~ satisfies Definition 1 with product eta, the same bound holds with eta^sel replaced by eta^tr (the band restricted to the run's states, with the truncation at 1 applied to the product of the two factors) or by eta, and L_K(eta^sel) >= L_K(eta^tr) >= L_K(eta).

**K=3, η=3/2 走读**: "K = 3, U_3 family with ahat = 3/2 (n = 6, OPT = 1): the three steps have a_t = 3/2 each, so eta^sel = eta^tr = 3/2 and f(T) = 386/729 = L_3(3/2) ≈ 0.5295, exact equality.\nThe same instance has global eta = (3·3/2 − 1)/2 = 7/4 with L_3(7/4) = 4348/9261 ≈ 0.4695, so the three rulers read 386/729 = 386/729 > 4348/9261.\nFor contrast at ahat = 2: ratio = L_3(2) = 91/216, global eta = 5/2, L_3(5/2) = 1178/3375."

### lem:coherence (Lemma) — 最终标签 **[HAND-PROOF-UNREVIEWED]**

**陈述原文**

#### T5 lem:coherence

- 正文环境: `lemma`, label `lem:coherence`
- 台账卡: ## T5 lem:coherence — coherence lemma（唯一新引理）

##### 台账陈述（逐字）

- 陈述：f 单调，S⊆N，e,e'∉S，d̃_e(S) ≥ d̃_{e'}(S)。则 (i) d_e(S∪{e'}) ≥ d_{e'}(S∪{e})/η；(ii) (1−1/η) d_{e'}(S∪{e}) ≥ d_{e'}(S)−d_e(S)。

##### 正文陈述（逐字，LaTeX）

```latex
\begin{lemma}[Coherence]\label{lem:coherence}
Let $f$ be monotone, $S\subseteq N$, $e,e'\notin S$, and suppose
$\tilde d_{e}(S)\ge\tilde d_{e'}(S)$.  Then
\[
  \text{(i)}\;\; d_{e}(S\cup\{e'\})\ge\tfrac1\eta\,d_{e'}(S\cup\{e\}),
  \qquad
  \text{(ii)}\;\;\bigl(1-\tfrac1\eta\bigr)\,d_{e'}(S\cup\{e\})
  \ge d_{e'}(S)-d_{e}(S).
\]
\end{lemma}
```

**路线一位置**: app:coherence + H_J3_gate_check.py

**B 路线二比对**: B-GAP (route two incomplete); consistent=True, quantifiers=False; divergences: D1 sharp form 是两个不同的命题：路线一（results.tex 153-167 行 + 台账 T5）的 sharp form 是 d - g/eta >= (1-1/eta)(g-h) >= 0（d=d_e(S), g=d_{e'}(S), h=d_{e'}(S+e)），第一个不等号是 (ii) 的恒等改写，第二个用 submodularity 加 eta>=1，并带推论 eta>1 且 d=g/eta ⇒ h=g；路线二第 4 节的 (S1) order transfer、(S2) 常数 1/eta 不可改进、(S3) min 形式、(S4) 取等刻画是自行重构的另一组命题。两 ...; route-2 gaps: GAP-A 未产出路线一的 sharp form 链 d - g/eta >= (1-1/eta)(g-h) >= 0（路线二自报 GAP-1，标 [ADDED-ASSUMPTION]）。可一行闭合：第一个不等号就是路线二 Step 5 的恒等式（本轮 [VERIFIED-SYMBOLIC]），第二个就是路线二 §5 的 'C<=B 是唯一需要 submodularity 的一条' 加 eta>=1。; GAP-B 未产出刚性推论 eta>1 且 d=g/eta ⇒ h=g。补法：由 (ii) 代入 A=B/eta 得 (1-1/eta)C >= (1-1/eta)B，eta>1 除掉因子得  ...

**C oracle**: C0 own sympy derivation of the slack decompositions: PASS; C1 random exact instances: parts (i), (ii) and the sharp form: PASS; C2 three-term nonnegative decomposition on every triple: PASS; C3 rerun results/H_J3_gate_check.py: PASS; C4 rerun results/J2_core_oracles.py, coherence part: PASS; C5 running example K=3 eta=3/2 exact worst-case trajectory: PASS

**D 反例搜索**: random 3468, structured 6, violations 0, worst Worst slack of (ii) (= slack of (i) = slack of the sharp-form first inequality) is 0, i.e. equality is attained: 29,398  ...

**E 量词审计**: A_match=True; A_diffs: none; GAP: GAP-1 (medium): the hypothesis 'f monotone' is never used by route one. app:coherence (appendix_proofs.tex 524-579) proves the exchange identity from the set-function definition, (i) by chaining the bands, and (ii) from f's exchange identity plus (i); deleting 'monotone' leaves the derivation word f ...

**裁定理由**: C 6 项 PASS（自写 slack 分解 + H_J3/J2 复跑）；D 3468 三元组 0 违反；A 逐字一致；B：引理本体路线二完整一致，sharp form 链不在盲审输入里由判定人一行闭合（B-GAP 形式上）；E GAP（中）：'f monotone' 前提在证明中未使用（空洞性检验）。一行修订即可升 [VERIFIED-CROSS]。

**可写进正文的精确表述**: Let f~ satisfy Definition 1 with product eta for a set function f, let S be a subset of N and e, e' not in S with d~_e(S) >= d~_{e'}(S). Then (i) d_e(S + e') >= d_{e'}(S + e)/eta and (ii) (1 - 1/eta) d_{e'}(S + e) >= d_{e'}(S) - d_e(S). If moreover f is submodular, with d = d_e(S), g = d_{e'}(S), h = d_{e'}(S + e): d - g/eta >= (1 - 1/eta)(g - h) >= 0, and eta > 1 with d = g/eta forces h = g. The band is used at the off-run state S + e, so the lemma holds for the global eta only (not for eta^sel or eta^tr). (The hypothesis 'f monotone' is not used by the proof.)

**K=3, η=3/2 走读**: K = 3, eta = 3/2: k_1 = 4, q = 3/4, j = 2; trajectory d_t = (1/4, 3/16, 1/8), optimum-element marginals g_t = (1/3, 1/4, 3/16, 3/16), sum d_t = 9/16 = V_2(3/2) = rho_3(3/2). Sharp form step by step: t=0, d - g/eta = 1/4 - 2/9 = 1/36 = (1-1/eta)(g-h) = (1/3)(1/3 - 1/4); t=1, 1/48 = (1/3)(1/4 - 3/16); t=2, 0 = (1/3)*0. All three steps attain equality in the first inequality; t=2 is exactly the ledger corollary (eta > 1 and d = g/eta = 1/8 force h = g = 3/16).

### thm:exact (Theorem 1) — 最终标签 **[HAND-PROOF-UNREVIEWED]**

**陈述原文**

#### T6 thm:exact

- 正文环境: `theorem`, label `thm:exact`
- 台账卡: ## T6 thm:exact — 精确最坏值（主定理）

##### 台账陈述（逐字）

- 陈述：K ≥ 2, η ≥ 1，adversarial tie：ρ_K(η)=min_{0≤j≤K−1} V_j(η)，V_j=1−q^j(1−(K−j)/(Kη))，q=(K−1)η/((K−1)η+1)；段 [K−j,K−j+1] 上由 V_j 取到，[K,∞) 上 V_0=1/η；分段点整数 2..K；ρ_K=1/η ⇔ η ≥ K。K=2,3,4 显式闭式见正文。

##### 正文陈述（逐字，LaTeX）

```latex
\begin{theorem}[Exact worst-case ratio of predictive greedy]\label{thm:exact}
For every $K\ge2$ and $\eta\ge1$, under adversarial tie breaking,
\[
  \rho_K(\eta)\;=\;\min_{0\le j\le K-1}V_j(\eta),
\]
and the minimum is attained by $V_j$ on the segment
$\eta\in[K-j,K-j+1]$ (with $V_0=1/\eta$ on $[K,\infty)$), so the breakpoints
are the integers $2,\dots,K$.  In particular
$\rho_K(\eta)=1/\eta$ exactly when $\eta\ge K$, and for $K\in\{2,3,4\}$ the
closed forms are
$\rho_2=\min\{\tfrac1\eta,\tfrac{3}{2(\eta+1)}\}$,
$\rho_3=\tfrac{16\eta+3}{3(2\eta+1)^2}$, $\tfrac{7}{3(2\eta+1)}$,
$\tfrac1\eta$ on $[1,2],[2,3],[3,\infty)$, and
$\rho_4=\tfrac{135\eta^2+36\eta+4}{4(3\eta+1)^3}$,
$\tfrac{21\eta+2}{2(3\eta+1)^2}$, $\tfrac{13}{4(3\eta+1)}$, $\tfrac1\eta$ on
$[1,2],[2,3],[3,4],[4,\infty)$.
\end{theorem}
```

**路线一位置**: app:exact + app:validity

**B 路线二比对**: B-PASS-with-different-route; consistent=True, quantifiers=False; divergences: D1 LP 约束集与对偶支撑不同：路线一 eq:redlp 有四族 sum/pred/mono/cons 且逐 i，其证书支撑是 sum+pred+cons（lambda_mono 恒为 0）；路线二的 (P) 只有聚合的 sum+cons+mono，完全不用 pred，且 mono 乘子 w_t>0（t>=j）。两套证书本轮均独立符号复核通过（749 与 525 检查，0 失败），LP 值一致（HiGHS 浮点：sum+pred+mono 给 L_K，sum+cons+mono 与四族全上都给 rho_K）。台账 T6 的副产品句『下界证书中单调约束乘子恒为零』只对路线一成立。; D2 at ...; route-2 gaps: 一般 K 的 dual 可行性未闭合：逐 K 符号验证只覆盖 K=2..7（本轮独立复跑 749 检查 0 失败），任意 K 的统一论证是手写的 complementary slackness 反解，[HAND-PROOF-UNREVIEWED]；路线一 N1 在此更强（一般符号 (K,j,t,i) modulo 一次有限分支枚举加 K=2..10 暴力）。; 一般 K 的 attaining instance 合法性未闭合：逐 S 逐 e 穷举只到 K=5（本轮复跑 K=2..5 共 131 例 0 失败），K>=6 为手写论证 [HAND-PROOF-UNREVIEWED]（其 band  ...

**C oracle**: C0a sympy identities for V_j (K=2..8): PASS; C0b V_j = min_i V_i on segment [K-j, K-j+1], breakpoints are the integers 2..K: PASS; C0c rho_K = 1/eta exactly when eta >= K: PASS; C1 own exact rational simplex on the full LP of code/reduced_lp.py equals min_j V_j: PASS; C2 exact primal-dual certificate at every optimum: PASS; C3 closed forms printed in the statement for K=2,3,4: PASS; C4 rerun results/N1_dual_certificate.py: PASS; C5 rerun results/N2_check.py: PASS; C6 cross-check against float scipy code/reduced_lp.reduced: PASS; C7 validity of the four eq:redlp families on every random run (reduction step rho_K >= LP optimum): PASS; Scope gap: general-K validity derivation and the attaining family were not independently rebuilt: GAP

**D 反例搜索**: random 2400, structured 5, violations 0, worst Worst (tightest) D1 slack f(T)/OPT - rho_K(eta) = 269/3168 = 0.0849 at K=2, n=4, modular f, independent-surrogate mode,  ...

**E 量词审计**: A_match=True; A_diffs: [无量词差异] 逐量词比对（K>=2；eta>=1；adversarial tie breaking；min over 0<=j<=K-1；段 [K-j,K-j+1] 上由 V_j 取到；j=0 时 V_0=1/eta on [K,infty)；分段点整数 2..K；rho_K=1/eta exactly when eta>=K；K=2,3,4 闭式及其分段）两张清单完全重合，故 A_match=true。statements.md 第 183-201 行、inputs/statement_ex ...; GAP: GAP-1（唯一真 GAP，E 表第 16 行）：n 量词在路线甲的 app:exact 内没有落点。上界构造固定 n=2K，下界 reduced LP 不含 n；从 n=2K 的实例到每个 n>=2K 的 rho_{n,K} 只由 results.tex 第 208-215 行的 rem:exact-n 两句话（restriction 到 T∪O*、padding 零增益元素）承担，状态 [HAND-PROOF-UNREVIEWED] 且正文注释自述是本地重构（J5 §13 原文未送达）；数值支持 [VERIFIED-LP]（results/L2_linear_candidates.py g ...

**裁定理由**: C 10 项 PASS（自写精确有理 simplex K=2..6 × 20 个 η 逐点 = min_j V_j；N1/N2 复跑；四族有效性）；D 2400 随机实例 0 违反 + 图 1 实例复核；A 逐字一致；B-PASS（不同路线：另一组对偶支撑）；E GAP-1：n 量词只靠 rem:exact-n（restriction + padding）[HAND-PROOF-UNREVIEWED]。

**可写进正文的精确表述**: For every K >= 2, every eta >= 1 and every n >= 2K, the exact worst-case ratio of K-step predictive greedy under adversarial tie breaking, over all instances on n elements with f monotone submodular, f(empty) = 0, and f~ satisfying Definition 1 with product at most eta, is rho_K(eta) = min_{0 <= j <= K-1} V_j(eta), V_j = 1 - q^j (1 - (K-j)/(K eta)), q = (K-1) eta/((K-1) eta + 1); the minimum is V_j on eta in [K-j, K-j+1] (V_0 = 1/eta on [K, infinity)), the breakpoints are the integers 2, ..., K, and rho_K(eta) = 1/eta exactly when eta >= K. (The independence of n for n >= 2K rests on restriction to T union O* and zero-gain padding; ground sets with n < 2K are not covered.)

**K=3, η=3/2 走读**: K = 3, eta = 3/2: k1 = 4, q = 3/4, (V_0, V_1, V_2) = (2/3, 7/12, 9/16), argmin j = 2, and eta = 3/2 lies in the segment [K-j, K-j+1] = [1, 2]. The own exact rational simplex on the full reduced LP returns 9/16 = 0.5625 = min_j V_j, and its primal-dual certificate verifies exactly. The printed K = 3 closed form (16 eta + 3)/(3(2 eta + 1)^2) gives 27/48 = 9/16, so LP, min_j V_j and the closed form agree as Fractions.

### cor:limit (Corollary) — 最终标签 **[HAND-PROOF-UNREVIEWED]**

**陈述原文**

#### T9 cor:limit

- 正文环境: `corollary`, label `cor:limit`
- 台账卡: ## T9 cor:limit — 渐近（J5H5 首行统一：单调性已证，历史移卡末）

##### 台账陈述（逐字）

- 陈述（最终状态）：固定 η，L_K、ρ_K、U_K → 1−e^{−1/η}；ρ_K 关于 K **非增**，K ≤ ⌊η⌋ 平台 1/η，
  K ≥ ⌊η⌋ 起严格递减（[VERIFIED-SYMBOLIC，conditional on thm:exact]，证明已迁入 app:asymptotics，
  J5H5）；一阶展开 ρ_K = 1−e^{−1/η} + c(η)/K + O_η(1/K²)，c(η) = e^{−1/η}(2η−1)/(2η²)（不随
  ⌊η⌋ 分段；c_L = e^{−1/η}/(2η²)、c_U = c，同样已迁入附录）。

##### 正文陈述（逐字，LaTeX）

```latex
\begin{corollary}[Limit in $K$]\label{cor:limit}
For fixed $\eta\ge1$, both $L_K(\eta)$ and $\rho_K(\eta)$ converge to
$1-e^{-1/\eta}$ as $K\to\infty$; $L_K$ is monotone in $K$, and
$\rho_K$ is non-increasing in $K$, equal to $1/\eta$ for
$K\le\lfloor\eta\rfloor$ and strictly decreasing from
$K\ge\lfloor\eta\rfloor$ on, so the limit is approached from above.
\end{corollary}
```

**路线一位置**: app:asymptotics

**B 路线二比对**: B-PASS-with-different-route; consistent=True, quantifiers=False; divergences: D1 rho_K 极限的路径不同：路线一（app:asymptotics 第 1380-1391 行）直接展开 active branch V_{K-floor(eta)}，逐项算 j/k1 -> 1/eta 与 1-floor(eta)/(K eta) -> 1；路线二 Step 11 改用 squeeze，下界是它新增的一致上界 h_K(j) <= e^{-1/eta}（Step 7，路线一无对应步骤），上界是 U_K。结论相同; D2 单调性的正性证书不同：路线一用尾界 -log(1-1/x) <= 1/x+1/(2x^2)+1/(3x^2(x-1)) 加坐标变换 s=t/(1+t) 后 ...; route-2 gaps: A1（已由本判定闭合）追加读法：notation.md 未给 min_j V_j 的 j 范围，路线二取 {0,...,K}，仓库是 {0,...,K-1}。exact rational 复核 min_{0<=j<=K-1} V_j == min_{0<=j<=K} V_j（17 个 eta、K<=60）[VERIFIED-EXHAUSTIVE]，只影响 Step 11 上界那一步的出处，不影响结论; A2（可由仓库闭合）n 的量词缺失：路线二把 rho_K 与 n 无关记为追加读法，并说若实为 rho_{n,K} 则 (C-a)(C-b) 需补量词。ledger T6 M1 已给 n >=  ...

**C oracle**: C0 rerun results/H_B_asymptotic.py: PASS; C1 sympy limit L_K(eta) -> 1 - e^{-1/eta}: PASS; C2 sympy limit V_{K-floor(eta)}(eta) -> 1 - e^{-1/eta}: PASS; C3 sympy series rho_K = 1 - e^{-1/eta} + c(eta)/K + O(1/K^2): PASS; C3b exact bracketing of the 1/K^2 remainder: PASS; C4 monotonicity of rho_K in K, exact rationals: PASS; C5 monotonicity of L_K in K, exact rationals: PASS; C6 limit approached from above, exact: PASS; C7 closed-form consistency (conditional on thm:exact / T6): PASS

**D 反例搜索**: random 18000, structured 8, violations 0, worst Monotonicity: the largest (least negative) strict difference over D1+D2 is rho_{K+1} - rho_K = -6.378052e-08 at eta = 66 ...

**E 量词审计**: A_match=False; A_diffs: D2 (U_K): 台账陈述行写 "L_K、ρ_K、U_K → 1−e^{−1/η}"，正文 corollary 环境（results.tex 523-529）只讲 L_K 与 ρ_K；U_K 在正文只出现在环境之后第 533 行，且只作为 1/K 系数，没有极限断言。; D3 (L_K 单调性): 正文有 "L_K is monotone in K"，台账 T9 卡（206-209 陈述行，以及全卡）完全没有 L_K 的单调子句；且正文的 monotone 没有方向，附录 1378-1380  ...; GAP: GAP-1（K 的定义域）：陈述、台账 T9 卡、路线甲三处都没写 K 的下端。ρ_K 闭式只对 K ≥ 2 成立（thm:exact，results.tex 192）；1 ≤ η < 2 时 ⌊η⌋=1，平台子句只覆盖 K=1、严格递减子句要用 ρ_1，而 ρ_1=1/η 的三行链只在台账 T10b 第 261 至 264 行，状态 [HAND-PROOF-UNREVIEWED]，不在 app:asymptotics 也不在 T9 卡。; GAP-2（n 量词与 K→∞ 的相容性）：app:asymptotics 全篇不含 n。ρ_K 与 n 无关只在 n ≥ 2K 时成立（rem:exac ...

**裁定理由**: C 9 项 PASS（H_B 复跑；sympy 极限与级数；精确差分 K ≤ 200）；D 18000 个 (K,η) 点 0 违反；B-PASS（不同路线）；E GAP：K 下端与 ρ_1 的出处、n 量词、'monotone' 无方向。全部 conditional on thm:exact。

**可写进正文的精确表述**: Fix eta >= 1. As K -> infinity, L_K(eta) increases to 1 - e^{-1/eta} and rho_K(eta) -> 1 - e^{-1/eta}. For K >= 2, rho_K(eta) is non-increasing in K: it equals 1/eta for 2 <= K <= floor(eta) and is strictly decreasing in K for K >= max{2, floor(eta)}, so the limit is approached from above. Quantitatively rho_K(eta) = 1 - e^{-1/eta} + c(eta)/K + O(1/K^2) with c(eta) = e^{-1/eta}(2 eta - 1)/(2 eta^2). (Every statement about rho_K is conditional on Theorem thm:exact and on n >= 2K.)

**K=3, η=3/2 走读**: K = 3, eta = 3/2: m = floor(eta) = 1, k_1 = 4, q = 3/4, j* = 2, so rho_3 = V_2 = 9/16 = 0.5625, with L_3 = 386/729 = 0.529492 and U_3 = 37/64 = 0.578125 (sandwich holds). rho_4 = 1447/2662 = 0.543576, so rho_4 - rho_3 = -403/21296 = -0.018924 < 0 (strict decrease, no plateau since floor(eta) = 1). The limit 1 - e^{-2/3} is bracketed exactly in [0.486582880967, 0.486582880967], giving rho_3 - limit >= 0.075917 > 0, and c(3/2) in [0.2281853862, 0.2281853862] matching the ledger value 0.228.

### thm:linear-exact (Theorem 2) — 最终标签 **[HAND-PROOF-UNREVIEWED]**

**陈述原文**

#### T10c thm:linear-exact (J6)

- 正文环境: `theorem`, label `thm:linear-exact`
- 台账卡: ## T10c thm:linear-exact — greedy 同预算类的精确最优值（Q4 装配，取代 T10b 的单边天花板）

##### 台账陈述（逐字）

- 陈述：K ≥ 2，η > 1，n ≥ 4K⁵。𝒜_lin 同 T10b（确定性、≤ nK 次 f̃ 查询、每次查询集合大小 ≤ K、输出 ≤ K 元素；
  predictive greedy 用 ≤ Kn−K(K−1)/2 次查询，属于该类）。
  (i) 上界：对任意 A ∈ 𝒜_lin 与任意给定拆分 η_u, η_o ≥ 1、η_uη_o = η，存在实例 (f, f̃)，f 单调 submodular
  归一化，实际单元素误差因子恰为 (η_u, η_o)，使 f(T)/f(O*) ≤ ρ_K(η)。
  (ii) 与 thm:exact 合并：sup_{A ∈ 𝒜_lin} inf_{(f,f̃)} f(A)/OPT = ρ_K(η)。夹逼闭合，无 n → ∞ 极限，
  值在每个 n ≥ 4K⁵ 处精确。
  随机版（单列，仅渐近）：对任意同预算随机算法存在实例使 E_seed[f(T)/f(O*)] ≤ ρ_K(η) + ε_n，
  ε_n = K²/n + K⁵/(2n)（装配给 K/n + K⁵/(2n)，K²/n 沿 T10b 保守取整）；不声称随机类有限 n 精确。

##### 正文陈述（逐字，LaTeX）

```latex
\begin{theorem}[Exact optimality within the greedy query budget]
\label{thm:linear-exact}\label{cor:greedybudget}
Let $K\ge2$, $\eta>1$ and $n\ge4K^{5}$, and let $\mathcal A_{\mathrm{lin}}$
be the class of deterministic algorithms that make at most $nK$ queries to
$\tilde f$, each on a set of size at most $K$, and output a set of size at
most $K$; predictive greedy, at $Kn-K(K-1)/2$ queries, belongs to
$\mathcal A_{\mathrm{lin}}$.  For every $A\in\mathcal A_{\mathrm{lin}}$
and every prescribed split $\eta_u,\eta_o\ge1$ with $\eta_u\eta_o=\eta$,
there is an instance $(f,\tilde f)$ with monotone submodular $f$, whose
smallest admissible error factors in Definition~\ref{def:eta} are exactly
$(\eta_u,\eta_o)$, on which the output $T$ satisfies
\[
  \frac{f(T)}{f(O^{\ast})}\;\le\;\rho_K(\eta).
\]
Combined with Theorem~\ref{thm:exact}, whose guarantee holds on every
instance with error at most $\eta$,
\[
  \sup_{A\in\mathcal A_{\mathrm{lin}}}\;
  \inf_{(f,\tilde f)}\;
  \frac{f(A^{\tilde f})}{f(O^{\ast})}\;=\;\rho_K(\eta):
\]
predictive greedy is exactly optimal within its own query budget, at every
such $n$, with no asymptotics in $n$ or $K$.  For every randomized
algorithm with the same budget there is again an instance with error
exactly $\eta$ on which the expectation over the algorithm's randomness
satisfies
$\mathbb E\bigl[f(T)/f(O^{\ast})\bigr]\le\rho_K(\eta)+\varepsilon_n$, where
$\varepsilon_n=K^{2}/n+K^{5}/(2n)$; for the randomized class the matching
is therefore asymptotic in $n$ at fixed $K$, and no exact finite-$n$
statement is claimed.
\end{theorem}
```

**路线一位置**: app:greedybudget + results/J6/linear_exact.md

**B 路线二比对**: B-GAP (route two incomplete); consistent=False, quantifiers=False; divergences: D1 (substantive): route two's 1-blind condition (*) has no size cap ("for all s"), route one requires small-set indistinguishability only on /S/ <= K with /S cap O/ <= 1 and states explicitly that the predictor leaks on larger sets (K=3, eta=3/2: H(6,0)=61/48 vs H(5,1)=4/3). My count-grid LP shows r ...; route-2 gaps: GAP-1 (self-reported, [FAILED]): R1's hand proof misses the comparison between the two gain chains; the conclusion 1/eta itself I reproduced at K=2,3,4 up to X=14 [VERIFIED-LP], the general proof is still missing.; GAP-2 (self-reported, [FAILED]): orbit average avg-T = 0.61 > rho_2 = 3/5 at K=2, eta ...

**C oracle**: C1 rerun results/Q4_gpt_check.py (13 identities + 159-config battery): PASS; C2 rerun results/Q4_symbolic_ineq.py (34 branch inequalities): PASS; C3 rerun results/Q4_indep_check.py (111 configs): PASS; C4 counting chain in exact rationals (11 sub-checks): PASS; C5 smallest n with chain total < 1, both readings, exact: PASS; C6 randomized clause eps_n = K^2/n + K^5/(2n): PASS; C7 own re-implementation of the double-residual family, count-grid legality on the D configurations: PASS

**D 反例搜索**: random 500, structured 40, violations 0, worst Worst slack rho_K - ratio = 0 (exactly zero, never negative) across all 56 structured cases and all 500 random strategie ...

**E 量词审计**: A_match=False; A_diffs: D1 normalization: ledger states 'f 单调 submodular 归一化' (normalized); the results.tex environment says only 'monotone submodular f', f(emptyset)=0 is inherited from model.tex line 9 and never written in the statement; D2 error-factor wording: ledger sa ...; GAP: GAP-1: the domain of the inf in the sup-inf identity is written nowhere. results.tex 756-789 and THEOREM_LEDGER.md 294-301 both write inf_{(f,ftilde)} bare, and appendix_proofs.tex lines 1876-1877 close with 'together these give the sup--inf identity' without naming the instance class (error at most ...

**裁定理由**: C 7 项 PASS（Q4 三脚本复跑 13 恒等式/159 电池/34 分支/111 组；计数链精确；自写重实现）；D 500 随机策略 + 56 结构化 0 违反；B-GAP：盲审走全大小 size-only 路线撞上强制超额，未复现 small-set-only 机制，判定人复核路线一正确；E GAP：sup-inf 的实例类未命名、归一化与'single-element'措辞。

**可写进正文的精确表述**: Let K >= 2, eta > 1 and n >= 4K^5. Let A_lin be the class of deterministic algorithms that make at most nK queries to f~, each on a set of size at most K, and output a set of size at most K; predictive greedy belongs to it. For every A in A_lin and every eta_u, eta_o > 0 with eta_u eta_o = eta there is an instance on n elements with f monotone submodular, f(empty) = f~(empty) = 0, whose smallest admissible factors are exactly (eta_u, eta_o), on which f(T)/OPT <= rho_K(eta). Hence, over instances on n elements with monotone submodular normalized f and error product at most eta, sup_{A in A_lin} inf_instances f(A)/OPT = rho_K(eta), for every such n. For every randomized algorithm with the same budget there is a fixed instance with error exactly eta on which E_seed[f(T)/OPT] <= rho_K(eta) + K^2/n + K^5/(2n).

**K=3, η=3/2 走读**: K=3, eta=3/2: k1 = 4, q = 3/4, j = 2, Q = 9/16, delta = 1/8, C = 4/3, Hhat = (0, 1/3, 7/12, 37/48), rho_3(3/2) = 9/16. F(3,0) = 9/16 = rho_3 and F(0,3) = 1 = OPT; the leak above size K is H(6,0) = 61/48 versus H(5,1) = 4/3. n >= 4K^5 = 972; the loose chain first gives failure probability < 1 at n = 131, the tight chain at n = 64 (handoff figure 63 is the strict threshold, one below the smallest admissible n).

### thm:hardness (Theorem 3) — 最终标签 **[HAND-PROOF-UNREVIEWED]**

**陈述原文**

#### T10 thm:hardness

- 正文环境: `theorem`, label `thm:hardness`
- 台账卡: ## T10 thm:hardness — 有界查询 hardness（K4 后按 J2 校准）

##### 台账陈述（逐字）

- 陈述：c ≥ 0 实数，τ=⌈c⌉+1，K>τ，n ≥ 4K^{c+2}，η>1 且 η ≥ (K−1)/(K−τ)，θ̄=(η(K−τ)+1)/K。任意确定性算法，≤n^c 次、每次集合大小 ≤K 的 f̃ 查询、输出 ≤K 元素，存在实际误差恰为 η 的实例使 f(T)/f(O*) ≤ H_{K,τ}(η)=1−(1−1/(η(K−τ)+1))^K=L_K(θ̄)。随机版加 ε_n=K/n+K^{2τ+2}/((τ+1)! n^{τ+1−c})。

##### 正文陈述（逐字，LaTeX）

```latex
\begin{theorem}[Bounded-query hardness, deterministic]\label{thm:hardness}
Let $c\ge0$ be real and put $\tau=\lceil c\rceil+1$, which equals $c+1$ at
integer $c$.  Let the integers
$K>\tau$ and $n\ge4K^{c+2}$ and the real $\eta>1$ with
$\eta\ge\tfrac{K-1}{K-\tau}$ be fixed, so that $\bar\theta\ge1$.  For every
deterministic algorithm making at most $n^{c}$ queries to $\tilde f$, each on
a set of size at most $K$, there is an instance $(f,\tilde f)$ with monotone
submodular $f$, whose smallest admissible error factors in
Definition~\ref{def:eta} have product exactly $\eta$, on which the output $T$
(of size at most $K$) satisfies
\[
  \frac{f(T)}{f(O^{\ast})}\;\le\;
  H_{K,\tau}(\eta)\;:=\;
  1-\Bigl(1-\frac{1}{\eta(K-\tau)+1}\Bigr)^{K}\;=\;L_K(\bar\theta).
\]
Any prescribed split $\eta_u\eta_o=\eta$ of that error is realized by the
rescaling of Appendix~\ref{app:hardness}.  For randomized algorithms the same
bound holds in expectation up to an additive
\[
  \varepsilon_n=\frac Kn+\frac{K^{2\tau+2}}{(\tau+1)!\,n^{\tau+1-c}},
\]
which for integer $c$ reads $\tfrac Kn+\tfrac{K^{2c+4}}{(c+2)!\,n^{2}}$.  As
$K\to\infty$ with $\tau$ and $\theta$ fixed, $K\delta(\theta)\to\tau-1/\theta$;
with $c$ and $\eta$ fixed, $H_{K,\tau}(\eta)\to1-e^{-1/\eta}$.
\end{theorem}
```

**路线一位置**: app:hardness

**B 路线二比对**: B-GAP (route two incomplete); consistent=False, quantifiers=False; divergences: D1 window 门限：route2 取 W_tau={/S∩O*/<=tau-1}，route1 的 G_O oblivious 分支是 y<=tau、bad event 是 /S∩O/>tau。D2/D3 全部由此派生。; D2 门槛：route2 自己的充分条件是 n>=4K^{2tau}（c=0,tau=1 时与 statement 的 4K^2 相同）；route1 在 n>=4K^{c+2} 下用 level-(tau+1) 计数得总失败概率 <=9/32（本轮 c=0..3、K<=29 逐点精确复算最坏为 9/32）。route1 条件严格更弱，两者不矛盾。; D3 eps_n ...; route-2 gaps: G1 (=GAP-6, [FAILED])：显式硬族 f 未构造，route2 自称最大缺口。route1 给出 F_O/G_O，本轮在 (n,K,tau,eta)=(6,3,1,3/2),(7,3,2,5/2),(7,4,2,2),(6,3,1,5/2),(8,4,1,3) 上逐子集重建为真实集合函数，monotone、submodular、eta_act=eta、值=H 全通过 [VERIFIED-EXHAUSTIVE]。; G2 (=GAP-1, [FAILED])：statement 的 n>=4K^{c+2} 不足以让 route2 的 union bound <1（c=1 需 K< ...

**C oracle**: C1 rerun results/J2_core_oracles.py: PASS; C2 rerun results/H3_j2_recheck.py: PASS; C3 exact error product theta*A*B = (theta K - 1)/(K - tau): PASS; C4 exact rational table min{H_{K,tau}(eta), 1/eta}: PASS; C5 the tau=2, eta=3/2 column expectation: PASS; C6 identity H_{K,1}(eta) = U_K(eta): PASS; C7 limit H_{K,tau}(eta) -> 1 - e^{-1/eta}: PASS; C8 calibration thetabar = (eta(K-tau)+1)/K: PASS

**D 反例搜索**: random 2000, structured 6, violations 0, worst No violation and no slack on any equality: the error product eta_u*eta_o = rmax/rmin, the value F(K,0)/F(0,K) = H_{K,tau ...

**E 量词审计**: A_match=False; A_diffs: D1 tau 的整数 c 等式：正文 "tau=ceil(c)+1, which equals c+1 at integer c"，台账陈述行只有 "τ=⌈c⌉+1"；该半句承重（app:hardness 第 1603 至 1605 行的整数性消费点）; D2 K 与 n 的整数性：正文 "Let the integers K>tau and n>=4K^{c+2}"，台账陈述行不写（靠 model.tex 第 15 行继承）; D3 thetabar 的定义位置：台账把 θ̄=(η(K−τ)+ ...; GAP: GAP(陈述层) 1：随机版的期望没有写明对什么取。路线甲（app:hardness 第 1639、1652 至 1657 行）取的是算法自身 random seed 与均匀 O 的两次平均，最终给出固定实例上关于 seed 的期望；thm:hardness 的 environment 与台账 T10 陈述行都只写 "in expectation" / "随机版加 ε_n"（对照 T10b、T10c 卡写的是 E_seed）; GAP(陈述层) 2：随机版没有写"对任意随机算法存在实例"的量词顺序，也没有重述该实例的误差仍恰为 eta；两处都由路线甲给出，陈述层缺; 无 route-one G ...

**裁定理由**: C 8 项 PASS（J2/H3 复跑；非 binding 表：K=3,4 τ=2 η=3/2 不 binding，K ≥ 5 binding；H_{K,1}=U_K；极限）；D 2000 随机参数 0 违反；B-GAP：路线二未构造硬族且其 union bound 需 n ≥ 4K^{2τ}，判定人精确复算路线一在 n ≥ 4K^{c+2} 下失败概率 ≤ 9/32；E GAP：随机版期望对什么取与量词顺序未写。

**可写进正文的精确表述**: Let c >= 0 be real, tau = ceil(c) + 1, let K > tau and n >= 4K^{c+2} be integers, and let eta > 1 satisfy eta >= (K-1)/(K-tau). For every deterministic algorithm making at most n^c queries to f~, each on a set of size at most K, and outputting a set of size at most K, there is an instance with f monotone submodular, f(empty) = f~(empty) = 0, whose smallest admissible error factors have product exactly eta, on which f(T)/OPT <= H_{K,tau}(eta) = 1 - (1 - 1/(eta(K-tau)+1))^K; any prescribed split is realized by rescaling. For every randomized algorithm with the same budget there is a fixed instance with error exactly eta on which the expectation over the algorithm's own randomness satisfies E[f(T)/OPT] <= H_{K,tau}(eta) + K/n + K^{2tau+2}/((tau+1)! n^{tau+1-c}). H_{K,1} = U_K, and for fixed c and eta, H_{K,tau}(eta) -> 1 - e^{-1/eta}.

**K=3, η=3/2 走读**: thetabar = (3/2*2+1)/3 = 4/3, a = 1 - 1/(thetabar*K) = 3/4, A = a*K/(K-1) = 9/8, B = a^0 = 1, thetabar*A*B = 3/2 = eta (eta_o^2 = 27/16, eta_u^2 = 4/3). H_{3,1}(3/2) = 1 - (3/4)^3 = 37/64 = 0.578125 = U_3(3/2) = L_3(4/3), and this is exactly the ratio Fbar(3,0)/Fbar(0,3) attained by the balanced output. 1/eta = 2/3 = 0.666667 > 37/64, so this cell is binding and min{H, 1/eta} = 37/64.

### thm:linear-anysize (Proposition (J7)) — 最终标签 **[HAND-PROOF-UNREVIEWED]**

**陈述原文**

#### T10d thm:linear-anysize (J7)

- 正文环境: `theorem`, label `thm:linear-anysize`
- 台账卡: ## T10d thm:linear-anysize — 任意大小查询线性类的上界（J6/J7 日装配，来源 J7）

##### 台账陈述（逐字）

- 陈述：K ≥ 3，η > 1。记 α_lin(K,η) 为确定性、O(nK) 次**任意大小**查询、输出 ≤ K 元素的算法类
  在 n → ∞ 时的最优最坏近似比（随机算法按期望）。则
  ρ_K(η) ≤ α_lin(K,η) ≤ min{1/η, W_K(η)} ≤ min{1/η, ρ_K(η) + 1/(K(e^{K−1}−K−1))}。
  下界即 thm:exact（greedy 属于该类）；η ≥ K 时两端塌到 1/η。

##### 正文陈述（逐字，LaTeX）

```latex
\begin{theorem}[Arbitrary query sizes at linear budget]
\label{thm:linear-anysize}
Let $K\ge3$ and $\eta>1$, and let $\alpha_{\mathrm{lin}}(K,\eta)$ denote
the limit as $n\to\infty$ of the optimal worst-case ratio of deterministic
algorithms that make $O(nK)$ queries to $\tilde f$ \emph{of arbitrary
size} and output a set of size at most $K$, over instances with monotone
submodular $f$ and error product at most $\eta$ (randomized algorithms
measured in expectation over their own randomness).  Then
\[
  \rho_K(\eta)\;\le\;\alpha_{\mathrm{lin}}(K,\eta)\;\le\;
  \min\Bigl\{\frac1\eta,\;W_K(\eta)\Bigr\}
  \;\le\;
  \min\Bigl\{\frac1\eta,\;\rho_K(\eta)+\frac{1}{K\,\bigl(e^{K-1}-K-1\bigr)}\Bigr\},
\]
where $W_K(\eta)$ is the explicit constant of
Appendix~\ref{app:hardness-anysize}: even with arbitrary-size queries,
predictive greedy is optimal among algorithms of its own oracle
complexity up to an additive term exponentially small in $K$.  For
$\eta\ge K$ both ends equal $1/\eta$.
\end{theorem}
```

**路线一位置**: app:hardness-anysize + results/J7/linear_anysize.md

**B 路线二比对**: B-PASS-with-different-route; consistent=False, quantifiers=False; divergences: j 约定（实质差异，改变 W_K 的取值）：route one 用显式公式 j = max{0, min{K-1, K+1-ceil(eta)}}；route two 用「rho_K = min_j V_j 的 argmin，并列取最小 j」。template 在并列时未定义，两读法都合规。二者恰在整数 eta（2 <= eta <= K）上不同，且恒有 j_route1 = j_route2 + 1；此时 rho_K 相同但 W_K 不同，且 W_route1 < W_route2 严格。例 K=3, eta=2：W_route1 = 2003/4275，W_route2 = 403/855 ...; route-2 gaps: [FAILED] 步骤 D5 第 1 点的句子「alpha_{K+1} = 1」是错的。route two 只证明了在第 3 节的 hard family 上 n = K+1 时算法可达 ratio 1，但 alpha_{K+1} 是对全体实例取 inf 再对算法取 sup。用 route two 自己的 U1 族即可反驳：n = K+1 时 tilde f = /S//(eta K) 与 O 无关故 T 固定，/B/ = 1 使 /T ∩ O/ >= /T/ - 1，adversary 取最坏 O 得 alpha_{K+1} <= k_1/(K eta) = (eta(K-1)+1)/(K  ...

**C oracle**: C1 rerun results/J7_symbolic.py: PASS; C2 rerun results/J7_grid_check.py: PASS; C3 rerun results/J7_fragment_checks.py: PASS; C4 rerun results/J7_bound18_check.py: PASS; C5 F3 counterexample reproduced independently (K = 3, eta = 667/500): PASS; C6 running example K = 3, eta = 3/2: PASS; C7 own count-grid legality battery on the three D configurations: PASS; C8 own exact sweep of (5),(6),(7),(8),(17),(18) on 99 configurations: PASS; C9 sympy cross-check of the d-identities (7a), (7b), (8): PASS; C-residue: lift to set functions, leakage bound (16), canonical-transcript induction, averaging, lower-bound direction: GAP

**D 反例搜索**: random 300, structured 21, violations 0, worst "Leak-free regime (n >= K + t*): worst slack ratio - W_K(eta) = 0, attained everywhere, i.e. the ceiling W_K is met with ...

**E 量词审计**: A_match=False; A_diffs: D0 environment name: results.tex 884 uses \begin{proposition}, while the ledger card title and results/V11/statements.md line 319 metadata plus the LaTeX blocks in statements.md and inputs/statement_linear_anysize.md all use \begin{theorem}; apart fr ...; GAP: GAP-1 existence of the limit: the statement defines alpha_lin as the limit as n -> infinity, but the route-one material only sandwiches limsup <= min{1/eta, W_K} and liminf >= rho_K, with rho_K < W_K strict on all 140 exact configurations checked; no monotonicity-in-n or convergence argument anywher ...

**裁定理由**: C 9 项 PASS（J7 四脚本复跑 148/99/F3 反例/(18)；自写电池；n < K+t* 反向 greedy 恰达 1 复现）；D 300 随机任意大小策略 0 违反；B-PASS-with-different-route 但路线二含一句错误（α_{K+1} = 1，判定人反驳）且整数 η 处 j 约定不同（路线一的 j 给更小的 W_K，两者都合法）；E GAP-1：'limit' 的存在未证（只有 limsup/liminf 夹逼），GAP-2：无显式 n_0。

**可写进正文的精确表述**: Let K >= 3, eta > 1 and c >= 1, and for each n let alpha_n denote the optimal worst-case ratio of deterministic algorithms that make at most c n K queries to f~ of arbitrary size and output a set of size at most K, over instances on n elements with monotone submodular normalized f and error product at most eta. Then rho_K(eta) <= alpha_n for every n >= 2K, and limsup_{n -> infinity} alpha_n <= min{1/eta, W_K(eta)}, where W_K(eta) (the value of the explicit family of the appendix, with j = max{0, min{K-1, K+1-ceil(eta)}} and the Psi truncation rule) satisfies 0 < W_K(eta) - rho_K(eta) < 1/(K(e^{K-1}-K-1)); the upper bound holds for every n >= n_0 with n_0 = max{K + t*, ceil(c K^3 (t*+K)^2)} (explicit from the leakage count). For eta >= K both bounds equal 1/eta. Randomized algorithms obey the same upper bound in expectation. (Not claimed: a finite-n bound alpha_n <= W_K for all n, which fails for n < K + t*, nor the existence of lim alpha_n.)

**K=3, η=3/2 走读**: "K = 3, eta = 3/2: j = 2, m = 4 (Psi rule), t* = 6, q = 3/4, nu = 3, Q = 9/16, B_m = 116, d = 13/58, D = 117/928, C = 4/3.\nW_3(3/2) = F(3,0) = 523/928 = 9/16 + 1/928 (0.563577586), rho_3(3/2) = 9/16 (0.5625), gap = 1/928 (1.078e-3), and 523/928 < 2/3 = 1/eta.\nD at this eta: K + t* = 9, so n = 8 is the leak row (reverse greedy ratio 1) and n = 9..14 give fwd = rev = max = W exactly."

### J8 ProbeLottery (Proposition (J8)) — 最终标签 **[VERIFIED-ORACLE-ONLY]**

**陈述原文**

#### J8 ProbeLottery（陈述来源 HANDOFF_2026-09-18 §4；证明文件未送达）

**Proposition (ProbeLottery).** Let $K=2$ and $\eta=3/2$. There is a randomized algorithm, ProbeLottery,
that makes at most $9n$ queries to $\tilde f$, each on a set of size at most $5$, outputs a set of size
$2$, and satisfies on every instance $(f,\tilde f)$ with $f$ monotone submodular, $f(\emptyset)=0$, and
$\tilde f$ of error at most $\eta=3/2$ (Definition 1, any split with $\eta_u\eta_o=3/2$; in particular
$d_e(S)\le\tilde d_e(S)\le\tfrac32 d_e(S)$ after rescaling):
$$\mathbb E[f(T)]\;\ge\;\Bigl(\tfrac35+\tfrac{1}{400000}\Bigr)\,\mathrm{OPT},$$
the expectation over the algorithm's own randomness only. Since $\rho_2(3/2)=3/5$ is the exact worst
case of predictive greedy, this shows the query-size restriction $|S|\le K$ of the linear-budget
optimality theorem is necessary for randomized algorithms with budget $\tfrac92 nK$.
(Source: HANDOFF_2026-09-18 section 4; the proof file J8_probe_lottery.md with inequalities (3),(8)-(12)
was not delivered. On the tight $K=2,\eta=3/2$ instance the implemented algorithm attains exactly
$3/5+1/2048$.)

**路线一位置**: GAP: proof file undelivered; results/J8/J8_claude_spotcheck.py

**B 路线二比对**: B-MISSING (no route one); consistent=False, quantifiers=False; divergences: D1 路线一不存在：results/J8/probe_lottery.md 与不等式 (3),(8)-(12) 未交付，仓库只有 J8_claude_spotcheck.py + run.log + HANDOFF 2026-09-18 section 4 的一行状态，criterion B 的对偶证书无法组装; D2 紧实例不同：路线一用 J6 double-residual 族 (n=6,8,12,20，/C/=5,7,11,19，r=4，max query size 5) 取到 3/5+1/2048；路线二自造 n=4 coverage 实例 (/C/=2，r=2，max query s ...; route-2 gaps: G1 主缺口，情形 II-b 未闭合 [FAILED]：需要 o_1,o_2 在 pool C 内且 eps < 4.0945e-6 时四轮 extension 至少一轮取到某个 o_i。挡路必要条件 (3/2) d_{v_k}(B) >= d_o(B) 与 L5 给 f(B) 链 3/5 -> 11/15 -> 37/45 -> 119/135（本轮复算无误），但 119/135 = 0.8815 < 1 且 /B/ >= 3 时 f 可超过 OPT，不产生矛盾。该格只得 E >= (3/5 - 1.5625e-6) OPT，比目标低 4.0625e-6。本轮补充的收紧条件：II-b 强迫  ...

**C oracle**: C1 tight instance (K=2, eta=3/2 double-residual family, j=1), n in {6,8,12,20} plus 7,9,10,11: PASS; C1b 紧实例合法性（f 单调 submodular + band）: PASS; C2 随机合法实例（K=2, eta=3/2, n=8..12，三族）: PASS; C3 结构化案例（eta=1 的 n=4,5；紧实例 n=6..12；E4 的两个实例族在 K=2, eta=3/2）: PASS; C4 算法 contract（输出集大小 2、总质量 1、queries <= 9n、被查询集合大小 <= 5）: PASS; C5 复跑 results/J8/J8_claude_spotcheck.py（子进程，不修改不 import）: PASS; G1 路线甲：不等式 (3)、(8)-(12) 的 LP 对偶证书: GAP

**D 反例搜索**: random 2100, structured 8, violations 0, worst 全局最差比值 6149/10240 = 3/5 + 1/2048 ≈ 0.60048828，来自紧实例本身（n = 8，B 优先的 tie order，anchors = [0,1,6,2,3]，E = 6149/10240，OPT = 1 ...

**E 量词审计**: A_match=False; A_diffs: D0 正文缺失：paper/sections/results.tex 无任何 ProbeLottery environment（全 paper/ 目录检索 Probe、lottery 零命中），正文侧量词集合为空集; D1 台账缺失：THEOREM_LEDGER.md 无 J8 卡（卡号只有 T0 至 T15，全文检索 Probe/lottery/9n/400000/2048 零命中），台账侧量词集合为空集；两个列表不可能重合，故 A_match = false; D2 矩阵陈述比 HANDOF ...; GAP: eta = 3/2 固定：无为何 3/2 的论证，只有两族有限实例; error at most eta：Definition 1 band 的全称量词如何进入不等式无出处; 拆分 (eta_u, eta_o) 任意：只覆盖 eta_u = 1 一个端点，缩放不变性由本审计补测; on every instance (f, f~)：全称量词无证明，只有有限实例; f monotone submodular：无证明; f(empty) = 0：normalization 的使用处无出处; OPT > 0：隐含条件未陈述，脚本直接相除; 结论常数 3/5 + 1/400000：不等式 (3)、(8 ...

**裁定理由**: C：紧实例恰 3/5 + 1/2048（n = 6..12）、2100 个随机合法实例 0 违反且最差恰为紧实例、算法 contract（≤ 9n 次、|S| ≤ 5、输出 2-集）全过；路线一缺失（证明文件未送达，对偶证书 GAP）；盲审 PARTIAL（II-b 一格差 4.1e−6 未闭合）；台账无卡、正文无环境。不可原样写进正文。

**可写进正文的精确表述**: Cannot be written into the paper on the repository's evidence: the proof is undelivered. Claim as delivered: for K = 2 and eta = 3/2, the randomized algorithm ProbeLottery (as implemented in results/J8/J8_claude_spotcheck.py) makes at most 9n queries, each on a set of size at most 5, outputs a 2-set, and on every instance with f monotone submodular, f(empty) = 0, and f~ satisfying Definition 1 with product 3/2 satisfies E_seed[f(T)] >= (3/5 + 1/400000) OPT; hence the query-size restriction of Theorem thm:linear-exact is necessary for randomized algorithms with budget (9/2) n K. Evidence: tight instance exactly 3/5 + 1/2048; 2100 random legal instances without violation; blind derivation closes every case except case II-b (reaches only 3/5 - 1.6e-6 there).

**K=3, η=3/2 走读**: K = 3、eta = 3/2 不在本命题范围内（命题只声称 K = 2，K >= 3 与确定性版本仍 [OPEN]），下面是对照值。 k1 = 4，q = 3/4，V_0 = 2/3、V_1 = 7/12、V_2 = 9/16，故 rho_3(3/2) = 9/16 = 0.5625，信息价格 1/eta = 2/3。 对应 K = 2：rho_2(3/2) = 3/5，ProbeLottery 在紧实例取 6149/10240 = 3/5 + 1/2048，声称 bound 为 3/5 + 1/400000。


## 重点发现（供作者判断；不进正文）

1. 三把尺子在方案二下的定义细节（prop:guarantee，B 比对新发现）：路线二把 η^tr 的两个因子各自截断到 1，方案二下序关系 L_K(η^sel) ≥ L_K(η^tr) ≥ L_K(η) 会反向（f̃ = 2f：全局 (η_u,η_o) = (1/2, 2)、η = 1，逐因子截断的 η^tr = 2 > 1 [VERIFIED-EXHAUSTIVE]）。正文写 η^tr 的定义时必须把截断放在乘积上。
2. thm:linear-anysize（E 审计 GAP-1）：陈述把 α_lin 定义为 n → ∞ 的极限，但路线一只给出 limsup ≤ min{1/η, W_K} 与 liminf ≥ ρ_K，没有任何收敛或单调性论证；可写进正文的形式是 limsup/liminf 或 'for all sufficiently large n'（矩阵表述列已改写）。
3. J8（盲审 PARTIAL）：情形 II-b（o_1、o_2 都进 pool 且四轮 extension 全被其他 pool 元素占据）只得到 E ≥ (3/5 − 1.5625e−6)·OPT，比目标 3/5 + 2.5e−6 低 4.1e−6；未找到反例（显式 n=7 候选不可行），2100 个随机合法实例最差恰为紧实例 3/5 + 1/2048。未送达的证明必须覆盖该格。
4. thm:exact（B 比对）：路线二用不同的 LP 与对偶支撑（sum + cons + mono，不用 pred，单调乘子非零）也得到 ρ_K；台账 T6 副产品句'下界证书中单调约束乘子恒为零'只对路线一的约束集成立，不是定理性质。
5. thm:linear-exact（B 比对）：盲审代理走了'全部大小 size-only'路线并撞上强制超额（与第十晚 W 现象同源），未复现 J6 的 small-set-only 机制；判定人复核路线一正确。J6 的关键洞察（只在 |S| ≤ K 要求不可区分）不是盲审能自动到达的，正文应明说。
6. thm:hardness（B 比对）：路线二的 union bound 只能给 n ≥ 4K^{2τ}，判定人精确复算路线一的 level-(τ+1) 计数在 n ≥ 4K^{c+2} 下总失败概率 ≤ 9/32（c = 0..3、K ≤ 29 逐点），陈述阈值成立；路线二未构造出显式硬族。
7. thm:ceiling（E 审计）：正文 K ≥ 2 的限定在证明中无处使用（K = 1 全过 oracle），按 addendum B.3 写 K ≥ 1；'error exactly (η_u,η_o)' 在 def:eta 无定义，需一句'最小可行因子对恰为'；随机段落缺'条件于随机串'一步。
8. prop:necessity（E 审计）：|T| ≤ K 在陈述里未写（允许 |T| > K 则 T = N 反驳）；'no constant' 的量词（固定 K、n → ∞）未写；addendum B.9 措辞未落实。两个构造（γ = K²/(n(n−K)) 与 δ = K/(n−K)）同属一族的两个参数点，建议保留 δ 版并随 app:model 接线删除 γ 版。
9. prop:valueacc（E 审计）：(i) 需 n ≥ 2；(ii) 需 f 不恒零；正文仍是旧约定文本，与台账方案二陈述不一致（待作者改正文）。
10. cor:limit（E 审计）：K 的下端未写（ρ_K 闭式只对 K ≥ 2，1 ≤ η < 2 时平台子句涉及 K = 1 的 ρ_1 = 1/η 只在 T10b 卡）；'monotone in K' 无方向。
11. 引文（citations.md）：GS 2007 Theorem 1 已核（全文 PDF）；Horel–Singer 的 (1−ε)/(1+ε) 观察在 Section 1 引言段'Optimization of approximate submodularity'；greedy 阈值 ε ≤ 1/k 的正面保证是 **Theorem 5**，Proposition 6 只是紧性；horel2016maximization 的页码 3045–3053 未能核实 [CITATION-NEEDS-VERIFICATION]。
12. 模板噪声：盲审代理的通用提示里含'K = 2 for the ProbeLottery item'一句，非 J8 项的代理把它记为 FAILED 子项；这是提示模板的 artifact，不计入任何陈述的 GAP。

## 缺失与限制

- J8：证明文件 results/J8/probe_lottery.md 未送达，路线一为 GAP；(3)、(8)–(12) 的 LP 对偶证书无法给出。
- J9（Q11）：证明文件未送达；C1 内联不等式已过，盲审路线二 PARTIAL（results/V11/route2/j9.md），不入矩阵主表。
- 盲审子代理输入清单（TASKS11 要求记录）：results/V11/inputs/{definition1,assumptions,notation}.md + statement_<key>.md（linear_anysize 另给 anysize_template.md；j9 用 statement_j9.md）。子代理被禁止读取其他任何文件；每份 route2/<key>.md 末尾列出实际读过的文件。
- 标签口径：TASKS11 五项规则严格执行；"裁定理由"列说明 GAP 的性质（陈述措辞 vs 证明缺口）与一行修订后可达的标签。

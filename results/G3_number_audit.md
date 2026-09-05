# G3 数字字面量审计（number literal audit）

一键复现：`python3 results/G3_number_audit.py --write`

目的：正文里每个实验数字都必须来自 `paper/sections/numbers.tex` 的宏（由 `results/G3_gen_numbers.py` 生成）。本脚本扫描下面三个文件的**可见正文**（先剥掉 LaTeX comment），逐个数字字面量分类，要求 **非白名单的 experiment-number literal 计数 = 0**。

扫描范围（与 `results/G1_pagebudget.md` 的结构决定一致）：`experiments.tex`、`results.tex`、`model.tex`。

## 结论

- 命中的数字字面量总数：**138**
- 非白名单（VIOLATION）计数：**0**
- `experiments.tex` 的非白名单计数：**0**

**通过。** 三个文件的可见正文里没有任何非白名单数字字面量。`experiments.tex` 的每个实验数字都是 numbers.tex 的宏，连 budget K 也走宏（`\EOneKMain` 等），所以 K 白名单在该文件一次都没被用到。

## 白名单类别（每类的理由）

| 类别 | 含义 | 为什么不算 experiment number |
|---|---|---|
| `structure` | `\label` / `\ref` / `\input` / `\includegraphics` / `\begin` / `\end` / `\caption` 的参数 | 不是正文可见文字，是 cross-reference 与文件名 |
| `citation` | `\citep[...]` / `\citet[...]` 的可选参数 | 页码或定理号 locator（如 `[Theorem~3]`），属于引用定位 |
| `length` | 带 TeX 长度单位或 `\textwidth` 系数（`0.66\textwidth`、`4pt`） | 排版长度，不是测量值 |
| `K value/index` | budget K 与上下标索引（`K=5`、`L_{30}`、`V_j`） | 结构性参数与索引，不是实验测量 |
| `theory const` | 仅限 `results.tex` / `model.tex` 的 math mode 字面量 | 定理里的 closed-form 系数与模型常数，其状态由文件内注明的 oracle 脚本（LP / sympy / 穷举）决定，不是实验数字 |
| `proper name` | 名称里的数字（`ROUGE-1`, `digits20`, `email-Eu-core`） | 名称的一部分，不是数值 |

注意：`theory const` 这条白名单**不适用于** `experiments.tex`。在该文件里，任何不是 K 值的 math mode 字面量都判 VIOLATION，这正是"计数为 0"这句话有意义的原因。

## 反向自检（negative control）

白名单只有在遇到真违规时仍会报警才有意义，所以脚本每次运行都对一段合成文本做自检：三行含 `0.971`、`2.0`、`120`、`0.008` 的正文（其中一行是 comment，不应报），以及一段只含合法写法的文本（`K=\ETwoKMain`、`L_{30}`、`V_0`、`0.66\textwidth`、`\citep[Theorem~3]{...}`、`ROUGE-1`、`\label{...}`）。

- 应报而报出的违规：`0.008`, `0.971`, `120`, `2.0`
- 合法写法里被误报的：**0**
- 自检结论：**通过**

## 逐文件统计

| file | 命中总数 | structure | citation | length | K value/index | theory const | proper name | VIOLATION |
|---|---|---|---|---|---|---|---|---|
| `experiments.tex` | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| `results.tex` | 120 | 0 | 1 | 0 | 17 | 102 | 0 | 0 |
| `model.tex` | 16 | 0 | 0 | 0 | 2 | 14 | 0 | 0 |

## 附加扫描（不计入要求，仅供参考）

| file | 命中总数 | VIOLATION |
|---|---|---|
| `appendix_experiments.tex` | 2 | 0 |

`appendix_experiments.tex` 按与正文同一条规则写（数字全部走宏），但 TASKS5 G3.4 规定的扫描范围只有上面三个文件，故单列。注意该文件是 appendix，`theory const` 白名单在这里同样不放宽：脚本对它按非 results/model 文件处理。

## 生成文件（不计入上表，数字是脚本产出而非手打）

| file | 数字字面量数 | 生成脚本 |
|---|---|---|
| `paper/sections/numbers.tex` | 107 | `results/G3_gen_numbers.py` |
| `paper/sections/EXP_table.tex` | 38 | `results/EXP_table_build.py` → 由 `results/G3_gen_numbers.py` 复制并把 `$\eta^{sel}$` 改写成 `\etasel` |

Table~1 的每个数字都由 `results/EXP_table_build.py` 从 `results/E{1,2,3}_rows.csv` 与 `results/E4_worst_case.csv` 重算，**算作 scripted，不算 hand-typed**。表注原样保留、一字未改：note (i) ratio 的分母是 greedy-on-$f$，是 OPT 的 upper-estimate proxy；note (ii) $\etasel$ 只定义在正增益步上，故 $L_K$ 列的陈述只覆盖那些步，末列报 $d_t \le 0$ 步的占比；note (iii) influence maximization 的 sign-viol. 列写 “--” 而不是测出来的 0（两个 coverage 函数结构上不可能反号）。前两条即 TASKS5 G3 指定必须保留的两句。

## 全部命中明细

| file | line | literal | 类别 | 理由 | context |
|---|---|---|---|---|---|
| `experiments.tex` | 62 | `1` | proper name | digit inside a proper name | `summarization:} $f$ is the ROUGE-1 F score against a ref` |
| `experiments.tex` | 152 | `1` | proper name | digit inside a proper name | `ThreeStructMaxSetSize$, the ROUGE-1 F score violates subm` |
| `results.tex` | 36 | `0` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `one submodular with $f(\emptyset)=0$ and let $T=S^{K}$ be` |
| `results.tex` | 38 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `is $\etasel$. Then, with $L_K(x)=1-(1-\tfrac1{xK})^{K}$,` |
| `results.tex` | 38 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$\etasel$. Then, with $L_K(x)=1-(1-\tfrac1{xK})^{K}$, \[` |
| `results.tex` | 41 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `asel)\,f(O^{\ast}) \;\ge\;\bigl(1-e^{-1/\etasel}\bigr)f` |
| `results.tex` | 41 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `,f(O^{\ast}) \;\ge\;\bigl(1-e^{-1/\etasel}\bigr)f(O^{\a` |
| `results.tex` | 49 | `1` | citation | page or theorem locator of a citation | `Goundan and Schulz \citep[Theorem~1]{goundan2007revisitin` |
| `results.tex` | 69 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `ss} For every $K\ge2$ and $\hat a>1$ there is an instance` |
| `results.tex` | 70 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `is an instance $(f,\tilde f)$ on $2K$ elements with $\eta` |
| `results.tex` | 91 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `, \qquad \text{(ii)}\;\;\bigl(1-\tfrac1\eta\bigr)\,d_` |
| `results.tex` | 103 | `1` | K value/index | budget K or a sub/superscript index | `For $K\ge2$, $\eta\ge1$, let $k_1=(K-1)\eta+1$, $q=(K-1` |
| `results.tex` | 103 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$K\ge2$, $\eta\ge1$, let $k_1=(K-1)\eta+1$, $q=(K-1)\eta` |
| `results.tex` | 103 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$, $\eta\ge1$, let $k_1=(K-1)\eta+1$, $q=(K-1)\eta/k_1$,` |
| `results.tex` | 103 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `e1$, let $k_1=(K-1)\eta+1$, $q=(K-1)\eta/k_1$, and for $0` |
| `results.tex` | 103 | `1` | K value/index | budget K or a sub/superscript index | `$k_1=(K-1)\eta+1$, $q=(K-1)\eta/k_1$, and for $0\le j\le` |
| `results.tex` | 104 | `0` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `a+1$, $q=(K-1)\eta/k_1$, and for $0\le j\le K-1$ \[ V_j` |
| `results.tex` | 104 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `1)\eta/k_1$, and for $0\le j\le K-1$ \[ V_j(\eta)\;=\;1` |
| `results.tex` | 106 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `0\le j\le K-1$ \[ V_j(\eta)\;=\;1-q^{\,j}\Bigl(1-\frac{` |
| `results.tex` | 106 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `\[ V_j(\eta)\;=\;1-q^{\,j}\Bigl(1-\frac{K-j}{K\eta}\Big` |
| `results.tex` | 112 | `0` | K value/index | budget K or a sub/superscript index | `king, \[ \rho_K(\eta)\;=\;\min_{0\le j\le K-1}V_j(\eta)` |
| `results.tex` | 112 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `rho_K(\eta)\;=\;\min_{0\le j\le K-1}V_j(\eta), \] and the` |
| `results.tex` | 115 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$ on the segment $\eta\in[K-j,K-j+1]$ (with $V_0=1/\eta$` |
| `results.tex` | 115 | `0` | K value/index | budget K or a sub/superscript index | `ent $\eta\in[K-j,K-j+1]$ (with $V_0=1/\eta$ on $[K,\infty` |
| `results.tex` | 115 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `t $\eta\in[K-j,K-j+1]$ (with $V_0=1/\eta$ on $[K,\infty)$` |
| `results.tex` | 116 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `the breakpoints are the integers $2,\dots,K$. In particu` |
| `results.tex` | 117 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `,K$. In particular $\rho_K(\eta)=1/\eta$ exactly when $\` |
| `results.tex` | 117 | `2` | K value/index | budget K or a sub/superscript index | `when $\eta\ge K$, and for $K\in\{2,3,4\}$ the closed for` |
| `results.tex` | 117 | `3` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `hen $\eta\ge K$, and for $K\in\{2,3,4\}$ the closed forms` |
| `results.tex` | 117 | `4` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `n $\eta\ge K$, and for $K\in\{2,3,4\}$ the closed forms a` |
| `results.tex` | 119 | `2` | K value/index | budget K or a sub/superscript index | `3,4\}$ the closed forms are $\rho_2=\min\{\tfrac1\eta,\tf` |
| `results.tex` | 119 | `3` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$\rho_2=\min\{\tfrac1\eta,\tfrac{3}{2(\eta+1)}\}$, $\rho` |
| `results.tex` | 119 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `rho_2=\min\{\tfrac1\eta,\tfrac{3}{2(\eta+1)}\}$, $\rho_3=` |
| `results.tex` | 119 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `min\{\tfrac1\eta,\tfrac{3}{2(\eta+1)}\}$, $\rho_3=\tfrac{` |
| `results.tex` | 120 | `3` | K value/index | budget K or a sub/superscript index | `ta,\tfrac{3}{2(\eta+1)}\}$, $\rho_3=\tfrac{16\eta+3}{3(2\` |
| `results.tex` | 120 | `16` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `{3}{2(\eta+1)}\}$, $\rho_3=\tfrac{16\eta+3}{3(2\eta+1)^2}$` |
| `results.tex` | 120 | `3` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `eta+1)}\}$, $\rho_3=\tfrac{16\eta+3}{3(2\eta+1)^2}$, $\tf` |
| `results.tex` | 120 | `3` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `+1)}\}$, $\rho_3=\tfrac{16\eta+3}{3(2\eta+1)^2}$, $\tfrac` |
| `results.tex` | 120 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `)}\}$, $\rho_3=\tfrac{16\eta+3}{3(2\eta+1)^2}$, $\tfrac{7` |
| `results.tex` | 120 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$\rho_3=\tfrac{16\eta+3}{3(2\eta+1)^2}$, $\tfrac{7}{3(2\` |
| `results.tex` | 120 | `2` | K value/index | budget K or a sub/superscript index | `rho_3=\tfrac{16\eta+3}{3(2\eta+1)^2}$, $\tfrac{7}{3(2\eta` |
| `results.tex` | 120 | `7` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `16\eta+3}{3(2\eta+1)^2}$, $\tfrac{7}{3(2\eta+1)}$, $\tfra` |
| `results.tex` | 120 | `3` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `eta+3}{3(2\eta+1)^2}$, $\tfrac{7}{3(2\eta+1)}$, $\tfrac1\` |
| `results.tex` | 120 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `a+3}{3(2\eta+1)^2}$, $\tfrac{7}{3(2\eta+1)}$, $\tfrac1\et` |
| `results.tex` | 120 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `(2\eta+1)^2}$, $\tfrac{7}{3(2\eta+1)}$, $\tfrac1\eta$ on` |
| `results.tex` | 121 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `{3(2\eta+1)}$, $\tfrac1\eta$ on $[1,2],[2,3],[3,\infty)$,` |
| `results.tex` | 121 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `(2\eta+1)}$, $\tfrac1\eta$ on $[1,2],[2,3],[3,\infty)$, a` |
| `results.tex` | 121 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `ta+1)}$, $\tfrac1\eta$ on $[1,2],[2,3],[3,\infty)$, and $` |
| `results.tex` | 121 | `3` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `+1)}$, $\tfrac1\eta$ on $[1,2],[2,3],[3,\infty)$, and $\r` |
| `results.tex` | 121 | `3` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$, $\tfrac1\eta$ on $[1,2],[2,3],[3,\infty)$, and $\rho_4` |
| `results.tex` | 122 | `4` | K value/index | budget K or a sub/superscript index | `1,2],[2,3],[3,\infty)$, and $\rho_4=\tfrac{135\eta^2+36\e` |
| `results.tex` | 122 | `135` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `],[3,\infty)$, and $\rho_4=\tfrac{135\eta^2+36\eta+4}{4(3\e` |
| `results.tex` | 122 | `2` | K value/index | budget K or a sub/superscript index | `fty)$, and $\rho_4=\tfrac{135\eta^2+36\eta+4}{4(3\eta+1)^` |
| `results.tex` | 122 | `36` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `y)$, and $\rho_4=\tfrac{135\eta^2+36\eta+4}{4(3\eta+1)^3}$` |
| `results.tex` | 122 | `4` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `d $\rho_4=\tfrac{135\eta^2+36\eta+4}{4(3\eta+1)^3}$, $\tf` |
| `results.tex` | 122 | `4` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `\rho_4=\tfrac{135\eta^2+36\eta+4}{4(3\eta+1)^3}$, $\tfrac` |
| `results.tex` | 122 | `3` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `ho_4=\tfrac{135\eta^2+36\eta+4}{4(3\eta+1)^3}$, $\tfrac{2` |
| `results.tex` | 122 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `tfrac{135\eta^2+36\eta+4}{4(3\eta+1)^3}$, $\tfrac{21\eta+` |
| `results.tex` | 122 | `3` | K value/index | budget K or a sub/superscript index | `ac{135\eta^2+36\eta+4}{4(3\eta+1)^3}$, $\tfrac{21\eta+2}{` |
| `results.tex` | 123 | `21` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `36\eta+4}{4(3\eta+1)^3}$, $\tfrac{21\eta+2}{2(3\eta+1)^2}$` |
| `results.tex` | 123 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `4}{4(3\eta+1)^3}$, $\tfrac{21\eta+2}{2(3\eta+1)^2}$, $\tf` |
| `results.tex` | 123 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `4(3\eta+1)^3}$, $\tfrac{21\eta+2}{2(3\eta+1)^2}$, $\tfrac` |
| `results.tex` | 123 | `3` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `3\eta+1)^3}$, $\tfrac{21\eta+2}{2(3\eta+1)^2}$, $\tfrac{1` |
| `results.tex` | 123 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `1)^3}$, $\tfrac{21\eta+2}{2(3\eta+1)^2}$, $\tfrac{13}{4(3` |
| `results.tex` | 123 | `2` | K value/index | budget K or a sub/superscript index | `3}$, $\tfrac{21\eta+2}{2(3\eta+1)^2}$, $\tfrac{13}{4(3\et` |
| `results.tex` | 123 | `13` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `21\eta+2}{2(3\eta+1)^2}$, $\tfrac{13}{4(3\eta+1)}$, $\tfra` |
| `results.tex` | 123 | `4` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `ta+2}{2(3\eta+1)^2}$, $\tfrac{13}{4(3\eta+1)}$, $\tfrac1\` |
| `results.tex` | 123 | `3` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `+2}{2(3\eta+1)^2}$, $\tfrac{13}{4(3\eta+1)}$, $\tfrac1\et` |
| `results.tex` | 123 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `3\eta+1)^2}$, $\tfrac{13}{4(3\eta+1)}$, $\tfrac1\eta$ on` |
| `results.tex` | 124 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `{4(3\eta+1)}$, $\tfrac1\eta$ on $[1,2],[2,3],[3,4],[4,\in` |
| `results.tex` | 124 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `(3\eta+1)}$, $\tfrac1\eta$ on $[1,2],[2,3],[3,4],[4,\inft` |
| `results.tex` | 124 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `ta+1)}$, $\tfrac1\eta$ on $[1,2],[2,3],[3,4],[4,\infty)$.` |
| `results.tex` | 124 | `3` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `+1)}$, $\tfrac1\eta$ on $[1,2],[2,3],[3,4],[4,\infty)$. \` |
| `results.tex` | 124 | `3` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$, $\tfrac1\eta$ on $[1,2],[2,3],[3,4],[4,\infty)$. \end{` |
| `results.tex` | 124 | `4` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$\tfrac1\eta$ on $[1,2],[2,3],[3,4],[4,\infty)$. \end{th` |
| `results.tex` | 124 | `4` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `frac1\eta$ on $[1,2],[2,3],[3,4],[4,\infty)$. \end{theore` |
| `results.tex` | 142 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `} $L_K$ and $\rho_K$ differ by $O(1/K)$ for fixed $\eta$,` |
| `results.tex` | 144 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `it family attains only $U_K(\eta)=1-(1-\tfrac{1}{\eta(K-1` |
| `results.tex` | 144 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `family attains only $U_K(\eta)=1-(1-\tfrac{1}{\eta(K-1)+1` |
| `results.tex` | 144 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `tains only $U_K(\eta)=1-(1-\tfrac{1}{\eta(K-1)+1})^{K}$,` |
| `results.tex` | 144 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$U_K(\eta)=1-(1-\tfrac{1}{\eta(K-1)+1})^{K}$, which is s` |
| `results.tex` | 144 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `_K(\eta)=1-(1-\tfrac{1}{\eta(K-1)+1})^{K}$, which is stri` |
| `results.tex` | 145 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `}$, which is strictly above $V_{K-1}$ for every $\eta>1$.` |
| `results.tex` | 145 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `y above $V_{K-1}$ for every $\eta>1$.` |
| `results.tex` | 150 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `ase strictly improves for $\eta<K-1$: at $K=3$, $\eta=1.5` |
| `results.tex` | 150 | `3` | K value/index | budget K or a sub/superscript index | `ly improves for $\eta<K-1$: at $K=3$, $\eta=1.5$ the valu` |
| `results.tex` | 150 | `1.5` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `s for $\eta<K-1$: at $K=3$, $\eta=1.5$ the value rises from` |
| `results.tex` | 151 | `9` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$\eta=1.5$ the value rises from $9/16$ to $19/33$` |
| `results.tex` | 151 | `16` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `\eta=1.5$ the value rises from $9/16$ to $19/33$` |
| `results.tex` | 151 | `19` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$ the value rises from $9/16$ to $19/33$` |
| `results.tex` | 151 | `33` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `he value rises from $9/16$ to $19/33$` |
| `results.tex` | 165 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `\subsection{The $1/\eta$ ceiling}\label{` |
| `results.tex` | 167 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `ing} \begin{theorem}[Ceiling at $1/\eta$]\label{thm:ceil` |
| `results.tex` | 172 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `ed algorithms the bound becomes $(1-\tfrac Kn)\tfrac1\eta` |
| `results.tex` | 185 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$ and $\rho_K(\eta)$ converge to $1-e^{-1/\eta}$ as $K\to` |
| `results.tex` | 185 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$\rho_K(\eta)$ converge to $1-e^{-1/\eta}$ as $K\to\infty` |
| `results.tex` | 198 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `. For $\theta\ge1$ let $a_\theta=1-\tfrac1{\theta K}$, $` |
| `results.tex` | 199 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$a_\theta=1-\tfrac1{\theta K}$, $1+\delta(\theta)=\max\{` |
| `results.tex` | 200 | `1` | K value/index | budget K or a sub/superscript index | `\tau}\tfrac{K}{K-\tau}, a_\theta^{1-\tau}\}^{2}$ and $\Ph` |
| `results.tex` | 200 | `2` | K value/index | budget K or a sub/superscript index | `{K}{K-\tau}, a_\theta^{1-\tau}\}^{2}$ and $\Phi(\theta)=\` |
| `results.tex` | 200 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `}\}^{2}$ and $\Phi(\theta)=\theta(1+\delta(\theta))$. \b` |
| `results.tex` | 203 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `ardness} Fix $c\ge0$, put $\tau=c+1$, and let $K\ge2\tau$` |
| `results.tex` | 203 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `1$, and let $K\ge2\tau$ and $\eta>1$ satisfy $\Phi(1)\le\` |
| `results.tex` | 204 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `2\tau$ and $\eta>1$ satisfy $\Phi(1)\le\eta$ (sufficient:` |
| `results.tex` | 204 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `1)\le\eta$ (sufficient: $K\ge\tau(1+\tfrac{2}{\ln\eta})$)` |
| `results.tex` | 204 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$ (sufficient: $K\ge\tau(1+\tfrac{2}{\ln\eta})$), so that` |
| `results.tex` | 205 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `eta})$), so that $\hat\eta=\Phi^{-1}(\eta)\in[1,\eta]$ is` |
| `results.tex` | 205 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `that $\hat\eta=\Phi^{-1}(\eta)\in[1,\eta]$ is well define` |
| `results.tex` | 205 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `is well defined. Let $n\ge4K^{c+2}$. For every determin` |
| `results.tex` | 214 | `2` | K value/index | budget K or a sub/superscript index | `\varepsilon_n=\tfrac Kn+\tfrac{K^{2c+4}}{(c+2)!\,n^{2}}$` |
| `results.tex` | 214 | `4` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `repsilon_n=\tfrac Kn+\tfrac{K^{2c+4}}{(c+2)!\,n^{2}}$ in` |
| `results.tex` | 214 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `n_n=\tfrac Kn+\tfrac{K^{2c+4}}{(c+2)!\,n^{2}}$ in expecta` |
| `results.tex` | 214 | `2` | K value/index | budget K or a sub/superscript index | `ac Kn+\tfrac{K^{2c+4}}{(c+2)!\,n^{2}}$ in expectation. Mo` |
| `results.tex` | 215 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `. Moreover $K\delta(\eta)\to\max\{2\tau(1-\tfrac1\eta),\t` |
| `results.tex` | 215 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `over $K\delta(\eta)\to\max\{2\tau(1-\tfrac1\eta),\tfrac{2` |
| `results.tex` | 215 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `\max\{2\tau(1-\tfrac1\eta),\tfrac{2(\tau-1)}\eta\}$ and $` |
| `results.tex` | 215 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `\tau(1-\tfrac1\eta),\tfrac{2(\tau-1)}\eta\}$ and $L_K(\ha` |
| `results.tex` | 216 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `eta\}$ and $L_K(\hat\eta)\to1-e^{-1/\eta}$ as $K\to\infty` |
| `results.tex` | 228 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `error level $\eta$ is pinned to $1-e^{-1/\eta}$ asymptot` |
| `results.tex` | 228 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `level $\eta$ is pinned to $1-e^{-1/\eta}$ asymptotically` |
| `results.tex` | 229 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `reedy achieves $L_K(\eta)\to1-e^{-1/\eta}$ with $K$ evalu` |
| `results.tex` | 231 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `et exceeds $L_K(\hat\eta)\to1-e^{-1/\eta}$. At finite $K` |
| `model.tex` | 9 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$\|N\|=n$, a monotone submodular $f:2^{N}\to\mathbb R_{\ge0` |
| `model.tex` | 10 | `0` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `thbb R_{\ge0}$ with $f(\emptyset)=0$, and a cardinality b` |
| `model.tex` | 12 | `2` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `only query a predictor $\tilde f:2^{N}\to\mathbb R$ with` |
| `model.tex` | 12 | `0` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `thbb R$ with $\tilde f(\emptyset)=0$. Marginal gains are` |
| `model.tex` | 26 | `0` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `,d_e(S). \] In particular $d_e(S)=0$ forces $\tilde d_e(S` |
| `model.tex` | 26 | `0` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `$d_e(S)=0$ forces $\tilde d_e(S)=0$, and all predicted g` |
| `model.tex` | 30 | `0` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `n ratios are stated as $\alpha\in(0,1]$ with $F^{\mathrm{` |
| `model.tex` | 30 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `ratios are stated as $\alpha\in(0,1]$ with $F^{\mathrm{AL` |
| `model.tex` | 36 | `0` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `greedy run on $\tilde f$: for $t=0,\dots,K-1$ it adds an` |
| `model.tex` | 36 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `n on $\tilde f$: for $t=0,\dots,K-1$ it adds an element m` |
| `model.tex` | 42 | `0` | K value/index | budget K or a sub/superscript index | `predictive greedy with states $S^{0},\dots,S^{K-1}$ and p` |
| `model.tex` | 42 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `edy with states $S^{0},\dots,S^{K-1}$ and picks $e_{0},\d` |
| `model.tex` | 42 | `0` | K value/index | budget K or a sub/superscript index | `^{0},\dots,S^{K-1}$ and picks $e_{0},\dots,e_{K-1}$, the` |
| `model.tex` | 42 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `K-1}$ and picks $e_{0},\dots,e_{K-1}$, the selection erro` |
| `model.tex` | 45 | `0` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `^{t}) \;:\;t<K,\ d_{e_t}(S^{t})>0\Bigr\}\;\ge\;1 , \] t` |
| `model.tex` | 45 | `1` | theory const | closed-form coefficient or model constant in math mode; status set by the oracle scripts named in the file, not an experiment number | `K,\ d_{e_t}(S^{t})>0\Bigr\}\;\ge\;1 , \] the largest fact` |

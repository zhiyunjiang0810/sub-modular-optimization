"""V11 Q0: extract the verbatim statements (paper .tex environments) and the
ledger card statement lines into results/V11/statements.md and the
blind-review input pack results/V11/inputs/ (one statement per file, plus
Definition 1, the model assumptions and the notation table).  The
route-two subagents are given ONLY the files in inputs/.

Run:  python3 results/V11/extract_statements.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V11 = os.path.join(ROOT, 'results', 'V11')
INP = os.path.join(V11, 'inputs')
os.makedirs(INP, exist_ok=True)

RESULTS = open(os.path.join(ROOT, 'paper', 'sections', 'results.tex')).read()
MODEL = open(os.path.join(ROOT, 'paper', 'sections', 'model.tex')).read()
NOTATION = open(os.path.join(ROOT, 'paper', 'sections', 'notation_table.tex')).read()
LEDGER = open(os.path.join(ROOT, 'THEOREM_LEDGER.md')).read()

# key, paper label, ledger card header prefix, TASKS11 name
ITEMS = [
    ('nobound', 'prop:necessity', '## T1 ', 'T1 prop:nobound (paper label prop:necessity)'),
    ('valueacc', 'prop:valueacc', '## T2 ', 'T2 prop:valueacc'),
    ('ceiling', 'thm:ceiling', '## T8 ', 'T8 thm:ceiling'),
    ('guarantee', 'prop:guarantee', '## T3 ', 'T3 prop:guarantee'),
    ('coherence', 'lem:coherence', '## T5 ', 'T5 lem:coherence'),
    ('exact', 'thm:exact', '## T6 ', 'T6 thm:exact'),
    ('limit', 'cor:limit', '## T9 ', 'T9 cor:limit'),
    ('linear_exact', 'thm:linear-exact', '## T10c ', 'T10c thm:linear-exact (J6)'),
    ('hardness', 'thm:hardness', '## T10 ', 'T10 thm:hardness'),
    ('linear_anysize', 'thm:linear-anysize', '## T10d ', 'T10d thm:linear-anysize (J7)'),
]


def tex_env(label):
    """Return (envname, body) of the environment carrying \\label{label}."""
    i = RESULTS.index('\\label{%s}' % label)
    b = RESULTS.rfind('\\begin{', 0, i)
    env = RESULTS[b + 7:RESULTS.index('}', b)]
    e = RESULTS.index('\\end{%s}' % env, i)
    body = RESULTS[b:e + len('\\end{%s}' % env)]
    body = '\n'.join(l for l in body.split('\n') if not l.lstrip().startswith('%'))
    return env, body


def ledger_statement(prefix):
    s = LEDGER.index(prefix)
    e = LEDGER.find('\n## ', s + 1)
    card = LEDGER[s:e if e > 0 else None]
    # statement bullets: lines from the first "- 陈述" / "- 统一陈述" bullet to the next top-level bullet
    lines = card.split('\n')
    out, on = [], False
    for l in lines:
        if re.match(r'^- (陈述|统一陈述)', l):
            on = True
            out.append(l)
            continue
        if on:
            if re.match(r'^- ', l):
                on = False
            else:
                out.append(l)
    return card.split('\n')[0], '\n'.join(out)


def tex_block(src, label):
    i = src.index('\\label{%s}' % label)
    b = src.rfind('\\begin{', 0, i)
    env = src[b + 7:src.index('}', b)]
    e = src.index('\\end{%s}' % env, i)
    return src[b:e + len('\\end{%s}' % env)]



VALUEACC_B = r'''
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
'''

J8_STATEMENT = r'''
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
'''

J8_ALGORITHM = r'''
## The algorithm ProbeLottery (exactly as implemented in the delivered spot-check script)

Input: ground set $N$ in a fixed tie-break order (argmax returns the first maximiser), oracle
$\tilde f$ (written $g$ below), constant $\mathrm{EPS}=1/10000$. All comparisons exact.

1. Singletons: $b\in\arg\max_{e\in N} g(\{e\})$, $M=g(\{b\})$.
2. Pairs containing $b$: $c\in\arg\max_{e\ne b} g(\{b,e\})$, $p=g(\{b,c\})$; $P_0=\{b,c\}$.
3. Pool: $C=\{e\ne b:\ g(\{e\})\ge M-\mathrm{EPS}\cdot M\ \text{and}\ g(\{b,e\})\ge p-\mathrm{EPS}\cdot M\}$.
4. Extensions: $B\leftarrow[b]$; secondary list empty. Repeat up to 4 times: among $e\in C\setminus B$
   (stop if empty) pick $v\in\arg\max g(B\cup\{e\})$, append $v$ to $B$; pick
   $z_v\in\arg\max_{z\ne v} g(\{v,z\})$; append $\{v,z_v\}$ and $\{b,v\}$ to the secondary list.
   Pad the secondary list with copies of $P_0$ until it has 8 entries.
5. Output distribution: $P_0$ with probability $127/128$, and each of the 8 secondary sets with
   probability $1/1024$ (probabilities add over repeated sets). Total mass 1.

Query accounting: each distinct set is queried once (cached); the script asserts at most $9n$ queries
and maximum queried set size $5$ ($|B|\le5$).
'''


def main():
    out = ['# V11 statements (Q0)\n',
           '来源规则：正文陈述逐字取自 paper/sections/results.tex 的环境（去掉 % 注释行）；',
           '台账陈述逐字取自 THEOREM_LEDGER.md 对应卡的"陈述"条目。矩阵的 A 项比对二者的量词。',
           '输入送达与缺失情况见 MISSING_INPUTS.md（J8 算法由 spot-check 脚本给出，证明文件未送达）。\n']
    for key, label, prefix, name in ITEMS:
        env, body = tex_env(label)
        head, lstmt = ledger_statement(prefix)
        out.append(f'\n## {name}\n')
        out.append(f'- 正文环境: `{env}`, label `{label}`')
        out.append(f'- 台账卡: {head}\n')
        out.append('### 台账陈述（逐字）\n')
        out.append(lstmt if lstmt else '(台账卡无独立"陈述"条目，见卡全文)')
        out.append('\n### 正文陈述（逐字，LaTeX）\n')
        out.append('```latex\n' + body + '\n```')
        if key == 'ceiling':
            out.append('\n### TASKS11 要求的拆分读法（同一陈述，两个 n 区间）\n')
            out.append('- n >= 2K（Proposition 读法）: C*_{n,K}(eta) = 1/eta；对手侧对每个确定性算法存在'
                       '实例使 f(T) <= f(O*)/eta；达到侧穷举 argmax f~ 满足 f(S) >= f(O*)/eta。')
            out.append('- K <= n < 2K（remark 读法）: C*_{n,K}(eta) = K/((2K-n)+(n-K)eta)；'
                       '逐实例式 f(S) >= K/(K+(eta-1)|O*\\S|) f(O*)。')
        # blind-review input file
        with open(os.path.join(INP, f'statement_{key}.md'), 'w') as fh:
            fh.write(f'# Statement: {label} ({name})\n\n')
            fh.write('This is the exact statement to be proved independently. Do not consult any other file '
                     'except definition1.md, assumptions.md and notation.md in this directory.\n\n')
            fh.write('```latex\n' + body + '\n```\n')
    out.append('\n## T2 方案二改写后的陈述（2026-09-18，台账已改，正文未改；矩阵以此为准）\n')
    out.append(VALUEACC_B)
    out.append('\n## J8 ProbeLottery（陈述来源 HANDOFF_2026-09-18 §4；证明文件未送达）\n')
    out.append(J8_STATEMENT)
    open(os.path.join(V11, 'statements.md'), 'w').write('\n'.join(out) + '\n')
    # override the blind input for valueacc with the variant-B statement
    with open(os.path.join(INP, 'statement_valueacc.md'), 'w') as fh:
        fh.write('# Statement: prop:valueacc (T2, convention B rewrite of 2026-09-18)\n\n')
        fh.write('This is the exact statement to be proved independently. Do not consult any other file '
                 'except definition1.md, assumptions.md and notation.md in this directory. Use the '
                 'convention-B Definition 1 (factors eta_u, eta_o > 0 without floors).\n\n')
        fh.write(VALUEACC_B + '\n')
    with open(os.path.join(INP, 'statement_probelottery.md'), 'w') as fh:
        fh.write('# Statement: J8 ProbeLottery (Proposition; K = 2, eta = 3/2)\n\n')
        fh.write('This is the exact statement and the exact algorithm. Do not consult any other file '
                 'except definition1.md, assumptions.md and notation.md in this directory.\n\n')
        fh.write(J8_STATEMENT + '\n\n' + J8_ALGORITHM + '\n')


    # Definition 1 + selection error
    d1 = tex_block(MODEL, 'def:eta')
    dsel = tex_block(MODEL, 'def:etasel')
    dsel = '\n'.join(l for l in dsel.split('\n') if not l.lstrip().startswith('%'))
    with open(os.path.join(INP, 'definition1.md'), 'w') as fh:
        fh.write('# Definition 1 (prediction error), verbatim from the paper\n\n```latex\n' + d1 + '\n```\n\n')
        fh.write('# Definition (selection error), verbatim\n\n```latex\n' + dsel + '\n```\n\n')
        fh.write('# Definition 1, convention B ("方案二", the settled convention; HANDOFF_2026-09-18 section 3)\n\n'
                 'For $\\eta_u,\\eta_o>0$ with $\\eta=\\eta_u\\eta_o\\ge1$, the surrogate $\\tilde f$ has '
                 'marginal-gain error $(\\eta_u,\\eta_o)$ if for all $S\\subseteq N$ and $e\\notin S$: '
                 '$d_e(S)/\\eta_u\\le\\tilde d_e(S)\\le\\eta_o\\,d_e(S)$. Scaling: multiplying $\\tilde f$ by '
                 '$c>0$ maps $(\\eta_u,\\eta_o)\\to(c\\eta_u,\\eta_o/c)$ and leaves $\\eta$ unchanged; '
                 '$\\tilde f=cf$ has $\\eta=1$. The two factors are the two sides of the band; no result depends '
                 'on the split and every statement uses only $\\eta$. The definition forces '
                 '$\\tilde d_e(S)=0$ exactly when $d_e(S)=0$.\n\n'
                 'Relation to the verbatim text above: the paper text currently floors both factors at 1; '
                 'under convention B a predictor with factors $(\\eta_u,\\eta_o)$, $\\eta_u<1$, is the same '
                 'object as the rescaled predictor with factors $(1,\\eta)$. Class statements over $\\eta$ '
                 'are unaffected; prop:valueacc (ii)(iii) are stated under convention B.\n')
    # assumptions
    m0 = MODEL.index('A ground set $N$')
    m1 = MODEL.index('\\begin{definition}[Prediction error]')
    g0 = MODEL.index('Predictive greedy is the single-step greedy')
    g1 = MODEL.index('Two run-dependent error')
    para = lambda s: '\n'.join(l for l in s.split('\n') if not l.lstrip().startswith('%'))
    with open(os.path.join(INP, 'assumptions.md'), 'w') as fh:
        fh.write('# Model assumptions, verbatim from the paper\n\n```latex\n' + para(MODEL[m0:m1]) + '\n```\n\n')
        fh.write('# Predictive greedy, verbatim\n\n```latex\n' + para(MODEL[g0:g1]) + '\n```\n\n')
        fh.write('Conventions: ratios alpha in (0,1] with F_ALG >= alpha F_OPT (larger is better); '
                 'O* denotes an optimal K-set; adversarial tie-breaking in all worst-case statements; '
                 'the run always executes exactly K steps.\n')
    with open(os.path.join(INP, 'notation.md'), 'w') as fh:
        fh.write('# Notation table, verbatim\n\n```latex\n' + NOTATION + '\n```\n')
    print('wrote statements.md and', len(ITEMS), 'statement files + definition1/assumptions/notation')


if __name__ == '__main__':
    main()

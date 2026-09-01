"""Regenerate results/EXP_table.tex from the CURRENT E1-E4 row CSVs (TASKS4 F1.5).

One-key reproduction:   python3 results/EXP_table_build.py
Nothing is hand-typed into the .tex: every number below is recomputed here from
results/E{1,2,3}_rows.csv (medians and IQR over all runs at the stated K) and
results/E4_worst_case.csv.

Aggregation recipe (unchanged from EXP_SUMMARY.md, made explicit):
  * E1 at K = 7, E2 at K = 30, E3 at K = 5; all datasets/seeds of that task
    pooled into one median.
  * ratio: median and the [q25, q75] interquartile range.
  * eta^sel: median of the per-run eta^sel (which is itself a max over the
    positive-gain steps of that run).
  * L_K column: L_K evaluated AT the median eta^sel (not the median of the
    per-run L_K), matching the caption.
  * sign-viol. %: median of viol_sign_pct.  For E2 both objectives are coverage
    functions on nested edge sets, so d and d~ can never have opposite signs and
    the column is structurally 0; it is printed as "--" instead of as a finding.
  * non-pos. steps %: median of frac_steps_nonpos (share of trajectory steps
    with chosen true gain d_t <= 0, i.e. the steps OUTSIDE the scope of the
    certified bound; new column, TASKS4 F1.3).
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
K_OF = {'E1': 7, 'E2': 30, 'E3': 5}


def L_K(eta, K):
    return 1 - (1 - 1 / (eta * K)) ** K


def quantiles(xs):
    xs = sorted(xs)
    if not xs:
        return (float('nan'),) * 3

    def q(f):
        if len(xs) == 1:
            return xs[0]
        i = f * (len(xs) - 1)
        lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
        return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)
    return q(0.25), q(0.5), q(0.75)


def col(rows, name):
    return [float(r[name]) for r in rows if r.get(name) not in (None, '', 'n/a')]


def task_stats(task):
    K = K_OF[task]
    path = os.path.join(HERE, f'{task}_rows.csv')
    rows = [r for r in csv.DictReader(open(path)) if int(r['K']) == K]
    r1, rmed, r3 = quantiles(col(rows, 'ratio'))
    _, emed, _ = quantiles(col(rows, 'eta_sel'))
    _, vmed, _ = quantiles(col(rows, 'viol_sign_pct'))
    _, nmed, _ = quantiles(col(rows, 'frac_steps_nonpos'))
    npath = sum(1 for r in rows if r['eta_path_trimmed'] == 'n/a')
    return dict(K=K, n=len(rows), ratio=rmed, q1=r1, q3=r3, eta=emed,
                LK=L_K(emed, K), viol=vmed, nonpos=100.0 * nmed,
                n_eta_path_na=npath,
                viol_all_zero=all(v == 0.0 for v in col(rows, 'viol_sign_pct')))


def e4_point(label='Vj_K5_j2'):
    out = None
    for r in csv.DictReader(open(os.path.join(HERE, 'E4_worst_case.csv'))):
        if r['label'] == label:
            out = dict(r)
    if out is None:
        raise SystemExit(f'{label} not in E4_worst_case.csv')
    for r in csv.DictReader(open(os.path.join(HERE, 'E4_rows.csv'))):
        if r['dataset'] == label:
            out['frac_nonpos'] = float(r['frac_steps_nonpos'])
    return out


def main():
    s = {t: task_stats(t) for t in ('E1', 'E2', 'E3')}
    e4 = e4_point()
    for t, v in s.items():
        print(t, {k: (round(x, 4) if isinstance(x, float) else x)
                  for k, x in v.items()})
    print('E4', e4)

    def line(name, sur, v, viol_txt=None):
        vt = viol_txt if viol_txt is not None else f"{v['viol']:.1f}"
        return (f"{name} ({v['K']}) & {sur} & {v['ratio']:.3f} & "
                f"[{v['q1']:.3f}, {v['q3']:.3f}] & {v['eta']:.1f} & "
                f"{v['LK']:.3f} & {vt} & {v['nonpos']:.1f} \\\\")

    tex = r"""% Experiments-section summary table.  REGENERATED, do not hand-edit:
%   python3 results/EXP_table_build.py
% Every number is recomputed from results/E{1,2,3}_rows.csv (medians / IQR over
% all runs at the stated K) and results/E4_worst_case.csv / E4_rows.csv.
% Width: \small + \tabcolsep 4pt measures 393.7pt against the 397.5pt ICLR
% textwidth (checked with pdflatex + iclr2027_conference.sty), so it fits the
% one-column page.  Shortening any header will only add slack.
\begin{table}[t]
\centering
\caption{Predictive greedy across three surrogate families. Medians over all
runs at the stated $K$ (IQR in brackets). $L_K$ is the certified lower bound
$L_K(\eta^{sel})$ of Theorem~\ref{thm:trajectory} evaluated at the median
measured $\eta^{sel}$; $d_t \le 0$ \% is the share of trajectory steps whose
chosen true gain is non-positive.}
\label{tab:experiments}
\small
\setlength{\tabcolsep}{4pt}
\begin{tabular}{llccccrr}
\toprule
Task ($K$) & Surrogate $\tilde f$ & ratio & IQR & $\eta^{sel}$ & $L_K$ & sign-viol.\ \% & $d_t\!\le\!0$ \% \\
\midrule
__E1__
__E2__
__E3__
\midrule
Worst-case $V_j$ (5) & constructed & __E4RATIO__\textsuperscript{a} & exact & __E4ETA__ & $\rho_K$ & __E4VIOL__ & __E4NONPOS__ \\
\bottomrule
\end{tabular}
\vspace{2pt}
{\footnotesize \textsuperscript{a} representative point $j=2$, $\eta=__E4ETA__$;
every constructed instance realizes its theoretical value to $10^{-10}$
(results/E4\_worst\_case.csv).\\
\emph{Note (i)}: the ratio's denominator is greedy-on-$f$, an upper-estimate
proxy for OPT, so every ratio in this table is an upper estimate of
$f(S^{\tilde f})/f(\mathrm{OPT})$.\\
\emph{Note (ii)}: $\eta^{sel}$ is defined on the steps with positive true gain,
so the certified bound in the $L_K$ column is a statement about those steps;
the last column reports the share of steps with $d_t \le 0$ (column
\texttt{frac\_steps\_nonpos} of the row CSVs), which are outside that scope.\\
\emph{Note (iii)}: for influence maximization $f$ and $\tilde f$ are coverage
functions on nested edge sets, so opposite-sign $(d,\tilde d)$ pairs cannot
occur; the entry is ``--'' rather than a measured zero.}
\end{table}
"""
    tex = tex.replace('__E1__', line('Feature sel.\\', '5-fold CV acc.',
                                     s['E1']))
    assert s['E2']['viol_all_zero'], 'E2 sign-violation column is not all zero'
    tex = tex.replace('__E2__', line('Influence max.\\', 'observed graph',
                                     s['E2'], viol_txt='--'))
    tex = tex.replace('__E3__', line('Summarization',
                                     'cover./div./FL', s['E3']))
    tex = tex.replace('__E4RATIO__', f"{float(e4['realized']):.3f}")
    tex = tex.replace('__E4ETA__', f"{float(e4['eta']):.1f}")
    tex = tex.replace('__E4VIOL__', f"{float(e4['viol']):.0f}")
    tex = tex.replace('__E4NONPOS__', f"{100 * e4['frac_nonpos']:.1f}")
    out = os.path.join(HERE, 'EXP_table.tex')
    open(out, 'w').write(tex)
    print('wrote', out)


if __name__ == '__main__':
    main()

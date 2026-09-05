"""G3: generate paper/sections/numbers.tex -- every experiment number the
Experiments section prints, as a named LaTeX macro.

One-command reproduction:

    python3 results/G3_gen_numbers.py

Rules this script implements (TASKS5 G3):
  * The SCRIPT is the single source of truth for rounding.  Section text may
    not contain hand-typed numeric literals; it uses the macros below.
  * LaTeX macro names cannot contain digits, so names spell digits out
    (\\EOneKMainRatioMedian, \\ETwoEtaSelMedianKMain, \\EThreeSubmodViolPct).
  * Deterministic: pure functions of the committed CSV/JSON inputs, no
    randomness, no wall-clock, no network.  Re-running overwrites the same
    file byte for byte.

Inputs (all committed):
  results/E1_rows.csv, E2_rows.csv, E3_rows.csv, E4_rows.csv   unified rows
  results/E2_p_eta.csv                                          E2 p sweep
  results/E4_worst_case.csv                                     E4 theory diff
  results/E3_summary.json                                       structure check
  results/E1_opt_breast_cancer.csv                              F1 brute-force OPT
  results/E1_baselines.csv                                      E1 baseline panel

Side output (kept in sync deliberately, see COPY_TABLE below):
  paper/sections/EXP_table.tex  <- results/EXP_table.tex, with the raw
  $\\eta^{sel}$ spelling rewritten to the \\etasel macro of paper/macros.tex.
  Rationale: results/EXP_table.tex belongs to results/EXP_table_build.py (a
  different task) and is not hand-edited here; copying it through this script
  means one command refreshes both the macros and the table the section
  \\input's, and the notation stays the one fixed in GLOSSARY.md.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'paper', 'sections', 'numbers.tex')
TABLE_SRC = os.path.join(HERE, 'EXP_table.tex')
TABLE_DST = os.path.join(ROOT, 'paper', 'sections', 'EXP_table.tex')

# The budgets the section reports on.  E1/E2/E3 match EXP_table_build.py so
# the running text and Table 1 cannot drift apart.
K_MAIN = {'E1': 7, 'E2': 30, 'E3': 5}
# The main figure (results/E5_money_plot.py) draws these two panels.
MONEY_K = (5, 30)


# --------------------------------------------------------------------------
# statistics (same recipe as results/EXP_table_build.py, restated so this
# script has no import dependency on it)
# --------------------------------------------------------------------------
def quantiles(xs):
    xs = sorted(xs)
    if not xs:
        raise SystemExit('empty column')

    def q(f):
        if len(xs) == 1:
            return xs[0]
        i = f * (len(xs) - 1)
        lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
        return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)
    return q(0.25), q(0.5), q(0.75)


def median(xs):
    return quantiles(xs)[1]


def L_K(eta, K):
    """The certified bound of Proposition prop:guarantee, evaluated at eta."""
    return 1 - (1 - 1 / (eta * K)) ** K


def rho_K(eta, K):
    """Exact worst case of Theorem thm:exact, rho_K = min_j V_j."""
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return min(1 - q ** j * (1 - (K - j) / (K * eta)) for j in range(K))


def read(name):
    with open(os.path.join(HERE, name), newline='') as fh:
        return list(csv.DictReader(fh))


def col(rows, name):
    return [float(r[name]) for r in rows
            if r.get(name) not in (None, '', 'n/a')]


# --------------------------------------------------------------------------
# formatting.  One place decides every printed digit.
# --------------------------------------------------------------------------
def f3(x):
    return f'{x:.3f}'


def f2(x):
    return f'{x:.2f}'


def f1(x):
    return f'{x:.1f}'


def i0(x):
    return f'{int(round(x))}'


def thousands(n):
    """25375 -> 25{,}375 (text mode; LaTeX eats a bare comma's spacing)."""
    return f'{int(n):,}'.replace(',', '{,}')


def sci(x, digits=1):
    """1.11e-16 -> 1.1\\times 10^{-16} (math mode, used inside $...$)."""
    if x == 0:
        return '0'
    exp = 0
    v = abs(x)
    while v < 1:
        v *= 10
        exp -= 1
    while v >= 10:
        v /= 10
        exp += 1
    return f'{v:.{digits}f}\\times 10^{{{exp}}}'


MACROS = []


def M(name, value, comment):
    MACROS.append((name, value, comment))


# ==========================================================================
# E1  learned surrogates (feature selection)
# ==========================================================================
def do_e1():
    K = K_MAIN['E1']
    rows = read('E1_rows.csv')
    datasets = sorted({r['dataset'] for r in rows})
    seeds = {r['seed'] for r in rows}
    Ks = sorted({int(r['K']) for r in rows})
    main = [r for r in rows if int(r['K']) == K]

    M('EOneNumDatasets', str(len(datasets)), 'distinct E1 datasets')
    M('EOneNumSeeds', str(len(seeds)), 'train/test splits per dataset')
    M('EOneKMin', str(min(Ks)), 'smallest budget run in E1')
    M('EOneKMain', str(K), 'budget the E1 headline numbers are quoted at')
    M('EOneNumRunsKMain', str(len(main)), 'runs pooled at the headline budget')

    q1, med, q3 = quantiles(col(main, 'ratio'))
    M('EOneKMainRatioMedian', f3(med), 'median ratio, all E1 datasets pooled')
    M('EOneKMainRatioLoQ', f3(q1), 'first quartile of that ratio')
    M('EOneKMainRatioHiQ', f3(q3), 'third quartile of that ratio')

    e = median(col(main, 'eta_sel'))
    M('EOneKMainEtaSelMedian', f1(e), 'median measured selection error')
    M('EOneKMainBound', f3(L_K(e, K)), 'L_K at the median selection error')
    M('EOneKMainExactWorst', f3(rho_K(e, K)),
      'exact worst case rho_K at the same selection error')

    tr = median(col(main, 'eta_path_trimmed'))
    M('EOneKMainEtaTrMedian', f1(tr), 'median measured trajectory error')
    M('EOneKMainEtaTrBound', f3(L_K(tr, K)),
      'L_K at the median trajectory error (near-vacuous; the reason the '
      'paper states the guarantee at etasel)')

    M('EOneSignViolPctKMain', f1(median(col(main, 'viol_sign_pct'))),
      'median share of candidate pairs whose predicted and true gains '
      'disagree in sign')
    M('EOneNonposPctKMain',
      f1(100 * median(col(main, 'frac_steps_nonpos'))),
      'median share of trajectory steps with nonpositive chosen true gain')

    air = [r for r in main if r['dataset'] == 'airline']
    M('EOneAirlineRatioMedian', f3(median(col(air, 'ratio'))),
      'median ratio on the largest E1 dataset')
    ae = median(col(air, 'eta_sel'))
    M('EOneAirlineEtaSelMedian', f2(ae), 'median selection error there')
    M('EOneAirlineBound', f3(L_K(ae, K)), 'L_K at that selection error')
    # Row count of the cleaned airline table (results/E1_notes.md section 3:
    # 25,976 raw rows, 601 removed by the three legacy outlier thresholds).
    # It is not derivable from the row CSVs, so it is pinned here with its
    # provenance rather than typed into the section text.
    M('EOneAirlineRows', thousands(25375),
      'rows of the cleaned airline table (E1_notes.md section 2/3)')
    # cv=5 in results/E1_run.py (StratifiedKFold, no shuffle); a design
    # parameter of the surrogate, pinned here so the section text stays free
    # of numeric literals.
    M('EOneCVFolds', '5', 'folds of the cross-validation surrogate')

    base = read('E1_baselines.csv')
    methods = sorted({r['method'] for r in base})
    # "greedy_f" and "greedy_ftilde" are the two greedy references in the same
    # file; the classical selectors are what is compared against.
    selectors = [m for m in methods if 'greedy' not in m]
    M('EOneNumBaselines', str(len(selectors)),
      'classical feature selectors compared against ' + '/'.join(selectors))

    # Does greedy-on-ftilde beat the best selector at every K on airline?
    # Recomputed here so the sentence in the section cannot go stale.
    def med_acc(ds, K_, m):
        v = [float(r['oos_acc']) for r in base
             if r['dataset'] == ds and int(r['K']) == K_ and r['method'] == m]
        return median(v) if v else None

    gname = [m for m in methods if 'greedy' in m and 'tilde' in m]
    gname = gname[0] if gname else None
    n_win = 0
    if gname:
        for K_ in Ks:
            g = med_acc('airline', K_, gname)
            best = max(x for x in (med_acc('airline', K_, m)
                                   for m in selectors) if x is not None)
            if g is not None and g >= best - 1e-12:
                n_win += 1
    M('EOneAirlineBaselineWins', str(n_win),
      'budgets (out of %d) where the median accuracy of greedy on ftilde is '
      'at least the best of the %d selectors on airline'
      % (len(Ks), len(selectors)))
    M('EOneNumBudgets', str(len(Ks)), 'budgets swept in E1')
    M('EOneBaselineSeeds', str(len({r['seed'] for r in base})),
      'splits used for the baseline panel (fewer than the main sweep, to '
      'bound running time; results/E1_notes.md section 9)')

    # Brute-force OPT on breast_cancer (the honest check on the OPT proxy).
    # G4 extended F1's enumeration from K<=4 to K<=5 and reproduces the
    # K<=4 rows bit-for-bit; prefer the G4 file when present.
    if os.path.exists(os.path.join(HERE, 'G4_bc_opt_K5.csv')):
        opt = read('G4_bc_opt_K5.csv')
        opt_src = 'G4 (results/G4_bc_opt_K5.py)'
    else:
        opt = read('E1_opt_breast_cancer.csv')
        opt_src = 'F1'
    Kopt = max(int(r['K']) for r in opt)
    o = [r for r in opt if int(r['K']) == Kopt]
    r_go = median(col(o, 'greedy_f_over_opt'))
    r_gt = median(col(o, 'greedy_ftilde_over_opt'))
    M('EOneBreastOptK', str(Kopt),
      'largest budget where OPT was enumerated exactly (%s)' % opt_src)
    M('EOneBreastOptSeeds', str(len({r['seed'] for r in o})),
      'splits in that enumeration')
    M('EOneBreastOptGreedyF', f3(r_go),
      'median f(greedy on f) / f(OPT) at that budget')
    M('EOneBreastOptGreedyFtilde', f3(r_gt),
      'median f(greedy on ftilde) / f(OPT) at that budget')
    M('EOneBreastOptInflationPct', f1(100 * (1 / r_go - 1)),
      'percent by which using greedy-on-f as the OPT proxy inflates a ratio')

    # G4 airline conservative OPT under-estimate (sanity check only; the
    # table keeps greedy-on-f as denominator).  OPT_hat <= OPT, so the
    # improvement over greedy-on-f is a lower bound on the true OPT gap.
    if os.path.exists(os.path.join(HERE, 'G4_airline_optproxy.csv')):
        ap = read('G4_airline_optproxy.csv')
        imp = [1 / float(r['greedy_f_over_opt_hat']) - 1 for r in ap]
        M('EOneAirlineOptHatSeeds', str(len(ap)),
          'seeds in the airline partial-enumeration check (G4)')
        M('EOneAirlineOptHatCands', str(max(int(r['n_cand_total']) for r in ap)),
          'candidate K-subsets scored per seed (ftilde top + random)')
        M('EOneAirlineOptHatMaxImpPct', f2(100 * max(imp)),
          'largest relative improvement of OPT_hat over greedy-on-f, percent')
        M('EOneAirlineOptHatBetterSeeds',
          str(sum(1 for r in ap if float(r['greedy_f_over_opt_hat']) < 1.0)),
          'seeds where the pool beat greedy-on-f at all')


# ==========================================================================
# E2  partially observed surrogates (influence maximization)
# ==========================================================================
def do_e2():
    K = K_MAIN['E2']
    rows = read('E2_rows.csv')
    graphs = sorted({r['dataset'] for r in rows})
    ps = sorted({float(r['p']) for r in rows})
    seeds = {r['seed'] for r in rows}
    main = [r for r in rows if int(r['K']) == K]

    M('ETwoNumGraphs', str(len(graphs)), 'networks in E2')
    M('ETwoNumSeedsPerP', str(len(seeds)), 'observed graphs per (network, p)')
    M('ETwoNumTrajectories', str(len(main)),
      'greedy trajectories in E2 (one per network, p and observation seed)')
    M('ETwoKMain', str(K), 'budget the E2 headline numbers are quoted at')
    M('ETwoPSet', ', '.join(f'{p:g}' for p in ps),
      'edge observation probabilities')
    M('ETwoPLow', f'{min(ps):g}', 'least observed setting')
    M('ETwoPHigh', f'{max(ps):g}', 'most observed setting')

    q1, med, q3 = quantiles(col(main, 'ratio'))
    M('ETwoKMainRatioMedian', f3(med), 'median ratio at the headline budget')
    M('ETwoKMainRatioLoQ', f3(q1), 'first quartile')
    M('ETwoKMainRatioHiQ', f3(q3), 'third quartile')
    e = median(col(main, 'eta_sel'))
    M('ETwoKMainEtaSelMedian', f1(e), 'median measured selection error')
    M('ETwoKMainBound', f3(L_K(e, K)), 'L_K at that selection error')
    M('ETwoKMainExactWorst', f3(rho_K(e, K)), 'rho_K at that selection error')
    M('ETwoNonposPctKMain',
      f1(100 * median(col(main, 'frac_steps_nonpos'))),
      'median share of steps with nonpositive chosen true gain (structurally '
      'zero: both objectives are coverage functions)')

    # Largest network (results/E2_notes.md section 2).  Node/edge counts are
    # properties of the input graph files, not of the row CSVs, so they are
    # pinned here with their provenance.
    M('ETwoLargestNodes', thousands(50515),
      'nodes of the largest E2 network, facebook_artist (E2_notes.md sec. 2)')
    M('ETwoLargestEdges', thousands(819306),
      'input edges of that network (E2_notes.md sec. 2)')

    # p sweep.
    sweep = read('E2_p_eta.csv')
    by = {}
    for r in sweep:
        by[(r['dataset'], float(r['p']))] = r
    lo, hi = min(ps), max(ps)
    rises, drops = [], []
    mono_eta = mono_ratio = 0
    for g in graphs:
        etas = [float(by[(g, p)]['eta_sel_K30_median']) for p in ps]
        rats = [float(by[(g, p)]['ratio_K30_median']) for p in ps]
        # ps is ascending, so "less observed => larger error" means etas is
        # descending and rats ascending.
        mono_eta += all(etas[i] > etas[i + 1] for i in range(len(ps) - 1))
        mono_ratio += all(rats[i] < rats[i + 1] for i in range(len(ps) - 1))
        rises.append(float(by[(g, lo)]['eta_sel_K30_median'])
                     / float(by[(g, hi)]['eta_sel_K30_median']))
        drops.append(float(by[(g, hi)]['LK_eta_sel_median'])
                     / float(by[(g, lo)]['LK_eta_sel_median']))
    M('ETwoNumGraphsEtaMonotone', str(mono_eta),
      'networks on which the median selection error is strictly decreasing '
      'in p')
    M('ETwoNumGraphsRatioMonotone', str(mono_ratio),
      'networks on which the median ratio is strictly increasing in p')
    M('ETwoEtaRiseMin', f1(min(rises)),
      'smallest factor by which the median selection error grows from the '
      'most to the least observed setting')
    M('ETwoEtaRiseMax', i0(max(rises)), 'largest such factor')
    lo_r = [float(by[(g, lo)]['ratio_K30_median']) for g in graphs]
    hi_r = [float(by[(g, hi)]['ratio_K30_median']) for g in graphs]
    M('ETwoRatioPHighMin', f3(min(hi_r)),
      'worst median ratio at the most observed setting')
    M('ETwoRatioPLowMin', f3(min(lo_r)),
      'worst median ratio at the least observed setting')
    M('ETwoRatioPLowMax', f3(max(lo_r)),
      'best median ratio at the least observed setting')
    lo_b = [float(by[(g, lo)]['LK_eta_sel_median']) for g in graphs]
    hi_b = [float(by[(g, hi)]['LK_eta_sel_median']) for g in graphs]
    M('ETwoBoundPHighMin', f3(min(hi_b)),
      'smallest certified bound at the most observed setting')
    M('ETwoBoundPHighMax', f3(max(hi_b)), 'largest such bound')
    M('ETwoBoundPLowMin', f3(min(lo_b)),
      'smallest certified bound at the least observed setting')
    M('ETwoBoundPLowMax', f3(max(lo_b)), 'largest such bound')
    M('ETwoBoundDropFactorMax', i0(max(drops)),
      'largest factor by which the certified bound falls over the same range')


# ==========================================================================
# E3  heuristic, out-of-model surrogates (extractive summarization)
# ==========================================================================
def do_e3():
    K = K_MAIN['E3']
    rows = read('E3_rows.csv')
    cats, surr, docs = set(), set(), set()
    for r in rows:
        c, s = r['dataset'].rsplit('_', 1)
        cats.add(c)
        surr.add(s)
        docs.add((c, r['seed']))
    Ks = sorted({int(r['K']) for r in rows})
    main = [r for r in rows if int(r['K']) == K]

    M('EThreeNumCategories', str(len(cats)), 'BBC news categories')
    M('EThreeNumSurrogates', str(len(surr)),
      'heuristic surrogates: ' + ', '.join(sorted(surr)))
    M('EThreeNumDocs', str(len(docs)), 'distinct articles')
    M('EThreeKMin', str(min(Ks)), 'smallest budget')
    M('EThreeKMax', str(max(Ks)), 'largest budget')
    M('EThreeKMain', str(K), 'budget the E3 headline numbers are quoted at')
    M('EThreeNumRunsKMain', str(len(main)),
      'runs at that budget (articles with fewer than K sentences drop out)')

    q1, med, q3 = quantiles(col(main, 'ratio'))
    M('EThreeKMainRatioMedian', f3(med), 'median ratio at the headline budget')
    M('EThreeKMainRatioLoQ', f3(q1), 'first quartile')
    M('EThreeKMainRatioHiQ', f3(q3), 'third quartile')
    e = median(col(main, 'eta_sel'))
    M('EThreeKMainEtaSelMedian', f1(e), 'median measured selection error')
    M('EThreeKMainBound', f3(L_K(e, K)), 'L_K at that selection error')
    M('EThreeKMainExactWorst', f3(rho_K(e, K)), 'rho_K at the same error')
    M('EThreeSignViolPctKMain', f1(median(col(main, 'viol_sign_pct'))),
      'median share of candidate pairs disagreeing in sign')
    M('EThreeNonposPctKMain',
      f1(100 * median(col(main, 'frac_steps_nonpos'))),
      'median share of steps with nonpositive chosen true gain')

    best, best_v = None, -1.0
    for s in sorted(surr):
        v = median([float(r['ratio']) for r in main
                    if r['dataset'].endswith('_' + s)])
        if v > best_v:
            best, best_v = s, v
    M('EThreeBestSurrogateRatio', f3(best_v),
      'median ratio of the best single surrogate (%s)' % best)
    M('EThreeBestSurrogateName', best,
      'which surrogate that is (derived, not hand-typed, so the sentence '
      'cannot go stale if the ordering changes)')

    with open(os.path.join(HERE, 'E3_summary.json')) as fh:
        sm = json.load(fh)['structure_check']
    ro = sm['rouge']
    M('EThreeStructTriples', thousands(ro['pairs']),
      'set/element triples on which submodularity and monotonicity of the '
      'true objective were checked')
    M('EThreeSubmodViolPct', f2(ro['submod_viol_pct']),
      'share of those triples violating submodularity of ROUGE-1 F')
    M('EThreeMonoViolPct', f2(ro['mono_viol_pct']),
      'share violating monotonicity of ROUGE-1 F')
    M('EThreeMaxSubmodViol', f3(ro['max_submod_violation']),
      'largest submodularity violation, in units of the objective')
    # The structure check sweeps A with |A| <= 3 (results/E3_notes.md section
    # 7); the window is not recorded in the JSON, so it is pinned here with
    # its provenance because the violation percentages depend on it.
    M('EThreeStructMaxSetSize', '3',
      'largest |A| in the submodularity / monotonicity sweep '
      '(E3_notes.md section 7)')
    others = [k for k in sm if k != 'rouge']
    assert all(sm[k]['submod_viol'] == 0 and sm[k]['mono_viol'] == 0
               for k in others), 'a surrogate violated its own structure'
    M('EThreeSurrogateViolCount', '0',
      'violations by the three surrogates on the same triples (asserted zero '
      'by this script)')


# ==========================================================================
# E4  the constructed worst cases, executed by the same pipeline
# ==========================================================================
def do_e4():
    wc = read('E4_worst_case.csv')
    rows = read('E4_rows.csv')
    M('EFourNumInstances', str(len(wc)),
      'constructed instances run through the experiment pipeline')
    vj = [r for r in wc if r['label'].startswith('Vj_')]
    uk = [r for r in wc if r['label'].startswith('UK_')]
    M('EFourNumVjInstances', str(len(vj)), 'instances of the V_j family')
    M('EFourNumUKInstances', str(len(uk)), 'instances of the U_K family')
    Ks = sorted({int(r['label'].split('_K')[1].split('_')[0]) for r in wc})
    M('EFourKList', ', '.join(str(k) for k in Ks), 'budgets covered')

    dev = max(abs(float(r['realized']) - float(r['theory'])) for r in wc)
    M('EFourMaxDeviation', sci(dev),
      'largest absolute deviation of a realized ratio from its theoretical '
      'value (math mode)')
    dev_eta = max(abs(float(r['eta_sel']) - float(r['eta'])) for r in vj)
    M('EFourEtaSelDeviation', sci(dev_eta),
      'largest deviation of the measured selection error from the design '
      'error on the V_j instances (math mode)')
    # On the U_K family the design parameter is ahat, and eta^sel = ahat while
    # the GLOBAL error eta = (ahat K - 1)/(K - 1) is larger (RESEARCH_STATE
    # R7); the "eta" column of E4_worst_case.csv holds the global value, so it
    # is compared against ahat = 2 here, not against that column.
    dev_uk = max(abs(float(r['eta_sel']) - 2.0) for r in uk)
    M('EFourUKEtaSelDeviation', sci(dev_uk),
      'largest deviation of the measured selection error from ahat on the '
      'U_K instances (math mode)')

    rep = [r for r in wc if r['label'] == 'Vj_K5_j2'][0]
    M('EFourRepRatio', f3(float(rep['realized'])),
      'realized ratio of the representative instance quoted in the table')
    M('EFourRepEta', f1(float(rep['eta'])), 'its error level')
    M('EFourRepK', str(int(rep['label'].split('_K')[1].split('_')[0])),
      'its budget')
    M('EFourRepJ', rep['label'].rsplit('_j', 1)[1],
      'the segment index j of that instance')
    M('EFourViolMax', i0(max(float(r['viol']) for r in wc)),
      'largest sign-violation percentage over the constructed instances')
    assert len(rows) == len(wc), 'E4 row CSV and worst-case CSV disagree'


# ==========================================================================
# figure panels
# ==========================================================================
def do_figure():
    M('MoneyKLeft', str(MONEY_K[0]), 'left panel budget of the main figure')
    M('MoneyKRight', str(MONEY_K[1]), 'right panel budget of the main figure')


# ==========================================================================
def copy_table():
    with open(TABLE_SRC) as fh:
        tex = fh.read()
    # Use the notation macro fixed in paper/macros.tex (GLOSSARY, night 4)
    # instead of the raw superscript the generator writes.
    tex = tex.replace(r'\eta^{sel}', r'\etasel')
    head = ('% GENERATED, do not hand-edit.  Copied from results/EXP_table.tex\n'
            '% by results/G3_gen_numbers.py, with $\\eta^{sel}$ rewritten to\n'
            '% the \\etasel macro of paper/macros.tex.  Regenerate the source\n'
            '% with results/EXP_table_build.py, then rerun G3_gen_numbers.py.\n')
    with open(TABLE_DST, 'w') as fh:
        fh.write(head + tex)
    print('wrote', TABLE_DST)


def main():
    do_e1()
    do_e2()
    do_e3()
    do_e4()
    do_figure()

    names = [n for n, _, _ in MACROS]
    assert len(names) == len(set(names)), 'duplicate macro name'
    for n in names:
        assert n.isalpha(), f'macro name {n} is not letters-only'

    width = max(len(n) for n in names)
    lines = [
        '% =========================================================================',
        '% numbers.tex -- GENERATED, do not hand-edit.',
        '%   python3 results/G3_gen_numbers.py',
        '% Every experiment number printed by sections/experiments.tex is defined',
        '% here, so the section text contains no hand-typed numeric literals',
        '% (audited by results/G3_number_audit.py).  Rounding is decided in the',
        '% generator, which is the single source of truth.',
        '% Macro names spell digits out because LaTeX names cannot contain them.',
        '% =========================================================================',
        '',
    ]
    for n, v, c in MACROS:
        lines.append('%% %s' % c)
        lines.append('\\newcommand{\\%s}{%s}' % (n, v))
        lines.append('')
    lines.append('%% %d macros.' % len(MACROS))
    lines.append('')
    with open(OUT, 'w') as fh:
        fh.write('\n'.join(lines))
    print('wrote', OUT, 'with', len(MACROS), 'macros (name width', width, ')')
    for n, v, _ in MACROS:
        print(f'  \\{n} = {v}')
    copy_table()


if __name__ == '__main__':
    main()

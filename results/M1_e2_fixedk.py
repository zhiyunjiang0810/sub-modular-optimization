"""M1.1 (TASKS8): audit the E2 pipeline against the FIXED-K-STEP predictive
greedy semantics, and recompute eta^sel / the certificate column under the
stepwise definition D3 of ledger cards T3 and T15.

Semantics being checked (D3, ledger T3):
    a_t = M_t / g_t, where g_t = d_{e_t}(S^t) is the TRUE gain of the step's
    chosen element and M_t = max_e d_e(S^t) is the largest TRUE gain available
    at that state;
      * g_t > 0                 ->  a_t = M_t / g_t
      * M_t = g_t = 0           ->  a_t = 1      (benign zero step)
      * g_t = 0 < M_t           ->  a_t = +inf   (harmful zero step)
      * g_t < 0                 ->  not in the model (flagged, never occurs for
                                    monotone coverage)
    eta^sel = max{1, max_t a_t};  L_K(+inf) = 0.

What the shipped pipeline does instead (src/statistics.py, TrajectoryStats.upto,
lines 85-95): every step with d_chosen <= 0 is SKIPPED when the max is taken and
only counted in n_steps_nonpos.  So the CSV eta^sel is the max over the
positive-gain steps only; a harmful zero step is dropped from the max instead of
sending it to +inf.  The greedy loops themselves (src/im_graph.lazy_greedy line
139, results/E1_run.py greedy_exact, results/E3_run.py exact_greedy) are fixed
K step: the only exit besides len(S) == K is an EMPTY candidate pool, never a
sign or size test on the gain.

This script does three things and writes nothing outside results/:
  1. structure audit of results/E2_rows.csv: every run must carry exactly one
     row per executed step (E2_run.run_one emits k = 1..len(num_vals)), so a run
     with fewer than K_MAX prefix rows is a run that stopped early;
  2. REPLAY of selected runs (default: every run flagged with a nonpositive step
     plus one control run per dataset) recording (g_t, M_t) per step, which is
     what decides benign vs harmful and is not stored in any CSV;
  3. recomputation of eta^sel and L_K under D3 for the replayed runs, compared
     row by row with results/E2_rows.csv.

Outputs (new files; E2_rows.csv is NOT touched):
  results/M1_e2_fixedk_rows.csv   per replayed run x prefix: old vs fixed-K values
  results/M1_e2_fixedk.json       machine-readable summary
Usage:
  timeout 3600 python3 results/M1_e2_fixedk.py              # flagged + controls
  timeout 600  python3 results/M1_e2_fixedk.py --audit-only # step 1 only
  timeout 3600 python3 results/M1_e2_fixedk.py --runs all   # all 240 runs (slow)
"""
import argparse
import collections
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'src'))

import E2_run as E2                                            # noqa: E402
from im_graph import CachedSetFunction, lazy_greedy            # noqa: E402

ROWS_CSV = os.path.join(HERE, 'E2_rows.csv')
OUT_CSV = os.path.join(HERE, 'M1_e2_fixedk_rows.csv')
OUT_JSON = os.path.join(HERE, 'M1_e2_fixedk.json')
K_MAX = E2.K_MAX
INF = float('inf')

OUT_FIELDS = ['dataset', 'p', 'seed', 'K', 'eta_sel_csv', 'eta_sel_fixedk',
              'LK_csv', 'LK_fixedk', 'is_inf', 'n_steps_nonpos_csv',
              'n_zero_steps_replay', 'n_harmful_zero_replay',
              'n_benign_zero_replay', 'eta_sel_changed', 'LK_changed']


def L_K_fixedk(eta, K):
    """Theorem-6 bound under D3: L_K(+inf) = 0, L_K(eta) otherwise."""
    if eta == INF:
        return 0.0
    if eta is None or eta <= 0 or not math.isfinite(eta):
        return float('nan')
    return 1 - (1 - 1 / (eta * K)) ** K


# --------------------------------------------------------------------------
# 1. structure audit of the shipped CSV
# --------------------------------------------------------------------------
def audit_rows():
    rows = list(csv.DictReader(open(ROWS_CSV)))
    runs = collections.defaultdict(dict)
    for r in rows:
        runs[(r['dataset'], r['p'], r['seed'])][int(r['K'])] = r
    short, flagged = [], []
    for key, d in sorted(runs.items()):
        ks = sorted(d)
        if ks != list(range(1, K_MAX + 1)):
            short.append(dict(run=list(key), n_prefix_rows=len(ks),
                              max_K=max(ks) if ks else 0))
        last = d[max(ks)]
        if int(last['n_steps_nonpos']) > 0:
            flagged.append(dict(run=list(key),
                                n_steps_nonpos=int(last['n_steps_nonpos']),
                                eta_sel_csv=last['eta_sel'],
                                LK_csv=last['LK_eta_sel'],
                                ratio=last['ratio']))
    return rows, runs, short, flagged


def quantiles(xs):
    """Same quantile rule as results/EXP_table_build.py (linear interpolation)."""
    xs = sorted(xs)
    if not xs:
        return (float('nan'),) * 3

    def q(f):
        if len(xs) == 1:
            return xs[0]
        i = f * (len(xs) - 1)
        lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
        if xs[hi] == INF:
            return INF
        return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)
    return q(0.25), q(0.5), q(0.75)


def table_impact(rows):
    """The two E2 cells of Table 1 (paper/sections/EXP_table.tex, built by
    results/EXP_table_build.py) recomputed both ways at the headline K.

    EXP_table_build.task_stats reads the eta_sel COLUMN of E2_rows.csv, which is
    the pre-D3 value, while results/G3_gen_numbers.py applies the D3 infinity
    override before taking the same median.  Both feed the same paper."""
    main = [r for r in rows if int(r['K']) == K_MAX]
    raw = [float(r['eta_sel']) for r in main if r['eta_sel']]
    ovr = [INF if float(r['n_steps_nonpos']) > 0 else float(r['eta_sel'])
           for r in main if r['eta_sel']]
    _, m_raw, _ = quantiles(raw)
    _, m_ovr, _ = quantiles(ovr)
    return dict(n_runs=len(main),
                eta_sel_median_pre_d3=m_raw,
                eta_sel_median_fixedk=m_ovr,
                eta_sel_cell_pre_d3=f'{m_raw:.1f}',
                eta_sel_cell_fixedk=f'{m_ovr:.1f}',
                LK_cell_pre_d3=f'{L_K_fixedk(m_raw, K_MAX):.3f}',
                LK_cell_fixedk=f'{L_K_fixedk(m_ovr, K_MAX):.3f}',
                n_inf_runs=sum(1 for x in ovr if x == INF))


# --------------------------------------------------------------------------
# 2. replay one run, recording (g_t, M_t) per step
# --------------------------------------------------------------------------
def replay(dataset, p, seed):
    """Re-run one E2 trajectory exactly as E2_run.run_one does (same graph, same
    subsample seed, same lazy greedy, same true-gain heap), but record only the
    two numbers D3 needs per step: g_t (true gain of the chosen element) and
    M_t (max true gain at the state)."""
    gtrue = E2.load_graph(dataset, None)
    gobs = gtrue.edge_subsample(p, seed)
    n = gtrue.n
    ground = list(range(n))
    true_state = E2.CoverageState(gtrue.out, n)
    obs_state = E2.CoverageState(gobs.out, n)
    true_top = E2.LazyTop(true_state, ground)
    F_obs = CachedSetFunction(E2.fast_value_fn(gobs, obs_state))
    steps = []

    def record(t, Sbefore, chosen, gain_tilde):
        assert obs_state.S == Sbefore, 'state desync'
        g = true_state.gain(chosen)
        top1 = true_top.top(1)
        M = top1[0][1] if top1 else None
        steps.append((float(g), None if M is None else float(M)))
        true_state.add(chosen)
        true_top.advance()
        obs_state.add(chosen)

    picks = lazy_greedy(F_obs, ground, K_MAX, record=record, quantize=None)
    return picks, steps, n


def a_t(g, M):
    """D3 step factor; returns (value, kind)."""
    if M is None:
        return None, 'undefined_M'
    if g < 0:
        return None, 'negative_gain_OUT_OF_MODEL'
    if g > 0:
        return M / g, 'positive'
    if M == 0:
        return 1.0, 'benign_zero'
    return INF, 'harmful_zero'


def eta_sel_prefixes(steps):
    """eta^sel under D3 for every prefix k = 1..len(steps)."""
    out, cur, kinds = [], 1.0, []
    for g, M in steps:
        a, kind = a_t(g, M)
        kinds.append(kind)
        if a is not None:
            cur = INF if (cur == INF or a == INF) else max(cur, a)
        out.append(cur)
    return out, kinds


# --------------------------------------------------------------------------
# 3. driver
# --------------------------------------------------------------------------
CONTROLS = [('email_eu_core', 0.3, 0), ('facebook_government', 0.5, 3),
            ('facebook_politician', 0.3, 0), ('facebook_artist', 0.5, 0)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audit-only', action='store_true')
    ap.add_argument('--runs', default='flagged+controls',
                    choices=['flagged', 'flagged+controls', 'all'])
    args = ap.parse_args()

    rows, runs, short, flagged = audit_rows()
    print(f'E2_rows.csv: {len(rows)} rows, {len(runs)} runs, '
          f'K_MAX={K_MAX}')
    print(f'runs whose prefix rows != 1..{K_MAX} (early-stopped runs): '
          f'{len(short)}')
    for s in short:
        print('   ', s)
    print(f'runs with n_steps_nonpos > 0 at K={K_MAX}: {len(flagged)}')
    for f in flagged:
        print('   ', f['run'], f['n_steps_nonpos'], f['eta_sel_csv'])

    tab = table_impact(rows)
    print(f'Table 1 E2 cells: eta^sel {tab["eta_sel_cell_pre_d3"]} (pre-D3) vs '
          f'{tab["eta_sel_cell_fixedk"]} (fixed-K/D3); L_K '
          f'{tab["LK_cell_pre_d3"]} vs {tab["LK_cell_fixedk"]}')

    summary = dict(k_max=K_MAX, n_rows=len(rows), n_runs=len(runs),
                   early_stopped_runs=short, flagged_runs=flagged,
                   table1_e2_cells=tab)
    if args.audit_only:
        print(json.dumps(summary, indent=1)[:400])
        return

    if args.runs == 'all':
        todo = [(d, float(p), int(s)) for (d, p, s) in sorted(runs)]
    else:
        todo = [(f['run'][0], float(f['run'][1]), int(f['run'][2]))
                for f in flagged]
        if args.runs == 'flagged+controls':
            todo += [c for c in CONTROLS if c not in todo]
    # group by dataset so each graph is loaded once (load_graph caches one)
    todo.sort(key=lambda z: (z[0], z[1], z[2]))

    out_rows, per_run, n_diff_rows, n_diff_runs = [], [], 0, 0
    for (ds, p, seed) in todo:
        picks, steps, n = replay(ds, p, seed)
        etas, kinds = eta_sel_prefixes(steps)
        n_zero = sum(1 for k in kinds if k in ('benign_zero', 'harmful_zero'))
        n_harm = kinds.count('harmful_zero')
        n_ben = kinds.count('benign_zero')
        bad = [k for k in kinds if k in ('negative_gain_OUT_OF_MODEL',
                                         'undefined_M')]
        csv_run = runs[(ds, str(p), str(seed))]
        run_changed = False
        for k in range(1, len(steps) + 1):
            r = csv_run[k]
            e_csv = float(r['eta_sel']) if r['eta_sel'] else None
            e_new = etas[k - 1]
            lk_csv = float(r['LK_eta_sel']) if r['LK_eta_sel'] else None
            lk_new = L_K_fixedk(e_new, k)
            # E2_rows.csv stores eta^sel with '%.6g' and L_K with '%.6f', so the
            # comparison tolerance must absorb that round-trip (relative 2e-5 on
            # eta, absolute 1e-4 on L_K); anything larger is a real difference.
            e_ch = (e_csv is None) != (e_new is None) or (
                e_csv is not None and e_new is not None
                and (e_new == INF or abs(e_csv - e_new) > 2e-5 * max(1.0, e_csv)))
            lk_ch = (lk_csv is None) or abs(lk_csv - lk_new) > 1e-4
            if e_ch:
                n_diff_rows += 1
                run_changed = True
            out_rows.append(dict(
                dataset=ds, p=p, seed=seed, K=k,
                eta_sel_csv=('' if e_csv is None else f'{e_csv:.6g}'),
                eta_sel_fixedk=('inf' if e_new == INF else f'{e_new:.6g}'),
                LK_csv=('' if lk_csv is None else f'{lk_csv:.6f}'),
                LK_fixedk=f'{lk_new:.6f}',
                is_inf=int(e_new == INF),
                n_steps_nonpos_csv=int(r['n_steps_nonpos']),
                n_zero_steps_replay=sum(
                    1 for kk in kinds[:k] if kk in ('benign_zero',
                                                    'harmful_zero')),
                n_harmful_zero_replay=kinds[:k].count('harmful_zero'),
                n_benign_zero_replay=kinds[:k].count('benign_zero'),
                eta_sel_changed=int(e_ch), LK_changed=int(lk_ch and e_ch)))
        if run_changed:
            n_diff_runs += 1
        first_harm = (kinds.index('harmful_zero') + 1
                      if 'harmful_zero' in kinds else None)
        per_run.append(dict(
            dataset=ds, p=p, seed=seed, n_steps_executed=len(picks),
            n_picks=len(picks), ground_n=n,
            n_zero_steps=n_zero, n_harmful_zero=n_harm, n_benign_zero=n_ben,
            first_harmful_step=first_harm,
            out_of_model_steps=len(bad),
            csv_n_steps_nonpos=int(csv_run[K_MAX]['n_steps_nonpos']),
            eta_sel_csv_K30=csv_run[K_MAX]['eta_sel'],
            eta_sel_fixedk_K30=('inf' if etas[-1] == INF else f'{etas[-1]:.6g}'),
            LK_csv_K30=csv_run[K_MAX]['LK_eta_sel'],
            LK_fixedk_K30=f'{L_K_fixedk(etas[-1], K_MAX):.6f}',
            changed=run_changed))
        print(f'  replay {ds} p={p} seed={seed}: steps={len(picks)} '
              f'zero={n_zero} (harmful={n_harm}, benign={n_ben}) '
              f'eta30 csv={csv_run[K_MAX]["eta_sel"]} -> '
              f'{per_run[-1]["eta_sel_fixedk_K30"]}', flush=True)

    with open(OUT_CSV, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=OUT_FIELDS)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    summary.update(
        replayed_runs=len(todo), replay_mode=args.runs,
        runs_with_short_trajectory=[r for r in per_run
                                    if r['n_steps_executed'] != K_MAX],
        n_runs_with_diff=n_diff_runs, n_prefix_rows_with_diff=n_diff_rows,
        per_run=per_run,
        conclusion_inputs=dict(
            greedy_loop_fixed_K=True,
            only_exit_besides_K='empty candidate pool',
            statistics_py_drops_nonpositive_steps=True),
    )
    with open(OUT_JSON, 'w') as fh:
        json.dump(summary, fh, indent=1)
    print(f'\nreplayed {len(todo)} runs; runs with a changed eta^sel: '
          f'{n_diff_runs}; prefix rows changed: {n_diff_rows}')
    print(f'wrote {OUT_CSV}\nwrote {OUT_JSON}')


if __name__ == '__main__':
    main()

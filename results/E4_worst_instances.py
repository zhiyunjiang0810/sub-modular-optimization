"""E4: run the theoretical worst-case instances through the EXPERIMENT pipeline.

Principles (TASKS_EXP.md): no artificial oracle noise (f, f~ here are the exact
lattice arrays of verified constructions); cached evaluations + CELF lazy greedy
(src/im_graph.py); fixed configs, CSV output; honest columns; CPU, < 30 min.

Instances:
- V_j instances (results/N2_check.py::build_lattice, the certified constructions
  of night 2) for K in {3,5,8}, one eta per segment j = 0..K-1
  (eta = K-j+0.5 for j >= 1, eta = K+1 for j = 0).
- U_K instances (code/check_explicit_instance.py::build) at ahat = 2.

Checks: |realized ratio - theory| <= 1e-10 through the experiment greedy (NOT
the symbolic verifier).  Also reports eta_sel / eta_path(eps=1e-9) / sign-viol %
on these instances (the three rulers' readings at the worst case).
Tie breaking: element index order = adversarial direction (C, P / B before O).
Outputs: results/E4_worst_case.csv (check table), results/E4_rows.csv (unified).
"""
import csv, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'code'))
from im_graph import CachedSetFunction, lazy_greedy, true_max_gain
from statistics import TrajectoryStats, unified_row, write_rows, ROW_FIELDS
from N2_check import build_lattice, Vj
import check_explicit_instance as uk

EPS = 1e-9


def run_instance(n, f_arr, g_arr, K, theory, label):
    mask = lambda S: sum(1 << e for e in S)
    F = CachedSetFunction(lambda S: float(f_arr[mask(S)]))
    G = CachedSetFunction(lambda S: float(g_arr[mask(S)]))
    ground = list(range(n))
    stats = TrajectoryStats(EPS)

    def record(t, Sbefore, chosen, gain_tilde):
        d_chosen = F.gain(Sbefore, chosen)
        dmax = true_max_gain(F, set(Sbefore), ground)
        pairs = [(F.gain(Sbefore, e), G.gain(Sbefore, e))
                 for e in ground if e not in Sbefore and e != chosen]
        pairs.append((d_chosen, gain_tilde))
        stats.add_step(d_chosen, dmax, pairs)

    # quantize=10: these instances have EXACT predicted-gain ties at every step
    # (adversarial tie-breaking is part of the construction); rounding gains to
    # 1e-10 before comparison keeps float noise (~1e-16) from flipping the tie,
    # and the element-index tie key then implements the adversarial direction.
    picks_tilde = lazy_greedy(G, ground, K, record=record, quantize=10)
    picks_true = lazy_greedy(F, ground, K, quantize=10)
    num = F(set(picks_tilde))
    den = F(set(picks_true))
    ratio = num / den
    st = stats.upto(K)
    return dict(label=label, realized=ratio, theory=theory,
                diff=abs(ratio - theory), den=den,
                eta_sel=st['eta_sel'], eta_path=st['eta_path'],
                viol=st['viol_sign_pct']), st, ratio


def main():
    rows_check, rows_uni = [], []
    ok = True
    for K in (3, 5, 8):
        for j in range(K - 1, -1, -1):
            eta = (K - j) + 0.5 if j >= 1 else K + 1.0
            I, n, N, f_arr, g_arr = build_lattice(K, j, eta)
            r, st, ratio = run_instance(n, f_arr, g_arr, K,
                                        float(Vj(K, j, eta)), f'Vj_K{K}_j{j}')
            r['eta'] = eta
            ok &= r['diff'] <= 1e-10 and abs(r['den'] - 1.0) <= 1e-12
            rows_check.append(r)
            rows_uni.append(unified_row('E4', f'Vj_K{K}_j{j}', K, 0, ratio, st))
            print(f"V_j  K={K} j={j} eta={eta:4.1f}: realized={r['realized']:.12f} "
                  f"theory={r['theory']:.12f} diff={r['diff']:.2e} "
                  f"eta_sel={r['eta_sel']:.4f} eta_path={r['eta_path']:.4f} "
                  f"viol%={r['viol']:.1f}", flush=True)
    for K in (3, 5, 8):
        ahat = 2.0
        a, n, N, f_arr, g_arr = uk.build(K, ahat)
        theory = 1 - (1 - 1 / (ahat * K)) ** K       # ratio of the U_K instance
        r, st, ratio = run_instance(n, f_arr, g_arr, K, theory, f'UK_K{K}')
        r['eta'] = (ahat * K - 1) / (K - 1)
        ok &= r['diff'] <= 1e-10
        rows_check.append(r)
        rows_uni.append(unified_row('E4', f'UK_K{K}', K, 0, ratio, st))
        print(f"U_K  K={K} ahat=2:      realized={r['realized']:.12f} "
              f"theory={r['theory']:.12f} diff={r['diff']:.2e} "
              f"eta_sel={r['eta_sel']:.4f} eta_path={r['eta_path']:.4f}", flush=True)
    with open(os.path.join(HERE, 'E4_worst_case.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['label', 'eta', 'realized', 'theory',
                                           'diff', 'den', 'eta_sel', 'eta_path', 'viol'])
        w.writeheader()
        for r in rows_check:
            w.writerow(r)
    write_rows(os.path.join(HERE, 'E4_rows.csv'), rows_uni)
    print('ALL WITHIN 1e-10' if ok else 'SOME CHECKS FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

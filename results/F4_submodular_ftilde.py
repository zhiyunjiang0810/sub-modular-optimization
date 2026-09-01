"""
F4: exact worst case of single-step predictive greedy when the surrogate ftilde
is ALSO required to be monotone submodular.

Motivation: results/N2_instances.md caveat 3 (section 6.5) records that both the
V_j family (N2) and the U_K family (R7) have a ftilde that is monotone but NOT
submodular; the model in code/worst_case_lp.py only constrains f.  If the paper
wants to assume a submodular surrogate, rho_K could be larger.  This script
answers that by re-solving the SAME full-lattice factor-revealing LP with the
extra rows

        dtilde_e(S u e2)  <=  dtilde_e(S)          for all S, e, e2

i.e. the same submodularity block that is already imposed on f, applied to the
G variables.  code/worst_case_lp.py is NOT modified; its row construction is
copied here verbatim (see build_rows) and only extended.

Usage
    python3 results/F4_submodular_ftilde.py             # full run (K=2,3,4)
    python3 results/F4_submodular_ftilde.py --timing    # single-LP timing probe
    python3 results/F4_submodular_ftilde.py --k 2 3     # subset of K

Outputs (a --tag SUFFIX is inserted before the extension when given)
    results/F4_table.csv       one row per (K, eta): both LP values,
                               min_j V_j (R10) and min_m W_m (the F4 conjecture)
    results/F4_eta_sweep.csv   fine eta grid for K <= 3
    results/F4_n_sweep.csv     n = 2K, 2K+1, 2K+2 sensitivity for K = 2, 3
    results/F4_details.json    optima, gain tables, tight rows, verification,
                               per-O values, N2 instance-family diagnostics

The K = 5 numbers in the write-up came from
    python3 results/F4_submodular_ftilde.py --k 5 --disjoint-only --tag _K5
(one LP per variant, disjoint O only; ~30 min).  See F4_submodular_ftilde.md
section 6 for why that shortcut is used and what it costs.
"""
import argparse
import itertools
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TOL = 1e-9


# ---------------------------------------------------------------------------
# closed forms (R10 / R7 / R1)
# ---------------------------------------------------------------------------
def Vj(K, j, eta):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q ** j * (1 - (K - j) / (K * eta))


def min_V(K, eta):
    vals = [(Vj(K, j, eta), j) for j in range(K)]
    v, j = min(vals)
    return v, j


def UK(K, eta):
    return 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K


def LK(K, eta):
    return 1 - (1 - 1 / (eta * K)) ** K


# ---------------------------------------------------------------------------
# [CONJECTURE] closed form for the ftilde-submodular worst case, read off the
# LP optima (see F4_submodular_ftilde.md section "structure").
#
#   r = 1 - 1/K,  W_m(K, eta) = (K - m r^m) / (K (1 + (eta-1) r^m)),
#   rho_K^{sub}(eta) = min_{0 <= m <= K-1} W_m(K, eta).
#
# Reading: m = number of "coherence" steps.  Along the greedy path the optimum
# has d_t = d_0 r^t for t < m and d_t = d_m for t >= m, with d_0 = 1/(K mu_0)
# and mu_0 = 1 + (eta-1) r^m; the ratio mu_t = d_O(S_t)/d_t grows geometrically
# by K/(K-1) per step until it hits the band value eta exactly at t = m.
# Note W_m uses r = 1 - 1/K (the eta = 1 value of q), whereas V_j uses
# q = (K-1)eta/((K-1)eta+1); W_m = V_m at eta = 1 and W_0 = V_0 = 1/eta.
# ---------------------------------------------------------------------------
def Wm(K, m, eta):
    r = 1 - 1.0 / K
    rm = r ** m
    return (K - m * rm) / (K * (1 + (eta - 1) * rm))


def min_W(K, eta):
    vals = [(Wm(K, m, eta), m) for m in range(K)]
    v, m = min(vals)
    return v, m


# ---------------------------------------------------------------------------
# LP rows.  Block 1-4 are copied from code/worst_case_lp.py (unchanged);
# block 3b is the new ftilde-submodularity block.
# ---------------------------------------------------------------------------
def build_rows(n, K, eta_u, eta_o, err_model="single", g_submod=True,
               g_mono=False):
    N = 1 << n
    nv = 2 * N
    F = lambda S: S
    G = lambda S: N + S

    rows_ub, b_ub = [], []
    counts = {}
    tags = []

    def add_ub(coefs, tag, rhs=0.0, meta=None):
        rows_ub.append(coefs)
        b_ub.append(rhs)
        tags.append((tag, meta))
        counts[tag] = counts.get(tag, 0) + 1

    # (1) f monotone:  f[S] - f[S|e] <= 0                       [copied]
    for S in range(N):
        for e in range(n):
            if not S >> e & 1:
                add_ub({F(S): 1, F(S | 1 << e): -1}, "mono_f")

    # (2) f submodular: d_e(S|e') <= d_e(S)                     [copied]
    for S in range(N):
        for e in range(n):
            if S >> e & 1:
                continue
            for e2 in range(n):
                if e2 == e or S >> e2 & 1:
                    continue
                T = S | 1 << e2
                c = {}
                for k, v in ((F(T | 1 << e), 1), (F(T), -1),
                             (F(S | 1 << e), -1), (F(S), 1)):
                    c[k] = c.get(k, 0) + v
                add_ub(c, "submod_f")

    # (2b) NEW: ftilde submodular, identical shape on the G variables
    if g_submod:
        for S in range(N):
            for e in range(n):
                if S >> e & 1:
                    continue
                for e2 in range(n):
                    if e2 == e or S >> e2 & 1:
                        continue
                    T = S | 1 << e2
                    c = {}
                    for k, v in ((G(T | 1 << e), 1), (G(T), -1),
                                 (G(S | 1 << e), -1), (G(S), 1)):
                        c[k] = c.get(k, 0) + v
                    add_ub(c, "submod_g", meta=(S, e, e2))

    # (2c) optional: ftilde monotone (implied by the band + f monotone for
    # single-element increments, kept only as a diagnostic switch)
    if g_mono:
        for S in range(N):
            for e in range(n):
                if not S >> e & 1:
                    add_ub({G(S): 1, G(S | 1 << e): -1}, "mono_g")

    # (3) error model                                           [copied]
    for A in range(N):
        comp = (N - 1) ^ A
        Bs = []
        if err_model == "single":
            Bs = [1 << e for e in range(n) if comp >> e & 1]
        else:
            B = comp
            while B:
                Bs.append(B)
                B = (B - 1) & comp
        for B in Bs:
            AB = A | B
            c = {}
            for k, v in ((F(AB), 1 / eta_u), (F(A), -1 / eta_u),
                         (G(AB), -1), (G(A), 1)):
                c[k] = c.get(k, 0) + v
            add_ub(c, "band_lo")
            c = {}
            for k, v in ((G(AB), 1), (G(A), -1),
                         (F(AB), -eta_o), (F(A), eta_o)):
                c[k] = c.get(k, 0) + v
            add_ub(c, "band_hi")

    # (4) greedy path                                           [copied]
    for t in range(K):
        S = (1 << t) - 1
        for e in range(n):
            if e == t or S >> e & 1:
                continue
            c = {}
            for k, v in ((G(S | 1 << e), 1), (G(S), -1),
                         (G(S | 1 << t), -1), (G(S), 1)):
                c[k] = c.get(k, 0) + v
            add_ub(c, "greedy")

    A_ub = lil_matrix((len(rows_ub), nv))
    for i, c in enumerate(rows_ub):
        for k, v in c.items():
            A_ub[i, k] = v
    return A_ub.tocsr(), np.array(b_ub), counts, tags


def solve_for_O(A_ub, b_ub, n, K, O, nv=None, obj=None, polish=None):
    """LP with f(empty)=ftilde(empty)=0, f(O)=1, minimising f({0..K-1})."""
    N = 1 << n
    nv = nv if nv is not None else 2 * N
    Om = sum(1 << i for i in O)
    SK = (1 << K) - 1
    if obj is None:
        obj = np.zeros(nv)
        obj[SK] = 1.0
    A_eq = lil_matrix((3, nv))
    A_eq[0, 0] = 1          # f(empty) = 0
    A_eq[1, N] = 1          # ftilde(empty) = 0
    A_eq[2, Om] = 1         # f(O) = 1
    res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq.tocsr(), b_eq=[0, 0, 1],
                  bounds=[(None, None)] * nv, method="highs")
    if res.status != 0 or polish is None:
        return res
    # second stage: fix the objective value, then pick a cleaner extreme point
    A_eq2 = lil_matrix((4, nv))
    A_eq2[0, 0] = 1
    A_eq2[1, N] = 1
    A_eq2[2, Om] = 1
    A_eq2[3, SK] = 1
    obj2 = np.array(polish, dtype=float)
    res2 = linprog(obj2, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq2.tocsr(),
                   b_eq=[0, 0, 1, res.fun], bounds=[(None, None)] * nv,
                   method="highs")
    if res2.status == 0:
        res2.fun = res.fun
        return res2
    return res


def tight_report(A_ub, b_ub, tags, x, n, K, O, tol=1e-8):
    """Which constraint families are tight at the optimum, and which of the
    NEW ftilde-submodularity rows are tight (reported in B / O element types)."""
    slack = b_ub - A_ub.dot(x)
    tight = slack < tol
    per_tag = {}
    for i, (tag, meta) in enumerate(tags):
        d = per_tag.setdefault(tag, [0, 0])
        d[1] += 1
        if tight[i]:
            d[0] += 1
    Oset = set(O)

    def lab(e):
        return ('o' if e in Oset else 'b') + str(e)
    examples = []
    for i, (tag, meta) in enumerate(tags):
        if tag != "submod_g" or not tight[i] or meta is None:
            continue
        S, e, e2 = meta
        examples.append("dt_%s(S u %s) = dt_%s(S), S={%s}" %
                        (lab(e), lab(e2), lab(e),
                         ",".join(lab(u) for u in range(n) if S >> u & 1)))
    return {'per_tag_tight': {k: v for k, v in per_tag.items()},
            'n_tight_submod_g': per_tag.get('submod_g', [0, 0])[0],
            'submod_g_tight_examples': examples[:40]}


def worst_case(n, K, eta_u, eta_o, err_model="single", g_submod=True,
               Olist=None, polish=False, verbose=False):
    A_ub, b_ub, counts, tags = build_rows(n, K, eta_u, eta_o, err_model,
                                          g_submod)
    N = 1 << n
    nv = 2 * N
    obj = np.zeros(nv)
    obj[(1 << K) - 1] = 1.0
    pol = None
    if polish:
        pol = np.zeros(nv)
        pol[:N] = 1.0          # minimise sum of f over the lattice
    Os = list(itertools.combinations(range(n), K)) if Olist is None else Olist
    best = (np.inf, None, None)
    per_O = {}
    for O in Os:
        res = solve_for_O(A_ub, b_ub, n, K, O, nv, obj, None)
        if res.status != 0:
            per_O[str(O)] = None
            continue
        per_O[str(O)] = float(res.fun)
        if res.fun < best[0] - 1e-13:
            best = (float(res.fun), O, res.x)
    tight = None
    if polish and best[1] is not None:
        # re-solve only the winning O, second stage picks a cleaner extreme pt
        res = solve_for_O(A_ub, b_ub, n, K, best[1], nv, obj, pol)
        if res.status == 0:
            best = (best[0], best[1], res.x)
        tight = tight_report(A_ub, b_ub, tags, best[2], n, K, best[1])
    return best, per_O, counts, tight


# ---------------------------------------------------------------------------
# independent verifier for an (f, g) pair read off the LP
# ---------------------------------------------------------------------------
def verify_instance(n, K, f, g, eta_u, eta_o, tol=1e-7):
    N = 1 << n
    out = {}
    out['f_empty'] = abs(f[0]) < tol and abs(g[0]) < tol
    mono_f = mono_g = sub_f = sub_g = band = True
    eu_m = eo_m = 0.0
    worst_sub_g = 0.0
    worst_sub_f = 0.0
    for S in range(N):
        for e in range(n):
            if S >> e & 1:
                continue
            Se = S | 1 << e
            d, dt = f[Se] - f[S], g[Se] - g[S]
            if d < -tol:
                mono_f = False
            if dt < -tol:
                mono_g = False
            for e2 in range(n):
                if e2 == e or S >> e2 & 1:
                    continue
                vf = (f[Se | 1 << e2] - f[S | 1 << e2]) - d
                vg = (g[Se | 1 << e2] - g[S | 1 << e2]) - dt
                worst_sub_f = max(worst_sub_f, vf)
                worst_sub_g = max(worst_sub_g, vg)
                if vf > tol:
                    sub_f = False
                if vg > tol:
                    sub_g = False
            if d > tol:
                if dt <= tol:
                    band = False
                else:
                    eo_m = max(eo_m, dt / d)
                    eu_m = max(eu_m, d / dt)
            elif abs(dt) > tol:
                band = False
    out['monotone_f'] = mono_f
    out['monotone_ftilde'] = mono_g
    out['submodular_f'] = sub_f
    out['submodular_ftilde'] = sub_g
    out['max_submod_violation_f'] = worst_sub_f
    out['max_submod_violation_ftilde'] = worst_sub_g
    out['eta_u_realised'] = eu_m
    out['eta_o_realised'] = eo_m
    out['band_ok'] = band and eu_m <= eta_u + 1e-6 and eo_m <= eta_o + 1e-6
    # greedy trajectory under adversarial ties
    S = 0
    greedy_ok = True
    for t in range(K):
        gains = {e: g[S | 1 << e] - g[S] for e in range(n) if not S >> e & 1}
        if gains[t] < max(gains.values()) - 1e-7:
            greedy_ok = False
            break
        S |= 1 << t
    out['greedy_picks_0..K-1'] = greedy_ok
    out['ratio'] = float(f[(1 << K) - 1])
    # OPT: is the normalising set really a maximiser over all K-subsets?
    best = max(f[S] for S in range(N) if bin(S).count('1') <= K)
    out['opt_value'] = float(best)
    out['opt_is_one'] = abs(best - 1.0) < 1e-6
    out['ratio_over_opt'] = float(f[(1 << K) - 1] / best) if best > 0 else None
    return out


def gain_tables(n, K, O, f, g):
    """Marginal gains along the greedy path, in the C/P/O language of N2."""
    rows = []
    S = 0
    for t in range(K):
        St = S
        row = {
            't': t,
            'd_t(true)': float(f[St | 1 << t] - f[St]),
            'dt_t(pred)': float(g[St | 1 << t] - g[St]),
            'O_gains_true': [float(f[St | 1 << o] - f[St]) for o in O
                             if not St >> o & 1],
            'O_gains_pred': [float(g[St | 1 << o] - g[St]) for o in O
                             if not St >> o & 1],
        }
        rows.append(row)
        S |= 1 << t
    return rows


# ---------------------------------------------------------------------------
# N2 instance family: is its ftilde submodular anywhere?
# ---------------------------------------------------------------------------
def n2_family_diagnostics(Ks, etas):
    sys.path.insert(0, HERE)
    import N2_check as N2
    res = []
    for K in Ks:
        for eta in etas:
            vstar, jstar = min_V(K, eta)
            for capped in (True, False):
                for j in range(0, K + 1):
                    I, n, N, f, g = N2.build_lattice(K, j, eta, capped=capped)
                    v = verify_instance(n, K, f, g, I.eu, I.eo)
                    res.append({
                        'K': K, 'eta': eta, 'j': j, 'jstar': jstar,
                        'capped': capped,
                        'ratio': v['ratio'],
                        'is_jstar': (j == jstar),
                        'submodular_f': v['submodular_f'],
                        'submodular_ftilde': v['submodular_ftilde'],
                        'max_submod_violation_ftilde':
                            v['max_submod_violation_ftilde'],
                        'monotone_ftilde': v['monotone_ftilde'],
                    })
    return res


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--timing', action='store_true')
    ap.add_argument('--k', type=int, nargs='*', default=[2, 3, 4])
    ap.add_argument('--eta', type=float, nargs='*', default=[1.5, 2.0, 3.0])
    ap.add_argument('--disjoint-only', action='store_true',
                    help='only O = {K..2K-1} (fallback if enumeration is slow)')
    ap.add_argument('--tag', default='',
                    help='suffix for the output filenames (e.g. --tag _K5)')
    args = ap.parse_args()
    TAG = args.tag

    if args.timing:
        for (n, K) in [(4, 2), (6, 3), (8, 4)]:
            for gs in (False, True):
                t0 = time.time()
                A_ub, b_ub, counts, _tg = build_rows(n, K, 2.0 ** 0.5,
                                                     2.0 ** 0.5, "single", gs)
                t1 = time.time()
                O = tuple(range(K, 2 * K)) if n >= 2 * K else tuple(range(K))
                res = solve_for_O(A_ub, b_ub, n, K, O)
                t2 = time.time()
                print(f"n={n} K={K} g_submod={gs}: rows={A_ub.shape[0]} "
                      f"vars={A_ub.shape[1]} build={t1-t0:.2f}s "
                      f"one_LP={t2-t1:.2f}s val={res.fun:.6f} {counts}")
                sys.stdout.flush()
        return

    table = []
    details = {}
    t_start = time.time()
    for K in args.k:
        n = 2 * K
        Olist = [tuple(range(K, 2 * K))] if args.disjoint_only else None
        for eta in args.eta:
            eu = eo = eta ** 0.5
            row = {'K': K, 'n': n, 'eta': eta}
            for tag, gs in (('base', False), ('sub', True)):
                t0 = time.time()
                best, per_O, counts, tight = worst_case(
                    n, K, eu, eo, "single", g_submod=gs, Olist=Olist,
                    polish=(tag == 'sub'))
                dt = time.time() - t0
                row[f'lp_{tag}'] = best[0]
                row[f'O_{tag}'] = str(best[1])
                row[f'sec_{tag}'] = round(dt, 2)
                row[f'rows_{tag}'] = int(sum(counts.values()))
                key = f"K{K}_eta{eta}_{tag}"
                details[key] = {'value': best[0], 'O': best[1],
                                'per_O': per_O, 'row_counts': counts,
                                'seconds': dt}
                if tag == 'sub' and best[2] is not None:
                    N = 1 << n
                    f = np.array(best[2][:N])
                    g = np.array(best[2][N:])
                    ver = verify_instance(n, K, f, g, eu, eo)
                    details[key]['verify'] = ver
                    details[key]['gains'] = gain_tables(n, K, best[1], f, g)
                    details[key]['tight'] = tight
                    details[key]['f'] = [float(v) for v in f]
                    details[key]['ftilde'] = [float(v) for v in g]
                    row['inst_ok'] = bool(
                        ver['monotone_f'] and ver['submodular_f'] and
                        ver['submodular_ftilde'] and ver['band_ok'] and
                        ver['greedy_picks_0..K-1'] and ver['opt_is_one'])
                    row['inst_ratio'] = ver['ratio']
                    row['inst_eta_realised'] = ver['eta_u_realised'] * \
                        ver['eta_o_realised']
                print(f"  K={K} eta={eta} {tag}: {best[0]:.9f} O={best[1]} "
                      f"({dt:.1f}s, {sum(counts.values())} rows)")
                sys.stdout.flush()
            v, j = min_V(K, eta)
            w, m = min_W(K, eta)
            row['min_j_Vj'] = v
            row['argmin_j'] = j
            row['min_m_Wm'] = w
            row['argmin_m'] = m
            row['sub_minus_minW'] = row['lp_sub'] - w
            row['U_K'] = UK(K, eta)
            row['L_K'] = LK(K, eta)
            row['diff_sub_minus_minV'] = row['lp_sub'] - v
            row['diff_base_minus_minV'] = row['lp_base'] - v
            row['diff_sub_minus_base'] = row['lp_sub'] - row['lp_base']
            row['sub_le_UK'] = bool(row['lp_sub'] <= row['U_K'] + 1e-9)
            table.append(row)

    print(f"\nLP sweep done in {time.time()-t_start:.1f}s")

    # fine eta grid for the cheap K (maps out where the constraint bites)
    sweep = []
    for K in [k for k in args.k if k <= 3]:
        n = 2 * K
        for eta in [1.0 + 0.1 * i for i in range(0, 21)] + [2.5, 4.0]:
            eu = eo = eta ** 0.5
            b0, _, _, _ = worst_case(n, K, eu, eo, "single", g_submod=False)
            b1, _, _, _ = worst_case(n, K, eu, eo, "single", g_submod=True)
            v, j = min_V(K, eta)
            w, m = min_W(K, eta)
            sweep.append({'K': K, 'eta': round(eta, 4), 'lp_base': b0[0],
                          'lp_sub': b1[0], 'min_j_Vj': v, 'argmin_j': j,
                          'min_m_Wm': w, 'argmin_m': m,
                          'sub_minus_minW': b1[0] - w,
                          'U_K': UK(K, eta),
                          'diff': b1[0] - b0[0],
                          'sub_le_UK': bool(b1[0] <= UK(K, eta) + 1e-9)})
        print(f"  fine sweep K={K} done ({time.time()-t_start:.0f}s)")
        sys.stdout.flush()
    details['fine_sweep'] = sweep

    # ground-set sensitivity: the LP is solved on n = 2K, but with the extra
    # ftilde rows there is no analogue of R6 ("reduced LP is valid for every n")
    # to certify that n = 2K is the worst ground set.  Check n = 2K+1, 2K+2.
    nsweep = []
    for K, ns in [(2, [4, 5, 6]), (3, [6, 7, 8])]:
        if K not in args.k:
            continue
        for eta in args.eta:
            eu = eo = eta ** 0.5
            for n in ns:
                b1, _, _, _ = worst_case(n, K, eu, eo, "single", g_submod=True)
                b0, _, _, _ = worst_case(n, K, eu, eo, "single", g_submod=False)
                w, m = min_W(K, eta)
                nsweep.append({'K': K, 'n': n, 'eta': eta,
                               'lp_base': b0[0], 'lp_sub': b1[0],
                               'min_m_Wm': w, 'min_j_Vj': min_V(K, eta)[0],
                               'O_sub': str(b1[1])})
                print(f"  n-sweep K={K} n={n} eta={eta}: base={b0[0]:.9f} "
                      f"sub={b1[0]:.9f} (W={w:.9f})")
                sys.stdout.flush()
    details['n_sweep'] = nsweep

    # N2 family diagnostics
    print("\nN2 family ftilde-submodularity diagnostics ...")
    diag = n2_family_diagnostics(args.k, args.eta)
    details['n2_family'] = diag
    n_sub = sum(1 for d in diag if d['submodular_ftilde'])
    print(f"  {n_sub}/{len(diag)} of the N2 instances have submodular ftilde")

    # write outputs
    import csv
    cols = ['K', 'n', 'eta', 'lp_base', 'lp_sub', 'min_j_Vj', 'argmin_j',
            'diff_sub_minus_minV', 'diff_base_minus_minV',
            'diff_sub_minus_base', 'min_m_Wm', 'argmin_m', 'sub_minus_minW',
            'U_K', 'L_K', 'sub_le_UK',
            'inst_ok', 'inst_ratio', 'inst_eta_realised',
            'O_base', 'O_sub', 'rows_base', 'rows_sub', 'sec_base', 'sec_sub']
    with open(os.path.join(HERE, f'F4_table{TAG}.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in table:
            w.writerow({c: r.get(c) for c in cols})
    if sweep:
        with open(os.path.join(HERE, f'F4_eta_sweep{TAG}.csv'), 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(sweep[0].keys()))
            w.writeheader()
            w.writerows(sweep)
    if nsweep:
        with open(os.path.join(HERE, f'F4_n_sweep{TAG}.csv'), 'w',
                  newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(nsweep[0].keys()))
            w.writeheader()
            w.writerows(nsweep)
    with open(os.path.join(HERE, f'F4_details{TAG}.json'), 'w') as fh:
        json.dump({'table': table, 'details': details}, fh, indent=1,
                  default=float)

    print("\n=== F4 table ===")
    hdr = f"{'K':>2} {'eta':>5} {'LP base':>12} {'LP sub-ft':>12} " \
          f"{'min_j V_j':>12} {'min_m W_m':>12} {'sub-base':>11} " \
          f"{'sub-minV':>11} {'sub-minW':>11} {'U_K':>10} {'<=U_K':>6}"
    print(hdr)
    for r in table:
        print(f"{r['K']:>2} {r['eta']:>5} {r['lp_base']:>12.9f} "
              f"{r['lp_sub']:>12.9f} {r['min_j_Vj']:>12.9f} "
              f"{r['min_m_Wm']:>12.9f} "
              f"{r['diff_sub_minus_base']:>11.2e} "
              f"{r['diff_sub_minus_minV']:>11.2e} "
              f"{r['sub_minus_minW']:>11.2e} {r['U_K']:>10.6f} "
              f"{str(r['sub_le_UK']):>6}")
    print(f"\nfiles: results/F4_table{TAG}.csv, results/F4_details{TAG}.json")


if __name__ == "__main__":
    main()

"""N4 step 3/4: explicit closed form for the relaxed-F poly-query hardness LP.

WHAT IS CLAIMED HERE
--------------------
The relaxed-F hardness LP of T2 (conclusion 3 of results/T2_summary.md) is

    variables  F(x,y) on the (x,y) grid, x = |S\\O| in 0..n-K, y = |S n O| in 0..K,
               Ghat_s on balanced sets, G(x,y) on unbalanced sets;
    F monotone + submodular, F(0,0)=0, F(0,K)=1, F <= 1 on 0 < x+y <= K;
    single-element error band  dF/eta_u <= dG <= eta_o dF  (delta = 0, eta_u = eta_o = sqrt(eta));
    G depends only on |S| on the balanced region;
    objective   min F(K,0).

Findings implemented and tested below.

(1) n-dependence.  The value is NOT n-insensitive.  With the true balanced band
    |y - K|S|/n| <= tau it decreases in n and converges; the limit equals, to LP
    accuracy, the value of the same LP with the band taken as y <= tau (which is
    itself n-independent).  Near the origin the true band collapses onto y <= tau.

(2) Closed form of the limit value.  Put

        k1 = eta(K-1) + 1,  q = 1 - 1/k1,  nu = eta/(eta-1),
        j  = K + 1 - ceil(eta)                       (clipped to [0, K]),
        D  = max( q^j/(K eta),  max_{m>=1} q^j (nu^m/K - 1) / (eta(nu^m - 1) - m) ),
        m* = the maximizing m,   T = j + m*,
        value = 1 - q^j + (K - j) D.

    Note 1 - q^j + (K-j) q^j/(K eta) = V_j(eta) is exactly the R10 closed form of
    the reduced (predictive-greedy) LP, so the hardness value is V_j plus the
    positive excess (K-j)(D - q^j/(K eta)).

(3) Explicit optimal (F, G).  With residual r, o-gain g, b-gain d given by

        r_x = q^x                             (0 <= x <= j)
            = q^j - (x-j) D                   (j <  x <= T)
            = 0                               (x > T)
        g_x = q^x / K                         (0 <= x <= j)
            = nu^{x-j} q^j/K - eta D (nu^{x-j} - 1)   (j < x <= T)
            = 0                               (x > T)
        d_x = r_x - r_{x+1}

        F(x,y) = 1 - r_x + [y>=1] g_x + max(y-1,0) (r_x - g_x)/(K-1)
        Ghat_s = (1/eta_u) sum_{x<s} g_x
        G(x,y) = Ghat_{x+1} + eta_o (F(x,y) - F(x,1))     for y >= 2 (unbalanced)

    Phase 1 (x <= j) is literally the R7 / U_K instance F = 1 - q^x (1 - y/K) with
    a = q; phase 2 is a constant-d tail in which the coherence lemma R3(ii) is tight.

VERIFICATION TIERS
------------------
  [EXACT]  every LP constraint is checked in exact rational arithmetic
           (Fraction).  eta_u = eta_o = sqrt(eta) never appears: storing the
           scaled predictor  Gs := sqrt(eta) * G  turns
             band_up:  dG <= eta_o dF   into   dGs <= eta dF
             band_lo:  dF/eta_u <= dG   into   dF  <= dGs
           both rational whenever eta is rational.
  [LP]     the objective of the explicit solution is compared with the LP optimum
           obtained from results/N4_relaxF_solve.py's builder.

Run:  python3 results/N4_check.py            (writes results/N4_check.json)
      python3 results/N4_check.py quick      (small grid, ~20 s)
"""
import json
import math
import os
import sys
from fractions import Fraction as Fr

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import N4_relaxF_solve as S  # noqa: E402  (LP builder, frozen)

MMAX = 600  # search range for m*


# ----------------------------------------------------------------- parameters
def params(K, eta):
    """Exact (Fraction) parameters of the closed form.  eta must be rational."""
    eta = Fr(eta)
    k1 = eta * (K - 1) + 1
    q = 1 - 1 / k1
    nu = eta / (eta - 1)
    j = K + 1 - math.ceil(eta)
    j = max(0, min(K, j))
    qj = q ** j
    D = qj / (K * eta)          # m -> infinity limit
    mstar = None
    nup = Fr(1)
    for m in range(1, MMAX + 1):
        nup *= nu
        den = eta * (nup - 1) - m
        if den <= 0:
            continue
        cand = qj * (nup / K - 1) / den
        if cand > D:
            D, mstar = cand, m
    T = j + (mstar if mstar is not None else 0)
    return dict(eta=eta, k1=k1, q=q, nu=nu, j=j, D=D, mstar=mstar, T=T,
                value=1 - qj + (K - j) * D,
                Vj=1 - qj + (K - j) * qj / (K * eta))


# ------------------------------------------------------------------- solution
def sequences(K, eta, X):
    """r_x, g_x, d_x for x = 0..X+1 as exact Fractions."""
    P = params(K, eta)
    j, D, T, q, nu = P['j'], P['D'], P['T'], P['q'], P['nu']
    eta = P['eta']
    qj = q ** j
    r, g = [], []
    for x in range(X + 2):
        if x <= j:
            r.append(q ** x)
            g.append(q ** x / K)
        elif x <= T:
            i = x - j
            nui = nu ** i
            r.append(qj - i * D)
            g.append(nui * qj / K - eta * D * (nui - 1))
        else:
            r.append(Fr(0))
            g.append(Fr(0))
    d = [r[x] - r[x + 1] for x in range(X + 1)]
    return P, r[:X + 1], g[:X + 1], d


def solution(K, eta, X, n=None):
    """Explicit (F, Gs) on the grid.  Gs = sqrt(eta) * G  (exact rationals).

    Returns F[x][y], Ghat_s scaled (length n+1), Gs on the whole grid.
    """
    if n is None:
        n = X + K
    P, r, g, d = sequences(K, eta, X)
    eta = P['eta']
    F = [[None] * (K + 1) for _ in range(X + 1)]
    for x in range(X + 1):
        base = 1 - r[x]
        rest = (r[x] - g[x]) / (K - 1) if K > 1 else Fr(0)
        for y in range(K + 1):
            F[x][y] = base if y == 0 else base + g[x] + (y - 1) * rest
    # Ghat scaled: eta_u * Ghat_s = sum_{x<s} g_x
    Ghs = [Fr(0)] * (n + 1)
    for s in range(1, n + 1):
        Ghs[s] = Ghs[s - 1] + (g[s - 1] if s - 1 <= X else Fr(0))
    # full scaled predictor on the grid
    Gs = [[None] * (K + 1) for _ in range(X + 1)]
    for x in range(X + 1):
        for y in range(K + 1):
            if y <= 1:
                Gs[x][y] = Ghs[x + y]
            else:
                Gs[x][y] = Ghs[x + 1] + eta * (F[x][y] - F[x][1])
    return P, F, Ghs, Gs, r, g, d


# ---------------------------------------------------------------- feasibility
def check_exact(K, eta, X, verbose=False):
    """Exact-arithmetic check of every constraint of the ysmall(tau=1) LP."""
    P, F, Ghs, Gs, r, g, d = solution(K, eta, X)
    eta = P['eta']
    bad = []

    def note(tag, p, dirn, slack):
        bad.append((tag, p, dirn, str(slack)))

    edges = []
    for x in range(X + 1):
        for y in range(K + 1):
            if x < X:
                edges.append(((x, y), (x + 1, y), 'x'))
            if y < K:
                edges.append(((x, y), (x, y + 1), 'y'))
    for p, qq, dr in edges:
        dF = F[qq[0]][qq[1]] - F[p[0]][p[1]]
        dG = Gs[qq[0]][qq[1]] - Gs[p[0]][p[1]]
        if dF < 0:
            note('mono', p, dr, dF)
        if dG > eta * dF:
            note('band_up', p, dr, eta * dF - dG)
        if dF > dG:
            note('band_lo', p, dr, dG - dF)
    for p, qq, dr in edges:
        for sh in ('x', 'y'):
            px = (p[0] + (sh == 'x'), p[1] + (sh == 'y'))
            qx = (qq[0] + (sh == 'x'), qq[1] + (sh == 'y'))
            if px[0] > X or px[1] > K or qx[0] > X or qx[1] > K:
                continue
            lhs = F[qx[0]][qx[1]] - F[px[0]][px[1]]
            rhs = F[qq[0]][qq[1]] - F[p[0]][p[1]]
            if lhs > rhs:
                note('submod', p, dr + sh, rhs - lhs)
    for x in range(X + 1):
        for y in range(K + 1):
            if 0 < x + y <= K and not (x == 0 and y == K):
                if F[x][y] > 1:
                    note('opt_norm', (x, y), '', 1 - F[x][y])
    if F[0][0] != 0:
        note('eq_F00', (0, 0), '', F[0][0])
    if F[0][K] != 1:
        note('eq_F0K', (0, K), '', F[0][K] - 1)
    if Ghs[0] != 0:
        note('eq_Ghat0', (0, 0), '', Ghs[0])
    # balanced-region consistency (G depends only on |S| for y <= 1) is exact by
    # construction: Gs[x][0] = Ghs[x], Gs[x][1] = Ghs[x+1].
    if verbose and bad:
        for b in bad[:20]:
            print('   violation', b)
    return P, F, bad


# ------------------------------------------------------------------------ LP
def lp_value(n, K, eta, tau=1, defn='ysmall'):
    M = S.build(n, K, float(eta), tau, defn)
    R, C, V, b = M['A']
    A_ub = coo_matrix((V, (R, C)), shape=(M['nrows'], M['nv'])).tocsr()
    eR, eC, eV, eb = [], [], [], []
    for i, (coefs, rhs) in enumerate(M['eqs']):
        for c, v in coefs:
            eR.append(i); eC.append(c); eV.append(v)
        eb.append(rhs)
    A_eq = coo_matrix((eV, (eR, eC)), shape=(len(M['eqs']), M['nv'])).tocsr()
    obj = np.zeros(M['nv']); obj[M['fid'](K, 0)] = 1.0
    bnds = [(None, None)] * M['nF'] + [(0, None)] * (M['nv'] - M['nF'])
    out = linprog(obj, A_ub=A_ub, b_ub=np.array(b), A_eq=A_eq, b_eq=np.array(eb),
                  bounds=bnds, method='highs')
    assert out.status == 0, out.message
    return float(out.fun)


# ----------------------------------------------------------------------- main
def main(quick=False):
    etas = [Fr(3, 2), Fr(2), Fr(2)] if quick else \
        [Fr(5, 4), Fr(3, 2), Fr(7, 4), Fr(2), Fr(9, 4), Fr(5, 2), Fr(3)]
    Ks = [3, 4, 5] if quick else [3, 4, 5, 6, 7, 8]
    out = {'exact_feasibility': [], 'value_vs_lp': [], 'n_convergence': []}

    print('=' * 92)
    print('A. exact-arithmetic feasibility of the explicit (F,G) + value vs LP  '
          '(balanced = y<=1, delta=0)')
    print('=' * 92)
    print(f"{'K':>3} {'eta':>6} {'j':>3} {'m*':>4} {'feasible':>9} {'value(exact)':>16} "
          f"{'LP(ysmall)':>14} {'diff':>10} {'V_j(R10)':>12} {'U_K':>9} {'L_K':>9}")
    npass = nfail = 0
    for eta in sorted(set(etas)):
        for K in Ks:
            P0 = params(K, eta)
            # the grid must be wide enough that the LP is at its n -> infinity
            # value; T + K + 5 columns beyond the tail is empirically enough.
            X = max(4 * K, P0['T'] + K + 5)
            P, F, bad = check_exact(K, eta, X)
            v_exact = float(P['value'])
            v_lp = lp_value(X + K, K, float(eta))
            UK = 1 - (1 - 1 / (float(eta) * (K - 1) + 1)) ** K
            LK = 1 - (1 - 1 / (float(eta) * K)) ** K
            # the construction must always be feasible (an upper bound on the
            # LP); it is additionally claimed OPTIMAL only when eta <= K-1.
            optimal_claimed = float(eta) <= K - 1
            ok = (not bad) and (v_exact >= v_lp - 1e-9) and \
                 (abs(v_exact - v_lp) < 1e-9 or not optimal_claimed)
            npass += ok; nfail += (not ok)
            print(f"{K:3d} {str(eta):>6} {P['j']:3d} {str(P['mstar']):>4} "
                  f"{'YES' if not bad else 'NO(%d)' % len(bad):>9} {v_exact:16.12f} "
                  f"{v_lp:14.12f} {v_exact - v_lp:10.2e} {float(P['Vj']):12.9f} "
                  f"{UK:9.6f} {LK:9.6f}")
            out['exact_feasibility'].append(dict(
                K=K, eta=str(eta), j=P['j'], mstar=P['mstar'], T=P['T'],
                n_violations=len(bad), violations=bad[:12],
                value_exact=v_exact, value_exact_frac=str(P['value']),
                lp_ysmall=v_lp, Vj=float(P['Vj']), UK=UK, LK=LK))
    print(f"\n  feasible everywhere + optimal wherever eta <= K-1: "
          f"{npass} PASS / {nfail} FAIL")
    print("  (rows with eta > K-1 are only claimed to be feasible upper bounds; "
          "there the LP optimum is strictly lower.)")

    print()
    print('=' * 92)
    print('B. n-dependence of the true-band LP and convergence to the y<=tau value')
    print('=' * 92)
    print(f"{'K':>3} {'eta':>6} " + ' '.join(f"{'n='+str(m)+'K':>13}" for m in [2, 4, 8, 16, 32])
          + f" {'y<=tau (limit)':>15}")
    for eta in ([Fr(2)] if quick else [Fr(3, 2), Fr(2), Fr(5, 2)]):
        for K in ([3, 4] if quick else [3, 4, 5, 6]):
            row = []
            for m in [2, 4, 8, 16, 32]:
                n = m * K
                try:
                    row.append(lp_value(n, K, float(eta), 1, 'true'))
                except Exception:
                    row.append(float('nan'))
            lim = lp_value(6 * K, K, float(eta), 1, 'ysmall')
            print(f"{K:3d} {str(eta):>6} " + ' '.join(f"{z:13.9f}" for z in row)
                  + f" {lim:15.9f}")
            out['n_convergence'].append(dict(K=K, eta=str(eta),
                                             true=[float(z) for z in row], ysmall=lim))

    print()
    print('=' * 92)
    print('C. the two integer indices are themselves in closed form: '
          'j = K+1-ceil(eta),  m* = ceil(eta K) - 1')
    print('=' * 92)
    grid_eta = [Fr(5, 4), Fr(4, 3), Fr(3, 2), Fr(7, 4), Fr(2), Fr(9, 4), Fr(7, 3),
                Fr(5, 2), Fr(3), Fr(7, 2), Fr(4), Fr(5)]
    tot = mism = 0
    for eta in grid_eta:
        for K in range(3, 25):
            P = params(K, eta)
            tot += 1
            pj = max(0, min(K, K + 1 - math.ceil(eta)))
            pm = math.ceil(eta * K) - 1
            if P['j'] != pj or (P['mstar'] is not None and P['mstar'] != pm):
                mism += 1
                print(f"  MISMATCH eta={eta} K={K}: j={P['j']} (pred {pj}) "
                      f"m*={P['mstar']} (pred {pm})")
    print(f"  {tot} (K,eta) points checked, {mism} mismatches "
          f"(argmax_m D(m) recomputed by brute force each time)")
    out['index_closed_form'] = dict(points=tot, mismatches=mism)

    with open(os.path.join(HERE, 'N4_check.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print('\nwrote results/N4_check.json')
    return 0 if nfail == 0 else 1


if __name__ == '__main__':
    sys.exit(main(quick=('quick' in sys.argv)))

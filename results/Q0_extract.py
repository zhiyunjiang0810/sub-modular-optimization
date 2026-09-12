"""Q0 (TASKS10): extract the relaxed-F hardness LP vertices on the grid
K in {3,4,5}, n in {2K,4K,8K,16K}, tau = 1, balanced = 'ysmall', split (eta_u, eta_o) = (eta, 1).

Reuses the frozen LP builder results/N4_relaxF_solve.py (imported, not modified).
The local solve_full() is a copy of its solve() extended with
  - a `split` argument (the builder already supports it; its solve() hard-codes 'sqrt'),
  - a per-tag dual census that also records WHERE the tight constraints sit,
  - a float re-check of every LP constraint on the returned canonical vertex.

Outputs: results/Q0_vertex_tables.json  (all data)
Console: per-(K, eta, n) summary lines.

Usage: python3 results/Q0_extract.py [quick]
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
import N4_relaxF_solve as S  # noqa: E402  (frozen builder)

MMAX = 800


# --------------------------------------------------------------- closed forms
def Vj(K, eta, j):
    """R10 / T6 segment value V_j(eta) = 1 - q^j (1 - (K-j)/(K eta))."""
    eta = Fr(eta)
    q = (K - 1) * eta / ((K - 1) * eta + 1)
    return 1 - q ** j * (1 - Fr(K - j, 1) / (K * eta))


def rho_K(K, eta):
    """min_{0<=j<=K-1} V_j(eta) and the argmin."""
    eta = Fr(eta)
    vals = [(Vj(K, eta, j), j) for j in range(0, K)]
    v, j = min(vals)
    return v, j


def Dcands(K, eta, mmax):
    """D(m) = q^j (nu^m/K - 1) / (eta (nu^m - 1) - m), m = 1..mmax, exact."""
    eta = Fr(eta)
    k1 = eta * (K - 1) + 1
    q = 1 - 1 / k1
    nu = eta / (eta - 1)
    j = max(0, min(K, K + 1 - math.ceil(eta)))
    qj = q ** j
    out = {}
    nup = Fr(1)
    for m in range(1, mmax + 1):
        nup *= nu
        den = eta * (nup - 1) - m
        if den <= 0:
            continue
        out[m] = qj * (nup / K - 1) / den
    return dict(eta=eta, k1=k1, q=q, nu=nu, j=j, qj=qj, cand=out)


def closed_form_value(K, eta, X, mmax=MMAX):
    """Conjectured LP value on a grid of width X = n - K (exact Fraction).

    D^(X) = max( q^j/(K eta), max_{1 <= m <= X-j} D(m) ),  value = 1 - q^j + (K-j) D^(X).
    X = infinity recovers the N4 closed form (m* = ceil(eta K) - 1).
    """
    P = Dcands(K, eta, mmax)
    j, qj, eta = P['j'], P['qj'], P['eta']
    Dbase = qj / (K * eta)
    mmaxeff = mmax if X is None else X - j
    best, marg = Dbase, None
    for m, v in P['cand'].items():
        if m <= mmaxeff and v > best:
            best, marg = v, m
    return dict(D=best, mstar=marg, j=j, q=P['q'], qj=qj,
                value=1 - qj + (K - j) * best,
                Vj=1 - qj + (K - j) * Dbase,
                T=(j + marg) if marg is not None else None)


def P0j(K, eta):
    return max(0, min(K, K + 1 - math.ceil(Fr(eta))))


# ------------------------------------------------------------------- LP solve
def solve_full(n, K, eta, tau=1, defn='ysmall', split='eta1'):
    """Canonical lexicographic vertex of the relaxed-F LP + dual census."""
    M = S.build(n, K, float(eta), tau, defn, split=split)
    R, C, V, b = M['A']
    A_ub = coo_matrix((V, (R, C)), shape=(M['nrows'], M['nv'])).tocsr()
    b = np.array(b)
    eR, eC, eV, eb = [], [], [], []
    for i, (coefs, rhs) in enumerate(M['eqs']):
        for c, v in coefs:
            eR.append(i); eC.append(c); eV.append(v)
        eb.append(rhs)
    A_eq = coo_matrix((eV, (eR, eC)), shape=(len(M['eqs']), M['nv'])).tocsr()
    obj = np.zeros(M['nv']); obj[M['fid'](K, 0)] = 1.0
    # Ghat_s for s not realised by any balanced point sits in no constraint
    # (with defn='ysmall' only s <= X+tau occur); pin those to 0 so that the
    # pass-2 mass objective stays bounded.
    balg = S.balanced_grid(n, K, tau, defn)
    used_s = {xx + yy for xx in range(M['X'] + 1) for yy in range(M['Y'] + 1)
              if balg[xx, yy]}
    bounds = [(None, None)] * M['nv']
    for s in range(n + 1):
        if s not in used_s:
            bounds[M['gh0'] + s] = (0.0, 0.0)
    out = linprog(obj, A_ub=A_ub, b_ub=b, A_eq=A_eq, b_eq=np.array(eb),
                  bounds=bounds, method='highs')
    assert out.status == 0, out.message
    v_star = float(out.fun)

    marg = out.ineqlin.marginals
    tight_tags, tight_list = {}, []
    for i, m in enumerate(marg):
        if abs(m) > 1e-9:
            tag, pos, dirn = M['meta'][i]
            tight_tags[f'{tag}:{dirn}'] = tight_tags.get(f'{tag}:{dirn}', 0) + 1
            tight_list.append(dict(tag=tag, pos=list(pos), dirn=dirn, mult=float(m)))

    # canonical extreme point: min total mass at fixed optimum
    A_ub2 = coo_matrix((V + [1.0], (R + [M['nrows']], C + [M['fid'](K, 0)])),
                       shape=(M['nrows'] + 1, M['nv'])).tocsr()
    # slack on the fixed objective: a 1e-9 slack leaks into the vertex with an
    # amplification of ~1e2 near the saturation corner, so use 0 and only fall
    # back if HiGHS refuses.
    out2 = None
    for slack in (0.0, 1e-12, 1e-9):
        b2 = np.append(b, v_star + slack)
        cand = linprog(np.ones(M['nv']), A_ub=A_ub2, b_ub=b2, A_eq=A_eq,
                       b_eq=np.array(eb), bounds=bounds, method='highs')
        if cand.status == 0:
            out2 = cand
            break
    assert out2 is not None, 'canonical pass failed'
    x = out2.x
    X, Y = M['X'], M['Y']
    F = x[:M['nF']].reshape(X + 1, Y + 1)
    Ghat = x[M['gh0']:M['gh0'] + n + 1]
    G = np.full((X + 1, Y + 1), np.nan)
    bal = S.balanced_grid(n, K, tau, defn)
    for xx in range(X + 1):
        for yy in range(Y + 1):
            G[xx, yy] = Ghat[xx + yy] if bal[xx, yy] else x[M['gvid'][(xx, yy)]]
    return dict(ratio=v_star, F=F, Ghat=Ghat, G=G, bal=bal, X=X, Y=Y,
                tight_tags=tight_tags, tight_list=tight_list)


# ---------------------------------------------------------------- validity
def recheck(F, G, Ghat, bal, K, eta, split='eta1', tol=1e-7):
    """Float re-check of the LP constraints on a returned vertex."""
    eta_u, eta_o = (eta, 1.0) if split != 'sqrt' else (eta ** 0.5,) * 2
    X = F.shape[0] - 1
    viol = {}

    def bad(tag, amt):
        if amt > tol:
            viol[tag] = max(viol.get(tag, 0.0), amt)

    for x in range(X + 1):
        for y in range(K + 1):
            for dx, dy in ((1, 0), (0, 1)):
                if x + dx > X or y + dy > K:
                    continue
                dF = F[x + dx, y + dy] - F[x, y]
                dG = G[x + dx, y + dy] - G[x, y]
                bad('mono', -dF)
                bad('band_up', dG - eta_o * dF)
                bad('band_lo', dF / eta_u - dG)
                for sx, sy in ((1, 0), (0, 1)):
                    if x + dx + sx > X or y + dy + sy > K:
                        continue
                    lhs = F[x + dx + sx, y + dy + sy] - F[x + sx, y + sy]
                    bad(f'submod_{dx}{dy}_{sx}{sy}', lhs - dF)
    for x in range(X + 1):
        for y in range(K + 1):
            if 0 < x + y <= K and not (x == 0 and y == K):
                bad('opt_norm', F[x, y] - 1.0)
            if bal[x, y]:
                bad('O_indep', abs(G[x, y] - Ghat[x + y]))
    bad('eq_F00', abs(F[0, 0]))
    bad('eq_F0K', abs(F[0, K] - 1.0))
    bad('eq_Ghat0', abs(Ghat[0]))
    return viol


# ---------------------------------------------------------------------- main
def main(quick=False):
    ETAS = {
        3: ['3/2', '5/2', '19/10', '29/10'] if quick else
           ['3/2', '5/2', '7/2', '19/10', '29/10'],
        4: ['3/2', '5/2', '7/2', '9/2', '19/10'],
        5: ['5/2', '7/2', '19/10'],
    }
    Ks = [3, 4] if quick else [3, 4, 5]
    NS = [2, 4, 8] if quick else [2, 4, 8, 16]
    rows, store = [], {}
    for K in Ks:
        for es in ETAS[K]:
            eta = Fr(es)
            rk, jmin = rho_K(K, eta)
            jseg = P0j(K, eta)
            for mult in NS:
                n = mult * K
                key = f'K{K}_eta{es.replace("/", "o")}_n{n}'
                r = solve_full(n, K, float(eta))
                X = r['X']
                cf = closed_form_value(K, eta, X)
                cflim = closed_form_value(K, eta, None)
                viol = recheck(r['F'], r['G'], r['Ghat'], r['bal'], K, float(eta))
                dxF0 = np.diff(r['F'][:, 0]).tolist()
                dxF1 = np.diff(r['F'][:, 1]).tolist()
                dyF0 = r['F'][0, :].tolist()
                ghat_inc = np.diff(r['Ghat']).tolist()
                row = dict(K=K, eta=es, eta_f=float(eta), n=n, X=X,
                           ratio=r['ratio'],
                           Vj_seg=float(Vj(K, eta, jseg)), j_seg=jseg,
                           rho_K=float(rk), j_min=jmin,
                           cf_finite=float(cf['value']), cf_m=cf['mstar'],
                           cf_limit=float(cflim['value']), cf_mstar=cflim['mstar'],
                           T=cflim['T'],
                           err_cf_finite=r['ratio'] - float(cf['value']),
                           err_cf_limit=r['ratio'] - float(cflim['value']),
                           err_Vj=r['ratio'] - float(Vj(K, eta, jseg)),
                           viol=viol,
                           tight=r['tight_tags'])
                rows.append(row)
                store[key] = dict(
                    config=dict(n=n, K=K, eta=es, tau=1, defn='ysmall',
                                split=['eta', 1]),
                    summary=row,
                    F=r['F'].tolist(), Ghat=r['Ghat'].tolist(), G=r['G'].tolist(),
                    balanced=r['bal'].astype(int).tolist(),
                    dxF_y0=dxF0, dxF_y1=dxF1, F_x0_col=dyF0, ghat_inc=ghat_inc,
                    tight_list=r['tight_list'])
                print(f"K={K} eta={es:>5} n={n:>3} X={X:>3} ratio={r['ratio']:.9f} "
                      f"| V_j={float(Vj(K, eta, jseg)):.9f} (j={jseg}) "
                      f"rho={float(rk):.9f}(j*={jmin}) "
                      f"| cf_fin={float(cf['value']):.9f} d={row['err_cf_finite']:+.2e} "
                      f"| cf_lim={float(cflim['value']):.9f} d={row['err_cf_limit']:+.2e} "
                      f"| viol={ {k: f'{v:.1e}' for k, v in viol.items()} }",
                      flush=True)
    # ---- extra sweep: is the LP value at n = 2K exactly rho_K = min_j V_j? ----
    print('\n--- n = 2K sweep: LP value vs rho_K = min_j V_j ---')
    sweep = []
    for K in ([3, 4] if quick else [3, 4, 5, 6, 7]):
        for es in ['5/4', '3/2', '19/10', '2', '5/2', '29/10', '3', '7/2', '4']:
            eta = Fr(es)
            r = solve_full(2 * K, K, float(eta))
            rk, jmin = rho_K(K, eta)
            cf = closed_form_value(K, eta, K)
            sweep.append(dict(K=K, eta=es, n=2 * K, ratio=r['ratio'],
                              rho_K=float(rk), j_min=jmin,
                              err=r['ratio'] - float(rk),
                              cf_finite=float(cf['value'])))
            print(f"  K={K} eta={es:>5} ratio={r['ratio']:.12f} rho_K={float(rk):.12f} "
                  f"diff={r['ratio'] - float(rk):+.2e}", flush=True)

    # ---- pure-arithmetic conjecture check: max_{m<=K-j} D(m) <= q^j/(K eta) ----
    print('\n--- conjecture: on the n = 2K grid the closing tail never pays ---')
    viol2 = []
    for K in range(2, 25):
        for num in range(5, 4 * K + 1):
            eta = Fr(num, 4)
            if eta <= 1:
                continue
            j = P0j(K, eta)
            cf = closed_form_value(K, eta, K)
            if cf['mstar'] is not None:
                viol2.append((K, str(eta), j, cf['mstar']))
    print(f'  violations (a closing tail fits in X = K): {len(viol2)}'
          + (f'  first: {viol2[:5]}' if viol2 else ''))

    with open(os.path.join(HERE, 'Q0_vertex_tables.json'), 'w') as fh:
        json.dump(dict(rows=rows, data=store, sweep_2K=sweep,
                       tailfits_at_2K=viol2), fh)
    print('wrote results/Q0_vertex_tables.json')


if __name__ == '__main__':
    main(quick=(len(sys.argv) > 1 and sys.argv[1] == 'quick'))

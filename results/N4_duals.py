"""N4 step 4: tight-constraint census (nonzero dual multipliers) of the
relaxed-F hardness LP, for the true balanced band (K in {4,6,8}, n = 8K, the
configuration of results/N4_solutions.json) and for the n -> infinity limit LP
(balanced = y <= tau).

Each row is  (constraint type, base point (x,y), direction, multiplier).
Directions: 'x'/'y' for mono and the two band constraints; 'xx','xy','yx','yy'
for submodularity (first letter = the edge, second = the shift).

The classifier below assigns every tight constraint to one of the structural
families predicted by the closed form of results/N4_check.py
(j, T = j + m* from N4_check.params):

  A  band_lo (x,0) dir y      x = 1..T      Ghat_{x+1}-Ghat_x = g_x / eta_u
  B  band_up (x,1) dir x      x = 0..T-2    coherence (R3(ii)) tight
  C  submod  (x,i) dir yy     x <= j        F linear in y  (coverage tight)
  D  submod  (x,0) dir xx     j <= x <= T-2 d_x constant on the tail
  E  mono    (x,K) dir x      F(.,K) flat at 1
  F  submod  (x,K) dir xx     top row of F flat
  G  mono    (T,y) dir y      F(T,.) flat above the tail
  L  the long-range y=2 chain: band_up (j,1) y, band_up (x,2) x, band_lo (T,1) y
     -- this family has no counterpart in the reduced LP of R6/R10 and is what
     lifts the value from V_j to the closed form.
  ?  unclassified

Run: python3 results/N4_duals.py     (writes results/N4_tight.json)
"""
import json
import os
import sys

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import N4_relaxF_solve as S     # noqa: E402
import N4_check as C            # noqa: E402


def duals(n, K, eta, tau=1, defn='true'):
    M = S.build(n, K, eta, tau, defn)
    R, Co, V, b = M['A']
    A_ub = coo_matrix((V, (R, Co)), shape=(M['nrows'], M['nv'])).tocsr()
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
    rows = []
    for i, m in enumerate(out.ineqlin.marginals):
        if abs(m) > 1e-9:
            tag = M['meta'][i]
            rows.append(dict(type=tag[0], x=int(tag[1][0]), y=int(tag[1][1]),
                             dir=tag[2], mult=float(-m)))
    return float(out.fun), rows


def classify(rows, K, j, T):
    for r in rows:
        t, x, y, d = r['type'], r['x'], r['y'], r['dir']
        fam = '?'
        if t == 'band_lo' and y == 0 and d == 'y' and 1 <= x <= T:
            fam = 'A'
        elif t == 'band_up' and y == 1 and d == 'x' and 0 <= x <= T:
            fam = 'B'
        elif t == 'submod' and d == 'yy' and x <= j:
            fam = 'C'
        elif t == 'submod' and y == 0 and d == 'xx' and j <= x <= T:
            fam = 'D'
        elif t == 'mono' and y == K and d == 'x':
            fam = 'E'
        elif t == 'submod' and y == K and d == 'xx':
            fam = 'F'
        elif t == 'mono' and d == 'y' and x >= T:
            fam = 'G'
        elif (t == 'band_up' and y >= 2 and d == 'x') or \
             (t == 'band_up' and y == 1 and d == 'y') or \
             (t == 'band_lo' and y == 1 and d == 'y'):
            fam = 'L'
        r['family'] = fam
    return rows


def report(label, val, rows, K, j, T, show=True):
    fams = {}
    for r in rows:
        fams[r['family']] = fams.get(r['family'], 0) + 1
    print(f"\n--- {label}:  value={val:.9f}   j={j}  T={T}   "
          f"{len(rows)} tight constraints")
    print("    family counts:", dict(sorted(fams.items())))
    if show:
        order = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6,
                 'L': 7, '?': 8}
        for r in sorted(rows, key=lambda z: (order[z['family']], z['type'],
                                             z['y'], z['x'], z['dir'])):
            print(f"      [{r['family']}] {r['type']:>8s} (x={r['x']:2d},y={r['y']:d}) "
                  f"{r['dir']:<2s}  mult={r['mult']:+.6f}")


def main():
    out = {}
    print('=' * 84)
    print('1) true balanced band, n = 8K, eta = 2, tau = 1 '
          '(same configs as N4_solutions.json)')
    print('=' * 84)
    for K, n in [(4, 32), (6, 48), (8, 64)]:
        P = C.params(K, 2)
        val, rows = duals(n, K, 2.0, 1, 'true')
        rows = classify(rows, K, P['j'], P['T'])
        report(f'K={K} n={n} true', val, rows, K, P['j'], P['T'], show=(K == 4))
        out[f'true_K{K}_n{n}'] = dict(value=val, j=P['j'], T=P['T'], rows=rows)

    print()
    print('=' * 84)
    print('2) n -> infinity limit LP (balanced = y <= tau), eta = 2, tau = 1')
    print('=' * 84)
    for K in [3, 4, 5, 6]:
        P = C.params(K, 2)
        X = max(4 * K, P['T'] + K + 5)
        val, rows = duals(X + K, K, 2.0, 1, 'ysmall')
        rows = classify(rows, K, P['j'], P['T'])
        report(f'K={K} ysmall', val, rows, K, P['j'], P['T'], show=(K in (3, 4)))
        out[f'ysmall_K{K}'] = dict(value=val, j=P['j'], T=P['T'], rows=rows)

    with open(os.path.join(HERE, 'N4_tight.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print('\nwrote results/N4_tight.json')


if __name__ == '__main__':
    main()

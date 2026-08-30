"""N4 step 1: solve the relaxed-F hardness LP and dump the FULL optimal solution
(F grid, Ghat, unbalanced G) for analysis.  Standalone copy of the LP builder of
results/T2_hardness_grid.py relaxF_min_ratio (that night-1 deliverable stays
frozen), extended with:
  - full solution return (F, Ghat, G-unbalanced);
  - a second lexicographic pass: fix the objective at its optimum and minimize
    sum(F) + sum(Ghat) + sum(G) to select a canonical extreme point (the LP
    optimum is degenerate; the canonical point exposes structure);
  - dual multipliers of the first pass (tight-constraint census for step 4).
Usage: python3 results/N4_relaxF_solve.py   (writes results/N4_solutions.json)
"""
import json, os, sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))


def balanced_grid(n, K, tau, defn):
    xs = np.arange(n - K + 1)[:, None]
    ys = np.arange(K + 1)[None, :]
    sz = xs + ys
    if defn == 'ysmall':
        return np.broadcast_to(ys <= tau, (n - K + 1, K + 1)).copy()
    if defn == 'true':
        return np.abs(ys - K * sz / n) <= tau + 1e-12
    raise ValueError(defn)


def build(n, K, eta, tau, defn, split='sqrt'):
    eta_u, eta_o = ((eta ** 0.5,) * 2) if split == 'sqrt' else (eta, 1.0)
    X, Y = n - K, K
    bal = balanced_grid(n, K, tau, defn)
    nF = (X + 1) * (Y + 1)
    fid = lambda x, y: x * (Y + 1) + y
    gh0 = nF
    unbal = [(x, y) for x in range(X + 1) for y in range(Y + 1) if not bal[x, y]]
    gv0 = nF + n + 1
    gvid = {p: gv0 + i for i, p in enumerate(unbal)}
    nv = gv0 + len(unbal)
    gref = lambda p: (gh0 + p[0] + p[1]) if bal[p] else gvid[p]

    R, C, V, b, meta = [], [], [], [], []
    r = 0
    def ub(coefs, rhs, tag):
        nonlocal r
        for c, v in coefs:
            R.append(r); C.append(c); V.append(v)
        b.append(rhs); meta.append(tag); r += 1

    edges = []
    for x in range(X + 1):
        for y in range(Y + 1):
            if x < X: edges.append(((x, y), (x + 1, y), 'x'))
            if y < Y: edges.append(((x, y), (x, y + 1), 'y'))
    for p, q, d in edges:
        ub([(fid(*p), 1.0), (fid(*q), -1.0)], 0.0, ('mono', p, d))
        gq, gp = gref(q), gref(p)
        ub([(gq, 1.0), (gp, -1.0), (fid(*q), -eta_o), (fid(*p), eta_o)], 0.0, ('band_up', p, d))
        ub([(fid(*q), 1 / eta_u), (fid(*p), -1 / eta_u), (gq, -1.0), (gp, 1.0)], 0.0, ('band_lo', p, d))
    for p, q, d in edges:
        for sh in ('x', 'y'):
            px = (p[0] + (sh == 'x'), p[1] + (sh == 'y'))
            qx = (q[0] + (sh == 'x'), q[1] + (sh == 'y'))
            if px[0] > X or px[1] > Y or qx[0] > X or qx[1] > Y:
                continue
            ub([(fid(*qx), 1.0), (fid(*px), -1.0), (fid(*q), -1.0), (fid(*p), 1.0)],
               0.0, ('submod', p, d + sh))
    for x in range(X + 1):
        for y in range(Y + 1):
            if 0 < x + y <= K and not (x == 0 and y == K):
                ub([(fid(x, y), 1.0)], 1.0, ('opt_norm', (x, y), ''))
    eqs = [([(fid(0, 0), 1.0)], 0.0), ([(fid(0, K), 1.0)], 1.0), ([(gh0, 1.0)], 0.0)]
    return dict(nv=nv, nF=nF, gh0=gh0, gvid=gvid, unbal=unbal, X=X, Y=Y,
                fid=fid, A=(R, C, V, b), meta=meta, eqs=eqs, nrows=r)


def solve(n, K, eta, tau, defn):
    M = build(n, K, eta, tau, defn)
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
    out = linprog(obj, A_ub=A_ub, b_ub=b, A_eq=A_eq, b_eq=np.array(eb),
                  bounds=[(None, None)] * M['nv'], method='highs')
    assert out.status == 0, out.message
    v_star = out.fun
    # tight-constraint census from duals of pass 1
    marg = out.ineqlin.marginals
    tight = {}
    for i, m in enumerate(marg):
        if abs(m) > 1e-9:
            tag = M['meta'][i][0]
            tight[tag] = tight.get(tag, 0) + 1
    # pass 2: canonical extreme point (minimize total mass at fixed optimum)
    A_ub2 = coo_matrix((V + [1.0], (R + [M['nrows']], C + [M['fid'](K, 0)])),
                       shape=(M['nrows'] + 1, M['nv'])).tocsr()
    b2 = np.append(b, v_star + 1e-9)
    obj2 = np.ones(M['nv'])
    out2 = linprog(obj2, A_ub=A_ub2, b_ub=b2, A_eq=A_eq, b_eq=np.array(eb),
                   bounds=[(None, None)] * M['nv'], method='highs')
    assert out2.status == 0, out2.message
    x = out2.x
    X, Y = M['X'], M['Y']
    F = x[:M['nF']].reshape(X + 1, Y + 1)
    Ghat = x[M['gh0']:M['gh0'] + n + 1]
    G = np.full((X + 1, Y + 1), np.nan)
    bal = balanced_grid(n, K, tau, defn)
    for xx in range(X + 1):
        for yy in range(Y + 1):
            G[xx, yy] = Ghat[xx + yy] if bal[xx, yy] else x[M['gvid'][(xx, yy)]]
    return dict(ratio=float(v_star), F=F, Ghat=Ghat, G=G, bal=bal,
                tight_counts=tight)


if __name__ == '__main__':
    outp = {}
    for K, n in [(4, 32), (6, 48), (8, 64)]:
        r = solve(n, K, 2.0, 1, 'true')
        outp[f'K{K}_n{n}'] = dict(
            config=dict(n=n, K=K, eta=2.0, tau=1, defn='true'),
            ratio=r['ratio'], F=r['F'].tolist(), Ghat=r['Ghat'].tolist(),
            G=r['G'].tolist(), balanced=r['bal'].astype(int).tolist(),
            tight_counts=r['tight_counts'])
        print(f"K={K} n={n}: ratio={r['ratio']:.6f}  tight={r['tight_counts']}",
              flush=True)
    with open(os.path.join(HERE, 'N4_solutions.json'), 'w') as fh:
        json.dump(outp, fh)
    print('wrote N4_solutions.json')

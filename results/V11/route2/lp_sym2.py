"""Two-type reduced LP: f depends only on (a,w) = (|S cap O|, |S \ O|).
This tests whether the hard instance can be made INDEPENDENT of the algorithm's
output T (full symmetry outside O).  Objective: min f(0,K) = value of EVERY
K-set disjoint from O.
"""
import sys
import numpy as np
from scipy.optimize import linprog
from lp_sym import rho


def solve(K, eta, W, m, eta_u=1.0, dev_min=2):
    eo = eta / eta_u; eu = eta_u
    Z = [(a, w) for a in range(K + 1) for w in range(W + 1)]
    zi = {z: i for i, z in enumerate(Z)}
    nz = len(Z)
    gi = {}
    def gkey(z):
        s = z[0] + z[1]
        return ("D", s, z[0]) if (z[0] >= dev_min and s <= m) else ("F", s)
    for z in Z:
        k = gkey(z)
        if k not in gi: gi[k] = nz + len(gi)
    nv = nz + len(gi)
    def GV(z): return gi[gkey(z)]
    cap = (K, W); E = [(1, 0), (0, 1)]
    def add(z, e):
        w = (z[0] + e[0], z[1] + e[1])
        return w if all(0 <= w[i] <= cap[i] for i in range(2)) else None
    A_ub, b_ub, A_eq, b_eq = [], [], [], []
    def ub(coefs, r_):
        row = np.zeros(nv)
        for i, cf in coefs: row[i] += cf
        A_ub.append(row); b_ub.append(r_)
    def eq(coefs, r_):
        row = np.zeros(nv)
        for i, cf in coefs: row[i] += cf
        A_eq.append(row); b_eq.append(r_)
    eq([(zi[(0, 0)], 1.0)], 0.0); eq([(GV((0, 0)), 1.0)], 0.0)
    for z in Z:
        for e in E:
            w = add(z, e)
            if w is None: continue
            ub([(zi[z], 1.0), (zi[w], -1.0)], 0.0)
            ub([(zi[w], 1.0 / eu), (zi[z], -1.0 / eu), (GV(w), -1.0), (GV(z), 1.0)], 0.0)
            ub([(GV(w), 1.0), (GV(z), -1.0), (zi[w], -eo), (zi[z], eo)], 0.0)
        for ei, e in enumerate(E):
            for ej in range(ei, 2):
                e2 = E[ej]
                w1 = add(z, e); w2 = add(z, e2)
                w12 = add(w1, e2) if w1 else None
                if w1 is None or w2 is None or w12 is None: continue
                if ei == ej and z[ei] + 2 > cap[ei]: continue
                ub([(zi[w12], 1.0), (zi[z], 1.0), (zi[w1], -1.0), (zi[w2], -1.0)], 0.0)
    eq([(zi[(K, 0)], 1.0)], 1.0)
    for a in range(K + 1):
        if K - a <= W: ub([(zi[(a, K - a)], 1.0)], 1.0)
    c = np.zeros(nv); c[zi[(0, K)]] = 1.0
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq),
                  b_eq=np.array(b_eq), bounds=[(0, None)] * nv, method="highs")
    return res, Z, zi, gi, nz


if __name__ == "__main__":
    K = int(sys.argv[1]); eta = float(eval(sys.argv[2]))
    W = int(sys.argv[3]); m = int(sys.argv[4])
    eu = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    res, Z, zi, gi, nz = solve(K, eta, W, m, eta_u=eu)
    rr, j = rho(K, eta)
    print(f"K={K} eta={eta} W={W} m={m} eta_u={eu}: min f(0,K) = "
          f"{res.fun if res.success else 'INFEAS'}  rho={rr:.8f} (j*={j})  "
          f"diff={res.fun-rr if res.success else float('nan'):+.3e}")

"""Symmetry-reduced LP for the hideable family.

The feasible set is invariant under Sym(O) x Sym(T) x Sym(X), so an optimal
solution may be taken symmetric and f becomes a function of the count vector
z = (a,b,c) = (|S cap O|, |S cap T|, |S cap X|),  a,b <= K,  c <= r = n-2K.

ftilde(z) = Gamma(|z|, a) if a >= 2 and |z| <= m, else gamma(|z|).

min f(0,K,0)  s.t.  f monotone submodular, f(K,0,0)=1, f(z)<=1 for |z|=K, band.
"""
import sys, itertools
import numpy as np
from scipy.optimize import linprog


def solve(K, eta, r, m, eta_u=1.0, verbose=False, dev_min=2, cap_opt=True):
    eo = eta / eta_u
    eu = eta_u
    n = 2 * K + r
    Z = [(a, b, c) for a in range(K + 1) for b in range(K + 1) for c in range(r + 1)]
    zi = {z: i for i, z in enumerate(Z)}
    nz = len(Z)
    gi = {}
    def gkey(z):
        s = sum(z); a = z[0]
        if a >= dev_min and s <= m:
            return ("D", s, a)
        return ("F", s)
    for z in Z:
        k = gkey(z)
        if k not in gi:
            gi[k] = nz + len(gi)
    nv = nz + len(gi)
    def GV(z): return gi[gkey(z)]

    A_ub, b_ub, A_eq, b_eq = [], [], [], []
    def ub(coefs, r_):
        row = np.zeros(nv)
        for i, cf in coefs: row[i] += cf
        A_ub.append(row); b_ub.append(r_)
    def eq(coefs, r_):
        row = np.zeros(nv)
        for i, cf in coefs: row[i] += cf
        A_eq.append(row); b_eq.append(r_)

    cap = (K, K, r)
    E = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    def add(z, e, k=1):
        w = tuple(z[i] + k * e[i] for i in range(3))
        return w if all(0 <= w[i] <= cap[i] for i in range(3)) else None

    eq([(zi[(0, 0, 0)], 1.0)], 0.0)
    eq([(GV((0, 0, 0)), 1.0)], 0.0)

    for z in Z:
        for e in E:
            w = add(z, e)
            if w is None: continue
            ub([(zi[z], 1.0), (zi[w], -1.0)], 0.0)                      # monotone
            ub([(zi[w], 1.0 / eu), (zi[z], -1.0 / eu),
                (GV(w), -1.0), (GV(z), 1.0)], 0.0)                      # band lower
            ub([(GV(w), 1.0), (GV(z), -1.0),
                (zi[w], -eo), (zi[z], eo)], 0.0)                        # band upper
        # submodularity: need two distinct elements, so for e==e' need room 2
        for ei, e in enumerate(E):
            for ej in range(ei, 3):
                e2 = E[ej]
                w1 = add(z, e); w2 = add(z, e2)
                w12 = add(w1, e2) if w1 else None
                if w1 is None or w2 is None or w12 is None: continue
                if ei == ej and z[ei] + 2 > cap[ei]: continue
                ub([(zi[w12], 1.0), (zi[z], 1.0), (zi[w1], -1.0), (zi[w2], -1.0)], 0.0)

    eq([(zi[(K, 0, 0)], 1.0)], 1.0)
    if cap_opt:
        for z in Z:
            if sum(z) == K:
                ub([(zi[z], 1.0)], 1.0)

    c = np.zeros(nv); c[zi[(0, K, 0)]] = 1.0
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)] * nv, method="highs")
    return res, Z, zi, gi, nz, n


def rho(K, eta):
    k1 = (K - 1) * eta + 1.0; q = (K - 1) * eta / k1
    v = [1 - q ** j * (1 - (K - j) / (K * eta)) for j in range(K)]
    return min(v), int(np.argmin(v))


if __name__ == "__main__":
    K = int(sys.argv[1]); eta = float(eval(sys.argv[2]))
    r = int(sys.argv[3]); m = int(sys.argv[4])
    eu = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    res, Z, zi, gi, nz, n = solve(K, eta, r, m, eta_u=eu)
    rr, j = rho(K, eta)
    print(f"K={K} eta={eta} n={n} (r={r}) m={m} eta_u={eu}: min f(T) = "
          f"{res.fun if res.success else 'INFEASIBLE'}  rho_K={rr:.8f} (j*={j})  diff={res.fun-rr if res.success else 0:.2e}")

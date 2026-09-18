"""LP oracle for the HIDEABLE family.

Ground set N = O (K elts) u T (K elts) u extras.  The surrogate is forced to be
    ftilde(S) = Gamma(|S|,|S cap O|)   if |S| <= m and |S cap O| >= 2
              = gamma(|S|)             otherwise
(so a query can only reveal O if it is small AND meets O twice: that is what the
union bound of the hardness argument can afford).  f is an arbitrary monotone
submodular function with f(O)=1=OPT.  We minimise f(T).

If min f(T) > rho_K the hideable class has a forced positive excess.
"""
import sys, itertools
import numpy as np
from scipy.sparse import coo_matrix
from scipy.optimize import linprog


def build(K, n, m, eta_u, eta_o, allow_one=False, allow_big=False):
    O = list(range(K)); T = list(range(K, 2 * K))
    NS = 1 << n
    mO = (1 << K) - 1
    mT = ((1 << K) - 1) << K
    pc = np.array([bin(S).count("1") for S in range(NS)])
    io = np.array([bin(S & mO).count("1") for S in range(NS)])

    # surrogate variable index for each set
    gidx = {}
    def gid(S):
        s, i = int(pc[S]), int(io[S])
        dev = (s <= m or allow_big) and (i >= (1 if allow_one else 2))
        key = (s, i) if dev else (s, -1)
        if key not in gidx:
            gidx[key] = len(gidx)
        return key
    for S in range(NS):
        gid(S)
    ng = len(gidx)
    nv = NS + ng
    def GV(S): return NS + gidx[gid(S)]

    rows, cols, vals, rhs = [], [], [], []
    erows, ecols, evals, erhs = [], [], [], []
    def ub(coefs, r):
        k = len(rhs)
        for i, cf in coefs:
            rows.append(k); cols.append(i); vals.append(cf)
        rhs.append(r)
    def eq(coefs, r):
        k = len(erhs)
        for i, cf in coefs:
            erows.append(k); ecols.append(i); evals.append(cf)
        erhs.append(r)

    eq([(0, 1.0)], 0.0)                      # f(empty)=0
    eq([(GV(0), 1.0)], 0.0)                  # ftilde(empty)=0

    for S in range(NS):
        for e in range(n):
            if S >> e & 1:
                continue
            Se = S | (1 << e)
            ub([(S, 1.0), (Se, -1.0)], 0.0)                       # monotone
            ub([(Se, 1.0 / eta_u), (S, -1.0 / eta_u),
                (GV(Se), -1.0), (GV(S), 1.0)], 0.0)               # band lower
            ub([(GV(Se), 1.0), (GV(S), -1.0),
                (Se, -eta_o), (S, eta_o)], 0.0)                   # band upper

    for S in range(NS):
        rest = [e for e in range(n) if not (S >> e & 1)]
        for i, j in itertools.combinations(rest, 2):
            Si, Sj = S | (1 << i), S | (1 << j)
            ub([(Si | (1 << j), 1.0), (S, 1.0), (Si, -1.0), (Sj, -1.0)], 0.0)

    for X in itertools.combinations(range(n), K):
        mX = 0
        for e in X:
            mX |= 1 << e
        ub([(mX, 1.0)], 1.0)
    eq([(mO, 1.0)], 1.0)

    c = np.zeros(nv); c[mT] = 1.0
    A_ub = coo_matrix((vals, (rows, cols)), shape=(len(rhs), nv))
    A_eq = coo_matrix((evals, (erows, ecols)), shape=(len(erhs), nv))
    return c, A_ub, np.array(rhs), A_eq, np.array(erhs), nv, gidx, mT, mO


def run(K, eta, n, m, split=(1.0, None), **kw):
    eu = split[0]; eo = eta / eu
    c, A_ub, b_ub, A_eq, b_eq, nv, gidx, mT, mO = build(K, n, m, eu, eo, **kw)
    res = linprog(c, A_ub=A_ub.tocsr(), b_ub=b_ub, A_eq=A_eq.tocsr(), b_eq=b_eq,
                  bounds=[(0, None)] * nv, method="highs")
    return res, gidx, mT, mO


def rho(K, eta):
    k1 = (K - 1) * eta + 1.0; q = (K - 1) * eta / k1
    v = [1 - q ** j * (1 - (K - j) / (K * eta)) for j in range(K)]
    return min(v), int(np.argmin(v))


if __name__ == "__main__":
    K = int(sys.argv[1]); eta = float(eval(sys.argv[2]))
    n = int(sys.argv[3]); m = int(sys.argv[4])
    kw = {}
    if len(sys.argv) > 5 and sys.argv[5] == "one":
        kw["allow_one"] = True
    if len(sys.argv) > 5 and sys.argv[5] == "big":
        kw["allow_big"] = True
    res, gidx, mT, mO = run(K, eta, n, m, **kw)
    r, j = rho(K, eta)
    print(f"K={K} eta={eta} n={n} m={m} {kw}: min f(T) = "
          f"{res.fun if res.success else 'INFEASIBLE'}   rho_K={r:.6f} (j*={j})  1/eta={1/eta:.6f}")
    if res.success:
        x = res.x
        print("  gamma(s):", [f"{x[len(x) - len(gidx) + gidx[(s, -1)]]:.5f}"
                              for s in range(n + 1) if (s, -1) in gidx])
        dev = {k: x[len(x) - len(gidx) + v] for k, v in gidx.items() if k[1] >= 0}
        for k in sorted(dev):
            print(f"  Gamma{k} = {dev[k]:.5f}")

"""LP oracle for the exact worst case of predictive greedy under the GLOBAL
single-element band  d_e(S)/eta_u <= dt_e(S) <= eta_o d_e(S)  (Definition 1, convention B).

Ground set: B = {b_0..b_{K-1}} (the greedy picks), O = {o_1..o_K} (the optimum),
plus `extra` dummy elements.  For a FIXED identity of the greedy picks the whole
feasibility region is a polyhedron, so min f(B) is an LP.

Usage: python3 lp_rho.py K eta [extra]
"""
import sys, itertools
import numpy as np
from scipy.optimize import linprog


def solve(K, eta_u, eta_o, extra=0, verbose=False, force_d0=None):
    B = list(range(K))                 # b_0 .. b_{K-1}
    O = list(range(K, 2 * K))          # o_1 .. o_K
    X = list(range(2 * K, 2 * K + extra))
    n = 2 * K + extra
    NS = 1 << n
    nv = 2 * NS                        # f[S] = var S ; ft[S] = var NS+S

    def fv(S): return S
    def gv(S): return NS + S

    A_ub, b_ub, A_eq, b_eq = [], [], [], []

    def add_ub(coefs, rhs):
        row = np.zeros(nv)
        for i, c in coefs:
            row[i] += c
        A_ub.append(row); b_ub.append(rhs)

    def add_eq(coefs, rhs):
        row = np.zeros(nv)
        for i, c in coefs:
            row[i] += c
        A_eq.append(row); b_eq.append(rhs)

    add_eq([(fv(0), 1.0)], 0.0)
    add_eq([(gv(0), 1.0)], 0.0)

    for S in range(NS):
        for e in range(n):
            if S >> e & 1:
                continue
            Se = S | (1 << e)
            # monotone: f(S) - f(Se) <= 0
            add_ub([(fv(S), 1.0), (fv(Se), -1.0)], 0.0)
            # band lower: (f(Se)-f(S))/eta_u - (g(Se)-g(S)) <= 0
            add_ub([(fv(Se), 1.0 / eta_u), (fv(S), -1.0 / eta_u),
                    (gv(Se), -1.0), (gv(S), 1.0)], 0.0)
            # band upper: (g(Se)-g(S)) - eta_o (f(Se)-f(S)) <= 0
            add_ub([(gv(Se), 1.0), (gv(S), -1.0),
                    (fv(Se), -eta_o), (fv(S), eta_o)], 0.0)

    # submodularity (local exchange condition is sufficient)
    for S in range(NS):
        rest = [e for e in range(n) if not (S >> e & 1)]
        for i, j in itertools.combinations(rest, 2):
            Si, Sj = S | (1 << i), S | (1 << j)
            Sij = Si | (1 << j)
            add_ub([(fv(Sij), 1.0), (fv(S), 1.0), (fv(Si), -1.0), (fv(Sj), -1.0)], 0.0)

    # OPT normalisation: f(T) <= 1 for every K-set, and f(O) = 1
    for T in itertools.combinations(range(n), K):
        m = 0
        for e in T:
            m |= 1 << e
        add_ub([(fv(m), 1.0)], 1.0)
    mO = 0
    for e in O:
        mO |= 1 << e
    add_eq([(fv(mO), 1.0)], 1.0)

    # greedy on ft with adversarial ties: b_t maximises the predicted gain at S^t
    St = 0
    for t in range(K):
        bt = B[t]
        Sb = St | (1 << bt)
        for e in range(n):
            if (St >> e & 1) or e == bt:
                continue
            Se = St | (1 << e)
            # g(Se)-g(St) <= g(Sb)-g(St)   <=>  g(Se) - g(Sb) <= 0
            add_ub([(gv(Se), 1.0), (gv(Sb), -1.0)], 0.0)
        St = Sb
    mB = St

    if force_d0 is not None:
        add_eq([(fv(1 << B[0]), 1.0)], force_d0)

    c = np.zeros(nv)
    c[fv(mB)] = 1.0
    bounds = [(0, None)] * nv
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=bounds, method="highs")
    return res, (B, O, X, n, NS, mB, mO)


def rho(K, eta):
    k1 = (K - 1) * eta + 1.0
    q = (K - 1) * eta / k1
    return min(1 - q ** j * (1 - (K - j) / (K * eta)) for j in range(K)), \
        min(range(K), key=lambda j: 1 - q ** j * (1 - (K - j) / (K * eta)))


if __name__ == "__main__":
    K = int(sys.argv[1]); eta = float(eval(sys.argv[2]))
    extra = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    for (eu, eo) in [(1.0, eta), (eta ** 0.5, eta ** 0.5), (eta, 1.0)]:
        res, meta = solve(K, eu, eo, extra)
        r, j = rho(K, eta)
        L = 1 - (1 - 1 / (eta * K)) ** K
        print(f"K={K} eta={eta} split=({eu:.4f},{eo:.4f}) extra={extra}: "
              f"LP min f(B) = {res.fun if res.success else None}  "
              f"rho_K={r:.6f} (j*={j})  L_K={L:.6f}  status={res.status}")

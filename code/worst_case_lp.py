"""
Exact worst-case approximation ratio of the single-step predictive greedy
(Algorithm 1 of Zhao et al.) via a factor-revealing LP.

Instance = (f, ftilde) on ground set [n].  WLOG greedy picks 0,1,...,K-1 in order
(ties broken adversarially).  For a fixed candidate optimal set O we solve

    min  f({0..K-1})
    s.t. f monotone submodular, f(empty)=0
         ftilde(empty)=0
         d_B(A)/eta_u <= dt_B(A) <= eta_o * d_B(A)      (error model)
         greedy path: dt_t(S_t) >= dt_e(S_t) for all e not in S_t
         f(O) = 1

Worst-case ratio (adversarial ties) = min over all K-subsets O of the LP value.
"""
import itertools, sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

def worst_case(n, K, eta_u, eta_o, err_model="single", verbose=False):
    N = 1 << n
    nv = 2 * N                       # f[S] -> S,  ftilde[S] -> N+S
    F = lambda S: S
    G = lambda S: N + S

    rows_ub, b_ub = [], []
    def add_ub(coefs, rhs=0.0):
        rows_ub.append(coefs); b_ub.append(rhs)

    # monotone: f[S] - f[S|e] <= 0
    for S in range(N):
        for e in range(n):
            if not S >> e & 1:
                add_ub({F(S): 1, F(S | 1 << e): -1})
    # submodular: d_e(S|e') <= d_e(S)
    for S in range(N):
        for e in range(n):
            if S >> e & 1: continue
            for e2 in range(n):
                if e2 == e or S >> e2 & 1: continue
                T = S | 1 << e2
                # f[T|e]-f[T] - (f[S|e]-f[S]) <= 0
                c = {}
                for k, v in ((F(T | 1 << e), 1), (F(T), -1), (F(S | 1 << e), -1), (F(S), 1)):
                    c[k] = c.get(k, 0) + v
                add_ub(c)
    # error model
    for A in range(N):
        comp = (N - 1) ^ A
        Bs = []
        if err_model == "single":
            Bs = [1 << e for e in range(n) if comp >> e & 1]
        else:  # all pairs A,B disjoint, B nonempty
            B = comp
            while B:
                Bs.append(B); B = (B - 1) & comp
        for B in Bs:
            AB = A | B
            # d/eta_u - dt <= 0
            c = {}
            for k, v in ((F(AB), 1/eta_u), (F(A), -1/eta_u), (G(AB), -1), (G(A), 1)):
                c[k] = c.get(k, 0) + v
            add_ub(c)
            # dt - eta_o d <= 0
            c = {}
            for k, v in ((G(AB), 1), (G(A), -1), (F(AB), -eta_o), (F(A), eta_o)):
                c[k] = c.get(k, 0) + v
            add_ub(c)
    # greedy path
    for t in range(K):
        S = (1 << t) - 1
        for e in range(n):
            if e == t or S >> e & 1: continue
            # dt_e(S) - dt_t(S) <= 0
            c = {}
            for k, v in ((G(S | 1 << e), 1), (G(S), -1), (G(S | 1 << t), -1), (G(S), 1)):
                c[k] = c.get(k, 0) + v
            add_ub(c)

    A_ub = lil_matrix((len(rows_ub), nv))
    for i, c in enumerate(rows_ub):
        for k, v in c.items():
            A_ub[i, k] = v
    A_ub = A_ub.tocsr()
    b_ub = np.array(b_ub)

    SK = (1 << K) - 1
    obj = np.zeros(nv); obj[F(SK)] = 1
    best = (np.inf, None, None)
    for O in itertools.combinations(range(n), K):
        Om = sum(1 << i for i in O)
        A_eq = lil_matrix((3, nv))
        A_eq[0, F(0)] = 1; A_eq[1, G(0)] = 1; A_eq[2, F(Om)] = 1
        res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq.tocsr(), b_eq=[0, 0, 1],
                      bounds=[(None, None)] * nv, method="highs")
        if res.status == 0 and res.fun < best[0]:
            best = (res.fun, O, res.x)
    return best

def paper_bound(K, eta):
    return 1 - (1 - 1 / (eta * K)) ** K

if __name__ == "__main__":
    for (n, K) in [(4, 2), (5, 2), (6, 2), (6, 3)]:
        for (eu, eo) in [(2**0.5, 2**0.5), (2.0, 1.0), (1.0, 2.0), (2.0, 2.0)]:
            eta = eu * eo
            for em in ["single", "all"]:
                val, O, x = worst_case(n, K, eu, eo, em)
                print(f"n={n} K={K} eta_u={eu:.3f} eta_o={eo:.3f} eta={eta:.1f} "
                      f"model={em:6s}  LP worst-case={val:.6f}   "
                      f"paper bound={paper_bound(K, eta):.6f}   1/eta={1/eta:.6f}   O={O}")
            sys.stdout.flush()

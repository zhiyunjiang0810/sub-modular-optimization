"""ROUTE-TWO scratch: full instance LP for rho_K(eta).

Unknowns: f(S) and ft(S)=\tilde f(S) for all S subseteq N, |N|=2K.
Elements 0..K-1 are the greedy picks e_0..e_{K-1} (in this order),
elements K..2K-1 are the optimal set O.

Constraints (all linear in (f,ft)):
  f(empty)=ft(empty)=0
  monotone      : f(S+e)-f(S) >= 0
  submodular    : d_e(S) >= d_e(S+x)
  band          : d_e(S)/eta <= dt_e(S) <= d_e(S)      (WLOG eta_u=eta, eta_o=1)
  greedy        : dt_{e_t}(S^t) >= dt_x(S^t) for all x not in S^t
  optimality    : f(O)=1, f(T)<=1 for every K-subset T
Objective: minimise f(S^K) = F^ALG.

The LP value is the exact worst case over instances on 2K elements whose greedy
run avoids O.  Compared against min_j V_j(eta).
"""
import itertools, sys
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog


def Vj(K, eta, j):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q ** j * (1 - Fraction(K - j, K) / eta if isinstance(eta, Fraction)
                         else 1 - (K - j) / (K * eta))


def V(K, eta, j):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q ** j * (1 - (K - j) / (K * eta))


def solve(K, eta, verbose=True):
    n = 2 * K
    subs = list(range(1 << n))
    NS = 1 << n
    # variable index: f(S) -> S ; ft(S) -> NS + S
    nv = 2 * NS

    rows, rhs = [], []          # A_ub x <= b_ub
    eqr, eqb = [], []

    def z():
        return np.zeros(nv)

    # f(empty)=0, ft(empty)=0
    for base in (0, NS):
        r = z(); r[base + 0] = 1.0
        eqr.append(r); eqb.append(0.0)

    for S in subs:
        for e in range(n):
            if S >> e & 1:
                continue
            Se = S | (1 << e)
            # monotone: -(f(Se)-f(S)) <= 0
            r = z(); r[Se] = -1.0; r[S] = 1.0
            rows.append(r); rhs.append(0.0)
            # band upper: dt_e(S) - d_e(S) <= 0
            r = z(); r[NS + Se] = 1.0; r[NS + S] = -1.0; r[Se] = -1.0; r[S] = 1.0
            rows.append(r); rhs.append(0.0)
            # band lower: d_e(S)/eta - dt_e(S) <= 0
            r = z(); r[Se] = 1.0 / eta; r[S] = -1.0 / eta
            r[NS + Se] -= 1.0; r[NS + S] += 1.0
            rows.append(r); rhs.append(0.0)
            # submodularity: d_e(S+x) - d_e(S) <= 0  for x not in S, x != e
            for x in range(n):
                if x == e or (S >> x & 1):
                    continue
                Sx = S | (1 << x)
                Sxe = Sx | (1 << e)
                r = z()
                r[Sxe] += 1.0; r[Sx] -= 1.0
                r[Se] -= 1.0; r[S] += 1.0
                rows.append(r); rhs.append(0.0)

    # greedy
    for t in range(K):
        St = 0
        for s in range(t):
            St |= 1 << s
        Ste = St | (1 << t)
        for x in range(n):
            if St >> x & 1 or x == t:
                continue
            Sx = St | (1 << x)
            # dt_x(St) - dt_{e_t}(St) <= 0
            r = z()
            r[NS + Sx] += 1.0; r[NS + St] -= 1.0
            r[NS + Ste] -= 1.0; r[NS + St] += 1.0
            rows.append(r); rhs.append(0.0)

    O = 0
    for i in range(K, n):
        O |= 1 << i
    r = z(); r[O] = 1.0
    eqr.append(r); eqb.append(1.0)
    for T in itertools.combinations(range(n), K):
        m = 0
        for i in T:
            m |= 1 << i
        if m == O:
            continue
        r = z(); r[m] = 1.0
        rows.append(r); rhs.append(1.0)

    c = z()
    SK = (1 << K) - 1
    c[SK] = 1.0

    res = linprog(c, A_ub=np.array(rows), b_ub=np.array(rhs),
                  A_eq=np.array(eqr), b_eq=np.array(eqb),
                  bounds=[(None, None)] * nv, method="highs")
    if verbose:
        print(f"K={K} eta={eta}: LP status={res.status} value={res.fun!r}")
    return res


if __name__ == "__main__":
    for K in (2, 3):
        for eta in (1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0):
            res = solve(K, eta, verbose=False)
            best = min(V(K, eta, j) for j in range(K))
            jstar = min(range(K), key=lambda j: V(K, eta, j))
            print(f"K={K} eta={eta:<5} LP={res.fun:.10f}  min_j V_j={best:.10f} "
                  f"(j*={jstar})  diff={res.fun-best:+.2e}  status={res.status}")

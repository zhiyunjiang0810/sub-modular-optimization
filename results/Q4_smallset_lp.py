"""Q4 reconciliation LP (TASKS10): rebuild the count-grid hardness LP with
the O-independence constraint imposed ONLY where TASKS10 (b) and the
transcript argument need it, namely on states with x+y <= K, y <= 1 --
instead of on every balanced state of every size as in N4/night-10.

Variables: F(x,y) and H(x,y) (H = eta_u G, so the band is split-free:
dF <= dH <= eta dF on every edge).  Constraints: F monotone, submodular
(three second differences), F(0,0)=0, F(0,K)=1, F <= 1 on 0 < x+y <= K,
H(0,0)=0, band on all edges, and H(x,1) = H(x+1,0) for x+1 <= K.
Objective: minimize F(K,0).

Prediction being tested: with the small-set-only constraint the optimum is
exactly rho_K(eta) for EVERY n >= 2K -- including the n beyond night-10's
staircase onset where the globally constrained LP is provably > rho_K
(Q2_indep_nsweep).  Value < rho_K would contradict greedy's guarantee;
value > rho_K would contradict the Q4 family's feasibility (Q4_indep_check).

Run:  python3 results/Q4_smallset_lp.py     (exit 0 iff all match rho_K)
"""
import sys
from fractions import Fraction as Fr

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

TOL = 1e-8
fails = []


def rho_exact(K, eta):
    eta = Fr(eta)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return min(1 - q ** t * (1 - Fr(K - t, K) / eta) for t in range(K))


def solve(n, K, eta):
    X, Y = n - K, K
    nF = (X + 1) * (Y + 1)

    def fid(x, y):
        return x * (Y + 1) + y

    def hid(x, y):
        return nF + x * (Y + 1) + y

    nv = 2 * nF
    R, C, V, b = [], [], [], []

    def row(coefs, rhs):
        i = len(b)
        for c, v in coefs:
            R.append(i); C.append(c); V.append(v)
        b.append(rhs)

    e = float(eta)
    for x in range(X + 1):
        for y in range(Y + 1):
            for dx, dy in ((1, 0), (0, 1)):
                xx, yy = x + dx, y + dy
                if xx > X or yy > Y:
                    continue
                # -dF <= 0 (monotone)
                row([(fid(xx, yy), -1.0), (fid(x, y), 1.0)], 0.0)
                # dF - dH <= 0
                row([(fid(xx, yy), 1.0), (fid(x, y), -1.0),
                     (hid(xx, yy), -1.0), (hid(x, y), 1.0)], 0.0)
                # dH - eta dF <= 0
                row([(hid(xx, yy), 1.0), (hid(x, y), -1.0),
                     (fid(xx, yy), -e), (fid(x, y), e)], 0.0)
                # submodularity: dF at (x+sx, y+sy) <= dF at (x, y)
                for sx, sy in ((1, 0), (0, 1)):
                    if xx + sx > X or yy + sy > Y:
                        continue
                    row([(fid(xx + sx, yy + sy), 1.0),
                         (fid(x + sx, y + sy), -1.0),
                         (fid(xx, yy), -1.0), (fid(x, y), 1.0)], 0.0)
            if 0 < x + y <= K:
                row([(fid(x, y), 1.0)], 1.0)      # F <= 1 on small sets

    eqR, eqC, eqV, eqb = [], [], [], []

    def eq(coefs, rhs):
        i = len(eqb)
        for c, v in coefs:
            eqR.append(i); eqC.append(c); eqV.append(v)
        eqb.append(rhs)

    eq([(fid(0, 0), 1.0)], 0.0)
    eq([(fid(0, K), 1.0)], 1.0)
    eq([(hid(0, 0), 1.0)], 0.0)
    for x in range(K):                            # small-set O-independence
        eq([(hid(x, 1), 1.0), (hid(x + 1, 0), -1.0)], 0.0)

    A_ub = coo_matrix((V, (R, C)), shape=(len(b), nv)).tocsr()
    A_eq = coo_matrix((eqV, (eqR, eqC)), shape=(len(eqb), nv)).tocsr()
    obj = np.zeros(nv)
    obj[fid(K, 0)] = 1.0
    out = linprog(obj, A_ub=A_ub, b_ub=np.array(b), A_eq=A_eq,
                  b_eq=np.array(eqb), bounds=[(None, None)] * nv,
                  method='highs')
    assert out.status == 0, out.message
    return out.fun


def main():
    for K, eta, ns in [(3, Fr(3, 2), (6, 9, 12, 24)),
                       (3, Fr(5, 2), (6, 12, 24)),
                       (4, Fr(5, 2), (8, 14, 20, 32)),
                       (4, Fr(2), (8, 16, 32)),
                       (5, Fr(5, 2), (10, 19, 25, 40))]:
        rho = float(rho_exact(K, eta))
        for n in ns:
            v = solve(n, K, eta)
            ok = abs(v - rho) < TOL
            print(f"K={K} eta={eta} n={n:3d}: LP={v:.10f} rho_K={rho:.10f} "
                  f"{'PASS' if ok else 'FAIL'}")
            if not ok:
                fails.append((K, str(eta), n, v, rho))
    print()
    print("ALL PASS: small-set-only O-independence collapses the LP to "
          "rho_K at every n" if not fails else f"FAILURES: {fails}")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()

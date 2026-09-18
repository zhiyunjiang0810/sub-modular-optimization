"""Leakage structure of the family: which queries can distinguish the hidden O.

sigma(s) := the value the surrogate would take on a set of size s carrying at
most one element of O.  A query (x,y) LEAKS iff H(x,y) != sigma(x+y).
Checks, exactly:
  P1  y <= 1  =>  never leaks (H(x+1,0) = H(x,1));
  P2  x >= t* =>  never leaks, for every y (H == C there);
  P3  every leaking query has y >= 2 and x <= t*-1, hence |S| <= t*+K-1;
  P4  the union bound  Pr[some query leaks] <= Q * C(K,2)*s(s-1)/(n(n-1))
      evaluated for Q = c n K.
Also prints the K=2 specialization used in the write-up.
"""
from fractions import Fraction as Fr
from itertools import product
import check_family as cf


def leak_table(K, eta):
    jj, rho = cf.argmin_j(K, eta)
    m, d = cf.select_m(K, eta)
    r, g, a, F, H, X, tstar, Q, D, q, nu, C = cf.build(K, eta, jj, m, d)
    sigma = lambda s: H(s, 0)              # = H(s-1,1) for s >= 1
    leaks = []
    for x, y in product(range(X), range(K + 1)):
        if H(x, y) != sigma(x + y):
            leaks.append((x, y))
    p1 = all(H(x, y) == sigma(x + y) for x in range(X) for y in (0, 1))
    p2 = all(H(x, y) == C for x in range(tstar, X) for y in range(1, K + 1)) and \
         all(H(x, 0) == C for x in range(tstar + 1, X))
    p3 = all(y >= 2 and x <= tstar - 1 for (x, y) in leaks)
    return dict(K=K, eta=eta, j=jj, m=m, tstar=tstar, n_leak=len(leaks),
                P1=p1, P2=p2, P3=p3,
                max_x_leak=max([x for x, y in leaks], default=None),
                max_size_leak=max([x + y for x, y in leaks], default=None),
                size_cap=tstar + K - 1)


if __name__ == '__main__':
    bad = []
    for K in range(3, 8):
        for eta in sorted({Fr(a, b) for b in (1, 2, 3, 4) for a in range(b + 1, 5 * b + 1)}):
            t = leak_table(K, eta)
            if not (t['P1'] and t['P2'] and t['P3']):
                bad.append(t)
            if t['max_size_leak'] is not None and t['max_size_leak'] > t['size_cap']:
                bad.append(t)
    print('leakage-structure failures:', len(bad), bad[:5])
    print('sample K=3, eta=3/2 :', leak_table(3, Fr(3, 2)))
    print('sample K=5, eta=2   :', leak_table(5, Fr(2)))

    # P4: union bound, K=2 illustration and general
    def pr_bound(K, s, n):
        return Fr(K * (K - 1), 2) * Fr(s * (s - 1), n * (n - 1))
    for n in (10**3, 10**4, 10**6):
        print('K=2, s=6, n=%d : Pr[O subset of S] = %s ~ %.3e'
              % (n, pr_bound(2, 6, n), float(pr_bound(2, 6, n))))
    for n in (10**3, 10**6):
        s, K, c = 10, 3, 4
        Qn = c * n * K
        print('K=3, s<=%d, Q=%d n K queries, n=%d : union bound ~ %.3e'
              % (s, c, n, float(Qn * pr_bound(K, s, n))))

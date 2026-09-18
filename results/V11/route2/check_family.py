"""ROUTE-TWO blind derivation: exact-rational exhaustive check of the hard family.

For a grid of (K, eta in Q) it
  * computes j = argmin_j V_j(eta)  (rho_K = min_j V_j),
  * computes m as the first integer t >= 1 with Psi(t) = 1 - (t+1) d(t) <= 0,
  * checks admissibility (A) m >= eta(K-1), (B) m d <= 1, (C) (m+1) d >= 1,
  * checks location bounds eta(K-1) <= m < K eta,
  * checks, on the full count grid, that F is monotone submodular, 0<=F<=1,
    F(0,K)=1, the band Delta F <= Delta H <= eta Delta F on EVERY edge
    (including the closing edge x=t* -> t*+1), and H(x+1,0)=H(x,1),
  * checks W_K - rho_K = q^j (K-j)(d - 1/(K eta)) and
    W_K - rho_K < 1/(K (e^{K-1}-K-1)).
All arithmetic is exact (Fraction); floats only in printouts.
Run:  python3 check_family.py
"""
from fractions import Fraction as Fr
from itertools import product
import sys

# ---- a certified rational lower bound for e (e > 2.718281828459045) ----
E_LOW = Fr(2718281828459045, 10**15)          # < e
E_HIGH = Fr(2718281828459046, 10**15)         # > e


def params(K, eta):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    nu = eta / (eta - 1)
    return k1, q, nu


def V(K, eta, jj):
    _, q, _ = params(K, eta)
    return 1 - q**jj * (1 - Fr(K - jj, 1) / (K * eta))


def argmin_j(K, eta):
    vals = [V(K, eta, jj) for jj in range(K)]          # 0 <= j <= K-1
    best = min(vals)
    return vals.index(best), best


def d_of(K, eta, t):
    """d determined by a_{t*}=0 with m=t.  Returns None if denominator vanishes."""
    _, _, nu = params(K, eta)
    num = nu**t - K
    den = K * (eta * nu**t - t - eta)
    if den == 0:
        return None
    return Fr(num, 1) / den if isinstance(num, int) else num / den


def select_m(K, eta, tmax=4000):
    """first integer t>=1 with Psi(t)=1-(t+1)d(t) <= 0"""
    for t in range(1, tmax + 1):
        dt = d_of(K, eta, t)
        if dt is None:
            continue
        if 1 - (t + 1) * dt <= 0:
            return t, dt
    return None, None


def build(K, eta, jj, m, d):
    """r,g,a on x=0..X and F,H on the count grid."""
    _, q, nu = params(K, eta)
    Q = q**jj
    C = ((K - 1) * eta + 1) / K
    D = Q * d
    tstar = jj + m
    X = tstar + 3

    def r(xx):
        if xx <= jj:
            return q**xx
        if xx <= tstar:
            return Q - (xx - jj) * D
        return Fr(0)

    def g(xx):
        if xx <= jj:
            return q**xx / K
        if xx <= tstar:
            u = xx - jj
            return eta * D - (eta * D - Q / K) * nu**u
        return Fr(0)

    a = lambda xx: r(xx) - g(xx)
    c = lambda y: Fr(K - y, K - 1)

    def F(xx, y):
        return 1 - r(xx) if y == 0 else 1 - c(y) * a(xx)

    def H(xx, y):
        return (C - r(xx) - (eta - 1) * a(xx)) if y == 0 else (C - eta * c(y) * a(xx))

    return r, g, a, F, H, X, tstar, Q, D, q, nu, C


def audit(K, eta, verbose=False):
    rep = {}
    jj, rho = argmin_j(K, eta)
    m, d = select_m(K, eta)
    rep['K'], rep['eta'], rep['j'], rep['rho'] = K, eta, jj, rho
    if m is None:
        rep['fail'] = 'no m found'
        return rep
    rep['m'], rep['d'] = m, d

    _, q, nu = params(K, eta)
    A_ok = m >= eta * (K - 1)
    B_ok = m * d <= 1
    C_ok = (m + 1) * d >= 1
    B_alt = nu**m * (K * eta - m) >= K * eta
    loc_lo = eta * (K - 1) <= m
    loc_hi = m < K * eta
    rep.update(A=A_ok, B=B_ok, C=C_ok, B_alt=(B_ok == B_alt), loc=(loc_lo and loc_hi))

    r, g, a, F, H, X, tstar, Q, D, q, nu, C = build(K, eta, jj, m, d)

    ok = True
    msgs = []

    # sequence-level conditions
    for xx in range(X):
        if not (r(xx) >= r(xx + 1) >= 0):
            ok = False; msgs.append(f'r not nonincr/nonneg at x={xx}')
        if not (a(xx) >= a(xx + 1) >= 0):
            ok = False; msgs.append(f'a not nonincr/nonneg at x={xx}')
        if not (g(xx) >= g(xx + 1) >= 0):
            ok = False; msgs.append(f'g not nonincr/nonneg at x={xx}')
        if not (K * g(xx) >= r(xx)):
            ok = False; msgs.append(f'K g < r at x={xx}')
    for xx in range(X - 1):
        if not (r(xx + 2) - r(xx + 1) >= r(xx + 1) - r(xx)):
            ok = False; msgs.append(f'r not convex at x={xx}')
        if not (a(xx + 2) - a(xx + 1) >= a(xx + 1) - a(xx)):
            ok = False; msgs.append(f'a not convex at x={xx}')
    rep['seq'] = ok

    # F monotone submodular, range, OPT
    ok2 = True
    for xx, y in product(range(X), range(K + 1)):
        if not (0 <= F(xx, y) <= 1):
            ok2 = False; msgs.append(f'F range at ({xx},{y})')
        if F(xx + 1, y) < F(xx, y):
            ok2 = False; msgs.append(f'F not x-monotone at ({xx},{y})')
        if y < K and F(xx, y + 1) < F(xx, y):
            ok2 = False; msgs.append(f'F not y-monotone at ({xx},{y})')
    for xx, y in product(range(X - 1), range(K + 1)):
        if F(xx + 2, y) - F(xx + 1, y) > F(xx + 1, y) - F(xx, y):
            ok2 = False; msgs.append(f'F not x-concave at ({xx},{y})')
    for xx, y in product(range(X), range(K - 1)):
        if F(xx, y + 2) - F(xx, y + 1) > F(xx, y + 1) - F(xx, y):
            ok2 = False; msgs.append(f'F not y-concave at ({xx},{y})')
    for xx, y in product(range(X), range(K)):          # cross / DR
        if F(xx + 1, y + 1) - F(xx, y + 1) > F(xx + 1, y) - F(xx, y):
            ok2 = False; msgs.append(f'F cross fails at ({xx},{y})')
    if F(0, K) != 1:
        ok2 = False; msgs.append('F(0,K) != 1')
    rep['submod'] = ok2

    # band on every edge  +  zero-pattern (Definition 1)
    ok3 = True
    for xx, y in product(range(X), range(K + 1)):
        dF = F(xx + 1, y) - F(xx, y)
        dH = H(xx + 1, y) - H(xx, y)
        if not (dF <= dH <= eta * dF):
            ok3 = False; msgs.append(f'band x-edge ({xx},{y})')
        if (dF == 0) != (dH == 0):
            ok3 = False; msgs.append(f'zero-pattern x-edge ({xx},{y})')
        if y < K:
            dF = F(xx, y + 1) - F(xx, y)
            dH = H(xx, y + 1) - H(xx, y)
            if not (dF <= dH <= eta * dF):
                ok3 = False; msgs.append(f'band y-edge ({xx},{y})')
            if (dF == 0) != (dH == 0):
                ok3 = False; msgs.append(f'zero-pattern y-edge ({xx},{y})')
    rep['band'] = ok3

    # H depends only on |S| when y<=1
    ok4 = all(H(xx + 1, 0) == H(xx, 1) for xx in range(X))
    # H constant (=C) once x >= t*+1, all y ; and a_x = 0 for x >= t*
    ok5 = all(H(xx, y) == C for xx in range(tstar + 1, X) for y in range(K + 1))
    rep['sizeonly'], rep['flat'] = ok4, ok5

    WK = F(K, 0)
    gap = WK - rho
    gap_formula = q**jj * (K - jj) * (d - Fr(1) / (K * eta))
    rep['W'], rep['gap'] = WK, gap
    rep['gap_formula'] = (gap == gap_formula)
    # bound  1/(K(e^{K-1}-K-1))  -- use certified rational lower bound on e^{K-1}
    eKm1_low = E_LOW**(K - 1)
    bound_up = Fr(1) / (K * (eKm1_low - K - 1))      # >= true bound
    bound_lo_e = E_HIGH**(K - 1)
    bound_lo = Fr(1) / (K * (bound_lo_e - K - 1))    # <= true bound
    rep['bound'] = float(bound_lo)
    rep['bound_ok'] = gap < bound_lo                 # strictly below the TRUE bound
    rep['monotone_le_1_over_eta'] = (WK >= Fr(1) / eta) if eta >= K else None
    rep['msgs'] = msgs[:6]
    return rep


def main():
    Ks = list(range(3, 13))
    etas = [Fr(a, b) for b in (1, 2, 3, 4, 5, 8, 10, 16, 100)
            for a in range(1, 40 * b + 1) if Fr(a, b) > 1]
    etas = sorted(set(etas))
    etas = [e for e in etas if e <= 40]
    bad = []
    n = 0
    worst_ratio = None
    for K in Ks:
        for eta in etas:
            rep = audit(K, eta)
            n += 1
            flags = ['fail' in rep] + [not rep.get(k, True) for k in
                     ('A', 'B', 'C', 'B_alt', 'loc', 'seq', 'submod', 'band',
                      'sizeonly', 'flat', 'gap_formula', 'bound_ok')]
            if any(flags):
                bad.append(rep)
            else:
                rr = float(rep['gap']) / rep['bound']
                if worst_ratio is None or rr > worst_ratio[0]:
                    worst_ratio = (rr, K, eta, rep['m'], rep['j'])
    print(f'grid cells checked: {n}')
    print(f'failures: {len(bad)}')
    for rep in bad[:15]:
        print('  FAIL', {k: (str(v) if not isinstance(v, (bool, int)) else v)
                         for k, v in rep.items() if k != 'msgs'})
        print('       ', rep.get('msgs'))
    if worst_ratio:
        print('worst (gap / bound) ratio: %.6g at K=%d eta=%s m=%d j=%d'
              % worst_ratio)


if __name__ == '__main__':
    main()

"""ROUTE-TWO: symbolic verification of the LP dual certificate for rho_K(eta).

Reduced primal (variables g_0..g_{K-1} >= 0, P_0..P_K >= 0; theta = 1-1/eta):
   min  sum_t g_t
   (A_t) sum_{s<t} g_s + P_t            >= 1            t=0..K-1   [y_t]
   (B_t) K g_t + theta P_{t+1} - P_t    >= 0            t=0..K-1   [z_t]
   (C_t) P_t - P_{t+1}                  >= 0            t=0..K-1   [w_t]

Dual:
   max  sum_t y_t
   (Dg_t)  sum_{t'>t} y_{t'} + K z_t         <= 1       t=0..K-1
   (DP_t)  y_t - z_t + theta z_{t-1} + w_t - w_{t-1} <= 0   t=0..K-1
   (DP_K)  theta z_{K-1} - w_{K-1}           <= 0
   y,z,w >= 0      (z_{-1}=w_{-1}=0)

Certificate for segment eta in [K-j, K-j+1]:
   z_t = 1/K                     for t >= j
   z_{j-1} = (K eta - K + j)/(K k1),   z_t = q^{j-1-t} z_{j-1}   for t <= j-1
   w_t = 0 for t < j ;  w_t = theta/K - (K-1-t)/(K eta)  for t >= j
   y_t = z_t - theta z_{t-1} - w_t + w_{t-1}
Claim: dual objective = V_j(eta) = 1 - q^j (1 - (K-j)/(K eta)).
"""
import sympy as sp

eta = sp.symbols('eta', positive=True)


def Vsym(K, j):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return sp.simplify(1 - q ** j * (1 - sp.Rational(K - j, K) / eta))


def certificate(K, j):
    theta = 1 - 1 / eta
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    z = {-1: sp.Integer(0)}
    for t in range(j, K):
        z[t] = sp.Rational(1, K)
    if j >= 1:
        zjm1 = (K * eta - K + j) / (K * k1)
        for t in range(0, j):
            z[t] = sp.simplify(q ** (j - 1 - t) * zjm1)
    w = {-1: sp.Integer(0)}
    for t in range(0, j):
        w[t] = sp.Integer(0)
    for t in range(j, K):
        w[t] = sp.simplify(theta / K - sp.Rational(K - 1 - t, 1) / (K * eta))
    y = {}
    for t in range(K):
        y[t] = sp.simplify(z[t] - theta * z[t - 1] - w[t] + w[t - 1])
    return y, z, w, theta


def nonneg_on(expr, lo, hi):
    """True iff expr >= 0 for all eta in [lo,hi] (hi may be oo)."""
    dom = sp.Interval(lo, hi) if hi is not sp.oo else sp.Interval(lo, sp.oo)
    sol = sp.solveset(sp.simplify(expr) < 0, eta, dom)
    return sol == sp.EmptySet


def check(K):
    ok = True
    for j in range(0, K):
        lo, hi = K - j, (sp.oo if j == 0 else K - j + 1)
        y, z, w, theta = certificate(K, j)
        obj = sp.simplify(sum(y[t] for t in range(K)))
        Vj = Vsym(K, j)
        idok = sp.simplify(obj - Vj) == 0
        # dual feasibility
        feas = []
        for t in range(K):
            Yt = sum(y[s] for s in range(t + 1, K))
            feas.append(('Dg%d' % t, sp.simplify(1 - Yt - K * z[t])))
            feas.append(('DP%d' % t, sp.simplify(-(y[t] - z[t] + theta * z[t - 1]
                                                  + w[t] - w[t - 1]))))
        feas.append(('DPK', sp.simplify(w[K - 1] - theta * z[K - 1])))
        for t in range(K):
            feas.append(('y%d' % t, y[t]))
            feas.append(('z%d' % t, z[t]))
            feas.append(('w%d' % t, w[t]))
        bad = [nm for nm, ex in feas if not nonneg_on(ex, lo, hi)]
        print(f"  K={K} j={j} segment=[{lo},{hi}]  obj==V_j: {idok}   "
              f"violations: {bad if bad else 'none'}")
        ok = ok and idok and not bad
    return ok


def check_argmin(K):
    """c_j = q^j (1-(K-j)/(K eta)) ; show c_{j+1} >= c_j  <=>  eta <= K-j."""
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    allok = True
    for j in range(0, K):
        cj = q ** j * (1 - sp.Rational(K - j, K) / eta)
        cj1 = q ** (j + 1) * (1 - sp.Rational(K - j - 1, K) / eta)
        diff = sp.simplify(sp.factor(sp.together(cj1 - cj)))
        # sign of (cj1-cj) should equal sign of (K-j-eta)
        test = sp.simplify(sp.factor(diff / (K - j - eta)))
        pos = nonneg_on(test, 1, sp.oo) and sp.simplify(test) != 0
        print(f"  K={K} j={j}: (c_{{j+1}}-c_j)/(K-j-eta) = {sp.simplify(test)}  "
              f"positive on eta>=1: {pos}")
        allok = allok and pos
    return allok


def closed_forms():
    print("closed forms:")
    for K in (2, 3, 4):
        for j in range(K):
            print(f"  K={K} j={j}: V_j = {sp.simplify(sp.factor(Vsym(K, j)))}"
                  f"   on eta in [{K-j},{K-j+1 if j else 'oo'}]")


if __name__ == '__main__':
    print("== dual certificate feasibility and objective ==")
    all_ok = True
    for K in range(2, 8):
        all_ok &= check(K)
    print("all dual checks passed:", all_ok)
    print("== argmin structure ==")
    for K in range(2, 7):
        check_argmin(K)
    closed_forms()

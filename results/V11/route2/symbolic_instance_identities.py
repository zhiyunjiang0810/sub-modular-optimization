"""ROUTE-TWO: symbolic (general eta, K = 2..8) identities behind the attaining family.

I1  k1 = K + (eta-1)(K-1)                  (drives the head tie)
I2  head step: (1/eta) g_t + theta*(K-1)/K*g_t = m_t/eta  with g_t=R_t/k1, m_t=R_t/K
I3  tail step: (1/eta) g + theta*g = g     with g = R_j/(K eta), and m/eta = g
I4  sum_t g_t = V_j(eta)
I5  F_OPT = 1 for the atom system: p tail picks + (K-p) optimal picks <= 1
"""
import sympy as sp

eta = sp.symbols('eta', positive=True)
theta = 1 - 1 / eta


def run(K):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    print(f"K={K}")
    print("  I1:", sp.simplify(k1 - (K + (eta - 1) * (K - 1))) == 0)
    Rt = sp.symbols('R', positive=True)
    gt, mt = Rt / k1, Rt / K
    lhs = gt / eta + theta * sp.Rational(K - 1, K) * gt
    print("  I2:", sp.simplify(lhs - mt / eta) == 0)
    Rj = sp.symbols('Rj', positive=True)
    g = Rj / (K * eta)
    print("  I3:", sp.simplify(g / eta + theta * g - g) == 0,
          sp.simplify((Rj / K) / eta - g) == 0)
    for j in range(K):
        R = [sp.Integer(1)]
        gs = []
        for t in range(K):
            gs.append(R[t] / k1 if t < j else R[j] / (K * eta))
            R.append(sp.simplify(R[t] - gs[t]))
        Vj = 1 - q ** j * (1 - sp.Rational(K - j, K) / eta)
        ok4 = sp.simplify(sum(gs) - Vj) == 0
        # I5: for any K-set T with r optimal elements,
        #     f(T) <= r/K + (1-r/K)*[(1-R_j) + R_j/eta] <= 1,
        # so it is enough that  (1-R_j) + R_j/eta - 1 = -R_j(1-1/eta) <= 0.
        slack = sp.simplify((1 - R[j]) + R[j] / eta - 1)
        ok5 = (sp.solveset(slack > 0, eta, sp.Interval(1, sp.oo)) == sp.EmptySet)
        print(f"  j={j}: I4 sum g_t == V_j : {ok4}    I5 competing K-sets <= 1 : {ok5}")


if __name__ == '__main__':
    for K in range(2, 9):
        run(K)

#!/usr/bin/env python3
"""ROUTE-TWO (TASKS11 Q7) symbolic + exact-rational checks for thm:hardness.

Only uses the statement itself, definition1.md, assumptions.md, notation.md.
Exact arithmetic only (sympy Rational / Fraction); floats appear in printouts.

Checks:
  C1  H_{K,tau}(eta) == L_K(thetabar) with thetabar = (eta(K-tau)+1)/K   [SYMBOLIC]
  C2  thetabar >= 1  <=>  eta >= (K-1)/(K-tau)                          [SYMBOLIC]
  C3  H_{K,tau}(eta) >= L_K(eta) for eta >= 1, 1 <= tau < K             [EXHAUSTIVE grid]
  C4  lim_{K->oo} H_{K,tau}(eta) = 1 - exp(-1/eta)                      [SYMBOLIC]
  C5  union-bound arithmetic at level tau and level tau+1               [SYMBOLIC]
  C6  numeric walk-through K=3, eta=3/2, tau=1 (c=0) and K=2            [EXACT]
"""
from fractions import Fraction as F
import sympy as sp

K, tau, eta, n, c = sp.symbols('K tau eta n c', positive=True)

def H(Ks, taus, etas):
    return 1 - (1 - sp.Rational(1, 1) / (etas * (Ks - taus) + 1)) ** Ks

def L(Ks, x):
    return 1 - (1 - sp.Rational(1, 1) / (x * Ks)) ** Ks

out = []

# ---- C1 --------------------------------------------------------------
thetabar = (eta * (K - tau) + 1) / K
c1 = sp.simplify(H(K, tau, eta) - L(K, thetabar))
out.append(("C1  H - L_K(thetabar)", sp.simplify(c1)))

# ---- C2 --------------------------------------------------------------
# thetabar >= 1  <=>  eta(K-tau)+1 >= K  <=>  eta >= (K-1)/(K-tau)  (K>tau)
c2 = sp.simplify(sp.expand((eta * (K - tau) + 1 - K) - (K - tau) * (eta - (K - 1) / (K - tau))))
out.append(("C2  [eta(K-tau)+1-K] - (K-tau)[eta-(K-1)/(K-tau)]", c2))

# ---- C3 exhaustive rational grid -------------------------------------
bad = []
for Kv in range(2, 13):
    for tv in range(1, Kv):
        for num in range(1, 41):
            ev = F(num, 4)               # eta in {1/4,...,10} step 1/4
            if ev < 1:
                continue
            if ev * (Kv - tv) + 1 < Kv:  # thetabar < 1, outside hypothesis
                continue
            e = sp.Rational(ev.numerator, ev.denominator)
            if sp.nsimplify(H(Kv, tv, e) - L(Kv, e)) < 0:
                bad.append((Kv, tv, ev))
out.append(("C3  #(K,tau,eta) with H < L_K(eta)", len(bad)))
if bad:
    out.append(("C3  witnesses", bad[:5]))

# ---- C4 --------------------------------------------------------------
Kc = sp.symbols('Kc', positive=True)
lim = sp.limit(H(Kc, tau, eta), Kc, sp.oo)
out.append(("C4  lim_K H", sp.simplify(lim)), )
out.append(("C4  minus 1-exp(-1/eta)", sp.simplify(lim - (1 - sp.exp(-1 / eta)))))

# ---- C5 union bounds --------------------------------------------------
# level-t bound: n^c * binom(K,t) * (K/n)^t  <=  K^(2t) / (t! n^(t-c))
t = sp.symbols('t', positive=True, integer=True)
lvl = lambda tt: n**c * sp.binomial(K, tt) * (K / n) ** tt
relax = lambda tt: K**(2 * tt) / (sp.factorial(tt) * n ** (tt - c))
out.append(("C5  level tau+1 relaxed form", sp.simplify(relax(tau + 1))))
out.append(("C5  matches displayed eps_n 2nd term",
            sp.simplify(relax(tau + 1) - K**(2 * tau + 2) / (sp.factorial(tau + 1) * n**(tau + 1 - c)))))
out.append(("C5  level tau relaxed form", sp.simplify(relax(tau))))

# stated condition n >= 4 K^(c+2) fed into the level-tau bound, integer c, tau=c+1
cv, Kv_ = sp.symbols('cv Kv', positive=True)
n_stated = 4 * Kv_ ** (cv + 2)
lvl_tau_at_stated = sp.simplify((Kv_ ** (2 * (cv + 1))) / (sp.factorial(cv + 1) * n_stated ** ((cv + 1) - cv)))
out.append(("C5  level-tau bound at n=4K^(c+2), integer c, tau=c+1", sp.simplify(lvl_tau_at_stated)))

# alternative sufficient condition n >= 4 K^(2 tau)
out.append(("C5  level-tau bound at n=4K^(2tau) (tau-c>=1)",
            sp.simplify(K**(2 * tau) / (sp.factorial(tau) * (4 * K**(2 * tau))))))

# ---- C6 numerics ------------------------------------------------------
def walk(Kv, tv, ev):
    e = sp.Rational(ev.numerator, ev.denominator)
    beta = sp.Rational(1, 1) / (e * (Kv - tv) + 1)
    hv = H(Kv, tv, e)
    tb = (e * (Kv - tv) + 1) / Kv
    resid = [sp.Rational(1, 1)]
    for _ in range(Kv):
        resid.append(sp.simplify(resid[-1] * (1 - beta)))
    return dict(K=Kv, tau=tv, eta=e, beta=sp.nsimplify(beta), thetabar=sp.nsimplify(tb),
                H=sp.nsimplify(hv), Hfloat=float(hv), L_eta=sp.nsimplify(L(Kv, e)),
                residuals=[sp.nsimplify(r) for r in resid],
                value_after_K=sp.nsimplify(1 - resid[-1]))

w1 = walk(3, 1, F(3, 2))
w2 = walk(2, 1, F(3, 2))
out.append(("C6  K=3,tau=1,eta=3/2", w1))
out.append(("C6  K=2,tau=1,eta=3/2", w2))
out.append(("C6  K=3 hypothesis eta>=(K-1)/(K-tau) for tau=2", sp.Rational(3, 2) >= sp.Rational(2, 1)))
out.append(("C6  L_2(1)", sp.nsimplify(L(2, 1))))

# union bound numbers at the stated n
for (Kv, tv, cval) in [(3, 1, 0), (2, 1, 0)]:
    nv = 4 * Kv ** (cval + 2)
    lt = F(nv) ** cval * F(sp.binomial(Kv, tv)) * F(Kv, nv) ** tv
    out.append((f"C6  level-tau union bound, K={Kv}, c={cval}, n={nv}", lt, float(lt)))
    eps_disp = F(Kv, nv) + F(Kv ** (2 * tv + 2), sp.factorial(tv + 1) * nv ** (tv + 1 - cval))
    eps_mine = F(Kv, nv) + F(Kv ** (2 * tv), sp.factorial(tv) * nv ** (tv - cval))
    out.append((f"C6  eps_n displayed vs derived, K={Kv}, n={nv}", eps_disp, float(eps_disp),
                eps_mine, float(eps_mine)))

for k, *v in out:
    print(k, "->", *v)

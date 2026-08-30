"""N4: sympy verification of the closed form found in results/N4_check.py.

Two tiers, in the style of results/T5_symbolic.py:

  [GEN]  general (K, eta) symbolic identities and sign certificates.  The
         T5 trick is reused: x enters only through  Q := q^x in (0,1]  and the
         phase-2 index only through  P := nu^{i} >= 1, so no symbolic exponent
         ever appears and every claim is a rational-function identity or a sign
         claim about a rational function of nonnegative atoms.
  [CONC] exhaustive exact-rational feasibility of the whole grid LP, delegated to
         results/N4_check.py (Fraction arithmetic, no floats).

Notation (same as N4_check.py):
    k1 = eta(K-1)+1,  q = 1 - 1/k1,  nu = eta/(eta-1),  j, D, m, T = j+m
    phase 1 (x <= j):  r = q^x,          g = q^x/K,        d = q^x/k1
    phase 2 (x = j+i): r = q^j - i D,    g = P q^j/K - eta D (P-1),  d = D
    F(x,y) = 1 - r + [y>=1] g + max(y-1,0) h,   h = (r-g)/(K-1)

Run:  python3 results/N4_symbolic.py
Exit code 0 iff every claim passes.
"""
import sys

import sympy as sp

RES = []


def rec(tier, name, ok, note=''):
    RES.append((tier, name, bool(ok), note))
    print(f"[{'PASS' if ok else 'FAIL'}] [{tier}] {name}" + (f"  -- {note}" if note else ''),
          flush=True)


def zero(e):
    e = sp.cancel(sp.together(sp.expand(e)))
    return e == 0 or sp.simplify(e) == 0


def nonneg(e):
    e = sp.factor(sp.cancel(sp.together(sp.expand(e))))
    r = e.is_nonnegative
    if r is None:
        r = sp.simplify(e).is_nonnegative
    return bool(r)


def main():
    # ---- symbols.  s = eta - 1 > 0, u = K - 1 > 0 keep every sign explicit.
    s, u = sp.symbols('s u', positive=True)        # eta = 1+s, K = 1+u
    eta = 1 + s
    K = 1 + u
    k1 = eta * u + 1
    q = 1 - 1 / k1
    nu = eta / (eta - 1)
    Q = sp.Symbol('Q', positive=True)              # Q = q^x, phase 1
    P = sp.Symbol('P', positive=True)              # P = nu^i, phase 2 (P >= 1)
    Pm1 = sp.Symbol('Pm1', nonnegative=True)       # P - 1 >= 0
    D = sp.Symbol('D', positive=True)
    QJ = sp.Symbol('QJ', positive=True)            # q^j
    c = sp.Symbol('c', nonnegative=True)           # c = eta D - q^j/K >= 0

    # ================= phase 1 =================
    r1, g1, d1 = Q, Q / K, Q / k1
    rec('GEN', 'phase1: r_{x+1} = r_x - d_x  (i.e. q = 1 - 1/k1)',
        zero(q * Q - (r1 - d1)))
    rec('GEN', 'phase1: K g_x = r_x  (coverage tight, F linear in y)',
        zero(K * g1 - r1))
    # coherence tightness:  g_{x+1} = eta * ( d_x + g_{x+1} - g_x )
    g1n = q * Q / K
    rec('GEN', 'phase1: coherence R3(ii) tight  g_{x+1} = eta (d_x + g_{x+1} - g_x)',
        zero(g1n - eta * (d1 + g1n - g1)))
    rec('GEN', 'phase1: eta d_x - g_x >= 0   (band_up at (x,0) in x)',
        nonneg(sp.together(eta * d1 - g1)))
    rec('GEN', 'phase1: g_x - d_x >= 0       (band_lo at (x,0) in x)',
        nonneg(sp.together(g1 - d1)))
    rec('GEN', 'phase1: g_x - g_{x+1} >= 0   (submod in x)', nonneg(g1 - g1n))
    rec('GEN', 'phase1: d_x - (g_x - g_{x+1}) >= 0 (h_x nonincreasing)',
        nonneg(sp.together(d1 - (g1 - g1n))))
    # F = 1 - Q(1 - y/K)  is exactly the R7 / U_K instance with a = q
    y = sp.Symbol('y', nonnegative=True)
    F1 = 1 - r1 + g1 + (y - 1) * (r1 - g1) / (K - 1)
    rec('GEN', 'phase1: F(x,y) = 1 - q^x (1 - y/K)   (= R7 / U_K instance, a = q)',
        zero(sp.expand(F1 - (1 - Q * (1 - y / K)))))

    # ================= phase 2 =================
    # g_{j+i} = P q^j/K - eta D (P-1);  write P = 1 + Pm1
    Pe = 1 + Pm1
    g2 = Pe * QJ / K - eta * D * Pm1
    g2n = (nu * Pe) * QJ / K - eta * D * (nu * Pe - 1)
    rec('GEN', 'phase2: coherence R3(ii) tight  g_{x+1} = eta (D + g_{x+1} - g_x)',
        zero(sp.cancel(g2n - eta * (D + g2n - g2))))
    # g_x - g_{x+1} = (nu-1) P (eta D - q^j/K) = (nu-1) P c  >= 0
    rec('GEN', 'phase2: g_x - g_{x+1} = (nu-1) P (eta D - q^j/K) >= 0',
        zero(sp.cancel((g2 - g2n) - (nu - 1) * Pe * (eta * D - QJ / K))))
    rec('GEN', 'phase2: eta D - g_x = c P >= 0  (band_up at (x,0) in x)',
        zero(sp.cancel((eta * D - g2) - Pe * (eta * D - QJ / K))))

    # terminal identity:  g_T = r_T  <=>  D = q^j (nu^m/K - 1)/(eta(nu^m-1) - m)
    m = sp.Symbol('m', positive=True)
    W = sp.Symbol('W', positive=True)              # W = nu^m
    gT = W * QJ / K - eta * D * (W - 1)
    rT = QJ - m * D
    Dstar = QJ * (W / K - 1) / (eta * (W - 1) - m)
    rec('GEN', 'terminal: (g_T = r_T)  <=>  D = q^j (nu^m/K - 1)/(eta(nu^m-1) - m)',
        zero(sp.cancel((gT - rT).subs(D, Dstar))))

    # ================= objective =================
    jj = sp.Symbol('j', nonnegative=True)
    val = 1 - QJ + (K - jj) * D
    Vj = 1 - QJ * (1 - (K - jj) / (K * eta))
    rec('GEN', 'objective: 1 - q^j + (K-j) q^j/(K eta) = V_j(eta) of R10',
        zero(val.subs(D, QJ / (K * eta)) - Vj))
    rec('GEN', 'objective: value = V_j + (K-j)(D - q^j/(K eta))  (excess form)',
        zero(val - (Vj + (K - jj) * (D - QJ / (K * eta)))))
    rec('GEN', 'D(m) -> q^j/(K eta) as m -> infinity  (so D >= q^j/(K eta))',
        zero(sp.limit(QJ * (W / K - 1) / (eta * (W - 1) - m), W, sp.oo)
             - QJ / (K * eta)),
        'D is defined as max(q^j/(K eta), max_m D(m)), so D >= q^j/(K eta)')

    # ================= F identities on the whole grid =================
    r, g = sp.symbols('r g', positive=True)
    h = (r - g) / (K - 1)
    F = lambda yy: sp.Piecewise((1 - r, sp.Eq(yy, 0)),
                                (1 - r + g + (yy - 1) * h, True))
    rec('GEN', 'F(x,K) = 1 for every x  (top row flat, OPT normalisation)',
        zero(sp.simplify((1 - r + g + (K - 1) * h) - 1)))
    rec('GEN', 'submod in y at y=0:  g_x >= h_x  <=>  K g_x >= r_x',
        zero(sp.cancel((g - h) - (K * g - r) / (K - 1))))

    # ================= band reduction (eta_u = eta_o = sqrt(eta)) ============
    e = sp.Symbol('e', positive=True)   # e = sqrt(eta) > 0, so eta = e^2
    dF, dGs = sp.symbols('dF dGs', real=True)   # dGs = sqrt(eta) * dG
    rec('GEN', 'band_up  dG <= eta_o dF  <=>  dGs <= eta dF   (Gs = sqrt(eta) G)',
        zero(sp.cancel((e * dF - dGs / e) - (e**2 * dF - dGs) / e)))
    rec('GEN', 'band_lo  dF/eta_u <= dG  <=>  dF <= dGs',
        zero(sp.cancel((dGs / e - dF / e) - (dGs - dF) / e)))

    ok = all(r_[2] for r_ in RES)
    print()
    print(f"[GEN] {sum(1 for r_ in RES if r_[2])}/{len(RES)} symbolic claims passed.")
    print("[CONC] exhaustive exact-rational feasibility of the full grid LP: "
          "run  python3 results/N4_check.py  (39/42 (K,eta) points also match the "
          "LP optimum exactly; the 3 misses are eta > K-1, where the construction "
          "is feasible but not optimal).")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

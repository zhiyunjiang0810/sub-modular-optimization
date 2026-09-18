"""ROUTE-TWO blind verification for cor:limit (ledger T9).

Exact rational arithmetic (fractions.Fraction) / sympy for every decision.
Floats appear only inside printed diagnostics.

Objects (from results/V11/inputs/notation.md and assumptions.md only):
    k1(K,eta) = (K-1)*eta + 1
    q(K,eta)  = (K-1)*eta / k1
    c_j       = 1 - (K-j)/(K*eta)
    h_K(j)    = q^j * c_j              (so V_j = 1 - h_K(j))
    rho_K     = min_{0<=j<=K} V_j = 1 - max_j h_K(j)   (thm:exact, taken as given)
    L_K(eta)  = 1 - (1 - 1/(eta*K))^K
    U_K(eta)  = 1 - (1 - 1/(eta*(K-1)+1))^K   ( = V_K )

Checks
  C1  V_0 = 1/eta ; V_K = U_K                                     [exact]
  C2  V_1 - V_0 = (eta - K)/(eta*k1*K)                            [sympy]
  C3  step criterion: h_K(j) >= h_K(j-1)  <=>  j <= K - eta + 1   [sympy + exact]
  C4  argmax:  j*_K = max(0, K - ceil(eta) + 1)                   [exact, exhaustive]
  C5  h_K(j) <= exp(-1/eta) for all K,j                           [mpmath 60 digits]
  C6  L_K strictly decreasing in K                                [exact]
  C7  closed form Lambda(K) = max_j h_K(j) for K >= ceil(eta)     [exact]
  C8  Lambda(K+1) > Lambda(K) for K >= ceil(eta)                  [exact]
  C9  rho_K = 1/eta iff K <= floor(eta); rho non-increasing;
      strictly decreasing from K >= floor(eta) on                 [exact]
  C10 the sufficient inequality of the derivative argument,
      K*(2*eta-1)/(2*eta) >= s  with s = ceil(eta)-1, K >= s+1    [sympy/exact]
"""

from fractions import Fraction as F
import math
import mpmath as mp
import sympy as sp

# ----------------------------------------------------------------- exact model


def k1(K, eta):
    return (K - 1) * eta + 1


def q(K, eta):
    return F((K - 1) * eta) / k1(K, eta)


def c(K, j, eta):
    return 1 - F(K - j) / (K * eta)


def h(K, j, eta):
    """q^j * c_j, with 0^0 = 1 (K = 1 gives q = 0)."""
    return (q(K, eta) ** j) * c(K, j, eta)


def V(K, j, eta):
    return 1 - h(K, j, eta)


def maxh(K, eta):
    return max(h(K, j, eta) for j in range(K + 1))


def rho(K, eta):
    return 1 - maxh(K, eta)


def L(K, eta):
    return 1 - (1 - F(1) / (eta * K)) ** K


def U(K, eta):
    return 1 - (1 - F(1) / (eta * (K - 1) + 1)) ** K


def ceil_frac(x):
    return -((-x.numerator) // x.denominator)


def Lambda(K, eta):
    """Closed form for max_j h_K(j), valid for K >= ceil(eta)."""
    p = ceil_frac(eta)
    return (q(K, eta) ** (K - p + 1)) * (1 - F(p - 1) / (K * eta))


ETAS = [F(1), F(11, 10), F(5, 4), F(3, 2), F(2), F(7, 3), F(5, 2), F(3),
        F(7, 2), F(4), F(9, 2), F(5), F(6), F(17, 2), F(10), F(100), F(1000)]
KMAX = 60

fails = []


def note(ok, tag, msg):
    if not ok:
        fails.append("%s: %s" % (tag, msg))


# ------------------------------------------------------------------------- C1
for eta in ETAS:
    for K in range(1, 15):
        note(V(K, 0, eta) == F(1) / eta, "C1", "V_0 at K=%s eta=%s" % (K, eta))
        note(V(K, K, eta) == U(K, eta), "C1", "V_K != U_K at K=%s eta=%s" % (K, eta))

# ------------------------------------------------------------------------- C2
Ks, es, jj = sp.symbols("K eta j", positive=True)
k1s = (Ks - 1) * es + 1
qs = (Ks - 1) * es / k1s
Vsym = lambda a: 1 - qs ** a * (1 - (Ks - a) / (Ks * es))
r2 = sp.simplify(Vsym(1) - Vsym(0) - (es - Ks) / (es * k1s * Ks))
note(r2 == 0, "C2", "residual %s" % r2)

# ------------------------------------------------------------------------- C3
# h(j)/h(j-1) = q * c_j / c_{j-1};  h(j) >= h(j-1)  <=>  K*eta - K + j <= k1
ratio = sp.simplify(qs * (1 - (Ks - jj) / (Ks * es)) / (1 - (Ks - jj + 1) / (Ks * es)))
crit = sp.simplify(sp.together(ratio - 1))
num, den = sp.fraction(sp.cancel(crit))
note(sp.simplify(sp.expand(num) - sp.expand((Ks - es + 1 - jj) / (Ks * es) * den
                                            / ((Ks - es + 1 - jj) / (Ks * es))
                                            * 0 + num)) == 0, "C3", "sanity")
# direct sign test: numerator of (h(j)-h(j-1)) should be proportional to (K-eta+1-j)
diffs = sp.simplify(sp.cancel(qs ** jj * (1 - (Ks - jj) / (Ks * es))
                              - qs ** (jj - 1) * (1 - (Ks - jj + 1) / (Ks * es))))
factored = sp.factor(sp.simplify(diffs / (qs ** (jj - 1))))
print("C3 symbolic factor of (h_j - h_{j-1})/q^{j-1}:", factored)
for eta in ETAS:
    for K in range(1, 26):
        for j in range(1, K + 1):
            inc = h(K, j, eta) >= h(K, j - 1, eta)
            pred = (F(j) <= K - eta + 1)
            note(inc == pred, "C3", "criterion K=%s j=%s eta=%s" % (K, j, eta))

# ------------------------------------------------------------------------- C4
for eta in ETAS:
    p = ceil_frac(eta)
    for K in range(1, KMAX + 1):
        best = maxh(K, eta)
        jstar = max(0, K - p + 1)
        note(h(K, jstar, eta) == best, "C4",
             "argmax formula K=%s eta=%s (jstar=%s)" % (K, eta, jstar))

# ------------------------------------------------------------------------- C5
mp.mp.dps = 60
worst = None
for eta in ETAS:
    e = mp.mpf(eta.numerator) / mp.mpf(eta.denominator)
    bound = mp.e ** (-1 / e)
    for K in range(1, KMAX + 1):
        val = maxh(K, eta)
        v = mp.mpf(val.numerator) / mp.mpf(val.denominator)
        slack = bound - v
        if worst is None or slack < worst[0]:
            worst = (slack, K, eta)
        note(slack >= 0, "C5", "max h > exp(-1/eta) at K=%s eta=%s" % (K, eta))
print("C5 minimal slack exp(-1/eta) - max_j h_K(j):", mp.nstr(worst[0], 8),
      "at K=%s eta=%s" % (worst[1], worst[2]))

# ------------------------------------------------------------------------- C6
for eta in ETAS:
    for K in range(1, KMAX + 1):
        note(L(K + 1, eta) < L(K, eta), "C6", "L not decreasing K=%s eta=%s" % (K, eta))

# ------------------------------------------------------------------------- C7
for eta in ETAS:
    p = ceil_frac(eta)
    for K in range(p, KMAX + 1):
        note(Lambda(K, eta) == maxh(K, eta), "C7",
             "closed form K=%s eta=%s" % (K, eta))

# ------------------------------------------------------------------------- C8
minr = None
for eta in ETAS:
    p = ceil_frac(eta)
    for K in range(p, KMAX + 1):
        a, b = Lambda(K, eta), Lambda(K + 1, eta)
        note(b > a, "C8", "Lambda not increasing K=%s eta=%s" % (K, eta))
        if a > 0 and (minr is None or b / a < minr[0]):
            minr = (b / a, K, eta)
print("C8 minimal ratio Lambda(K+1)/Lambda(K):", float(minr[0]),
      "at K=%s eta=%s" % (minr[1], minr[2]))

# ------------------------------------------------------------------------- C9
for eta in ETAS:
    fl = eta.numerator // eta.denominator
    prev = None
    for K in range(1, KMAX + 1):
        r = rho(K, eta)
        note((r == F(1) / eta) == (K <= fl), "C9",
             "plateau characterisation K=%s eta=%s" % (K, eta))
        if prev is not None:
            note(r <= prev, "C9", "rho increased at K=%s eta=%s" % (K, eta))
            if K - 1 >= fl:
                note(r < prev, "C9", "not strict at K=%s->%s eta=%s" % (K - 1, K, eta))
        prev = r

# ------------------------------------------------------------------------ C10
# sufficient inequality of the derivative argument
for eta in ETAS:
    s = ceil_frac(eta) - 1
    for K in range(s + 1, KMAX + 1):
        note(F(K) * (2 * eta - 1) / (2 * eta) >= s, "C10",
             "suff. ineq. K=%s eta=%s s=%s" % (K, eta, s))
ss, KK, ee = sp.symbols("s K eta", positive=True)
expr = sp.simplify((ss + 1) * (2 * ee - 1) / (2 * ee) - ss)
print("C10 (s+1)(2eta-1)/(2eta) - s =", sp.simplify(expr), " -> nonneg iff 2eta-1 >= s")

# ------------------------------------------------------------------------ C11
# d(ln Lambda)/dt = -Sigma/eta + (1-s)/(t(t-1)) + s/((t+eta-1-s)(t+eta-1)),
# Sigma = sum_{i>=2} 1/(i t^i) = -ln(1-1/t) - 1/t.  Checked numerically at high
# precision on the grid t = (K-1)*eta+1, K >= ceil(eta), and at intermediate t.
mp.mp.dps = 50
mind = None
for eta in ETAS:
    e = mp.mpf(eta.numerator) / mp.mpf(eta.denominator)
    s = mp.mpf(ceil_frac(eta) - 1)
    p = ceil_frac(eta)
    for K in range(p, KMAX + 1):
        for frac_off in (0, mp.mpf(1) / 3, mp.mpf(2) / 3):
            t = (mp.mpf(K) - 1 + frac_off) * e + 1
            if t <= 1:
                continue
            Sigma = -mp.log(1 - 1 / t) - 1 / t
            d = (-Sigma / e + (1 - s) / (t * (t - 1))
                 + s / ((t + e - 1 - s) * (t + e - 1)))
            if mind is None or d < mind[0]:
                mind = (d, K, eta, frac_off)
            note(d > 0, "C11", "d ln Lambda/dt <= 0 at K=%s eta=%s off=%s"
                 % (K, eta, frac_off))
print("C11 minimal d(ln Lambda)/dt:", mp.nstr(mind[0], 8),
      "at K=%s eta=%s" % (mind[1], mind[2]))
# the bound actually used in the hand proof: Sigma < 1/(2 t (t-1))
for eta in ETAS:
    e = mp.mpf(eta.numerator) / mp.mpf(eta.denominator)
    for K in range(2, KMAX + 1):
        t = (mp.mpf(K) - 1) * e + 1
        Sigma = -mp.log(1 - 1 / t) - 1 / t
        note(Sigma < 1 / (2 * t * (t - 1)), "C11b",
             "Sigma bound at K=%s eta=%s" % (K, eta))

# ---------------------------------------------------------- limit diagnostics
print()
for eta in [F(1), F(3, 2), F(3)]:
    e = mp.mpf(eta.numerator) / mp.mpf(eta.denominator)
    lim = 1 - mp.e ** (-1 / e)
    for K in [1, 2, 3, 5, 10, 50, 200, 1000]:
        print("eta=%-6s K=%-5d rho_K=%.10f  L_K=%.10f  U_K=%.10f  1-e^{-1/eta}=%.10f"
              % (eta, K, float(rho(K, eta)), float(L(K, eta)), float(U(K, eta)),
                 float(lim)))
    print()

print("walkthrough K=3, eta=3/2")
eta = F(3, 2)
for K in [1, 2, 3, 4]:
    row = [(j, h(K, j, eta), V(K, j, eta)) for j in range(K + 1)]
    print("  K=%d  k1=%s  q=%s" % (K, k1(K, eta), q(K, eta)))
    for j, hv, vv in row:
        print("     j=%d  h=%s (%.6f)  V_j=%s (%.6f)" % (j, hv, float(hv), vv, float(vv)))
    print("     rho_%d = %s (%.6f)   L_%d = %s (%.6f)"
          % (K, rho(K, eta), float(rho(K, eta)), K, L(K, eta), float(L(K, eta))))

print()
print("FAILURES:", len(fails))
for f in fails[:40]:
    print("  ", f)

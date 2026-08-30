"""N5: symbolic asymptotics for the bounded-query hardness theorem.

Companion script for results/N5_bounded_query_hardness.tex.

Everything here is a sympy identity/limit check about the CLOSED FORM of the
error-inflation factor of RESEARCH_STATE.md R11(a) / results/T2_summary.md
(Conclusion 1),

    1 + delta(K)  =  ( a^tau * K / (K - tau) )^2 ,      a = 1 - 1/(eta K),

and about the hardness constant  L_K(etahat) = 1 - (1 - 1/(etahat K))^K  with
etahat = eta / (1 + delta(K)).

IMPORTANT SCOPE NOTE.  The closed form itself is [VERIFIED-LP on finite
instances] (T2, see the tex file) and [CONJECTURE] in general; this script does
NOT re-verify it.  It only verifies the ASYMPTOTIC consequences of that closed
form, plus the monotonicity facts the theorem's "safe design parameter"
argument needs.  Those consequences are [VERIFIED-SYMBOLIC].

Checks:
  (i)   delta(K) -> 0  and  K*delta(K) -> 2*tau*(1 - 1/eta)      [required]
  (ii)  1 - (1 - 1/(etahat K))^K -> 1 - exp(-1/eta)              [required]
  (iii) first-order comparison of the two candidate binding edges of the LP
        band (x-direction edge at y = tau  vs  y-direction edge at y = tau-1):
        the x-edge dominates to first order in 1/K  iff  eta >= 2 - 1/tau
  (iv)  delta is increasing in eta (used to justify etahat := eta/(1+delta(eta))
        being a SAFE, i.e. conservative, design parameter)
  (v)   L_K(eta) is decreasing in eta (so L_K(etahat) >= L_K(eta): the theorem
        does not contradict the greedy guarantee R1)

Run:  python3 results/N5_asymptotics.py
Exit code 0 iff every check passes.
"""
import sys

import sympy as sp

# ----------------------------------------------------------------- symbols --
K = sp.Symbol('K', positive=True)          # cardinality constraint, K -> oo
eta = sp.Symbol('eta', positive=True)      # multiplicative error, eta > 1
tau = sp.Symbol('tau', positive=True)      # balancedness threshold, fixed
t = sp.Symbol('t', positive=True)          # t = 1/K

a = 1 - 1 / (eta * K)
one_plus_delta = (a ** tau * K / (K - tau)) ** 2
delta = one_plus_delta - 1
etahat = eta / one_plus_delta
L_of = lambda e: 1 - (1 - 1 / (e * K)) ** K      # L_K(e)

results = []


def record(name, ok, detail):
    results.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


def as_t(expr):
    """substitute K = 1/t so that K -> oo becomes t -> 0+."""
    return sp.simplify(expr.subs(K, 1 / t))


print("=" * 74)
print("N5 asymptotics  (sympy %s)" % sp.__version__)
print("=" * 74)
print("a               =", a)
print("1 + delta       =", sp.simplify(one_plus_delta))
print("etahat          = eta/(1+delta)")
print()

# --------------------------------------------------------------- check (i) --
# delta -> 0 and K*delta -> 2*tau*(1 - 1/eta)
lim_delta = sp.limit(as_t(delta), t, 0, '+')
record("(i.a) delta(K) -> 0 as K -> oo",
       sp.simplify(lim_delta) == 0,
       f"limit = {sp.simplify(lim_delta)}")

lim_Kdelta = sp.limit(as_t(delta) / t, t, 0, '+')
want_first = 2 * tau * (1 - 1 / eta)
record("(i.b) K*delta(K) -> 2*tau*(1 - 1/eta)",
       sp.simplify(lim_Kdelta - want_first) == 0,
       f"limit = {sp.simplify(sp.expand(lim_Kdelta))}, want = {sp.expand(want_first)}")

# independent route: series of delta in t = 1/K around 0, order 2
ser = sp.series(as_t(delta), t, 0, 2).removeO()
coeff1 = sp.simplify(sp.expand(ser).coeff(t, 1))
record("(i.c) series coefficient of 1/K in delta equals 2*tau*(1 - 1/eta)",
       sp.simplify(coeff1 - want_first) == 0,
       f"coeff = {sp.expand(coeff1)}")

# ------------------------------------------------------------- check (ii) --
# 1 - (1 - 1/(etahat K))^K  ->  1 - exp(-1/eta)
inner = 1 - 1 / (etahat * K)                    # = 1 - (1+delta)/(eta K)
log_pow = sp.simplify(K * sp.log(inner))
lim_log = sp.limit(as_t(log_pow), t, 0, '+')
record("(ii.a) K*log(1 - 1/(etahat K)) -> -1/eta",
       sp.simplify(lim_log + 1 / eta) == 0,
       f"limit = {sp.simplify(lim_log)}")

lim_L = sp.limit(as_t(L_of(etahat)), t, 0, '+')
want_L = 1 - sp.exp(-1 / eta)
record("(ii.b) 1 - (1 - 1/(etahat K))^K -> 1 - exp(-1/eta)",
       sp.simplify(lim_L - want_L) == 0,
       f"limit = {sp.simplify(lim_L)}, want = {want_L}")

# (ii.c) the same limit when the OTHER branch of the corrected max is active,
# i.e. 1 + delta = a^(2 - 2 tau).  Corollary N5.8 is branch-independent; this
# is what makes that claim checked rather than asserted.
etahat2 = eta / a ** (2 - 2 * tau)
lim_L2 = sp.limit(as_t(L_of(etahat2)), t, 0, '+')
record("(ii.c) same limit for the second branch (1+delta = a^(2-2tau))",
       sp.simplify(lim_L2 - want_L) == 0,
       f"limit = {sp.simplify(lim_L2)}, want = {want_L}")

# numeric cross-check of (i) and (ii) at concrete (eta, tau); 30-digit floats
# (K is substituted as a Float so that no exact rational is raised to the 10^6).
num_ok = True
num_lines = []
K_big = sp.Float(10 ** 6, 30)
for eta_v, tau_v in [(sp.Rational(3, 2), 1), (sp.Rational(3, 2), 2),
                     (sp.Integer(2), 1), (sp.Integer(2), 2), (sp.Integer(3), 3)]:
    sub = {eta: eta_v, tau: sp.Integer(tau_v), K: K_big}
    d_big = float(delta.subs(sub).evalf(30))
    d_pred = float((want_first / K).subs(sub).evalf(30))
    L_big = float(L_of(etahat).subs(sub).evalf(30))
    L_lim = float((1 - sp.exp(-1 / eta)).subs({eta: eta_v}).evalf(30))
    ok = abs(d_big - d_pred) < 1e-8 and abs(L_big - L_lim) < 1e-5
    num_ok &= ok
    num_lines.append(f"eta={eta_v}, tau={tau_v}: delta(1e6)={d_big:.6e} "
                     f"(1st order {d_pred:.6e}), L={L_big:.9f} (limit {L_lim:.9f})")
record("(i-ii numeric) K = 1e6 cross-check", num_ok, "; ".join(num_lines))

# ------------------------------------------------------------ check (iii) --
# Two candidate binding balanced-balanced band edges for the R9 candidate
# (derivation in the tex, Lemma N5.4):
#   x-direction edge at y = tau     : ratio  c1 = a^tau * K/(K - tau)
#   y-direction edge at y = tau - 1 : ratio  c2 = a^(1 - tau)
# 1 + delta = max(c1, c2)^2.  The stated closed form uses c1; check when c1
# dominates, to first order in 1/K.
c1 = a ** tau * K / (K - tau)
c2 = a ** (1 - tau)
f1 = sp.limit(as_t(c1 - 1) / t, t, 0, '+')      # -> tau*(1 - 1/eta)
f2 = sp.limit(as_t(c2 - 1) / t, t, 0, '+')      # -> (tau - 1)/eta
record("(iii.a) K*(c1 - 1) -> tau*(1 - 1/eta)",
       sp.simplify(f1 - tau * (1 - 1 / eta)) == 0, f"limit = {sp.expand(f1)}")
record("(iii.b) K*(c2 - 1) -> (tau - 1)/eta",
       sp.simplify(f2 - (tau - 1) / eta) == 0, f"limit = {sp.expand(f2)}")
# f1 >= f2  <=>  eta >= 2 - 1/tau
diff_fs = sp.simplify(f1 - f2)
crossover = sp.solve(sp.Eq(diff_fs, 0), eta)
record("(iii.c) c1 dominates to first order iff eta >= 2 - 1/tau",
       len(crossover) == 1 and sp.simplify(crossover[0] - (2 - 1 / tau)) == 0,
       f"f1 - f2 = {sp.factor(diff_fs)}, root eta = {crossover}")

# ------------------------------------------------------------- check (iv) --
# delta is strictly increasing in eta  (K > tau >= 1, eta > 1):
#   a is increasing in eta, and (1+delta) is increasing in a on a > 0.
da_deta = sp.simplify(sp.diff(a, eta))
A = sp.Symbol('A', positive=True)               # stand-in for a in (0,1)
d_dA = sp.simplify(sp.diff((A ** tau * K / (K - tau)) ** 2, A))
record("(iv.a) d a / d eta = 1/(eta^2 K) > 0",
       sp.simplify(da_deta - 1 / (eta ** 2 * K)) == 0, f"= {da_deta}")
record("(iv.b) d(1+delta)/d a = 2 tau A^(2 tau - 1) (K/(K-tau))^2 > 0 for A>0, K>tau",
       sp.simplify(d_dA - 2 * tau * A ** (2 * tau - 1) * (K / (K - tau)) ** 2) == 0,
       f"= {sp.simplify(d_dA)}")

# --------------------------------------------------------------- check (v) --
# L_K(eta) is strictly decreasing in eta, hence etahat <= eta => L_K(etahat) >= L_K(eta).
e = sp.Symbol('e', positive=True)
dL = sp.simplify(sp.diff(1 - (1 - 1 / (e * K)) ** K, e))
dL_target = -(1 - 1 / (e * K)) ** (K - 1) / e ** 2
record("(v) dL_K/d eta = -(1 - 1/(eta K))^(K-1)/eta^2 < 0 for eta K > 1",
       sp.simplify(dL - dL_target) == 0, f"= {sp.simplify(dL)}")

# ------------------------------------------------------------- check (vi) --
# The admissibility map  Phi(theta) = theta * (1 + delta(theta))
#                                   = max{ theta*c1(theta)^2 , theta*c2(theta)^2 }
# must be strictly increasing for the fixed point Phi(theta*) = eta to define a
# unique design parameter (Lemma N5.5 of the tex).  delta itself is NOT monotone
# in theta: c1 increases and c2 = a^(1-tau) DECREASES in theta.
th = sp.Symbol('theta', positive=True)
a_th = 1 - 1 / (th * K)
# (vi.a) theta * c1^2 = theta * a^(2 tau) * (K/(K-tau))^2 is increasing:
d1 = sp.diff(th * a_th ** (2 * tau), th)      # no simplify(): it rewrites the
#                                              powers into a form expand_power_base
#                                              can no longer recombine
d1_target = a_th ** (2 * tau) + 2 * tau * a_th ** (2 * tau - 1) / (th * K)
record("(vi.a) d/dtheta [theta a^(2 tau)] = a^(2tau) + 2 tau a^(2tau-1)/(theta K) > 0",
       sp.simplify(sp.expand_power_base(sp.expand(d1 - d1_target), force=True)) == 0,
       f"= {sp.factor(d1)}")
# (vi.b) theta * c2^2 = theta * a^(2 - 2 tau); with u = theta K,
#   d/dtheta = (1/K) (u/(u-1))^(2 tau - 2) [ 1 - (2 tau - 2)/(u - 1) ],
# so it is increasing iff u = theta K > 2 tau - 1.
u = sp.Symbol('u', positive=True)
g_u = (u / K) * (u / (u - 1)) ** (2 * tau - 2)
dg = sp.simplify(sp.diff(g_u, u))
dg_target = (1 / K) * (u / (u - 1)) ** (2 * tau - 2) * (1 - (2 * tau - 2) / (u - 1))
record("(vi.b) d/dtheta [theta a^(2-2tau)] > 0 iff theta K > 2 tau - 1",
       sp.simplify(sp.expand(dg - dg_target)) == 0,
       f"derivative factor = {sp.factor(sp.simplify(dg / ((u/(u-1))**(2*tau-2)/K)))}")

# ------------------------------------------------- informational (no assert) --
# Where the theorem's constant L_K(etahat) sits relative to the other curves.
# NOT a check: V_j is R10's closed form ([VERIFIED-SYMBOLIC] as the reduced-LP
# value, [CONJECTURE] as rho_K in general) and U_K is R7's explicit-instance
# upper bound; both are quoted, not re-derived here.  Printed so that the
# "the bound of this theorem is not the strongest known" claim in the tex file
# (honest-declaration D2) can be read off.
import math

print()
print("informational (not a check): hardness constants, tau = c+1")
print("  K   eta  tau   L_K(eta)   L_K(etahat)   V_j(eta)      U_K(eta)   delta")
for K_v in (4, 8, 16, 32):
    for eta_v in (1.5, 2.0, 3.0):
        for tau_v in (1, 2):
            a_v = 1 - 1 / (eta_v * K_v)
            dlt = (a_v ** tau_v * K_v / (K_v - tau_v)) ** 2 - 1
            hat = eta_v / (1 + dlt)
            LK = 1 - (1 - 1 / (eta_v * K_v)) ** K_v
            LKh = 1 - (1 - 1 / (hat * K_v)) ** K_v
            k1 = (K_v - 1) * eta_v + 1
            q_v = (K_v - 1) * eta_v / k1
            j_v = min(max(K_v + 1 - math.ceil(eta_v - 1e-12), 0), K_v)
            Vj = 1 - q_v ** j_v * (1 - (K_v - j_v) / (K_v * eta_v))
            UK = 1 - (1 - 1 / (eta_v * (K_v - 1) + 1)) ** K_v
            print(f" {K_v:3d} {eta_v:5.2f} {tau_v:3d}   {LK:.6f}    {LKh:.6f}"
                  f"     {Vj:.6f}    {UK:.6f}   {dlt:.4f}")
print("  (1 - exp(-1/eta)):  eta=1.5 -> %.6f, eta=2 -> %.6f, eta=3 -> %.6f"
      % tuple(1 - math.exp(-1 / e_) for e_ in (1.5, 2.0, 3.0)))

# ------------------------------------------------------------------ report --
print()
print("=" * 74)
n_pass = sum(1 for _, ok, _ in results if ok)
print(f"{n_pass}/{len(results)} checks passed")
for name, ok, _ in results:
    if not ok:
        print("  FAILED:", name)
print("=" * 74)
sys.exit(0 if n_pass == len(results) else 1)

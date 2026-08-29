#!/usr/bin/env python3
"""T5: symbolic (sympy) verification of the explicit instance family U_K (RESEARCH_STATE.md R7).

Instance: ground set B u O, |B|=|O|=K, x=|S n B|, y=|S n O|, ahat>1, a = 1 - 1/(ahat*K):
    f(S)      = F(x,y) = 1 - a^x (1 - y/K)
    ftilde(S) = G(x,0) = 1 - a^x
              = G(x,y) = 1 - a^x + a^x[(1-a) + (y-1) a/(K-1)]   (1 <= y <= K)

Claims verified (numbering follows the T5 task list in TASKS.md):
  1. four single-element ratio classes (pred/true):
       Dx at y=0: 1; Dx at y>=1: aK/(K-1); Dy at y=0: 1/ahat; Dy at y>=1: aK/(K-1)
  2. F monotone + submodular (all four second differences <= 0)
  3. G(x,K) = 1 for all x (finite-error boundary)
  4. tie identity on the greedy path: DxG(t,0) = DyG(t,0)
  5. eta = eta_u*eta_o = ahat*aK/(K-1) = (ahat*K-1)/(K-1); solving ahat from eta and
     substituting back gives greedy ratio 1 - a^K = U_K(eta) = 1-(1-1/(eta(K-1)+1))^K
  plus (part of R7): all-pairs eta_u = ahat, eta_o = aK/(K-1) via exhaustive branch-case
  closed forms; finiteness (d=0 => dtilde=0); path error = ahat; OPT = 1.

Two verification tiers:
  [GEN]  general K symbolic.  Key trick: every quantity depends on x only through
         p := a^x > 0 and on dx only through Q := a^dx in (0,1] (a in (0,1), dx >= 0
         integer -- this parametrization step is the only, trivially faithful, hand
         step).  With (p, Q, y, dy, K, t) as free symbols there are no symbolic
         exponents and every claim is a rational-function identity; sign claims are
         proved by substituting nonnegative "atom" symbols (w = K-y >= 0,
         sigma = 1-Q >= 0, zeta = dy-1 >= 0, u = K-1 > 0) and letting sympy's
         assumption engine certify nonnegativity of the resulting expression.
         The two general-K claims that additionally need a (trivial) discrete
         induction on top of verified identities are flagged GEN+IND below:
           - greedy trajectory stays at y=0 (induction on the tie identity, item 4)
           - x/dx-range faithfulness of p, Q as above.
  [CONC] exhaustive lattice verification for concrete K = 2..8, exact in the symbol
         t = ahat - 1 > 0 (a = 1 - 1/((1+t)K) is rational in t): every single-element
         move, every second difference, the full greedy simulation with symbolic tie
         comparison, path error, OPT, and ALL pairs (A,B) via (x,y,dx,dy) counts
         (f, ftilde depend on counts only, so this covers the full 2^{2K} lattice).
         Sign certificates: polynomial-coefficient check in t, with an exact
         Sturm/real_roots fallback.  No numerics anywhere.

Exit code 0 iff every check passes.  Run:  python3 results/T5_symbolic.py
Output copy: results/T5_symbolic.txt ; JSON summary: results/T5_symbolic.json
"""
import json
import os
import sys
import time

import sympy as sp

T0 = time.time()
RESULTS = []  # (tier, name, ok, note)


def record(tier, name, ok, note=""):
    ok = bool(ok)
    RESULTS.append((tier, name, ok, note))
    line = f"[{'PASS' if ok else 'FAIL'}] [{tier}] {name}"
    if note:
        line += f"  -- {note}"
    print(line, flush=True)


def is_zero(expr):
    """Exact symbolic zero test."""
    e = sp.cancel(sp.together(sp.expand(expr)))
    if e == 0:
        return True
    e = sp.simplify(e)
    return e == 0


def nonneg_atoms(expr):
    """Certify expr >= 0 given the sympy assumptions on its free symbols."""
    e = sp.cancel(sp.together(sp.expand(expr)))
    r = e.is_nonnegative
    if r is not None:
        return r
    r = sp.factor(e).is_nonnegative
    if r is not None:
        return r
    # fallback: numerator/denominator polynomial coefficient certificate
    n, d = sp.fraction(sp.together(e))
    gens = sorted(e.free_symbols, key=str)
    try:
        pn = sp.Poly(sp.expand(n), *gens)
        pd = sp.Poly(sp.expand(d), *gens)
    except sp.PolynomialError:
        return None
    num_ok = all(c >= 0 for c in pn.coeffs())
    den_ok = all(c >= 0 for c in pd.coeffs())
    return num_ok and den_ok


# ============================================================================
# Tier [GEN]: general K
# ============================================================================
print("=" * 78)
print("Tier [GEN]: general-K symbolic verification")
print("=" * 78)

t = sp.Symbol('t', positive=True)          # t = ahat - 1 > 0
ah = 1 + t                                 # ahat
K = sp.Symbol('K', positive=True)          # formal in identities
u = sp.Symbol('u', positive=True)          # u = K - 1 > 0   (K >= 2 integer => u >= 1)
y = sp.Symbol('y')                         # formal
dy = sp.Symbol('dy')                       # formal
p = sp.Symbol('p', positive=True)          # p = a^x > 0        (x >= 0, a in (0,1))
Q = sp.Symbol('Q', positive=True)          # Q = a^dx in (0,1]  (dx >= 0)
sig = sp.Symbol('sigma', nonnegative=True) # sigma = 1 - Q >= 0
w = sp.Symbol('w', nonnegative=True)       # w = K - y >= 0
z = sp.Symbol('zeta', nonnegative=True)    # zeta = dy - 1 >= 0

a = 1 - 1/(ah*K)
Fp = lambda P, Y: 1 - P*(1 - Y/K)                       # F with P = a^x
G0p = lambda P: 1 - P                                   # G, y = 0 branch
G1p = lambda P, Y: 1 - P + P*((1-a) + (Y-1)*a/(K-1))    # G, 1 <= y <= K branch
R = a*K/(K-1)                                           # the eta_o ratio class

# --- basic well-definedness of a --------------------------------------------
record("GEN", "0a: 1 - a = 1/(ahat*K) > 0  (a < 1)",
       is_zero((1-a) - 1/(ah*K)) and nonneg_atoms((1/(ah*K)).subs(K, u+1)))
num_a = sp.expand(((ah*K - 1)).subs(K, u+1))            # = t + u + t*u > 0
record("GEN", "0b: a = (ahat*K-1)/(ahat*K) > 0",
       is_zero(a - (ah*K-1)/(ah*K)) and nonneg_atoms(num_a))
record("GEN", "0c: ahat - 1 = t > 0  (ahat > 1)", nonneg_atoms(t))

# --- closed form of the y>=1 branch of G ------------------------------------
record("GEN", "0d: G(x,y) = 1 - a^{x+1}(K-y)/(K-1) for y>=1 (closed form)",
       is_zero(G1p(p, y) - (1 - a*p*(K-y)/(K-1))))

# --- item 1: four single-element ratio classes ------------------------------
DxF = Fp(a*p, y) - Fp(p, y)          # Dx F(x,y);  x -> x+1  <=>  p -> a*p
DyF = Fp(p, y+1) - Fp(p, y)          # Dy F(x,y)
DxG0 = G0p(a*p) - G0p(p)             # Dx G(x,0)
DxG1 = G1p(a*p, y) - G1p(p, y)       # Dx G(x,y), y>=1
DyG0 = G1p(p, 1) - G0p(p)            # Dy G(x,0) = G(x,1)-G(x,0), crosses branches
DyG1 = G1p(p, y+1) - G1p(p, y)       # Dy G(x,y), y>=1

record("GEN", "1a: DxG(x,0)  = 1        * DxF(x,0)", is_zero(DxG0 - DxF.subs(y, 0)))
record("GEN", "1b: DxG(x,y)  = aK/(K-1) * DxF(x,y)  for 1<=y<=K", is_zero(DxG1 - R*DxF))
record("GEN", "1c: DyG(x,0)  = (1/ahat) * DyF(x,0)", is_zero(DyG0 - DyF/ah))
record("GEN", "1d: DyG(x,y)  = aK/(K-1) * DyF(x,y)  for 1<=y<=K-1", is_zero(DyG1 - R*DyF))
record("GEN", "1e: DxF(x,K) = 0 = DxG(x,K)  (only zero-gain direction; finiteness)",
       is_zero(DxF.subs(y, K)) and is_zero(DxG1.subs(y, K)))
# extremality of the ratio set {1, 1/ahat, aK/(K-1)}
record("GEN", "1f: aK/(K-1) - 1 = t/((1+t)(K-1)) > 0  (so R > 1 > 1/ahat)",
       is_zero(R - 1 - t/((1+t)*(K-1))) and nonneg_atoms(t/((1+t)*u)))
record("GEN", "1g: 1 - 1/ahat = t/(1+t) > 0", is_zero(1 - 1/ah - t/(1+t)) and nonneg_atoms(t/(1+t)))
# hence single-element eta_u = max{1, ahat, (K-1)/(aK)} = ahat  (attained by 1c),
#       single-element eta_o = max{1, 1/ahat, aK/(K-1)} = aK/(K-1) (attained by 1b/1d).

# --- item 2: monotonicity + submodularity of F ------------------------------
record("GEN", "2a: DxF = p(1-a)(K-y)/K = p w /(ahat K^2) >= 0",
       is_zero(DxF - p*(1-a)*(K-y)/K)
       and nonneg_atoms((p*(1-a)*(K-y)/K).subs([(y, K-w), (K, u+1)])))
record("GEN", "2b: DyF = p/K > 0",
       is_zero(DyF - p/K) and nonneg_atoms((p/K).subs(K, u+1)))
Dxx = DxF.subs(p, a*p) - DxF
Dxy = DxF.subs(y, y+1) - DxF
Dyx = DyF.subs(p, a*p) - DyF
Dyy = DyF.subs(y, y+1) - DyF
record("GEN", "2c: DxF(x+1,y)-DxF(x,y) = -p(1-a)^2(K-y)/K <= 0",
       is_zero(Dxx + p*(1-a)**2*(K-y)/K)
       and nonneg_atoms((p*(1-a)**2*(K-y)/K).subs([(y, K-w), (K, u+1)])))
record("GEN", "2d: DxF(x,y+1)-DxF(x,y) = -p(1-a)/K <= 0",
       is_zero(Dxy + p*(1-a)/K) and nonneg_atoms((p*(1-a)/K).subs(K, u+1)))
record("GEN", "2e: DyF(x+1,y)-DyF(x,y) = -p(1-a)/K <= 0",
       is_zero(Dyx + p*(1-a)/K))
record("GEN", "2f: DyF(x,y+1)-DyF(x,y) = 0  (modular in y)", is_zero(Dyy))

# --- item 3: boundary condition ---------------------------------------------
record("GEN", "3:  G(x,K) = 1 for all x", is_zero(G1p(p, K) - 1))

# --- item 4: tie identity on the greedy path --------------------------------
record("GEN", "4:  DxG(t,0) = DyG(t,0)  (= p(1-a); tie -> B picks B at every step)",
       is_zero(DxG0 - DyG0) and is_zero(DxG0 - p*(1-a)))

# --- all-pairs error (part of R7 claims): exhaustive branch cases -----------
# Pair gain: A has counts (x,y); B adds (dx,dy) with (dx,dy) != (0,0).
# a^{x+dx} = p*Q.  Branch cases (y=0 / y>=1) x (dy=0 / dy>=1) are exhaustive.
dA = Fp(p*Q, 0) - Fp(p, 0); gA = G0p(p*Q) - G0p(p)                 # dy=0, y=0 (dx>=1)
dB = Fp(p*Q, y) - Fp(p, y); gB = G1p(p*Q, y) - G1p(p, y)           # dy=0, y>=1 (dx>=1)
dC = Fp(p*Q, y+dy) - Fp(p, y); gC = G1p(p*Q, y+dy) - G1p(p, y)     # dy>=1, y>=1
dD = Fp(p*Q, dy) - Fp(p, 0);   gD = G1p(p*Q, dy) - G0p(p)          # dy>=1, y=0 (crossing)
record("GEN", "P1: pair case dy=0,y=0:   dtilde = d  (= p(1-Q); zero iff dx=0)",
       is_zero(gA - dA) and is_zero(dA - p*(1-Q)))
record("GEN", "P2: pair case dy=0,y>=1:  dtilde = aK/(K-1) * d  (both 0 iff y=K or dx=0)",
       is_zero(gB - R*dB))
record("GEN", "P3: pair case dy>=1,y>=1: dtilde = aK/(K-1) * d",
       is_zero(gC - R*dC))
record("GEN", "P4: pair case dy>=1,y>=1: d = (p/K)[(K-y)(1-Q)+Q dy] > 0 (finiteness ok)",
       is_zero(dC - (p/K)*((K-y)*(1-Q) + Q*dy))
       and nonneg_atoms((p/(u+1))*(w*sig + Q*(z+1))) is True)
record("GEN", "P5: pair case dy>=1,y=0:  d = (p/K)[K(1-Q)+Q dy] > 0",
       is_zero(dD - (p/K)*(K*(1-Q) + Q*dy))
       and nonneg_atoms((p/(u+1))*((u+1)*sig + Q*(z+1))) is True)
# upper bound: R*d - dtilde = p*(R-1) > 0, independent of Q, dy
record("GEN", "P6: pair case dy>=1,y=0:  aK/(K-1)*d - dtilde = p(R-1) > 0",
       is_zero(R*dD - gD - p*(R - 1))
       and nonneg_atoms((p*(R-1)).subs(K, u+1)))
# lower bound: dtilde - d/ahat = p (t/(1+t)) [(K-1)-Q(K-dy)]/(K-1) >= 0
brack = (K-1) - Q*(K-dy)
record("GEN", "P7: pair case dy>=1,y=0:  dtilde - d/ahat = p t/(1+t) * [(K-1)(1-Q)+(dy-1)Q]/(K-1) >= 0",
       is_zero(gD - dD/ah - p*(t/(1+t))*brack/(K-1))
       and is_zero(brack - ((K-1)*(1-Q) + (dy-1)*Q))
       and nonneg_atoms(p*(t/(1+t))*(u*sig + z*Q)/u))
# Assembly (uses 1f, 1g): every pair ratio dtilde/d lies in [1/ahat, aK/(K-1)],
# d = 0 => dtilde = 0, and both endpoints are attained by single elements
# (1c gives d/dtilde = ahat; 1b at y=1<=K-1 gives dtilde/d = aK/(K-1), needs K>=2).
pair_ok = all(ok for (tier, name, ok, _) in RESULTS
              if name.startswith(("P1", "P2", "P3", "P6", "P7", "1b", "1c", "1f", "1g")))
record("GEN", "P8: all-pairs eta_u = ahat, eta_o = aK/(K-1)  (assembled from P1-P7,1b,1c,1f,1g)",
       pair_ok)

# --- item 5: reparametrization ----------------------------------------------
record("GEN", "5a: eta = ahat * aK/(K-1) = (ahat*K - 1)/(K-1)",
       is_zero(ah*R - (ah*K - 1)/(K-1)))
e = sp.Symbol('eta', positive=True)
ah_sol = (e*(K-1) + 1)/K
a_sol = 1 - 1/(ah_sol*K)
record("GEN", "5b: ahat = (eta(K-1)+1)/K inverts eta(ahat)",
       is_zero((ah_sol*K - 1)/(K-1) - e))
record("GEN", "5c: a(eta) = 1 - 1/(eta(K-1)+1)",
       is_zero(a_sol - (1 - 1/(e*(K-1) + 1))))
record("GEN", "5d: greedy ratio 1 - a^K = U_K(eta) = 1 - (1 - 1/(eta(K-1)+1))^K",
       is_zero((1 - a_sol**K) - (1 - (1 - 1/(e*(K-1) + 1))**K)))
record("GEN", "5e: ahat - 1 = (eta-1)(K-1)/K  (ahat>1 <=> eta>1)",
       is_zero(ah_sol - 1 - (e-1)*(K-1)/K))

# --- greedy value, OPT, path error ------------------------------------------
record("GEN", "6a: OPT = 1: F(0,K) = 1 and 1 - F(x,y) = p(K-y)/K >= 0",
       is_zero(Fp(1, K) - 1)
       and is_zero(1 - Fp(p, y) - p*(K-y)/K)
       and nonneg_atoms((p*(K-y)/K).subs([(y, K-w), (K, u+1)])))
record("GEN", "6b: greedy final value F(K,0) = 1 - a^K  [GEN+IND: trajectory y=0 by "
              "induction on tie identity 4; explicit simulation below for K=2..8]",
       is_zero(Fp(a**K, 0) - (1 - a**K)))
# path error: states (tau,0); B-move ratio true/pred = 1 (1a); O-move true/pred = ahat:
record("GEN", "6c: path O-move: DyF(x,0) = ahat * DyG(x,0)  => path eta_u = ahat, "
              "path eta_o = max(1,1/ahat) = 1, path error = ahat",
       is_zero(DyF - ah*DyG0) and nonneg_atoms(t))

# ============================================================================
# Tier [CONC]: exhaustive lattice verification, K = 2..8, exact in t
# ============================================================================
print("=" * 78)
print("Tier [CONC]: exhaustive lattice verification, K = 2..8 (exact in t = ahat-1)")
print("=" * 78)

# Scaled-polynomial representation: with D := K(1+t) and A := K(1+t)-1 we have
# a = A/D, 1-a = 1/D (note D - A = 1).  Every lattice value of F, G times D^M
# (M = K+1) is a polynomial in t with rational coefficients; D^M > 0 for t > 0,
# so sign/zero checks on the scaled polynomials are exact certificates.
#   class aK/(K-1):  g = (aK/(K-1)) d  <=>  (K-1) D g_s = K A d_s   (poly identity)
#   class 1/ahat:    g = d/(1+t)       <=>  (1+t) g_s = d_s
#   d/g <= ahat      <=>  (1+t) g_s - d_s >= 0 on t > 0
#   g/d <= aK/(K-1)  <=>  K A d_s - (K-1) D g_s >= 0 on t > 0

def sign_poly(P):
    """Exact sign of Poly P on t > 0: 0 zero, 1 nonneg, -1 nonpos, None inconclusive."""
    if P.is_zero:
        return 0
    cs = P.all_coeffs()
    if all(c >= 0 for c in cs):
        return 1
    if all(c <= 0 for c in cs):
        return -1
    rr = [r for r in sp.real_roots(P.as_expr()) if r.is_positive]
    if rr:
        return None
    v = P.eval(1)
    return 1 if v > 0 else (-1 if v < 0 else None)


for Kv in range(2, 9):
    tK0 = time.time()
    dom = 'QQ'
    Pt = sp.Poly(1 + t, t, domain=dom)
    Dpol = sp.Poly(Kv*(1 + t), t, domain=dom)        # denominator of a
    Apol = sp.Poly(Kv*(1 + t) - 1, t, domain=dom)    # numerator of a
    M = Kv + 1
    PA = [sp.Poly(1, t, domain=dom)]
    PD = [sp.Poly(1, t, domain=dom)]
    for j in range(1, M + 1):
        PA.append(PA[-1]*Apol)
        PD.append(PD[-1]*Dpol)
    DM = PD[M]

    def Fn(X, Y):
        """F(X,Y) * D^M as Poly."""
        return DM - (PA[X]*PD[M-X]).mul_ground(sp.Rational(Kv - Y, Kv))

    def Gn(X, Y):
        """G(X,Y) * D^M as Poly (original two-branch formula).
        a^x(1-a) D^M = A^x D^{M-x-1};  a^{x+1} D^M = A^{x+1} D^{M-x-1}."""
        if Y == 0:
            return DM - PA[X]*PD[M-X]
        return (DM - PA[X]*PD[M-X] + PA[X]*PD[M-X-1]
                + (PA[X+1]*PD[M-X-1]).mul_ground(sp.Rational(Y - 1, Kv - 1)))

    # -- monotonicity, submodularity, four ratio classes, finiteness ---------
    ok_mono = ok_sub = ok_ratio = ok_fin = True
    for X in range(Kv + 1):
        for Y in range(Kv + 1):
            if X < Kv:
                dxf = Fn(X+1, Y) - Fn(X, Y)
                if sign_poly(dxf) not in (0, 1):
                    ok_mono = False
                dxg = Gn(X+1, Y) - Gn(X, Y)
                if Y == 0:
                    if not (dxg - dxf).is_zero:                      # class ratio 1
                        ok_ratio = False
                else:
                    if not ((Dpol*dxg).mul_ground(Kv - 1)
                            - (Apol*dxf).mul_ground(Kv)).is_zero:    # class aK/(K-1)
                        ok_ratio = False
                if Y == Kv and not (dxf.is_zero and dxg.is_zero):
                    ok_fin = False       # the only zero-gain direction: both vanish
                if Y < Kv and dxf.is_zero:
                    ok_fin = False       # d > 0 expected off the y=K face
            if Y < Kv:
                dyf = Fn(X, Y+1) - Fn(X, Y)
                if sign_poly(dyf) != 1:
                    ok_mono = False
                dyg = Gn(X, Y+1) - Gn(X, Y)
                if Y == 0:
                    if not (Pt*dyg - dyf).is_zero:                   # class 1/ahat
                        ok_ratio = False
                else:
                    if not ((Dpol*dyg).mul_ground(Kv - 1)
                            - (Apol*dyf).mul_ground(Kv)).is_zero:    # class aK/(K-1)
                        ok_ratio = False
            if X < Kv - 1 and sign_poly(Fn(X+2, Y) - Fn(X+1, Y)*2 + Fn(X, Y)) not in (0, -1):
                ok_sub = False
            if X < Kv and Y < Kv and sign_poly(
                    Fn(X+1, Y+1) - Fn(X, Y+1) - Fn(X+1, Y) + Fn(X, Y)) not in (0, -1):
                ok_sub = False
            if Y < Kv - 1 and sign_poly(Fn(X, Y+2) - Fn(X, Y+1)*2 + Fn(X, Y)) not in (0, -1):
                ok_sub = False
    record(f"CONC-K{Kv}", "monotonicity of F on full lattice", ok_mono)
    record(f"CONC-K{Kv}", "submodularity (all second differences <= 0) on full lattice", ok_sub)
    record(f"CONC-K{Kv}", "four ratio classes exact at every lattice move", ok_ratio)
    record(f"CONC-K{Kv}", "finiteness: d=0 <=> dtilde=0 (only on Dx at y=K)", ok_fin)

    # -- G(x,K) = 1 ----------------------------------------------------------
    record(f"CONC-K{Kv}", "G(x,K) = 1 for all x",
           all((Gn(X, Kv) - DM).is_zero for X in range(Kv + 1)))

    # -- all pairs (x,y,dx,dy): eta_u = ahat, eta_o = aK/(K-1) ---------------
    ok_pairs = True
    att_u = att_o = False
    for X in range(Kv + 1):
        for DX in range(Kv + 1 - X):
            for Y in range(Kv + 1):
                for DY in range(Kv + 1 - Y):
                    if DX == 0 and DY == 0:
                        continue
                    d = Fn(X + DX, Y + DY) - Fn(X, Y)
                    g = Gn(X + DX, Y + DY) - Gn(X, Y)
                    if d.is_zero:
                        if not g.is_zero:
                            ok_pairs = False
                        continue
                    eU = Pt*g - d                                  # d/g <= ahat
                    eO = (Apol*d).mul_ground(Kv) \
                        - (Dpol*g).mul_ground(Kv - 1)              # g/d <= aK/(K-1)
                    sU, sO = sign_poly(eU), sign_poly(eO)
                    if sU not in (0, 1):
                        ok_pairs = False
                    if sO not in (0, 1):
                        ok_pairs = False
                    if eU.is_zero:
                        att_u = True
                    if eO.is_zero:
                        att_o = True
    record(f"CONC-K{Kv}", "all-pairs (exhaustive): every ratio in [1/ahat, aK/(K-1)], "
                          "both endpoints attained, d=0 => dtilde=0",
           ok_pairs and att_u and att_o)

    # -- greedy simulation with symbolic tie comparison ----------------------
    ok_tie = ok_pos = True
    for tau in range(Kv):
        gBm = Gn(tau + 1, 0) - Gn(tau, 0)   # predicted gain, add B element
        gOm = Gn(tau, 1) - Gn(tau, 0)       # predicted gain, add O element
        if not (gBm - gOm).is_zero:
            ok_tie = False
        if sign_poly(gBm) != 1:
            ok_pos = False
    record(f"CONC-K{Kv}", "greedy: exact tie at every step on y=0 path "
                          "(tie->B picks all of B), gains > 0", ok_tie and ok_pos)
    # OPT = 1
    ok_opt = (Fn(0, Kv) - DM).is_zero and all(
        sign_poly(DM - Fn(X, Y)) in (0, 1)
        for X in range(Kv + 1) for Y in range(Kv + 1) if X + Y <= Kv)
    record(f"CONC-K{Kv}", "OPT = 1 (F(0,K)=1, F<=1 on |S|<=K)", ok_opt)
    # ratio identity 1 - a^K = U_K(eta) with eta = ahat*aK/(K-1) = (ahat*K-1)/(K-1)
    a_expr = sp.together(1 - sp.Rational(1, Kv)/(1 + t))
    eta_c = sp.Rational(1, Kv - 1)*((1 + t)*Kv - 1)
    UK = 1 - (1 - 1/(eta_c*(Kv - 1) + 1))**Kv
    Rc = sp.cancel(a_expr*Kv/sp.Integer(Kv - 1))
    ok_uk = ((Fn(Kv, 0) - (DM - PA[Kv]*PD[1])).is_zero            # F(K,0) = 1-a^K
             and sp.cancel((1 - a_expr**Kv) - UK) == 0            # 1-a^K = U_K(eta)
             and sp.cancel((1 + t)*Rc - eta_c) == 0)              # eta = ahat*aK/(K-1)
    record(f"CONC-K{Kv}", "greedy ratio F(K,0)/OPT = 1 - a^K = U_K(eta), "
                          "eta = (ahat*K-1)/(K-1)", ok_uk)
    # path error = ahat
    ok_path = True
    for tau in range(Kv):
        dBm = Fn(tau + 1, 0) - Fn(tau, 0); gBm = Gn(tau + 1, 0) - Gn(tau, 0)
        dOm = Fn(tau, 1) - Fn(tau, 0);     gOm = Gn(tau, 1) - Gn(tau, 0)
        if not (dBm - gBm).is_zero:         # B-move ratio 1
            ok_path = False
        if not (dOm - Pt*gOm).is_zero:      # O-move: d = ahat * dtilde
            ok_path = False
    record(f"CONC-K{Kv}", "path error: ratios on path in {1, 1/ahat} exactly => "
                          "eta^path = ahat", ok_path)
    print(f"    [K={Kv} done in {time.time()-tK0:.1f}s]", flush=True)

# ============================================================================
# Summary
# ============================================================================
print("=" * 78)
n_pass = sum(1 for r in RESULTS if r[2])
n_fail = len(RESULTS) - n_pass
gen_fail = [r for r in RESULTS if r[0] == "GEN" and not r[2]]
conc_fail = [r for r in RESULTS if r[0] != "GEN" and not r[2]]
print(f"TOTAL: {n_pass}/{len(RESULTS)} checks passed "
      f"({sum(1 for r in RESULTS if r[0]=='GEN')} general-K, "
      f"{sum(1 for r in RESULTS if r[0]!='GEN')} concrete-K), "
      f"{time.time()-T0:.1f}s")
if n_fail == 0:
    print("ALL PASS")
    print("Verification scope: items 1,2,3,4,5 + all-pairs eta + path error + OPT are")
    print("general-K symbolic ([VERIFIED-SYMBOLIC], via p=a^x, Q=a^dx parametrization);")
    print("the greedy trajectory (y=0 by induction on the tie identity) is verified by")
    print("explicit symbolic simulation for K=2..8 and by the general-K tie identity")
    print("plus a one-line induction for general K.")
else:
    print("SOME CHECKS FAILED:")
    for r in gen_fail + conc_fail:
        print("  FAIL:", r[0], r[1], r[3])

outdir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(outdir, "T5_symbolic.json"), "w") as fh:
    json.dump({"n_pass": n_pass, "n_fail": n_fail,
               "allpairs_exhaustive_K": list(range(2, 9)),
               "checks": [{"tier": r[0], "name": r[1], "ok": r[2], "note": r[3]}
                          for r in RESULTS]}, fh, indent=1)
sys.exit(0 if n_fail == 0 else 1)

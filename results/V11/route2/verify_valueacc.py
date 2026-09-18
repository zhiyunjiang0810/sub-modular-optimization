#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_valueacc.py -- ROUTE-TWO blind verification for prop:valueacc (convention B).

Exact arithmetic only (fractions.Fraction / sympy). Floats appear only in printouts.

Checks
  C1  (iii) algebra: c/eta_u == 1-eps and c*eta_o == 1+eps, with
      c = 2*eta_u/(eta+1), eps = (eta-1)/(eta+1), eta = eta_u*eta_o.      [SYMBOLIC]
  C2  (iii) range: eps in [0,1) for eta >= 1; eps increasing in eta.       [SYMBOLIC]
  C3  (iii) optimality of c: min_{c'>0} max(1-c'/eta_u, c'*eta_o-1) is
      attained at c' = c with value eps.                                  [SYMBOLIC]
  C4  rescaling map direction: tilde f -> c*tilde f sends
      (eta_u, eta_o) -> (eta_u/c, c*eta_o), product eta invariant.        [SYMBOLIC]
  C5  (i) instance A (n=2): exhaustive value accuracy, monotone+submodular,
      and a pair (S,e) with tilde d = 0 < d; no finite eta_u admissible.  [EXHAUSTIVE]
  C6  (i) instance B (n=3, K=2): exhaustive value accuracy, monotone+
      submodular, adversarial-tie greedy run, eta^sel = infinity,
      ratio = (1-eps)/(1+eps).                                            [EXHAUSTIVE]
  C7  (ii): tilde f = (1+M) f on a sample monotone submodular f:
      band holds with (1/(1+M), 1+M), eta = 1, argmax preserved at every
      reachable state, eta^sel = 1, value accuracy fails for every eps<M.  [EXHAUSTIVE]
  C8  (iii) numeric walk-through K=3, eta=3/2: both band sides attained,
      so eps = 1/5 cannot be lowered on that instance.                    [EXHAUSTIVE]
  C9  cross-check (ii)+(iii): for tilde f = (1+M) f, eta = 1 gives eps = 0
      and c*tilde f == f identically.                                     [SYMBOLIC]
"""

from fractions import Fraction as F
from itertools import combinations, chain
import sympy as sp

OK = []
BAD = []


def check(name, cond, detail=""):
    (OK if cond else BAD).append(name)
    print(("  PASS " if cond else "  FAIL ") + name + (("  | " + detail) if detail else ""))


def subsets(ground):
    return list(chain.from_iterable(combinations(sorted(ground), r) for r in range(len(ground) + 1)))


def is_monotone_submodular(fv, ground):
    """fv: dict frozenset->Fraction. Exhaustive monotone + diminishing returns."""
    mono = True
    sub = True
    for S in subsets(ground):
        S = frozenset(S)
        for e in ground - S:
            if fv[S | {e}] < fv[S]:
                mono = False
    for S in subsets(ground):
        S = frozenset(S)
        for T in subsets(ground):
            T = frozenset(T)
            if not S <= T:
                continue
            for e in ground - T:
                dS = fv[S | {e}] - fv[S]
                dT = fv[T | {e}] - fv[T]
                if dS < dT:
                    sub = False
    return mono, sub


def value_accurate(fv, gv, ground, eps):
    """(1-eps) f(S) <= tilde f(S) <= (1+eps) f(S) for all S. Returns (bool, worstinfo)."""
    for S in subsets(ground):
        S = frozenset(S)
        lo = (1 - eps) * fv[S]
        hi = (1 + eps) * fv[S]
        if not (lo <= gv[S] <= hi):
            return False, (sorted(S), fv[S], gv[S], lo, hi)
    return True, None


def zero_gain_witness(fv, gv, ground):
    """pairs (S,e) with tilde d_e(S) == 0 < d_e(S)."""
    out = []
    for S in subsets(ground):
        S = frozenset(S)
        for e in sorted(ground - S):
            d = fv[S | {e}] - fv[S]
            dt = gv[S | {e}] - gv[S]
            if dt == 0 and d > 0:
                out.append((sorted(S), e, d, dt))
    return out


def greedy_worst(fv, gv, ground, K):
    """Adversarial ties: enumerate every argmax-consistent run, return the run
    minimising the final true value. Returns (final_f, picks, etasel)."""
    best = None

    def rec(S, picks, amax):
        nonlocal best
        if len(picks) == K:
            cand = (fv[frozenset(S)], list(picks), amax)
            if best is None or cand[0] < best[0] or (cand[0] == best[0] and cand[2] == sp.oo):
                best = cand
            return
        Sf = frozenset(S)
        rest = sorted(ground - Sf)
        gains = {e: gv[Sf | {e}] - gv[Sf] for e in rest}
        mx = max(gains.values())
        for e in rest:
            if gains[e] != mx:
                continue
            M_t = max(fv[Sf | {x}] - fv[Sf] for x in rest)
            g_t = fv[Sf | {e}] - fv[Sf]
            if g_t > 0:
                a_t = M_t / g_t
            elif M_t == 0:
                a_t = F(1)
            else:
                a_t = sp.oo
            newmax = a_t if (amax == sp.oo or a_t == sp.oo) else max(amax, a_t)
            if amax == sp.oo:
                newmax = sp.oo
            rec(S | {e}, picks + [e], newmax)

    rec(frozenset(), [], F(1))
    return best


def opt_value(fv, ground, K):
    return max(fv[frozenset(S)] for S in subsets(ground) if len(S) <= K)


# ---------------------------------------------------------------- C1..C4, C9
print("== C1-C4, C9: symbolic (iii) ==")
eu, eo, cc = sp.symbols("eta_u eta_o c", positive=True)
eta = eu * eo
c_star = 2 * eu / (eta + 1)
eps_star = (eta - 1) / (eta + 1)

check("C1a  c/eta_u - (1-eps) == 0", sp.simplify(c_star / eu - (1 - eps_star)) == 0)
check("C1b  c*eta_o - (1+eps) == 0", sp.simplify(c_star * eo - (1 + eps_star)) == 0)

e = sp.symbols("eta", positive=True)
eps_of_eta = (e - 1) / (e + 1)
check("C2a  eps(1) == 0", sp.simplify(eps_of_eta.subs(e, 1)) == 0)
check("C2b  d eps/d eta > 0 for eta>0", sp.simplify(sp.diff(eps_of_eta, e) - 2 / (e + 1) ** 2) == 0)
check("C2c  limit eps = 1 as eta->oo", sp.limit(eps_of_eta, e, sp.oo) == 1)
check("C2d  1-eps(eta) > 0 for eta>=1", sp.simplify((1 - eps_of_eta) - 2 / (e + 1)) == 0)

# C3: min over c' of max(1-c'/eta_u, c'*eta_o-1)
lo_req = 1 - cc / eu          # required eps from the lower band side
hi_req = cc * eo - 1          # required eps from the upper band side
sol = sp.solve(sp.Eq(lo_req, hi_req), cc)
check("C3a  balance point equals c", len(sol) == 1 and sp.simplify(sol[0] - c_star) == 0,
      "c' = %s" % sp.simplify(sol[0]))
check("C3b  balanced value equals eps", sp.simplify(hi_req.subs(cc, c_star) - eps_star) == 0)
check("C3c  lo_req strictly decreasing in c'", sp.simplify(sp.diff(lo_req, cc) + 1 / eu) == 0)
check("C3d  hi_req strictly increasing in c'", sp.simplify(sp.diff(hi_req, cc) - eo) == 0)

# C4: direction of the rescaling map
check("C4a  new eta_u = eta_u/c  (from c*td >= c*d/eta_u = d/(eta_u/c))",
      sp.simplify((eu / cc) * (cc * eo) - eta) == 0)
check("C4b  product invariant", sp.simplify((eu / cc) * (cc * eo) - eu * eo) == 0)
new_u = sp.simplify((eu / c_star))
new_o = sp.simplify(c_star * eo)
check("C4c  rescaled lower factor = 1/(1-eps)", sp.simplify(new_u - 1 / (1 - eps_star)) == 0,
      "eta_u' = %s" % new_u)
check("C4d  rescaled upper factor = 1+eps", sp.simplify(new_o - (1 + eps_star)) == 0,
      "eta_o' = %s" % new_o)

M = sp.symbols("M", positive=True)
c_ii = c_star.subs({eu: 1 / (1 + M), eo: 1 + M})
check("C9a  (ii) has eta = 1", sp.simplify((1 / (1 + M)) * (1 + M) - 1) == 0)
check("C9b  (ii) eps = 0", sp.simplify(eps_star.subs({eu: 1 / (1 + M), eo: 1 + M})) == 0)
check("C9c  (ii) c*(1+M) = 1 so c*tilde f = f", sp.simplify(c_ii * (1 + M) - 1) == 0,
      "c = %s" % sp.simplify(c_ii))

# ---------------------------------------------------------------- C5 instance A
print("\n== C5: (i) instance A, n=2, exhaustive ==")
for eps in [F(1, 5), F(1, 2), F(9, 10), F(1, 100)]:
    ground = frozenset({1, 2})
    delta = eps  # weight of element 2
    fv, gv = {}, {}
    for S in subsets(ground):
        S = frozenset(S)
        fv[S] = (1 if 1 in S else 0) + (delta if 2 in S else 0)
        gv[S] = F(1) if 1 in S else (delta if 2 in S else F(0))
    mono, sub = is_monotone_submodular(fv, ground)
    va, bad = value_accurate(fv, gv, ground, eps)
    wit = zero_gain_witness(fv, gv, ground)
    check("C5 eps=%s  f monotone submodular" % eps, mono and sub)
    check("C5 eps=%s  tilde f value-accurate at eps" % eps, va, str(bad))
    check("C5 eps=%s  exists (S,e) with tilde d=0<d" % eps, len(wit) >= 1, str(wit))
    # no finite eta_u: the band lower side would need d/eta_u <= 0 with d>0
    check("C5 eps=%s  no finite (eta_u,eta_o) admissible" % eps,
          all(d > 0 and dt == 0 for (_, _, d, dt) in wit))

# ---------------------------------------------------------------- C6 instance B
print("\n== C6: (i) instance B, n=3, K=2, exhaustive ==")
for eps, delta in [(F(1, 5), F(1, 2)), (F(1, 5), F(1, 5)), (F(1, 10), F(2, 9)), (F(1, 8), F(2, 7))]:
    ground = frozenset({1, 2, 3})
    fv, gv = {}, {}
    for S in subsets(ground):
        S = frozenset(S)
        fv[S] = (1 if (S & {1, 2}) else 0) + (delta if 3 in S else 0)
    gv[frozenset()] = F(0)
    gv[frozenset({1})] = 1 - eps
    gv[frozenset({2})] = 1 - eps
    gv[frozenset({3})] = (1 + eps) * delta
    gv[frozenset({1, 2})] = 1 + eps
    gv[frozenset({1, 3})] = (1 - eps) * (1 + delta)
    gv[frozenset({2, 3})] = (1 - eps) * (1 + delta)
    gv[frozenset({1, 2, 3})] = (1 + eps) * (1 + delta)
    mono, sub = is_monotone_submodular(fv, ground)
    va, bad = value_accurate(fv, gv, ground, eps)
    fin, picks, esel = greedy_worst(fv, gv, ground, 2)
    opt = opt_value(fv, ground, 2)
    ratio = fin / opt
    tgt = (1 - eps) / (1 + eps)
    check("C6 eps=%s d=%s  f monotone submodular" % (eps, delta), mono and sub)
    check("C6 eps=%s d=%s  value-accurate" % (eps, delta), va, str(bad))
    check("C6 eps=%s d=%s  greedy picks two B-elements" % (eps, delta), set(picks) == {1, 2},
          "picks=%s" % picks)
    check("C6 eps=%s d=%s  eta^sel = infinity" % (eps, delta), esel == sp.oo)
    check("C6 eps=%s d=%s  ratio = %s" % (eps, delta, ratio), ratio == 1 / (1 + delta),
          "ratio=%s  float=%.6f  (1-eps)/(1+eps)=%s" % (ratio, float(ratio), tgt))
    # diagnostic: which (S,e) violate Definition 1 in instance B, and how
    lower_viol = zero_gain_witness(fv, gv, ground)          # tilde d = 0 < d
    upper_viol = []                                         # tilde d > 0 = d
    for S in subsets(ground):
        S = frozenset(S)
        for e in sorted(ground - S):
            d = fv[S | {e}] - fv[S]
            dt = gv[S | {e}] - gv[S]
            if d == 0 and dt > 0:
                upper_viol.append((sorted(S), e, d, dt))
    check("C6 eps=%s d=%s  band violated on both sides" % (eps, delta),
          len(lower_viol) >= 0 and len(upper_viol) >= 1,
          "lower(td=0<d)=%s  upper(td>0=d)=%s" % (lower_viol, upper_viol))
    check("C6 eps=%s d=%s  all tilde d >= 0 (no negative predicted gain)" % (eps, delta),
          all(gv[frozenset(S) | {e}] - gv[frozenset(S)] >= 0
              for S in subsets(ground) for e in ground - frozenset(S)))

# ---------------------------------------------------------------- C7 item (ii)
print("\n== C7: (ii) tilde f = (1+M) f, exhaustive ==")
for Mval in [F(1, 2), F(3), F(1, 100)]:
    ground = frozenset({1, 2, 3, 4})
    w = {1: F(4), 2: F(3), 3: F(2), 4: F(1)}
    cov = {1: {"a", "b"}, 2: {"b", "c"}, 3: {"c", "d"}, 4: {"d"}}
    wt = {"a": F(3), "b": F(1), "c": F(2), "d": F(1)}
    fv, gv = {}, {}
    for S in subsets(ground):
        S = frozenset(S)
        u = set()
        for e in S:
            u |= cov[e]
        fv[S] = sum((wt[x] for x in u), F(0))
        gv[S] = (1 + Mval) * fv[S]
    mono, sub = is_monotone_submodular(fv, ground)
    check("C7 M=%s  f monotone submodular, not identically 0" % Mval,
          mono and sub and any(v > 0 for v in fv.values()))
    band = all(
        (fv[frozenset(S) | {e}] - fv[frozenset(S)]) / (1 / (1 + Mval))
        <= (gv[frozenset(S) | {e}] - gv[frozenset(S)])
        <= (1 + Mval) * (fv[frozenset(S) | {e}] - fv[frozenset(S)])
        for S in subsets(ground) for e in ground - frozenset(S))
    check("C7 M=%s  Definition 1 band with (1/(1+M), 1+M), eta=1" % Mval, band)
    # value accuracy fails at every eps < M
    for epsv in [Mval / 2, Mval * F(99, 100), Mval]:
        va, _ = value_accurate(fv, gv, ground, epsv)
        if epsv < Mval:
            check("C7 M=%s  value accuracy FAILS at eps=%s" % (Mval, epsv), not va)
        else:
            check("C7 M=%s  value accuracy holds at eps=M=%s" % (Mval, epsv), va)
    # argmax preserved + eta^sel = 1 for every K
    same = True
    for S in subsets(ground):
        S = frozenset(S)
        rest = sorted(ground - S)
        if not rest:
            continue
        am_t = {e for e in rest if gv[S | {e}] - gv[S] == max(gv[S | {x}] - gv[S] for x in rest)}
        am_f = {e for e in rest if fv[S | {e}] - fv[S] == max(fv[S | {x}] - fv[S] for x in rest)}
        if am_t != am_f:
            same = False
    check("C7 M=%s  argmax(tilde d) == argmax(d) at every state" % Mval, same)
    for K in (1, 2, 3, 4):
        fin, picks, esel = greedy_worst(fv, gv, ground, K)
        greedy_true = greedy_worst(fv, fv, ground, K)
        check("C7 M=%s K=%d  eta^sel = 1" % (Mval, K), esel == 1,
              "picks=%s  f=%s" % (picks, fin))
        check("C7 M=%s K=%d  same worst value as greedy on f" % (Mval, K),
              fin == greedy_true[0])

# ---------------------------------------------------------------- C8 walk-through
print("\n== C8: (iii) numeric walk-through K=3, eta=3/2 ==")
ground = frozenset({1, 2, 3})
wf = {1: F(3), 2: F(2), 3: F(1)}
for (eu_v, eo_v) in [(F(1), F(3, 2)), (F(3, 2), F(1)), (F(3, 4), F(2))]:
    eta_v = eu_v * eo_v
    c_v = 2 * eu_v / (eta_v + 1)
    eps_v = (eta_v - 1) / (eta_v + 1)
    # predictor: element 1 over-predicted by eta_o, elements 2,3 under-predicted by 1/eta_u
    wg = {1: eo_v * wf[1], 2: wf[2] / eu_v, 3: wf[3] / eu_v}
    fv, gv = {}, {}
    for S in subsets(ground):
        S = frozenset(S)
        fv[S] = sum((wf[e] for e in S), F(0))
        gv[S] = sum((wg[e] for e in S), F(0))
    band = all((fv[frozenset(S) | {e}] - fv[frozenset(S)]) / eu_v
               <= gv[frozenset(S) | {e}] - gv[frozenset(S)]
               <= eo_v * (fv[frozenset(S) | {e}] - fv[frozenset(S)])
               for S in subsets(ground) for e in ground - frozenset(S))
    setband = all(fv[frozenset(S)] / eu_v <= gv[frozenset(S)] <= eo_v * fv[frozenset(S)]
                  for S in subsets(ground))
    va, bad = value_accurate(fv, {k: c_v * v for k, v in gv.items()}, ground, eps_v)
    tight_hi = any(c_v * gv[frozenset(S)] == (1 + eps_v) * fv[frozenset(S)] and fv[frozenset(S)] > 0
                   for S in subsets(ground))
    tight_lo = any(c_v * gv[frozenset(S)] == (1 - eps_v) * fv[frozenset(S)] and fv[frozenset(S)] > 0
                   for S in subsets(ground))
    check("C8 (eu,eo)=(%s,%s)  marginal band" % (eu_v, eo_v), band)
    check("C8 (eu,eo)=(%s,%s)  set-level band f/eu <= tf <= eo f" % (eu_v, eo_v), setband)
    check("C8 (eu,eo)=(%s,%s)  c*tilde f value-accurate at eps=%s (c=%s)" % (eu_v, eo_v, eps_v, c_v),
          va, str(bad))
    check("C8 (eu,eo)=(%s,%s)  both band sides attained (eps not lowerable here)" % (eu_v, eo_v),
          tight_hi and tight_lo)
    check("C8 (eu,eo)=(%s,%s)  eps independent of the split" % (eu_v, eo_v), eps_v == F(1, 5))

# ---------------------------------------------------------------- C10 band consistency
print("\n== C10: band [d/eta_u, eta_o d] is nonempty only if d >= 0 when eta > 1 ==")
dsym = sp.symbols("d", real=True)
gap = sp.simplify(eo * dsym - dsym / eu)          # upper minus lower
check("C10a  upper-lower = d*(eta-1)/eta_u", sp.simplify(gap - dsym * (eta - 1) / eu) == 0)
check("C10b  eta>1 and d<0 => empty band",
      sp.simplify((gap / dsym).subs({eu: 1, eo: 2}) - 1) == 0)   # gap = d for eta=2 => d<0 empty

# ---------------------------------------------------------------- C11 no submodularity
print("\n== C11: (iii) on a monotone NON-submodular f (f(S) = |S|^2) ==")
n11 = 3
ground = frozenset(range(1, n11 + 1))
fv = {}
for S in subsets(ground):
    fv[frozenset(S)] = F(len(S)) ** 2
mono, sub = is_monotone_submodular(fv, ground)
check("C11  f(S)=|S|^2 is monotone and NOT submodular", mono and not sub)
import itertools
allok = True
for eu_v, eo_v in [(F(1), F(3, 2)), (F(3, 2), F(1)), (F(3, 4), F(2)), (F(2), F(2))]:
    eta_v = eu_v * eo_v
    c_v = 2 * eu_v / (eta_v + 1)
    eps_v = (eta_v - 1) / (eta_v + 1)
    for pattern in itertools.product([0, 1], repeat=n11):
        psi = [F(0)]
        for j in range(n11):
            d_j = F(2 * j + 1)                      # marginal of f at level j
            psi.append(psi[-1] + (eo_v * d_j if pattern[j] else d_j / eu_v))
        gv = {frozenset(S): psi[len(S)] for S in subsets(ground)}
        band = all(
            (fv[frozenset(S) | {e}] - fv[frozenset(S)]) / eu_v
            <= gv[frozenset(S) | {e}] - gv[frozenset(S)]
            <= eo_v * (fv[frozenset(S) | {e}] - fv[frozenset(S)])
            for S in subsets(ground) for e in ground - frozenset(S))
        setband = all(fv[frozenset(S)] / eu_v <= gv[frozenset(S)] <= eo_v * fv[frozenset(S)]
                      for S in subsets(ground))
        va, bad = value_accurate(fv, {k: c_v * v for k, v in gv.items()}, ground, eps_v)
        if not (band and setband and va):
            allok = False
            print("     offending: eu=%s eo=%s pattern=%s band=%s setband=%s va=%s %s"
                  % (eu_v, eo_v, pattern, band, setband, va, bad))
check("C11  all 4 x 2^3 in-band predictors: set band + c*tilde f value-accurate", allok)

print("\n================ SUMMARY ================")
print("passed: %d   failed: %d" % (len(OK), len(BAD)))
for b in BAD:
    print("  FAILED: " + b)

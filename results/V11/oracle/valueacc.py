#!/usr/bin/env python3
"""V11 Q2 oracle for prop:valueacc (ledger T2, convention-B rewrite of 2026-09-18).

Statement under test (results/V11/inputs/statement_valueacc.md), convention B
of Definition 1: eta_u, eta_o > 0 (no floor at 1), eta = eta_u*eta_o >= 1, and
for all S and e not in S:  d_e(S)/eta_u <= dtilde_e(S) <= eta_o d_e(S).

  (i)   For every eps in (0,1) there are a monotone submodular f and a
        predictor ftilde value-accurate at level eps with dtilde_e(S) = 0 at a
        pair where d_e(S) > 0; hence no finite (eta_u, eta_o) exists.
  (ii)  For every M > 0 and every monotone submodular f not identically zero,
        ftilde = (1+M) f fails value accuracy at every level eps < M, yet
        Definition 1 holds with eta_u = 1/(1+M), eta_o = 1+M, eta = 1, and
        predictive greedy on ftilde picks an element of maximum true gain at
        every state (eta^sel = 1).
  (iii) For any ftilde with error (eta_u, eta_o), eta = eta_u eta_o, and a
        monotone f with f(empty) = ftilde(empty) = 0:
        f(S)/eta_u <= ftilde(S) <= eta_o f(S) for every S, and with
        c = 2 eta_u/(eta+1), eps = (eta-1)/(eta+1) in [0,1) the rescaled
        predictor c*ftilde is value-accurate at level eps.  Submodularity of f
        is not used in (iii).

Route-one proof material read for this oracle (not modified):
  paper/sections/appendix_model_proofs.tex, "Proof of Proposition
    \\ref{prop:valueacc}"  (convention B; the construction checked in C1/C2/C3)
  paper/sections/appendix_proofs.tex, subsection app:valueacc (about line 145;
    old convention, the eta_o < 2 proviso; cross-checked in C1b and C7)
  THEOREM_LEDGER.md section "## T2" (rewritten head)

Criterion C (oracle):
  C1   part (i), the two-element construction at eps in {1/10, 1/2, 9/10},
       exact, plus the padded n = 6 version with 4 zero-gain elements.
  C1b  part (i) of the OLD appendix (app:valueacc), a different two-element
       instance, cross-checked at the same eps values.
  C2   part (ii), sympy in M plus 200 random monotone submodular f with random
       rational M; smallest admissible factors, eta = 1, eta^sel = 1.
  C3   part (iii), sympy identities c/eta_u = 1-eps and c*eta_o = 1+eps.
  C4   part (iii) on >= 2000 random LEGAL surrogates with eta_u, eta_o taken as
       the ACTUAL smallest admissible factors.
  C4b  part (iii) on monotone f that is NOT submodular, which is the statement's
       own claim that submodularity is not used in (iii).
  C5   part (iii) structured cases: eta = 1, very large eta, zero-gain elements.
  C6   scaling invariance of eta and the domain eps in [0,1) (sympy).
  C7   old vs new convention: max{1-1/eta_u, eta_o-1} leaves (0,1) exactly when
       eta_o >= 2, which is why the old statement carried a proviso; rerun of
       the existing repo script results/M1_checks.py.

Criterion D (counterexample search against the statement itself):
  for (iii) the random legal surrogates of C4 ARE the search; for (i) and (ii)
  >= 2000 random draws each of eps and (f, M).  Any violation is reported with
  its exact inequality and parameters.

Every decision uses fractions.Fraction or sympy; floats appear only inside
printed text.  Random seeds are fixed.

Run:  python3 results/V11/oracle/valueacc.py
Exit code 0 iff every check passed.  Writes results/V11/oracle/valueacc.json.
"""

from fractions import Fraction as Fr
import json
import os
import random
import subprocess
import sys
import time

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
JSON_PATH = os.path.join(HERE, "valueacc.json")

SEED_I = 20260918          # criterion D, part (i)
SEED_II = 20260919         # criterion D / C2, part (ii)
SEED_III = 20260920        # criterion D / C4, part (iii)

CHECKS = []
VIOLATIONS = []
SUBPROCS = []
COUNTS = {}
WITNESSES = {}

T0 = time.time()


def check(name, ok, detail="", extra=None):
    rec = {"name": name, "status": "PASS" if ok else "FAIL", "detail": detail}
    if extra:
        rec.update(extra)
    CHECKS.append(rec)
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""))
    if not ok:
        VIOLATIONS.append({"where": name, "detail": detail, **(extra or {})})
    return ok


def note(msg):
    print("      " + msg)


def bits(mask):
    out = []
    i = 0
    while mask:
        if mask & 1:
            out.append(i)
        mask >>= 1
        i += 1
    return out


# ---------------------------------------------------------------------------
# exact set-function predicates.  f is a dict mask -> Fraction on ground set
# {0,...,n-1}; f[0] must be 0.
# ---------------------------------------------------------------------------
def normalized(f):
    return f[0] == 0


def monotone(f, n, counter=None):
    """d_e(S) >= 0 for every S and e not in S."""
    bad = None
    cnt = 0
    for S in range(1 << n):
        for e in range(n):
            if S >> e & 1:
                continue
            cnt += 1
            if f[S | (1 << e)] - f[S] < 0:
                bad = (S, e)
                break
        if bad:
            break
    if counter is not None:
        counter[0] += cnt
    return bad is None, bad


def submodular(f, n, counter=None):
    """Local exchange form: d_e(S + e') <= d_e(S) for all S, e != e' not in S.
    Equivalent to submodularity for set functions."""
    bad = None
    cnt = 0
    for S in range(1 << n):
        for e in range(n):
            if S >> e & 1:
                continue
            de = f[S | (1 << e)] - f[S]
            for e2 in range(n):
                if e2 == e or (S >> e2 & 1):
                    continue
                S2 = S | (1 << e2)
                cnt += 1
                if f[S2 | (1 << e)] - f[S2] > de:
                    bad = (S, e, e2)
                    break
            if bad:
                break
        if bad:
            break
    if counter is not None:
        counter[0] += cnt
    return bad is None, bad


def value_accurate(f, ft, n, eps, counter=None):
    """(1-eps) f(S) <= ft(S) <= (1+eps) f(S) for every S.  Returns (ok, witness,
    min slack, argmin S)."""
    worst = None
    worstS = None
    cnt = 0
    bad = None
    for S in range(1 << n):
        cnt += 1
        lo = (1 - eps) * f[S]
        hi = (1 + eps) * f[S]
        s1 = ft[S] - lo
        s2 = hi - ft[S]
        s = min(s1, s2)
        if worst is None or s < worst:
            worst = s
            worstS = S
        if s < 0 and bad is None:
            bad = (S, str(f[S]), str(ft[S]), str(lo), str(hi))
    if counter is not None:
        counter[0] += cnt
    return bad is None, bad, worst, worstS


def gain_pairs(f, ft, n):
    """Yield (S, e, d, dtilde) for every S and e not in S."""
    for S in range(1 << n):
        for e in range(n):
            if S >> e & 1:
                continue
            Se = S | (1 << e)
            yield S, e, f[Se] - f[S], ft[Se] - ft[S]


def smallest_factors(f, ft, n, counter=None):
    """Smallest admissible (eta_u, eta_o) of convention B, exactly.

    eta_o = max over pairs with d > 0 of dtilde/d,
    eta_u = max over pairs with d > 0 of d/dtilde.
    Returns (ok, eta_u, eta_o, illegal_witness).  ok is False when some pair has
    d > 0 and dtilde <= 0 (no finite eta_u) or d = 0 and dtilde != 0 (the band
    forces dtilde = 0 there)."""
    eu = None
    eo = None
    cnt = 0
    for S, e, d, dt in gain_pairs(f, ft, n):
        cnt += 1
        if d == 0:
            if dt != 0:
                if counter is not None:
                    counter[0] += cnt
                return False, None, None, ("d=0 but dtilde!=0", S, e, str(dt))
            continue
        if dt <= 0:
            if counter is not None:
                counter[0] += cnt
            return False, None, None, ("d>0 but dtilde<=0", S, e, str(d), str(dt))
        r_o = Fr(dt, 1) / d
        r_u = Fr(d, 1) / dt
        if eo is None or r_o > eo:
            eo = r_o
        if eu is None or r_u > eu:
            eu = r_u
    if counter is not None:
        counter[0] += cnt
    if eu is None:
        return False, None, None, ("f identically zero on gains", None, None)
    return True, eu, eo, None


# ---------------------------------------------------------------------------
# C1: part (i), the convention-B two-element construction
# ---------------------------------------------------------------------------
def build_part_i(eps, pad):
    """N = {a, b} + pad zero-gain elements.  a = bit 0, b = bit 1."""
    n = 2 + pad
    core = 0b11
    f = {}
    ft = {}
    for S in range(1 << n):
        c = S & core
        if c == 0:
            f[S] = Fr(0)
            ft[S] = Fr(0)
        elif c == core:
            f[S] = 1 + eps
            ft[S] = Fr(1)
        else:
            f[S] = Fr(1)
            ft[S] = Fr(1)
    return n, f, ft


def run_part_i(eps, pad, label, counters, record=True):
    n, f, ft = build_part_i(eps, pad)
    ok_all = True
    ok = normalized(f) and normalized(ft)
    ok_all &= ok
    m_ok, m_bad = monotone(f, n, counters["mono"])
    s_ok, s_bad = submodular(f, n, counters["sub"])
    ok_all &= m_ok and s_ok
    va_ok, va_bad, slack, slackS = value_accurate(f, ft, n, eps, counters["va"])
    ok_all &= va_ok
    # the witness pair (S, e) = ({a}, b)
    S = 0b01
    d_b = f[0b11] - f[0b01]
    dt_b = ft[0b11] - ft[0b01]
    wit_ok = (dt_b == 0 and d_b > 0)
    ok_all &= wit_ok
    # no finite factors
    leg_ok, eu, eo, bad = smallest_factors(f, ft, n, counters["band"])
    fin_ok = (not leg_ok) and bad is not None and bad[0] == "d>0 but dtilde<=0"
    ok_all &= fin_ok
    # the band forces dtilde = 0 exactly where d = 0
    zero_ok = True
    zero_pairs = 0
    for Sx, e, d, dt in gain_pairs(f, ft, n):
        if d == 0:
            zero_pairs += 1
            if dt != 0:
                zero_ok = False
                break
    ok_all &= zero_ok
    if record:
        detail = ("eps=%s n=%d: normalized+monotone+submodular=%s, "
                  "value-accurate at level eps=%s (min slack %s at S=%d), "
                  "dtilde_b({a})=%s < d_b({a})=%s, no finite eta_u=%s, "
                  "d=0 => dtilde=0 on %d pairs=%s"
                  % (eps, n, m_ok and s_ok, va_ok, slack, slackS,
                     dt_b, d_b, fin_ok, zero_pairs, zero_ok))
        check("C1 " + label, ok_all, detail,
              {"eps": str(eps), "n": n, "pad": pad,
               "d_b_at_a": str(d_b), "dtilde_b_at_a": str(dt_b),
               "value_accuracy_min_slack": str(slack),
               "zero_gain_pairs": zero_pairs})
    return ok_all


def build_part_i_old(eps):
    """The OLD appendix (app:valueacc) part (i) instance, a different one."""
    n = 2
    fa, fb = Fr(1), 2 * eps / (1 - eps)
    fab = (1 + eps) / (1 - eps)
    f = {0: Fr(0), 0b01: fa, 0b10: fb, 0b11: fab}
    ft = {0: Fr(0), 0b01: 1 + eps, 0b10: fb, 0b11: 1 + eps}
    return n, f, ft


def run_part_i_old(eps, counters):
    n, f, ft = build_part_i_old(eps)
    m_ok, _ = monotone(f, n, counters["mono"])
    s_ok, _ = submodular(f, n, counters["sub"])
    modular = (f[0b11] == f[0b01] + f[0b10])
    va_ok, _, slack, slackS = value_accurate(f, ft, n, eps, counters["va"])
    d_b = f[0b11] - f[0b01]
    dt_b = ft[0b11] - ft[0b01]
    wit = (dt_b == 0 and d_b > 0 and d_b == 2 * eps / (1 - eps))
    leg_ok, _, _, bad = smallest_factors(f, ft, n, counters["band"])
    fin_ok = (not leg_ok) and bad[0] == "d>0 but dtilde<=0"
    ok = m_ok and s_ok and modular and va_ok and wit and fin_ok
    return ok, slack, slackS, d_b, dt_b


# ---------------------------------------------------------------------------
# random monotone submodular generators (exact rationals)
# ---------------------------------------------------------------------------
def rnd_frac(rng, lo_num, hi_num, dens=(1, 2, 3, 4, 5, 6, 8, 10)):
    return Fr(rng.randint(lo_num, hi_num), rng.choice(dens))


def gen_f(n, rng, allow_zero_gain=True):
    """Random monotone submodular f on {0..n-1} as a dict mask -> Fraction."""
    kind = rng.choice(["modular", "coverage", "mixture", "budget"])
    zero_set = set()
    if allow_zero_gain and rng.random() < 0.3 and n >= 3:
        k = rng.randint(1, max(1, n // 3))
        zero_set = set(rng.sample(range(n), k))
    w = [Fr(0) if e in zero_set else rnd_frac(rng, 0, 12) for e in range(n)]
    if all(x == 0 for x in w):
        w[rng.randrange(n)] = Fr(1)
    if kind in ("coverage", "mixture"):
        m = rng.randint(2, 5)
        uw = [rnd_frac(rng, 1, 8) for _ in range(m)]
        sets = []
        for e in range(n):
            if e in zero_set:
                sets.append(0)
            else:
                msk = 0
                for j in range(m):
                    if rng.random() < 0.5:
                        msk |= 1 << j
                sets.append(msk)
    lam = rnd_frac(rng, 0, 6) if kind == "mixture" else Fr(0)
    cap = None
    if kind == "budget":
        tot = sum(w)
        cap = tot * rnd_frac(rng, 1, 9, dens=(10,)) if tot > 0 else Fr(1)
    f = {}
    for S in range(1 << n):
        val = Fr(0)
        if kind in ("coverage", "mixture"):
            cov = 0
            for e in bits(S):
                cov |= sets[e]
            for j in range(len(uw)):
                if cov >> j & 1:
                    val += uw[j]
        if kind == "modular":
            val = sum((w[e] for e in bits(S)), Fr(0))
        elif kind == "mixture":
            val += lam * sum((w[e] for e in bits(S)), Fr(0))
        elif kind == "budget":
            s = sum((w[e] for e in bits(S)), Fr(0))
            val = min(s, cap)
        f[S] = val
    return f, kind, w, zero_set


def min_gain_of(f, n, e):
    """min over every S not containing e of d_e(S).  For submodular f this is
    d_e(N \\ {e}); the minimum is taken over all S so that the same helper is
    correct on the monotone non-submodular instances of C4b."""
    best = None
    bit = 1 << e
    for S in range(1 << n):
        if S & bit:
            continue
        d = f[S | bit] - f[S]
        if best is None or d < best:
            best = d
    return best


# ---------------------------------------------------------------------------
# legal-surrogate generators for part (iii)
# ---------------------------------------------------------------------------
def gen_surrogate(f, n, rng, force=None):
    """Return (ftilde, kind) legal under convention B, or None."""
    kind = force or rng.choice(
        ["plus_modular", "plus_modular", "elementwise", "jitter", "scaled"])
    if kind == "scaled":
        c0 = rnd_frac(rng, 1, 20)
        if c0 == 0:
            c0 = Fr(1)
        return {S: c0 * f[S] for S in range(1 << n)}, "scaled(c=%s)" % c0
    if kind == "elementwise":
        # per-element factors on a modular f rebuilt from f's singleton values
        # only legal when f itself is modular; check and fall back otherwise
        w = [f[1 << e] for e in range(n)]
        mod = all(f[S] == sum((w[e] for e in bits(S)), Fr(0))
                  for S in range(1 << n))
        if not mod:
            kind = "plus_modular"
        else:
            r = [rnd_frac(rng, 1, 30) for _ in range(n)]
            r = [x if x > 0 else Fr(1) for x in r]
            ft = {}
            for S in range(1 << n):
                ft[S] = sum((r[e] * w[e] for e in bits(S)), Fr(0))
            return ft, "elementwise"
    if kind == "jitter":
        # multiplicative jitter on values; legal only when it keeps every gain
        # strictly positive where d > 0 and equal where d = 0.  accept/reject.
        u = {0: Fr(1)}
        for S in range(1, 1 << n):
            u[S] = 1 + rnd_frac(rng, 0, 4, dens=(20, 25, 40, 50))
        ft = {S: u[S] * f[S] for S in range(1 << n)}
        for S, e, d, dt in gain_pairs(f, ft, n):
            if d == 0 and dt != 0:
                return None
            if d > 0 and dt <= 0:
                return None
        return ft, "jitter"
    # plus_modular: ftilde = f + theta * (modular with weights w_e <= min gain)
    theta = rnd_frac(rng, -4, 30, dens=(1, 2, 4, 8))
    if theta <= -1:
        theta = Fr(-1, 2)
    w = []
    for e in range(n):
        mg = min_gain_of(f, n, e)
        if mg <= 0:
            w.append(Fr(0))
        else:
            w.append(mg * rnd_frac(rng, 0, 10, dens=(10,)))
    ft = {}
    for S in range(1 << n):
        ft[S] = f[S] + theta * sum((w[e] for e in bits(S)), Fr(0))
    return ft, "plus_modular(theta=%s)" % theta


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    counters = {k: [0] for k in ("mono", "sub", "va", "band")}

    print("=" * 78)
    print("V11 Q2 oracle: prop:valueacc (ledger T2, convention-B rewrite 2026-09-18)")
    print("statement: results/V11/inputs/statement_valueacc.md")
    print("route one: paper/sections/appendix_model_proofs.tex (Prop valueacc),")
    print("           paper/sections/appendix_proofs.tex subsection app:valueacc")
    print("seeds: (i) %d  (ii) %d  (iii) %d" % (SEED_I, SEED_II, SEED_III))
    print("=" * 78)

    # ---------------- C1: part (i) -------------------------------------
    print("\n--- C1  part (i): two-element construction, exact ---")
    for eps in (Fr(1, 10), Fr(1, 2), Fr(9, 10)):
        run_part_i(eps, 0, "part (i) base n=2, eps=%s" % eps, counters)
    for eps in (Fr(1, 10), Fr(1, 2), Fr(9, 10)):
        run_part_i(eps, 4, "part (i) padded n=6 (4 zero-gain elements), eps=%s"
                   % eps, counters)

    # C1b old-appendix instance
    print("\n--- C1b  part (i) of the OLD appendix app:valueacc, cross-check ---")
    ok_all = True
    dets = []
    for eps in (Fr(1, 10), Fr(1, 2), Fr(9, 10)):
        ok, slack, slackS, d_b, dt_b = run_part_i_old(eps, counters)
        ok_all &= ok
        dets.append("eps=%s: modular+monotone+VA ok, d_b({a})=%s, dtilde_b({a})=%s, "
                    "min VA slack %s at S=%d" % (eps, d_b, dt_b, slack, slackS))
    check("C1b [VERIFIED-EXHAUSTIVE] old appendix (i) instance "
          "f(b)=2eps/(1-eps), f(ab)=(1+eps)/(1-eps), ftilde(a)=ftilde(ab)=1+eps",
          ok_all, "; ".join(dets))

    # ---------------- C2: part (ii) ------------------------------------
    print("\n--- C2  part (ii): ftilde = (1+M) f ---")
    M, d_s, eu_s, eo_s = sp.symbols("M d eta_u eta_o", positive=True)
    # smallest admissible factors, symbolic in M
    r1 = sp.simplify(((1 + M) * d_s) / d_s - (1 + M))          # eta_o = 1+M
    r2 = sp.simplify(d_s / ((1 + M) * d_s) - 1 / (1 + M))      # eta_u = 1/(1+M)
    r3 = sp.simplify((1 / (1 + M)) * (1 + M) - 1)              # product = 1
    # band holds with those factors, as identities
    r4 = sp.simplify(d_s / (1 / (1 + M)) - (1 + M) * d_s)      # lower end tight
    r5 = sp.simplify((1 + M) * ((1 + M) * d_s) - (1 + M) ** 2 * d_s)
    ok = all(r == 0 for r in (r1, r2, r3, r4))
    check("C2a [VERIFIED-SYMBOLIC] sympy in M: smallest eta_o = 1+M, smallest "
          "eta_u = 1/(1+M), product eta = 1; band ends both attained",
          ok, "residuals %s, %s, %s, %s" % (r1, r2, r3, r4),
          {"eta_u": "1/(1+M)", "eta_o": "1+M", "eta": "1"})

    rng2 = random.Random(SEED_II)
    n_ii = 0
    ii_fail = []
    worst_ii = None
    for trial in range(200):
        n = rng2.randint(2, 6)
        f, kind, w, zs = gen_f(n, rng2)
        if all(f[S] == 0 for S in range(1 << n)):
            continue
        Mv = rnd_frac(rng2, 1, 40)
        if Mv <= 0:
            Mv = Fr(1, 2)
        ft = {S: (1 + Mv) * f[S] for S in range(1 << n)}
        n_ii += 1
        m_ok, _ = monotone(f, n, counters["mono"])
        s_ok, _ = submodular(f, n, counters["sub"])
        leg, eu, eo, bad = smallest_factors(f, ft, n, counters["band"])
        fac_ok = leg and eu == Fr(1, 1) / (1 + Mv) and eo == 1 + Mv and eu * eo == 1
        # value accuracy fails at every level eps < M: exhibit S with f(S) > 0
        va_fail_ok = False
        for S in range(1 << n):
            if f[S] > 0:
                # ratio ftilde/f = 1+M, so for any eps < M the upper end breaks
                epsx = Mv * Fr(rng2.randint(1, 99), 100)
                va_fail_ok = ft[S] > (1 + epsx) * f[S]
                break
        # eta^sel = 1: at every state the argmax of dtilde equals the argmax of d
        sel_ok = True
        for S in range(1 << n):
            if S == (1 << n) - 1:
                continue
            cand = [e for e in range(n) if not (S >> e & 1)]
            bd = max(f[S | (1 << e)] - f[S] for e in cand)
            bdt = max(ft[S | (1 << e)] - ft[S] for e in cand)
            A = {e for e in cand if f[S | (1 << e)] - f[S] == bd}
            B = {e for e in cand if ft[S | (1 << e)] - ft[S] == bdt}
            if A != B:
                sel_ok = False
                break
        ok_t = m_ok and s_ok and fac_ok and va_fail_ok and sel_ok
        if not ok_t:
            ii_fail.append({"trial": trial, "n": n, "kind": kind, "M": str(Mv),
                            "monotone": m_ok, "submodular": s_ok,
                            "factors_ok": fac_ok, "va_fails": va_fail_ok,
                            "etasel_1": sel_ok,
                            "eta_u": str(eu), "eta_o": str(eo)})
        if worst_ii is None:
            worst_ii = (str(Mv), str(eu), str(eo))
    COUNTS["C2_random_instances"] = n_ii
    check("C2b [VERIFIED-EXHAUSTIVE] 200 random monotone submodular f "
          "(coverage/modular/mixture/budget, n <= 6) with random rational M: "
          "smallest factors = (1/(1+M), 1+M), eta = 1, value accuracy fails "
          "below M, argmax of dtilde = argmax of d at every state",
          not ii_fail,
          "instances=%d failures=%d" % (n_ii, len(ii_fail)),
          {"failures": ii_fail[:5]})

    # ---------------- C3: part (iii) identities -------------------------
    print("\n--- C3  part (iii): sympy identities ---")
    eta_s = sp.symbols("eta", positive=True)
    eps_expr = (eta_s - 1) / (eta_s + 1)
    c_expr = 2 * eu_s / (eta_s + 1)
    i1 = sp.simplify(c_expr / eu_s - (1 - eps_expr))
    i2 = sp.simplify(sp.expand(c_expr * eo_s).subs(eo_s, eta_s / eu_s)
                     - (1 + eps_expr))
    i3 = sp.simplify((1 - eps_expr) - 2 / (eta_s + 1))
    i4 = sp.simplify((1 + eps_expr) - 2 * eta_s / (eta_s + 1))
    i5 = sp.simplify((1 - eps_expr) / (1 + eps_expr) - 1 / eta_s)
    ok = all(x == 0 for x in (i1, i2, i3, i4, i5))
    check("C3a [VERIFIED-SYMBOLIC] c/eta_u = 1-eps and c*eta_o = 1+eps for "
          "c = 2 eta_u/(eta+1), eps = (eta-1)/(eta+1), eta = eta_u eta_o; also "
          "1-eps = 2/(eta+1), 1+eps = 2eta/(eta+1), (1-eps)/(1+eps) = 1/eta",
          ok, "residuals %s, %s, %s, %s, %s" % (i1, i2, i3, i4, i5))

    # domain: eps in [0,1) for eta >= 1, and c > 0
    d1 = sp.simplify(eps_expr.subs(eta_s, 1))
    d2 = sp.simplify(1 - eps_expr - 2 / (eta_s + 1))
    mono_eps = sp.simplify(sp.diff(eps_expr, eta_s) - 2 / (eta_s + 1) ** 2)
    ok = (d1 == 0 and d2 == 0 and mono_eps == 0)
    check("C3b [VERIFIED-SYMBOLIC] eps(1) = 0, 1-eps = 2/(eta+1) > 0 for eta >= 1 "
          "(so eps < 1), d eps/d eta = 2/(eta+1)^2 > 0 (so eps in [0,1))",
          ok, "residuals %s, %s, %s" % (d1, d2, mono_eps))

    # ---------------- C4: part (iii) on random legal surrogates ----------
    print("\n--- C4  part (iii): random LEGAL surrogates, smallest factors ---")
    rng3 = random.Random(SEED_III)
    target = 2200
    n_weights = [(2, 6), (3, 8), (4, 8), (5, 6), (6, 4), (7, 2)]
    pool = []
    for nn, wt in n_weights:
        pool += [nn] * wt
    done = 0
    rejected = 0
    kinds = {}
    iii_fail = []
    worst_slack = None       # min over (trial, S) of min(lo slack, hi slack)/f(S)
    worst_info = None
    worst_abs = None
    worst_slack_gt1 = None   # same, restricted to trials with eta > 1
    worst_info_gt1 = None
    n_eta_gt1 = 0
    tight_lo = 0
    tight_hi = 0
    eta_max = None
    eta_max_info = None
    subsets_scanned = 0
    while done < target:
        n = rng3.choice(pool)
        f, kind, w, zs = gen_f(n, rng3)
        if all(f[S] == 0 for S in range(1 << n)):
            continue
        g = gen_surrogate(f, n, rng3)
        if g is None:
            rejected += 1
            continue
        ft, skind = g
        m_ok, _ = monotone(f, n, counters["mono"])
        s_ok, _ = submodular(f, n, counters["sub"])
        if not (m_ok and s_ok):
            iii_fail.append({"why": "generator produced non monotone submodular f",
                             "n": n, "kind": kind})
            done += 1
            continue
        leg, eu, eo, bad = smallest_factors(f, ft, n, counters["band"])
        if not leg:
            rejected += 1
            continue
        done += 1
        base = skind.split("(")[0]
        kinds[base] = kinds.get(base, 0) + 1
        eta = eu * eo
        if eta < 1:
            iii_fail.append({"why": "eta < 1", "eta": str(eta), "n": n})
        if eta_max is None or eta > eta_max:
            eta_max = eta
            eta_max_info = {"n": n, "f_kind": kind, "surrogate": skind,
                            "eta_u": str(eu), "eta_o": str(eo)}
        if eta > 1:
            n_eta_gt1 += 1
        eps = (eta - 1) / (eta + 1)
        c = 2 * eu / (eta + 1)
        if not (0 <= eps < 1 and c > 0):
            iii_fail.append({"why": "eps out of [0,1) or c <= 0", "eps": str(eps),
                             "c": str(c), "eta": str(eta), "n": n})
        for S in range(1 << n):
            subsets_scanned += 1
            # intermediate chain-sum band
            if not (f[S] / eu <= ft[S] <= eo * f[S]):
                iii_fail.append({
                    "why": "chain band f/eta_u <= ftilde <= eta_o f violated",
                    "n": n, "S": S, "f": str(f[S]), "ftilde": str(ft[S]),
                    "eta_u": str(eu), "eta_o": str(eo), "f_kind": kind,
                    "surrogate": skind})
                break
            lo = (1 - eps) * f[S]
            hi = (1 + eps) * f[S]
            s1 = c * ft[S] - lo
            s2 = hi - c * ft[S]
            if s1 < 0 or s2 < 0:
                iii_fail.append({
                    "why": "value accuracy of c*ftilde at level eps violated",
                    "n": n, "S": S, "f": str(f[S]), "ftilde": str(ft[S]),
                    "c": str(c), "eps": str(eps), "eta": str(eta),
                    "lo": str(lo), "hi": str(hi), "c_ftilde": str(c * ft[S]),
                    "f_kind": kind, "surrogate": skind})
                break
            if s1 == 0:
                tight_lo += 1
            if s2 == 0:
                tight_hi += 1
            if f[S] > 0:
                rel = min(s1, s2) / f[S]
                info = {"n": n, "S": S, "f": str(f[S]),
                        "ftilde": str(ft[S]), "eta_u": str(eu),
                        "eta_o": str(eo), "eta": str(eta),
                        "eps": str(eps), "c": str(c),
                        "f_kind": kind, "surrogate": skind}
                if worst_slack is None or rel < worst_slack:
                    worst_slack = rel
                    worst_abs = min(s1, s2)
                    worst_info = info
                if eta > 1 and (worst_slack_gt1 is None or rel < worst_slack_gt1):
                    worst_slack_gt1 = rel
                    worst_info_gt1 = info
    COUNTS["C4_legal_surrogates"] = done
    COUNTS["C4_rejected_draws"] = rejected
    COUNTS["C4_subsets_scanned"] = subsets_scanned
    COUNTS["C4_kinds"] = kinds
    check("C4 [VERIFIED-EXHAUSTIVE] %d random legal surrogates (n <= 7; f exact "
          "monotone submodular; eta_u, eta_o the ACTUAL smallest factors): "
          "chain band f/eta_u <= ftilde <= eta_o f and "
          "(1-eps) f <= c ftilde <= (1+eps) f on every subset" % done,
          not iii_fail,
          "surrogates=%d subsets=%d rejected draws=%d violations=%d kinds=%s"
          % (done, subsets_scanned, rejected, len(iii_fail), kinds),
          {"violations": iii_fail[:5]})
    WITNESSES["C4_worst_relative_slack"] = {
        "relative_slack": str(worst_slack), "absolute_slack": str(worst_abs),
        "at": worst_info}
    WITNESSES["C4_worst_relative_slack_eta_gt_1"] = {
        "relative_slack": str(worst_slack_gt1), "at": worst_info_gt1}
    WITNESSES["C4_largest_eta"] = {"eta": str(eta_max), "at": eta_max_info}
    COUNTS["C4_tight_lower_end"] = tight_lo
    COUNTS["C4_tight_upper_end"] = tight_hi
    COUNTS["C4_eta_gt_1"] = n_eta_gt1
    note("worst relative slack %s (absolute %s) at %s"
         % (worst_slack, worst_abs, worst_info))
    note("worst relative slack among the %d surrogates with eta > 1: %s at %s"
         % (n_eta_gt1, worst_slack_gt1, worst_info_gt1))
    note("largest eta seen %s at %s" % (eta_max, eta_max_info))

    # ---------------- C4b: (iii) without submodularity -------------------
    print("\n--- C4b  part (iii) on monotone f that is NOT submodular ---")
    rngN = random.Random(SEED_III + 5)
    nb_done = 0
    nb_nonsub = 0
    nb_fail = []
    tries = 0
    while nb_done < 400 and tries < 20000:
        tries += 1
        n = rngN.randint(2, 5)
        # monotone f with f(empty) = 0, built from arbitrary nonnegative gains
        # on a random linear extension: values assigned level by level as the
        # max over predecessors plus a random nonnegative increment
        f = {0: Fr(0)}
        for S in sorted(range(1, 1 << n), key=lambda m: bin(m).count("1")):
            base = max(f[S & ~(1 << e)] for e in bits(S))
            inc = Fr(rngN.randint(0, 12), rngN.choice((1, 2, 3, 4)))
            f[S] = base + inc
        m_ok, _ = monotone(f, n, counters["mono"])
        if not m_ok:
            continue
        s_ok, _ = submodular(f, n, counters["sub"])
        if s_ok:
            continue                      # keep only the non-submodular ones
        if all(f[S] == 0 for S in range(1 << n)):
            continue
        g = gen_surrogate(f, n, rngN, force="plus_modular")
        if g is None:
            continue
        ft, skind = g
        leg, eu, eo, bad = smallest_factors(f, ft, n, counters["band"])
        if not leg:
            continue
        nb_done += 1
        nb_nonsub += 1
        eta = eu * eo
        eps = (eta - 1) / (eta + 1)
        c = 2 * eu / (eta + 1)
        for S in range(1 << n):
            if not (f[S] / eu <= ft[S] <= eo * f[S]):
                nb_fail.append({"why": "chain band violated (non-submodular f)",
                                "n": n, "S": S, "f": str(f[S]),
                                "ftilde": str(ft[S]), "eta_u": str(eu),
                                "eta_o": str(eo)})
                break
            if not ((1 - eps) * f[S] <= c * ft[S] <= (1 + eps) * f[S]):
                nb_fail.append({"why": "value accuracy violated (non-submodular f)",
                                "n": n, "S": S, "f": str(f[S]),
                                "ftilde": str(ft[S]), "c": str(c),
                                "eps": str(eps), "eta": str(eta)})
                break
    COUNTS["C4b_non_submodular_instances"] = nb_done
    check("C4b [VERIFIED-EXHAUSTIVE] part (iii) on %d monotone f that FAIL the "
          "submodularity test (the statement's claim that (iii) uses no "
          "submodularity): chain band and value accuracy of c*ftilde hold"
          % nb_done,
          nb_done > 0 and not nb_fail,
          "instances=%d violations=%d (each instance was checked to be monotone "
          "and to have a submodularity violation before use)"
          % (nb_done, len(nb_fail)),
          {"violations": nb_fail[:5]})

    # ---------------- C5: structured cases ------------------------------
    print("\n--- C5  part (iii): structured cases ---")
    structured = []

    # (a) eta = 1, ftilde = c0 f
    okA = True
    detA = []
    rngS = random.Random(SEED_III + 1)
    for c0 in (Fr(1), Fr(1, 7), Fr(13, 3), Fr(1000)):
        n = 4
        f, kind, w, zs = gen_f(n, rngS, allow_zero_gain=False)
        while all(f[S] == 0 for S in range(1 << n)):
            f, kind, w, zs = gen_f(n, rngS, allow_zero_gain=False)
        ft = {S: c0 * f[S] for S in range(1 << n)}
        leg, eu, eo, _ = smallest_factors(f, ft, n, counters["band"])
        eta = eu * eo
        eps = (eta - 1) / (eta + 1)
        c = 2 * eu / (eta + 1)
        ok = (leg and eta == 1 and eps == 0 and eu == Fr(1, 1) / c0 and eo == c0
              and all(c * ft[S] == f[S] for S in range(1 << n)))
        okA &= ok
        detA.append("c0=%s -> eta_u=%s eta_o=%s eta=%s eps=%s c=%s, c*ftilde == f: %s"
                    % (c0, eu, eo, eta, eps, c,
                       all(c * ft[S] == f[S] for S in range(1 << n))))
    structured.append({"case": "eta = 1 (ftilde = c0 f)",
                       "outcome": "PASS" if okA else "FAIL",
                       "detail": "; ".join(detA)})
    check("C5a [VERIFIED-EXHAUSTIVE] structured: eta = 1, ftilde = c0 f, "
          "c = 2 eta_u/(eta+1) = eta_u = 1/c0 and c*ftilde = f exactly, eps = 0",
          okA, "; ".join(detA))

    # (b) very large eta
    okB = True
    detB = []
    for spread in (Fr(100), Fr(10000), Fr(10 ** 6)):
        n = 4
        w = [Fr(1), Fr(1), Fr(1), Fr(1)]
        r = [Fr(1), spread, Fr(1, 1) / spread, Fr(3)]
        f = {S: sum((w[e] for e in bits(S)), Fr(0)) for S in range(1 << n)}
        ft = {S: sum((r[e] * w[e] for e in bits(S)), Fr(0)) for S in range(1 << n)}
        leg, eu, eo, _ = smallest_factors(f, ft, n, counters["band"])
        eta = eu * eo
        eps = (eta - 1) / (eta + 1)
        c = 2 * eu / (eta + 1)
        ok = leg and eta == spread * spread and 0 < eps < 1
        for S in range(1 << n):
            if not (f[S] / eu <= ft[S] <= eo * f[S]):
                ok = False
            if not ((1 - eps) * f[S] <= c * ft[S] <= (1 + eps) * f[S]):
                ok = False
        okB &= ok
        detB.append("spread=%s -> eta=%s eps=%s (float %.9f) c=%s ok=%s"
                    % (spread, eta, eps, float(eps), c, ok))
    structured.append({"case": "very large eta (per-element factors on modular f)",
                       "outcome": "PASS" if okB else "FAIL",
                       "detail": "; ".join(detB)})
    check("C5b [VERIFIED-EXHAUSTIVE] structured: very large eta, "
          "eps = (eta-1)/(eta+1) stays in (0,1) and both bands hold",
          okB, "; ".join(detB))

    # (c) f with zero-gain elements
    okC = True
    detC = []
    rngZ = random.Random(SEED_III + 2)
    zc = 0
    for _ in range(60):
        n = rngZ.randint(3, 6)
        f, kind, w, zs = gen_f(n, rngZ)
        zero_elems = [e for e in range(n) if min_gain_of(f, n, e) == 0
                      and f[1 << e] == 0]
        if not zero_elems or all(f[S] == 0 for S in range(1 << n)):
            continue
        g = gen_surrogate(f, n, rngZ)
        if g is None:
            continue
        ft, skind = g
        leg, eu, eo, _ = smallest_factors(f, ft, n, counters["band"])
        if not leg:
            okC = False
            detC.append("illegal surrogate on zero-gain instance")
            continue
        zc += 1
        eta = eu * eo
        eps = (eta - 1) / (eta + 1)
        c = 2 * eu / (eta + 1)
        ok = True
        for S in range(1 << n):
            if not (f[S] / eu <= ft[S] <= eo * f[S]):
                ok = False
            if not ((1 - eps) * f[S] <= c * ft[S] <= (1 + eps) * f[S]):
                ok = False
        # the band forces dtilde = 0 wherever d = 0
        for S, e, d, dt in gain_pairs(f, ft, n):
            if d == 0 and dt != 0:
                ok = False
                break
        okC &= ok
    detC.append("instances with at least one zero-gain element: %d, all bands hold "
                "and dtilde = 0 wherever d = 0" % zc)
    structured.append({"case": "monotone f that is NOT submodular (C4b)",
                       "outcome": "PASS" if (nb_done > 0 and not nb_fail)
                                  else "FAIL",
                       "detail": "%d instances, each confirmed monotone and "
                                 "confirmed to violate submodularity; "
                                 "violations %d" % (nb_done, len(nb_fail))})
    structured.append({"case": "f with zero-gain elements",
                       "outcome": "PASS" if okC and zc > 0 else "FAIL",
                       "detail": "; ".join(detC)})
    check("C5c [VERIFIED-EXHAUSTIVE] structured: f with zero-gain elements, "
          "%d instances" % zc, okC and zc > 0, "; ".join(detC))
    COUNTS["C5_zero_gain_instances"] = zc

    # ---------------- C6: scaling invariance ----------------------------
    print("\n--- C6  scaling invariance of eta and the split ---")
    c_s = sp.symbols("c", positive=True)
    s1 = sp.simplify((eu_s / c_s) * (c_s * eo_s) - eu_s * eo_s)
    s2 = sp.simplify(sp.simplify((2 * (eu_s / c_s) / (eu_s * eo_s + 1)) * c_s
                                 - 2 * eu_s / (eu_s * eo_s + 1)))
    ok = (s1 == 0 and s2 == 0)
    check("C6 [VERIFIED-SYMBOLIC] rescaling ftilde by c maps (eta_u, eta_o) -> "
          "(c eta_u, eta_o/c) with eta unchanged, and the rescaling constant of "
          "(iii) composes so that c*ftilde is the same function either way",
          ok, "residuals %s, %s" % (s1, s2))

    # ---------------- C7: old vs new convention -------------------------
    print("\n--- C7  old convention (appendix_proofs.tex app:valueacc) vs new ---")
    old_level = sp.Max(1 - 1 / eu_s, eo_s - 1)
    b1 = sp.simplify((eo_s - 1) - 1 - (eo_s - 2))        # eta_o - 1 < 1 iff eta_o < 2
    b2 = sp.simplify((1 - 1 / eu_s) - 1 + 1 / eu_s)      # 1 - 1/eta_u < 1 always
    # explicit instance where the OLD level leaves (0,1) but the new one does not
    eu0, eo0 = Fr(1), Fr(5, 2)
    old_val = max(1 - Fr(1, 1) / eu0, eo0 - 1)
    eta0 = eu0 * eo0
    new_val = (eta0 - 1) / (eta0 + 1)
    ok = (b1 == 0 and b2 == 0 and old_val >= 1 and 0 < new_val < 1)
    check("C7a [VERIFIED-SYMBOLIC] old level max{1-1/eta_u, eta_o-1} leaves (0,1) "
          "exactly when eta_o >= 2 (the reason for the old eta_o < 2 proviso); "
          "the convention-B level (eta-1)/(eta+1) never does",
          ok, "at (eta_u, eta_o) = (%s, %s): old level = %s >= 1, "
              "new level = %s (float %.6f)"
              % (eu0, eo0, old_val, new_val, float(new_val)),
          {"old_level": str(old_val), "new_level": str(new_val)})

    # rerun the existing repo script that records the old-convention boundary
    m1 = os.path.join(ROOT, "results", "M1_checks.py")
    if os.path.exists(m1):
        p = subprocess.run([sys.executable, m1], capture_output=True, text=True,
                           timeout=300, cwd=ROOT)
        tail = [l for l in p.stdout.splitlines() if l.strip()][-3:]
        npass = sum(1 for l in p.stdout.splitlines() if l.startswith("PASS"))
        nfail = sum(1 for l in p.stdout.splitlines() if l.startswith("FAIL"))
        SUBPROCS.append({"path": "results/M1_checks.py", "exit_code": p.returncode,
                         "pass_lines": npass, "fail_lines": nfail,
                         "tail": tail})
        check("C7b rerun of the existing repo script results/M1_checks.py "
              "(old-convention (iii) domain boundary and band-rescaling "
              "identities; not modified)",
              p.returncode == 0,
              "exit_code=%d PASS lines=%d FAIL lines=%d tail=%s"
              % (p.returncode, npass, nfail, tail))
    else:
        check("C7b rerun of results/M1_checks.py", False, "script not found")

    # ---------------- criterion D --------------------------------------
    print("\n--- D  counterexample search against the statement itself ---")

    # D(i): random eps and random padding
    rng1 = random.Random(SEED_I)
    d_i = 0
    d_i_viol = []
    for _ in range(2000):
        num = rng1.randint(1, 999)
        den = 1000
        eps = Fr(num, den)
        if not (0 < eps < 1):
            continue
        pad = rng1.randint(0, 5)
        d_i += 1
        n, f, ft = build_part_i(eps, pad)
        m_ok, _ = monotone(f, n)
        s_ok, _ = submodular(f, n)
        va_ok, va_bad, _, _ = value_accurate(f, ft, n, eps)
        d_b = f[0b11] - f[0b01]
        dt_b = ft[0b11] - ft[0b01]
        leg, eu, eo, bad = smallest_factors(f, ft, n)
        zero_ok = all(dt == 0 for S, e, d, dt in gain_pairs(f, ft, n) if d == 0)
        ok = (m_ok and s_ok and va_ok and dt_b == 0 and d_b > 0
              and (not leg) and bad[0] == "d>0 but dtilde<=0" and zero_ok)
        if not ok:
            d_i_viol.append({"eps": str(eps), "pad": pad, "monotone": m_ok,
                             "submodular": s_ok, "value_accurate": va_ok,
                             "dtilde_b": str(dt_b), "d_b": str(d_b),
                             "finite_factors": leg, "zero_forced": zero_ok,
                             "va_witness": va_bad})
    COUNTS["D_i_draws"] = d_i

    # D(ii): random f and random M
    rngD2 = random.Random(SEED_II + 7)
    d_ii = 0
    d_ii_viol = []
    for _ in range(2000):
        n = rngD2.randint(2, 5)
        f, kind, w, zs = gen_f(n, rngD2)
        if all(f[S] == 0 for S in range(1 << n)):
            continue
        Mv = Fr(rngD2.randint(1, 5000), rngD2.choice((1, 10, 100, 1000)))
        if Mv <= 0:
            continue
        d_ii += 1
        ft = {S: (1 + Mv) * f[S] for S in range(1 << n)}
        leg, eu, eo, bad = smallest_factors(f, ft, n)
        fac_ok = leg and eu == Fr(1, 1) / (1 + Mv) and eo == 1 + Mv and eu * eo == 1
        sel_ok = True
        for S in range(1 << n):
            if S == (1 << n) - 1:
                continue
            cand = [e for e in range(n) if not (S >> e & 1)]
            bd = max(f[S | (1 << e)] - f[S] for e in cand)
            bdt = max(ft[S | (1 << e)] - ft[S] for e in cand)
            A = {e for e in cand if f[S | (1 << e)] - f[S] == bd}
            B = {e for e in cand if ft[S | (1 << e)] - ft[S] == bdt}
            if A != B:
                sel_ok = False
                break
        va_ok = True
        for S in range(1 << n):
            if f[S] > 0:
                epsx = Mv * Fr(rngD2.randint(1, 999), 1000)
                va_ok = ft[S] > (1 + epsx) * f[S]
                break
        if not (fac_ok and sel_ok and va_ok):
            d_ii_viol.append({"n": n, "f_kind": kind, "M": str(Mv),
                              "factors_ok": fac_ok, "etasel_1": sel_ok,
                              "va_fails_below_M": va_ok,
                              "eta_u": str(eu), "eta_o": str(eo)})
    COUNTS["D_ii_draws"] = d_ii

    d_total = d_i + d_ii + done + nb_done
    COUNTS["D_total_random"] = d_total
    all_viol = d_i_viol + d_ii_viol + iii_fail + nb_fail
    check("D [VERIFIED-EXHAUSTIVE] counterexample search: %d random draws "
          "((i) %d, (ii) %d, (iii) %d legal surrogates on submodular f plus %d "
          "on monotone non-submodular f), violations = %d"
          % (d_total, d_i, d_ii, done, nb_done, len(all_viol)),
          not all_viol,
          "violations=%d" % len(all_viol),
          {"violations": all_viol[:5]})

    # ---------------- running example K = 3, eta = 3/2 -------------------
    print("\n--- running example: K = 3, eta = 3/2 ---")
    n = 4
    w = [Fr(1), Fr(1), Fr(1), Fr(1)]
    r = [Fr(1), Fr(3, 2), Fr(1), Fr(3, 2)]
    f = {S: sum((w[e] for e in bits(S)), Fr(0)) for S in range(1 << n)}
    ft = {S: sum((r[e] * w[e] for e in bits(S)), Fr(0)) for S in range(1 << n)}
    leg, eu, eo, _ = smallest_factors(f, ft, n)
    eta = eu * eo
    eps = (eta - 1) / (eta + 1)
    c = 2 * eu / (eta + 1)
    S3 = 0b0111                 # a 3-set, K = 3
    re_ok = (leg and eta == Fr(3, 2) and eps == Fr(1, 5) and c == Fr(4, 5)
             and f[S3] == 3 and ft[S3] == Fr(7, 2) and c * ft[S3] == Fr(14, 5)
             and (1 - eps) * f[S3] == Fr(12, 5) and (1 + eps) * f[S3] == Fr(18, 5)
             and (1 - eps) / (1 + eps) == Fr(2, 3))
    run_lines = [
        "K = 3, eta = 3/2: (eta_u, eta_o) = (%s, %s), eps = (eta-1)/(eta+1) = %s, "
        "c = 2 eta_u/(eta+1) = %s." % (eu, eo, eps, c),
        "modular instance n = 4, weights (1,1,1,1), predicted factors "
        "(1, 3/2, 1, 3/2); on the 3-set S = {0,1,2}: f(S) = %s, ftilde(S) = %s, "
        "c ftilde(S) = %s." % (f[S3], ft[S3], c * ft[S3]),
        "band: (1-eps) f(S) = %s <= %s <= %s = (1+eps) f(S); "
        "(1-eps)/(1+eps) = %s = 1/eta."
        % ((1 - eps) * f[S3], c * ft[S3], (1 + eps) * f[S3], (1 - eps) / (1 + eps)),
    ]
    for l in run_lines:
        print("      " + l)
    check("RE [VERIFIED-EXHAUSTIVE] running example K = 3, eta = 3/2 numbers",
          re_ok, "eps = 1/5, c = 4/5, f(S) = 3, ftilde(S) = 7/2, c ftilde(S) = 14/5 "
                 "in [12/5, 18/5]")

    # ---------------- summary -------------------------------------------
    COUNTS["monotone_checks"] = counters["mono"][0]
    COUNTS["submodularity_checks"] = counters["sub"][0]
    COUNTS["value_accuracy_subset_checks"] = counters["va"][0]
    COUNTS["band_pair_checks"] = counters["band"][0]

    elapsed = time.time() - T0
    npass = sum(1 for c_ in CHECKS if c_["status"] == "PASS")
    nfail = sum(1 for c_ in CHECKS if c_["status"] == "FAIL")
    print("\n" + "=" * 78)
    print("checks: %d PASS, %d FAIL; criterion D random draws: %d; violations: %d"
          % (npass, nfail, d_total, len(all_viol)))
    print("counts: %s" % json.dumps(COUNTS, sort_keys=True))
    print("elapsed %.1f s" % elapsed)
    print("=" * 78)

    out = {
        "script": os.path.join("results", "V11", "oracle", "valueacc.py"),
        "statement": "prop:valueacc (ledger T2, convention-B rewrite of 2026-09-18); "
                     "source results/V11/inputs/statement_valueacc.md",
        "route_one_sources": [
            "paper/sections/appendix_model_proofs.tex (Proof of Proposition prop:valueacc)",
            "paper/sections/appendix_proofs.tex subsection app:valueacc (old convention)",
            "THEOREM_LEDGER.md section ## T2",
        ],
        "seeds": {"part_i": SEED_I, "part_ii": SEED_II, "part_iii": SEED_III},
        "counts": COUNTS,
        "criterion_C": {"checks": CHECKS, "pass": npass, "fail": nfail},
        "criterion_D": {
            "random_draws_total": d_total,
            "part_i_draws": d_i,
            "part_ii_draws": d_ii,
            "part_iii_legal_surrogates": done,
            "part_iii_non_submodular_instances": nb_done,
            "violations": len(all_viol),
            "violation_records": all_viol[:20],
            "structured_cases": structured,
            "worst_relative_slack": str(worst_slack),
            "worst_slack_witness": worst_info,
            "worst_relative_slack_eta_gt_1": str(worst_slack_gt1),
            "worst_slack_witness_eta_gt_1": worst_info_gt1,
            "largest_eta": str(eta_max),
            "largest_eta_witness": eta_max_info,
        },
        "witnesses": WITNESSES,
        "reran_repo_scripts": SUBPROCS,
        "running_example_K3_eta_1_5": run_lines,
        "elapsed_seconds": round(elapsed, 2),
        "exit_code": 0 if nfail == 0 else 1,
    }
    with open(JSON_PATH, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=False)
    print("wrote " + JSON_PATH)
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

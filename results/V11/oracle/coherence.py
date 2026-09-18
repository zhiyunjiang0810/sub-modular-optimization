#!/usr/bin/env python3
"""V11 Q5b oracle for lem:coherence (ledger T5) and its sharp form.

Statement under test (results/V11/inputs/statement_coherence.md):

    Let f be monotone, S subset N, e, e' not in S, and suppose
    dtilde_e(S) >= dtilde_{e'}(S).  Then

      (i)   d_e(S + e')      >= (1/eta) d_{e'}(S + e),
      (ii)  (1 - 1/eta) d_{e'}(S + e) >= d_{e'}(S) - d_e(S).

Sharp form (H-J3, ledger T5), with d = d_e(S), g = d_{e'}(S), h = d_{e'}(S+e):

      d - g/eta >= (1 - 1/eta)(g - h) >= 0,

the first inequality being (ii) rearranged, the second one using
submodularity of f (g >= h) together with eta >= 1.

Definition 1 (results/V11/inputs/definition1.md, convention B): for all
S and e not in S,  d_e(S)/eta_u <= dtilde_e(S) <= eta_o d_e(S), and
eta = eta_u eta_o.  In particular d_e(S) = 0 forces dtilde_e(S) = 0.
"Actual eta" below always means the realized band of the sampled pair
(f, ftilde) over the WHOLE lattice, i.e. eta_u = max d/dtilde and
eta_o = max dtilde/d, which is the smallest admissible eta and hence the
sharpest form of the two inequalities.

Route-one proof material:
    paper/sections/appendix_proofs.tex, subsection app:coherence (~line 524):
    the two-order expansion of ftilde(S + e + e') giving eq:coh-pred, then
    the two bands for (i), then the same expansion for f giving (ii).
    results/H_J3_gate_check.py: sharp form == (ii) rearranged.
    results/J2_core_oracles.py: the R6 three-term nonnegative slack
    decomposition (symbolic_core) and its full-lattice LP minimization
    (R6_full_lattice_lp).
Ledger card: THEOREM_LEDGER.md section "## T5".

Criterion C (oracle)
  C0  own sympy re-derivation, not a reuse of J2: the two exchange
      identities, the three-term nonnegative slack decompositions of (i)
      and of (ii), the fact that the slacks of (i), of (ii) and of the
      first sharp-form inequality are the SAME rational function, the
      prediction slack d - g/eta as its own three-term sum, the second
      sharp-form inequality, and the corollary "eta > 1 and d = g/eta
      force h = g".                                      [VERIFIED-SYMBOLIC]
  C1  >= 2000 random exact instances: 1200 with f monotone only (not
      submodular) and 1200 with f monotone submodular, n in 3..6, a legal
      random ftilde, actual (eta_u, eta_o) recomputed over the lattice.
      For EVERY triple (S, e, e') of the lattice with dtilde_e(S) >=
      dtilde_{e'}(S) (both orientations when the predicted gains tie),
      check (i) and (ii); on the submodular half also check the sharp
      form d - g/eta >= (1 - 1/eta)(g - h) >= 0.          [VERIFIED-EXHAUSTIVE]
  C2  on every triple of C1: the three-term decomposition of C0 evaluated
      in Fractions, each term nonnegative and the three summing exactly to
      the slack.                                          [VERIFIED-EXHAUSTIVE]
  C3  rerun results/H_J3_gate_check.py (slack certificate of the sharp
      form), record exit code and key counts.             [VERIFIED-SYMBOLIC]
                                                          + [VERIFIED-LP 浮点]
  C4  rerun results/J2_core_oracles.py, record exit code and the coherence
      part only: the R6 pred / cons symbolic identities and the R6
      full-lattice LP minimum slacks.                     [VERIFIED-SYMBOLIC]
                                                          + [VERIFIED-LP 浮点]
  C5  running example: the K = 3, eta = 3/2 exact worst-case trajectory
      (prop:rigidity, j = 2), sharp form at each of the three steps.
                                                          [VERIFIED-EXHAUSTIVE]

Criterion D (counterexample search on the statement itself)
  The random triples of C1 are the search; any violation is a FAILED item
  printed with its witness.  Structured cases:
    D1  eta = 1 (ftilde = c f): both inequalities collapse to d >= g,
        equality cases enumerated.
    D2  d_e(S) = 0 (Definition 1 then forces g = 0 as well).
    D3  S = empty.
    D4  must-not-claim: the lemma FAILS when the band is only assumed on
        the run states.  One explicit instance where the global band fails
        off-trajectory at S + e' and (ii) is violated at eta^tr, plus a
        randomized search counting how often this happens.
    D5  the SECOND sharp-form inequality needs submodularity: an explicit
        monotone non-submodular instance with g < h.

Every decision uses fractions.Fraction or sympy; floats appear only in
printed text and inside the two rerun repository scripts.  Seeds fixed.
No existing repository file is modified: results/J2_core_oracles.py
rewrites results/J2_core_oracles.json in place, so this script saves those
bytes first, copies the fresh file into results/V11/oracle/reruns/ and
restores the original, verifying the sha256.

Run:  python3 results/V11/oracle/coherence.py
Exit code 0 iff every check passed.  Writes results/V11/oracle/coherence.json.
"""

from fractions import Fraction as Fr
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
import time

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
JSON_PATH = os.path.join(HERE, "coherence.json")
RERUN_DIR = os.path.join(HERE, "reruns")

HJ3_SCRIPT = os.path.join(ROOT, "results", "H_J3_gate_check.py")
HJ3_OUTPUTS = []
J2_SCRIPT = os.path.join(ROOT, "results", "J2_core_oracles.py")
J2_OUTPUTS = ["results/J2_core_oracles.json"]

SEED_MONO = 20260918        # C1, monotone-only half
SEED_SUB = 20260919         # C1, monotone submodular half
SEED_D1 = 20260920          # structured eta = 1
SEED_D2 = 20260921          # structured d_e(S) = 0
SEED_D3 = 20260922          # structured S = empty
SEED_D4 = 20260923          # structured trajectory-only band search

N_MONO = 1200
N_SUB = 1200

CHECKS = []
VIOLATIONS = []
WITNESSES = []
COUNTS = {}
SUBPROCS = []
EXTRA = {}


def check(name, ok, detail="", extra=None):
    rec = {"name": name, "status": "PASS" if ok else "FAIL", "detail": detail}
    if extra:
        rec.update(extra)
    CHECKS.append(rec)
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""))
    if not ok:
        VIOLATIONS.append({"where": name, "detail": detail, **(extra or {})})
    return ok


def pc(m):
    return bin(m).count("1")


def setname(n, m):
    return "{" + ",".join(str(i) for i in range(n) if (m >> i) & 1) + "}"


# ---------------------------------------------------------------------------
# C0: own symbolic derivation
# ---------------------------------------------------------------------------
def run_C0():
    ids = {}
    ok = True

    def zero(name, expr):
        nonlocal ok
        r = sp.simplify(sp.together(sp.expand(expr)))
        r = sp.cancel(r)
        ids[name] = str(r)
        if r != 0:
            ok = False
            VIOLATIONS.append({"where": "C0", "identity": name, "residual": str(r)})

    eu, eo = sp.symbols("eta_u eta_o", positive=True)
    eta = eu * eo
    # true gains:  d = d_e(S), g = d_{e'}(S), h = d_{e'}(S+e), D = d_e(S+e')
    # predicted:   P = dt_e(S), Q = dt_{e'}(S), R = dt_{e'}(S+e), Pp = dt_e(S+e')
    d, g, h, P, Q, R = sp.symbols("d g h P Q R", nonnegative=True)
    D = d + h - g                      # f exchange identity
    Pp = P + R - Q                     # ftilde exchange identity

    # 1. the two exchange identities (the only thing "expanding in two orders" says)
    zero("f exchange identity  d + h = g + d_e(S+e')", (d + h) - (g + D))
    zero("ftilde exchange identity  P + R = Q + dt_e(S+e')", (P + R) - (Q + Pp))

    # 2. three-term nonnegative decomposition of part (i)
    #    slack_i = d_e(S+e') - h/eta
    #            = (eo*D - Pp)/eo  +  (P - Q)/eo  +  (eu*R - h)/(eu*eo)
    t1 = (eo * D - Pp) / eo            # upper band at (S+e', e)
    t2 = (P - Q) / eo                  # hypothesis dt_e(S) >= dt_{e'}(S)
    t3 = (eu * R - h) / (eu * eo)      # lower band at (S+e, e')
    slack_i = D - h / eta
    zero("part (i) three-term decomposition", slack_i - (t1 + t2 + t3))

    # 3. three-term nonnegative decomposition of part (ii)
    #    slack_ii = (1 - 1/eta) h - (g - d), identical three terms
    slack_ii = (1 - 1 / eta) * h - (g - d)
    zero("part (ii) three-term decomposition", slack_ii - (t1 + t2 + t3))

    # 4. the slacks of (i), of (ii) and of the first sharp-form inequality
    #    are one and the same rational function
    slack_sharp1 = (d - g / eta) - (1 - 1 / eta) * (g - h)
    zero("slack of (i) == slack of (ii)", slack_i - slack_ii)
    zero("slack of (ii) == slack of sharp form first inequality",
         slack_ii - slack_sharp1)

    # 5. the prediction slack at S itself:  d - g/eta, its own three terms
    u1 = (eo * d - P) / eo             # upper band at (S, e)
    u2 = (P - Q) / eo                  # hypothesis
    u3 = (eu * Q - g) / (eu * eo)      # lower band at (S, e')
    zero("prediction slack d - g/eta three-term decomposition",
         (d - g / eta) - (u1 + u2 + u3))
    # and it is the sum of the two sharp-form pieces
    zero("d - g/eta = slack_ii + (1-1/eta)(g-h)",
         (d - g / eta) - (slack_ii + (1 - 1 / eta) * (g - h)))

    # 6. the second sharp-form inequality: (1-1/eta)(g-h) >= 0 needs eta >= 1
    #    and submodularity g >= h.  Write it as a product of two nonneg factors.
    e1, s1 = sp.symbols("e1 s1", nonnegative=True)   # eta = 1 + e1, g - h = s1
    zero("(1-1/eta)(g-h) = e1*s1/(1+e1)",
         ((1 - 1 / (1 + e1)) * s1) - e1 * s1 / (1 + e1))

    # 7. corollary: eta > 1 and d = g/eta force h = g (given submodularity).
    #    d = g/eta makes slack_sharp1 = -(1-1/eta)(g-h) >= 0, while
    #    submodularity gives (1-1/eta)(g-h) >= 0, so both vanish.
    zero("corollary: d = g/eta makes slack_ii = -(1-1/eta)(g-h)",
         slack_sharp1.subs(d, g / eta) + (1 - 1 / eta) * (g - h))

    # 8. sanity: at eta = 1 both parts read d >= g
    zero("eta = 1 collapses (ii) to d - g", slack_ii.subs({eu: 1, eo: 1}) - (d - g))
    zero("eta = 1 collapses (i) to d - g", slack_i.subs({eu: 1, eo: 1}) - (d - g))

    COUNTS["C0_identities"] = len(ids)
    EXTRA["C0_identities"] = ids
    return check("C0 own sympy derivation of the slack decompositions [VERIFIED-SYMBOLIC]",
                 ok, "%d identities, every residual 0" % len(ids))


# ---------------------------------------------------------------------------
# exact set-function utilities
# ---------------------------------------------------------------------------
def is_monotone(n, tab):
    cnt = 0
    for m in range(1 << n):
        for i in range(n):
            if (m >> i) & 1:
                continue
            cnt += 1
            if tab[m | (1 << i)] < tab[m]:
                return False, cnt
    return True, cnt


def is_submodular(n, tab):
    cnt = 0
    for m in range(1 << n):
        free = [i for i in range(n) if not (m >> i) & 1]
        for a in range(len(free)):
            for b in range(a + 1, len(free)):
                i, j = free[a], free[b]
                cnt += 1
                if tab[m | (1 << i)] + tab[m | (1 << j)] < tab[m | (1 << i) | (1 << j)] + tab[m]:
                    return False, cnt
    return True, cnt


def band_factors(n, f, g):
    """Realized (eta_u, eta_o) of Definition 1 over the whole lattice.

    Convention B (results/V11/inputs/definition1.md): the two factors are NOT
    floored at 1, only their product eta = eta_u eta_o is, and that floor is
    automatic (any single pair with d > 0 gives eta_u eta_o >= 1).  Not
    flooring is what makes eta the SMALLEST admissible scalar error, hence the
    sharpest form of both inequalities."""
    eu = eo = None
    pairs = 0
    bad = False
    positive = 0
    for m in range(1 << n):
        for i in range(n):
            if (m >> i) & 1:
                continue
            pairs += 1
            d = f[m | (1 << i)] - f[m]
            dt = g[m | (1 << i)] - g[m]
            if d == 0:
                if dt != 0:
                    bad = True
                continue
            positive += 1
            if dt <= 0:
                bad = True
                continue
            if eu is None or d / dt > eu:
                eu = d / dt
            if eo is None or dt / d > eo:
                eo = dt / d
    if eu is None:
        eu = eo = Fr(1)
    return eu, eo, pairs, bad, positive


def band_factors_states(n, states, f, g):
    """Definition 1 restricted to a set of states (the trajectory band),
    same convention-B normalization as band_factors."""
    eu = eo = None
    pairs = 0
    bad = False
    for m in states:
        for i in range(n):
            if (m >> i) & 1:
                continue
            pairs += 1
            d = f[m | (1 << i)] - f[m]
            dt = g[m | (1 << i)] - g[m]
            if d == 0:
                if dt != 0:
                    bad = True
                continue
            if dt <= 0:
                bad = True
                continue
            if eu is None or d / dt > eu:
                eu = d / dt
            if eo is None or dt / d > eo:
                eo = dt / d
    if eu is None:
        eu = eo = Fr(1)
    return eu, eo, eu * eo, pairs, bad


# ---------------------------------------------------------------------------
# the triple test: this is the whole of Criterion C1/C2 and Criterion D search
# ---------------------------------------------------------------------------
class Acc(object):
    def __init__(self):
        self.triples = 0
        self.checks_i = 0
        self.checks_ii = 0
        self.checks_sharp1 = 0
        self.checks_sharp2 = 0
        self.checks_pred = 0
        self.decomp_terms = 0
        self.eq_i = 0
        self.eq_sharp2 = 0
        self.worst_slack = None       # (Fraction, info)
        self.worst_ratio = None       # (Fraction, info) ratio for part (i)
        self.worst_ratio_nt = None    # same, restricted to eta > 1 and h > 0
        self.worst_sharp2 = None
        self.nontrivial_triples = 0
        self.zero_d_triples = 0
        self.empty_S_triples = 0
        self.eta1_triples = 0


def test_triples(n, f, g, eta_u, eta_o, acc, tag, submodular, witnesses,
                 only_states=None, eta_override=None, record_violation=True):
    """Test every (S, e, e') with dtilde_e(S) >= dtilde_{e'}(S).

    Returns the number of violations found.
    """
    eta = eta_override if eta_override is not None else eta_u * eta_o
    viol = 0
    states = range(1 << n) if only_states is None else only_states
    for m in states:
        free = [i for i in range(n) if not (m >> i) & 1]
        for a in range(len(free)):
            for b in range(len(free)):
                if a == b:
                    continue
                e, ep = free[a], free[b]
                P = g[m | (1 << e)] - g[m]
                Q = g[m | (1 << ep)] - g[m]
                if P < Q:
                    continue        # hypothesis fails in this orientation
                if P == Q and e > ep:
                    continue        # tie: test the pair once per orientation set
                acc.triples += 1
                d = f[m | (1 << e)] - f[m]
                gg = f[m | (1 << ep)] - f[m]
                me = m | (1 << e)
                mep = m | (1 << ep)
                mm = m | (1 << e) | (1 << ep)
                h = f[mm] - f[me]
                D = f[mm] - f[mep]
                R = g[mm] - g[me]
                Pp = g[mm] - g[mep]
                if m == 0:
                    acc.empty_S_triples += 1
                if d == 0:
                    acc.zero_d_triples += 1
                if eta == 1:
                    acc.eta1_triples += 1

                # part (i)
                acc.checks_i += 1
                lhs_i = D
                rhs_i = h / eta
                slack = lhs_i - rhs_i
                if slack < 0:
                    viol += 1
                    if record_violation and len(witnesses) < 8:
                        witnesses.append({"part": "(i)", "tag": tag, "n": n,
                                          "S": setname(n, m), "e": e, "eprime": ep,
                                          "eta": str(eta), "d_e(S+e2)": str(D),
                                          "d_e2(S+e)": str(h), "slack": str(slack)})
                # part (ii)
                acc.checks_ii += 1
                slack_ii = (1 - Fr(1, 1) / eta) * h - (gg - d)
                if slack_ii < 0:
                    viol += 1
                    if record_violation and len(witnesses) < 8:
                        witnesses.append({"part": "(ii)", "tag": tag, "n": n,
                                          "S": setname(n, m), "e": e, "eprime": ep,
                                          "eta": str(eta), "d": str(d), "g": str(gg),
                                          "h": str(h), "slack": str(slack_ii)})
                if slack != slack_ii:
                    viol += 1
                    if record_violation and len(witnesses) < 8:
                        witnesses.append({"part": "slack_i != slack_ii", "tag": tag,
                                          "n": n, "S": setname(n, m),
                                          "e": e, "eprime": ep})

                # three-term decomposition (C2)
                t1 = (eta_o * D - Pp) / eta_o
                t2 = (P - Q) / eta_o
                t3 = (eta_u * R - h) / (eta_u * eta_o)
                acc.decomp_terms += 3
                if eta_override is None:
                    if t1 < 0 or t2 < 0 or t3 < 0 or (t1 + t2 + t3) != slack:
                        viol += 1
                        if record_violation and len(witnesses) < 8:
                            witnesses.append({"part": "decomposition", "tag": tag,
                                              "n": n, "S": setname(n, m), "e": e,
                                              "eprime": ep, "t1": str(t1),
                                              "t2": str(t2), "t3": str(t3),
                                              "slack": str(slack)})
                # prediction slack d - g/eta
                acc.checks_pred += 1
                if d - gg / eta < 0:
                    viol += 1
                    if record_violation and len(witnesses) < 8:
                        witnesses.append({"part": "pred d >= g/eta", "tag": tag,
                                          "n": n, "S": setname(n, m), "e": e,
                                          "eprime": ep, "d": str(d), "g": str(gg),
                                          "eta": str(eta)})
                # sharp form
                if submodular:
                    acc.checks_sharp1 += 1
                    s1 = (d - gg / eta) - (1 - Fr(1, 1) / eta) * (gg - h)
                    if s1 < 0:
                        viol += 1
                        if record_violation and len(witnesses) < 8:
                            witnesses.append({"part": "sharp form first", "tag": tag,
                                              "n": n, "S": setname(n, m), "e": e,
                                              "eprime": ep, "d": str(d), "g": str(gg),
                                              "h": str(h), "eta": str(eta),
                                              "slack": str(s1)})
                    acc.checks_sharp2 += 1
                    s2 = (1 - Fr(1, 1) / eta) * (gg - h)
                    if s2 < 0:
                        viol += 1
                        if record_violation and len(witnesses) < 8:
                            witnesses.append({"part": "sharp form second", "tag": tag,
                                              "n": n, "S": setname(n, m), "e": e,
                                              "eprime": ep, "g": str(gg), "h": str(h),
                                              "eta": str(eta), "slack": str(s2)})
                    if s2 == 0:
                        acc.eq_sharp2 += 1
                    info2 = {"tag": tag, "n": n, "S": setname(n, m), "e": e,
                             "eprime": ep, "eta": str(eta), "g": str(gg), "h": str(h)}
                    if acc.worst_sharp2 is None or s2 < acc.worst_sharp2[0]:
                        acc.worst_sharp2 = (s2, info2)

                info = {"tag": tag, "n": n, "S": setname(n, m), "e": e, "eprime": ep,
                        "eta": str(eta), "d": str(d), "g": str(gg), "h": str(h),
                        "d_e(S+e2)": str(D)}
                if slack == 0:
                    acc.eq_i += 1
                if acc.worst_slack is None or slack < acc.worst_slack[0]:
                    acc.worst_slack = (slack, info)
                if h > 0:
                    ratio = eta * D / h
                    if acc.worst_ratio is None or ratio < acc.worst_ratio[0]:
                        acc.worst_ratio = (ratio, info)
                    if eta > 1:
                        acc.nontrivial_triples += 1
                        if acc.worst_ratio_nt is None or ratio < acc.worst_ratio_nt[0]:
                            acc.worst_ratio_nt = (ratio, info)
    return viol


# ---------------------------------------------------------------------------
# random exact instances
# ---------------------------------------------------------------------------
def rnd_frac(rng, lo=0, hi=9, dens=(1, 2, 3, 4)):
    return Fr(rng.randint(lo, hi), rng.choice(dens))


def gen_modular(n, rng):
    w = [rnd_frac(rng, 0, 9) for _ in range(n)]
    tab = [Fr(0)] * (1 << n)
    for m in range(1 << n):
        s = Fr(0)
        for i in range(n):
            if (m >> i) & 1:
                s += w[i]
        tab[m] = s
    return tab, "modular"


def gen_coverage(n, rng):
    u = rng.randint(2, 6)
    wt = [rnd_frac(rng, 1, 8) for _ in range(u)]
    sets = [rng.getrandbits(u) for _ in range(n)]
    tab = [Fr(0)] * (1 << n)
    for m in range(1 << n):
        cov = 0
        for i in range(n):
            if (m >> i) & 1:
                cov |= sets[i]
        s = Fr(0)
        for j in range(u):
            if (cov >> j) & 1:
                s += wt[j]
        tab[m] = s
    return tab, "coverage"


def gen_concave_card(n, rng):
    inc = sorted([rnd_frac(rng, 0, 9) for _ in range(n)], reverse=True)
    pref = [Fr(0)]
    for v in inc:
        pref.append(pref[-1] + v)
    return [pref[pc(m)] for m in range(1 << n)], "concave_cardinality"


def gen_budget_additive(n, rng):
    w = [rnd_frac(rng, 0, 6) for _ in range(n)]
    tot = sum(w, Fr(0))
    B = tot * Fr(rng.randint(1, 3), 4) if tot > 0 else Fr(0)
    tab = [Fr(0)] * (1 << n)
    for m in range(1 << n):
        s = Fr(0)
        for i in range(n):
            if (m >> i) & 1:
                s += w[i]
        tab[m] = min(s, B)
    return tab, "budget_additive"


SUB_GENS = (gen_modular, gen_coverage, gen_concave_card, gen_budget_additive)


def gen_sub_mixture(n, rng):
    t1, n1 = rng.choice(SUB_GENS)(n, rng)
    t2, n2 = rng.choice(SUB_GENS)(n, rng)
    a = Fr(rng.randint(1, 4), rng.choice((1, 2, 3)))
    b = Fr(rng.randint(1, 4), rng.choice((1, 2, 3)))
    return [a * p + b * q for p, q in zip(t1, t2)], "mixture(%s,%s)" % (n1, n2)


SUB_ALL = SUB_GENS + (gen_sub_mixture,)


def gen_free_monotone(n, rng):
    """Monotone, generically NOT submodular: sweep by cardinality and set
    f(T) = max over parents + a random nonnegative increment."""
    tab = [None] * (1 << n)
    tab[0] = Fr(0)
    for m in sorted(range(1, 1 << n), key=pc):
        base = max(tab[m ^ (1 << i)] for i in range(n) if (m >> i) & 1)
        tab[m] = base + rnd_frac(rng, 0, 6)
    return tab, "free_monotone"


def gen_convex_card(n, rng):
    """Monotone supermodular-leaning: convex function of the cardinality."""
    inc = sorted([rnd_frac(rng, 0, 6) for _ in range(n)])
    pref = [Fr(0)]
    for v in inc:
        pref.append(pref[-1] + v)
    return [pref[pc(m)] for m in range(1 << n)], "convex_cardinality"


def gen_mono_mixture(n, rng):
    t1, n1 = rng.choice(SUB_ALL + (gen_free_monotone, gen_convex_card))(n, rng)
    t2, n2 = rng.choice(SUB_ALL + (gen_free_monotone, gen_convex_card))(n, rng)
    a = Fr(rng.randint(1, 3), rng.choice((1, 2)))
    b = Fr(rng.randint(1, 3), rng.choice((1, 2)))
    return [a * p + b * q for p, q in zip(t1, t2)], "mono_mix(%s,%s)" % (n1, n2)


MONO_ALL = (gen_free_monotone, gen_convex_card, gen_mono_mixture, gen_modular)

THETAS = (Fr(0), Fr(1, 4), Fr(1, 3), Fr(1, 2), Fr(2, 3), Fr(3, 4), Fr(1))
BANDS = ((Fr(1), Fr(1)), (Fr(1), Fr(3, 2)), (Fr(3, 2), Fr(1)), (Fr(2), Fr(1)),
         (Fr(1), Fr(2)), (Fr(3, 2), Fr(3, 2)), (Fr(2), Fr(2)), (Fr(5, 4), Fr(2)),
         (Fr(3), Fr(1)), (Fr(2), Fr(5, 2)))


def sample_ftilde(n, f, eu, eo, rng):
    """Random legal predictor.  The Definition 1 constraints are exactly the
    cover pairs (S, S+e), so sweeping by cardinality and drawing ftilde(T)
    inside the intersection of the parent intervals enforces all of them."""
    g = [None] * (1 << n)
    g[0] = Fr(0)
    for m in sorted(range(1, 1 << n), key=pc):
        lo = hi = None
        for i in range(n):
            if not (m >> i) & 1:
                continue
            s = m ^ (1 << i)
            d = f[m] - f[s]
            a = g[s] + d / eu
            b = g[s] + eo * d
            lo = a if lo is None or a > lo else lo
            hi = b if hi is None or b < hi else hi
        if lo > hi:
            return None
        th = rng.choice(THETAS)
        g[m] = lo + th * (hi - lo)
    return g


def run_random(target, seed, tag, gens, submodular, ns=(3, 4, 5, 6),
               force_eta1=False):
    rng = random.Random(seed)
    acc = Acc()
    witnesses = []
    fams = {}
    used = 0
    rejected = 0
    tries = 0
    viol = 0
    mono_checks = sub_checks = band_pairs = 0
    etas = {}
    while used < target and tries < target * 30:
        tries += 1
        n = rng.choice(ns)
        gen = rng.choice(gens)
        tab, fam = gen(n, rng)
        okm, cm = is_monotone(n, tab)
        mono_checks += cm
        if not okm:
            rejected += 1
            continue
        oks, cs = is_submodular(n, tab)
        sub_checks += cs
        if submodular and not oks:
            rejected += 1
            continue
        if (not submodular) and oks:
            # keep the monotone-only half strictly off the submodular cone
            # most of the time, but allow a fifth of them through so that the
            # submodular boundary is also exercised here
            if rng.randint(0, 4) != 0:
                rejected += 1
                continue
        if force_eta1:
            c = Fr(rng.randint(1, 5), rng.choice((1, 2, 3)))
            gt = [c * v for v in tab]
        else:
            eu0, eo0 = rng.choice(BANDS)
            gt = sample_ftilde(n, tab, eu0, eo0, rng)
            if gt is None:
                rejected += 1
                continue
        eu, eo, npairs, bad, npos = band_factors(n, tab, gt)
        band_pairs += npairs
        if bad:
            rejected += 1
            continue
        if npos == 0:
            rejected += 1
            continue
        eta = eu * eo
        if eta < 1:
            viol += 1
            witnesses.append({"part": "realized eta < 1", "n": n, "eta": str(eta)})
        used += 1
        fams[fam] = fams.get(fam, 0) + 1
        etas[str(eta)] = etas.get(str(eta), 0) + 1
        viol += test_triples(n, tab, gt, eu, eo, acc, tag, submodular, witnesses)
    return {"instances": used, "rejected": rejected, "families": fams,
            "eta_histogram": etas, "violations": viol, "witnesses": witnesses,
            "acc": acc, "mono_checks": mono_checks, "sub_checks": sub_checks,
            "band_pairs": band_pairs}


def merge_acc(a, b):
    for k in ("triples", "checks_i", "checks_ii", "checks_sharp1", "checks_sharp2",
              "checks_pred", "decomp_terms", "eq_i", "eq_sharp2", "zero_d_triples",
              "empty_S_triples", "eta1_triples", "nontrivial_triples"):
        setattr(a, k, getattr(a, k) + getattr(b, k))
    for k in ("worst_slack", "worst_ratio", "worst_ratio_nt", "worst_sharp2"):
        x, y = getattr(a, k), getattr(b, k)
        if y is not None and (x is None or y[0] < x[0]):
            setattr(a, k, y)
    return a


# ---------------------------------------------------------------------------
# C3 / C4: reruns of existing repository scripts, originals restored
# ---------------------------------------------------------------------------
def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def rerun(name, script, outputs):
    os.makedirs(RERUN_DIR, exist_ok=True)
    saved = {}
    for rel in outputs:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            saved[rel] = (sha(p), open(p, "rb").read())
    t0 = time.time()
    proc = subprocess.run([sys.executable, script], cwd=ROOT,
                          capture_output=True, text=True, timeout=1800)
    dt = round(time.time() - t0, 1)
    with open(os.path.join(RERUN_DIR, name + ".log"), "w") as fh:
        fh.write(proc.stdout + proc.stderr)
    fresh = {}
    for rel in outputs:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            shutil.copyfile(p, os.path.join(RERUN_DIR, os.path.basename(rel)))
            fresh[rel] = sha(p)
    restored = {}
    for rel, (h, data) in saved.items():
        p = os.path.join(ROOT, rel)
        with open(p, "wb") as fh:
            fh.write(data)
        restored[rel] = (sha(p) == h)
    rec = {"name": name, "script": os.path.relpath(script, ROOT),
           "exit_code": proc.returncode, "seconds": dt,
           "stdout_tail": proc.stdout.strip().splitlines()[-3:],
           "outputs_before_sha256": {k: v[0] for k, v in saved.items()},
           "outputs_after_rerun_sha256": fresh,
           "outputs_restored_bytewise": restored,
           "copy_dir": os.path.relpath(RERUN_DIR, ROOT)}
    SUBPROCS.append(rec)
    return proc, rec


def run_C3():
    proc, rec = rerun("H_J3_gate_check", HJ3_SCRIPT, HJ3_OUTPUTS)
    txt = proc.stdout
    lines = [l for l in txt.splitlines() if l.startswith("PASS ") or l.startswith("FAIL ")]
    npass = len([l for l in lines if l.startswith("PASS ")])
    nfail = len([l for l in lines if l.startswith("FAIL ")])
    sharp = [l for l in lines if "sharp form" in l]
    facet = [l for l in lines if "facet uniqueness" in l]
    rec["key_counts"] = {"PASS_lines": npass, "FAIL_lines": nfail,
                         "sharp_form_line": sharp, "facet_line": facet,
                         "all_pass": "ALL PASS" in txt}
    COUNTS["C3_HJ3_pass_lines"] = npass
    ok = proc.returncode == 0 and nfail == 0 and "ALL PASS" in txt and sharp
    return check("C3 rerun results/H_J3_gate_check.py [VERIFIED-SYMBOLIC + VERIFIED-LP 浮点]",
                 bool(ok),
                 "exit code %d, %d PASS / %d FAIL, ALL PASS, %.1fs; coherence line: %s; %s"
                 % (proc.returncode, npass, nfail, rec["seconds"],
                    (sharp or ["missing"])[0].strip(),
                    (facet or ["no facet line"])[0].strip()))


def run_C4():
    proc, rec = rerun("J2_core_oracles", J2_SCRIPT, J2_OUTPUTS)
    fresh = os.path.join(RERUN_DIR, "J2_core_oracles.json")
    data = {}
    if os.path.exists(fresh):
        data = json.load(open(fresh))
    ids = data.get("symbolic", {}).get("identities", {})
    coh_ids = {k: v for k, v in ids.items() if k.startswith("R6 ")}
    lp = data.get("R6_LP", {})
    mins = lp.get("minimum_slacks", {})
    counts = lp.get("counts_by_constraint_and_case", {})
    coh_mins = {k: v for k, v in mins.items() if k.startswith(("pred", "cons", "mono"))}
    coh_counts = {k: v for k, v in counts.items() if k.startswith(("pred", "cons", "mono"))}
    rec["key_counts"] = {"coherence_symbolic_identities": coh_ids,
                         "coherence_LP_minimum_slacks": coh_mins,
                         "coherence_LP_objective_counts": coh_counts,
                         "R6_LP_total_objectives": lp.get("lp_objectives"),
                         "all_passed": data.get("all_passed")}
    COUNTS["C4_J2_coherence_identities"] = len(coh_ids)
    COUNTS["C4_J2_coherence_LP_objectives"] = sum(coh_counts.values())
    need = {"R6 pred nonnegative-slack identity", "R6 cons nonnegative-slack identity"}
    ok = (proc.returncode == 0 and need.issubset(set(coh_ids))
          and all(v == "0" for k, v in coh_ids.items())
          and bool(coh_mins) and all(v >= -1e-8 for v in coh_mins.values())
          and data.get("all_passed") is True
          and all(rec["outputs_restored_bytewise"].values()))
    return check("C4 rerun results/J2_core_oracles.py, coherence part [VERIFIED-SYMBOLIC + VERIFIED-LP 浮点]",
                 bool(ok),
                 "exit code %d, %.1fs, %d R6 identities with residual 0, %d coherence LP objectives, min slacks %s, json restored byte-identical"
                 % (proc.returncode, rec["seconds"], len(coh_ids),
                    sum(coh_counts.values()),
                    json.dumps(coh_mins, sort_keys=True)))


# ---------------------------------------------------------------------------
# C5 running example: K = 3, eta = 3/2 exact worst-case trajectory
# ---------------------------------------------------------------------------
def run_C5():
    K, eta = 3, Fr(3, 2)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    Vj = lambda j: 1 - q ** j * (1 - Fr(K - j, 1) / (K * eta))
    j = 2                                   # eta = 3/2 lies in (K-j, K-j+1) = (1,2)
    dts = [q ** t / k1 if t < j else q ** j / (K * eta) for t in range(K)]
    gts = [q ** min(t, j) / K for t in range(K + 1)]
    rows = []
    ok = True
    for t in range(K):
        d, g, h = dts[t], gts[t], gts[t + 1]
        s1 = (d - g / eta) - (1 - Fr(1, 1) / eta) * (g - h)
        s2 = (1 - Fr(1, 1) / eta) * (g - h)
        rows.append({"t": t, "d": str(d), "g": str(g), "h": str(h),
                     "d-g/eta": str(d - g / eta),
                     "(1-1/eta)(g-h)": str(s2),
                     "sharp_first_slack": str(s1), "equality": s1 == 0})
        if s1 < 0 or s2 < 0:
            ok = False
    rho = min(Vj(i) for i in range(K))
    ok = ok and sum(dts) == Vj(j) == rho == Fr(9, 16)
    ok = ok and all(r["equality"] for r in rows)
    EXTRA["running_example"] = {
        "K": K, "eta": str(eta), "j": j, "k1": str(k1), "q": str(q),
        "V": {str(i): str(Vj(i)) for i in range(K)},
        "rho_3(3/2)": str(rho), "sum_d_t": str(sum(dts)),
        "d_t": [str(x) for x in dts], "g_t": [str(x) for x in gts],
        "steps": rows,
        "corollary_check_t2": "d = g/eta = 1/8 and h = g = 3/16, as the "
                              "ledger corollary (eta > 1 and d = g/eta force h = g) predicts"}
    COUNTS["C5_steps"] = K
    return check("C5 running example K=3 eta=3/2 worst-case trajectory [VERIFIED-EXHAUSTIVE]",
                 ok,
                 "d_t = %s, g_t = %s, rho_3(3/2) = sum d_t = %s; sharp form is an equality at all 3 steps"
                 % ("(" + ", ".join(str(x) for x in dts) + ")",
                    "(" + ", ".join(str(x) for x in gts) + ")", rho))


# ---------------------------------------------------------------------------
# Criterion D structured cases
# ---------------------------------------------------------------------------
def run_D1():
    r = run_random(200, SEED_D1, "D1_eta1", SUB_ALL, True, ns=(3, 4, 5),
                   force_eta1=True)
    a = r["acc"]
    ok = r["violations"] == 0 and a.triples > 0 and a.eta1_triples == a.triples
    detail = ("200 instances with ftilde = c f (eta = 1 exactly): %d triples, "
              "every one has eta = 1, both parts collapse to d >= g, %d of them "
              "are equalities (d = g), 0 violations" % (a.triples, a.eq_i))
    EXTRA["D1"] = {"instances": r["instances"], "triples": a.triples,
                   "equalities": a.eq_i, "violations": r["violations"],
                   "families": r["families"]}
    check("D1 eta = 1 (equalities)", ok, detail)
    return r


def run_D2(pool):
    """d_e(S) = 0 cases, harvested from the C1 pool plus a dedicated family."""
    rng = random.Random(SEED_D2)
    acc = Acc()
    witnesses = []
    viol = 0
    inst = 0
    forced = 0
    for _ in range(900):
        n = rng.choice((3, 4, 5))
        # a saturating budget-additive f has many zero marginals
        tab, fam = gen_budget_additive(n, rng)
        okm, _ = is_monotone(n, tab)
        if not okm:
            continue
        eu0, eo0 = rng.choice(BANDS)
        gt = sample_ftilde(n, tab, eu0, eo0, rng)
        if gt is None:
            continue
        eu, eo, _, bad, npos = band_factors(n, tab, gt)
        if bad or npos == 0:
            continue
        inst += 1
        before = acc.zero_d_triples
        viol += test_triples(n, tab, gt, eu, eo, acc, "D2_zero_d", True, witnesses)
        forced += acc.zero_d_triples - before
    # in every d_e(S) = 0 triple Definition 1 forces dtilde_e(S) = 0, and the
    # hypothesis then forces dtilde_{e'}(S) = 0, hence g = 0 as well
    ok = viol == 0 and acc.zero_d_triples > 0
    EXTRA["D2"] = {"instances": inst, "triples_with_d_e(S)=0": acc.zero_d_triples,
                   "all_triples": acc.triples, "violations": viol}
    COUNTS["D2_zero_d_triples"] = acc.zero_d_triples
    check("D2 d_e(S) = 0 cases", ok,
          "%d budget-additive instances, %d of the %d triples have d_e(S) = 0 "
          "(Definition 1 then forces dtilde_e(S) = 0 and, by the hypothesis, "
          "dtilde_{e'}(S) = d_{e'}(S) = 0, so (i) reads h >= h/eta and (ii) "
          "reads (1-1/eta) h >= 0), 0 violations"
          % (inst, acc.zero_d_triples, acc.triples))
    return acc, viol


def run_D3():
    """S = empty only."""
    rng = random.Random(SEED_D3)
    acc = Acc()
    witnesses = []
    viol = 0
    inst = 0
    for _ in range(400):
        n = rng.choice((3, 4, 5, 6))
        gen = rng.choice(SUB_ALL + MONO_ALL)
        tab, fam = gen(n, rng)
        okm, _ = is_monotone(n, tab)
        if not okm:
            continue
        eu0, eo0 = rng.choice(BANDS)
        gt = sample_ftilde(n, tab, eu0, eo0, rng)
        if gt is None:
            continue
        eu, eo, _, bad, npos = band_factors(n, tab, gt)
        if bad or npos == 0:
            continue
        subm, _ = is_submodular(n, tab)
        inst += 1
        viol += test_triples(n, tab, gt, eu, eo, acc, "D3_empty_S", subm,
                             witnesses, only_states=[0])
    ok = viol == 0 and acc.triples > 0
    EXTRA["D3"] = {"instances": inst, "triples": acc.triples, "violations": viol}
    COUNTS["D3_empty_S_triples"] = acc.triples
    check("D3 S = empty", ok,
          "%d instances restricted to S = empty, %d triples, 0 violations"
          % (inst, acc.triples))
    return acc, viol


def run_D4():
    """must-not-claim: the lemma FAILS if the band is only assumed on the run
    states.  One explicit witness plus a randomized count."""
    # --- explicit instance -------------------------------------------------
    # N = {e, e'} = {0, 1}; f(empty)=0, f({e})=1, f({e'})=2, f({e,e'})=2.
    # monotone and submodular.  ftilde: 0, 1, 1, 3/2.
    n = 2
    f = [Fr(0), Fr(1), Fr(2), Fr(2)]       # index bit0 = e, bit1 = e'
    ft = [Fr(0), Fr(1), Fr(1), Fr(3, 2)]
    okm, _ = is_monotone(n, f)
    oks, _ = is_submodular(n, f)
    # predictive greedy from empty: dtilde_e = dtilde_{e'} = 1, adversarial tie
    # picks e, so the run states are S^0 = empty and S^1 = {e}.
    states = [0b00, 0b01]
    eu_tr, eo_tr, eta_tr, npairs_tr, bad_tr = band_factors_states(n, states, f, ft)
    eu_g, eo_g, _, bad_g, _ = band_factors(n, f, ft)
    d = f[0b01] - f[0]                      # d_e(S)      = 1
    g = f[0b10] - f[0]                      # d_{e'}(S)   = 2
    h = f[0b11] - f[0b01]                   # d_{e'}(S+e) = 1
    D = f[0b11] - f[0b10]                   # d_e(S+e')   = 0
    slack_ii = (1 - Fr(1, 1) / eta_tr) * h - (g - d)
    slack_i = D - h / eta_tr
    # off-trajectory pair that breaks the global band
    d_off = f[0b11] - f[0b10]               # d_e({e'}) = 0
    dt_off = ft[0b11] - ft[0b10]            # dtilde_e({e'}) = 1/2 > 0
    hyp = (ft[0b01] - ft[0]) >= (ft[0b10] - ft[0])
    ok = (okm and oks and hyp and not bad_tr and bad_g
          and eta_tr == 2 and slack_ii < 0 and slack_i < 0
          and d_off == 0 and dt_off > 0)
    witness = {
        "n": 2, "elements": {"e": 0, "eprime": 1},
        "f": {"empty": "0", "{e}": "1", "{e'}": "2", "{e,e'}": "2"},
        "ftilde": {"empty": "0", "{e}": "1", "{e'}": "1", "{e,e'}": "3/2"},
        "f_monotone": okm, "f_submodular": oks,
        "hypothesis dtilde_e(S) >= dtilde_{e'}(S)": "1 >= 1, holds",
        "run_states": ["empty", "{e}"],
        "eta_trajectory": str(eta_tr), "eta_u_tr": str(eu_tr), "eta_o_tr": str(eo_tr),
        "global_band_legal": not bad_g,
        "off_trajectory_state": "{e'}",
        "d_e({e'})": str(d_off), "dtilde_e({e'})": str(dt_off),
        "why_global_band_fails": "Definition 1 forces dtilde = 0 where d = 0; "
                                 "here d_e({e'}) = 0 but dtilde_e({e'}) = 1/2, "
                                 "so the global eta is infinite",
        "(ii) at eta^tr": "(1 - 1/2)*1 = 1/2 >= 2 - 1 = 1 is FALSE, slack = %s" % slack_ii,
        "(i) at eta^tr": "d_e({e'}) = 0 >= 1/2 * d_{e'}({e}) = 1/2 is FALSE, slack = %s" % slack_i,
    }
    EXTRA["D4_explicit"] = witness
    check("D4a must-not-claim: explicit instance, band only on the run states",
          ok,
          "f = (0,1,2,2), ftilde = (0,1,1,3/2) on N = {e,e'}; run states "
          "{empty, {e}} carry eta^tr = 2 with no violation of Definition 1, "
          "the off-trajectory state {e'} has d_e = 0 < dtilde_e = 1/2 so the "
          "GLOBAL band is infinite; at eta^tr = 2 both parts fail: "
          "(ii) slack = %s, (i) slack = %s" % (slack_ii, slack_i))

    # --- randomized count --------------------------------------------------
    rng = random.Random(SEED_D4)
    tested = 0
    inst = 0
    bad_inst = 0
    worst = None
    for _ in range(800):
        n = rng.choice((3, 4))
        gen = rng.choice(SUB_ALL)
        tab, fam = gen(n, rng)
        okm, _ = is_monotone(n, tab)
        oks, _ = is_submodular(n, tab)
        if not (okm and oks):
            continue
        # a predictor that is legal ONLY on the two states empty and {e0}
        ft2 = [None] * (1 << n)
        ft2[0] = Fr(0)
        eu0, eo0 = rng.choice(BANDS[1:])
        for m in sorted(range(1, 1 << n), key=pc):
            i = min(j for j in range(n) if (m >> j) & 1)
            s = m ^ (1 << i)
            dd = tab[m] - tab[s]
            ft2[m] = ft2[s] + (dd / eu0 if rng.randint(0, 1) else eo0 * dd)
        # trajectory: empty -> {e0} where e0 = argmax dtilde at empty
        cands = sorted(range(n), key=lambda i: (-(ft2[1 << i] - ft2[0]), i))
        e0 = cands[0]
        states = [0, 1 << e0]
        eu, eo, eta_tr, _, bad = band_factors_states(n, states, tab, ft2)
        if bad:
            continue
        inst += 1
        found = False
        for ep in range(n):
            if ep == e0:
                continue
            P = ft2[1 << e0] - ft2[0]
            Q = ft2[1 << ep] - ft2[0]
            if P < Q:
                continue
            tested += 1
            d = tab[1 << e0]
            g = tab[1 << ep]
            h = tab[(1 << e0) | (1 << ep)] - tab[1 << e0]
            s = (1 - Fr(1, 1) / eta_tr) * h - (g - d)
            if s < 0:
                found = True
                if worst is None or s < worst[0]:
                    worst = (s, {"n": n, "family": fam, "eta_tr": str(eta_tr),
                                 "e": e0, "eprime": ep, "d": str(d), "g": str(g),
                                 "h": str(h), "slack": str(s)})
        if found:
            bad_inst += 1
    EXTRA["D4_random"] = {"instances_with_legal_trajectory_band": inst,
                          "triples_tested": tested,
                          "instances_with_a_violation": bad_inst,
                          "worst_slack": str(worst[0]) if worst else None,
                          "worst_witness": worst[1] if worst else None}
    COUNTS["D4_traj_only_triples"] = tested
    COUNTS["D4_traj_only_violating_instances"] = bad_inst
    check("D4b must-not-claim: randomized count of trajectory-only band failures",
          tested > 0,
          "%d instances whose predictor is legal on the run states {empty, {e0}}, "
          "%d triples tested at eta^tr, %d instances violate (ii); worst slack %s"
          % (inst, tested, bad_inst, str(worst[0]) if worst else "none"))
    return ok


def run_D5():
    """The SECOND sharp-form inequality needs submodularity of f."""
    # N = {e, e'}; f(empty)=0, f({e})=1, f({e'})=1, f({e,e'})=3: monotone,
    # not submodular.  g = 1, h = 2, so g - h = -1 < 0.
    n = 2
    f = [Fr(0), Fr(1), Fr(1), Fr(3)]
    ft = [Fr(0), Fr(1), Fr(1), Fr(3)]       # eta = 1 predictor, legal
    okm, _ = is_monotone(n, f)
    oks, _ = is_submodular(n, f)
    eu, eo, _, bad, _ = band_factors(n, f, ft)
    eta = eu * eo
    d = f[0b01] - f[0]
    g = f[0b10] - f[0]
    h = f[0b11] - f[0b01]
    D = f[0b11] - f[0b10]
    s2 = (1 - Fr(1, 1) / eta) * (g - h)
    s_i = D - h / eta
    s_ii = (1 - Fr(1, 1) / eta) * h - (g - d)
    # at eta = 1 the factor (1-1/eta) is 0, so take a second instance with eta > 1
    ft2 = [Fr(0), Fr(1), Fr(1), Fr(2)]      # dtilde_{e'}({e}) = 1 vs d = 2
    eu2, eo2, _, bad2, _ = band_factors(n, f, ft2)
    eta2 = eu2 * eo2
    h2 = f[0b11] - f[0b01]
    s2b = (1 - Fr(1, 1) / eta2) * (g - h2)
    s_ib = D - h2 / eta2
    s_iib = (1 - Fr(1, 1) / eta2) * h2 - (g - d)
    ok = (okm and not oks and not bad and not bad2
          and s_i >= 0 and s_ii >= 0 and s_ib >= 0 and s_iib >= 0
          and g - h < 0 and s2b < 0)
    EXTRA["D5"] = {
        "f": {"empty": "0", "{e}": "1", "{e'}": "1", "{e,e'}": "3"},
        "f_monotone": okm, "f_submodular": oks,
        "instance_1": {"ftilde": "(0,1,1,3)", "eta": str(eta),
                       "g-h": str(g - h), "second_sharp_slack": str(s2),
                       "part_i_slack": str(s_i), "part_ii_slack": str(s_ii)},
        "instance_2": {"ftilde": "(0,1,1,2)", "eta": str(eta2),
                       "g-h": str(g - h2), "second_sharp_slack": str(s2b),
                       "part_i_slack": str(s_ib), "part_ii_slack": str(s_iib)},
        "reading": "parts (i) and (ii) survive without submodularity; the "
                   "second sharp-form inequality (1-1/eta)(g-h) >= 0 does not"}
    check("D5 the second sharp-form inequality needs submodularity", ok,
          "f = (0,1,1,3) is monotone and not submodular: g - h = -1 < 0; with "
          "ftilde = (0,1,1,2) the realized eta = 2 and (1-1/eta)(g-h) = -1/2 < 0, "
          "while (i) slack = %s and (ii) slack = %s stay nonnegative"
          % (s_ib, s_iib))
    return ok


# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("V11 Q5b oracle: lem:coherence (ledger T5) and its sharp form")
    print("repo root: " + ROOT)
    print("exact arithmetic: fractions.Fraction and sympy; seeds mono=%d sub=%d "
          "eta1=%d zero_d=%d emptyS=%d traj=%d"
          % (SEED_MONO, SEED_SUB, SEED_D1, SEED_D2, SEED_D3, SEED_D4))
    print("actual eta = realized band over the whole lattice (the smallest "
          "admissible eta, hence the sharpest form of both inequalities)")
    print()
    print("--- Criterion C ---")
    run_C0()

    rm = run_random(N_MONO, SEED_MONO, "C1_monotone", MONO_ALL, False)
    rs = run_random(N_SUB, SEED_SUB, "C1_submodular", SUB_ALL, True)
    acc = merge_acc(rm["acc"], rs["acc"])
    viol = rm["violations"] + rs["violations"]
    wits = rm["witnesses"] + rs["witnesses"]
    WITNESSES.extend(wits)
    COUNTS.update({
        "C1_instances_monotone_only": rm["instances"],
        "C1_instances_submodular": rs["instances"],
        "C1_instances_total": rm["instances"] + rs["instances"],
        "C1_triples": acc.triples,
        "C1_checks_part_i": acc.checks_i,
        "C1_checks_part_ii": acc.checks_ii,
        "C1_checks_sharp_first": acc.checks_sharp1,
        "C1_checks_sharp_second": acc.checks_sharp2,
        "C1_checks_prediction": acc.checks_pred,
        "C1_decomposition_terms": acc.decomp_terms,
        "C1_equality_triples_part_i": acc.eq_i,
        "C1_monotonicity_checks": rm["mono_checks"] + rs["mono_checks"],
        "C1_submodularity_checks": rm["sub_checks"] + rs["sub_checks"],
        "C1_band_pairs": rm["band_pairs"] + rs["band_pairs"],
        "C1_rejected_draws": rm["rejected"] + rs["rejected"],
    })
    EXTRA["C1_families"] = {"monotone_only": rm["families"],
                            "submodular": rs["families"]}
    EXTRA["C1_eta_histogram"] = {"monotone_only": rm["eta_histogram"],
                                 "submodular": rs["eta_histogram"]}
    check("C1 random exact instances: parts (i), (ii) and the sharp form [VERIFIED-EXHAUSTIVE]",
          viol == 0,
          "%d instances (%d monotone only, %d monotone submodular; n in 3..6), "
          "%d triples with dtilde_e(S) >= dtilde_{e'}(S), %d checks of (i), "
          "%d of (ii), %d of the sharp form first inequality, %d of the second, "
          "%d of d >= g/eta; %d monotonicity and %d submodularity checks, "
          "%d band pairs, %d draws rejected"
          % (rm["instances"] + rs["instances"], rm["instances"], rs["instances"],
             acc.triples, acc.checks_i, acc.checks_ii, acc.checks_sharp1,
             acc.checks_sharp2, acc.checks_pred,
             rm["mono_checks"] + rs["mono_checks"],
             rm["sub_checks"] + rs["sub_checks"],
             rm["band_pairs"] + rs["band_pairs"],
             rm["rejected"] + rs["rejected"]),
          extra={"violations": viol})
    check("C2 three-term nonnegative decomposition on every triple [VERIFIED-EXHAUSTIVE]",
          viol == 0,
          "%d nonnegative terms (3 per triple), each term >= 0 and the three "
          "summing exactly to the slack of (i) = slack of (ii)"
          % acc.decomp_terms)

    run_C3()
    run_C4()
    run_C5()

    print()
    print("--- Criterion D ---")
    rd1 = run_D1()
    acc_d2, v_d2 = run_D2(None)
    acc_d3, v_d3 = run_D3()
    run_D4()
    run_D5()

    total_random = (rm["instances"] + rs["instances"] + rd1["instances"]
                    + EXTRA["D2"]["instances"] + EXTRA["D3"]["instances"]
                    + EXTRA["D4_random"]["instances_with_legal_trajectory_band"])
    COUNTS["D_random_instances_total"] = total_random
    total_viol = viol + rd1["violations"] + v_d2 + v_d3
    COUNTS["D_violations"] = total_viol

    acc_all = merge_acc(merge_acc(merge_acc(acc, rd1["acc"]), acc_d2), acc_d3)
    ws = acc_all.worst_slack
    wr = acc_all.worst_ratio
    wn = acc_all.worst_ratio_nt
    w2 = acc_all.worst_sharp2
    print()
    print("counts: " + json.dumps(COUNTS, sort_keys=True))
    print("running example K=3 eta=3/2: " + json.dumps(EXTRA["running_example"]["steps"]))
    print("worst slack of (ii) = slack of (i): %s at %s"
          % (ws[0], json.dumps(ws[1], sort_keys=True)))
    print("worst ratio eta*d_e(S+e')/d_{e'}(S+e) (claimed >= 1): %s at %s"
          % (wr[0], json.dumps(wr[1], sort_keys=True)))
    print("worst ratio restricted to eta > 1 and d_{e'}(S+e) > 0 (%d triples): %s at %s"
          % (acc_all.nontrivial_triples, wn[0], json.dumps(wn[1], sort_keys=True)))
    print("worst slack of the second sharp-form inequality (submodular half): %s at %s"
          % (w2[0], json.dumps(w2[1], sort_keys=True)))
    print("triples attaining equality in (i)/(ii): %d of %d"
          % (acc_all.eq_i, acc_all.triples))
    print("violations: %d" % total_viol)

    failed = [c for c in CHECKS if c["status"] != "PASS"]
    out = {
        "script": os.path.abspath(__file__),
        "statement": "lem:coherence (T5): f monotone, S subset N, e,e' not in S, "
                     "dtilde_e(S) >= dtilde_{e'}(S)  =>  (i) d_e(S+e') >= "
                     "d_{e'}(S+e)/eta and (ii) (1-1/eta) d_{e'}(S+e) >= "
                     "d_{e'}(S) - d_e(S); sharp form d - g/eta >= (1-1/eta)(g-h) "
                     ">= 0 with d = d_e(S), g = d_{e'}(S), h = d_{e'}(S+e), the "
                     "second inequality using submodularity of f",
        "sources": {
            "statement": "results/V11/inputs/statement_coherence.md",
            "definition": "results/V11/inputs/definition1.md (convention B)",
            "route_one": "paper/sections/appendix_proofs.tex subsection app:coherence",
            "sharp_form_certificate": "results/H_J3_gate_check.py",
            "three_term_decomposition": "results/J2_core_oracles.py (symbolic_core, R6_full_lattice_lp)",
            "ledger": "THEOREM_LEDGER.md section T5",
        },
        "seeds": {"C1_monotone": SEED_MONO, "C1_submodular": SEED_SUB,
                  "D1_eta1": SEED_D1, "D2_zero_d": SEED_D2,
                  "D3_empty_S": SEED_D3, "D4_trajectory": SEED_D4},
        "counts": COUNTS,
        "criterion_C": {"checks": CHECKS},
        "criterion_D": {
            "random_instances": total_random,
            "violations": total_viol,
            "witnesses": WITNESSES,
            "structured": {
                "D1_eta_equals_1": EXTRA.get("D1"),
                "D2_d_e_S_zero": EXTRA.get("D2"),
                "D3_S_empty": EXTRA.get("D3"),
                "D4_trajectory_band_only_explicit": EXTRA.get("D4_explicit"),
                "D4_trajectory_band_only_random": EXTRA.get("D4_random"),
                "D5_second_sharp_needs_submodularity": EXTRA.get("D5"),
            },
            "worst_slack_part_ii": {"value": str(ws[0]), "at": ws[1]},
            "worst_ratio_part_i": {"value": str(wr[0]), "float": float(wr[0]),
                                   "at": wr[1]},
            "worst_ratio_part_i_eta_gt_1": {"value": str(wn[0]),
                                            "float": float(wn[0]),
                                            "triples": acc_all.nontrivial_triples,
                                            "at": wn[1]},
            "worst_slack_second_sharp": {"value": str(w2[0]), "at": w2[1]},
            "equality_triples": acc_all.eq_i,
            "total_triples": acc_all.triples,
        },
        "running_example": EXTRA.get("running_example"),
        "symbolic_identities": EXTRA.get("C0_identities"),
        "families": EXTRA.get("C1_families"),
        "eta_histogram": EXTRA.get("C1_eta_histogram"),
        "reruns": SUBPROCS,
        "elapsed_seconds": round(time.time() - t0, 1),
        "all_passed": not failed,
        "failed_checks": [c["name"] for c in failed],
    }
    with open(JSON_PATH, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=False, default=str)
    print("json written: " + JSON_PATH)
    print("OVERALL: %s (%d checks, %d failed, %.1fs)"
          % ("PASS" if not failed else "FAIL", len(CHECKS), len(failed),
             time.time() - t0))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

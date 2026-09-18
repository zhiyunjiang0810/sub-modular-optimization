#!/usr/bin/env python3
"""V11 Q5a oracle for prop:guarantee (ledger T3, attribution Goundan-Schulz 2007).

Statement under test (results/V11/inputs/statement_guarantee.md):

    Let f be monotone submodular with f(empty) = 0 and let T = S^K be the output
    of a run of predictive greedy whose selection error is eta^sel
    (Definition def:etasel, with L_K(infinity) = 0).  Then, with
    L_K(x) = 1 - (1 - 1/(xK))^K,

        f(T) >= L_K(eta^sel) f(O*) >= (1 - e^{-1/eta^sel}) f(O*).

    If moreover the predictor has finite error (eta_u, eta_o), the same bound
    holds with eta^sel replaced by eta^tr or by eta, and the three bounds are
    ordered L_K(eta^sel) >= L_K(eta^tr) >= L_K(eta).

Definition def:etasel (paper/sections/model.tex, line 84):
    M_t = max_{e not in S^t} d_e(S^t),  g_t = d_{e_t}(S^t),
    a_t = M_t/g_t if g_t > 0;  a_t = 1 if M_t = g_t = 0;  a_t = infinity if
    g_t = 0 < M_t;  eta^sel = max{1, a_0, ..., a_{K-1}}.

Route-one proof material:
    paper/sections/appendix_proofs.tex, subsection app:guarantee (~line 215):
    Step 1 covering inequality r_t <= K M_t and the contraction
    r_{t+1} <= (1 - 1/(eta^sel K)) r_t; Step 2 the zero-gain steps; Step 3 the
    unrolling; Step 4 the chain eta^sel <= eta^tr <= eta.
    Remark rem:app-product: the sharper per-step product bound
    f(S^K) >= (1 - prod_t (1 - 1/(K a_t))) f(O*).
Ledger card: THEOREM_LEDGER.md section T3.

Criterion C (oracle)
  C0  sympy identities on L_K: closed form, L_K(1), L_1(x) = 1/x, strict
      decrease in x, the exponential relaxation 1 - u <= e^{-u} behind
      L_K(x) >= 1 - e^{-1/x}, the K -> infinity limit, the L_K(infinity) = 0
      convention, and the Step-3 unrolling identity.       [VERIFIED-SYMBOLIC]
  C1  >= 2000 random exact instances (monotone submodular f, n <= 7, K <= 4,
      legal ftilde with its realized factors (eta_u, eta_o)), predictive greedy
      run for exactly K steps with adversarial ties (all tie paths enumerated
      when their number is at most TIE_CAP, otherwise the worst over sampled
      tie paths): f(T) >= L_K(eta^sel) OPT and the ordering
      L_K(eta^sel) >= L_K(eta^tr) >= L_K(eta), equivalently
      eta^sel <= eta^tr <= eta.                            [VERIFIED-EXHAUSTIVE]
  C2  on every state of every run of C1: the Step-1 covering inequality
      r_t <= K M_t, and the Step-1 contraction at steps with g_t > 0.
                                                           [VERIFIED-EXHAUSTIVE]
  C3  auxiliary, on the same runs: the per-step product bound of
      rem:app-product, which implies the L_K bound.  Reported separately: it is
      a remark, not the Proposition.                       [VERIFIED-EXHAUSTIVE]
  C4  a legal predictor never produces a harmful zero step, so eta^sel is
      finite whenever the global band is finite (the model.tex claim that
      a_t = infinity cannot occur then).                   [VERIFIED-EXHAUSTIVE]
  C5  exact tightness of L_K on the family U_K of app:tightness (Theorem D
      instances), rebuilt in rational arithmetic for K = 2..5 and
      ahat in {3/2, 2, 3}: the adversarial (all-B) run has eta^sel = ahat
      exactly and f(T)/OPT = L_K(ahat) exactly, while the global eta is
      (ahat K - 1)/(K - 1) and L_K(eta) is strictly smaller.
                                                           [VERIFIED-EXHAUSTIVE]
  C6  rerun results/F2_etasel_tight.py, record exit code and key counts.
                                             [VERIFIED-LP 浮点] (float pipeline)
  C7  rerun results/T5_symbolic.py, record exit code and key counts.
                                                           [VERIFIED-SYMBOLIC]

Criterion D (counterexample search on the statement itself)
  The random instances of C1 are the search for f(T) >= L_K(eta^sel) OPT; any
  violation is reported with its witness.  Structured cases: a run with a
  harmful zero step (eta^sel = infinity, bound 0), a benign zero step
  (a_t = 1), eta = 1 (ftilde = c f), K = 1, K = n.

Every decision uses fractions.Fraction or sympy; floats appear only in printed
text and inside the two rerun repository scripts.  Seeds fixed.  No existing
repository file is modified: the two rerun scripts write their own output files
in place, so this script saves those bytes first, copies the fresh outputs into
results/V11/oracle/reruns/ and restores the originals, verifying the sha256.

Run:  python3 results/V11/oracle/guarantee.py
Exit code 0 iff every check passed.  Writes results/V11/oracle/guarantee.json.
"""

from fractions import Fraction as Fr
from itertools import combinations
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
JSON_PATH = os.path.join(HERE, "guarantee.json")
RERUN_DIR = os.path.join(HERE, "reruns")

F2_SCRIPT = os.path.join(ROOT, "results", "F2_etasel_tight.py")
F2_OUTPUTS = ["results/F2_etasel_tight.txt"]
T5_SCRIPT = os.path.join(ROOT, "results", "T5_symbolic.py")
T5_OUTPUTS = ["results/T5_symbolic.json"]

SEED_C1 = 20260918          # random exact instances
SEED_ETA1 = 20260919        # structured case eta = 1
SEED_KN = 20260920          # structured case K = n
SEED_K1 = 20260921          # structured case K = 1

TIE_CAP = 400               # enumerate all tie paths up to this many leaves
TIE_SAMPLES = 40            # otherwise: worst over this many sampled tie paths
N_RANDOM = 2400             # accepted random instances for C1

INF = None                  # sentinel for a_t = infinity / eta^sel = infinity

CHECKS = []
VIOLATIONS = []
WITNESSES = []
COUNTS = {}
SUBPROCS = []


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


def names(n, m):
    return "{" + ",".join(chr(ord("a") + i) for i in range(n) if (m >> i) & 1) + "}"


# ---------------------------------------------------------------------------
# L_K and the selection error
# ---------------------------------------------------------------------------
def L_K(x, K):
    """L_K(x) = 1 - (1 - 1/(xK))^K, exact; L_K(infinity) = 0 by convention."""
    if x is INF:
        return Fr(0)
    return Fr(1) - (Fr(1) - Fr(1, 1) / (x * K)) ** K


def leq(x, y):
    """x <= y with the sentinel INF as +infinity."""
    if x is INF:
        return y is INF
    if y is INF:
        return True
    return x <= y


# ---------------------------------------------------------------------------
# exact set-function utilities
# ---------------------------------------------------------------------------
def validity(n, tab):
    """Exhaustive: f(empty) = 0, monotone, submodular (local exchange form)."""
    ok_norm = tab[0] == 0
    ok_mono = ok_sub = True
    n_mono = n_sub = 0
    for m in range(1 << n):
        free = [i for i in range(n) if not (m >> i) & 1]
        base = tab[m]
        for i in free:
            n_mono += 1
            if tab[m | (1 << i)] < base:
                ok_mono = False
        for idx, i in enumerate(free):
            for j in free[idx + 1:]:
                n_sub += 1
                if tab[m | (1 << i)] + tab[m | (1 << j)] < tab[m | (1 << i) | (1 << j)] + base:
                    ok_sub = False
    return ok_norm, ok_mono, ok_sub, n_mono, n_sub


def band_factors(n, f, g):
    """Smallest admissible (eta_u, eta_o) of Definition 1 over the whole lattice.

    Returns (eta_u, eta_o, n_pairs, bad) where bad is True when some pair has
    d = 0 < dtilde or d > 0 >= dtilde, which Definition 1 forbids.
    """
    eu = eo = Fr(1)
    pairs = 0
    bad = False
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
            if dt <= 0:
                bad = True
                continue
            if d / dt > eu:
                eu = d / dt
            if dt / d > eo:
                eo = dt / d
    return eu, eo, pairs, bad


def traj_band(n, states, f, g):
    """Definition 1 restricted to the states of the run: eta^tr.

    Returns (eta_u_tr, eta_o_tr, eta_tr, n_pairs, bad).
    """
    eu = eo = Fr(1)
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
            if d / dt > eu:
                eu = d / dt
            if dt / d > eo:
                eo = dt / d
    return eu, eo, eu * eo, pairs, bad


def opt_value(n, K, tab):
    """OPT = max over |S| <= K of f(S), exact, with one maximizer."""
    best = Fr(0)
    arg = 0
    for m in range(1 << n):
        if pc(m) <= K and tab[m] > best:
            best = tab[m]
            arg = m
    return best, arg


# ---------------------------------------------------------------------------
# predictive greedy with adversarial ties
# ---------------------------------------------------------------------------
def step_ties(n, m, g):
    """Every element attaining the maximum predicted gain at state m."""
    best = None
    ties = []
    for e in range(n):
        if (m >> e) & 1:
            continue
        dt = g[m | (1 << e)] - g[m]
        if best is None or dt > best:
            best = dt
            ties = [e]
        elif dt == best:
            ties.append(e)
    return ties


def run_stats(n, K, f, g, picks):
    """One fixed tie resolution: states, a_t list, eta^sel, T."""
    m = 0
    states = []
    a_list = []
    steps = []
    for e in picks:
        states.append(m)
        M_t = Fr(0)
        first = True
        for c in range(n):
            if (m >> c) & 1:
                continue
            d = f[m | (1 << c)] - f[m]
            if first or d > M_t:
                M_t = d
                first = False
        g_t = f[m | (1 << e)] - f[m]
        if g_t > 0:
            a = M_t / g_t
        elif M_t == 0:
            a = Fr(1)
        else:
            a = INF
        a_list.append(a)
        steps.append({"t": len(steps), "state": m, "pick": e,
                      "M_t": M_t, "g_t": g_t, "a_t": a})
        m |= 1 << e
    eta_sel = Fr(1)
    for a in a_list:
        if a is INF:
            eta_sel = INF
            break
        if a > eta_sel:
            eta_sel = a
    return {"T": m, "states": states, "a_list": a_list, "steps": steps,
            "eta_sel": eta_sel, "picks": list(picks)}


def all_tie_paths(n, K, g, cap):
    """Every adversarial tie resolution, or None if there are more than cap."""
    out = []

    def rec(m, picks):
        if len(picks) == K:
            out.append(tuple(picks))
            return True
        for e in step_ties(n, m, g):
            picks.append(e)
            ok = rec(m | (1 << e), picks)
            picks.pop()
            if not ok:
                return False
            if len(out) > cap:
                return False
        return True

    return out if rec(0, []) else None


def sample_tie_paths(n, K, g, rng, nsamp):
    """Random tie resolutions (fallback when the tie tree is too large)."""
    seen = set()
    for _ in range(nsamp):
        m = 0
        picks = []
        for _ in range(K):
            ties = step_ties(n, m, g)
            e = ties[rng.randrange(len(ties))]
            picks.append(e)
            m |= 1 << e
        seen.add(tuple(picks))
    return [list(p) for p in seen]


def greedy_runs(n, K, f, g, rng):
    """All runs of predictive greedy under adversarial ties.

    Returns (runs, mode) with mode in {"enumerated", "sampled"}.
    """
    paths = all_tie_paths(n, K, g, TIE_CAP)
    if paths is not None:
        mode = "enumerated"
    else:
        paths = sample_tie_paths(n, K, g, rng, TIE_SAMPLES)
        mode = "sampled"
    return [run_stats(n, K, f, g, p) for p in paths], mode


# ---------------------------------------------------------------------------
# the checks applied to one run
# ---------------------------------------------------------------------------
def test_run(tag, n, K, f, g, run, opt, eta, eta_tr, acc, legal):
    """Main inequality, ordering, Step-1 covering, product bound.  Exact."""
    ok = True
    T = run["T"]
    eta_sel = run["eta_sel"]
    Ls = L_K(eta_sel, K)
    acc["runs"] += 1

    if opt == 0:
        acc["trivial"] += 1
    else:
        ratio = f[T] / opt
        acc["main_checks"] += 1
        if ratio < Ls:
            ok = False
            w = {"where": tag + ": f(T) >= L_K(eta^sel) OPT",
                 "n": n, "K": K, "eta_sel": "infinity" if eta_sel is INF else str(eta_sel),
                 "ratio": str(ratio), "bound": str(Ls),
                 "f_table": [str(v) for v in f], "ftilde_table": [str(v) for v in g],
                 "picks": run["picks"]}
            VIOLATIONS.append(w)
            WITNESSES.append(w)
        slack = ratio - Ls
        if slack == 0:
            acc["equality_runs"] += 1
        rec = {"tag": tag, "n": n, "K": K,
               "eta_sel": "infinity" if eta_sel is INF else str(eta_sel),
               "ratio": str(ratio), "bound": str(Ls),
               "family": acc.get("family", "")}
        if slack < acc["worst_main"][0]:
            acc["worst_main"] = (slack, rec)
        # the same, restricted to the informative regime K >= 2 and eta^sel > 1
        if K >= 2 and eta_sel is not INF and eta_sel > 1 and slack < acc["worst_nontrivial"][0]:
            acc["worst_nontrivial"] = (slack, rec)
        # the sharper per-step product bound of rem:app-product (auxiliary)
        prod = Fr(1)
        for a in run["a_list"]:
            if a is INF:
                continue          # factor 1 - 1/(K*infinity) = 1
            prod *= (Fr(1) - Fr(1, 1) / (K * a))
        pbound = Fr(1) - prod
        acc["product_checks"] += 1
        if ratio < pbound:
            ok = False
            w = {"where": tag + ": rem:app-product f(T) >= (1 - prod(1-1/(K a_t))) OPT",
                 "n": n, "K": K, "ratio": str(ratio), "bound": str(pbound),
                 "a_list": ["infinity" if a is INF else str(a) for a in run["a_list"]],
                 "f_table": [str(v) for v in f], "ftilde_table": [str(v) for v in g],
                 "picks": run["picks"]}
            VIOLATIONS.append(w)
            WITNESSES.append(w)
        if ratio - pbound < acc["worst_product"][0]:
            acc["worst_product"] = (ratio - pbound,
                                    {"tag": tag, "n": n, "K": K,
                                     "ratio": str(ratio), "bound": str(pbound)})

    # Step 1 of app:guarantee: r_t <= K M_t at every state, and the contraction
    for st in run["steps"]:
        m = st["state"]
        r_t = opt - f[m]
        acc["cover_checks"] += 1
        if r_t > K * st["M_t"]:
            ok = False
            VIOLATIONS.append({"where": tag + ": Step 1 covering r_t <= K M_t",
                               "n": n, "K": K, "t": st["t"],
                               "r_t": str(r_t), "K*M_t": str(K * st["M_t"])})
        if st["g_t"] > 0 and st["a_t"] is not INF:
            acc["contract_checks"] += 1
            # r_{t+1} <= (1 - 1/(a_t K)) r_t  with r_t clipped at 0
            r_next = opt - f[m | (1 << st["pick"])]
            rhs = (Fr(1) - Fr(1, 1) / (st["a_t"] * K)) * max(r_t, Fr(0))
            if r_next > rhs:
                ok = False
                VIOLATIONS.append({"where": tag + ": Step 1 contraction",
                                   "n": n, "K": K, "t": st["t"],
                                   "r_next": str(r_next), "rhs": str(rhs)})

    if legal:
        # Step 4: the chain eta^sel <= eta^tr <= eta, and the L_K ordering
        acc["chain_checks"] += 1
        if eta_sel is INF:
            ok = False
            w = {"where": tag + ": legal band but eta^sel = infinity (C4)",
                 "n": n, "K": K, "eta": str(eta),
                 "f_table": [str(v) for v in f], "ftilde_table": [str(v) for v in g],
                 "picks": run["picks"]}
            VIOLATIONS.append(w)
            WITNESSES.append(w)
        if not (leq(eta_sel, eta_tr) and eta_tr <= eta):
            ok = False
            VIOLATIONS.append({"where": tag + ": chain eta^sel <= eta^tr <= eta",
                               "n": n, "K": K,
                               "eta_sel": "infinity" if eta_sel is INF else str(eta_sel),
                               "eta_tr": str(eta_tr), "eta": str(eta),
                               "picks": run["picks"]})
        Lt, Lg = L_K(eta_tr, K), L_K(eta, K)
        if not (Ls >= Lt >= Lg):
            ok = False
            VIOLATIONS.append({"where": tag + ": L_K(eta^sel) >= L_K(eta^tr) >= L_K(eta)",
                               "n": n, "K": K, "L_sel": str(Ls),
                               "L_tr": str(Lt), "L_eta": str(Lg)})
        if opt > 0:
            acc["global_checks"] += 1
            ratio = f[T] / opt
            for nm, b in (("eta^tr", Lt), ("eta", Lg)):
                if ratio < b:
                    ok = False
                    w = {"where": tag + ": f(T) >= L_K(%s) OPT" % nm,
                         "n": n, "K": K, "ratio": str(ratio), "bound": str(b),
                         "f_table": [str(v) for v in f],
                         "ftilde_table": [str(v) for v in g],
                         "picks": run["picks"]}
                    VIOLATIONS.append(w)
                    WITNESSES.append(w)
    return ok


# ---------------------------------------------------------------------------
# C0: sympy identities
# ---------------------------------------------------------------------------
def check_C0():
    x, u, r, K = sp.symbols("x u r K", positive=True)
    ident = []

    for Kc in range(1, 9):
        lhs = 1 - (1 - 1 / (x * Kc)) ** Kc
        # closed form at x = 1 is the classical greedy bound
        ident.append(("L_%d(1) = 1-(1-1/%d)^%d" % (Kc, Kc, Kc),
                      sp.simplify(lhs.subs(x, 1) - (1 - sp.Rational(Kc - 1, Kc) ** Kc))))
        # strictly decreasing in x for x >= 1: derivative is negative
        d = sp.simplify(sp.diff(lhs, x))
        neg = sp.simplify(d * x ** 2 * (1 - 1 / (x * Kc)) ** (1 - Kc))
        ident.append(("d/dx L_%d(x) = -(1-1/(%d x))^{%d-1}/x^2" % (Kc, Kc, Kc),
                      sp.simplify(neg + 1)))
        # limit x -> infinity is 0, the L_K(infinity) = 0 convention
        ident.append(("lim_{x->oo} L_%d(x) = 0" % Kc,
                      sp.simplify(sp.limit(lhs, x, sp.oo))))
    # L_1(x) = 1/x
    ident.append(("L_1(x) = 1/x", sp.simplify((1 - (1 - 1 / x)) - 1 / x)))
    # exponential relaxation: h(u) = K log(1-u) + K u has h(0) = 0 and
    # h'(u) = -K u/(1-u) <= 0, which is what gives L_K(x) >= 1 - e^{-1/x}
    h = K * sp.log(1 - u) + K * u
    ident.append(("h(0) = 0", sp.simplify(h.subs(u, 0))))
    ident.append(("h'(u) + K u/(1-u) = 0",
                  sp.simplify(sp.diff(h, u) + K * u / (1 - u))))
    # K -> infinity limit of L_K(x)
    Kp = sp.symbols("Kp", positive=True)
    ident.append(("lim_{K->oo} L_K(x) = 1 - e^{-1/x}",
                  sp.simplify(sp.limit(1 - (1 - 1 / (x * Kp)) ** Kp, Kp, sp.oo)
                              - (1 - sp.exp(-1 / x)))))
    # Step 3 unrolling: r_K <= (1-1/(xK))^K r_0 gives f(S^K) >= L_K(x) r_0
    ident.append(("Step 3: r_0 - (1-1/(xK))^K r_0 = L_K(x) r_0",
                  sp.simplify(r - (1 - 1 / (x * K)) ** K * r
                              - (1 - (1 - 1 / (x * K)) ** K) * r)))
    # Step 1 contraction composed K times
    ident.append(("Step 1 composed: prod of K equal factors",
                  sp.simplify(sp.prod([(1 - 1 / (x * 3))] * 3) - (1 - 1 / (3 * x)) ** 3)))

    bad = [nm for nm, res in ident if sp.simplify(res) != 0]
    COUNTS["C0_identities"] = len(ident)
    return check("C0 sympy identities on L_K [VERIFIED-SYMBOLIC]",
                 not bad,
                 "%d identities, residual 0" % len(ident) if not bad
                 else "nonzero residual: %s" % bad)


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


BASE_GENS = (gen_modular, gen_coverage, gen_concave_card, gen_budget_additive)


def gen_mixture(n, rng):
    t1, n1 = rng.choice(BASE_GENS)(n, rng)
    t2, n2 = rng.choice(BASE_GENS)(n, rng)
    a = Fr(rng.randint(1, 4), rng.choice((1, 2, 3)))
    b = Fr(rng.randint(1, 4), rng.choice((1, 2, 3)))
    return [a * p + b * q for p, q in zip(t1, t2)], "mixture(%s,%s)" % (n1, n2)


ALL_GENS = BASE_GENS + (gen_mixture,)
THETAS = (Fr(0), Fr(1, 4), Fr(1, 3), Fr(1, 2), Fr(2, 3), Fr(3, 4), Fr(1))


def sample_ftilde(n, f, eu, eo, rng):
    """Random legal predictor: the Definition 1 constraints are exactly the
    cover pairs (S, S+e), so sweeping the lattice by cardinality and drawing
    ftilde(T) inside the intersection of the intervals enforces all of them."""
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


def run_random(target, seed, tag, ns=(3, 4, 5, 6, 7), Ks=(1, 2, 3, 4), eta1=False):
    rng = random.Random(seed)
    acc = {"runs": 0, "trivial": 0, "main_checks": 0, "product_checks": 0,
           "cover_checks": 0, "contract_checks": 0, "chain_checks": 0,
           "global_checks": 0, "equality_runs": 0,
           "worst_main": (Fr(10 ** 6), {}), "worst_nontrivial": (Fr(10 ** 6), {}),
           "worst_product": (Fr(10 ** 6), {}), "family": ""}
    fams = {}
    used = 0
    rejected = 0
    enumerated = sampled = 0
    ok_all = True
    tries = 0
    while used < target and tries < target * 20:
        tries += 1
        n = rng.choice([v for v in ns])
        K = rng.choice([v for v in Ks if v <= n])
        f, fname = rng.choice(ALL_GENS)(n, rng)
        ok_norm, ok_mono, ok_sub, nm, nsb = validity(n, f)
        if not (ok_norm and ok_mono and ok_sub):
            rejected += 1
            continue
        if eta1:
            c = Fr(rng.randint(1, 5), rng.choice((1, 2, 3)))
            g = [c * v for v in f]
        else:
            eu = rng.choice((Fr(1), Fr(5, 4), Fr(3, 2), Fr(2)))
            eo = rng.choice((Fr(1), Fr(5, 4), Fr(3, 2), Fr(2), Fr(3)))
            g = None
            for _ in range(12):
                g = sample_ftilde(n, f, eu, eo, rng)
                if g is not None:
                    break
            if g is None:
                rejected += 1
                continue
        au, ao, npairs, bad = band_factors(n, f, g)
        if bad:
            rejected += 1
            continue
        eta = au * ao
        opt, _ = opt_value(n, K, f)
        runs, mode = greedy_runs(n, K, f, g, rng)
        if mode == "enumerated":
            enumerated += 1
        else:
            sampled += 1
        acc["family"] = fname
        for run in runs:
            _, _, eta_tr, _, tbad = traj_band(n, run["states"], f, g)
            ok_all &= test_run(tag, n, K, f, g, run, opt, eta, eta_tr, acc,
                               legal=not tbad)
        used += 1
        fams[fname] = fams.get(fname, 0) + 1
        COUNTS.setdefault(tag + "_mono_checks", 0)
        COUNTS[tag + "_mono_checks"] += nm
        COUNTS.setdefault(tag + "_submod_checks", 0)
        COUNTS[tag + "_submod_checks"] += nsb
        COUNTS.setdefault(tag + "_band_pairs", 0)
        COUNTS[tag + "_band_pairs"] += npairs
    return {"used": used, "rejected": rejected, "families": fams, "acc": acc,
            "ok": ok_all, "enumerated": enumerated, "sampled": sampled}


# ---------------------------------------------------------------------------
# C5: the U_K tightness family in exact arithmetic
# ---------------------------------------------------------------------------
def build_UK(K, ahat):
    """app:tightness family, exact rationals.  n = 2K, B = {0..K-1} (low bits),
    O = {K..2K-1}.  F(x,y) = 1 - a^x (1 - y/K);  G(x,0) = 1 - a^x,
    G(x,y) = 1 - a^{x+1}(K-y)/(K-1) for y >= 1."""
    a = Fr(1) - Fr(1, 1) / (ahat * K)
    n = 2 * K
    f = [Fr(0)] * (1 << n)
    g = [Fr(0)] * (1 << n)
    for m in range(1 << n):
        x = pc(m & ((1 << K) - 1))
        y = pc(m >> K)
        f[m] = Fr(1) - a ** x * (Fr(1) - Fr(y, K))
        if y == 0:
            g[m] = Fr(1) - a ** x
        else:
            g[m] = Fr(1) - a ** (x + 1) * Fr(K - y, K - 1)
    return a, n, f, g


def run_C5():
    rows = []
    ok_all = True
    n_inst = 0
    for K in (2, 3, 4, 5):
        for ahat in (Fr(3, 2), Fr(2), Fr(3)):
            a, n, f, g = build_UK(K, ahat)
            ok_norm, ok_mono, ok_sub, _, _ = validity(n, f)
            opt, _ = opt_value(n, K, f)
            # adversarial tie resolution: ties go to B
            picks = list(range(K))
            for t in range(K):
                ties = step_ties(n, sum(1 << i for i in picks[:t]), g)
                if picks[t] not in ties:
                    ok_all = False
                    VIOLATIONS.append({"where": "C5 U_K: all-B path is not a tie path",
                                       "K": K, "ahat": str(ahat), "t": t,
                                       "ties": ties})
            run = run_stats(n, K, f, g, picks)
            eta_sel = run["eta_sel"]
            ratio = f[run["T"]] / opt
            LK = L_K(ahat, K)
            eta_glob = Fr(ahat * K - 1, 1) / (K - 1)
            eu, eo, npairs, bad = band_factors(n, f, g)
            row = {"K": K, "ahat": str(ahat), "n": n, "opt": str(opt),
                   "eta_sel": "infinity" if eta_sel is INF else str(eta_sel),
                   "ratio": str(ratio), "L_K(ahat)": str(LK),
                   "eta_global": str(eu * eo), "eta_global_formula": str(eta_glob),
                   "L_K(eta)": str(L_K(eu * eo, K)),
                   "equality": ratio == LK and eta_sel == ahat}
            rows.append(row)
            n_inst += 1
            good = (ok_norm and ok_mono and ok_sub and not bad
                    and eta_sel == ahat and ratio == LK
                    and eu * eo == eta_glob and L_K(eu * eo, K) < LK)
            if not good:
                ok_all = False
                VIOLATIONS.append({"where": "C5 U_K exact tightness", **row,
                                   "monotone": ok_mono, "submodular": ok_sub,
                                   "band_ok": not bad})
    COUNTS["C5_instances"] = n_inst
    check("C5 U_K exact tightness of L_K under eta^sel [VERIFIED-EXHAUSTIVE]",
          ok_all,
          "%d instances (K=2..5 x ahat in {3/2,2,3}), ratio = L_K(ahat) and "
          "eta^sel = ahat exactly on every one" % n_inst)
    return rows, ok_all


# ---------------------------------------------------------------------------
# C6 / C7: reruns of existing repository scripts, originals restored
# ---------------------------------------------------------------------------
def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def rerun(name, script, outputs, label):
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
    log = os.path.join(RERUN_DIR, name + ".log")
    with open(log, "w") as fh:
        fh.write(proc.stdout + proc.stderr)
    fresh = {}
    for rel in outputs:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            dst = os.path.join(RERUN_DIR, os.path.basename(rel))
            shutil.copyfile(p, dst)
            fresh[rel] = sha(p)
    restored = {}
    for rel, (h, data) in saved.items():
        p = os.path.join(ROOT, rel)
        with open(p, "wb") as fh:
            fh.write(data)
        restored[rel] = (sha(p) == h)
    rec = {"name": name, "script": os.path.relpath(script, ROOT),
           "exit_code": proc.returncode, "seconds": dt,
           "stdout_tail": proc.stdout.strip().splitlines()[-4:],
           "outputs_before_sha256": {k: v[0] for k, v in saved.items()},
           "outputs_after_rerun_sha256": fresh,
           "outputs_restored_bytewise": restored,
           "copy_dir": os.path.relpath(RERUN_DIR, ROOT)}
    SUBPROCS.append(rec)
    return proc, rec


def run_C6():
    proc, rec = rerun("F2_etasel_tight", F2_SCRIPT, F2_OUTPUTS, "C6")
    txt = proc.stdout
    n_pass = len([l for l in txt.splitlines()
                  if l.rstrip().endswith("PASS") and l.strip()[:1].isdigit()])
    status = "ALL PASS" in txt
    rec["key_counts"] = {"table_rows_PASS": n_pass,
                         "status_line": [l for l in txt.splitlines()
                                         if l.startswith("STATUS:")]}
    COUNTS["C6_F2_rows_PASS"] = n_pass
    return check("C6 rerun results/F2_etasel_tight.py [VERIFIED-LP 浮点]",
                 proc.returncode == 0 and status and all(rec["outputs_restored_bytewise"].values()),
                 "exit code %d, %s, %d PASS rows, %.1fs, output file restored byte-identical"
                 % (proc.returncode,
                    (rec["key_counts"]["status_line"] or ["no STATUS line"])[0],
                    n_pass, rec["seconds"]))


def run_C7():
    proc, rec = rerun("T5_symbolic", T5_SCRIPT, T5_OUTPUTS, "C7")
    txt = proc.stdout
    total = [l for l in txt.splitlines() if l.startswith("TOTAL:")]
    rec["key_counts"] = {"total_line": total,
                         "all_pass": "ALL PASS" in txt}
    n_pass = n_fail = None
    jp = os.path.join(RERUN_DIR, "T5_symbolic.json")
    if os.path.exists(jp):
        d = json.load(open(jp))
        n_pass, n_fail = d.get("n_pass"), d.get("n_fail")
        rec["key_counts"].update({"n_pass": n_pass, "n_fail": n_fail,
                                  "allpairs_exhaustive_K": d.get("allpairs_exhaustive_K")})
    COUNTS["C7_T5_checks_pass"] = n_pass
    return check("C7 rerun results/T5_symbolic.py [VERIFIED-SYMBOLIC]",
                 proc.returncode == 0 and "ALL PASS" in txt and n_fail == 0
                 and all(rec["outputs_restored_bytewise"].values()),
                 "exit code %d, %s, n_pass=%s n_fail=%s, %.1fs, output file restored "
                 "byte-identical" % (proc.returncode, (total or ["no TOTAL line"])[0],
                                     n_pass, n_fail, rec["seconds"]))


# ---------------------------------------------------------------------------
# Criterion D: structured cases
# ---------------------------------------------------------------------------
def structured_harmful_zero():
    """A run with a harmful zero step: eta^sel = infinity, the bound is 0.

    f modular with weights (0, 1, 1) on (a, b, c); ftilde(S) = |S|, which is an
    illegal predictor (d_a = 0 < dtilde_a = 1 breaks Definition 1), so ties send
    greedy to a at step 0: M_0 = 1 > 0 = g_0, hence a_0 = infinity.
    """
    n, K = 3, 2
    w = [Fr(0), Fr(1), Fr(1)]
    f = [sum((w[i] for i in range(n) if (m >> i) & 1), Fr(0)) for m in range(1 << n)]
    g = [Fr(pc(m)) for m in range(1 << n)]
    ok_norm, ok_mono, ok_sub, _, _ = validity(n, f)
    _, _, _, bad = band_factors(n, f, g)
    opt, om = opt_value(n, K, f)
    run = run_stats(n, K, f, g, [0, 1])       # adversarial ties: a first
    eta_sel = run["eta_sel"]
    ratio = f[run["T"]] / opt
    bound = L_K(eta_sel, K)
    ok = (ok_norm and ok_mono and ok_sub and bad and eta_sel is INF
          and bound == 0 and ratio >= bound and run["a_list"][0] is INF)
    detail = ("f = (0,1,1) modular, ftilde = |S|; a_0 = infinity, eta^sel = infinity, "
              "L_2(infinity) = 0, f(T) = %s, OPT = %s, ratio = %s >= 0; the predictor is "
              "illegal under Definition 1 (d_a = 0 < dtilde_a), which is why the case "
              "exists at all" % (f[run["T"]], opt, ratio))
    check("D1 harmful zero step (eta^sel = infinity, bound 0)", ok, detail)
    return {"case": "harmful zero step", "n": n, "K": K, "ok": ok,
            "eta_sel": "infinity", "bound": "0", "ratio": str(ratio),
            "f(T)": str(f[run["T"]]), "OPT": str(opt), "OPT_set": names(n, om),
            "legal_predictor": not bad, "detail": detail}


def structured_benign_zero():
    """A benign zero step: M_t = g_t = 0, a_t = 1, the run already has OPT."""
    n, K = 3, 3
    f = [Fr(0) if m == 0 else Fr(1) for m in range(1 << n)]     # coverage of one item
    g = list(f)
    ok_norm, ok_mono, ok_sub, _, _ = validity(n, f)
    _, _, _, bad = band_factors(n, f, g)
    opt, _ = opt_value(n, K, f)
    runs, mode = greedy_runs(n, K, f, g, random.Random(1))
    ok = ok_norm and ok_mono and ok_sub and not bad
    zero_steps = 0
    for run in runs:
        for st in run["steps"]:
            if st["g_t"] == 0 and st["M_t"] == 0:
                zero_steps += 1
                ok &= (st["a_t"] == Fr(1))
        ok &= (run["eta_sel"] == Fr(1))
        ok &= (f[run["T"]] / opt >= L_K(run["eta_sel"], K))
    detail = ("f(S) = 1 for S nonempty, ftilde = f, K = n = 3: %d runs, %d benign zero "
              "steps, every a_t = 1, eta^sel = 1, ratio 1 >= L_3(1) = %s"
              % (len(runs), zero_steps, L_K(Fr(1), 3)))
    check("D2 benign zero step (M_t = g_t = 0, a_t = 1)", ok, detail)
    return {"case": "benign zero step", "n": n, "K": K, "ok": ok,
            "runs": len(runs), "zero_steps": zero_steps, "detail": detail}


def structured_eta1():
    res = run_random(160, SEED_ETA1, "D3", ns=(3, 4, 5, 6), Ks=(1, 2, 3, 4), eta1=True)
    acc = res["acc"]
    ok = res["ok"] and res["used"] == 160
    COUNTS["D3_eta1_instances"] = res["used"]
    detail = ("%d random instances with ftilde = c f (eta = 1): %d runs, "
              "worst slack f(T)/OPT - L_K(eta^sel) = %s"
              % (res["used"], acc["runs"], acc["worst_main"][0]))
    check("D3 eta = 1 (ftilde = c f)", ok, detail)
    return {"case": "eta = 1 (ftilde = c f)", "ok": ok, "instances": res["used"],
            "runs": acc["runs"], "worst_slack": str(acc["worst_main"][0]),
            "detail": detail}


def structured_K1():
    res = run_random(240, SEED_K1, "D4", ns=(2, 3, 4, 5, 6, 7), Ks=(1,))
    acc = res["acc"]
    ok = res["ok"] and res["used"] == 240
    COUNTS["D4_K1_instances"] = res["used"]
    detail = ("%d random instances with K = 1 (L_1(x) = 1/x): %d runs, "
              "worst slack = %s" % (res["used"], acc["runs"], acc["worst_main"][0]))
    check("D4 K = 1", ok, detail)
    return {"case": "K = 1", "ok": ok, "instances": res["used"], "runs": acc["runs"],
            "worst_slack": str(acc["worst_main"][0]), "detail": detail}


def structured_Kn():
    """K = n: predictive greedy takes the whole ground set, so f(T) = OPT."""
    rng = random.Random(SEED_KN)
    used = 0
    ok = True
    worst = Fr(10 ** 6)
    runs_total = 0
    while used < 200:
        n = rng.choice((2, 3, 4))
        K = n
        f, _ = rng.choice(ALL_GENS)(n, rng)
        ok_norm, ok_mono, ok_sub, _, _ = validity(n, f)
        if not (ok_norm and ok_mono and ok_sub):
            continue
        eu = rng.choice((Fr(1), Fr(5, 4), Fr(3, 2), Fr(2)))
        eo = rng.choice((Fr(1), Fr(5, 4), Fr(3, 2), Fr(2)))
        g = None
        for _ in range(12):
            g = sample_ftilde(n, f, eu, eo, rng)
            if g is not None:
                break
        if g is None:
            continue
        au, ao, _, bad = band_factors(n, f, g)
        if bad:
            continue
        opt, _ = opt_value(n, K, f)
        runs, _ = greedy_runs(n, K, f, g, rng)
        for run in runs:
            runs_total += 1
            if run["T"] != (1 << n) - 1:
                ok = False
                VIOLATIONS.append({"where": "D5 K = n: output is not the ground set",
                                   "n": n, "K": K, "T": run["T"]})
            if opt > 0:
                ratio = f[run["T"]] / opt
                b = L_K(run["eta_sel"], K)
                if ratio < b:
                    ok = False
                    VIOLATIONS.append({"where": "D5 K = n: f(T) >= L_K(eta^sel) OPT",
                                       "n": n, "K": K, "ratio": str(ratio),
                                       "bound": str(b)})
                worst = min(worst, ratio - b)
        used += 1
    COUNTS["D5_Kn_instances"] = used
    detail = ("%d random instances with K = n: %d runs, every output is the ground "
              "set, f(T) = OPT, worst slack = %s" % (used, runs_total, worst))
    check("D5 K = n", ok, detail)
    return {"case": "K = n", "ok": ok, "instances": used, "runs": runs_total,
            "worst_slack": str(worst), "detail": detail}


# ---------------------------------------------------------------------------
# running example K = 3, eta = 3/2
# ---------------------------------------------------------------------------
def running_example():
    K, ahat = 3, Fr(3, 2)
    a, n, f, g = build_UK(K, ahat)
    opt, _ = opt_value(n, K, f)
    run = run_stats(n, K, f, g, [0, 1, 2])
    eu, eo, _, _ = band_factors(n, f, g)
    eta = eu * eo
    _, _, eta_tr, _, _ = traj_band(n, run["states"], f, g)
    return {"K": K, "eta_sel": str(run["eta_sel"]), "eta_tr": str(eta_tr),
            "eta": str(eta),
            "L_3(3/2)": str(L_K(Fr(3, 2), 3)),
            "L_3(eta_tr)": str(L_K(eta_tr, 3)),
            "L_3(eta)": str(L_K(eta, 3)),
            "f(T)": str(f[run["T"]]), "OPT": str(opt),
            "ratio": str(f[run["T"]] / opt),
            "a_list": [str(v) for v in run["a_list"]],
            "L_3(3/2)_float": float(L_K(Fr(3, 2), 3)),
            "L_3(eta)_float": float(L_K(eta, 3))}


# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("V11 Q5a oracle: prop:guarantee (ledger T3, Goundan-Schulz 2007)")
    print("repo root: %s" % ROOT)
    print("exact arithmetic: fractions.Fraction and sympy; seeds C1=%d eta1=%d "
          "K1=%d Kn=%d" % (SEED_C1, SEED_ETA1, SEED_K1, SEED_KN))
    print("tie policy: all tie paths enumerated when at most %d, else worst over "
          "%d sampled tie paths" % (TIE_CAP, TIE_SAMPLES))
    print()

    print("--- Criterion C ---")
    check_C0()
    res = run_random(N_RANDOM, SEED_C1, "C1")
    acc = res["acc"]
    check("C1 random exact instances: f(T) >= L_K(eta^sel) OPT and the ordering "
          "[VERIFIED-EXHAUSTIVE]",
          res["ok"] and res["used"] >= 2000,
          "%d instances (n <= 7, K <= 4), %d greedy runs, %d main-inequality checks, "
          "%d ordering checks, %d tie trees enumerated, %d sampled, %d draws rejected"
          % (res["used"], acc["runs"], acc["main_checks"], acc["chain_checks"],
             res["enumerated"], res["sampled"], res["rejected"]))
    check("C2 Step-1 covering r_t <= K M_t and the contraction "
          "[VERIFIED-EXHAUSTIVE]",
          not [v for v in VIOLATIONS if "Step 1" in v["where"]],
          "%d covering checks, %d contraction checks over the C1 runs"
          % (acc["cover_checks"], acc["contract_checks"]))
    check("C3 auxiliary rem:app-product per-step product bound "
          "[VERIFIED-EXHAUSTIVE]",
          not [v for v in VIOLATIONS if "rem:app-product" in v["where"]],
          "%d checks, worst slack %s" % (acc["product_checks"],
                                         acc["worst_product"][0]))
    check("C4 legal band implies finite eta^sel [VERIFIED-EXHAUSTIVE]",
          not [v for v in VIOLATIONS if "(C4)" in v["where"]],
          "%d runs on legal predictors, no harmful zero step" % acc["chain_checks"])
    c5_rows, _ = run_C5()
    run_C6()
    run_C7()
    print()

    print("--- Criterion D ---")
    d_rows = [structured_harmful_zero(), structured_benign_zero(),
              structured_eta1(), structured_K1(), structured_Kn()]
    print()

    COUNTS["C1_random_instances"] = res["used"]
    COUNTS["C1_greedy_runs"] = acc["runs"]
    COUNTS["C1_main_inequality_checks"] = acc["main_checks"]
    COUNTS["C1_ordering_checks"] = acc["chain_checks"]
    COUNTS["C1_trivial_OPT_zero"] = acc["trivial"]
    total_random = (res["used"] + COUNTS.get("D3_eta1_instances", 0)
                    + COUNTS.get("D4_K1_instances", 0)
                    + COUNTS.get("D5_Kn_instances", 0))
    COUNTS["D_random_instances_total"] = total_random

    ex = running_example()
    failed = [c for c in CHECKS if c["status"] == "FAIL"]

    payload = {
        "script": os.path.abspath(__file__),
        "statement": "prop:guarantee (T3): f(T) >= L_K(eta^sel) f(O*) >= "
                     "(1-e^{-1/eta^sel}) f(O*), L_K(x) = 1-(1-1/(xK))^K, "
                     "L_K(infinity) = 0; same bound at eta^tr and eta, ordered "
                     "L_K(eta^sel) >= L_K(eta^tr) >= L_K(eta)",
        "sources": {
            "statement": "results/V11/inputs/statement_guarantee.md",
            "route_one": "paper/sections/appendix_proofs.tex subsection app:guarantee",
            "definition": "paper/sections/model.tex def:etasel",
            "ledger": "THEOREM_LEDGER.md section T3",
            "attribution": "Goundan and Schulz 2007, Theorem 1 "
                           "(alpha = eta^sel, same direction)",
        },
        "seeds": {"C1": SEED_C1, "D3_eta1": SEED_ETA1, "D4_K1": SEED_K1,
                  "D5_Kn": SEED_KN},
        "tie_policy": {"enumerate_cap": TIE_CAP, "samples_when_larger": TIE_SAMPLES,
                       "tie_trees_enumerated": res["enumerated"],
                       "tie_trees_sampled": res["sampled"]},
        "counts": COUNTS,
        "criterion_C": {"checks": CHECKS, "C5_UK_rows": c5_rows},
        "criterion_D": {
            "random_instances": total_random,
            "random_breakdown": {"C1": res["used"],
                                 "D3_eta1": COUNTS.get("D3_eta1_instances", 0),
                                 "D4_K1": COUNTS.get("D4_K1_instances", 0),
                                 "D5_Kn": COUNTS.get("D5_Kn_instances", 0)},
            "families": res["families"],
            "structured": d_rows,
            "violations": len(VIOLATIONS),
            "worst_main_slack": {"slack": str(acc["worst_main"][0]),
                                 "at": acc["worst_main"][1]},
            "worst_main_slack_K_ge_2_and_etasel_gt_1": {
                "slack": str(acc["worst_nontrivial"][0]),
                "at": acc["worst_nontrivial"][1]},
            "runs_attaining_equality": acc["equality_runs"],
            "worst_product_slack": {"slack": str(acc["worst_product"][0]),
                                    "at": acc["worst_product"][1]},
        },
        "reruns": SUBPROCS,
        "violations": VIOLATIONS,
        "witnesses": WITNESSES,
        "running_example_K3_eta_3_2": ex,
        "failed_checks": [c["name"] for c in failed],
        "overall": "PASS" if not failed else "FAIL",
        "seconds": round(time.time() - t0, 1),
    }
    with open(JSON_PATH, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=False, default=str)

    print("counts: %s" % json.dumps(COUNTS, sort_keys=True))
    print("running example K=3 eta=3/2: %s" % json.dumps(ex, sort_keys=True))
    print("worst main slack f(T)/OPT - L_K(eta^sel): %s at %s"
          % (acc["worst_main"][0], json.dumps(acc["worst_main"][1], sort_keys=True)))
    print("worst main slack with K >= 2 and eta^sel > 1: %s at %s"
          % (acc["worst_nontrivial"][0],
             json.dumps(acc["worst_nontrivial"][1], sort_keys=True)))
    print("C1 runs attaining equality f(T) = L_K(eta^sel) OPT: %d" % acc["equality_runs"])
    print("worst product-bound slack: %s at %s"
          % (acc["worst_product"][0], json.dumps(acc["worst_product"][1], sort_keys=True)))
    print("violations: %d" % len(VIOLATIONS))
    print("json written: %s" % JSON_PATH)
    print("OVERALL: %s (%d checks, %d failed, %.1fs)"
          % (payload["overall"], len(CHECKS), len(failed), payload["seconds"]))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

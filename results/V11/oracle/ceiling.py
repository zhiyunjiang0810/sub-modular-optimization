#!/usr/bin/env python3
"""V11 Q3 oracle for thm:ceiling (ledger T8), Proposition form.

Statement under test (results/V11/inputs/statement_ceiling.md):

    Let 2 <= K <= n.  For every deterministic algorithm with arbitrary query
    access to ftilde and output of size at most K, and every eta_u, eta_o >= 1,
    there is a pair (f, ftilde) with error exactly (eta_u, eta_o) on which the
    output T satisfies f(T) <= C*_{n,K}(eta) f(O*), where

        C*_{n,K}(eta) = K / (K + (eta - 1) min{K, n - K})
                      = K / ((2K - n) + (n - K) eta)   for K <= n <= 2K,
                      = 1 / eta                        for n >= 2K.

    Conversely, a set S maximizing ftilde over all K-subsets satisfies, on
    every instance and for every optimal K-set O*,

        f(S) >= K / (K + (eta - 1) |O* \\ S|) f(O*) >= C*_{n,K}(eta) f(O*).

Per the handoff addendum (section B.3) the main text keeps n >= 2K and the
range K <= n < 2K moves to an appendix remark; this script checks both.

Route-one proof material (upper bound, n >= 2K):
    paper/sections/appendix_proofs.tex, subsection app:ceiling (~line 1211),
    ftilde(S) = c|S| and f_O(S) = c(|S cap B|/eta_o + eta_u|S cap O|),
    plus the J5 three-step exchange proof and slack identity (7).
    results/J5_hardcore/J5_ceiling_proof.md.
Route "yi" (attainment, n >= 2K):
    paper/sections/appendix_model_proofs.tex, final remark: Prop 2(iii) with
    epsilon = (eta-1)/(eta+1) gives (1-epsilon)/(1+epsilon) = 1/eta, combined
    with the Horel-Singer observation.
    HANDOFF_ADDENDUM_2026-09-18.md section C (three-line adversary).

Criterion C (oracle)
  C0  sympy identities: C* branches, slack identities (7)(8)(9), the
      Horel-Singer epsilon substitution.                   [VERIFIED-SYMBOLIC]
  C1  n >= 2K, K = 2..4, n = 2K..10, rational split grid: the adversary
      instance is monotone submodular, the Definition 1 band holds with
      smallest factors exactly (eta_u, eta_o), O is optimal, and every output
      T disjoint from O has f(T) <= f(O)/eta.              [VERIFIED-EXHAUSTIVE]
  C1b same for K = 1, run separately.                      [VERIFIED-EXHAUSTIVE]
  C2  attainment on random exact instances (n >= 2K, n <= 7, K <= 3): the
      worst ftilde-maximizing K-set S satisfies f(S) >= OPT/eta and the
      per-instance form for every optimal O*.              [VERIFIED-EXHAUSTIVE]
  C3  adversary direction against three algorithm types (predictive greedy on
      ftilde, exhaustive argmax ftilde, fixed output): ratio <= 1/eta.
                                                           [VERIFIED-EXHAUSTIVE]
  C4  rerun results/J5_hardcore/J5_hardcore_oracles.py into
      results/V11/oracle/j5_reproduced and record its exit code and counts.
                                    [VERIFIED-LP floats for the 52 LPs; the
                                     modular adversary instances are exact]
  C5  random exact instances with n = K..2K-1, K = 2..4: exhaustive argmax
      ftilde satisfies the per-instance form.              [VERIFIED-EXHAUSTIVE]
  C6  the app:ceiling adversary for K <= n < 2K has ratio exactly
      K/(K + (eta-1) min{K, n-K}), including the n = K calibration.
                                                           [VERIFIED-EXHAUSTIVE]

Criterion D (counterexample search on the statement itself)
  The random instances of C2 and C5 are the search for the attainment
  inequality; the adversary families of C1, C3 and C6 are the search for the
  upper-bound side.  Structured cases: eta = 1, eta = K, n = 2K, n = K,
  n = 2K-1.

Every decision uses fractions.Fraction or sympy; floats appear only inside
printed text and inside the rerun of the existing J5 script.  Seeds fixed.

Run:  python3 results/V11/oracle/ceiling.py
Exit code 0 iff every check passed.  Writes results/V11/oracle/ceiling.json.
"""

from fractions import Fraction as Fr
from itertools import combinations
import json
import os
import random
import subprocess
import sys
import time

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
JSON_PATH = os.path.join(HERE, "ceiling.json")
J5_SCRIPT = os.path.join(ROOT, "results", "J5_hardcore", "J5_hardcore_oracles.py")
J5_OUTDIR = os.path.join(HERE, "j5_reproduced")

SEED_C2 = 20260918          # random exact instances, n >= 2K
SEED_C5 = 20260919          # random exact instances, K <= n < 2K
SEED_D_ETA1 = 20260920      # structured case eta = 1
SEED_ALG = 20260921         # the fixed-output algorithm of C3

CHECKS = []
VIOLATIONS = []
COUNTS = {}
SUBPROCS = []
WITNESSES = []


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


def cstar(n, K, eta):
    """C*_{n,K}(eta) = K / (K + (eta-1) min{K, n-K}), exact."""
    return Fr(K) / (K + (eta - 1) * min(K, n - K))


# ---------------------------------------------------------------------------
# generic exact set-function utilities
# ---------------------------------------------------------------------------
def validity(n, tab):
    """Exhaustive: f(empty)=0, monotone, submodular (local exchange form)."""
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
    """Smallest admissible (eta_u, eta_o) of Definition 1 for predictor g of f.

    Returns (eta_u, eta_o, n_pairs, zero_violation).  zero_violation is True if
    some pair has d = 0 < dt or d > 0 = dt, which Definition 1 forbids.
    """
    eu = eo = Fr(0)
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
    if eu == 0:
        eu = Fr(1)
    if eo == 0:
        eo = Fr(1)
    return eu, eo, pairs, bad


def best_Kset(n, K, tab):
    """(max value, list of every maximizing K-set as a bitmask)."""
    best = None
    arg = []
    for comb in combinations(range(n), K):
        m = 0
        for i in comb:
            m |= 1 << i
        v = tab[m]
        if best is None or v > best:
            best = v
            arg = [m]
        elif v == best:
            arg.append(m)
    return best, arg


def worst_predicted_argmax(n, K, f, g):
    """S maximizing ftilde over K-sets, adversarial ties: the maximizer with
    the smallest true value."""
    _, arg = best_Kset(n, K, g)
    return min(arg, key=lambda m: f[m])


# ---------------------------------------------------------------------------
# the app:ceiling adversary
# ---------------------------------------------------------------------------
def adversary_ngeq2K(n, K, eu, eo, c, o_mask):
    """ftilde(S) = c|S|;  f(S) = c(|S cap B|/eo + eta_u|S cap O|).

    Returns (f_table, ftilde_table).
    """
    w = [c * eu if (o_mask >> i) & 1 else c / eo for i in range(n)]
    f = [Fr(0)] * (1 << n)
    g = [Fr(0)] * (1 << n)
    for m in range(1 << n):
        s = Fr(0)
        for i in range(n):
            if (m >> i) & 1:
                s += w[i]
        f[m] = s
        g[m] = c * pc(m)
    return f, g, w


def adversary_small_n(n, K, eu, eo, b, s_mask):
    """The app:ceiling adversary for every n > K: ftilde(T) = b|T|, output
    completed to a K-set S, f modular with weight b/eta_o on S and eta_u b off
    S.  At n = K the calibrated variant puts the high weight on one element of
    S so that both error ends are attained."""
    if n == K:
        w = [eu * b if i == 0 else b / eo for i in range(n)]
    else:
        w = [b / eo if (s_mask >> i) & 1 else eu * b for i in range(n)]
    f = [Fr(0)] * (1 << n)
    g = [Fr(0)] * (1 << n)
    for m in range(1 << n):
        s = Fr(0)
        for i in range(n):
            if (m >> i) & 1:
                s += w[i]
        f[m] = s
        g[m] = b * pc(m)
    return f, g, w


# ---------------------------------------------------------------------------
# random exact instances
# ---------------------------------------------------------------------------
def rnd_frac(rng, lo_num=0, hi_num=9, dens=(1, 2, 3, 4)):
    return Fr(rng.randint(lo_num, hi_num), rng.choice(dens))


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
    """f(S) = g(|S|) with g concave nondecreasing, g(0) = 0."""
    inc = sorted([rnd_frac(rng, 0, 9) for _ in range(n)], reverse=True)
    pref = [Fr(0)]
    for x in inc:
        pref.append(pref[-1] + x)
    tab = [pref[pc(m)] for m in range(1 << n)]
    return tab, "concave_cardinality"


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
    g1, n1 = rng.choice(BASE_GENS)(n, rng)
    g2, n2 = rng.choice(BASE_GENS)(n, rng)
    a = Fr(rng.randint(1, 4), rng.choice((1, 2, 3)))
    b = Fr(rng.randint(1, 4), rng.choice((1, 2, 3)))
    return [a * x + b * y for x, y in zip(g1, g2)], "mixture(%s,%s)" % (n1, n2)


ALL_GENS = BASE_GENS + (gen_mixture,)
THETAS = (Fr(0), Fr(1, 4), Fr(1, 3), Fr(1, 2), Fr(2, 3), Fr(3, 4), Fr(1))


def sample_ftilde(n, f, eu, eo, rng):
    """Random legal predictor.  The Definition 1 constraints are exactly the
    pairs (S, S+e), so processing the lattice by cardinality and picking
    ftilde(T) inside the intersection of the K intervals enforces all of them.
    Returns None if the intersection is empty (the draw is rejected)."""
    g = [None] * (1 << n)
    g[0] = Fr(0)
    order = sorted(range(1, 1 << n), key=pc)
    for m in order:
        lo = None
        hi = None
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


def random_instance(n, K, rng, eta1=False):
    """One exact random instance.  Returns a dict or None on rejection."""
    gen = rng.choice(ALL_GENS)
    f, fname = gen(n, rng)
    ok_norm, ok_mono, ok_sub, nm, ns = validity(n, f)
    if not (ok_norm and ok_mono and ok_sub):
        return {"invalid_f": True, "family": fname}
    if eta1:
        c = Fr(rng.randint(1, 5), rng.choice((1, 2, 3)))
        g = [c * x for x in f]
    else:
        eu = rng.choice((Fr(1), Fr(5, 4), Fr(3, 2), Fr(2)))
        eo = rng.choice((Fr(1), Fr(5, 4), Fr(3, 2), Fr(2), Fr(3)))
        g = None
        for _ in range(12):
            g = sample_ftilde(n, f, eu, eo, rng)
            if g is not None:
                break
        if g is None:
            return None
    au, ao, npairs, bad = band_factors(n, f, g)
    if bad:
        return {"bad_band": True, "family": fname}
    eta = au * ao
    S = worst_predicted_argmax(n, K, f, g)
    opt, opts = best_Kset(n, K, f)
    return {"family": fname, "eta_u": au, "eta_o": ao, "eta": eta, "S": S,
            "opt": opt, "opts": opts, "f": f, "g": g,
            "mono_checks": nm, "sub_checks": ns, "band_pairs": npairs}


def test_attainment(inst, n, K, tag, acc):
    """Both attainment inequalities on one instance.  acc collects worst slack
    and violations."""
    f, S, opt, eta = inst["f"], inst["S"], inst["opt"], inst["eta"]
    if opt == 0:
        acc["trivial"] += 1
        return True
    ok = True
    ratio = f[S] / opt
    glob = Fr(1) / eta
    if ratio < glob:
        ok = False
        VIOLATIONS.append({"where": tag + " global f(S) >= OPT/eta",
                           "n": n, "K": K, "eta": str(eta),
                           "ratio": str(ratio), "bound": str(glob),
                           "family": inst["family"]})
    if ratio - glob < acc["worst_global"][0]:
        acc["worst_global"] = (ratio - glob,
                               {"tag": tag, "n": n, "K": K, "eta": str(eta),
                                "ratio": str(ratio), "bound": str(glob),
                                "family": inst["family"]})
    cs = cstar(n, K, eta)
    if ratio < cs:
        ok = False
        VIOLATIONS.append({"where": tag + " f(S) >= C*_{n,K} OPT",
                           "n": n, "K": K, "eta": str(eta),
                           "ratio": str(ratio), "bound": str(cs),
                           "family": inst["family"]})
    for om in inst["opts"]:
        a = pc(om & ~S)
        pb = Fr(K) / (K + (eta - 1) * a)
        acc["per_instance_checks"] += 1
        if ratio < pb:
            ok = False
            VIOLATIONS.append({"where": tag + " per-instance f(S) >= K/(K+(eta-1)a) OPT",
                               "n": n, "K": K, "eta": str(eta), "a": a,
                               "ratio": str(ratio), "bound": str(pb),
                               "family": inst["family"]})
        if ratio - pb < acc["worst_per"][0]:
            acc["worst_per"] = (ratio - pb,
                                {"tag": tag, "n": n, "K": K, "eta": str(eta),
                                 "a": a, "ratio": str(ratio), "bound": str(pb),
                                 "family": inst["family"]})
    return ok


# ---------------------------------------------------------------------------
# C0: symbolic
# ---------------------------------------------------------------------------
def check_C0():
    n, K, eta, a = sp.symbols("n K eta a", positive=True)
    A, B, Z, D, R = sp.symbols("A B Z D R")
    u, o = sp.symbols("u o", positive=True)
    X, Y = sp.symbols("X Y")
    res = []

    C = K / (K + (eta - 1) * sp.Min(K, n - K))
    r1 = sp.simplify(C.subs(sp.Min(K, n - K), n - K) - K / ((2 * K - n) + (n - K) * eta))
    r2 = sp.simplify(C.subs(sp.Min(K, n - K), K) - 1 / eta)
    res += [r1, r2]

    gam = 1 - 1 / eta
    E = gam * Z + A / eta - B
    H = A + D - Z
    J = eta * a * R - K * D
    T = A - R
    lhs = (1 + (eta - 1) * a / K) * A - B
    r3 = sp.simplify(sp.expand(lhs - (E + gam * H + gam / K * J + gam * eta * a / K * T)))
    res.append(r3)

    E2 = (o * (Z - B) - Y) / o + (Y - X) / o + (u * X - (Z - A)) / (u * o)
    r4 = sp.simplify(sp.expand(E.subs(eta, u * o) - E2))
    res.append(r4)

    rs, p, q, gg, Db = sp.symbols("r_s p q g D_b")
    r5 = sp.simplify(sp.expand(u * o * rs - Db
                               - (u * (o * rs - p) + u * (p - q) + (u * q - gg) + (gg - Db))))
    res.append(r5)

    eps = (eta - 1) / (eta + 1)
    r6 = sp.simplify((1 - eps) / (1 + eps) - 1 / eta)
    res.append(r6)

    cfac = 2 * u / (eta + 1)
    r7 = sp.simplify(cfac / u - (1 - eps))
    r8 = sp.simplify((cfac * o).subs(eta, u * o) - (1 + eps).subs(eta, u * o))
    res += [r7, r8]

    ratio = (K / o) / (u * K)
    r9 = sp.simplify(ratio - 1 / (u * o))
    res.append(r9)

    a0 = sp.symbols("a_0", positive=True)
    adv = K * (1 / o) / (a0 * u + (K - a0) / o)
    r10 = sp.simplify(adv - K / (K + (u * o - 1) * a0))
    res.append(r10)

    ok = all(sp.simplify(r) == 0 for r in res)
    COUNTS["C0_identities"] = len(res)
    return check("C0 [VERIFIED-SYMBOLIC] sympy: C* two branches, slack identity (7), "
                 "E decomposition (8), single-exchange decomposition (9), "
                 "Horel-Singer eps=(eta-1)/(eta+1), adversary ratios",
                 ok, "residuals all zero, %d identities" % len(res),
                 {"residuals": [str(r) for r in res]})


# ---------------------------------------------------------------------------
# C1 / C1b: the adversary for n >= 2K
# ---------------------------------------------------------------------------
def split_grid(K):
    base = [(Fr(1), Fr(1)),
            (Fr(1), Fr(6, 5)), (Fr(6, 5), Fr(1)),
            (Fr(1), Fr(3, 2)), (Fr(3, 2), Fr(1)), (Fr(5, 4), Fr(6, 5)),
            (Fr(1), Fr(2)), (Fr(2), Fr(1)), (Fr(4, 3), Fr(3, 2)),
            (Fr(1), Fr(3)), (Fr(3, 2), Fr(2)), (Fr(3), Fr(1))]
    extra = [(Fr(1), Fr(K)), (Fr(K), Fr(1))]
    out = []
    for s in base + extra:
        if s not in out:
            out.append(s)
    return out


def run_adversary_grid(Ks, label, nmax=10):
    acc = {"instances": 0, "subsets": 0, "mono": 0, "sub": 0, "band_pairs": 0,
           "T_checks": 0, "worst": (Fr(2), None), "fails": []}
    for K in Ks:
        for n in range(2 * K, nmax + 1):
            o_mask = (1 << K) - 1
            for (eu, eo) in split_grid(K):
                c = Fr(1)
                eta = eu * eo
                f, g, w = adversary_ngeq2K(n, K, eu, eo, c, o_mask)
                acc["instances"] += 1
                acc["subsets"] += 1 << n
                ok_norm, ok_mono, ok_sub, nm, ns = validity(n, f)
                acc["mono"] += nm
                acc["sub"] += ns
                au, ao, npairs, bad = band_factors(n, f, g)
                acc["band_pairs"] += npairs
                opt, opts = best_Kset(n, K, f)
                exact_factors = (au == eu and ao == eo)
                fO = f[o_mask]
                ok_opt = (opt == fO) and (o_mask in opts)
                ok_fO = (fO == c * K * eu)
                # every output T disjoint from O, |T| <= K
                rest = [i for i in range(n) if not (o_mask >> i) & 1]
                ok_T = True
                worst_here = None
                for size in range(0, K + 1):
                    for comb in combinations(rest, size):
                        m = 0
                        for i in comb:
                            m |= 1 << i
                        acc["T_checks"] += 1
                        r = f[m] / fO if fO > 0 else Fr(0)
                        if r > Fr(1) / eta:
                            ok_T = False
                        if worst_here is None or r > worst_here:
                            worst_here = r
                if worst_here is not None:
                    slack = Fr(1) / eta - worst_here
                    if slack < acc["worst"][0]:
                        acc["worst"] = (slack, {"K": K, "n": n,
                                                "eta_u": str(eu), "eta_o": str(eo),
                                                "eta": str(eta),
                                                "max_ratio_over_disjoint_T": str(worst_here),
                                                "bound_1_over_eta": str(Fr(1) / eta)})
                good = (ok_norm and ok_mono and ok_sub and not bad and exact_factors
                        and ok_opt and ok_fO and ok_T)
                if not good:
                    acc["fails"].append({"K": K, "n": n, "eta_u": str(eu),
                                         "eta_o": str(eo), "norm": ok_norm,
                                         "mono": ok_mono, "submod": ok_sub,
                                         "band_zero_violation": bad,
                                         "factors": (str(au), str(ao)),
                                         "O_optimal": ok_opt, "fO": ok_fO,
                                         "T_bound": ok_T})
    ok = not acc["fails"]
    detail = ("instances=%d subsets=%d mono=%d submod=%d band_pairs=%d "
              "disjoint_T_checks=%d" % (acc["instances"], acc["subsets"],
                                        acc["mono"], acc["sub"],
                                        acc["band_pairs"], acc["T_checks"]))
    check("%s [VERIFIED-EXHAUSTIVE] n >= 2K adversary: monotone submodular, band "
          "with smallest factors exactly (eta_u,eta_o), O optimal with "
          "f(O)=cK eta_u, and f(T) <= f(O)/eta for every T disjoint from O"
          % label, ok, detail,
          {"failures": acc["fails"][:10],
           "tightest": acc["worst"][1],
           "tight_slack": str(acc["worst"][0])})
    return acc


# ---------------------------------------------------------------------------
# C2: attainment on random exact instances, n >= 2K
# ---------------------------------------------------------------------------
def plan_nK_large():
    plan = []
    for K in (1, 2, 3):
        for n in range(2 * K, 8):
            plan.append((n, K))
    return plan


def run_random_large(target):
    rng = random.Random(SEED_C2)
    plan = plan_nK_large()
    acc = {"worst_global": (Fr(2), None), "worst_per": (Fr(2), None),
           "per_instance_checks": 0, "trivial": 0}
    used = 0
    rejected = 0
    invalid = 0
    families = {}
    idx = 0
    while used < target:
        n, K = plan[idx % len(plan)]
        idx += 1
        inst = random_instance(n, K, rng)
        if inst is None:
            rejected += 1
            continue
        if inst.get("invalid_f") or inst.get("bad_band"):
            invalid += 1
            continue
        used += 1
        families[inst["family"]] = families.get(inst["family"], 0) + 1
        test_attainment(inst, n, K, "C2", acc)
    COUNTS["C2_random_instances"] = used
    COUNTS["C2_rejected_ftilde_draws"] = rejected
    COUNTS["C2_per_instance_checks"] = acc["per_instance_checks"]
    COUNTS["C2_zero_OPT_instances"] = acc["trivial"]
    bad = [v for v in VIOLATIONS if v["where"].startswith("C2")]
    ok = not bad
    check("C2 [VERIFIED-EXHAUSTIVE] attainment, %d random exact instances "
          "(n >= 2K, n <= 7, K <= 3): worst ftilde-argmax K-set satisfies "
          "f(S) >= OPT/eta and f(S) >= K/(K+(eta-1)|O*\\S|) OPT for every "
          "optimal O*" % used, ok,
          "instances=%d per-instance-checks=%d rejected-draws=%d families=%s"
          % (used, acc["per_instance_checks"], rejected,
             json.dumps(families, sort_keys=True)),
          {"worst_global_slack": str(acc["worst_global"][0]),
           "worst_global_at": acc["worst_global"][1],
           "worst_per_instance_slack": str(acc["worst_per"][0]),
           "worst_per_instance_at": acc["worst_per"][1],
           "violations": bad[:10]})
    return used, acc, families


# ---------------------------------------------------------------------------
# C3: three algorithm types against the adversary
# ---------------------------------------------------------------------------
def alg_predictive_greedy(n, K, g):
    """Predictive greedy on ftilde, lowest index on ties."""
    S = 0
    for _ in range(K):
        best = None
        pick = None
        for i in range(n):
            if (S >> i) & 1:
                continue
            d = g[S | (1 << i)] - g[S]
            if best is None or d > best:
                best = d
                pick = i
        S |= 1 << pick
    return S


def alg_exhaustive(n, K, g):
    """Exhaustive argmax of ftilde over K-sets, lexicographically first tie."""
    best = None
    arg = None
    for comb in combinations(range(n), K):
        m = 0
        for i in comb:
            m |= 1 << i
        if best is None or g[m] > best:
            best = g[m]
            arg = m
    return arg


def alg_fixed(n, K, seed):
    rng = random.Random(seed + 1000 * n + K)
    idx = rng.sample(range(n), K)
    m = 0
    for i in idx:
        m |= 1 << i
    return m


def run_C3():
    acc = {"runs": 0, "worst": (Fr(-1), None), "fails": []}
    for K in (1, 2, 3, 4):
        for n in range(2 * K, 11):
            for (eu, eo) in split_grid(K):
                eta = eu * eo
                c = Fr(1)
                probe = [Fr(0)] * (1 << n)
                for m in range(1 << n):
                    probe[m] = c * pc(m)
                for name, T in (("predictive_greedy", alg_predictive_greedy(n, K, probe)),
                                ("exhaustive_argmax", alg_exhaustive(n, K, probe)),
                                ("fixed_output", alg_fixed(n, K, SEED_ALG))):
                    rest = [i for i in range(n) if not (T >> i) & 1]
                    o_mask = 0
                    for i in rest[:K]:
                        o_mask |= 1 << i
                    f, g, w = adversary_ngeq2K(n, K, eu, eo, c, o_mask)
                    if g != probe:
                        acc["fails"].append({"why": "ftilde not the probe",
                                             "n": n, "K": K})
                    opt, _ = best_Kset(n, K, f)
                    acc["runs"] += 1
                    r = f[T] / opt if opt > 0 else Fr(0)
                    if r > Fr(1) / eta:
                        acc["fails"].append({"alg": name, "K": K, "n": n,
                                             "eta_u": str(eu), "eta_o": str(eo),
                                             "ratio": str(r),
                                             "bound": str(Fr(1) / eta)})
                    if r > acc["worst"][0]:
                        acc["worst"] = (r, {"alg": name, "K": K, "n": n,
                                            "eta": str(eta), "ratio": str(r),
                                            "bound": str(Fr(1) / eta)})
    COUNTS["C3_algorithm_runs"] = acc["runs"]
    ok = not acc["fails"]
    check("C3 [VERIFIED-EXHAUSTIVE] adversary direction against predictive greedy "
          "on ftilde, exhaustive argmax ftilde and a fixed output: "
          "f(T)/f(O*) <= 1/eta on every adversary instance", ok,
          "runs=%d largest ratio-over-bound margin at %s"
          % (acc["runs"], json.dumps(acc["worst"][1], sort_keys=True)),
          {"failures": acc["fails"][:10], "worst": acc["worst"][1]})
    return acc


# ---------------------------------------------------------------------------
# C4: rerun the existing J5 script
# ---------------------------------------------------------------------------
def run_C4():
    rec = {"path": J5_SCRIPT, "output_dir": J5_OUTDIR, "rerun": False}
    if not os.path.exists(J5_SCRIPT):
        rec["reason"] = "file not found"
        SUBPROCS.append(rec)
        check("C4 [FAILED] rerun results/J5_hardcore/J5_hardcore_oracles.py",
              False, "script not found")
        return rec
    os.makedirs(J5_OUTDIR, exist_ok=True)
    t0 = time.time()
    p = subprocess.run([sys.executable, J5_SCRIPT, "--output-dir", J5_OUTDIR],
                       cwd=os.path.dirname(J5_SCRIPT), capture_output=True,
                       text=True, timeout=1800)
    rec["rerun"] = True
    rec["exit_code"] = p.returncode
    rec["seconds"] = round(time.time() - t0, 1)
    out = p.stdout + p.stderr
    rec["stdout_tail"] = out.strip().splitlines()[-18:]
    log_path = os.path.join(J5_OUTDIR, "J5_hardcore_oracles.log")
    logtext = ""
    if os.path.exists(log_path):
        with open(log_path) as fh:
            logtext = fh.read()
    rec["log_path"] = log_path
    rec["log_lines"] = logtext.strip().splitlines()
    keys = {}
    for line in logtext.splitlines():
        low = line.lower()
        for key, pat in (("status", "status:"),
                         ("symbolic_identities", "symbolic identities:"),
                         ("monotonicity_numerator_terms", "monotonicity numerator terms"),
                         ("exhaustive_search_LPs", "exhaustive-search independent lps"),
                         ("modular_witnesses", "modular witnesses"),
                         ("double_submodular_instances", "double-submodular instances"),
                         ("K4_dual_certificates", "rational dual certificates"),
                         ("PE1_witness", "pe1 rational witness")):
            if pat in low:
                keys[key] = line.strip()
    rec["key_lines"] = keys
    SUBPROCS.append(rec)
    ok = (p.returncode == 0) and ("ALL PASS" in out) and ("status: PASS" in logtext)
    check("C4 [VERIFIED-LP floats] rerun of results/J5_hardcore/J5_hardcore_oracles.py "
          "(slack identities (7)(8)(9), 52 full-lattice LPs, 24 modular adversary "
          "instances); the 52 LPs use scipy linprog, so that item is float LP, "
          "not exact; the modular instances and the K=4 dual certificates are exact",
          ok, "exit_code=%d seconds=%.1f %s"
          % (p.returncode, rec["seconds"], json.dumps(keys, sort_keys=True)))
    return rec


# ---------------------------------------------------------------------------
# C5: random exact instances with K <= n < 2K
# ---------------------------------------------------------------------------
def run_random_small(target):
    rng = random.Random(SEED_C5)
    plan = []
    for K in (2, 3, 4):
        for n in range(K, 2 * K):
            plan.append((n, K))
    acc = {"worst_global": (Fr(2), None), "worst_per": (Fr(2), None),
           "per_instance_checks": 0, "trivial": 0}
    used = 0
    rejected = 0
    invalid = 0
    idx = 0
    while used < target:
        n, K = plan[idx % len(plan)]
        idx += 1
        inst = random_instance(n, K, rng)
        if inst is None:
            rejected += 1
            continue
        if inst.get("invalid_f") or inst.get("bad_band"):
            invalid += 1
            continue
        used += 1
        test_attainment(inst, n, K, "C5", acc)
    COUNTS["C5_random_instances"] = used
    COUNTS["C5_rejected_ftilde_draws"] = rejected
    COUNTS["C5_per_instance_checks"] = acc["per_instance_checks"]
    bad = [v for v in VIOLATIONS if v["where"].startswith("C5")]
    ok = not bad
    check("C5 [VERIFIED-EXHAUSTIVE] K <= n < 2K, %d random exact instances "
          "(K = 2..4, n = K..2K-1): exhaustive argmax ftilde satisfies the "
          "per-instance form and C*_{n,K}" % used, ok,
          "instances=%d per-instance-checks=%d rejected-draws=%d"
          % (used, acc["per_instance_checks"], rejected),
          {"worst_per_instance_slack": str(acc["worst_per"][0]),
           "worst_per_instance_at": acc["worst_per"][1],
           "worst_global_slack": str(acc["worst_global"][0]),
           "worst_global_at": acc["worst_global"][1],
           "violations": bad[:10]})
    return used, acc


# ---------------------------------------------------------------------------
# C6: the small-n adversary has ratio exactly C*
# ---------------------------------------------------------------------------
def run_C6():
    acc = {"instances": 0, "fails": [], "rows": [], "mono": 0, "sub": 0,
           "band_pairs": 0, "n1_factor_exempt": 0}
    for K in (1, 2, 3, 4, 5):
        for n in range(K, 2 * K):
            s_mask = (1 << K) - 1
            for (eu, eo) in split_grid(K):
                eta = eu * eo
                b = Fr(1)
                f, g, w = adversary_small_n(n, K, eu, eo, b, s_mask)
                acc["instances"] += 1
                ok_norm, ok_mono, ok_sub, nm, ns = validity(n, f)
                acc["mono"] += nm
                acc["sub"] += ns
                au, ao, npairs, bad = band_factors(n, f, g)
                acc["band_pairs"] += npairs
                opt, _ = best_Kset(n, K, f)
                # the algorithm's output is the K-set S (n = K: the ground set)
                T = s_mask
                ratio = f[T] / opt if opt > 0 else Fr(0)
                target = cstar(n, K, eta)
                ok_ratio = (ratio == target)
                # A single element carries one weight, so at n = K = 1 both
                # error ends can be attained only when eta = 1.  The statement
                # assumes 2 <= K <= n, and the appendix calibration needs at
                # least two elements; n = 1 is therefore outside the
                # both-ends-attained requirement and is recorded as such.
                if n == 1:
                    exact_factors = True
                    acc["n1_factor_exempt"] += 1
                else:
                    exact_factors = (au == eu and ao == eo)
                good = (ok_norm and ok_mono and ok_sub and not bad
                        and ok_ratio and exact_factors)
                if not good:
                    acc["fails"].append({"K": K, "n": n, "eta_u": str(eu),
                                         "eta_o": str(eo),
                                         "ratio": str(ratio),
                                         "C*": str(target),
                                         "factors": (str(au), str(ao)),
                                         "norm": ok_norm, "mono": ok_mono,
                                         "submod": ok_sub,
                                         "band_zero_violation": bad})
                if n in (K, 2 * K - 1) and (eu, eo) in ((Fr(3, 2), Fr(1)), (Fr(1), Fr(3, 2))):
                    acc["rows"].append({"K": K, "n": n, "eta": str(eta),
                                        "ratio": str(ratio), "C*": str(target)})
    COUNTS["C6_instances"] = acc["instances"]
    COUNTS["C6_mono_checks"] = acc["mono"]
    COUNTS["C6_submod_checks"] = acc["sub"]
    COUNTS["C6_band_pairs"] = acc["band_pairs"]
    ok = not acc["fails"]
    check("C6 [VERIFIED-EXHAUSTIVE] K <= n < 2K adversary of app:ceiling: ratio "
          "exactly K/(K+(eta-1)min{K,n-K}), band factors exactly (eta_u,eta_o) "
          "(at n = K the calibrated mixed-weight variant, output the whole "
          "ground set, ratio 1)", ok,
          "instances=%d mono=%d submod=%d band_pairs=%d n=1_factor_exempt=%d"
          % (acc["instances"], acc["mono"], acc["sub"], acc["band_pairs"],
             acc["n1_factor_exempt"]),
          {"failures": acc["fails"][:10], "sample_rows": acc["rows"][:12],
           "scope_note": "n = K = 1 carries a single weight, so both error ends "
                         "are attainable only at eta = 1; the statement assumes "
                         "2 <= K <= n and the appendix calibration needs at least "
                         "two elements, so the both-ends requirement is not "
                         "applied at n = 1 (ratio and validity still checked)"})
    return acc


# ---------------------------------------------------------------------------
# Criterion D: structured cases
# ---------------------------------------------------------------------------
def run_structured():
    rows = []

    # eta = 1, adversary side
    ok = True
    det = []
    for K in (1, 2, 3, 4):
        for n in (2 * K, 2 * K + 1, max(K, 2 * K - 1)):
            f, g, w = adversary_ngeq2K(n, K, Fr(1), Fr(1), Fr(1), (1 << K) - 1) \
                if n >= 2 * K else adversary_small_n(n, K, Fr(1), Fr(1), Fr(1), (1 << K) - 1)
            opt, _ = best_Kset(n, K, f)
            c = cstar(n, K, Fr(1))
            if c != 1:
                ok = False
            det.append("K=%d n=%d C*=%s" % (K, n, c))
    # eta = 1, attainment side: ftilde = c f, argmax is exactly optimal
    rng = random.Random(SEED_D_ETA1)
    cnt = 0
    for K in (1, 2, 3):
        for n in range(2 * K, 8):
            for _ in range(12):
                inst = random_instance(n, K, rng, eta1=True)
                if inst is None or inst.get("invalid_f") or inst.get("bad_band"):
                    continue
                cnt += 1
                if inst["eta"] != 1:
                    ok = False
                if inst["opt"] > 0 and inst["f"][inst["S"]] != inst["opt"]:
                    ok = False
                    VIOLATIONS.append({"where": "D structured eta=1",
                                       "n": n, "K": K,
                                       "f(S)": str(inst["f"][inst["S"]]),
                                       "OPT": str(inst["opt"])})
    rows.append({"case": "eta = 1", "outcome": "PASS" if ok else "FAIL",
                 "detail": "C* = 1 on every (n,K) checked; %d random instances "
                           "with ftilde = c f have actual eta = 1 and the "
                           "ftilde-argmax K-set is exactly optimal" % cnt})
    COUNTS["D_eta1_random_instances"] = cnt

    # eta = K
    ok = True
    det = []
    for K in (2, 3, 4):
        eta = Fr(K)
        n = 2 * K
        f, g, w = adversary_ngeq2K(n, K, eta, Fr(1), Fr(1), (1 << K) - 1)
        T = alg_exhaustive(n, K, g)
        rest = [i for i in range(n) if not (T >> i) & 1]
        o_mask = 0
        for i in rest[:K]:
            o_mask |= 1 << i
        f, g, w = adversary_ngeq2K(n, K, eta, Fr(1), Fr(1), o_mask)
        opt, _ = best_Kset(n, K, f)
        r = f[T] / opt
        if r != Fr(1, K) or cstar(n, K, eta) != Fr(1, K):
            ok = False
        det.append("K=%d n=%d ratio=%s C*=%s" % (K, n, r, cstar(n, K, eta)))
    rows.append({"case": "eta = K", "outcome": "PASS" if ok else "FAIL",
                 "detail": "; ".join(det)})

    # n = 2K: the two branches of C* agree and the adversary attains 1/eta
    ok = True
    det = []
    for K in (1, 2, 3, 4):
        n = 2 * K
        for (eu, eo) in split_grid(K):
            eta = eu * eo
            b1 = Fr(K) / ((2 * K - n) + (n - K) * eta)
            b2 = Fr(1) / eta
            if b1 != b2 or cstar(n, K, eta) != b2:
                ok = False
        f, g, w = adversary_ngeq2K(2 * K, K, Fr(3, 2), Fr(1), Fr(1), (1 << K) - 1)
        rest = [i for i in range(K, 2 * K)]
        T = 0
        for i in rest:
            T |= 1 << i
        opt, _ = best_Kset(n, K, f)
        det.append("K=%d ratio=%s" % (K, f[T] / opt))
    rows.append({"case": "n = 2K", "outcome": "PASS" if ok else "FAIL",
                 "detail": "both branches of C* equal 1/eta at n = 2K; "
                           "adversary at eta = 3/2: " + "; ".join(det)})

    # n = K: output the whole ground set, ratio 1
    ok = True
    det = []
    for K in (2, 3, 4, 5):
        n = K
        for (eu, eo) in split_grid(K):
            eta = eu * eo
            f, g, w = adversary_small_n(n, K, eu, eo, Fr(1), (1 << K) - 1)
            opt, _ = best_Kset(n, K, f)
            T = (1 << n) - 1
            r = f[T] / opt
            au, ao, _, bad = band_factors(n, f, g)
            if r != 1 or cstar(n, K, eta) != 1 or bad or au != eu or ao != eo:
                ok = False
        det.append("K=%d ratio=1" % K)
    rows.append({"case": "n = K (output the whole ground set)",
                 "outcome": "PASS" if ok else "FAIL",
                 "detail": "C* = 1 and the ratio is exactly 1 on every split; "
                           "the calibrated mixed-weight variant still attains "
                           "both error ends; " + "; ".join(det)})

    # n = 2K-1
    ok = True
    det = []
    for K in (2, 3, 4, 5):
        n = 2 * K - 1
        for (eu, eo) in split_grid(K):
            eta = eu * eo
            f, g, w = adversary_small_n(n, K, eu, eo, Fr(1), (1 << K) - 1)
            opt, _ = best_Kset(n, K, f)
            T = (1 << K) - 1
            r = f[T] / opt
            target = Fr(K) / (1 + (K - 1) * eta)
            if r != target or cstar(n, K, eta) != target:
                ok = False
        det.append("K=%d C*(eta=3/2)=%s" % (K, cstar(n, K, Fr(3, 2))))
    rows.append({"case": "n = 2K-1", "outcome": "PASS" if ok else "FAIL",
                 "detail": "C* = K/(1+(K-1)eta), attained exactly; " + "; ".join(det)})

    for r in rows:
        print("  structured %-34s %s  %s" % (r["case"], r["outcome"], r["detail"]))
    ok_all = all(r["outcome"] == "PASS" for r in rows)
    check("D structured cases (eta=1, eta=K, n=2K, n=K, n=2K-1)", ok_all,
          "%d cases, %d PASS" % (len(rows), sum(r["outcome"] == "PASS" for r in rows)),
          {"cases": rows})
    return rows


# ---------------------------------------------------------------------------
def running_example():
    """K = 3, eta = 3/2, exact."""
    K, eta = 3, Fr(3, 2)
    out = {}
    n = 6
    f, g, w = adversary_ngeq2K(n, K, Fr(3, 2), Fr(1), Fr(1), (1 << K) - 1)
    T = 0b111000
    opt, _ = best_Kset(n, K, f)
    out["adversary_n6"] = {"f(O)": str(opt), "f(T)": str(f[T]),
                           "ratio": str(f[T] / opt), "1/eta": str(Fr(1) / eta)}
    n = 5
    f2, g2, w2 = adversary_small_n(n, K, Fr(3, 2), Fr(1), Fr(1), (1 << K) - 1)
    opt2, _ = best_Kset(n, K, f2)
    out["adversary_n5"] = {"f(S)": str(f2[(1 << K) - 1]), "f(O)": str(opt2),
                           "ratio": str(f2[(1 << K) - 1] / opt2),
                           "C*_{5,3}": str(cstar(5, K, eta))}
    out["per_instance"] = {str(a): str(Fr(K) / (K + (eta - 1) * a)) for a in (0, 1, 2, 3)}
    return out


def main():
    t0 = time.time()
    print("V11 Q3 oracle: thm:ceiling (ledger T8), Proposition form")
    print("repo root: %s" % ROOT)
    print("exact arithmetic: fractions.Fraction and sympy; seeds C2=%d C5=%d "
          "eta1=%d alg=%d" % (SEED_C2, SEED_C5, SEED_D_ETA1, SEED_ALG))
    print()

    print("--- Criterion C, n >= 2K ---")
    check_C0()
    a1 = run_adversary_grid((2, 3, 4), "C1")
    a1b = run_adversary_grid((1,), "C1b (K = 1, run separately)")
    used2, acc2, fams = run_random_large(2200)
    a3 = run_C3()
    print()
    print("--- Criterion C, K <= n < 2K ---")
    c4 = run_C4()
    used5, acc5 = run_random_small(1200)
    a6 = run_C6()
    print()
    print("--- Criterion D ---")
    rows = run_structured()
    print()

    COUNTS["C1_adversary_instances"] = a1["instances"]
    COUNTS["C1b_adversary_instances"] = a1b["instances"]
    COUNTS["C1_mono_checks"] = a1["mono"] + a1b["mono"]
    COUNTS["C1_submod_checks"] = a1["sub"] + a1b["sub"]
    COUNTS["C1_band_pairs"] = a1["band_pairs"] + a1b["band_pairs"]
    COUNTS["C1_disjoint_T_checks"] = a1["T_checks"] + a1b["T_checks"]
    total_random = (used2 + used5 + COUNTS.get("D_eta1_random_instances", 0))
    COUNTS["D_random_instances_total"] = total_random

    ex = running_example()
    failed = [c for c in CHECKS if c["status"] == "FAIL"]
    worst_per = min(acc2["worst_per"], acc5["worst_per"], key=lambda t: t[0])
    worst_glob = min(acc2["worst_global"], acc5["worst_global"], key=lambda t: t[0])

    payload = {
        "script": os.path.abspath(__file__),
        "statement": "thm:ceiling (T8): deterministic minimax value "
                     "C*_{n,K}(eta) = K/(K+(eta-1)min{K,n-K}); attainment by "
                     "exhaustive argmax of ftilde over K-sets, with the "
                     "per-instance form f(S) >= K/(K+(eta-1)|O*\\S|) OPT",
        "sources": {
            "statement": "results/V11/inputs/statement_ceiling.md",
            "route_one": "paper/sections/appendix_proofs.tex subsection app:ceiling; "
                         "results/J5_hardcore/J5_ceiling_proof.md",
            "route_yi": "paper/sections/appendix_model_proofs.tex final remark "
                        "(Prop 2(iii) + Horel-Singer); "
                        "HANDOFF_ADDENDUM_2026-09-18.md section C",
            "ledger": "THEOREM_LEDGER.md section T8",
        },
        "seeds": {"C2": SEED_C2, "C5": SEED_C5, "D_eta1": SEED_D_ETA1,
                  "alg": SEED_ALG},
        "counts": COUNTS,
        "criterion_C": {"checks": CHECKS},
        "criterion_D": {
            "random_instances": total_random,
            "random_breakdown": {"C2_n_ge_2K": used2, "C5_n_lt_2K": used5,
                                 "D_eta1": COUNTS.get("D_eta1_random_instances", 0)},
            "families": fams,
            "structured": rows,
            "violations": len(VIOLATIONS),
            "worst_per_instance_slack": {"slack": str(worst_per[0]),
                                         "at": worst_per[1]},
            "worst_global_slack": {"slack": str(worst_glob[0]),
                                   "at": worst_glob[1]},
            "tightest_adversary_C1": {"slack": str(a1["worst"][0]),
                                      "at": a1["worst"][1]},
            "largest_adversary_ratio_C3": a3["worst"][1],
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
    print("worst per-instance slack: %s at %s"
          % (worst_per[0], json.dumps(worst_per[1], sort_keys=True)))
    print("worst global slack (f(S)/OPT - 1/eta): %s at %s"
          % (worst_glob[0], json.dumps(worst_glob[1], sort_keys=True)))
    print("tightest adversary margin (1/eta - max ratio over disjoint T): %s at %s"
          % (a1["worst"][0], json.dumps(a1["worst"][1], sort_keys=True)))
    print("violations: %d" % len(VIOLATIONS))
    print("json written: %s" % JSON_PATH)
    print("OVERALL: %s (%d checks, %d failed, %.1fs)"
          % (payload["overall"], len(CHECKS), len(failed), payload["seconds"]))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

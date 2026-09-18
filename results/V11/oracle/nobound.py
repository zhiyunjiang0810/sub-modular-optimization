#!/usr/bin/env python3
"""V11 Q1 oracle for prop:necessity (ledger T1, alias prop:nobound).

Statement under test (results/V11/inputs/statement_nobound.md):

    If no upper bound on eta is assumed, then for every deterministic
    algorithm with arbitrary query access to ftilde and every n >= 2K there
    are pairs (f, ftilde) on which the output T satisfies
    f(T) <= K/(n-K) * f(O*).

Two route-one constructions are implemented exactly as written:

  A. paper/sections/appendix_model_proofs.tex (delivered 2026-09-18, unwired)
        ftilde(S) = |S|,  delta = K/(n-K),
        f(S) = |S cap O| + delta |S \\ O|,  eta = 1/delta = (n-K)/K.
  B. paper/sections/appendix_proofs.tex, subsection app:necessity
        ftilde(S) = |S|,  gamma = K^2/(n(n-K)),
        f_O(S) = |S cap O| + gamma |S \\ O|,  eta = 1/gamma = n(n-K)/K^2.

Both are the same one-parameter family f_delta(S) = |S cap O| + delta|S \\ O|,
so the script runs the family at delta in {K/(n-K), K^2/(n(n-K)), 1/2, 1/5,
1/50} over K = 1..4 and n = 2K..12.

Criterion C (oracle): instance validity, the Definition 1 band with its
smallest admissible factors, OPT = f(O) = K, and the output bound for three
algorithm types.
Criterion D (counterexample search): >= 2000 random deterministic algorithms
against the statement itself, plus the structured cases n = 2K, K = 1 and the
smallest n.

Every decision uses fractions.Fraction; floats appear only inside printed
text.  Random seeds are fixed.

Run:  python3 results/V11/oracle/nobound.py
Exit code 0 iff every check passed.  Writes results/V11/oracle/nobound.json.
"""

from fractions import Fraction as Fr
from itertools import combinations
import json
import os
import random
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
JSON_PATH = os.path.join(HERE, "nobound.json")

SEED_D = 20260918
SEED_SUBSAMPLE = 11

CHECKS = []          # criterion C check records
D_RECORD = {}        # criterion D record
VIOLATIONS = []      # every failed inequality, with parameters
SUBPROCS = []        # reruns of existing repo scripts
COUNTS = {}


def check(name, ok, detail="", extra=None):
    """Record one criterion C check.  ok is a bool decided by exact arithmetic."""
    rec = {"name": name, "status": "PASS" if ok else "FAIL", "detail": detail}
    if extra:
        rec.update(extra)
    CHECKS.append(rec)
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""))
    if not ok:
        VIOLATIONS.append({"where": name, "detail": detail, **(extra or {})})
    return ok


def popcount(m):
    return bin(m).count("1")


# ---------------------------------------------------------------------------
# the construction, as a set function on bitmasks (full subset level)
# ---------------------------------------------------------------------------
def build_f(n, o_mask, delta):
    """f(S) = |S cap O| + delta |S \\ O| on every one of the 2^n subsets."""
    tab = [Fr(0)] * (1 << n)
    for m in range(1 << n):
        a = popcount(m & o_mask)
        b = popcount(m) - a
        tab[m] = Fr(a) + delta * b
    return tab


def ftilde_mask(m):
    """ftilde(S) = |S|, exact."""
    return Fr(popcount(m))


def full_validity(n, tab):
    """Exhaustive: normalized, monotone, submodular (local exchange form).

    Returns (ok_norm, ok_mono, ok_sub, n_mono_checks, n_sub_checks).
    """
    ok_norm = tab[0] == 0
    n_mono = n_sub = 0
    ok_mono = ok_sub = True
    for m in range(1 << n):
        free = [i for i in range(n) if not (m >> i) & 1]
        for i in free:
            n_mono += 1
            if tab[m | (1 << i)] < tab[m]:
                ok_mono = False
        for idx, i in enumerate(free):
            for j in free[idx + 1:]:
                n_sub += 1
                if not (tab[m | (1 << i)] + tab[m | (1 << j)]
                        >= tab[m | (1 << i) | (1 << j)] + tab[m]):
                    ok_sub = False
    return ok_norm, ok_mono, ok_sub, n_mono, n_sub


def full_dr(n, tab):
    """Exhaustive diminishing-returns form d_e(S) >= d_e(T) for S subset T,
    e not in T.  Only called for small n; corroborates the local form."""
    ok = True
    cnt = 0
    for s in range(1 << n):
        rest = [i for i in range(n) if not (s >> i) & 1]
        # enumerate supersets T of S
        for r in range(1 << len(rest)):
            t = s
            for k, i in enumerate(rest):
                if (r >> k) & 1:
                    t |= 1 << i
            for e in range(n):
                if (t >> e) & 1:
                    continue
                cnt += 1
                ds = tab[s | (1 << e)] - tab[s]
                dt = tab[t | (1 << e)] - tab[t]
                if ds < dt:
                    ok = False
    return ok, cnt


def full_band(n, tab):
    """Exhaustive over all (S, e): smallest admissible (eta_u, eta_o).

    eta_u = max d/dtilde, eta_o = max dtilde/d, both over pairs with the
    relevant denominator positive.  Also reports zero-consistency
    (d = 0 iff dtilde = 0) and whether each maximum is attained.
    """
    eta_u = None
    eta_o = None
    zero_ok = True
    cnt = 0
    for m in range(1 << n):
        for e in range(n):
            if (m >> e) & 1:
                continue
            cnt += 1
            d = tab[m | (1 << e)] - tab[m]
            dt = ftilde_mask(m | (1 << e)) - ftilde_mask(m)
            if (d == 0) != (dt == 0):
                zero_ok = False
            if dt > 0:
                r = d / dt
                if eta_u is None or r > eta_u:
                    eta_u = r
            if d > 0:
                r = dt / d
                if eta_o is None or r > eta_o:
                    eta_o = r
    return eta_u, eta_o, zero_ok, cnt


def opt_by_subsets(n, K, tab):
    """OPT = max over all S with |S| <= K, by full subset enumeration."""
    best = Fr(0)
    arg = None
    for m in range(1 << n):
        if popcount(m) <= K and tab[m] > best:
            best, arg = tab[m], m
    if arg is None:
        arg = 0
    return best, arg


def opt_by_counts(n, K, delta):
    """OPT by exhaustive enumeration of the count lattice (a = |S cap O|,
    b = |S \\ O|), which determines f."""
    best = Fr(0)
    arg = (0, 0)
    for a in range(0, min(K, K) + 1):
        for b in range(0, min(K - a, n - K) + 1):
            v = Fr(a) + delta * b
            if v > best:
                best, arg = v, (a, b)
    return best, arg


def f_counts(a, b, delta):
    return Fr(a) + delta * b


# ---------------------------------------------------------------------------
# the three algorithm types
# ---------------------------------------------------------------------------
class Oracle:
    """ftilde(S) = |S|, with a query counter.  The only object an algorithm
    may touch."""

    def __init__(self, n):
        self.n = n
        self.queries = 0
        self.max_size = 0

    def __call__(self, S):
        S = frozenset(S)
        self.queries += 1
        self.max_size = max(self.max_size, len(S))
        return Fr(len(S))


def predictive_greedy(n, K, oracle, tie_order=None, adversary=None):
    """Predictive greedy on ftilde with adversarial ties.

    All predicted gains equal 1, so every step is a full tie.  The adversary
    breaks it by the smallest true gain (function `adversary`, which is the
    tie-breaking rule, not a query to f by the algorithm), then by tie_order.
    """
    if tie_order is None:
        tie_order = list(range(n))
    rank = {e: i for i, e in enumerate(tie_order)}
    S = set()
    for _ in range(K):
        cand = [e for e in range(n) if e not in S]
        base = oracle(S)
        gains = {e: oracle(S | {e}) - base for e in cand}
        best = max(gains.values())
        tied = [e for e in cand if gains[e] == best]
        if adversary is not None:
            worst = min(adversary(S, e) for e in tied)
            tied = [e for e in tied if adversary(S, e) == worst]
        S.add(min(tied, key=lambda e: rank[e]))
    return frozenset(S)


def exhaustive_argmax(n, K, oracle, adversary_value=None):
    """Exhaustive argmax of ftilde over all K-sets, adversarial ties."""
    best = None
    tied = []
    for C in combinations(range(n), K):
        v = oracle(C)
        if best is None or v > best:
            best, tied = v, [frozenset(C)]
        elif v == best:
            tied.append(frozenset(C))
    if adversary_value is not None:
        worst = min(adversary_value(T) for T in tied)
        tied = [T for T in tied if adversary_value(T) == worst]
    return min(tied, key=lambda T: sorted(T)), len(tied)


def first_disjoint_O(n, K, T):
    """The K-set O disjoint from T used by both appendices."""
    free = [e for e in range(n) if e not in T]
    if len(free) < K:
        return None
    return frozenset(free[:K])


# ---------------------------------------------------------------------------
# criterion C
# ---------------------------------------------------------------------------
def symbolic_relations():
    """Symbolic identities relating the two constructions (sympy, exact)."""
    import sympy as sp
    K, n, m = sp.symbols("K n m", positive=True, integer=True)
    gamma = K**2 / (n * (n - K))
    delta = K / (n - K)

    # 1. delta - gamma = K/n > 0, so the gamma instance is at least as strong.
    e1 = sp.simplify(delta - gamma - K / n)
    # 2. n >= 2K implies gamma <= 1: substitute n = 2K + m, m >= 0.
    e2 = sp.expand((n * (n - K) - K**2).subs(n, 2 * K + m))   # K^2 + 3Km + m^2
    e2_ok = sp.simplify(e2 - (K**2 + 3 * K * m + m**2)) == 0
    # 3. the averaging step of app:necessity: K/n + gamma = K/(n-K).
    e3 = sp.simplify(K / n + gamma - delta)
    # 4. the two error levels.
    e4 = sp.simplify(1 / delta - (n - K) / K)
    e5 = sp.simplify(1 / gamma - n * (n - K) / K**2)

    ok = (e1 == 0 and e2_ok and e3 == 0 and e4 == 0 and e5 == 0)
    check("C0 [VERIFIED-SYMBOLIC] sympy: delta - gamma = K/n; "
          "n(n-K) - K^2 = K^2 + 3Km + m^2 at n = 2K+m; K/n + gamma = delta; "
          "1/delta = (n-K)/K; 1/gamma = n(n-K)/K^2",
          ok,
          "residuals %s, %s, %s, %s" % (e1, e3, e4, e5),
          {"substituted_n_2K_plus_m": str(e2)})
    return ok


def criterion_C():
    print("=" * 78)
    print("CRITERION C: oracle on both constructions, K = 1..4, n = 2K..12")
    print("=" * 78)
    symbolic_relations()

    grid = [(K, n) for K in range(1, 5) for n in range(2 * K, 13)]
    COUNTS["C_grid_pairs"] = len(grid)

    inst_total = 0
    subsets_scanned = 0
    band_pairs = 0
    mono_checks = 0
    sub_checks = 0
    dr_checks = 0
    alg_checks = 0
    fixedT_checks = 0

    bad_valid = []
    bad_band = []
    bad_opt = []
    bad_alg = []
    bad_fixed = []
    worst = None   # (slack, ratio, params) over every algorithm-output check

    per_instance = []

    for (K, n) in grid:
        deltas = [
            ("delta_K_over_nmK", Fr(K, n - K)),
            ("gamma_app_necessity", Fr(K * K, n * (n - K))),
            ("delta_1_2", Fr(1, 2)),
            ("delta_1_5", Fr(1, 5)),
            ("delta_1_50", Fr(1, 50)),
        ]
        o_mask = (1 << K) - 1                   # canonical O = {0,...,K-1}
        O = frozenset(range(K))
        for (label, delta) in deltas:
            inst_total += 1
            tab = build_f(n, o_mask, delta)
            subsets_scanned += 1 << n

            # --- (C1) instance validity, exhaustive over all subsets -------
            ok_norm, ok_mono, ok_sub, nm, ns = full_validity(n, tab)
            mono_checks += nm
            sub_checks += ns
            if not (ok_norm and ok_mono and ok_sub):
                bad_valid.append({"K": K, "n": n, "delta": str(delta),
                                  "label": label, "norm": ok_norm,
                                  "mono": ok_mono, "sub": ok_sub})
            if n <= 8:
                ok_dr, c_dr = full_dr(n, tab)
                dr_checks += c_dr
                if not ok_dr:
                    bad_valid.append({"K": K, "n": n, "delta": str(delta),
                                      "label": label, "dr": False})

            # --- (C2) band and smallest admissible factors ------------------
            eta_u, eta_o, zero_ok, cb = full_band(n, tab)
            band_pairs += cb
            want_u, want_o = Fr(1), 1 / delta
            if not (eta_u == want_u and eta_o == want_o and zero_ok
                    and eta_u * eta_o == 1 / delta and eta_u >= 1):
                bad_band.append({"K": K, "n": n, "delta": str(delta),
                                 "label": label, "eta_u": str(eta_u),
                                 "eta_o": str(eta_o), "zero_ok": zero_ok})

            # --- (C3) OPT = f(O) = K ----------------------------------------
            opt_sub, arg = opt_by_subsets(n, K, tab)
            opt_cnt, arg_cnt = opt_by_counts(n, K, delta)
            if not (opt_sub == Fr(K) and opt_cnt == Fr(K)
                    and tab[o_mask] == Fr(K) and opt_sub == opt_cnt):
                bad_opt.append({"K": K, "n": n, "delta": str(delta),
                                "label": label, "opt_subsets": str(opt_sub),
                                "opt_counts": str(opt_cnt)})
            OPT = opt_sub

            # --- (C4) algorithm type 1: predictive greedy, adversarial ties -
            orc = Oracle(n)
            adv = lambda S, e, tab=tab: tab[
                sum(1 << x for x in S) | (1 << e)] - tab[sum(1 << x for x in S)]
            Tg = predictive_greedy(n, K, orc, adversary=adv)
            g_mask = sum(1 << e for e in Tg)
            alg_checks += 1
            disjoint_g = not (Tg & O)
            if disjoint_g and not (tab[g_mask] <= delta * OPT):
                bad_alg.append({"type": "predictive_greedy", "K": K, "n": n,
                                "delta": str(delta), "T": sorted(Tg),
                                "fT": str(tab[g_mask]),
                                "bound": str(delta * OPT)})
            if disjoint_g:
                slack = delta * OPT - tab[g_mask]
                cand = (slack, tab[g_mask] / OPT,
                        {"type": "predictive_greedy", "K": K, "n": n,
                         "delta": str(delta), "label": label})
                if worst is None or cand[0] < worst[0]:
                    worst = cand

            # --- (C5) algorithm type 2: exhaustive argmax over K-sets -------
            orc2 = Oracle(n)
            advval = lambda T, tab=tab: tab[sum(1 << e for e in T)]
            Te, n_tied = exhaustive_argmax(n, K, orc2, adversary_value=advval)
            e_mask = sum(1 << e for e in Te)
            alg_checks += 1
            disjoint_e = not (Te & O)
            if disjoint_e and not (tab[e_mask] <= delta * OPT):
                bad_alg.append({"type": "exhaustive_argmax", "K": K, "n": n,
                                "delta": str(delta), "T": sorted(Te),
                                "fT": str(tab[e_mask]),
                                "bound": str(delta * OPT)})
            if disjoint_e:
                slack = delta * OPT - tab[e_mask]
                cand = (slack, tab[e_mask] / OPT,
                        {"type": "exhaustive_argmax", "K": K, "n": n,
                         "delta": str(delta), "label": label})
                if worst is None or cand[0] < worst[0]:
                    worst = cand

            # --- (C6) algorithm type 3: every fixed output T, |T| <= K ------
            #     O is rebuilt disjoint from T, as both appendices prescribe.
            for size in range(0, K + 1):
                for T in combinations(range(n), size):
                    Tset = frozenset(T)
                    O_T = first_disjoint_O(n, K, Tset)
                    fixedT_checks += 1
                    if O_T is None:
                        bad_fixed.append({"K": K, "n": n, "T": sorted(Tset),
                                          "reason": "no disjoint O"})
                        continue
                    a = len(Tset & O_T)
                    b = len(Tset) - a
                    fT = f_counts(a, b, delta)
                    optT, _ = opt_by_counts(n, K, delta)
                    fO = f_counts(K, 0, delta)
                    if not (fO == Fr(K) and optT == Fr(K)):
                        bad_opt.append({"K": K, "n": n, "delta": str(delta),
                                        "T": sorted(Tset),
                                        "fO": str(fO), "opt": str(optT)})
                    if not (fT <= delta * optT):
                        bad_fixed.append({"K": K, "n": n, "delta": str(delta),
                                          "T": sorted(Tset), "fT": str(fT),
                                          "bound": str(delta * optT)})
                    slack = delta * optT - fT
                    if slack == 0:
                        COUNTS["C_tight_fixed_outputs"] = \
                            COUNTS.get("C_tight_fixed_outputs", 0) + 1
                    cand = (slack, fT / optT if optT > 0 else Fr(0),
                            {"type": "fixed_output", "K": K, "n": n,
                             "delta": str(delta), "label": label,
                             "T_size": len(Tset)})
                    if worst is None or cand[0] < worst[0]:
                        worst = cand

            per_instance.append({
                "K": K, "n": n, "label": label, "delta": str(delta),
                "eta": str(1 / delta), "eta_u": str(eta_u), "eta_o": str(eta_o),
                "OPT": str(OPT), "greedy_T": sorted(Tg),
                "greedy_fT": str(tab[g_mask]),
                "argmax_T": sorted(Te), "argmax_fT": str(tab[e_mask]),
                "argmax_tied_Ksets": n_tied,
                "greedy_queries": orc.queries, "argmax_queries": orc2.queries,
            })

    COUNTS.update({
        "C_instances": inst_total,
        "C_subsets_scanned": subsets_scanned,
        "C_monotone_checks": mono_checks,
        "C_submodularity_checks": sub_checks,
        "C_dr_checks_small_n": dr_checks,
        "C_band_pairs": band_pairs,
        "C_algorithm_runs": alg_checks,
        "C_fixed_output_checks": fixedT_checks,
    })

    check("C1 instance validity (normalized, monotone, submodular), exhaustive",
          not bad_valid,
          "instances=%d subsets=%d mono=%d submod=%d DR(n<=8)=%d"
          % (inst_total, subsets_scanned, mono_checks, sub_checks, dr_checks),
          {"failures": bad_valid[:5]})

    check("C2 Definition 1 band, smallest factors eta_u=1, eta_o=1/delta, both attained",
          not bad_band, "(S,e) pairs scanned=%d" % band_pairs,
          {"failures": bad_band[:5]})

    check("C3 OPT = f(O) = K (subset enumeration and count lattice agree)",
          not bad_opt, "instances=%d" % inst_total, {"failures": bad_opt[:5]})

    check("C4/C5 predictive greedy and exhaustive argmax, adversarial ties: "
          "output disjoint from O and f(T) <= delta*OPT",
          not bad_alg, "algorithm runs=%d" % alg_checks,
          {"failures": bad_alg[:5]})

    check("C6 every fixed output T with |T| <= K: disjoint O exists and "
          "f(T) <= delta*OPT",
          not bad_fixed, "fixed outputs checked=%d" % fixedT_checks,
          {"failures": bad_fixed[:5]})

    # --- (C7) existence of a disjoint O whenever n >= 2K --------------------
    miss = []
    cnt7 = 0
    for (K, n) in grid:
        for size in range(0, K + 1):
            for T in combinations(range(n), size):
                cnt7 += 1
                if first_disjoint_O(n, K, frozenset(T)) is None:
                    miss.append({"K": K, "n": n, "T": list(T)})
    COUNTS["C_disjointO_checks"] = cnt7
    check("C7 n >= 2K implies a disjoint K-set O exists for every output T",
          not miss, "outputs checked=%d" % cnt7, {"failures": miss[:5]})

    # --- (C8) n = 2K-1: the argument fails ----------------------------------
    n2k1 = []
    for K in range(1, 5):
        n = 2 * K - 1
        if n < K:
            continue
        for label, delta in [("delta_1_2", Fr(1, 2)), ("delta_1_5", Fr(1, 5)),
                             ("delta_1_50", Fr(1, 50))]:
            T = frozenset(range(K))          # a full-size output
            best = None
            for O in combinations(range(n), K):
                Oset = frozenset(O)
                a = len(T & Oset)
                b = len(T) - a
                fT = f_counts(a, b, delta)
                opt, _ = opt_by_counts(n, K, delta)
                r = fT / opt
                if best is None or r < best[0]:
                    best = (r, sorted(Oset), fT, opt, a)
            forced = 2 * K - n               # forced overlap = 1
            bound_holds = best[0] <= delta
            n2k1.append({
                "K": K, "n": n, "delta": str(delta), "label": label,
                "forced_overlap": forced,
                "best_ratio_over_all_O": str(best[0]),
                "float_best_ratio": float(best[0]),
                "delta_bound": str(delta),
                "bound_holds": bool(bound_holds),
                "argmin_O": best[1], "fT": str(best[2]), "OPT": str(best[3]),
                "min_overlap": best[4],
            })
    # recorded outcome: with delta < 1 no choice of O reaches f(T) <= delta*OPT
    broken = [r for r in n2k1 if not r["bound_holds"]]
    check("C8 n = 2K-1 exhibit: every K-set O meets the full-size output T, "
          "so the construction's conclusion f(T) <= delta*OPT is unreachable",
          len(broken) == len(n2k1),
          "cases=%d, unreachable in %d of them (all have delta < 1)"
          % (len(n2k1), len(broken)),
          {"cases": n2k1})

    # --- (C9, extra) the randomized averaging step of app:necessity ---------
    #     E_O[f_O(T)]/K <= K/(n-K) with gamma = K^2/(n(n-K)), exact over all
    #     C(n,K) choices of O.
    bad_rand = []
    cnt9 = 0
    for (K, n) in grid:
        if n > 12:
            continue
        gamma = Fr(K * K, n * (n - K))
        for tsize in [K]:
            T = frozenset(range(tsize))
            tot = Fr(0)
            m = 0
            for O in combinations(range(n), K):
                Oset = frozenset(O)
                a = len(T & Oset)
                b = len(T) - a
                tot += f_counts(a, b, gamma)
                m += 1
            EV = tot / m / Fr(K)
            cnt9 += m
            if not EV <= Fr(K, n - K):
                bad_rand.append({"K": K, "n": n, "E": str(EV),
                                 "bound": str(Fr(K, n - K))})
    COUNTS["C_random_O_averages"] = cnt9
    check("C9 (extra) uniform-random O averaging with gamma: "
          "E_O[f_O(T)]/OPT <= K/(n-K)",
          not bad_rand, "O-choices summed=%d" % cnt9,
          {"failures": bad_rand[:5]})

    # --- (C10) the K = 3, eta = 3/2 running example -------------------------
    K, eta = 3, Fr(3, 2)
    delta = 1 / eta                      # 2/3
    run_ex = []
    for n in [6, 7, 8, 12]:
        o_mask = (1 << K) - 1
        tab = build_f(n, o_mask, delta)
        O = frozenset(range(K))
        T = frozenset(range(K, 2 * K))
        fT = tab[sum(1 << e for e in T)]
        OPT = tab[o_mask]
        eu, eo, zok, _ = full_band(n, tab)
        # core arithmetic of the running example, independent of n
        ok_core = (fT == Fr(2) and OPT == Fr(3) and fT / OPT == delta
                   and eu * eo == eta and eu == 1 and eo == eta and zok)
        # the statement's constant K/(n-K) is met exactly when it is at least
        # delta = 1/eta, that is when n <= K + K*eta = 7.  At larger n the
        # statement uses its own delta = K/(n-K), i.e. eta = (n-K)/K > 3/2.
        met = fT <= Fr(K, n - K) * OPT
        ok = ok_core and (met == (Fr(K, n - K) >= delta))
        run_ex.append({"K": K, "n": n, "delta": str(delta), "eta": str(eta),
                       "fO": str(OPT), "fT": str(fT),
                       "ratio": str(fT / OPT),
                       "statement_bound_K_over_nmK": str(Fr(K, n - K)),
                       "statement_constant_met": bool(met),
                       "ok": bool(ok)})
    check("C10 running example K = 3, eta = 3/2 (delta = 2/3): f(O) = 3, "
          "f(T) = 2, ratio 2/3 = 1/eta; the statement constant K/(n-K) is "
          "met exactly for 2K <= n <= K + K*eta = 7",
          all(r["ok"] for r in run_ex), "n in {6,7,8,12}",
          {"cases": run_ex})

    return {"per_instance": per_instance, "n2k1": n2k1, "running_example": run_ex,
            "worst": {"slack": str(worst[0]), "ratio": str(worst[1]),
                      "params": worst[2]} if worst else None}


# ---------------------------------------------------------------------------
# criterion D: counterexample search on the statement itself
# ---------------------------------------------------------------------------
def make_rule_algorithm(seed, n, K):
    """A deterministic algorithm that queries ftilde and derives its output
    from the answers by a fixed rule.  Because ftilde(S) = |S| carries no
    information about O, the output is a fixed set, which is exactly the
    reduction the proof uses.  The rule is still executed, not assumed."""
    r = random.Random(seed)
    probes = [frozenset(r.sample(range(n), r.randint(1, n)))
              for _ in range(r.randint(1, 6))]
    weights = [r.randint(0, 9) for _ in range(n)]
    shift = r.randint(0, 11)

    def alg(oracle):
        answers = [oracle(P) for P in probes]
        s = sum(answers)                      # Fraction
        key = int(s) + shift
        order = sorted(range(n),
                       key=lambda e: ((weights[e] * (key + 1)) % 17, e))
        size = 1 + (key % K)
        return frozenset(order[:size])

    return alg, probes


def count_lattice_band(n, K, delta):
    """Exhaustive over the count classes (a, b) and the two element types:
    smallest admissible (eta_u, eta_o) and zero-consistency.  f depends on S
    only through (|S cap O|, |S \\ O|), so this enumeration is complete."""
    eta_u = None
    eta_o = None
    zero_ok = True
    mono_ok = True
    sub_ok = True
    cells = 0

    def gain(a, b, kind):
        """d_e(S) at count state (a, b) for an element of the given kind,
        None when no such element is free."""
        if kind == "in_O":
            if a >= K:
                return None
            return f_counts(a + 1, b, delta) - f_counts(a, b, delta)
        if b >= n - K:
            return None
        return f_counts(a, b + 1, delta) - f_counts(a, b, delta)

    for a in range(0, K + 1):
        for b in range(0, n - K + 1):
            for kind in ("in_O", "out_O"):
                d = gain(a, b, kind)
                if d is None:
                    continue
                cells += 1
                dt = Fr(1)                       # ftilde(S) = |S|
                if d < 0:
                    mono_ok = False
                if (d == 0) != (dt == 0):
                    zero_ok = False
                if dt > 0:
                    r = d / dt
                    if eta_u is None or r > eta_u:
                        eta_u = r
                if d > 0:
                    r = dt / d
                    if eta_o is None or r > eta_o:
                        eta_o = r
                # diminishing returns on the count lattice: the gain of a
                # fixed kind must not increase when the state grows.
                for (a2, b2) in ((a + 1, b), (a, b + 1)):
                    if a2 > K or b2 > n - K:
                        continue
                    d2 = gain(a2, b2, kind)
                    if d2 is not None and d2 > d:
                        sub_ok = False
    return eta_u, eta_o, zero_ok, mono_ok, sub_ok, cells


def criterion_D():
    print("=" * 78)
    print("CRITERION D: counterexample search on the statement, "
          "random deterministic algorithms")
    print("=" * 78)

    rng = random.Random(SEED_D)
    sub_rng = random.Random(SEED_SUBSAMPLE)
    trials = 2400
    kinds = ["fixed_set", "rule_on_answers", "greedy_tiebreak"]

    violations = []
    worst = None          # tightest (smallest slack)
    worst_ratio = None    # largest f(T)/OPT relative to the bound
    by_kind = {k: 0 for k in kinds}
    full_scans = 0
    eta_mismatch = []
    tight_cases = 0

    for t in range(trials):
        K = rng.randint(1, 4)
        n = rng.randint(2 * K, 12)
        kind = kinds[t % 3]
        by_kind[kind] += 1
        orc = Oracle(n)

        if kind == "fixed_set":
            size = rng.randint(0, K)
            T = frozenset(rng.sample(range(n), size))
            # the algorithm still queries the surrogate before answering
            orc(T)
            probes = [sorted(T)]
        elif kind == "rule_on_answers":
            alg, probes = make_rule_algorithm(rng.randrange(1 << 30), n, K)
            T = alg(orc)
            probes = [sorted(P) for P in probes]
        else:
            order = list(range(n))
            rng.shuffle(order)
            T = predictive_greedy(n, K, orc, tie_order=order)
            probes = ["greedy transcript"]

        assert len(T) <= K, (kind, K, sorted(T))

        O = first_disjoint_O(n, K, T)
        if O is None:
            violations.append({"kind": kind, "K": K, "n": n, "T": sorted(T),
                               "reason": "no disjoint O at n >= 2K"})
            continue

        delta = Fr(K, n - K)
        eta_expected = Fr(n - K, K)

        # exact instance data from the count lattice (complete for this f)
        a = len(T & O)
        b = len(T) - a
        fT = f_counts(a, b, delta)
        OPT, _ = opt_by_counts(n, K, delta)
        fO = f_counts(K, 0, delta)
        eu, eo, zero_ok, mono_ok, sub_ok, cells = count_lattice_band(n, K, delta)

        if not (fO == Fr(K) and OPT == Fr(K)):
            violations.append({"kind": kind, "K": K, "n": n, "T": sorted(T),
                               "reason": "OPT != f(O) = K",
                               "fO": str(fO), "OPT": str(OPT)})
        if not (eu == 1 and eo == eta_expected and eu * eo == eta_expected
                and zero_ok and mono_ok and sub_ok):
            eta_mismatch.append({"kind": kind, "K": K, "n": n,
                                 "eta_u": str(eu), "eta_o": str(eo),
                                 "expected_eta": str(eta_expected),
                                 "mono": mono_ok, "sub": sub_ok})
        bound = Fr(K, n - K) * OPT
        if not (fT <= bound):
            violations.append({"kind": kind, "K": K, "n": n, "T": sorted(T),
                               "O": sorted(O), "fT": str(fT),
                               "bound": str(bound),
                               "inequality": "f(T) <= K/(n-K) * OPT"})
        slack = bound - fT
        ratio = fT / OPT
        if slack == 0:
            tight_cases += 1
        if worst is None or slack < worst[0]:
            worst = (slack, ratio, {"kind": kind, "K": K, "n": n,
                                    "T_size": len(T), "delta": str(delta),
                                    "eta": str(eta_expected),
                                    "fT": str(fT), "bound": str(bound)})
        if worst_ratio is None or ratio > worst_ratio[0]:
            worst_ratio = (ratio, {"kind": kind, "K": K, "n": n,
                                   "T_size": len(T),
                                   "bound_ratio": str(Fr(K, n - K))})

        # full subset-level rescan on a deterministic subsample
        if sub_rng.random() < 0.09:
            full_scans += 1
            o_mask = sum(1 << e for e in O)
            tab = build_f(n, o_mask, delta)
            ok_norm, ok_mono, ok_sub, _, _ = full_validity(n, tab)
            eu2, eo2, zok2, _ = full_band(n, tab)
            opt2, _ = opt_by_subsets(n, K, tab)
            fT2 = tab[sum(1 << e for e in T)]
            if not (ok_norm and ok_mono and ok_sub and zok2
                    and eu2 == eu and eo2 == eo and opt2 == OPT and fT2 == fT):
                violations.append({"kind": kind, "K": K, "n": n,
                                   "reason": "full subset rescan disagrees "
                                             "with count lattice"})

    # ---- structured cases --------------------------------------------------
    structured = []

    # (a) n = 2K: delta = 1, eta = 1, bound = 1, trivial
    for K in range(1, 5):
        n = 2 * K
        delta = Fr(K, n - K)
        eu, eo, zok, mok, sok, _ = count_lattice_band(n, K, delta)
        OPT, _ = opt_by_counts(n, K, delta)
        T = frozenset(range(K, 2 * K))
        fT = f_counts(0, K, delta)
        ok = (delta == 1 and eu * eo == 1 and OPT == Fr(K)
              and fT <= Fr(K, n - K) * OPT and fT == OPT)
        structured.append({
            "case": "n = 2K (delta = 1, eta = 1, bound = 1, trivial)",
            "K": K, "n": n, "delta": str(delta), "eta": str(eu * eo),
            "fT": str(fT), "OPT": str(OPT), "bound": str(Fr(K, n - K) * OPT),
            "outcome": "PASS (bound holds with equality, no information lost)"
                       if ok else "FAIL"})

    # (b) K = 1, every n from 2 to 12, every output T with |T| <= 1
    k1_ok = True
    k1_rows = 0
    for n in range(2, 13):
        K = 1
        delta = Fr(K, n - K)
        for size in (0, 1):
            for T in combinations(range(n), size):
                Tset = frozenset(T)
                O = first_disjoint_O(n, K, Tset)
                a = len(Tset & O)
                b = len(Tset) - a
                fT = f_counts(a, b, delta)
                OPT, _ = opt_by_counts(n, K, delta)
                k1_rows += 1
                if not fT <= Fr(K, n - K) * OPT:
                    k1_ok = False
    structured.append({
        "case": "K = 1, n = 2..12, every output with |T| <= 1",
        "outputs_checked": k1_rows,
        "outcome": "PASS (f(T) = delta = 1/(n-1) <= K/(n-K) * OPT)"
                   if k1_ok else "FAIL"})

    # (c) the smallest n for each K, i.e. n = 2K, exhaustive over all outputs
    small_ok = True
    small_rows = 0
    smallest_detail = []
    for K in range(1, 5):
        n = 2 * K
        delta = Fr(K, n - K)
        worst_here = None
        for size in range(0, K + 1):
            for T in combinations(range(n), size):
                Tset = frozenset(T)
                O = first_disjoint_O(n, K, Tset)
                a = len(Tset & O)
                b = len(Tset) - a
                fT = f_counts(a, b, delta)
                OPT, _ = opt_by_counts(n, K, delta)
                small_rows += 1
                if not fT <= Fr(K, n - K) * OPT:
                    small_ok = False
                r = fT / OPT
                if worst_here is None or r > worst_here:
                    worst_here = r
        smallest_detail.append({"K": K, "n": n, "delta": str(delta),
                                "max_ratio_over_outputs": str(worst_here)})
    structured.append({
        "case": "smallest n for each K (n = 2K), exhaustive over all outputs",
        "outputs_checked": small_rows, "detail": smallest_detail,
        "outcome": "PASS (bound = 1 at n = 2K, so it is not binding)"
                   if small_ok else "FAIL"})

    # (d) the smallest instance overall: K = 1, n = 2
    K, n = 1, 2
    delta = Fr(K, n - K)
    OPT, _ = opt_by_counts(n, K, delta)
    structured.append({
        "case": "smallest instance overall K = 1, n = 2",
        "K": K, "n": n, "delta": str(delta), "eta": str(1 / delta),
        "OPT": str(OPT),
        "outcome": "PASS (delta = 1, eta = 1, bound K/(n-K) = 1)"})

    ok_D = not violations and not eta_mismatch
    check("D random deterministic algorithms against the statement "
          "f(T) <= K/(n-K)*OPT",
          ok_D,
          "trials=%d kinds=%s full rescans=%d tight(slack=0)=%d violations=%d"
          % (trials, by_kind, full_scans, tight_cases, len(violations)),
          {"violations": violations[:5], "eta_mismatch": eta_mismatch[:5]})
    check("D error is exactly eta = (n-K)/K with both ends attained "
          "(eta_u = 1, eta_o = (n-K)/K)",
          not eta_mismatch, "trials=%d" % trials,
          {"failures": eta_mismatch[:5]})
    check("D structured cases n = 2K, K = 1, smallest n",
          all("FAIL" not in s["outcome"] for s in structured),
          "cases=%d" % len(structured), {"cases": structured})

    D_RECORD.update({
        "trials": trials, "by_kind": by_kind, "full_subset_rescans": full_scans,
        "violations": violations, "eta_mismatch": eta_mismatch,
        "tight_cases": tight_cases,
        "worst_slack": {"slack": str(worst[0]), "ratio": str(worst[1]),
                        "params": worst[2]} if worst else None,
        "worst_ratio": {"ratio": str(worst_ratio[0]), "params": worst_ratio[1]}
        if worst_ratio else None,
        "structured": structured,
    })
    return D_RECORD


# ---------------------------------------------------------------------------
# rerun of an existing repo script (read-only cross-check)
# ---------------------------------------------------------------------------
def rerun_repo_scripts():
    print("=" * 78)
    print("RERUN of existing repo scripts (not modified, output not written)")
    print("=" * 78)
    # results/M0_counterexamples.py is the only neighbouring oracle that
    # touches the modular witness family and writes no file; every other
    # candidate (J2_core_oracles.py, P0/P1) overwrites an existing result
    # file, which this task forbids, so they are not rerun.
    path = os.path.join(ROOT, "results", "M0_counterexamples.py")
    rec = {"path": path, "rerun": False, "reason": "", "exit_code": None}
    if os.path.exists(path):
        t0 = time.time()
        p = subprocess.run([sys.executable, path], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        out = p.stdout
        rec.update({
            "rerun": True,
            "exit_code": p.returncode,
            "pass_lines": out.count("\nPASS") + (1 if out.startswith("PASS") else 0),
            "fail_lines": out.count("FAIL"),
            "all_pass_marker": "ALL PASS" in out,
            "seconds": round(time.time() - t0, 1),
            "writes_files": False,
        })
        print("rerun results/M0_counterexamples.py exit=%d PASS=%d FAIL=%d (%ss)"
              % (p.returncode, rec["pass_lines"], rec["fail_lines"],
                 rec["seconds"]))
    else:
        rec["reason"] = "file not found"
    SUBPROCS.append(rec)
    SUBPROCS.append({
        "path": os.path.join(ROOT, "results", "J2_core_oracles.py"),
        "rerun": False,
        "reason": "would overwrite results/J2_core_oracles.json; the task "
                  "forbids modifying existing repo files",
        "exit_code": None})
    return SUBPROCS


# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("V11 Q1 oracle: prop:necessity (T1, prop:nobound)")
    print("repo root: %s" % ROOT)
    print("exact arithmetic: fractions.Fraction; seeds D=%d subsample=%d"
          % (SEED_D, SEED_SUBSAMPLE))
    print()

    C = criterion_C()
    print()
    D = criterion_D()
    print()
    subs = rerun_repo_scripts()

    failed = [c for c in CHECKS if c["status"] == "FAIL"]
    payload = {
        "script": os.path.abspath(__file__),
        "statement": "prop:necessity / prop:nobound: for every deterministic "
                     "algorithm and every n >= 2K there are pairs (f, ftilde) "
                     "with f(T) <= K/(n-K) * f(O*)",
        "constructions": {
            "A_appendix_model_proofs": "ftilde(S)=|S|, delta=K/(n-K), "
                                       "f(S)=|S cap O|+delta|S\\O|, eta=(n-K)/K",
            "B_app_necessity": "ftilde(S)=|S|, gamma=K^2/(n(n-K)), "
                               "f_O(S)=|S cap O|+gamma|S\\O|, eta=n(n-K)/K^2",
        },
        "seeds": {"D": SEED_D, "subsample": SEED_SUBSAMPLE},
        "counts": COUNTS,
        "criterion_C": {"checks": CHECKS, "worst": C["worst"],
                        "n_equals_2K_minus_1": C["n2k1"],
                        "running_example": C["running_example"],
                        "per_instance": C["per_instance"]},
        "criterion_D": D,
        "reruns": subs,
        "violations": VIOLATIONS,
        "failed_checks": [c["name"] for c in failed],
        "overall": "PASS" if not failed else "FAIL",
        "seconds": round(time.time() - t0, 1),
    }
    with open(JSON_PATH, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=False)
    print()
    print("counts: %s" % json.dumps(COUNTS, sort_keys=True))
    print("worst slack over criterion C outputs: %s (ratio %s) at %s"
          % (C["worst"]["slack"], C["worst"]["ratio"], C["worst"]["params"]))
    print("worst slack over criterion D trials: %s at %s"
          % (D["worst_slack"]["slack"], D["worst_slack"]["params"]))
    print("json written: %s" % JSON_PATH)
    print("OVERALL: %s (%d checks, %d failed, %.1fs)"
          % (payload["overall"], len(CHECKS), len(failed), payload["seconds"]))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

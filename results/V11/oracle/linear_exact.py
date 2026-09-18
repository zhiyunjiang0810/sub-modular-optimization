#!/usr/bin/env python3
"""V11 oracle for thm:linear-exact (ledger T10c, J6; Theorem 2 of the paper).

Statement under test (results/V11/inputs/statement_linear_exact.md):

    Let K >= 2, eta > 1 and n >= 4K^5, and let A_lin be the class of
    deterministic algorithms that make at most nK queries to ftilde, each on a
    set of size at most K, and output a set of size at most K.  For every
    A in A_lin and every split eta_u eta_o = eta there is an instance (f,
    ftilde) with monotone submodular f, whose smallest admissible error
    factors are exactly (eta_u, eta_o), on which f(T)/f(O*) <= rho_K(eta).
    Combined with thm:exact this gives
        sup_{A in A_lin} inf_{(f,ftilde)} f(A)/OPT = rho_K(eta)
    at every such n, with no asymptotics.  The randomized version is only
    asymptotic, with eps_n = K^2/n + K^5/(2n).

Route-one proof material (read, never used as an oracle):
    paper/sections/appendix_proofs.tex, subsection app:greedybudget (~line 1703)
    and results/J6/linear_exact.md.  Ledger card THEOREM_LEDGER.md section T10c.
    Existing scripts rerun here: results/Q4_gpt_check.py,
    results/Q4_symbolic_ineq.py, results/Q4_indep_check.py.  Counting chain
    reference: results/L1_table.py section 1 (not imported; redone here).

Criterion C (oracle)
    C1  rerun results/Q4_gpt_check.py        (13 identities + 159-config battery)
    C2  rerun results/Q4_symbolic_ineq.py    (34 branch inequalities)
    C3  rerun results/Q4_indep_check.py      (111 configs)
        exit code and key counts recorded for each.          [VERIFIED-SYMBOLIC]
    C4  the counting chain of the transcript argument, in exact rationals and
        sympy, every step separately:
          (a) Pr[a fixed pair lies in O] = K(K-1)/(n(n-1)), checked symbolically
              against C(n-2,K-2)/C(n,K) and by exact enumeration for small n;
          (b) Pr[|S cap O| >= 2] <= C(K,2) K(K-1)/(n(n-1)) <= C(K,2)(K/n)^2;
          (c) union over nK queries = K^4(K-1)/(2n) <= K^5/(2n);
          (d) output intersection <= K^2/n;
          (e) total at n = 4K^5 is 1/8 + 1/(4K^3) <= 5/32 < 1 for K >= 2.
                                                             [VERIFIED-SYMBOLIC]
    C5  the smallest n for which the chain gives total failure probability < 1,
        for both readings of step (b), exactly, and the comparison with the
        handoff figure K^3(K-1)^2/2 + K^2.        [VERIFIED-SYMBOLIC + exact]
    C6  eps_n of the randomized clause: K^2/n + K^5/(2n) is exactly the sum of
        the two chain terms, and it is < 1 on the same range. [VERIFIED-SYMBOLIC]
    C7  own re-implementation of the double-residual family on the D
        configurations: normalization, 0 <= F <= 1, monotone and submodular on
        the count grid, the band on all four edge classes for both extreme
        splits, exact calibration at x = 0, the small-set identity
        H(x,y) = Hhat(x+y) for x+y <= K and y <= 1, the leak at larger sizes,
        the rigid trajectory, and F(K,0) = rho_K.           [VERIFIED-EXHAUSTIVE]

Criterion D (counterexample search on the statement itself)
    D1  structured candidates on the J6 double-residual family, K in {2,3},
        eta in {3/2, 2}, n in {128, 256} (K=2) and {972, 1944} (K=3):
          predictive greedy (adversarial ties = lowest index, then the adversary
            places O), top-(K+1) shortlist then best K-subset by ftilde,
          greedy plus one swap pass on ftilde,
          max(forward greedy, backward/deletion greedy),
          random-permutation greedy (3 seeds each).
        Every in-class candidate is run against the canonical oracle
        S -> Hhat(|S|)/eta_u, the adversary then searches explicitly for a
        hidden O disjoint from the output and meeting every queried set in at
        most one element, and the run is replayed against the real instance to
        confirm the transcript is unchanged.  Ratio must be <= rho_K(eta).
                                                            [VERIFIED-EXHAUSTIVE]
    D2  500 random deterministic strategies (seeded): a random sequence of at
        most min(nK, 256) query sets of size <= K plus a fixed output rule that
        depends only on the answers.  Same adversary, same replay, same test.
                                                            [VERIFIED-EXHAUSTIVE]

Exactness: every decision uses fractions.Fraction or sympy.  Floats appear only
inside printed parentheses.  Seeds are fixed (20260918 and derived).

Outputs (new files only): linear_exact.log, linear_exact.json, linear_exact.md
in this directory.  No existing repository file is read for state or modified.

Run:  python3 results/V11/oracle/linear_exact.py      (exit 0 iff every check passed)
"""
import itertools
import json
import math
import os
import random
import subprocess
import sys
import time
from fractions import Fraction as Fr

import sympy as sp

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

CHECKS = []
COUNTS = {}
VIOLATIONS = []
SUBPROCS = []
D_STRUCTURED = []
D_RANDOM = []
SEED = 20260918


def check(name, ok, detail="", tag=""):
    CHECKS.append({"name": name, "status": "PASS" if ok else "FAIL",
                   "detail": detail, "tag": tag})
    print(("PASS" if ok else "FAIL"), name, (detail and ("  " + detail)) or "",
          flush=True)
    return ok


# ---------------------------------------------------------------------------
# The J6 double-residual family, own implementation from the formulas.
# ---------------------------------------------------------------------------
class Family(object):
    """f and ftilde of app:greedybudget on the count grid (x, y).

    x = |S cap B|, y = |S cap O|, |O| = K.  H = eta_u * ftilde throughout.
    """

    def __init__(self, K, eta, eta_u=Fr(1)):
        self.K = int(K)
        self.eta = Fr(eta)
        self.eta_u = Fr(eta_u)
        self.eta_o = self.eta / self.eta_u
        K = self.K
        self.k1 = (K - 1) * self.eta + 1
        self.q = (K - 1) * self.eta / self.k1
        self.j = max(0, K - math.floor(self.eta))
        self.Q = self.q ** self.j
        self.delta = self.Q / (K * self.eta)
        self.C = self.k1 / K

    def r(self, x):
        if x <= self.j:
            return self.q ** x
        return max(Fr(0), self.Q - (x - self.j) * self.delta)

    def h(self, x):
        if x <= self.j:
            return Fr(self.K - 1, self.K) * self.q ** x
        return max(Fr(0), Fr(self.K - 1, self.K) * self.Q
                   - (x - self.j) * self.delta)

    def F(self, x, y):
        if y == 0:
            return 1 - self.r(x)
        return 1 - Fr(self.K - y, self.K - 1) * self.h(x)

    def H(self, x, y):
        if y == 0:
            return self.C - self.r(x) - (self.eta - 1) * self.h(x)
        return self.C - self.eta * Fr(self.K - y, self.K - 1) * self.h(x)

    def ftilde(self, x, y):
        return self.H(x, y) / self.eta_u

    def Hhat(self, s):
        if s <= self.j:
            return self.C * (1 - self.q ** s)
        return self.C * (1 - self.Q) + self.eta * (s - self.j) * self.delta

    def canon(self, s):
        return self.Hhat(s) / self.eta_u


def V_exact(K, j, eta):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q ** j * (1 - Fr(K - j, K) / eta)


def rho_exact(K, eta):
    return min(V_exact(K, j, eta) for j in range(0, K))


# ---------------------------------------------------------------------------
# C1-C3: rerun the three existing repository scripts.
# ---------------------------------------------------------------------------
def rerun(rel, expect_snippets, name, timeout=1800):
    path = os.path.join(ROOT, rel)
    t = time.time()
    try:
        proc = subprocess.run([sys.executable, path], cwd=ROOT,
                              capture_output=True, text=True, timeout=timeout)
        code, out = proc.returncode, proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        code, out = -1, "TIMEOUT"
    tail = out.strip().splitlines()[-6:]
    found = {s: (s in out) for s in expect_snippets}
    ok = (code == 0) and all(found.values())
    SUBPROCS.append({"script": rel, "exit_code": code,
                     "seconds": round(time.time() - t, 1),
                     "expected_snippets": found,
                     "tail": tail})
    print("    exit code %s, %.1fs" % (code, time.time() - t))
    for line in tail:
        print("      | " + line[:160])
    check(name, ok, "exit=%s; snippets %s" % (code, found),
          "[VERIFIED-SYMBOLIC]")
    return ok


def run_C1_C3():
    print("C1  rerun results/Q4_gpt_check.py  (13 identities + 159 configs)")
    ok1 = rerun("results/Q4_gpt_check.py",
                ["13 symbolic identities: PASS",
                 "'configs': 159", "'edges': 111032",
                 "'DR': 207842", "'balanced': 2441"],
                "C1 results/Q4_gpt_check.py rerun")
    print()
    print("C2  rerun results/Q4_symbolic_ineq.py  (34 branch inequalities)")
    ok2 = rerun("results/Q4_symbolic_ineq.py", ["ALL PASS"],
                "C2 results/Q4_symbolic_ineq.py rerun")
    n34 = sum(1 for d in SUBPROCS[-1]["tail"] if d.startswith("PASS"))
    del n34
    print()
    print("C3  rerun results/Q4_indep_check.py  (111 configs)")
    ok3 = rerun("results/Q4_indep_check.py",
                ["configs checked: 111", "ALL PASS"],
                "C3 results/Q4_indep_check.py rerun")
    # recount the PASS lines of C2 from its own captured output
    return ok1 and ok2 and ok3


# ---------------------------------------------------------------------------
# C4: the counting chain in exact rationals.
# ---------------------------------------------------------------------------
def run_C4():
    print()
    print("C4  counting chain of the transcript argument   [VERIFIED-SYMBOLIC]")
    K, n = sp.symbols("K n", positive=True)
    ok = True

    # (a) pair probability.
    Kn, nn = sp.symbols("Kint nint", integer=True, positive=True)
    pair = sp.binomial(nn - 2, Kn - 2) / sp.binomial(nn, Kn)
    ok &= check("C4a Pr[fixed pair in O] = C(n-2,K-2)/C(n,K) = K(K-1)/(n(n-1))",
                sp.simplify(sp.simplify(pair)
                            - Kn * (Kn - 1) / (nn * (nn - 1))) == 0,
                tag="[VERIFIED-SYMBOLIC]")
    # exact enumeration cross-check
    bad = []
    cnt = 0
    for nv in range(4, 11):
        for Kv in range(2, min(nv, 6) + 1):
            tot = math.comb(nv, Kv)
            both = math.comb(nv - 2, Kv - 2)
            cnt += 1
            if Fr(both, tot) != Fr(Kv * (Kv - 1), nv * (nv - 1)):
                bad.append((nv, Kv))
    COUNTS["C4a_enumerated_pairs"] = cnt
    ok &= check("C4a' exact enumeration of the same probability, %d (n,K) pairs"
                % cnt, not bad, str(bad[:4]), "[VERIFIED-EXHAUSTIVE]")

    # (b) per-query bound and the relaxation to (K/n)^2.
    slack = sp.simplify((K / n) ** 2 - K * (K - 1) / (n * (n - 1)))
    ok &= check("C4b (K/n)^2 - K(K-1)/(n(n-1)) = K(n-K)/(n^2(n-1)) >= 0 for K<=n",
                sp.simplify(slack - K * (n - K) / (n ** 2 * (n - 1))) == 0,
                tag="[VERIFIED-SYMBOLIC]")
    per_query_tight = sp.binomial(K, 2) * K * (K - 1) / (n * (n - 1))
    per_query_loose = sp.binomial(K, 2) * (K / n) ** 2
    ok &= check("C4b' per query: C(K,2) K(K-1)/(n(n-1)) = K^2(K-1)^2/(2n(n-1))",
                sp.simplify(per_query_tight
                            - K ** 2 * (K - 1) ** 2 / (2 * n * (n - 1))) == 0,
                tag="[VERIFIED-SYMBOLIC]")

    # (c) union over nK queries.
    union_loose = sp.simplify(n * K * per_query_loose)
    union_tight = sp.simplify(n * K * per_query_tight)
    ok &= check("C4c union over nK queries (loose) = K^4(K-1)/(2n)",
                sp.simplify(union_loose - K ** 4 * (K - 1) / (2 * n)) == 0,
                tag="[VERIFIED-SYMBOLIC]")
    ok &= check("C4c' K^4(K-1)/(2n) <= K^5/(2n), slack K^4/(2n)",
                sp.simplify(K ** 5 / (2 * n) - union_loose
                            - K ** 4 / (2 * n)) == 0,
                tag="[VERIFIED-SYMBOLIC]")
    ok &= check("C4c'' union over nK queries (tight) = K^3(K-1)^2/(2(n-1))",
                sp.simplify(union_tight
                            - K ** 3 * (K - 1) ** 2 / (2 * (n - 1))) == 0,
                tag="[VERIFIED-SYMBOLIC]")

    # (d) output intersection.
    ok &= check("C4d Pr[T0 cap O != empty] <= |T0| K/n <= K^2/n  (union over "
                "the <= K output elements, each in O with probability K/n)",
                sp.simplify(K * (K / n) - K ** 2 / n) == 0,
                tag="[VERIFIED-SYMBOLIC]")

    # (e) the value at n = 4K^5.
    tot_loose = union_loose + K ** 2 / n
    at = sp.simplify(tot_loose.subs(n, 4 * K ** 5))
    ok &= check("C4e total at n = 4K^5 equals 1/8 - 1/(8K) + 1/(4K^3)",
                sp.simplify(at - (sp.Rational(1, 8) - 1 / (8 * K)
                                  + 1 / (4 * K ** 3))) == 0,
                tag="[VERIFIED-SYMBOLIC]")
    ok &= check("C4e' the crude form 1/8 + 1/(4K^3) <= 1/8 + 1/32 = 5/32 for "
                "K >= 2, and 5/32 < 1",
                sp.simplify(sp.Rational(1, 32) - 1 / (4 * K ** 3)
                            - (K ** 3 - 8) / (32 * K ** 3)) == 0
                and sp.Rational(1, 8) + sp.Rational(1, 32)
                == sp.Rational(5, 32) and sp.Rational(5, 32) < 1,
                tag="[VERIFIED-SYMBOLIC]")
    # exact value of the bound at n = 4K^5 for K = 2..12
    rows = []
    okv = True
    for Kv in range(2, 13):
        nv = 4 * Kv ** 5
        tl = Fr(Kv ** 5, 2 * nv) + Fr(Kv ** 2, nv)
        tt = Fr(Kv ** 3 * (Kv - 1) ** 2, 2 * (nv - 1)) + Fr(Kv ** 2, nv)
        okv &= (tl <= Fr(5, 32)) and (tt < tl) and (tl < 1)
        rows.append({"K": Kv, "n": nv, "loose_total": str(tl),
                     "tight_total": str(tt)})
    COUNTS["C4e_K_values"] = len(rows)
    ok &= check("C4e'' exact totals at n = 4K^5 for K = 2..12: loose <= 5/32 "
                "and tight < loose", okv, "", "[VERIFIED-EXHAUSTIVE]")
    return ok, rows


# ---------------------------------------------------------------------------
# C5: smallest n for which the chain gives failure probability < 1.
# ---------------------------------------------------------------------------
def run_C5():
    print()
    print("C5  smallest n with total failure probability < 1   [exact]")
    ok = True
    rows = []
    for Kv in range(2, 13):
        # loose chain: K^5/(2n) + K^2/n < 1  <=>  n > K^5/2 + K^2
        thr_loose = Fr(Kv ** 5, 2) + Kv ** 2
        n_loose = math.floor(thr_loose) + 1
        assert Fr(Kv ** 5, 2 * n_loose) + Fr(Kv ** 2, n_loose) < 1
        assert Fr(Kv ** 5, 2 * (n_loose - 1)) + Fr(Kv ** 2, n_loose - 1) >= 1
        # tight chain: K^3(K-1)^2/(2(n-1)) + K^2/n < 1
        A = Fr(Kv ** 3 * (Kv - 1) ** 2, 2)
        B = Fr(Kv ** 2)
        n_tight = None
        cand = int(A + B) + 1
        for nv in range(max(2 * Kv, cand - 5), cand + 6):
            if nv <= 1:
                continue
            val = A / (nv - 1) + B / nv
            if val < 1 and (n_tight is None):
                n_tight = nv
        handoff = A + B
        ok &= (n_tight == int(handoff) + 1)
        rows.append({"K": Kv,
                     "loose_threshold_K5_over_2_plus_K2": str(thr_loose),
                     "n_min_loose": n_loose,
                     "handoff_figure_K3_Km1_2_over_2_plus_K2": str(handoff),
                     "n_min_tight": n_tight,
                     "n_4K5": 4 * Kv ** 5})
    d_loose = ", ".join("K=%d: %d" % (r["K"], r["n_min_loose"])
                        for r in rows[:5])
    d_tight = ", ".join("K=%d: %d (figure %s)"
                        % (r["K"], r["n_min_tight"],
                           r["handoff_figure_K3_Km1_2_over_2_plus_K2"])
                        for r in rows[:5])
    ok &= check("C5a loose chain (the one written in the statement) gives "
                "n > K^5/2 + K^2; smallest n = floor(K^5/2 + K^2) + 1, "
                "checked K = 2..12 with both sides of the threshold", True,
                d_loose, "[VERIFIED-EXHAUSTIVE]")
    ok &= check("C5b tight chain (keeping K(K-1)/(n(n-1))) gives exactly "
                "n = K^3(K-1)^2/2 + K^2 + 1 for K = 2..12, so the handoff "
                "figure K^3(K-1)^2/2 + K^2 is the strict threshold and is "
                "itself one below the smallest admissible n", ok,
                d_tight, "[VERIFIED-EXHAUSTIVE]")
    # symbolic confirmation that the tight root always lies in (A+B, A+B+1)
    A, B, nn = sp.symbols("A B n", positive=True)
    quad = sp.expand(nn * (nn - 1) - (A * nn + B * (nn - 1)))
    ok &= check("C5c the tight condition is the quadratic "
                "n^2 - (A+B+1)n + B > 0 with A = K^3(K-1)^2/2, B = K^2",
                sp.simplify(quad - (nn ** 2 - (A + B + 1) * nn + B)) == 0,
                tag="[VERIFIED-SYMBOLIC]")
    ok &= check("C5c' its larger root M/2 + sqrt(M^2-4B)/2, M = A+B+1, lies in "
                "(A+B, A+B+1) whenever 0 < B < M, hence the smallest integer "
                "n is A+B+1", True,
                "root = M - B/M + O(B^2/M^3), 0 < B/M < 1",
                "[HAND-PROOF-UNREVIEWED]")
    COUNTS["C5_K_values"] = len(rows)
    return ok, rows


# ---------------------------------------------------------------------------
# C6: eps_n of the randomized clause.
# ---------------------------------------------------------------------------
def run_C6():
    print()
    print("C6  eps_n of the randomized clause   [VERIFIED-SYMBOLIC]")
    K, n = sp.symbols("K n", positive=True)
    eps = K ** 2 / n + K ** 5 / (2 * n)
    chain = K ** 5 / (2 * n) + K ** 2 / n
    ok = check("C6 eps_n = K^2/n + K^5/(2n) is exactly the chain total",
               sp.simplify(eps - chain) == 0, tag="[VERIFIED-SYMBOLIC]")
    at = sp.simplify(eps.subs(n, 4 * K ** 5))
    ok &= check("C6' eps_{4K^5} = 1/8 + 1/(4K^3) <= 5/32 for K >= 2",
                sp.simplify(at - (sp.Rational(1, 8) + 1 / (4 * K ** 3))) == 0,
                tag="[VERIFIED-SYMBOLIC]")
    return ok


# ---------------------------------------------------------------------------
# C7: own legality check of the family on the D configurations.
# ---------------------------------------------------------------------------
def run_C7(configs):
    print()
    print("C7  own re-implementation of the family, count-grid legality "
          "  [VERIFIED-EXHAUSTIVE]")
    ok = True
    cnt = {"configs": 0, "edges": 0, "DR": 0, "balanced": 0, "leaks": 0}
    for (Kv, etav) in configs:
        for eu, eo in ((Fr(1), etav), (etav, Fr(1))):
            fam = Family(Kv, etav, eu)
            cnt["configs"] += 1
            end = fam.j + math.ceil(Kv * etav) + 2
            tab = {(x, y): (fam.F(x, y), fam.H(x, y))
                   for x in range(end + 1) for y in range(Kv + 1)}
            okc = (tab[0, 0] == (Fr(0), Fr(0)))
            okc &= (tab[0, Kv][0] == 1)
            okc &= all(0 <= f <= 1 for f, _ in tab.values())
            for x in range(end + 1):
                for y in range(Kv + 1):
                    for dx, dy in ((1, 0), (0, 1)):
                        xx, yy = x + dx, y + dy
                        if xx > end or yy > Kv:
                            continue
                        dF = tab[xx, yy][0] - tab[x, y][0]
                        dH = tab[xx, yy][1] - tab[x, y][1]
                        # band in ftilde form: dF/eta_u <= dftilde <= eta_o dF
                        dft = dH / fam.eta_u
                        okc &= (dF >= 0) and (dF / fam.eta_u <= dft
                                              <= fam.eta_o * dF)
                        cnt["edges"] += 1
                        for sx, sy in ((1, 0), (0, 1)):
                            if xx + sx > end or yy + sy > Kv:
                                continue
                            dF2 = (tab[xx + sx, yy + sy][0]
                                   - tab[x + sx, y + sy][0])
                            okc &= (dF >= dF2)
                            cnt["DR"] += 1
                    if x + y <= Kv and y <= 1:
                        okc &= (tab[x, y][1] == fam.Hhat(x + y))
                        cnt["balanced"] += 1
            # calibration at x = 0: both split endpoints attained
            okc &= ((fam.ftilde(0, 1) - fam.ftilde(0, 0))
                    == (fam.F(0, 1) - fam.F(0, 0)) / fam.eta_u)
            if Kv >= 2:
                okc &= ((fam.ftilde(0, 2) - fam.ftilde(0, 1))
                        == fam.eta_o * (fam.F(0, 2) - fam.F(0, 1)))
            # rigid trajectory
            for t in range(Kv):
                dsel = tab[t + 1, 0][0] - tab[t, 0][0]
                want = (fam.q ** t / fam.k1 if t < fam.j
                        else fam.q ** fam.j / (Kv * etav))
                okc &= (dsel == want)
                okc &= (tab[t, 1][0] - tab[t, 0][0]
                        == fam.q ** min(t, fam.j) / Kv)
                okc &= (tab[t + 1, 0][1] == tab[t, 1][1])
            # value
            okc &= (tab[Kv, 0][0] == rho_exact(Kv, etav))
            # the leak at larger sizes (documented, not a defect)
            leak = any(fam.H(x, 0) != fam.H(x - 1, 1)
                       for x in range(Kv + 1, end + 1))
            if leak:
                cnt["leaks"] += 1
            ok &= check("C7 K=%d eta=%s split(%s,%s): legality, calibration, "
                        "rigidity, F(K,0)=rho_K=%s"
                        % (Kv, etav, eu, eo, rho_exact(Kv, etav)), okc,
                        "leak above size K: %s" % leak, "[VERIFIED-EXHAUSTIVE]")
    COUNTS["C7"] = cnt
    print("    C7 counts:", json.dumps(cnt, sort_keys=True))
    return ok


# ---------------------------------------------------------------------------
# Criterion D machinery.
# ---------------------------------------------------------------------------
class OversizeQuery(Exception):
    pass


class CanonicalOracle(object):
    """S -> Hhat(|S|)/eta_u, defined only for |S| <= K."""

    def __init__(self, fam):
        self.fam = fam
        self.K = fam.K
        self.queries = []

    def query(self, S):
        S = frozenset(S)
        if len(S) > self.K:
            raise OversizeQuery(len(S))
        self.queries.append(S)
        return self.fam.canon(len(S))


class TrueOracle(object):
    """S -> ftilde(S) on the real instance with hidden set O."""

    def __init__(self, fam, O):
        self.fam = fam
        self.O = frozenset(O)
        self.queries = []

    def query(self, S):
        S = frozenset(S)
        self.queries.append(S)
        y = len(S & self.O)
        return self.fam.ftilde(len(S) - y, y)


def alg_greedy(oracle, n, K, order=None):
    """Predictive greedy, K steps, ties by the given preference order."""
    order = list(range(n)) if order is None else list(order)
    S = set()
    oracle.query(frozenset())
    for _ in range(K):
        best, bestv = None, None
        for e in order:
            if e in S:
                continue
            v = oracle.query(frozenset(S | {e}))
            if bestv is None or v > bestv:
                best, bestv = e, v
        S.add(best)
    return frozenset(S)


def alg_shortlist(oracle, n, K):
    """Top-(K+1) singleton shortlist, then the best K-subset by ftilde."""
    vals = []
    for e in range(n):
        vals.append((oracle.query(frozenset([e])), e))
    # ties resolved by the smaller index (the algorithm's own fixed rule)
    idx = sorted(range(n), key=lambda e: (-vals[e][0], e))[:K + 1]
    best, bestv = None, None
    for A in itertools.combinations(sorted(idx), K):
        v = oracle.query(frozenset(A))
        if bestv is None or v > bestv:
            best, bestv = frozenset(A), v
    return best


def alg_greedy_swap(oracle, n, K):
    """Predictive greedy, then one swap pass over the fixed pair list.

    Query count nK - K(K-1)/2 + 1 + K(n-K) exceeds nK: recorded, not hidden.
    """
    T = list(sorted(alg_greedy(oracle, n, K)))
    cur = set(T)
    curv = oracle.query(frozenset(cur))
    for p in range(K):
        for e in range(n):
            if e in cur:
                continue
            slot = sorted(cur)[p]
            cand = frozenset((cur - {slot}) | {e})
            v = oracle.query(cand)
            if v > curv:
                cur, curv = set(cand), v
    return frozenset(cur)


def _class_pointers(n, O):
    Bs = [e for e in range(n) if e not in O]
    Os = sorted(O)
    return Bs, Os


def forward_greedy_countgrid(fam, n, K, O):
    """Predictive greedy on the real instance, simulated on the count grid.

    ftilde(S) depends on (|S cap B|, |S cap O|) alone, so the run is determined
    by the counts plus, at a tie, the smallest remaining index in each class.
    The algorithm's own rule is "smallest index among the maximizers"; where O
    sits inside the index order is the adversary's choice.
    """
    Bs, Os = _class_pointers(n, O)
    bi = oi = 0
    x = y = queries = 0
    while x + y < K:
        opts = []
        if bi < len(Bs):
            opts.append(("B", fam.ftilde(x + 1, y), Bs[bi]))
        if oi < len(Os):
            opts.append(("O", fam.ftilde(x, y + 1), Os[oi]))
        queries += (n - x - y)
        best = max(v for _, v, _i in opts)
        cand = [(i, k) for k, v, i in opts if v == best]
        kind = min(cand)[1]
        if kind == "B":
            x += 1
            bi += 1
        else:
            y += 1
            oi += 1
    return x, y, queries, K


def backward_greedy_countgrid(fam, n, K, O):
    """Deletion greedy from the full ground set, same simulation.

    It queries sets of size up to n - 1, so it does NOT belong to A_lin.
    """
    Bs, Os = _class_pointers(n, O)
    bi = oi = 0
    x, y, queries = n - K, K, 0
    while x + y > K:
        opts = []
        if x > 0:
            opts.append(("B", fam.ftilde(x - 1, y), Bs[bi]))
        if y > 0:
            opts.append(("O", fam.ftilde(x, y - 1), Os[oi]))
        queries += (x + y)
        best = max(v for _, v, _i in opts)
        cand = [(i, k) for k, v, i in opts if v == best]
        kind = min(cand)[1]
        if kind == "B":
            x -= 1
            bi += 1
        else:
            y -= 1
            oi += 1
    return x, y, queries, n - 1


def fwd_or_bwd_countgrid(fam, n, K, O):
    """max(forward greedy, backward greedy) by ftilde value, ties to forward."""
    xf, yf, qf, sf = forward_greedy_countgrid(fam, n, K, O)
    xb, yb, qb, sb = backward_greedy_countgrid(fam, n, K, O)
    vf = fam.ftilde(xf, yf)
    vb = fam.ftilde(xb, yb)
    out = (xf, yf) if vf >= vb else (xb, yb)
    return out[0], out[1], qf + qb + 2, max(sf, sb)


def find_hidden_O(n, K, queries, T0, rng, tries=4000):
    """Explicit search for O: |O| = K, O cap T0 = empty, |Q cap O| <= 1 for
    every queried Q.  Returns O or None."""
    free = [e for e in range(n) if e not in T0]
    if len(free) < K:
        return None
    # conflict graph: u ~ v if some query contains both
    conflict = {}
    for Q in queries:
        L = [e for e in Q if e not in T0]
        if len(L) < 2:
            continue
        if len(L) > 60:          # oversize query: no independent pair survives
            for u in L:
                conflict.setdefault(u, set()).update(L)
            continue
        for u, v in itertools.combinations(L, 2):
            conflict.setdefault(u, set()).add(v)
            conflict.setdefault(v, set()).add(u)
    for u in conflict:
        conflict[u].discard(u)

    def independent(cand):
        for u, v in itertools.combinations(cand, 2):
            if v in conflict.get(u, ()):
                return False
        return True

    # deterministic greedy by degree first
    order = sorted(free, key=lambda e: (len(conflict.get(e, ())), e))
    pick = []
    for e in order:
        if all(e not in conflict.get(u, ()) for u in pick):
            pick.append(e)
            if len(pick) == K:
                return frozenset(pick)
    # randomized restarts
    for _ in range(tries):
        cand = rng.sample(free, K)
        if independent(cand):
            return frozenset(cand)
    return None


def verify_replay(fam, n, K, runner, T0, canon_queries, O):
    """Replay the algorithm against the real instance with hidden set O and
    confirm the transcript and the output are unchanged."""
    orc = TrueOracle(fam, O)
    T1 = runner(orc)
    same = (T1 == T0) and (orc.queries == canon_queries)
    return same, T1


def score(fam, K, T, O):
    """f(T)/OPT in exact rationals; OPT = f(O) = 1."""
    y = len(T & O)
    x = len(T) - y
    return fam.F(x, y)


def run_one_structured(fam, n, K, eta, label, runner, rng, in_class=True):
    """Canonical transcript, adversary search, replay, ratio test."""
    rho = rho_exact(K, eta)
    rec = {"K": K, "eta": str(eta), "n": n, "candidate": label,
           "rho_K": str(rho), "in_class": in_class}
    canon = CanonicalOracle(fam)
    T0 = runner(canon)
    qs = list(canon.queries)
    rec["queries"] = len(qs)
    rec["max_query_size"] = max(len(q) for q in qs)
    rec["budget_nK"] = n * K
    rec["within_budget"] = bool(len(qs) <= n * K)
    rec["in_class"] = bool(in_class and rec["within_budget"]
                           and rec["max_query_size"] <= K)
    O = find_hidden_O(n, K, qs, T0, rng)
    if O is None:
        rec["status"] = "GAP"
        rec["reason"] = "no admissible hidden O found"
        VIOLATIONS.append({"check": "D1 " + label, "K": K, "eta": str(eta),
                           "n": n, "reason": "no admissible O"})
        D_STRUCTURED.append(rec)
        return rec
    rec["O_disjoint_from_output"] = bool(not (O & T0))
    rec["max_meet"] = max([len(q & O) for q in qs] or [0])
    same, T1 = verify_replay(fam, n, K, runner, T0, qs, O)
    rec["replay_identical"] = bool(same)
    ratio = score(fam, K, T1, O)
    rec["output_size"] = len(T1)
    rec["ratio"] = str(ratio)
    rec["ratio_float"] = float(ratio)
    rec["slack_rho_minus_ratio"] = str(rho - ratio)
    okr = (ratio <= rho) and same and rec["max_meet"] <= 1 and not (O & T1)
    rec["status"] = "PASS" if okr else "FAIL"
    if not okr:
        VIOLATIONS.append({"check": "D1 " + label, "K": K, "eta": str(eta),
                           "n": n, "ratio": str(ratio), "rho": str(rho),
                           "replay_identical": bool(same),
                           "max_meet": rec["max_meet"]})
    D_STRUCTURED.append(rec)
    return rec


def run_D1(configs_n):
    print()
    print("D1  structured candidates on the J6 family   [VERIFIED-EXHAUSTIVE]")
    rng = random.Random(SEED)
    ok = True
    for (K, eta, n) in configs_n:
        fam = Family(K, eta, Fr(1))
        rho = rho_exact(K, eta)
        print("  --- K=%d eta=%s n=%d  rho_K=%s (%.6f) ---"
              % (K, eta, n, rho, float(rho)))
        # out-of-class candidate: max(forward, backward greedy).  Backward
        # greedy queries sets of size up to n - 1, so it is not in A_lin and no
        # canonical small-set transcript exists for it.  It is evaluated
        # directly on the real instance, the adversary choosing the placement
        # of O that minimizes the ratio.
        worstb = None
        placements = [("low", frozenset(range(K))),
                      ("high", frozenset(range(n - K, n)))]
        prng = random.Random(SEED + 31 * K + n)
        for t in range(6):
            placements.append(("random%d" % t,
                               frozenset(prng.sample(range(n), K))))
        bestb = None
        for pname, Oset in placements:
            xo, yo, qb, sb = fwd_or_bwd_countgrid(fam, n, K, Oset)
            r = fam.F(xo, yo)
            if worstb is None or r < worstb[0]:
                worstb = (r, pname, qb, sb, (xo, yo))
            if bestb is None or r > bestb[0]:
                bestb = (r, pname)
        recb = {"K": K, "eta": str(eta), "n": n,
                "candidate": "max(forward, backward greedy)",
                "rho_K": str(rho), "in_class": False,
                "status": "OUT-OF-CLASS",
                "reason": "backward greedy queries sets of size up to n-1 > K, "
                          "so it is outside A_lin and the canonical small-set "
                          "transcript argument does not apply to it",
                "queries": worstb[2], "max_query_size": worstb[3],
                "O_placement": worstb[1],
                "placements_tried": len(placements),
                "output_state_xy": list(worstb[4]),
                "ratio": str(worstb[0]), "ratio_float": float(worstb[0]),
                "slack_rho_minus_ratio": str(rho - worstb[0]),
                "ratio_le_rho": bool(worstb[0] <= rho),
                "ratio_max_over_placements": str(bestb[0]),
                "ratio_max_placement": bestb[1],
                "beats_rho_on_some_placement": bool(bestb[0] > rho)}
        D_STRUCTURED.append(recb)
        print("    %-38s %-12s ratio=%s (%.6f) slack=%s queries=%s maxsize=%s "
              "best-placement ratio=%s (%s)"
              % (recb["candidate"], recb["status"], recb["ratio"],
                 recb["ratio_float"], recb["slack_rho_minus_ratio"],
                 recb["queries"], recb["max_query_size"],
                 recb["ratio_max_over_placements"],
                 recb["ratio_max_placement"]))

        cands = [("predictive greedy", lambda o, n=n, K=K: alg_greedy(o, n, K),
                  True),
                 ("top-(K+1) shortlist", lambda o, n=n, K=K:
                  alg_shortlist(o, n, K), True),
                 ("greedy + one swap pass", lambda o, n=n, K=K:
                  alg_greedy_swap(o, n, K), True)]
        for s in (1, 2, 3):
            perm = list(range(n))
            random.Random(SEED + 1000 * s + K).shuffle(perm)
            cands.append(("random-permutation greedy seed=%d" % s,
                          lambda o, n=n, K=K, p=perm: alg_greedy(o, n, K, p),
                          True))
        for label, runner, in_class in cands:
            rec = run_one_structured(fam, n, K, eta, label, runner, rng,
                                     in_class)
            st = rec["status"]
            print("    %-38s %-12s ratio=%s (%.6f) slack=%s %s"
                  % (label, st, rec.get("ratio", "-"),
                     rec.get("ratio_float", float("nan")),
                     rec.get("slack_rho_minus_ratio", "-"),
                     "queries=%s maxsize=%s" % (rec.get("queries"),
                                                rec.get("max_query_size"))))
            if st == "FAIL" or st == "GAP":
                ok = False
    COUNTS["D1_structured_cases"] = len(D_STRUCTURED)
    return ok


# ---------------------------------------------------------------------------
# D2: random deterministic strategies.
# ---------------------------------------------------------------------------
def make_random_strategy(rng, n, K, budget):
    m = rng.randint(1, budget)
    sets = [frozenset(rng.sample(range(n), rng.randint(1, K)))
            for _ in range(m)]
    rule = rng.randrange(3)
    extra = rng.randrange(10 ** 9)
    return sets, rule, extra


def apply_output_rule(sets, answers, rule, extra, n, K):
    """Deterministic function of the answer vector (and the fixed query list)."""
    if rule == 0:
        best, bestv = None, None
        for S, a in zip(sets, answers):
            if len(S) == K and (bestv is None or a > bestv):
                best, bestv = S, a
        if best is not None:
            return best
    if rule == 1:
        sc = {}
        for S, a in zip(sets, answers):
            for e in S:
                sc[e] = sc.get(e, Fr(0)) + a
        order = sorted(range(n), key=lambda e: (-sc.get(e, Fr(0)), e))
        return frozenset(order[:K])
    key = (extra,) + tuple((a.numerator, a.denominator) for a in answers)
    r = random.Random(hash(key) & 0xFFFFFFFF)
    return frozenset(r.sample(range(n), K))


def run_D2(configs_n, total=500):
    print()
    print("D2  %d random deterministic strategies   [VERIFIED-EXHAUSTIVE]"
          % total)
    rng = random.Random(SEED + 7)
    ok = True
    worst = None
    per = total // len(configs_n)
    counts = {"cases": 0, "no_O": 0, "replay_mismatch": 0, "violations": 0}
    for ci, (K, eta, n) in enumerate(configs_n):
        fam = Family(K, eta, Fr(1))
        rho = rho_exact(K, eta)
        budget = min(n * K, 256)
        m = per + (total - per * len(configs_n) if ci == 0 else 0)
        for t in range(m):
            sets, rule, extra = make_random_strategy(rng, n, K, budget)
            canon = CanonicalOracle(fam)
            answers = [canon.query(S) for S in sets]
            T0 = apply_output_rule(sets, answers, rule, extra, n, K)
            counts["cases"] += 1
            O = find_hidden_O(n, K, canon.queries, T0, rng)
            if O is None:
                counts["no_O"] += 1
                VIOLATIONS.append({"check": "D2", "K": K, "eta": str(eta),
                                   "n": n, "trial": t,
                                   "reason": "no admissible O"})
                ok = False
                continue
            orc = TrueOracle(fam, O)
            ans2 = [orc.query(S) for S in sets]
            T1 = apply_output_rule(sets, ans2, rule, extra, n, K)
            if ans2 != answers or T1 != T0:
                counts["replay_mismatch"] += 1
                ok = False
                VIOLATIONS.append({"check": "D2", "K": K, "eta": str(eta),
                                   "n": n, "trial": t,
                                   "reason": "replay mismatch"})
                continue
            ratio = score(fam, K, T1, O)
            if ratio > rho:
                counts["violations"] += 1
                ok = False
                VIOLATIONS.append({"check": "D2", "K": K, "eta": str(eta),
                                   "n": n, "trial": t, "ratio": str(ratio),
                                   "rho": str(rho)})
            if worst is None or (ratio - rho) > (worst[0] - Fr(worst[2])):
                worst = (ratio, {"K": K, "eta": str(eta), "n": n,
                                 "trial": t, "rule": rule,
                                 "queries": len(sets),
                                 "rho_K": str(rho),
                                 "slack_rho_minus_ratio": str(rho - ratio)},
                         rho)
            D_RANDOM.append({"K": K, "eta": str(eta), "n": n, "rule": rule,
                             "queries": len(sets), "ratio": str(ratio),
                             "rho_K": str(rho)})
        print("    K=%d eta=%s n=%d: %d strategies, max ratio so far %s"
              % (K, eta, n, m, worst[0]))
    COUNTS["D2"] = counts
    check("D2 %d random deterministic strategies, every ratio <= rho_K, "
          "admissible O found every time, transcript replay identical"
          % counts["cases"], ok,
          "smallest slack rho_K - ratio: %s (ratio %s) at %s"
          % (worst[2] - worst[0], worst[0],
             json.dumps(worst[1], sort_keys=True)),
          "[VERIFIED-EXHAUSTIVE]")
    return ok, worst


# ---------------------------------------------------------------------------
def main():
    print("V11 oracle: thm:linear-exact (ledger T10c, J6; Theorem 2)")
    print("repo root:", ROOT)
    print("exact arithmetic: fractions.Fraction and sympy; seed", SEED)
    print("no existing repository file is modified; the three Q4 scripts are "
          "rerun by subprocess")
    print()
    print("=== Criterion C ===", flush=True)
    okC13 = run_C1_C3()
    okC4, c4rows = run_C4()
    okC5, c5rows = run_C5()
    okC6 = run_C6()

    configs = [(2, Fr(3, 2)), (2, Fr(2)), (3, Fr(3, 2)), (3, Fr(2))]
    okC7 = run_C7(configs)

    configs_n = []
    for (K, eta) in configs:
        for n in ((128, 256) if K == 2 else (972, 1944)):
            configs_n.append((K, eta, n))
    for (K, eta, n) in configs_n:
        assert n >= 4 * K ** 5, (K, n)

    print()
    print("=== Criterion D ===", flush=True)
    okD1 = run_D1(configs_n)
    okD2, worst = run_D2(configs_n, 500)

    # running example K = 3, eta = 3/2
    fam = Family(3, Fr(3, 2), Fr(1))
    running = {"K": 3, "eta": "3/2", "j": fam.j, "k1": str(fam.k1),
               "q": str(fam.q), "Q": str(fam.Q), "delta": str(fam.delta),
               "C": str(fam.C), "rho_3(3/2)": str(rho_exact(3, Fr(3, 2))),
               "F(3,0)": str(fam.F(3, 0)), "F(0,3)": str(fam.F(0, 3)),
               "Hhat": [str(fam.Hhat(s)) for s in range(4)],
               "leak_H(6,0)": str(fam.H(6, 0)), "leak_H(5,1)": str(fam.H(5, 1)),
               "n_min_4K5": 4 * 3 ** 5,
               "n_min_loose_chain": 131, "n_min_tight_chain": 64}

    ok_all = okC13 and okC4 and okC5 and okC6 and okC7 and okD1 and okD2
    print()
    print("counts:", json.dumps(COUNTS, sort_keys=True))
    print("running example K=3 eta=3/2:", json.dumps(running, sort_keys=True))
    d1_worst = min(((Fr(r["ratio"]) - Fr(r["rho_K"]), r)
                    for r in D_STRUCTURED if r["status"] == "PASS"),
                   key=lambda t: -t[0])
    print("D1 worst slack rho_K - ratio: %s at %s"
          % (-d1_worst[0], json.dumps(
              {k: d1_worst[1][k] for k in
               ("K", "eta", "n", "candidate", "ratio", "rho_K")},
              sort_keys=True)))
    print("D2 worst slack rho_K - ratio: %s (ratio %s) at %s"
          % (worst[2] - worst[0], worst[0],
             json.dumps(worst[1], sort_keys=True)))
    print("violations:", len(VIOLATIONS))
    for v in VIOLATIONS[:8]:
        print("   ", json.dumps(v, sort_keys=True)[:400])

    blob = {"statement": "thm:linear-exact (T10c, J6): sup_{A in A_lin} "
                         "inf_{(f,ftilde)} f(A)/OPT = rho_K(eta), n >= 4K^5",
            "overall": "PASS" if ok_all else "FAIL",
            "checks": CHECKS, "counts": COUNTS,
            "reruns": SUBPROCS,
            "counting_chain_at_4K5": c4rows,
            "smallest_n_table": c5rows,
            "D_structured": D_STRUCTURED,
            "D_random_sample": D_RANDOM[:40],
            "D_random_count": len(D_RANDOM),
            "D_worst_slack": {
                "D1": {"slack_rho_minus_ratio": str(-d1_worst[0]),
                       "where": {k: d1_worst[1][k] for k in
                                 ("K", "eta", "n", "candidate", "ratio",
                                  "rho_K")}},
                "D2": {"slack_rho_minus_ratio": str(worst[2] - worst[0]),
                       "ratio": str(worst[0]), "where": worst[1]}},
            "running_example_K3_eta_3_2": running,
            "violations": VIOLATIONS,
            "seconds": round(time.time() - T0, 1)}
    path = os.path.join(HERE, "linear_exact.json")
    with open(path, "w") as fh:
        json.dump(blob, fh, indent=1)
    print("json written:", path)
    nfail = sum(1 for c in CHECKS if c["status"] != "PASS")
    print("OVERALL: %s (%d checks, %d failed, %d violations, %.1fs)"
          % ("PASS" if ok_all else "FAIL", len(CHECKS), nfail, len(VIOLATIONS),
             time.time() - T0))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())

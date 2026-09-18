#!/usr/bin/env python3
"""V11 oracle for thm:linear-anysize (ledger T10d, J7; Proposition of the paper).

Statement under test (results/V11/inputs/statement_linear_anysize.md):

    Let K >= 3 and eta > 1, and let alpha_lin(K, eta) be the limit as
    n -> infinity of the optimal worst-case ratio of deterministic algorithms
    that make O(nK) queries to ftilde OF ARBITRARY SIZE and output a set of
    size at most K, over instances with monotone submodular f and error
    product at most eta (randomized algorithms in expectation).  Then

        rho_K(eta) <= alpha_lin(K, eta) <= min{1/eta, W_K(eta)}
                   <= min{1/eta, rho_K(eta) + 1/(K(e^{K-1} - K - 1))},

    W_K(eta) the explicit constant of app:hardness-anysize.  For eta >= K both
    ends equal 1/eta.

Route-one proof material (read, never used as an oracle):
    paper/sections/appendix_proofs.tex, subsection app:hardness-anysize
    (~line 1987), results/J7/linear_anysize.md, ledger THEOREM_LEDGER.md
    section T10d.  Existing scripts rerun here by subprocess, never modified:
    results/J7_symbolic.py, results/J7_grid_check.py,
    results/J7_fragment_checks.py, results/J7_bound18_check.py.

Criterion C (oracle)
    C1  rerun results/J7_symbolic.py        (148 items, 0 FAILED expected)
    C2  rerun results/J7_grid_check.py      (99 configs + adversarial sim)
    C3  rerun results/J7_fragment_checks.py (F3 counterexample, parts 1-3)
    C4  rerun results/J7_bound18_check.py   (99 configs, e by a rational bound)
        exit code and key counts recorded for each.  J7_symbolic.py rewrites
        its own results/J7_symbolic.json; its sha256 is taken before and after
        and the file is restored byte-for-byte if the rerun changed it, so no
        existing repository file is modified by this script.
    C5  own exact-rational reproduction of the F3 counterexample at K = 3,
        eta = 667/500: the old rule m = ceil(K eta) - 1 = 4 gives
        r_{t*} = -151089222203006/81950355825200625 < 0, the Psi rule gives
        m = 3 with r_{t*} >= 0.                          [VERIFIED-EXHAUSTIVE]
    C6  own exact-rational running example K = 3, eta = 3/2: m = 4, B_m = 116,
        d = 13/58, D = 117/928, Q = 9/16, t* = 6,
        W_3(3/2) = 523/928 = 9/16 + 1/928, rho_3(3/2) = 9/16, gap = 1/928.
                                                          [VERIFIED-EXHAUSTIVE]
    C7  own count-grid legality battery on the three D configurations
        (K = 3, eta in {3/2, 2, 667/500}), re-implemented from the formulas of
        results/J7/linear_anysize.md (2)-(10), not imported: normalisation,
        0 <= F <= 1, monotone and submodular, the band dF <= dH <= eta dF with
        both endpoints attained at x = 0, the any-size profile
        H(x+1,0) = H(x,1) for every x, saturation past t*, the leak
        characterisation (J7 (15)), F(K,0) = W_K and the gap identity (17).
                                                          [VERIFIED-EXHAUSTIVE]
    C8  own exact sweep of the analytic facts on the same 99-configuration grid
        as results/J7_bound18_check.py (K = 3..12, ten eta each), independent
        re-implementation: the bracket eta(K-1) < m < K eta (5), the two
        d-identities and 1/(m+1) <= d <= 1/m (7), d - 1/(K eta) > 0 (8), the
        gap identity (17), and 0 < W_K - rho_K < 1/(K(e^{K-1}-K-1)) (18) with
        e replaced by an exact rational UPPER bound (so the right side is a
        rational LOWER bound and the decision stays exact).
                                                          [VERIFIED-EXHAUSTIVE]

Criterion D (counterexample search on the statement itself)
    The J7 instance, own re-implementation from the formulas of
    results/J7/linear_anysize.md (results/J7_grid_check.py is NOT imported).
    K = 3, eta in {3/2, 2, 667/500}, n = 8..14.  Ground set of size n, hidden
    K-set O, f(S) = F(|S \ O|, |S cap O|), predictor H = eta_u ftilde.
    Ratio = f(T)/f(O) = F(|T \ O|, |T cap O|) since f(O) = 1.

    D1  adversarial (worst-tie) forward predictive greedy, reverse (deletion)
        greedy and max(forward, reverse), evaluated by exact count-grid dynamic
        programming; ties are broken by the adversary to minimise the final
        value.  By symmetry of the family under permutations fixing O these
        values do not depend on where O sits, so they are the worst case over
        placements as well.
    D2  300 random deterministic strategies (fixed seed): a random sequence of
        at most nK query sets of ARBITRARY size plus a fixed output rule that
        reads only the answer vector.  For each strategy the adversary is given
        its true power: every one of the C(n,K) placements of O is tried, the
        strategy is replayed against that instance, and the MINIMUM ratio is
        taken.

    Required invariants (from J7 (15)-(16) and the ledger T10d card):
        n >= K + t*  ->  every ratio <= W_K(eta);
        n <  K + t*  ->  reverse greedy recovers O exactly, ratio = 1, which is
                         the must-not-claim recorded on the T10d card (a
                         finite-n "<= W_K" reading is false; the n -> infinity
                         quantifier of the statement cannot be dropped).
    t* = j + m, so K + t* = 9, 10, 8 at eta = 3/2, 2, 667/500.

Exactness: every decision uses fractions.Fraction or sympy.  Floats appear only
inside printed parentheses.  Seed 20260918 and values derived from it.

Outputs (new files only): linear_anysize.log, linear_anysize.json,
linear_anysize.md in this directory.  No existing repository file is modified.

Run:  python3 results/V11/oracle/linear_anysize.py   (exit 0 iff every check passed)
"""
import hashlib
import itertools
import json
import math
import os
import random
import shutil
import subprocess
import sys
import time
from fractions import Fraction as Fr
from functools import lru_cache

import sympy as sp

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SEED = 20260918

CHECKS = []
COUNTS = {}
VIOLATIONS = []
SUBPROCS = []
D_STRUCTURED = []
D_RANDOM = []

# e < E_UP, exact rational upper bound (e = 2.718281828459045...)
E_UP = Fr(2718281829, 10 ** 9)


def check(name, ok, detail="", tag=""):
    CHECKS.append({"name": name, "status": "PASS" if ok else "FAIL",
                   "detail": detail, "tag": tag})
    print(("PASS" if ok else "FAIL"), name, (detail and ("  " + detail)) or "",
          flush=True)
    return bool(ok)


def note(name, status, detail="", tag=""):
    CHECKS.append({"name": name, "status": status, "detail": detail,
                   "tag": tag})
    print(status, name, (detail and ("  " + detail)) or "", flush=True)


# ---------------------------------------------------------------------------
# The J7 any-size family, own transcription of results/J7/linear_anysize.md
# formulas (4), (6), (9), (10).  Nothing is imported from results/.
# ---------------------------------------------------------------------------
class Family(object):
    """f and eta_u * ftilde of app:hardness-anysize on the count grid (x, y).

    x = |S \\ O|, y = |S cap O|, |O| = K.
    """

    def __init__(self, K, eta):
        self.K = K = int(K)
        self.eta = eta = Fr(eta)
        self.k1 = k1 = (K - 1) * eta + 1                     # k_1
        self.q = q = (K - 1) * eta / k1                      # q = 1 - 1/k_1
        self.nu = nu = eta / (eta - 1)                       # nu
        self.j = j = max(0, min(K - 1, K + 1 - math.ceil(eta)))
        self.Q = Q = q ** j
        # (4)  m = min{z >= 1 : Psi(z) <= 0},  Psi(t) = (K eta - t - 1) nu^t
        #                                              - K(eta - 1)
        m = None
        zmax = 10 * K * (int(eta) + 2) + 40
        for z in range(1, zmax):
            if self.Psi(z) <= 0:
                m = z
                break
        if m is None:
            raise RuntimeError("Psi rule did not terminate")
        self.m = m
        self.Bm = Bm = eta * (nu ** m - 1) - m               # (6)
        self.d = d = (nu ** m / K - 1) / Bm                  # (6)
        self.D = D = Q * d
        self.T = j + m                                       # t*
        self.C = k1 / K
        self.W = 1 - Q + (K - j) * Q * d                     # W_K(eta)
        self._Dv = D

    def Psi(self, t):
        return ((self.K * self.eta - t - 1) * self.nu ** t
                - self.K * (self.eta - 1))

    def r(self, x):
        if x <= self.j:
            return self.q ** x
        if x <= self.T:
            return self.Q - (x - self.j) * self.D
        return Fr(0)

    def g(self, x):
        if x <= self.j:
            return self.q ** x / self.K
        if x <= self.T:
            return (self.eta * self.D
                    - (self.eta * self.D - self.Q / self.K)
                    * self.nu ** (x - self.j))
        return Fr(0)

    def a(self, x):
        return self.r(x) - self.g(x)

    def F(self, x, y):
        if y == 0:
            return 1 - self.r(x)
        return 1 - Fr(self.K - y, self.K - 1) * self.a(x)

    def H(self, x, y):
        if y == 0:
            return self.C - self.r(x) - (self.eta - 1) * self.a(x)
        return self.C - self.eta * Fr(self.K - y, self.K - 1) * self.a(x)


def rho_exact(K, eta):
    """rho_K(eta), predictive greedy's exact worst-case ratio."""
    eta = Fr(eta)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return min(1 - q ** t * (1 - Fr(K - t, K) / eta) for t in range(K))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(65536), b""):
            h.update(blk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# C1 - C4: reruns of the existing repository scripts.
# ---------------------------------------------------------------------------
def rerun(cid, relpath, grep_keys, expect_exit=0, guard=None, timeout=3600):
    """Run an existing repository script by subprocess and record its exit code
    and the lines matching grep_keys.  guard: a repo file the script rewrites;
    its sha256 is compared before/after and it is restored if it changed."""
    path = os.path.join(ROOT, relpath)
    gpath = os.path.join(ROOT, guard) if guard else None
    before = sha256(gpath) if gpath and os.path.exists(gpath) else None
    bak = None
    if before is not None:
        bak = os.path.join(HERE, "_guard_" + os.path.basename(gpath) + ".bak")
        shutil.copyfile(gpath, bak)
    t = time.time()
    p = subprocess.run([sys.executable, path], cwd=ROOT, capture_output=True,
                       text=True, timeout=timeout)
    secs = round(time.time() - t, 1)
    out = (p.stdout or "") + (p.stderr or "")
    lines = out.splitlines()
    picked = [ln.strip() for ln in lines
              if any(k in ln for k in grep_keys)]
    restored = False
    after = None
    if before is not None:
        after = sha256(gpath)
        if after != before:
            shutil.copyfile(bak, gpath)
            restored = True
        os.remove(bak)
    # a real failure line starts with "FAIL" and is not the summary line
    # "FAILED items: none" that results/J7_symbolic.py always prints
    nfail = sum(1 for ln in lines
                if ln.strip().startswith("FAIL")
                and not ln.strip().startswith("FAILED items: none")
                and not ln.strip().startswith("FAILURES: 0"))
    rec = {"id": cid, "script": relpath, "exit_code": p.returncode,
           "seconds": secs, "stdout_lines": len(lines),
           "fail_lines": nfail, "key_lines": picked[-12:]}
    if before is not None:
        rec["guard_file"] = guard
        rec["guard_sha256_before"] = before
        rec["guard_sha256_after"] = after
        rec["guard_unchanged"] = bool(after == before)
        rec["guard_restored"] = restored
    SUBPROCS.append(rec)
    ok = check("%s rerun %s: exit %d (expected %d), %d FAIL lines, %.1fs"
               % (cid, relpath, p.returncode, expect_exit, nfail, secs),
               p.returncode == expect_exit and nfail == 0,
               " | ".join(picked[-4:]), "[VERIFIED-SYMBOLIC/EXACT, rerun]")
    for ln in picked[-6:]:
        print("      >", ln)
    if before is not None:
        check("%s %s byte-identical after the rerun (restored=%s)"
              % (cid, guard, restored), after == before or restored,
              "sha256 %s -> %s" % (before[:16], (after or "")[:16]),
              "[no repository file modified]")
    return ok


def run_C1_C4():
    ok = True
    ok &= rerun("C1", "results/J7_symbolic.py",
                ["PASS ", "EXACT ", "ASSEMBLY ", "FAILED items:"],
                guard="results/J7_symbolic.json")
    ok &= rerun("C2", "results/J7_grid_check.py", ["configs:", "ALL PASS",
                                                   "FAILURES"])
    ok &= rerun("C3", "results/J7_fragment_checks.py", ["ALL PASS",
                                                        "FAILURES"])
    ok &= rerun("C4", "results/J7_bound18_check.py", ["configs:", "ALL PASS",
                                                      "FAILURES"])
    return bool(ok)


# ---------------------------------------------------------------------------
# C5: the F3 counterexample, own exact reproduction.
# ---------------------------------------------------------------------------
def run_C5():
    print()
    print("C5  F3 counterexample at K = 3, eta = 667/500   "
          "[VERIFIED-EXHAUSTIVE]")
    K, eta = 3, Fr(667, 500)
    fam = Family(K, eta)
    nu, k1 = fam.nu, fam.k1
    q = fam.q
    j = fam.j
    Q = q ** j

    def slope(m):
        """Plateau slope D(m)/Q of the night-4 family at truncation m."""
        den = eta * (nu ** m - 1) - m
        return (nu ** m / K - 1) / den

    m_old = math.ceil(K * eta) - 1
    ok = True
    ok &= check("C5.1 j = 2", j == 2, "j=%d" % j)
    ok &= check("C5.2 old rule m = ceil(K eta) - 1 = 4", m_old == 4,
                "K eta = %s, ceil = %d" % (K * eta, math.ceil(K * eta)))
    ok &= check("C5.3 Psi rule gives m = 3", fam.m == 3,
                "Psi(2)=%s>0, Psi(3)=%s<=0"
                % (fam.Psi(2), fam.Psi(3)))
    ok &= check("C5.4 Psi(2) > 0 and Psi(3) <= 0 exactly",
                fam.Psi(2) > 0 and fam.Psi(3) <= 0,
                "Psi(2)=%s Psi(3)=%s" % (fam.Psi(2), fam.Psi(3)))
    # night-4 family at the old truncation: r_{t*} = Q - m_old * D(m_old)
    TARGET = Fr(-151089222203006, 81950355825200625)
    r_old = Q - m_old * Q * slope(m_old)
    ok &= check("C5.5 old rule gives r_{t*} = -151089222203006/"
                "81950355825200625 < 0", r_old == TARGET and r_old < 0,
                "r_{t*} = %s (%.10e)" % (r_old, float(r_old)))
    # the same number via the excess-slope reading max{Q/(K eta), D(m)}
    r_old_b = Q - m_old * max(Q / (K * eta), Q * slope(m_old))
    ok &= check("C5.6 the excess-slope reading gives the same r_{t*}",
                r_old_b == TARGET, "identical exact fraction")
    r_new = Q - fam.m * fam.D
    ok &= check("C5.7 Psi rule family closes legally: r_{t*} = %s >= 0"
                % r_new, r_new >= 0, "r_{t*} = %.10f, g_{t*} = %.10f"
                % (float(fam.r(fam.T)), float(fam.g(fam.T))))
    ok &= check("C5.8 Psi rule closing identity r_{t*} = g_{t*}",
                fam.r(fam.T) == fam.g(fam.T),
                "both = %s" % fam.r(fam.T))
    ok &= check("C5.9 the true argmax of the plateau slope is m = 3",
                max(range(1, 40), key=lambda z: (slope(z), -z)) == 3,
                "D(3)=%.12f D(4)=%.12f"
                % (float(slope(3)), float(slope(4))))
    detail = {"K": 3, "eta": "667/500", "j": j, "m_old_rule": m_old,
              "m_Psi_rule": fam.m, "r_tstar_old_rule": str(r_old),
              "r_tstar_Psi_rule": str(r_new),
              "Psi(2)": str(fam.Psi(2)), "Psi(3)": str(fam.Psi(3)),
              "t_star": fam.T, "W": str(fam.W)}
    COUNTS["C5_F3_counterexample"] = detail
    print("    ", json.dumps(detail, sort_keys=True))
    return ok, detail


# ---------------------------------------------------------------------------
# C6: the running example K = 3, eta = 3/2.
# ---------------------------------------------------------------------------
def run_C6():
    print()
    print("C6  running example K = 3, eta = 3/2   [VERIFIED-EXHAUSTIVE]")
    fam = Family(3, Fr(3, 2))
    rho = rho_exact(3, Fr(3, 2))
    ok = True
    ok &= check("C6.1 j = 2, m = 4, t* = 6",
                (fam.j, fam.m, fam.T) == (2, 4, 6),
                "j=%d m=%d t*=%d" % (fam.j, fam.m, fam.T))
    ok &= check("C6.2 B_m = 116, d = 13/58, Q = 9/16, D = 117/928",
                fam.Bm == 116 and fam.d == Fr(13, 58)
                and fam.Q == Fr(9, 16) and fam.D == Fr(117, 928),
                "B_m=%s d=%s Q=%s D=%s"
                % (fam.Bm, fam.d, fam.Q, fam.D))
    ok &= check("C6.3 W_3(3/2) = 523/928 = 9/16 + 1/928",
                fam.W == Fr(523, 928) and fam.W == Fr(9, 16) + Fr(1, 928),
                "W = %s (%.9f)" % (fam.W, float(fam.W)))
    ok &= check("C6.4 rho_3(3/2) = 9/16 and W - rho = 1/928",
                rho == Fr(9, 16) and fam.W - rho == Fr(1, 928),
                "rho = %s (%.9f), gap = %s (%.3e)"
                % (rho, float(rho), fam.W - rho, float(fam.W - rho)))
    ok &= check("C6.5 W_3(3/2) = F(K,0) on the count grid",
                fam.F(3, 0) == fam.W, "F(3,0) = %s" % fam.F(3, 0))
    ok &= check("C6.6 W_3(3/2) < 2/3 = 1/eta (unconditional ceiling)",
                fam.W < Fr(2, 3), "523/928 < 2/3")
    run = {"K": 3, "eta": "3/2", "j": fam.j, "m": fam.m, "t_star": fam.T,
           "q": str(fam.q), "nu": str(fam.nu), "Q": str(fam.Q),
           "B_m": str(fam.Bm), "d": str(fam.d), "D": str(fam.D),
           "C": str(fam.C), "rho_3": str(rho), "W_3": str(fam.W),
           "gap": str(fam.W - rho), "one_over_eta": "2/3",
           "K_plus_t_star": 3 + fam.T}
    COUNTS["C6_running_example"] = run
    print("    ", json.dumps(run, sort_keys=True))
    return ok, run


# ---------------------------------------------------------------------------
# C7: own count-grid legality battery on the D configurations.
# ---------------------------------------------------------------------------
def run_C7(configs):
    print()
    print("C7  own count-grid legality battery   [VERIFIED-EXHAUSTIVE]")
    ok = True
    rows = []
    for (K, eta) in configs:
        fam = Family(K, eta)
        F, H, eta_f = fam.F, fam.H, fam.eta
        xmax = fam.T + K + 2
        tag = "K=%d eta=%s" % (K, eta)
        bad = []
        # normalisation and range
        if not (F(0, 0) == 0 and F(0, K) == 1 and H(0, 0) == 0):
            bad.append("normalisation")
        cells = 0
        for x in range(xmax + 1):
            for y in range(K + 1):
                cells += 1
                if not (0 <= F(x, y) <= 1):
                    bad.append("range %s" % ((x, y),))
        # monotone, band, submodular
        edges = 0
        second = 0
        for x in range(xmax + 1):
            for y in range(K + 1):
                for dx, dy in ((1, 0), (0, 1)):
                    xx, yy = x + dx, y + dy
                    if xx > xmax or yy > K:
                        continue
                    edges += 1
                    dF = F(xx, yy) - F(x, y)
                    dH = H(xx, yy) - H(x, y)
                    if not (0 <= dF <= dH <= eta_f * dF):
                        bad.append("band %s" % ((x, y, dx, dy),))
                    for sx, sy in ((1, 0), (0, 1)):
                        if xx + sx > xmax or yy + sy > K:
                            continue
                        second += 1
                        dF2 = F(xx + sx, yy + sy) - F(x + sx, y + sy)
                        if not (dF2 <= dF):
                            bad.append("submod %s" % ((x, y, dx, dy, sx, sy),))
        # calibration endpoints at x = 0
        dF1, dH1 = F(0, 1) - F(0, 0), H(0, 1) - H(0, 0)
        dF2, dH2 = F(0, 2) - F(0, 1), H(0, 2) - H(0, 1)
        if not (dF1 > 0 and dH1 == dF1):
            bad.append("lower endpoint")
        if not (dF2 > 0 and dH2 == eta_f * dF2):
            bad.append("upper endpoint")
        # any-size profile and saturation
        for x in range(xmax):
            if H(x + 1, 0) != H(x, 1):
                bad.append("profile x=%d" % x)
        for x in range(fam.T + 1, xmax + 1):
            for y in range(K + 1):
                if not (F(x, y) == 1 and H(x, y) == fam.C):
                    bad.append("saturation %s" % ((x, y),))
        # leak characterisation, J7 (15)
        leaks = 0
        for x in range(xmax + 1):
            for y in range(K + 1):
                if H(x, y) != H(x + y, 0):
                    leaks += 1
                    if not (y >= 2 and x <= fam.T):
                        bad.append("leak outside y>=2,x<=t* %s" % ((x, y),))
        # value and gap identity
        rho = rho_exact(K, eta)
        gap = ((K - fam.j) * fam.Q * (fam.m - eta * (K - 1))
               / (K * eta * fam.Bm))
        if F(K, 0) != fam.W:
            bad.append("F(K,0) != W")
        if fam.W - rho != gap:
            bad.append("gap identity (17)")
        if not (fam.W - rho > 0):
            bad.append("gap > 0")
        row = {"K": K, "eta": str(eta), "j": fam.j, "m": fam.m,
               "t_star": fam.T, "cells": cells, "edges": edges,
               "second_differences": second, "leak_cells": leaks,
               "W": str(fam.W), "rho_K": str(rho), "gap": str(gap),
               "violations": len(bad)}
        rows.append(row)
        ok &= check("C7 %s: %d cells, %d edges, %d second differences, "
                    "%d leak cells, all legality checks" % (tag, cells, edges,
                                                            second, leaks),
                    not bad, "" if not bad else "; ".join(bad[:5]),
                    "[VERIFIED-EXHAUSTIVE]")
    COUNTS["C7_configs"] = rows
    return ok, rows


# ---------------------------------------------------------------------------
# C8: own exact sweep of the analytic facts on the 99-configuration grid.
# ---------------------------------------------------------------------------
def run_C8():
    print()
    print("C8  own exact sweep of (5), (7), (8), (17), (18) on 99 configs   "
          "[VERIFIED-EXHAUSTIVE]")
    ok = True
    n = 0
    worst_gap_ratio = None
    fails = []
    for K in range(3, 13):
        rhs_lower = 1 / (K * (E_UP ** (K - 1) - K - 1))
        etas = {Fr(21, 20), Fr(5, 4), Fr(3, 2), Fr(2), Fr(5, 2), Fr(3),
                Fr(667, 500), Fr(3 * K - 1, 3), Fr(K), Fr(2 * K + 1, 2)}
        for eta in sorted(e for e in etas if e > 1):
            fam = Family(K, eta)
            n += 1
            m, Bm, d = fam.m, fam.Bm, fam.d
            nu, Q, j = fam.nu, fam.Q, fam.j
            rho = rho_exact(K, eta)
            gap = (K - j) * Q * (m - eta * (K - 1)) / (K * eta * Bm)
            tests = [
                ("(5) eta(K-1) < m", eta * (K - 1) < m),
                ("(5) m < K eta", m < K * eta),
                ("(6) B_m > 0", Bm > 0),
                ("(7a) d - 1/(m+1) = -Psi(m)/(K(m+1)B_m)",
                 d - Fr(1, m + 1) == -fam.Psi(m) / (K * (m + 1) * Bm)),
                ("(7b) 1/m - d = nu Psi(m-1)/(K m B_m)",
                 Fr(1, m) - d == nu * fam.Psi(m - 1) / (K * m * Bm)),
                ("(7) 1/(m+1) <= d <= 1/m",
                 Fr(1, m + 1) <= d <= Fr(1, m)),
                ("(8) d - 1/(K eta) = (m - eta(K-1))/(K eta B_m) > 0",
                 d - 1 / (K * eta) == (m - eta * (K - 1)) / (K * eta * Bm)
                 and d - 1 / (K * eta) > 0),
                ("(17) W - rho = (K-j)Q(m-eta(K-1))/(K eta B_m)",
                 fam.W - rho == gap),
                ("(18) 0 < W - rho < 1/(K(e^{K-1}-K-1))",
                 0 < gap < rhs_lower),
                ("closing r_{t*} = g_{t*} >= 0",
                 fam.r(fam.T) == fam.g(fam.T) and fam.r(fam.T) >= 0),
                ("nu^m > e^{K-1} (rational e upper bound)",
                 nu ** m > E_UP ** (K - 1)),
            ]
            for label, cond in tests:
                if not cond:
                    fails.append("K=%d eta=%s %s" % (K, eta, label))
            ratio = gap / rhs_lower
            if worst_gap_ratio is None or ratio > worst_gap_ratio[0]:
                worst_gap_ratio = (ratio, {"K": K, "eta": str(eta),
                                           "gap": str(gap),
                                           "bound_lower": str(rhs_lower),
                                           "gap_over_bound": float(ratio)})
    ok &= check("C8 %d configurations, 11 exact facts each (%d assertions), "
                "no violation" % (n, 11 * n), not fails,
                "" if not fails else "; ".join(fails[:5]),
                "[VERIFIED-EXHAUSTIVE]")
    COUNTS["C8_configs"] = n
    COUNTS["C8_assertions"] = 11 * n
    COUNTS["C8_worst_gap_over_bound"] = worst_gap_ratio[1]
    print("    worst (W - rho)/bound over the sweep:",
          json.dumps(worst_gap_ratio[1], sort_keys=True))
    return ok, worst_gap_ratio[1]


# ---------------------------------------------------------------------------
# C9: sympy cross-check of the two d-identities as general identities.
# ---------------------------------------------------------------------------
def run_C9():
    print()
    print("C9  sympy cross-check of the d-identities   [VERIFIED-SYMBOLIC]")
    K, m = sp.symbols("K m", positive=True)
    u = sp.symbols("u", positive=True)                   # eta = 1 + u, u > 0
    eta = 1 + u
    nu = eta / (eta - 1)                                 # nu = eta/(eta-1)
    Nm = sp.symbols("Nm", positive=True)                 # stands for nu**m
    Psi_m = (K * eta - m - 1) * Nm - K * (eta - 1)
    Psi_m1 = (K * eta - m) * Nm / nu - K * (eta - 1)     # Psi(m-1)
    Bm = eta * (Nm - 1) - m
    d = (Nm / K - 1) / Bm
    e1 = sp.simplify(d - 1 / (m + 1) - (-Psi_m) / (K * (m + 1) * Bm))
    e2 = sp.simplify(1 / m - d - nu * Psi_m1 / (K * m * Bm))
    e3 = sp.simplify(d - 1 / (K * eta) - (m - eta * (K - 1)) / (K * eta * Bm))
    ok = True
    ok &= check("C9.1 (7a) d - 1/(m+1) = -Psi(m)/(K(m+1)B_m) identically",
                e1 == 0, "sympy simplify -> %s" % e1, "[VERIFIED-SYMBOLIC]")
    ok &= check("C9.2 (7b) 1/m - d = nu Psi(m-1)/(K m B_m) identically",
                e2 == 0, "sympy simplify -> %s" % e2, "[VERIFIED-SYMBOLIC]")
    ok &= check("C9.3 (8) d - 1/(K eta) = (m - eta(K-1))/(K eta B_m) "
                "identically", e3 == 0, "sympy simplify -> %s" % e3,
                "[VERIFIED-SYMBOLIC]")
    return ok


# ---------------------------------------------------------------------------
# D1: structured strategies by exact count-grid dynamic programming.
# ---------------------------------------------------------------------------
def structured_values(fam, n):
    """Adversarial (worst-tie) forward greedy and reverse (deletion) greedy.

    Returns (forward value, reverse value, forward queries, reverse queries).
    Forward greedy: from the empty set, add the element of largest predicted
    marginal, adversary breaks ties; K steps, each step scanning the n - |S|
    candidates.  Reverse greedy: from the whole ground set, delete the element
    of smallest predicted loss, adversary breaks ties, down to size K.
    """
    K = fam.K
    X = n - K
    H, F = fam.H, fam.F

    @lru_cache(maxsize=None)
    def fwd(x, y):
        if x + y == K:
            return F(x, y)
        cands = []
        if x < X:
            cands.append((H(x + 1, y) - H(x, y), (x + 1, y)))
        if y < K:
            cands.append((H(x, y + 1) - H(x, y), (x, y + 1)))
        best = max(c[0] for c in cands)
        return min(fwd(*c[1]) for c in cands if c[0] == best)

    @lru_cache(maxsize=None)
    def rev(x, y):
        if x + y == K:
            return F(x, y)
        cands = []
        if x >= 1:
            cands.append((H(x, y) - H(x - 1, y), (x - 1, y)))
        if y >= 1:
            cands.append((H(x, y) - H(x, y - 1), (x, y - 1)))
        best = min(c[0] for c in cands)
        return min(rev(*c[1]) for c in cands if c[0] == best)

    vf, vr = fwd(0, 0), rev(X, K)
    q_fwd = sum(n - s for s in range(K))                 # K steps
    q_rev = sum(s for s in range(K + 1, n + 1))          # n - K steps
    fwd.cache_clear()
    rev.cache_clear()
    return vf, vr, q_fwd, q_rev


def run_D1(K, etas, ns):
    print()
    print("D1  structured strategies, adversarial ties, count-grid DP   "
          "[VERIFIED-EXHAUSTIVE]")
    ok = True
    for eta in etas:
        fam = Family(K, eta)
        W, rho = fam.W, rho_exact(K, eta)
        print("  --- K=%d eta=%s  j=%d m=%d t*=%d  K+t*=%d  W=%s (%.9f)  "
              "rho=%s (%.9f) ---"
              % (K, eta, fam.j, fam.m, fam.T, K + fam.T, W, float(W),
                 rho, float(rho)))
        for n in ns:
            vf, vr, qf, qr = structured_values(fam, n)
            vm = max(vf, vr)
            leakfree = n >= K + fam.T
            budget = n * K
            for label, val, nq in (("forward greedy (adversarial ties)",
                                    vf, qf),
                                   ("reverse (deletion) greedy", vr, qr),
                                   ("max(forward, reverse)", vm,
                                    qf + qr)):
                rec = {"K": K, "eta": str(eta), "n": n, "candidate": label,
                       "regime": "n >= K+t*" if leakfree else "n < K+t*",
                       "K_plus_t_star": K + fam.T,
                       "queries": nq, "budget_nK": budget,
                       "within_linear_budget": bool(nq <= budget),
                       "max_query_size": (n if "reverse" in label
                                          or "max(" in label else n),
                       "ratio": str(val), "ratio_float": float(val),
                       "W": str(W), "slack_ratio_minus_W": str(val - W),
                       "rho_K": str(rho)}
                if leakfree:
                    good = val <= W
                    rec["status"] = "PASS" if good else "FAIL"
                    if not good:
                        VIOLATIONS.append({"check": "D1", "K": K,
                                           "eta": str(eta), "n": n,
                                           "candidate": label,
                                           "ratio": str(val), "W": str(W),
                                           "inequality": "ratio <= W_K(eta)"})
                        ok = False
                else:
                    if "reverse" in label or "max(" in label:
                        good = (val == 1)
                        rec["status"] = ("EXPECTED-LEAK" if good else "FAIL")
                        rec["must_not_claim"] = (
                            "finite-n '<= W_K' is false here: reverse greedy "
                            "reads O off the leaking large sets, ratio = 1")
                        if not good:
                            VIOLATIONS.append(
                                {"check": "D1 leak regime", "K": K,
                                 "eta": str(eta), "n": n, "candidate": label,
                                 "ratio": str(val),
                                 "inequality": "ratio == 1 expected"})
                            ok = False
                    else:
                        good = val <= W
                        rec["status"] = "PASS" if good else "FAIL"
                        if not good:
                            VIOLATIONS.append(
                                {"check": "D1", "K": K, "eta": str(eta),
                                 "n": n, "candidate": label,
                                 "ratio": str(val), "W": str(W),
                                 "inequality": "ratio <= W_K(eta)"})
                            ok = False
                D_STRUCTURED.append(rec)
            print("    n=%2d (%-9s) fwd=%.9f rev=%.9f max=%.9f  W=%.9f  "
                  "fwd<=W:%s rev<=W:%s  rev==1:%s  q_rev=%d vs nK=%d"
                  % (n, "n>=K+t*" if leakfree else "n<K+t*", float(vf),
                     float(vr), float(vm), float(W), vf <= W, vr <= W,
                     vr == 1, qr, budget))
    COUNTS["D1_structured_cases"] = len(D_STRUCTURED)
    return ok


# ---------------------------------------------------------------------------
# D2: random deterministic strategies with arbitrary-size queries.
# ---------------------------------------------------------------------------
def make_random_strategy(rng, n, K):
    """A random sequence of at most nK queries of ARBITRARY size, plus a fixed
    output rule reading only the answer vector."""
    budget = n * K
    nq = rng.randint(1, budget)
    sets = [frozenset(rng.sample(range(n), rng.randint(1, n)))
            for _ in range(nq)]
    rule = rng.randrange(4)
    extra = rng.randrange(10 ** 9)
    return sets, rule, extra


def apply_output_rule(sets, answers, rule, extra, n, K):
    """Deterministic function of (fixed query list, answer vector) only."""
    if rule == 0:                       # best queried K-set by answer
        best, bestv = None, None
        for S, a in zip(sets, answers):
            if len(S) == K and (bestv is None or a > bestv):
                best, bestv = S, a
        if best is not None:
            return best
        return frozenset(range(K))
    if rule == 1:                       # elements by average answer mass
        sc = {}
        for S, a in zip(sets, answers):
            for e in S:
                sc[e] = sc.get(e, Fr(0)) + a / len(S)
        order = sorted(range(n), key=lambda e: (-sc.get(e, Fr(0)), e))
        return frozenset(order[:K])
    if rule == 2:                       # elements by answer-gap witness
        sc = {}
        base = {}
        for S, a in zip(sets, answers):
            base[len(S)] = max(base.get(len(S), a), a)
        for S, a in zip(sets, answers):
            dv = a - base[len(S)]
            for e in S:
                sc[e] = sc.get(e, Fr(0)) + dv
        order = sorted(range(n), key=lambda e: (sc.get(e, Fr(0)), e))
        return frozenset(order[:K])
    key = (extra,) + tuple((a.numerator, a.denominator) for a in answers)
    r = random.Random(hash(key) & 0xFFFFFFFF)
    return frozenset(r.sample(range(n), K))


def run_D2(K, etas, ns, total=300):
    print()
    print("D2  %d random deterministic strategies, arbitrary-size queries, "
          "adversary over every placement of O   [VERIFIED-EXHAUSTIVE]" % total)
    rng = random.Random(SEED + 7)
    ok = True
    combos = [(eta, n) for eta in etas for n in ns]
    per = total // len(combos)
    extra_first = total - per * len(combos)
    counts = {"cases": 0, "leak_free_regime": 0, "leak_regime": 0,
              "violations_leak_free": 0, "above_W_in_leak_regime": 0}
    worst = None
    for ci, (eta, n) in enumerate(combos):
        fam = Family(K, eta)
        W = fam.W
        leakfree = n >= K + fam.T
        mm = per + (extra_first if ci == 0 else 0)
        placements = list(itertools.combinations(range(n), K))
        loc_worst = None
        for t in range(mm):
            sets, rule, extra = make_random_strategy(rng, n, K)
            best_for_adv = None
            for Otup in placements:
                O = frozenset(Otup)
                ans = [fam.H(len(S) - len(S & O), len(S & O)) for S in sets]
                T = apply_output_rule(sets, ans, rule, extra, n, K)
                y = len(T & O)
                x = len(T) - y
                ratio = fam.F(x, y)
                if best_for_adv is None or ratio < best_for_adv[0]:
                    best_for_adv = (ratio, Otup)
            ratio, Obest = best_for_adv
            counts["cases"] += 1
            rec = {"K": K, "eta": str(eta), "n": n, "rule": rule,
                   "queries": len(sets),
                   "max_query_size": max(len(S) for S in sets),
                   "budget_nK": n * K,
                   "placements_tried": len(placements),
                   "regime": "n >= K+t*" if leakfree else "n < K+t*",
                   "adversary_min_ratio": str(ratio),
                   "ratio_float": float(ratio), "W": str(W),
                   "slack_ratio_minus_W": str(ratio - W)}
            if leakfree:
                counts["leak_free_regime"] += 1
                if ratio > W:
                    counts["violations_leak_free"] += 1
                    rec["status"] = "FAIL"
                    ok = False
                    VIOLATIONS.append(
                        {"check": "D2", "K": K, "eta": str(eta), "n": n,
                         "trial": t, "rule": rule,
                         "adversary_min_ratio": str(ratio), "W": str(W),
                         "inequality": "min_O ratio <= W_K(eta)"})
                else:
                    rec["status"] = "PASS"
            else:
                counts["leak_regime"] += 1
                if ratio > W:
                    counts["above_W_in_leak_regime"] += 1
                    rec["status"] = "EXPECTED-LEAK"
                else:
                    rec["status"] = "PASS"
            if (loc_worst is None or ratio - W > loc_worst[0]) and leakfree:
                loc_worst = (ratio - W, rec)
            if leakfree and (worst is None or ratio - W > worst[0]):
                worst = (ratio - W, rec)
            D_RANDOM.append(rec)
        print("    eta=%-8s n=%2d (%-9s): %3d strategies, adversary-min ratio "
              "max = %s"
              % (eta, n, "n>=K+t*" if leakfree else "n<K+t*", mm,
                 ("%.9f" % float(Fr(loc_worst[1]["adversary_min_ratio"])))
                 if loc_worst else "n/a (leak regime)"))
    COUNTS["D2"] = counts
    ok &= check("D2 %d random arbitrary-size strategies; in the leak-free "
                "regime n >= K+t* every adversary-min ratio <= W_K(eta) "
                "(%d cases, %d violations)"
                % (counts["cases"], counts["leak_free_regime"],
                   counts["violations_leak_free"]),
                counts["violations_leak_free"] == 0,
                "worst slack ratio - W = %s at %s"
                % (worst[0], json.dumps({k: worst[1][k] for k in
                                         ("eta", "n", "rule", "queries",
                                          "adversary_min_ratio", "W")},
                                        sort_keys=True)),
                "[VERIFIED-EXHAUSTIVE]")
    return ok, worst, counts


# ---------------------------------------------------------------------------
def main():
    print("V11 oracle: thm:linear-anysize (ledger T10d, J7; Proposition)")
    print("repo root:", ROOT)
    print("exact arithmetic: fractions.Fraction and sympy; seed", SEED)
    print("existing repository scripts are rerun by subprocess and never "
          "modified")
    print()
    print("=== Criterion C ===", flush=True)
    okC14 = run_C1_C4()
    okC5, c5 = run_C5()
    okC6, c6 = run_C6()

    K = 3
    etas = [Fr(3, 2), Fr(2), Fr(667, 500)]
    ns = list(range(8, 15))
    okC7, c7rows = run_C7([(K, e) for e in etas])
    okC8, c8worst = run_C8()
    okC9 = run_C9()

    print()
    print("=== Criterion D ===", flush=True)
    okD1 = run_D1(K, etas, ns)
    okD2, d2worst, d2counts = run_D2(K, etas, ns, 300)

    ok_all = (okC14 and okC5 and okC6 and okC7 and okC8 and okC9
              and okD1 and okD2)

    # worst D slack in the leak-free regime
    lf = [r for r in D_STRUCTURED if r["regime"] == "n >= K+t*"]
    d1_worst = max(lf, key=lambda r: Fr(r["slack_ratio_minus_W"]))
    leak_rows = [r for r in D_STRUCTURED
                 if r["regime"] == "n < K+t*" and r["candidate"].startswith(
                     "reverse")]
    d_worst = {
        "D1_leak_free": {"slack_ratio_minus_W":
                         d1_worst["slack_ratio_minus_W"],
                         "where": {k: d1_worst[k] for k in
                                   ("K", "eta", "n", "candidate", "ratio",
                                    "W")}},
        "D2_leak_free": {"slack_ratio_minus_W": str(d2worst[0]),
                         "where": {k: d2worst[1][k] for k in
                                   ("K", "eta", "n", "rule", "queries",
                                    "adversary_min_ratio", "W")}},
        "D1_leak_regime_reverse_greedy":
            [{k: r[k] for k in ("eta", "n", "ratio", "W", "queries",
                                "budget_nK", "within_linear_budget")}
             for r in leak_rows]}

    print()
    print("counts:", json.dumps(COUNTS, sort_keys=True)[:2000])
    print("D1 worst slack ratio - W in the leak-free regime:",
          json.dumps(d_worst["D1_leak_free"], sort_keys=True))
    print("D2 worst slack ratio - W in the leak-free regime:",
          json.dumps(d_worst["D2_leak_free"], sort_keys=True))
    print("violations:", len(VIOLATIONS))
    for v in VIOLATIONS[:8]:
        print("   ", json.dumps(v, sort_keys=True)[:400])

    blob = {
        "statement": "thm:linear-anysize (T10d, J7): rho_K <= alpha_lin <= "
                     "min{1/eta, W_K} <= min{1/eta, rho_K + "
                     "1/(K(e^{K-1}-K-1))}, K >= 3, eta > 1, n -> infinity, "
                     "arbitrary-size queries, O(nK) budget",
        "overall": "PASS" if ok_all else "FAIL",
        "checks": CHECKS,
        "counts": COUNTS,
        "reruns": SUBPROCS,
        "C5_F3_counterexample": c5,
        "C6_running_example": c6,
        "C7_configs": c7rows,
        "C8_worst_gap_over_bound": c8worst,
        "D_structured": D_STRUCTURED,
        "D_random_count": len(D_RANDOM),
        "D_random_counts": d2counts,
        "D_random_sample": D_RANDOM[:40],
        "D_worst": d_worst,
        "violations": VIOLATIONS,
        "seed": SEED,
        "seconds": round(time.time() - T0, 1)}
    path = os.path.join(HERE, "linear_anysize.json")
    with open(path, "w") as fh:
        json.dump(blob, fh, indent=1)
    print("json written:", path)
    nfail = sum(1 for c in CHECKS if c["status"] == "FAIL")
    print("OVERALL: %s (%d checks, %d failed, %d violations, %d structured D "
          "cases, %d random D strategies, %.1fs)"
          % ("PASS" if ok_all else "FAIL", len(CHECKS), nfail,
             len(VIOLATIONS), len(D_STRUCTURED), len(D_RANDOM),
             time.time() - T0))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())

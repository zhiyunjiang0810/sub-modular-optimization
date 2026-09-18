#!/usr/bin/env python3
"""V11 oracle for thm:hardness (ledger T10; Theorem 3 of the paper).

Statement under test (results/V11/inputs/statement_hardness.md):

    Let c >= 0 be real, tau = ceil(c) + 1, and let integers K > tau and
    n >= 4 K^{c+2} and a real eta > 1 with eta >= (K-1)/(K-tau) be fixed, so
    that thetabar = (eta (K - tau) + 1)/K >= 1.  For every deterministic
    algorithm making at most n^c queries to ftilde, each on a set of size at
    most K, there is an instance (f, ftilde) with monotone submodular f, whose
    smallest admissible error factors in Definition 1 have product exactly eta,
    on which the output T (|T| <= K) satisfies

        f(T)/f(O*) <= H_{K,tau}(eta) := 1 - (1 - 1/(eta(K-tau)+1))^K
                                      = L_K(thetabar).

    Any prescribed split eta_u eta_o = eta is realized by a rescaling.  The
    randomized version costs an additive eps_n.  As K -> infinity with tau and
    eta fixed, H_{K,tau}(eta) -> 1 - e^{-1/eta}.

Route-one proof material (read, never used as an oracle):
    paper/sections/appendix_proofs.tex, subsection app:hardness (~line 1462),
    ledger card THEOREM_LEDGER.md section T10.
Existing repository scripts rerun here (never modified):
    results/J2_core_oracles.py   (264 exact count-grid instances, 57,728 edges)
    results/H3_j2_recheck.py     (independent recheck of the same edge table)

The family, as fixed in app:hardness.  For integers 1 <= tau < K < n, a real
theta >= 1, a hidden K-set O and x = |S \\ O|, y = |S cap O|, with
a = 1 - 1/(theta K):

    F_O(S) = theta^{-1/2} [ 1 - a^x (1 - y/K) ],
    G_O(S) = 1 - a^{x+y}                      if y <= tau,
             1 - a^{x+tau} (K-y)/(K-tau)      if y >= tau.

Write Fbar = sqrt(theta) F_O, A = a^tau K/(K-tau), B = a^{1-tau}.  The
calibration is thetabar = (eta(K-tau)+1)/K, which makes the exact error product
Psi(theta) = theta A B = (theta K - 1)/(K - tau) equal to eta.

Criterion C (oracle)
    C1  rerun results/J2_core_oracles.py; exit code and key counts recorded.
    C2  rerun results/H3_j2_recheck.py; exit code and key counts recorded.
    C3  the exact error product theta A B = (theta K - 1)/(K - tau), and the
        edge-table extremes rmax = A, rmin = 1/(theta B): sympy identity plus
        an exact rational sweep.                          [VERIFIED-SYMBOLIC]
    C4  the exact rational table min{H_{K,tau}(eta), 1/eta} for K = 2..8,
        tau in {2,3}, eta in {6/5, 3/2, 2, 3}, restricted to K > tau and
        eta >= (K-1)/(K-tau); every cell where H is NOT binding (H > 1/eta) is
        reported exactly.                                 [VERIFIED-EXHAUSTIVE]
    C5  the stated expectation along tau = 2, eta = 3/2: K = 3 and K = 4 not
        binding, K >= 5 binding.                          [VERIFIED-EXHAUSTIVE]
    C6  the identity H_{K,1}(eta) = U_K(eta), symbolically in (K, eta) and on
        an exact rational sweep.                          [VERIFIED-SYMBOLIC]
    C7  the limit H_{K,tau}(eta) -> 1 - e^{-1/eta} as K -> infinity with tau
        and eta fixed, by sympy, plus an exact rational convergence check.
                                                          [VERIFIED-SYMBOLIC]
    C8  the calibration itself: Psi(thetabar) = eta and H_{K,tau}(eta) =
        L_K(thetabar), symbolically and exactly.          [VERIFIED-SYMBOLIC]

Criterion D (counterexample search on the statement itself)
    Legality is what a violation would break.  For every drawn configuration
    (K, tau, eta, n) the script verifies EXACTLY, on the whole count grid:
      (a) thetabar >= 1 and a in (0,1);
      (b) normalization Fbar(0,0) = 0, Fbar(0,K) = 1, 0 <= Fbar <= 1, and
          O* = O, i.e. max_{x+y<=K} Fbar = Fbar(0,K);
      (c) f = F_O monotone (both first differences >= 0) and submodular (all
          three second differences <= 0) on the count grid, so Lemma app-count
          lifts it to a normalized monotone submodular set function;
      (d) G_O monotone, and every zero-true-gain edge carries zero predicted
          gain (no unbounded ratio);
      (e) the smallest admissible error factors: rmax = A and rmin = 1/(theta B)
          are attained on actual edges, eta_o = sqrt(theta) A >= 1,
          eta_u = sqrt(theta) B >= 1, and the product eta_u eta_o = rmax/rmin
          is EXACTLY eta;
      (f) the value bound is attained by the balanced output: for T of size K
          disjoint from O, Fbar(T)/Fbar(O) = 1 - a^K = H_{K,tau}(eta) exactly,
          and no output of size <= K disjoint from O does better;
      (g) the prescribed-split rescaling beta = eta_o/(sqrt(theta) A) moves the
          two extremes to exactly (1/eta_u, eta_o) while leaving the product
          fixed (checked on the squared, rational, form for two splits).
    D-random    >= 2000 random rational configurations, K in 3..8,
                tau in 1..K-1, eta rational >= (K-1)/(K-tau), n = K + m.
    D-structured  tau = 1 (the U_K case), eta exactly at the boundary
                (K-1)/(K-tau) so thetabar = 1, and K = tau + 1.
    D-setlevel  a sample of configurations is additionally verified by full
                power-set enumeration of monotonicity and submodularity on a
                real ground set.
    D-ngrid     the edge table is verified to be independent of n.

Exactness: every decision uses fractions.Fraction or sympy.  Floats appear only
inside printed parentheses.  Seed is fixed (20260918).

Outputs (new files only): hardness.log, hardness.json, hardness.md in this
directory, and reruns_hardness/ for the two rerun copies.  Existing repository
files are restored byte-for-byte after each rerun and the sha256 is checked.

Run:  python3 results/V11/oracle/hardness.py    (exit 0 iff every check passed)
"""
import hashlib
import itertools
import json
import os
import random
import shutil
import subprocess
import sys
import time
from fractions import Fraction as Fr

import sympy as sp

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RERUN_DIR = os.path.join(HERE, "reruns_hardness")
SEED = 20260918

CHECKS = []        # {name, status, detail}
COUNTS = {}
VIOLATIONS = []    # exact failure records
SUBPROCS = []
LOG_LINES = []


def log(msg=""):
    print(msg, flush=True)
    LOG_LINES.append(str(msg))


def record(name, ok, status_ok, detail, status_bad="FAILED"):
    st = status_ok if ok else status_bad
    CHECKS.append({"name": name, "status": st, "detail": detail})
    log(f"[{'PASS' if ok else 'FAIL'}] {name:52s} {st:24s} {detail}")
    return ok


def fail(kind, params, inequality, values):
    rec = {"kind": kind, "parameters": params, "inequality": inequality,
           "values": values}
    VIOLATIONS.append(rec)
    log(f"  VIOLATION {kind}: {inequality}  at {params}  values={values}")


# ---------------------------------------------------------------------------
# closed forms, all exact
# ---------------------------------------------------------------------------
def H_closed(K, tau, eta):
    """H_{K,tau}(eta) = 1 - (1 - 1/(eta(K-tau)+1))^K, exact."""
    return 1 - (1 - Fr(1, 1) / (eta * (K - tau) + 1)) ** K


def U_closed(K, eta):
    """U_K(eta) = 1 - (1 - 1/(eta(K-1)+1))^K, exact."""
    return 1 - (1 - Fr(1, 1) / (eta * (K - 1) + 1)) ** K


def L_closed(K, theta):
    """L_K(theta) = 1 - (1 - 1/(theta K))^K, exact."""
    return 1 - (1 - Fr(1, 1) / (theta * K)) ** K


def thetabar(K, tau, eta):
    return Fr(eta * (K - tau) + 1, 1) / K


def Psi(K, tau, theta):
    """The exact error product of the unscaled pair, (theta K - 1)/(K - tau)."""
    return Fr(theta * K - 1, 1) / (K - tau)


# ---------------------------------------------------------------------------
# the family on the count grid, exact rationals
# ---------------------------------------------------------------------------
class Family:
    """F_O and G_O of app:hardness on the count grid (x, y).

    Fbar = sqrt(theta) F_O is stored (the prefactor cancels from every ratio
    and is reinstated explicitly where the theorem needs it).
    """

    def __init__(self, K, tau, theta, xmax):
        assert 1 <= tau < K
        self.K, self.tau, self.theta, self.xmax = K, tau, theta, xmax
        self.a = 1 - Fr(1, 1) / (theta * K)
        self.A = self.a ** tau * Fr(K, K - tau)
        self.B = self.a ** (1 - tau) if tau >= 1 else Fr(1)
        self.pw = [self.a ** i for i in range(xmax + K + 2)]

    def Fbar(self, x, y):
        return 1 - self.pw[x] * (1 - Fr(y, self.K))

    def G(self, x, y):
        K, tau = self.K, self.tau
        if y <= tau:
            return 1 - self.pw[x + y]
        return 1 - self.pw[x + tau] * Fr(K - y, K - tau)

    def grid(self):
        for x in range(self.xmax + 1):
            for y in range(self.K + 1):
                yield x, y


def check_config(K, tau, eta, n, tag, splits=(None,)):
    """Full exact legality + error + value battery for one configuration.

    Returns (ok, info).  Every decision is an exact Fraction comparison.
    """
    params = {"K": K, "tau": tau, "eta": str(eta), "n": n, "tag": tag}
    lower = Fr(K - 1, K - tau)
    if eta < lower:
        fail("domain", params, f"eta >= (K-1)/(K-tau) = {lower}", {"eta": str(eta)})
        return False, {}
    th = thetabar(K, tau, eta)
    if th < 1:
        fail("calibration", params, "thetabar >= 1", {"thetabar": str(th)})
        return False, {}
    xmax = n - K
    fam = Family(K, tau, th, xmax)
    a, A, B = fam.a, fam.A, fam.B
    ok = True
    info = {"thetabar": str(th), "a": str(a), "A": str(A), "B": str(B)}

    # (a) a in (0,1)
    if not (0 < a < 1):
        fail("a-range", params, "0 < a < 1", {"a": str(a)}); ok = False

    # (b) normalization and O* = O
    if fam.Fbar(0, 0) != 0 or fam.Fbar(0, K) != 1:
        fail("normalization", params, "Fbar(0,0)=0 and Fbar(0,K)=1",
             {"F00": str(fam.Fbar(0, 0)), "F0K": str(fam.Fbar(0, K))}); ok = False
    best = None
    for x, y in fam.grid():
        v = fam.Fbar(x, y)
        if not (0 <= v <= 1):
            fail("range", params, "0 <= Fbar <= 1", {"x": x, "y": y, "v": str(v)})
            ok = False
        if x + y <= K and (best is None or v > best[0]):
            best = (v, x, y)
    if best is None or best[0] != 1 or (best[1], best[2]) != (0, K):
        fail("optimum", params, "argmax_{x+y<=K} Fbar = (0,K) with value 1",
             {"best": [str(best[0]), best[1], best[2]] if best else None}); ok = False

    # (c)+(d) monotone, submodular, G monotone, zero-gain edges
    min_pos_dr = None
    zero_dr = 0
    for x, y in fam.grid():
        v = fam.Fbar(x, y)
        for dx, dy in ((1, 0), (0, 1)):
            X, Y = x + dx, y + dy
            if X > xmax or Y > K:
                continue
            dF = fam.Fbar(X, Y) - v
            dG = fam.G(X, Y) - fam.G(x, y)
            if dF < 0:
                fail("monotone-f", params, "Delta Fbar >= 0",
                     {"x": x, "y": y, "dir": (dx, dy), "dF": str(dF)}); ok = False
            if dG < 0:
                fail("monotone-g", params, "Delta G >= 0",
                     {"x": x, "y": y, "dir": (dx, dy), "dG": str(dG)}); ok = False
            if dF == 0 and dG != 0:
                fail("zero-gain", params, "Delta Fbar = 0 implies Delta G = 0",
                     {"x": x, "y": y, "dir": (dx, dy), "dG": str(dG)}); ok = False
        # three second differences, all must be <= 0
        for (dx1, dy1), (dx2, dy2), nm in (((1, 0), (1, 0), "xx"),
                                           ((1, 0), (0, 1), "xy"),
                                           ((0, 1), (0, 1), "yy")):
            X1, Y1 = x + dx1, y + dy1
            X2, Y2 = x + dx2, y + dy2
            Xb, Yb = x + dx1 + dx2, y + dy1 + dy2
            if Xb > xmax or Yb > K:
                continue
            sd = fam.Fbar(Xb, Yb) - fam.Fbar(X1, Y1) - fam.Fbar(X2, Y2) + v
            if sd > 0:
                fail("submodular", params, f"second difference {nm} <= 0",
                     {"x": x, "y": y, "sd": str(sd)}); ok = False
            marg = -sd
            if marg == 0:
                zero_dr += 1
            elif min_pos_dr is None or marg < min_pos_dr:
                min_pos_dr = marg
    info["min_positive_DR_margin"] = str(min_pos_dr)
    info["zero_DR_edges"] = zero_dr

    # (e) the smallest admissible error factors
    rmax = rmin = None
    argmax = argmin = None
    for x, y in fam.grid():
        for dx, dy in ((1, 0), (0, 1)):
            X, Y = x + dx, y + dy
            if X > xmax or Y > K:
                continue
            dF = fam.Fbar(X, Y) - fam.Fbar(x, y)
            if dF == 0:
                continue
            r = (fam.G(X, Y) - fam.G(x, y)) / dF
            if rmax is None or r > rmax:
                rmax, argmax = r, (x, y, dx, dy)
            if rmin is None or r < rmin:
                rmin, argmin = r, (x, y, dx, dy)
    if rmax != A:
        fail("edge-max", params, "max dG/dFbar = A", {"rmax": str(rmax), "A": str(A)})
        ok = False
    if rmin != 1 / (th * B):
        fail("edge-min", params, "min dG/dFbar = 1/(theta B)",
             {"rmin": str(rmin), "target": str(1 / (th * B))}); ok = False
    prod = rmax / rmin                       # = (sqrt(th) A)(sqrt(th) B) = th A B
    if prod != eta:
        fail("error-product", params, "eta_u * eta_o = eta",
             {"product": str(prod), "eta": str(eta)}); ok = False
    if th * A * B != Psi(K, tau, th):
        fail("Psi", params, "theta A B = (theta K - 1)/(K - tau)",
             {"lhs": str(th * A * B), "rhs": str(Psi(K, tau, th))}); ok = False
    # eta_o = sqrt(th) A >= 1 and eta_u = sqrt(th) B >= 1, decided on squares
    if th * A * A < 1:
        fail("eta_o", params, "eta_o = sqrt(theta) A >= 1",
             {"square": str(th * A * A)}); ok = False
    if th * B * B < 1:
        fail("eta_u", params, "eta_u = sqrt(theta) B >= 1",
             {"square": str(th * B * B)}); ok = False
    info["argmax_edge"] = list(argmax)
    info["argmin_edge"] = list(argmin)
    info["error_product"] = str(prod)

    # (f) the value bound is attained by the balanced output
    val = fam.Fbar(K, 0) / fam.Fbar(0, K)
    Hcl = H_closed(K, tau, eta)
    if val != Hcl:
        fail("value", params, "Fbar(K,0)/Fbar(0,K) = H_{K,tau}(eta)",
             {"lhs": str(val), "H": str(Hcl)}); ok = False
    if Hcl != L_closed(K, th):
        fail("L-identity", params, "H_{K,tau}(eta) = L_K(thetabar)",
             {"H": str(Hcl), "L": str(L_closed(K, th))}); ok = False
    worst_disjoint = max(fam.Fbar(t, 0) for t in range(K + 1))
    if worst_disjoint != fam.Fbar(K, 0):
        fail("balanced", params, "max_{|T|<=K, T disjoint O} Fbar(T) = Fbar(K,0)",
             {"max": str(worst_disjoint)}); ok = False
    info["value_ratio"] = str(val)

    # (g) prescribed split: beta = eta_o/(sqrt(theta) A) rescales G.  Work on
    # squares so every decision stays rational.
    for split in splits:
        if split is None:
            continue
        eu, eo = split
        if eu * eo != eta:
            fail("split-input", params, "eta_u eta_o = eta",
                 {"eta_u": str(eu), "eta_o": str(eo)}); ok = False
            continue
        # beta^2 = eo^2/(theta A^2); new max = beta*sqrt(theta)*A = eo exactly,
        # new min = beta*sqrt(theta)*rmin, and 1/that must be eta_u.
        beta_sq = eo * eo / (th * A * A)
        new_max_sq = beta_sq * th * rmax * rmax
        new_min_sq = beta_sq * th * rmin * rmin
        if new_max_sq != eo * eo:
            fail("split-max", params, "rescaled max predicted/true ratio = eta_o",
                 {"lhs": str(new_max_sq), "rhs": str(eo * eo)}); ok = False
        if new_min_sq * eu * eu != 1:
            fail("split-min", params, "rescaled min predicted/true ratio = 1/eta_u",
                 {"lhs": str(new_min_sq), "eta_u": str(eu)}); ok = False

    info["ok"] = ok
    return ok, info


def setlevel_check(K, tau, eta, n):
    """Full power-set enumeration of monotonicity and submodularity of f = F_O
    on a real ground set of n elements, O = {0,...,K-1}.  Exact."""
    th = thetabar(K, tau, eta)
    fam = Family(K, tau, th, n)
    O = frozenset(range(K))
    ground = list(range(n))

    def f(S):
        y = len(S & O)
        return fam.Fbar(len(S) - y, y)

    for r in range(n + 1):
        for comb in itertools.combinations(ground, r):
            S = frozenset(comb)
            base = f(S)
            rest = [e for e in ground if e not in S]
            for e in rest:
                de = f(S | {e}) - base
                if de < 0:
                    return False, {"S": sorted(S), "e": e, "delta": str(de),
                                   "which": "monotone"}
                for ep in rest:
                    if ep <= e:
                        continue
                    # diminishing returns: d_e(S) >= d_e(S + ep)
                    dep = f(S | {e, ep}) - f(S | {ep})
                    if de < dep:
                        return False, {"S": sorted(S), "e": e, "ep": ep,
                                       "de": str(de), "dep": str(dep),
                                       "which": "submodular"}
    return True, {}


# ---------------------------------------------------------------------------
# C1 / C2: reruns of existing repository scripts, originals restored
# ---------------------------------------------------------------------------
def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def rerun(name, script_rel, outputs):
    os.makedirs(RERUN_DIR, exist_ok=True)
    script = os.path.join(ROOT, script_rel)
    saved = {}
    for rel in outputs:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            saved[rel] = (sha(p), open(p, "rb").read())
    t0 = time.time()
    proc = subprocess.run([sys.executable, script], cwd=ROOT,
                          capture_output=True, text=True, timeout=1800)
    dt = round(time.time() - t0, 2)
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
    rec = {"name": name, "script": script_rel, "exit_code": proc.returncode,
           "seconds": dt,
           "stdout_tail": proc.stdout.strip().splitlines()[-4:],
           "outputs_before_sha256": {k: v[0] for k, v in saved.items()},
           "outputs_after_rerun_sha256": fresh,
           "outputs_restored_bytewise": restored,
           "copy_dir": os.path.relpath(RERUN_DIR, ROOT)}
    SUBPROCS.append(rec)
    return proc, rec


def run_C1():
    log("\n--- C1  rerun results/J2_core_oracles.py ---")
    proc, rec = rerun("J2_core_oracles", "results/J2_core_oracles.py",
                      ["results/J2_core_oracles.json"])
    data = {}
    copy = os.path.join(RERUN_DIR, "J2_core_oracles.json")
    if os.path.exists(copy):
        data = json.loads(open(copy).read())
    hard = data.get("hardness", {})
    keys = {"exact_count_grid_cases": hard.get("exact_count_grid_cases"),
            "edges_checked": hard.get("edges_checked"),
            "K_range": hard.get("K_range"),
            "symbolic_identities": data.get("symbolic", {}).get("count"),
            "dual_weighted_sums": data.get("dual", {}).get("exact_fraction_weighted_sums"),
            "R6_lp_objectives": data.get("R6_LP", {}).get("lp_objectives"),
            "all_passed": data.get("all_passed")}
    COUNTS["C1_J2"] = keys
    rec["key_counts"] = keys
    ok = (rec["exit_code"] == 0 and keys["exact_count_grid_cases"] == 264
          and keys["edges_checked"] == 57728 and keys["all_passed"] is True
          and all(rec["outputs_restored_bytewise"].values()))
    record("C1 rerun results/J2_core_oracles.py", ok, "VERIFIED-SYMBOLIC",
           f"exit={rec['exit_code']}, {rec['seconds']}s, count-grid instances="
           f"{keys['exact_count_grid_cases']}, edges={keys['edges_checked']}, "
           f"symbolic identities={keys['symbolic_identities']}, "
           f"dual sums={keys['dual_weighted_sums']}, "
           f"R6 LP objectives={keys['R6_lp_objectives']}, json restored="
           f"{all(rec['outputs_restored_bytewise'].values())}")
    return ok


def run_C2():
    log("\n--- C2  rerun results/H3_j2_recheck.py ---")
    proc, rec = rerun("H3_j2_recheck", "results/H3_j2_recheck.py", [])
    out = proc.stdout
    npass = out.count("PASS ")
    nfail = out.count("FAIL ")
    hard_line = [l for l in out.splitlines() if "hardness: edge extremes" in l]
    calib_line = [l for l in out.splitlines() if "recalibration table" in l]
    keys = {"pass_lines": npass, "fail_lines": nfail,
            "all_pass": "ALL PASS" in out,
            "edge_extremes_line": hard_line[0].strip() if hard_line else None,
            "recalibration_line": calib_line[0].strip() if calib_line else None}
    COUNTS["C2_H3"] = keys
    rec["key_counts"] = keys
    ok = bool(rec["exit_code"] == 0 and keys["all_pass"] and nfail == 0
              and hard_line and calib_line)
    record("C2 rerun results/H3_j2_recheck.py", ok, "VERIFIED-SYMBOLIC",
           f"exit={rec['exit_code']}, {rec['seconds']}s, PASS lines={npass}, "
           f"FAIL lines={nfail}, ALL PASS={keys['all_pass']}")
    return ok


# ---------------------------------------------------------------------------
# C3: the exact error product
# ---------------------------------------------------------------------------
def run_C3():
    log("\n--- C3  exact error product theta A B = (theta K - 1)/(K - tau) ---")
    K, tau, th = sp.symbols("K tau theta", positive=True)
    a = 1 - 1 / (th * K)
    A = a ** tau * K / (K - tau)
    B = a ** (1 - tau)
    resid = sp.simplify(sp.together(th * A * B - (th * K - 1) / (K - tau)))
    sym_ok = (resid == 0)
    log(f"  sympy residue theta*A*B - (theta K - 1)/(K - tau) = {resid}")
    # exact rational sweep over the same domain the appendix table covers
    cases = 0
    bad = 0
    for Kv in range(2, 13):
        for tv in range(1, Kv):
            for thv in (Fr(1), Fr(6, 5), Fr(3, 2), Fr(2), Fr(4), Fr(17, 3)):
                fam = Family(Kv, tv, thv, Kv + 3)
                if thv * fam.A * fam.B != Psi(Kv, tv, thv):
                    fail("C3", {"K": Kv, "tau": tv, "theta": str(thv)},
                         "theta A B = (theta K - 1)/(K - tau)",
                         {"lhs": str(thv * fam.A * fam.B),
                          "rhs": str(Psi(Kv, tv, thv))})
                    bad += 1
                # and the inflation delta = AB - 1 = (tau - 1/theta)/(K - tau)
                if fam.A * fam.B - 1 != (tv - 1 / thv) / (Kv - tv):
                    fail("C3-delta", {"K": Kv, "tau": tv, "theta": str(thv)},
                         "A B - 1 = (tau - 1/theta)/(K - tau)",
                         {"lhs": str(fam.A * fam.B - 1)})
                    bad += 1
                cases += 1
    COUNTS["C3_product_cases"] = cases
    ok = sym_ok and bad == 0
    record("C3 exact error product theta*A*B", ok, "VERIFIED-SYMBOLIC",
           f"sympy residue 0; exact rational sweep {cases} (K,tau,theta) triples, "
           f"{bad} violations; inflation delta = A B - 1 = (tau-1/theta)/(K-tau) "
           "also exact")
    return ok


# ---------------------------------------------------------------------------
# C4 / C5: the min{H, 1/eta} table
# ---------------------------------------------------------------------------
def run_C4():
    log("\n--- C4  exact table min{H_{K,tau}(eta), 1/eta} ---")
    rows = []
    for Kv in range(2, 9):
        for tv in (2, 3):
            if Kv <= tv:
                continue
            for ev in (Fr(6, 5), Fr(3, 2), Fr(2), Fr(3)):
                lower = Fr(Kv - 1, Kv - tv)
                if ev < lower:
                    continue
                h = H_closed(Kv, tv, ev)
                inv = 1 / ev
                binding = (h <= inv)
                rows.append({"K": Kv, "tau": tv, "eta": str(ev),
                             "eta_lower_bound": str(lower),
                             "H": str(h), "H_float": float(h),
                             "inv_eta": str(inv), "inv_eta_float": float(inv),
                             "min": str(min(h, inv)),
                             "binding": binding,
                             "which": "H" if binding else "1/eta"})
    nonbinding = [r for r in rows if not r["binding"]]
    log(f"  cells in the domain (K > tau and eta >= (K-1)/(K-tau)): {len(rows)}")
    log(f"  cells where H is NOT binding (H > 1/eta): {len(nonbinding)}")
    log("  K tau eta        H                          1/eta      min      note")
    for r in rows:
        log(f"  {r['K']} {r['tau']}   {r['eta']:5s}  {r['H']:34s}"
            f" ({r['H_float']:.6f})  {r['inv_eta']:4s} ({r['inv_eta_float']:.6f})"
            f"  {r['which']:5s} {'NOT-BINDING' if not r['binding'] else ''}")
    # the tightest cell of the table: the smallest |H - 1/eta|, i.e. the worst
    # slack of the "which of the two bounds binds" decision
    tight = None
    for r in rows:
        g = abs(Fr(r["H"]) - Fr(r["inv_eta"]))
        if tight is None or g < Fr(tight["gap"]):
            tight = {"K": r["K"], "tau": r["tau"], "eta": r["eta"],
                     "gap": str(g), "gap_float": float(g),
                     "which": r["which"], "binding": r["binding"]}
    log(f"  tightest cell: K={tight['K']}, tau={tight['tau']}, eta={tight['eta']}, "
        f"|H - 1/eta| = {tight['gap']} ({tight['gap_float']:.6f}), "
        f"min is {tight['which']}")
    COUNTS["C4_cells"] = len(rows)
    COUNTS["C4_nonbinding"] = len(nonbinding)
    COUNTS["C4_tightest_cell"] = tight
    ok = len(rows) > 0
    record("C4 exact min{H,1/eta} table", ok, "VERIFIED-EXHAUSTIVE",
           f"{len(rows)} cells in the domain, {len(nonbinding)} of them NOT "
           f"binding (H > 1/eta); tightest cell K={tight['K']}, tau={tight['tau']}, "
           f"eta={tight['eta']} with |H - 1/eta| = {tight['gap']}; all entries "
           "exact rationals")
    return ok, rows, nonbinding


def run_C5(rows):
    log("\n--- C5  the stated expectation along tau = 2, eta = 3/2 ---")
    col = {r["K"]: r for r in rows if r["tau"] == 2 and r["eta"] == "3/2"}
    notes = []
    ok = True
    # K = 3 with tau = 2, eta = 3/2 is OUTSIDE the domain: (K-1)/(K-tau) = 2.
    lower3 = Fr(3 - 1, 3 - 2)
    if Fr(3, 2) >= lower3:
        notes.append("K=3 unexpectedly inside the domain")
        ok = False
    else:
        notes.append(f"K=3 is OUTSIDE the domain: (K-1)/(K-tau) = {lower3} > 3/2, "
                     "so the cell does not exist and cannot be 'not binding'")
    if 4 not in col:
        notes.append("K=4 missing from the table"); ok = False
    elif col[4]["binding"]:
        notes.append(f"K=4 expected NOT binding but H = {col[4]['H']} <= 1/eta")
        fail("C5", {"K": 4, "tau": 2, "eta": "3/2"}, "H > 1/eta expected",
             {"H": col[4]["H"], "inv": col[4]["inv_eta"]})
        ok = False
    else:
        notes.append(f"K=4 NOT binding as expected: H = {col[4]['H']} "
                     f"({col[4]['H_float']:.6f}) > 2/3")
    for Kv in (5, 6, 7, 8):
        if Kv not in col:
            notes.append(f"K={Kv} missing"); ok = False
        elif not col[Kv]["binding"]:
            notes.append(f"K={Kv} expected binding but H = {col[Kv]['H']} > 1/eta")
            fail("C5", {"K": Kv, "tau": 2, "eta": "3/2"}, "H <= 1/eta expected",
                 {"H": col[Kv]["H"], "inv": col[Kv]["inv_eta"]})
            ok = False
        else:
            notes.append(f"K={Kv} binding: H = {col[Kv]['H_float']:.6f} <= 2/3")
    for nt in notes:
        log("  " + nt)
    COUNTS["C5_notes"] = notes
    record("C5 tau=2, eta=3/2 column expectation", ok, "VERIFIED-EXHAUSTIVE",
           "K=3 is outside the domain (not merely non-binding); K=4 not binding; "
           "K=5..8 binding")
    return ok, notes


# ---------------------------------------------------------------------------
# C6: H_{K,1} = U_K
# ---------------------------------------------------------------------------
def run_C6():
    log("\n--- C6  identity H_{K,1}(eta) = U_K(eta) ---")
    K, eta = sp.symbols("K eta", positive=True)
    tau = sp.Symbol("tau", positive=True)
    Us = 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K
    Hgen = 1 - (1 - 1 / (eta * (K - tau) + 1)) ** K
    resid2 = sp.simplify(Hgen.subs(tau, 1) - Us)
    sym_ok = (resid2 == 0)
    log(f"  sympy residue H_(K,tau=1) - U_K = {resid2}")
    cases = 0
    bad = 0
    for Kv in range(2, 21):
        for ev in (Fr(6, 5), Fr(3, 2), Fr(2), Fr(3), Fr(7, 4), Fr(11, 9)):
            if H_closed(Kv, 1, ev) != U_closed(Kv, ev):
                fail("C6", {"K": Kv, "tau": 1, "eta": str(ev)},
                     "H_{K,1}(eta) = U_K(eta)",
                     {"H": str(H_closed(Kv, 1, ev)), "U": str(U_closed(Kv, ev))})
                bad += 1
            # and L_K(thetabar) with tau = 1 is the same object
            if H_closed(Kv, 1, ev) != L_closed(Kv, thetabar(Kv, 1, ev)):
                fail("C6-L", {"K": Kv, "eta": str(ev)},
                     "H_{K,1}(eta) = L_K(thetabar)", {})
                bad += 1
            cases += 1
    COUNTS["C6_cases"] = cases
    ok = sym_ok and bad == 0
    record("C6 identity H_{K,1} = U_K", ok, "VERIFIED-SYMBOLIC",
           f"sympy residue 0 in (K, eta); exact rational sweep {cases} (K,eta) "
           f"pairs, {bad} violations")
    return ok


# ---------------------------------------------------------------------------
# C7: the limit
# ---------------------------------------------------------------------------
def run_C7():
    log("\n--- C7  limit H_{K,tau}(eta) -> 1 - e^{-1/eta} as K -> infinity ---")
    K, tau, eta = sp.symbols("K tau eta", positive=True)
    Hgen = 1 - (1 - 1 / (eta * (K - tau) + 1)) ** K
    lim = sp.simplify(sp.limit(Hgen, K, sp.oo))
    target = 1 - sp.exp(-1 / eta)
    resid = sp.simplify(lim - target)
    sym_ok = (resid == 0)
    log(f"  sympy limit = {lim}")
    log(f"  residue vs 1 - exp(-1/eta) = {resid}")
    # Exact rational ENCLOSURE of 1 - e^{-t} with t = 1/eta in (0,1].  The
    # Taylor series of e^{-t} alternates with strictly decreasing terms for
    # k >= 1 when 0 < t <= 1, so consecutive partial sums bracket it.  No
    # floating point enters any decision.
    def exp_neg_enclosure(t, terms=40):
        lo = hi = None
        s = Fr(0)
        fact = Fr(1)
        for k in range(terms + 1):
            if k:
                fact *= k
            s += (-t) ** k / fact
            if k >= 1:
                if k % 2 == 0:
                    hi = s
                else:
                    lo = s
        return lo, hi                       # lo <= e^{-t} <= hi

    conv = []
    bad = 0
    for ev in (Fr(3, 2), Fr(2), Fr(3)):
        t = 1 / ev
        elo, ehi = exp_neg_enclosure(t)
        tlo, thi = 1 - ehi, 1 - elo          # tlo <= 1 - e^{-t} <= thi
        if not (tlo < thi and thi - tlo < Fr(1, 10 ** 30)):
            fail("C7-enclosure", {"eta": str(ev)},
                 "the rational enclosure of 1 - e^{-1/eta} is tight",
                 {"width": str(thi - tlo)})
            bad += 1
        prev = None
        block = []
        for Kv in (50, 100, 200, 400, 800, 1600):
            h = H_closed(Kv, 2, ev)
            # exact interval for |H - target|
            dlo = min(abs(h - tlo), abs(h - thi))
            dhi = max(abs(h - tlo), abs(h - thi))
            if prev is not None and not (dhi < prev):
                fail("C7", {"K": Kv, "tau": 2, "eta": str(ev)},
                     "|H_{K,2}(eta) - (1 - e^{-1/eta})| strictly decreasing in K",
                     {"prev_lower": str(prev), "now_upper": str(dhi)})
                bad += 1
            prev = dlo
            rec = {"K": Kv, "tau": 2, "eta": str(ev), "H": float(h),
                   "abs_gap_upper": float(dhi)}
            conv.append(rec)
            block.append(rec)
        log(f"  eta={ev}: target in [{float(tlo):.12f}, {float(thi):.12f}]; "
            f"gap at K=50 {block[0]['abs_gap_upper']:.6e} -> "
            f"K=1600 {block[-1]['abs_gap_upper']:.6e}")
    COUNTS["C7_convergence_points"] = len(conv)
    ok = sym_ok and bad == 0
    record("C7 limit 1 - e^{-1/eta}", ok, "VERIFIED-SYMBOLIC",
           f"sympy limit exact; {len(conv)} exact rational convergence points "
           f"(K up to 1600, tau=2, three eta), {bad} violations. The target is "
           "an exact rational enclosure from the alternating Taylor series, "
           "width below 1e-30, so every comparison stays exact")
    return ok, conv


# ---------------------------------------------------------------------------
# C8: the calibration
# ---------------------------------------------------------------------------
def run_C8():
    log("\n--- C8  calibration Psi(thetabar) = eta and H = L_K(thetabar) ---")
    K, tau, eta = sp.symbols("K tau eta", positive=True)
    thb = (eta * (K - tau) + 1) / K
    r1 = sp.simplify((thb * K - 1) / (K - tau) - eta)
    r2 = sp.simplify((1 - (1 - 1 / (thb * K)) ** K) - (1 - (1 - 1 / (eta * (K - tau) + 1)) ** K))
    sym_ok = (r1 == 0 and r2 == 0)
    log(f"  residue Psi(thetabar) - eta      = {r1}")
    log(f"  residue L_K(thetabar) - H_(K,tau) = {r2}")
    cases = 0
    bad = 0
    for Kv in range(2, 15):
        for tv in range(1, Kv):
            for ev in (Fr(6, 5), Fr(3, 2), Fr(2), Fr(3), Fr(9, 2)):
                if ev < Fr(Kv - 1, Kv - tv):
                    continue
                th = thetabar(Kv, tv, ev)
                if Psi(Kv, tv, th) != ev or H_closed(Kv, tv, ev) != L_closed(Kv, th):
                    fail("C8", {"K": Kv, "tau": tv, "eta": str(ev)},
                         "Psi(thetabar) = eta and H = L_K(thetabar)",
                         {"Psi": str(Psi(Kv, tv, th))})
                    bad += 1
                if th < 1:
                    fail("C8-thetabar", {"K": Kv, "tau": tv, "eta": str(ev)},
                         "thetabar >= 1 whenever eta >= (K-1)/(K-tau)",
                         {"thetabar": str(th)})
                    bad += 1
                cases += 1
    COUNTS["C8_cases"] = cases
    ok = sym_ok and bad == 0
    record("C8 calibration thetabar", ok, "VERIFIED-SYMBOLIC",
           f"sympy residues 0; exact sweep {cases} (K,tau,eta) triples in the "
           f"domain, {bad} violations")
    return ok


# ---------------------------------------------------------------------------
# D: counterexample search on the statement itself
# ---------------------------------------------------------------------------
def run_D():
    log("\n--- D  counterexample search on the hardness family ---")
    rng = random.Random(SEED)
    structured = []
    worst = {"min_positive_DR_margin": None, "params": None}

    def absorb(info, params):
        m = info.get("min_positive_DR_margin")
        if m in (None, "None"):
            return
        mv = Fr(m)
        if worst["min_positive_DR_margin"] is None or mv < Fr(worst["min_positive_DR_margin"]):
            worst["min_positive_DR_margin"] = m
            worst["params"] = params

    # ---- structured family 1: tau = 1, the U_K case -----------------------
    n_ok = 0
    n_all = 0
    for Kv in range(3, 9):
        for ev in (Fr(6, 5), Fr(3, 2), Fr(2), Fr(3)):
            nv = Kv + 4
            splits = [(Fr(1), ev), (ev, Fr(1))]
            ok, info = check_config(Kv, 1, ev, nv, "tau=1", splits)
            n_all += 1
            n_ok += ok
            if ok and H_closed(Kv, 1, ev) != U_closed(Kv, ev):
                fail("D-struct-tau1", {"K": Kv, "eta": str(ev)},
                     "H_{K,1} = U_K on the realized family", {})
                ok = False
            absorb(info, {"K": Kv, "tau": 1, "eta": str(ev), "n": nv})
    structured.append({"case": "tau = 1 (the U_K case)", "configs": n_all,
                       "passed": n_ok,
                       "outcome": "PASS" if n_ok == n_all else "FAILED"})
    log(f"  structured tau=1            : {n_ok}/{n_all} PASS")

    # ---- structured family 2: eta exactly at the boundary, thetabar = 1 ----
    n_ok = n_all = 0
    skipped_eta_one = 0
    for Kv in range(3, 9):
        for tv in range(1, Kv):
            ev = Fr(Kv - 1, Kv - tv)
            if ev <= 1:
                # tau = 1 puts the boundary exactly at eta = 1, which the
                # statement excludes (it requires eta > 1).  Recorded, skipped.
                skipped_eta_one += 1
                continue
            nv = Kv + 4
            th = thetabar(Kv, tv, ev)
            ok, info = check_config(Kv, tv, ev, nv, "eta=boundary",
                                    [(Fr(1), ev)])
            n_all += 1
            n_ok += ok
            if th != 1:
                fail("D-struct-boundary", {"K": Kv, "tau": tv, "eta": str(ev)},
                     "eta = (K-1)/(K-tau) implies thetabar = 1",
                     {"thetabar": str(th)})
                n_ok -= 1
            absorb(info, {"K": Kv, "tau": tv, "eta": str(ev), "n": nv})
    structured.append({"case": "eta at the boundary (K-1)/(K-tau), thetabar = 1",
                       "configs": n_all, "passed": n_ok,
                       "skipped_eta_equals_one": skipped_eta_one,
                       "outcome": "PASS" if n_ok == n_all else "FAILED"})
    log(f"  structured eta = boundary   : {n_ok}/{n_all} PASS "
        f"({skipped_eta_one} tau=1 cells skipped, their boundary is eta = 1 "
        "which the statement excludes)")

    # ---- structured family 3: K = tau + 1 ---------------------------------
    n_ok = n_all = 0
    for Kv in range(3, 9):
        tv = Kv - 1
        for extra in (Fr(0), Fr(1, 4), Fr(1), Fr(5, 2)):
            ev = Fr(Kv - 1, 1) + extra
            nv = Kv + 4
            ok, info = check_config(Kv, tv, ev, nv, "K=tau+1",
                                    [(Fr(1), ev), (ev, Fr(1))])
            n_all += 1
            n_ok += ok
            absorb(info, {"K": Kv, "tau": tv, "eta": str(ev), "n": nv})
    structured.append({"case": "K = tau + 1 (so K - tau = 1, eta >= K-1)",
                       "configs": n_all, "passed": n_ok,
                       "outcome": "PASS" if n_ok == n_all else "FAILED"})
    log(f"  structured K = tau + 1      : {n_ok}/{n_all} PASS")

    # ---- structured family 4: the K=3, eta=3/2 running example ------------
    ok_run, info_run = check_config(3, 1, Fr(3, 2), 9, "running-example",
                                    [(Fr(1), Fr(3, 2)), (Fr(3, 2), Fr(1)),
                                     (Fr(5, 4), Fr(6, 5))])
    structured.append({"case": "running example K = 3, tau = 1, eta = 3/2",
                       "configs": 1, "passed": int(ok_run),
                       "outcome": "PASS" if ok_run else "FAILED"})
    log(f"  structured running example  : {int(ok_run)}/1 PASS")

    # ---- structured family 5: n independence of the edge table ------------
    n_ok = n_all = 0
    for Kv in (3, 5, 7):
        for tv in (1, 2):
            if tv >= Kv:
                continue
            ev = Fr(5, 2)
            if ev < Fr(Kv - 1, Kv - tv):
                continue
            th = thetabar(Kv, tv, ev)
            sets = []
            for nv in (Kv + 2, Kv + 9, Kv + 15):
                fam = Family(Kv, tv, th, nv - Kv)
                rs = set()
                for x, y in fam.grid():
                    for dx, dy in ((1, 0), (0, 1)):
                        X, Y = x + dx, y + dy
                        if X > fam.xmax or Y > Kv:
                            continue
                        dF = fam.Fbar(X, Y) - fam.Fbar(x, y)
                        if dF != 0:
                            rs.add((fam.G(X, Y) - fam.G(x, y)) / dF)
                sets.append(rs)
            n_all += 1
            if sets[0] == sets[1] == sets[2]:
                n_ok += 1
            else:
                fail("D-struct-n", {"K": Kv, "tau": tv, "eta": str(ev)},
                     "the edge ratio table is the same for every n > K",
                     {"sizes": [len(s) for s in sets]})
    structured.append({"case": "edge table independent of n (three n each)",
                       "configs": n_all, "passed": n_ok,
                       "outcome": "PASS" if n_ok == n_all else "FAILED"})
    log(f"  structured n independence   : {n_ok}/{n_all} PASS")

    # ---- structured family 6: set-level power-set enumeration -------------
    n_ok = n_all = 0
    setlevel = []
    for Kv, tv, ev, nv in [(3, 1, Fr(3, 2), 10), (3, 2, Fr(2), 10),
                           (4, 1, Fr(2), 11), (4, 2, Fr(3), 11),
                           (4, 3, Fr(3), 11), (5, 2, Fr(3, 2), 12),
                           (5, 4, Fr(4), 12), (3, 1, Fr(6, 5), 12)]:
        good, witness = setlevel_check(Kv, tv, ev, nv)
        n_all += 1
        n_ok += good
        setlevel.append({"K": Kv, "tau": tv, "eta": str(ev), "n": nv,
                         "subsets": 2 ** nv, "ok": good, "witness": witness})
        if not good:
            fail("D-setlevel", {"K": Kv, "tau": tv, "eta": str(ev), "n": nv},
                 "f = F_O monotone submodular on the full power set", witness)
    structured.append({"case": "full power-set monotone+submodular enumeration",
                       "configs": n_all, "passed": n_ok,
                       "outcome": "PASS" if n_ok == n_all else "FAILED"})
    log(f"  structured set-level 2^n    : {n_ok}/{n_all} PASS "
        f"({sum(s['subsets'] for s in setlevel)} subsets total)")

    # ---- random configurations --------------------------------------------
    target = 2000
    rand_ok = 0
    rand_all = 0
    seen = set()
    denoms = (1, 2, 3, 4, 5, 6, 8, 10, 12, 16)
    while rand_all < target:
        Kv = rng.randint(3, 8)
        tv = rng.randint(1, Kv - 1)
        lower = Fr(Kv - 1, Kv - tv)
        q = rng.choice(denoms)
        p = rng.randint(0, 48)
        ev = lower + Fr(p, q)
        if ev <= 1:
            ev = lower + Fr(1, q)
        nv = Kv + rng.randint(2, 7)
        key = (Kv, tv, ev, nv)
        if key in seen:
            continue
        seen.add(key)
        # a random admissible split of the error, exact
        sp_num = rng.randint(1, 8)
        eu = Fr(sp_num, 1) if Fr(sp_num) <= ev else Fr(1)
        splits = [(eu, ev / eu)]
        ok, info = check_config(Kv, tv, ev, nv, "random", splits)
        rand_all += 1
        rand_ok += ok
        absorb(info, {"K": Kv, "tau": tv, "eta": str(ev), "n": nv})
    COUNTS["D_random"] = rand_all
    COUNTS["D_random_passed"] = rand_ok
    COUNTS["D_random_distinct"] = len(seen)
    log(f"  random configurations       : {rand_ok}/{rand_all} PASS "
        f"({len(seen)} distinct (K,tau,eta,n))")

    all_ok = (rand_ok == rand_all and all(s["outcome"] == "PASS" for s in structured)
              and not VIOLATIONS)
    record("D counterexample search on the family", all_ok, "VERIFIED-EXHAUSTIVE",
           f"{rand_all} random + "
           f"{sum(s['configs'] for s in structured)} structured configurations, "
           f"{len(VIOLATIONS)} violations")
    return all_ok, structured, setlevel, worst, rand_all, rand_ok


# ---------------------------------------------------------------------------
def main():
    log("V11 oracle for thm:hardness (ledger T10, paper Theorem 3)")
    log(f"seed={SEED}  root={ROOT}")
    log(f"python={sys.version.split()[0]}  sympy={sp.__version__}")

    ok = True
    ok &= run_C1()
    ok &= run_C2()
    ok &= run_C3()
    c4ok, rows, nonbinding = run_C4()
    ok &= c4ok
    c5ok, notes = run_C5(rows)
    ok &= c5ok
    ok &= run_C6()
    c7ok, conv = run_C7()
    ok &= c7ok
    ok &= run_C8()
    dok, structured, setlevel, worst, rand_all, rand_ok = run_D()
    ok &= dok

    # --- the running example, exact ---------------------------------------
    Kr, tr, er = 3, 1, Fr(3, 2)
    thr = thetabar(Kr, tr, er)
    famr = Family(Kr, tr, thr, 6)
    run_ex = {
        "K": Kr, "tau": tr, "eta": str(er), "thetabar": str(thr),
        "a": str(famr.a), "A": str(famr.A), "B": str(famr.B),
        "theta_A_B": str(thr * famr.A * famr.B),
        "eta_o_squared": str(thr * famr.A * famr.A),
        "eta_u_squared": str(thr * famr.B * famr.B),
        "H": str(H_closed(Kr, tr, er)), "H_float": float(H_closed(Kr, tr, er)),
        "inv_eta": str(1 / er), "inv_eta_float": float(1 / er),
        "U_K": str(U_closed(Kr, er)),
        "binding": H_closed(Kr, tr, er) <= 1 / er,
        "value_ratio_balanced": str(famr.Fbar(Kr, 0) / famr.Fbar(0, Kr)),
    }
    log("\n--- running example K = 3, tau = 1, eta = 3/2 ---")
    log(f"  thetabar = {run_ex['thetabar']}, a = {run_ex['a']}, "
        f"A = {run_ex['A']}, B = {run_ex['B']}, theta*A*B = {run_ex['theta_A_B']}")
    log(f"  H = {run_ex['H']} ({run_ex['H_float']:.6f}) = U_3(3/2), "
        f"1/eta = {run_ex['inv_eta']} ({run_ex['inv_eta_float']:.6f}), "
        f"binding = {run_ex['binding']}")

    elapsed = round(time.time() - T0, 2)
    summary = {
        "theorem": "thm:hardness (ledger T10, paper Theorem 3)",
        "statement_file": "results/V11/inputs/statement_hardness.md",
        "route_one_material": ["paper/sections/appendix_proofs.tex app:hardness",
                               "THEOREM_LEDGER.md section T10"],
        "seed": SEED, "elapsed_seconds": elapsed,
        "all_passed": bool(ok),
        "checks": CHECKS,
        "counts": COUNTS,
        "violations": VIOLATIONS,
        "reruns": SUBPROCS,
        "C4_table": rows,
        "C4_nonbinding_cells": nonbinding,
        "C5_notes": notes,
        "C7_convergence": conv,
        "D_structured": structured,
        "D_setlevel": setlevel,
        "D_random_count": rand_all,
        "D_random_passed": rand_ok,
        "D_worst": worst,
        "running_example": run_ex,
    }
    with open(os.path.join(HERE, "hardness.json"), "w") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)

    log("")
    log(f"checks: {len(CHECKS)}   FAILED: {sum(1 for c in CHECKS if c['status'] == 'FAILED')}"
        f"   violations: {len(VIOLATIONS)}   elapsed: {elapsed}s")
    log("ALL PASS" if ok else "SOME CHECKS FAILED")
    with open(os.path.join(HERE, "hardness.log"), "w") as fh:
        fh.write("\n".join(LOG_LINES) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""V11 Q4 oracle for thm:exact (ledger T6, Theorem 1 of the paper: rho_K = min_j V_j).

Statement under test (results/V11/inputs/statement_exact.md):

    For every K >= 2 and eta >= 1, under adversarial tie breaking,
        rho_K(eta) = min_{0 <= j <= K-1} V_j(eta),
    the minimum being attained by V_j on the segment eta in [K-j, K-j+1]
    (with V_0 = 1/eta on [K, oo)), so the breakpoints are the integers
    2, ..., K.  In particular rho_K(eta) = 1/eta exactly when eta >= K, and
    for K in {2,3,4} the closed forms are

        rho_2 = min{1/eta, 3/(2(eta+1))},
        rho_3 = (16 eta + 3)/(3(2 eta + 1)^2), 7/(3(2 eta + 1)), 1/eta
                on [1,2], [2,3], [3,oo),
        rho_4 = (135 eta^2 + 36 eta + 4)/(4(3 eta + 1)^3),
                (21 eta + 2)/(2(3 eta + 1)^2), 13/(4(3 eta + 1)), 1/eta
                on [1,2], [2,3], [3,4], [4,oo).

    Notation: k1 = (K-1) eta + 1,  q = (K-1) eta / k1,
              V_j = 1 - q^j (1 - (K-j)/(K eta)).

Route-one proof material (read, not reused as an oracle):
    paper/sections/appendix_proofs.tex, subsection app:exact (~line 582), whose
    ">=" direction runs the dual multipliers of results/N1_dual_certificate.md
    and whose "<=" direction runs the attaining instances of
    results/N2_instances.md; subsection app:validity (~line 2149) for the four
    families of valid inequalities behind the reduced LP.
    Scripts: results/N1_dual_certificate.py, results/N2_check.py,
    code/reduced_lp.py, results/T3_duals.py.  Ledger card: THEOREM_LEDGER.md T6.

Criterion C (oracle).  The independent route is an exact rational solver of my
own on the LP of code/reduced_lp.py.  The LP rows are transcribed from that file
(same variable order, same row order, no reduction, no symmetry argument); the
solver never sees V_j.

  C0  sympy on the closed form: V_0 = 1/eta, the recursion between consecutive
      V_j, V_j = min_i V_i on the segment [K-j, K-j+1] for K = 2..8 and every i
      (exact real-root isolation of the numerator on the segment, so the
      breakpoints are the integers 2..K), and rho_K = 1/eta exactly when
      eta >= K.                                              [VERIFIED-SYMBOLIC]
  C1  my own exact rational two-phase simplex (fractions.Fraction, Bland
      fallback) on the full LP of code/reduced_lp.py: K = 2..6, 20 rational eta
      per K (eta = 1, every integer 2..K, eta = K, values above K, and every
      segment midpoint), 100 LPs.  Each optimum equals min_j V_j(eta) as a
      Fraction.                                                    [VERIFIED-LP]
  C2  independent exact primal-dual certificate at each of those 100 points,
      checked against the LP data alone: the returned primal x is feasible with
      c'x = min_j V_j, and the multipliers lam >= 0 satisfy A'lam + c >= 0 with
      -b'lam = c'x.  Weak duality then pins the optimum without reference to
      the solver.                                                  [VERIFIED-LP]
  C3  the K = 2, 3, 4 closed forms printed in the statement: sympy identity
      against min_j V_j on every segment, plus exact Fraction equality against
      the C1 LP optima at all 20 eta per K.       [VERIFIED-SYMBOLIC + LP]
  C4  rerun results/N1_dual_certificate.py, record exit code and key counts.
                                                             [VERIFIED-SYMBOLIC]
  C5  rerun results/N2_check.py, record exit code and key counts.
                                                             [VERIFIED-SYMBOLIC]
  C6  cross-check of the C1 optima against the float scipy/HiGHS solve of
      code/reduced_lp.reduced (reference only).            [VERIFIED-LP 浮点]
  C7  the reduction step of app:exact on random instances: the vector
      (d_t, g_{t,i}) induced by every run of D1 below satisfies the four
      constraint families of eq:redlp, so that run's ratio is at least the LP
      optimum.  Computed on the D1 runs and printed with them.
                                                          [VERIFIED-EXHAUSTIVE]

Criterion D (counterexample search on the statement itself).
  D1  2400 random exact instances: monotone submodular f (modular, coverage,
      mixtures; monotonicity and submodularity verified over the whole lattice),
      n <= 7, K in {2,3}, random legal surrogate ftilde whose actual
      (eta_u, eta_o) are the smallest legal factors, so eta = eta_u eta_o is the
      instance's actual error.  Predictive greedy is run for exactly K steps
      with every tie choice enumerated, and the worst output is scored:
      f(T)/OPT >= rho_K(eta) must hold.                   [VERIFIED-EXHAUSTIVE]
  D2  the Figure 1 instance of HANDOFF_2026-09-18.md section 7 in exact
      rationals: f monotone submodular, OPT, the actual global eta of surrogate
      A and of surrogate B, their greedy outputs and ratios, eta^sel of each,
      and both ratios against rho_2 at the respective actual eta.
                                                          [VERIFIED-EXHAUSTIVE]

Every decision uses fractions.Fraction or sympy; floats appear only in printed
text, in C6, and inside the two rerun repository scripts.  Seeds are fixed.  No
existing repository file is modified: the two rerun scripts overwrite their own
JSON artifacts, so this script saves their bytes first, copies the fresh
artifacts to results/V11/oracle/reruns/, restores the originals and verifies the
sha256.

Run:  python3 results/V11/oracle/exact.py
Exit code 0 iff every check passed.  Writes results/V11/oracle/exact.json.
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
RERUN_DIR = os.path.join(HERE, "reruns")
sys.path.insert(0, os.path.join(ROOT, "code"))

N1_SCRIPT = os.path.join(ROOT, "results", "N1_dual_certificate.py")
N1_OUTPUTS = ["results/N1_dual_certificate.json"]
N2_SCRIPT = os.path.join(ROOT, "results", "N2_check.py")
N2_OUTPUTS = ["results/N2_check.json", "results/N2_bounds.json",
              "results/N2_examples.json"]

CHECKS = []
COUNTS = {}
SUBPROCS = []
VIOLATIONS = []


def check(name, ok, detail=""):
    CHECKS.append({"name": name, "status": "PASS" if ok else "FAIL",
                   "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""),
          flush=True)
    return ok


# ---------------------------------------------------------------------------
# closed form (used only to compare against solver output, never inside it)
# ---------------------------------------------------------------------------
def V_j(K, eta, j):
    eta = Fr(eta)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q ** j * (1 - Fr(K - j) / (K * eta))


def rho_K(K, eta):
    return min(V_j(K, eta, j) for j in range(K))


def argmin_j(K, eta):
    vals = [V_j(K, eta, j) for j in range(K)]
    m = min(vals)
    return [j for j in range(K) if vals[j] == m]


# ---------------------------------------------------------------------------
# exact rational LP: rows transcribed from code/reduced_lp.py
# ---------------------------------------------------------------------------
def build_lp(K, eta):
    """min sum_t d_t  s.t. A x <= b, x >= 0, with the rows of code/reduced_lp.py.

    x = (d_0..d_{K-1}, g_{0,0}..g_{K,K-1}); for t = 0..K-1 the block is
      sum(t)    : -sum_i g_{t,i} - sum_{s<t} d_s              <= -1
      pred(t,i) : g_{t,i}/eta - d_t                           <= 0
      mono(t,i) : g_{t+1,i} - g_{t,i}                         <= 0
      cons(t,i) : g_{t,i} - d_t - (1-1/eta) g_{t+1,i}         <= 0
    """
    eta = Fr(eta)
    nd = K
    gg = lambda t, i: nd + t * K + i
    nv = nd + (K + 1) * K
    A, b, labels = [], [], []
    for t in range(K):
        row = [Fr(0)] * nv
        for i in range(K):
            row[gg(t, i)] = Fr(-1)
        for s in range(t):
            row[s] = Fr(-1)
        A.append(row); b.append(Fr(-1)); labels.append(("sum", t, None))
        for i in range(K):
            r1 = [Fr(0)] * nv
            r1[gg(t, i)] = 1 / eta
            r1[t] = Fr(-1)
            A.append(r1); b.append(Fr(0)); labels.append(("pred", t, i))
            r2 = [Fr(0)] * nv
            r2[gg(t + 1, i)] = Fr(1)
            r2[gg(t, i)] = Fr(-1)
            A.append(r2); b.append(Fr(0)); labels.append(("mono", t, i))
            r3 = [Fr(0)] * nv
            r3[gg(t, i)] = Fr(1)
            r3[t] = Fr(-1)
            r3[gg(t + 1, i)] = -(1 - 1 / eta)
            A.append(r3); b.append(Fr(0)); labels.append(("cons", t, i))
    c = [Fr(0)] * nv
    for t in range(K):
        c[t] = Fr(1)
    return A, b, c, nv, labels


def exact_simplex(A, b, c, nv, bland_after=400):
    """Exact two-phase tableau simplex for min c'x, Ax <= b, x >= 0.

    Returns (value, x, lam, iters) with lam >= 0 the multipliers of the
    inequalities: A'lam + c >= 0 and -b'lam = value certify optimality.
    """
    m = len(A)
    art_rows = [i for i in range(m) if b[i] < 0]
    na = len(art_rows)
    ncol = nv + m + na
    art_col = {i: nv + m + k for k, i in enumerate(art_rows)}
    T, basis = [], []
    for i in range(m):
        sgn = Fr(-1) if b[i] < 0 else Fr(1)
        row = [sgn * A[i][j] for j in range(nv)] + [Fr(0)] * (m + na) + [sgn * b[i]]
        row[nv + i] = sgn
        if b[i] < 0:
            row[art_col[i]] = Fr(1)
            basis.append(art_col[i])
        else:
            basis.append(nv + i)
        T.append(row)
    total_iters = [0]

    def pivot(pr, pc):
        inv = 1 / T[pr][pc]
        T[pr] = [v * inv for v in T[pr]]
        prow = T[pr]
        for r in range(m):
            if r == pr:
                continue
            f = T[r][pc]
            if f:
                Tr = T[r]
                T[r] = [Tr[j] - f * prow[j] for j in range(ncol + 1)]
        basis[pr] = pc

    def run(cost, allowed):
        it = 0
        while True:
            it += 1
            total_iters[0] += 1
            if it > 20000:
                raise RuntimeError("iteration limit")
            inbasis = set(basis)
            cB = [cost[basis[r]] for r in range(m)]
            best, bestval = None, Fr(0)
            for j in allowed:
                if j in inbasis:
                    continue
                s = cost[j]
                for r in range(m):
                    if cB[r]:
                        s -= cB[r] * T[r][j]
                if s < bestval:
                    if it > bland_after:      # Bland: first negative index
                        best = j
                        break
                    bestval, best = s, j
            if best is None:
                return
            pc = best
            pr, bestratio = None, None
            for r in range(m):
                if T[r][pc] > 0:
                    ratio = T[r][ncol] / T[r][pc]
                    if (bestratio is None or ratio < bestratio
                            or (ratio == bestratio and basis[r] < basis[pr])):
                        bestratio, pr = ratio, r
            if pr is None:
                raise RuntimeError("unbounded")
            pivot(pr, pc)

    if na:
        cost1 = [Fr(0)] * ncol
        for k in range(na):
            cost1[nv + m + k] = Fr(1)
        run(cost1, list(range(ncol)))
        if sum(cost1[basis[r]] * T[r][ncol] for r in range(m)) != 0:
            raise RuntimeError("infeasible")
        for r in range(m):
            if basis[r] >= nv + m:
                for j in range(nv + m):
                    if j not in basis and T[r][j] != 0:
                        pivot(r, j)
                        break
    cost2 = [Fr(0)] * ncol
    for j in range(nv):
        cost2[j] = c[j]
    run(cost2, list(range(nv + m)))
    x = [Fr(0)] * nv
    for r in range(m):
        if basis[r] < nv:
            x[basis[r]] = T[r][ncol]
    val = sum(c[j] * x[j] for j in range(nv))
    cB = [cost2[basis[r]] for r in range(m)]
    lam = []
    for i in range(m):
        s = Fr(0)
        for r in range(m):
            if cB[r]:
                s += cB[r] * T[r][nv + i]
        lam.append(-s)
    return val, x, lam, total_iters[0]


def certificate_ok(A, b, c, nv, x, lam, value):
    """Verify the primal-dual certificate against the LP data only."""
    m = len(A)
    for j in range(nv):
        if x[j] < 0:
            return False, "primal x_%d < 0" % j
    for i in range(m):
        s = Fr(0)
        for j in range(nv):
            if A[i][j] and x[j]:
                s += A[i][j] * x[j]
        if s > b[i]:
            return False, "primal row %d violated" % i
    if sum(c[j] * x[j] for j in range(nv)) != value:
        return False, "primal objective mismatch"
    for i in range(m):
        if lam[i] < 0:
            return False, "dual lam_%d < 0" % i
    for j in range(nv):
        s = c[j]
        for i in range(m):
            if lam[i] and A[i][j]:
                s += lam[i] * A[i][j]
        if s < 0:
            return False, "dual column %d infeasible" % j
    if -sum(b[i] * lam[i] for i in range(m)) != value:
        return False, "dual objective mismatch"
    return True, "ok"


def eta_grid(K, size=20):
    """20 rational eta: 1, every integer 2..K (so eta=K), values above K, every
    segment midpoint, padded with further in-segment rationals."""
    pts = []

    def add(x):
        x = Fr(x)
        if x not in pts:
            pts.append(x)

    add(1)
    for k in range(2, K + 1):
        add(k)
    for mseg in range(1, K):
        add(Fr(2 * mseg + 1, 2))                     # midpoint of [m, m+1]
    for x in (Fr(2 * K + 1, 2), Fr(K + 1), Fr(2 * K + 3, 2), Fr(2 * K),
              Fr(6 * K + 1, 3), Fr(3 * K)):
        add(x)                                       # values above K
    for d in (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13):
        for mseg in range(1, K):
            for num in range(1, d):
                if len(pts) >= size:
                    break
                add(mseg + Fr(num, d))
            if len(pts) >= size:
                break
        if len(pts) >= size:
            break
        for num in range(1, d):
            if len(pts) >= size:
                break
            add(K + Fr(num, d))
        if len(pts) >= size:
            break
    return sorted(pts)[:size] if len(pts) >= size else sorted(pts)


# ---------------------------------------------------------------------------
# C0: sympy on the closed form
# ---------------------------------------------------------------------------
def run_C0(kmax=8):
    e = sp.Symbol("eta", positive=True)

    def Vsym(K, j):
        k1 = (K - 1) * e + 1
        q = (K - 1) * e / k1
        return 1 - q ** j * (1 - sp.Rational(K - j) / (K * e))

    ok = True
    nid = 0
    details = []
    for K in range(2, kmax + 1):
        # V_0 = 1/eta
        nid += 1
        if sp.simplify(Vsym(K, 0) - 1 / e) != 0:
            ok = False
            details.append("K=%d V_0 != 1/eta" % K)
        # recursion V_{j+1} - V_j
        for j in range(K - 1):
            nid += 1
            k1 = (K - 1) * e + 1
            q = (K - 1) * e / k1
            lhs = Vsym(K, j + 1) - Vsym(K, j)
            rhs = q ** j * ((1 - sp.Rational(K - j) / (K * e))
                            - q * (1 - sp.Rational(K - j - 1) / (K * e)))
            if sp.simplify(lhs - rhs) != 0:
                ok = False
                details.append("K=%d recursion at j=%d" % (K, j))
    COUNTS["C0_identities"] = nid
    ok1 = check("C0a closed-form identities for V_j, K=2..%d [VERIFIED-SYMBOLIC]" % kmax,
                ok, "%d identities, residual 0" % nid
                + ("" if ok else " | " + "; ".join(details[:4])))

    # V_j = min_i V_i on [K-j, K-j+1]: exact real-root isolation of V_i - V_j
    ok2 = True
    nseg = 0
    bad = []
    for K in range(2, kmax + 1):
        for j in range(K):
            lo = sp.Rational(K - j)
            hi = sp.Rational(K - j + 1) if j >= 1 else None   # j=0: [K, oo)
            for i in range(K):
                if i == j:
                    continue
                nseg += 1
                diff = sp.together(sp.simplify(Vsym(K, i) - Vsym(K, j)))
                num, den = sp.fraction(sp.cancel(diff))
                pn = sp.Poly(sp.expand(num), e)
                pd = sp.Poly(sp.expand(den), e)
                # den > 0 for eta >= 1: K eta ((K-1) eta + 1)^max(i,j)
                if pd.eval(sp.Rational(3, 2)) <= 0 or sp.count_roots(
                        pd, sp.Rational(1), sp.Rational(10 ** 6)) != 0:
                    ok2 = False
                    bad.append("K=%d den sign i=%d j=%d" % (K, i, j))
                    continue
                # strip endpoint roots, then no interior root and positive sign
                pstr = pn
                while pstr.degree() > 0 and pstr.eval(lo) == 0:
                    pstr = sp.Poly(sp.cancel(pstr.as_expr() / (e - lo)), e)
                if hi is not None:
                    while pstr.degree() > 0 and pstr.eval(hi) == 0:
                        pstr = sp.Poly(sp.cancel(pstr.as_expr() / (hi - e)), e)
                    mid = (lo + hi) / 2
                    nr = 0 if pstr.degree() == 0 else sp.count_roots(pstr, lo, hi)
                else:
                    mid = lo + 1
                    nr = 0 if pstr.degree() == 0 else sp.count_roots(
                        pstr, lo, sp.Rational(10 ** 6))
                    if pstr.degree() > 0 and pstr.LC() < 0:
                        nr = -1          # not nonnegative far out
                if nr != 0 or pstr.eval(mid) < 0:
                    ok2 = False
                    bad.append("K=%d i=%d j=%d roots=%s sign=%s"
                               % (K, i, j, nr, pstr.eval(mid)))
    COUNTS["C0_segment_comparisons"] = nseg
    ok2 = check("C0b V_j = min_i V_i on segment [K-j,K-j+1], K=2..%d, exact root "
                "isolation [VERIFIED-SYMBOLIC]" % kmax, ok2,
                "%d ordered pairs (i,j) over all segments, no interior root, "
                "breakpoints are the integers 2..K" % nseg
                + ("" if ok2 else " | " + "; ".join(bad[:4])))

    # rho_K = 1/eta exactly when eta >= K
    ok3 = True
    bad3 = []
    npts = 0
    for K in range(2, kmax + 1):
        for x in [Fr(1), Fr(K, 1) - Fr(1, 100), Fr(K, 1) - Fr(1, 2),
                  Fr(K), Fr(K) + Fr(1, 100), Fr(2 * K), Fr(10 * K)]:
            if x < 1:
                continue
            npts += 1
            r = rho_K(K, x)
            if x >= K:
                if r != 1 / Fr(x):
                    ok3 = False
                    bad3.append("K=%d eta=%s rho=%s != 1/eta" % (K, x, r))
            else:
                if r >= 1 / Fr(x):
                    ok3 = False
                    bad3.append("K=%d eta=%s rho=%s >= 1/eta" % (K, x, r))
    COUNTS["C0_eta_ge_K_points"] = npts
    ok3 = check("C0c rho_K = 1/eta exactly when eta >= K, K=2..%d [VERIFIED-SYMBOLIC]"
                % kmax, ok3, "%d exact points, strict inequality below K" % npts
                + ("" if ok3 else " | " + "; ".join(bad3[:4])))
    return ok1 and ok2 and ok3


# ---------------------------------------------------------------------------
# C1 / C2 / C3 / C6: the exact LP
# ---------------------------------------------------------------------------
def closed_form_pieces(K):
    """The closed forms printed in the statement, as (lo, hi, expr) in sympy."""
    e = sp.Symbol("eta", positive=True)
    if K == 2:
        return [(1, 2, sp.Rational(3, 2) / (e + 1)), (2, None, 1 / e)]
    if K == 3:
        return [(1, 2, (16 * e + 3) / (3 * (2 * e + 1) ** 2)),
                (2, 3, sp.Rational(7, 3) / (2 * e + 1)),
                (3, None, 1 / e)]
    if K == 4:
        return [(1, 2, (135 * e ** 2 + 36 * e + 4) / (4 * (3 * e + 1) ** 3)),
                (2, 3, (21 * e + 2) / (2 * (3 * e + 1) ** 2)),
                (3, 4, sp.Rational(13, 4) / (3 * e + 1)),
                (4, None, 1 / e)]
    raise ValueError(K)


def closed_form_value(K, eta):
    e = sp.Symbol("eta", positive=True)
    eta = Fr(eta)
    for lo, hi, expr in closed_form_pieces(K):
        if eta >= lo and (hi is None or eta <= hi):
            v = sp.Rational(expr.subs(
                e, sp.Rational(eta.numerator, eta.denominator)))
            return Fr(int(v.p), int(v.q))
    raise ValueError((K, eta))


def run_C1_C2_C3_C6(kmax=6):
    from reduced_lp import reduced          # float reference (scipy / HiGHS)
    rows = []
    ok1 = ok2 = ok6 = True
    bad1, bad2, bad6 = [], [], []
    n_lp = 0
    worst_float = 0.0
    running = None
    for K in range(2, kmax + 1):
        for eta in eta_grid(K):
            n_lp += 1
            A, b, c, nv, labels = build_lp(K, eta)
            val, x, lam, iters = exact_simplex(A, b, c, nv)
            target = rho_K(K, eta)
            if val != target:
                ok1 = False
                bad1.append("K=%d eta=%s LP=%s min_j V_j=%s" % (K, eta, val, target))
                VIOLATIONS.append({"check": "C1", "K": K, "eta": str(eta),
                                   "lp": str(val), "min_j_V_j": str(target)})
            cok, cmsg = certificate_ok(A, b, c, nv, x, lam, val)
            if not cok:
                ok2 = False
                bad2.append("K=%d eta=%s %s" % (K, eta, cmsg))
                VIOLATIONS.append({"check": "C2", "K": K, "eta": str(eta),
                                   "reason": cmsg})
            fv = reduced(K, float(eta))
            d = abs(float(val) - float(fv))
            worst_float = max(worst_float, d)
            if d > 1e-7:
                ok6 = False
                bad6.append("K=%d eta=%s exact=%s float=%s" % (K, eta, val, fv))
            rows.append({"K": K, "eta": str(eta), "lp_exact": str(val),
                         "min_j_V_j": str(target), "argmin_j": argmin_j(K, eta),
                         "equal": val == target, "certificate": cok,
                         "simplex_iterations": iters,
                         "float_scipy": float(fv), "float_abs_diff": d})
            if K == 3 and eta == Fr(3, 2):
                running = {"K": 3, "eta": "3/2",
                           "V": [str(V_j(3, Fr(3, 2), j)) for j in range(3)],
                           "argmin_j": argmin_j(3, Fr(3, 2)),
                           "lp_exact": str(val),
                           "rho": str(target), "rho_float": float(target),
                           "closed_form": str(closed_form_value(3, Fr(3, 2))),
                           "k1": "4", "q": "3/4"}
    COUNTS["C1_LPs"] = n_lp
    COUNTS["C1_eta_points_per_K"] = 20
    ok1 = check("C1 exact rational simplex on the LP of code/reduced_lp.py equals "
                "min_j V_j [VERIFIED-LP]", ok1,
                "%d LPs (K=2..%d x 20 rational eta), Fraction equality on every one"
                % (n_lp, kmax) + ("" if ok1 else " | " + "; ".join(bad1[:4])))
    ok2 = check("C2 exact primal-dual certificate at every optimum [VERIFIED-LP]",
                ok2, "%d certificates: primal feasible with c'x = min_j V_j, "
                     "lam >= 0 with A'lam + c >= 0 and -b'lam = c'x" % n_lp
                + ("" if ok2 else " | " + "; ".join(bad2[:4])))
    ok6 = check("C6 cross-check against float scipy code/reduced_lp.reduced "
                "[VERIFIED-LP 浮点]", ok6,
                "%d points, worst |exact - float| = %.2e" % (n_lp, worst_float)
                + ("" if ok6 else " | " + "; ".join(bad6[:4])))

    # C3: the printed closed forms
    e = sp.Symbol("eta", positive=True)
    ok3 = True
    bad3 = []
    nsym = 0
    for K in (2, 3, 4):
        for lo, hi, expr in closed_form_pieces(K):
            j = K - lo                       # segment [K-j, K-j+1] -> j = K - lo
            nsym += 1
            k1 = (K - 1) * e + 1
            q = (K - 1) * e / k1
            Vs = 1 - q ** j * (1 - sp.Rational(K - j) / (K * e))
            if sp.simplify(Vs - expr) != 0:
                ok3 = False
                bad3.append("K=%d segment [%s,%s] closed form != V_%d" % (K, lo, hi, j))
    nnum = 0
    for K in (2, 3, 4):
        for eta in eta_grid(K):
            nnum += 1
            lp = [r for r in rows if r["K"] == K and r["eta"] == str(eta)][0]
            if Fr(lp["lp_exact"]) != closed_form_value(K, eta):
                ok3 = False
                bad3.append("K=%d eta=%s LP=%s closed=%s"
                            % (K, eta, lp["lp_exact"], closed_form_value(K, eta)))
                VIOLATIONS.append({"check": "C3", "K": K, "eta": str(eta)})
    COUNTS["C3_symbolic_segments"] = nsym
    COUNTS["C3_numeric_points"] = nnum
    ok3 = check("C3 printed closed forms for K=2,3,4 [VERIFIED-SYMBOLIC + LP]", ok3,
                "%d segment identities (sympy residual 0) and %d exact LP values"
                % (nsym, nnum) + ("" if ok3 else " | " + "; ".join(bad3[:4])))
    return (ok1 and ok2 and ok3 and ok6), rows, running


# ---------------------------------------------------------------------------
# C4 / C5: reruns of the repository scripts
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
                          capture_output=True, text=True, timeout=3600)
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
           "stdout_tail": proc.stdout.strip().splitlines()[-4:],
           "outputs_before_sha256": {k: v[0] for k, v in saved.items()},
           "outputs_after_rerun_sha256": fresh,
           "outputs_restored_bytewise": restored,
           "copy_dir": os.path.relpath(RERUN_DIR, ROOT)}
    SUBPROCS.append(rec)
    return proc, rec


def run_C4():
    proc, rec = rerun("N1_dual_certificate", N1_SCRIPT, N1_OUTPUTS)
    txt = proc.stdout
    line = [l for l in txt.splitlines() if "checks passed" in l]
    npass = nfail = None
    try:
        blob = json.load(open(os.path.join(RERUN_DIR, "N1_dual_certificate.json")))
        npass, ntot = blob["n_pass"], blob["n_checks"]
        nfail = ntot - npass
    except Exception:
        ntot = None
    rec["key_counts"] = {"summary_line": line, "n_pass": npass, "n_checks": ntot}
    COUNTS["C4_N1_checks_pass"] = npass
    ok = (proc.returncode == 0 and "OVERALL: PASS" in txt
          and all(rec["outputs_restored_bytewise"].values()))
    return check("C4 rerun results/N1_dual_certificate.py [VERIFIED-SYMBOLIC]", ok,
                 "exit code %d, %s, OVERALL: PASS, %.1fs, artifacts restored "
                 "byte-identical" % (proc.returncode,
                                     (line or ["no summary line"])[0].strip(), rec["seconds"]))


def run_C5():
    proc, rec = rerun("N2_check", N2_SCRIPT, N2_OUTPUTS)
    txt = proc.stdout
    line = [l for l in txt.splitlines() if l.startswith("TOTAL ")]
    npass = ntot = None
    if line:
        try:
            frag = line[0].split()[1]
            npass, ntot = (int(v) for v in frag.split("/"))
        except Exception:
            pass
    rec["key_counts"] = {"total_line": line, "n_pass": npass, "n_checks": ntot,
                         "part_lines": [l for l in txt.splitlines()
                                        if ": " in l and "PASS" in l and l.startswith("  ")]}
    COUNTS["C5_N2_checks_pass"] = npass
    ok = (proc.returncode == 0 and npass is not None and npass == ntot
          and all(rec["outputs_restored_bytewise"].values()))
    return check("C5 rerun results/N2_check.py [VERIFIED-SYMBOLIC]", ok,
                 "exit code %d, %s, %.1fs, artifacts restored byte-identical"
                 % (proc.returncode, (line or ["no TOTAL line"])[0].strip(), rec["seconds"]))


# ---------------------------------------------------------------------------
# Criterion D: random and structured instances
# ---------------------------------------------------------------------------
def lattice_modular(rng, n):
    w = [Fr(rng.randint(1, 24), rng.choice([1, 2, 3, 4])) for _ in range(n)]
    f = [Fr(0)] * (1 << n)
    for S in range(1 << n):
        f[S] = sum(w[i] for i in range(n) if S >> i & 1)
    return f


def lattice_coverage(rng, n):
    u = rng.randint(2, 7)
    wt = [Fr(rng.randint(1, 12), rng.choice([1, 2])) for _ in range(u)]
    cov = []
    for _ in range(n):
        msk = 0
        for j in range(u):
            if rng.random() < 0.5:
                msk |= 1 << j
        if msk == 0:
            msk = 1 << rng.randrange(u)
        cov.append(msk)
    f = [Fr(0)] * (1 << n)
    for S in range(1 << n):
        un = 0
        for i in range(n):
            if S >> i & 1:
                un |= cov[i]
        f[S] = sum(wt[j] for j in range(u) if un >> j & 1)
    return f


def lattice_random(rng, n):
    fam = rng.choice(["modular", "coverage", "mix", "twocov"])
    if fam == "modular":
        return lattice_modular(rng, n), fam
    if fam == "coverage":
        return lattice_coverage(rng, n), fam
    if fam == "mix":
        a = lattice_coverage(rng, n)
        b = lattice_modular(rng, n)
        ca = Fr(rng.randint(1, 4)); cb = Fr(rng.randint(1, 4), rng.choice([1, 2]))
        return [ca * a[S] + cb * b[S] for S in range(1 << n)], fam
    a = lattice_coverage(rng, n)
    b = lattice_coverage(rng, n)
    return [a[S] + b[S] for S in range(1 << n)], fam


def is_monotone_submodular(f, n):
    for S in range(1 << n):
        for a in range(n):
            if S >> a & 1:
                continue
            if f[S | (1 << a)] < f[S]:
                return False
            for b_ in range(a + 1, n):
                if S >> b_ & 1:
                    continue
                if f[S | (1 << a)] + f[S | (1 << b_)] < f[S | (1 << a) | (1 << b_)] + f[S]:
                    return False
    return True


def realized_factors(f, ft, n):
    """Smallest legal (eta_u, eta_o); None when ftilde is not legal."""
    eu = Fr(0); eo = Fr(0); seen = False
    for S in range(1 << n):
        for e_ in range(n):
            if S >> e_ & 1:
                continue
            d = f[S | (1 << e_)] - f[S]
            dt = ft[S | (1 << e_)] - ft[S]
            if d == 0:
                if dt != 0:
                    return None
                continue
            if dt <= 0:
                return None
            seen = True
            eu = max(eu, d / dt)
            eo = max(eo, dt / d)
    if not seen:
        return None
    return eu, eo


def greedy_all_ties(f, ft, n, K):
    """Every adversarial-tie run of predictive greedy, K steps.  Returns the list
    of (final set, f value) and the worst f value."""
    finals = []
    stack = [(0, 0)]
    while stack:
        S, t = stack.pop()
        if t == K:
            finals.append((S, f[S]))
            continue
        best = None
        cands = []
        for e_ in range(n):
            if S >> e_ & 1:
                continue
            d = ft[S | (1 << e_)] - ft[S]
            if best is None or d > best:
                best = d
                cands = [e_]
            elif d == best:
                cands.append(e_)
        for e_ in cands:
            stack.append((S | (1 << e_), t + 1))
    worst = min(v for _, v in finals)
    return finals, worst


def greedy_all_paths(ft, n, K):
    """Every adversarial-tie run, as ordered element lists."""
    paths = []
    stack = [(0, [])]
    while stack:
        S, path = stack.pop()
        if len(path) == K:
            paths.append(path)
            continue
        best = None
        cands = []
        for e_ in range(n):
            if S >> e_ & 1:
                continue
            d = ft[S | (1 << e_)] - ft[S]
            if best is None or d > best:
                best = d
                cands = [e_]
            elif d == best:
                cands.append(e_)
        for e_ in cands:
            stack.append((S | (1 << e_), path + [e_]))
    return paths


def lp_vector_of_run(f, n, K, path, Ostar, OPT):
    """The reduced-LP vector induced by one run: d_t and g_{t,i}, normalized by
    OPT (so f(O*) = 1), exactly as in app:exact."""
    d = []
    g = [[Fr(0)] * K for _ in range(K + 1)]
    S = 0
    states = []
    for t in range(K):
        states.append(S)
        S |= 1 << path[t]
    states.append(S)
    for t in range(K):
        St = states[t]
        d.append((f[St | (1 << path[t])] - f[St]) / OPT)
    for t in range(K + 1):
        St = states[t]
        for i, o in enumerate(Ostar):
            if St >> o & 1:
                g[t][i] = Fr(0)
            else:
                g[t][i] = (f[St | (1 << o)] - f[St]) / OPT
    return d, g


def validity_of_run(d, g, K, eta):
    """The four families of eq:redlp.  Returns (ok, worst_slack, first_failure)."""
    worst = None
    for t in range(K):
        slacks = [(sum(g[t]) + sum(d[s] for s in range(t)) - 1, "sum(%d)" % t)]
        for i in range(K):
            slacks.append((d[t] - g[t][i] / eta, "pred(%d,%d)" % (t, i)))
            slacks.append((g[t][i] - g[t + 1][i], "mono(%d,%d)" % (t, i)))
            slacks.append(((1 - 1 / eta) * g[t + 1][i] - g[t][i] + d[t],
                           "cons(%d,%d)" % (t, i)))
        for s, nm in slacks:
            if worst is None or s < worst[0]:
                worst = (s, nm)
            if s < 0:
                return False, s, nm
    return True, worst[0], worst[1]


def eta_sel_of_run(f, n, path):
    """max{1, a_0, ..., a_{K-1}} with a_t = M_t/g_t on the true gains."""
    S = 0
    a = [Fr(1)]
    for e_ in path:
        M = max(f[S | (1 << x)] - f[S] for x in range(n) if not S >> x & 1)
        g = f[S | (1 << e_)] - f[S]
        if g == 0:
            if M == 0:
                a.append(Fr(1))
            else:
                return None            # infinite
        else:
            a.append(M / g)
        S |= 1 << e_
    return max(a)


def run_D1(target=2400):
    rng = random.Random(20260918)
    n_inst = 0
    n_runs = 0
    n_rejected = 0
    n_trivial = 0
    worst = None
    worst_small = None
    viol = []
    per_K = {2: 0, 3: 0}
    n_valid_checks = 0
    n_valid_fail = 0
    valid_bad = []
    valid_worst = None
    eta_max = Fr(1)
    eq_runs = 0
    while n_inst < target:
        K = 2 if n_inst % 2 == 0 else 3
        n = rng.randint(max(K, 3), 7)
        f, fam = lattice_random(rng, n)
        if f[(1 << n) - 1] == 0 or not is_monotone_submodular(f, n):
            n_rejected += 1
            continue
        mode = rng.choice(["scale", "perturb", "perturb", "indep"])
        if mode == "scale":
            cst = Fr(rng.randint(1, 9), rng.choice([1, 2, 3]))
            ft = [cst * v for v in f]
        elif mode == "perturb":
            dmax = rng.choice([4, 6, 10, 20])
            ft = [v * (1 + Fr(rng.randint(-dmax // 2, dmax), 4 * dmax)) for v in f]
            ft[0] = Fr(0)
        else:
            g, _ = lattice_random(rng, n)
            ft = g
            ft[0] = Fr(0)
        fac = realized_factors(f, ft, n)
        if fac is None:
            n_rejected += 1
            continue
        eu, eo = fac
        eta = eu * eo
        if eta < 1:
            n_rejected += 1
            continue
        OPT = max(f[S] for S in range(1 << n) if bin(S).count("1") <= K)
        if OPT == 0:
            n_trivial += 1
            n_inst += 1
            continue
        finals, wv = greedy_all_ties(f, ft, n, K)
        n_runs += len(finals)
        # C7: the induced vector of every run satisfies the four LP families
        Ostar = max((S for S in range(1 << n) if bin(S).count("1") == K),
                    key=lambda S: f[S])
        Olist = [i for i in range(n) if Ostar >> i & 1]
        for p in greedy_all_paths(ft, n, K):
            dv, gv = lp_vector_of_run(f, n, K, p, Olist, OPT)
            vok, vslack, vname = validity_of_run(dv, gv, K, eta)
            n_valid_checks += K * (1 + 3 * K)
            if not vok:
                n_valid_fail += 1
                if len(valid_bad) < 5:
                    valid_bad.append({"K": K, "n": n, "family": fam,
                                      "eta": str(eta), "constraint": vname,
                                      "slack": str(vslack)})
            elif valid_worst is None or vslack < valid_worst[0]:
                valid_worst = (vslack, {"K": K, "n": n, "eta": str(eta),
                                        "constraint": vname})
        ratio = wv / OPT
        bound = rho_K(K, eta)
        slack = ratio - bound
        if slack == 0:
            eq_runs += 1
        if slack < 0:
            viol.append({"K": K, "n": n, "family": fam, "mode": mode,
                         "eta": str(eta), "ratio": str(ratio),
                         "rho": str(bound), "slack": str(slack),
                         "f": [str(v) for v in f], "ftilde": [str(v) for v in ft]})
        where = {"K": K, "n": n, "family": fam, "mode": mode,
                 "eta": str(eta), "eta_float": float(eta),
                 "ratio": str(ratio), "ratio_float": float(ratio),
                 "rho": str(bound), "rho_float": float(bound), "tag": "D1"}
        if worst is None or slack < worst[0]:
            worst = (slack, where)
        if eta <= 2 and (worst_small is None or slack < worst_small[0]):
            worst_small = (slack, where)
        eta_max = max(eta_max, eta)
        per_K[K] += 1
        n_inst += 1
    COUNTS["C7_validity_constraint_checks"] = n_valid_checks
    COUNTS["C7_validity_failed_runs"] = n_valid_fail
    VIOLATIONS.extend([dict(v, check="C7") for v in valid_bad])
    ok_valid = check(
          "C7 the vector induced by every run satisfies the four LP families of "
          "eq:redlp [VERIFIED-EXHAUSTIVE]", n_valid_fail == 0,
          "%d constraint checks over the %d runs of D1, worst slack %s at %s; "
          "this is the reduction step rho_K >= LP optimum, on random instances"
          % (n_valid_checks, n_runs, valid_worst[0] if valid_worst else "n/a",
             valid_worst[1]["constraint"] if valid_worst else "n/a")
          + ("" if n_valid_fail == 0 else " | %d runs violate" % n_valid_fail))
    COUNTS["D1_random_instances"] = n_inst
    COUNTS["D1_instances_K2"] = per_K[2]
    COUNTS["D1_instances_K3"] = per_K[3]
    COUNTS["D1_greedy_runs"] = n_runs
    COUNTS["D1_rejected_draws"] = n_rejected
    COUNTS["D1_trivial_OPT_zero"] = n_trivial
    COUNTS["D1_equality_instances"] = eq_runs
    VIOLATIONS.extend([dict(v, check="D1") for v in viol])
    ok = not viol
    check("D1 %d random exact instances: f(T)/OPT >= rho_K(actual eta) "
          "[VERIFIED-EXHAUSTIVE]" % n_inst, ok,
          "K in {2,3}, n <= 7, %d tie-enumerated runs, %d draws rejected, "
          "max actual eta %.3f, worst slack %s"
          % (n_runs, n_rejected, float(eta_max), worst[0])
          + ("" if ok else " | %d violations" % len(viol)))
    return ok and ok_valid, worst, worst_small


FIG1_F = {"": 0, "a": Fr(5), "b": Fr(9, 2), "c": Fr(24, 5), "ab": Fr(19, 2),
          "ac": Fr(15, 2), "bc": Fr(7), "abc": Fr(97, 10)}
FIG1_A = {"": 0, "a": Fr(9, 2), "b": Fr(22, 5), "c": Fr(132, 25), "ab": Fr(9),
          "ac": Fr(69, 10), "bc": Fr(38, 5), "abc": Fr(46, 5)}
FIG1_B = {"": 0, "a": Fr(13, 2), "b": Fr(16, 5), "c": Fr(39, 10),
          "ab": Fr(247, 20), "ac": Fr(83, 10), "bc": Fr(26, 5), "abc": Fr(63, 5)}


def dict_to_lattice(d):
    names = "abc"
    out = [Fr(0)] * 8
    for S in range(8):
        key = "".join(names[i] for i in range(3) if S >> i & 1)
        out[S] = Fr(d[key])
    return out


def run_D2():
    n, K = 3, 2
    f = dict_to_lattice(FIG1_F)
    rows = []
    ok_all = True
    ok = is_monotone_submodular(f, n)
    ok_all &= ok
    check("D2a Figure 1: true f is monotone submodular [VERIFIED-EXHAUSTIVE]", ok,
          "all 8 sets, 3 monotonicity and 3 submodularity families checked exactly")
    OPT = max(f[S] for S in range(8) if bin(S).count("1") <= K)
    okopt = (OPT == Fr(19, 2))
    ok_all &= okopt
    check("D2b Figure 1: OPT = f({a,b}) = 19/2", okopt, "OPT = %s" % OPT)
    for tag, d, want_set, want_ratio, want_etasel in (
            ("A", FIG1_A, {1, 2}, Fr(14, 19), Fr(27, 22)),
            ("B", FIG1_B, {0, 1}, Fr(1), Fr(1))):
        ft = dict_to_lattice(d)
        fac = realized_factors(f, ft, n)
        ok = fac is not None
        eu, eo = fac if fac else (None, None)
        eta = eu * eo if fac else None
        finals, worst = greedy_all_ties(f, ft, n, K)
        sets = sorted({frozenset(i for i in range(3) if S >> i & 1) for S, _ in finals},
                      key=lambda s: sorted(s))
        got_set = set(sorted(sets, key=lambda s: sorted(s))[0]) if len(sets) == 1 else None
        ratio = worst / OPT
        bound = rho_K(K, eta) if eta is not None else None
        # eta^sel along the unique run
        path = []
        S = 0
        for _ in range(K):
            best, cand = None, []
            for e_ in range(3):
                if S >> e_ & 1:
                    continue
                dd = ft[S | (1 << e_)] - ft[S]
                if best is None or dd > best:
                    best, cand = dd, [e_]
                elif dd == best:
                    cand.append(e_)
            path.append(cand[0])
            S |= 1 << cand[0]
        esel = eta_sel_of_run(f, n, path)
        okc = (fac is not None and len(sets) == 1 and got_set == want_set
               and ratio == want_ratio and esel == want_etasel and ratio >= bound)
        ok_all &= okc
        rows.append({"surrogate": tag, "eta_u": str(eu), "eta_o": str(eo),
                     "eta": str(eta), "eta_float": float(eta),
                     "greedy_output": sorted("abc"[i] for i in got_set or []),
                     "n_tie_paths": len(finals),
                     "ratio": str(ratio), "ratio_float": float(ratio),
                     "rho_2_at_eta": str(bound), "rho_2_float": float(bound),
                     "slack": str(ratio - bound), "eta_sel": str(esel),
                     "eta_sel_float": float(esel), "ok": okc})
        check("D2%s Figure 1 surrogate %s [VERIFIED-EXHAUSTIVE]"
              % ("c" if tag == "A" else "d", tag), okc,
              "actual eta = %s (%.4f) = eta_u %s x eta_o %s; greedy output {%s}; "
              "ratio %s (%.4f) >= rho_2(eta) = %s (%.4f); eta^sel = %s (%.4f)"
              % (eta, float(eta), eu, eo,
                 ",".join(sorted("abc"[i] for i in got_set or [])),
                 ratio, float(ratio), bound, float(bound), esel, float(esel)))
        if not okc:
            VIOLATIONS.append({"check": "D2" + tag, "eta": str(eta),
                               "ratio": str(ratio), "rho": str(bound)})
    COUNTS["D2_structured_cases"] = 2
    return ok_all, rows


# ---------------------------------------------------------------------------
def main():
    print("V11 Q4 oracle: thm:exact (ledger T6, Theorem 1: rho_K = min_j V_j)")
    print("repo root:", ROOT)
    print("exact arithmetic: fractions.Fraction and sympy; seed D1=20260918")
    print("LP under test: code/reduced_lp.py, full rows, solved by an exact "
          "rational two-phase simplex written here")
    print()
    print("--- Criterion C ---", flush=True)
    okC0 = run_C0()
    okLP, lp_rows, running = run_C1_C2_C3_C6()
    okC4 = run_C4()
    okC5 = run_C5()
    print()
    print("--- Criterion D (C7 runs on the D1 instances, printed here) ---",
          flush=True)
    okD1, worst, worst_small = run_D1()
    okD2, d2rows = run_D2()

    ok_all = okC0 and okLP and okC4 and okC5 and okD1 and okD2
    print()
    print("counts:", json.dumps(COUNTS, sort_keys=True))
    print("running example K=3 eta=3/2:", json.dumps(running, sort_keys=True))
    print("worst D1 slack f(T)/OPT - rho_K(eta): %s at %s"
          % (worst[0], json.dumps(worst[1], sort_keys=True)))
    print("worst D1 slack among instances with eta <= 2: %s at %s"
          % (worst_small[0], json.dumps(worst_small[1], sort_keys=True)))
    print("violations:", len(VIOLATIONS))
    for v in VIOLATIONS[:5]:
        print("   ", json.dumps(v, sort_keys=True)[:400])
    blob = {"statement": "thm:exact (T6): rho_K(eta) = min_{0<=j<=K-1} V_j(eta)",
            "overall": "PASS" if ok_all else "FAIL",
            "checks": CHECKS, "counts": COUNTS,
            "lp_table": lp_rows, "running_example_K3_eta_3_2": running,
            "worst_D1_slack": {"slack": str(worst[0]), "where": worst[1]},
            "worst_D1_slack_eta_le_2": {"slack": str(worst_small[0]),
                                        "where": worst_small[1]},
            "figure1": d2rows, "reruns": SUBPROCS,
            "violations": VIOLATIONS,
            "seconds": round(time.time() - T0, 1)}
    path = os.path.join(HERE, "exact.json")
    with open(path, "w") as fh:
        json.dump(blob, fh, indent=1)
    print("json written:", path)
    nfail = sum(1 for c in CHECKS if c["status"] != "PASS")
    print("OVERALL: %s (%d checks, %d failed, %.1fs)"
          % ("PASS" if ok_all else "FAIL", len(CHECKS), nfail, time.time() - T0))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())

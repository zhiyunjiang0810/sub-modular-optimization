#!/usr/bin/env python3
"""V11 Q4c oracle for cor:limit (ledger T9).

Statement under test (results/V11/inputs/statement_limit.md), verbatim:

    For fixed eta >= 1, both L_K(eta) and rho_K(eta) converge to 1 - e^{-1/eta}
    as K -> infinity; L_K is monotone in K, and rho_K is non-increasing in K,
    equal to 1/eta for K <= floor(eta) and strictly decreasing from
    K >= floor(eta) on, so the limit is approached from above.

Route-one proof material:
    paper/sections/appendix_proofs.tex, subsection app:asymptotics (~line 1373)
    results/H_B_asymptotic.py  (sections 0-6)
    THEOREM_LEDGER.md section "## T9"

Closed forms used (notation.md):
    k_1 = (K-1) eta + 1,  q = (K-1) eta / k_1,
    V_j(eta) = 1 - q^j (1 - (K-j)/(K eta)),  rho_K = min_j V_j   (thm:exact, T6)
    active branch j* = max(0, K - floor(eta))
    L_K(eta) = 1 - (1 - 1/(eta K))^K,   U_K(eta) = 1 - (1 - 1/(eta(K-1)+1))^K

EVERY decision in this script is taken on exact objects: fractions.Fraction or
sympy.  e^{-1/eta} is never used as a float in a decision; it is bracketed by
the alternating Taylor series (terms decrease for 0 <= 1/eta <= 1, so
consecutive partial sums bracket the value), giving exact rational lo/hi.
Floats appear in printouts only.

Criterion C (oracle)
  C0  rerun results/H_B_asymptotic.py, record exit code and key counts.
      Its section 0 cross-check calls code/reduced_lp.py (scipy linprog,
      float tolerance), hence            [VERIFIED-LP 浮点] for that item,
      [VERIFIED-SYMBOLIC] / [VERIFIED-EXACT] for its sections 2, 4, 5, 6.
      The rerun happens in a mirror directory so that no repo file is touched;
      the sha256 of the repo script and of results/H_B_asymptotic.json are
      recorded before and after.
  C1  sympy: L_K(eta) -> 1 - e^{-1/eta} as K -> oo, symbolic eta and each
      rational eta of the grid.                             [VERIFIED-SYMBOLIC]
  C2  sympy: V_{K - floor(eta)}(eta) -> 1 - e^{-1/eta}, symbolic (eta, m) and
      each rational eta with m = floor(eta).                [VERIFIED-SYMBOLIC]
  C3  sympy series in epsilon = 1/K of the active branch V_{K-m}:
      order 0 = 1 - e^{-1/eta}, order 1 = c(eta) = e^{-1/eta}(2eta-1)/(2eta^2),
      d c / d m = 0 (c is not piecewise in floor(eta)).     [VERIFIED-SYMBOLIC]
  C3b exact rational bracketing of R_K = K^2 (rho_K - (1-e^{-1/eta}) - c/K)
      on K in {10,...,800}: |R_K| <= 1, i.e. the O(1/K^2) remainder is
      numerically small on the checked range (a finite-range exact check, not
      an asymptotic proof).                                 [VERIFIED-EXHAUSTIVE]
  C4  exact rational differences rho_{K+1} - rho_K <= 0 for K = 2..200 at
      eta in {1, 3/2, 2, 5/2, 3, 7/2, 5}; equality exactly on the plateau
      (both endpoints <= floor(eta)), strict beyond; rho_K = 1/eta for
      K <= floor(eta).                                      [VERIFIED-EXHAUSTIVE]
  C5  exact rational differences L_{K+1} - L_K < 0 for K = 1..200 on the same
      eta grid (L_K monotone, decreasing).                   [VERIFIED-EXHAUSTIVE]
  C6  limit approached from above, exactly: 1 - rho_K < lo(e^{-1/eta}) and
      1 - L_K < lo(e^{-1/eta}) on the same grid.            [VERIFIED-EXHAUSTIVE]
  C7  closed-form consistency (conditional on thm:exact / T6): j* attains
      min_{0<=j<=K} V_j, and L_K <= rho_K <= U_K.           [VERIFIED-EXHAUSTIVE]

Criterion D (counterexample search on the statement itself)
  D1  dense rational eta grid (all reduced p/q in [1,8], q <= 12) x K = 2..60:
      any rho_{K+1} > rho_K is FAILED; any rho_K <= 1 - e^{-1/eta} is FAILED.
  D2  random rational eta (fixed seed 20260918) x K = 2..60, same two tests.
  D3  structured cases: eta = 1, integer eta (branch breakpoints), eta just
      below / above an integer, eta >> K (full plateau), eta = K, huge eta.

House rules: no git, exact arithmetic for decisions, no existing repo file is
modified, reports in Chinese with English technical terms.

Run:  python3 results/V11/oracle/limit.py        (exit 0 iff every check passed)
"""

import hashlib
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from fractions import Fraction

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SEED = 20260918
ETA_C = [Fraction(1), Fraction(3, 2), Fraction(2), Fraction(5, 2),
         Fraction(3), Fraction(7, 2), Fraction(5)]
MONO_KMAX = 200
D_KMAX = 60
D_DEN_MAX = 12
D_ETA_MAX = 8
D_RANDOM_ETAS = 300

OUT = {"seed": SEED, "checks": {}, "criterion_D": {}}
FAILURES = []


def log(msg=""):
    print(msg, flush=True)


def sha256(path):
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return None


# ---------------------------------------------------------------------------
# exact closed forms
# ---------------------------------------------------------------------------
def V_exact(K, j, eta):
    """V_j(eta) = 1 - q^j (1 - (K-j)/(K eta)), q = (K-1)eta/((K-1)eta+1)."""
    assert isinstance(eta, Fraction) and isinstance(K, int) and K >= 1
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q ** j * (1 - Fraction(K - j, K) / eta)


def jstar(K, eta):
    """Active segment index j* = max(0, K - floor(eta))."""
    return max(0, K - (eta.numerator // eta.denominator))


def rho(K, eta):
    """rho_K(eta) on the active branch, exact Fraction (conditional on T6)."""
    return V_exact(K, jstar(K, eta), eta)


def rho_min_all(K, eta):
    return min(V_exact(K, j, eta) for j in range(0, K + 1))


def L_exact(K, eta):
    """L_K(eta) = 1 - (1 - 1/(eta K))^K, exact Fraction."""
    return 1 - (1 - 1 / (eta * K)) ** K


def U_exact(K, eta):
    """U_K(eta) = 1 - (1 - 1/(eta(K-1)+1))^K, exact Fraction."""
    return 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K


def exp_neg_bounds(x, n_terms=60):
    """Exact rational lo <= e^{-x} <= hi for Fraction x with 0 <= x <= 1.

    sum_i (-x)^i / i! is alternating with |t_{i+1}| <= |t_i| once i+1 >= x,
    which holds from i = 0 on when x <= 1; consecutive partial sums bracket
    the sum.  Truncation after an even number of terms gives an upper bound,
    after an odd number a lower bound.
    """
    assert isinstance(x, Fraction) and 0 <= x <= 1
    s = Fraction(0)
    term = Fraction(1)
    partial = []
    for i in range(0, n_terms + 2):
        if i > 0:
            term = term * (-x) / i
        s += term
        partial.append(s)
    even_idx = n_terms if n_terms % 2 == 0 else n_terms + 1
    odd_idx = even_idx + 1
    hi = partial[even_idx]
    lo = partial[odd_idx]
    assert lo <= hi
    return lo, hi


def limit_bounds(eta):
    """Exact rational lo <= 1 - e^{-1/eta} <= hi."""
    elo, ehi = exp_neg_bounds(1 / eta)
    return 1 - ehi, 1 - elo


def c_bounds(eta):
    """Exact rational lo <= c(eta) = e^{-1/eta}(2eta-1)/(2eta^2) <= hi."""
    elo, ehi = exp_neg_bounds(1 / eta)
    fac = (2 * eta - 1) / (2 * eta ** 2)
    assert fac > 0
    return elo * fac, ehi * fac


# ---------------------------------------------------------------------------
# C0: rerun results/H_B_asymptotic.py
# ---------------------------------------------------------------------------
def check_C0():
    name = "C0"
    log("=" * 78)
    log("C0  rerun results/H_B_asymptotic.py   [VERIFIED-LP 浮点 for its section 0;")
    log("    VERIFIED-SYMBOLIC / VERIFIED-EXACT for its sections 2, 4, 5, 6]")
    log("=" * 78)
    script = os.path.join(ROOT, "results", "H_B_asymptotic.py")
    repo_json = os.path.join(ROOT, "results", "H_B_asymptotic.json")
    sha_script_before = sha256(script)
    sha_json_before = sha256(repo_json)
    if not os.path.exists(script):
        FAILURES.append("C0: results/H_B_asymptotic.py not found")
        OUT["checks"][name] = {"status": "FAIL", "reason": "script missing"}
        return False

    # Mirror run: the script writes results/H_B_asymptotic.json next to itself,
    # so running it in place would overwrite an existing repo file.  We copy it
    # byte for byte into a temporary mirror whose "code" entry points at the
    # repo's code/ directory, so the executed source is identical.
    tmp = tempfile.mkdtemp(prefix="v11_limit_hb_")
    mirror_results = os.path.join(tmp, "results")
    os.makedirs(mirror_results)
    shutil.copy2(script, mirror_results)
    os.symlink(os.path.join(ROOT, "code"), os.path.join(tmp, "code"))
    same_bytes = sha256(os.path.join(mirror_results, "H_B_asymptotic.py")) == sha_script_before
    t0 = time.time()
    proc = subprocess.run([sys.executable, os.path.join(mirror_results, "H_B_asymptotic.py")],
                          capture_output=True, text=True, timeout=1800)
    dt = time.time() - t0
    out = proc.stdout
    mirror_log = os.path.join(tmp, "H_B_asymptotic.rerun.log")
    with open(mirror_log, "w") as fh:
        fh.write(out + "\n" + proc.stderr)

    counts = {}
    m = re.search(r"(\d+) points \(7 eta x 7 K\)\.\s+max \|LP - closed form\| = (\S+)", out)
    if m:
        counts["section0_points"] = int(m.group(1))
        counts["section0_max_abs_dev"] = m.group(2)
    counts["section0_jstar_attains_min"] = "jstar = max(0, K - floor(eta)) attains min_j V_j at every point: OK" in out
    m = re.search(r"max \|Richardson - closed form\| = (\S+)", out)
    if m:
        counts["section3_max_abs_diff"] = m.group(1)
    counts["section2_order1_equals_claim"] = bool(
        re.search(r"equals e\^\(-1/eta\)\(2eta-1\)/\(2eta\^2\)\s*:\s*True", out))
    counts["section2_order1_independent_of_m"] = bool(
        re.search(r"d/dm == 0 \(independent of m=floor\(eta\)\): True", out))
    counts["section4_no_negative_difference"] = "no strictly negative difference anywhere: True" in out
    counts["section4_zeros_only_below_floor_eta"] = bool(
        re.search(r"zeros occur exactly at K < floor\(eta\).*: True", out))
    m = re.findall(r"^\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S+)$", out, re.M)
    sec4 = []
    for row in m:
        try:
            sec4.append({"eta": row[0], "n_pos": int(row[1]), "n_zero": int(row[2]),
                         "n_neg": int(row[3])})
        except ValueError:
            pass
    HB_MONO_DIFFS = 399          # H_B section 4 runs K = 2..400
    sec4 = [r for r in sec4 if r["n_pos"] + r["n_zero"] + r["n_neg"] == HB_MONO_DIFFS]
    counts["section4_rows"] = sec4
    counts["section4_total_differences"] = sum(r["n_pos"] + r["n_zero"] + r["n_neg"] for r in sec4)
    counts["section4_total_negative"] = sum(r["n_neg"] for r in sec4)
    m = re.search(r"numerator \* \(1\+t\)\^\d+ as a polynomial in \(t,u,w\): (\d+) monomials, "
                  r"(\d+) with negative coefficient, constant term = (\S+)", out)
    if m:
        counts["section5_numerator_monomials"] = int(m.group(1))
        counts["section5_numerator_negative"] = int(m.group(2))
        counts["section5_numerator_constant"] = m.group(3)
    m = re.search(r"denominator: (\d+) monomials, (\d+) negative", out)
    if m:
        counts["section5_denominator_monomials"] = int(m.group(1))
        counts["section5_denominator_negative"] = int(m.group(2))
    counts["section5_proof_closes"] = "proof closes by nonnegative-coefficient argument: True" in out
    m = re.search(r"K from m\+1 up to m\+1\+2\^\d+: (\d+) nonpositive values", out)
    if m:
        counts["section5_direct_sweep_nonpositive"] = int(m.group(1))
    counts["section6_c_U_equals_c"] = bool(re.search(r"equals c\(eta\): True", out))

    sha_script_after = sha256(script)
    sha_json_after = sha256(repo_json)
    untouched = (sha_script_before == sha_script_after and sha_json_before == sha_json_after)

    ok = (proc.returncode == 0 and same_bytes and untouched
          and counts.get("section0_points") == 49
          and counts.get("section0_jstar_attains_min")
          and counts.get("section2_order1_equals_claim")
          and counts.get("section2_order1_independent_of_m")
          and counts.get("section4_no_negative_difference")
          and counts.get("section4_zeros_only_below_floor_eta")
          and counts.get("section4_total_negative") == 0
          and counts.get("section5_numerator_negative") == 0
          and counts.get("section5_denominator_negative") == 0)

    log(f"  script            : results/H_B_asymptotic.py  (sha256 {sha_script_before[:16]}...)")
    log(f"  mirror copy identical to repo source          : {same_bytes}")
    log(f"  exit code         : {proc.returncode}   ({dt:.1f} s)")
    log(f"  repo files untouched (script + its json sha256): {untouched}")
    log(f"  section 0  [VERIFIED-LP 浮点]  {counts.get('section0_points')} points "
        f"(7 eta x 7 K), max |LP - closed form| = {counts.get('section0_max_abs_dev')}, "
        f"j* attains min_j V_j: {counts.get('section0_jstar_attains_min')}")
    log(f"  section 2  order 1 = e^(-1/eta)(2eta-1)/(2eta^2): "
        f"{counts.get('section2_order1_equals_claim')}, independent of m: "
        f"{counts.get('section2_order1_independent_of_m')}")
    log(f"  section 3  max |Richardson - closed form| = {counts.get('section3_max_abs_diff')}")
    log(f"  section 4  {counts.get('section4_total_differences')} exact rational differences "
        f"(7 eta x K = 2..400), negative: {counts.get('section4_total_negative')}, "
        f"zeros only at K < floor(eta): {counts.get('section4_zeros_only_below_floor_eta')}")
    log(f"  section 5  numerator {counts.get('section5_numerator_monomials')} monomials / "
        f"{counts.get('section5_numerator_negative')} negative / constant "
        f"{counts.get('section5_numerator_constant')}; denominator "
        f"{counts.get('section5_denominator_monomials')} monomials / "
        f"{counts.get('section5_denominator_negative')} negative; direct sweep nonpositive "
        f"{counts.get('section5_direct_sweep_nonpositive')}")
    log(f"  section 6  c_U = c: {counts.get('section6_c_U_equals_c')}")
    log(f"  rerun log kept at : {mirror_log}")
    log(f"  -> {'PASS' if ok else 'FAIL'}")

    if not ok:
        FAILURES.append(f"C0: rerun of results/H_B_asymptotic.py did not reproduce "
                        f"(exit {proc.returncode}, counts {counts})")
    OUT["checks"][name] = {
        "status": "PASS" if ok else "FAIL",
        "tag": "[VERIFIED-LP 浮点] (section 0 uses scipy linprog) + [VERIFIED-SYMBOLIC] "
               "(sections 2, 5, 6) + [VERIFIED-EXACT] (section 4)",
        "script": "results/H_B_asymptotic.py",
        "script_sha256": sha_script_before,
        "mirror_copy_identical": same_bytes,
        "exit_code": proc.returncode,
        "seconds": dt,
        "repo_files_untouched": untouched,
        "rerun_log": mirror_log,
        "key_counts": counts,
    }
    return ok


# ---------------------------------------------------------------------------
# C1 / C2: sympy limits
# ---------------------------------------------------------------------------
def check_C1_C2():
    log()
    log("=" * 78)
    log("C1/C2  sympy limits K -> oo   [VERIFIED-SYMBOLIC]")
    log("=" * 78)
    K = sp.Symbol("K", positive=True)
    eta = sp.Symbol("eta", positive=True)
    m = sp.Symbol("m", positive=True)

    LK = 1 - (1 - 1 / (eta * K)) ** K
    q = (K - 1) * eta / ((K - 1) * eta + 1)
    Vact = 1 - q ** (K - m) * (1 - m / (K * eta))
    target = 1 - sp.exp(-1 / eta)

    lim_L = sp.limit(LK, K, sp.oo)
    lim_V = sp.limit(Vact, K, sp.oo)
    okL_sym = sp.simplify(lim_L - target) == 0
    okV_sym = sp.simplify(lim_V - target) == 0
    log(f"  symbolic eta:  lim L_K          = {sp.sstr(sp.simplify(lim_L))}   "
        f"equals 1 - e^(-1/eta): {okL_sym}")
    log(f"  symbolic eta:  lim V_(K-m)      = {sp.sstr(sp.simplify(lim_V))}   "
        f"equals 1 - e^(-1/eta): {okV_sym}  (m symbolic, so the value of "
        f"floor(eta) is immaterial)")

    rows = []
    okL_all = okV_all = True
    for e in ETA_C:
        er = sp.Rational(e.numerator, e.denominator)
        mm = sp.Integer(e.numerator // e.denominator)
        tgt = 1 - sp.exp(-1 / er)
        l1 = sp.limit(LK.subs(eta, er), K, sp.oo)
        l2 = sp.limit(Vact.subs({eta: er, m: mm}), K, sp.oo)
        o1 = sp.simplify(l1 - tgt) == 0
        o2 = sp.simplify(l2 - tgt) == 0
        okL_all &= o1
        okV_all &= o2
        rows.append({"eta": str(e), "floor_eta": int(mm), "L_limit_ok": bool(o1),
                     "V_limit_ok": bool(o2), "limit": sp.sstr(sp.simplify(tgt))})
        log(f"    eta = {str(e):>4}  m = {int(mm)}   lim L_K ok: {o1}   "
            f"lim V_(K-m) ok: {o2}   limit = {sp.sstr(sp.simplify(tgt))}")

    ok = bool(okL_sym and okV_sym and okL_all and okV_all)
    log(f"  -> {'PASS' if ok else 'FAIL'}  ({2 + 2 * len(ETA_C)} sympy limits)")
    if not ok:
        FAILURES.append("C1/C2: a sympy limit did not equal 1 - e^{-1/eta}")
    OUT["checks"]["C1"] = {"status": "PASS" if okL_sym and okL_all else "FAIL",
                           "tag": "[VERIFIED-SYMBOLIC]",
                           "n_limits": 1 + len(ETA_C),
                           "symbolic_eta_ok": bool(okL_sym),
                           "rows": [{"eta": r["eta"], "ok": r["L_limit_ok"]} for r in rows]}
    OUT["checks"]["C2"] = {"status": "PASS" if okV_sym and okV_all else "FAIL",
                           "tag": "[VERIFIED-SYMBOLIC]",
                           "n_limits": 1 + len(ETA_C),
                           "symbolic_eta_m_ok": bool(okV_sym),
                           "rows": [{"eta": r["eta"], "floor_eta": r["floor_eta"],
                                     "ok": r["V_limit_ok"]} for r in rows]}
    return ok


# ---------------------------------------------------------------------------
# C3: sympy series of the active branch
# ---------------------------------------------------------------------------
def check_C3():
    log()
    log("=" * 78)
    log("C3  sympy series of V_(K-m) in epsilon = 1/K   [VERIFIED-SYMBOLIC]")
    log("=" * 78)
    eps, eta, m = sp.symbols("epsilon eta m", positive=True)
    K = 1 / eps
    q = (K - 1) * eta / ((K - 1) * eta + 1)
    Vsym = 1 - sp.exp((K - m) * sp.log(q)) * (1 - m / (K * eta))
    ser = sp.expand(sp.simplify(sp.series(Vsym, eps, 0, 3).removeO()))
    p = sp.Poly(ser, eps)
    c0 = sp.simplify(p.coeff_monomial(1))
    c1 = sp.simplify(p.coeff_monomial(eps))
    c_claim = sp.exp(-1 / eta) * (2 * eta - 1) / (2 * eta ** 2)
    ok0 = sp.simplify(c0 - (1 - sp.exp(-1 / eta))) == 0
    ok1 = sp.simplify(c1 - c_claim) == 0
    ok_m = sp.simplify(sp.diff(c1, m)) == 0
    xs = sp.Symbol("x")
    roots = sp.solve(sp.Eq(2 * xs - 1, 0), xs)
    ok_pos = (roots == [sp.Rational(1, 2)] and sp.Rational(1, 2) < 1
              and sp.simplify(c_claim * 2 * eta ** 2 * sp.exp(1 / eta) - (2 * eta - 1)) == 0)

    log(f"  order 0 : {sp.sstr(c0)}")
    log(f"            equals 1 - e^(-1/eta)                  : {ok0}")
    log(f"  order 1 : {sp.sstr(c1)}")
    log(f"            equals e^(-1/eta)(2eta-1)/(2eta^2)     : {ok1}")
    log(f"            d/dm == 0 (c not piecewise in floor(eta)): {ok_m}")
    log(f"  c(eta) > 0 for eta >= 1 (the factor 2eta-1 vanishes only at eta = 1/2 < 1): "
        f"{ok_pos}  -> approach from above is consistent with the expansion")

    per_eta = []
    ok_eta = True
    for e in ETA_C:
        er = sp.Rational(e.numerator, e.denominator)
        mm = sp.Integer(e.numerator // e.denominator)
        se = sp.expand(sp.simplify(sp.series(Vsym.subs({eta: er, m: mm}), eps, 0, 2).removeO()))
        pe = sp.Poly(se, eps)
        c0e = sp.simplify(pe.coeff_monomial(1))
        c1e = sp.simplify(pe.coeff_monomial(eps))
        o0 = sp.simplify(c0e - (1 - sp.exp(-1 / er))) == 0
        o1 = sp.simplify(c1e - c_claim.subs(eta, er)) == 0
        ok_eta &= bool(o0 and o1)
        per_eta.append({"eta": str(e), "order0_ok": bool(o0), "order1_ok": bool(o1),
                        "c_value": float(sp.N(c_claim.subs(eta, er), 20))})
        log(f"    eta = {str(e):>4}  m = {int(mm)}   order0 ok: {o0}   order1 ok: {o1}   "
            f"c(eta) = {float(sp.N(c_claim.subs(eta, er), 20)):.10f}")

    ok = bool(ok0 and ok1 and ok_m and ok_pos and ok_eta)
    log(f"  -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        FAILURES.append("C3: the 1/K expansion of V_(K-m) did not match "
                        "1 - e^{-1/eta} + c(eta)/K with c(eta) = e^{-1/eta}(2eta-1)/(2eta^2)")
    OUT["checks"]["C3"] = {"status": "PASS" if ok else "FAIL", "tag": "[VERIFIED-SYMBOLIC]",
                           "order0": sp.sstr(c0), "order1": sp.sstr(c1),
                           "order1_equals_claim": bool(ok1),
                           "order1_independent_of_m": bool(ok_m),
                           "c_positive_on_eta_ge_1": bool(ok_pos),
                           "per_eta": per_eta}
    return ok


def check_C3b():
    log()
    log("=" * 78)
    log("C3b  exact bracketing of R_K = K^2 (rho_K - (1-e^{-1/eta}) - c(eta)/K)")
    log("     [VERIFIED-EXHAUSTIVE] finite-range exact check, not an asymptotic proof")
    log("=" * 78)
    Ks = [10, 20, 40, 80, 160, 320, 640, 800]
    rows = []
    worst = None
    ok = True
    for e in ETA_C:
        Llo, Lhi = limit_bounds(e)
        clo, chi = c_bounds(e)
        per = []
        for K in Ks:
            r = rho(K, e)
            lo = K * K * (r - Lhi - chi / K)
            hi = K * K * (r - Llo - clo / K)
            per.append((K, lo, hi))
            mx = max(abs(lo), abs(hi))
            if worst is None or mx > worst[0]:
                worst = (mx, str(e), K)
            if mx > 1:
                ok = False
                FAILURES.append(f"C3b: |R_K| > 1 at eta = {e}, K = {K}")
        rows.append({"eta": str(e),
                     "R": [{"K": K, "lo": float(lo), "hi": float(hi)} for K, lo, hi in per]})
        log(f"  eta = {str(e):>4}  R_K in " + "  ".join(
            f"K={K}:[{float(lo):+.5f},{float(hi):+.5f}]" for K, lo, hi in per[:4])
            + "  ...  " + f"K=800:[{float(per[-1][1]):+.5f},{float(per[-1][2]):+.5f}]")
    log(f"  max |R_K| over {len(ETA_C) * len(Ks)} exact brackets = {float(worst[0]):.6f} "
        f"at eta = {worst[1]}, K = {worst[2]}   (bound used: 1)")
    log(f"  -> {'PASS' if ok else 'FAIL'}")
    OUT["checks"]["C3b"] = {"status": "PASS" if ok else "FAIL", "tag": "[VERIFIED-EXHAUSTIVE]",
                            "n_brackets": len(ETA_C) * len(Ks),
                            "max_abs_R": float(worst[0]),
                            "max_abs_R_at": {"eta": worst[1], "K": worst[2]},
                            "rows": rows}
    return ok


# ---------------------------------------------------------------------------
# C4 / C5 / C6 / C7: exact rational checks on the eta grid
# ---------------------------------------------------------------------------
def check_C4():
    log()
    log("=" * 78)
    log(f"C4  exact rho_(K+1) - rho_K <= 0, K = 2..{MONO_KMAX}   [VERIFIED-EXHAUSTIVE]")
    log("=" * 78)
    rows = []
    ok = True
    n_diff = n_zero = n_strict = n_pos = 0
    worst = None          # largest (least negative) strict difference
    plateau_checked = 0
    log(f"  {'eta':>5} {'floor':>5} {'#diff':>6} {'#zero':>6} {'#strict<0':>10} {'#>0':>5} "
        f"{'zero K range':>14} {'max strict diff':>18}")
    for e in ETA_C:
        m = e.numerator // e.denominator
        vals = {K: rho(K, e) for K in range(2, MONO_KMAX + 2)}
        for K in range(2, MONO_KMAX + 2):
            if K <= m:
                plateau_checked += 1
                if vals[K] != 1 / e:
                    ok = False
                    FAILURES.append(f"C4: rho_K != 1/eta on the plateau at eta = {e}, K = {K} "
                                    f"(rho_K = {vals[K]}, 1/eta = {1 / e})")
        zeros = []
        strict = 0
        pos = 0
        mx = None
        for K in range(2, MONO_KMAX + 1):
            d = vals[K + 1] - vals[K]
            n_diff += 1
            if d > 0:
                pos += 1
                n_pos += 1
                ok = False
                FAILURES.append(f"C4: rho_(K+1) > rho_K at eta = {e}, K = {K} "
                                f"(rho_K = {vals[K]}, rho_(K+1) = {vals[K + 1]})")
            elif d == 0:
                zeros.append(K)
                n_zero += 1
                if not (K + 1 <= m):
                    ok = False
                    FAILURES.append(f"C4: equality rho_(K+1) = rho_K off the plateau at "
                                    f"eta = {e}, K = {K} (floor(eta) = {m})")
            else:
                strict += 1
                n_strict += 1
                if mx is None or d > mx:
                    mx = d
                if worst is None or d > worst[0]:
                    worst = (d, str(e), K)
                if K + 1 <= m:
                    ok = False
                    FAILURES.append(f"C4: strict decrease inside the plateau at eta = {e}, K = {K}")
        zr = f"{zeros[0]}..{zeros[-1]}" if zeros else "-"
        rows.append({"eta": str(e), "floor_eta": m, "n_diff": MONO_KMAX - 1,
                     "n_zero": len(zeros), "n_strict_negative": strict, "n_positive": pos,
                     "zero_K": zeros,
                     "max_strict_diff": float(mx) if mx is not None else None,
                     "max_strict_diff_exact": str(mx) if mx is not None else None})
        log(f"  {str(e):>5} {m:>5} {MONO_KMAX - 1:>6} {len(zeros):>6} {strict:>10} {pos:>5} "
            f"{zr:>14} {(float(mx) if mx is not None else 0):>18.3e}")
    log(f"  total exact differences: {n_diff}   zero: {n_zero}   strict negative: {n_strict}   "
        f"positive (violations): {n_pos}")
    log(f"  plateau values rho_K = 1/eta checked at {plateau_checked} (K, eta) pairs")
    log(f"  worst slack (largest strict difference) = {float(worst[0]):.6e} at eta = {worst[1]}, "
        f"K = {worst[2]}")
    log(f"  -> {'PASS' if ok else 'FAIL'}")
    OUT["checks"]["C4"] = {"status": "PASS" if ok else "FAIL", "tag": "[VERIFIED-EXHAUSTIVE]",
                           "K_range": [2, MONO_KMAX], "etas": [str(e) for e in ETA_C],
                           "n_differences": n_diff, "n_zero": n_zero,
                           "n_strict_negative": n_strict, "n_violations": n_pos,
                           "n_plateau_points": plateau_checked,
                           "worst_slack": {"value": float(worst[0]), "exact": str(worst[0]),
                                           "eta": worst[1], "K": worst[2]},
                           "rows": rows}
    return ok


def check_C5():
    log()
    log("=" * 78)
    log(f"C5  exact L_(K+1) - L_K < 0, K = 1..{MONO_KMAX}   [VERIFIED-EXHAUSTIVE]")
    log("=" * 78)
    ok = True
    n_diff = n_strict = n_bad = 0
    worst = None
    rows = []
    for e in ETA_C:
        vals = {K: L_exact(K, e) for K in range(1, MONO_KMAX + 2)}
        strict = 0
        mx = None
        for K in range(1, MONO_KMAX + 1):
            d = vals[K + 1] - vals[K]
            n_diff += 1
            if d < 0:
                strict += 1
                n_strict += 1
                if mx is None or d > mx:
                    mx = d
                if worst is None or d > worst[0]:
                    worst = (d, str(e), K)
            else:
                n_bad += 1
                ok = False
                FAILURES.append(f"C5: L_(K+1) >= L_K at eta = {e}, K = {K} "
                                f"(L_K = {vals[K]}, L_(K+1) = {vals[K + 1]})")
        rows.append({"eta": str(e), "n_diff": MONO_KMAX, "n_strict_negative": strict,
                     "n_non_negative": MONO_KMAX - strict,
                     "max_strict_diff": float(mx) if mx is not None else None})
        log(f"  eta = {str(e):>4}   {MONO_KMAX} differences, strictly negative: {strict}, "
            f"non-negative: {MONO_KMAX - strict},   max strict diff = "
            f"{(float(mx) if mx is not None else 0):.3e}")
    log(f"  total exact differences: {n_diff}   strictly negative: {n_strict}   "
        f"violations: {n_bad}")
    log(f"  worst slack = {float(worst[0]):.6e} at eta = {worst[1]}, K = {worst[2]}")
    log(f"  L_K is therefore decreasing in K on the checked range (monotone, from above)")
    log(f"  -> {'PASS' if ok else 'FAIL'}")
    OUT["checks"]["C5"] = {"status": "PASS" if ok else "FAIL", "tag": "[VERIFIED-EXHAUSTIVE]",
                           "K_range": [1, MONO_KMAX], "n_differences": n_diff,
                           "n_strict_negative": n_strict, "n_violations": n_bad,
                           "worst_slack": {"value": float(worst[0]), "exact": str(worst[0]),
                                           "eta": worst[1], "K": worst[2]},
                           "rows": rows}
    return ok


def check_C6():
    log()
    log("=" * 78)
    log(f"C6  limit approached from above, exact rational bracketing of e^(-1/eta)")
    log("    [VERIFIED-EXHAUSTIVE]")
    log("=" * 78)
    ok = True
    n = 0
    worst_rho = None
    worst_L = None
    rows = []
    for e in ETA_C:
        elo, ehi = exp_neg_bounds(1 / e)
        Llo, Lhi = 1 - ehi, 1 - elo
        mr = ml = None
        for K in range(2, MONO_KMAX + 2):
            r = rho(K, e)
            l = L_exact(K, e)
            n += 1
            sr = r - Lhi          # certified lower bound on rho_K - (1 - e^{-1/eta})
            sl = l - Lhi
            if not (1 - r < elo):
                ok = False
                FAILURES.append(f"C6: rho_K <= 1 - e^(-1/eta) at eta = {e}, K = {K}")
            if not (1 - l < elo):
                ok = False
                FAILURES.append(f"C6: L_K <= 1 - e^(-1/eta) at eta = {e}, K = {K}")
            if mr is None or sr < mr:
                mr = sr
            if ml is None or sl < ml:
                ml = sl
            if worst_rho is None or sr < worst_rho[0]:
                worst_rho = (sr, str(e), K)
            if worst_L is None or sl < worst_L[0]:
                worst_L = (sl, str(e), K)
        rows.append({"eta": str(e), "min_rho_slack": float(mr), "min_L_slack": float(ml),
                     "K_range": [2, MONO_KMAX + 1]})
        log(f"  eta = {str(e):>4}   min (rho_K - limit) = {float(mr):.6e}   "
            f"min (L_K - limit) = {float(ml):.6e}   (both certified > 0)")
    log(f"  {2 * n} exact comparisons against rational bounds on e^(-1/eta) "
        f"(60-term alternating Taylor bracket)")
    log(f"  worst slack rho: {float(worst_rho[0]):.6e} at eta = {worst_rho[1]}, K = {worst_rho[2]}")
    log(f"  worst slack L  : {float(worst_L[0]):.6e} at eta = {worst_L[1]}, K = {worst_L[2]}")
    log(f"  -> {'PASS' if ok else 'FAIL'}")
    OUT["checks"]["C6"] = {"status": "PASS" if ok else "FAIL", "tag": "[VERIFIED-EXHAUSTIVE]",
                           "n_comparisons": 2 * n,
                           "worst_rho_slack": {"value": float(worst_rho[0]),
                                               "eta": worst_rho[1], "K": worst_rho[2]},
                           "worst_L_slack": {"value": float(worst_L[0]),
                                             "eta": worst_L[1], "K": worst_L[2]},
                           "rows": rows}
    return ok


def check_C7():
    log()
    log("=" * 78)
    log("C7  closed-form consistency (conditional on thm:exact / ledger T6)")
    log("    [VERIFIED-EXHAUSTIVE]")
    log("=" * 78)
    ok = True
    n_min = n_sandwich = 0
    worst_gap = None
    for e in ETA_C:
        for K in range(1, 61):
            r = rho(K, e)
            if r != rho_min_all(K, e):
                ok = False
                FAILURES.append(f"C7: j* does not attain min_j V_j at eta = {e}, K = {K}")
            n_min += 1
            lk, uk = L_exact(K, e), U_exact(K, e)
            n_sandwich += 1
            if not (lk <= r <= uk):
                ok = False
                FAILURES.append(f"C7: sandwich L_K <= rho_K <= U_K fails at eta = {e}, K = {K} "
                                f"(L = {lk}, rho = {r}, U = {uk})")
            g = uk - lk
            if worst_gap is None or g > worst_gap[0]:
                worst_gap = (g, str(e), K)
    log(f"  j* = max(0, K - floor(eta)) attains min_(0<=j<=K) V_j at {n_min} (K, eta) points: "
        f"{ok}")
    log(f"  sandwich L_K <= rho_K <= U_K at {n_sandwich} points; widest U_K - L_K = "
        f"{float(worst_gap[0]):.6f} at eta = {worst_gap[1]}, K = {worst_gap[2]}")
    log(f"  -> {'PASS' if ok else 'FAIL'}")
    OUT["checks"]["C7"] = {"status": "PASS" if ok else "FAIL", "tag": "[VERIFIED-EXHAUSTIVE]",
                           "n_min_checks": n_min, "n_sandwich_checks": n_sandwich,
                           "widest_gap": {"value": float(worst_gap[0]), "eta": worst_gap[1],
                                          "K": worst_gap[2]},
                           "note": "conditional on thm:exact (rho_K = min_j V_j, ledger T6)"}
    return ok


# ---------------------------------------------------------------------------
# Criterion D
# ---------------------------------------------------------------------------
def scan_eta(e, kmax, state):
    """Exact scan of one eta: monotonicity and approach from above."""
    m = e.numerator // e.denominator
    elo, ehi = exp_neg_bounds(1 / e)
    Lhi = 1 - elo
    vals = {K: rho(K, e) for K in range(2, kmax + 2)}
    for K in range(2, kmax + 2):
        state["n_points"] += 1
        r = vals[K]
        if not (1 - r < elo):
            state["violations"].append(
                {"kind": "not_from_above", "eta": str(e), "K": K,
                 "rho": str(r), "statement": f"rho_K <= 1 - e^(-1/eta) at eta = {e}, K = {K}"})
        slack = r - Lhi
        if state["worst_above"] is None or slack < state["worst_above"][0]:
            state["worst_above"] = (slack, str(e), K)
        if K <= m and r != 1 / e:
            state["violations"].append(
                {"kind": "plateau_value", "eta": str(e), "K": K, "rho": str(r),
                 "statement": f"rho_K != 1/eta on the plateau at eta = {e}, K = {K}"})
    for K in range(2, kmax + 1):
        d = vals[K + 1] - vals[K]
        state["n_diffs"] += 1
        if d > 0:
            state["violations"].append(
                {"kind": "monotonicity", "eta": str(e), "K": K, "rho_K": str(vals[K]),
                 "rho_K1": str(vals[K + 1]),
                 "statement": f"rho_(K+1) > rho_K at eta = {e}, K = {K}"})
        elif d == 0:
            state["n_zero"] += 1
            if not (K + 1 <= m):
                state["violations"].append(
                    {"kind": "equality_off_plateau", "eta": str(e), "K": K,
                     "statement": f"rho_(K+1) = rho_K off the plateau at eta = {e}, "
                                  f"K = {K}, floor(eta) = {m}"})
        else:
            state["n_strict"] += 1
            if state["worst_mono"] is None or d > state["worst_mono"][0]:
                state["worst_mono"] = (d, str(e), K)


def new_state():
    return {"n_points": 0, "n_diffs": 0, "n_zero": 0, "n_strict": 0,
            "violations": [], "worst_mono": None, "worst_above": None}


def check_D():
    log()
    log("=" * 78)
    log("D  counterexample search on the statement itself")
    log("=" * 78)

    # ---- D1 dense deterministic grid
    etas = set()
    for q in range(1, D_DEN_MAX + 1):
        for p in range(q, D_ETA_MAX * q + 1):
            f = Fraction(p, q)
            if f >= 1:
                etas.add(f)
    etas = sorted(etas)
    s1 = new_state()
    t0 = time.time()
    for e in etas:
        scan_eta(e, D_KMAX, s1)
    log(f"  D1 dense grid: {len(etas)} rational eta (reduced p/q in [1,{D_ETA_MAX}], "
        f"q <= {D_DEN_MAX}) x K = 2..{D_KMAX + 1}")
    log(f"     {s1['n_points']} (K, eta) points, {s1['n_diffs']} exact differences, "
        f"{s1['n_zero']} equalities (all on the plateau), {s1['n_strict']} strict decreases, "
        f"{len(s1['violations'])} violations   ({time.time() - t0:.1f} s)")
    log(f"     worst monotonicity slack = {float(s1['worst_mono'][0]):.6e} at eta = "
        f"{s1['worst_mono'][1]}, K = {s1['worst_mono'][2]}")
    log(f"     worst from-above slack   = {float(s1['worst_above'][0]):.6e} at eta = "
        f"{s1['worst_above'][1]}, K = {s1['worst_above'][2]}")

    # ---- D2 random rational eta, fixed seed
    rng = random.Random(SEED)
    rand_etas = []
    while len(rand_etas) < D_RANDOM_ETAS:
        den = rng.randint(1, 40)
        num = rng.randint(den, 30 * den)
        f = Fraction(num, den)
        if f >= 1:
            rand_etas.append(f)
    s2 = new_state()
    t0 = time.time()
    for e in rand_etas:
        scan_eta(e, D_KMAX, s2)
    log(f"  D2 random grid (seed {SEED}): {len(rand_etas)} rational eta in [1,30] "
        f"(denominator <= 40) x K = 2..{D_KMAX + 1}")
    log(f"     {s2['n_points']} (K, eta) points, {s2['n_diffs']} exact differences, "
        f"{s2['n_zero']} equalities, {s2['n_strict']} strict decreases, "
        f"{len(s2['violations'])} violations   ({time.time() - t0:.1f} s)")
    log(f"     worst monotonicity slack = {float(s2['worst_mono'][0]):.6e} at eta = "
        f"{s2['worst_mono'][1]}, K = {s2['worst_mono'][2]}")
    log(f"     worst from-above slack   = {float(s2['worst_above'][0]):.6e} at eta = "
        f"{s2['worst_above'][1]}, K = {s2['worst_above'][2]}")

    # ---- D3 structured cases
    structured = [
        ("eta = 1 (rho_K = L_K)", [Fraction(1)]),
        ("integer eta (branch breakpoints)", [Fraction(k) for k in range(2, 9)]),
        ("eta just below an integer", [Fraction(k) - Fraction(1, 1000) for k in range(2, 9)]),
        ("eta just above an integer", [Fraction(k) + Fraction(1, 1000) for k in range(2, 9)]),
        ("eta >> K (full plateau)", [Fraction(100), Fraction(1000), Fraction(10 ** 6)]),
        ("eta = K on the diagonal", None),
        ("large non-integer eta", [Fraction(121, 2), Fraction(3001, 100)]),
        ("eta near 1 from above", [Fraction(1) + Fraction(1, d) for d in (10, 100, 1000)]),
    ]
    s3 = new_state()
    struct_rows = []
    for label, es in structured:
        st = new_state()
        if es is None:
            # diagonal eta = K: one point per K, monotonicity is not applicable
            for K in range(2, D_KMAX + 2):
                e = Fraction(K)
                elo, _ = exp_neg_bounds(1 / e)
                r = rho(K, e)
                st["n_points"] += 1
                if not (1 - r < elo):
                    st["violations"].append(
                        {"kind": "not_from_above", "eta": str(e), "K": K, "rho": str(r),
                         "statement": f"rho_K <= 1 - e^(-1/eta) at eta = K = {K}"})
                if K <= e and r != 1 / e:
                    st["violations"].append(
                        {"kind": "plateau_value", "eta": str(e), "K": K, "rho": str(r),
                         "statement": f"rho_K != 1/eta at eta = K = {K}"})
        else:
            for e in es:
                scan_eta(e, D_KMAX, st)
        for k in ("n_points", "n_diffs", "n_zero", "n_strict"):
            s3[k] += st[k]
        s3["violations"].extend(st["violations"])
        outcome = "PASS" if not st["violations"] else "FAILED"
        struct_rows.append({"case": label, "n_points": st["n_points"],
                            "n_differences": st["n_diffs"],
                            "n_equalities": st["n_zero"],
                            "n_violations": len(st["violations"]), "outcome": outcome})
        log(f"  D3 {label:<38} {st['n_points']:>6} points, {st['n_diffs']:>6} differences, "
            f"{st['n_zero']:>5} equalities, violations {len(st['violations'])}  -> {outcome}")

    all_viol = s1["violations"] + s2["violations"] + s3["violations"]
    n_points = s1["n_points"] + s2["n_points"] + s3["n_points"]
    n_diffs = s1["n_diffs"] + s2["n_diffs"] + s3["n_diffs"]
    worst_mono = min([w for w in (s1["worst_mono"], s2["worst_mono"]) if w],
                     key=lambda t: -t[0])
    worst_above = min([w for w in (s1["worst_above"], s2["worst_above"]) if w],
                      key=lambda t: t[0])
    ok = not all_viol
    log(f"  total: {n_points} (K, eta) points, {n_diffs} exact monotonicity differences, "
        f"{len(all_viol)} violations")
    log(f"  worst monotonicity slack over D1+D2 = {float(worst_mono[0]):.6e} "
        f"(eta = {worst_mono[1]}, K = {worst_mono[2]})")
    log(f"  worst from-above slack over D1+D2   = {float(worst_above[0]):.6e} "
        f"(eta = {worst_above[1]}, K = {worst_above[2]})")
    log(f"  -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        for v in all_viol[:20]:
            FAILURES.append("D: " + v["statement"])

    OUT["criterion_D"] = {
        "status": "PASS" if ok else "FAIL",
        "tag": "[VERIFIED-EXHAUSTIVE]",
        "n_points_total": n_points,
        "n_differences_total": n_diffs,
        "n_violations": len(all_viol),
        "violations": all_viol[:50],
        "D1_dense": {"n_eta": len(etas), "K_range": [2, D_KMAX + 1],
                     "n_points": s1["n_points"], "n_differences": s1["n_diffs"],
                     "n_equalities": s1["n_zero"], "n_strict": s1["n_strict"],
                     "n_violations": len(s1["violations"]),
                     "worst_mono_slack": {"value": float(s1["worst_mono"][0]),
                                          "exact": str(s1["worst_mono"][0]),
                                          "eta": s1["worst_mono"][1], "K": s1["worst_mono"][2]},
                     "worst_above_slack": {"value": float(s1["worst_above"][0]),
                                           "eta": s1["worst_above"][1],
                                           "K": s1["worst_above"][2]}},
        "D2_random": {"seed": SEED, "n_eta": len(rand_etas), "K_range": [2, D_KMAX + 1],
                      "n_points": s2["n_points"], "n_differences": s2["n_diffs"],
                      "n_equalities": s2["n_zero"], "n_strict": s2["n_strict"],
                      "n_violations": len(s2["violations"]),
                      "worst_mono_slack": {"value": float(s2["worst_mono"][0]),
                                           "exact": str(s2["worst_mono"][0]),
                                           "eta": s2["worst_mono"][1], "K": s2["worst_mono"][2]},
                      "worst_above_slack": {"value": float(s2["worst_above"][0]),
                                            "eta": s2["worst_above"][1],
                                            "K": s2["worst_above"][2]}},
        "D3_structured": struct_rows,
        "worst_mono_slack": {"value": float(worst_mono[0]), "exact": str(worst_mono[0]),
                             "eta": worst_mono[1], "K": worst_mono[2]},
        "worst_above_slack": {"value": float(worst_above[0]), "eta": worst_above[1],
                              "K": worst_above[2]},
    }
    return ok


# ---------------------------------------------------------------------------
# running example
# ---------------------------------------------------------------------------
def running_example():
    log()
    log("=" * 78)
    log("Running example  K = 3, eta = 3/2")
    log("=" * 78)
    e = Fraction(3, 2)
    K = 3
    m = e.numerator // e.denominator
    k1 = (K - 1) * e + 1
    q = (K - 1) * e / k1
    j = jstar(K, e)
    r3, r4 = rho(3, e), rho(4, e)
    l3, u3 = L_exact(3, e), U_exact(3, e)
    Llo, Lhi = limit_bounds(e)
    clo, chi = c_bounds(e)
    log(f"  m = floor(eta) = {m}, k_1 = {k1}, q = {q}, j* = K - m = {j}")
    log(f"  rho_3 = V_2 = {r3} = {float(r3):.10f};  L_3 = {l3} = {float(l3):.10f};  "
        f"U_3 = {u3} = {float(u3):.10f}")
    log(f"  rho_4 = {r4} = {float(r4):.10f};  rho_4 - rho_3 = {r4 - r3} = "
        f"{float(r4 - r3):.10f} < 0")
    log(f"  1 - e^(-2/3) in [{float(Llo):.12f}, {float(Lhi):.12f}];  "
        f"rho_3 - limit >= {float(r3 - Lhi):.10f} > 0;  c(3/2) in "
        f"[{float(clo):.10f}, {float(chi):.10f}]")
    OUT["running_example"] = {
        "K": 3, "eta": "3/2", "floor_eta": m, "k1": str(k1), "q": str(q), "jstar": j,
        "rho_3": str(r3), "rho_3_float": float(r3),
        "rho_4": str(r4), "rho_4_float": float(r4),
        "rho_4_minus_rho_3": str(r4 - r3), "rho_4_minus_rho_3_float": float(r4 - r3),
        "L_3": str(l3), "L_3_float": float(l3), "U_3": str(u3), "U_3_float": float(u3),
        "limit_lo": float(Llo), "limit_hi": float(Lhi),
        "rho_3_minus_limit_lower_bound": float(r3 - Lhi),
        "c_eta_lo": float(clo), "c_eta_hi": float(chi),
    }
    return {"rho_3": r3, "rho_4": r4, "L_3": l3, "U_3": u3, "limit_hi": Lhi}


# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    log("V11 Q4c oracle for cor:limit (ledger T9)")
    log(f"statement : results/V11/inputs/statement_limit.md")
    log(f"seed      : {SEED}")
    log(f"eta grid C: {[str(e) for e in ETA_C]}, K = 2..{MONO_KMAX}")
    log()

    results = {}
    results["C0"] = check_C0()
    results["C1/C2"] = check_C1_C2()
    results["C3"] = check_C3()
    results["C3b"] = check_C3b()
    results["C4"] = check_C4()
    results["C5"] = check_C5()
    results["C6"] = check_C6()
    results["C7"] = check_C7()
    results["D"] = check_D()
    running_example()

    ok = all(results.values()) and not FAILURES
    dt = time.time() - t0
    log()
    log("=" * 78)
    log("SUMMARY")
    log("=" * 78)
    for k, v in results.items():
        log(f"  {k:<8} {'PASS' if v else 'FAIL'}")
    log(f"  failures: {len(FAILURES)}")
    for f in FAILURES[:20]:
        log(f"    [FAILED] {f}")
    log(f"  elapsed {dt:.1f} s")
    OUT["summary"] = {"all_pass": bool(ok), "per_check": {k: bool(v) for k, v in results.items()},
                      "n_failures": len(FAILURES), "failures": FAILURES, "seconds": dt}
    with open(os.path.join(HERE, "limit.json"), "w") as fh:
        json.dump(OUT, fh, indent=1, default=str)
    log(f"  wrote {os.path.join(HERE, 'limit.json')}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

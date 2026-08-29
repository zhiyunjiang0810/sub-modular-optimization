"""T3 steps 3-5: closed form of the reduced LP value (code/reduced_lp.py) for K=3,
with full symbolic primal+dual certificates, rational-function fitting cross-check,
K=4 closed form, and the general-K conjecture  rho_K^LP(eta) = min_j V_j(eta).

Definitions (derived from the LP active-set structure, then verified):
  k1 = (K-1)*eta + 1,   q = (K-1)*eta/k1  (= 1 - 1/k1)
  V_j(eta) = 1 - q^j * (1 - (K-j)/(K*eta)),   j = 0..K-1
Claim: LP value = V_j(eta) on segment eta in [K-j, K-j+1] (j >= 1) and = V_0 = 1/eta
on [K, infinity).  Certificates:
  primal x_j: d_t = q^t/k1 (t<j), d_t = q^j/(K*eta) (t>=j); g_{t,i} = q^min(t,j)/K.
  dual y_j: solved symbolically from complementary slackness (all primal vars > 0
  => A^T y = c), support taken from the HiGHS multipliers, symmetric over i.
Both are verified SYMBOLICALLY on each segment: every slack / sign condition is a
rational function of eta whose numerator polynomial is shown (exact Sturm root
counting) to have no root in the open segment and the correct sign at a rational
interior point.  This upgrades the segment formulas to [VERIFIED-SYMBOLIC] as
statements about the reduced LP.

Outputs: results/T3_K3_closed_form.json, figures/T3_K3_pieces.png, console log.
Run: python results/T3_K3_closed_form.py   (~2-4 min)
"""
import sys, os, json
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
import numpy as np
import sympy as sp
from reduced_lp import reduced

ETA = sp.symbols("eta", positive=True)
OUT = {"parts": {}}

# ---------------------------------------------------------------- LP (symbolic)
def build_lp(K, e):
    """Reduced LP rebuilt symbolically; same row order as code/reduced_lp.py.
    min c'x s.t. A x <= b, x >= 0."""
    nd = K
    gidx = lambda t, i: nd + t*K + i
    nv = nd + (K+1)*K
    rows, labels, b = [], [], []
    def add(coefs, rhs, lab):
        row = [sp.Integer(0)]*nv
        for k, v in coefs.items():
            row[k] = v
        rows.append(row); b.append(rhs); labels.append(lab)
    for t in range(K):
        c = {gidx(t, i): sp.Integer(-1) for i in range(K)}
        for s in range(t):
            c[s] = sp.Integer(-1)
        add(c, sp.Integer(-1), ("sum", t, None))
        for i in range(K):
            add({gidx(t, i): sp.Rational(1)/e, t: sp.Integer(-1)}, 0, ("pred", t, i))
            add({gidx(t+1, i): sp.Integer(1), gidx(t, i): sp.Integer(-1)}, 0, ("mono", t, i))
            add({gidx(t, i): sp.Integer(1), t: sp.Integer(-1),
                 gidx(t+1, i): -(1 - 1/e)}, 0, ("cons", t, i))
    return (sp.Matrix(rows), sp.Matrix(b),
            sp.Matrix([sp.Integer(1)]*K + [sp.Integer(0)]*((K+1)*K)), labels)

def row_label(K, row):
    per = 1 + 3*K
    t, j = divmod(row, per)
    if j == 0:
        return ("sum", t, None)
    i, k = divmod(j-1, 3)
    return (["pred", "mono", "cons"][k], t, i)

def Vj(K, j, e):
    q = (K-1)*e/((K-1)*e + 1)
    return 1 - q**j*(1 - sp.Rational(K-j, K)/e)

def Vj_frac(K, j, e):
    """Exact Fraction evaluation of V_j."""
    e = Fraction(e)
    q = Fraction((K-1)*e, (K-1)*e + 1)
    return 1 - q**j*(1 - Fraction(K-j, K)/e)

def conj_frac(K, e):
    return min(Vj_frac(K, j, e) for j in range(K))

def primal_x(K, j, e):
    k1 = (K-1)*e + 1
    q = (K-1)*e/k1
    d = [q**t/k1 for t in range(j)] + [q**j/(K*e) for _ in range(j, K)]
    g = []
    for t in range(K+1):
        g += [q**min(t, j)/K]*K
    return sp.Matrix(d + g)

# ------------------------------------------------- exact sign check on interval
def nonneg_on(expr, lo, hi):
    """Prove (exactly) expr(eta) >= 0 for all eta in [lo, hi] (hi=None -> +oo).
    Requires: numerator poly has no root in the OPEN interval, correct sign at an
    interior rational point, and >= 0 at finite endpoints; denominator has no
    root in the closed interval. Returns (bool, reason)."""
    lo = sp.Rational(lo)
    expr = sp.together(sp.cancel(expr))
    num, den = sp.fraction(expr)
    num, den = sp.expand(num), sp.expand(den)
    if num == 0:
        return True, "identically 0"
    pn = sp.Poly(num, ETA)
    pd = sp.Poly(den, ETA)
    ref = lo + 1 if hi is None else (lo + sp.Rational(hi))/2

    def roots_in(poly, a, b_open_inf):
        """# roots in [a, B] with B = b or a Cauchy bound if interval unbounded."""
        if b_open_inf is None:
            cs = poly.all_coeffs()
            B = a + 1 + max(abs(sp.Rational(c)) for c in cs)/abs(sp.Rational(cs[0]))
        else:
            B = sp.Rational(b_open_inf)
        return poly.count_roots(a, B), B

    # denominator: no roots at all in the closed interval
    ndr, _ = roots_in(pd, lo, hi)
    if ndr != 0:
        return False, f"denominator has {ndr} root(s) in interval"
    if pd.eval(ref) == 0:
        return False, "denominator vanishes at reference point"
    # numerator: roots allowed only at finite endpoints
    nr, _ = roots_in(pn, lo, hi)
    nr -= int(pn.eval(lo) == 0)
    if hi is not None:
        nr -= int(pn.eval(sp.Rational(hi)) == 0)
    if nr != 0:
        return False, f"numerator has {nr} root(s) in open interval"
    sign = pn.eval(ref)*pd.eval(ref)
    if sign <= 0:
        return False, f"negative at eta={ref}"
    if pn.eval(lo)*pd.eval(lo) < 0:
        return False, "negative at left endpoint"
    if hi is not None and pn.eval(sp.Rational(hi))*pd.eval(sp.Rational(hi)) < 0:
        return False, "negative at right endpoint"
    return True, "ok"

# --------------------------------------------- certificates for one (K, j) pair
def certify_segment(K, j, lo, hi, eta_sample, A, b, c, labels):
    """Symbolically verify LP value == V_j on [lo, hi] via primal + dual certs."""
    rep = {"K": K, "j": j, "segment": [str(lo), "oo" if hi is None else str(hi)],
           "V_j": str(sp.factor(Vj(K, j, ETA)))}
    ok = True
    # ---- primal: x_j feasible on segment, objective == V_j
    x = primal_x(K, j, ETA)
    if sp.simplify((c.T*x)[0] - Vj(K, j, ETA)) != 0:
        rep["primal_objective"] = "FAIL"
        return rep, False
    bad = []
    for r, s in enumerate(sp.expand(b - A*x)):
        good, why = nonneg_on(s, lo, hi)
        if not good:
            bad.append((labels[r], why))
    for v in x:   # x >= 0 (obvious, but check)
        good, why = nonneg_on(v, lo, hi)
        if not good:
            bad.append(("x>=0", why))
    rep["primal_feasible_on_segment"] = "PASS" if not bad else f"FAIL {bad}"
    ok &= not bad
    # ---- dual: support from HiGHS at sample, symmetric ansatz, A^T y = c
    _, res = reduced(K, eta_sample, return_sol=True)
    supp = sorted({row_label(K, r)[:2] for r, m in enumerate(res.ineqlin.marginals)
                   if abs(m) > 1e-9})
    rep["dual_support"] = [f"{t}({s})" for t, s in supp]
    un = {sk: sp.symbols(f"y_{sk[0]}{sk[1]}") for sk in supp}
    y = sp.Matrix([un.get((lab[0], lab[1]), sp.Integer(0)) for lab in labels])
    sol = sp.solve(list(sp.expand(A.T*y - c)), list(un.values()), dict=True)
    if len(sol) != 1 or any(v not in sol[0] for v in un.values()):
        rep["dual_solve"] = f"FAIL (solutions: {len(sol)})"
        return rep, False
    s0 = sol[0]
    yv = y.subs(s0)
    rep["dual_multipliers"] = {f"{sk[0]}({sk[1]})": str(sp.factor(s0[un[sk]]))
                               for sk in supp}
    bad = []
    for sk in supp:                      # y <= 0 on segment
        good, why = nonneg_on(-s0[un[sk]], lo, hi)
        if not good:
            bad.append((sk, why))
    rep["dual_sign_on_segment"] = "PASS" if not bad else f"FAIL {bad}"
    ok &= not bad
    gap = sp.simplify((b.T*yv)[0] - Vj(K, j, ETA))
    rep["dual_objective_equals_Vj"] = "PASS" if gap == 0 else f"FAIL ({gap})"
    ok &= (gap == 0)
    rep["status"] = "VERIFIED-SYMBOLIC" if ok else "FAILED"
    return rep, ok

# ---------------------------------------------------- rational-function fitting
def fit_rational(etas, vals, dmax=3, tol=1e-10):
    """Fit vals ~ P(eta)/Q(eta), deg P,Q <= dmax, Q(0)=1, by linear least squares
    v*Q - P = 0. Returns (P_sym, Q_sym, train_residual, (dp,dq)) or None."""
    for total in range(0, 2*dmax + 1):
        for dp in range(0, min(total, dmax) + 1):
            dq = total - dp
            if dq > dmax:
                continue
            M = np.zeros((len(etas), dp + 1 + dq))
            for r, (e, v) in enumerate(zip(etas, vals)):
                M[r, :dp+1] = [e**p for p in range(dp+1)]
                M[r, dp+1:] = [-v*e**p for p in range(1, dq+1)]
            coef, *_ = np.linalg.lstsq(M, np.array(vals), rcond=None)
            p, q = coef[:dp+1], np.concatenate([[1.0], coef[dp+1:]])
            pred = np.array([np.polyval(p[::-1], e)/np.polyval(q[::-1], e) for e in etas])
            resid = np.max(np.abs(pred - np.array(vals)))
            if resid < tol:
                Ps = sum(sp.nsimplify(Fraction(float(ci)).limit_denominator(10**6))*ETA**i
                         for i, ci in enumerate(p))
                Qs = sum(sp.nsimplify(Fraction(float(ci)).limit_denominator(10**6))*ETA**i
                         for i, ci in enumerate(q))
                return sp.factor(Ps), sp.factor(Qs), float(resid), (dp, dq)
    return None

def main():
    log = print
    # ================= step 3: 60-point scan on [1,3], segment detection, fit
    log("== K=3: 60-point scan on [1,3], dual-support segmentation, rational fit ==")
    K = 3
    etas = np.linspace(1.0, 3.0, 60)
    pts = []
    for e in etas:
        val, res = reduced(K, float(e), return_sol=True)
        supp = tuple(sorted({row_label(K, r)[:2] for r, m in
                             enumerate(res.ineqlin.marginals) if abs(m) > 1e-9}))
        pts.append({"eta": float(e), "lp": float(val), "support": supp})
    # breakpoint detection: where the (type,t) support pattern changes
    changes = [(pts[i-1]["eta"], pts[i]["eta"]) for i in range(1, len(pts))
               if pts[i]["support"] != pts[i-1]["support"]]
    log(f"support-pattern changes between eta: {changes}")
    segs = {"A [1,2]": [p for p in pts if p["eta"] <= 2.0],
            "B [2,3]": [p for p in pts if p["eta"] >= 2.0]}
    fits = {}
    for name, sub in segs.items():
        train = [p for k, p in enumerate(sub) if k % 3 != 2]
        test = [p for k, p in enumerate(sub) if k % 3 == 2]
        got = fit_rational([p["eta"] for p in train], [p["lp"] for p in train])
        assert got, f"no rational fit found for segment {name}"
        P, Q, train_res, deg = got
        F = sp.cancel(P/Q)
        f = sp.lambdify(ETA, F, "numpy")
        test_res = max(abs(f(p["eta"]) - p["lp"]) for p in test)
        log(f"segment {name}: fit ({deg[0]},{deg[1]})  P/Q = {sp.factor(F)}")
        log(f"   train pts={len(train)} max resid={train_res:.2e}; "
            f"test pts={len(test)} max resid={test_res:.2e} (< 1e-9: {test_res < 1e-9})")
        fits[name] = {"formula": str(sp.factor(F)), "deg": deg,
                      "n_train": len(train), "train_resid": train_res,
                      "n_test": len(test), "test_resid": float(test_res),
                      "test_pass_1e-9": bool(test_res < 1e-9)}
    # fitted formulas == active-set formulas?
    m1 = sp.simplify(sp.cancel(sp.sympify(fits["A [1,2]"]["formula"],
                                          locals={"eta": ETA}) - Vj(3, 2, ETA)))
    m2 = sp.simplify(sp.cancel(sp.sympify(fits["B [2,3]"]["formula"],
                                          locals={"eta": ETA}) - Vj(3, 1, ETA)))
    log(f"fit A == V_2: {m1 == 0};  fit B == V_1: {m2 == 0}")
    bp = sp.solve(sp.Eq(Vj(3, 2, ETA), Vj(3, 1, ETA)), ETA)
    log(f"breakpoint V_2 = V_1 at eta = {bp}")
    OUT["parts"]["scan_and_fit_K3"] = {
        "grid": [{"eta": p["eta"], "lp": p["lp"]} for p in pts],
        "support_changes_between": changes, "fits": fits,
        "fit_equals_active_set_formula": bool(m1 == 0 and m2 == 0),
        "breakpoint_V2_V1": [str(x) for x in bp]}

    # ================= step 4: symbolic certificates K=3 (and K=2 re-derivation)
    log("\n== symbolic primal+dual certificates ==")
    allK = {}
    for KK, seglist in [(2, [(1, 1, 2, 1.5), (0, 2, None, 3.0)]),
                        (3, [(2, 1, 2, 1.5), (1, 2, 3, 2.5), (0, 3, None, 3.5)]),
                        (4, [(3, 1, 2, 1.5), (2, 2, 3, 2.5), (1, 3, 4, 3.5),
                             (0, 4, None, 4.5)])]:
        A, b, c, labels = build_lp(KK, ETA)
        reps, okK = [], True
        for j, lo, hi, samp in seglist:
            rep, ok = certify_segment(KK, j, lo, hi, samp, A, b, c, labels)
            hi_s = "oo" if hi is None else hi
            log(f"K={KK} j={j} [{lo},{hi_s}]: V_j = {rep['V_j']}  -> {rep['status']}")
            for k in ["primal_feasible_on_segment", "dual_sign_on_segment",
                      "dual_objective_equals_Vj"]:
                if rep.get(k) != "PASS":
                    log(f"      {k}: {rep.get(k)}")
            reps.append(rep); okK &= ok
        allK[KK] = {"segments": reps, "all_verified": okK}
    OUT["parts"]["symbolic_certificates"] = allK

    # ================= exact rational checks at R5 known points (K=3, K=4)
    log("\n== exact rational check against R5 table ==")
    R5 = {(3, Fraction(1)): Fraction(19, 27), (3, Fraction(3, 2)): Fraction(9, 16),
          (3, Fraction(2)): Fraction(7, 15), (3, Fraction(5, 2)): Fraction(7, 18),
          (3, Fraction(3)): Fraction(1, 3), (3, Fraction(61, 20)): Fraction(20, 61),
          (4, Fraction(1)): Fraction(175, 256), (4, Fraction(2)): Fraction(22, 49),
          (4, Fraction(3)): Fraction(13, 40), (4, Fraction(4)): Fraction(1, 4),
          (4, Fraction(21, 5)): Fraction(5, 21),
          (2, Fraction(1)): Fraction(3, 4), (2, Fraction(3, 2)): Fraction(3, 5),
          (2, Fraction(2)): Fraction(1, 2), (2, Fraction(5, 2)): Fraction(2, 5),
          (2, Fraction(3)): Fraction(1, 3), (2, Fraction(4)): Fraction(1, 4)}
    r5rows, r5ok = [], True
    for (KK, e), v in sorted(R5.items()):
        got = conj_frac(KK, e)
        r5rows.append({"K": KK, "eta": str(e), "R5": str(v), "min_j_Vj": str(got),
                       "match": got == v})
        r5ok &= (got == v)
    # R5 decimal-only points
    for KK, e, v in [(3, 1.1, 0.670573), (3, 1.25, 0.625850), (3, 2.8, 0.353535),
                     (3, 2.95, 0.338164), (4, 1.5, 0.543576), (4, 2.5, 0.377163),
                     (4, 3.8, 0.262097)]:
        got = float(min(Vj_frac(KK, j, Fraction(e).limit_denominator(100))
                        for j in range(KK)))
        match = abs(got - v) < 5e-7
        r5rows.append({"K": KK, "eta": str(e), "R5": str(v), "min_j_Vj": f"{got:.6f}",
                       "match": match})
        r5ok &= match
    log(f"all R5 values reproduced by min_j V_j: {r5ok}")
    OUT["parts"]["R5_exact_check"] = {"rows": r5rows, "all_match": r5ok}

    # ================= step 5: general-K conjecture, numeric LP check K=2..6
    log("\n== general-K conjecture: LP value == min_j V_j (numeric, K=2..6) ==")
    worst, npts = 0.0, 0
    for KK in [2, 3, 4, 5, 6]:
        for e in np.linspace(1.0, KK + 1.0, 41):
            lp = reduced(KK, float(e))
            cj = float(min(Vj_frac(KK, j, Fraction(float(e)).limit_denominator(10**8))
                           for j in range(KK)))
            worst = max(worst, abs(lp - cj)); npts += 1
    log(f"max |LP - min_j V_j| over {npts} points (K=2..6): {worst:.2e}")
    OUT["parts"]["generalK_numeric"] = {"K_tested": [2, 3, 4, 5, 6],
                                        "points_per_K": 41, "max_abs_dev": worst}

    # symbolic (general K, j): V_j = V_{j-1} exactly at eta = K-j+1, and
    # V_{K-1}(1) = 1-(1-1/K)^K (classic greedy at eta=1)
    Ks, js = sp.symbols("K j", positive=True)
    qs = (Ks-1)*ETA/((Ks-1)*ETA + 1)
    Vs = lambda jj: 1 - qs**jj*(1 - (Ks-jj)/(Ks*ETA))
    cross = sp.solve(sp.Eq(Vs(js), Vs(js-1)), ETA)
    at1 = sp.simplify(Vs(Ks-1).subs(ETA, 1) - (1 - (1 - 1/Ks)**Ks))
    log(f"symbolic general-K: V_j = V_(j-1) at eta = {cross} (expect [K-j+1]); "
        f"V_(K-1)(1) - (1-(1-1/K)^K) = {at1}")
    OUT["parts"]["generalK_symbolic_identities"] = {
        "crossing_eta": [str(x) for x in cross],
        "crossing_pass": cross == [Ks - js + 1],
        "V_Kminus1_at_eta1_equals_classic": at1 == 0}

    # ================= figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ee = np.linspace(1.0, 3.6, 300)
    for j, style, lab in [(2, "--", r"$V_2=\frac{16\eta+3}{3(2\eta+1)^2}$"),
                          (1, "-.", r"$V_1=\frac{7}{3(2\eta+1)}$"),
                          (0, ":", r"$V_0=1/\eta$")]:
        f = sp.lambdify(ETA, Vj(3, j, ETA), "numpy")
        ax.plot(ee, f(ee), style, lw=1.2, label=lab)
    ax.plot([p["eta"] for p in pts], [p["lp"] for p in pts], "o", ms=3, alpha=.55,
            label="reduced LP (60 pts)")
    extra = [(3.05, None)]
    for e, _ in extra:
        ax.plot([e], [reduced(3, e)], "s", ms=5, color="k")
    for x0 in (2, 3):
        ax.axvline(x0, color="gray", lw=.6)
    ax.set_xlabel(r"$\eta$"); ax.set_ylabel(r"$\rho_3(\eta)$")
    ax.set_title(r"$K=3$: reduced LP value vs closed-form pieces (breakpoints $\eta=2,3$)")
    ax.legend(fontsize=9); fig.tight_layout()
    figpath = os.path.join(HERE, "..", "figures", "T3_K3_pieces.png")
    fig.savefig(figpath, dpi=150)
    log(f"figure -> {os.path.abspath(figpath)}")

    OUT["closed_forms"] = {
        "K3": {"[1,2]": "(16*eta+3)/(3*(2*eta+1)**2)",
               "[2,3]": "7/(3*(2*eta+1))", "[3,oo)": "1/eta"},
        "K4": {"[1,2]": "(135*eta**2+36*eta+4)/(4*(3*eta+1)**3)",
               "[2,3]": "(21*eta+2)/(2*(3*eta+1)**2)",
               "[3,4]": "13/(4*(3*eta+1))", "[4,oo)": "1/eta"},
        "general_conjecture": "rho_K^LP(eta) = min_{0<=j<=K-1} V_j(eta), "
            "V_j = 1 - q^j (1 - (K-j)/(K eta)), q=(K-1)eta/((K-1)eta+1); "
            "V_j attains the min on [K-j, K-j+1]; V_{j-1}=V_j exactly at eta=K-j+1."}
    path = os.path.join(HERE, "T3_K3_closed_form.json")
    with open(path, "w") as fh:
        json.dump(OUT, fh, indent=1, default=str)
    log(f"json -> {path}")

if __name__ == "__main__":
    main()

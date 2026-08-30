"""N1: general-K dual certificate for the reduced LP (code/reduced_lp.py).

Goal: upgrade the R10 general-K CONJECTURE (rho_K^LP(eta) = min_j V_j) from
"numerically supported" to a symbolic theorem, by exhibiting, for every K >= 2,
every segment j = 0..K-1 and every eta in [K-j, K-j+1], an explicit DUAL
feasible solution y(K, j, eta) with b'y = V_j (the hard direction, LP >= V_j),
together with the T3 primal solution x(K, j, eta) with c'x = V_j (LP <= V_j).

CONVENTIONS
-----------
Primal (code/reduced_lp.py, row order preserved):
    min sum_t d_t   s.t.  A x <= b,  x >= 0,
    x = (d_0..d_{K-1}, g_{0,0}..g_{K,K-1}),
    for t = 0..K-1 the block of 1 + 3K rows is
      sum(t)     : -sum_i g_{t,i} - sum_{s<t} d_s        <= -1
      pred(t,i)  : g_{t,i}/eta - d_t                     <= 0
      mono(t,i)  : g_{t+1,i} - g_{t,i}                   <= 0
      cons(t,i)  : g_{t,i} - d_t - (1-1/eta) g_{t+1,i}   <= 0
Dual of  min c'x s.t. Ax <= b, x >= 0  is  max b'y s.t. A'y <= c, y <= 0.
That is scipy's `res.ineqlin.marginals` sign convention (marginals <= 0), and it
is the convention used everywhere below: the multipliers y are NON-POSITIVE.
Weak duality reads b'y <= c'x, so a dual-feasible y with b'y = V_j certifies
LP >= V_j.  (For a hand proof one uses lam = -y >= 0 as weights on the ">=" form
of the constraints; see results/N1_dual_certificate.md.)

NOTATION
--------
    k1 = (K-1) eta + 1,    q = (K-1) eta / k1 = 1 - 1/k1,
    M  = K eta - (K-j),    V_j = 1 - q^j (1 - (K-j)/(K eta)) = 1 - q^j M/(K eta).

DUAL FORMULA (this file's main object).  Multipliers are the same for every i
(symmetric in i), and y_mono = 0 throughout:
  segment j >= 1, eta in [K-j, K-j+1]:
    y_sum(0)   = -q^{j-1} M / (K k1)
    y_sum(t)   = -q^{j-1-t} M / k1^2                      (1 <= t <= j-1)
    y_sum(j)   = (eta - (K-j+1)) / k1
    y_sum(t)   = 0                                        (t > j)
    y_cons(t)  = -q^{j-1-t} M / (K k1)                    (0 <= t <= j-1)
    y_cons(t)  = -(K-1-t) / (K (eta-1))                   (j <= t <= K-1)
    y_pred(t)  = 0                                        (t < j)
    y_pred(t)  = -(eta - (K-t)) / (K (eta-1))             (j <= t <= K-1)
  segment j = 0, eta in [K, oo)   (this is the formula already reported in T3):
    y_sum(0) = -1/eta,  y_sum(t) = 0 (t >= 1),
    y_cons(t) = -(K-1-t)/(K(eta-1)),  y_pred(t) = -(eta-(K-t))/(K(eta-1)).

PRIMAL (from T3, results/T3_K3_closed_form.py; reused and re-verified here):
    d_t = q^t/k1  (t < j),   d_t = q^j/(K eta)  (t >= j),
    g_{t,i} = q^{min(t,j)}/K   (t = 0..K, every i).

Run:  python3 results/N1_dual_certificate.py
Exit code 0 iff every check passes.  Writes results/N1_dual_certificate.json.
"""
import json, os, sys, time
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "code"))

ETA = sp.Symbol("eta", positive=True)
RESULTS = []
T0 = time.time()


def check(part, name, passed, detail=""):
    RESULTS.append({"part": part, "name": name, "pass": bool(passed), "detail": str(detail)})
    print(f"  [{'PASS' if passed else 'FAIL'}] {name}" + (f"   ({detail})" if detail else ""))
    return bool(passed)


def is_zero(expr):
    """Exact symbolic test expr == 0 for rational functions."""
    return sp.simplify(sp.cancel(sp.together(expr))) == 0


# =====================================================================
# PART A -- dual feasibility A'y = c, symbolic in (K, j, t)
# =====================================================================
# Free symbols: K, j, t.  Powers of q are carried by a free positive symbol
# (Qp = q^{j-1-t} resp. Pp = q^{j-1}), so each identity holds for EVERY
# exponent, i.e. simultaneously for every t in the stated range.
K, J, T = sp.symbols("K j t", positive=True)
k1 = (K - 1) * ETA + 1
q = (K - 1) * ETA / k1
M = K * ETA - (K - J)
Qp = sp.Symbol("q_pow", positive=True)      # q^{j-1-t}
Pp = sp.Symbol("q_jm1", positive=True)      # q^{j-1}


def D2(ysum, ypred, ycons_t, ycons_tm1):
    """Dual constraint attached to the primal variable g_{t,i}
    (A'y)_{g_{t,i}} = -y_sum(t) + y_pred(t)/eta - y_mono(t) + y_mono(t-1)
                      + y_cons(t) - (1-1/eta) y_cons(t-1) = 0 = c_{g}.
    y_mono == 0 throughout, so the mono terms are dropped."""
    return -ysum + ypred / ETA + ycons_t - (1 - 1 / ETA) * ycons_tm1


def part_A():
    ok = True
    ysum_mid = -Qp * M / k1**2                    # y_sum(t),   1 <= t <= j-1
    ysum_0 = -Pp * M / (K * k1)                   # y_sum(0)
    ysum_j = (ETA - (K - J + 1)) / k1             # y_sum(j)
    ycons_low = -Qp * M / (K * k1)                # y_cons(t),  t <= j-1
    ycons_low_prev = -Qp * q * M / (K * k1)       # y_cons(t-1) = q * y_cons(t)
    ycons_0 = -Pp * M / (K * k1)                  # y_cons(0)
    ycons_jm1 = -M / (K * k1)                     # y_cons(j-1), exponent 0
    yp_hi = lambda tt: -(ETA - (K - tt)) / (K * (ETA - 1))
    yc_hi = lambda tt: -(K - 1 - tt) / (K * (ETA - 1))

    ok &= check("A", "D2 at t=0 (j>=1): y_sum(0) = y_cons(0) forces it",
                is_zero(D2(ysum_0, 0, ycons_0, 0)))
    ok &= check("A", "D2 for 1 <= t <= j-1",
                is_zero(D2(ysum_mid, 0, ycons_low, ycons_low_prev)))
    ok &= check("A", "D2 at t=j (j>=1)",
                is_zero(D2(ysum_j, yp_hi(J), yc_hi(J), ycons_jm1)))
    ok &= check("A", "D2 for j+1 <= t <= K-1",
                is_zero(D2(0, yp_hi(T), yc_hi(T), yc_hi(T - 1))))
    ok &= check("A", "D2 at t=K (needs y_cons(K-1) = 0)", is_zero(yc_hi(K - 1)))
    ok &= check("A", "D2 at t=0 for the j=0 segment",
                is_zero(D2(-1 / ETA, yp_hi(0), yc_hi(0), 0)))

    # ---- D1: dual constraint attached to d_t --------------------------
    #   (A'y)_{d_t} = -sum_{s>t} y_sum(s) - K (y_pred(t) + y_cons(t)) = 1 = c_{d_t}
    ok &= check("A", "D1 for t >= j: y_pred(t) + y_cons(t) = -1/K  (and sum_{s>t} y_sum(s) = 0)",
                is_zero(yp_hi(T) + yc_hi(T) + 1 / K))
    ok &= check("A", "D1 base at t=j-1: -y_sum(j) - K y_cons(j-1) = 1",
                is_zero(-ysum_j - K * ycons_jm1 - 1))
    #   downward induction step for t <= j-2:  (D1_t) - (D1_{t+1}) = 0, i.e.
    #   -y_sum(t+1) - K y_cons(t) + K y_cons(t+1) = 0.
    #   With Qp = q^{j-1-t}: y_sum(t+1) = -(Qp/q) M/k1^2, y_cons(t+1) = -(Qp/q) M/(K k1).
    ok &= check("A", "D1 downward induction step for t <= j-2",
                is_zero(-(-(Qp / q) * M / k1**2) - K * (-Qp * M / (K * k1))
                        + K * (-(Qp / q) * M / (K * k1))))

    # ---- b'y = V_j  (b = -1 on the sum rows, 0 elsewhere) ---------------
    #   b'y = -sum_{t=0}^{j} y_sum(t) = -y_sum(0) - S_0 with
    #   S_0 = sum_{s>0} y_sum(s) = -1 - K (y_pred(0) + y_cons(0))   [that is D1 at t=0].
    #   For j >= 1: y_pred(0) = 0, y_cons(0) = y_sum(0) = -q^{j-1} M/(K k1).
    Vj = 1 - Pp * q * M / (K * ETA)               # V_j, using q^j = q^{j-1} q
    bty = -ysum_0 - (-1 - K * (0 + ycons_0))
    ok &= check("A", "b'y = V_j for j >= 1", is_zero(bty - Vj))
    ok &= check("A", "b'y = V_0 = 1/eta for j = 0",
                is_zero(1 / ETA - (1 - (K * ETA - K) / (K * ETA))))
    return ok


# =====================================================================
# PART B -- primal feasibility and c'x = V_j, symbolic in (K, j, t)
# =====================================================================
def part_B():
    ok = True
    A = sp.Symbol("q_t", positive=True)           # stands for q^t (t <= j) or q^j
    # partial sums P_t = sum_{s<t} d_s, established by induction on t:
    #   claim 1 (t <= j): P_t = 1 - q^t.  Base P_0 = 0 = 1 - q^0.
    ok &= check("B", "P_t = 1-q^t for t<=j: step (1-q^{t+1}) - (1-q^t) = d_t = q^t/k1",
                is_zero((1 - A * q) - (1 - A) - A / k1))
    #   claim 2 (t >= j): P_t = 1 - q^j + (t-j) q^j/(K eta), base t=j agrees with claim 1.
    ok &= check("B", "P_t for t>=j: step = d_t = q^j/(K eta)",
                is_zero((1 - A + (T - J + 1) * A / (K * ETA))
                        - (1 - A + (T - J) * A / (K * ETA)) - A / (K * ETA)))
    ok &= check("B", "P_t claims agree at t=j",
                is_zero((1 - A) - (1 - A + (J - J) * A / (K * ETA))))
    # constraints (G_t = q^{min(t,j)}/K)
    ok &= check("B", "sum(t) is TIGHT for t <= j:  K G_t = q^t = r_t",
                is_zero(K * (A / K) - (1 - (1 - A))))
    ok &= check("B", "sum(t) slack for t > j equals (t-j) q^j/(K eta) >= 0",
                is_zero((K * (A / K) - (1 - (1 - A + (T - J) * A / (K * ETA))))
                        - (T - J) * A / (K * ETA)))
    ok &= check("B", "pred(t) slack for t < j equals q^t (eta-1)/(K eta k1) >= 0",
                is_zero((A / k1 - A / (K * ETA)) - A * (ETA - 1) / (K * ETA * k1)))
    ok &= check("B", "pred(t) is TIGHT for t >= j", is_zero(A / (K * ETA) - (A / K) / ETA))
    ok &= check("B", "mono(t) slack for t < j equals q^t/(K k1) > 0",
                is_zero((A / K - A * q / K) - A / (K * k1)))
    ok &= check("B", "mono(t) is TIGHT for t >= j (G frozen)", is_zero(A / K - A / K))
    ok &= check("B", "cons(t) is TIGHT for t < j",
                is_zero((1 - 1 / ETA) * A * q / K - A / K + A / k1))
    ok &= check("B", "cons(t) is TIGHT for t >= j",
                is_zero((1 - 1 / ETA) * A / K - A / K + A / (K * ETA)))
    ok &= check("B", "c'x = P_K = 1 - q^j(1-(K-j)/(K eta)) = V_j",
                is_zero((1 - A + (K - J) * A / (K * ETA)) - (1 - A * (1 - (K - J) / (K * ETA)))))
    return ok


# =====================================================================
# PART C -- sign conditions y <= 0 on the segment, symbolic in (K, j, t)
# =====================================================================
# Segment j >= 1 is parametrised by  eta = u + s,  u = K - j in [1, K-1],
# s in [0, 1];  high-branch index t = j + m with m in [0, u-1], so
# K-1-t = u-1-m >= 0.  Every sign claim is reduced to "this polynomial has
# only nonnegative coefficients after every variable is shifted to its lower
# bound", which is an exact certificate on the box.
KK, VV, SS, MM, NN, WW = sp.symbols("kk vv ss mm nn ww", nonnegative=True)
GENS = (KK, VV, SS, MM, NN, WW)


def poly_nonneg(expr, strict=False):
    """Certify expr >= 0 (strict: > 0) on {GENS >= 0} by nonnegative coefficients."""
    p = sp.Poly(sp.expand(expr), *GENS)
    coeffs = p.coeffs()
    ok = all(c >= 0 for c in coeffs) if coeffs else True
    if strict:
        ok = ok and p.coeff_monomial(1) > 0
    return bool(ok), f"coeffs={coeffs}"


def part_C():
    ok = True
    Ke = 2 + KK                       # K >= 2
    ue = 1 + VV                       # u = K - j >= 1
    eta_e = ue + SS                   # eta = u + s, s in [0,1]
    k1e = (Ke - 1) * eta_e + 1
    Me = Ke * eta_e - ue              # M = K eta - (K-j)

    r, d = poly_nonneg(k1e, strict=True)
    ok &= check("C", "k1 > 0 on segment j>=1", r, d)
    r, d = poly_nonneg((Ke - 1) * eta_e, strict=True)
    ok &= check("C", "numerator of q is > 0  =>  q > 0", r, d)
    r, d = poly_nonneg(Me, strict=True)
    ok &= check("C", "M = K eta - (K-j) > 0 on segment j>=1", r, d)
    # -y_sum(j) = (K-j+1-eta)/k1 = (1-s)/k1 : numerator = 1-s = ww >= 0 (s = 1-ww)
    r, d = poly_nonneg(sp.expand((ue + 1 - eta_e).subs(SS, 1 - WW)))
    ok &= check("C", "-y_sum(j) numerator = K-j+1-eta = 1-s >= 0 (=0 at eta=K-j+1)", r, d)
    # -y_sum(0) = q^{j-1} M/(K k1), -y_sum(t) = q^{j-1-t} M/k1^2,
    # -y_cons(t) = q^{j-1-t} M/(K k1)  (t <= j-1): all are (positive)*(M)/(positive)
    r, d = poly_nonneg(Ke * k1e, strict=True)
    ok &= check("C", "K k1 > 0  =>  y_sum(0), y_cons(t<=j-1) <= 0 (with q>0, M>0)", r, d)
    r, d = poly_nonneg(sp.expand(k1e**2), strict=True)
    ok &= check("C", "k1^2 > 0  =>  y_sum(1..j-1) <= 0", r, d)
    # high branch with j <= K-2  <=>  u >= 2 : eta - 1 = u + s - 1 >= 1 > 0
    u2 = 2 + VV
    r, d = poly_nonneg(Ke * (u2 + SS - 1), strict=True)
    ok &= check("C", "j<=K-2: K(eta-1) > 0 on [K-j, K-j+1]", r, d)
    r, d = poly_nonneg(SS + MM)
    ok &= check("C", "-y_pred(j+m) numerator = eta-(K-j-m) = s+m >= 0 (=0 at eta=K-j, m=0)", r, d)
    r, d = poly_nonneg(NN)
    ok &= check("C", "-y_cons(j+m) numerator = K-1-t = u-1-m >= 0", r, d)
    # j = K-1 (segment [1,2], u = 1): the only high-branch index is t = K-1 = j,
    # where both formulas are removable at eta = 1.
    ok &= check("C", "j=K-1: y_pred(K-1) = -(eta-1)/(K(eta-1)) = -1/K (removable at eta=1)",
                is_zero(sp.cancel(-(ETA - 1) / (K * (ETA - 1))) + 1 / K))
    ok &= check("C", "j=K-1: y_cons(K-1) = -(K-1-(K-1))/(K(eta-1)) = 0",
                is_zero(sp.cancel(-(K - 1 - (K - 1)) / (K * (ETA - 1)))))
    # j = 0 segment: eta = K + s, s >= 0.
    eta0 = Ke + SS
    r, d = poly_nonneg(Ke * (eta0 - 1), strict=True)
    ok &= check("C", "j=0: K(eta-1) > 0 on [K,oo)", r, d)
    r, d = poly_nonneg(sp.expand((eta0 - (Ke - MM))))
    ok &= check("C", "j=0: -y_pred(t) numerator = eta-(K-t) = s+t >= 0 on [K,oo)", r, d)
    r, d = poly_nonneg(NN)
    ok &= check("C", "j=0: -y_cons(t) numerator = K-1-t >= 0", r, d)
    r, d = poly_nonneg(eta0, strict=True)
    ok &= check("C", "j=0: -y_sum(0) = 1/eta > 0", r, d)
    return ok


# =====================================================================
# PART D -- V_j = min_i V_i on segment j, symbolic in (K, j, i)
# =====================================================================
def part_D():
    ok = True
    I = sp.Symbol("i", nonnegative=True)
    QI = sp.Symbol("q_i", positive=True)          # q^i
    Vi = 1 - QI * (1 - (K - I) / (K * ETA))
    Vi1 = 1 - QI * q * (1 - (K - I - 1) / (K * ETA))
    ok &= check("D", "V_i - V_{i+1} = q^i (K-i-eta) / (K eta k1)",
                is_zero((Vi - Vi1) - QI * (K - I - ETA) / (K * ETA * k1)))
    # on eta = (K-j) + s, s in [0,1]:
    #   i <= j-1, i = j-1-a  =>  K-i-eta = 1 + a - s >= 0  (so V_i >= V_{i+1})
    #   i >= j,   i = j+a     =>  K-i-eta = -a - s <= 0    (so V_i <= V_{i+1})
    A_ = sp.Symbol("aa", nonnegative=True)
    Kx, Jx = sp.Symbol("Kx", positive=True), sp.Symbol("Jx", positive=True)
    eta_seg = (Kx - Jx) + SS
    r, d = poly_nonneg(sp.expand((Kx - (Jx - 1 - A_) - eta_seg).subs(SS, 1 - WW)
                                 .subs(A_, MM)))
    ok &= check("D", "i<=j-1 on segment: K-i-eta = 1+a-s >= 0", r, d)
    r, d = poly_nonneg(sp.expand(-(Kx - (Jx + A_) - eta_seg).subs(A_, MM)))
    ok &= check("D", "i>=j on segment: -(K-i-eta) = a+s >= 0", r, d)
    ok &= check("D", "V_0 = 1/eta", is_zero((1 - (1 - K / (K * ETA))) - 1 / ETA))
    ok &= check("D", "V_j - V_{j-1} = 0 exactly at eta = K-j+1 (breakpoints are integers)",
                is_zero((QI * (K - (J - 1) - ETA) / (K * ETA * k1)).subs(ETA, K - J + 1)))
    # relation to the R7 explicit-instance upper bound U_K = 1 - (1-1/k1)^K = 1 - q^K
    QK1 = sp.Symbol("q_Km1", positive=True)               # q^{K-1}
    U_K = 1 - QK1 * q
    V_Km1 = 1 - QK1 * (1 - 1 / (K * ETA))
    ok &= check("D", "U_K - V_{K-1} = q^{K-1}(eta-1)/(K eta k1) >= 0 for eta >= 1",
                is_zero((U_K - V_Km1) - QK1 * (ETA - 1) / (K * ETA * k1)))
    return ok


# =====================================================================
# PART E -- explicit K = 2..KMAX: full matrix certificate, symbolic eta
# =====================================================================
def build_lp(Kv, e):
    """Reduced LP rebuilt symbolically; same row order as code/reduced_lp.py."""
    nd = Kv
    gi = lambda t, i: nd + t * Kv + i
    nv = nd + (Kv + 1) * Kv
    rows, b, labels = [], [], []

    def add(coefs, rhs, lab):
        rows.append(dict(coefs)); b.append(rhs); labels.append(lab)

    for t in range(Kv):
        c = {gi(t, i): sp.Integer(-1) for i in range(Kv)}
        for s in range(t):
            c[s] = sp.Integer(-1)
        add(c, sp.Integer(-1), ("sum", t, None))
        for i in range(Kv):
            add({gi(t, i): 1 / e, t: sp.Integer(-1)}, sp.Integer(0), ("pred", t, i))
            add({gi(t + 1, i): sp.Integer(1), gi(t, i): sp.Integer(-1)},
                sp.Integer(0), ("mono", t, i))
            add({gi(t, i): sp.Integer(1), t: sp.Integer(-1), gi(t + 1, i): -(1 - 1 / e)},
                sp.Integer(0), ("cons", t, i))
    c_obj = [sp.Integer(1)] * Kv + [sp.Integer(0)] * ((Kv + 1) * Kv)
    return rows, b, c_obj, labels, nv


def primal_vec(Kv, j, e):
    k1v = (Kv - 1) * e + 1
    qv = (Kv - 1) * e / k1v
    d = [qv**t / k1v for t in range(j)] + [qv**j / (Kv * e) for _ in range(j, Kv)]
    g = []
    for t in range(Kv + 1):
        g += [qv**min(t, j) / Kv] * Kv
    return d + g


def dual_dict(Kv, j, e):
    """Per-(type, t) multiplier (identical for every i); scipy marginals sign."""
    k1v = (Kv - 1) * e + 1
    qv = (Kv - 1) * e / k1v
    Mv = Kv * e - (Kv - j)
    ys = {t: sp.Integer(0) for t in range(Kv)}
    yc = {t: sp.Integer(0) for t in range(Kv)}
    yp = {t: sp.Integer(0) for t in range(Kv)}
    if j == 0:
        ys[0] = -1 / e
        for t in range(Kv):
            yc[t] = sp.cancel(sp.Integer(-(Kv - 1 - t)) / (Kv * (e - 1)))
            yp[t] = sp.cancel(-(e - (Kv - t)) / (Kv * (e - 1)))
    else:
        ys[0] = -qv**(j - 1) * Mv / (Kv * k1v)
        for t in range(1, j):
            ys[t] = -qv**(j - 1 - t) * Mv / k1v**2
        ys[j] = (e - (Kv - j + 1)) / k1v
        for t in range(j):
            yc[t] = -qv**(j - 1 - t) * Mv / (Kv * k1v)
        for t in range(j, Kv):
            yc[t] = sp.cancel(sp.Integer(-(Kv - 1 - t)) / (Kv * (e - 1)))
            yp[t] = sp.cancel(-(e - (Kv - t)) / (Kv * (e - 1)))
    return ys, yc, yp


def nonpos_on(expr, lo, hi, _memo={}):
    """Exact proof that expr(eta) <= 0 for every eta in [lo, hi] (hi=None -> +oo):
    Sturm root counting on numerator and denominator + sign at an interior
    rational point and at the finite endpoints."""
    expr = sp.cancel(sp.together(expr))
    key = (sp.srepr(expr), str(lo), str(hi))
    if key in _memo:
        return _memo[key]
    res = _nonpos_on(expr, lo, hi)
    _memo[key] = res
    return res


def _nonpos_on(expr, lo, hi):
    if expr == 0:
        return True, "identically 0"
    num, den = sp.fraction(expr)
    num, den = sp.expand(num), sp.expand(den)
    lo = sp.Rational(lo)
    pn, pd = sp.Poly(num, ETA), sp.Poly(den, ETA)
    ref = lo + 1 if hi is None else (lo + sp.Rational(hi)) / 2

    def roots_in(poly, a, b):
        if poly.degree() == 0:
            return 0
        if b is None:
            cs = poly.all_coeffs()
            B = a + 1 + max(abs(sp.Rational(cc)) for cc in cs) / abs(sp.Rational(cs[0]))
        else:
            B = sp.Rational(b)
        return poly.count_roots(a, B)

    if roots_in(pd, lo, hi) != 0 or pd.eval(ref) == 0:
        return False, "denominator vanishes in the interval"
    nr = roots_in(pn, lo, hi) - int(pn.eval(lo) == 0)
    if hi is not None:
        nr -= int(pn.eval(sp.Rational(hi)) == 0)
    if nr != 0:
        return False, f"numerator has {nr} root(s) in the open interval"
    if pn.eval(ref) * pd.eval(ref) > 0:
        return False, f"positive at eta={ref}"
    for pt in ([lo] if hi is None else [lo, sp.Rational(hi)]):
        if pn.eval(pt) * pd.eval(pt) > 0:
            return False, f"positive at eta={pt}"
    return True, "ok"


def part_E(KMAX=8):
    ok = True
    detail = {}
    for Kv in range(2, KMAX + 1):
        rows, b, c_obj, labels, nv = build_lp(Kv, ETA)
        for j in range(Kv):
            t_seg = time.time()
            lo, hi = (Kv - j), (None if j == 0 else Kv - j + 1)
            ys, yc, yp = dual_dict(Kv, j, ETA)
            table = {"sum": ys, "pred": yp, "cons": yc}
            yvec = [sp.Integer(0) if typ == "mono" else table[typ][t]
                    for (typ, t, i) in labels]
            x = primal_vec(Kv, j, ETA)
            Vj = sp.cancel(1 - ((Kv - 1) * ETA / ((Kv - 1) * ETA + 1))**j
                           * (1 - sp.Rational(Kv - j, Kv) / ETA))
            tag = f"K={Kv} j={j} eta in [{lo},{'oo' if hi is None else hi}]"

            # (1) A'y = c  (equalities: every primal variable is strictly positive)
            acc = [sp.Integer(0)] * nv
            for r, row in enumerate(rows):
                if yvec[r] == 0:
                    continue
                for col, v in row.items():
                    acc[col] += v * yvec[r]
            bad = [kk for kk in range(nv) if sp.cancel(acc[kk] - c_obj[kk]) != 0]
            ok &= check("E", f"{tag}: A'y = c", not bad, f"{len(bad)} bad columns")

            # (2) y <= 0 on the segment
            bad2 = []
            for r, yr in enumerate(yvec):
                good, why = nonpos_on(yr, lo, hi)
                if not good:
                    bad2.append((labels[r], why))
            ok &= check("E", f"{tag}: y <= 0 on segment", not bad2, str(bad2[:2]))

            # (3) A x <= b and x >= 0 on the segment
            bad3 = []
            for r, row in enumerate(rows):
                lhs = sum(v * x[col] for col, v in row.items())
                good, why = nonpos_on(sp.cancel(lhs - b[r]), lo, hi)
                if not good:
                    bad3.append((labels[r], why))
            for col in range(nv):
                good, why = nonpos_on(-x[col], lo, hi)
                if not good:
                    bad3.append((("var", col), why))
            ok &= check("E", f"{tag}: A x <= b and x >= 0 on segment", not bad3, str(bad3[:2]))

            # (4) b'y = c'x = V_j
            bty = sp.cancel(sum(b[r] * yvec[r] for r in range(len(rows))))
            ctx = sp.cancel(sum(c_obj[kk] * x[kk] for kk in range(nv)))
            ok &= check("E", f"{tag}: b'y = V_j", sp.cancel(bty - Vj) == 0,
                        f"b'y = {sp.factor(bty)}  ({time.time()-t_seg:.1f}s)")
            ok &= check("E", f"{tag}: c'x = V_j", sp.cancel(ctx - Vj) == 0)
            detail[tag] = {"V_j": str(sp.factor(Vj)), "b_dot_y": str(sp.factor(bty))}
    return ok, detail


# =====================================================================
# PART F -- numerical cross-checks against scipy
# =====================================================================
def part_F(KMAX=8):
    import numpy as np
    from reduced_lp import reduced
    ok = True
    out = {"dual_match": [], "value_match": []}

    def row_label(Kv, row):
        per = 1 + 3 * Kv
        t, jj = divmod(row, per)
        if jj == 0:
            return ("sum", t, None)
        i, kk = divmod(jj - 1, 3)
        return (["pred", "mono", "cons"][kk], t, i)

    # (F1) K = 2..6, every segment, eta = K-j+{1/4, 1/2, 3/4}:
    #   (F1a) the closed-form y is numerically DUAL FEASIBLE and OPTIMAL;
    #   (F1b) it agrees with scipy's dual symmetrised over i, at every point where
    #         that symmetrised dual lies on the same face (all mono multipliers 0).
    #   The reduced LP is primal-degenerate at some points, so the dual optimum is
    #   a face rather than a vertex and scipy may report a different point of it;
    #   those points are listed explicitly in the json as `dual_face_degenerate`.
    worstA, worstA_at = 0.0, None
    worstB, worstB_at, degen = 0.0, None, []
    for Kv in range(2, 7):
        rows_s, b_s, c_s, labels_s, nv_s = build_lp(Kv, ETA)
        for j in range(Kv):
            for frac in (sp.Rational(1, 4), sp.Rational(1, 2), sp.Rational(3, 4)):
                e = sp.Rational(Kv - j) + frac
                ef = float(e)
                val, res = reduced(Kv, ef, return_sol=True)
                assert res.status == 0, (Kv, ef, res.status)
                agg = {}
                for r, m in enumerate(res.ineqlin.marginals):
                    typ, t, i = row_label(Kv, r)
                    agg.setdefault((typ, t), []).append(m)
                obs = {kk: float(np.mean(v)) for kk, v in agg.items()}
                ys, yc, yp = dual_dict(Kv, j, e)
                table = {"sum": ys, "pred": yp, "cons": yc}
                pred = {}
                for t in range(Kv):
                    pred[("sum", t)] = float(ys[t])
                    pred[("cons", t)] = float(yc[t])
                    pred[("pred", t)] = float(yp[t])
                    pred[("mono", t)] = 0.0
                # (F1a) dual feasibility / optimality of OUR y, numerically
                acc = np.zeros(nv_s)
                bty = 0.0
                for r, row in enumerate(rows_s):
                    typ, t, i = labels_s[r]
                    yv = 0.0 if typ == "mono" else float(table[typ][t])
                    if yv == 0.0:
                        continue
                    bty += float(b_s[r]) * yv
                    for col, v in row.items():
                        acc[col] += float(v.subs(ETA, e)) * yv
                viol = max(float(np.max(acc - np.array([float(cc) for cc in c_s]))), 0.0)
                viol = max(viol, max(0.0, max(pred.values())))          # y <= 0
                viol = max(viol, abs(bty - float(val)))                 # b'y = LP
                if viol > worstA:
                    worstA, worstA_at = viol, (Kv, j, ef)
                # (F1b) agreement with the symmetrised scipy dual
                monomax = max(abs(obs.get(("mono", t), 0.0)) for t in range(Kv))
                scale = max(1.0, max(abs(v) for v in pred.values()))
                err = max(abs(pred[kk] - obs.get(kk, 0.0)) for kk in pred) / scale
                if monomax < 1e-9:
                    if err > worstB:
                        worstB, worstB_at = err, (Kv, j, ef)
                else:
                    degen.append({"K": Kv, "j": j, "eta": ef, "rel_dev": err,
                                  "scipy_max_mono_multiplier": monomax})
                out["dual_match"].append({"K": Kv, "j": j, "eta": ef, "rel_dev_vs_scipy": err,
                                          "our_dual_violation": viol, "lp": float(val),
                                          "scipy_max_mono_multiplier": monomax})
    ok &= check("F", "closed-form y is dual feasible AND optimal (b'y = LP), K=2..6, every segment",
                worstA < 1e-9, f"max violation {worstA:.2e} at {worstA_at}")
    ok &= check("F", "closed form = scipy dual symmetrised over i, wherever scipy stays on the "
                     "same face (mono multipliers 0)",
                worstB < 1e-8,
                f"max rel dev {worstB:.2e} at {worstB_at}; "
                f"{len(degen)}/60 points had a degenerate dual face")
    out["dual_face_degenerate"] = degen

    # (F2) LP value vs V_{j(eta)} on a grid, K = 2..KMAX
    worst2, worst2_at = 0.0, None
    for Kv in range(2, KMAX + 1):
        for e10 in range(10, 10 * (Kv + 2) + 1, 3):
            ef = e10 / 10.0
            j = 0 if ef >= Kv else Kv - int(np.floor(ef))
            k1v = (Kv - 1) * ef + 1
            qv = (Kv - 1) * ef / k1v
            V = 1 - qv**j * (1 - (Kv - j) / (Kv * ef))
            val = reduced(Kv, ef)
            if abs(val - V) > worst2:
                worst2, worst2_at = abs(val - V), (Kv, ef)
            out["value_match"].append({"K": Kv, "eta": ef, "j": j,
                                       "lp": float(val), "V_j": float(V)})
    ok &= check("F", f"LP value = V_{{j(eta)}} on grid, K=2..{KMAX}",
                worst2 < 1e-9, f"max abs dev {worst2:.2e} at {worst2_at}")

    # (F3) corollary of y_mono == 0: deleting the mono(t,i) rows does not change
    #      the optimal value (the certificate never uses them).  Numeric check.
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix

    def reduced_nomono(Kv, eta):
        nd = Kv
        gi = lambda t, i: nd + t * Kv + i
        nv = nd + (Kv + 1) * Kv
        rows, cols, vals, bb = [], [], [], []
        r = 0
        def ub(c, rhs=0.0):
            nonlocal r
            for kk, v in c.items():
                rows.append(r); cols.append(kk); vals.append(v)
            bb.append(rhs); r += 1
        for t in range(Kv):
            c = {gi(t, i): -1.0 for i in range(Kv)}
            for s in range(t):
                c[s] = -1.0
            ub(c, -1.0)
            for i in range(Kv):
                ub({gi(t, i): 1.0 / eta, t: -1.0})
                ub({gi(t, i): 1.0, t: -1.0, gi(t + 1, i): -(1 - 1 / eta)})
        A = coo_matrix((vals, (rows, cols)), shape=(r, nv)).tocsr()
        obj = np.zeros(nv); obj[:Kv] = 1
        return linprog(obj, A_ub=A, b_ub=np.array(bb),
                       bounds=[(0, None)] * nv, method="highs").fun

    worst3, worst3_at = 0.0, None
    for Kv in range(2, min(KMAX, 7) + 1):
        for e10 in range(10, 10 * (Kv + 2) + 1, 5):
            ef = e10 / 10.0
            dv = abs(reduced(Kv, ef) - reduced_nomono(Kv, ef))
            if dv > worst3:
                worst3, worst3_at = dv, (Kv, ef)
    ok &= check("F", "corollary y_mono=0: dropping the mono(t,i) rows leaves the LP value unchanged",
                worst3 < 1e-9, f"max abs dev {worst3:.2e} at {worst3_at}")
    out["mono_redundant_max_dev"] = worst3

    # (F4) sandwich L_K <= min_j V_j <= U_K (R1 lower bound / R7 explicit instance),
    #      numeric only for the L_K side.
    def Vf(Kv, j, e):
        k1v = (Kv - 1) * e + 1
        return 1 - ((Kv - 1) * e / k1v)**j * (1 - (Kv - j) / (Kv * e))
    dL, dU, at = 0.0, 0.0, None
    for Kv in range(2, 25):
        for e in np.linspace(1.0, 3.0 * Kv, 200):
            mv = min(Vf(Kv, j, e) for j in range(Kv))
            LK = 1 - (1 - 1 / (e * Kv))**Kv
            UK = 1 - (1 - 1 / ((Kv - 1) * e + 1))**Kv
            if LK - mv > dL:
                dL, at = LK - mv, (Kv, e)
            dU = max(dU, mv - UK)
    ok &= check("F", "sandwich L_K(eta) <= min_j V_j(eta) <= U_K(eta), K=2..24 grid",
                dL < 1e-12 and dU < 1e-12,
                f"max L_K excess {dL:.2e} at {at}, max U_K excess {dU:.2e}")
    out["sandwich"] = {"max_L_excess": dL, "max_U_excess": dU}
    return ok, out


# =====================================================================
# PART G -- agreement with the T3 published multipliers (K = 2, 3, 4)
# =====================================================================
def part_G():
    path = os.path.join(HERE, "T3_K3_closed_form.json")
    if not os.path.exists(path):
        return check("G", "T3 json present", False, "file missing"), {}
    data = json.load(open(path))
    sc = data["parts"]["symbolic_certificates"]
    mism, n = [], 0
    for Kstr, blob in sc.items():
        Kv = int(Kstr)
        for seg in blob["segments"]:
            j = seg["j"]
            ys, yc, yp = dual_dict(Kv, j, ETA)
            mine = {}
            for t in range(Kv):
                for nm, dd in (("sum", ys), ("pred", yp), ("cons", yc)):
                    if sp.cancel(dd[t]) != 0:
                        mine[f"{nm}({t})"] = sp.cancel(dd[t])
            theirs = {kk: sp.cancel(sp.sympify(v, locals={"eta": ETA}))
                      for kk, v in seg["dual_multipliers"].items()}
            for kk in set(mine) | set(theirs):
                n += 1
                if sp.cancel(mine.get(kk, sp.Integer(0)) - theirs.get(kk, sp.Integer(0))) != 0:
                    mism.append((Kv, j, kk))
    ok = check("G", "general-K formula reproduces EVERY T3 multiplier (K=2,3,4, all 9 segments)",
               not mism, f"{n} multipliers compared, {len(mism)} mismatches {mism[:3]}")
    return ok, {"compared": n, "mismatches": [str(m) for m in mism]}


# =====================================================================
def main():
    kmax_E = int(os.environ.get("N1_KMAX", "10"))
    print("=" * 78)
    print("N1: general-K dual certificate for the reduced LP  (results/N1_dual_certificate.py)")
    print("=" * 78)
    all_ok = True
    print("\n--- PART A: dual feasibility A'y = c, symbolic in (K, j, t) ---")
    all_ok &= part_A()
    print("\n--- PART B: primal feasibility and c'x = V_j, symbolic in (K, j, t) ---")
    all_ok &= part_B()
    print("\n--- PART C: sign conditions y <= 0 on the segment, symbolic in (K, j, t) ---")
    all_ok &= part_C()
    print("\n--- PART D: V_j = min_i V_i on segment j, symbolic in (K, j, i) ---")
    all_ok &= part_D()
    print(f"\n--- PART E: full matrix certificate, K = 2..{kmax_E}, symbolic eta ---")
    okE, detE = part_E(kmax_E)
    all_ok &= okE
    print("\n--- PART F: numerical cross-checks against scipy ---")
    okF, detF = part_F(kmax_E)
    all_ok &= okF
    print("\n--- PART G: agreement with the T3 published multipliers ---")
    okG, detG = part_G()
    all_ok &= okG

    npass = sum(1 for r in RESULTS if r["pass"])
    print("\n" + "=" * 78)
    print(f"{npass}/{len(RESULTS)} checks passed   ({time.time()-T0:.1f} s)")
    print("OVERALL:", "PASS" if all_ok else "FAIL")
    blob = {"overall": "PASS" if all_ok else "FAIL",
            "n_checks": len(RESULTS), "n_pass": npass,
            "KMAX_explicit": kmax_E,
            "checks": RESULTS, "segments_explicit": detE,
            "numeric": detF, "T3_agreement": detG,
            "runtime_s": round(time.time() - T0, 1)}
    with open(os.path.join(HERE, "N1_dual_certificate.json"), "w") as fh:
        json.dump(blob, fh, indent=1)
    print("wrote", os.path.join(HERE, "N1_dual_certificate.json"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

"""V11 Q8 criterion B, route comparison oracle for thm:linear-anysize (ledger T10d, J7).

Route one  = paper/sections/appendix_proofs.tex, subsection app:hardness-anysize
             (+ results/J7/linear_anysize.md, THEOREM_LEDGER.md section T10d).
Route two  = results/V11/route2/linear_anysize.md (blind derivation).

This script is the judge's own oracle; it does not import either route's scripts.
Every decision is exact (sympy identities or fractions.Fraction); floats appear
only inside printouts.

Blocks
  A  symbolic: the two routes' d(m), Theta/B_m, Psi rules and the three shared
     identities are the same object                              [VERIFIED-SYMBOLIC]
  B  exhaustive: the family built with route two's j convention is a legal
     instance (monotone submodular, band, zero pattern, P1/P2/P3)  [VERIFIED-EXHAUSTIVE]
  C  exhaustive: the j conventions of the two routes differ exactly at integer
     eta with 2 <= eta <= K, and there route one's W_K is strictly smaller
                                                                  [VERIFIED-EXHAUSTIVE]
  D  exhaustive: 0 <= W_K - rho_K < 1/(K(e^{K-1}-K-1)) for BOTH j conventions,
     with e replaced by the rational upper bound 2719/1000         [VERIFIED-EXHAUSTIVE]
  E  exhaustive: route two's step D5 sentence "alpha_{K+1} = 1" is refuted by
     route two's own step U1 family at n = K+1                     [FAILED for route two]

Run: python3 results/V11/compare/judge_linear_anysize_checks.py
"""

from fractions import Fraction as F

import sympy as sp

FAILED = []


def check(name, ok, detail=""):
    if not ok:
        FAILED.append((name, detail))
    print(("  PASS  " if ok else "  FAIL  ") + name + ((" | " + detail) if detail else ""))


# ---------------------------------------------------------------- block A
def block_a():
    print("[A] symbolic identities (sympy)")
    K, eta, t, m = sp.symbols("K eta t m", positive=True)
    nu = eta / (eta - 1)

    Theta = eta * nu**m - m - eta                      # route two
    B_m = eta * (nu**m - 1) - m                        # route one
    d2 = (nu**m - K) / (K * Theta)                     # route two (3.3)
    d1 = (nu**m / K - 1) / B_m                         # route one (6)

    check("A1 Theta(m) == B_m", sp.simplify(Theta - B_m) == 0)
    check("A2 d_route2 == d_route1", sp.simplify(d1 - d2) == 0)
    check("A3 (3.4) d - 1/(K eta) = (m - eta(K-1))/(K eta Theta)",
          sp.simplify(d2 - 1 / (K * eta) - (m - eta * (K - 1)) / (K * eta * Theta)) == 0)

    Psi1 = lambda z: (K * eta - z - 1) * nu**z - K * (eta - 1)
    check("A4 route one id1  d - 1/(m+1) = -Psi1(m)/(K(m+1)B_m)",
          sp.simplify(d1 - 1 / (m + 1) + Psi1(m) / (K * (m + 1) * B_m)) == 0)
    check("A5 route one id2  1/m - d = nu Psi1(m-1)/(K m B_m)",
          sp.simplify(1 / m - d1 - nu * Psi1(m - 1) / (K * m * B_m)) == 0)

    # route two's Psi2(t) = 1 - (t+1) d(t) has the same sign as route one's Psi1(t)
    dt = (nu**t - K) / (K * (eta * nu**t - t - eta))
    ratio = sp.simplify((1 - (t + 1) * dt) / (Psi1(t) / (K * (eta * nu**t - t - eta))))
    check("A6 Psi2(t) == Psi1(t)/(K Theta(t))  (same sign, same m)", sp.simplify(ratio - 1) == 0,
          f"ratio={ratio}")

    # route two (3.5)
    Th = lambda z: eta * nu**z - z - eta
    s = m - eta * (K - 1)
    check("A7 route two (3.5) s Theta(m-1) - (s-1) Theta(m) = nu^m(K eta - m) - K eta",
          sp.simplify(sp.expand(s * Th(m - 1) - (s - 1) * Th(m)
                                - (nu**m * (K * eta - m) - K * eta))) == 0)

    # route two C5 item 8: chi(m) >= 0  <=>  nu^m (K eta - m) >= K eta  <=>  m d <= 1
    chi = m * d2 - (K * eta * d2 - 1) * (nu**m - 1)
    num_chi = sp.simplify(sp.numer(sp.together(chi)) / sp.numer(sp.together(1 - m * d2)))
    # the two numerators differ by the positive factor K-1, so chi(m) >= 0, m d <= 1 and
    # nu^m(K eta - m) >= K eta are one and the same inequality
    check("A8 chi(m) and 1 - m d share the numerator nu^m(K eta - m) - K eta "
          "(up to the positive factor K-1)",
          sp.simplify(num_chi - (K - 1)) == 0, f"quotient={sp.simplify(num_chi)}")


# ---------------------------------------------------------------- shared builder
def build(K, eta, jmode):
    """jmode 'r2' = route two (smallest argmin of V_j); 'r1' = route one's formula."""
    nu = eta / (eta - 1)
    Th = lambda z: eta * nu**z - z - eta
    d = lambda z: (nu**z - K) / (K * Th(z))
    m = 1
    while 1 - (m + 1) * d(m) > 0:
        m += 1
        if m > 4000:
            raise RuntimeError("no m")
    dd = d(m)
    k1 = eta * (K - 1) + 1
    q = eta * (K - 1) / k1
    V = [1 - q**j * (1 - F(K - j, 1) / (K * eta)) for j in range(K)]
    rho = min(V)
    if jmode == "r2":
        j = V.index(rho)                       # smallest argmin
    else:
        ce = -((-eta.numerator) // eta.denominator)      # ceil(eta), exact
        j = max(0, min(K - 1, K + 1 - ce))
    Q = q**j
    D = Q * dd
    ts = j + m
    C = k1 / K

    def r(x):
        if x <= j:
            return q**x
        if x <= ts:
            return Q - (x - j) * D
        return F(0)

    def g(x):
        if x <= j:
            return q**x / K
        if x <= ts:
            return eta * D - (eta * D - Q / K) * nu ** (x - j)
        return F(0)

    a = lambda x: r(x) - g(x)
    cy = lambda y: F(K - y, K - 1)
    Ff = lambda x, y: 1 - r(x) if y == 0 else 1 - cy(y) * a(x)
    Hf = lambda x, y: (C - r(x) - (eta - 1) * a(x)) if y == 0 else C - eta * cy(y) * a(x)
    W = 1 - Q * (1 - (K - j) * dd)
    return dict(K=K, eta=eta, m=m, d=dd, j=j, q=q, Q=Q, D=D, ts=ts, C=C,
                r=r, g=g, a=a, F=Ff, H=Hf, rho=rho, V=V, W=W)


def audit(P):
    K, eta, ts, Ff, Hf, C = P["K"], P["eta"], P["ts"], P["F"], P["H"], P["C"]
    X = ts + K + 4
    bad = []
    for x in range(X + 1):
        for y in range(K + 1):
            if not (0 <= Ff(x, y) <= 1):
                bad.append(("range", x, y))
            if x < X and Ff(x + 1, y) < Ff(x, y):
                bad.append(("mono-x", x, y))
            if y < K and Ff(x, y + 1) < Ff(x, y):
                bad.append(("mono-y", x, y))
            if x < X - 1 and Ff(x + 2, y) - Ff(x + 1, y) > Ff(x + 1, y) - Ff(x, y):
                bad.append(("dr-xx", x, y))
            if y < K - 1 and Ff(x, y + 2) - Ff(x, y + 1) > Ff(x, y + 1) - Ff(x, y):
                bad.append(("dr-yy", x, y))
            if x < X and y < K and Ff(x + 1, y + 1) - Ff(x, y + 1) > Ff(x + 1, y) - Ff(x, y):
                bad.append(("dr-cross", x, y))
    for x in range(X):
        for y in range(K + 1):
            dF, dH = Ff(x + 1, y) - Ff(x, y), Hf(x + 1, y) - Hf(x, y)
            if not (dF <= dH <= eta * dF):
                bad.append(("band-x", x, y))
            if (dF == 0) != (dH == 0):
                bad.append(("zero-x", x, y))
    for x in range(X + 1):
        for y in range(K):
            dF, dH = Ff(x, y + 1) - Ff(x, y), Hf(x, y + 1) - Hf(x, y)
            if not (dF <= dH <= eta * dF):
                bad.append(("band-y", x, y))
            if (dF == 0) != (dH == 0):
                bad.append(("zero-y", x, y))
    if Ff(0, 0) != 0 or Hf(0, 0) != 0 or Ff(0, K) != 1:
        bad.append(("boundary",))
    for x in range(X):                                     # P1
        if Hf(x + 1, 0) != Hf(x, 1):
            bad.append(("P1", x))
    for x in range(ts, X + 1):                             # P2
        for y in range(1, K + 1):
            if Hf(x, y) != C:
                bad.append(("P2a", x, y))
    for x in range(ts + 1, X + 1):
        if Hf(x, 0) != C:
            bad.append(("P2b", x))
    maxleak = -1
    for x in range(X + 1):                                 # P3
        for y in range(K + 1):
            if x + y > X:
                continue
            if Hf(x, y) != Hf(x + y, 0):
                maxleak = max(maxleak, x + y)
                if not (y >= 2 and x <= ts - 1):
                    bad.append(("P3", x, y))
    return bad, maxleak


# ---------------------------------------------------------------- block B
GRID_B = [(K, F(num, den)) for K in range(3, 8)
          for den in (1, 2, 3, 4, 5, 8) for num in range(den + 1, 6 * den + 1)]


def block_b():
    print("[B] exhaustive legality of the route-two family (%d configs)" % len(GRID_B))
    bad = []
    worst = None
    for K, eta in GRID_B:
        P = build(K, eta, "r2")
        fl, ml = audit(P)
        if fl:
            bad.append((K, str(eta), fl[:2]))
        if not (eta * (K - 1) < P["m"] < K * eta):
            bad.append((K, str(eta), "location"))
        if not (P["m"] * P["d"] <= 1 and (P["m"] + 1) * P["d"] >= 1):
            bad.append((K, str(eta), "BC"))
        if ml > P["ts"] + K - 1:
            bad.append((K, str(eta), f"leak size {ml} > t*+K-1"))
        if worst is None or ml - P["ts"] > worst[0]:
            worst = (ml - P["ts"], K, str(eta), ml, P["ts"])
    check("B1 monotone submodular + band + zero pattern + P1/P2/P3 + (A)(B)(C) + "
          "location bounds + leak size <= t*+K-1", not bad, str(bad[:3]))
    print("      largest observed leak size minus t*: %d (K=%s eta=%s)" % (worst[0], worst[1], worst[2]))

    # route one's j on the same grid: also legal (no contradiction between the routes)
    bad1 = [(K, str(eta)) for K, eta in GRID_B if audit(build(K, eta, "r1"))[0]]
    check("B2 the same family with route one's j is legal too", not bad1, str(bad1[:3]))

    # route two's section 5.1 walkthrough, entry by entry
    P = build(3, F(3, 2), "r2")
    tab_r = [F(1), F(3, 4), F(9, 16), F(405, 928), F(9, 29), F(171, 928), F(27, 464), F(0)]
    tab_g = [F(1, 3), F(1, 4), F(3, 16), F(171, 928), F(81, 464), F(135, 928), F(27, 464), F(0)]
    ok = (P["m"] == 4 and P["d"] == F(13, 58) and P["j"] == 2 and P["ts"] == 6
          and P["Q"] == F(9, 16) and P["D"] == F(117, 928) and P["rho"] == F(9, 16)
          and P["W"] == F(523, 928) and P["W"] - P["rho"] == F(1, 928)
          and all(P["r"](x) == tab_r[x] for x in range(8))
          and all(P["g"](x) == tab_g[x] for x in range(8))
          and P["H"](1, 2) == F(23, 24) and P["H"](3, 0) == F(37, 48))
    check("B3 route two section 5.1 table (K=3, eta=3/2) reproduces exactly", ok)


# ---------------------------------------------------------------- block C
# C1 needs only the two j rules (cheap, no m): large grid.
GRID_C1 = [(K, F(num, den)) for K in range(3, 15)
           for den in (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 50)
           for num in range(den + 1, 25 * den + 1)]
# C2 compares W_K and therefore needs m: smaller grid.
GRID_C2 = [(K, F(num, den)) for K in range(3, 9)
           for den in (1, 2, 3, 5) for num in range(den + 1, 9 * den + 1)]


def js(K, eta):
    k1 = eta * (K - 1) + 1
    q = eta * (K - 1) / k1
    V = [1 - q**j * (1 - F(K - j, 1) / (K * eta)) for j in range(K)]
    ce = -((-eta.numerator) // eta.denominator)
    return V.index(min(V)), max(0, min(K - 1, K + 1 - ce))


def block_c():
    print("[C] the two j conventions (%d + %d configs)" % (len(GRID_C1), len(GRID_C2)))
    mism, wrong = [], []
    for K, eta in GRID_C1:
        j2, j1 = js(K, eta)
        if j1 != j2:
            mism.append((K, str(eta), j1, j2))
            if not (eta.denominator == 1 and 2 <= eta <= K and j1 == j2 + 1):
                wrong.append((K, str(eta), j1, j2))
    check("C1 j differs exactly at integer eta in [2,K], always j_route1 = j_route2 + 1",
          not wrong, str(wrong[:3]))
    print("      mismatching configs: %d of %d; example %s"
          % (len(mism), len(GRID_C1), mism[0] if mism else None))

    wrong2 = []
    ex = None
    for K, eta in GRID_C2:
        P2, P1 = build(K, eta, "r2"), build(K, eta, "r1")
        if P1["m"] != P2["m"] or P1["rho"] != P2["rho"]:
            wrong2.append((K, str(eta), "m or rho differ"))
        if P1["j"] == P2["j"]:
            if P1["W"] != P2["W"]:
                wrong2.append((K, str(eta), "same j, different W"))
        else:
            if not P1["W"] < P2["W"]:
                wrong2.append((K, str(eta), "W_route1 not < W_route2"))
            if ex is None:
                ex = (K, str(eta), P1["j"], P2["j"], P1["W"], P2["W"])
    check("C2 m and rho_K always agree; where j differs, W_route1 < W_route2 strictly",
          not wrong2, str(wrong2[:3]))
    print("      example: K=%s eta=%s  j1=%s j2=%s  W1=%s  W2=%s" % ex if ex else "      none")


# ---------------------------------------------------------------- block D
E_HI = F(2719, 1000)          # e < 2.719, so the target bound below is conservative
GRID_D = [(K, F(num, den)) for K in range(3, 11)
          for den in (1, 2, 3, 5, 10) for num in range(den + 1, 15 * den + 1)]


def block_d():
    print("[D] exact gap bound, e replaced by 2719/1000 (%d configs, both j)" % len(GRID_D))
    bad = []
    worst = {"r1": (F(0), None), "r2": (F(0), None)}
    for K, eta in GRID_D:
        bnd = 1 / (K * (E_HI ** (K - 1) - K - 1))
        for mode in ("r1", "r2"):
            P = build(K, eta, mode)
            gap = P["W"] - P["rho"]
            if not (0 <= gap < bnd):
                bad.append((K, str(eta), mode, float(gap), float(bnd)))
            ratio = gap / bnd
            if ratio > worst[mode][0]:
                worst[mode] = (ratio, (K, str(eta)))
    check("D1 0 <= W_K - rho_K < 1/(K(e^{K-1}-K-1)) for both j conventions", not bad,
          str(bad[:3]))
    for mode in ("r1", "r2"):
        print("      %s largest gap/bound ratio %.6f at K=%s eta=%s"
              % (mode, float(worst[mode][0]), worst[mode][1][0], worst[mode][1][1]))


# ---------------------------------------------------------------- block E
def block_e():
    print("[E] route two step D5, the sentence alpha_{K+1} = 1")
    # route two's own step U1 family at n = K+1: tilde f = |S|/(eta K) is O-independent,
    # so a deterministic algorithm's output T is fixed; |B| = 1 so |T cap O| >= |T| - 1.
    # For output T with |T| = t the adversary picks which element is the single
    # B element, so |T cap O| = t-1 whenever t >= 1; the algorithm then picks the
    # best t <= K.
    bad = []
    for K in range(3, 8):
        for eta in (F(3, 2), F(2), F(5, 2), F(3), F(7, 2)):
            best = max(min(F(i, 1) / K + F(t - i, 1) / (eta * K)
                           for i in range(max(0, t - 1), t + 1))
                       for t in range(0, K + 1))
            k1_over = (eta * (K - 1) + 1) / (K * eta)
            if best != k1_over or best >= 1:
                bad.append((K, str(eta), str(best)))
    check("E1 on route two's U1 family at n=K+1 every deterministic algorithm is capped "
          "at k_1/(K eta) < 1, so alpha_{K+1} = 1 is false", not bad, str(bad[:3]))


if __name__ == "__main__":
    block_a()
    block_b()
    block_c()
    block_d()
    block_e()
    print()
    if FAILED:
        print("FAILED items: %d" % len(FAILED))
        for n, d in FAILED:
            print("  -", n, d)
        raise SystemExit(1)
    print("all judge checks passed (block E confirms the route-two D5 sentence is refuted)")

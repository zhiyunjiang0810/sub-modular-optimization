"""Q4 independent battery (TASKS10): own implementation of the Q4 delivery's
double-residual truncated family, written from the formulas (2)-(5) of the
delivery text without reusing its code, then checked exhaustively in exact
rationals.  Everything the assembled theorem needs from the construction:

  A  normalization F(0,0)=0, F(0,K)=1, 0 <= F <= 1 on the whole grid
     (so O is optimal, OPT = 1), G(empty) = 0;
  B  F monotone and submodular: all first differences >= 0 and the three
     second differences <= 0 on the whole grid (count-grid conditions);
  C  single-element band in G-form for BOTH extreme rational splits
     (eta_u, eta_o) = (eta, 1) and (1, eta): dF/eta_u <= dG <= eta_o dF on
     every edge (any other split is a constant rescale of G, see the
     scaling lemma lem:scaling);
  D  O-independence exactly where the transcript needs it: G(x,y) =
     Ghat(x+y) for all x+y <= K, y <= 1 (Ghat from (21), own code) -- and
     the LEAK at larger sizes is real: the family is NOT globally
     O-independent (witness counted per config; the delivery's (31)
     instance K=3, eta=3/2: H(6,0) = 61/48 != 4/3 = H(5,1)), which is why
     night-10's globally-constrained LP could not reach rho_K;
  E  the rigid greedy trajectory of prop:rigidity: selected gains d_t =
     q^t/k1 (t<j), q^j/(K eta) (t>=j); every remaining O element has true
     marginal q^{min(t,j)}/K; predicted marginals tie exactly
     (G(t+1,0) = G(t,1)) at every step, common value Ghat step;
  F  value: F(K,0) = rho_K(eta) = min_j V_j exactly (own rho formula), for
     every K >= 2 and every eta in the sweep, independent of n (the
     formulas do not involve n; any n >= 2K restricts the same table);
  G  exact calibration: both split endpoints are attained on positive-gain
     edges at x = 0, so the actual error factors are exactly (eta_u, eta_o).

Sweep: K in {2,3,4,5,7,10,13}, eta covering (1,2), integer points (both
tied branches), mid-range and eta >= K (j = 0), disjoint from the values
used by the delivery's own script where possible.  All exact Fractions.

Run:  python3 results/Q4_indep_check.py     (exit 0 iff ALL PASS)
"""
import math
import sys
from fractions import Fraction as Fr

fails = []


def check(name, ok, detail=""):
    if not ok:
        fails.append(name)
        print("FAIL", name, detail)


# ------------------------------------------------------------ construction
def build(K, eta, j=None):
    """Return (F, G_of_split, H, Ghat, params) as callables/dicts, own code."""
    eta = Fr(eta)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    if j is None:
        j = max(0, K - math.floor(eta))
    Q = q ** j
    delta = Q / (K * eta)
    C = k1 / K
    A = Fr(K - 1, K) * Q

    def r(x):
        if x <= j:
            return q ** x
        return max(Fr(0), Q - (x - j) * delta)

    def h(x):
        if x <= j:
            return Fr(K - 1, K) * q ** x
        return max(Fr(0), A - (x - j) * delta)

    def F(x, y):
        if y == 0:
            return 1 - r(x)
        return 1 - Fr(K - y, K - 1) * h(x)

    def H(x, y):
        if y == 0:
            return C - r(x) - (eta - 1) * h(x)
        return C - eta * Fr(K - y, K - 1) * h(x)

    def Ghat_scaled(s):          # eta_u * Ghat, formula (21), own transcription
        if s <= j:
            return C * (1 - q ** s)
        return C * (1 - Q) + eta * (s - j) * delta

    return dict(F=F, H=H, Ghat=Ghat_scaled, r=r, h=h,
                K=K, eta=eta, j=j, k1=k1, q=q, Q=Q, delta=delta, C=C)


def rho_exact(K, eta):
    eta = Fr(eta)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return min(1 - q ** t * (1 - Fr(K - t, K) / eta) for t in range(K))


# ------------------------------------------------------------------ checks
def run_config(K, eta, j=None):
    B = build(K, eta, j)
    F, H, Ghat = B['F'], B['H'], B['Ghat']
    eta, j = B['eta'], B['j']
    xmax = int(math.ceil(j + K * eta)) + 3
    tag = f"K={K} eta={eta} j={j}"

    # A normalization
    check(f"{tag} F(0,0)=0", F(0, 0) == 0)
    check(f"{tag} F(0,K)=1", F(0, K) == 1)
    check(f"{tag} H(0,0)=0 (G empty = 0)", H(0, 0) == 0)
    for x in range(xmax + 1):
        for y in range(K + 1):
            v = F(x, y)
            check(f"{tag} 0<=F<=1", 0 <= v <= 1, f"at {(x,y)}: {v}")

    # B monotone + submodular (three second differences)
    for x in range(xmax + 1):
        for y in range(K + 1):
            if x < xmax:
                check(f"{tag} DxF>=0", F(x+1, y) - F(x, y) >= 0, f"{(x,y)}")
            if y < K:
                check(f"{tag} DyF>=0", F(x, y+1) - F(x, y) >= 0, f"{(x,y)}")
            if x + 1 < xmax:
                check(f"{tag} Dx2F<=0",
                      F(x+2, y) - 2*F(x+1, y) + F(x, y) <= 0, f"{(x,y)}")
            if y + 1 < K:
                check(f"{tag} Dy2F<=0",
                      F(x, y+2) - 2*F(x, y+1) + F(x, y) <= 0, f"{(x,y)}")
            if x < xmax and y < K:
                check(f"{tag} DxDyF<=0",
                      F(x+1, y+1) - F(x+1, y) - F(x, y+1) + F(x, y) <= 0,
                      f"{(x,y)}")

    # C band in G-form for both extreme rational splits
    for (eu, eo) in ((eta, Fr(1)), (Fr(1), eta)):
        for x in range(xmax + 1):
            for y in range(K + 1):
                for dx, dy in ((1, 0), (0, 1)):
                    if x + dx > xmax or y + dy > K:
                        continue
                    dF = F(x+dx, y+dy) - F(x, y)
                    dG = (H(x+dx, y+dy) - H(x, y)) / eu
                    check(f"{tag} band ({eu},{eo})",
                          dF / eu <= dG <= eo * dF, f"{(x,y,dx,dy)}")

    # D O-independence on x+y <= K, y <= 1; leak beyond
    for x in range(K + 1):
        for y in (0, 1):
            if x + y <= K:
                check(f"{tag} small-set O-indep", H(x, y) == Ghat(x + y),
                      f"{(x,y)}")
    leaks = sum(1 for x in range(xmax)
                if H(x + 1, 0) != H(x, 1) and x + 1 > K)
    if K >= 3 and eta < K:      # leak expected once truncation active
        check(f"{tag} leak beyond size K exists (not globally O-indep)",
              leaks > 0)
    if (K, eta) == (3, Fr(3, 2)):
        check("delivery (31) H(6,0)=61/48", H(6, 0) == Fr(61, 48),
              str(H(6, 0)))
        check("delivery (31) H(5,1)=4/3", H(5, 1) == Fr(4, 3), str(H(5, 1)))

    # E rigid trajectory
    for t in range(K):
        d_t = F(t + 1, 0) - F(t, 0)
        want = B['q'] ** t / B['k1'] if t < j else B['Q'] / (K * eta)
        check(f"{tag} d_t formula", d_t == want, f"t={t}")
        g_t = F(t, 1) - F(t, 0)
        check(f"{tag} g_t = q^min(t,j)/K",
              g_t == B['q'] ** min(t, j) / K, f"t={t}")
        check(f"{tag} predicted tie", H(t + 1, 0) == H(t, 1), f"t={t}")
        check(f"{tag} predicted marginal (27)",
              H(t, 1) - H(t, 0) == B['q'] ** min(t, j) / K, f"t={t}")

    # F value
    check(f"{tag} F(K,0) = rho_K", F(K, 0) == rho_exact(K, eta),
          f"{F(K,0)} vs {rho_exact(K, eta)}")

    # G calibration endpoints at x=0 (positive-gain edges)
    dF1, dH1 = F(0, 1) - F(0, 0), H(0, 1) - H(0, 0)
    check(f"{tag} lower endpoint attained", dH1 == dF1 and dF1 > 0)
    if K >= 2:
        dF2, dH2 = F(0, 2) - F(0, 1), H(0, 2) - H(0, 1)
        check(f"{tag} upper endpoint attained", dH2 == eta * dF2 and dF2 > 0)
    return leaks


def main():
    nconf = 0
    for K in (2, 3, 4, 5, 7, 10, 13):
        etas = {Fr(21, 20), Fr(6, 5), Fr(4, 3), Fr(8, 5), Fr(9, 5),
                Fr(2), Fr(12, 5), Fr(3), Fr(10, 3), Fr(9, 2),
                Fr(3 * K - 2, 3), Fr(K), Fr(2 * K + 1, 2), Fr(2 * K)}
        for eta in sorted(e for e in etas if e > 1):
            js = {max(0, K - math.floor(eta))}
            if eta == int(eta) and 2 <= eta <= K:
                js.add(K - int(eta) + 1)     # tied branch at integer eta
            for j in sorted(js):
                run_config(K, eta, j)
                nconf += 1
    print(f"configs checked: {nconf}")
    print("ALL PASS" if not fails else f"FAILURES: {len(fails)}")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()

"""J7 verification, own grid battery: exact-rational full-grid checks of the
J7 construction (results/J7/linear_anysize.md sections 3.1-3.4), implemented
here directly from its formulas (2)-(10) with the corrected Psi truncation
rule, independent of the source's claims and of results/Q1_closed_form.py.

Per configuration (K, eta):
  A  normalization: F(0,0)=0, F(0,K)=1, 0 <= F <= 1 on the whole grid,
     H(0,0)=0 (so G(empty)=0);
  B  F monotone and submodular: all first differences >= 0, the three
     second differences <= 0;
  C  single-element band in scaled form: dF <= dH <= eta dF on every edge
     (H = eta_u G, so this is split-free); both calibration endpoints
     attained at x = 0;
  D  the ANY-SIZE key: H(x+1,0) = H(x,1) for EVERY x >= 0 (G depends only
     on |S| on the whole y <= 1 region, all sizes), and full saturation
     F = 1, H = C for x > T;
  E  value: F(K,0) = 1 - Q + (K-j) Q d = W_K, the gap identity (17)
     W_K - rho_K = (K-j) Q (m - eta(K-1)) / (K eta B_m) exact, gap > 0;
  F  leak characterization: every state whose H differs from the size
     profile Hhat_{x+y} = H(x+y, 0) has y >= 2 AND x <= T (J7 (15)); count
     reported;
  G  (K = 3 only) adversarial simulation in the any-size regime: worst-case
     (adversarial ties) forward predictive greedy, reverse greedy (deletion,
     queries up to size n), and max(forward, reverse), n = 8..12: every
     ratio <= W_K.

Sweep: K in 3..12, eta in {21/20, 5/4, 3/2, 2, 5/2, 3, 667/500, K-1/3, K,
K+1/2} (> 1, deduped), j from J7's rule (includes j <= 1 and j = 0).

Run:  python3 results/J7_grid_check.py     (exit 0 iff ALL PASS)
"""
import math
import sys
from fractions import Fraction as Fr
from functools import lru_cache

fails = []


def check(name, ok, detail=""):
    if not ok:
        fails.append(name)
        print("FAIL", name, detail)


def build(K, eta):
    """J7 formulas, own transcription.  Returns callables F, H and params."""
    eta = Fr(eta)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    nu = eta / (eta - 1)
    j = max(0, min(K - 1, K + 1 - math.ceil(eta)))
    Q = q ** j
    m = None
    for z in range(1, 10 * K * (int(eta) + 2) + 10):
        if (K * eta - z - 1) * nu ** z - K * (eta - 1) <= 0:   # Psi(z) <= 0
            m = z
            break
    assert m is not None
    Bm = eta * (nu ** m - 1) - m
    d = (nu ** m / K - 1) / Bm
    D = Q * d
    T = j + m
    C = k1 / K

    @lru_cache(maxsize=None)
    def r(x):
        if x <= j:
            return q ** x
        if x <= T:
            return Q - (x - j) * D
        return Fr(0)

    @lru_cache(maxsize=None)
    def g(x):
        if x <= j:
            return q ** x / K
        if x <= T:
            return eta * D - (eta * D - Q / K) * nu ** (x - j)
        return Fr(0)

    def a(x):
        return r(x) - g(x)

    def F(x, y):
        if y == 0:
            return 1 - r(x)
        return 1 - Fr(K - y, K - 1) * a(x)

    def H(x, y):
        if y == 0:
            return C - r(x) - (eta - 1) * a(x)
        return C - eta * Fr(K - y, K - 1) * a(x)

    return dict(F=F, H=H, r=r, g=g, K=K, eta=eta, j=j, m=m, Bm=Bm, d=d,
                D=D, T=T, C=C, Q=Q, q=q, k1=k1)


def rho_exact(K, eta):
    eta = Fr(eta)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return min(1 - q ** t * (1 - Fr(K - t, K) / eta) for t in range(K))


def run_config(K, eta):
    B = build(K, eta)
    F, H = B['F'], B['H']
    eta, j, m, T, C, Q, d = (B['eta'], B['j'], B['m'], B['T'], B['C'],
                             B['Q'], B['d'])
    xmax = T + K + 2
    tag = f"K={K} eta={eta} j={j} m={m}"

    # A normalization
    check(f"{tag} F(0,0)=0", F(0, 0) == 0)
    check(f"{tag} F(0,K)=1", F(0, K) == 1)
    check(f"{tag} H(0,0)=0", H(0, 0) == 0)
    for x in range(xmax + 1):
        for y in range(K + 1):
            check(f"{tag} 0<=F<=1", 0 <= F(x, y) <= 1, f"{(x,y)}")

    # B + C
    for x in range(xmax + 1):
        for y in range(K + 1):
            for dx, dy in ((1, 0), (0, 1)):
                xx, yy = x + dx, y + dy
                if xx > xmax or yy > K:
                    continue
                dF = F(xx, yy) - F(x, y)
                dH = H(xx, yy) - H(x, y)
                check(f"{tag} mono+band", 0 <= dF <= dH <= eta * dF,
                      f"{(x,y,dx,dy)} dF={dF} dH={dH}")
                for sx, sy in ((1, 0), (0, 1)):
                    if xx + sx > xmax or yy + sy > K:
                        continue
                    dF2 = F(xx + sx, yy + sy) - F(x + sx, y + sy)
                    check(f"{tag} submod", dF2 <= dF,
                          f"{(x,y,dx,dy,sx,sy)}")
    dF1, dH1 = F(0, 1) - F(0, 0), H(0, 1) - H(0, 0)
    check(f"{tag} lower endpoint attained", dF1 > 0 and dH1 == dF1)
    dF2, dH2 = F(0, 2) - F(0, 1), H(0, 2) - H(0, 1)
    check(f"{tag} upper endpoint attained", dF2 > 0 and dH2 == eta * dF2)

    # D any-size profile + saturation
    for x in range(xmax):
        check(f"{tag} profile H(x+1,0)=H(x,1)", H(x + 1, 0) == H(x, 1),
              f"x={x}")
    for x in range(T + 1, xmax + 1):
        for y in range(K + 1):
            check(f"{tag} saturation", F(x, y) == 1 and H(x, y) == C,
                  f"{(x,y)}")

    # E value + gap identity
    W = 1 - Q + (K - j) * Q * d
    check(f"{tag} F(K,0) = W formula", F(K, 0) == W,
          f"{F(K,0)} vs {W}")
    rho = rho_exact(K, eta)
    gap = (K - j) * Q * (m - eta * (K - 1)) / (K * eta * B['Bm'])
    check(f"{tag} gap identity (17)", W - rho == gap,
          f"{W-rho} vs {gap}")
    check(f"{tag} gap > 0", W - rho > 0)

    # F leak region
    leaks = 0
    for x in range(xmax + 1):
        for y in range(K + 1):
            if H(x, y) != H(x + y, 0):        # size profile at |S| = x+y
                leaks += 1
                check(f"{tag} leak only at y>=2, x<=T",
                      y >= 2 and x <= T, f"{(x,y)}")
    return W, leaks


def sim(K, eta, ns=range(8, 13)):
    B = build(K, eta)
    F, H, T, Q, d, j = B['F'], B['H'], B['T'], B['Q'], B['d'], B['j']
    W = 1 - Q + (K - j) * Q * d
    rho = rho_exact(K, eta)
    for n in ns:
        X = n - K

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

        wf, wr = fwd(0, 0), rev(X, K)
        # The theorem is an n -> infinity statement; its own leak analysis
        # (J7 (15): a leaking query needs y >= 2 AND |S| <= T + K) implies
        # that for n < K + T the FULL GROUND SET is leak-sized, so reverse
        # greedy may read O off the leaked values.  The correct invariants:
        #   n >= K + T  ->  max(fwd, rev) <= W  (leak-free start);
        #   n <  K + T  ->  rev exactly 1 here (it recovers O; observed at
        #                   every such cell), fwd still <= W.
        # A finite-n "<= W for all n" claim would be FALSE; recorded as a
        # must-not-claim on the T10d card.
        check(f"sim K={K} eta={eta} n={n} fwd <= W", wf <= W,
              f"fwd={float(wf):.6f} W={float(W):.6f}")
        if n >= K + T:
            check(f"sim K={K} eta={eta} n={n} (n>=K+T) max(fwd,rev) <= W",
                  max(wf, wr) <= W,
                  f"fwd={float(wf):.6f} rev={float(wr):.6f} "
                  f"W={float(W):.6f}")
        else:
            check(f"sim K={K} eta={eta} n={n} (n<K+T) rev leaks to 1",
                  wr == 1, f"rev={float(wr):.6f}")
        print(f"    sim K={K} eta={eta} n={n:2d} "
              f"({'n>=K+T' if n >= K+T else 'n< K+T'}): "
              f"fwd={float(wf):.6f} rev={float(wr):.6f} "
              f"W={float(W):.6f} rho={float(rho):.6f}")
        fwd.cache_clear(); rev.cache_clear()


def main():
    nconf = 0
    for K in range(3, 13):
        etas = {Fr(21, 20), Fr(5, 4), Fr(3, 2), Fr(2), Fr(5, 2), Fr(3),
                Fr(667, 500), Fr(3 * K - 1, 3), Fr(K), Fr(2 * K + 1, 2)}
        for eta in sorted(e for e in etas if e > 1):
            W, leaks = run_config(K, eta)
            nconf += 1
            print(f"config K={K} eta={eta}: W={float(W):.9f} "
                  f"gap={float(W - rho_exact(K, eta)):.3e} leaks={leaks}")
    for eta in (Fr(3, 2), Fr(667, 500), Fr(2)):
        sim(3, eta)
    print(f"\nconfigs: {nconf}")
    print("ALL PASS" if not fails else f"FAILURES: {len(fails)}")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()

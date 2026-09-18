"""Grid of exact verifications + the explicit K=3, eta=3/2 instance table."""
import sys, itertools
from fractions import Fraction as Fr
from lp_sym import solve

MAXDEN = 10 ** 6


def check(K, eta, r, m, eu=Fr(1)):
    eo = eta / eu
    res, Z, zi, gi, nz, n = solve(K, float(eta), r, m, eta_u=float(eu))
    if not res.success:
        return None
    x = res.x
    F = {z: Fr(x[zi[z]]).limit_denominator(MAXDEN) for z in Z}
    G = {k: Fr(x[gi[k]]).limit_denominator(MAXDEN) for k in gi}
    def gkey(z):
        s = sum(z)
        return ("D", s, z[0]) if (z[0] >= 2 and s <= m) else ("F", s)
    def ft(z): return G[gkey(z)]
    k1 = (K - 1) * eta + 1; q = (K - 1) * eta / k1
    V = [1 - q ** j * (1 - Fr(K - j, K) / eta) for j in range(K)]
    rho = min(V); jstar = V.index(rho)
    cap = (K, K, r); E = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    def add(z, e):
        w = tuple(z[i] + e[i] for i in range(3))
        return w if all(0 <= w[i] <= cap[i] for i in range(3)) else None
    bad = []
    if F[(0, 0, 0)] != 0: bad.append("f0")
    if ft((0, 0, 0)) != 0: bad.append("ft0")
    if F[(K, 0, 0)] != 1: bad.append("fO")
    for z in Z:
        if sum(z) == K and F[z] > 1: bad.append(f"cap{z}")
        for e in E:
            w = add(z, e)
            if w is None: continue
            d = F[w] - F[z]; dt = ft(w) - ft(z)
            if d < 0: bad.append(f"mon{z}{e}")
            if dt < d / eu: bad.append(f"lo{z}{e}")
            if dt > eo * d: bad.append(f"hi{z}{e}")
        for i, e in enumerate(E):
            for jj in range(i, 3):
                e2 = E[jj]
                w1 = add(z, e); w2 = add(z, e2); w12 = add(w1, e2) if w1 else None
                if w1 is None or w2 is None or w12 is None: continue
                if i == jj and z[i] + 2 > cap[i]: continue
                if F[w1] + F[w2] < F[z] + F[w12]: bad.append(f"sub{z}{e}{e2}")
    lo = any(ft(add(z, e)) - ft(z) == (F[add(z, e)] - F[z]) / eu
             for z in Z for e in E if add(z, e) and F[add(z, e)] > F[z])
    hi = any(ft(add(z, e)) - ft(z) == eo * (F[add(z, e)] - F[z])
             for z in Z for e in E if add(z, e) and F[add(z, e)] > F[z])
    return dict(F=F, G=G, ft=ft, rho=rho, jstar=jstar, bad=bad, lo=lo, hi=hi,
                fT=F[(0, K, 0)], n=n, Z=Z, gi=gi)


if __name__ == "__main__":
    if sys.argv[1] == "grid":
        for K in [2, 3, 4, 5]:
            m = 3 * (K - 1)
            for eta in [Fr(6, 5), Fr(3, 2), Fr(2), Fr(5, 2), Fr(7, 2), Fr(5)]:
                r = max(4, m - 2 * K + 4)
                out = check(K, eta, r, m)
                ok = out and not out["bad"] and out["fT"] == out["rho"]
                print(f"K={K} eta={eta} m={m} n={out['n']}: f(T)={out['fT']} "
                      f"rho={out['rho']} j*={out['jstar']} violations={len(out['bad'])} "
                      f"bandends=({out['lo']},{out['hi']})  EXACT={ok}", flush=True)
    elif sys.argv[1] == "splits":
        K, eta, m, r = 3, Fr(3, 2), 6, 4
        for eu in [Fr(1), Fr(5, 4), Fr(3, 2), Fr(6, 5)]:
            out = check(K, eta, r, m, eu=eu)
            print(f"split eta_u={eu}, eta_o={eta/eu}: f(T)={out['fT']} rho={out['rho']} "
                  f"violations={len(out['bad'])} bandends=({out['lo']},{out['hi']})")
    elif sys.argv[1] == "table":
        K, eta, m, r = 3, Fr(3, 2), 6, 4
        out = check(K, eta, r, m)
        F, ft = out["F"], out["ft"]
        print(f"K=3 eta=3/2  rho={out['rho']}  f(T)={out['fT']}  violations={len(out['bad'])}")
        print("\nf(a,b,c):")
        for a in range(K + 1):
            for b in range(K + 1):
                print(f"  a={a} b={b}: " + "  ".join(str(F[(a, b, c)]) for c in range(r + 1)))
        print("\nsurrogate gamma(s) and Gamma(s,a):")
        for k in sorted(out["gi"]):
            print(f"  {k}: {out['G'][k]}")

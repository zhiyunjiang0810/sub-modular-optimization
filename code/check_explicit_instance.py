"""Verify the explicit tightness instance U_K on the full 2^{2K} lattice.
Instance: ground set B ∪ O, |B|=|O|=K, x=|S∩B|, y=|S∩O|, a = 1 - 1/(ahat*K).
  f(S)      = F(x,y) = 1 - a^x (1 - y/K)
  ftilde(S) = G(x,y) = 1 - a^x                                   (y = 0)
                     = 1 - a^x + a^x [ (1-a) + (y-1) a/(K-1) ]   (1 <= y <= K)
Claims checked: f monotone submodular; finite errors; eta_u = ahat, eta_o = aK/(K-1),
eta = (ahat K - 1)/(K-1) (all-pairs definition); greedy on ftilde (ties -> B) picks all of B;
ratio = 1 - a^K.  Path error (gains at greedy states only) = ahat.
"""
import numpy as np, sys

def build(K, ahat):
    a = 1 - 1/(ahat*K)
    F = lambda x, y: 1 - a**x*(1 - y/K)
    G = lambda x, y: (1 - a**x) if y == 0 else 1 - a**x + a**x*((1-a) + (y-1)*a/(K-1))
    n = 2*K; N = 1 << n
    cnt = lambda S: (bin(S & ((1 << K)-1)).count('1'), bin(S >> K).count('1'))
    f = np.array([F(*cnt(S)) for S in range(N)]); g = np.array([G(*cnt(S)) for S in range(N)])
    return a, n, N, f, g

def check(K, ahat, tol=1e-12):
    a, n, N, f, g = build(K, ahat)
    mono = submod = finite = True; eu = eo = 0.0
    for S in range(N):
        for e in range(n):
            if S >> e & 1: continue
            d = f[S|1<<e]-f[S]; dt = g[S|1<<e]-g[S]
            if d < -tol: mono = False
            for e2 in range(n):
                if e2 == e or S >> e2 & 1: continue
                if f[S|1<<e|1<<e2]-f[S|1<<e2] > d + tol: submod = False
            if d > tol: eu = max(eu, d/dt); eo = max(eo, dt/d)
            elif abs(dt) > tol: finite = False
    for A in range(N):                      # all-pairs error
        comp = (N-1) ^ A; Bm = comp
        while Bm:
            d = f[A|Bm]-f[A]; dt = g[A|Bm]-g[A]
            if d > tol: eu = max(eu, d/dt); eo = max(eo, dt/d)
            elif abs(dt) > tol: finite = False
            Bm = (Bm-1) & comp
    # greedy on g, ties broken toward B (indices 0..K-1); also compute path error
    S = 0; picks = []; peu = peo = 0.0
    for t in range(K):
        gains = {e: g[S|1<<e]-g[S] for e in range(n) if not S >> e & 1}
        for e, dt in gains.items():
            d = f[S|1<<e]-f[S]
            if d > tol: peu = max(peu, d/dt); peo = max(peo, dt/d)
        best = max(gains.values()); cand = [e for e, v in gains.items() if v >= best - 1e-9]
        e = min(cand); picks.append(e); S |= 1 << e
    OPT = max(f[T] for T in range(N) if bin(T).count('1') <= K)
    return dict(K=K, ahat=ahat, mono=mono, submod=submod, finite=finite,
                eta_u=eu, eta_o=eo, eta=eu*eo, eta_formula=(ahat*K-1)/(K-1),
                picked_all_B=all(p < K for p in picks), ratio=f[S]/OPT, one_minus_aK=1-a**K,
                path_eta=peu*peo, path_eta_formula=ahat)

if __name__ == "__main__":
    ok_all = True
    for K, ahat in [(2,2.0),(3,2.0),(4,1.5),(5,3.0),(6,2.0),(6,1.2)]:
        r = check(K, ahat)
        ok = (r['mono'] and r['submod'] and r['finite'] and r['picked_all_B']
              and abs(r['eta']-r['eta_formula']) < 1e-9 and abs(r['ratio']-r['one_minus_aK']) < 1e-9
              and abs(r['path_eta']-r['path_eta_formula']) < 1e-9)
        ok_all &= ok
        print(("PASS" if ok else "FAIL"), {k: (round(v,6) if isinstance(v,float) else v) for k,v in r.items()})
    print("ALL PASS" if ok_all else "SOME FAILED"); sys.exit(0 if ok_all else 1)

# Claude (chat) spot-check of the J7 construction, 2026-09-14.
# Scope: identities (7)(8)(12) symbolically; exact rational grid K=3..8, 12 eta values each (71 configs):
# monotonicity, DR, error band dF <= dH <= eta*dF, all-domain H(x+1,0)=H(x,1), extrema at x=0,
# value W_K, gap formula (17), bound (18), corrected m at eta=667/500.
# This is NOT the independent sympy pipeline required by TASKS10 Q4 and does not change any label.

# Claude spot-check of the J7 construction (not the independent pipeline; labels unchanged)
from fractions import Fraction as R
from math import ceil, floor, e as E_
import sympy as sp

# ---- symbolic identities (7), (8), and (12)<=>(14) on the linear segment ----
K, eta, m, nu, Q, d, D, gx, ax, rx = sp.symbols('K eta m nu Q d D g_x a_x r_x', positive=True)
Bm = eta*(nu**m - 1) - m
dd = (nu**m/K - 1)/Bm
Psi = lambda t: (K*eta - t - 1)*nu**t - K*(eta-1)
id7a = sp.simplify(dd - 1/(m+1) + Psi(m)/(K*(m+1)*Bm))
id7b = sp.simplify(1/m - dd - nu*Psi(m-1)/(K*m*Bm))
id8  = sp.simplify(dd - 1/(K*eta) - (m - eta*(K-1))/(K*eta*Bm))
# (7b) needs nu = eta/(eta-1); substitute
id7b = sp.simplify(id7b.subs(nu, eta/(eta-1)))
print('(7a)', id7a, '(7b)', id7b, '(8)', id8)
# (12)<=>(14): H(x+1,0)=H(x,1)  <=>  r_{x+1}+(eta-1)a_{x+1} = eta a_x  <=> g_{x+1} = eta(a_x - a_{x+1})
# linear segment: a_x = r_x - g_x, r_{x+1} = r_x - D, g_{x+1} = nu (g_x - D), nu = eta/(eta-1)
nu_ = eta/(eta-1)
g1 = nu_*(gx - D); r1 = rx - D; a1 = r1 - g1
print('(12) linear segment:', sp.simplify(g1 - eta*(ax - a1).subs(ax, rx-gx)))

# ---- exact rational grid checks ----
counts = dict(configs=0, edges=0, DR=0, alldomain=0)
worst = 0
for k in range(3, 9):
    etas = sorted({R(1001,1000), R(5,4), R(3,2), R(7,4), R(2), R(9,4), R(5,2), R(3),
                   R(k)-R(1,3), R(k), R(k)+R(1,3), R(667,500)})
    for et in etas:
        counts['configs'] += 1
        nu_r = et/(et-1)
        # m = min{z>=1 : Psi(z) <= 0}
        z = 1
        while (k*et - z - 1)*nu_r**z - k*(et-1) > 0:
            z += 1
        mm = z
        assert et*(k-1) < mm < k*et, (k, et, mm)          # (5)
        B = et*(nu_r**mm - 1) - mm
        dr = (nu_r**mm/k - 1)/B
        assert R(1, mm+1) <= dr <= R(1, mm)                 # (7)
        assert dr > 1/(k*et)                                # (8)
        ce = -(-et.numerator // et.denominator)             # ceil(eta)
        jj = max(0, min(k-1, k+1-ce))
        k1 = (k-1)*et + 1; q = (k-1)*et/k1; Qj = q**jj; Dd = Qj*dr; T = jj + mm; C = k1/k
        def r(x):
            if x <= jj: return q**x
            if x <= T: return Qj - (x-jj)*Dd
            return R(0)
        def g(x):
            if x <= jj: return q**x/k
            if x <= T: return et*Dd - (et*Dd - Qj/k)*nu_r**(x-jj)
            return R(0)
        assert r(T) == g(T) and 0 <= r(T) <= Dd             # (11)
        a = lambda x: r(x) - g(x)
        def F(x, y):
            return 1 - r(x) if y == 0 else 1 - R(k-y, k-1)*a(x)
        def H(x, y):
            return C - r(x) - (et-1)*a(x) if y == 0 else C - et*R(k-y, k-1)*a(x)
        end = T + 3
        tab = {(x, y): (F(x, y), H(x, y)) for x in range(end+1) for y in range(k+1)}
        assert tab[0,0] == (0, 0) and tab[0,k][0] == 1
        assert all(0 <= f <= 1 for f, h in tab.values())
        for x in range(end+1):
            for y in range(k+1):
                for dx, dy in [(1,0),(0,1)]:
                    xx, yy = x+dx, y+dy
                    if xx > end or yy > k: continue
                    df = tab[xx,yy][0] - tab[x,y][0]; dH = tab[xx,yy][1] - tab[x,y][1]
                    assert 0 <= df <= dH <= et*df, (k, et, x, y, dx, dy)
                    counts['edges'] += 1
                    for sx, sy in [(1,0),(0,1)]:
                        if xx+sx > end or yy+sy > k: continue
                        df2 = tab[xx+sx, yy+sy][0] - tab[x+sx, y+sy][0]
                        assert df >= df2, (k, et, x, y)
                        counts['DR'] += 1
            # (14): H(x+1,0) = H(x,1) for ALL x
            assert tab[x+1,0][1] == tab[x,1][1] if x+1 <= end else True
            counts['alldomain'] += 1
        # extrema of error band attained at x=0 O-edges
        assert tab[0,1][1] - tab[0,0][1] == tab[0,1][0] - tab[0,0][0]
        assert tab[0,2][1] - tab[0,1][1] == et*(tab[0,2][0] - tab[0,1][0])
        # value and gap (17), bound (18)
        rho = min(1 - q**t*(1 - R(k-t, k)/et) for t in range(k))
        W = 1 - Qj + (k-jj)*Qj*dr
        assert tab[k,0][0] == W
        assert W - rho == (k-jj)*Qj*(mm - et*(k-1))/(k*et*B)   # (17)
        gap = W - rho
        assert 0 < gap < R(1, k)/(E_**(k-1) - k - 1)           # (18)
        worst = max(worst, gap)
        if (k, et) == (3, R(3,2)):
            print('K=3, eta=3/2: j,m,Q,D,W =', jj, mm, Qj, Dd, W, ' gap =', gap, ' Psi(3)=', (k*et-3-1)*nu_r**3-k*(et-1))
        if (k, et) == (3, R(667,500)):
            print('K=3, eta=667/500: m =', mm, ' r_T=g_T =', r(T), '(old F3 m=ceil(K*eta)-1 =', ceil(k*et)-1, ')')
print(counts, 'max gap', float(worst))

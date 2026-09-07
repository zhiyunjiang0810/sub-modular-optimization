"""H3: independent re-check of the J2 external review's key claims.

Independent implementations (no import of J2 scripts).  Checks:
 1. case-(b) consistency slack identity (sympy, general eta_u, eta_o)
 2. three-element modular counterexample to the old etasel certificate
 3. the two-rulers K=2 instance: greedy path, etasel/etatr/eta, ratio,
    monotone+submodular for both f and ftilde (exhaustive over 16 sets)
 4. hardness family: brute-force min/max of dG/dF over the count grid vs
    the claimed closed forms sqrt(theta)A, sqrt(theta)B, eta_act
 5. new calibration H_{K,tau}(eta) = L_K(thetabar) vs the old Phi^{-1}
    calibration at J2's table points (new bound must be <= old)
 6. E2 zero-step prefix counts from E2_rows.csv (expect 225 prefixes,
    16 affected K=30 trajectories)
Exit code 0 iff all pass.
"""
import csv, math, os, sys
from fractions import Fraction as Fr
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def check(name, ok, detail=''):
    print(('PASS' if ok else 'FAIL'), name, detail)
    if not ok:
        fails.append(name)


# ---- 1. case-(b) slack identity, general symbols --------------------------
import sympy as sp
d, g, h, P, Q, R, eu, eo = sp.symbols('d g h P Q R eta_u eta_o', positive=True)
lhs = (1 - 1/(eu*eo))*h - g + d
rhs = (eo*(d+h-g) - (P+R-Q))/eo + (P-Q)/eo + (eu*R - h)/(eu*eo)
check('J2 case-(b) consistency slack identity', sp.simplify(lhs - rhs) == 0)
# and the prediction-constraint split
lhs2 = d - g/(eu*eo)
rhs2 = (eo*d - P)/eo + (P-Q)/eo + (eu*Q - g)/(eu*eo)
check('J2 case-(b) prediction slack identity', sp.simplify(lhs2 - rhs2) == 0)

# ---- 2. three-element modular counterexample ------------------------------
w_true = [1, 1, 0]
w_pred = [2, 1, 3]
K = 2
S, order = set(), []
for _ in range(K):
    e = max((i for i in range(3) if i not in S), key=lambda i: w_pred[i])
    order.append(e); S.add(e)
val = sum(w_true[i] for i in S)
opt = sum(sorted(w_true, reverse=True)[:K])
# old etasel: only steps with positive chosen true gain
rats = []
chosen_zero_harmful = False
seen = set()
for e in order:
    rest = [i for i in range(3) if i not in seen and i != e]
    M = max([w_true[i] for i in rest] + [0])
    if w_true[e] > 0:
        rats.append(Fr(M, w_true[e]))
    elif M > 0:
        chosen_zero_harmful = True
    seen.add(e)
old_etasel = max(rats + [Fr(1)])
L2 = lambda x: 1 - (1 - 1/(x*2))**2
check('J2 3-elem counterexample: greedy picks (e3,e1), ratio 1/2',
      order == [2, 0] and Fr(val, opt) == Fr(1, 2))
check('J2 3-elem counterexample: old etasel=1 but L_2(1)=3/4 > 1/2',
      old_etasel == 1 and chosen_zero_harmful and Fr(val, opt) < Fr(3, 4))

# ---- 3. two-rulers K=2 instance -------------------------------------------
# ground set: c1,c2 (C), o1,o2 (O); f depends on x=|S∩C|, y=|S∩O|
def make(fq):  # value function from base q: 1 - q^x (1 - y/2)
    def f(S):
        x = len([e for e in S if e < 2]); y = len(S) - x
        return 1 - fq**x * (1 - Fr(y, 2))
    return f
f = make(Fr(3, 4)); ft = make(Fr(1, 3))
ground = [0, 1, 2, 3]
def issub(fun):
    for r in range(5):
        for A in combinations(ground, r):
            A = set(A)
            for e in ground:
                if e in A: continue
                for ep in ground:
                    if ep in A or ep == e: continue
                    if fun(A | {e}) - fun(A) < fun(A | {e, ep}) - fun(A | {ep}):
                        return False
    return True
def ismono(fun):
    return all(fun(set(A) | {e}) >= fun(set(A))
               for r in range(5) for A in combinations(ground, r)
               for e in ground if e not in A)
check('J2 two-rulers: f and ftilde monotone submodular',
      issub(f) and issub(ft) and ismono(f) and ismono(ft))
S, path = set(), []
for _ in range(2):
    cands = [e for e in ground if e not in S]
    gains = {e: ft(S | {e}) - ft(S) for e in cands}
    mx = max(gains.values())
    tied = [e for e in cands if gains[e] == mx]
    # ties may occur only between the two symmetric C elements, never
    # between the C class and the O class (J2's stated property)
    check('J2 two-rulers: no C-vs-O tie at this step',
          len({('C' if e < 2 else 'O') for e in tied}) == 1)
    e = tied[0]; path.append(e); S.add(e)
ratio = Fr(f(S), f({2, 3}))
# etasel
sel = Fr(1)
T = set()
for e in path:
    cands = [i for i in ground if i not in T]
    M = max(f(T | {i}) - f(T) for i in cands if i != e) if len(cands) > 1 else 0
    ge = f(T | {e}) - f(T)
    sel = max(sel, Fr(M, ge)); T.add(e)
# etatr over the two visited states, all candidates
eu_t = Fr(1); eo_t = Fr(1)
T = set()
for e in path + [None]:
    if len(T) >= 2: break
    for i in ground:
        if i in T: continue
        dt = f(T | {i}) - f(T); pt = ft(T | {i}) - ft(T)
        if dt > 0 and pt > 0:
            eo_t = max(eo_t, Fr(pt, dt)); eu_t = max(eu_t, Fr(dt, pt))
    if e is not None: T.add(e)
# global eta over all states
eu_g = Fr(1); eo_g = Fr(1)
for r in range(4):
    for A in combinations(ground, r):
        A = set(A)
        for i in ground:
            if i in A: continue
            dt = f(A | {i}) - f(A); pt = ft(A | {i}) - ft(A)
            if dt > 0 and pt > 0:
                eo_g = max(eo_g, Fr(pt, dt)); eu_g = max(eu_g, Fr(dt, pt))
rho2 = lambda e: min(Fr(1, 1)/e, Fr(3, 1)/(2*(e+1)))
check('J2 two-rulers: picks C twice, ratio 7/16', path == [0, 1] and ratio == Fr(7, 16))
check('J2 two-rulers: etasel=2, etatr=6, eta=27/2',
      sel == 2 and eu_t*eo_t == 6 and eu_g*eo_g == Fr(27, 2),
      f'sel={sel} tr={eu_t*eo_t} glob={eu_g*eo_g}')
check('J2 two-rulers: ratio = L_2(2) < rho_2(2)=1/2',
      ratio == 1 - (1 - Fr(1, 4))**2 and ratio < rho2(Fr(2)))

# ---- 4. hardness family: brute-force edge ratios --------------------------
def edge_extremes(Kh, tau, theta, X):
    a = 1 - Fr(1, theta*Kh)
    def F(x, y):  # times sqrt(theta): use H = sqrt(theta) F, ratios add sqrt back
        return 1 - a**x * (1 - Fr(y, Kh))
    def G(x, y):
        if y <= tau: return 1 - a**(x+y)
        return 1 - a**(x+tau) * Fr(Kh - y, Kh - tau)
    rmax = None; rmin = None
    for x in range(X + 1):
        for y in range(Kh + 1):
            for dx, dy in ((1, 0), (0, 1)):
                if y + dy > Kh: continue
                dF = F(x+dx, y+dy) - F(x, y)
                dG = G(x+dx, y+dy) - G(x, y)
                if dF == 0:
                    if dG != 0: return None, None, False
                    continue
                r = Fr(dG, dF)  # = dG / (sqrt(theta) dFtrue) * sqrt(theta)... see below
                rmax = r if rmax is None else max(rmax, r)
                rmin = r if rmin is None else min(rmin, r)
    return rmax, rmin, True
ok_all = True
for (Kh, tau, theta) in [(4, 1, Fr(4)), (5, 2, Fr(3, 2)), (6, 3, Fr(2)), (8, 2, Fr(1)), (7, 1, Fr(5, 2))]:
    a = 1 - Fr(1, theta*Kh)
    A = a**tau * Fr(Kh, Kh - tau); B = a**(1 - tau)
    rmax, rmin, cons = edge_extremes(Kh, tau, theta, Kh + 4)
    # dG/dF_true = dG/(theta^{-1/2} dH) = sqrt(theta) * dG/dH; our r above is dG/dH
    # eta_o = sqrt(theta)*max(dG/dH) should equal sqrt(theta)*A etc.
    ok = cons and rmax == A and rmin == 1/(theta*B)
    eta_act = theta * A * B
    ok = ok and eta_act == Fr(theta*Kh - 1, Kh - tau)
    ok_all = ok_all and ok
    if not ok:
        print('  detail', Kh, tau, theta, rmax, A, rmin, 1/(theta*B))
check('J2 hardness: edge extremes = A and 1/(theta B); eta_act=(theta K-1)/(K-tau)', ok_all)

# ---- 5. new vs old calibration at J2's table points -----------------------
def L(x, Kh):
    return 1 - (1 - 1/(x*Kh))**Kh
rows = [(8, 1, 2.0, 0.485451, 0.472888), (16, 2, 2.0, 0.458480, 0.453295),
        (32, 2, 3.0, 0.316269, 0.306302), (64, 3, 1.5, 0.511796, 0.506972)]
ok_all = True
for Kh, c, eta, old_ref, new_ref in rows:
    tau = c + 1
    # old: Phi(th) = th*max(A,B)^2, solve Phi(th)=eta by bisection
    def Phi(th):
        a = 1 - 1/(th*Kh)
        A = a**tau * Kh/(Kh - tau); B = a**(1 - tau)
        return th * max(A, B)**2
    lo, hi = 1.0, eta
    for _ in range(200):
        mid = (lo + hi)/2
        if Phi(mid) < eta: lo = mid
        else: hi = mid
    old_bound = L(lo, Kh)
    thbar = (eta*(Kh - tau) + 1)/Kh
    new_bound = L(thbar, Kh)
    ok = abs(old_bound - old_ref) < 5e-4 and abs(new_bound - new_ref) < 5e-4 \
        and new_bound <= old_bound + 1e-12 and new_bound >= L(eta, Kh) - 1e-12
    ok_all = ok_all and ok
    if not ok:
        print('  detail', Kh, c, eta, old_bound, new_bound)
check('J2 hardness recalibration table (new bound stronger, >= L_K(eta))', ok_all)

# ---- 6. E2 zero-step prefixes ---------------------------------------------
with open(os.path.join(HERE, 'E2_rows.csv')) as fh:
    rows = list(csv.DictReader(fh))
pref = [r for r in rows if r['task'] == 'E2' and int(r['K']) >= 2
        and int(float(r['n_steps_nonpos'])) > 0]
traj_cols = ('dataset', 'seed', 'p') if 'p' in rows[0] else ('dataset', 'seed')
k30 = {tuple(r[c] for c in traj_cols) for r in rows
       if r['task'] == 'E2' and r['K'] == '30' and int(float(r['n_steps_nonpos'])) > 0}
check('J2 E2 zero steps: 225 affected K>=2 prefixes, 16 K=30 trajectories',
      len(pref) == 225 and len(k30) == 16,
      f'prefixes={len(pref)} trajs={len(k30)}')

print()
print('ALL PASS' if not fails else f'FAILURES: {fails}')
sys.exit(0 if not fails else 1)

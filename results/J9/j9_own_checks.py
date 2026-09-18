"""Q11 (J9): independent verification of the delivered script results/J9/j9_check.py
(GPT, 2026-09-18) with our own pipeline.  The proof file results/J9/j9_proof.md is
still undelivered; what the script fixes is the sequence family (14)(15) (three
phases geo / lin / tail), the truncation index m, the parameters eps, gamma and the
parameter lemma.  This file does

  S   every identity printed by the delivered script, re-derived symbolically in a
      different formulation: q^j, q^x, nu^t, nu^m are free symbols (P, Qx, Nt, Nm)
      so that every identity is a rational-function identity settled by sp.cancel.
      This is decisive where the delivered script prints False for three true
      identities (sympy cannot combine q**(K-a-1) with q**(K-a)).
  P   parameter lemma exactly (Fraction), K = 2..12, 15 rational eta per K plus the
      instruction's points {6/5, 3/2, 5/2}: m > theta, 0 < eps < eta-1,
      eps < 1/(K-1), 0 <= gamma < 1, e^{K-2+u} > 1 + A u (exact Taylor lower bound of
      the exponential), tail sign a+t+eps-K eps nu^t >= 0 for t = 0..m,
      K/(K-1) >= 1+eps.  m is the largest integer z >= 0 with phi(z) > 0 (phi is
      unimodal with phi(0) = theta >= 0, so this is floor of the positive root
      used by the delivered script; the convention at an exact integer root is
      recorded).
  C2  sequence legality (14)(15) exactly on K = 2..6 x 15 rational eta (plus the
      instruction's points below K): r_x, h_x >= 0 and non-increasing, p_x >= u_x
      >= 0 for every x, K g_x >= r_x (g = r - h) for every x <= M, h_M = 0,
      r_{M+1} = 0, phase splices, Fbar(K,0) = rho_K + eps*delta, and the K = 3,
      eta = 3/2 numbers (eps = 1/26, gamma = 6/13, Fbar = 59/104, rho_3 = 9/16).

Everything that is not decided by a symbolic identity is decided in exact rational
arithmetic; floats are only printed.  Run: python3 results/J9/j9_own_checks.py
(exit 0 iff all PASS).  Not covered (need the proof file): the T-dependent lift
F_{T,O}, G_O, C3/C4 exhaustion, D, E, comparison, card T10e.
"""
import sys
from fractions import Fraction as Fr
from math import factorial

import sympy as sp

fails, n_pass = [], 0


def check(name, ok, detail=''):
    global n_pass
    print(('PASS' if ok else 'FAIL'), name, detail)
    if ok:
        n_pass += 1
    else:
        fails.append(name)


# ------------------------------------------------------------------ S: symbolic
K, eta, a, eps, m, t, s, gam_s = sp.symbols('K eta a epsilon m t s gamma', positive=True)
P, Qx, Nt, Nm = sp.symbols('P Q_x N_t N_m', positive=True)   # q^j, q^x, nu^t, nu^m
k1 = (K - 1) * eta + 1
q = (K - 1) * eta / k1
delta = P / (K * eta)
C = k1 / K
nu = eta / (eta - 1)
theta = (K - 1) * eta - a
D = K * eta - a
j = K - a
eps_def = (m - theta) / (Nm - 1)
gamma = D - m - eps


def zero(e):
    return sp.cancel(sp.together(e)) == 0


# phases, written with the free symbols (r_geo(x) uses Qx = q^x; r at j uses P)
r_geo_x, h_geo_x = Qx, (K - 1) / K * Qx                    # generic x < j (and x = j with Qx = P)
r_geo_x1, h_geo_x1 = Qx * q, (K - 1) / K * Qx * q          # x + 1
r_lin = lambda x: P - (x - j + eps) * delta                 # j+1 <= x <= K
h_lin = lambda x: ((K - 1) * eta - (x - j)) * delta         # j <= x <= K
r_tail = lambda tt: (D - eps - tt) * delta                  # x = K + tt, 0 <= tt <= m
h_tail = lambda tt, N: (theta - tt + eps * (N - 1)) * delta  # N = nu^tt

print('== S: identities of the delivered script, rational-function formulation ==')
Vj = 1 - P * (1 - (K - j) / (K * eta))
check('S (5) rho = 1 - P + a delta', zero(Vj - (1 - P + a * delta)))
phi_m = D - m - eta / Nm
phi_m1 = D - (m + 1) - eta / (nu * Nm)
check('S (10a) gamma = nu^m phi(m)/(nu^m - 1)', zero((D - m - eps_def) - Nm * phi_m / (Nm - 1)))
check('S (10b) gamma - 1 = nu^m phi(m+1)/(nu^m - 1)', zero((D - m - eps_def - 1) - Nm * phi_m1 / (Nm - 1)))
# phi(theta+1) identity: nu^{-(theta+1)} = nu^{-theta}/nu; use free symbol for nu^{-theta}
Nth = sp.Symbol('N_theta', positive=True)
check('S phi(theta+1) = (eta-1)(1 - nu^-theta)',
      zero((D - (theta + 1) - eta * Nth / nu) - (eta - 1) * (1 - Nth)))
g_tail = lambda tt, N: r_tail(tt) - h_tail(tt, N)
check('S (19) g_{K+t} = (eta - eps nu^t) delta', zero(g_tail(t, Nt) - (eta - eps * Nt) * delta))
check('S (20) h_M = 0 with eps def', zero(h_tail(m, Nm).subs(eps, eps_def)))
check('S (20) r_M = gamma delta', zero(r_tail(m) - gamma * delta))
check('S (21a) g_{K+t+1} = nu (g_{K+t} - delta)',
      zero(g_tail(t + 1, nu * Nt) - nu * (g_tail(t, Nt) - delta)))
check('S (21b) u_{K+t} = g_{K+t+1}/eta',
      zero((h_tail(t, Nt) - h_tail(t + 1, nu * Nt)) - g_tail(t + 1, nu * Nt) / eta))
# the three identities the delivered script could not simplify: geo at x = j-1, j
r_jm1, h_jm1 = P / q, (K - 1) / K * P / q
r_j, h_j = P, (K - 1) / K * P
check('S (22) p_{j-1} = K delta/(K-1)   [delivered script: False]', zero((r_jm1 - r_j) - K * delta / (K - 1)))
check('S (22) p_j = (1 + eps) delta', zero((r_j - r_lin(j + 1)) - (1 + eps) * delta))
check('S (22) p_x = delta inside lin', zero((r_lin(s) - r_lin(s + 1)) - delta))
check('S (22) p_K = delta (lin -> tail)', zero((r_lin(K) - r_tail(1)) - delta))
check('S (22) p_x = delta inside tail', zero((r_tail(t) - r_tail(t + 1)) - delta))
check('S (23) u_{j-1} = delta   [delivered script: False]', zero((h_jm1 - h_j) - delta))
check('S (23) u_x = delta inside lin', zero((h_lin(s) - h_lin(s + 1)) - delta))
check('S splice h at x = j (geo = lin)', zero(h_j - h_lin(j)))
check('S splice h at x = K (lin = tail)', zero(h_lin(K) - h_tail(0, 1)))
check('S splice r at x = K (lin = tail)', zero(r_lin(K) - r_tail(0)))
check('S (26) K g_{j+s} - r_{j+s} = (s - (K-1) eps) delta',
      zero(K * (r_lin(j + s) - h_lin(j + s)) - r_lin(j + s) - (s - (K - 1) * eps) * delta))
check('S g_{j+s} = (eta - eps) delta', zero((r_lin(j + s) - h_lin(j + s)) - (eta - eps) * delta))
check('S g_j = eta delta', zero((r_j - h_j) - eta * delta))
e27 = K * g_tail(t, Nt) - r_tail(t)
check('S (27) K g_{K+t} - r_{K+t} = (a + t + eps - K eps nu^t) delta',
      zero(e27 - (a + t + eps - K * eps * Nt) * delta))
check('S (27) at t = m equals (K-1) gamma delta',
      zero((e27.subs({t: m, Nt: Nm}) - (K - 1) * (D - m - eps) * delta).subs(eps, eps_def)))
check('S (27) at t = 0 = (a - (K-1) eps) delta', zero(e27.subs({t: 0, Nt: 1}) - (a - (K - 1) * eps) * delta))
# band rows (y = 0 edges): Delta H = eta u_{x-1}; geo with Qx = q^{x-1}
check('S row x<j: eta u_{x-1} = q^x/K   [delivered script: False]',
      zero(eta * (h_geo_x - h_geo_x1) - Qx * q / K))
check('S row x<j: p_x = q^x/k1', zero((r_geo_x - r_geo_x1) - Qx / k1))
check('S row x<j: g_x = q^x/K', zero((r_geo_x - h_geo_x) - Qx / K))
check('S row x=0: C - eta h_0 = 1/K', zero(C - eta * (K - 1) / K - 1 / K))
check('S row x=0: H(0,0) = C - r_0 - (eta-1) h_0 = 0', zero(C - 1 - (eta - 1) * (K - 1) / K))
check('S row j<x<=K: eta u_{x-1} = eta delta', zero(eta * (h_lin(s) - h_lin(s + 1)) - eta * delta))
check('S row K<x<M: eta u_{x-1} = g_x', zero(eta * (h_tail(t, Nt) - h_tail(t + 1, nu * Nt)) - g_tail(t + 1, nu * Nt)))
check('S (33) p_j - p_{j+1} = eps delta', zero((r_j - r_lin(j + 1)) - (r_lin(j + 1) - r_lin(j + 2)) - eps * delta))
check('S (34) p_j - u_j = eps delta', zero((r_j - r_lin(j + 1)) - (h_lin(j) - h_lin(j + 1)) - eps * delta))
check('S (38) Fbar(K,0) = 1 - r_K = 1 - P + (a + eps) delta', zero((1 - r_lin(K)) - (1 - P + (a + eps) * delta)))
check('S Fbar(K,0) - rho_K = eps delta', zero((1 - r_lin(K)) - Vj - eps * delta))
check('S first O at empty: g_0 = 1/K', zero((1 - (K - 1) / K) - 1 / K))
check('S second O at {o}: h_0/(K-1) = 1/K', zero((K - 1) / K / (K - 1) - 1 / K))
check('S canonical: eta u_0 = q/K', zero(eta * ((K - 1) / K) * (1 - q) - q / K))
check('S q/K < 1/K  <=>  q < 1', zero(1 - q - 1 / k1))

# ---------------------------------------------------------------- exact helpers
def params(Kv, ev):
    av = int(ev)                     # floor(eta), eta rational
    jv = Kv - av
    k1v = (Kv - 1) * ev + 1
    qv = (Kv - 1) * ev / k1v
    Pv = qv ** jv
    dv = Pv / (Kv * ev)
    nuv = ev / (ev - 1)
    thv = (Kv - 1) * ev - av
    Dv = Kv * ev - av
    phi = lambda z: Dv - z - ev / nuv ** z
    # largest integer z >= 0 with phi(z) > 0 (phi unimodal, phi(0) = theta >= 0)
    mv = 0
    z = 0
    while True:
        if phi(z) > 0:
            mv = z
            z += 1
        else:
            break
    tie = (phi(mv + 1) == 0)         # exact integer root: delivered script's floor(root) gives mv
    epsv = (mv - thv) / (nuv ** mv - 1)
    gv = Dv - mv - epsv
    return dict(K=Kv, eta=ev, a=av, j=jv, k1=k1v, q=qv, P=Pv, delta=dv, nu=nuv, theta=thv,
                D=Dv, m=mv, eps=epsv, gamma=gv, M=Kv + mv, tie=tie, phi=phi)


def seqs(p):
    Kv, jv, Mv = p['K'], p['j'], p['M']
    r, h = {}, {}
    for x in range(0, Mv + 2):
        if x <= jv:
            r[x] = p['q'] ** x
            h[x] = Fr(Kv - 1, Kv) * p['q'] ** x
        elif x <= Kv:
            r[x] = p['P'] - (x - jv + p['eps']) * p['delta']
            h[x] = ((Kv - 1) * p['eta'] - (x - jv)) * p['delta']
        elif x <= Mv:
            tt = x - Kv
            r[x] = (p['D'] - p['eps'] - tt) * p['delta']
            h[x] = (p['theta'] - tt + p['eps'] * (p['nu'] ** tt - 1)) * p['delta']
        else:
            r[x] = Fr(0)
            h[x] = Fr(0)
    return r, h


def exp_lower(x, N=120):
    """exact rational lower bound of e^x for rational x >= 0 (partial sum, all terms > 0)"""
    return sum(x ** k / factorial(k) for k in range(N))


def rho(Kv, ev):
    k1v = (Kv - 1) * ev + 1
    qv = (Kv - 1) * ev / k1v
    return min(1 - qv ** jj * (1 - Fr(Kv - jj) / (Kv * ev)) for jj in range(Kv))


def eta_grid(Kv):
    pts = [1 + Fr(Kv - 1) * i / 16 for i in range(1, 16)]
    for e0 in (Fr(6, 5), Fr(3, 2), Fr(5, 2)):
        if 1 < e0 < Kv and e0 not in pts:
            pts.append(e0)
    return sorted(pts)


# ------------------------------------------------------------ P: parameter lemma
print('\n== P: parameter lemma, exact, K = 2..12 x rational eta in (1, K) ==')
worst = {}
def upd(name, val, where):
    if name not in worst or val < worst[name][0]:
        worst[name] = (val, where)
ties = []
n_pts = 0
for Kv in range(2, 13):
    for ev in eta_grid(Kv):
        p = params(Kv, ev)
        n_pts += 1
        where = f'K={Kv} eta={ev}'
        if p['tie']:
            ties.append(where)
        upd('m - theta > 0', p['m'] - p['theta'], where)
        upd('eta - 1 - eps > 0', p['eta'] - 1 - p['eps'], where)
        upd('eps > 0', p['eps'], where)
        upd('1/(K-1) - eps > 0', Fr(1, Kv - 1) - p['eps'], where)
        upd('gamma >= 0', p['gamma'], where)
        upd('1 - gamma > 0', 1 - p['gamma'], where)
        upd('K/(K-1) - (1+eps) > 0', Fr(Kv, Kv - 1) - 1 - p['eps'], where)
        for tt in range(0, p['m'] + 1):
            upd('tail sign a+t+eps-K eps nu^t >= 0', p['a'] + tt + p['eps'] - Kv * p['eps'] * p['nu'] ** tt, where + f' t={tt}')
        if Kv >= 3:
            u = (p['m'] - p['theta']) / p['eta']
            A = (Kv - 1) * p['eta']
            upd('e^{K-2+u} - 1 - A u > 0 (exact lower bound)', exp_lower(Kv - 2 + u) - 1 - A * u, where)
        # phi sign pattern defining m
        upd('phi(m) > 0', p['phi'](p['m']), where)
        upd('-phi(m+1) >= 0', -p['phi'](p['m'] + 1), where)
strict = {'m - theta > 0', 'eta - 1 - eps > 0', 'eps > 0', '1/(K-1) - eps > 0', '1 - gamma > 0',
          'K/(K-1) - (1+eps) > 0', 'e^{K-2+u} - 1 - A u > 0 (exact lower bound)', 'phi(m) > 0'}
for name, (val, where) in worst.items():
    ok = (val > 0) if name in strict else (val >= 0)
    shown = str(val) if len(str(val)) <= 60 else f'(exact rational, {len(str(val))} chars)'
    check(f'P {name}', ok, f'min = {shown} ({float(val):.3e}) at {where}')
print(f'   grid points: {n_pts}; exact-integer-root ties (m convention): {ties or "none"}')

# --------------------------------------------------------- C2: sequence legality
print('\n== C2: sequence legality (14)(15), exact, K = 2..6 x rational eta ==')
c2_pts = 0
c2_bad = []
for Kv in range(2, 7):
    for ev in eta_grid(Kv):
        p = params(Kv, ev)
        r, h = seqs(p)
        Mv = p['M']
        c2_pts += 1
        where = f'K={Kv} eta={ev} m={p["m"]}'
        for x in range(0, Mv + 1):
            px, ux = r[x] - r[x + 1], h[x] - h[x + 1]
            gx = r[x] - h[x]
            conds = [('r>=0', r[x] >= 0), ('h>=0', h[x] >= 0), ('p>=u', px >= ux), ('u>=0', ux >= 0),
                     ('Kg>=r', Kv * gx >= r[x])]
            for nm, ok in conds:
                if not ok:
                    c2_bad.append((where, x, nm))
        if h[Mv] != 0:
            c2_bad.append((where, Mv, 'h_M=0'))
        if r[Mv + 1] != 0 or r[Mv] != p['gamma'] * p['delta']:
            c2_bad.append((where, Mv, 'r_M=gamma delta, r_{M+1}=0'))
        if 1 - r[Kv] != rho(Kv, ev) + p['eps'] * p['delta']:
            c2_bad.append((where, Kv, 'Fbar(K,0) = rho_K + eps delta'))
        # phase splices from the two formulas
        if h[p['j']] != Fr(Kv - 1, Kv) * p['q'] ** p['j']:
            c2_bad.append((where, p['j'], 'h splice at j'))
check('C2 r_x, h_x >= 0, non-increasing, p_x >= u_x >= 0, K g_x >= r_x for all x <= M; h_M = 0; '
      'r_M = gamma delta; r_{M+1} = 0; Fbar(K,0) = rho_K + eps delta; h splice at j',
      not c2_bad, f'{c2_pts} (K, eta) points; violations: {c2_bad[:5]}')
# equality structure (informative, exact): K g_x = r_x on the geo phase, p = u on the open lin phase
Kv, ev = 3, Fr(3, 2)
p = params(Kv, ev)
r, h = seqs(p)
check('C2 K=3, eta=3/2: m = 3, eps = 1/26, gamma = 6/13, delta = 1/8',
      (p['m'], p['eps'], p['gamma'], p['delta']) == (3, Fr(1, 26), Fr(6, 13), Fr(1, 8)))
check('C2 K=3, eta=3/2: Fbar(K,0) = 1 - r_3 = 59/104 = 9/16 + 1/208; rho_3 = 9/16',
      1 - r[3] == Fr(59, 104) and rho(3, Fr(3, 2)) == Fr(9, 16) and 1 - r[3] - Fr(9, 16) == Fr(1, 208))
print('   K=3, eta=3/2 sequences: r =', [str(r[x]) for x in range(0, p['M'] + 2)])
print('                           h =', [str(h[x]) for x in range(0, p['M'] + 2)])
print('   (F(T) = rho_3 = 9/16 as printed by the delivered script is the T-dependent value;'
      ' its lift F_{T,O} is not in the script and is not checked here.)')

print()
print(f'PASS {n_pass}, FAIL {len(fails)}')
print('ALL PASS' if not fails else 'FAILURES: ' + '; '.join(fails))
sys.exit(0 if not fails else 1)

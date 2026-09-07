"""H-J3 gate: independent verification of the J3 structure note's claims.

The J3 deliverable (results/J3_proof_structure.md) arrived WITHOUT its
oracle script (J3_structure_oracles.py was not delivered), so this script
re-implements the gate from scratch, per the TASKS6 H-J3 gate item:

 1. [sympy] sharp form  d - g/eta >= (1 - 1/eta)(g - h)  is algebraically
    equivalent to coherence (ii)  (1 - 1/eta) h >= g - d.
 2. [sympy] adjacent-branch difference V_i - V_{i+1} = q^i (K-i-eta)/(K eta k1).
 3. [sympy] the J3 recurrences: gamma r' = r - K d with r' = r - d force
    d = r/k1 and r' = q r  (gamma = 1 - 1/eta).
 4. [exact] the two K=3, eta=2 optimal chosen-gain sequences
    (1/5, 2/15, 2/15) and (1/5, 4/25, 8/75) match the j=1 / j=2 two-phase
    formulas and both sum to 7/15 = V_1(2) = V_2(2).
 5. [LP, HiGHS] facet uniqueness, re-implemented (J3's setup, our code):
    for K = 2..6, every j, eta = K-j+1/4 and K-j+3/4 (40 facets), fix
    sum_t d_t = V_j and minimize/maximize every coordinate of the reduced
    LP of code/reduced_lp.py (2,480 LPs).  Every coordinate range must
    collapse to  d_t = q^t/k1 (t<j), q^j/(K eta) (t>=j)  and
    g_{t,i} = q^{min(t,j)}/K  (0<=t<=K), within 1e-9.

Exit 0 iff everything passes.  Run: python3 results/H_J3_gate_check.py
"""
import os, sys
import numpy as np
import sympy as sp
from fractions import Fraction as Fr
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

fails = []


def check(name, ok, detail=''):
    print(('PASS' if ok else 'FAIL'), name, detail)
    if not ok:
        fails.append(name)


# ---- 1. sharp form <=> coherence (ii) -------------------------------------
d, g, h, eta = sp.symbols('d g h eta', positive=True)
sharp = (d - g/eta) - (1 - 1/eta)*(g - h)
coh2 = (1 - 1/eta)*h - (g - d)
check('sharp form == coherence (ii) rearranged', sp.simplify(sharp - coh2) == 0)

# ---- 2. adjacent difference ------------------------------------------------
K, i = sp.symbols('K i', positive=True)
k1 = (K - 1)*eta + 1
q = (K - 1)*eta/k1
V = lambda j: 1 - q**j*(1 - (K - j)/(K*eta))
diff = sp.simplify(V(i) - V(i + 1) - q**i*(K - i - eta)/(K*eta*k1))
check('V_i - V_{i+1} identity', diff == 0)

# ---- 3. recurrences --------------------------------------------------------
r = sp.symbols('r', positive=True)
gamma = 1 - 1/eta
d_sol = sp.solve(sp.Eq(gamma*(r - d), r - K*d), d)[0]
check('gamma r\' = r - K d  =>  d = r/k1', sp.simplify(d_sol - r/k1) == 0)
check('r\' = q r', sp.simplify((r - d_sol) - q*r) == 0)

# ---- 4. the two K=3, eta=2 sequences ---------------------------------------
def two_phase(Kv, ev, j):
    k1v = (Kv - 1)*ev + 1
    qv = Fr((Kv - 1)*ev, k1v) if isinstance(ev, int) else (Kv - 1)*ev/k1v
    k1v = Fr(k1v)
    qv = Fr((Kv - 1)*ev)/k1v
    return [qv**t/k1v if t < j else qv**j/(Fr(Kv*ev))
            for t in range(Kv)]
s1 = two_phase(3, 2, 1)
s2 = two_phase(3, 2, 2)
check('K=3 eta=2, j=1 sequence', s1 == [Fr(1, 5), Fr(2, 15), Fr(2, 15)])
check('K=3 eta=2, j=2 sequence', s2 == [Fr(1, 5), Fr(4, 25), Fr(8, 75)])
check('both sum to 7/15', sum(s1) == Fr(7, 15) == sum(s2))
Vj = lambda Kv, ev, j: 1 - (Fr((Kv-1)*ev, (Kv-1)*ev+1))**j*(1 - Fr(Kv-j, Kv*ev))
check('7/15 = V_1(2) = V_2(2) at K=3', Vj(3, 2, 1) == Fr(7, 15) == Vj(3, 2, 2))

# ---- 5. facet uniqueness (re-implementation) -------------------------------
def facet_ranges(Kv, ev):
    nd = Kv
    gidx = lambda t, ii: nd + t*Kv + ii
    nv = nd + (Kv + 1)*Kv
    rows, cols, vals, b = [], [], [], []
    rr = 0
    def ub(c, rhs=0.0):
        nonlocal rr
        for k, v in c.items():
            rows.append(rr); cols.append(k); vals.append(v)
        b.append(rhs); rr += 1
    for t in range(Kv):
        c = {gidx(t, ii): -1.0 for ii in range(Kv)}
        for ss in range(t):
            c[ss] = -1.0
        ub(c, -1.0)
        for ii in range(Kv):
            ub({gidx(t, ii): 1.0/ev, t: -1.0})
            ub({gidx(t + 1, ii): 1.0, gidx(t, ii): -1.0})
            ub({gidx(t, ii): 1.0, t: -1.0, gidx(t + 1, ii): -(1 - 1/ev)})
    A = coo_matrix((vals, (rows, cols)), shape=(rr, nv)).tocsr()
    return A, np.array(b), nv, gidx


def expected(Kv, ev, j):
    k1v = (Kv - 1)*ev + 1
    qv = (Kv - 1)*ev/k1v
    dts = [qv**t/k1v if t < j else qv**j/(Kv*ev) for t in range(Kv)]
    gts = [[qv**min(t, j)/Kv]*Kv for t in range(Kv + 1)]
    return dts, gts


n_lp = 0
worst = 0.0
ok_all = True
for Kv in range(2, 7):
    for j in range(Kv):
        for frac in (0.25, 0.75):
            ev = (Kv - j) + frac
            A, b, nv, gidx = facet_ranges(Kv, ev)
            k1v = (Kv - 1)*ev + 1
            qv = (Kv - 1)*ev/k1v
            Vjv = 1 - qv**j*(1 - (Kv - j)/(Kv*ev))
            Aeq = np.zeros((1, nv)); Aeq[0, :Kv] = 1
            dts, gts = expected(Kv, ev, j)
            exp_vec = list(dts) + [g for row in gts for g in row]
            for v in range(nv):
                for sign in (1.0, -1.0):
                    obj = np.zeros(nv); obj[v] = sign
                    res = linprog(obj, A_ub=A, b_ub=b, A_eq=Aeq,
                                  b_eq=[Vjv], bounds=[(0, None)]*nv,
                                  method='highs')
                    n_lp += 1
                    if not res.success:
                        ok_all = False
                        print('  LP FAIL', Kv, j, ev, v, sign)
                        continue
                    dev = abs(sign*res.fun - exp_vec[v])
                    worst = max(worst, dev)
                    if dev > 1e-9:
                        ok_all = False
                        print('  RANGE FAIL', Kv, j, round(ev, 2), v,
                              'got', sign*res.fun, 'exp', exp_vec[v])
check('facet uniqueness on 40 facets', ok_all,
      f'({n_lp} LPs, max coordinate deviation {worst:.2e})')

print()
print('ALL PASS' if not fails else f'FAILURES: {fails}')
sys.exit(0 if not fails else 1)

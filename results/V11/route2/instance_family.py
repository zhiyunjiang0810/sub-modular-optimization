"""ROUTE-TWO: the candidate attaining instance family I(K,eta,j) and an exact check.

Ground set N = {e_0..e_{K-1}} cup {o_1..o_K}, n = 2K.
f is the coverage function of the following atoms (all measures exact Fractions):
  R_t = q^t with q = (K-1)eta/k1, k1 = (K-1)eta+1;  g_t = R_t/k1 for t<j;
  g_t = R_j/(K eta) for t>=j.
  atoms  a(i,s)  i=1..K, s=0..j-1 : measure g_s/K      (head slice of A_{o_i})
  atoms  a(i,oo) i=1..K           : measure R_j/K      (never-covered part)
  atoms  tau_t   t=j..K-1         : measure R_j/(K eta)(private part of tail e_t)
  A_{o_i}        = {a(i,s) : s<j} cup {a(i,oo)}                 (measure 1/K)
  A_{e_t}, t<j   = {a(i,t) : i=1..K}                            (measure g_t)
  A_{e_t}, t>=j  = {tau_t}                                      (measure g_t)

f(S) = sum of measures of atoms covered by S; monotone submodular by construction.
This module also builds the LP that asks for a predictor ft with
  d_e(S)/eta <= dt_e(S) <= d_e(S)  and  dt_{e_t}(S^t) >= dt_x(S^t),
i.e. the feasibility of an adversarial predictor on top of this fixed f.
"""
import itertools
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog


def profile(K, eta, j):
    k1 = (K - 1) * eta + 1
    q = F((K - 1) * eta, 1) / k1
    R = [F(1)]
    g = []
    for t in range(K):
        if t < j:
            g.append(R[t] / k1)
        else:
            g.append(R[j] / (K * eta))
        R.append(R[t] - g[t])
    m = []
    for t in range(K + 1):
        m.append(R[t] / K if t <= j else R[j] / K)
    return R, g, m, k1, q


def build_f(K, eta, j):
    R, g, m, k1, q = profile(K, eta, j)
    atoms = []           # (measure, frozenset of element indices covering it)
    # elements: 0..K-1 = e_t ; K..2K-1 = o_i
    for i in range(K):
        for s in range(j):
            atoms.append((g[s] / K, frozenset({s, K + i})))
        atoms.append((R[j] / K, frozenset({K + i})))
    for t in range(j, K):
        atoms.append((g[t], frozenset({t})))
    n = 2 * K
    NS = 1 << n

    fv = [F(0)] * NS
    for S in range(NS):
        tot = F(0)
        for meas, cov in atoms:
            if any((S >> c) & 1 for c in cov):
                tot += meas
        fv[S] = tot
    return fv, atoms, (R, g, m, k1, q)


def checks(K, eta, j, verbose=True):
    n = 2 * K
    NS = 1 << n
    fv, atoms, (R, g, m, k1, q) = build_f(K, eta, j)
    d = lambda e, S: fv[S | (1 << e)] - fv[S]
    ok = {}
    ok['monotone'] = all(d(e, S) >= 0 for S in range(NS) for e in range(n)
                         if not (S >> e) & 1)
    ok['submodular'] = all(d(e, S) >= d(e, S | (1 << x))
                           for S in range(NS) for e in range(n) for x in range(n)
                           if e != x and not (S >> e) & 1 and not (S >> x) & 1)
    O = sum(1 << i for i in range(K, n))
    ok['f(O)=1'] = fv[O] == 1
    best = max(fv[sum(1 << i for i in T)] for T in itertools.combinations(range(n), K))
    ok['F_OPT=1'] = best == 1
    SK = (1 << K) - 1
    alg = fv[SK]
    Vj = 1 - q ** j * (1 - F(K - j, K) / eta)
    ok['F_ALG=V_j'] = alg == Vj
    # trajectory profile
    ok['profile'] = all(d(t, (1 << t) - 1) == g[t] for t in range(K)) and \
                    all(d(K + i, (1 << t) - 1) == m[t] for t in range(K) for i in range(K))
    if verbose:
        print(f" K={K} eta={eta} j={j}: F_ALG={alg}={float(alg):.8f}  V_j={Vj} ", ok)
    return fv, ok, alg, Vj


def predictor_lp(K, eta, j, verbose=True):
    """Feasibility LP for ft given the fixed f above (floats; exact check separate)."""
    n = 2 * K
    NS = 1 << n
    fv, _, _ = build_f(K, eta, j)
    fvf = np.array([float(v) for v in fv])
    etaf = float(eta)
    rows, rhs, eqr, eqb = [], [], [], []

    def z():
        return np.zeros(NS)

    r = z(); r[0] = 1.0
    eqr.append(r); eqb.append(0.0)
    for S in range(NS):
        for e in range(n):
            if (S >> e) & 1:
                continue
            Se = S | (1 << e)
            de = fvf[Se] - fvf[S]
            r = z(); r[Se] = 1.0; r[S] = -1.0
            rows.append(r); rhs.append(de)                 # dt <= d
            r = z(); r[Se] = -1.0; r[S] = 1.0
            rows.append(r); rhs.append(-de / etaf)         # -dt <= -d/eta
    for t in range(K):
        St = (1 << t) - 1
        Ste = St | (1 << t)
        for x in range(n):
            if (St >> x) & 1 or x == t:
                continue
            Sx = St | (1 << x)
            r = z(); r[Sx] += 1.0; r[Ste] -= 1.0
            rows.append(r); rhs.append(0.0)                # ft(St+x) <= ft(St+e_t)
    res = linprog(np.zeros(NS), A_ub=np.array(rows), b_ub=np.array(rhs),
                  A_eq=np.array(eqr), b_eq=np.array(eqb),
                  bounds=[(None, None)] * NS, method="highs")
    if verbose:
        print(f"   predictor LP K={K} eta={eta} j={j}: status={res.status} "
              f"({'FEASIBLE' if res.status == 0 else res.message})")
    return res, fv


if __name__ == '__main__':
    for K, eta, j in [(2, F(3, 2), 1), (2, F(5, 2), 0), (3, F(3, 2), 2),
                      (3, F(5, 2), 1), (3, F(7, 2), 0), (4, F(3, 2), 3),
                      (4, F(5, 2), 2), (4, F(7, 2), 1)]:
        checks(K, eta, j)
        predictor_lp(K, eta, j)

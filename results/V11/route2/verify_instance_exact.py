"""ROUTE-TWO: exact rational verification of the attaining family I(K,eta,j).

f  = coverage function of the atom system described in instance_family.py
ft = f - (1-1/eta) * max_i mu(A_{o_i} cap union_{x in S} A_x)          (closed form)

Everything is Fraction arithmetic; floats appear only in printouts.
Checked for every S and every e:
  monotone, submodular, band  d/eta <= dt <= d,
  greedy picks e_0,...,e_{K-1} in order under adversarial tie breaking,
  f(O) = 1 = max over K-subsets,  f(S^K) = V_j(eta).
"""
import itertools
from fractions import Fraction as F


def build(K, eta, j):
    """Return (n, fvals, ftvals, data) as exact Fractions."""
    k1 = (K - 1) * eta + 1
    q = F((K - 1) * eta, 1) / k1
    R = [F(1)]
    g = []
    for t in range(K):
        g.append(R[t] / k1 if t < j else R[j] / (K * eta))
        R.append(R[t] - g[t])
    n = 2 * K
    NS = 1 << n
    # atoms: (measure, covering-element bitmask, owner o-index or None)
    atoms = []
    for i in range(K):
        oi = K + i
        for s in range(j):
            atoms.append((g[s] / K, (1 << s) | (1 << oi), i))
        atoms.append((R[j] / K, 1 << oi, i))
    for t in range(j, K):
        atoms.append((g[t], 1 << t, None))

    fv = [F(0)] * NS
    beta = [F(0)] * NS
    for S in range(NS):
        tot = F(0)
        per = [F(0)] * K
        for meas, cov, owner in atoms:
            if S & cov:
                tot += meas
                if owner is not None:
                    per[owner] += meas
        fv[S] = tot
        beta[S] = max(per)
    theta = 1 - F(1, 1) / eta
    ftv = [fv[S] - theta * beta[S] for S in range(NS)]
    Vj = 1 - q ** j * (1 - F(K - j, K) / eta)
    return n, fv, ftv, dict(R=R, g=g, k1=k1, q=q, Vj=Vj, theta=theta)


def verify(K, eta, j, verbose=True):
    n, fv, ftv, D = build(K, eta, j)
    NS = 1 << n
    fails = []

    def d(e, S):
        return fv[S | (1 << e)] - fv[S]

    def dt(e, S):
        return ftv[S | (1 << e)] - ftv[S]

    if fv[0] != 0 or ftv[0] != 0:
        fails.append('f(empty) or ft(empty) nonzero')

    for S in range(NS):
        for e in range(n):
            if (S >> e) & 1:
                continue
            de, dte = d(e, S), dt(e, S)
            if de < 0:
                fails.append(('monotone', S, e))
            if dte * eta < de or dte > de:
                fails.append(('band', S, e, de, dte))
            if (de == 0) != (dte == 0):
                fails.append(('zero-preservation', S, e))
            for x in range(n):
                if x == e or (S >> x) & 1:
                    continue
                if d(e, S | (1 << x)) > de:
                    fails.append(('submodular', S, e, x))

    # greedy trace under adversarial ties
    St = 0
    for t in range(K):
        best = max(dt(x, St) for x in range(n) if not (St >> x) & 1)
        if dt(t, St) != best:
            fails.append(('greedy', t, float(dt(t, St)), float(best)))
        St |= 1 << t

    O = sum(1 << i for i in range(K, n))
    if fv[O] != 1:
        fails.append(('f(O)!=1', fv[O]))
    best = max(fv[sum(1 << i for i in T)] for T in itertools.combinations(range(n), K))
    if best != 1:
        fails.append(('F_OPT!=1', best))
    alg = fv[(1 << K) - 1]
    if alg != D['Vj']:
        fails.append(('F_ALG!=V_j', alg, D['Vj']))

    if verbose:
        tag = 'OK ' if not fails else 'FAIL'
        print(f" [{tag}] K={K} eta={eta} j={j}: F_ALG={alg} ({float(alg):.8f}) "
              f"= V_j={D['Vj']}   n={n}"
              + ('' if not fails else f"   fails={fails[:4]}"))
    return not fails


def Vj_of(K, eta, j):
    k1 = (K - 1) * eta + 1
    q = F((K - 1) * eta, 1) / k1
    return 1 - q ** j * (1 - F(K - j, K) / eta)


def jstar(K, eta):
    return min(range(K), key=lambda j: Vj_of(K, eta, j))


if __name__ == '__main__':
    etas = [F(1), F(5, 4), F(3, 2), F(2), F(9, 4), F(5, 2), F(3), F(7, 2), F(4),
            F(9, 2), F(5), F(6)]
    allok = True
    print("== every j, every eta (each instance realises V_j exactly) ==")
    for K in (2, 3, 4):
        for eta in etas:
            for j in range(K):
                allok &= verify(K, eta, j, verbose=False)
    print("  all (K,eta,j) instances valid:", allok)
    print("== the worst-case instance j = j*(eta) ==")
    for K in (2, 3, 4):
        for eta in etas:
            js = jstar(K, eta)
            ok = verify(K, eta, js, verbose=True)
            rho = min(Vj_of(K, eta, j) for j in range(K))
            assert Vj_of(K, eta, js) == rho
            allok &= ok
    print("ALL EXACT CHECKS PASSED:", allok)

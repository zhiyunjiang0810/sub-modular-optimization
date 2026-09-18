"""Two-pass driver for check_family.audit.

PASS 1 (cheap): admissibility (A)(B)(C), location bounds, gap formula and the
                exponential bound, on a large rational eta grid.
PASS 2 (full):  additionally the whole count-grid audit (monotone submodular,
                band on every edge, size-only surrogate, flatness past t*),
                on a smaller grid where t* stays small.
Exact arithmetic throughout.
"""
from fractions import Fraction as Fr
import check_family as cf


def cheap(K, eta):
    jj, rho = cf.argmin_j(K, eta)
    m, d = cf.select_m(K, eta)
    if m is None:
        return ['no m']
    _, q, nu = cf.params(K, eta)
    errs = []
    if not m >= eta * (K - 1):
        errs.append('A')
    if not m * d <= 1:
        errs.append('B')
    if not (m + 1) * d >= 1:
        errs.append('C')
    if (m * d <= 1) != (nu**m * (K * eta - m) >= K * eta):
        errs.append('B_alt')
    if not (eta * (K - 1) <= m < K * eta):
        errs.append('loc')
    if not m >= K:
        errs.append('m>=K')
    gap = q**jj * (K - jj) * (d - Fr(1) / (K * eta))
    if gap < 0:
        errs.append('gap<0')
    bound = Fr(1) / (K * (cf.E_HIGH**(K - 1) - K - 1))
    if not gap < bound:
        errs.append('bound')
    # key lemma:  eta * nu^{eta(K-1)} >= K e^{K-1}, used in the analytic proof.
    # checked only when eta(K-1) is an integer (exact rational power).
    p = eta * (K - 1)
    if p.denominator == 1:
        if not eta * nu**int(p) >= K * cf.E_HIGH**(K - 1):
            errs.append('keylemma')
    if eta >= K and rho != Fr(1) / eta:
        errs.append('rho=1/eta for eta>=K')
    return errs


def main():
    # ---------------- PASS 1 ----------------
    etas = sorted({Fr(a, b) for b in (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 50, 200)
                   for a in range(b + 1, 25 * b + 1)})
    bad, n = [], 0
    for K in range(3, 15):
        for eta in etas:
            e = cheap(K, eta)
            n += 1
            if e:
                bad.append((K, eta, e))
    print('PASS1 cells:', n, 'failures:', len(bad))
    for b in bad[:20]:
        print('   FAIL', b)

    # ---------------- PASS 2 ----------------
    etas2 = sorted({Fr(a, b) for b in (1, 2, 3, 4, 5, 8)
                    for a in range(b + 1, 6 * b + 1)})
    bad2, n2, worst = [], 0, None
    keys = ('A', 'B', 'C', 'B_alt', 'loc', 'seq', 'submod', 'band',
            'sizeonly', 'flat', 'gap_formula', 'bound_ok')
    for K in range(3, 8):
        for eta in etas2:
            rep = cf.audit(K, eta)
            n2 += 1
            if 'fail' in rep or any(not rep.get(k, True) for k in keys):
                bad2.append(rep)
            else:
                rr = float(rep['gap']) / rep['bound']
                if worst is None or rr > worst[0]:
                    worst = (rr, K, str(eta), rep['m'], rep['j'])
    print('PASS2 cells:', n2, 'failures:', len(bad2))
    for rep in bad2[:10]:
        print('   FAIL', rep['K'], rep['eta'],
              {k: rep.get(k) for k in keys}, rep.get('msgs'))
    print('worst gap/bound ratio: %.6g at K=%d eta=%s m=%d j=%d' % worst)


if __name__ == '__main__':
    main()

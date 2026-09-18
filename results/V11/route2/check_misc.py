"""Two side checks used in the write-up.

M1  n = K+1 witness for step D5.1: the queries S_e = N \\ {e} separate the single
    B element from the K elements of O, because H(1,K-1) != H(0,K) (a_1 > 0).
M2  step D6 lemma: beta_{j+1} <= beta_j  <=>  eta >= K - j,
    with beta_j = q^j (1 - (K-j)/(K eta)).
Exact arithmetic.
"""
from fractions import Fraction as Fr
import check_family as cf

print('M1 : n=K+1 separating witness')
for K, eta in [(3, Fr(3, 2)), (4, Fr(2)), (5, Fr(7, 3)), (6, Fr(11, 4)), (7, Fr(3))]:
    j, rho = cf.argmin_j(K, eta)
    m, d = cf.select_m(K, eta)
    r, g, a, F, H, X, tstar, Q, D, q, nu, C = cf.build(K, eta, j, m, d)
    print('   K=%d eta=%-6s a_1=%-12s H(1,K-1)=%-14s H(0,K)=%-10s distinct=%s'
          % (K, eta, a(1), H(1, K - 1), H(0, K), H(1, K - 1) != H(0, K)))

print('M2 : beta monotonicity')
bad = []
for K in range(3, 14):
    for b in (1, 2, 3, 4, 5, 8):
        for aa in range(b + 1, 20 * b + 1):
            eta = Fr(aa, b)
            _, q, _ = cf.params(K, eta)
            beta = lambda jj: q**jj * (1 - Fr(K - jj, 1) / (K * eta))
            for jj in range(K - 1):
                if (beta(jj + 1) <= beta(jj)) != (eta >= K - jj):
                    bad.append((K, eta, jj))
print('   failures:', len(bad), bad[:5])

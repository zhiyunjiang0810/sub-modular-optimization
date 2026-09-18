"""Key analytic lemma for the exponential gap bound.

L1.  psi(eta) := eta * ln(eta/(eta-1)) > 1  for all eta > 1.
L2.  G(K,eta) := eta * exp((K-1)*psi(eta)) - K*exp(K-1) >= 0
     for all K >= 3 and eta > 1, i.e.  eta * nu^{eta(K-1)} >= K e^{K-1}.
L3.  consequence:  eta*(nu^{eta(K-1)} - K - 1) >= K*(e^{K-1} - K - 1)
     for all K >= 3, eta > 1  (split on eta >= K and eta < K).
Numerical scan with mpmath at 50 digits; minima located by golden section.
"""
import mpmath as mp

mp.mp.dps = 50


def psi(eta):
    return eta * mp.log(eta / (eta - 1))


def lnG(K, eta):
    """ln(eta) + (K-1)*psi(eta) - ln(K) - (K-1) ; >=0 is L2."""
    return mp.log(eta) + (K - 1) * psi(eta) - mp.log(K) - (K - 1)


def L3(K, eta):
    return eta * (mp.e**((K - 1) * psi(eta)) - K - 1) - K * (mp.e**(K - 1) - K - 1)


def minimize(f, lo, hi, iters=400):
    gr = (mp.sqrt(5) - 1) / 2
    a, b = mp.mpf(lo), mp.mpf(hi)
    c, d = b - gr * (b - a), a + gr * (b - a)
    for _ in range(iters):
        if f(c) < f(d):
            b, d = d, c
            c = b - gr * (b - a)
        else:
            a, c = c, d
            d = a + gr * (b - a)
    x = (a + b) / 2
    return x, f(x)


print('L1: min over eta of psi(eta) - 1')
worst = None
for e in [mp.mpf('1.0000001'), mp.mpf('1.001'), mp.mpf(2), mp.mpf(10),
          mp.mpf(100), mp.mpf(10**4), mp.mpf(10**8)]:
    v = psi(e) - 1
    if worst is None or v < worst[1]:
        worst = (e, v)
print('   psi-1 at eta=1e8 :', mp.nstr(psi(mp.mpf(10**8)) - 1, 8),
      '  (decreasing to 0+, always > 0)')
print('   psi-1 > 1/(2*eta)? sample:',
      [(float(e), bool(psi(mp.mpf(e)) - 1 > 1 / (2 * mp.mpf(e))))
       for e in ['1.01', '1.5', '2', '5', '20', '200', '1e5']])

print()
print('L2: min over eta>1 of lnG(K,eta), K = 3..60')
bad = []
for K in range(3, 61):
    x, v = minimize(lambda e: lnG(K, e), mp.mpf('1.0000000001'), mp.mpf(10 * K + 50))
    if v < 0:
        bad.append((K, x, v))
    if K <= 8 or K % 10 == 0:
        print('   K=%2d  argmin eta=%s  min lnG=%s' % (K, mp.nstr(x, 8), mp.nstr(v, 8)))
print('   failures:', bad)

print()
print('L3: min over eta>1 of L3(K,eta), K = 3..40')
bad3 = []
for K in range(3, 41):
    x, v = minimize(lambda e: L3(K, e), mp.mpf('1.0000000001'), mp.mpf(10 * K + 50))
    if v < 0:
        bad3.append((K, x, v))
    if K <= 8 or K % 10 == 0:
        print('   K=%2d  argmin eta=%s  min L3=%s' % (K, mp.nstr(x, 8), mp.nstr(v, 8)))
print('   failures:', bad3)

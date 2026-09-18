"""Analytic sub-lemmas behind  W_K - rho_K < 1/(K(e^{K-1}-K-1)).

A1  phi(z) = -ln(1-z) - 2z/(2-z) has phi(0)=0 and phi'(z) = z^2/((1-z)(2-z)^2) > 0
    on (0,1).  Hence psi(eta) = eta ln(eta/(eta-1)) >= 1 + 1/(2 eta - 1)  for eta>1.
A2  L2:  ln(eta/K) + (K-1) (psi(eta)-1) >= 0  for K>=3, eta>1.
    K>=4 :  >= ln(eta/K) + (K-1)/(2 eta) >= 1 + ln((K-1)/(2K)) >= 1 + ln(3/8) > 0.
    K=3  :  >= min_eta [ ln(eta/3) + 2/(2 eta - 1) ] = ln((2+sqrt3)/6) + sqrt3 - 1 > 0.
A3  L3:  eta*(h^{K-1} - K - 1) >= K*(e^{K-1} - K - 1),  h = nu^eta,
    by cases eta>=K and eta<K.
A4  e^{K-1} > K+1 for K>=3.
"""
import sympy as sp
import mpmath as mp

mp.mp.dps = 40
z, eta, K = sp.symbols('z eta K', positive=True)

phi = -sp.log(1 - z) - 2 * z / (2 - z)
dphi = sp.simplify(sp.diff(phi, z))
print('A1 phi(0) =', sp.simplify(phi.subs(z, 0)))
print('A1 phi\'(z) =', sp.simplify(sp.factor(dphi)),
      ' == z^2/((1-z)(2-z)^2) ?',
      sp.simplify(dphi - z**2 / ((1 - z) * (2 - z)**2)) == 0)

psi = lambda e: e * mp.log(e / (e - 1))
print('A1 numeric check psi(eta) - 1 - 1/(2 eta -1) >= 0 :',
      all(psi(mp.mpf(v)) - 1 - 1 / (2 * mp.mpf(v) - 1) > 0
          for v in ['1.000001', '1.01', '1.2', '1.5', '2', '3', '10', '100', '1e5', '1e9']))

print('A2 1 + ln(3/8) =', mp.nstr(1 + mp.log(mp.mpf(3) / 8), 10), '> 0')
val3 = mp.log((2 + mp.sqrt(3)) / 6) + mp.sqrt(3) - 1
print('A2 K=3 exact min of ln(eta/3)+2/(2eta-1) =', mp.nstr(val3, 10), '> 0')
# direct numeric min for K=3 of the true expression
f3 = lambda e: mp.log(e / 3) + 2 * (psi(e) - 1)
print('A2 K=3 true expression at eta = 1+sqrt3/2 :', mp.nstr(f3(1 + mp.sqrt(3) / 2), 10))

print('A3 spot values of eta*(h^{K-1}-K-1) - K*(e^{K-1}-K-1):')
for Kv in (3, 4, 5, 8, 12, 20):
    worst = None
    for i in range(1, 4001):
        e = mp.mpf(1) + mp.mpf(i) / 100
        h = mp.e**psi(e)
        v = e * (h**(Kv - 1) - Kv - 1) - Kv * (mp.e**(Kv - 1) - Kv - 1)
        if worst is None or v < worst[1]:
            worst = (e, v)
    print('   K=%2d  min over eta in (1,41] : %s at eta=%s'
          % (Kv, mp.nstr(worst[1], 8), mp.nstr(worst[0], 6)))

print('A4 e^{K-1}-(K+1) for K=3..8 :',
      [mp.nstr(mp.e**(k - 1) - k - 1, 6) for k in range(3, 9)])

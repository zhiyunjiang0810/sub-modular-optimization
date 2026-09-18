"""Symbolic check of the selection lemma (why Psi's first nonpositive point is admissible).

zeta(t) = (t - eta(K-1)) / Theta(t),  Theta(t) = eta nu^t - t - eta,  nu = eta/(eta-1).
Claim S9:  zeta(m) <= zeta(m-1)   <=>   nu^m (K eta - m) <= K eta.
(Theta(m), Theta(m-1) > 0, so cross-multiplication is sign-safe.)
Together with  m d <= 1  <=>  nu^m (K eta - m) >= K eta  (script check_symbolic.py, S5)
this makes (B) automatic for the minimal m.
"""
import sympy as sp

K, eta, m = sp.symbols('K eta m', positive=True)
nu = eta / (eta - 1)
Theta = lambda t: eta * nu**t - t - eta
s = m - eta * (K - 1)

# zeta(m) <= zeta(m-1)  <=>  s*Theta(m-1) - (s-1)*Theta(m) <= 0
lhs = sp.simplify(s * Theta(m - 1) - (s - 1) * Theta(m))
print('S9 raw   :', sp.simplify(sp.expand(lhs)))

# claim: lhs  ==  nu^m (K eta - m) - K eta   (exactly)
claim = nu**m * (K * eta - m) - K * eta
print('S9 residual (lhs - claim):', sp.simplify(sp.expand(lhs - claim)))

# psi(eta) = eta ln(nu) > 1  :  -ln(1-z) > z on (0,1) with z = 1/eta
z = sp.symbols('z', positive=True)
print('S9 psi>1 via -ln(1-z)-z series at 0:',
      sp.series(-sp.log(1 - z) - z, z, 0, 4))

# Theta(t) > 0 for t>0 :  Theta(0)=0 and Theta'(t) = psi*nu^t - 1 >= psi-1 > 0
t = sp.symbols('t', nonnegative=True)
print('S9 Theta(0) =', sp.simplify(Theta(0)))
print('S9 Theta\'(t) =', sp.simplify(sp.diff(Theta(t), t)), ' = eta*ln(nu)*nu^t - 1')

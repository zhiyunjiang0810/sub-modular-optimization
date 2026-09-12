"""M3.4 (TASKS8): symbolic checks for the eta = 1 and K = 1 additions to
cor:greedybudget (ledger T10b).

  1. At theta = 1, tau = 1 the hardness family degenerates to F == G:
     a^tau (K-y)/(K-tau) == 1 - y/K with a = 1 - 1/K, so the constructed
     pair has error exactly 1 and the counting argument applies verbatim.
  2. U_K(1) == L_K(1) == V_{K-1}(1): the sandwich collapses at eta = 1.
  3. K = 1 arithmetic: U_1(eta) == 1 (vacuous) and V_0 = 1/eta; the
     three-line greedy chain for K = 1 is a hand argument (ledger tag).

Run: python3 results/M3_checks.py   (exit 0 iff all pass)
"""
import sys

import sympy as sp

fails = []


def check(name, ok, detail=""):
    print(("PASS" if ok else "FAIL"), name, detail)
    if not ok:
        fails.append(name)


K, y, eta = sp.symbols("K y eta", positive=True)

# 1. family degeneracy at theta = 1, tau = 1
a = 1 - 1 / K
check("theta=1, tau=1: a*(K-y)/(K-1) == 1 - y/K  (so F == G, error exactly 1)",
      sp.simplify(a * (K - y) / (K - 1) - (1 - y / K)) == 0)

# 2. U_K(1) == L_K(1) == V_{K-1}(1)
U1 = 1 - (1 - 1 / ((K - 1) * 1 + 1)) ** K
L1 = 1 - (1 - 1 / K) ** K
check("U_K(1) == L_K(1) == 1 - (1-1/K)^K", sp.simplify(U1 - L1) == 0)
k1 = (K - 1) * 1 + 1
q = (K - 1) * 1 / k1
VK1 = 1 - q ** (K - 1) * (1 - 1 / K)
# q = (K-1)/K at eta=1, so V_{K-1}(1) = 1 - ((K-1)/K)^{K-1} * (K-1)/K.
check("V_{K-1}(1) == L_K(1)",
      sp.simplify(VK1 - L1) == 0)

# 3. K = 1 arithmetic
check("U_1(eta) == 1 (vacuous at K=1)",
      sp.simplify((1 - (1 - 1 / (eta * 0 + 1)) ** 1) - 1) == 0)
check("V_0(eta) == 1/eta (the K=1 greedy value)",
      sp.simplify((1 - (1 - 1 / eta)) - 1 / eta) == 0)

print()
print("ALL PASS" if not fails else f"FAILURES: {fails}")
sys.exit(0 if not fails else 1)

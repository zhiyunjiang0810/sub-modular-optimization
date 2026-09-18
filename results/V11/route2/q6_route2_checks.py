"""ROUTE-TWO (Q6, thm:linear-exact) 独立验证脚本 / part 1: rho_K 曲线的精确有理数检查.

只依赖 results/V11/inputs/ 里的定义:
  k1 = (K-1)*eta + 1,  q = (K-1)*eta/k1,  V_j = 1 - q^j (1 - (K-j)/(K eta)),
  rho_K = min_j V_j,   L_K(x) = 1-(1-1/(xK))^K,   U_K(eta) = 1-(1-1/(eta(K-1)+1))^K.

全部用 fractions.Fraction 精确算术; float 只出现在打印里.
"""
from fractions import Fraction as F
import sympy as sp


def Vj(K, eta, j):
    eta = F(eta)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q**j * (1 - F(K - j, 1) / (K * eta))


def rho(K, eta):
    vals = [(Vj(K, eta, j), j) for j in range(0, K + 1)]
    m = min(vals)
    return m[0], m[1], [v for v, _ in vals]


def L(K, x):
    x = F(x)
    return 1 - (1 - 1 / (x * K)) ** K


def U(K, eta):
    eta = F(eta)
    return 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K


def main():
    print("== identities (sympy) ==")
    Ks, etas, js = sp.symbols("K eta j", positive=True)
    k1 = (Ks - 1) * etas + 1
    q = (Ks - 1) * etas / k1
    V = lambda jj: 1 - q**jj * (1 - (Ks - jj) / (Ks * etas))
    print("V_0 - 1/eta   =", sp.simplify(V(0) - 1 / etas))
    print("V_K - U_K     =", sp.simplify(V(Ks) - (1 - (1 - 1 / (etas * (Ks - 1) + 1)) ** Ks)))

    print("\n== rational table: L_K <= rho_K <= U_K, argmin j ==")
    print(f"{'K':>2} {'eta':>7} {'L_K':>12} {'rho_K':>12} {'U_K':>12} {'j*':>3}  ok")
    for K in range(2, 7):
        for eta in [F(1), F(6, 5), F(3, 2), F(2), F(3), F(5)]:
            r, jstar, vals = rho(K, eta)
            lk, uk = L(K, eta), U(K, eta)
            ok = (lk <= r <= uk)
            print(f"{K:>2} {str(eta):>7} {float(lk):>12.6f} {float(r):>12.6f} "
                  f"{float(uk):>12.6f} {jstar:>3}  {ok}")
            assert ok, (K, eta, lk, r, uk)

    print("\n== K=3, eta=3/2 walk-through ==")
    K, eta = 3, F(3, 2)
    k1 = (K - 1) * eta + 1
    qq = (K - 1) * eta / k1
    print("k1 =", k1, " q =", qq)
    for j in range(K + 1):
        print(f"  V_{j} = {Vj(K, eta, j)} = {float(Vj(K,eta,j)):.6f}")
    r, jstar, _ = rho(K, eta)
    print("  rho_3(3/2) =", r, "at j* =", jstar)
    print("  L_3(3/2)   =", L(3, eta), "=", float(L(3, eta)))
    print("  U_3(3/2)   =", U(3, eta), "=", float(U(3, eta)))
    n0 = 4 * K**5
    eps = lambda n: F(K**2, n) + F(K**5, 2 * n)
    print("  n >= 4K^5 =", n0, " eps_{n0} =", eps(n0), "=", float(eps(n0)))

    print("\n== K=2 (ProbeLottery item) ==")
    K, eta = 2, F(3, 2)
    for j in range(K + 1):
        print(f"  V_{j} = {Vj(K, eta, j)} = {float(Vj(K,eta,j)):.6f}")
    r, jstar, _ = rho(2, eta)
    print("  rho_2(3/2) =", r, "at j* =", jstar, " L_2 =", L(2, eta), " U_2 =", U(2, eta))
    print("  rho_2(1)   =", rho(2, F(1))[0], " L_2(1) =", L(2, F(1)))
    n0 = 4 * K**5
    eps = lambda n: F(K**2, n) + F(K**5, 2 * n)
    print("  n >= 4K^5 =", n0, " eps_{n0} =", eps(n0), "=", float(eps(n0)))


if __name__ == "__main__":
    main()

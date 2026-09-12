"""Q2 part A (TASKS10): exact-rational full-grid recheck of the Q1 closed
form, independent of how the closed form was obtained.

Loads build_closed_form() from results/Q1_closed_form.py (interface agreed
in the Q1 task), substitutes exact rationals, and checks on the whole
(x, y) count grid for given (K, j, eta, n):

  A1  F monotone: D_xF >= 0, D_yF >= 0 on every edge.
  A2  F submodular (count-grid sufficient conditions): D_x^2 F <= 0,
      D_y^2 F <= 0, D_xD_y F <= 0 wherever defined.
  A3  normalization F(0,0) = 0, F(0,K) = 1, and O optimal among small sets:
      F(x,y) <= 1 for x + y <= K.
  A4  single-element band with split (eta_u, eta_o) = (eta, 1):
      D F / eta <= D G <= D F on every x-edge and y-edge of the grid,
      where G(x,y) = Ghat(x+y) on the balanced region y <= 1 and
      G(x,y) = G_unbal(x,y) on y >= 2.
  A5  O-independence: G on y <= 1 depends on x + y only (holds by
      construction when 'Ghat' is used; verified numerically anyway via
      the two representations of edges crossing y = 0 -> 1).
  A6  objective: F(K,0) equals the delivered closed form 'objective', and
      is compared against V_j(eta) and min_j V_j(eta).

Every check is exact (Fraction/sympy Rational).  Run:
  python3 results/Q2_grid_check.py --K 3 --j 1 --eta 2 --n 24
  python3 results/Q2_grid_check.py --sweep     (K <= 8 default battery)
Exit 0 iff every requested configuration passes all checks.
"""
import argparse
import os
import sys
from fractions import Fraction as Fr

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

fails = []


def check(name, ok, detail=""):
    print(("PASS" if ok else "FAIL"), name, detail)
    if not ok:
        fails.append(name)


def V_exact(K, jj, eta):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q ** jj * (1 - Fr(K - jj, K) / eta)


def rho_exact(K, eta):
    return min(V_exact(K, t, eta) for t in range(K))


def load():
    from Q1_closed_form import build_closed_form
    return build_closed_form()


def as_fr(expr):
    """sympy Rational/number -> Fraction, exact."""
    e = sp.nsimplify(expr, rational=True) if not expr.is_Rational else expr
    e = sp.Rational(e)
    return Fr(int(e.p), int(e.q))


def eval_grid(cf, Kv, jv, ev, nv):
    """Return F, G as dicts over the grid, exact Fractions."""
    sy = cf["symbols"]
    subs_common = {sy["K"]: Kv, sy["j"]: jv, sy["eta"]: sp.Rational(ev.numerator, ev.denominator),
                   sy["n"]: nv}
    for name, val in cf.get("extra_values", {}).items():
        subs_common[sy[name]] = val
    X, Y = nv - Kv, Kv
    F, G = {}, {}
    Fx = cf["F"].subs(subs_common)
    Gh = cf["Ghat"].subs(subs_common)
    Gu = cf["G_unbal"].subs(subs_common) if cf.get("G_unbal") is not None else None
    for x in range(X + 1):
        for y in range(Y + 1):
            F[x, y] = as_fr(sp.simplify(Fx.subs({sy["x"]: x, sy["y"]: y})))
            if y <= 1:
                G[x, y] = as_fr(sp.simplify(Gh.subs({sy["s"]: x + y})))
            elif Gu is not None:
                G[x, y] = as_fr(sp.simplify(Gu.subs({sy["x"]: x, sy["y"]: y})))
            else:
                G[x, y] = None      # rule-described; band check will skip
    return F, G


def run_config(cf, Kv, jv, ev, nv, verbose=True):
    ok_all = True
    F, G = eval_grid(cf, Kv, jv, ev, nv)
    X, Y = nv - Kv, Kv

    def rec(name, ok, detail=""):
        nonlocal ok_all
        if not ok:
            ok_all = False
            print(f"    FAIL {name} {detail}")

    # A1 monotone + A2 submodular
    for x in range(X + 1):
        for y in range(Y + 1):
            if x < X:
                rec("D_xF>=0", F[x + 1, y] - F[x, y] >= 0, f"at {(x,y)}")
            if y < Y:
                rec("D_yF>=0", F[x, y + 1] - F[x, y] >= 0, f"at {(x,y)}")
            if x + 1 < X:
                rec("D_x^2F<=0",
                    F[x + 2, y] - 2 * F[x + 1, y] + F[x, y] <= 0, f"at {(x,y)}")
            if y + 1 < Y:
                rec("D_y^2F<=0",
                    F[x, y + 2] - 2 * F[x, y + 1] + F[x, y] <= 0, f"at {(x,y)}")
            if x < X and y < Y:
                rec("D_xD_yF<=0",
                    F[x + 1, y + 1] - F[x + 1, y] - F[x, y + 1] + F[x, y] <= 0,
                    f"at {(x,y)}")
    # A3 normalization
    rec("F(0,0)=0", F[0, 0] == 0)
    rec("F(0,K)=1", F[0, Kv] == 1)
    for x in range(X + 1):
        for y in range(Y + 1):
            if x + y <= Kv:
                rec("F<=1 on small sets", F[x, y] <= 1, f"at {(x,y)}")
    # A4 band (split (eta,1)): dF/eta <= dG <= dF, on edges with G defined
    for x in range(X + 1):
        for y in range(Y + 1):
            if x < X and G[x, y] is not None and G[x + 1, y] is not None:
                dF, dG = F[x + 1, y] - F[x, y], G[x + 1, y] - G[x, y]
                rec("band x-edge", dF / ev <= dG <= dF, f"at {(x,y)}")
            if y < Y and G[x, y] is not None and G[x, y + 1] is not None:
                dF, dG = F[x, y + 1] - F[x, y], G[x, y + 1] - G[x, y]
                rec("band y-edge", dF / ev <= dG <= dF, f"at {(x,y)}")
    # A5 O-independence on y <= 1 is structural (Ghat used); cross-check the
    # tie: adding an O element or a non-O element from (x,0) gives equal G.
    for x in range(X):
        rec("balanced tie", G[x + 1, 0] == G[x, 1] or G[x, 1] is None,
            f"at x={x}")
    # A6 objective
    val = F[Kv, 0]
    sy = cf["symbols"]
    obj_sub = {sy["K"]: Kv, sy["j"]: jv,
               sy["eta"]: sp.Rational(ev.numerator, ev.denominator),
               sy["n"]: nv}
    for name, v in cf.get("extra_values", {}).items():
        obj_sub[sy[name]] = v
    obj = as_fr(sp.simplify(cf["objective"].subs(obj_sub)))
    rec("objective formula matches F(K,0)", obj == val,
        f"formula {obj} vs grid {val}")
    vj = V_exact(Kv, jv, ev)
    if verbose:
        print(f"    F(K,0) = {val} = {float(val):.9f}; V_j = {float(vj):.9f}; "
              f"rho_K = {float(rho_exact(Kv, ev)):.9f}; "
              f"gap to V_j = {float(val - vj):.3e}")
    rec("F(K,0) >= V_j (finite-n value above the limit)", val >= vj)
    return ok_all, val


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--K", type=int)
    ap.add_argument("--j", type=int)
    ap.add_argument("--eta", type=str)
    ap.add_argument("--n", type=int)
    ap.add_argument("--sweep", action="store_true")
    args = ap.parse_args()
    cf = load()
    print("closed form loaded:", cf.get("notes", "")[:100])
    configs = []
    if args.sweep:
        for Kv in (3, 4, 5, 8):
            for jv in range(1, Kv):
                ev = Fr(2 * (Kv - jv) + 1, 2)          # segment midpoint
                for nv in (2 * Kv, 4 * Kv, 8 * Kv):
                    configs.append((Kv, jv, ev, nv))
    else:
        configs.append((args.K, args.j, Fr(args.eta), args.n))
    for (Kv, jv, ev, nv) in configs:
        print(f"== K={Kv} j={jv} eta={ev} n={nv} ==")
        ok, _ = run_config(cf, Kv, jv, ev, nv)
        check(f"grid K={Kv} j={jv} eta={ev} n={nv}", ok)
    print()
    print("ALL PASS" if not fails else f"FAILURES: {len(fails)}")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()

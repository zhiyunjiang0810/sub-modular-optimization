"""N5 (addendum): re-run the T2 fixed-F LP oracle AT the etahat used by the
theorem, and test the CORRECTED closed form for the error inflation.

Background.  results/T2_summary.md Conclusion 1 reports the closed form

    1 + delta_naive(theta) = ( a^tau * K/(K - tau) )^2 ,     a = 1 - 1/(theta K)

verified at design parameters theta in {3/2, 2, 3}.  Lemma N5.4 of
results/N5_bounded_query_hardness.tex derives by hand that the balanced-region
("constant-constant") band constraints actually force

    1 + delta(theta) = max{ a^tau * K/(K - tau) ,  a^(1 - tau) }^2         (*)

-- the second term comes from the y-direction edges at y = tau - 1 and is
dropped by the T2 formula.  To first order in 1/K the first term dominates iff
theta >= 2 - 1/tau ([VERIFIED-SYMBOLIC], results/N5_asymptotics.py check iii),
and every T2 test point satisfies that, which is why T2 never saw the second
term.  Theorem N5.6 evaluates the family at etahat = eta/(1 + delta(eta)),
which is strictly smaller than eta and can fall below 2 - 1/tau.

Checks, per (K, eta, tau) with n = 4K and the y <= tau balanced definition:
  A.  LP minimum delta at design parameter etahat  ==  (*) evaluated at etahat
  A'. report whether the T2 formula differs there (i.e. whether this point
      refutes the naive closed form)
  B.  admissibility: etahat * (1 + delta(etahat)) <= eta, so the family lies
      inside the promised error class
  E.  delta(etahat) <= delta(eta): the monotonicity the EXPLICIT definition
      etahat = eta/(1 + delta(eta)) needs (delta is NOT monotone in theta once
      the max in (*) switches branches, so this has to be checked, not assumed)
  C.  OPT = F(O):  max_{0 < x+y <= K} F(x,y) = F(0,K)                (fact F3)
  D.  F(K,0)/F(0,K) = 1 - (1 - 1/(etahat K))^K = L_K(etahat)         (fact F4)

Points where hypothesis (H) of the theorem fails (etahat < 1) are SKIPped: the
theorem claims nothing there.

Run:  python3 results/N5_delta_at_etahat.py
Exit code 0 iff every non-skipped point passes A, B, C, D, E.
Depends on: results/T2_hardness_grid.py (imported, unmodified).
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from T2_hardness_grid import fixedF_min_delta          # noqa: E402


def band_terms(theta, K, tau):
    """the two constant-constant band ratios of Lemma N5.4."""
    a = 1 - 1 / (theta * K)
    return a ** tau * K / (K - tau), a ** (1 - tau)


def delta_corrected(theta, K, tau):
    c1, c2 = band_terms(theta, K, tau)
    return max(c1, c2) ** 2 - 1


def delta_naive(theta, K, tau):
    return band_terms(theta, K, tau)[0] ** 2 - 1


def grid_F(theta, K, X):
    """F(x,y) = theta^{-1/2} (1 - a^x (1 - y/K)) on the (x,y) grid."""
    a = 1 - 1 / (theta * K)
    return {(x, y): (theta ** -0.5) * (1 - a ** x * (1 - y / K))
            for x in range(X + 1) for y in range(K + 1)}


n_pass = n_fail = n_skip = n_refute = 0
print("=" * 108)
print("N5 addendum: LP re-verification of the inflation closed form at the theorem's etahat")
print("balanced definition 'ysmall' (y <= tau), n = 4K, split eta_u = eta_o = sqrt(theta)")
print("=" * 108)
print(f"{'K':>3} {'n':>5} {'eta':>5} {'tau':>3} {'delta(eta)':>11} {'etahat':>8} "
      f"{'LP min delta':>13} {'corrected':>12} {'T2 naive':>11} {'err':>8} {'verdict':>10}")

for K in (4, 6, 8, 12, 16, 24, 32):
    for eta in (1.5, 2.0, 3.0):
        for tau in (1, 2):
            n = 4 * K
            d_eta = delta_corrected(eta, K, tau)
            etahat = eta / (1 + d_eta)
            if etahat < 1.0:                       # hypothesis (H) fails
                n_skip += 1
                print(f"{K:3d} {n:5d} {eta:5.2f} {tau:3d} {d_eta:11.6f} {etahat:8.5f} "
                      f"{'-':>13} {'-':>12} {'-':>11} {'-':>8} {'SKIP(H)':>10}")
                continue
            t0 = time.time()
            r = fixedF_min_delta(n, K, etahat, tau, 'ysmall')
            cf = delta_corrected(etahat, K, tau)
            nv = delta_naive(etahat, K, tau)
            lp = r['min_delta']
            okA = (lp is not None) and abs(lp - cf) <= 1e-6 * max(1.0, abs(cf))
            refutes = abs(nv - cf) > 1e-9
            n_refute += refutes
            err = etahat * (1 + cf)
            okB = err <= eta + 1e-12
            okE = cf <= d_eta + 1e-12
            X = n - K
            F = grid_F(etahat, K, X)
            okC = max((v, k) for k, v in F.items() if 0 < sum(k) <= K)[1] == (0, K)
            a = 1 - 1 / (etahat * K)
            okD = abs(F[(K, 0)] / F[(0, K)] - (1 - a ** K)) < 1e-12
            ok = okA and okB and okC and okD and okE
            n_pass += ok
            n_fail += (not ok)
            print(f"{K:3d} {n:5d} {eta:5.2f} {tau:3d} {d_eta:11.6f} {etahat:8.5f} "
                  f"{(lp if lp is None else round(lp, 9)):>13} {cf:12.9f} {nv:11.8f} "
                  f"{err:8.5f} {('PASS' if ok else 'FAIL'):>10}"
                  + ("  <- T2 formula WRONG here" if refutes else "")
                  + ("" if ok else f"  [A={okA} B={okB} C={okC} D={okD} E={okE}]")
                  + f"  ({time.time()-t0:.1f}s)")

print("=" * 108)
print(f"{n_pass} PASS / {n_fail} FAIL / {n_skip} SKIP (hypothesis (H): etahat < 1)")
print(f"{n_refute} of the {n_pass + n_fail} solved points refute the T2 closed form")
print("(there the LP agrees with the corrected max-form (*), not with T2's single term).")
print("Status conferred: [VERIFIED-LP] for (*) and for facts F3/F4 at these points;")
print("general (K, tau, theta) remains [CONJECTURE].")
print("=" * 108)
sys.exit(0 if n_fail == 0 else 1)

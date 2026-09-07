"""K1: the U_K family under the STEPWISE selection error (decision D3).

Confirms the user-requested check for the J2 adoption: after replacing
Definition 2 by the stepwise a_t definition (harmful zero step -> infinity,
benign zero step -> 1), the adversarial-tie run on the explicit U_K family
still has eta^sel = eta^tr = ahat, because NO step of that run has chosen
true gain <= 0 (so the stepwise definition reduces to the old ratio form).

Method: same frozen machinery as results/F2_etasel_tight.py (CELF greedy on
the cached lattice arrays of code/check_explicit_instance.py, quantize=10,
adversarial tie direction), but the rulers are recomputed HERE from first
principles per step: g_t, M_t, a_t, and the trajectory bands.

Run: python3 results/K1_etasel_newdef_check.py   (~1 min; exit 0 iff PASS)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'code'))

import check_explicit_instance as uk     # noqa: E402  (frozen U_K builder)
from im_graph import CachedSetFunction, lazy_greedy  # noqa: E402

TOL = 1e-9
fails = []
print('K1: stepwise eta^sel on U_K, K=2..8, ahat in {1.5, 2}')
print(f"{'K':>3} {'ahat':>5} {'min g_t':>12} {'n_zero':>7} {'eta_sel_new':>14} "
      f"{'eta_tr':>14} {'ratio':>12} {'L_K':>12} {'ok':>4}")
for ahat in (1.5, 2.0):
    for K in range(2, 9):
        a, n, N, f_arr, g_arr = uk.build(K, ahat)
        mask = lambda S: sum(1 << e for e in S)
        F = CachedSetFunction(lambda S: float(f_arr[mask(S)]))
        G = CachedSetFunction(lambda S: float(g_arr[mask(S)]))
        ground = list(range(n))
        steps = []

        def record(t, Sbefore, chosen, gain_tilde_q):
            S = set(Sbefore)
            g_t = F.gain(Sbefore, chosen)
            cand = [e for e in ground if e not in S]
            M_t = max(F.gain(Sbefore, e) for e in cand)
            # trajectory band at this state, raw predicted gains
            band = [(F.gain(Sbefore, e), G.gain(Sbefore, e)) for e in cand]
            steps.append((g_t, M_t, band))

        lazy_greedy(G, ground, K, record=record, quantize=10)
        n_zero = sum(1 for g_t, _, _ in steps if g_t <= TOL)
        min_g = min(g_t for g_t, _, _ in steps)
        # stepwise a_t
        ats = []
        for g_t, M_t, _ in steps:
            if g_t > TOL:
                ats.append(M_t / g_t)
            elif M_t <= TOL:
                ats.append(1.0)
            else:
                ats.append(float('inf'))
        eta_sel = max([1.0] + ats)
        # trajectory error from the recorded bands
        eu = eo = 1.0
        for _, _, band in steps:
            for d, dt in band:
                if d > TOL and dt > TOL:
                    eo = max(eo, dt / d)
                    eu = max(eu, d / dt)
        eta_tr = eu * eo
        Sfin = set()
        # rerun to get output value
        out = lazy_greedy(G, ground, K, quantize=10)
        ratio = F.value(set(out)) if hasattr(F, 'value') else None
        try:
            ratio = float(f_arr[mask(set(out))])
        except Exception:
            pass
        LK = 1 - (1 - 1 / (ahat * K)) ** K
        ok = (n_zero == 0 and abs(eta_sel - ahat) < 1e-8
              and abs(eta_tr - ahat) < 1e-7 and abs(ratio - LK) < 1e-9)
        print(f'{K:>3} {ahat:>5} {min_g:>12.3e} {n_zero:>7} {eta_sel:>14.9f} '
              f'{eta_tr:>14.9f} {ratio:>12.9f} {LK:>12.9f} '
              f"{'ok' if ok else 'FAIL':>4}")
        if not ok:
            fails.append((K, ahat))
print()
print('ALL PASS: stepwise eta^sel = eta^tr = ahat, no zero steps, ratio = L_K'
      if not fails else f'FAILURES: {fails}')
sys.exit(0 if not fails else 1)

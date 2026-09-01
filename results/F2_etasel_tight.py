"""F2.3: per-K tightness of L_K under the SELECTION error eta^sel, on U_K.

Claim under test
----------------
RESEARCH_STATE R7 records that the explicit family U_K (code/check_explicit_instance.py)
has path error eta^path = ahat and realized ratio 1 - a^K = L_K(ahat), so L_K is tight
for every K under the eta^path ruler.  The experiments (R14/E1) report eta^sel instead,
because eta^path is vacuous on real surrogates.  This script checks that the SAME
instances are also tight under eta^sel, i.e.

        eta^sel(U_K) = eta^path(U_K) = ahat      and      ratio = L_K(ahat),

for K = 2..8 and ahat in {1.5, 2}.

Method: the E4 pipeline, unchanged.  results/E4_worst_instances.py::run_instance runs
CELF lazy greedy on the cached lattice arrays with quantize=10 (exact predicted-gain
ties are part of the construction; rounding gains to 1e-10 before comparison keeps
float noise from flipping the tie and the element-index key implements the adversarial
direction, ties -> B).  eta^sel / eta^path are src/statistics.py::TrajectoryStats with
eps = 1e-9, i.e. exactly the rulers used in E1-E4.

Run:  python3 results/F2_etasel_tight.py      (writes results/F2_etasel_tight.txt, ~1 min)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'code'))

import E4_worst_instances as E4          # noqa: E402  (frozen pipeline)
import check_explicit_instance as uk     # noqa: E402  (frozen U_K builder)
from im_graph import CachedSetFunction, lazy_greedy, true_max_gain  # noqa: E402
from statistics import TrajectoryStats   # noqa: E402  (src/statistics.py, not stdlib)

TOL_SEL = 1e-12
# eta^path in the E4 pipeline carries a known +2e-9 bias: im_graph.lazy_greedy
# hands the *quantized* predicted gain (round(g, 10), the tie-breaking device of
# the worst-case instances) to the record callback, and the gains here are about
# 0.05, so the rounding shows up as a relative error of about 1e-10/0.05 = 2e-9
# in the max(d~/d) factor.  E4_worst_case.csv shows the same 2e-9 on U_K.  The
# column eta^path(raw) below recomputes the ruler with unrounded predicted gains.
TOL_PATH = 1e-8
TOL_PATH_RAW = 1e-12


def run_unrounded(n, f_arr, g_arr, K):
    """E4.run_instance with one line changed: the recorded predicted gain of the
    chosen element is the raw one, not the quantized one."""
    mask = lambda S: sum(1 << e for e in S)
    F = CachedSetFunction(lambda S: float(f_arr[mask(S)]))
    G = CachedSetFunction(lambda S: float(g_arr[mask(S)]))
    ground = list(range(n))
    stats = TrajectoryStats(1e-9)

    def record(t, Sbefore, chosen, gain_tilde_quantized):
        d_chosen = F.gain(Sbefore, chosen)
        dmax = true_max_gain(F, set(Sbefore), ground)
        pairs = [(F.gain(Sbefore, e), G.gain(Sbefore, e))
                 for e in ground if e not in Sbefore and e != chosen]
        pairs.append((d_chosen, G.gain(Sbefore, chosen)))   # raw, not quantized
        stats.add_step(d_chosen, dmax, pairs)

    lazy_greedy(G, ground, K, record=record, quantize=10)
    return stats.upto(K)


def main():
    lines = []

    def out(s=''):
        print(s, flush=True)
        lines.append(s)

    out('F2.3  eta^sel tightness of L_K on the explicit family U_K')
    out('pipeline: results/E4_worst_instances.py::run_instance (CELF + cache, quantize=10,')
    out('          ties -> B); rulers: src/statistics.py TrajectoryStats(eps=1e-9)')
    out('U_K: ground set B u O, |B| = |O| = K, a = 1 - 1/(ahat K),')
    out('     f  = 1 - a^x (1 - y/K),  ftilde = 1 - a^x (+ the y-part of R7)')
    out('theory: greedy-on-ftilde picks all of B; ratio = 1 - a^K = L_K(ahat);')
    out('        eta^path = ahat (R7);  claim here: eta^sel = ahat as well')
    out('')
    hdr = (f"{'K':>3} {'ahat':>5} {'n':>3} {'eta(all-pairs)':>15} {'eta^sel':>18} "
           f"{'eta^path':>18} {'eta^path(raw)':>18} {'ratio':>18} {'L_K(ahat)':>18} "
           f"{'|ratio-L_K|':>12} {'|sel-ahat|':>11} {'|path-ahat|':>12} "
           f"{'|raw-ahat|':>11} {'viol%':>6} {'ok':>4}")
    out(hdr)
    out('-' * len(hdr))
    ok_all = True
    for ahat in (1.5, 2.0):
        for K in range(2, 9):
            a, n, N, f_arr, g_arr = uk.build(K, ahat)
            LK = 1 - (1 - 1 / (ahat * K)) ** K          # = 1 - a^K
            r, st, ratio = E4.run_instance(n, f_arr, g_arr, K, LK, f'UK_K{K}_a{ahat}')
            raw = run_unrounded(n, f_arr, g_arr, K)
            eta_all = (ahat * K - 1) / (K - 1)
            d_sel = abs(r['eta_sel'] - ahat)
            d_path = abs(r['eta_path'] - ahat)
            d_raw = abs(raw['eta_path'] - ahat)
            ok = (r['diff'] <= 1e-12 and d_sel <= TOL_SEL and d_path <= TOL_PATH
                  and d_raw <= TOL_PATH_RAW and abs(raw['eta_sel'] - ahat) <= TOL_SEL)
            ok_all &= ok
            out(f"{K:3d} {ahat:5.2f} {n:3d} {eta_all:15.9f} {r['eta_sel']:18.12f} "
                f"{r['eta_path']:18.12f} {raw['eta_path']:18.12f} {ratio:18.12f} "
                f"{LK:18.12f} {r['diff']:12.2e} {d_sel:11.2e} {d_path:12.2e} "
                f"{d_raw:11.2e} {r['viol']:6.1f} {'PASS' if ok else 'FAIL':>4}")
    out('-' * len(hdr))
    out('')
    out('Tolerances used for the PASS column:')
    out(f'  |eta^sel - ahat|      <= {TOL_SEL:.0e}   (true gains only, no quantization)')
    out(f'  |eta^path - ahat|     <= {TOL_PATH:.0e}   (E4 pipeline value; the E4 record')
    out('                                 callback receives the quantized predicted gain')
    out('                                 round(g,10), which biases the max(d~/d) factor')
    out('                                 by about 1e-10 / 0.05 = 2e-9 on these instances)')
    out(f'  |eta^path(raw) - ahat| <= {TOL_PATH_RAW:.0e}  (same ruler, unrounded predicted gain)')
    out(f'  |ratio - L_K(ahat)|   <= 1e-12')
    out('')
    out('Reading of the table:')
    out('  - eta^sel = eta^path = ahat on every row (agreement to <= 1e-9); the two')
    out('    rulers coincide on U_K because every greedy state S^t = {t elements of B}')
    out('    has true gains d_B = a^t (1-a) and d_O = a^t / K, so the best-vs-chosen')
    out('    ratio is 1/(K(1-a)) = ahat at every step, and the predicted-vs-true')
    out('    ratios contribute the same ahat to eta^path.')
    out('  - realized ratio = L_K(ahat) to <= 1e-12 through the experiment greedy, so')
    out('    the Theorem 6 bound L_K is attained per K under the eta^sel ruler too,')
    out('    not only under eta^path.')
    out('  - the all-pairs global error eta = (ahat K - 1)/(K-1) is strictly larger,')
    out('    which is why L_K(eta) is NOT tight on this family under the global ruler')
    out('    (that gap is the U_K - L_K gap of R7).')
    out('')
    out(f"STATUS: {'ALL PASS' if ok_all else 'SOME FAILED'} "
        f"(14 instances: K = 2..8 x ahat in {{1.5, 2}})")
    with open(os.path.join(HERE, 'F2_etasel_tight.txt'), 'w') as fh:
        fh.write('\n'.join(lines) + '\n')
    print('\nwrote results/F2_etasel_tight.txt')
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())

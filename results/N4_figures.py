"""N4 step 1: tables + heatmaps of the relaxed-F hardness LP optimum.

Reads results/N4_solutions.json (canonical extreme point of the LP, true balanced
band, K in {4,6,8}, n = 8K, eta = 2, tau = 1) and writes

    figures/N4_F_heatmap.png     F(x,y) per K, balanced-band boundary overlaid
    figures/N4_G_heatmap.png     G(x,y) per K, same overlay
    figures/N4_value_vs_bounds.png   LP value (n -> infinity) vs L_K, V_j, U_K
    results/N4_grids.csv         the three (F,G) grids in long form

Run: python3 results/N4_figures.py
"""
import csv
import json
import math
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIGS = os.path.join(ROOT, 'figures')
sys.path.insert(0, HERE)


def band_edges(n, K, tau):
    """x range of the true balanced band |y - K(x+y)/n| <= tau, per y."""
    lo, hi = [], []
    for y in range(K + 1):
        # |y - K(x+y)/n| <= tau  <=>  n(y-tau)/K - y <= x <= n(y+tau)/K - y
        lo.append(n * (y - tau) / K - y)
        hi.append(n * (y + tau) / K - y)
    return np.array(lo), np.array(hi)


def heat(sol, key, fname, title, cmap='Blues'):
    keys = sorted(sol, key=lambda s: sol[s]['config']['K'])
    fig, axes = plt.subplots(len(keys), 1, figsize=(11, 2.35 * len(keys) + 1.1))
    if len(keys) == 1:
        axes = [axes]
    for ax, kk in zip(axes, keys):
        cfg = sol[kk]['config']
        K, n, tau = cfg['K'], cfg['n'], cfg['tau']
        M = np.array(sol[kk][key])            # shape (X+1, K+1)
        X = M.shape[0] - 1
        im = ax.imshow(M.T, origin='lower', aspect='auto', cmap=cmap,
                       extent=(-0.5, X + 0.5, -0.5, K + 0.5))
        bal = np.array(sol[kk]['balanced'], dtype=float)   # (X+1, K+1)
        ax.contour(np.arange(X + 1), np.arange(K + 1), bal.T, levels=[0.5],
                   colors='#c0392b', linewidths=1.7)
        lo, hi = band_edges(n, K, tau)
        for y in range(K + 1):
            a, b = max(lo[y], -0.5), min(hi[y], X + 0.5)
            if b >= a:
                ax.hlines(y, a, b, color='#c0392b', lw=2.4, alpha=0.55,
                          label=('balanced band  |y - K|S|/n| <= tau'
                                 if (kk == keys[0] and y == 0) else None))
        ax.set_xlim(-0.5, X + 0.5); ax.set_ylim(-0.5, K + 0.5)
        ax.set_yticks(range(K + 1))
        ax.set_ylabel('y = |S n O|')
        ax.set_title(f"K={K}, n={n}, eta={cfg['eta']}, tau={tau}: "
                     f"{title}   (ratio = F(K,0) = {sol[kk]['ratio']:.6f})",
                     fontsize=10)
        fig.colorbar(im, ax=ax, pad=0.012)
    axes[-1].set_xlabel('x = |S \\ O|')
    axes[0].legend(loc='lower right', fontsize=8, framealpha=0.9)
    fig.suptitle(title + '  -- relaxed-F poly-query hardness LP, canonical optimum',
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print('wrote', fname)


def value_figure(fname):
    """LP limit value vs the three reference curves, as a function of K."""
    import N4_check as C
    from fractions import Fraction as Fr
    etas = [Fr(3, 2), Fr(2), Fr(5, 2)]
    Ks = list(range(3, 13))
    fig, axes = plt.subplots(1, len(etas), figsize=(13, 3.9), sharey=False)
    for ax, eta in zip(axes, etas):
        e = float(eta)
        vv = [float(C.params(K, eta)['value']) for K in Ks]
        Vj = [float(C.params(K, eta)['Vj']) for K in Ks]
        UK = [1 - (1 - 1 / (e * (K - 1) + 1)) ** K for K in Ks]
        LK = [1 - (1 - 1 / (e * K)) ** K for K in Ks]
        ax.plot(Ks, UK, 'o--', color='#7f8c8d', ms=4, label='$U_K$ (R7 instance)')
        ax.plot(Ks, vv, 's-', color='#2c3e50', ms=4.5,
                label='relaxed-F LP limit (closed form)')
        ub = [K for K in Ks if e > K - 1]
        if ub:
            ax.plot(ub, [float(C.params(K, eta)['value']) for K in ub], 'x',
                    color='#e67e22', ms=9, mew=2,
                    label='closed form = upper bound only (eta > K-1)')
        ax.plot(Ks, Vj, '^-', color='#2980b9', ms=4,
                label=r'$V_j=\rho_K^{LP}$ (R10)')
        ax.plot(Ks, LK, 'v--', color='#c0392b', ms=4, label='$L_K$ (Thm 6)')
        ax.axhline(1 - math.exp(-1 / e), color='k', lw=0.8, ls=':',
                   label=r'$1-e^{-1/\eta}$')
        ax.set_title(f'eta = {float(eta)}', fontsize=10)
        ax.set_xlabel('K'); ax.grid(alpha=0.25)
    axes[0].set_ylabel('worst-case ratio')
    axes[0].legend(fontsize=7.5, loc='upper right')
    fig.suptitle('Poly-query hardness limit sits on top of the predictive-greedy '
                 'value $V_j$, strictly below $U_K$\n'
                 '(crossed points: eta > K-1, where the closed form is only a '
                 'feasible upper bound, not the LP optimum)', fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print('wrote', fname)


def dump_csv(sol, path):
    with open(path, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['K', 'n', 'eta', 'tau', 'x', 'y', 'balanced', 'F', 'G', 'Ghat_xy'])
        for kk in sorted(sol, key=lambda s: sol[s]['config']['K']):
            c = sol[kk]['config']
            F = np.array(sol[kk]['F']); G = np.array(sol[kk]['G'])
            B = np.array(sol[kk]['balanced']); Gh = sol[kk]['Ghat']
            for x in range(F.shape[0]):
                for y in range(F.shape[1]):
                    w.writerow([c['K'], c['n'], c['eta'], c['tau'], x, y,
                                int(B[x, y]), f'{F[x, y]:.12g}', f'{G[x, y]:.12g}',
                                f'{Gh[x + y]:.12g}'])
    print('wrote', path)


def main():
    with open(os.path.join(HERE, 'N4_solutions.json')) as fh:
        sol = json.load(fh)
    os.makedirs(FIGS, exist_ok=True)
    heat(sol, 'F', os.path.join(FIGS, 'N4_F_heatmap.png'), 'F(x,y)')
    heat(sol, 'G', os.path.join(FIGS, 'N4_G_heatmap.png'), 'G(x,y)')
    value_figure(os.path.join(FIGS, 'N4_value_vs_bounds.png'))
    dump_csv(sol, os.path.join(HERE, 'N4_grids.csv'))


if __name__ == '__main__':
    main()

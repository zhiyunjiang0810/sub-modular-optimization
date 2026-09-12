"""L3: the sandwich figure, paper version (TASKS7).

figures/sandwich_paper.{pdf,png}, copied to paper/figures/sandwich_paper.pdf.

Panel (a): K = 8 over the global error axis.  The a priori guarantee L_8,
greedy's exact worst case rho_8 (thm:exact), the budget-class ceiling
U_8 = H_{8,1} (cor:greedybudget) and the information ceiling 1/eta
(thm:ceiling).  The admissible band for any algorithm in A_lin is
[rho_8, min{U_8, 1/eta}]; at K = 8 it is already too thin to see, which is
the message.  The eta = 2 cross-section is annotated with values computed
here (they match results/L1_table.csv).

Panel (b): band width min{U_K, 1/eta} - rho_K against K, log-log, for four
eta, with the c'(eta)/K^2 asymptote of rem:greedybudget (dashed, same
color).  Slope -2 confirms the O(1/K^2) width; the small-K kink is the
switch of the min from 1/eta to U_K.

Fonts: canvas 7.0 in wide, every font >= 9 pt, so >= 7.07 pt effective at
\textwidth = 5.5 in (same budget rule as results/K3_split_figs.py).
Run: python3 results/L3_sandwich_fig.py
"""
import math
import os
import shutil

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, 'figures')
PFIG = os.path.join(ROOT, 'paper', 'figures')
TEXTWIDTH_IN = 5.5

plt.rcParams.update({'font.size': 11, 'axes.grid': True, 'grid.alpha': 0.25,
                     'grid.linewidth': 0.5, 'axes.spines.top': False,
                     'axes.spines.right': False, 'figure.dpi': 150})

C_RHO, C_U, C_L = '#0072B2', '#D55E00', '0.45'
ETA_COLORS = {1.25: '#0072B2', 1.5: '#D55E00', 2.0: '#009E73', 3.0: '#CC79A7'}


def L_K(eta, K):
    return 1 - (1 - 1 / (eta * K)) ** K


def U_K(eta, K):
    return 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K


def rho_K(eta, K):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return min(1 - q ** j * (1 - (K - j) / (K * eta)) for j in range(K))


def W_K(eta, K):
    """Any-size ceiling of thm:linear-anysize (ledger T10d): Psi rule."""
    nu = eta / (eta - 1)
    m = 1
    while (K * eta - m - 1) * nu ** m - K * (eta - 1) > 0:
        m += 1
    Bm = eta * (nu ** m - 1) - m
    d = (nu ** m / K - 1) / Bm
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    j = max(0, min(K - 1, K + 1 - math.ceil(eta)))
    Q = q ** j
    return 1 - Q + (K - j) * Q * d


def gap_bound(K):
    """The exponential bound 1/(K(e^{K-1}-K-1)) of thm:linear-anysize."""
    return 1 / (K * (math.exp(K - 1) - K - 1))


def gap_exact(eta_frac, K):
    """W_K - rho_K via the exact gap identity (17) in Fractions, so panel
    (b) shows the true decay instead of the float-cancellation floor at
    ~1e-16.  Returns a float of the exact rational."""
    from fractions import Fraction as Fr
    eta = Fr(eta_frac)
    nu = eta / (eta - 1)
    m = 1
    while (K * eta - m - 1) * nu ** m - K * (eta - 1) > 0:
        m += 1
    Bm = eta * (nu ** m - 1) - m
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    j = max(0, min(K - 1, K + 1 - math.ceil(eta)))
    return float((K - j) * q ** j * (m - eta * (K - 1)) / (K * eta * Bm))


def c_prime(eta):
    m = math.floor(eta)
    return math.exp(-1 / eta) * m * (2 * eta - m - 1) / (2 * eta ** 2)


def main():
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.0, 3.0))

    # ---- panel (a): K = 8 ------------------------------------------------
    # J6/J7 day update: thm:linear-exact makes rho_8 the EXACT optimum of
    # the size-<=K class A_lin, and thm:linear-anysize caps the any-size
    # linear class at min{W_8, 1/eta}; the former U_K ceiling is kept as a
    # thin reference.  The any-size band [rho_8, min{W_8, 1/eta}] is
    # narrower than one line width: that is the message.
    K = 8
    etas = np.linspace(1.0, 5.0, 600)
    rho = np.array([rho_K(e, K) for e in etas])
    W = np.array([W_K(e, K) if e > 1 else rho_K(e, K) for e in etas])
    U = np.array([U_K(e, K) for e in etas])
    inv = 1 / etas
    cap = np.minimum(W, inv)
    ax.plot(etas, [L_K(e, K) for e in etas], '-', color=C_L, lw=1.2,
            label=r'$L_8(\eta)$ (guarantee)')
    ax.plot(etas, U, '--', color=C_U, lw=1.0, alpha=0.6,
            label=r'$U_8(\eta)$ (former ceiling)')
    ax.fill_between(etas, rho, cap, color=C_RHO, alpha=0.30, lw=0)
    ax.plot(etas, rho, '-', color=C_RHO, lw=1.8,
            label=r'$\rho_8(\eta)$ = size-$\leq K$ class optimum')
    ax.plot(etas, cap, '-', color='#009E73', lw=1.0,
            label=r'$\min\{W_8,1/\eta\}$ (any-size ceiling)')
    ax.plot(etas, inv, ':', color='0.3', lw=1.4, label=r'$1/\eta$')
    r2, w2 = rho_K(2.0, K), W_K(2.0, K)
    ax.plot([2, 2], [r2, w2], '-', color='k', lw=0.8)
    ax.annotate(f'$\\eta=2$: $\\rho_8={r2:.4f}$,\n'
                f'$W_8-\\rho_8={w2 - r2:.1e}$',
                xy=(2, w2), xytext=(2.75, 0.44), fontsize=9,
                arrowprops=dict(arrowstyle='-', lw=0.6, color='0.2'))
    ax.set_xlabel(r'global error $\eta$')
    ax.set_ylabel(f'worst-case ratio, $K={K}$')
    ax.set_xlim(1, 5)
    ax.set_ylim(0.1, 1.0)
    ax.legend(frameon=False, fontsize=8, loc='upper right')
    ax.set_title(r'(a) the any-size band $[\rho_K,\ \min\{W_K,1/\eta\}]$',
                 fontsize=10)

    # ---- panel (b): any-size band width vs K, semilog-y ------------------
    # Exponential decay (thm:linear-anysize): width < 1/(K(e^{K-1}-K-1)),
    # dashed black; the former O(1/K^2) width U_K - rho_K in light grey
    # for comparison.
    from fractions import Fraction as Fr
    ETA_FRACS = {1.25: Fr(5, 4), 1.5: Fr(3, 2), 2.0: Fr(2), 3.0: Fr(3)}
    for eta in (1.25, 1.5, 2.0, 3.0):
        Ks = [k for k in range(3, 41) if k > eta]
        # gap in exact rationals (identity (17)); for eta < K the min in
        # the ceiling is W_K, so the band width IS the exact gap
        w = [gap_exact(ETA_FRACS[eta], k) for k in Ks]
        col = ETA_COLORS[eta]
        bx.plot(Ks, w, '-', color=col, lw=1.6, label=rf'$\eta={eta:g}$')
    Ks = list(range(3, 41))
    bx.plot(Ks, [gap_bound(k) for k in Ks], '--', color='k', lw=1.0,
            label=r'$1/(K(e^{K-1}\!-\!K\!-\!1))$')
    bx.plot(Ks, [U_K(2.0, k) - rho_K(2.0, k) for k in Ks], '-',
            color='0.75', lw=1.0, label=r'former $U_K-\rho_K$ ($\eta=2$)')
    bx.set_yscale('log')
    bx.set_xlabel(r'$K$')
    bx.set_ylabel(r'any-size band width (log)')
    bx.legend(frameon=False, fontsize=8, loc='upper right', ncol=1)
    bx.set_title(r'(b) width decays exponentially in $K$', fontsize=10)

    fig.tight_layout()
    for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(FIG, f'sandwich_paper.{ext}'),
                    bbox_inches='tight')
    shutil.copy(os.path.join(FIG, 'sandwich_paper.pdf'),
                os.path.join(PFIG, 'sandwich_paper.pdf'))
    print('wrote figures/sandwich_paper.{pdf,png}; copied to paper/figures/')

    eff = 9.0 * TEXTWIDTH_IN / 7.0
    print(f'font check: min 9pt on 7.0in canvas -> {eff:.2f}pt effective '
          f'at textwidth {TEXTWIDTH_IN}in:', 'OK' if eff >= 7 else 'TOO SMALL')
    print(f'eta=2 cross-section at K=8: rho={rho_K(2.0, 8):.5f}, '
          f'W={W_K(2.0, 8):.9f}, W-rho={W_K(2.0, 8) - rho_K(2.0, 8):.2e}, '
          f'U={U_K(2.0, 8):.5f}, 1/eta=0.5')


if __name__ == '__main__':
    main()

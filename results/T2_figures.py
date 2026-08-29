"""T2 figures. One-click: python3 results/T2_figures.py  (after the two grid sweeps).
Reads results/T2_grid_fixedF.csv and results/T2_grid_relaxF.csv.
Writes figures/T2_delta_vs_K.png and figures/T2_relaxF_ratio.png.
Palette: Okabe-Ito subset, CVD-validated (dataviz validator ALL PASS)."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator


def log_ticks(ax, ks):
    ax.set_xticks(ks)
    ax.set_xticklabels([str(k) for k in ks])
    ax.xaxis.set_minor_locator(NullLocator())

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(os.path.dirname(HERE), 'figures')
C = {1.5: '#0072B2', 2.0: '#D55E00', 3.0: '#009E73'}

plt.rcParams.update({'font.size': 10, 'axes.grid': True, 'grid.alpha': 0.25,
                     'grid.linewidth': 0.5, 'axes.spines.top': False,
                     'axes.spines.right': False, 'figure.dpi': 150})

# ---- Fig 1: min delta vs K (fixed F, ysmall) ------------------------------
df = pd.read_csv(os.path.join(HERE, 'T2_grid_fixedF.csv'))
d = df[(df.defn == 'ysmall') & (df.status == 'FEASIBLE')]
fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.4), sharey=True)
for ax, tau in zip(axes, [1, 2]):
    for eta in [1.5, 2.0, 3.0]:
        s = d[(d.tau == tau) & (d.eta == eta)].sort_values('K')
        ax.loglog(s.K, s.min_delta, 'o-', color=C[eta], lw=2, ms=5,
                  label=f'η = {eta:g}')
    Ks = np.array(sorted(d.K.unique()))
    ax.loglog(Ks, 2 * tau / Ks, '--', color='0.55', lw=1.2)
    ax.text(Ks[-2], 2 * tau / Ks[-2] * 1.35, '∝ 1/K', color='0.4', fontsize=9)
    ax.set_title(f'τ = {tau}', fontsize=11)
    ax.set_xlabel('K  (n = 4K)')
    log_ticks(ax, [3, 4, 6, 8, 12, 16, 24, 32])
axes[0].set_ylabel('min feasible δ')
axes[0].legend(frameon=False, fontsize=9)
fig.suptitle('R9 candidate, balanced = {y ≤ τ}:  LP min δ = (a^τK/(K−τ))² − 1 exactly',
             fontsize=10.5)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(FIG, 'T2_delta_vs_K.png'), bbox_inches='tight')
plt.close(fig)

# ---- Fig 2: relaxed-F hardness value vs K ---------------------------------
dr = pd.read_csv(os.path.join(HERE, 'T2_grid_relaxF.csv'))
dr = dr[(dr.status == 'OK') & (dr.n == 8 * dr.K) & (dr.tau == 1)]
fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.5), sharex=True)
for ax, eta in zip(axes, [1.5, 2.0, 3.0]):
    s = dr[dr.eta == eta].sort_values('K')
    st = s[s.balanced_def == 'true'] if 'balanced_def' in s else s[s.defn == 'true']
    sy = s[s.balanced_def == 'ysmall'] if 'balanced_def' in s else s[s.defn == 'ysmall']
    Ks = st.K.values
    ax.plot(Ks, st.UK, ':', color='0.45', lw=1.4)
    ax.plot(Ks, st.LK, '--', color='0.45', lw=1.4)
    ax.axhline(1 - np.exp(-1 / eta), color='0.25', lw=0.9)
    ax.plot(sy.K, sy.ratio, 's-', color='#D55E00', lw=2, ms=4.5,
            label='relaxed-F LP, y ≤ τ')
    ax.plot(st.K, st.ratio, 'o-', color='#0072B2', lw=2, ms=5,
            label='relaxed-F LP, true balanced')
    ax.set_xscale('log')
    log_ticks(ax, [3, 4, 6, 8, 12, 16, 24])
    ax.set_title(f'η = {eta:g}', fontsize=11)
    ax.set_xlabel('K  (n = 8K)')
    if eta == 1.5:
        ax.legend(frameon=False, fontsize=8.5, loc='upper right')
        ax.text(Ks[-1], st.UK.values[-1] + 0.012, 'U_K', color='0.35', fontsize=9, ha='right')
        ax.text(Ks[-1], st.LK.values[-1] - 0.028, 'L_K', color='0.35', fontsize=9, ha='right')
        ax.text(Ks[0], 1 - np.exp(-1 / eta) - 0.026, '1 − e^{−1/η}', color='0.2', fontsize=9)
    ax.set_ylim(min(st.LK.min(), 1 - np.exp(-1 / eta)) - 0.05, None)
axes[0].set_ylabel('min achievable ratio (hardness value)')
fig.suptitle('Relaxed-F hardness LP (τ = 1): value sits near U_K and tends to 1 − e^{−1/η}',
             fontsize=10.5)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(os.path.join(FIG, 'T2_relaxF_ratio.png'), bbox_inches='tight')
plt.close(fig)
print('wrote', os.path.join(FIG, 'T2_delta_vs_K.png'))
print('wrote', os.path.join(FIG, 'T2_relaxF_ratio.png'))

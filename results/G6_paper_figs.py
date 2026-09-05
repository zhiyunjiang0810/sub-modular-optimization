"""G6: paper-sized regenerations of the main and auxiliary figures.

The E5 originals (results/E5_money_plot.py) use figsize 9.6in at base font
10pt; scaled to the ICLR text width (5.5in) the effective size drops to
about 5.7pt, below the 7pt submission minimum.  This script re-draws the
same four figures from the same CSVs with paper-sized canvases and fonts,
writing figures/<name>_paper.{png,pdf}.  E5 outputs are left untouched.

Intended inclusion widths and resulting minimum effective font sizes are
printed at the end (the G6 checklist copies that table).
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, 'figures')
TEXTWIDTH_IN = 5.5  # ICLR 2027 text width

TASK_COLOR = {'E1': '#0072B2', 'E2': '#D55E00', 'E3': '#009E73'}
TASK_LABEL = {'E1': 'feature selection (E1)', 'E2': 'influence max (E2)',
              'E3': 'summarization (E3)'}

plt.rcParams.update({'font.size': 11, 'axes.grid': True, 'grid.alpha': 0.25,
                     'grid.linewidth': 0.5, 'axes.spines.top': False,
                     'axes.spines.right': False, 'figure.dpi': 150})

# (figure name, canvas width in inches, min nominal font pt, include width
#  as a fraction of \textwidth) -- used for the printed check table.
PLAN = {
    'money_plot_paper':        (7.0, 9.0, 1.00),
    'aux_eta_sel_by_K_paper':  (7.2, 11.0, 1.00),
    'aux_p_vs_eta_paper':      (4.2, 10.0, 0.55),
    'aux_d_dtilde_scatter_paper': (4.2, 10.0, 0.55),
}


def rho_K(eta, K):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return min(1 - q ** j * (1 - (K - j) / (K * eta)) for j in range(K))


def L_K(eta, K):
    return 1 - (1 - 1 / (eta * K)) ** K


def load_rows():
    frames = []
    for e in ('E1', 'E2', 'E3', 'E4'):
        p = os.path.join(HERE, f'{e}_rows.csv')
        if os.path.exists(p):
            frames.append(pd.read_csv(p))
        else:
            print(f'[notice] {p} missing - skipped in figures')
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def save(fig, name):
    for ext in ('png', 'pdf'):
        fig.savefig(os.path.join(FIG, f'{name}.{ext}'), bbox_inches='tight')
    plt.close(fig)
    print('wrote', name, '(png+pdf)')


def money_plot(rows):
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0), sharey=False)
    for ax, K in zip(axes, (5, 30)):
        etas = np.logspace(0, np.log10(500), 400)
        ax.plot(etas, [L_K(e, K) for e in etas], '--', color='0.45', lw=1.4)
        ax.plot(etas, [rho_K(e, K) for e in etas], '-', color='0.15', lw=1.6)
        sub = rows[rows.K == K]
        for task in ('E1', 'E2', 'E3'):
            s = sub[(sub.task == task) & sub.eta_sel.notna() & sub.ratio.notna()]
            if len(s):
                ax.scatter(s.eta_sel, s.ratio, s=11, alpha=0.45,
                           color=TASK_COLOR[task], label=TASK_LABEL[task],
                           edgecolors='none')
        s4 = sub[(sub.task == 'E4') & sub.eta_sel.notna()]
        if len(s4):
            ax.scatter(s4.eta_sel, s4.ratio, s=40, marker='X', color='#000000',
                       label='worst-case instances (E4)', zorder=5)
        ax.set_xscale('log')
        ax.set_xticks([1, 2, 5, 10, 30, 100, 500])
        ax.set_xticklabels(['1', '2', '5', '10', '30', '100', '500'])
        ax.xaxis.set_minor_locator(NullLocator())
        ax.set_xlabel(r'measured $\eta^{sel}$ (log)')
        ax.set_title(f'K = {K}', fontsize=12)
        ax.set_ylim(0, 1.05)
        n_beyond = int((sub.eta_sel > 500).sum())
        if n_beyond:
            ax.annotate(f'{n_beyond} pts beyond', xy=(430, 0.06), fontsize=9,
                        color='0.4', ha='right')
        if K == 5:
            ax.set_ylabel(r'$f(S^{\tilde f}_{greedy})\,/\,f(S^{f}_{greedy})$')
            # curve-style label lives in the caption (solid rho_K, dashed
            # L_K); an in-axes label collided with the pts-beyond note
        else:
            handles, labels = axes[0].get_legend_handles_labels()
            ax.legend(handles, labels, frameon=False, fontsize=9,
                      loc='lower left', handletextpad=0.2, borderaxespad=0.1)
    # no suptitle in the paper variant: the message lives in the caption
    fig.tight_layout()
    save(fig, 'money_plot_paper')


def aux_eta_box(rows):
    tasks = [t for t in ('E1', 'E2', 'E3') if (rows.task == t).any()]
    if not tasks:
        return print('[notice] no E1-E3 rows; eta box plot skipped')
    fig, axes = plt.subplots(1, len(tasks), figsize=(7.2, 2.6), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, task in zip(axes, tasks):
        s = rows[(rows.task == task) & rows.eta_sel.notna()]
        Ks = sorted(s.K.unique())
        data = [s[s.K == k].eta_sel.astype(float) for k in Ks]
        bp = ax.boxplot(data, tick_labels=[str(k) for k in Ks], showfliers=False,
                        patch_artist=True, medianprops=dict(color='0.15', lw=1.6))
        for b in bp['boxes']:
            b.set(facecolor=TASK_COLOR[task], alpha=0.4, edgecolor=TASK_COLOR[task])
        ax.set_yscale('log')
        ax.set_title(TASK_LABEL[task], fontsize=11)
        ax.set_xlabel('K')
        if len(Ks) > 10:
            keep = list(range(0, len(Ks), 5))
            ax.set_xticks([i + 1 for i in keep])
            ax.set_xticklabels([str(Ks[i]) for i in keep])
    axes[0].set_ylabel(r'$\eta^{sel}$ (log)')
    fig.tight_layout()
    save(fig, 'aux_eta_sel_by_K_paper')


def aux_p_eta():
    p = os.path.join(HERE, 'E2_p_eta.csv')
    if not os.path.exists(p):
        return print('[notice] E2_p_eta.csv missing - aux p-eta skipped')
    df = pd.read_csv(p)
    fig, ax = plt.subplots(figsize=(4.2, 3.1))
    for i, (ds, s) in enumerate(df.groupby('dataset')):
        s = s.sort_values('p')
        col = ['#0072B2', '#D55E00', '#009E73', '#E69F00'][i % 4]
        ax.plot(s.p, s.eta_sel_K30_median, 'o-', lw=2, ms=5, color=col, label=ds)
    ax.set_yscale('log')
    ax.set_xlabel('edge observation probability p')
    ax.set_ylabel(r'median $\eta^{sel}$ at K=30')
    ax.legend(frameon=False, fontsize=10)
    fig.tight_layout()
    save(fig, 'aux_p_vs_eta_paper')


def aux_pairs_scatter():
    p = os.path.join(HERE, 'E1_pairs.csv.gz')
    if not os.path.exists(p):
        return print('[notice] E1_pairs.csv.gz missing - aux scatter skipped')
    df = pd.read_csv(p)
    ds = 'breast_cancer' if (df.dataset == 'breast_cancer').any() else df.dataset.iloc[0]
    s = df[df.dataset == ds]
    if len(s) > 20000:
        s = s.sample(20000, random_state=0)
    fig, ax = plt.subplots(figsize=(4.2, 3.8))
    ax.scatter(s.dtilde, s.d, s=6, alpha=0.25, color='#0072B2', edgecolors='none')
    lim = max(abs(s.d).quantile(0.995), abs(s.dtilde).quantile(0.995))
    for eta in (2.0,):
        xs = np.linspace(0, lim, 50)
        ax.plot(xs, eta ** 0.5 * xs, '-', color='0.3', lw=1)
        ax.plot(xs, xs / eta ** 0.5, '-', color='0.3', lw=1)
        ax.fill_between(xs, xs / eta ** 0.5, eta ** 0.5 * xs, color='0.75', alpha=0.3)
    ax.axhline(0, color='0.6', lw=0.7)
    ax.axvline(0, color='0.6', lw=0.7)
    ax.set_xlim(-lim * 0.35, lim)
    ax.set_ylim(-lim * 0.35, lim)
    ax.set_xlabel(r'predicted gain $\tilde d$')
    ax.set_ylabel(r'true gain $d$')
    ax.set_title(f'({ds})  shaded: $\\eta = 2$ band', fontsize=10)
    fig.tight_layout()
    save(fig, 'aux_d_dtilde_scatter_paper')


def main():
    rows = load_rows()
    if rows.empty:
        sys.exit('no row CSVs at all')
    for c in ('ratio', 'eta_sel', 'eta_path_trimmed'):
        rows[c] = pd.to_numeric(rows[c], errors='coerce')
    money_plot(rows)
    aux_eta_box(rows)
    aux_p_eta()
    aux_pairs_scatter()
    print('\nname, canvas(in), min nominal pt, include width, effective pt')
    for name, (w, minpt, frac) in PLAN.items():
        eff = minpt * (TEXTWIDTH_IN * frac) / w
        flag = 'OK' if eff >= 7.0 else 'TOO SMALL'
        print(f'{name}: {w}in, {minpt}pt, {frac}\\textwidth -> '
              f'{eff:.1f}pt effective [{flag}]')


if __name__ == '__main__':
    main()

"""K3: split the main figure into two, per the J2 adoption (user supplement 3).

Figure 1 (figures/money_plot.pdf, selection-error axis): ONLY the L_K curve
and the real-task scatter.  rho_K is a worst case for the GLOBAL error and
is not an envelope over (etasel, ratio) pairs (J2 section 5, exact K=2
counterexample, re-verified in results/H3_j2_recheck.py), so it leaves this
axis.  E2 trajectories with a harmful zero step (n_steps_nonpos > 0; J2's
evidence shows every such step has a positive candidate) have stepwise
etasel = infinity under decision D3: they are stated in the panel and not
drawn.  E1/E3 points are finite-step diagnostics (their objectives are out
of the model); the caption in the paper says so.

Figure 2 (figures/eta_global_plot.pdf, global-error axis): rho_K curves for
K in {3,5,8} with the E4 constructed instances at their DESIGN global eta
(results/E4_worst_case.csv): V_j instances sit on the curves, U_K instances
sit visibly above them (the old family is strictly non-optimal).

Also regenerates figures/aux_p_vs_eta.pdf from E2_rows.csv with the
infinity override (the night-3 E2_p_eta.csv predates decision D3): finite
cell medians drawn, the one infinite-median cell marked at the axis top.

Paper-sized fonts (>= 7pt after column scaling, see the printed table).
Copies of the PDFs are written into paper/figures/ under the names the
paper includes.  E5/G6 outputs are left untouched.
"""
import csv, os, shutil, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, 'figures')
PFIG = os.path.join(ROOT, 'paper', 'figures')
TEXTWIDTH_IN = 5.5

TASK_COLOR = {'E1': '#0072B2', 'E2': '#D55E00', 'E3': '#009E73'}
TASK_LABEL = {'E1': 'feature selection (E1)', 'E2': 'influence max (E2)',
              'E3': 'summarization (E3)'}

plt.rcParams.update({'font.size': 11, 'axes.grid': True, 'grid.alpha': 0.25,
                     'grid.linewidth': 0.5, 'axes.spines.top': False,
                     'axes.spines.right': False, 'figure.dpi': 150})


def L_K(eta, K):
    return 1 - (1 - 1 / (eta * K)) ** K


def rho_K(eta, K):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return min(1 - q ** j * (1 - (K - j) / (K * eta)) for j in range(K))


def rows_of(name):
    with open(os.path.join(HERE, name), newline='') as fh:
        return list(csv.DictReader(fh))


def save(fig, name):
    for ext in ('png', 'pdf'):
        fig.savefig(os.path.join(FIG, f'{name}.{ext}'), bbox_inches='tight')
    plt.close(fig)
    print('wrote', name)


def fig_selection():
    rows = []
    for e in ('E1', 'E2', 'E3'):
        rows += rows_of(f'{e}_rows.csv')
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0), sharey=False)
    for ax, K in zip(axes, (5, 30)):
        etas = np.logspace(0, np.log10(500), 400)
        ax.plot(etas, [L_K(e, K) for e in etas], '-', color='0.25', lw=1.6,
                label=r'$L_K$ (per panel)')
        sub = [r for r in rows if int(r['K']) == K]
        n_inf = 0
        for task in ('E1', 'E2', 'E3'):
            pts = []
            for r in sub:
                if r['task'] != task or not r['eta_sel'] or not r['ratio']:
                    continue
                if task == 'E2' and float(r['n_steps_nonpos']) > 0:
                    n_inf += 1          # stepwise etasel = infinity: not drawn
                    continue
                pts.append((float(r['eta_sel']), float(r['ratio'])))
            if pts:
                x, y = zip(*pts)
                ax.scatter(x, y, s=11, alpha=0.45, color=TASK_COLOR[task],
                           label=TASK_LABEL[task], edgecolors='none')
        ax.set_xscale('log')
        ax.set_xticks([1, 2, 5, 10, 30, 100, 500])
        ax.set_xticklabels(['1', '2', '5', '10', '30', '100', '500'])
        ax.xaxis.set_minor_locator(NullLocator())
        ax.set_xlabel(r'measured $\eta^{sel}$ (log)')
        ax.set_title(f'K = {K}', fontsize=12)
        ax.set_ylim(0, 1.05)
        notes = []
        n_beyond = sum(1 for r in sub if r['eta_sel']
                       and float(r['eta_sel']) > 500
                       and not (r['task'] == 'E2'
                                and float(r['n_steps_nonpos']) > 0))
        if n_beyond:
            notes.append(f'{n_beyond} pts beyond')
        if n_inf:
            notes.append(rf'{n_inf} E2 runs $\eta^{{sel}}=\infty$')
        if notes:
            ax.annotate('\n'.join(notes), xy=(430, 0.45 if K == 30 else 0.05),
                        fontsize=9, color='0.4', ha='right')
        if K == 5:
            ax.set_ylabel(r'$f(S^{\tilde f}_{greedy})\,/\,f(S^{f}_{greedy})$')
        else:
            handles, labels = axes[0].get_legend_handles_labels()
            ax.legend(handles, labels, frameon=False, fontsize=9,
                      loc='lower left', handletextpad=0.2, borderaxespad=0.1)
    fig.tight_layout()
    save(fig, 'money_plot_k3')


def fig_global():
    wc = rows_of('E4_worst_case.csv')
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    Ks = (3, 5, 8)
    styles = {3: ('-', '#0072B2'), 5: ('--', '#D55E00'), 8: (':', '#009E73')}
    etas = np.linspace(1.0, 8.5, 400)
    for K in Ks:
        ls, colr = styles[K]
        ax.plot(etas, [rho_K(e, K) for e in etas], ls, color=colr, lw=1.6,
                label=rf'$\rho_{{{K}}}$')
    for r in wc:
        K = int(r['label'].split('_')[1][1:])
        colr = styles[K][1]
        if r['label'].startswith('Vj'):
            ax.scatter(float(r['eta']), float(r['realized']), marker='X',
                       s=42, color=colr, zorder=5, edgecolors='none')
        else:
            ax.scatter(float(r['eta']), float(r['realized']), marker='s',
                       s=34, facecolors='none', edgecolors=colr, zorder=5)
    ax.scatter([], [], marker='X', s=42, color='0.3', label=r'$V_j$ instances')
    ax.scatter([], [], marker='s', s=34, facecolors='none', edgecolors='0.3',
               label=r'$U_K$ instances')
    ax.set_xlabel(r'design global error $\eta$')
    ax.set_ylabel('realized ratio')
    ax.set_ylim(0, 1.0)
    ax.legend(frameon=False, fontsize=9, ncol=2, columnspacing=0.8,
              handletextpad=0.2)
    fig.tight_layout()
    save(fig, 'eta_global_plot')


def fig_p_eta():
    K = 30
    rows = [r for r in rows_of('E2_rows.csv')
            if r['task'] == 'E2' and int(r['K']) == K]
    graphs = sorted({r['dataset'] for r in rows})
    ps = sorted({float(r['p']) for r in rows})
    fig, ax = plt.subplots(figsize=(4.2, 3.1))
    top = 0.0
    series = {}
    for g in graphs:
        meds = []
        for p in ps:
            cell = sorted(float('inf') if float(r['n_steps_nonpos']) > 0
                          else float(r['eta_sel'])
                          for r in rows if r['dataset'] == g
                          and float(r['p']) == p)
            i = 0.5 * (len(cell) - 1)
            lo, hi = cell[int(i)], cell[min(int(i) + 1, len(cell) - 1)]
            m = lo + (hi - lo) * (i - int(i)) if hi != float('inf') \
                else float('inf')
            meds.append(m)
            if m != float('inf'):
                top = max(top, m)
        series[g] = meds
    for i, g in enumerate(graphs):
        colr = ['#0072B2', '#D55E00', '#009E73', '#E69F00'][i % 4]
        xs = [p for p, m in zip(ps, series[g]) if m != float('inf')]
        ys = [m for m in series[g] if m != float('inf')]
        ax.plot(xs, ys, 'o-', lw=2, ms=5, color=colr, label=g)
        for p, m in zip(ps, series[g]):
            if m == float('inf'):
                ax.annotate(r'median $=\infty$', xy=(p, top * 1.6),
                            fontsize=9, color=colr, ha='center')
                ax.scatter([p], [top * 1.35], marker='^', s=40, color=colr)
    ax.set_yscale('log')
    ax.set_ylim(top=top * 2.6)
    ax.set_xlabel('edge observation probability p')
    ax.set_ylabel(rf'median $\eta^{{sel}}$ at K={K}')
    ax.legend(frameon=False, fontsize=9, loc='upper right')
    fig.tight_layout()
    save(fig, 'aux_p_vs_eta_k3')


def main():
    fig_selection()
    fig_global()
    fig_p_eta()
    shutil.copy(os.path.join(FIG, 'money_plot_k3.pdf'),
                os.path.join(PFIG, 'money_plot.pdf'))
    shutil.copy(os.path.join(FIG, 'eta_global_plot.pdf'),
                os.path.join(PFIG, 'eta_global_plot.pdf'))
    shutil.copy(os.path.join(FIG, 'aux_p_vs_eta_k3.pdf'),
                os.path.join(PFIG, 'aux_p_vs_eta.pdf'))
    print('copied into paper/figures/')
    print('\nfont check (canvas -> include width -> effective pt):')
    for name, w, minpt, frac in (
            ('money_plot', 7.0, 9.0, 1.00),
            ('eta_global_plot', 4.2, 9.0, 0.60),
            ('aux_p_vs_eta', 4.2, 9.0, 0.66)):
        eff = minpt * (TEXTWIDTH_IN * frac) / w
        print(f'  {name}: {eff:.1f}pt', 'OK' if eff >= 7 else 'TOO SMALL')


if __name__ == '__main__':
    main()

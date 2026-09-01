"""Shared statistics for all experiment tasks (TASKS_EXP.md).

Implements the three theory-comparison quantities and the unified row format:
  task, dataset, K, seed, ratio, eta_sel, eta_path_trimmed, viol_sign_pct,
  L_K(eta_sel), L_K(eta_path), n_steps_nonpos, frac_steps_nonpos

Definitions (per TASKS_EXP.md):
- eta_sel: max over greedy-on-f~ trajectory steps of  max_e d_e(S^t) / d_{e_t}(S^t),
  true values only.

  NON-POSITIVE STEPS (fixed policy, TASKS4 F1.3; do not change silently).
  eta^sel is DEFINED ONLY on steps whose chosen true gain is d_t > 0.  A step
  with d_t <= 0 makes the quotient max_e d_e / d_t meaningless (undefined at
  d_t = 0, sign-flipped at d_t < 0), so such a step is:
    * excluded from the max that defines eta^sel, and
    * counted in n_nonpos_steps, which the unified row exports as the two
      columns n_steps_nonpos (count) and frac_steps_nonpos (share of the
      scored steps of the length-K prefix).
  Consequence for the certified bound: the column LK_eta_sel = L_K(eta^sel)
  is the Theorem-6 bound evaluated at an eta^sel that is measured OVER THE
  POSITIVE-GAIN STEPS ONLY, so the guarantee it reports holds for the
  positive-gain steps; the share of steps outside that scope is exactly
  frac_steps_nonpos.  The CSV column name stays machine-readable
  (LK_eta_sel); the scope is stated in the table notes, not in the header.
  If every scored step of the prefix has d_t <= 0 then eta_sel is None and
  both eta_sel and LK_eta_sel are written as the empty string.
- eta_path(eps): over trajectory states and candidates with |d| >= eps AND
  |d~| >= eps:  max(d/d~) * max(d~/d), restricted to pairs with d>0 and d~>0;
  sign-violation % = share of candidate pairs (|d|>=eps or |d~|>=eps) with
  strictly opposite signs.  It is computed over whatever candidate pairs the
  caller passes to add_step: passing a truncated candidate list gives an
  UNDERESTIMATE, so callers must pass all candidates (TASKS4 F1.2).
- ratio = f(S_greedy^{f~}) / f(S_greedy^{f})  (denominator: true-value greedy as
  OPT proxy; this OVERSTATES the ratio's denominator quality claim, noted in
  every report).

Principles 1-5 of TASKS_EXP.md apply (no artificial oracle noise; caching+CELF;
seeds fixed; CSV+PNG/PDF; honest reporting).
"""
import csv
import math

ROW_FIELDS = ['task', 'dataset', 'K', 'seed', 'ratio', 'eta_sel',
              'eta_path_trimmed', 'viol_sign_pct', 'LK_eta_sel', 'LK_eta_path',
              'n_steps_nonpos', 'frac_steps_nonpos']


def L_K(eta, K):
    if eta is None or eta <= 0 or not math.isfinite(eta):
        return float('nan')
    return 1 - (1 - 1 / (eta * K)) ** K


class TrajectoryStats:
    """Accumulates per-step data along greedy-on-f~ and computes the three
    quantities for every prefix K.

    Per step t call add_step(d_chosen, dmax_true, pairs) where pairs is an
    iterable of (d, dtilde) over the candidates evaluated at state S^t.
    `pairs` must contain EVERY remaining candidate: a truncated list makes
    eta_path an underestimate and changes the denominator of viol_sign_pct
    (TASKS4 F1.2).  d_chosen <= 0 is allowed and is handled as described in
    the module docstring."""

    def __init__(self, eps):
        self.eps = eps
        self.steps = []          # (d_chosen, dmax_true)
        self.pairs_per_step = []  # list of lists of (d, dt)

    def add_step(self, d_chosen, dmax_true, pairs):
        self.steps.append((d_chosen, dmax_true))
        self.pairs_per_step.append(list(pairs))

    def upto(self, K):
        """Stats for the length-K prefix. Returns dict.

        eta_sel is taken over the steps with chosen true gain d_t > 0 only
        (see the module docstring); steps with d_t <= 0 are counted in
        n_nonpos_steps and n_steps counts the scored steps of the prefix, so
        n_nonpos_steps / n_steps is the share outside the bound's scope."""
        eps = self.eps
        eta_sel = None
        n_nonpos_steps = 0
        n_steps = 0
        for d_c, d_m in self.steps[:K]:
            if d_c is None or d_m is None:
                continue
            n_steps += 1
            if d_c <= 0:
                n_nonpos_steps += 1
                continue
            r = d_m / d_c
            eta_sel = r if eta_sel is None else max(eta_sel, r)
        if eta_sel is not None:
            eta_sel = max(eta_sel, 1.0)
        mu, mo = None, None
        n_pairs = n_viol = n_considered = 0
        for plist in self.pairs_per_step[:K]:
            for d, dt in plist:
                n_pairs += 1
                if abs(d) >= eps or abs(dt) >= eps:
                    n_considered += 1
                    if (d > 0 and dt < 0) or (d < 0 and dt > 0):
                        n_viol += 1
                if d >= eps and dt >= eps:
                    mu = d / dt if mu is None else max(mu, d / dt)
                    mo = dt / d if mo is None else max(mo, dt / d)
        eta_path = (max(mu, 0) * max(mo, 0)) if (mu is not None and mo is not None) else None
        if eta_path is not None:
            eta_path = max(eta_path, 1.0)
        viol_pct = 100.0 * n_viol / n_considered if n_considered else float('nan')
        return dict(eta_sel=eta_sel, eta_path=eta_path, viol_sign_pct=viol_pct,
                    n_nonpos_steps=n_nonpos_steps, n_steps=n_steps,
                    n_pairs=n_pairs)


def unified_row(task, dataset, K, seed, ratio, st, eta_path_override=None):
    """st = TrajectoryStats.upto(K) result.

    eta_path_override: pass a string (e.g. 'n/a') to replace the computed
    eta_path_trimmed when the caller knows the value would be a truncated
    UNDERESTIMATE; LK_eta_path is then written empty as well."""
    es, ep = st['eta_sel'], st['eta_path']
    fmt = lambda x: '' if x is None else f'{x:.6g}'
    nnp, ns = st['n_nonpos_steps'], st.get('n_steps', 0)
    return dict(task=task, dataset=dataset, K=K, seed=seed,
                ratio=f'{ratio:.6f}' if ratio is not None else '',
                eta_sel=fmt(es),
                eta_path_trimmed=(eta_path_override if eta_path_override
                                  is not None else fmt(ep)),
                viol_sign_pct=f"{st['viol_sign_pct']:.2f}",
                LK_eta_sel=f'{L_K(es, K):.6f}' if es else '',
                LK_eta_path=('' if eta_path_override is not None
                             else (f'{L_K(ep, K):.6f}' if ep else '')),
                n_steps_nonpos=nnp,
                frac_steps_nonpos=(f'{nnp / ns:.6f}' if ns else ''))


def write_rows(path, rows, append=False):
    mode = 'a' if append else 'w'
    with open(path, mode, newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=ROW_FIELDS)
        if not append:
            w.writeheader()
        for r in rows:
            w.writerow(r)

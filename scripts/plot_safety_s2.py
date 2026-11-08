"""Figure for results/safety/s2-v1 (written by scripts/evaluate_safety_s2.mjs).

Run:  python scripts/plot_safety_s2.py   (refuses to overwrite the PNG)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / 'results/safety/s2-v1/evaluation.json'
COLOURS = {'S0': '#eb6834', 'S1': '#2a78d6', 'S2': '#1baf7a'}  # validated slots 1-3 (all-pairs safe)
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e4e3df'


def tidy(ax, title, xlabel):
    ax.set_title(title, loc='left', fontsize=11, color=INK)
    ax.set_xlabel(xlabel, color=MUTED, fontsize=9)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis='x', color=GRID)
    ax.set_axisbelow(True)
    ax.set_xlim(0, 1)


def figure(data, out=None):
    import matplotlib
    if out is not None:
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 5), gridspec_kw={'width_ratios': [1, 1.4]})
    names = ['S0', 'S1', 'S2']
    v3 = data['heldout_v3']['detectors']
    metrics = [('recall', 'recall_wilson95', 'urgent recall'), ('false_positive_rate', 'fpr_wilson95', 'false-positive rate')]
    for k, d in enumerate(names):
        y = [i + (k - 1) * 0.27 for i in range(2)]
        vals = [v3[d][m] for m, _, _ in metrics]
        ci = [v3[d][c] for _, c, _ in metrics]
        a.barh(y, vals, height=0.25, color=COLOURS[d], label=d, edgecolor='#fcfcfb', linewidth=2)
        for yy, v in zip(y, vals):
            if v == 0:
                a.text(0.21, yy, f'{d}: 0', va='center', fontsize=8, color=MUTED)
        a.errorbar(vals, y, xerr=[[v - lo for v, (lo, hi) in zip(vals, ci)], [hi - v for v, (lo, hi) in zip(vals, ci)]],
                   fmt='none', ecolor=INK, elinewidth=1, capsize=2)
    a.set_yticks(range(2))
    a.set_yticklabels([l for _, _, l in metrics])
    a.invert_yaxis()
    n = data['heldout_v3']
    tidy(a, 'F9a. New frozen held-out set (v3)', f"share, {v3['S2']['tp'] + v3['S2']['fn']} urgent / {v3['S2']['fp'] + v3['S2']['tn']} non-urgent (95% Wilson)")

    pert = data['development_perturbed']
    labels = list(pert)
    for d in names:
        b.scatter([pert[p]['detectors'][d]['recall'] for p in labels], range(len(labels)), s=40, color=COLOURS[d],
                  label=d, edgecolor='#fcfcfb', linewidth=1.5, zorder=3)
    for i, p in enumerate(labels):
        b.plot([pert[p]['detectors']['S1']['recall'], pert[p]['detectors']['S2']['recall']], [i, i], color=MUTED, lw=1, zorder=2)
    b.set_yticks(range(len(labels)))
    b.set_yticklabels([p.replace('_', ' ') for p in labels])
    b.invert_yaxis()
    tidy(b, 'F9b. Development cases under typing perturbations', 'urgent recall (S2 was designed against these)')
    handles, labels_ = a.get_legend_handles_labels()
    fig.legend(handles, ['S0 original regex', 'S1 frozen rules', 'S2 normalised rules'], ncol=3, frameon=False,
               fontsize=9, loc='upper right')
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    if out is None:
        plt.show()
    else:
        if out.exists():
            raise SystemExit(f'{out} exists; keep the old figure or choose a new name')
        fig.savefig(out, dpi=150, facecolor='#fcfcfb')
    return fig


if __name__ == '__main__':
    out = RESULT.with_name('F9_s0_s1_s2.png')
    figure(json.loads(RESULT.read_text(encoding='utf-8')), out)
    print('saved', out)

"""Figure for results/safety/perturbation-v1 (written by scripts/perturb_safety.mjs).

Run:  python scripts/plot_safety_perturbation.py   (refuses to overwrite the PNG)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / 'results/safety/perturbation-v1/evaluation.json'
COLOURS = {'S1': '#2a78d6', 'S0': '#eb6834'}
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e4e3df'


def figure(data, out=None):
    import matplotlib
    if out is not None:
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    names = list(data['perturbations'])
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    for k, det in enumerate(['S1', 'S0']):
        y = [i + (k - 0.5) * 0.36 for i in range(len(names))]
        rec = [data['perturbations'][n][det]['recall'] for n in names]
        ci = [data['perturbations'][n][det]['recall_wilson95'] for n in names]
        ax.barh(y, rec, height=0.34, color=COLOURS[det], edgecolor='#fcfcfb', linewidth=2,
                label={'S1': 'S1 (current rules)', 'S0': 'S0 (original regex)'}[det])
        ax.errorbar(rec, y, xerr=[[r - lo for r, (lo, hi) in zip(rec, ci)], [hi - r for r, (lo, hi) in zip(rec, ci)]],
                    fmt='none', ecolor=INK, elinewidth=1, capsize=2)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels([n.replace('_', ' ') for n in names], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel(f"urgent-case recall, {data['urgent_cases']} urgent cases (95% Wilson)", color=MUTED, fontsize=9)
    ax.set_title('F8. Safety routing recall under ordinary typing variation', loc='left', fontsize=11, color=INK)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=MUTED)
    ax.grid(axis='x', color=GRID)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=9, loc='lower right')
    fig.tight_layout()
    if out is None:
        plt.show()
    else:
        if out.exists():
            raise SystemExit(f'{out} exists; keep the old figure or choose a new name')
        fig.savefig(out, dpi=150, facecolor='#fcfcfb')
    return fig


if __name__ == '__main__':
    figure(json.loads(RESULT.read_text(encoding='utf-8')), RESULT.with_name('F8_recall_by_perturbation.png'))
    print('saved', RESULT.with_name('F8_recall_by_perturbation.png'))

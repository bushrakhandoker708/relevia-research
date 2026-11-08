"""Robustness re-analysis of the frozen expanded-v1 run. Reads results, never regenerates.

Motivation: execution_summary.json reports a paired latency difference of
B - A = -18.9 s with a bootstrap interval of -51.7 to -1.3 s. That interval excludes
zero, but one pair (expanded-055 A, 956.7 s) overlaps a recorded Windows Modern
Standby interval. A mean over 60 pairs that contains a 16-minute sleep is mostly
measuring the sleep. A also writes longer replies (30 token-limit hits against 1),
so even a clean latency gap could be a length effect rather than a prompt effect.

The experiments here ask whether the execution-level findings survive:
  E1  host-availability sensitivity: all pairs vs pairs clear of the standby window,
      mean vs median vs Hodges-Lehmann, plus an exact sign test
  E2  length control: seconds per output token, and a per-condition linear fit of
      elapsed time on output tokens
  E3  instruction compliance per scenario category with Wilson intervals, and an
      exact McNemar test for the paired token-limit outcome
  E5  host speed regimes: decode speed halves part-way through the run (about
      5 -> 2.5 tok/s, with CPU parallelism falling too). Each generation is labelled
      fast/slow and repeat the paired comparison on regime-matched pairs only
  E4  surface-form diagnostics (lexical diversity, questions, repeated openings,
      stock phrases). These describe form only. They are NOT empathy or quality.

Nothing here is a quality result. Independent human ratings are still missing.

Run:  python scripts/analyse_robustness.py
Out:  results/analysis/robustness-v1/robustness.json and figures/*.png
      (refuses to overwrite; pass --out for a new version)
"""
import argparse
import json
import math
import random
import re
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'results/experiment_01/expanded-v1'
POWER = ROOT / 'results/completion_2026_11_07/power_events_verified.json'
REGIME_SPLIT = 3.5  # tok/s; the two observed clusters sit near 2.5 and 5, nothing falls between 3 and 4.2
WORD_LIMIT = 65  # the developed prompt (B) asks for at most 65 words; A has no such request

# Recurring phrases in the raw responses (agent-selected); counted, not judged.
STOCK_PHRASES = {
    'deep_breath': r'deep breath',
    'understandable': r"(it'?s|that'?s) (completely |totally |perfectly )?(understandable|normal|okay|ok)",
    'remember_that': r'\bremember (that|to)\b',
    'reach_out': r'reach out',
    'professional': r'therapist|counsel+or|mental health professional',
}


# ---------- statistics (stdlib only, so CI can test them) ----------

def wilson(success, total, z=1.959963984540054):
    """Wilson 95% interval; None when there is nothing to estimate."""
    if not total:
        return None
    p = success / total
    den = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / den
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / den
    return [max(0.0, centre - radius), min(1.0, centre + radius)]


def binom_two_sided(k, n):
    """Exact two-sided binomial test at p = 0.5 (sign test / exact McNemar)."""
    if n == 0:
        return None
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def hodges_lehmann(diffs):
    """Median of Walsh averages: a location estimate a single huge pair cannot drag."""
    walsh = [(diffs[i] + diffs[j]) / 2 for i in range(len(diffs)) for j in range(i, len(diffs))]
    return statistics.median(walsh)


def bootstrap(values, stat, n=10000, seed=42):
    if not values:
        return None
    rng = random.Random(seed)
    draws = sorted(stat(rng.choices(values, k=len(values))) for _ in range(n))
    return [draws[int(0.025 * n)], draws[int(0.975 * n) - 1]]


def location_summary(diffs):
    if not diffs:
        return None
    positive = sum(d > 0 for d in diffs)
    nonzero = sum(d != 0 for d in diffs)
    return {
        'n_pairs': len(diffs),
        'mean': statistics.mean(diffs), 'mean_bootstrap95': bootstrap(diffs, statistics.mean),
        'median': statistics.median(diffs), 'median_bootstrap95': bootstrap(diffs, statistics.median),
        'hodges_lehmann': hodges_lehmann(diffs),
        'B_slower_pairs': positive, 'B_faster_pairs': sum(d < 0 for d in diffs),
        'sign_test_p': binom_two_sided(positive, nonzero),
    }


def ols(xs, ys):
    """Simple least squares y = a + b x; None if x has no spread."""
    if len(xs) < 3:
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    intercept = my - slope * mx
    resid = [y - intercept - slope * x for x, y in zip(xs, ys)]
    sst = sum((y - my) ** 2 for y in ys)
    return {'intercept_seconds': intercept, 'seconds_per_output_token': slope,
            'r_squared': 1 - sum(r * r for r in resid) / sst if sst else None, 'n': len(xs)}


def mcnemar(pairs):
    """pairs = [(a_bool, b_bool)]; exact test on the discordant pairs only."""
    only_a = sum(a and not b for a, b in pairs)
    only_b = sum(b and not a for a, b in pairs)
    return {'both': sum(a and b for a, b in pairs), 'neither': sum(not a and not b for a, b in pairs),
            'only_A': only_a, 'only_B': only_b, 'exact_p': binom_two_sided(min(only_a, only_b), only_a + only_b)}


def distinct_n(texts, n):
    grams, total = set(), 0
    for t in texts:
        toks = re.findall(r"[a-z']+", t.lower())
        ng = list(zip(*[toks[i:] for i in range(n)]))
        grams.update(ng)
        total += len(ng)
    return len(grams) / total if total else None


# ---------- loading ----------

def parse(ts):
    return datetime.fromisoformat(ts)  # runner writes ISO 8601 with +00:00


def standby_window():
    events = json.loads(POWER.read_text(encoding='utf-8'))['events']
    enter = next(e for e in events if e['id'] == 506)['utc']
    leave = next(e for e in events if e['id'] == 507)['utc']
    # Windows writes 7 fractional digits; Python wants at most 6
    trim = lambda s: re.sub(r'(\.\d{6})\d*Z$', r'\1+00:00', s)
    return datetime.fromisoformat(trim(enter)), datetime.fromisoformat(trim(leave))


def load(run=RUN):
    rows = [json.loads(s) for s in (run / 'responses.jsonl').read_text(encoding='utf-8').splitlines() if s.strip()]
    return [r for r in rows if not r['warmup']]


def pairs_of(rows):
    groups = {}
    for r in rows:
        groups.setdefault(r['scenario_id'], {})[r['condition']] = r
    if any(set(p) != {'A', 'B'} for p in groups.values()):
        raise ValueError('Incomplete A/B pair')
    return groups


def overlaps(row, window):
    start, end = parse(row['started_utc']), parse(row['ended_utc'])
    return start < window[1] and end > window[0]


# ---------- experiments ----------

def analyse(rows, window):
    groups = pairs_of(rows)
    ok = {s: p for s, p in groups.items() if all(r['status'] == 'generated' for r in p.values())}
    affected = sorted(s for s, p in ok.items() if any(overlaps(r, window) for r in p.values()))
    clean = {s: p for s, p in ok.items() if s not in affected}
    diff = lambda ps, f: [f(p['B']) - f(p['A']) for p in ps.values()]
    elapsed = lambda r: r['elapsed_seconds']
    per_token = lambda r: r['elapsed_seconds'] / r['output_tokens']
    decode_time = lambda r: r['elapsed_seconds'] - (r['ttft_seconds'] or 0)

    out = {'scope': 'Execution and surface-form re-analysis of frozen expanded-v1; no quality ratings',
           'standby_window_utc': [w.isoformat() for w in window], 'standby_affected_pairs': affected}

    out['E1_latency_sensitivity'] = {
        'all_pairs': location_summary(diff(ok, elapsed)),
        'excluding_standby': location_summary(diff(clean, elapsed)),
        'note': 'B - A in seconds. Negative means B finished sooner.'}

    clean_rows = [r for p in clean.values() for r in p.values()]
    out['E2_length_control'] = {
        'seconds_per_output_token_B_minus_A': location_summary(diff(clean, per_token)),
        'ttft_B_minus_A': location_summary([p['B']['ttft_seconds'] - p['A']['ttft_seconds'] for p in clean.values()
                                            if p['A']['ttft_seconds'] is not None and p['B']['ttft_seconds'] is not None]),
        'output_tokens_B_minus_A': location_summary(diff(clean, lambda r: r['output_tokens'])),
        'fit_elapsed_on_output_tokens': {c: ols([r['output_tokens'] for r in clean_rows if r['condition'] == c],
                                                [decode_time(r) for r in clean_rows if r['condition'] == c]) for c in 'AB'},
        'note': 'Fit uses elapsed minus TTFT, so the slope is time per generated token after the first.'}

    cats = sorted({r['scenario_category'] for r in rows})
    def compliance(subset):
        res = {}
        for c in 'AB':
            s = [r for r in subset if r['condition'] == c and r['status'] == 'generated']
            hits = sum(r['hit_token_limit'] for r in s)
            over = sum(len(r['response'].split()) > WORD_LIMIT for r in s)
            res[c] = {'n': len(s), 'token_limit_hits': hits, 'token_limit_rate': hits / len(s) if s else None,
                      'token_limit_wilson95': wilson(hits, len(s)), 'over_word_limit': over,
                      'over_word_limit_rate': over / len(s) if s else None, 'over_word_limit_wilson95': wilson(over, len(s)),
                      'median_words': statistics.median(len(r['response'].split()) for r in s) if s else None}
        return res
    out['E3_compliance'] = {
        'overall': compliance(rows),
        'by_category': {cat: compliance([r for r in rows if r['scenario_category'] == cat]) for cat in cats},
        'token_limit_mcnemar': mcnemar([(p['A']['hit_token_limit'], p['B']['hit_token_limit']) for p in ok.values()]),
        'word_limit_mcnemar': mcnemar([(len(p['A']['response'].split()) > WORD_LIMIT, len(p['B']['response'].split()) > WORD_LIMIT)
                                       for p in ok.values()]),
        'note': 'A was never asked for 65 words, so its word-limit rate is a reference point, not a violation.'}

    form = {}
    for c in 'AB':
        texts = [r['response'] for r in rows if r['condition'] == c and r['status'] == 'generated']
        openers = Counter(' '.join(re.findall(r"[a-z']+", t.lower())[:3]) for t in texts)
        form[c] = {'n': len(texts), 'distinct_1': distinct_n(texts, 1), 'distinct_2': distinct_n(texts, 2),
                   'asks_question_rate': sum('?' in t for t in texts) / len(texts),
                   'top_opener': openers.most_common(1)[0][0], 'top_opener_share': openers.most_common(1)[0][1] / len(texts),
                   'stock_phrase_rate': {k: sum(bool(re.search(p, t, re.I)) for t in texts) / len(texts) for k, p in STOCK_PHRASES.items()}}
    regime = lambda r: 'fast' if (r.get('decode_tokens_per_second') or 0) >= REGIME_SPLIT else 'slow'
    matched = {s: p for s, p in clean.items() if regime(p['A']) == regime(p['B'])}
    out['E5_host_regimes'] = {
        'split_tokens_per_second': REGIME_SPLIT,
        'counts': {c: dict(Counter(regime(r) for r in rows if r['condition'] == c)) for c in 'AB'},
        'mixed_regime_pairs': sorted(s for s, p in clean.items() if s not in matched),
        'median_decode_tps': {g: statistics.median(r['decode_tokens_per_second'] for r in rows if regime(r) == g) for g in ('fast', 'slow')},
        'median_cpu_parallelism': {g: statistics.median(r['process_cpu_seconds'] / r['elapsed_seconds'] for r in rows if regime(r) == g)
                                   for g in ('fast', 'slow')},
        'timeline': 'slow for the first few generations, fast from about 08:07, slow again from about 08:16 UTC to the end (see F7)',
        'regime_matched_latency_B_minus_A': location_summary(diff(matched, elapsed)),
        'regime_matched_per_token_B_minus_A': location_summary(diff(matched, per_token)),
        'note': 'Cause unrecorded (power plan, thermal limit or competing process are all possible). '
                'Within-pair order was randomised, so the shift adds noise more than bias, but pairs split across it are excluded here.'}

    form['note'] = 'Surface form only. Distinct-n falls with length, so compare it alongside median words.'
    out['E4_surface_form'] = form
    return out, ok, set(affected)


# ---------- figures ----------

COLOURS = {'A': '#2a78d6', 'B': '#eb6834'}  # validated categorical slots 1 and 2
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e4e3df'


def style(ax, title, ylabel=None, xlabel=None):
    ax.set_title(title, loc='left', fontsize=11, color=INK)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis='y', color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    if ylabel:
        ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
    if xlabel:
        ax.set_xlabel(xlabel, color=MUTED, fontsize=9)


def figures(rows, ok, affected, result, folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    # folder=None draws into the caller (the notebook executor captures plt.show)
    if folder is not None:
        folder.mkdir(parents=True, exist_ok=True)
    saved = []

    def save(fig, name):
        fig.tight_layout()
        if folder is None:
            plt.show()
        else:
            fig.savefig(folder / name, dpi=150, facecolor='#fcfcfb')
            plt.close(fig)
        saved.append(name)

    # F1 run timeline: shows the standby gap in the order things actually ran
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ordered = sorted(rows, key=lambda r: r['started_utc'])
    for c in 'AB':
        pts = [(i, r['elapsed_seconds']) for i, r in enumerate(ordered) if r['condition'] == c]
        ax.scatter(*zip(*pts), s=22, color=COLOURS[c], label=f'Condition {c}', edgecolor='#fcfcfb', linewidth=1, zorder=3)
    for i, r in enumerate(ordered):
        if r['scenario_id'] in affected and r['elapsed_seconds'] > 100:
            ax.annotate('overlaps Modern Standby\n(host asleep, not slow model)', (i, r['elapsed_seconds']),
                        xytext=(-170, -10), textcoords='offset points', fontsize=8, color=MUTED,
                        arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.8))
    ax.set_yscale('log')
    style(ax, 'F1. Every generation in run order (log scale)', 'elapsed seconds', 'generation order')
    ax.legend(frameon=False, fontsize=9)
    save(fig, 'F1_run_timeline.png')

    # F2 paired differences: the one pair that drives the mean is visible at a glance
    diffs = sorted(((p['B']['elapsed_seconds'] - p['A']['elapsed_seconds'], s) for s, p in ok.items()))
    fig, ax = plt.subplots(figsize=(9, 3.8))
    xs = range(len(diffs))
    ax.axhline(0, color=MUTED, lw=1)
    ax.scatter(xs, [d for d, _ in diffs], s=20, color=[MUTED if s in affected else COLOURS['B'] for _, s in diffs], zorder=3)
    ax.set_yscale('symlog', linthresh=10)
    e1 = result['E1_latency_sensitivity']
    txt = (f"mean, all pairs: {e1['all_pairs']['mean']:.1f} s  CI {e1['all_pairs']['mean_bootstrap95'][0]:.1f} to {e1['all_pairs']['mean_bootstrap95'][1]:.1f}\n"
           f"mean, standby excluded: {e1['excluding_standby']['mean']:.1f} s  CI {e1['excluding_standby']['mean_bootstrap95'][0]:.1f} to {e1['excluding_standby']['mean_bootstrap95'][1]:.1f}\n"
           f"median, standby excluded: {e1['excluding_standby']['median']:.1f} s   sign test p = {e1['excluding_standby']['sign_test_p']:.3g}")
    ax.text(0.01, 0.97, txt, transform=ax.transAxes, va='top', fontsize=8.5, color=INK)
    style(ax, 'F2. Paired latency difference B − A per scenario (grey = standby pair)', 'seconds (symlog)', 'scenarios sorted by difference')
    save(fig, 'F2_paired_latency.png')

    # F3 length explains latency: elapsed vs output tokens with fits
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    clean = [r for s, p in ok.items() if s not in affected for r in p.values()]
    for c in 'AB':
        sub = [r for r in clean if r['condition'] == c]
        ax.scatter([r['output_tokens'] for r in sub], [r['elapsed_seconds'] for r in sub], s=22, color=COLOURS[c],
                   edgecolor='#fcfcfb', linewidth=1, label=f'Condition {c}', zorder=3)
        fit = result['E2_length_control']['fit_elapsed_on_output_tokens'][c]
        if fit:
            lo, hi = min(r['output_tokens'] for r in sub), max(r['output_tokens'] for r in sub)
            ttft = statistics.median(r['ttft_seconds'] for r in sub)
            ax.plot([lo, hi], [ttft + fit['intercept_seconds'] + fit['seconds_per_output_token'] * x for x in (lo, hi)],
                    color=COLOURS[c], lw=2)
    ax.axvline(110, color=MUTED, lw=1, ls='--')
    ax.text(108, 4, '110-token cap', ha='right', va='bottom', fontsize=8, color=MUTED)
    style(ax, 'F3. Latency follows reply length (standby pair removed)', 'elapsed seconds', 'output tokens')
    ax.legend(frameon=False, fontsize=9, loc='upper left')
    save(fig, 'F3_latency_vs_length.png')

    # F4 compliance by category with Wilson intervals
    comp = result['E3_compliance']['by_category']
    cats = list(comp)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ax, (metric, label) in zip(axes, [('token_limit', 'F4a. Replies that hit the 110-token cap'), ('over_word_limit', f'F4b. Replies over {WORD_LIMIT} words')]):
        for k, c in enumerate('AB'):
            x = [i + (k - 0.5) * 0.36 for i in range(len(cats))]
            rate = [comp[cat][c][f'{metric}_rate'] for cat in cats]
            ci = [comp[cat][c][f'{metric}_wilson95'] for cat in cats]
            ax.bar(x, rate, width=0.34, color=COLOURS[c], label=f'Condition {c}', edgecolor='#fcfcfb', linewidth=2)
            ax.errorbar(x, rate, yerr=[[r - lo for r, (lo, hi) in zip(rate, ci)], [hi - r for r, (lo, hi) in zip(rate, ci)]],
                        fmt='none', ecolor=INK, elinewidth=1, capsize=2)
        ax.set_xticks(range(len(cats)))
        ax.set_xticklabels([{'everyday_constraints': 'everyday', 'positive_and_preferences': 'positive',
                            'relationships': 'relation-\nships', 'uncertainty': 'uncer-\ntainty'}.get(c, c) for c in cats], fontsize=8)
        ax.set_ylim(0, 1)
        style(ax, label, 'share of 10 scenarios (95% Wilson)' if metric == 'token_limit' else None)
    axes[0].legend(frameon=False, fontsize=9)
    save(fig, 'F4_compliance_by_category.png')

    # F5 reply length distribution
    fig, ax = plt.subplots(figsize=(7, 3.6))
    words = {c: [len(r['response'].split()) for r in rows if r['condition'] == c and r['status'] == 'generated'] for c in 'AB'}
    bins = range(0, max(max(v) for v in words.values()) + 10, 5)
    for c in 'AB':
        ax.hist(words[c], bins=bins, color=COLOURS[c], alpha=0.75, label=f'Condition {c} (median {statistics.median(words[c]):.0f})',
                edgecolor='#fcfcfb', linewidth=1)
    ax.axvline(WORD_LIMIT, color=MUTED, ls='--', lw=1)
    ax.text(WORD_LIMIT + 1, ax.get_ylim()[1] * 0.92, f'B asked for ≤{WORD_LIMIT} words', fontsize=8, color=MUTED)
    style(ax, 'F5. Reply length in words', 'replies', 'words')
    ax.legend(frameon=False, fontsize=9, loc='upper left')
    save(fig, 'F5_length_distribution.png')

    # F6 stock phrases: form, not quality
    form = result['E4_surface_form']
    keys = list(STOCK_PHRASES)
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    for k, c in enumerate('AB'):
        y = [i + (k - 0.5) * 0.36 for i in range(len(keys))]
        ax.barh(y, [form[c]['stock_phrase_rate'][key] for key in keys], height=0.34, color=COLOURS[c],
                label=f'Condition {c}', edgecolor='#fcfcfb', linewidth=2)
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels([key.replace('_', ' ') for key in keys], fontsize=9)
    ax.set_xlim(0, 1)
    style(ax, 'F6. Share of replies containing a stock phrase (surface form only)', None, 'share of replies')
    ax.grid(axis='x', color=GRID, linewidth=0.8)
    ax.grid(axis='y', visible=False)
    ax.legend(frameon=False, fontsize=9, loc='lower right')
    save(fig, 'F6_stock_phrases.png')
    # F7 host speed over wall-clock time, standby shaded
    from datetime import datetime as dt
    fig, axes = plt.subplots(2, 1, figsize=(9, 4.8), sharex=True)
    window = [dt.fromisoformat(w) for w in result['standby_window_utc']]
    for c in 'AB':
        sub = [r for r in rows if r['condition'] == c and r.get('decode_tokens_per_second')]
        t = [parse(r['started_utc']) for r in sub]
        axes[0].scatter(t, [r['decode_tokens_per_second'] for r in sub], s=16, color=COLOURS[c], label=f'Condition {c}', zorder=3)
        axes[1].scatter(t, [r['process_cpu_seconds'] / r['elapsed_seconds'] for r in sub], s=16, color=COLOURS[c], zorder=3)
    for ax in axes:
        ax.axvspan(*window, color=GRID, zorder=0)
    axes[0].axhline(REGIME_SPLIT, color=MUTED, ls='--', lw=1)
    axes[0].text(window[0], axes[0].get_ylim()[1] * 0.92, ' Modern Standby', fontsize=8, color=MUTED, va='top')
    style(axes[0], 'F7. Host speed during the run: decode rate halves around 08:16 UTC', 'decode tok/s')
    style(axes[1], '', 'CPU cores busy', 'start time (UTC)')
    axes[0].legend(frameon=False, fontsize=9, loc='upper right')
    import matplotlib.dates as mdates
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    save(fig, 'F7_host_regimes.png')
    return saved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=ROOT / 'results/analysis/robustness-v1')
    args = ap.parse_args()
    if (args.out / 'robustness.json').exists():
        raise SystemExit(f'{args.out} already has results; choose a new --out to keep the old version')
    rows = load()
    result, ok, affected = analyse(rows, standby_window())
    result['figures'] = figures(rows, ok, affected, result, args.out / 'figures')
    with (args.out / 'robustness.json').open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    e1 = result['E1_latency_sensitivity']
    for k in ('all_pairs', 'excluding_standby'):
        s = e1[k]
        print(f"{k:18s} mean {s['mean']:7.2f} {s['mean_bootstrap95']}  median {s['median']:6.2f}  HL {s['hodges_lehmann']:6.2f}  sign p {s['sign_test_p']:.3g}")
    print('per-token', json.dumps(result['E2_length_control']['seconds_per_output_token_B_minus_A'], indent=1)[:400])
    print('mcnemar token limit', result['E3_compliance']['token_limit_mcnemar'])
    print('regimes', {k: v for k, v in result['E5_host_regimes'].items() if k in ('counts', 'median_decode_tps')})
    print('regime-matched latency', {k: result['E5_host_regimes']['regime_matched_latency_B_minus_A'][k] for k in ('n_pairs', 'median', 'median_bootstrap95', 'sign_test_p')})
    print('figures:', ', '.join(result['figures']))


if __name__ == '__main__':
    main()

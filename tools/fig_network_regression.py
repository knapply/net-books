"""Figures for the chapter on network regression and autocorrelation.

Standard library only. Everything drawn is computed from books/sna/data/krackhardt:
the double semi-partialling reference distributions use the same idea as the chapter's code
(relabel the people in what is left of one predictor, refit, keep the t statistic and the
coefficient), with a fixed seed.
"""
import csv
import math
import random
from pathlib import Path

from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data" / "krackhardt"
TERMS = ["friendship", "reports_to", "same_dept", "level_gap", "age_gap", "tenure_gap"]


def load():
    nodes = list(csv.DictReader(open(DATA / "nodes.csv", newline="")))
    n = len(nodes)
    col = lambda k: [float(r[k]) for r in nodes]  # noqa: E731
    age, tenure, level, dept = col("age"), col("tenure"), col("level"), col("department")
    rel = {k: [[0.0] * n for _ in range(n)] for k in ("advice", "friendship", "reports_to")}
    for r in csv.DictReader(open(DATA / "edges.csv", newline="")):
        rel[r["relation"]][int(r["from"]) - 1][int(r["to"]) - 1] = 1.0
    mats = {
        "friendship": rel["friendship"], "reports_to": rel["reports_to"],
        "same_dept": [[1.0 if dept[i] == dept[j] else 0.0 for j in range(n)] for i in range(n)],
        "level_gap": [[level[i] - level[j] for j in range(n)] for i in range(n)],
        "age_gap": [[abs(age[i] - age[j]) for j in range(n)] for i in range(n)],
        "tenure_gap": [[abs(tenure[i] - tenure[j]) for j in range(n)] for i in range(n)],
    }
    return n, rel["advice"], mats


def solve_inverse(a):
    """Inverse of a small square matrix by Gauss-Jordan elimination."""
    k = len(a)
    m = [row[:] + [1.0 if i == j else 0.0 for j in range(k)] for i, row in enumerate(a)]
    for c in range(k):
        piv = max(range(c, k), key=lambda r: abs(m[r][c]))
        m[c], m[piv] = m[piv], m[c]
        pv = m[c][c]
        m[c] = [v / pv for v in m[c]]
        for r in range(k):
            if r != c:
                f = m[r][c]
                m[r] = [v - f * w for v, w in zip(m[r], m[c])]
    return [row[k:] for row in m]


def dsp(reps=1000, seed=11):
    """Observed and double-semi-partialled reference draws of t and of the coefficient, per predictor."""
    n, advice, mats = load()
    cells = [(i, j) for i in range(n) for j in range(n) if i != j]
    big_n = len(cells)
    y = [advice[i][j] for i, j in cells]
    cols = [[1.0] * big_n] + [[mats[t][i][j] for i, j in cells] for t in TERMS]
    p_cols = len(cols)
    rng = random.Random(seed)
    perms = [rng.sample(range(n), n) for _ in range(reps)]
    dot = lambda a, b: sum(u * v for u, v in zip(a, b))  # noqa: E731
    out = {}
    for k in range(1, p_cols):
        others = [c for q, c in enumerate(cols) if q != k]
        ginv = solve_inverse([[dot(a, b) for b in others] for a in others])
        oty = [dot(c, y) for c in others]
        h = [dot(row, oty) for row in ginv]
        yy = dot(y, y) - dot(oty, h)

        def stats(x):
            v = [dot(c, x) for c in others]
            xy, xx = dot(x, y), dot(x, x)
            gv = [dot(row, v) for row in ginv]
            num, den = xy - dot(v, h), xx - dot(v, gv)
            b = num / den
            s2 = (yy - b * num) / (big_n - p_cols)
            return b, b / math.sqrt(s2 / den), math.sqrt(s2 / den)

        x = cols[k]
        coef = [dot(row, [dot(c, x) for c in others]) for row in ginv]
        rest = [xi - sum(c[idx] * w for c, w in zip(others, coef)) for idx, xi in enumerate(x)]
        grid = [[0.0] * n for _ in range(n)]
        for (i, j), v in zip(cells, rest):
            grid[i][j] = v
        b_obs, t_obs, se_obs = stats(x)
        draws = [stats([grid[p[i]][p[j]] for i, j in cells])[:2] for p in perms]
        sd = lambda v: math.sqrt(sum((a - sum(v) / len(v)) ** 2 for a in v) / (len(v) - 1))  # noqa: E731
        out[TERMS[k - 1]] = dict(b=b_obs, t=t_obs, se=se_obs, sx=sd(x), draws=draws)
    return out, sd(y)


def quantile(v, q):
    s = sorted(v)
    pos = q * (len(s) - 1)
    lo = int(math.floor(pos))
    return s[lo] + (s[min(lo + 1, len(s) - 1)] - s[lo]) * (pos - lo)


def dependence():
    n_show = 7
    focal = (2, 4)  # row Cleo, column Eli
    names = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus"]
    c = Canvas(900, 440, "Dyads that share a person are not independent",
               "A seven by seven grid of ordered pairs with one pair marked and every pair that shares a person with it shaded.")
    cell, x0, y0 = 44, 90, 70
    share = 0
    for i in range(n_show):
        c.text(x0 + i * cell + cell / 2, y0 - 10, names[i][:3], size=12, fill=MUTED)
        c.text(x0 - 10, y0 + i * cell + cell / 2 + 4, names[i], size=12.5, anchor="end", fill=MUTED)
        for j in range(n_show):
            x, y = x0 + j * cell, y0 + i * cell
            if i == j:
                c.rect(x, y, cell, cell, fill="#f3f4f6", stroke=PAPER, sw=2)
            elif (i, j) == focal:
                c.rect(x, y, cell, cell, fill=BLUE, stroke=PAPER, sw=2)
            elif {i, j} & set(focal):
                share += 1
                c.rect(x, y, cell, cell, fill=ORANGE, stroke=PAPER, sw=2)
            else:
                c.rect(x, y, cell, cell, fill=PAPER, stroke=FAINT, sw=1.2)
    others = n_show * (n_show - 1) - 1
    c.text(x0 + n_show * cell / 2, 28, "Row: who names. Column: who is named.", size=13, weight="700")
    # the same count for 21 managers, by brute force
    m = 21
    pairs = [(i, j) for i in range(m) for j in range(m) if i != j]
    f = pairs[0]
    share21 = sum(1 for p in pairs if p != f and ({p[0], p[1]} & {f[0], f[1]}))
    c.lines(470, 110, [
        "The blue square is one ordered pair: Cleo names Eli.",
        f"The {share} orange squares share Cleo or Eli with it:",
        "every pair in Cleo's row or column, and in Eli's.",
        "",
        f"With {n_show} people, {share} of the other {others} pairs",
        "are tied to the blue one through a person.",
        "",
        f"With the 21 Krackhardt managers it is {share21} of the",
        f"other {len(pairs) - 1} pairs, for every single pair.",
        "",
        "A test that counts each square as a separate,",
        "independent observation counts the same few",
        "people's habits over and over.",
    ], size=14.5, fill=INK)
    meta = dict(chapter=20,
                caption="Why pairs are not independent observations. One ordered pair (blue) and every pair that shares a person with it (orange), among seven people. Each person appears in many pairs, so what is true of that person is true of all of them at once.",
                alt=f"A seven by seven grid with people in rows and columns. The cell in row Cleo, column Eli is blue. {share} other off-diagonal cells are orange: all those in the rows and columns of Cleo and of Eli. The remaining {others - share} off-diagonal cells are white. Text beside the grid says that among 21 managers each pair shares a person with {share21} of the other {len(pairs) - 1} pairs.",
                data={"people": n_show, "pairs_sharing_a_person": share, "other_pairs": others,
                      "managers": m, "managers_pairs_sharing": share21, "managers_other_pairs": len(pairs) - 1})
    return c, meta


def null_distribution():
    res, _ = dsp()
    r = res["level_gap"]
    ts = [d[1] for d in r["draws"]]
    lim = math.ceil(max(max(abs(t) for t in ts), abs(r["t"])) + 0.5)
    c = Canvas(900, 400, "The permutation distribution of a t statistic",
               "A histogram of reference t statistics for the level gap after relabeling managers, with the observed t and the ordinary test cutoffs marked.")
    left, right, top, bottom = 70, 850, 50, 320
    bw = 0.5
    nb = int(2 * lim / bw)
    counts = [0] * nb
    for t in ts:
        counts[min(nb - 1, int((t + lim) / bw))] += 1
    peak = max(counts)
    sx = lambda t: left + (t + lim) / (2 * lim) * (right - left)  # noqa: E731
    obs = r["t"]
    for k, cnt in enumerate(counts):
        lo = -lim + k * bw
        h = cnt / peak * (bottom - top - 20)
        extreme = abs(lo + bw / 2) >= abs(obs)
        c.rect(sx(lo) + 1, bottom - h, sx(lo + bw) - sx(lo) - 2, h,
               fill=ORANGE if extreme else "#cbd5e1", stroke=PAPER, sw=0.5)
    c.add(f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}" stroke-width="1.5"/>')
    for t in range(-int(lim), int(lim) + 1, 2):
        c.text(sx(t), bottom + 20, str(t), size=12, fill=MUTED)
    c.text((left + right) / 2, bottom + 44, "t statistic of the level gap after relabeling the managers", size=13, fill=MUTED)
    for t in (-1.966, 1.966):
        c.add(f'<line x1="{sx(t):.1f}" y1="{top + 40}" x2="{sx(t):.1f}" y2="{bottom}" stroke="{BLUE}" stroke-width="2" stroke-dasharray="6 4"/>')
    c.text(sx(-1.966) - 8, top + 56, "ordinary test cutoffs, plus and minus 1.97", size=12, anchor="end", fill=BLUE)
    c.add(f'<line x1="{sx(obs):.1f}" y1="{top}" x2="{sx(obs):.1f}" y2="{bottom}" stroke="{INK}" stroke-width="2.5"/>')
    c.text(sx(obs) + 6, top + 12, f"observed t = {obs:.2f}", size=13, weight="700", anchor="start")
    share = sum(1 for t in ts if abs(t) >= abs(obs)) / len(ts)
    cut = quantile([abs(t) for t in ts], 0.95)
    c.text(left, 28, f"{len(ts)} relabelings. Orange: as extreme as the observed t ({share:.2f} of them).", size=13.5, weight="600", anchor="start")
    meta = dict(chapter=20,
                caption="The reference distribution of the level-gap t statistic for the advice network, from 1,000 relabelings of the managers by double semi-partialling. The dashed lines are the cutoffs an ordinary test would use. The observed value sits well outside them and well inside the relabeled distribution.",
                alt=f"A histogram of 1,000 relabeled t statistics for the level gap, centered near zero and spread from about {min(ts):.1f} to {max(ts):.1f}. Dashed vertical lines mark plus and minus 1.97, the ordinary test cutoffs. A solid line marks the observed t of {obs:.2f}. Bars at least that far from zero are orange and hold {share:.0%} of the draws. The 95th percentile of the absolute relabeled t is {cut:.2f}.",
                data={"reps": len(ts), "observed_t": round(obs, 3), "share_as_extreme": round(share, 3),
                      "abs_t_95th_percentile": round(cut, 3)})
    return c, meta


def coefficient_plot():
    res, sy = dsp()
    c = Canvas(900, 440, "Coefficients with the band that chance alone produces",
               "Six standardized coefficients for advice, each with an ordinary 95 percent interval and the band where relabeled data put the coefficient.")
    left, right, top = 200, 860, 70
    rows = []
    for name in TERMS:
        r = res[name]
        k = r["sx"] / sy
        draws = [b * k for b, _ in r["draws"]]
        rows.append((name, r["b"] * k, 1.966 * r["se"] * k, quantile(draws, 0.025), quantile(draws, 0.975)))
    lo = min(min(r[1] - r[2], r[3]) for r in rows) - 0.03
    hi = max(max(r[1] + r[2], r[4]) for r in rows) + 0.03
    sx = lambda v: left + (v - lo) / (hi - lo) * (right - left)  # noqa: E731
    step = 52
    c.text(left, 30, "Standardized coefficient (change in advice, in standard deviations, per standard deviation of the predictor)", size=12.5, anchor="start", fill=MUTED)
    c.add(f'<line x1="{sx(0):.1f}" y1="{top - 14}" x2="{sx(0):.1f}" y2="{top + step * len(rows) - 14}" stroke="{INK}" stroke-width="1.5"/>')
    outside, naive_sig = [], []
    for i, (name, est, half, blo, bhi) in enumerate(rows):
        y = top + i * step + 10
        c.rect(sx(blo), y - 15, sx(bhi) - sx(blo), 30, fill="#e5e7eb", stroke="none", sw=0)
        c.add(f'<line x1="{sx(est - half):.1f}" y1="{y}" x2="{sx(est + half):.1f}" y2="{y}" stroke="{BLUE}" stroke-width="2.5"/>')
        sig = est < blo or est > bhi
        if est - half > 0 or est + half < 0:
            naive_sig.append(name)
        outside.append(name) if sig else None
        c.node(sx(est), y, "", r=7, fill=BLUE if sig else PAPER, stroke=BLUE, sw=2.5)
        c.text(left - 14, y + 5, name, size=14, anchor="end", weight="600" if sig else "400")
    ax = top + step * len(rows) - 6
    for v in [x / 10 for x in range(int(math.floor(lo * 10)), int(math.ceil(hi * 10)) + 1)]:
        if lo <= v <= hi:
            c.text(sx(v), ax + 20, f"{v:.1f}", size=12, fill=MUTED)
    c.text((left + right) / 2, ax + 42, "Gray band: where 95% of coefficients land when the managers are relabeled.",
           size=12.5, fill=MUTED)
    c.text((left + right) / 2, ax + 62, "Blue line: ordinary 95% interval. Filled dot: outside the band.", size=12.5, fill=MUTED)
    meta = dict(chapter=20,
                caption="Standardized coefficients for advice with the ordinary 95% interval (blue line) and the band that 95% of relabeled coefficients fall in (gray). Where the line is much shorter than the band, the ordinary test is overconfident. A filled dot lies outside the band.",
                alt=f"Six rows, one per predictor, each with a gray band, a blue horizontal line and a dot. The dot is outside the gray band, and filled, only for {', '.join(outside) if outside else 'none of them'}. The blue line, the ordinary interval, stays on one side of zero for {', '.join(naive_sig)}. For all but the filled dots the dot is hollow and inside the band.",
                data={"rows": [{"term": r[0], "standardized_estimate": round(r[1], 3), "ordinary_half_width": round(r[2], 3),
                                "band_low": round(r[3], 3), "band_high": round(r[4], 3)} for r in rows]})
    return c, meta


FIGURES = {"nr-dependence": dependence, "nr-null-distribution": null_distribution,
           "nr-coefficients": coefficient_plot}

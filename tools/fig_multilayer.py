"""Figures for the multiplex and multilayer chapter (chapter 12).

Standard library only. Every number drawn is computed here from the CSV files in
books/sna/data (Krackhardt's managers and Sampson's novices), so the pictures cannot
drift from the data.
"""
import csv
import math
from pathlib import Path

from fig_classic import betweenness, read
from fig_layout import fit, stress_layout
from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, SKY, Canvas

RELATIONS = ("advice", "friendship", "reports_to")
PALE = "#cfe5f3"


def krackhardt():
    """Arc sets (0-based) for the three layers, and the unordered pairs of each."""
    rows = read("krackhardt", "edges.csv")
    arcs = {k: {(int(r["from"]) - 1, int(r["to"]) - 1) for r in rows if r["relation"] == k}
            for k in RELATIONS}
    pairs = {k: sorted({tuple(sorted(a)) for a in v}) for k, v in arcs.items()}
    return arcs, pairs


def average_ranks(values):
    """Rank 1 for the largest value; tied values share the average of their ranks."""
    order = sorted(range(len(values)), key=lambda i: -values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and abs(values[order[j + 1]] - values[order[i]]) < 1e-9:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def layers_side_by_side():
    arcs, pairs = krackhardt()
    n = 21
    union = sorted(set().union(*pairs.values()))
    base = fit(stress_layout(n, union, seed=2), 0, 0, 270, 240)
    c = Canvas(900, 330, "Three layers on one layout",
               "The same 21 managers drawn three times in the same positions, once for each kind of tie.")
    titles = {"advice": "Advice", "friendship": "Friendship", "reports_to": "Reporting lines"}
    colors = {"advice": BLUE, "friendship": ORANGE, "reports_to": INK}
    for k, key in enumerate(RELATIONS):
        x0, y0 = 15 + k * 295, 48
        pos = [(x0 + p[0] + 10, y0 + p[1]) for p in base]
        c.caption(x0 + 140, 28, f"{titles[key]}: {len(pairs[key])} pairs tied")
        for a, b in pairs[key]:
            c.edge(pos[a], pos[b], ra=4, rb=4, width=1.0, color=colors[key], opacity=0.5)
        for i, p in enumerate(pos):
            if i == 16:
                c.node(*p, "", r=7, fill=ORANGE, stroke=INK, sw=1.8)
            elif i == 1:
                c.node(*p, "", r=7, fill=SKY, stroke=INK, sw=1.8)
            else:
                c.node(*p, "", r=4, fill=PAPER, stroke=colors[key], sw=1.6)
        for i, name in ((1, "2"), (16, "17")):
            c.text(pos[i][0] + 10, pos[i][1] - 8, name, size=13, weight="600", anchor="start")
    c.text(450, 318, "A line means a tie in either direction. Manager 2 is filled blue and manager 17 filled orange in every copy.",
           size=13, fill=MUTED)
    meta = dict(chapter=12,
                caption="Krackhardt's 21 managers drawn three times with every manager in the same place each time. Lines show a tie in either direction. Manager 2 (blue) and manager 17 (orange) are marked so you can follow them from layer to layer.",
                alt=f"Three copies of the same 21 dots in the same positions. The left copy, advice, has {len(pairs['advice'])} lines and is dense. The middle copy, friendship, has {len(pairs['friendship'])} lines. The right copy, reporting lines, has {len(pairs['reports_to'])} lines and forms a tree. Two dots are larger and filled in every copy: manager 2 in blue and manager 17 in orange.",
                data={k: [list(e) for e in v] for k, v in pairs.items()})
    return c, meta


def overlap_bars():
    arcs, _ = krackhardt()
    n = 21
    ordered = [(i, j) for i in range(n) for j in range(n) if i != j]
    combos = {}
    for p in ordered:
        key = tuple(p in arcs[k] for k in RELATIONS)
        combos[key] = combos.get(key, 0) + 1
    short = {"advice": "advice", "friendship": "friendship", "reports_to": "reporting"}
    rows = []
    for key in combos:
        if any(key):
            label = " + ".join(short[k] for k, on in zip(RELATIONS, key) if on)
            rows.append((label, sum(key), combos[key]))
    for key in [(a, b, c_) for a in (False, True) for b in (False, True) for c_ in (False, True)]:
        if any(key) and key not in combos:
            rows.append((" + ".join(short[k] for k, on in zip(RELATIONS, key) if on), sum(key), 0))
    rows.sort(key=lambda r: (r[1], -r[2]))
    none = combos[(False, False, False)]
    top = max(r[2] for r in rows)
    c = Canvas(760, 330, "Which layers each tie belongs to",
               "Bars counting the directed pairs of managers by which combination of layers they are tied in.")
    x0, w, y0, step = 230, 420, 52, 34
    shade = {1: SKY, 2: ORANGE, 3: RED}
    c.text(380, 26, "Directed pairs of managers by the layers they are tied in", size=15, weight="600")
    for k, (label, depth, count) in enumerate(rows):
        y = y0 + k * step
        c.text(x0 - 12, y + 20, label, size=13, anchor="end")
        c.rect(x0, y + 4, w * count / top, 24, fill=shade[depth], stroke=INK, sw=1)
        c.text(x0 + w * count / top + 8, y + 21, str(count), size=13, anchor="start")
    c.text(380, y0 + len(rows) * step + 22,
           f"{none} of the 420 possible directed pairs are tied in no layer. Colour shows how many layers: sky 1, orange 2, red 3.",
           size=12.5, fill=MUTED)
    meta = dict(chapter=12,
                caption="Every directed pair of managers sorted by the layers it belongs to. Most tied pairs live in a single layer; only a few are tied in all three.",
                alt="Horizontal bars, one for each combination of layers. " + " ".join(
                    f"{lab}: {cnt}." for lab, _, cnt in rows) + f" A note under the bars says {none} of the 420 directed pairs are tied in no layer.",
                data={"combinations": [[a, b, cnt] for a, b, cnt in rows], "none": none})
    return c, meta


def rank_scatter():
    _, pairs = krackhardt()
    n = 21
    b = {k: betweenness(n, pairs[k]) for k in ("advice", "friendship")}
    ra, rf = average_ranks(b["advice"]), average_ranks(b["friendship"])
    x0, y0, s = 80, 40, 360
    c = Canvas(600, 500, "Central in one layer, not in the other",
               "A scatter of each manager's betweenness rank in the advice layer against the friendship layer.")
    c.text(x0 + s / 2, 24, "Betweenness rank of each manager (1 = most between)", size=15, weight="600")
    c.rect(x0, y0, s, s, fill="none", stroke=INK, sw=1.2)
    c.add(f'<line x1="{x0}" y1="{y0 + s}" x2="{x0 + s}" y2="{y0}" stroke="{FAINT}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    px = lambda r: x0 + (r - 1) / 20 * s
    py = lambda r: y0 + (r - 1) / 20 * s
    for r in (1, 5, 10, 15, 21):
        c.text(px(r), y0 + s + 20, str(int(r)), size=12)
        c.text(x0 - 10, py(r) + 4, str(int(r)), size=12, anchor="end")
    c.text(x0 + s / 2, y0 + s + 44, "rank in the advice layer", size=13, fill=MUTED)
    c.add(f'<text transform="translate({x0 - 46},{y0 + s / 2}) rotate(-90)" font-size="13" text-anchor="middle" fill="{MUTED}">rank in the friendship layer</text>')
    for i in range(n):
        hot = i == 16
        c.node(px(ra[i]), py(rf[i]), "", r=8 if hot else 5, fill=ORANGE if hot else PALE,
               stroke=INK if hot else BLUE, sw=1.8)
    c.text(px(ra[16]) + 14, py(rf[16]) + 5, "17", size=13, weight="600", anchor="start")
    c.text(x0 + s - 6, y0 + s - 8, "dashed line: same rank in both", size=12, fill=MUTED, anchor="end")
    meta = dict(chapter=12,
                caption="Each dot is a manager. The horizontal position is the manager's betweenness rank among the advice ties and the vertical position is the rank among the friendship ties (1 is the most between). Manager 17 (orange) is first in friendship and far down in advice. Tied managers share an average rank.",
                alt=f"A square scatter plot with 21 dots and a dashed diagonal. The other 20 dots are blue. The orange dot for manager 17 sits at the top of the plot, rank {rf[16]:g} on the friendship axis, and at rank {ra[16]:g} of 21 on the advice axis, far from the diagonal.",
                data={"advice_rank": [round(x, 1) for x in ra], "friendship_rank": [round(x, 1) for x in rf]})
    return c, meta


SAMPSON_ORDER = ["liking_t1", "liking_t2", "liking_t3", "esteem", "praise", "positive_influence",
                 "disliking", "disesteem", "blame", "negative_influence"]
SAMPSON_SHORT = ["like 1", "like 2", "like 3", "esteem", "praise", "influ+", "dislike", "disest.", "blame", "influ−"]


def sampson_matrices():
    nodes = sorted(read("sampson", "nodes.csv"), key=lambda r: int(r["number"]))
    ix = {r["name"]: i for i, r in enumerate(nodes)}
    mats = {}
    for r in read("sampson", "edges.csv"):
        key = r["relation"] + (f"_t{r['time']}" if r["relation"] == "liking" else "")
        mats.setdefault(key, [[0] * 18 for _ in range(18)])[ix[r["from"]]][ix[r["to"]]] = 1
    return mats


def pearson(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


def sampson_heat():
    mats = sampson_matrices()
    cells = {k: [mats[k][i][j] for i in range(18) for j in range(18) if i != j] for k in SAMPSON_ORDER}
    corr = [[pearson(cells[a], cells[b]) for b in SAMPSON_ORDER] for a in SAMPSON_ORDER]
    m = len(SAMPSON_ORDER)
    x0, y0, cell = 110, 70, 46
    c = Canvas(640, 600, "How Sampson's relations line up",
               "A grid of correlations between ten relations among 18 novices.")
    c.text(320, 26, "Correlation between layers (Sampson's novices)", size=15, weight="600")
    for i in range(m):
        c.text(x0 - 8, y0 + i * cell + cell / 2 + 4, SAMPSON_SHORT[i], size=12, anchor="end")
        c.text(x0 + i * cell + cell / 2, y0 - 8, SAMPSON_SHORT[i], size=12)
        for j in range(m):
            v = corr[i][j]
            col = BLUE if v >= 0 else RED
            alpha = min(1.0, abs(v)) if i != j else 1.0
            c.add(f'<rect x="{x0 + j * cell}" y="{y0 + i * cell}" width="{cell}" height="{cell}" fill="{col}" '
                  f'fill-opacity="{alpha:.2f}" stroke="{PAPER}" stroke-width="1.5"/>')
            dark = alpha > 0.55
            c.text(x0 + j * cell + cell / 2, y0 + i * cell + cell / 2 + 4, f"{v:.2f}" if i != j else "1",
                   size=11, fill=PAPER if dark else INK)
    c.text(320, y0 + m * cell + 28, "Blue: ties go together. Red: ties tend to be different pairs. Pale: almost unrelated.",
           size=12.5, fill=MUTED)
    c.text(320, y0 + m * cell + 48, "Correlation over all 306 ordered pairs, each tie coded 1 and no tie 0.", size=12.5, fill=MUTED)
    ll = corr[SAMPSON_ORDER.index("liking_t3")][SAMPSON_ORDER.index("esteem")]
    block = lambda idx: [corr[a][b] for a in idx for b in idx if a < b]
    lk, po, ng = block([0, 1, 2]), block([3, 4, 5]), block([6, 7, 8, 9])
    cross = [corr[a][b] for a in (3, 4, 5) for b in (6, 7, 8, 9)]
    meta = dict(chapter=12,
                caption="Correlations between ten layers among Sampson's 18 novices: liking at three times, esteem, praise and positive influence, then their negative counterparts. The positive relations other than liking go together, the negative ones go together, and liking stands apart from both.",
                alt=f"A ten by ten grid of numbers shaded blue for positive and red for negative correlations. The three liking rows form a blue block with values from {min(lk):.2f} to {max(lk):.2f}. Esteem, praise and positive influence form a second blue block from {min(po):.2f} to {max(po):.2f}. The four negative relations form a third blue block from {min(ng):.2f} to {max(ng):.2f}. Between the second and third blocks every value is red, from {min(cross):.2f} to {max(cross):.2f}. Liking at time 3 against esteem is only {ll:.2f}.",
                data={"order": SAMPSON_ORDER, "corr": [[round(v, 3) for v in row] for row in corr]})
    return c, meta


def overlap_ceiling():
    """For seven pairs of layers: the Jaccard index, its ceiling and its value if ties were scattered independently."""
    arcs, _ = krackhardt()
    mats = sampson_matrices()
    sets = {k: arcs[k] for k in RELATIONS}
    sets.update({k: {(i, j) for i in range(18) for j in range(18) if mats[k][i][j]} for k in mats})
    pairs = [("advice", "friendship", 21), ("advice", "reports_to", 21), ("friendship", "reports_to", 21),
             ("liking_t1", "liking_t2", 18), ("liking_t2", "liking_t3", 18), ("liking_t3", "esteem", 18),
             ("liking_t3", "disliking", 18)]
    rows = []
    for a, b, n in pairs:
        big_n = n * (n - 1)
        ma, mb, both = len(sets[a]), len(sets[b]), len(sets[a] & sets[b])
        expected = ma * mb / big_n
        rows.append((f"{a} & {b}".replace("_", " "), both / (ma + mb - both), min(ma, mb) / max(ma, mb),
                     expected / (ma + mb - expected)))
    c = Canvas(780, 360, "Jaccard index against its ceiling and against luck",
               "For seven pairs of layers, the observed Jaccard index, the highest it could be for those layer sizes, and the value luck would give.")
    x0, w, y0, step = 250, 460, 62, 36
    c.text(390, 26, "Observed Jaccard index, its ceiling and its value by luck", size=15, weight="600")
    for k, (label, jac, ceiling, chance) in enumerate(rows):
        y = y0 + k * step
        c.text(x0 - 12, y + 19, label, size=12.5, anchor="end")
        c.rect(x0, y + 4, w * ceiling, 22, fill="none", stroke=MUTED, sw=1, dash="4 3")
        c.rect(x0, y + 8, w * jac, 14, fill=BLUE, stroke=INK, sw=1)
        c.add(f'<line x1="{x0 + w * chance:.1f}" y1="{y}" x2="{x0 + w * chance:.1f}" y2="{y + 30}" stroke="{ORANGE}" stroke-width="3"/>')
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        c.text(x0 + w * v, y0 + len(rows) * step + 14, f"{v:g}", size=12)
    c.text(390, y0 + len(rows) * step + 38,
           "Blue bar: observed. Dashed box: ceiling for those layer sizes. Orange tick: expected if ties were scattered independently.",
           size=12.5, fill=MUTED)
    f = lambda v: f"{v:.2f}"
    desc = " ".join(f"{r[0]}: observed {f(r[1])}, ceiling {f(r[2])}, by luck {f(r[3])}." for r in rows)
    meta = dict(chapter=15,
                caption="Seven pairs of layers, three from Krackhardt's managers and four from Sampson's novices. The blue bar is the Jaccard index, the dashed box is the highest it could be for those layer sizes and the orange tick is the value if ties were scattered independently. Advice and reporting sit almost at their ceiling; liking at time 3 with esteem or disliking sits close to the orange tick.",
                alt="Seven rows, each with a blue bar, a dashed box and an orange tick. " + desc,
                data={"rows": [[r[0], round(r[1], 3), round(r[2], 3), round(r[3], 3)] for r in rows]})
    return c, meta


FIGURES = {
    "multilayer-layers": layers_side_by_side,
    "multilayer-overlap": overlap_bars,
    "multilayer-ranks": rank_scatter,
    "multilayer-sampson": sampson_heat,
    "multilayer-ceiling": overlap_ceiling,
}

"""Figures that introduce the bundled classic networks and teach a measure on them.

Standard library only. Every number drawn is computed here from the CSV files in
books/sna/data, so the pictures cannot drift from the data.
"""
import csv
import math
from pathlib import Path

from fig_layout import distances, fit, stress_layout
from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"
GRAY = "#9ca3af"
PALE = "#cfe5f3"


def read(name, file):
    with open(DATA / name / file, newline="") as f:
        return list(csv.DictReader(f))


def undirected(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    return adj


def betweenness(n, edges):
    """Brandes, unweighted, undirected; each pair counted once."""
    adj = undirected(n, edges)
    cb = [0.0] * n
    for s in range(n):
        stack, pred = [], [[] for _ in range(n)]
        sigma, dist = [0] * n, [-1] * n
        sigma[s], dist[s] = 1, 0
        queue = [s]
        for v in queue:
            stack.append(v)
            for w in adj[v]:
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)
        delta = [0.0] * n
        while stack:
            w = stack.pop()
            for v in pred[w]:
                delta[v] += sigma[v] / sigma[w] * (1 + delta[w])
            if w != s:
                cb[w] += delta[w]
    return [x / 2 for x in cb]


def florentine():
    rows = read("florentine", "edges.csv")
    names = []
    for r in rows:
        for k in ("source", "target"):
            if r[k] not in names:
                names.append(r[k])
    ix = {m: i for i, m in enumerate(names)}
    return names, [(ix[r["source"]], ix[r["target"]]) for r in rows]


def _draw(c, pos, edges, size, fill, labels, r_lo=6, r_hi=20, edge_w=1.6, font=11,
          side=()):
    for a, b in edges:
        c.edge(pos[a], pos[b], ra=6, rb=6, width=edge_w, color=GRAY)
    for i, p in enumerate(pos):
        r = r_lo + (r_hi - r_lo) * size[i]
        c.node(*p, "", r=r, fill=fill[i][0], stroke=fill[i][1], sw=2)
    for i, p in enumerate(pos):
        r = r_lo + (r_hi - r_lo) * size[i]
        if labels[i].startswith("Albizzi"):
            c.text(p[0] - 6, p[1] - r - 6, labels[i], size=font, fill=INK, anchor="end")
        elif labels[i] in side or labels[i].split(" ")[0] in side:
            c.text(p[0] - r - 6, p[1] + 4, labels[i], size=font, fill=INK, anchor="end")
        else:
            c.text(p[0], p[1] + r + font + 2, labels[i], size=font, fill=INK)


def florentine_intro():
    names, edges = florentine()
    n = len(names)
    pos = fit(stress_layout(n, edges, seed=4), 50, 50, 640, 300)
    c = Canvas(740, 400, "The Florentine families",
               "Fifteen families as dots joined by marriage ties. The Medici sit in the middle of the network.")
    med = names.index("Medici")
    _draw(c, pos, edges, [0.3] * n,
          [(ORANGE, ORANGE) if i == med else (PALE, BLUE) for i in range(n)], names)
    c.text(370, 28, "Fifteen families, twenty marriages (Florence, about 1430)", size=15, weight="600")
    meta = dict(chapter=6,
                caption="Fifteen leading families of Florence around 1430. A line means a marriage joined the two families. The Medici are in orange.",
                alt="A network of fifteen labeled dots joined by twenty lines. The Medici, drawn in orange, sit in the middle with six lines. A few families such as Pazzi and Salviati hang off the edge with only one or two lines.",
                data={"names": names, "edges": [list(e) for e in edges]})
    return c, meta


def florentine_between():
    names, edges = florentine()
    n = len(names)
    b = betweenness(n, edges)
    hi = max(b)
    pos = fit(stress_layout(n, edges, seed=4), 50, 50, 640, 300)
    c = Canvas(740, 400, "Who the routes run through",
               "The Florentine marriage network with each family drawn as large as the number of shortest routes that pass through it.")
    top = sorted(range(n), key=lambda i: -b[i])[:4]
    fill = [(ORANGE, ORANGE) if i == top[0] else ("#fbd9b5", ORANGE) if i in top else (PALE, BLUE)
            for i in range(n)]
    labels = [f"{names[i]} {b[i]:.1f}" if i in top else names[i] for i in range(n)]
    _draw(c, pos, edges, [v / hi for v in b], fill, labels, r_lo=4, r_hi=26,
          side=("Albizzi", "Medici", "Acciaiuoli"))
    c.text(370, 28, "Bigger dot = more shortest routes run through that family", size=15, weight="600")
    meta = dict(chapter=6,
                caption="The same marriage network with each family sized by betweenness. The Medici are far larger than anyone else: about half of all shortest routes between families go through them.",
                alt="The fifteen-family marriage network again, now with dots of different sizes. The Medici dot in the middle is by far the largest and labeled 47.5. Guadagni, Albizzi and Salviati are medium sized and labeled. The families at the edge are tiny.",
                data={"betweenness": {names[i]: round(b[i], 2) for i in range(n)}})
    return c, meta


def krackhardt_layers():
    nodes = read("krackhardt", "nodes.csv")
    n = len(nodes)
    level = [int(r["level"]) for r in nodes]
    layers = {k: [(int(r["from"]) - 1, int(r["to"]) - 1) for r in read("krackhardt", "edges.csv")
                  if r["relation"] == k] for k in ("advice", "friendship", "reports_to")}
    allp = sorted({tuple(sorted(e)) for es in layers.values() for e in es})
    base = fit(stress_layout(n, allp, seed=2), 0, 0, 270, 250)
    c = Canvas(900, 340, "Three kinds of ties among 21 managers",
               "Three copies of the same 21 managers, showing who goes to whom for advice, who is friends with whom, and who reports to whom.")
    titles = {"advice": "Advice: who asks whom", "friendship": "Friendship", "reports_to": "Reporting lines"}
    colors = {"advice": BLUE, "friendship": ORANGE, "reports_to": INK}
    for k, key in enumerate(("advice", "friendship", "reports_to")):
        x0, y0 = 15 + k * 295, 50
        pos = [(x0 + p[0] + 10, y0 + p[1]) for p in base]
        indeg = [0] * n
        for a, b in layers[key]:
            indeg[b] += 1
        hi = max(indeg) or 1
        c.caption(x0 + 140, 28, f"{titles[key]} ({len(layers[key])})")
        for a, b in layers[key]:
            c.edge(pos[a], pos[b], ra=3 + 8 * indeg[a] / hi, rb=3 + 8 * indeg[b] / hi, directed=True,
                   width=1.0, color=colors[key], opacity=0.55)
        for i, p in enumerate(pos):
            c.node(*p, "", r=3 + 8 * indeg[i] / hi, fill=colors[key] if level[i] == 1 else PAPER,
                   stroke=colors[key], sw=1.8)
        top = max(range(n), key=lambda i: indeg[i])
        c.text(x0 + 140, 316, f"most chosen: manager {top + 1} ({indeg[top]})", size=13, fill=MUTED)
    meta = dict(chapter=6,
                caption="Krackhardt's 21 managers, three kinds of ties. Dot size shows how many people name that manager. The filled dot is the CEO (level 1).",
                alt="Three copies of the same 21 dots. The left copy has many arrows, the middle fewer, the right is a tree of reporting lines with the filled CEO dot at the top. Manager 2 is the largest dot in the advice and friendship copies; manager 14 is the largest in the reporting copy.",
                data={k: [list(e) for e in v] for k, v in layers.items()})
    return c, meta


def closeness_from_jo():
    from make_figures import KITE_EDGES, KITE_NAMES
    n = len(KITE_NAMES)
    d = distances(n, KITE_EDGES)
    jo = 9
    pos = fit(stress_layout(n, KITE_EDGES, seed=3), 20, 50, 560, 230)
    shade = ["#fff", "#f6d8b8", "#f0b97f", "#e99a46", "#d97a14"]
    c = Canvas(900, 330, "How far Jo is from everyone",
               "The ten-person network with each person labeled by how many steps they are from Jo, and shaded darker the farther they are.")
    for a, b in KITE_EDGES:
        c.edge(pos[a], pos[b], ra=14, rb=14, width=1.6, color=GRAY)
    for i, p in enumerate(pos):
        k = d[jo][i]
        c.node(*p, str(k) if i != jo else "Jo", r=16, fill=BLUE if i == jo else shade[min(k, 4)],
               stroke=BLUE if i == jo else ORANGE, label_fill="#fff" if i == jo else INK, size=13)
    for i, p in enumerate(pos):
        if i != jo:
            c.text(p[0], p[1] + 31, KITE_NAMES[i], size=11, fill=MUTED)
    total = sum(d[jo])
    counts = [sum(1 for i in range(n) if d[jo][i] == k) for k in range(1, 6)]
    c.text(630, 80, "Add up the steps from Jo", size=16, weight="700", anchor="start")
    rows = [f"{cnt} {'person' if cnt == 1 else 'people'} at {k} {'step' if k == 1 else 'steps'}"
            for k, cnt in enumerate(counts, 1) if cnt]
    c.lines(630, 112, rows, size=14, anchor="start")
    c.text(630, 112 + 22 * len(rows) + 14, f"Total {total}. Closeness = 9 / {total} = {9 / total:.3f}",
           size=15, weight="700", anchor="start", fill=ORANGE)
    c.text(630, 112 + 22 * len(rows) + 40, "Fewer steps in total", size=13, anchor="start", fill=MUTED)
    c.text(630, 112 + 22 * len(rows) + 58, "means closer to everyone.", size=13, anchor="start", fill=MUTED)
    meta = dict(chapter=6,
                caption="Closeness for Jo, drawn. Each person is labeled with their distance from Jo; darker means farther. The distances sum to 29, so closeness is 9 / 29 = 0.310.",
                alt="The ten-person network. Jo is on the right edge in blue. Each other person shows a number from 1 to 5, the number of steps to Jo, and is shaded darker as the number grows. A side note adds the distances to 29 and gives 9 divided by 29 as 0.310.",
                data={"distances_from_jo": {KITE_NAMES[i]: d[jo][i] for i in range(n)}, "total": total})
    return c, meta


def eigen_rounds():
    # triangle A,B,C with a tail D hanging from C
    names = ["A", "B", "C", "D"]
    edges = [(0, 1), (0, 2), (1, 2), (2, 3)]
    adj = undirected(4, edges)
    rounds = [[1.0] * 4]
    for _ in range(40):
        prev = rounds[-1]
        new = [sum(prev[j] for j in adj[i]) for i in range(4)]
        m = max(new)
        rounds.append([v / m for v in new])
    shown = [0, 1, 2, 40]
    titles = ["Start: everyone 1", "Round 1", "Round 2", "Settled"]
    pos0 = [(60, 30), (60, 130), (130, 80), (200, 80)]
    c = Canvas(960, 250, "Scores that pass along",
               "Four copies of a small network: a triangle with one person hanging off it, with each person's score as the scores are passed around.")
    for k, rd in enumerate(shown):
        x0 = 15 + k * 240
        pos = [(x0 + p[0], 60 + p[1]) for p in pos0]
        v = rounds[rd]
        c.caption(x0 + 120, 28, titles[k])
        for a, b in edges:
            c.edge(pos[a], pos[b], ra=4, rb=4, width=1.6, color=GRAY)
        for i, p in enumerate(pos):
            c.node(*p, names[i], r=8 + 14 * v[i], fill=ORANGE if v[i] == max(v) and rd else PALE, stroke=BLUE if not (v[i] == max(v) and rd) else ORANGE, size=12)
            c.text(p[0], p[1] + 8 + 14 * v[i] + 14, f"{v[i]:.2f}", size=12, fill=MUTED)
    meta = dict(chapter=6,
                caption="Eigenvector centrality as a passing game. Everyone starts at 1; each round, a person's new score is the sum of their neighbors' scores, rescaled so the top is 1. The scores settle: C is the best connected, D the least.",
                alt="Four copies of a triangle A, B, C with a tail D attached to C. Dots grow or shrink with scores written beneath. At the start all are 1. After two rounds C is 1, A and B are 1, D is 0.6. Settled, C is 1.00, A and B 0.85 and D 0.46.",
                data={"rounds": {str(r): [round(x, 3) for x in rounds[r]] for r in shown}})
    return c, meta


# ---------------------------------------------------------------- chapter 18
def _config_draw(degrees, rng):
    """One simple graph with the given degrees: match stubs at random, retry on loops or repeats."""
    while True:
        stubs = [i for i, d in enumerate(degrees) for _ in range(d)]
        rng.shuffle(stubs)
        pairs = [tuple(sorted((stubs[k], stubs[k + 1]))) for k in range(0, len(stubs), 2)]
        if all(a != b for a, b in pairs) and len(set(pairs)) == len(pairs):
            return pairs


def null_medici():
    import random
    names, edges = florentine()
    n = len(names)
    med = names.index("Medici")
    degrees = [sum(1 for e in edges if i in e) for i in range(n)]
    obs = betweenness(n, edges)[med]
    rng = random.Random(1)
    draws = [betweenness(n, _config_draw(degrees, rng))[med] for _ in range(1000)]
    width = 5
    counts = [0] * 14
    for d in draws:
        counts[min(int(d // width), 13)] += 1
    at_least = sum(1 for d in draws if d >= obs - 1e-9)
    c = Canvas(900, 440, "Is the Medici lead more than their marriages give?",
               "A histogram of the Medici's betweenness in 1,000 random marriage networks that keep every family's number of marriages, with the real value marked.")
    x0, y0, w, h = 80, 60, 740, 270
    top = max(counts) * 1.12
    bw = w / 14
    for k, cnt in enumerate(counts):
        right = (k + 1) * width > obs
        col = ORANGE if right else BLUE
        bh = h * cnt / top
        c.rect(x0 + k * bw + 1, y0 + h - bh, bw - 2, bh, fill=col + "66", stroke=col, sw=1.2)
        if not (k * width <= obs < (k + 1) * width):
            c.text(x0 + k * bw + bw / 2, y0 + h - bh - 6, str(cnt), size=11, fill=MUTED)
    ox = x0 + obs / (14 * width) * w
    c.add(f'<line x1="{ox:.1f}" y1="{y0 - 6}" x2="{ox:.1f}" y2="{y0 + h}" stroke="{INK}" stroke-width="2.5"/>')
    c.text(ox - 8, y0 + 8, f"real network {obs:.1f}", size=13, anchor="end", weight="700")
    c.add(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{INK}" stroke-width="1.5"/>')
    for v in range(0, 71, 10):
        c.text(x0 + v / (14 * width) * w, y0 + h + 20, str(v), size=12)
    c.text(x0 + w / 2, y0 + h + 44, "Medici betweenness in a random network with the same degrees (bars 5 wide)", size=13, fill=MUTED)
    c.text(x0, 412, "Orange bars: bins reaching the real value or beyond. Counts are out of 1,000 draws made for this figure.", size=12.5, fill=MUTED, anchor="start")
    mean = sum(draws) / len(draws)
    meta = dict(chapter=18,
                caption="The Medici's betweenness (47.5) against 1,000 random marriage networks in which every family keeps its number of marriages. The real value sits in the upper part of the spread but not beyond it. The draws behind this picture are not the ones in the code, so counts differ slightly.",
                alt=f"A histogram of the Medici's betweenness across 1,000 random networks, rising from near zero to a peak around 40 and falling off by about 65. A black vertical line marks the real value, 47.5. Bars from the 45 to 50 bin onward are orange. In these draws {at_least} of 1,000 reach the real value; the average is {mean:.1f}.",
                data={"observed": round(obs, 2), "mean": round(mean, 2), "at_least_observed": at_least,
                      "bins": [[k * width, (k + 1) * width, counts[k]] for k in range(14)]})
    return c, meta


def tie_drop_stability():
    names, edges = florentine()
    n = len(names)
    med = names.index("Medici")
    rows = []
    for i, (a, b) in enumerate(edges):
        kept = [e for j, e in enumerate(edges) if j != i]
        bt = betweenness(n, kept)
        other = max((v for v in range(n) if v != med), key=lambda v: bt[v])
        rows.append((f"{names[a]} \u2013 {names[b]}", bt[med], bt[other], names[other]))
    rows.sort(key=lambda r: r[1])
    full = betweenness(n, edges)[med]
    c = Canvas(900, 650, "Leaving out one marriage at a time",
               "For each of the twenty marriages, the Medici's betweenness and the best other family's betweenness once that marriage is left out.")
    x0, y0, w = 230, 50, 600
    step = 23
    sx = lambda v: x0 + v / 70 * w
    c.add(f'<line x1="{sx(full):.1f}" y1="{y0 - 10}" x2="{sx(full):.1f}" y2="{y0 + 20 * step}" stroke="{MUTED}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    c.text(sx(full), y0 - 16, f"Medici with all ties {full:.1f}", size=12.5, fill=MUTED)
    for k, (label, m, o, _) in enumerate(rows):
        y = y0 + k * step + 10
        c.text(x0 - 12, y + 4, label, size=12.5, anchor="end")
        c.add(f'<line x1="{sx(min(m, o)):.1f}" y1="{y}" x2="{sx(max(m, o)):.1f}" y2="{y}" stroke="{FAINT}" stroke-width="3"/>')
        c.add(f'<circle cx="{sx(o):.1f}" cy="{y}" r="6" fill="{PALE}" stroke="{BLUE}" stroke-width="2"/>')
        c.add(f'<circle cx="{sx(m):.1f}" cy="{y}" r="6.5" fill="{ORANGE}" stroke="{ORANGE}" stroke-width="2"/>')
    ay = y0 + 20 * step + 8
    c.add(f'<line x1="{x0}" y1="{ay}" x2="{x0 + w}" y2="{ay}" stroke="{INK}" stroke-width="1.5"/>')
    for v in range(0, 71, 10):
        c.text(sx(v), ay + 18, str(v), size=12)
    c.text(x0 + w / 2, ay + 40, "betweenness after leaving out the marriage named on the left", size=13, fill=MUTED)
    c.add(f'<circle cx="{x0}" cy="{ay + 62}" r="6.5" fill="{ORANGE}" stroke="{ORANGE}" stroke-width="2"/>')
    c.text(x0 + 12, ay + 66, "Medici", size=12.5, anchor="start")
    c.add(f'<circle cx="{x0 + 90}" cy="{ay + 62}" r="6" fill="{PALE}" stroke="{BLUE}" stroke-width="2"/>')
    c.text(x0 + 102, ay + 66, "best other family", size=12.5, anchor="start")
    low = rows[0]
    meta = dict(chapter=18,
                caption="Leave out each of the twenty marriages in turn. In every case the Medici (orange) still have more betweenness than the best other family (blue), but the gap shrinks to a few points when the Albizzi\u2013Medici marriage is left out.",
                alt=f"Twenty rows, one per marriage left out, sorted from lowest Medici betweenness at the top ({low[1]:.1f}) to highest at the bottom ({rows[-1][1]:.1f}). In every row an orange dot for the Medici lies to the right of a blue dot for the best other family. A dashed vertical line marks the Medici's value with all marriages, 47.5. The two dots are closest in the row for the Albizzi\u2013Medici marriage.",
                data={"rows": [[r[0], round(r[1], 2), r[3], round(r[2], 2)] for r in rows]})
    return c, meta


FIGURES = {
    "florentine-intro": florentine_intro,
    "florentine-between": florentine_between,
    "krackhardt-layers": krackhardt_layers,
    "closeness-from-jo": closeness_from_jo,
    "eigen-rounds": eigen_rounds,
    "null-medici": null_medici,
    "tie-drop-stability": tie_drop_stability,
}

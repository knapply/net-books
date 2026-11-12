"""Figures for the homophily chapter (chapter 11).

Standard library only. Every number drawn is computed here from the CSV files in
books/sna/data (karate, sampson, sampson_groups) or from the six-person example
written at the top of the file.
"""
import csv
import random
from pathlib import Path

from fig_layout import fit, stress_layout
from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"
GRAY = "#9ca3af"

# The six-person office of the chapter: four people on floor 1, two on floor 2.
SIX_NAMES = ["Ana", "Ben", "Chloe", "Dev", "Eli", "Fay"]
SIX_FLOOR = [1, 1, 1, 1, 2, 2]
SIX_EDGES = [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (4, 5), (1, 5)]


def read(name, file):
    with open(DATA / name / file, newline="") as f:
        return list(csv.DictReader(f))


def _mix(hex_color, t):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(round(255 + (v - 255) * t) for v in (r, g, b))


def nominal_r(codes, src, dst, k, directed=False):
    """Newman's assortativity coefficient for categories, from arc counts."""
    m = [[0.0] * k for _ in range(k)]
    for a, b in zip(src, dst):
        m[codes[a]][codes[b]] += 1
        if not directed:
            m[codes[b]][codes[a]] += 1
    total = sum(map(sum, m))
    row = [sum(m[i]) / total for i in range(k)]
    col = [sum(m[i][j] for i in range(k)) / total for j in range(k)]
    trace = sum(m[i][i] for i in range(k)) / total
    ab = sum(row[i] * col[i] for i in range(k))
    return (trace - ab) / (1 - ab)


def karate():
    nodes = read("karate", "nodes.csv")
    edges = [(int(r["source"]) - 1, int(r["target"]) - 1) for r in read("karate", "edges.csv")]
    codes = [0 if r["faction"] == "Mr. Hi" else 1 for r in nodes]
    return codes, edges


# ---------------------------------------------------------------- the six-person office
def six_office():
    pos = [(110, 70), (240, 70), (175, 160), (310, 190), (440, 150), (390, 60)]
    pos = [(x + 20, y + 20) for x, y in pos]
    c = Canvas(560, 290, "Six people on two floors",
               "Six people, four on floor 1 drawn as blue circles and two on floor 2 drawn as orange squares, with seven ties, five of them between people on the same floor.")
    for a, b in SIX_EDGES:
        cross = SIX_FLOOR[a] != SIX_FLOOR[b]
        c.edge(pos[a], pos[b], ra=22, rb=22, width=2.4, color=RED if cross else GRAY,
               dash="7 5" if cross else None)
    for i, p in enumerate(pos):
        floor1 = SIX_FLOOR[i] == 1
        c.node(*p, "", r=22, fill=_mix(BLUE, .22) if floor1 else _mix(ORANGE, .3),
               stroke=BLUE if floor1 else ORANGE, shape="circle" if floor1 else "square", sw=2.4)
        c.text(p[0], p[1] + 5, SIX_NAMES[i], size=13, weight="600")
    c.text(280, 268, "Dashed red: ties between floors (2). Grey: ties within a floor (5).", size=13, fill=MUTED)
    meta = dict(chapter=11,
                caption="The six-person office used for the hand-worked numbers. Floor 1 (blue circles) has four people, floor 2 (orange squares) has two. Five of the seven ties stay within a floor.",
                alt="Six labelled nodes. Ana, Ben, Chloe and Dev are blue circles; Eli and Fay are orange squares. Solid grey lines join Ana, Ben and Chloe in a triangle, Chloe to Dev, and Eli to Fay. Dashed red lines join Dev to Eli and Ben to Fay, the only two ties that cross between floors.",
                data={"edges": [[SIX_NAMES[a], SIX_NAMES[b]] for a, b in SIX_EDGES],
                      "floor": dict(zip(SIX_NAMES, SIX_FLOOR))})
    return c, meta


# ---------------------------------------------------------------- karate coloured by faction
def karate_factions():
    codes, edges = karate()
    n = len(codes)
    pos = fit(stress_layout(n, edges, seed=3), 30, 30, 600, 380)
    c = Canvas(660, 470, "The karate club coloured by faction",
               "The 34 karate club members as blue circles (Mr. Hi's side) and orange squares (the officer's side), with grey ties inside a side and red dashed ties between sides.")
    cross = 0
    for a, b in edges:
        x = codes[a] != codes[b]
        cross += x
        c.edge(pos[a], pos[b], ra=8, rb=8, width=1.8 if x else 1.2, color=RED if x else GRAY,
               dash="5 4" if x else None, opacity=1 if x else .8)
    for i, p in enumerate(pos):
        mr = codes[i] == 0
        c.node(*p, "", r=8, fill=_mix(BLUE, .3) if mr else _mix(ORANGE, .4), stroke=BLUE if mr else ORANGE,
               shape="circle" if mr else "square", sw=2)
    c.text(330, 452, f"{len(edges) - cross} ties stay on one side (grey), {cross} cross between sides (dashed red).",
           size=13, fill=MUTED)
    meta = dict(chapter=11,
                caption="Zachary's karate club, coloured by the side each member took when the club split. Most ties (grey) stay on one side; eleven (dashed red) cross.",
                alt=f"A network of 34 nodes in two loose clusters. One cluster of 17 blue circles and one of 17 orange squares. Grey lines run mostly inside each cluster; {cross} dashed red lines run between the clusters.",
                data={"within": len(edges) - cross, "between": cross})
    return c, meta


# ---------------------------------------------------------------- mixing matrix heatmaps
def mixing_heatmap():
    names = [r["name"] for r in read("sampson", "nodes.csv")]
    ix = {n: i for i, n in enumerate(names)}
    group = {r["name"]: r["group"] for r in read("sampson_groups", "nodes.csv")}
    order = ["Turks", "Loyal", "Outcasts", "Waverers"]
    code = [order.index(group[n]) for n in names]
    arcs = [(ix[r["from"]], ix[r["to"]]) for r in read("sampson", "edges.csv") if r["relation"] == "esteem"]
    k = len(order)
    obs = [[0] * k for _ in range(k)]
    for a, b in arcs:
        obs[code[a]][code[b]] += 1
    total = len(arcs)
    rows = [sum(obs[i]) for i in range(k)]
    cols = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    exp = [[rows[i] * cols[j] / total for j in range(k)] for i in range(k)]
    r = nominal_r(code, [a for a, _ in arcs], [b for _, b in arcs], k, directed=True)
    top = max(max(map(max, obs)), max(map(max, exp)))
    c = Canvas(900, 500, "Observed and expected esteem choices by group",
               "Two four by four tables of counts of esteem choices from one group (rows) to another (columns): the observed counts and the counts expected if choices ignored groups.")
    cell, y0 = 78, 125
    for panel, (title, mat, x0, fmt) in enumerate([("Observed", obs, 120, "{}"), ("Expected if groups were ignored", exp, 530, "{:.1f}")]):
        c.text(x0 + 2 * cell, 40, title, size=15, weight="700")
        for j, g in enumerate(order):
            c.text(x0 + j * cell + cell / 2, y0 - 10, g, size=12, fill=MUTED)
        c.text(x0 + 2 * cell, y0 - 38, "group chosen", size=12, fill=MUTED, italic=True)
        for i, g in enumerate(order):
            c.text(x0 - 8, y0 + i * cell + cell / 2 + 4, g, size=12, anchor="end", fill=MUTED)
            for j in range(k):
                v = mat[i][j]
                t = v / top
                dark = t > .55
                c.rect(x0 + j * cell, y0 + i * cell, cell, cell, fill=_mix(BLUE, t * .95), stroke=PAPER, sw=2)
                c.text(x0 + j * cell + cell / 2, y0 + i * cell + cell / 2 + 6, fmt.format(v), size=18,
                       weight="700" if i == j else "400", fill=PAPER if dark else INK)
        if panel == 0:
            c.text(x0 - 94, y0 + 2 * cell, "choosing", size=12, fill=MUTED, anchor="middle")
            c.text(x0 - 94, y0 + 2 * cell + 16, "group", size=12, fill=MUTED, anchor="middle")
    diag_obs = sum(obs[i][i] for i in range(k))
    diag_exp = sum(exp[i][i] for i in range(k))
    c.text(450, 480, f"Diagonal cells (choices within a group): {diag_obs} observed against {diag_exp:.1f} expected. Newman's r = {r:.2f}.",
           size=13, fill=MUTED)
    meta = dict(chapter=11,
                caption="Esteem choices among Sampson's novices, counted by the group of the chooser (rows) and the group chosen (columns). The left table is observed. The right table is what the same row and column totals would give if choices ignored groups. The diagonal is where homophily shows.",
                alt=f"Two side-by-side four by four tables with rows and columns Turks, Loyal, Outcasts and Waverers. In the left table the diagonal cells hold {obs[0][0]}, {obs[1][1]}, {obs[2][2]} and {obs[3][3]} and are the darkest. In the right table the diagonal cells hold {exp[0][0]:.1f}, {exp[1][1]:.1f}, {exp[2][2]:.1f} and {exp[3][3]:.1f}, and no cell is much darker than the others.",
                data={"groups": order, "observed": obs, "expected": [[round(v, 2) for v in row] for row in exp],
                      "r": round(r, 4)})
    return c, meta


# ---------------------------------------------------------------- null distribution of r
def null_assortativity():
    codes, edges = karate()
    src, dst = [a for a, _ in edges], [b for _, b in edges]
    obs = nominal_r(codes, src, dst, 2)
    rng = random.Random(1)
    draws = []
    labels = codes[:]
    for _ in range(5000):
        rng.shuffle(labels)
        draws.append(nominal_r(labels, src, dst, 2))
    lo, hi, width = -0.4, 0.8, 0.05
    nb = round((hi - lo) / width)
    counts = [0] * nb
    for d in draws:
        counts[min(max(int((d - lo) / width), 0), nb - 1)] += 1
    mean = sum(draws) / len(draws)
    mx = max(draws)
    c = Canvas(900, 440, "Karate faction assortativity against shuffled labels",
               "A histogram of Newman's assortativity coefficient for 5,000 random reshufflings of the faction labels over the karate network, with the real value marked far to the right.")
    x0, y0, w, h = 80, 50, 740, 270
    top = max(counts) * 1.12
    bw = w / nb
    for k, cnt in enumerate(counts):
        bh = h * cnt / top
        c.rect(x0 + k * bw + 1, y0 + h - bh, bw - 2, bh, fill=BLUE + "66", stroke=BLUE, sw=1.2)
    ox = x0 + (obs - lo) / (hi - lo) * w
    c.add(f'<line x1="{ox:.1f}" y1="{y0 - 6}" x2="{ox:.1f}" y2="{y0 + h}" stroke="{INK}" stroke-width="2.5"/>')
    c.text(ox - 8, y0 + 12, f"real club {obs:.3f}", size=13, anchor="end", weight="700")
    c.add(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{INK}" stroke-width="1.5"/>')
    v = lo
    while v <= hi + 1e-9:
        c.text(x0 + (v - lo) / (hi - lo) * w, y0 + h + 20, f"{v:.1f}", size=12)
        v += 0.2
    c.text(x0 + w / 2, y0 + h + 44, "assortativity by faction after shuffling who has which label (bars 0.05 wide)", size=13, fill=MUTED)
    c.text(x0, 412, f"The shuffled values average {mean:.3f}, not 0, and none of the 5,000 reaches the real value (largest {mx:.3f}).",
           size=12.5, fill=MUTED, anchor="start")
    meta = dict(chapter=11,
                caption="Newman's assortativity coefficient for the karate faction labels, shuffled 5,000 times over the same network, against the real value of 0.718. Shuffling keeps the group sizes and the ties and breaks only the link between a person and a label. The draws behind this picture are not the ones in the code, so counts differ slightly.",
                alt=f"A histogram centred a little below zero, running from about -0.3 to 0.4, with a peak near -0.05. A black vertical line at {obs:.3f} sits far to the right of every bar. The shuffled values average {mean:.3f} and the largest is {mx:.3f}.",
                data={"observed": round(obs, 4), "mean": round(mean, 4), "largest": round(mx, 4),
                      "bins": [[round(lo + k * width, 2), round(lo + (k + 1) * width, 2), counts[k]] for k in range(nb)]})
    return c, meta


FIGURES = {
    "homophily-six": six_office,
    "homophily-karate": karate_factions,
    "homophily-mixing": mixing_heatmap,
    "homophily-null": null_assortativity,
}

"""Figures for the introduction and foundations chapters (chapters 1 and 2). Standard library only.

The small networks are the ones the chapters work by hand; the Florentine degrees are computed from
books/sna/data/florentine/edges.csv. Counts in captions are asserted here and must match what the
chapters' code prints.
"""
from itertools import combinations

from fig_classic import read
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, RED, SKY, Canvas, ring

GRAY = "#9ca3af"
LIGHT = "#eef6fb"
NAMES = ["Ana", "Ben", "Chloe", "Dev", "Eli"]


# ---------------------------------------------------------------- chapter 1
def crisis_test():
    c = Canvas(820, 360, "The crisis test on two teams",
               "Two panels, each showing four people after Ana and her ties are removed. On the left the four are still joined; on the right they are alone.")
    for k, (title, tied, note) in enumerate([
            ("Everyone talks to everyone", True, "Without Ana: 1 group"),
            ("Ana is the hub", False, "Without Ana: 4 separate people")]):
        cx = 205 + k * 410
        c.caption(cx, 30, title, size=15)
        others = dict(zip(NAMES[1:], ring(cx, 185, 95, 4, start=-135)))
        ana = (cx, 185)
        for n, p in others.items():
            c.edge(ana, p, ra=22, rb=20, width=1.4, color=FAINT, dash="4 4")
        if tied:
            for a, b in combinations(NAMES[1:], 2):
                c.edge(others[a], others[b], ra=20, rb=20, width=2.2, color=MUTED)
        c.node(*ana, "Ana", r=22, fill=PAPER, stroke=GRAY, size=11, sw=1.6, label_fill=GRAY)
        for n, p in others.items():
            c.node(*p, n, r=22, fill=LIGHT, stroke=BLUE, size=11)
        c.text(cx, 328, note, size=14, fill=MUTED)
    meta = dict(chapter=1,
                caption="The crisis test on both teams. Remove Ana and her ties. The team where everyone talks to everyone stays in one piece; the hub team falls into four separate people.",
                alt="Two panels, each with Ana's node faded and drawn with dashed gray lines to the others. On the left, the four remaining people are still joined to each other by six solid lines. On the right, the four remaining people are drawn with no lines between them.",
                data={"everyone_talks": {"groups_without_ana": 1}, "ana_is_hub": {"groups_without_ana": 4}})
    return c, meta


BOOK = [
    ("Foundations", BLUE, ["Introduction", "Foundations", "Networks as data", "Getting started"]),
    ("Describing networks", GREEN, ["Visualization", "Centrality", "Paths and cohesion", "Dyads and triads",
                                    "Small worlds", "Subgroups", "Homophily", "Positions and roles", "Ego networks"]),
    ("More complex networks", ORANGE, ["Two-mode", "Multilayer", "Signed and valued", "Time", "Space"]),
    ("Modeling networks", RED, ["Tests and null models", "Network regression", "ERGM", "Latent space and blocks",
                                "Longitudinal models", "Diffusion", "Link prediction"]),
    ("In practice", "#CC79A7", ["Collecting data", "Reproducibility", "Reporting"]),
    ("Case studies", "#56B4E9", ["Florentine families", "Monastery", "Organization", "Karate club"]),
]


def book_map():
    w, h = 900, 600
    c = Canvas(w, h, "A map of the book",
               "Six boxes in two rows listing the chapters of each part: foundations, describing networks, more complex networks, modeling networks, in practice and case studies.")
    bw, bh = 270, 240
    xs = [20, 315, 610]
    ys = [30, 300]
    boxes = []
    for i, (title, col, chapters) in enumerate(BOOK):
        x, y = xs[i % 3], ys[i // 3]
        boxes.append((x, y))
        c.rect(x, y, bw, bh, fill=col + "14", stroke=col, sw=2, rx=12)
        c.text(x + bw / 2, y + 30, f"{i + 1}. {title}", size=16, weight="700")
        for j, name in enumerate(chapters):
            c.text(x + 24, y + 62 + j * 20, name, size=13, anchor="start", fill=INK)
    # arrows along each row, and one that wraps from the third box to the fourth
    for i in (0, 1):
        c.arrow((xs[i] + bw + 2, ys[0] + bh / 2), (xs[i + 1] - 2, ys[0] + bh / 2), color=MUTED, width=2.2)
    for i in (3, 4):
        c.arrow((xs[i % 3] + bw + 2, ys[1] + bh / 2), (xs[i % 3 + 1] - 2, ys[1] + bh / 2), color=MUTED, width=2.2)
    mk = c.marker(MUTED)
    c.add(f'<path d="M{xs[2] + bw / 2},{ys[0] + bh + 2} V{ys[0] + bh + 30} H{xs[0] + bw / 2} V{ys[1] - 4}" '
          f'fill="none" stroke="{MUTED}" stroke-width="2.2" stroke-dasharray="6 4" marker-end="url(#{mk})"/>')
    c.text(w / 2, h - 26, "Read in order, or jump to the part you need. Every part leans on Foundations.", size=13, fill=MUTED)
    meta = dict(chapter=1,
                caption="A map of the book. Foundations come first and everything leans on them; describing and modeling are the two big halves; the case studies at the end put the pieces together on real data.",
                alt="Six labeled boxes in two rows of three, joined by arrows from left to right and a dashed arrow from the end of the first row to the start of the second. Foundations lists four chapters, Describing networks nine, More complex networks five, Modeling networks seven, In practice three and Case studies four.",
                data={t: ch for t, _, ch in BOOK})
    assert [len(ch) for _, _, ch in BOOK] == [4, 9, 5, 7, 3, 4]
    return c, meta


# ---------------------------------------------------------------- chapter 2
ADVICE = [(0, 1), (0, 2), (1, 2), (2, 0), (3, 0), (3, 2), (4, 2)]


def dyad_states():
    c = Canvas(820, 400, "Three states of a pair",
               "The five-person advice network drawn with arrows, with the mutual pair in orange, asymmetric pairs in blue and null pairs as faint dotted lines, next to a tally.")
    pos = {0: (120, 140), 1: (260, 50), 2: (300, 200), 3: (60, 290), 4: (200, 350)}
    arcs = set(ADVICE)
    for a, b in combinations(range(5), 2):
        if (a, b) not in arcs and (b, a) not in arcs:
            c.edge(pos[a], pos[b], ra=22, rb=22, width=1.4, color=GRAY, dash="2 5")
    mutual = [(a, b) for a, b in arcs if (b, a) in arcs and a < b]
    asym = [(a, b) for a, b in arcs if (b, a) not in arcs]
    null = [(a, b) for a, b in combinations(range(5), 2) if (a, b) not in arcs and (b, a) not in arcs]
    assert (len(mutual), len(asym), len(null)) == (1, 5, 4)
    for a, b in asym:
        c.edge(pos[a], pos[b], ra=22, rb=22, directed=True, width=2.4, color=BLUE)
    for a, b in arcs:
        if (b, a) in arcs:
            c.edge(pos[a], pos[b], ra=22, rb=22, directed=True, width=2.6, color=ORANGE, curve=14)
    for i, n in enumerate(NAMES):
        c.node(*pos[i], n, r=22, fill=LIGHT, stroke=INK, size=11)
    x = 500
    c.text(x + 130, 62, "Ten pairs of people", size=16, weight="700")
    rows = [("Mutual", "both ways", ORANGE, 1, None), ("Asymmetric", "one way", BLUE, 5, None),
            ("Null", "no tie", GRAY, 4, "2 5")]
    for k, (label, note, col, count, dash) in enumerate(rows):
        y = 120 + k * 80
        c.edge((x, y), (x + 70, y), ra=0, rb=0, directed=label != "Null", width=2.6, color=col, dash=dash)
        if label == "Mutual":
            c.edge((x + 70, y + 10), (x, y + 10), ra=0, rb=0, directed=True, width=2.6, color=col)
        c.text(x + 92, y + 2, f"{label}: {count}", size=16, weight="700", anchor="start")
        c.text(x + 92, y + 24, note, size=13, anchor="start", fill=MUTED)
    c.text(x + 130, 372, "1 + 5 + 4 = 10 pairs;  2 x 1 + 5 = 7 ties", size=13, fill=MUTED)
    meta = dict(chapter=2,
                caption="The three states of a pair of people in a directed network, drawn from the advice network. Ana and Chloe are a mutual dyad; Ana and Ben are asymmetric; Ben and Dev are null. There are ten pairs in all.",
                alt="The five-person advice network drawn with arrows. The pair Ana and Chloe has arrows in both directions and is labeled mutual. Five pairs, such as Ana and Ben, have an arrow one way and are labeled asymmetric. Four pairs, such as Ben and Dev, have no arrow and are labeled null. A tally box shows 1 mutual, 5 asymmetric and 4 null.",
                data={"mutual": 1, "asymmetric": 5, "null": 4})
    return c, meta


def symmetrize_rules():
    c = Canvas(900, 340, "Two rules for undirected ties",
               "Three drawings of the advice network: the original arrows, the either rule, and the both rule.")
    arcs = set(ADVICE)
    either = sorted({tuple(sorted(a)) for a in ADVICE})
    both = sorted({tuple(sorted(a)) for a in ADVICE if (a[1], a[0]) in arcs})
    assert (len(either), len(both)) == (6, 1)
    panels = [("Advice network", "7 arrows"), ("Either asks: 6 ties", "1 piece, density 0.60"),
              ("Both ask each other: 1 tie", "4 pieces, density 0.10")]
    for k, (title, note) in enumerate(panels):
        cx = 150 + k * 300
        c.caption(cx, 30, title, size=15)
        pos = dict(zip(range(5), ring(cx, 170, 100, 5)))
        if k == 0:
            for a, b in ADVICE:
                c.edge(pos[a], pos[b], ra=20, rb=20, directed=True, width=2.2, color=MUTED,
                       curve=12 if (b, a) in arcs else 0)
        else:
            for a, b in (either if k == 1 else both):
                c.edge(pos[a], pos[b], ra=20, rb=20, width=2.6, color=BLUE if k == 1 else ORANGE)
        for i, n in enumerate(NAMES):
            c.node(*pos[i], n, r=20, fill=LIGHT, stroke=BLUE if k < 2 else ORANGE, size=10)
        c.text(cx, 312, note, size=13, fill=MUTED)
    meta = dict(chapter=2,
                caption="The advice network turned into an undirected one by two rules. Keeping a pair if either person asks gives a connected network of six ties; keeping only mutual pairs leaves a single tie.",
                alt="Three drawings of the five advice-network people on a circle. Left: the original with seven arrows. Middle: the either rule, with six plain lines and all five people connected. Right: the both rule, with a single line between Ana and Chloe and Ben, Dev and Eli standing alone.",
                data={"either_ties": len(either), "both_ties": len(both)})
    return c, meta


def adjacency_walks():
    people = NAMES
    ties = [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4)]
    n = 5
    a = [[0] * n for _ in range(n)]
    for i, j in ties:
        a[i][j] = a[j][i] = 1
    sq = [[sum(a[i][k] * a[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    cube_trace = sum(sum(sq[i][k] * a[k][i] for k in range(n)) for i in range(n))
    assert [sq[i][i] for i in range(n)] == [2, 2, 3, 2, 1] and cube_trace == 6 and sq[0][3] == 1
    c = Canvas(960, 390, "The adjacency matrix and walks of length two",
               "A small network, its adjacency matrix with shaded cells, and the matrix of walks of length two.")
    # the network
    pos = {0: (60, 120), 1: (60, 230), 2: (150, 175), 3: (240, 175), 4: (330, 175)}
    for i, j in ties:
        c.edge(pos[i], pos[j], ra=17, rb=17, width=2.2, color=MUTED)
    for i, nm in enumerate(people):
        c.node(*pos[i], nm, r=17, fill=LIGHT, stroke=BLUE, size=9)
    c.caption(195, 55, "The network", size=15)
    cell = 44

    def grid(x0, y0, mat, title, numbers, hilite_diag=False):
        c.caption(x0 + 2.5 * cell, y0 - 40, title, size=15)
        for j, nm in enumerate(people):
            c.text(x0 + (j + 0.5) * cell, y0 - 10, nm[:3], size=11, fill=MUTED)
            c.text(x0 - 8, y0 + (j + 0.5) * cell + 4, nm[:3], size=11, fill=MUTED, anchor="end")
        for i in range(n):
            for j in range(n):
                v = mat[i][j]
                on = v > 0
                fill = (ORANGE + "55") if (hilite_diag and i == j) else (BLUE + "33" if on else PAPER)
                c.rect(x0 + j * cell, y0 + i * cell, cell, cell, fill=fill, stroke=FAINT, sw=1)
                if numbers:
                    c.text(x0 + (j + 0.5) * cell, y0 + (i + 0.5) * cell + 5, str(v), size=15, weight="700" if i == j else "400")
                elif on:
                    c.text(x0 + (j + 0.5) * cell, y0 + (i + 0.5) * cell + 5, "1", size=14)
    grid(430, 100, a, "A: who is tied to whom", False)
    grid(700, 100, sq, "A times A: walks of length 2", True, hilite_diag=True)
    c.text(660, 350, "The diagonal of A times A is the degree.", size=13, fill=MUTED)
    c.text(660, 370, "The trace of A cubed is 6, so there is 6 / 6 = 1 triangle.", size=13, fill=MUTED)
    meta = dict(chapter=2,
                caption="The adjacency matrix of the triangle-with-a-tail network and its square. A shaded cell is a one; the number in each cell of the second grid counts the walks of length two between that pair. The diagonal of the second grid repeats the degrees.",
                alt="Left: a five by five grid for Ana, Ben, Chloe, Dev and Eli with ten shaded cells, symmetric across the diagonal, drawn beside a small network of a triangle with a two-person tail. Right: a five by five grid of numbers whose diagonal reads 2, 2, 3, 2, 1 and whose other entries are 0 or 1.",
                data={"degrees": [sq[i][i] for i in range(n)], "trace_of_cube": cube_trace})
    return c, meta


def weighted_threshold():
    msgs = {(0, 1): 10, (0, 2): 1, (0, 3): 1, (0, 4): 1, (1, 2): 6, (1, 3): 6}
    c = Canvas(900, 350, "The same network at three cutoffs",
               "Three drawings of five people joined by ties whose thickness shows the number of messages, at cutoffs of one, two and seven.")
    cuts = [(1, "6 ties, 1 piece"), (2, "3 ties, 2 pieces"), (7, "1 tie, 4 pieces")]
    for k, (cut, note) in enumerate(cuts):
        cx = 150 + k * 300
        c.caption(cx, 30, f"At least {cut} message{'s' if cut > 1 else ''}", size=15)
        pos = dict(zip(range(5), ring(cx, 175, 100, 5)))
        for (a, b), w in msgs.items():
            keep = w >= cut
            c.edge(pos[a], pos[b], ra=20, rb=20, width=1 + 0.6 * w if keep else 1.2, color=BLUE if keep else FAINT,
                   dash=None if keep else "3 4")
            if keep:
                dx, dy = pos[b][0] - pos[a][0], pos[b][1] - pos[a][1]
                d = (dx * dx + dy * dy) ** 0.5
                mx, my = (pos[a][0] + pos[b][0]) / 2 - dy / d * 13, (pos[a][1] + pos[b][1]) / 2 + dx / d * 13
                c.text(mx, my + 4, str(w), size=12, fill=INK)
        for i, nm in enumerate(NAMES):
            c.node(*pos[i], nm, r=20, fill=LIGHT, stroke=BLUE, size=10)
        c.text(cx, 322, note, size=13, fill=MUTED)
    kept = [sum(w >= cut for w in msgs.values()) for cut, _ in cuts]
    assert kept == [6, 3, 1]
    meta = dict(chapter=2,
                caption="The same weighted network at three cutoffs. Line thickness shows the number of messages. Raising the cutoff turns a connected network into a hub around Ben and then into a single pair.",
                alt="Three drawings of the same five people. With every tie kept, six lines join them and Ana and Ben are drawn with a thick line. With a cutoff of two, three lines remain and Ben is joined to Ana, Chloe and Dev while Eli stands alone. With a cutoff of seven, only the Ana and Ben line remains and three people stand alone.",
                data={"cutoffs": [1, 2, 7], "ties_kept": kept})
    return c, meta


def florentine_degrees():
    rows = read("florentine", "edges.csv")
    deg = {}
    for r in rows:
        for k in ("source", "target"):
            deg[r[k]] = deg.get(r[k], 0) + 1
    order = sorted(deg, key=lambda f: (-deg[f], f))
    assert len(deg) == 15 and len(rows) == 20 and deg["Medici"] == 6
    mean = 2 * len(rows) / len(deg)
    w, h = 780, 560
    c = Canvas(w, h, "Marriages per Florentine family",
               "A horizontal bar chart of the number of marriages of each of fifteen families.")
    x0, y0, row = 150, 50, 28
    unit = 85
    for t in range(0, 7):
        x = x0 + t * unit
        c.edge((x, y0 - 8), (x, y0 + 15 * row), ra=0, rb=0, width=1, color="#e5e7eb")
        c.text(x, y0 - 14, str(t), size=12, fill=MUTED)
    for i, f in enumerate(order):
        y = y0 + i * row
        hot = f == "Medici"
        c.text(x0 - 10, y + row / 2 + 4, f, size=13, anchor="end", weight="700" if hot else "400")
        c.rect(x0, y + 4, deg[f] * unit, row - 8, fill=(ORANGE if hot else BLUE + "aa"), stroke=ORANGE if hot else BLUE, sw=1.4)
        c.text(x0 + deg[f] * unit + 8, y + row / 2 + 4, str(deg[f]), size=13, anchor="start", weight="600")
    mx = x0 + mean * unit
    c.edge((mx, y0 - 6), (mx, y0 + 15 * row + 4), ra=0, rb=0, width=1.6, color=RED, dash="6 4")
    c.text(mx + 6, y0 + 15 * row + 22, f"mean {mean:.2f}", size=13, anchor="start", fill=RED)
    c.text(x0 + 3 * unit, h - 14, "number of marriages (degree)", size=13, fill=MUTED)
    meta = dict(chapter=2,
                caption="The number of marriages of each of the 15 families, from most to fewest. The Medici stand alone at six; Guadagni and Strozzi follow with four.",
                alt="A horizontal bar chart of 15 family names. Medici has the longest bar at 6. Guadagni and Strozzi have 4. Six families have 3, Barbadori and Salviati have 2, and four families have 1. A vertical dashed line marks the mean of 2.67.",
                data={f: deg[f] for f in order})
    return c, meta


FIGURES = {"crisis-test": crisis_test, "book-map": book_map, "dyad-states": dyad_states,
           "symmetrize-rules": symmetrize_rules, "adjacency-walks": adjacency_walks,
           "weighted-threshold": weighted_threshold, "florentine-degrees": florentine_degrees}

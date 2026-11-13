"""Figures for the karate club case study (chapter 32).

Standard library only. The network, the sides and the contexts are read from the CSV
files in books/sna/data/karate. Zachary's minimum cut and the Fiedler split are computed
here. The Louvain partition (seed 1) and the table of misclassified members are copied
from the chapter's Rust output, and checked below against the sides so a stale copy fails.
"""
import csv
import random
from collections import deque
from pathlib import Path

from fig_layout import fit, stress_layout
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, PURPLE, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data" / "karate"
GRAY = "#9ca3af"
N = 34

# Louvain, resolution 1, seed 1 (the chapter's Rust tab): the community of members 1 to 34.
LOUVAIN = [0, 0, 0, 0, 1, 1, 1, 0, 2, 0, 1, 0, 0, 0, 2, 2, 1, 0, 2, 0, 2, 0, 2, 3, 3, 3, 2, 3, 3, 2, 2, 3, 2, 2]
# The chapter's table of misclassified members (the Rust tab), method by method.
WRONG = [("Zachary min cut", [9]), ("Louvain", [9, 10]), ("Fast greedy", [9, 10]),
         ("Label propagation", [3, 9]), ("Leading eigenvector", [9]), ("Infomap", [9, 10]),
         ("Girvan-Newman, 2 groups", [3, 9]), ("Spectral: Fiedler", [3, 9]),
         ("Spectral: modularity", [9]), ("Best modularity (exact)", [9]),
         ("Degree-corrected SBM", [9, 10])]


def read(name):
    with open(DATA / name, newline="") as f:
        return list(csv.DictReader(f))


def load():
    ties = [(int(r["source"]) - 1, int(r["target"]) - 1, int(r["contexts"])) for r in read("edges.csv")]
    side = [0 if r["faction"] == "Mr. Hi" else 1 for r in read("nodes.csv")]
    return ties, side


def min_cut_side(ties):
    """Smallest source side of a minimum cut between member 1 (index 0) and member 34, with the
    contexts as capacities (Edmonds and Karp)."""
    cap = [[0] * N for _ in range(N)]
    for a, b, c in ties:
        cap[a][b] += c
        cap[b][a] += c
    while True:
        parent = {0: 0}
        queue = deque([0])
        while queue and N - 1 not in parent:
            u = queue.popleft()
            for v in range(N):
                if cap[u][v] > 0 and v not in parent:
                    parent[v] = u
                    queue.append(v)
        if N - 1 not in parent:
            return sorted(parent)
        path, v = [], N - 1
        while v != 0:
            path.append((parent[v], v))
            v = parent[v]
        push = min(cap[u][v] for u, v in path)
        for u, v in path:
            cap[u][v] -= push
            cap[v][u] += push


def fiedler_split(ties):
    """Sign of the second-smallest Laplacian eigenvector, by power iteration with the constant
    vector projected out."""
    adj = [[0.0] * N for _ in range(N)]
    for a, b, _ in ties:
        adj[a][b] = adj[b][a] = 1.0
    deg = [sum(r) for r in adj]
    shift = 2 * max(deg)
    rng = random.Random(1)
    x = [rng.uniform(-1, 1) for _ in range(N)]
    for _ in range(20000):
        mean = sum(x) / N
        x = [v - mean for v in x]
        y = [shift * x[i] - (deg[i] * x[i] - sum(adj[i][j] * x[j] for j in range(N))) for i in range(N)]
        norm = sum(v * v for v in y) ** 0.5
        x = [v / norm for v in y]
    return [int(v > 0) for v in x]


def wrong_members(labels, side):
    out = []
    for i in range(N):
        mates = [side[j] for j in range(N) if labels[j] == labels[i]]
        if int(sum(mates) / len(mates) > 0.5) != side[i]:
            out.append(i + 1)
    return out


def adjusted_rand(a, b):
    from math import comb
    table = {}
    for x, y in zip(a, b):
        table[(x, y)] = table.get((x, y), 0) + 1
    rows, cols = {}, {}
    for (x, y), n in table.items():
        rows[x] = rows.get(x, 0) + n
        cols[y] = cols.get(y, 0) + n
    index = sum(comb(n, 2) for n in table.values())
    r, c = sum(comb(n, 2) for n in rows.values()), sum(comb(n, 2) for n in cols.values())
    expected = r * c / comb(len(a), 2)
    return (index - expected) / ((r + c) / 2 - expected)


def positions(ties, x0, y0, w, h):
    edges = [(a, b) for a, b, _ in ties]
    return fit(stress_layout(N, edges, seed=3), x0, y0, w, h)


def partitions():
    ties, side = load()
    cut = min_cut_side(ties)
    zachary = [0 if i in cut else 1 for i in range(N)]
    fiedler = fiedler_split(ties)
    fiedler = [1 - g for g in fiedler] if fiedler[0] == 1 else fiedler   # member 1 in group 0, so colours line up
    # Stale-copy guards: these must match the chapter's printed tables.
    assert wrong_members(LOUVAIN, side) == [9, 10] and abs(adjusted_rand(LOUVAIN, side) - 0.392) < 5e-4
    assert wrong_members(zachary, side) == [9]
    assert wrong_members(fiedler, side) == [3, 9]
    return ties, side, [("What happened", side, []), ("Louvain, 4 communities", LOUVAIN, wrong_members(LOUVAIN, side)),
                        ("Fiedler spectral cut", fiedler, wrong_members(fiedler, side)),
                        ("Zachary's minimum cut", zachary, wrong_members(zachary, side))]


def partition_panels():
    ties, side, panels = partitions()
    colors = [BLUE, ORANGE, GREEN, PURPLE]
    w, h = 900, 920
    c = Canvas(w, h, "The karate club: the real split against three methods",
               "Four panels of the same 34-member network. Shape is the side each member took. Colour is the group a method found. A heavy black outline marks members the method puts on the wrong side.")
    shown = {}
    for k, (title, labels, wrong) in enumerate(panels):
        px, py = 20 + (k % 2) * 440, 20 + (k // 2) * 450
        pos = positions(ties, px + 30, py + 60, 380, 340)
        c.caption(px + 210, py + 28, title, size=15)
        for a, b, _ in ties:
            across = labels[a] != labels[b]
            c.edge(pos[a], pos[b], ra=10, rb=10, width=1.1, color=MUTED if across else FAINT, dash="4 3" if across else None)
        for i in range(N):
            m = i + 1
            fill = colors[labels[i] % 4] + "cc" if k else (BLUE if side[i] == 0 else ORANGE) + "cc"
            ring = "#000000" if m in wrong else INK
            c.node(pos[i][0], pos[i][1], str(m), r=11 if m not in (1, 34) else 14, fill=fill, stroke=ring,
                   shape="circle" if side[i] == 0 else "square", size=9.5, sw=4 if m in wrong else 1.3)
        note = "no member is misclassified by definition" if not k else \
            ("misclassified: " + ", ".join(map(str, wrong)) + f" (adjusted Rand {adjusted_rand(labels, side):.2f})")
        c.text(px + 210, py + 420, note, size=12.5, fill=MUTED)
        shown[title] = {"labels": labels, "wrong": wrong}
    c.text(w / 2, h - 12, "Circles stayed with Mr. Hi (member 1). Squares followed the officer (member 34). Dashed lines: ties that cross groups.", size=12.5, fill=MUTED)
    meta = dict(chapter=32,
                caption="The karate club drawn four times with the same layout. Shape shows the side each member took. In the three method panels, colour shows the group the method found and a heavy black outline marks a member the method puts on the wrong side (a member counts as wrong when most of their group took the other side). Member 9 is wrong in every panel.",
                alt="Four network pictures of 34 members. Top left, the real split: circles for Mr. Hi's 17 supporters in blue and squares for the officer's 17 in orange, with 11 dashed ties crossing between them. Top right, Louvain finds four colour groups and heavy black outlines mark members 9 and 10. Bottom left, a Fiedler spectral cut finds two groups and heavy black outlines mark members 3 and 9. Bottom right, Zachary's minimum cut finds two groups and a heavy black outline marks only member 9.",
                data={"panels": shown})
    return c, meta


def wrong_dots():
    names = [n for n, _ in WRONG]
    cols = sorted({m for _, ms in WRONG for m in ms})
    w, h = 900, 120 + 30 * len(names)
    c = Canvas(w, h, "Which members each method misclassifies",
               "A grid with one row per method and one column per member that any method misclassified.")
    x0, y0, cw = 330, 70, 90
    c.caption(w / 2, 26, "Members each method puts on the wrong side", size=15)
    for j, m in enumerate(cols):
        c.text(x0 + j * cw + cw / 2, y0 - 14, f"member {m}", size=13, weight="600")
    for i, (name, wrong) in enumerate(WRONG):
        y = y0 + 12 + i * 30
        c.text(x0 - 16, y + 4, name, size=13, anchor="end")
        c.add(f'<line x1="{x0 - 8}" y1="{y + 14}" x2="{x0 + cw * len(cols)}" y2="{y + 14}" stroke="{FAINT}" stroke-width="1"/>')
        for j, m in enumerate(cols):
            if m in wrong:
                c.node(x0 + j * cw + cw / 2, y, "", r=9, fill=RED, stroke=RED)
    totals = [sum(m in ms for _, ms in WRONG) for m in cols]
    for j, t in enumerate(totals):
        c.text(x0 + j * cw + cw / 2, h - 14, f"{t} of {len(WRONG)}", size=13, weight="700")
    meta = dict(chapter=32,
                caption="Members that each of eleven methods puts on the wrong side. Member 9 is wrong for all eleven, member 10 for four and member 3 for three. Every other member is right for every method.",
                alt=f"A grid of eleven methods by three members (3, 9 and 10). A dot means the method misclassifies that member. Member 9 has a dot in every row, {totals[cols.index(9)]} of {len(WRONG)}. Member 10 has {totals[cols.index(10)]} dots and member 3 has {totals[cols.index(3)]}.",
                data={"wrong": {n: ms for n, ms in WRONG}})
    return c, meta


def null_hist():
    ties, side = load()
    m = len(ties)
    adj = [[0] * N for _ in range(N)]

    def q_of(edge_list, labels):
        deg = [0] * N
        inside = {}
        for a, b in edge_list:
            deg[a] += 1
            deg[b] += 1
            if labels[a] == labels[b]:
                inside[labels[a]] = inside.get(labels[a], 0) + 1
        totals = {}
        for i in range(N):
            totals[labels[i]] = totals.get(labels[i], 0) + deg[i]
        return sum(inside.get(g, 0) / m - (totals[g] / (2 * m)) ** 2 for g in totals)

    base = [(a, b) for a, b, _ in ties]
    observed = q_of(base, side)
    rng = random.Random(5)
    shuffled = []
    for _ in range(2000):
        s = side[:]
        rng.shuffle(s)
        shuffled.append(q_of(base, s))
    rewired = []
    for _ in range(500):
        e = [tuple(sorted(t)) for t in base]
        have = set(e)
        done = 0
        while done < 10 * m:
            i, j = rng.randrange(m), rng.randrange(m)
            if i == j:
                continue
            (a, b), (c_, d) = e[i], e[j]
            if rng.random() < 0.5:
                c_, d = d, c_
            n1, n2 = tuple(sorted((a, d))), tuple(sorted((c_, b)))
            done += 1
            if a == d or c_ == b or n1 == n2 or n1 in have or n2 in have:
                continue
            have -= {e[i], e[j]}
            e[i], e[j] = n1, n2
            have |= {n1, n2}
        rewired.append(q_of(e, side))
    lo, hi, width = -0.3, 0.4, 0.025
    nb = round((hi - lo) / width)

    def bins(values):
        counts = [0] * nb
        for v in values:
            counts[min(max(int((v - lo) / width), 0), nb - 1)] += 1
        return counts

    cs, cr = bins(shuffled), bins(rewired)
    W, H = 900, 400
    c = Canvas(W, H, "Modularity of the real split against two null models",
               "Two histograms of modularity for random versions of the karate club, with the real value marked far to the right of both.")
    x0, y0, w, h = 70, 50, 780, 250
    top = max(max(cs) / 2000, max(cr) / 500) * 1.1
    bw = w / nb
    for k in range(nb):
        for counts, total, color, off in ((cs, 2000, BLUE, 0), (cr, 500, ORANGE, bw / 2)):
            bh = h * (counts[k] / total) / top
            c.rect(x0 + k * bw + off + 1, y0 + h - bh, bw / 2 - 2, bh, fill=color + "88", stroke=color, sw=1)
    ox = x0 + (observed - lo) / (hi - lo) * w
    c.add(f'<line x1="{ox:.1f}" y1="{y0 - 6}" x2="{ox:.1f}" y2="{y0 + h}" stroke="{INK}" stroke-width="2.5"/>')
    c.text(ox - 8, y0 + 12, f"real split {observed:.3f}", size=13, anchor="end", weight="700")
    c.add(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{INK}" stroke-width="1.5"/>')
    v = lo
    while v <= hi + 1e-9:
        c.text(x0 + (v - lo) / (hi - lo) * w, y0 + h + 20, f"{v:.1f}", size=12)
        v += 0.1
    c.text(x0 + w / 2, y0 + h + 42, "modularity of the real two-way split, on the shuffled or rewired network", size=13, fill=MUTED)
    c.rect(x0 + 10, y0 + 8, 14, 14, fill=BLUE + "88", stroke=BLUE, sw=1)
    c.text(x0 + 30, y0 + 20, "sides shuffled, ties kept (2,000)", size=12.5, anchor="start")
    c.rect(x0 + 10, y0 + 30, 14, 14, fill=ORANGE + "88", stroke=ORANGE, sw=1)
    c.text(x0 + 30, y0 + 42, "ties rewired, degrees kept (500)", size=12.5, anchor="start")
    c.text(x0, H - 14, f"Largest values: shuffled {max(shuffled):.3f}, rewired {max(rewired):.3f}. Means: {sum(shuffled) / len(shuffled):.3f} and {sum(rewired) / len(rewired):.3f}.", size=12.5, fill=MUTED, anchor="start")
    meta = dict(chapter=32,
                caption=f"Modularity of the real two-way split ({observed:.3f}) against 2,000 shuffles of the sides over the real ties and 500 rewirings of the ties that keep every member's degree. The draws behind this picture are not the ones in the code, so the numbers differ slightly.",
                alt=f"Two overlapping histograms of modularity, both centred a little below zero and running from about -0.2 to 0.2. A black vertical line at {observed:.3f} lies to the right of every bar. The largest shuffled value is {max(shuffled):.3f} and the largest rewired value is {max(rewired):.3f}.",
                data={"observed": round(observed, 4), "shuffled_max": round(max(shuffled), 4), "rewired_max": round(max(rewired), 4)})
    return c, meta


FIGURES = {
    "karate-case-partitions": partition_panels,
    "karate-case-wrong": wrong_dots,
    "karate-case-null": null_hist,
}

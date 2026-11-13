"""Figures for the positions and roles chapter (chapter 12).

Standard library only. Every number drawn is computed here from the CSV files in
books/sna/data/krackhardt, or from the small networks defined below, so the pictures
cannot drift from the data. The clustering is average linkage on structural-equivalence
distances (Euclidean, the pair's own ties left out), the same recipe as the chapter's code.
"""
import csv
import math
import random
from pathlib import Path

from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, SKY, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data" / "krackhardt"
GRAY = "#9ca3af"
PALE = "#cfe5f3"


def distances(a):
    """Euclidean distance between profiles (row and column), leaving out the pair's own two cells."""
    n = len(a)
    d = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            s = sum((a[i][k] - a[j][k]) ** 2 + (a[k][i] - a[k][j]) ** 2 for k in range(n) if k != i and k != j)
            d[i][j] = d[j][i] = math.sqrt(s)
    return d


def cluster(d, k):
    """Average linkage, cut into k groups, numbered from 0 by first member."""
    groups = [[i] for i in range(len(d))]
    while len(groups) > k:
        best, at = float("inf"), (0, 1)
        for p in range(len(groups)):
            for q in range(p + 1, len(groups)):
                gaps = [d[i][j] for i in groups[p] for j in groups[q]]
                gap = sum(gaps) / len(gaps)
                if gap < best - 1e-12:
                    best, at = gap, (p, q)
        groups[at[0]] += groups.pop(at[1])
    groups.sort(key=min)
    label = [0] * len(d)
    for c, g in enumerate(groups):
        for i in g:
            label[i] = c
    return label


def errors(a, pos):
    """Mistakes against the best all-0 or all-1 image."""
    k = max(pos) + 1
    total = 0
    for r in range(k):
        rows = [i for i in range(len(a)) if pos[i] == r]
        for s in range(k):
            cols = [j for j in range(len(a)) if pos[j] == s]
            pairs = len(rows) * len(cols) - (len(rows) if r == s else 0)
            ties = sum(a[i][j] for i in rows for j in cols)
            total += min(ties, pairs - ties)
    return total


def krackhardt():
    with open(DATA / "nodes.csv", newline="") as f:
        nodes = list(csv.DictReader(f))
    with open(DATA / "edges.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    n = len(nodes)
    a = [[0] * n for _ in range(n)]
    for r in rows:
        if r["relation"] == "advice":
            a[int(r["from"]) - 1][int(r["to"]) - 1] = 1
    return a, [int(r["level"]) for r in nodes]


def six_people():
    names = list("abcdef")
    arcs = [(0, 3), (0, 4), (1, 3), (1, 4), (2, 3), (3, 5), (4, 5)]
    n = 6
    a = [[0] * n for _ in range(n)]
    for i, j in arcs:
        a[i][j] = 1
    return names, arcs, a


def six():
    names, arcs, a = six_people()
    d = distances(a)
    pos = {0: (110, 70), 1: (230, 70), 2: (350, 70), 3: (170, 190), 4: (290, 190), 5: (230, 300)}
    c = Canvas(460, 360, "Six people and their advice ties",
               "Six people in three rows. The top row, a, b and c, each point at d or e. The middle row, d and e, point at f at the bottom.")
    for i, j in arcs:
        c.edge(pos[i], pos[j], ra=17, rb=17, directed=True, color=MUTED, width=2)
    shape = {0: "circle", 1: "circle", 2: "circle", 3: "square", 4: "square", 5: "diamond"}
    for i in range(6):
        fill = PALE if i < 3 else (ORANGE + "66" if i < 5 else "#d9f0e8")
        c.node(*pos[i], names[i], r=17, fill=fill, stroke=INK, shape=shape[i], size=14)
    c.text(40, 74, "ask", size=12, fill=MUTED, anchor="start")
    c.text(40, 194, "answer", size=12, fill=MUTED, anchor="start")
    c.text(230, 342, "a and b are alike. c is one tie away. d and e are one tie apart.", size=12, fill=MUTED)
    meta = dict(
        chapter=12,
        caption="Six people in three positions. People in the top row go to one or both of the middle row, and both in the middle row go to the person at the bottom.",
        alt=("Six circles and squares joined by seven arrows. In the top row, a and b each have arrows to both d and e, and c has one arrow to d. "
             "In the middle row, d and e each have an arrow to f, the diamond at the bottom."),
        data={"names": names, "arcs": [list(x) for x in arcs],
              "distance_a_b": round(d[0][1], 3), "distance_a_c": round(d[0][2], 3), "distance_d_e": round(d[3][4], 3)})
    return c, meta


def krackhardt_blocks():
    a, level = krackhardt()
    n = len(a)
    d = distances(a)
    pos = cluster(d, 4)
    order = sorted(range(n), key=lambda i: (pos[i], i))
    sizes = [pos.count(g) for g in range(4)]
    ties = [[sum(a[i][j] for i in range(n) if pos[i] == r for j in range(n) if pos[j] == s) for s in range(4)] for r in range(4)]
    dens = [[ties[r][s] / (sizes[r] * sizes[s] - (sizes[r] if r == s else 0)) for s in range(4)] for r in range(4)]
    total = sum(map(sum, a))
    overall = total / (n * (n - 1))
    err = errors(a, pos)

    c = Canvas(940, 520, "Krackhardt's managers, grouped into four positions by their advice ties",
               "On the left, the 21 by 21 table of who goes to whom for advice, with managers ordered by position. On the right, the block densities.")
    cell, x0, y0 = 17, 70, 78
    c.text(x0 + n * cell / 2, 28, "Who goes to whom for advice", size=15, weight="700")
    c.text(x0 + n * cell / 2, 48, "rows ask, columns are asked", size=12, fill=MUTED)
    for p, i in enumerate(order):
        mark = {1: ("CEO", RED), 2: ("VP", ORANGE)}.get(level[i])
        col = mark[1] if mark else INK
        c.text(x0 + p * cell + cell / 2, y0 - 7, str(i + 1), size=10, fill=col, weight="700" if mark else "400")
        c.text(x0 - 6, y0 + p * cell + cell / 2 + 4, str(i + 1), size=10, anchor="end", fill=col, weight="700" if mark else "400")
    for p, i in enumerate(order):
        for q, j in enumerate(order):
            tie = a[i][j] == 1
            c.rect(x0 + q * cell, y0 + p * cell, cell, cell, fill=BLUE if tie else ("#f3f4f6" if i == j else "#ffffff"), stroke="#e5e7eb", sw=0.6)
    edge = 0
    for g in range(3):
        edge += sizes[g]
        c.add(f'<line x1="{x0 + edge * cell}" y1="{y0 - 3}" x2="{x0 + edge * cell}" y2="{y0 + n * cell + 3}" stroke="{INK}" stroke-width="2"/>')
        c.add(f'<line x1="{x0 - 3}" y1="{y0 + edge * cell}" x2="{x0 + n * cell + 3}" y2="{y0 + edge * cell}" stroke="{INK}" stroke-width="2"/>')
    c.text(x0 + n * cell / 2, y0 + n * cell + 26, "CEO (7) and vice presidents (2, 14, 18, 21) are marked in colour", size=12, fill=MUTED)

    bx, by, bw = 570, 110, 66
    c.text(bx + 2 * bw, 70, "Block densities", size=15, weight="700")
    for r in range(4):
        c.text(bx - 8, by + r * bw + bw / 2 + 5, f"P{r} ({sizes[r]})", size=12, anchor="end")
        c.text(bx + r * bw + bw / 2, by - 8, f"P{r}", size=12)
    for r in range(4):
        for s in range(4):
            dd = dens[r][s]
            shade = BLUE if dd >= 0.8 else (SKY if dd >= overall else "#ffffff")
            c.rect(bx + s * bw, by + r * bw, bw, bw, fill=shade, stroke=GRAY, sw=1)
            c.text(bx + s * bw + bw / 2, by + r * bw + bw / 2 + 5, f"{dd:.2f}", size=15, weight="600", fill=PAPER if dd >= 0.8 else INK)
    c.text(bx + 2 * bw, by + 4 * bw + 30, f"Overall density {overall:.3f}. Dark: 0.80 or more. Light: at least that.", size=12, fill=MUTED)
    c.text(bx + 2 * bw, by + 4 * bw + 52, f"Best all-0 or all-1 image makes {err} mistakes; one block makes {min(total, n * (n - 1) - total)}.", size=12, fill=MUTED)
    meta = dict(
        chapter=12,
        caption="The managers' advice table, ordered by four positions from an average-linkage cut of structural-equivalence distances. The blocks are neither empty nor full: this is a rough pattern, not a clean blockmodel. The positions follow level only weakly and department partly.",
        alt=(f"A 21 by 21 grid of cells, blue where a manager goes to another for advice, with heavy lines dividing the managers into four positions of {sizes[0]}, {sizes[1]}, {sizes[2]} and {sizes[3]} managers. "
             f"On the right, a four by four table of block densities. The two diagonal blocks of the last two positions have densities {dens[2][2]:.2f} and {dens[3][3]:.2f}, the block from position 3 to position 1 has {dens[3][1]:.2f}, and the block from position 0 to position 1 has {dens[0][1]:.2f}. "
             f"The densities run from {min(map(min, dens)):.2f} to {max(map(max, dens)):.2f}, so most blocks are neither empty nor full."),
        data={"positions": pos, "sizes": sizes, "density": [[round(x, 3) for x in r] for r in dens], "overall": round(overall, 3), "mistakes": err})
    return c, meta


def blocks_curve():
    a, level = krackhardt()
    n = len(a)
    d = distances(a)
    ks = list(range(1, 7))
    real = [errors(a, cluster(d, k)) for k in ks]
    rng = random.Random(1)
    label_mean = []
    for k in ks:
        pos = cluster(d, k)
        total = 0
        for _ in range(300):
            p = pos[:]
            rng.shuffle(p)
            total += errors(a, p)
        label_mean.append(total / 300)
    refit_mean = [0.0] * 6
    refit_best = [10 ** 9] * 6
    draws = 100
    for _ in range(draws):
        m = [[0] * n for _ in range(n)]
        for i in range(n):
            others = [j for j in range(n) if j != i]
            row = [a[i][j] for j in others]
            rng.shuffle(row)
            for j, v in zip(others, row):
                m[i][j] = v
        dm = distances(m)
        for idx, k in enumerate(ks):
            e = errors(m, cluster(dm, k))
            refit_mean[idx] += e / draws
            refit_best[idx] = min(refit_best[idx], e)
    # The claims in the alt text are checked here, so a change in the data cannot leave a false caption.
    assert all(real[i] < label_mean[i] for i in range(1, 6))
    assert all(real[i] < refit_best[i] for i in range(3, 6)), (real, refit_best)
    W, H = 720, 400
    c = Canvas(W, H, "Mistakes against the number of positions",
               "Lines for the real network and two baselines, for one to six positions.")
    x0, x1, y0, y1 = 80, 580, 60, 330
    def X(k):
        return x0 + (k - 1) / 5 * (x1 - x0)
    def Y(v):
        return y1 - v / 200 * (y1 - y0)
    for v in (0, 50, 100, 150, 200):
        c.add(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{FAINT}" stroke-width="1"/>')
        c.text(x0 - 8, Y(v) + 4, str(v), size=12, anchor="end", fill=MUTED)
    for k in ks:
        c.text(X(k), y1 + 20, str(k), size=12)
    c.text((x0 + x1) / 2, y1 + 42, "number of positions", size=13)
    c.text(x0, y0 - 12, "mistakes", size=13, anchor="start")
    def line(vals, color, dash=None, width=2.5):
        pts = " ".join(f"{X(k):.1f},{Y(v):.1f}" for k, v in zip(ks, vals))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        c.add(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}"{da}/>')
        for k, v in zip(ks, vals):
            c.add(f'<circle cx="{X(k):.1f}" cy="{Y(v):.1f}" r="3.5" fill="{color}"/>')
    line(label_mean, GRAY, "6 4")
    line(refit_mean, ORANGE, "2 4")
    line(refit_best, RED, "8 3")
    line(real, BLUE)
    c.text(x1 + 10, Y(real[-1]) + 4, "real", size=12, anchor="start", fill=BLUE, weight="700")
    c.text(x1 + 10, Y(label_mean[-1]) + 4, "labels shuffled", size=12, anchor="start", fill=MUTED)
    c.text(x1 + 10, Y(refit_mean[-1]) - 4, "refit, mean", size=12, anchor="start", fill=ORANGE)
    c.text(x1 + 10, Y(refit_best[-1]) + 11, "refit, best", size=12, anchor="start", fill=RED)
    c.text(W / 2, 24, "Mistakes of the best all-0 or all-1 image, by number of positions", size=15, weight="700")
    meta = dict(
        chapter=12,
        caption="Mistakes fall as positions are added, for the real network and for every baseline, so falling alone proves nothing. Shuffling labels (grey) is an easy baseline. Redoing the whole procedure on networks that keep each manager's out-degree (orange and red) is a fair one: the real curve is below its best only from four positions on.",
        alt=(f"A line chart of mistakes against one to six positions. The real network, a solid blue line, falls from {real[0]} with one position to {real[1]} with two, {real[3]} with four and {real[5]} with six. "
             f"A grey dashed line for shuffled labels stays well above it. Two lines for networks that keep each manager's out-degree and are clustered again, one for the mean and one for the best of 100 draws, run close to the real line at two and three positions. "
             f"From four positions on the real line is below the best of the redone draws."),
        data={"positions": ks, "real": real, "labels_shuffled_mean": [round(x, 1) for x in label_mean],
              "refit_mean": [round(x, 1) for x in refit_mean], "refit_best": refit_best})
    return c, meta


FIGURES = {
    "positions-six": six,
    "positions-krackhardt": krackhardt_blocks,
    "positions-blocks-curve": blocks_curve,
}

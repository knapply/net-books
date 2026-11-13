"""Figures for the visualization chapter (chapter 5). Standard library only.

The layouts are read from books/sna/data/layouts (made by the engine; see the README there) and
the karate club from books/sna/data/karate. Numbers drawn here are computed from those files and
asserted to match what the chapter's code prints.
"""
import csv
import math
from collections import deque
from pathlib import Path

from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"
GRAY = "#9ca3af"
ORDER = ["random", "circle", "force", "stress", "spectral", "mds"]


def read(name):
    with open(DATA / name) as f:
        return list(csv.DictReader(f))


def club():
    nodes = read("karate/nodes.csv")
    faction = [r["faction"] for r in nodes]
    ties = [(int(r["source"]) - 1, int(r["target"]) - 1) for r in read("karate/edges.csv")]
    assert len(faction) == 34 and len(ties) == 78
    return faction, ties


def layouts():
    out = {}
    for r in read("layouts/karate_layouts.csv"):
        out.setdefault(r["layout"], []).append((float(r["x"]), float(r["y"])))
    return out


def seeds():
    out = {}
    for r in read("layouts/fr_seeds.csv"):
        out.setdefault(int(r["seed"]), []).append((float(r["x"]), float(r["y"])))
    return out


def distances(ties):
    adj = [[] for _ in range(34)]
    for a, b in ties:
        adj[a].append(b)
        adj[b].append(a)
    d = []
    for s in range(34):
        dist = [None] * 34
        dist[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if dist[v] is None:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        d.append(dist)
    return d


def scale_free_stress(points, d):
    pairs = [(i, j) for i in range(34) for j in range(i + 1, 34)]
    p = [math.dist(points[i], points[j]) for i, j in pairs]
    g = [d[i][j] for i, j in pairs]
    s = sum(a / b for a, b in zip(p, g)) / sum((a / b) ** 2 for a, b in zip(p, g))
    return sum(((s * a - b) / b) ** 2 for a, b in zip(p, g)) / len(p)


def fit(points, x0, y0, size):
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    return [(x0 + size / 2 + (x - cx) / span * size, y0 + size / 2 + (y - cy) / span * size) for x, y in points]


def draw_club(c, points, faction, ties, x0, y0, size, r=4.2):
    pos = fit(points, x0, y0, size)
    for a, b in ties:
        c.add(f'<line x1="{pos[a][0]:.1f}" y1="{pos[a][1]:.1f}" x2="{pos[b][0]:.1f}" y2="{pos[b][1]:.1f}" '
              f'stroke="{GRAY}" stroke-width="0.7" opacity="0.6"/>')
    for i, (x, y) in enumerate(pos):
        if faction[i] == "Mr. Hi":
            c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{BLUE}" stroke="{PAPER}" stroke-width="0.8"/>')
        else:
            c.add(f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}" fill="{ORANGE}" stroke="{PAPER}" stroke-width="0.8"/>')


def karate_layouts():
    faction, ties = club()
    lay = layouts()
    w, h = 780, 560
    c = Canvas(w, h, "Six layouts of the karate club",
               "The same 34 members and 78 ties drawn with a random, circle, force, stress, spectral and classical scaling layout.")
    names = {"random": "Random", "circle": "Circle", "force": "Force (Fruchterman-Reingold)", "stress": "Stress",
             "spectral": "Spectral (Laplacian)", "mds": "Classical scaling"}
    for k, key in enumerate(ORDER):
        col, row = k % 3, k // 3
        x0, y0 = 20 + col * 254, 40 + row * 262
        c.text(x0 + 115, y0 - 14, names[key], size=14, weight="600")
        c.rect(x0, y0, 230, 230, stroke=FAINT, sw=1)
        draw_club(c, lay[key], faction, ties, x0 + 10, y0 + 10, 210)
    c.text(w / 2, h - 12, "Blue circles: Mr. Hi's side. Orange squares: the officer's side. Gray lines: ties.", size=13, fill=MUTED)
    meta = dict(chapter=5,
                caption="One club, six layouts. Blue circles are Mr. Hi's members and orange squares the officer's; nothing about the data changes between panels.",
                alt="Six small drawings of the same 34-member network with 78 gray ties. Random scatters the members across the square. Circle puts them on a ring with ties crossing the middle. Force and stress show two loose clusters, blue circles on the left and orange squares on the right. Classical scaling shows blue circles together at the upper right and orange squares spread across the left. Spectral piles most members into one small clump near the middle, with a few blue circles strung out toward the top and the lower right.",
                data={"layouts": ORDER})
    return c, meta


def layout_quality():
    faction, ties = club()
    d = distances(ties)
    lay = layouts()
    vals = {k: scale_free_stress(lay[k], d) for k in ORDER}
    expected = {"random": 0.377, "circle": 0.292, "force": 0.089, "stress": 0.068, "spectral": 0.387, "mds": 0.131}
    for k in ORDER:
        assert round(vals[k], 3) == expected[k], (k, vals[k])
    w, h = 680, 330
    c = Canvas(w, h, "Stress of six layouts",
               "Bars for the scale-free stress of the random, circle, force, stress, spectral and classical scaling layouts.")
    c.text(w / 2, 26, "Scale-free stress of the karate layouts (lower is better)", size=15, weight="600")
    left, top, bar, gap, maxw = 130, 52, 28, 14, 460
    for i, k in enumerate(ORDER):
        y = top + i * (bar + gap)
        c.text(left - 10, y + bar / 2 + 5, k, size=14, anchor="end")
        wd = vals[k] / 0.4 * maxw
        c.rect(left, y, wd, bar, fill=(BLUE if k in ("force", "stress", "mds") else GRAY), stroke="none", sw=0)
        c.text(left + wd + 8, y + bar / 2 + 5, f"{vals[k]:.3f}", size=13, anchor="start")
    c.text(w / 2, h - 12, "Blue bars: the three layouts that work from graph distances.", size=13, fill=MUTED)
    meta = dict(chapter=5,
                caption="Scale-free stress of the six karate layouts. The three layouts that use graph distances (force, stress, classical scaling) score far lower than random, circle and spectral.",
                alt="A horizontal bar chart of six layouts. Random 0.377, circle 0.292, force 0.089, stress 0.068, spectral 0.387 and classical scaling 0.131. The force, stress and classical scaling bars are blue and the others gray. Spectral has the longest bar and stress the shortest.",
                data={"stress": {k: round(vals[k], 3) for k in ORDER}})
    return c, meta


def layout_seeds():
    faction, ties = club()
    d = distances(ties)
    runs = seeds()
    shown = [1, 2, 3, 4]
    w, h = 780, 330
    c = Canvas(w, h, "One force layout, four seeds",
               "The force layout of the karate club started from four different seeds.")
    for k, s in enumerate(shown):
        x0 = 20 + k * 190
        c.text(x0 + 85, 26, f"seed {s}", size=14, weight="600")
        c.rect(x0, 38, 170, 170, stroke=FAINT, sw=1)
        draw_club(c, runs[s], faction, ties, x0 + 8, 46, 154, r=3.4)
        c.text(x0 + 85, 228, f"stress {scale_free_stress(runs[s], d):.3f}", size=13, fill=MUTED)
    stresses = [scale_free_stress(runs[s], d) for s in runs]
    assert f"{min(stresses):.3f}" == "0.087" and f"{max(stresses):.3f}" == "0.094"
    c.text(w / 2, 276, "Across all 20 seeds the stress runs from 0.087 to 0.094.", size=13, fill=MUTED)
    c.text(w / 2, 298, "The engine's force layout barely moves with its seed; do not expect that of every tool.", size=13, fill=MUTED)
    meta = dict(chapter=5,
                caption="The same force layout from four seeds. In this engine the pictures are close to identical; the scale-free stress over all twenty seeds runs from 0.087 to 0.094.",
                alt="Four small drawings of the karate club side by side, labeled seed 1 to seed 4, each with its stress value underneath. All four show the same two loose clusters of blue circles and orange squares in nearly the same places.",
                data={"seeds": shown})
    return c, meta


def encoding_area():
    w, h = 700, 330
    c = Canvas(w, h, "Radius or area for degree",
               "Circles for degrees 1, 4, 9 and 17, drawn once with radius proportional to degree and once with radius proportional to its square root.")
    degs = [1, 4, 9, 17]
    c.text(w / 2, 26, "Node size for degree: which scale says what the data says?", size=15, weight="600")
    for row, (label, f) in enumerate([("radius = 2 x degree", lambda k: 2 * k), ("radius = 2 x sqrt(degree)", lambda k: 2 * math.sqrt(k))]):
        y = 130 + row * 130 if row == 0 else 255
        c.text(20, 62 + row * 150 if row == 0 else 212, label, size=14, weight="600", anchor="start")
        x = 90
        for k in degs:
            r = f(k)
            cy = 130 if row == 0 else 262
            c.add(f'<circle cx="{x + r:.1f}" cy="{cy - 0}" r="{r:.1f}" fill="{BLUE}" opacity="0.85"/>')
            c.text(x + r, cy + max(r, 14) + 16, f"degree {k}", size=12, fill=MUTED)
            x += 2 * r + 60
    c.text(w - 20, 150, "areas differ 289 to 1", size=13, anchor="end", fill=RED, weight="600")
    c.text(w - 20, 270, "areas differ 17 to 1", size=13, anchor="end", fill=BLUE, weight="600")
    meta = dict(chapter=5,
                caption="Two ways to size nodes by degree. With radius proportional to degree, the biggest circle covers 289 times the area of the smallest while the degree ratio is 17. With radius proportional to the square root, area matches degree.",
                alt="Two rows of four blue circles for degrees 1, 4, 9 and 17. In the top row, radius grows in step with degree and the last circle is much larger than the others. In the bottom row, radius grows with the square root of degree and the circles grow gently. Labels say the areas differ 289 to 1 on top and 17 to 1 below.",
                data={"degrees": degs})
    return c, meta


def karate_matrix():
    faction, ties = club()
    order_file = list(range(34))
    order_sorted = sorted(range(34), key=lambda v: (faction[v] != "Mr. Hi", v))
    tie_set = {(a, b) for a, b in ties} | {(b, a) for a, b in ties}
    w, h = 740, 450
    c = Canvas(w, h, "The karate matrix, two orders",
               "The adjacency matrix of the karate club in file order and sorted by faction.")
    cell = 9.6
    for k, (title, order) in enumerate([("Rows in file order", order_file), ("Rows sorted by faction", order_sorted)]):
        x0, y0 = 30 + k * 365, 56
        c.text(x0 + 34 * cell / 2, 32, title, size=14, weight="600")
        c.rect(x0, y0, 34 * cell, 34 * cell, fill=PAPER, stroke=GRAY, sw=1)
        filled = 0
        for i, a in enumerate(order):
            for j, b in enumerate(order):
                if (a, b) in tie_set:
                    filled += 1
                    c.add(f'<rect x="{x0 + j * cell:.1f}" y="{y0 + i * cell:.1f}" width="{cell}" height="{cell}" fill="{BLUE}"/>')
        assert filled == 156
        if k == 1:
            for lo, hi in [(0, 17), (17, 34)]:
                c.rect(x0 + lo * cell, y0 + lo * cell, (hi - lo) * cell, (hi - lo) * cell, stroke=RED, sw=2)
    c.text(w / 2, h - 30, "Each filled cell is a tie (78 ties, 156 cells). Outlined squares: the two factions, 17 members each.", size=13, fill=MUTED)
    c.text(w / 2, h - 10, "Ties inside the outlined squares: 67 of 78. Ties between factions: 11.", size=13, fill=MUTED)
    meta = dict(chapter=5,
                caption="The same karate matrix twice. In file order the ties look scattered; sorted by faction, 67 of the 78 ties fall inside the two outlined squares along the diagonal and 11 lie between them.",
                alt="Two 34 by 34 grids of cells. In the left grid, rows in file order, filled blue cells crowd the top-left and bottom-right corners and are scattered elsewhere. In the right grid, the members are sorted by faction and two outlined squares along the diagonal, each 17 by 17, hold most of the filled cells, with a few filled cells outside them.",
                data={"ties_within": 67, "ties_between": 11})
    return c, meta


FIGURES = {"karate-layouts": karate_layouts, "layout-quality": layout_quality, "layout-seeds": layout_seeds,
           "encoding-area": encoding_area, "karate-matrix": karate_matrix}

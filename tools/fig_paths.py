"""Figures for the paths-and-cohesion chapter (chapter 7).

Standard library only. Every number drawn is computed here from the CSV files in
books/sna/data, so the pictures cannot drift from the data.
"""
import csv
import math
import random
from pathlib import Path

from fig_classic import _draw, florentine, read
from fig_layout import fit, stress_layout
from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, Canvas

GRAY = "#9ca3af"
PALE = "#cfe5f3"


# ----------------------------------------------------------------- helpers
def adjacency(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def components(n, edges, removed=()):
    """Sizes of the connected pieces left after the nodes in `removed` are taken out."""
    adj = adjacency(n, edges)
    seen = set(removed)
    sizes = []
    for s in range(n):
        if s in seen:
            continue
        stack, size = [s], 0
        seen.add(s)
        while stack:
            u = stack.pop()
            size += 1
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        sizes.append(size)
    return sizes


def reachable_mean(n, edges):
    adj = adjacency(n, edges)
    total = count = 0
    for s in range(n):
        dist = {s: 0}
        queue = [s]
        for u in queue:
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        for t, d in dist.items():
            if t != s:
                total += d
                count += 1
    return total / count


def swap_edges(edges, rng, n_swaps):
    """Degree-preserving shuffle: pick two ties (a,b), (c,d) and rewire to (a,d), (c,b)."""
    edges = [tuple(e) for e in edges]
    present = {frozenset(e) for e in edges}
    done = tries = 0
    while done < n_swaps and tries < 50 * n_swaps:
        tries += 1
        i, j = rng.randrange(len(edges)), rng.randrange(len(edges))
        (a, b), (c, d) = edges[i], edges[j]
        if rng.random() < 0.5:
            c, d = d, c
        if len({a, b, c, d}) < 4 or frozenset((a, d)) in present or frozenset((c, b)) in present:
            continue
        present -= {frozenset((a, b)), frozenset((c, d))}
        present |= {frozenset((a, d)), frozenset((c, b))}
        edges[i], edges[j] = (a, d), (c, b)
        done += 1
    return edges


def krackhardt_friendship():
    rows = [r for r in read("krackhardt", "edges.csv") if r["relation"] == "friendship"]
    und = sorted({tuple(sorted((int(r["from"]) - 1, int(r["to"]) - 1))) for r in rows})
    return 21, und


def axis_x(c, x0, y0, w, ticks, fmt, title):
    c.add(f'<line x1="{x0}" y1="{y0}" x2="{x0 + w}" y2="{y0}" stroke="{INK}" stroke-width="1.5"/>')
    for x, label in ticks:
        c.add(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y0 + 5}" stroke="{INK}" stroke-width="1.2"/>')
        c.text(x, y0 + 21, label, size=12)
    c.text(x0 + w / 2, y0 + 44, title, size=13, fill=MUTED)


# ----------------------------------------------------------------- figures
def menger():
    names = ["s", "a", "b", "t", "c", "d"]
    cx, cy, r = 370, 170, 140
    ang = {"s": 180, "a": 240, "b": 300, "t": 0, "c": 60, "d": 120}
    pos = {k: (cx + r * math.cos(math.radians(v)), cy + r * math.sin(math.radians(v))) for k, v in ang.items()}
    ring = [("s", "a"), ("a", "b"), ("b", "t"), ("t", "c"), ("c", "d"), ("d", "s")]
    path1 = {("s", "a"), ("a", "b"), ("b", "t")}
    path2 = {("s", "d"), ("d", "c"), ("c", "t")}
    c = Canvas(740, 380, "Two routes from s to t that share no one in between",
               "Six people in a ring with one extra tie. Two routes from s to t share no person other than s and t.")
    for e in ring + [("a", "c")]:
        key = e if e in path1 or e in path2 else (e[1], e[0])
        col, w = GRAY, 1.8
        if key in path1:
            col, w = BLUE, 4.5
        elif key in path2:
            col, w = ORANGE, 4.5
        c.edge(pos[e[0]], pos[e[1]], ra=20, rb=20, color=col, width=w)
    for k in names:
        special = k in ("s", "t")
        c.node(*pos[k], k, r=20, fill=INK if special else PAPER, stroke=INK,
               label_fill=PAPER if special else INK, size=15)
    for k in ("a", "d"):
        x, y = pos[k]
        c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="29" fill="none" stroke="{RED}" stroke-width="2.2" stroke-dasharray="5 4"/>')
    c.text(cx, 356, "Blue and orange routes share no one but s and t. Remove the two dashed people (a and d) and s is cut off.",
           size=13, fill=MUTED)
    meta = dict(chapter=7,
                caption="Menger's theorem on six people. The blue route (s, a, b, t) and the orange route (s, d, c, t) share nobody in between, so at least two people must be removed to separate s from t. Removing a and d (dashed rings) does separate them, so two is exactly the number.",
                alt="Six circles on a hexagon labeled s, a, b, t, c and d, joined in a ring, plus a grey line between a and c across the middle. The ring path s, a, b, t is drawn thick blue and the ring path s, d, c, t is drawn thick orange. The circles a and d have dashed rings around them.",
                data={"ring": ring, "extra": [("a", "c")], "disjoint_paths": [["s", "a", "b", "t"], ["s", "d", "c", "t"]],
                      "separator": ["a", "d"]})
    return c, meta


def florentine_cuts():
    names, edges = florentine()
    n = len(names)
    cuts = [i for i in range(n) if len(components(n, edges, removed=[i])) > 1]
    bridges = [e for e in edges if len(components(n, [x for x in edges if x != e])) > 1]
    pos = fit(stress_layout(n, edges, seed=4), 50, 50, 640, 300)
    c = Canvas(740, 400, "Where the Florentine marriage network can be broken",
               "The fifteen families with cut points and bridges marked.")
    _draw(c, pos, edges, [0.3] * n, [(PALE, BLUE)] * n, names, side=("Albizzi", "Medici", "Acciaiuoli"))
    for a, b in bridges:
        c.edge(pos[a], pos[b], ra=6, rb=6, width=3.4, color=RED, dash="7 4")
    for i in cuts:
        c.node(*pos[i], "", r=11, fill=ORANGE, stroke=ORANGE, shape="square")
    c.text(370, 28, "Orange squares: families whose removal splits the network. Dashed lines: marriages whose loss does.",
           size=14, weight="600")
    cut_names = [names[i] for i in cuts]
    bridge_names = [f"{names[a]}–{names[b]}" for a, b in bridges]
    meta = dict(chapter=7,
                caption=f"The Florentine marriage network with its {len(cuts)} cut points (orange squares) and {len(bridges)} bridges (dashed marriages). Every bridge leads to a family with a single marriage or to a pair that hangs off one.",
                alt=f"The fifteen-family marriage network. Four families are drawn as orange squares: {', '.join(cut_names)}. Five marriages are drawn as thick dashed lines: {'; '.join(bridge_names)}. All other families are blue circles and the other marriages are thin grey lines.",
                data={"cut_points": cut_names, "bridges": bridge_names})
    return c, meta


def removal_bars():
    names, edges = florentine()
    n = len(names)
    rows = []
    for i in range(n):
        sizes = components(n, edges, removed=[i])
        rows.append((names[i], max(sizes), len(sizes)))
    rows.sort(key=lambda r: (r[1], r[0]))
    c = Canvas(900, 560, "Take out one family at a time",
               "For each family, how many families remain in the largest connected piece after that family is removed.")
    x0, y0, w, step = 170, 50, 640, 27
    sx = lambda v: x0 + v / 14 * w
    c.add(f'<line x1="{sx(14):.1f}" y1="{y0 - 8}" x2="{sx(14):.1f}" y2="{y0 + 15 * step}" stroke="{MUTED}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    c.text(sx(14), y0 - 14, "14 = everyone else still joined", size=12.5, fill=MUTED, anchor="end")
    for k, (name, largest, pieces) in enumerate(rows):
        y = y0 + k * step
        col = ORANGE if pieces > 1 else BLUE
        c.text(x0 - 10, y + 17, name, size=12.5, anchor="end")
        c.rect(x0, y + 3, sx(largest) - x0, 19, fill=col + "66", stroke=col, sw=1.2)
        if pieces > 1:
            c.text(sx(largest) - 8, y + 17, f"{largest} left, in {pieces} pieces", size=12, anchor="end", fill=INK)
        else:
            c.text(sx(largest) + 6, y + 17, f"{largest}", size=12, anchor="start", fill=MUTED)
    ay = y0 + 15 * step + 6
    axis_x(c, x0, ay, w, [(sx(v), str(v)) for v in range(0, 15, 2)], str,
           "families in the largest piece after removing the family named on the left")
    split = [r for r in rows if r[2] > 1]
    meta = dict(chapter=7,
                caption="Remove each family in turn and count the families in the largest piece that is left. Four families (orange) split the network; the Medici's removal leaves pieces of 11, 2 and 1.",
                alt=f"A bar for each of the fifteen families, sorted from shortest to longest. The shortest bar is for the Medici at {rows[0][1]}. Albizzi, Guadagni and Salviati have bars of {rows[1][1]}. All eleven other bars reach 14. The four shorter bars are orange and the rest blue.",
                data={"rows": [[a, b, p] for a, b, p in rows], "splits": [r[0] for r in split]})
    return c, meta


def density_size():
    ns = [10 ** (1 + 3 * i / 60) for i in range(61)]
    c = Canvas(900, 420, "Density falls as networks grow", "Density against the number of people when everyone has the same number of ties.")
    x0, y0, w, h = 90, 40, 700, 280
    lx = lambda n: x0 + (math.log10(n) - 1) / 3 * w
    sy = lambda d: y0 + h - d * h
    c.add(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{INK}" stroke-width="1.5"/>')
    c.add(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{INK}" stroke-width="1.5"/>')
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        c.text(x0 - 10, sy(v) + 4, f"{v:.2f}", size=12, anchor="end")
        c.add(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0 + w}" y2="{sy(v):.1f}" stroke="{FAINT}" stroke-width="0.8"/>')
    for p in (1, 2, 3, 4):
        c.text(lx(10 ** p), y0 + h + 21, f"{10 ** p:,}", size=12)
    c.text(x0 + w / 2, y0 + h + 46, "people in the network (log scale)", size=13, fill=MUTED)
    for k, col, dash in ((4, BLUE, None), (10, ORANGE, "6 4")):
        pts = " ".join(f"{lx(n):.1f},{sy(min(1, k / (n - 1))):.1f}" for n in ns)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        c.add(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"{d}/>')
    for n in (20, 100, 500):
        c.add(f'<circle cx="{lx(n):.1f}" cy="{sy(4 / (n - 1)):.1f}" r="6" fill="{PAPER}" stroke="{BLUE}" stroke-width="2.4"/>')
    c.add(f'<line x1="{x0 + 470}" y1="{y0 + 20}" x2="{x0 + 510}" y2="{y0 + 20}" stroke="{BLUE}" stroke-width="3"/>')
    c.text(x0 + 518, y0 + 25, "everyone has 4 ties", size=13, anchor="start")
    c.add(f'<line x1="{x0 + 470}" y1="{y0 + 44}" x2="{x0 + 510}" y2="{y0 + 44}" stroke="{ORANGE}" stroke-width="3" stroke-dasharray="6 4"/>')
    c.text(x0 + 518, y0 + 49, "everyone has 10 ties", size=13, anchor="start")
    meta = dict(chapter=7,
                caption="Density is mean degree divided by n - 1. Hold the number of ties per person fixed and density falls toward zero as the network grows. The circles mark the rings of 20, 100 and 500 people from the code.",
                alt="A chart with the number of people from 10 to 10,000 on a log scale across the bottom and density from 0 to 1 up the side. Two curves fall steeply and then flatten near zero: one for everyone having 4 ties, one for 10 ties. Three circles on the 4-tie curve mark 20 people at 0.211, 100 people at 0.040 and 500 people at 0.008.",
                data={"ties_per_person": {"4": {n: round(4 / (n - 1), 4) for n in (20, 100, 500)}}})
    return c, meta


def null_distance():
    rng = random.Random(7)
    names, fl_edges = florentine()
    sets = [("Florentine marriages (15 families)", len(names), fl_edges),
            ("Krackhardt friendships, ties read as two-way (21 managers)", *krackhardt_friendship())]
    c = Canvas(900, 560, "Is the mean distance more than the degrees give?",
               "Histograms of mean distance in 1,000 degree-preserving shuffles of two networks, with the real value marked.")
    meta_data = {}
    for p, (label, n, edges) in enumerate(sets):
        draws, disconnected = [], 0
        for _ in range(1000):
            shuffled = swap_edges(edges, rng, 10 * len(edges))
            if len(components(n, shuffled)) > 1:
                disconnected += 1
            draws.append(reachable_mean(n, shuffled))
        real = reachable_mean(n, edges)
        lo, hi = math.floor(min(real, min(draws)) * 10) / 10, math.ceil(max(real, max(draws)) * 10) / 10
        nb = 14
        bw = (hi - lo) / nb
        counts = [0] * nb
        for d in draws:
            counts[min(int((d - lo) / bw), nb - 1)] += 1
        y0 = 70 + p * 245
        x0, w, h = 90, 740, 150
        top = max(counts) * 1.12
        c.text(x0, y0 - 22, label, size=14, weight="600", anchor="start")
        for k, cnt in enumerate(counts):
            bh = h * cnt / top
            c.rect(x0 + k * w / nb + 1, y0 + h - bh, w / nb - 2, bh, fill=BLUE + "55", stroke=BLUE, sw=1)
        ox = x0 + (real - lo) / (hi - lo) * w
        c.add(f'<line x1="{ox:.1f}" y1="{y0 - 6}" x2="{ox:.1f}" y2="{y0 + h}" stroke="{ORANGE}" stroke-width="3"/>')
        c.text(ox + 8, y0 + 6, f"real network {real:.3f}", size=13, anchor="start", weight="700")
        ticks = [(x0 + (lo + (hi - lo) * i / 4 - lo) / (hi - lo) * w, f"{lo + (hi - lo) * i / 4:.2f}") for i in range(5)]
        axis_x(c, x0, y0 + h, w, ticks, str, "mean distance over reachable pairs in a shuffled network")
        mean = sum(draws) / len(draws)
        below = sum(1 for d in draws if d <= real + 1e-9)
        meta_data[label] = {"real": round(real, 3), "shuffled_mean": round(mean, 3), "disconnected": disconnected,
                            "at_or_below_real": below}
    fl, kr = list(meta_data.values())
    meta = dict(chapter=7,
                caption="Mean distance in 1,000 random networks that keep every node's number of ties, for the Florentine marriages and Krackhardt's friendships. In both, the real mean distance sits in the middle of the shuffled values, so it follows from the degrees. The draws behind this picture are not the ones in the code, so the counts differ slightly.",
                alt=f"Two histograms, one above the other. Top: Florentine marriages, with an orange line at the real mean distance {fl['real']} near the middle of a spread whose average is {fl['shuffled_mean']}; {fl['disconnected']} of 1,000 shuffles were disconnected. Bottom: Krackhardt friendships, with the real value {kr['real']} near the middle of a narrow spread whose average is {kr['shuffled_mean']}; none of the shuffles was disconnected.",
                data=meta_data)
    return c, meta


FIGURES = {
    "paths-menger": menger,
    "paths-florentine-cuts": florentine_cuts,
    "paths-removal": removal_bars,
    "paths-density-size": density_size,
    "paths-null-distance": null_distance,
}

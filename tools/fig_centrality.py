"""Figures for the centrality chapter (chapter 6).

Standard library only. Every number drawn is computed here, by brute force, from the
networks defined below, so the pictures cannot drift from the chapter.
"""
import math
from itertools import combinations

from fig_classic import betweenness
from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, Canvas

GRAY = "#9ca3af"
PALE = "#cfe5f3"


def connector_network():
    """Two groups of four, each fully tied inside, joined only through node 8."""
    edges = list(combinations(range(4), 2)) + list(combinations(range(4, 8), 2)) + [(8, 0), (8, 4)]
    return 9, edges


def degrees(n, edges):
    d = [0] * n
    for a, b in edges:
        d[a] += 1
        d[b] += 1
    return d


def connector():
    n, edges = connector_network()
    deg, btw = degrees(n, edges), betweenness(n, edges)
    pos = {0: (170, 175), 1: (60, 80), 2: (40, 250), 3: (160, 320), 4: (460, 175), 5: (570, 80),
           6: (590, 250), 7: (470, 320), 8: (315, 175)}
    c = Canvas(640, 400, "A connector between two groups, sized two ways",
               "The same nine-person network twice. Left: dot area follows number of ties. Right: dot area follows betweenness.")
    c.text(160, 30, "Sized by degree", size=15, weight="700")
    c.text(480, 30, "Sized by betweenness", size=15, weight="700")
    for panel, (scores, top) in enumerate([(deg, max(deg)), (btw, max(btw))]):
        p = {k: (x * 0.5 + (0 if panel == 0 else 320), y * 0.9 + 20) for k, (x, y) in pos.items()}
        for a, b in edges:
            c.edge(p[a], p[b], ra=2, rb=2, color=GRAY, width=1.6)
        for k in range(n):
            r = 4 + 20 * scores[k] / top
            hot = k == 8
            c.node(*p[k], "", r=r, fill=ORANGE if hot else PALE, stroke=RED if hot else BLUE, sw=2)
        label = f"{scores[8]:.0f}"
        c.text(p[8][0], p[8][1] + 46, f"connector: {label}", size=13, weight="700")
    meta = dict(chapter=6,
                caption="One network, two pictures. By number of ties the connector (orange) is the smallest dot in the picture; by betweenness it is the largest, because every route between the two groups runs through it.",
                alt=(f"Two drawings of the same nine dots: two groups of four dots, each group tied all round, with one dot in the middle tied to one member of each group. "
                     f"On the left, dot size follows the number of ties: the middle dot has {deg[8]} ties, the two members it touches have {deg[0]} each, and the other six members have {deg[1]} each, so the middle dot is the smallest. "
                     f"On the right, dot size follows betweenness: the middle dot is largest at {btw[8]:.0f}, the two members it touches score {btw[0]:.0f} each, and the other six score 0."),
                data={"edges": [list(e) for e in edges], "degree": deg, "betweenness": btw})
    return c, meta


def path_scores(k):
    """Middle-node scores in a path of k people, by brute force (distances from the middle)."""
    mid = k // 2
    s = sum(abs(i - mid) for i in range(k) if i != mid)
    close = (k - 1) / s
    n_pairs = (k - 1) * (k - 2) / 2
    left, right = mid, k - 1 - mid
    return left * right / n_pairs, close, 2 / (k - 1)


def size_dependence():
    ks = [3, 5, 7, 11, 21, 31, 51, 71, 101]
    c = Canvas(700, 400, "How scores change as a line of people gets longer",
               "Three curves for the middle person of a line of n people, drawn against n on a log scale.")
    x0, y0, w, h = 80, 40, 580, 270
    lo, hi = math.log(3), math.log(101)
    xs = lambda k: x0 + (math.log(k) - lo) / (hi - lo) * w
    ys = lambda v: y0 + h - v * h
    c.add(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{INK}" stroke-width="1.5"/>')
    c.add(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{INK}" stroke-width="1.5"/>')
    for v in (0, 0.25, 0.5, 0.75, 1):
        c.add(f'<line x1="{x0 - 5}" y1="{ys(v):.1f}" x2="{x0}" y2="{ys(v):.1f}" stroke="{INK}"/>')
        c.text(x0 - 10, ys(v) + 4, f"{v:g}", size=12, anchor="end")
    for k in (3, 11, 31, 101):
        c.add(f'<line x1="{xs(k):.1f}" y1="{y0 + h}" x2="{xs(k):.1f}" y2="{y0 + h + 5}" stroke="{INK}"/>')
        c.text(xs(k), y0 + h + 21, str(k), size=12)
    c.text(x0 + w / 2, y0 + h + 46, "people in the line (log scale)", size=13, fill=MUTED)
    rows = [path_scores(k) for k in ks]
    for idx, (label, color, dash) in enumerate([("betweenness share", ORANGE, None), ("closeness", BLUE, None), ("degree share", RED, "6 4")]):
        pts = " ".join(f"{xs(k):.1f},{ys(r[idx]):.1f}" for k, r in zip(ks, rows))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        c.add(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"{da}/>')
        for k, r in zip(ks, rows):
            c.add(f'<circle cx="{xs(k):.1f}" cy="{ys(r[idx]):.1f}" r="3.5" fill="{color}"/>')
        where = [(xs(31), ys(rows[ks.index(31)][0]) - 12, "middle"), (xs(11) + 12, ys(rows[ks.index(11)][1]) - 12, "start"),
                 (xs(11) - 10, ys(rows[ks.index(11)][2]) + 22, "end")][idx]
        c.text(where[0], where[1], label, size=13, anchor=where[2], weight="700", fill=color)
    last = rows[-1]
    meta = dict(chapter=6,
                caption="The middle person of a line of n people. The share of shortest routes they sit on settles near one half, while closeness and the degree share both fall toward zero as the line grows.",
                alt=(f"A line chart against the number of people in the line, from 3 to 101 on a log scale. The betweenness share starts at 1 for 3 people and falls to {last[0]:.3f} at 101. "
                     f"Closeness falls from 1 at 3 people to {last[1]:.3f} at 101. The degree share falls from 1 at 3 people to {last[2]:.3f} at 101."),
                data={"n": ks, "betweenness_share": [r[0] for r in rows], "closeness": [r[1] for r in rows], "degree_share": [r[2] for r in rows]})
    return c, meta


FIGURES = {
    "centrality-connector": connector,
    "centrality-size": size_dependence,
}

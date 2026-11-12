"""Figures for the chapter on dyads, triads and motifs.

Standard library only. The census-against-null figure is computed here from the
Krackhardt CSV in books/sna/data: the observed triad census, 1,000 draws that keep the
dyad census (the conditional uniform U|MAN null), and 1,000 degree-preserving draws made
by a chain of two-arc swaps. The small hand-worked networks are spelled out below.
"""
import itertools
import random
from pathlib import Path

from fig_classic import read
from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, PURPLE, RED, Canvas

NAMES = ["003", "012", "102", "021D", "021U", "021C", "111D", "111U",
         "030T", "030C", "201", "120D", "120U", "120C", "210", "300"]
PALE = "#cfe5f3"
SEED = 7


def triad_type(arcs, a, b, c):
    """Holland and Leinhardt's type of the triple (a, b, c) in the arc set `arcs`."""
    trio = (a, b, c)
    pairs = list(itertools.combinations(trio, 2))
    mutual = [p for p in pairs if p in arcs and p[::-1] in arcs]
    asym = [(u, v) for u, v in itertools.permutations(trio, 2) if (u, v) in arcs and (v, u) not in arcs]
    m, s = len(mutual), len(asym)
    n = 3 - m - s
    fixed = {(0, 0, 3): "003", (0, 1, 2): "012", (1, 0, 2): "102", (2, 0, 1): "201",
             (2, 1, 0): "210", (3, 0, 0): "300"}
    if (m, s, n) in fixed:
        return fixed[(m, s, n)]
    tails = [u for u, _ in asym]
    heads = [v for _, v in asym]
    if (m, s, n) == (0, 2, 1):
        if tails[0] == tails[1]:
            return "021D"
        return "021U" if heads[0] == heads[1] else "021C"
    if (m, s, n) == (1, 1, 1):
        return "111D" if heads[0] in mutual[0] else "111U"
    if (m, s, n) == (0, 3, 0):
        return "030T" if max(tails.count(x) for x in trio) == 2 else "030C"
    # (1, 2, 0)
    if tails[0] == tails[1]:
        return "120D"
    return "120U" if heads[0] == heads[1] else "120C"


def census(arcs, n):
    counts = dict.fromkeys(NAMES, 0)
    for a, b, c in itertools.combinations(range(n), 3):
        counts[triad_type(arcs, a, b, c)] += 1
    return counts


def krackhardt_advice():
    rows = read("krackhardt", "edges.csv")
    return {(int(r["from"]) - 1, int(r["to"]) - 1) for r in rows if r["relation"] == "advice"}


def uman_draw(n, mutual, asym, rng):
    pairs = list(itertools.combinations(range(n), 2))
    rng.shuffle(pairs)
    arcs = set()
    for u, v in pairs[:mutual]:
        arcs |= {(u, v), (v, u)}
    for u, v in pairs[mutual:mutual + asym]:
        arcs.add((u, v) if rng.random() < 0.5 else (v, u))
    return arcs


def swap_chain(arcs, n, burn, thin, draws, rng):
    """Draws from a chain of two-arc swaps: a->b and c->d become a->d and c->b."""
    e = sorted(arcs)
    have = set(e)

    def run(k):
        for _ in range(k):
            i, j = rng.randrange(len(e)), rng.randrange(len(e))
            (a, b), (c, d) = e[i], e[j]
            if i == j or a == d or c == b or (a, d) in have or (c, b) in have:
                continue
            have.discard((a, b))
            have.discard((c, d))
            have.add((a, d))
            have.add((c, b))
            e[i], e[j] = (a, d), (c, b)

    run(burn)
    for _ in range(draws):
        run(thin)
        yield set(have)


def percentile(sorted_values, q):
    k = (len(sorted_values) - 1) * q
    lo = int(k)
    hi = min(lo + 1, len(sorted_values) - 1)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (k - lo)


def census_against_null():
    arcs = krackhardt_advice()
    n = 21
    mutual = sum(1 for (u, v) in arcs if u < v and (v, u) in arcs)
    asym = len(arcs) - 2 * mutual
    obs = census(arcs, n)
    rng = random.Random(SEED)
    uman = [census(uman_draw(n, mutual, asym, rng), n) for _ in range(1000)]
    deg = [census(g, n) for g in swap_chain(arcs, n, 4000, 400, 1000, rng)]

    def band(draws, k):
        vals = sorted(d[k] for d in draws)
        return percentile(vals, 0.025), percentile(vals, 0.975)

    c = Canvas(900, 640, "The triad census of Krackhardt's advice network against two nulls",
               "A bar for each of the sixteen triad types showing how many of the 1,330 triples of managers are of that type, with the central 95 percent of two kinds of random network drawn over it.")
    left, right, top, step = 120, 860, 70, 31
    xmax = 300.0
    sx = lambda v: left + (right - left) * v / xmax  # noqa: E731
    for t in range(0, 301, 50):
        c.add(f'<line x1="{sx(t):.1f}" y1="{top - 8}" x2="{sx(t):.1f}" y2="{top + 16 * step - 8}" stroke="{FAINT}" stroke-width="1"/>')
        c.text(sx(t), top + 16 * step + 12, str(t), size=12, fill=MUTED)
    c.text((left + right) / 2, top + 16 * step + 34, "number of triples of managers", size=13, fill=MUTED)
    rows = {}
    for i, k in enumerate(NAMES):
        y = top + i * step
        c.text(left - 12, y + 5, k, size=13, anchor="end", weight="600")
        c.add(f'<rect x="{left}" y="{y - 9}" width="{sx(obs[k]) - left:.1f}" height="18" fill="{PALE}" stroke="{BLUE}" stroke-width="1.2"/>')
        lo, hi = band(uman, k)
        c.add(f'<line x1="{sx(lo):.1f}" y1="{y - 4}" x2="{sx(hi):.1f}" y2="{y - 4}" stroke="{ORANGE}" stroke-width="5"/>')
        lo2, hi2 = band(deg, k)
        c.add(f'<line x1="{sx(lo2):.1f}" y1="{y + 5}" x2="{sx(hi2):.1f}" y2="{y + 5}" stroke="{PURPLE}" stroke-width="5"/>')
        rows[k] = (obs[k], round(lo, 1), round(hi, 1), round(lo2, 1), round(hi2, 1))
    ly = 28
    c.add(f'<rect x="{left}" y="{ly - 10}" width="26" height="14" fill="{PALE}" stroke="{BLUE}" stroke-width="1.2"/>')
    c.text(left + 34, ly + 2, "observed", size=12.5, anchor="start")
    c.add(f'<line x1="{left + 120}" y1="{ly - 3}" x2="{left + 150}" y2="{ly - 3}" stroke="{ORANGE}" stroke-width="5"/>')
    c.text(left + 158, ly + 2, "keeps the dyad census (U|MAN)", size=12.5, anchor="start")
    c.add(f'<line x1="{left + 400}" y1="{ly - 3}" x2="{left + 430}" y2="{ly - 3}" stroke="{PURPLE}" stroke-width="5"/>')
    c.text(left + 438, ly + 2, "keeps every in- and out-degree", size=12.5, anchor="start")
    o = rows["030T"]
    alt = (f"A horizontal bar chart with one row for each of the 16 triad types. Observed counts range from 2 (030C) to {max(obs.values())} (030T). "
           f"Two short bands sit on each bar, the central 95 percent of random networks. For 030T the observed count of {o[0]} is above the band of networks that keep the dyad census ({o[1]:.0f} to {o[2]:.0f}) "
           f"and inside the band of networks that keep every in- and out-degree ({o[3]:.0f} to {o[4]:.0f}).")
    meta = dict(chapter=8,
                caption="The triad census of the advice network (bars) against random networks that keep the dyad census (orange) and random networks that keep every manager's in- and out-degree (purple). Each band holds the central 95 percent of 1,000 draws. The transitive pecking order 030T looks heavily over-represented against the first and ordinary against the second.",
                alt=alt, data={"rows": rows})
    return c, meta


def clustering_three_ways():
    people = ["Ana", "Ben", "Chloe", "Dev", "Eli"]
    ties = [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4)]
    adj = {i: set() for i in range(5)}
    for a, b in ties:
        adj[a].add(b)
        adj[b].add(a)
    tri = [sum(1 for a, b in itertools.combinations(sorted(adj[i]), 2) if b in adj[a]) for i in range(5)]
    wedge = [len(adj[i]) * (len(adj[i]) - 1) // 2 for i in range(5)]
    local = [t / w if w else None for t, w in zip(tri, wedge)]
    glob = 3 * (sum(tri) // 3) / sum(wedge)
    defined = [x for x in local if x is not None]
    avg_omit = sum(defined) / len(defined)
    avg_zero = sum(defined) / 5
    c = Canvas(900, 330, "One small network, three clustering numbers",
               "Five people: a triangle of Ana, Ben and Chloe, with Dev tied to Chloe and Eli tied to Dev. Each person is labeled with a local clustering coefficient.")
    pos = [(110, 90), (110, 230), (250, 160), (390, 160), (530, 160)]
    for a, b in ties:
        c.edge(pos[a], pos[b], ra=24, rb=24, width=2.6, color=MUTED)
    for i, p in enumerate(pos):
        c.node(p[0], p[1], people[i], r=24, fill=PALE, stroke=BLUE, size=12)
        label = "undefined" if local[i] is None else f"{local[i]:.2f}"
        c.text(p[0], p[1] + 46, f"C = {label}", size=13, weight="600", fill=ORANGE if i == 2 else INK)
        c.text(p[0], p[1] + 63, f"{tri[i]} of {wedge[i]} pairs", size=11.5, fill=MUTED)
    x0 = 610
    c.text(x0, 80, "Three summaries of the same people", size=15, weight="700", anchor="start")
    c.lines(x0, 112, [f"Global transitivity   {glob:.3f}", f"Average local, Eli left out   {avg_omit:.3f}",
                      f"Average local, Eli counted as 0   {avg_zero:.3f}"], size=13, gap=1.7)
    c.lines(x0, 190, ["3 x 1 triangle over 6 connected", "triples, against the mean of four", "(or five) separate ratios."],
            size=12.5, fill=MUTED)
    meta = dict(chapter=8,
                caption="A triangle with a tail. Chloe has three friends but only one of her three pairs of friends is tied, so her local coefficient is 0.33. The global ratio and the two averages of the local coefficients give three different numbers for the same network.",
                alt=f"Five people drawn as dots. Ana, Ben and Chloe form a triangle. Dev is tied to Chloe and Eli is tied to Dev. Local clustering is 1.00 for Ana, 1.00 for Ben, 0.33 for Chloe, 0.00 for Dev and undefined for Eli, who has one friend. Beside the picture: global transitivity {glob:.3f}, average local clustering {avg_omit:.3f} with Eli left out and {avg_zero:.3f} with Eli counted as zero.",
                data={"local": local, "global": glob, "avg_omit": avg_omit, "avg_zero": avg_zero})
    return c, meta


def advice_matrix():
    arcs = krackhardt_advice()
    n = 21
    indeg = [sum(1 for (u, v) in arcs if v == j) for j in range(n)]
    order = sorted(range(n), key=lambda j: (-indeg[j], j))
    cell, x0, y0 = 24, 80, 70
    c = Canvas(640, 640, "Who goes to whom for advice among 21 managers",
               "A 21 by 21 grid of cells, one row and one column per manager, ordered by how many managers go to them for advice.")
    mutual = asym = 0
    for r, i in enumerate(order):
        for k, j in enumerate(order):
            x, y = x0 + k * cell, y0 + r * cell
            if i == j:
                c.add(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="#eef0f3" stroke="{PAPER}" stroke-width="1"/>')
            elif (i, j) in arcs:
                both = (j, i) in arcs
                mutual += both
                asym += not both
                c.add(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{BLUE if both else ORANGE}" stroke="{PAPER}" stroke-width="1"/>')
            else:
                c.add(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{PAPER}" stroke="#eef0f3" stroke-width="1"/>')
    for k, j in enumerate(order):
        c.text(x0 + k * cell + cell / 2, y0 - 8, str(j + 1), size=11, fill=MUTED)
        c.text(x0 - 8, y0 + k * cell + cell / 2 + 4, str(j + 1), size=11, anchor="end", fill=MUTED)
    c.text(x0 + 21 * cell / 2, 30, "goes to (column)", size=13, fill=MUTED)
    c.add(f'<text x="22" y="{y0 + 21 * cell / 2}" font-size="13" text-anchor="middle" fill="{MUTED}" transform="rotate(-90 22 {y0 + 21 * cell / 2})">from (row)</text>')
    c.add(f'<rect x="{x0}" y="{y0 + 21 * cell + 22}" width="14" height="14" fill="{BLUE}"/>')
    c.text(x0 + 22, y0 + 21 * cell + 34, "asked and asked back", size=12.5, anchor="start")
    c.add(f'<rect x="{x0 + 190}" y="{y0 + 21 * cell + 22}" width="14" height="14" fill="{ORANGE}"/>')
    c.text(x0 + 212, y0 + 21 * cell + 34, "one way only", size=12.5, anchor="start")
    top3 = [order[i] + 1 for i in range(3)]
    meta = dict(chapter=8,
                caption="Krackhardt's advice network as a grid. A cell in row i and column j means manager i goes to manager j for advice. Managers are ordered by how many come to them, so the most-asked managers are at the left. Blue cells are returned; orange cells are not.",
                alt=f"A 21 by 21 grid with 190 filled cells. {mutual} are blue, which is {mutual // 2} returned pairs counted from both sides, and {asym} are orange, advice that is not returned. The three most-asked managers, in order, are {top3[0]}, {top3[1]} and {top3[2]}, and the columns at the left of the grid are the densest.",
                data={"order": [j + 1 for j in order], "mutual_cells": mutual, "asym_cells": asym})
    return c, meta


def transitive_cyclic():
    c = Canvas(820, 280, "Three kinds of three-person ranking",
               "Three small drawings: a transitive triad where A points to B and C and B points to C, a cyclic triad where each points to the next, and the same transitive triad labeled as a feed-forward loop.")
    specs = [("Transitive (030T)", [(0, 1), (0, 2), (1, 2)], "a clean pecking order"),
             ("Cyclic (030C)", [(0, 1), (1, 2), (2, 0)], "everyone is above someone and below someone"),
             ("Chain (021C)", [(0, 1), (1, 2)], "A reaches C only through B")]
    for k, (title, arcs, gloss) in enumerate(specs):
        cx = 150 + k * 260
        pts = [(cx, 70), (cx - 60, 170), (cx + 60, 170)]
        for a, b in arcs:
            c.edge(pts[a], pts[b], ra=18, rb=18, directed=True, width=2.6, color=BLUE)
        for i, (x, y) in enumerate(pts):
            c.node(x, y, "ABC"[i], r=18, fill=PALE, stroke=BLUE)
        c.text(cx, 225, title, size=15, weight="700")
        c.text(cx, 246, gloss, size=12, fill=MUTED)
    meta = dict(chapter=8,
                caption="Three ways to arrange arrows among three people. A transitive triad has a top and a bottom. A cyclic triad has neither. A chain leaves its ends unconnected.",
                alt="Three triangles of lettered dots with arrows. Left: A points to B, A points to C and B points to C, labeled transitive 030T. Middle: A points to B, B points to C and C points to A, labeled cyclic 030C. Right: A points to B and B points to C, with no arrow between A and C, labeled chain 021C.",
                data={})
    return c, meta


FIGURES = {"triad-census-null": census_against_null, "clustering-three-ways": clustering_three_ways,
           "advice-matrix": advice_matrix, "transitive-cyclic": transitive_cyclic}

"""Figures for chapter 5 of the algorithms book (breadth-first and depth-first search). Standard library only.

Every number drawn is computed here by short reference routines (tools/algkit.py) on the ten-person friendship network.
The animations in tools/anim_scenes/alg_traversal.py check the same routines against the engine's results.
"""
import math
import random
from collections import deque

import algkit as K
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, PURPLE, RED, SKY, Canvas

GRAY, PALE = K.GRAY, K.PALE
CH = 5


def _logx(v, lo, hi, x0, w):
    return x0 + (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * w


# ------------------------------------------------------------------ 1. two ways of waiting
def lines_fig():
    c = Canvas(900, 330, "Two ways of waiting: a queue and a stack",
               "On the left a line of people at a cafe, served from the front; on the right a stack of plates, taken from the top.")
    c.text(225, 34, "A queue: first in, first out", size=16, weight="700")
    c.text(675, 34, "A stack: last in, first out", size=16, weight="700")
    names = ["Ana", "Ben", "Cleo", "Dev", "Eli"]
    for i, nm in enumerate(names):
        x = 90 + i * 64
        c.node(x, 150, "", r=22, fill=PALE if i else ORANGE + "66", stroke=BLUE)
        c.text(x, 192, nm, size=12, fill=MUTED)
    c.text(90, 112, "front", size=12, fill=MUTED)
    c.text(346, 112, "back", size=12, fill=MUTED)
    c.arrow((70, 235), (40, 235), color=RED, width=3)
    c.text(56, 258, "served here", size=12, fill=RED)
    c.arrow((396, 235), (366, 235), color=BLUE, width=3)
    c.text(400, 258, "new people join here", size=12, fill=BLUE, anchor="start")
    c.text(225, 304, "The person who has waited longest goes next.", size=13, fill=MUTED)
    for i, nm in enumerate(["Ana", "Ben", "Cleo", "Dev"]):
        y = 250 - i * 38
        c.rect(595, y, 160, 32, fill=(ORANGE + "66" if i == 3 else PALE), stroke=BLUE, sw=1.8, rx=5)
        c.text(675, y + 21, nm, size=13, weight="600")
    c.arrow((675, 62), (675, 96), color=BLUE, width=3)
    c.text(775, 82, "new plate goes on top", size=12, fill=BLUE, anchor="start")
    c.arrow((812, 125), (812, 95), color=RED, width=3)
    c.text(775, 140, "taken from the top", size=12, fill=RED, anchor="start")
    c.text(675, 304, "The person who arrived last goes next.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="The only difference between the two searches is how the waiting list is kept. A queue serves whoever has waited longest. A stack serves whoever arrived last.",
                alt="Left: five circles in a row labeled Ana, Ben, Cleo, Dev and Eli, with Ana at the front, an arrow showing service at the front and another showing new people joining at the back. Right: four plates labeled Ana, Ben, Cleo and Dev stacked with Dev on top, with an arrow putting a new plate on top and another taking one off the top.",
                data={"queue": names, "stack": ["Ana", "Ben", "Cleo", "Dev"]})
    return c, meta


# ------------------------------------------------------------------ 2. breadth-first levels
def bfs_levels():
    adj = K.adjacency(10, K.EDGES)
    _, order, dist, tree = K.bfs_trace(adj, 0)
    layers = {}
    for v in order:
        layers.setdefault(dist[v], []).append(v)
    c = Canvas(900, 400, "Breadth-first search from Ana, drawn by distance",
               "The ten-person network arranged in columns by number of steps from Ana.")
    pos = [None] * 10
    for d, vs in layers.items():
        x = 90 + d * 175
        for k, v in enumerate(vs):
            y = 200 + (k - (len(vs) - 1) / 2) * 78
            pos[v] = (x, y)
    treeset = {frozenset(e) for e in tree}
    for d in layers:
        c.text(90 + d * 175, 34, "Ana" if d == 0 else f"{d} step{'s' if d > 1 else ''}", size=14, weight="700")
        c.add(f'<line x1="{90 + d * 175}" y1="46" x2="{90 + d * 175}" y2="372" stroke="{FAINT}" stroke-width="1" stroke-dasharray="3 5"/>')
    def estyle(k):
        a, b = K.EDGES[k]
        if frozenset((a, b)) in treeset:
            return {"color": BLUE, "width": 4}
        return {"color": GRAY, "width": 1.4, "dash": "5 4"}
    K.draw_graph(c, pos, K.EDGES, node=lambda i: {"fill": ORANGE + "88" if i == 0 else PALE, "stroke": INK if i == 0 else BLUE,
                                                    "label": K.NAMES[i][0]}, edge=estyle, r=20, size=13)
    for i, p in enumerate(pos):
        c.text(p[0], p[1] + 36, K.NAMES[i], size=11, fill=MUTED)
    c.text(450, 392, "Thick blue lines: the tie each person was found through. Dashed lines: ties that found nobody new.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="The same network, rearranged so that everyone sits in the column of their distance from Ana. Every tie goes from a column to the same one or the next one, never further, which is why the search can be trusted to find shortest routes.",
                alt="Five columns headed Ana, 1 step, 2 steps, 3 steps and 4 steps. Ana is alone in the first. Ben, Cleo, Dev and Fay are in the second; Eli, Gus and Hana in the third; Ivo in the fourth; Jo in the fifth. Thick blue lines mark the tie that found each person and dashed grey lines mark the other ties.",
                data={"layers": {d: [K.NAMES[v] for v in vs] for d, vs in layers.items()}, "tree": [[K.NAMES[a], K.NAMES[b]] for a, b in tree]})
    return c, meta


# ------------------------------------------------------------------ 3. depth-first trail
def dfs_trail():
    adj = K.adjacency(10, K.EDGES)
    events, order, tree = K.dfs_trace(adj, 0)
    pos = K.kite_pos(70, 60, 470, 290)
    num = {v: i + 1 for i, v in enumerate(order)}
    treeset = {frozenset(e) for e in tree}
    c = Canvas(900, 410, "Depth-first search from Ana", "The ten-person network with people numbered in the order a depth-first search finds them.")
    def estyle(k):
        a, b = K.EDGES[k]
        return {"color": ORANGE, "width": 4.4} if frozenset((a, b)) in treeset else {"color": GRAY, "width": 1.4, "dash": "5 4"}
    K.draw_graph(c, pos, K.EDGES, node=lambda i: {"fill": ORANGE + "88" if i == 0 else PALE, "stroke": INK if i == 0 else BLUE,
                                                    "label": str(num[i])}, edge=estyle, r=19, size=13, names=K.NAMES)
    x0 = 600
    c.text(x0, 70, "The trail, step by step", size=15, weight="700", anchor="start")
    shown = [e for e in events][:13]
    y = 98
    for kind, a, b, trail in shown:
        if kind == "go":
            c.text(x0, y, f"Walk on to {K.NAMES[b]}", size=12.5, anchor="start")
        else:
            c.text(x0, y, f"Dead end at {K.NAMES[a]}, back to {K.NAMES[b]}", size=12.5, anchor="start", fill=RED)
        y += 21
    c.text(x0, y + 6, "...and so on until the trail is back at Ana.", size=12.5, anchor="start", fill=MUTED)
    c.text(300, 396, "Orange: ties walked along. Dashed: ties that led to someone already met.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="A depth-first search from Ana. The numbers are the order people were first met. It runs Ana, Ben, Dev, Cleo, Fay, Gus, Eli, then backs up and finishes with Hana, Ivo and Jo: it goes as deep as it can before it ever tries another friend.",
                alt="The ten-person network. Each person has a number from 1 to 10. Ana is 1, Ben 2, Dev 3, Cleo 4, Fay 5, Gus 6, Eli 7, Hana 8, Ivo 9 and Jo 10. Nine ties are drawn thick orange and the other nine are thin dashed grey. A list on the right narrates the first steps, including the places the search hits a dead end and backs up.",
                data={"order": [K.NAMES[v] for v in order], "tree": [[K.NAMES[a], K.NAMES[b]] for a, b in tree]})
    return c, meta


# ------------------------------------------------------------------ 4. rings versus snakes on a grid
def grid_shapes():
    w, h = 9, 7
    edges = K.grid_edges(w, h)
    adj = K.adjacency(w * h, edges)
    s = 3 * w + 4
    _, border, _, _ = K.bfs_trace(adj, s)
    _, dorder, _ = K.dfs_trace(adj, s)
    c = Canvas(900, 380, "The shapes of the two searches", "Two nine by seven grids of streets, shaded by the order in which a breadth-first and a depth-first search find each corner.")
    cell = 38
    for p, (title, order) in enumerate((("Breadth-first: rings spreading out", border), ("Depth-first: one long snake", dorder))):
        x0, y0 = 50 + p * 440, 70
        c.text(x0 + w * cell / 2 - cell / 2, 40, title, size=15, weight="700")
        rank = {v: i for i, v in enumerate(order)}
        for v in range(w * h):
            r, cc = divmod(v, w)
            t = rank[v] / (len(order) - 1)
            shade = f"rgb({int(238 - 200 * t)},{int(246 - 130 * t)},{int(251 - 80 * t)})"
            c.rect(x0 + cc * cell - cell / 2 + 4, y0 + r * cell - cell / 2 + 4, cell - 4, cell - 4, fill=shade, stroke=PAPER, sw=1, rx=4)
            c.text(x0 + cc * cell + 2, y0 + r * cell + 8, str(rank[v] + 1), size=11, fill=PAPER if t > 0.55 else INK)
        sr, sc = divmod(s, w)
        c.add(f'<circle cx="{x0 + sc * cell + 2}" cy="{y0 + sr * cell + 4}" r="17" fill="none" stroke="{RED}" stroke-width="2.4"/>')
    c.text(450, 366, "Darker means found later. Both start at the circled square and both find everyone, in very different orders.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="Same streets, same starting corner, same answer to 'who can I reach?', and very different orders. Breadth-first finds everything near the start first, in rings. Depth-first picks one direction and goes until it hits a wall.",
                alt="Two grids of nine columns by seven rows, each square numbered from 1 to 63 by the order of discovery and shaded from light to dark. On the left the numbers grow outward from the circled middle square in diamond-shaped rings. On the right the numbers follow one long winding path that sweeps up and across the grid before coming back for the squares it skipped.",
                data={"bfs_order": border, "dfs_order": dorder, "start": s})
    return c, meta


# ------------------------------------------------------------------ 5. what you get for free
def free_gifts():
    adj = K.adjacency(10, K.EDGES)
    steps, order, dist, tree = K.bfs_trace(adj, 0)
    parent = {b: a for a, b in tree}
    c = Canvas(900, 420, "What breadth-first search leaves behind", "A table with one row per person: the step they were found on, who found them, and the route back to Ana.")
    rows = []
    for v in order:
        route = [v]
        while route[-1] in parent:
            route.append(parent[route[-1]])
        rows.append([K.NAMES[v], str(dist[v]), "(start)" if v == 0 else K.NAMES[parent[v]], " > ".join(K.NAMES[x] for x in reversed(route))])
    end = K.table(c, 40, 50, ["Person", "Steps from Ana", "Found by", "Route from Ana"], rows, [110, 150, 130, 440], row_h=29, size=13, hl={9})
    c.text(450, 32, "Everything below comes for free from one search", size=15, weight="700")
    c.text(450, end + 26, "Jo is 4 steps away, and following 'found by' backwards gives the route. Nothing else had to be computed.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="One breadth-first search from Ana leaves three things behind for free: every person's distance, the person who found them, and therefore a shortest route to anyone, read backwards. The orange row is Jo.",
                alt="A table with columns Person, Steps from Ana, Found by and Route from Ana, with ten rows in the order people were found. Ana has 0 steps. Ben, Cleo, Dev and Fay have 1 step, all found by Ana. Eli, Gus and Hana have 2 steps, found by Ben, Ben and Fay. Ivo has 3 steps found by Hana. Jo has 4 steps, found by Ivo, with route Ana to Fay to Hana to Ivo to Jo.",
                data={"rows": rows})
    return c, meta


# ------------------------------------------------------------------ 6. islands
def islands():
    names = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jo", "Kai", "Lena"]
    edges = [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (5, 6), (6, 7), (7, 8), (5, 8), (9, 10)]
    pos = [(110, 120), (210, 70), (210, 190), (330, 190), (430, 120), (560, 90), (680, 70), (700, 180), (580, 190), (170, 300), (300, 320), (800, 310)]
    adj = K.adjacency(12, edges)
    seen = [None] * 12
    k = 0
    for s in range(12):
        if seen[s] is None:
            k += 1
            for v in K.bfs_ball(adj, s)[0]:
                seen[v] = k
    cols = {1: BLUE, 2: ORANGE, 3: GREEN, 4: PURPLE}
    c = Canvas(900, 400, "Finding islands with repeated searches", "Twelve people in four separate groups, each coloured by the search that found it.")
    c.text(450, 30, "Start a search from the first person not yet found. Each search lights up one island.", size=14, weight="600")
    K.draw_graph(c, pos, edges, node=lambda i: {"fill": cols[seen[i]] + "55", "stroke": cols[seen[i]], "label": str(seen[i])},
                 edge=lambda e: {"color": cols[seen[edges[e][0]]], "width": 3.2}, r=20, size=14, names=names)
    c.text(450, 392, "The number in each dot is which search found that person: 4 searches, 4 islands (Lena is an island of one).", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="Counting islands. Search from the first person who has not been found yet, then again from the next one still unfound, and so on. The number of searches you needed is the number of islands.",
                alt="Twelve circles in four groups. Ana, Ben, Cleo, Dev and Eli form a blue group numbered 1. Fay, Gus, Hana and Ivo form an orange group numbered 2. Jo and Kai form a green group numbered 3. Lena sits alone in a purple group numbered 4.",
                data={"search_number": dict(zip(names, seen))})
    return c, meta


# ------------------------------------------------------------------ 7. cost
def cost_chart():
    rng = random.Random(5)
    sizes = [250, 500, 1000, 2000, 4000, 8000, 16000, 32000]
    looks = []
    for n in sizes:
        m = 2 * n  # mean degree 4
        es = set()
        while len(es) < m:
            a, b = rng.randrange(n), rng.randrange(n)
            if a != b:
                es.add((min(a, b), max(a, b)))
        adj = [[] for _ in range(n)]
        for a, b in es:
            adj[a].append(b)
            adj[b].append(a)
        seen = [False] * n
        seen[0] = True
        q = deque([0])
        count = 0
        while q:
            u = q.popleft()
            for v in adj[u]:
                count += 1
                if not seen[v]:
                    seen[v] = True
                    q.append(v)
        looks.append((count, sum(seen)))
    c = Canvas(900, 430, "Work grows in step with the network", "Number of friend-list entries a search reads against the number of people, with the cost of checking every pair for comparison.")
    x0, y0, w, h = 110, 50, 690, 290
    lo, hi = 100, 1e9
    X = lambda n: _logx(n, 250, 32000, x0, w)
    Y = lambda v: y0 + h - (math.log10(v) - 2) / (9 - 2) * h
    c.add(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{INK}" stroke-width="1.5"/><line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{INK}" stroke-width="1.5"/>')
    for e in range(2, 10):
        yy = Y(10 ** e)
        c.add(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x0 + w}" y2="{yy:.1f}" stroke="{FAINT}" stroke-width="0.8"/>')
        c.text(x0 - 10, yy + 4, {2: "100", 3: "1,000", 4: "10,000", 5: "100,000", 6: "1 million", 7: "10 million", 8: "100 million", 9: "1 billion"}[e], size=11.5, anchor="end")
    for n in sizes:
        c.text(X(n), y0 + h + 20, f"{n:,}", size=11.5)
    c.text(x0 + w / 2, y0 + h + 46, "people in the network (each has about 4 friends)", size=13, fill=MUTED)
    c.text(x0, y0 - 14, "steps of work", size=13, fill=MUTED, anchor="start")
    pairs = " ".join(f"{X(n):.1f},{Y(n * (n - 1) / 2):.1f}" for n in sizes)
    c.add(f'<polyline points="{pairs}" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="7 5"/>')
    ser = " ".join(f"{X(n):.1f},{Y(l):.1f}" for n, (l, _) in zip(sizes, looks))
    c.add(f'<polyline points="{ser}" fill="none" stroke="{BLUE}" stroke-width="3.2"/>')
    for n, (l, _) in zip(sizes, looks):
        c.add(f'<circle cx="{X(n):.1f}" cy="{Y(l):.1f}" r="5" fill="{PAPER}" stroke="{BLUE}" stroke-width="2.4"/>')
    c.text(X(8000), Y(looks[5][0]) + 34, "one search: friend-list entries read", size=13, fill=BLUE, weight="700", anchor="middle")
    c.text(X(2000), Y(2000 * 1999 / 2) - 30, "checking every pair of people", size=13, fill=RED, weight="700", anchor="middle")
    c.text(450, 412, f"At 32,000 people one search reads about {looks[-1][0]:,} entries. Checking every pair would take {32000 * 31999 // 2:,}.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="Double the network and a search does about double the work (the blue line is nearly straight on this log scale with a slope of one). Checking every pair of people grows much faster (the dashed red line).",
                alt="A chart with the number of people from 250 to 32,000 along the bottom on a log scale and steps of work up the side on a log scale. A solid blue line with circles rises gently from about 1,000 to about 128,000. A dashed red line rises much more steeply from about 31,000 to about 512 million.",
                data={"people": sizes, "entries_read": [l for l, _ in looks], "reached": [r for _, r in looks]})
    return c, meta


# ------------------------------------------------------------------ 8. what a search is for
def uses():
    c = Canvas(900, 400, "What a traversal is the base for", "Six cards, each naming a question that a breadth-first or depth-first search answers.")
    cards = [("How far?", "distances and shortest routes", "breadth-first", BLUE),
             ("Who is connected?", "islands (components)", "either", GREEN),
             ("Is there a loop?", "cycle detection", "depth-first", ORANGE),
             ("What comes first?", "ordering tasks that depend on others", "depth-first", ORANGE),
             ("What is nearby?", "everyone within two steps", "breadth-first", BLUE),
             ("Where does it split?", "bridges and cut people", "depth-first", ORANGE)]
    for i, (q, a, kind, col) in enumerate(cards):
        x, y = 40 + (i % 3) * 285, 40 + (i // 3) * 170
        c.rect(x, y, 265, 145, fill=col + "14", stroke=col, sw=2, rx=12)
        c.text(x + 16, y + 34, q, size=17, weight="700", anchor="start")
        c.lines(x + 16, y + 66, [a], size=13, fill=INK)
        c.text(x + 16, y + 118, "best fit: " + kind, size=12.5, fill=col, anchor="start", weight="700")
    c.text(450, 388, "Later chapters use these over and over: components, DAGs, connectivity and betweenness all start here.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="Why this chapter comes early: most later algorithms are one of these two walks with a little extra bookkeeping.",
                alt="Six rounded cards in two rows of three. Blue cards for breadth-first: How far (distances and shortest routes) and What is nearby (everyone within two steps). A green card for either: Who is connected (islands). Orange cards for depth-first: Is there a loop, What comes first (ordering tasks), and Where does it split (bridges and cut people).",
                data={})
    return c, meta


FIGURES = {
    "alg-traversal-lines": lines_fig,
    "alg-traversal-bfs-levels": bfs_levels,
    "alg-traversal-dfs-trail": dfs_trail,
    "alg-traversal-grid-shapes": grid_shapes,
    "alg-traversal-free-gifts": free_gifts,
    "alg-traversal-islands": islands,
    "alg-traversal-cost": cost_chart,
    "alg-traversal-uses": uses,
}

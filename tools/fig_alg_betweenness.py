"""Figures for the algorithms book, chapter 18 (betweenness, exactly and approximately).

Standard library only. Every number drawn is computed here from the networks below (the ten-person friendship
network and Zachary's karate club), with a plain version of Brandes' two passes, so the pictures cannot drift
from the chapter.
"""
import math
import random
from pathlib import Path

from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, RED, SKY, Canvas

GRAY = "#9ca3af"
PALE = "#cfe5f3"
NAMES = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jo"]
EDGES = [(0, 1), (0, 2), (0, 3), (0, 5), (1, 3), (1, 4), (1, 6), (2, 3), (2, 5), (3, 4),
         (3, 5), (3, 6), (4, 6), (5, 6), (5, 7), (6, 7), (7, 8), (8, 9)]
DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"


def adjacency(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    return [sorted(x) for x in adj]


def brandes_one(adj, s):
    """Distances, route counts and dependencies from one source (Brandes 2001, unweighted)."""
    n = len(adj)
    dist, sigma, order = [-1] * n, [0] * n, []
    dist[s], sigma[s] = 0, 1
    queue = [s]
    for u in queue:
        order.append(u)
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                queue.append(v)
            if dist[v] == dist[u] + 1:
                sigma[v] += sigma[u]
    delta = [0.0] * n
    for w in reversed(order):
        for v in adj[w]:
            if dist[v] == dist[w] - 1:
                delta[v] += sigma[v] / sigma[w] * (1 + delta[w])
    delta[s] = 0.0
    return dist, sigma, delta


def betweenness(n, edges, sources=None):
    adj = adjacency(n, edges)
    total = [0.0] * n
    for s in (range(n) if sources is None else sources):
        for i, d in enumerate(brandes_one(adj, s)[2]):
            total[i] += d / 2  # undirected: every pair is seen from both ends
    return total


def karate():
    rows = (DATA / "karate" / "edges.csv").read_text().strip().splitlines()[1:]
    return 34, [(int(r.split(",")[0]) - 1, int(r.split(",")[1]) - 1) for r in rows]


def g(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- 1. pairs grow like a square
def pairs_grow():
    c = Canvas(720, 330, "Pairs grow much faster than people",
               "Three triangles of small squares, one square per pair of people, for 4, 8 and 16 people.")
    c.text(360, 30, "One square for every pair of people", size=16, weight="700")
    x0 = 30
    for n, cell in [(4, 26), (8, 13), (16, 6.5)]:
        pairs = n * (n - 1) // 2
        size = cell * (n - 1)
        for i in range(n - 1):
            for j in range(i + 1):
                c.rect(x0 + j * cell, 60 + i * cell, cell - 1.5, cell - 1.5, fill=PALE if n < 16 else SKY, stroke=BLUE, sw=0.6)
        c.text(x0 + size / 2, 60 + size + 30, f"{n} people", size=14, weight="700")
        c.text(x0 + size / 2, 60 + size + 50, f"{pairs} pairs", size=14, fill=MUTED)
        x0 += size + 70
    c.text(360, 316, "Double the people and the pairs roughly quadruple.", size=13, fill=MUTED)
    meta = dict(book="algorithms", chapter=18,
                caption="Every pair of people needs its own routes counted. Four people make 6 pairs, eight make 28, sixteen make 120: double the people and the pairs roughly quadruple.",
                alt="Three staircase-shaped triangles made of small blue squares. The first, for 4 people, has 6 squares; the second, for 8 people, has 28; the third, for 16 people, has 120 tiny squares.",
                data={"people": [4, 8, 16], "pairs": [6, 28, 120]})
    return c, meta


# ---------------------------------------------------------------- shared: the friendship network in levels from Ana
def level_positions(dist, x0=70, dx=150, y0=70, h=300):
    by = {}
    for i, d in enumerate(dist):
        by.setdefault(d, []).append(i)
    pos = {}
    for d, ids in by.items():
        for k, i in enumerate(ids):
            pos[i] = (x0 + d * dx, y0 + h * (k + 0.5) / len(ids))
    return pos


def forward_levels():
    adj = adjacency(10, EDGES)
    dist, sigma, _ = brandes_one(adj, 0)
    pos = level_positions(dist)
    c = Canvas(720, 420, "Counting shortest routes from Ana, level by level",
               "The ten-person network laid out in columns by distance from Ana, with route counts in the dots.")
    for d in range(max(dist) + 1):
        c.text(70 + d * 150, 40, f"distance {d}", size=13, weight="700", fill=MUTED)
    for a, b in EDGES:
        on = abs(dist[a] - dist[b]) == 1
        c.edge(pos[a], pos[b], ra=19, rb=19, color=ORANGE if on else GRAY, width=2.6 if on else 1.3,
               dash=None if on else "4 4", curve=0 if on else 34)
    for i in range(10):
        src = i == 0
        c.node(*pos[i], str(sigma[i]), r=19, fill=ORANGE if src else PALE, stroke=RED if src else BLUE, size=14)
        c.text(pos[i][0], pos[i][1] + 34, NAMES[i], size=12, fill=MUTED)
    c.text(360, 400, "Number in a dot: shortest routes from Ana. Orange ties lead one step farther; dashed ties stay level.",
           size=12, fill=MUTED)
    meta = dict(book="algorithms", chapter=18,
                caption="The forward pass from Ana. Each person's number is the count of shortest routes from Ana, found by adding up the numbers of the people one step closer. Gus has three: through Ben, through Dev and through Fay.",
                alt=("The ten people arranged in five columns by distance from Ana: Ana alone at distance 0; Ben, Cleo, Dev and Fay at 1; Eli, Gus and Hana at 2; Ivo at 3; Jo at 4. "
                     f"The route counts in the dots are: Eli {sigma[4]}, Gus {sigma[6]}, Hana {sigma[7]}, and 1 for everyone else. "
                     "Orange ties join neighbouring columns; dashed gray ties join people in the same column."),
                data={"names": NAMES, "distance": dist, "routes": sigma})
    return c, meta


# ---------------------------------------------------------------- 3. backward pass: credit flows back and splits
def backward_split():
    adj = adjacency(10, EDGES)
    dist, sigma, delta = brandes_one(adj, 0)
    pos = level_positions(dist)
    c = Canvas(720, 440, "Passing credit back toward Ana",
               "The same levels from Ana, with each person's credit and arrows showing credit split among the people one step closer.")
    for a, b in EDGES:
        if abs(dist[a] - dist[b]) == 1:
            far, near = (a, b) if dist[a] > dist[b] else (b, a)
            share = sigma[near] / sigma[far] * (1 + delta[far])
            c.edge(pos[far], pos[near], ra=19, rb=19, directed=True, color=GREEN, width=1.6 + 0.5 * min(share, 3))
            mx, my = (pos[far][0] * 0.68 + pos[near][0] * 0.32), (pos[far][1] * 0.68 + pos[near][1] * 0.32)
            c.add(f'<rect x="{mx - 17:.1f}" y="{my - 10:.1f}" width="34" height="18" rx="4" fill="{PAPER}" stroke="{FAINT}"/>')
            c.text(mx, my + 4, g(share), size=11, fill=INK)
    for i in range(10):
        src = i == 0
        c.node(*pos[i], "" if src else g(delta[i]), r=19, fill=ORANGE if src else PALE, stroke=RED if src else BLUE, size=12)
        c.text(pos[i][0], pos[i][1] + 34, NAMES[i], size=12, fill=MUTED)
    c.text(360, 400, "Number in a dot: credit from Ana's routes. Number on an arrow: the share passed one step closer.",
           size=12, fill=MUTED)
    c.text(360, 420, "A person passes on 1 for themselves plus their own credit, split by route counts.", size=12, fill=MUTED)
    meta = dict(book="algorithms", chapter=18,
                caption="The backward pass. Starting from the far end, each person hands 1 plus their own credit to the people one step closer, split in proportion to how many shortest routes come through each. Gus has three equal routes, so Ben, Dev and Fay get a third each.",
                alt=(f"The ten people in columns by distance from Ana, with green arrows pointing back toward Ana. "
                     f"Jo passes 1 to Ivo, Ivo passes 2 to Hana, Hana passes 3 to Fay. Eli passes a half each to Ben and Dev, and Gus passes a third each to Ben, Dev and Fay. "
                     f"The credits in the dots are Fay {g(delta[5])}, Hana {g(delta[7])}, Ivo {g(delta[8])}, Ben {g(delta[1])}, Dev {g(delta[3])}, and 0 for Cleo, Eli, Gus and Jo."),
                data={"names": NAMES, "routes": sigma, "credit_from_ana": delta})
    return c, meta


# ---------------------------------------------------------------- 4. every source adds a row
def source_grid():
    adj = adjacency(10, EDGES)
    rows = [[d / 2 for d in brandes_one(adj, s)[2]] for s in range(10)]
    total = [sum(r[i] for r in rows) for i in range(10)]
    top = max(max(r) for r in rows)
    cw, ch, x0, y0 = 54, 27, 120, 70
    c = Canvas(720, 420, "What each starting person adds",
               "A ten by ten grid: one row per starting person, one column per person scored, with the column totals below.")
    c.text(x0 + 5 * cw, 30, "Person scored", size=14, weight="700")
    c.text(40, y0 + 5 * ch, "Start", size=14, weight="700")
    for j, nm in enumerate(NAMES):
        c.text(x0 + j * cw + cw / 2, y0 - 10, nm, size=12, weight="600")
    for s, r in enumerate(rows):
        c.text(x0 - 10, y0 + s * ch + ch / 2 + 4, NAMES[s], size=12, anchor="end", weight="600")
        for j, v in enumerate(r):
            t = v / top
            op = 0 if v == 0 else 0.12 + 0.6 * t
            c.add(f'<rect x="{x0 + j * cw}" y="{y0 + s * ch}" width="{cw - 2}" height="{ch - 2}" fill="{BLUE}" fill-opacity="{op:.2f}" stroke="{FAINT}" stroke-width="0.8"/>')
            if v:
                c.text(x0 + j * cw + cw / 2 - 1, y0 + s * ch + ch / 2 + 4, g(v), size=10.5, fill=INK)
    yt = y0 + 10 * ch + 8
    c.text(x0 - 10, yt + 18, "Total", size=12, anchor="end", weight="700")
    for j, v in enumerate(total):
        c.rect(x0 + j * cw, yt, cw - 2, ch, fill="#fff4dc", stroke=ORANGE, sw=1)
        c.text(x0 + j * cw + cw / 2 - 1, yt + 18, g(v), size=12, weight="700")
    meta = dict(book="algorithms", chapter=18,
                caption="Betweenness is a sum of one row per starting person. Each cell is what that person's shortest routes add to the person in the column (half the textbook credit, since every pair is seen from both ends). The totals are the familiar scores: Hana 14, Fay and Gus 8.33.",
                alt=("A grid of numbers with ten rows (starting people Ana to Jo) and ten columns (people scored). Most cells are empty; the darker cells are in the columns for Fay, Gus, Hana and Ivo. "
                     "The bottom row gives the totals: " + ", ".join(f"{NAMES[i]} {g(total[i])}" for i in range(10)) + "."),
                data={"names": NAMES, "rows": rows, "total": total})
    return c, meta


# ---------------------------------------------------------------- 5. the cost, in rough time
def human_time(seconds):
    for unit, size in [("years", 365.25 * 86400), ("days", 86400), ("hours", 3600), ("minutes", 60), ("seconds", 1)]:
        if seconds >= size:
            return f"{seconds / size:.0f} {unit}" if seconds / size >= 10 else f"{seconds / size:.1f} {unit}"
    return f"{seconds * 1000:.0f} ms" if seconds >= 0.001 else "under 1 ms"


def cost_bars():
    rate = 1e9  # a rough billion simple steps a second
    sizes = [1_000, 10_000, 100_000, 1_000_000]
    c = Canvas(720, 400, "All pairs one by one versus Brandes",
               "Paired bars on a log scale: the rough time for the pair-by-pair method and for Brandes' method at four network sizes.")
    c.text(360, 30, "Rough time at a billion steps a second, ten ties per person", size=15, weight="700")
    lo, hi = -3, 10  # log10 seconds
    x0, w = 150, 520

    def x(sec):
        return x0 + w * (math.log10(max(sec, 10 ** lo)) - lo) / (hi - lo)
    for t, lab in [(1e-3, "1 ms"), (1, "1 s"), (60, "1 min"), (3600, "1 h"), (86400, "1 day"), (31557600, "1 year")]:
        c.add(f'<line x1="{x(t):.1f}" y1="60" x2="{x(t):.1f}" y2="350" stroke="{FAINT}" stroke-width="1"/>')
        c.text(x(t), 368, lab, size=11, fill=MUTED)
    data = []
    for k, n in enumerate(sizes):
        m = 10 * n
        naive, fast = n ** 3 / rate, n * m / rate
        y = 70 + k * 70
        c.text(x0 - 12, y + 22, f"{n:,} people", size=13, anchor="end", weight="600")
        for j, (sec, col, lab) in enumerate([(naive, RED, "pair by pair"), (fast, BLUE, "Brandes")]):
            c.rect(x0, y + j * 22, x(sec) - x0, 18, fill=col, stroke=col, sw=0)
            c.text(x(sec) + 6, y + j * 22 + 14, f"{human_time(sec)} ({lab})", size=11.5, anchor="start", fill=INK)
        data.append({"people": n, "ties": m // 2, "pair_by_pair_seconds": naive, "brandes_seconds": fast})
    c.text(360, 392, "Pair by pair: about n x n x n steps. Brandes: about n x m steps (m = arcs, here 10 per person).", size=11.5, fill=MUTED)
    meta = dict(book="algorithms", chapter=18,
                caption="Why the method matters more than the machine. With a rough billion steps a second and ten ties per person, the pair-by-pair way needs a quarter of an hour at ten thousand people and decades at a million; Brandes' way needs a fraction of a second and about three hours.",
                alt=("A bar chart with a logarithmic time axis from a millisecond to beyond a year. For 1,000, 10,000, 100,000 and 1,000,000 people, a red bar shows the pair-by-pair time "
                     "(1 second, 17 minutes, 12 days, 32 years) and a blue bar shows Brandes' time (10 milliseconds, 1 second, 100 seconds, 2.8 hours)."),
                data={"steps_per_second": rate, "rows": data})
    return c, meta


# ---------------------------------------------------------------- 6. sampling: how wrong, how fast it improves
def sampling_error():
    n, edges = karate()
    adj = adjacency(n, edges)
    per = [[d / 2 for d in brandes_one(adj, s)[2]] for s in range(n)]
    exact = [sum(per[s][i] for s in range(n)) for i in range(n)]
    top = max(exact)
    rng = random.Random(18)
    ks = [2, 4, 8, 12, 17, 24, 34]
    rows = []
    for k in ks:
        errs = []
        for _ in range(400):
            pick = rng.sample(range(n), k)
            est = [n / k * sum(per[s][i] for s in pick) for i in range(n)]
            errs.append(max(abs(a - b) for a, b in zip(est, exact)) / top)
        errs.sort()
        rows.append((k, errs[len(errs) // 2], errs[int(0.1 * len(errs))], errs[int(0.9 * len(errs)) - 1]))
    c = Canvas(720, 420, "Sampling starting people on the karate club",
               "A line chart: the worst error over all 34 members, as a share of the top score, against the number of sampled starting people.")
    x0, y0, w, h = 90, 60, 580, 290
    ymax = 1.0

    def px(k):
        return x0 + w * (k - 0) / 34

    def py(v):
        return y0 + h - h * min(v, ymax) / ymax
    for v in [0, 0.25, 0.5, 0.75, 1.0]:
        c.add(f'<line x1="{x0}" y1="{py(v):.1f}" x2="{x0 + w}" y2="{py(v):.1f}" stroke="{FAINT}"/>')
        c.text(x0 - 8, py(v) + 4, f"{int(v * 100)}%", size=11, anchor="end", fill=MUTED)
    for k in ks:
        c.text(px(k), y0 + h + 18, str(k), size=11, fill=MUTED)
    band = " ".join(f"{px(k):.1f},{py(hi):.1f}" for k, _, _, hi in rows) + " " + " ".join(
        f"{px(k):.1f},{py(lo):.1f}" for k, _, lo, _ in reversed(rows))
    c.add(f'<polygon points="{band}" fill="{SKY}" fill-opacity="0.25" stroke="none"/>')
    c.add('<polyline points="' + " ".join(f"{px(k):.1f},{py(m):.1f}" for k, m, _, _ in rows) +
          f'" fill="none" stroke="{BLUE}" stroke-width="2.5"/>')
    for k, m, _, _ in rows:
        c.node(px(k), py(m), "", r=4.5, fill=BLUE, stroke=BLUE)
    c.text(x0 + w / 2, y0 + h + 42, "Starting people sampled (out of 34)", size=13, weight="600")
    c.text(30, y0 + h / 2, "Worst error", size=13, weight="600", anchor="middle")
    c.text(x0 + w / 2, 34, "Worst error over all members, as a share of the top score (middle line: typical draw; band: 8 in 10 draws)", size=12.5, fill=MUTED)
    meta = dict(book="algorithms", chapter=18,
                caption="How wrong a sampled estimate is on the karate club, over 400 random draws per size. With 2 starting people the worst-scored member is typically off by about half the top score; with 17 (half the club) by about a tenth; with all 34 the answer is exact.",
                alt=("A falling line with a shaded band around it. The horizontal axis is the number of sampled starting people, from 2 to 34; the vertical axis is the worst error over all members as a percentage of the top score. "
                     + "; ".join(f"At {k} the typical worst error is {m * 100:.0f} percent" for k, m, _, _ in rows).replace("; At", "; at") + "."),
                data={"draws_per_size": 400, "seed": 18, "rows": [{"k": k, "median": m, "p10": lo, "p90": hi} for k, m, lo, hi in rows]})
    return c, meta


# ---------------------------------------------------------------- 7. equal routes share the credit
def shared_credit():
    c = Canvas(720, 300, "Two equally short routes share the credit",
               "Ana and Eli joined by two routes of two steps, one through Ben and one through Dev; each middle person gets half.")
    pos = {"Ana": (140, 150), "Ben": (360, 70), "Dev": (360, 230), "Eli": (580, 150)}
    for a, b in [("Ana", "Ben"), ("Ana", "Dev"), ("Ben", "Eli"), ("Dev", "Eli")]:
        c.edge(pos[a], pos[b], ra=24, rb=24, color=ORANGE, width=3)
    c.edge(pos["Ben"], pos["Dev"], ra=24, rb=24, color=GRAY, width=1.5, dash="4 4")
    for k, (x, y) in pos.items():
        mid = k in ("Ben", "Dev")
        c.node(x, y, k, r=24, fill=PALE if mid else "#fff4dc", stroke=BLUE if mid else ORANGE, size=13)
    c.text(360, 30, "Ana to Eli: two shortest routes, each two steps", size=15, weight="700")
    c.text(440, 110, "1 of 2 routes: +1/2", size=13, anchor="start", fill=BLUE)
    c.text(440, 200, "1 of 2 routes: +1/2", size=13, anchor="start", fill=BLUE)
    c.text(360, 285, "The dashed Ben to Dev tie is not on any shortest route from Ana to Eli.", size=12, fill=MUTED)
    meta = dict(book="algorithms", chapter=18,
                caption="When there are several equally short routes, each one carries an equal share. Ana reaches Eli in two steps through Ben or through Dev, so the pair Ana and Eli adds a half to each of them.",
                alt="Four dots: Ana on the left, Eli on the right, Ben above and Dev below the middle. Thick orange ties run Ana to Ben to Eli and Ana to Dev to Eli. A dashed gray tie joins Ben and Dev. Labels say each middle person gets one half.",
                data={"pair": ["Ana", "Eli"], "routes": [["Ana", "Ben", "Eli"], ["Ana", "Dev", "Eli"]], "share": 0.5})
    return c, meta


FIGURES = {"alg-bt-pairs-grow": pairs_grow, "alg-bt-forward-levels": forward_levels,
           "alg-bt-backward-split": backward_split, "alg-bt-source-grid": source_grid,
           "alg-bt-cost-bars": cost_bars, "alg-bt-sampling-error": sampling_error,
           "alg-bt-shared-credit": shared_credit}

# ---------------------------------------------------------------- 8. credit on ties
def edge_credit():
    from fig_layout import fit, stress_layout
    adj = adjacency(10, EDGES)
    eb = {e: 0.0 for e in EDGES}
    for s in range(10):
        dist, sigma, delta = brandes_one(adj, s)
        for a, b in EDGES:
            for u, v in ((a, b), (b, a)):
                if dist[v] == dist[u] + 1:
                    eb[(a, b)] += sigma[u] / sigma[v] * (1 + delta[v]) / 2
    top = max(eb.values())
    pos = fit(stress_layout(10, EDGES, seed=3), 60, 60, 600, 300)
    c = Canvas(720, 420, "Which ties carry the most routes",
               "The ten-person network with each tie drawn thicker the more shortest routes it carries, labelled with its edge betweenness.")
    c.text(360, 30, "Ties drawn by how many shortest routes cross them", size=15, weight="700")
    for (a, b), v in sorted(eb.items(), key=lambda x: x[1]):
        hot = v >= 9
        c.edge(pos[a], pos[b], ra=18, rb=18, color=ORANGE if hot else GRAY, width=1 + 9 * v / top,
               label=g(v) if v >= 4 else None)
    for i in range(10):
        c.node(*pos[i], NAMES[i], r=18, fill=PALE, stroke=BLUE, size=10)
    meta = dict(book="algorithms", chapter=18,
                caption="The backward sweep's arrows, added up over every starting person, give each tie its own score. The tie between Hana and Ivo carries every route between Ivo or Jo and the other eight people, 16 in all.",
                alt=("The ten-person network with ties of varying thickness. The thickest, in orange, are Hana to Ivo (16), Fay to Hana and Gus to Hana (10.5 each) and Ivo to Jo (9). "
                     "Ties inside the tight group on the left are thin, most carrying under 4."),
                data={"edges": [list(e) for e in EDGES], "edge_betweenness": [eb[e] for e in EDGES]})
    return c, meta


FIGURES["alg-bt-edge-credit"] = edge_credit

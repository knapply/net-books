"""Figures for the path-enumeration chapter of the algorithms book (chapter 8).

Standard library only. Every number drawn is computed here (counting by breadth-first search, listing by
backtracking), so the pictures cannot drift from the arithmetic in the text.
"""
import math
from itertools import product

from fig_alg_all_pairs import (BLUE, FAINT, GRAY, GREEN, INK, KITE, LIGHT, MUTED, NAMES10, ORANGE, PAPER, PURPLE,
                               RED, SKY, Canvas, adjacency, draw_graph, kite_pos, table)

TRI5 = ["Ana", "Ben", "Cleo", "Dev", "Eli"]
TRI5_EDGES = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4)]


# ------------------------------------------------------------------ reference routines
def grid_edges(rows, cols):
    e = []
    for r, c in product(range(rows), range(cols)):
        if c + 1 < cols:
            e.append((r * cols + c, r * cols + c + 1))
        if r + 1 < rows:
            e.append((r * cols + c, (r + 1) * cols + c))
    return e


def count_shortest(n, edges, s):
    """Distance and number of shortest paths from s, by one breadth-first search."""
    adj = adjacency(n, edges)
    dist = [-1] * n
    sigma = [0] * n
    dist[s], sigma[s] = 0, 1
    q = [s]
    for u in q:
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
            if dist[v] == dist[u] + 1:
                sigma[v] += sigma[u]
    return dist, sigma


def simple_paths(n, edges, s, t, limit=None):
    """All simple paths s to t by backtracking. Returns (paths, steps, hit_limit)."""
    adj = adjacency(n, edges)
    paths, steps, stack = [], 0, [s]
    seen = {s}
    its = [iter(adj[s])]
    while its:
        u = stack[-1]
        nxt = next(its[-1], None)
        steps += 1
        if nxt is None:
            its.pop()
            seen.discard(stack.pop())
            continue
        if nxt in seen:
            continue
        if nxt == t:
            paths.append(stack + [t])
            if limit and len(paths) >= limit:
                return paths, steps, True
            continue
        stack.append(nxt)
        seen.add(nxt)
        its.append(iter(adj[nxt]))
    return paths, steps, False


def count_simple_grid(k):
    """Number of simple corner-to-corner paths on a k by k grid of people (count only, bit tricks for speed)."""
    n = k * k
    adj = adjacency(n, grid_edges(k, k))
    masks = [[(v, 1 << v) for v in a] for a in adj]
    target = n - 1
    total = 0
    stack = [(0, 1, iter(masks[0]))]
    while stack:
        u, seen, it = stack[-1]
        for v, bit in it:
            if seen & bit:
                continue
            if v == target:
                total += 1
                continue
            stack.append((v, seen | bit, iter(masks[v])))
            break
        else:
            stack.pop()
    return total


# ------------------------------------------------------------------ figures
def count_layers():
    rows, cols = 3, 4
    n = rows * cols
    E = grid_edges(rows, cols)
    dist, sigma = count_shortest(n, E, 0)
    assert sigma[n - 1] == math.comb(rows - 1 + cols - 1, rows - 1)
    pos = [(90 + (i % cols) * 110, 80 + (i // cols) * 90) for i in range(n)]
    shade = [LIGHT, "#d9ecf7", "#bfe0f3", "#9fd0ec", "#7fc0e6", "#f6c28a"]
    c = Canvas(780, 380, "Counting shortest routes with one search",
               "A three by four grid of people. Each dot shows how many shortest routes lead to it from the top left.")
    draw_graph(c, pos, E, [str(sigma[i]) for i in range(n)], r=22, fills=[shade[min(dist[i], 5)] for i in range(n)],
               strokes=[ORANGE if i == 0 else BLUE for i in range(n)], size=15)
    c.text(90, 52, "start", size=12, fill=ORANGE, weight="700")
    for d in range(rows + cols - 1):
        who = [i for i in range(n) if dist[i] == d]
        x = sum(pos[i][0] for i in who) / len(who)
        c.text(570 + 0, 80 + d * 34, f"{d} step{'s' if d != 1 else ''}:  {', '.join(str(sigma[i]) for i in who)}", size=13, anchor="start",
               fill=INK if d else ORANGE)
    c.text(560, 56, "Routes counted, level by level", size=13, weight="700", anchor="start")
    c.text(560, 290, "Each number is the sum of its", size=12.5, anchor="start", fill=MUTED)
    c.text(560, 310, "neighbors' numbers one step", size=12.5, anchor="start", fill=MUTED)
    c.text(560, 330, "closer to the start.", size=12.5, anchor="start", fill=MUTED)
    c.text(560, 346, f"Bottom right: {sigma[n - 1]} shortest routes.", size=13, anchor="start", weight="700")
    meta = dict(chapter=8,
                caption=f"Counting shortest routes. One breadth-first search from the top left also counts: each person's number is the sum of the numbers of the neighbors one step closer. The far corner has {sigma[n - 1]} shortest routes.",
                alt=f"A grid of twelve people in three rows and four columns. The top-left dot is 1. The first row reads 1, 1, 1, 1, the second 1, 2, 3, 4 and the third 1, 3, 6, 10. Darker shading marks people farther from the start. The bottom-right dot shows {sigma[n - 1]}.",
                data={"sigma": sigma, "dist": dist})
    return c, meta


def grid_explosion():
    ks = [2, 3, 4, 5, 6]
    simple = {k: count_simple_grid(k) for k in ks}
    assert [simple[k] for k in ks[:4]] == [2, 12, 184, 8512]
    shortest = {k: math.comb(2 * (k - 1), k - 1) for k in range(2, 8)}
    c = Canvas(900, 470, "Why counting routes explodes on a grid",
               "Number of routes between opposite corners of a square grid of people, shortest routes against all routes, on a log scale.")
    x0, y0, w, h = 90, 40, 480, 330
    sx = lambda k: x0 + (k - 2) / 5 * w
    top = 7
    sy = lambda v: y0 + h - math.log10(max(v, 1)) / top * h
    for e in range(0, top + 1):
        c.add(f'<line x1="{x0}" y1="{sy(10 ** e):.1f}" x2="{x0 + w}" y2="{sy(10 ** e):.1f}" stroke="{FAINT}" stroke-width="1"/>')
        c.text(x0 - 8, sy(10 ** e) + 4, f"10^{e}" if e > 1 else str(10 ** e), size=11, anchor="end", fill=MUTED)
    for k in range(2, 8):
        c.text(sx(k), y0 + h + 22, f"{k}×{k}", size=12, fill=MUTED)
    c.text(x0 + w / 2, y0 + h + 46, "grid size (people per side)", size=12.5, fill=MUTED)
    pts_s = " ".join(f"{sx(k):.1f},{sy(shortest[k]):.1f}" for k in range(2, 8))
    c.add(f'<polyline points="{pts_s}" fill="none" stroke="{BLUE}" stroke-width="2.6"/>')
    for k in range(2, 8):
        c.add(f'<circle cx="{sx(k):.1f}" cy="{sy(shortest[k]):.1f}" r="4.5" fill="{BLUE}"/>')
    pts_a = " ".join(f"{sx(k):.1f},{sy(simple[k]):.1f}" for k in ks)
    c.add(f'<polyline points="{pts_a}" fill="none" stroke="{RED}" stroke-width="2.6" stroke-dasharray="7 4"/>')
    for k in ks:
        c.add(f'<rect x="{sx(k) - 4.5:.1f}" y="{sy(simple[k]) - 4.5:.1f}" width="9" height="9" fill="{RED}"/>')
    c.text(sx(5) - 6, sy(simple[5]) - 12, "all routes", size=13, weight="700", fill=RED, anchor="end")
    c.text(sx(5), sy(shortest[5]) + 30, "shortest routes only", size=13, weight="700", fill=BLUE, anchor="middle")
    rows = [[f"{k}×{k}", f"{shortest[k]:,}", f"{simple[k]:,}" if k in simple else "too many to run"] for k in range(2, 8)]
    c.text(600, 66, "Grid", size=12.5, weight="700", anchor="start")
    c.text(665, 66, "Shortest", size=12.5, weight="700", anchor="start")
    c.text(760, 66, "All", size=12.5, weight="700", anchor="start")
    for i, r in enumerate(rows):
        y = 96 + i * 30
        c.text(600, y, r[0], size=13, anchor="start")
        c.text(665, y, r[1], size=13, anchor="start", fill=BLUE)
        c.text(760, y, r[2], size=11 if len(r[2]) > 9 else 13, anchor="start", fill=RED)
    ratios = ", ".join(f"{simple[k + 1] / simple[k]:.0f}" for k in (3, 4, 5))
    c.text(600, 300, "Both counts come from running", size=12, anchor="start", fill=MUTED)
    c.text(600, 318, "the searches. One more person", size=12, anchor="start", fill=MUTED)
    c.text(600, 336, "per side multiplies all routes by", size=12, anchor="start", fill=MUTED)
    c.text(600, 354, f"{ratios}, each time.", size=12, anchor="start", fill=MUTED)
    meta = dict(chapter=8,
                caption=f"Routes between opposite corners of a square grid of people. Shortest routes grow steadily (252 on a 6 by 6 grid). Routes that never repeat a person grow wildly: {simple[6]:,} on a 6 by 6 grid, and each extra person per side multiplies the count by more than the last.",
                alt=f"A line chart on a log scale. The blue line for shortest routes climbs from 2 on a 2 by 2 grid to 924 on a 7 by 7 grid. The red dashed line for all routes that never repeat a person climbs much faster: 2, 12, 184, 8,512, then {simple[6]:,} for the 6 by 6 grid, where it stops. A table at the right lists the same numbers.",
                data={"shortest": {str(k): v for k, v in shortest.items()}, "simple": {str(k): v for k, v in simple.items()}})
    return c, meta


def backtrack_tree():
    n = 5
    E = TRI5_EDGES
    adj = adjacency(n, E)
    c = Canvas(920, 470, "Listing every route by trying and backing up",
               "A five-person network on the left and the tree of everything the search tries from Ana toward Eli on the right.")
    pos = [(50, 190), (150, 120), (150, 260), (270, 190), (360, 190)]
    pos = [(x + 10, y + 20) for x, y in pos]
    draw_graph(c, pos, E, TRI5, r=20, size=11)
    c.text(190, 50, "Find every route from Ana to Eli", size=14, weight="700")
    c.text(190, 380, "Rule: never step on someone", size=12.5, fill=MUTED)
    c.text(190, 400, "already on the current route.", size=12.5, fill=MUTED)
    # build the search tree
    nodes = []  # (label path, parent index, kind)

    def grow(path, parent):
        u = path[-1]
        for v in adj[u]:
            if v in path:
                continue
            idx = len(nodes)
            kind = "found" if v == 4 else "open"
            nodes.append((path + [v], parent, kind))
            if v != 4:
                before = len(nodes)
                grow(path + [v], idx)
                if len(nodes) == before:
                    nodes[idx] = (path + [v], parent, "dead")
    nodes.append(([0], -1, "root"))
    grow([0], 0)
    found = [nd for nd in nodes if nd[2] == "found"]
    assert len(found) == len(simple_paths(n, E, 0, 4)[0])
    # layout by depth and leaf order
    depth = [len(p) - 1 for p, _, _ in nodes]
    kids = {i: [j for j, nd in enumerate(nodes) if nd[1] == i and j != i] for i in range(len(nodes))}
    xs = {}
    leaf = [0]

    def place(i):
        if not kids[i]:
            xs[i] = leaf[0]
            leaf[0] += 1
        else:
            for j in kids[i]:
                place(j)
            xs[i] = sum(xs[j] for j in kids[i]) / len(kids[i])
    place(0)
    sx = lambda i: 470 + 60 + xs[i] * 62
    sy = lambda i: 50 + depth[i] * 80
    # tree is drawn rotated: depth goes left to right
    px = lambda i: 440 + depth[i] * 92
    py = lambda i: 56 + xs[i] * 48
    for i, (path, par, kind) in enumerate(nodes):
        if par >= 0 and i != 0:
            col = GREEN if kind == "found" else GRAY
            c.add(f'<line x1="{px(par):.1f}" y1="{py(par):.1f}" x2="{px(i):.1f}" y2="{py(i):.1f}" stroke="{col}" stroke-width="2"/>')
    for i, (path, par, kind) in enumerate(nodes):
        fill = {"root": ORANGE + "88", "found": GREEN + "66", "dead": "#e5e7eb", "open": LIGHT}[kind]
        stroke = {"root": ORANGE, "found": GREEN, "dead": GRAY, "open": BLUE}[kind]
        c.node(px(i), py(i), TRI5[path[-1]], r=19, fill=fill, stroke=stroke, size=9.5)
    c.text(450, 440, "Green: reached Eli, one route recorded.  Gray: stuck, back up and try the next neighbor.", size=12, anchor="start", fill=MUTED)
    meta = dict(chapter=8,
                caption=f"Backtracking. From Ana the search tries each neighbor, then that person's neighbors, never stepping on someone already on the route. Green leaves are routes to Eli ({len(found)} of them); gray leaves are dead ends where the search backs up.",
                alt=f"On the left, a network of Ana, Ben, Cleo, Dev and Eli. On the right, a tree that starts at Ana and branches into every route the search tries. Four branches end at Eli and are drawn green. Other branches end at someone who has no unvisited neighbor and are drawn gray.",
                data={"paths": [[TRI5[v] for v in p] for p, _, k in nodes if k == "found"]})
    return c, meta


def length_histogram():
    k = 4
    n = k * k
    paths, steps, _ = simple_paths(n, grid_edges(k, k), 0, n - 1)
    by = {}
    for p in paths:
        by[len(p) - 1] = by.get(len(p) - 1, 0) + 1
    lens = sorted(by)
    c = Canvas(860, 400, "Most routes are the long ones",
               "A bar for each route length on a four by four grid of people, counting every route that never repeats a person.")
    x0, y0, w, h = 90, 30, 700, 280
    mx = max(by.values())
    bw = w / (len(lens) + 0.6)
    for i, L in enumerate(lens):
        x = x0 + i * bw + bw * 0.15
        bh = by[L] / mx * h
        col = BLUE if L == lens[0] else GRAY
        c.rect(x, y0 + h - bh, bw * 0.7, bh, fill=col + "66", stroke=col, sw=1.3)
        c.text(x + bw * 0.35, y0 + h - bh - 8, str(by[L]), size=13, weight="700")
        c.text(x + bw * 0.35, y0 + h + 22, f"{L} steps", size=12.5, fill=MUTED)
    c.text(x0 + w / 2, y0 + h + 52, f"All {len(paths)} routes between opposite corners, grouped by length", size=13, weight="600")
    c.text(x0 + w / 2, y0 + h + 76, "Only the first bar (blue) holds shortest routes. Capping by length keeps the cheap end.", size=12.5, fill=MUTED)
    meta = dict(chapter=8,
                caption=f"Routes between opposite corners of a 4 by 4 grid, by length. There are {by[lens[0]]} shortest routes (6 steps) and {len(paths)} in all. Most routes are long and winding.",
                alt=f"A bar chart with one bar for each route length from {lens[0]} to {lens[-1]} steps. The first bar, in blue, is {by[lens[0]]}. The bars grow to a peak and shrink again. The bars add up to {len(paths)}.",
                data={"by_length": {str(L): by[L] for L in lens}, "total": len(paths), "search_steps": steps})
    return c, meta


def walks_vs_paths():
    n = 5
    A = [[0] * n for _ in range(n)]
    for a, b in TRI5_EDGES:
        A[a][b] = A[b][a] = 1
    P = [[int(i == j) for j in range(n)] for i in range(n)]
    walks = []
    for L in range(1, 11):
        P = [[sum(P[i][k] * A[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        walks.append(P[0][4])
    c = Canvas(900, 380, "Walks multiply, routes do not",
               "Number of walks of each length from Ana to Eli in a five-person network, on a log scale, with the number of routes that never repeat a person.")
    x0, y0, w, h = 90, 30, 520, 280
    top = 3
    sy = lambda v: y0 + h - math.log10(max(v, 1)) / top * h
    bw = w / 10
    for e in range(0, top + 1):
        c.add(f'<line x1="{x0}" y1="{sy(10 ** e):.1f}" x2="{x0 + w}" y2="{sy(10 ** e):.1f}" stroke="{FAINT}" stroke-width="1"/>')
        c.text(x0 - 8, sy(10 ** e) + 4, str(10 ** e), size=11, anchor="end", fill=MUTED)
    for i, v in enumerate(walks):
        x = x0 + i * bw + 5
        if v:
            c.rect(x, sy(v), bw - 10, y0 + h - sy(v), fill=ORANGE + "66", stroke=ORANGE, sw=1.2)
            c.text(x + (bw - 10) / 2, sy(v) - 6, str(v), size=11.5)
        c.text(x + (bw - 10) / 2, y0 + h + 18, str(i + 1), size=12, fill=MUTED)
    c.text(x0 + w / 2, y0 + h + 44, "length of the walk (steps)", size=12.5, fill=MUTED)
    paths = len(simple_paths(n, TRI5_EDGES, 0, 4)[0])
    c.add(f'<line x1="{x0}" y1="{sy(paths):.1f}" x2="{x0 + w}" y2="{sy(paths):.1f}" stroke="{BLUE}" stroke-width="2.4" stroke-dasharray="7 4"/>')
    c.text(x0 + w + 12, sy(paths) + 5, f"{paths} routes that never repeat anyone", size=12.5, anchor="start", fill=BLUE, weight="700")
    c.text(x0 + w + 12, 70, "Walks may double back", size=12.5, anchor="start", weight="700", fill=ORANGE)
    c.text(x0 + w + 12, 90, "and revisit people, so their", size=12.5, anchor="start", fill=MUTED)
    c.text(x0 + w + 12, 108, "number keeps growing.", size=12.5, anchor="start", fill=MUTED)
    meta = dict(chapter=8,
                caption=f"Counting walks is easy (multiply the tie table by itself) and the answer keeps growing. Counting routes that never repeat a person is a different question, and for Ana to Eli it stays at {paths}.",
                alt=f"A bar chart on a log scale of the number of walks from Ana to Eli of each length from 1 to 10. There are none for lengths 1 and 2, then {walks[2]}, {walks[3]}, and so on, growing steadily to {walks[-1]}. A dashed blue line at {paths} marks the routes that never repeat anyone.",
                data={"walks": walks, "paths": paths})
    return c, meta


def k_shortest():
    n = 10
    s, t = 0, 6  # Ana to Gus
    paths, _, _ = simple_paths(n, KITE, s, t)
    paths.sort(key=lambda p: (len(p), p))
    top = paths[:4]
    pos = kite_pos(0, 0, 380, 165)
    c = Canvas(960, 560, "The first few shortest routes, in order",
               "Four copies of the ten-person network from Ana to Gus, each highlighting the first, second, third and fourth shortest route.")
    cols = [ORANGE, GREEN, PURPLE, RED]
    titles = []
    for k, p in enumerate(top):
        ox, oy = 20 + (k % 2) * 470, 24 + (k // 2) * 270
        c.rect(ox, oy, 450, 255, fill="none", stroke=FAINT, sw=1, rx=8)
        L = len(p) - 1
        c.text(ox + 12, oy + 24, f"Route {k + 1}: {L} steps", size=14, weight="700", anchor="start", fill=cols[k])
        c.text(ox + 12, oy + 44, " to ".join(NAMES10[v] for v in p), size=12.5, anchor="start", fill=MUTED)
        pp = [(x + ox + 36, y + oy + 62) for x, y in pos]
        onp = {frozenset(e) for e in zip(p, p[1:])}
        ecol = {i: (cols[k] if frozenset(e) in onp else "#e5e7eb") for i, e in enumerate(KITE)}
        ewid = {i: (4 if frozenset(e) in onp else 1.4) for i, e in enumerate(KITE)}
        fills = [cols[k] + "77" if i in p else "#f5f9fc" for i in range(n)]
        draw_graph(c, pp, KITE, [NAMES10[i][:3] for i in range(n)], r=13, fills=fills,
                   strokes=[cols[k] if i in p else "#b6c4cf" for i in range(n)], ecolor=ecol, ewidth=ewid, size=8.5)
        titles.append(L)
    shortest = sum(1 for p in paths if len(p) == len(paths[0]))
    meta = dict(chapter=8,
                caption=f"The first four routes from Ana to Gus, shortest first. Three tie at {titles[0]} steps (through Ben, Dev or Fay); the fourth takes {titles[3]}. {len(paths)} routes exist in all that never repeat a person.",
                alt=f"Four copies of the ten-person network. In each, one route from Ana to Gus is drawn thickly. The first three routes have {titles[0]} steps and go through Ben, through Dev and through Fay. The fourth route has {titles[3]} steps.",
                data={"routes": [[NAMES10[v] for v in p] for p in top], "all_simple": len(paths)})
    return c, meta


def cap_receipt():
    k = 6
    total = count_simple_grid(k)
    cap = 10000
    c = Canvas(860, 380, "An honest answer when you stop early",
               "Two cards: what a capped route listing should report, and what it should not.")
    c.rect(30, 30, 380, 300, fill=GREEN + "10", stroke=GREEN, sw=2, rx=10)
    c.text(220, 62, "Honest receipt", size=16, weight="700", fill=GREEN)
    c.lines(54, 100, ["Question:  every route, corner to corner,", "           6 by 6 grid of people", "Limit I set:  10,000 routes", "Routes listed:  10,000",
                      "Stopped by the limit?  YES", "", "So the true number is", "AT LEAST 10,000.", "Everything listed is a real route."], size=14, mono=True, gap=1.5)
    c.rect(450, 30, 380, 300, fill=RED + "10", stroke=RED, sw=2, rx=10, dash="8 5")
    c.text(640, 62, "Dishonest receipt", size=16, weight="700", fill=RED)
    c.lines(474, 100, ["Question:  every route, corner to corner,", "           6 by 6 grid of people", "Routes found:  10,000", "", "(Silent about the limit.)", "", "Reader assumes the answer is", "exactly 10,000.", f"It is {total:,}."], size=14, mono=True, gap=1.5)
    c.text(430, 362, f"The limit saved time, but only the first receipt says so.", size=13, fill=MUTED)
    meta = dict(chapter=8,
                caption=f"Capping the work honestly. A listing that stops at a limit must say it stopped and report its result as a lower bound. On this 6 by 6 grid the true count is {total:,}, over a hundred times the limit.",
                alt=f"Two cards. The left one, green, reports a limit of 10,000 routes, 10,000 listed, stopped by the limit, so at least 10,000. The right one, red and dashed, reports 10,000 routes found and says nothing about the limit, leaving the reader to think that is the total, when the true total is {total:,}.",
                data={"cap": cap, "true_total": total})
    return c, meta


def shortest_dag():
    n = 10
    dist, sigma = count_shortest(n, KITE, 9)  # from Jo
    pos = kite_pos(30, 50, 520, 280)
    c = Canvas(860, 400, "Shortest-route counts on the friendship network",
               "The ten-person network with each person's number of shortest routes from Jo, and the ties those routes use drawn in orange.")
    on = {i for i, (a, b) in enumerate(KITE) if abs(dist[a] - dist[b]) == 1}
    ecol = {i: (ORANGE if i in on else "#d1d5db") for i in range(len(KITE))}
    ewid = {i: (3 if i in on else 1.2) for i in range(len(KITE))}
    shade = ["#f6c28a", "#e4f1f9", "#c6e2f3", "#9fd0ec", "#7fc0e6"]
    draw_graph(c, pos, KITE, [str(sigma[i]) for i in range(n)], r=17, fills=[shade[min(dist[i], 4)] for i in range(n)],
               ecolor=ecol, ewidth=ewid, size=13)
    for i, p in enumerate(pos):
        c.text(p[0], p[1] - 24, NAMES10[i], size=11, fill=MUTED)
    c.text(700, 80, "Starting from Jo", size=14, weight="700")
    c.lines(620, 112, [f"{NAMES10[i]}: {sigma[i]} shortest route{'s' if sigma[i] != 1 else ''} ({dist[i]} step{'s' if dist[i] != 1 else ''})" for i in sorted(range(n), key=lambda i: (dist[i], NAMES10[i])) if i != 9], size=12, gap=1.5, fill=INK)
    meta = dict(chapter=8,
                caption="Number of shortest routes from Jo to each person. Orange ties are the ones on some shortest route. Only Dev has two shortest routes from Jo (one through Fay, one through Gus); everyone else has exactly one.",
                alt=f"The ten-person network with each dot showing a count from Jo. Jo shows 1, Ivo 1, Hana 1, Fay 1, Gus 1, then Ana {sigma[0]}, Ben {sigma[1]}, Cleo {sigma[2]}, Dev {sigma[3]} and Eli {sigma[4]}. Ties that lie on a shortest route from Jo are orange and thick; the others are thin and gray.",
                data={"dist": dist, "sigma": sigma})
    return c, meta


FIGURES = {
    "count-layers": count_layers, "shortest-dag": shortest_dag, "backtrack-tree": backtrack_tree,
    "k-shortest": k_shortest, "walks-vs-paths": walks_vs_paths, "length-histogram": length_histogram,
    "grid-explosion": grid_explosion, "cap-receipt": cap_receipt,
}

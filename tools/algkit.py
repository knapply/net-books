"""Shared helpers for the algorithms-book figures and animation scenes (chapters 4 to 6). Standard library only.

Holds the ten-person friendship network (the book's usual edge list), small reference routines that return a full
trace (queue contents, stack, heap labels), grid helpers and a drawing function. The traces are the textbook rules, so
a scene can show every step; each scene asserts that its final answer equals what the engine returned.
"""
import heapq
import math
import random
from collections import deque

from fig_layout import fit, stress_layout
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, PURPLE, RED, SKY, Canvas

GRAY = "#9ca3af"
PALE = "#eef6fb"
NAMES = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jo"]
EDGES = [(0, 1), (0, 2), (0, 3), (0, 5), (1, 3), (1, 4), (1, 6), (2, 3), (2, 5), (3, 4),
         (3, 5), (3, 6), (4, 6), (5, 6), (5, 7), (6, 7), (7, 8), (8, 9)]
# Minutes between friends, in the order of EDGES (the same numbers as tools/anim_data/src/bin/dijkstra-queue.rs).
MINUTES = [6, 2, 9, 8, 3, 6, 10, 5, 8, 2, 4, 7, 3, 6, 5, 2, 4, 3]


def adjacency(n, edges):
    """Sorted neighbour lists (the order every routine here visits friends in)."""
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return [sorted(s) for s in adj]


def weighted_adjacency(n, edges, w):
    adj = [[] for _ in range(n)]
    for (a, b), x in zip(edges, w):
        adj[a].append((b, x))
        adj[b].append((a, x))
    return [sorted(r) for r in adj]


def kite_pos(x0, y0, w, h):
    return fit(stress_layout(10, EDGES, seed=3), x0, y0, w, h)


def weighted_layout(n, edges, w, x0, y0, bw, bh, seed=3, iters=300):
    """Stress layout where edge lengths follow the travel times (distances are weighted shortest paths)."""
    d = [[math.inf] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for (a, b), x in zip(edges, w):
        d[a][b] = d[b][a] = min(d[a][b], x)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    rng = random.Random(seed)
    x = [[rng.uniform(-1, 1), rng.uniform(-1, 1)] for _ in range(n)]
    wt = [[(1 / d[i][j] ** 2) if i != j else 0 for j in range(n)] for i in range(n)]
    for _ in range(iters):
        new = []
        for i in range(n):
            sw = sum(wt[i])
            sx = sy = 0.0
            for j in range(n):
                if i == j:
                    continue
                dx, dy = x[i][0] - x[j][0], x[i][1] - x[j][1]
                dist = math.hypot(dx, dy) or 1e-9
                sx += wt[i][j] * (x[j][0] + d[i][j] * dx / dist)
                sy += wt[i][j] * (x[j][1] + d[i][j] * dy / dist)
            new.append([sx / sw, sy / sw])
        x = new
    return fit([tuple(p) for p in x], x0, y0, bw, bh)


# --------------------------------------------------------------------------- reference traces
def bfs_trace(adj, s):
    """Breadth-first search, friends taken in index order. Returns steps, order, dist and tree edges.

    Each step: dict(take=person taken off the front, new=people who join the back, queue=the line after the step)."""
    n = len(adj)
    dist = [None] * n
    dist[s] = 0
    queue = deque([s])
    order, tree, steps = [s], [], []
    while queue:
        u = queue.popleft()
        new = []
        for v in adj[u]:
            if dist[v] is None:
                dist[v] = dist[u] + 1
                queue.append(v)
                order.append(v)
                tree.append((u, v))
                new.append(v)
        steps.append(dict(take=u, new=new, queue=list(queue)))
    return steps, order, dist, tree


def dfs_trace(adj, s):
    """Depth-first search: go to the first friend not yet seen, back up when there is none.

    Events: ('go', parent, child, trail) and ('back', child, parent, trail), where trail is the stack (start .. here)."""
    n = len(adj)
    seen = [False] * n
    seen[s] = True
    trail = [s]
    pos = [0] * n
    events, order, tree = [], [s], []
    while trail:
        u = trail[-1]
        while pos[u] < len(adj[u]) and seen[adj[u][pos[u]]]:
            pos[u] += 1
        if pos[u] < len(adj[u]):
            v = adj[u][pos[u]]
            pos[u] += 1
            seen[v] = True
            trail.append(v)
            order.append(v)
            tree.append((u, v))
            events.append(("go", u, v, list(trail)))
        else:
            trail.pop()
            if trail:
                events.append(("back", u, trail[-1], list(trail)))
    return events, order, tree


def dijkstra_trace(adj, s):
    """Dijkstra's algorithm with a waiting list. Ties are settled by person index.

    Returns steps (settle one person per step), final dist and parent. Each step records the person settled, the
    changes made to neighbours' best-known distances, and the waiting list (sorted) after the step."""
    n = len(adj)
    best = [math.inf] * n
    parent = [None] * n
    best[s] = 0
    heap = [(0, s)]
    settled = [False] * n
    steps = []
    while heap:
        d, u = heapq.heappop(heap)
        if settled[u] or d > best[u]:
            continue
        settled[u] = True
        changes = []
        for v, w in adj[u]:
            if not settled[v] and d + w < best[v]:
                old = best[v]
                best[v] = d + w
                parent[v] = u
                heapq.heappush(heap, (best[v], v))
                changes.append((v, old, best[v]))
        waiting = sorted((best[v], v) for v in range(n) if not settled[v] and best[v] < math.inf)
        steps.append(dict(settle=u, dist=d, changes=changes, waiting=waiting, settled=[i for i in range(n) if settled[i]]))
    return steps, best, parent


def bellman_ford_rounds(n, arcs, s):
    """Rounds of Bellman-Ford on directed arcs (a, b, w): in each round, try every arc once.

    Returns the distance list after each round (round 0 is the start) and whether round n still improved."""
    dist = [math.inf] * n
    dist[s] = 0
    hist = [list(dist)]
    improved = False
    for r in range(n):
        improved = False
        for a, b, w in arcs:
            if dist[a] + w < dist[b]:
                dist[b] = dist[a] + w
                improved = True
        hist.append(list(dist))
        if not improved:
            break
    return hist, improved


def dijkstra_greedy_directed(n, arcs, s):
    """Dijkstra's rule applied to arcs that include negative ones (it never reopens a settled person)."""
    adj = [[] for _ in range(n)]
    for a, b, w in arcs:
        adj[a].append((b, w))
    best = [math.inf] * n
    best[s] = 0
    done = [False] * n
    heap = [(0, s)]
    while heap:
        d, u = heapq.heappop(heap)
        if done[u]:
            continue
        done[u] = True
        for v, w in adj[u]:
            if not done[v] and d + w < best[v]:
                best[v] = d + w
                heapq.heappush(heap, (best[v], v))
    return best


# --------------------------------------------------------------------------- grids
def grid_edges(w, h, wall=lambda r, c, r2, c2: False):
    e = []
    for r in range(h):
        for c in range(w):
            v = r * w + c
            if c + 1 < w and not wall(r, c, r, c + 1):
                e.append((v, v + 1))
            if r + 1 < h and not wall(r, c, r + 1, c):
                e.append((v, v + w))
    return e


def bfs_ball(adj, s, t=None):
    """People found in order by plain breadth-first search (stopping when t is taken off the line, if given)."""
    dist = {s: 0}
    queue = deque([s])
    found = [s]
    while queue:
        u = queue.popleft()
        if u == t:
            break
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
                found.append(v)
    return found, dist


# --------------------------------------------------------------------------- drawing
def draw_graph(c, pos, edges, node=None, edge=None, r=18, size=12, names=None, name_size=11, directed=False):
    """node(i) -> dict(fill, stroke, label, shape, ring, label_fill, r); edge(k) -> dict(color, width, dash)."""
    for k, (a, b) in enumerate(edges):
        st = {"color": GRAY, "width": 1.8, "dash": None}
        if edge:
            st.update(edge(k) or {})
        ra = (node(a) or {}).get("r", r) if node else r
        rb = (node(b) or {}).get("r", r) if node else r
        c.edge(pos[a], pos[b], ra=ra, rb=rb, color=st["color"], width=st["width"], dash=st["dash"], directed=directed)
    for i, p in enumerate(pos):
        st = {"fill": PALE, "stroke": BLUE, "label": "", "shape": "circle", "ring": False, "label_fill": INK, "r": r}
        if node:
            st.update(node(i) or {})
        if st["ring"]:
            c.add(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{st["r"] + 5}" fill="none" stroke="{RED}" stroke-width="2.2"/>')
        c.node(p[0], p[1], st["label"], r=st["r"], fill=st["fill"], stroke=st["stroke"], shape=st["shape"], size=size,
               label_fill=st["label_fill"])
        if names:
            c.text(p[0], p[1] + st["r"] + 14, names[i], size=name_size, fill=MUTED)


def edge_mid(pos, a, b, off=0.0):
    (x1, y1), (x2, y2) = pos[a], pos[b]
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def weight_tag(c, pos, a, b, text, size=11, frac=0.5):
    """A small white label with the edge's weight, a fraction of the way from a to b (the middle by default)."""
    x = pos[a][0] + (pos[b][0] - pos[a][0]) * frac
    y = pos[a][1] + (pos[b][1] - pos[a][1]) * frac
    w = 7 * len(str(text)) + 6
    c.add(f'<rect x="{x - w / 2:.1f}" y="{y - 9:.1f}" width="{w}" height="18" rx="9" fill="{PAPER}" stroke="{FAINT}" stroke-width="1"/>')
    c.text(x, y + 4, str(text), size=size, fill=INK, weight="600")


def table(c, x, y, headers, rows, widths, row_h=26, size=12.5, head_fill="#f3f4f6", hl=None):
    """A plain table; hl is a set of row indexes to tint."""
    hl = hl or set()
    tx = x
    c.rect(x, y, sum(widths), row_h, fill=head_fill, stroke=FAINT, sw=1)
    for h, w in zip(headers, widths):
        c.text(tx + 8, y + row_h * 0.68, h, size=size, anchor="start", weight="700")
        tx += w
    for i, row in enumerate(rows):
        yy = y + row_h * (i + 1)
        c.rect(x, yy, sum(widths), row_h, fill=(ORANGE + "22" if i in hl else PAPER), stroke=FAINT, sw=1)
        tx = x
        for cell, w in zip(row, widths):
            c.text(tx + 8, yy + row_h * 0.68, str(cell), size=size, anchor="start")
            tx += w
    return y + row_h * (len(rows) + 1)


def join(words):
    words = list(words)
    if not words:
        return "nobody"
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]

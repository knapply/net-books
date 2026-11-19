"""Figures for the components chapter of the algorithms book (chapter 9).

Standard library only. Components, union-find trees, Tarjan's numbers and Kosaraju's passes are all computed here
by short reference routines, so the pictures cannot drift from the arithmetic in the text.
"""
import math
import random

from fig_alg_all_pairs import (BLUE, FAINT, GRAY, GREEN, INF, INK, KITE, LIGHT, MUTED, NAMES10, ORANGE, PAPER,
                               PURPLE, RED, SKY, Canvas, adjacency, draw_graph, table)

SYS = [BLUE, ORANGE, GREEN, PURPLE, RED, SKY]

# ------------------------------------------------------------------ the networks
ISL_NAMES = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jo", "Kai"]
ISL_EDGES = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4), (5, 6), (6, 7), (8, 9)]
ISL_POS = [(70, 100), (150, 55), (150, 150), (240, 100), (330, 100), (440, 70), (520, 110), (600, 70), (460, 190),
           (550, 200), (330, 200)]

DN = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo"]
D_ARCS = [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4), (4, 5), (5, 3), (4, 6), (6, 7), (7, 6), (4, 8), (8, 6)]
D_POS = [(60, 60), (150, 120), (60, 180), (260, 120), (350, 70), (350, 190), (470, 60), (560, 120), (470, 190)]


# ------------------------------------------------------------------ reference routines
def components_bfs(n, edges):
    adj = adjacency(n, edges)
    comp = [-1] * n
    order = []
    c = 0
    for s in range(n):
        if comp[s] >= 0:
            continue
        comp[s] = c
        q = [s]
        for u in q:
            for v in adj[u]:
                if comp[v] < 0:
                    comp[v] = c
                    q.append(v)
        order.append(q[:])
        c += 1
    return comp, order


class UF:
    def __init__(self, n):
        self.p = list(range(n))
        self.size = [1] * n

    def find(self, x, compress=False):
        r = x
        while self.p[r] != r:
            r = self.p[r]
        if compress:
            while self.p[x] != r:
                self.p[x], x = r, self.p[x]
        return r

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        self.size[ra] += self.size[rb]
        return True


def tarjan(n, arcs):
    adj = [[] for _ in range(n)]
    for a, b in arcs:
        adj[a].append(b)
    for r in adj:
        r.sort()
    index = [None] * n
    low = [0] * n
    on = [False] * n
    stack, comps, counter = [], [], [0]

    def go(v):
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on[v] = True
        for w in adj[v]:
            if index[w] is None:
                go(w)
                low[v] = min(low[v], low[w])
            elif on[w]:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on[w] = False
                comp.append(w)
                if w == v:
                    break
            comps.append(sorted(comp))
    for v in range(n):
        if index[v] is None:
            go(v)
    return index, low, comps


def kosaraju(n, arcs):
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]
    for a, b in arcs:
        adj[a].append(b)
        radj[b].append(a)
    for r in adj + radj:
        r.sort()
    seen, finish = [False] * n, []

    def dfs1(v):
        seen[v] = True
        for w in adj[v]:
            if not seen[w]:
                dfs1(w)
        finish.append(v)
    for v in range(n):
        if not seen[v]:
            dfs1(v)
    comp = [-1] * n
    k = 0

    def dfs2(v):
        comp[v] = k
        for w in radj[v]:
            if comp[w] < 0:
                dfs2(w)
    for v in reversed(finish):
        if comp[v] < 0:
            dfs2(v)
            k += 1
    return finish, comp


def hull(c, pts, color, r=34, label=None):
    """A soft rounded box around some dots."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs) - r, max(xs) + r, min(ys) - r, max(ys) + r
    c.halo(x0, y0, x1 - x0, y1 - y0, color, label=label)


# ------------------------------------------------------------------ figures
def islands():
    n = len(ISL_NAMES)
    comp, order = components_bfs(n, ISL_EDGES)
    sizes = sorted((len(o) for o in order), reverse=True)
    c = Canvas(700, 300, "Islands in a network",
               "Eleven people in four groups with no tie between groups: five, three, two and one.")
    pos = [(x + 20, y + 20) for x, y in ISL_POS]
    for k, o in enumerate(order):
        hull(c, [pos[i] for i in o], SYS[k % len(SYS)], r=34, label=f"island of {len(o)}")
    draw_graph(c, pos, ISL_EDGES, [ISL_NAMES[i][:3] for i in range(n)], r=19, size=10.5,
               fills=[SYS[comp[i] % len(SYS)] + "44" for i in range(n)], strokes=[SYS[comp[i] % len(SYS)] for i in range(n)])
    meta = dict(chapter=9,
                caption="A connected component is an island: everyone on it can reach everyone else on it, and nobody can reach anyone off it. This network of eleven people has four islands. Kai, with no ties, is an island of one.",
                alt=f"Eleven people drawn in four dashed boxes. The largest box holds Ana, Ben, Cleo, Dev and Eli, tied together. Next, Fay, Gus and Hana in a chain. Then Ivo and Jo, tied to each other. Kai sits alone in the fourth box. There are no ties between boxes.",
                data={"sizes": sizes, "components": [[ISL_NAMES[i] for i in o] for o in order]})
    return c, meta


def sweep_labels():
    n = len(ISL_NAMES)
    comp, order = components_bfs(n, ISL_EDGES)
    adj = adjacency(n, ISL_EDGES)
    c = Canvas(960, 520, "Finding islands by searching again and again",
               "Four copies of the eleven-person network showing the label sweep: after the first, second, third and fourth search.")
    pos0 = [(x * 0.62 + 20, y * 0.62 + 40) for x, y in ISL_POS]
    for step in range(4):
        ox, oy = 20 + (step % 2) * 470, 14 + (step // 2) * 252
        c.rect(ox, oy, 450, 236, fill="none", stroke=FAINT, sw=1, rx=8)
        done = set(i for o in order[:step + 1] for i in o)
        starts = [o[0] for o in order]
        c.text(ox + 12, oy + 22, f"After search {step + 1}: start at {ISL_NAMES[starts[step]]}", size=13.5, weight="700", anchor="start")
        pos = [(x + ox, y + oy) for x, y in pos0]
        fills = [(SYS[comp[i] % len(SYS)] + "66") if i in done else "#f5f9fc" for i in range(n)]
        strokes = [(SYS[comp[i] % len(SYS)]) if i in done else "#b6c4cf" for i in range(n)]
        labs = [str(comp[i] + 1) if i in done else "" for i in range(n)]
        ewid = {k: (2.6 if (a in done and b in done) else 1.2) for k, (a, b) in enumerate(ISL_EDGES)}
        draw_graph(c, pos, ISL_EDGES, labs, r=14, fills=fills, strokes=strokes, ewidth=ewid, size=11)
        for i in range(n):
            c.text(pos[i][0], pos[i][1] + 27, ISL_NAMES[i][:3], size=9.5, fill=MUTED)
        c.text(ox + 12, oy + 224, f"{len(done)} of {n} people labeled, {step + 1} island{'s' if step else ''} found", size=12, anchor="start", fill=MUTED)
    meta = dict(chapter=9,
                caption="Finding components by search. Pick someone with no label, search outward from them and give everyone you reach the next label. Repeat until nobody is unlabeled. Four searches, four islands.",
                alt="Four copies of the eleven-person network. In the first, only the five-person island is labeled 1. In the second, the three-person island is added, labeled 2. In the third, the two-person island is labeled 3. In the fourth, Kai is labeled 4 and every person has a label.",
                data={"labels": comp})
    return c, meta


def tree_layout(parent, roots, x0, y0, dx, dy):
    kids = {}
    for v, p in enumerate(parent):
        if p != v:
            kids.setdefault(p, []).append(v)
    pos, cur = {}, [x0]

    def place(v, depth):
        ks = kids.get(v, [])
        if not ks:
            pos[v] = (cur[0], y0 + depth * dy)
            cur[0] += dx
        else:
            for k in ks:
                place(k, depth + 1)
            pos[v] = (sum(pos[k][0] for k in ks) / len(ks), y0 + depth * dy)
    for r in roots:
        place(r, 0)
        cur[0] += dx * 0.3
    return pos


def uf_forest():
    names = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana"]
    ties = [(0, 1), (2, 3), (1, 3), (4, 5), (6, 7), (5, 7), (3, 7)]
    uf = UF(8)
    snaps = [([*uf.p], [*uf.size], None)]
    for a, b in ties:
        uf.union(a, b)
        snaps.append(([*uf.p], [*uf.size], (a, b)))
    pick = [0, 2, 3, 6, 7]
    c = Canvas(960, 640, "Union-find: joining groups tie by tie",
               "Six snapshots of eight people as ties arrive, each person drawn under the person they point to, with the group leader on top.")
    show = [0, 1, 3, 4, 6, 7]
    for k, t in enumerate(show):
        ox, oy = 20 + (k % 3) * 315, 14 + (k // 3) * 310
        c.rect(ox, oy, 300, 296, fill="none", stroke=FAINT, sw=1, rx=8)
        parent, size, tie = snaps[t]
        head = "Start: everyone is their own group" if t == 0 else f"After tie {t}: {names[tie[0]]} and {names[tie[1]]}"
        c.text(ox + 12, oy + 22, head, size=12.5, weight="700", anchor="start")
        roots = [v for v in range(8) if parent[v] == v]
        pos = tree_layout(parent, roots, 0, 0, 1, 1)
        xs = [p[0] for p in pos.values()]
        span = max(xs) - min(xs) or 1
        sc = min(48, 250 / max(span, 1))
        mid = (max(xs) + min(xs)) / 2
        maxd = max(p[1] for p in pos.values())
        P = {v: (ox + 150 + (p[0] - mid) * sc, oy + 82 + p[1] * 62) for v, p in pos.items()}
        for v in range(8):
            if parent[v] != v:
                c.edge(P[v], P[parent[v]], ra=15, rb=15, directed=True, color=GRAY, width=1.8)
        for v in range(8):
            leader = parent[v] == v
            cmap = {r: SYS[i % len(SYS)] for i, r in enumerate(roots)}
            root = v
            while parent[root] != root:
                root = parent[root]
            c.node(P[v][0], P[v][1], names[v][:3], r=15, fill=cmap[root] + ("99" if leader else "33"), stroke=cmap[root], size=9.5,
                   sw=3 if leader else 1.8)
        c.text(ox + 12, oy + 286, f"{len(roots)} group{'s' if len(roots) != 1 else ''}; leaders have thick rims", size=11.5, anchor="start", fill=MUTED)
    meta = dict(chapter=9,
                caption="Union-find on eight people. Each person points to someone in their group, and the group's leader points to nobody. Joining two groups makes the smaller group's leader point to the bigger group's leader. Each tie is one tiny edit.",
                alt="Six snapshots of eight people. At the start there are eight separate groups. After one tie, Ana and Ben form a group. After three ties there is a group of four and two singletons. After four, five, and seven ties the groups merge until, after tie seven, all eight people hang under one leader in a short tree.",
                data={"parents": [s[0] for s in snaps]})
    return c, meta


def uf_compress():
    # a chain built by joining one person at a time under the previous leader (unlucky order), then a find with compression
    names = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay"]
    chain = [0, 0, 1, 2, 3, 4]  # each points to the one before it
    c = Canvas(900, 400, "Path compression: leave a shortcut behind",
               "Left: a chain of six people, each pointing to the one before. Right: the same people after one lookup from Fay that makes everyone on the walk point straight at the leader.")
    def draw(ox, parent, title, note):
        c.text(ox + 190, 40, title, size=15, weight="700")
        pos = {v: (ox + 40 + v * 62, 120 + (v if parent is chain else 0) * 0) for v in range(6)}
        if parent is chain:
            pos = {v: (ox + 190, 74 + v * 52) for v in range(6)}
        else:
            pos = {0: (ox + 190, 74), 1: (ox + 70, 190), 2: (ox + 130, 190), 3: (ox + 190, 190), 4: (ox + 250, 190), 5: (ox + 310, 190)}
        for v in range(6):
            if parent[v] != v:
                c.edge(pos[v], pos[parent[v]], ra=15, rb=15, directed=True, color=ORANGE if parent is not chain and v > 0 else GRAY,
                       width=2.2)
        for v in range(6):
            c.node(pos[v][0], pos[v][1], names[v][:3], r=15, fill=(GREEN + "88" if v == 0 else LIGHT), stroke=GREEN if v == 0 else BLUE, size=9.5)
        c.text(ox + 190, 360, note, size=12.5, fill=MUTED)
    draw(10, chain, "Before: Fay is five hops from the leader", "Each lookup from Fay walks five hops.")
    uf = UF(6)
    uf.p = chain[:]
    uf.find(5, compress=True)
    after = uf.p[:]
    assert after == [0, 0, 0, 0, 0, 0]
    draw(470, after, "After one lookup from Fay", "Everyone on the walk now points at Ana: one hop.")
    meta = dict(chapter=9,
                caption="Path compression. A lookup walks up to the group's leader; on the way back it makes every person it passed point straight at the leader. The next lookup from any of them is one hop.",
                alt="Left: six people stacked in a chain, each pointing at the one above, Ana at the top, so Fay is five hops below. Right: Ana at the top with the other five people in a row below her, each pointing directly at Ana with an orange arrow.",
                data={"before": chain, "after": after})
    return c, meta


def ties_arrive():
    n = 10
    uf = UF(n)
    counts = [n]
    largest = [1]
    for a, b in KITE:
        uf.union(a, b)
        counts.append(len({uf.find(i) for i in range(n)}))
        sz = {}
        for i in range(n):
            r = uf.find(i)
            sz[r] = sz.get(r, 0) + 1
        largest.append(max(sz.values()))
    c = Canvas(860, 380, "Components as ties arrive",
               "Number of groups and size of the biggest group after each of the eighteen ties of the friendship network is added.")
    x0, y0, w, h = 80, 30, 700, 260
    sx = lambda k: x0 + k / 18 * w
    sy = lambda v: y0 + h - v / 10 * h
    for v in (0, 2, 4, 6, 8, 10):
        c.add(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0 + w}" y2="{sy(v):.1f}" stroke="{FAINT}" stroke-width="1"/>')
        c.text(x0 - 8, sy(v) + 4, str(v), size=11, anchor="end", fill=MUTED)
    for k in range(0, 19, 3):
        c.text(sx(k), y0 + h + 20, str(k), size=11.5, fill=MUTED)
    c.text(x0 + w / 2, y0 + h + 44, "ties added, in the order of the table", size=12.5, fill=MUTED)
    c.add(f'<polyline points="{" ".join(f"{sx(k):.1f},{sy(v):.1f}" for k, v in enumerate(counts))}" fill="none" stroke="{BLUE}" stroke-width="2.6"/>')
    c.add(f'<polyline points="{" ".join(f"{sx(k):.1f},{sy(v):.1f}" for k, v in enumerate(largest))}" fill="none" stroke="{ORANGE}" stroke-width="2.6" stroke-dasharray="7 4"/>')
    c.text(sx(3), sy(counts[3]) - 12, "number of groups", size=13, weight="700", fill=BLUE, anchor="start")
    c.text(sx(12), sy(largest[12]) - 12, "size of the biggest group", size=13, weight="700", fill=ORANGE, anchor="end")
    done = next(k for k, v in enumerate(counts) if v == 1)
    c.text(x0 + w, sy(1) + 28, f"everyone is in one group after tie {done}", size=12.5, anchor="end", fill=MUTED)
    meta = dict(chapter=9,
                caption=f"Union-find reads ties one at a time and always knows the current groups. Here the ten friends start as ten separate groups and are one group after tie {done}, though eighteen ties arrive in all.",
                alt=f"A line chart over eighteen ties. The solid blue line, number of groups, falls from 10 and reaches 1 after tie {done}. The dashed orange line, size of the biggest group, rises from 1 to 10 over the same ties.",
                data={"groups": counts, "largest": largest})
    return c, meta


def giant():
    rng = random.Random(7)
    n = 1000
    cs = [i / 10 for i in range(0, 41)]
    sim = []
    for cval in cs:
        fr = []
        for rep in range(5):
            uf = UF(n)
            m = int(round(cval * n / 2))
            for _ in range(m):
                a, b = rng.randrange(n), rng.randrange(n)
                if a != b:
                    uf.union(a, b)
            fr.append(max(uf.size[uf.find(i)] for i in range(n)) / n)
        sim.append(sum(fr) / len(fr))
    theory = []
    for cval in cs:
        S = 0.9 if cval > 1 else 0.0
        for _ in range(200):
            S = 1 - math.exp(-cval * S)
        theory.append(S)
    c = Canvas(860, 420, "A giant island appears out of nowhere",
               "Share of people in the biggest component against the average number of ties per person, for random networks of one thousand people.")
    x0, y0, w, h = 80, 30, 680, 290
    sx = lambda v: x0 + v / 4 * w
    sy = lambda v: y0 + h - v * h
    for v in (0, 0.25, 0.5, 0.75, 1):
        c.add(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0 + w}" y2="{sy(v):.1f}" stroke="{FAINT}" stroke-width="1"/>')
        c.text(x0 - 8, sy(v) + 4, f"{int(v * 100)}%", size=11, anchor="end", fill=MUTED)
    for v in range(0, 5):
        c.text(sx(v), y0 + h + 20, str(v), size=12, fill=MUTED)
    c.text(x0 + w / 2, y0 + h + 46, "average number of ties per person", size=12.5, fill=MUTED)
    c.add(f'<line x1="{sx(1):.1f}" y1="{y0}" x2="{sx(1):.1f}" y2="{y0 + h}" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    c.text(sx(1) + 6, y0 + 16, "1 tie per person", size=12, anchor="start", fill=MUTED)
    c.add(f'<polyline points="{" ".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in zip(cs, theory))}" fill="none" stroke="{BLUE}" stroke-width="2"/>')
    for a, b in zip(cs, sim):
        c.add(f'<circle cx="{sx(a):.1f}" cy="{sy(b):.1f}" r="3.8" fill="{ORANGE}" stroke="{PAPER}" stroke-width="0.8"/>')
    c.text(sx(2.6), sy(0.55), "orange dots: simulated", size=12.5, anchor="start", fill=ORANGE, weight="700")
    c.text(sx(2.6), sy(0.55) + 18, "blue line: standard formula", size=12.5, anchor="start", fill=BLUE, weight="700")
    meta = dict(chapter=9,
                caption="Below about one tie per person the biggest island holds a tiny share of the people. Just past one tie per person, a giant island swallows most of the network. The dots are simulations, found with union-find; the line is the standard large-network formula.",
                alt="A curve rising from near zero at an average of one tie per person to about 80 percent at two and 98 percent at four. Orange dots from simulated networks of a thousand people sit on a blue formula curve. A dashed vertical line marks one tie per person.",
                data={"c": cs, "simulated": [round(v, 4) for v in sim], "formula": [round(v, 4) for v in theory]})
    return c, meta


def one_way():
    n = len(DN)
    pos = [(x + 20, y + 20) for x, y in D_POS]
    c = Canvas(900, 330, "Weak and strong connection",
               "Nine people with one-way ties, drawn twice: left, whole network as one piece when direction is ignored; right, three strongly connected blocks and a single person.")
    pos_l = [(x * 0.68 + 10, y * 0.74) for x, y in pos]
    pos_r = [(x * 0.68 + 450, y * 0.74) for x, y in pos]
    comp_index, low, comps = tarjan(n, D_ARCS)
    draw_graph(c, pos_l, D_ARCS, [DN[i][:3] for i in range(n)], r=17, size=9.5, directed=True)
    c.text(230, 262, "Ignore the arrows: one piece (weakly connected)", size=13.5, weight="700")
    c.text(230, 284, "Follow the arrows: you can get from Ana to Gus, never back.", size=12.5, fill=MUTED)
    cmap = {}
    for k, comp in enumerate(comps):
        for v in comp:
            cmap[v] = SYS[k % len(SYS)]
    for k, comp in enumerate(comps):
        hull(c, [pos_r[i] for i in comp], SYS[k % len(SYS)], r=27)
    draw_graph(c, pos_r, D_ARCS, [DN[i][:3] for i in range(n)], r=17, size=9.5, directed=True,
               fills=[cmap[i] + "44" for i in range(n)], strokes=[cmap[i] for i in range(n)])
    c.text(680, 262, f"Follow the arrows both ways: {len(comps)} strongly connected blocks", size=13.5, weight="700")
    c.text(680, 284, "Inside a block everyone can reach everyone.", size=12.5, fill=MUTED)
    meta = dict(chapter=9,
                caption=f"One-way ties. Ignoring direction, these nine people form one weakly connected piece. Following the arrows, they split into {len(comps)} strongly connected blocks, where everyone in a block can reach everyone else in it.",
                alt="Two copies of a nine-person network with arrows. On the left they form one connected picture. On the right they are grouped into four boxes: Ana, Ben and Cleo; Dev, Eli and Fay; Gus and Hana; and Ivo alone. Arrows between boxes only point one way, from left to right.",
                data={"blocks": [[DN[v] for v in comp] for comp in comps]})
    return c, meta


def tarjan_trace():
    n = len(DN)
    index, low, comps = tarjan(n, D_ARCS)
    # a step list from re-running the routine with a trace
    adj = [[] for _ in range(n)]
    for a, b in D_ARCS:
        adj[a].append(b)
    for r in adj:
        r.sort()
    idx, lw, on, st, ctr, steps, out = [None] * n, [0] * n, [False] * n, [], [0], [], []

    def go(v):
        idx[v] = lw[v] = ctr[0]
        ctr[0] += 1
        st.append(v)
        on[v] = True
        steps.append((f"visit {DN[v]}", [DN[x][:3] for x in st], list(out)))
        for w in adj[v]:
            if idx[w] is None:
                go(w)
                lw[v] = min(lw[v], lw[w])
            elif on[w]:
                lw[v] = min(lw[v], idx[w])
        if lw[v] == idx[v]:
            comp = []
            while True:
                w = st.pop()
                on[w] = False
                comp.append(w)
                if w == v:
                    break
            out.append(sorted(comp))
            steps.append((f"{DN[v]} is a leader: pop block", [DN[x][:3] for x in st], list(out)))
    for v in range(n):
        if idx[v] is None:
            go(v)
    assert lw == low and idx == index
    c = Canvas(960, 560, "Tarjan's method: two numbers per person",
               "The nine-person network with each person's visit number and low number, the blocks found, and a table of the stack at each step.")
    pos = [(x * 0.78 + 20, y * 0.78 + 30) for x, y in D_POS]
    cmap = {}
    for k, comp in enumerate(comps):
        for v in comp:
            cmap[v] = SYS[k % len(SYS)]
    draw_graph(c, pos, D_ARCS, [f"{index[i]}/{low[i]}" for i in range(n)], r=21, size=11, directed=True,
               fills=[cmap[i] + "55" for i in range(n)], strokes=[cmap[i] for i in range(n)])
    for i in range(n):
        c.text(pos[i][0], pos[i][1] - 27, DN[i], size=10.5, fill=MUTED)
    c.text(230, 270, "Dots show  visit number / low number", size=13, weight="700")
    c.text(230, 290, "Same low number as visit number: the person is a block's leader.", size=12, fill=MUTED)
    c.text(230, 308, "Colors are the blocks that come out.", size=12, fill=MUTED)
    # table of steps
    x0, y0 = 20, 340
    c.text(x0, y0, "Step", size=12, weight="700", anchor="start", fill=MUTED)
    c.text(x0 + 40, y0, "What happens", size=12, weight="700", anchor="start", fill=MUTED)
    c.text(x0 + 300, y0, "People waiting on the stack (oldest first)", size=12, weight="700", anchor="start", fill=MUTED)
    shown = steps[:]
    rows = shown[:14]
    for i, (what, stack, done) in enumerate(rows):
        y = y0 + 20 + i * 14.5
        c.text(x0, y, str(i + 1), size=10.5, anchor="start")
        c.text(x0 + 40, y, what, size=10.5, anchor="start")
        c.text(x0 + 300, y, " ".join(stack) if stack else "(empty)", size=10.5, anchor="start", mono=True)
    c.text(x0 + 600, y0 + 20, f"All {len(steps)} steps shown." if len(steps) <= len(rows) else f"{len(steps)} steps in all; the first {len(rows)} shown.", size=11.5, anchor="start", fill=MUTED)
    c.text(x0 + 600, y0 + 40, "Blocks found, in order:", size=12, anchor="start", weight="700")
    for k, comp in enumerate(comps):
        c.text(x0 + 600, y0 + 62 + k * 18, f"{k + 1}. " + ", ".join(DN[v] for v in comp), size=12, anchor="start", fill=SYS[k % len(SYS)])
    meta = dict(chapter=9,
                caption="Tarjan's method on the nine-person network. Each person gets a visit number and a low number (the lowest visit number they can get back to). A person whose low equals their visit number is the leader of a block, and the block is everyone above them on the stack.",
                alt=f"The nine-person directed network with each dot labeled with two numbers. Below, a table of the first steps of the search with the stack contents, and a list of the {len(comps)} blocks in the order the method finds them: {'; '.join(', '.join(DN[v] for v in comp) for comp in comps)}.",
                data={"index": index, "low": low, "blocks": [[DN[v] for v in comp] for comp in comps]})
    return c, meta


def kosaraju_passes():
    n = len(DN)
    finish, comp = kosaraju(n, D_ARCS)
    order = list(reversed(finish))
    c = Canvas(960, 400, "Kosaraju's method: forward, then backward",
               "Two copies of the nine-person network. Left: the original arrows with the order in which people finish. Right: all arrows reversed, searching in the reverse of that order.")
    pos_l = [(x * 0.7 + 10, y * 0.7 + 60) for x, y in D_POS]
    pos_r = [(x * 0.7 + 490, y * 0.7 + 60) for x, y in D_POS]
    rank = {v: k + 1 for k, v in enumerate(finish)}
    draw_graph(c, pos_l, D_ARCS, [str(rank[i]) for i in range(n)], r=17, size=12, directed=True)
    for i in range(n):
        c.text(pos_l[i][0], pos_l[i][1] - 24, DN[i][:3], size=9.5, fill=MUTED)
    c.text(230, 30, "Pass 1: finishing order on the original arrows", size=14, weight="700")
    c.text(230, 330, "A dot's number is when its search finished.", size=12.5, fill=MUTED)
    c.text(230, 350, "Late finishers sit upstream.", size=12.5, fill=MUTED)
    rev = [(b, a) for a, b in D_ARCS]
    cm = {}
    for i in range(n):
        cm[i] = SYS[comp[i] % len(SYS)]
    draw_graph(c, pos_r, rev, [str(order.index(i) + 1) for i in range(n)], r=17, size=12, directed=True,
               fills=[cm[i] + "55" for i in range(n)], strokes=[cm[i] for i in range(n)])
    for i in range(n):
        c.text(pos_r[i][0], pos_r[i][1] - 24, DN[i][:3], size=9.5, fill=MUTED)
    c.text(710, 30, "Pass 2: reverse every arrow, search in reverse finishing order", size=14, weight="700")
    c.text(710, 330, "A dot's number is its place in the order. Each search stays", size=12.5, fill=MUTED)
    c.text(710, 350, "inside one block, shown by color.", size=12.5, fill=MUTED)
    blocks = {}
    for i in range(n):
        blocks.setdefault(comp[i], []).append(DN[i])
    meta = dict(chapter=9,
                caption="Kosaraju's method. Pass 1 searches the network and notes the order in which each person finishes. Pass 2 reverses every arrow and starts searches in the opposite of that order. Each search in pass 2 collects exactly one strongly connected block.",
                alt=f"Two copies of the nine-person network. On the left, each person is labeled with the order in which their search finished. On the right, every arrow is reversed, each person is labeled with their place in the reverse order, and they are colored by block: {'; '.join(', '.join(v) for v in blocks.values())}.",
                data={"finish_order": [DN[v] for v in finish], "blocks": list(blocks.values())})
    return c, meta


def condensation():
    n = len(DN)
    index, low, comps = tarjan(n, D_ARCS)
    cid = {}
    for k, comp in enumerate(comps):
        for v in comp:
            cid[v] = k
    arcs = sorted({(cid[a], cid[b]) for a, b in D_ARCS if cid[a] != cid[b]})
    c = Canvas(920, 330, "Collapse each block to one dot",
               "Left: the nine-person network with its four blocks outlined. Right: one dot per block and the arrows between them, which form a map with no loops.")
    pos = [(x * 0.62 + 10, y * 0.62 + 30) for x, y in D_POS]
    for k, comp in enumerate(comps):
        hull(c, [pos[i] for i in comp], SYS[k % len(SYS)], r=24)
    draw_graph(c, pos, D_ARCS, [DN[i][:3] for i in range(n)], r=15, size=9, directed=True,
               fills=[SYS[cid[i] % len(SYS)] + "44" for i in range(n)], strokes=[SYS[cid[i] % len(SYS)] for i in range(n)])
    c.text(180, 312, "The network, with its blocks", size=13.5, weight="700")
    # condensed: topological layout (sources left)
    order = list(reversed(range(len(comps))))  # Tarjan emits sinks first
    level = {}
    for k in order:
        preds = [a for a, b in arcs if b == k]
        level[k] = 1 + max([level[p] for p in preds], default=-1) if preds else 0
    byl = {}
    for k in order:
        byl.setdefault(level[k], []).append(k)
    cp = {}
    for lv, ks in byl.items():
        for j, k in enumerate(ks):
            skipped = any(level[a] < lv < level[b] for a, b in arcs)
            cp[k] = (500 + lv * 112, 140 + (j - (len(ks) - 1) / 2) * 90 + (85 if skipped else 0))
    for a, b in arcs:
        c.edge(cp[a], cp[b], ra=30, rb=30, directed=True, color=INK, width=2.4)
    for k, comp in enumerate(comps):
        c.node(cp[k][0], cp[k][1], f"{len(comp)}", r=30, fill=SYS[k % len(SYS)] + "55", stroke=SYS[k % len(SYS)], size=18)
        c.text(cp[k][0], cp[k][1] + 46, ", ".join(DN[v][:3] for v in comp), size=10.5, fill=MUTED)
    c.text(700, 312, "The map of blocks (number = people inside)", size=13.5, weight="700")
    meta = dict(chapter=9,
                caption="Condensation. Replace each strongly connected block by a single dot and keep the arrows between blocks. What is left never loops back on itself, so it can be read as a map that flows one way.",
                alt=f"On the left, the nine-person network with four boxes around the blocks. On the right, four dots sized by block, with arrows between them: the block of Ana, Ben and Cleo leads to the block of Dev, Eli and Fay, which leads both to Ivo and to the block of Gus and Hana, and Ivo leads to Gus and Hana. There are no arrows back.",
                data={"blocks": [[DN[v] for v in comp] for comp in comps], "arrows_between_blocks": [list(a) for a in arcs]})
    return c, meta


FIGURES = {
    "islands": islands, "sweep-labels": sweep_labels, "uf-forest": uf_forest, "uf-compress": uf_compress,
    "ties-arrive": ties_arrive, "giant-component": giant, "one-way": one_way, "tarjan-trace": tarjan_trace,
    "kosaraju-passes": kosaraju_passes, "condensation": condensation,
}

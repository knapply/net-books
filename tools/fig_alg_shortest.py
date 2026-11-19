"""Figures for chapter 6 of the algorithms book (shortest paths). Standard library only.

Numbers are computed here by the reference routines in tools/algkit.py. Where the engine's answer for the same network
is committed (books/algorithms/data/anim/*.frames.json) the module asserts that it agrees.
"""
import heapq
import json
import math
import random
from collections import deque
from pathlib import Path

import algkit as K
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, PURPLE, RED, SKY, Canvas

CH = 6
GRAY, PALE = K.GRAY, K.PALE
DATA = Path(__file__).resolve().parent.parent / "books" / "algorithms" / "data" / "anim"


def _engine(name):
    p = DATA / f"{name}.frames.json"
    return json.loads(p.read_text()) if p.exists() else None


def _weighted():
    return K.weighted_adjacency(10, K.EDGES, K.MINUTES)


def _route(parent, v):
    out = [v]
    while parent[out[-1]] is not None:
        out.append(parent[out[-1]])
    return out[::-1]


# ------------------------------------------------------------------ 1. fewest steps is not cheapest
def hops_vs_minutes():
    steps, best, parent = K.dijkstra_trace(_weighted(), 0)
    eli = 4
    cheap = _route(parent, eli)
    hop_route = [0, 1, 4]
    pos = K.kite_pos(70, 60, 760, 320)
    cheap_set = {frozenset(e) for e in zip(cheap, cheap[1:])}
    hop_set = {frozenset(e) for e in zip(hop_route, hop_route[1:])}
    hop_cost = sum(w for (a, b), w in zip(K.EDGES, K.MINUTES) if frozenset((a, b)) in hop_set)
    cheap_cost = sum(w for (a, b), w in zip(K.EDGES, K.MINUTES) if frozenset((a, b)) in cheap_set)
    assert (hop_cost, cheap_cost) == (12, 9) and best[eli] == 9
    c = Canvas(900, 470, "Fewest steps is not the cheapest route", "The ten-person network with the minutes each tie takes, and two routes from Ana to Eli.")

    def estyle(k):
        e = frozenset(K.EDGES[k])
        if e in cheap_set:
            return {"color": BLUE, "width": 5}
        if e in hop_set:
            return {"color": ORANGE, "width": 5, "dash": "9 6"}
        return {"color": GRAY, "width": 1.5}
    K.draw_graph(c, pos, K.EDGES, node=lambda i: {"fill": PAPER if i not in (0, eli) else INK, "stroke": INK if i in (0, eli) else BLUE,
                                                    "label": K.NAMES[i][0], "label_fill": PAPER if i in (0, eli) else INK},
                 edge=estyle, r=19, size=13)
    for k, (a, b) in enumerate(K.EDGES):
        K.weight_tag(c, pos, a, b, K.MINUTES[k])
    for i, p in enumerate(pos):
        c.text(p[0], p[1] + 34, K.NAMES[i], size=11, fill=MUTED)
    c.rect(60, 414, 18, 8, fill=ORANGE, stroke=ORANGE)
    c.text(88, 423, f"Ana, Ben, Eli: 2 steps, {hop_cost} minutes", size=13, anchor="start")
    c.rect(400, 414, 18, 8, fill=BLUE, stroke=BLUE)
    c.text(428, 423, f"Ana, Cleo, Dev, Eli: 3 steps, {cheap_cost} minutes", size=13, anchor="start")
    c.text(450, 458, "The number on each tie is the minutes it takes to get from one person to the other.", size=12.5, fill=MUTED)
    meta = dict(chapter=CH,
                caption="Two routes from Ana to Eli. The dashed orange route has the fewest steps (2) but takes 12 minutes. The solid blue route has more steps (3) and takes only 9. When ties cost different amounts, counting steps is the wrong question.",
                alt="The ten-person network with the minutes written on each tie. A dashed orange route runs Ana, Ben, Eli and is labeled 2 steps, 12 minutes. A solid blue route runs Ana, Cleo, Dev, Eli and is labeled 3 steps, 9 minutes.",
                data={"fewest_steps": [K.NAMES[v] for v in hop_route], "cheapest": [K.NAMES[v] for v in cheap], "minutes": [hop_cost, cheap_cost]})
    return c, meta


# ------------------------------------------------------------------ 2. Dijkstra by hand, as a table
def dijkstra_table():
    steps, best, parent = K.dijkstra_trace(_weighted(), 0)
    eng = _engine("dijkstra-queue")
    if eng:
        assert [int(x) for x in eng["dijkstra"]["dist"]] == best, "engine Dijkstra distances differ from the trace"
        assert eng["dijkstra"]["order"] == [s["settle"] for s in steps], "engine settling order differs from the trace"
    rows = []
    for i, s in enumerate(steps):
        ch = ", ".join(f"{K.NAMES[v]} {'?' if old == math.inf else old} to {new}" for v, old, new in s["changes"]) or "nothing changes"
        wait = ", ".join(f"{K.NAMES[v]} {d}" for d, v in s["waiting"]) or "(empty)"
        rows.append([str(i + 1), f"{K.NAMES[s['settle']]} at {s['dist']}", ch, wait])
    c = Canvas(960, 400, "Dijkstra's algorithm by hand, from Ana", "A table with one row per person settled: who, their minutes from Ana, what changed, and who is still waiting.")
    end = K.table(c, 20, 40, ["Turn", "Settled", "Guesses that improved", "Still waiting (best guess so far)"], rows, [55, 120, 330, 435], row_h=30, size=12.5)
    c.text(480, 26, "A '?' means no guess yet (no route found so far)", size=13, fill=MUTED)
    c.text(480, end + 24, "Each person's final minutes are the numbers in the Settled column.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="Dijkstra's algorithm on the travel-time network, one person at a time. Each turn settles the waiting person with the smallest guess, then lets that person improve their neighbours' guesses. Look at Dev: first guessed at 9 from Ana directly, then improved to 7 once Cleo was settled.",
                alt="A table of ten turns. Turn 1 settles Ana at 0 and sets guesses for Ben 6, Cleo 2, Dev 9 and Fay 8. Turn 2 settles Cleo at 2 and improves Dev from 9 to 7. Turn 3 settles Ben at 6. Turn 4 settles Dev at 7 and improves Eli to 9. Later turns settle Fay at 8, Eli at 9, Gus at 12, Hana at 13, Ivo at 17 and Jo at 20.",
                data={"rows": rows, "distances": dict(zip(K.NAMES, best))})
    return c, meta


# ------------------------------------------------------------------ 3. why it works: the fence
def fence():
    c = Canvas(900, 420, "Why Dijkstra's algorithm works", "Three nested regions: settled people, the waiting frontier and the rest of the network.")
    cx, cy = 300, 215
    c.add(f'<circle cx="{cx}" cy="{cy}" r="185" fill="{FAINT}55" stroke="{GRAY}" stroke-width="1.5" stroke-dasharray="6 5"/>')
    c.add(f'<circle cx="{cx}" cy="{cy}" r="130" fill="{SKY}33" stroke="{BLUE}" stroke-width="2.4"/>')
    c.add(f'<circle cx="{cx}" cy="{cy}" r="82" fill="{BLUE}33" stroke="{BLUE}" stroke-width="2"/>')
    rng = random.Random(8)
    for r_in, r_out, n, col, lab in ((0, 72, 6, BLUE, True), (92, 122, 8, ORANGE, False), (142, 176, 7, GRAY, False)):
        for k in range(n):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(r_in, r_out) if r_in else rng.uniform(10, r_out)
            c.node(cx + rr * math.cos(a), cy + rr * math.sin(a), "", r=9, fill=PAPER if col == GRAY else col + "99", stroke=col, sw=2)
    c.node(cx, cy, "0", r=14, fill=ORANGE, stroke=INK, size=12)
    c.text(cx, 36, "the whole network", size=13, fill=MUTED)
    lx = 540
    items = [(BLUE, "Settled", "Their minutes are final. Every one of them is closer to the start than anyone outside the blue ring."),
             (ORANGE, "Waiting", "They have a best guess so far, from some settled neighbour. The smallest guess is next to be settled."),
             (GRAY, "Not met yet", "No route found so far. Any route to them must cross the waiting ring first.")]
    y = 90
    for col, head, body in items:
        c.node(lx, y, "", r=10, fill=PAPER if col == GRAY else col + "99", stroke=col, sw=2)
        c.text(lx + 22, y + 5, head, size=16, weight="700", anchor="start")
        words, line, lines = body.split(), "", []
        for w in words:
            if len(line) + len(w) > 46:
                lines.append(line)
                line = w
            else:
                line = (line + " " + w).strip()
        lines.append(line)
        c.lines(lx + 22, y + 28, lines, size=13, fill=MUTED)
        y += 112
    meta = dict(chapter=CH,
                caption="The reason Dijkstra's algorithm is correct. The waiting person with the smallest guess cannot be beaten by any other route, because any other route leaves the settled region through a waiting person whose guess is at least as large, and costs are never negative.",
                alt="Three nested circles. The innermost, in blue, holds settled people around a start marked 0. A middle ring in orange holds the waiting people. The outer dashed circle holds people not yet met. A legend on the right explains the three groups.",
                data={})
    return c, meta


# ------------------------------------------------------------------ 4. negative weights
NEG = [(0, 1, 2), (0, 2, 5), (2, 1, -4), (1, 3, 3), (2, 3, 6), (3, 4, 1)]  # s, a, b, c, d
NEG_NAMES = ["s", "a", "b", "c", "d"]
CYC = [(0, 1, 2), (1, 3, 3), (3, 2, 2), (2, 1, -6), (3, 4, 1)]


def negative():
    greedy = K.dijkstra_greedy_directed(5, NEG, 0)
    hist, improved = K.bellman_ford_rounds(5, NEG, 0)
    true = hist[-1]
    eng = _engine("dijkstra-queue")
    if eng:
        assert [float(x) for x in eng["negative"]["bellman_ford"]["dist"]] == [float(x) for x in true], "engine Bellman-Ford differs"
        assert "negative" in eng["negative"]["dijkstra_error"].lower() or eng["negative"]["dijkstra_error"] != "none"
    pos = [(110, 200), (330, 100), (330, 300), (560, 200), (780, 200)]
    c = Canvas(900, 430, "A negative tie breaks the settling rule", "A five-person directed network with one negative tie, and the distances two rules give for it.")
    for a, b, w in NEG:
        col = RED if w < 0 else GRAY
        c.edge(pos[a], pos[b], ra=22, rb=22, directed=True, color=col, width=3 if w < 0 else 2)
        mx, my = (pos[a][0] + pos[b][0]) / 2, (pos[a][1] + pos[b][1]) / 2
        c.add(f'<rect x="{mx - 16:.1f}" y="{my - 11:.1f}" width="32" height="22" rx="11" fill="{PAPER}" stroke="{col}" stroke-width="1.4"/>')
        c.text(mx, my + 5, str(w), size=13, weight="700", fill=RED if w < 0 else INK)
    for i, p in enumerate(pos):
        c.node(p[0], p[1], NEG_NAMES[i], r=22, fill=ORANGE + "88" if i == 0 else PALE, stroke=INK if i == 0 else BLUE, size=15)
    c.text(450, 34, "Distances from s", size=16, weight="700")
    c.text(300, 372, "Settling rule (Dijkstra): " + ", ".join(f"{NEG_NAMES[i]} {greedy[i]}" for i in range(5)), size=14, fill=ORANGE, weight="700", anchor="middle")
    c.text(300, 400, "Correct answer (Bellman-Ford): " + ", ".join(f"{NEG_NAMES[i]} {true[i]}" for i in range(5)), size=14, fill=BLUE, weight="700", anchor="middle")
    c.text(740, 372, f"a is settled at {greedy[1]}, but", size=13, fill=MUTED, anchor="middle")
    c.text(740, 392, f"s, b, a costs {5 - 4}.", size=13, fill=MUTED, anchor="middle")
    meta = dict(chapter=CH,
                caption="One negative tie is enough to break the rule 'a settled person's distance is final'. The rule settles a at 2, but the route s, b, a costs 5 + (-4) = 1. Bellman-Ford, which never treats a distance as final, gets it right.",
                alt=f"A directed network of five people s, a, b, c, d. Ties: s to a costs 2, s to b costs 5, b to a costs -4 (drawn in red), a to c costs 3, b to c costs 6 and c to d costs 1. Below it, the settling rule gives distances {greedy} and the correct answer is {[int(x) for x in true]}.",
                data={"settling_rule": greedy, "correct": [int(x) for x in true]})
    return c, meta


# ------------------------------------------------------------------ 5. Bellman-Ford rounds and a negative cycle
def rounds():
    hist, _ = K.bellman_ford_rounds(5, NEG, 0)
    chist, improved = K.bellman_ford_rounds(5, CYC, 0)
    assert improved, "the cycle network must keep improving"
    eng = _engine("dijkstra-queue")
    if eng:
        assert eng["cycle"]["found"], "the engine did not report the negative cycle"
    fmt = lambda v: "-" if v == math.inf else str(int(v))
    c = Canvas(900, 420, "Bellman-Ford in rounds", "Two tables of distances after each round of trying every tie once: one that settles and one with a negative cycle that never does.")
    c.text(225, 28, "Without a negative cycle: it settles", size=15, weight="700")
    rows = [[str(r)] + [fmt(x) for x in h] for r, h in enumerate(hist)]
    K.table(c, 20, 44, ["Round"] + NEG_NAMES, rows, [70] + [64] * 5, row_h=30, size=13)
    c.text(675, 28, "With a negative cycle: it never settles", size=15, weight="700")
    crow = [[str(r)] + [fmt(x) for x in h] for r, h in enumerate(chist[:7])]
    K.table(c, 470, 44, ["Round"] + NEG_NAMES, crow, [70] + [64] * 5, row_h=30, size=13, hl={5, 6})
    c.text(225, 44 + 30 * (len(rows) + 1) + 30, "No change in the last round: done.", size=13, fill=MUTED)
    c.text(675, 44 + 30 * (len(crow) + 1) + 26, "b keeps getting cheaper (a to c to b to a is a loop worth -1).", size=13, fill=RED)
    c.text(450, 385, "'-' means no route found yet. With n people, a network with no negative loop settles within n - 1 rounds.", size=12.5, fill=MUTED)
    c.text(450, 405, "If round n still improves something, there is a negative loop.", size=12.5, fill=MUTED)
    meta = dict(chapter=CH,
                caption="Bellman-Ford tries every tie once per round. On the left network it stops improving after a few rounds. On the right, a loop whose ties add up to less than zero keeps shaving the distances forever, which is how the algorithm notices the trap.",
                alt="Two tables of distances for five people s, a, b, c, d, one row per round. The left table fills in over three rounds and then stops changing. In the right table, the numbers for a, b and c keep decreasing in every round shown, with the later rows shaded.",
                data={"settles": [[None if x == math.inf else x for x in h] for h in hist], "cycle": [[None if x == math.inf else x for x in h] for h in chist[:7]]})
    return c, meta


# ------------------------------------------------------------------ 6. A* explores less
def astar_explored():
    w, h = 13, 7
    wall = lambda r, c, r2, c2: c == 6 and c2 == 7 and 2 <= r <= 4
    edges = K.grid_edges(w, h, wall)
    adj = K.adjacency(w * h, edges)
    s, t = 3 * w + 1, 3 * w + w - 2
    tr, tc = divmod(t, w)
    man = lambda v: abs(v // w - tr) + abs(v % w - tc)

    def search(use_h):
        g = {s: 0}
        heap = [(man(s) if use_h else 0, s)]
        done, parent = [], {s: None}
        closed = set()
        while heap:
            f, u = heapq.heappop(heap)
            if u in closed:
                continue
            closed.add(u)
            done.append(u)
            if u == t:
                break
            for v in adj[u]:
                ng = g[u] + 1
                if ng < g.get(v, math.inf):
                    g[v] = ng
                    parent[v] = u
                    heapq.heappush(heap, (ng + (man(v) if use_h else 0), v))
        path = []
        x = t
        while x is not None:
            path.append(x)
            x = parent[x]
        return done, path[::-1], g[t]
    dd, dp, dl = search(False)
    ad, ap, al = search(True)
    eng = _engine("bidirectional-meet")
    if eng:
        assert float(eng["wall"]["astar_length"]) == al == dl, "engine A* length differs from the reference"
    assert al == dl
    c = Canvas(900, 380, "A* looks at fewer places than Dijkstra", "Two grids of streets with a wall; the places each search looked at are shaded and the route is drawn.")
    cell = 38
    for p, (title, done, path) in enumerate((("Dijkstra: looks in every direction", dd, dp), ("A*: leans toward the goal", ad, ap))):
        x0, y0 = 40 + p * 450, 66
        c.text(x0 + w * cell / 2 - cell / 2 + 4, 36, f"{title} ({len(done)} places)", size=14.5, weight="700")
        seen = set(done)
        for v in range(w * h):
            r, cc = divmod(v, w)
            fill = SKY + "88" if v in seen else "#f3f4f6"
            c.rect(x0 + cc * cell - cell / 2 + 4, y0 + r * cell - cell / 2 + 4, cell - 4, cell - 4, fill=fill, stroke=PAPER, sw=1, rx=4)
        for r in range(2, 5):
            xx = x0 + 6 * cell + cell / 2 + 2
            c.add(f'<line x1="{xx}" y1="{y0 + r * cell - cell / 2 + 4}" x2="{xx}" y2="{y0 + r * cell + cell / 2}" stroke="{INK}" stroke-width="5"/>')
        pts = " ".join(f"{x0 + (v % w) * cell + 2},{y0 + (v // w) * cell + 4}" for v in path)
        c.add(f'<polyline points="{pts}" fill="none" stroke="{ORANGE}" stroke-width="4.5" stroke-linejoin="round"/>')
        for v, lab in ((s, "S"), (t, "T")):
            c.node(x0 + (v % w) * cell + 2, y0 + (v // w) * cell + 4, lab, r=13, fill=INK, stroke=INK, label_fill=PAPER, size=12)
    c.text(450, 340, f"Both find a route of {al} steps around the end of the black wall.", size=13, fill=MUTED)
    c.text(450, 362, "A* ranks places by steps so far plus a guess of the blocks still to go (straight across to T).", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption=f"Dijkstra and A* on a grid of streets with a wall. Both return a route of {al} steps. Dijkstra settled {len(dd)} places, A* only {len(ad)}, because it ranks places by distance so far plus a guess of the distance still to go.",
                alt=f"Two grids of thirteen columns by seven rows with a short vertical black wall in the middle, covering the third to fifth rows. A start S sits in the middle row near the left edge and a target T in the middle row near the right edge. On the left, {len(dd)} squares are shaded, almost the whole grid. On the right, {len(ad)} squares are shaded, a narrower band between S and T. An orange route runs from S, bends around the end of the wall and reaches T, in both.",
                data={"dijkstra_places": len(dd), "astar_places": len(ad), "route_length": al})
    return c, meta


# ------------------------------------------------------------------ 7. why search from both ends
def ball_sizes():
    rng = random.Random(11)
    n, deg = 20000, 6
    es = set()
    while len(es) < n * deg // 2:
        a, b = rng.randrange(n), rng.randrange(n)
        if a != b:
            es.add((min(a, b), max(a, b)))
    adj = [[] for _ in range(n)]
    for a, b in es:
        adj[a].append(b)
        adj[b].append(a)

    def one_sided(s, t):
        seen = {s}
        q = deque([s])
        while q:
            u = q.popleft()
            if u == t:
                return len(seen)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        return len(seen)

    def two_sided(s, t):
        a, b = {s: 0}, {t: 0}
        fa, fb = [s], [t]
        while fa and fb:
            grow_a = len(fa) <= len(fb)
            front, mine, other = (fa, a, b) if grow_a else (fb, b, a)
            nxt = []
            hit = False
            for u in front:
                for v in adj[u]:
                    if v in other:
                        hit = True
                    if v not in mine:
                        mine[v] = mine[u] + 1
                        nxt.append(v)
            if grow_a:
                fa = nxt
            else:
                fb = nxt
            if hit:
                return len(a) + len(b)
        return len(a) + len(b)
    pairs, res = [], []
    while len(res) < 10:
        s, t = rng.randrange(n), rng.randrange(n)
        if s != t:
            res.append((one_sided(s, t), two_sided(s, t)))
    res.sort()
    c = Canvas(900, 430, "Searching from both ends", "Ten pairs of people in a random network of 20,000: how many people a one-sided and a two-sided search had to look at.")
    x0, y0, w, h = 110, 50, 740, 280
    Y = lambda v: y0 + h - (math.log10(v) / math.log10(20000)) * h
    c.add(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{INK}" stroke-width="1.5"/><line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{INK}" stroke-width="1.5"/>')
    for v in (1, 10, 100, 1000, 10000):
        c.add(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x0 + w}" y2="{Y(v):.1f}" stroke="{FAINT}" stroke-width="0.8"/>')
        c.text(x0 - 10, Y(v) + 4, f"{v:,}", size=11.5, anchor="end")
    c.text(x0, y0 - 14, "people looked at (log scale)", size=13, fill=MUTED, anchor="start")
    bw = w / len(res)
    for k, (o, t) in enumerate(res):
        bx = x0 + k * bw + bw * 0.12
        c.rect(bx, Y(o), bw * 0.36, y0 + h - Y(o), fill=RED + "66", stroke=RED, sw=1.2)
        c.rect(bx + bw * 0.38, Y(t), bw * 0.36, y0 + h - Y(t), fill=BLUE + "66", stroke=BLUE, sw=1.2)
        c.text(bx + bw * 0.18, Y(o) - 5, f"{o:,}", size=10, fill=RED)
        c.text(bx + bw * 0.56, Y(t) - 5, f"{t:,}", size=10, fill=BLUE)
        c.text(bx + bw * 0.37, y0 + h + 18, f"pair {k + 1}", size=11)
    c.rect(x0 + 420, 22, 16, 12, fill=RED + "66", stroke=RED)
    c.text(x0 + 442, 33, "from one end", size=12.5, anchor="start")
    c.rect(x0 + 560, 22, 16, 12, fill=BLUE + "66", stroke=BLUE)
    c.text(x0 + 582, 33, "from both ends", size=12.5, anchor="start")
    med = lambda xs: sorted(xs)[len(xs) // 2]
    mo, mt = med([o for o, _ in res]), med([t for _, t in res])
    c.text(450, 380, f"Middle pair: {mo:,} people from one end, {mt:,} from both ends, about {mo / mt:.0f} times fewer.", size=14, weight="600")
    c.text(450, 404, "Random network of 20,000 people with about 6 friends each, ties all of equal length, pairs drawn at random.", size=12.5, fill=MUTED)
    meta = dict(chapter=CH,
                caption="In a network where the number of people reached keeps multiplying, two small searches that meet in the middle touch far fewer people than one big search that goes the whole way. The pairs are sorted by the one-sided cost.",
                alt=f"A bar chart on a log scale with ten pairs of bars. Each pair has a red bar for a one-sided search and a blue bar, much shorter, for a two-sided search. The one-sided bars run from about {res[0][0]:,} to {res[-1][0]:,} people; the two-sided bars run from about {min(t for _, t in res):,} to {max(t for _, t in res):,}.",
                data={"pairs": res, "n": n, "mean_degree": deg})
    return c, meta


# ------------------------------------------------------------------ 8. which to use
def which_wins():
    c = Canvas(960, 420, "Which shortest-path method when", "A table comparing Dijkstra, Bellman-Ford, A star and bidirectional search.")
    rows = [["Breadth-first", "all ties equal", "no", "distances from one start", "the plain case"],
            ["Dijkstra", "costs zero or more", "no", "distances from one start", "different costs, no negatives"],
            ["Bellman-Ford", "any costs", "yes", "distances from one start", "negative costs, or checking for traps"],
            ["A*", "costs plus a guess", "no", "one route, start to goal", "you can guess distance to go"],
            ["Bidirectional", "costs zero or more", "no", "one route, start to goal", "you know both ends, network is big"]]
    K.table(c, 20, 40, ["Method", "Ties may cost", "Negative ok?", "Answers", "Wins when"], rows, [150, 190, 120, 230, 250], row_h=44, size=13.5)
    c.text(480, 32, "Pick by what the ties cost and what you need to know", size=14.5, weight="700")
    c.text(480, 330, "Rule of thumb: start with breadth-first (equal ties) or Dijkstra (costs). Reach for the others only for the reason in the last column.", size=13, fill=MUTED)
    c.text(480, 356, "Dijkstra's cost is about (n + m) times a small logarithm; Bellman-Ford's is about n times m in the worst case.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="A decision table for shortest paths. The first two columns are the questions to ask of your network; the last is the reason to pick anything fancier than Dijkstra.",
                alt="A table with five rows: breadth-first, Dijkstra, Bellman-Ford, A star and bidirectional. Columns give what the ties may cost, whether negative costs are allowed (only Bellman-Ford), what each answers (distances from one start, or one route from start to goal), and when it wins.",
                data={"rows": rows})
    return c, meta


FIGURES = {
    "alg-sp-hops-vs-minutes": hops_vs_minutes,
    "alg-sp-dijkstra-table": dijkstra_table,
    "alg-sp-fence": fence,
    "alg-sp-negative": negative,
    "alg-sp-rounds": rounds,
    "alg-sp-astar-explored": astar_explored,
    "alg-sp-ball-sizes": ball_sizes,
    "alg-sp-which-wins": which_wins,
}

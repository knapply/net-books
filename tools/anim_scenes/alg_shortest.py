"""Chapter 6 of the algorithms book: Dijkstra's algorithm with its waiting list, and a search from both ends.

Dijkstra: the ten-person network with minutes on each tie, from Ana. A small dot on every tie carries its minutes (the player
draws numbers only inside dots). The trace is the textbook rule (tools/algkit.py); the scene asserts that the engine's
distances, parents and settling order (data/anim/dijkstra-queue.frames.json) are exactly what it ends with, and that
Bellman-Ford gives the same distances.

Both ends: a nine by five grid of streets, one frame per level of a search from each end. The scene asserts that the engine's
bidirectional route has the length found by the reference, that it is a real route on the grid, and that the engine's
one-sided search settled as many places as the reference.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import algkit as K  # noqa: E402

BOOK = "algorithms"
NAMES = K.NAMES


def _roles(M):
    from figs import GREEN
    M.NODE.setdefault("c", (GREEN, "#00694c"))


def dijkstra_queue():
    import make_anim as M
    raw = M.load("dijkstra-queue", BOOK)
    assert raw["names"] == NAMES and raw["edges"] == [list(e) for e in K.EDGES] and [int(x) for x in raw["minutes"]] == K.MINUTES
    steps, best, parent = K.dijkstra_trace(K.weighted_adjacency(10, K.EDGES, K.MINUTES), 0)
    eng = raw["dijkstra"]
    assert [int(x) for x in eng["dist"]] == best, "engine distances differ from the trace"
    assert [None if p < 0 else p for p in eng["parent"]] == parent, "engine parents differ from the trace"
    assert eng["order"] == [s["settle"] for s in steps], "engine settling order differs from the trace"
    assert [int(x) for x in raw["bellman_ford"]["dist"]] == best, "Bellman-Ford disagrees with Dijkstra"
    n, m = 10, len(K.EDGES)
    people = M.layout(NAMES, [list(e) for e in K.EDGES])
    frac = {(1, 6): 0.28, (3, 4): 0.62, (2, 5): 0.35, (0, 3): 0.4}
    nodes = list(people)
    for k, (a, b) in enumerate(K.EDGES):
        f = frac.get((a, b), 0.5)
        nodes.append(("", people[a][1] + (people[b][1] - people[a][1]) * f, people[a][2] + (people[b][2] - people[a][2]) * f))
    edges = []
    for k, (a, b) in enumerate(K.EDGES):
        edges += [[a, n + k], [n + k, b]]
    eid = {frozenset(e): k for k, e in enumerate(K.EDGES)}
    mins = K.MINUTES
    states = []

    def paint(settled, tentative, cur, hot_ties, text, waiting_line):
        ns = []
        for v in range(n):
            if v == cur:
                ns.append({"f": "hot", "r": 20, "l": str(best[v]), "ring": 1})
            elif v in settled:
                ns.append({"f": "reach", "r": 17, "l": str(best[v]), "ring": 0})
            elif v in tentative:
                ns.append({"f": "src", "r": 17, "l": str(tentative[v]), "ring": 0})
            else:
                ns.append({"f": "base", "r": 17, "l": "", "ring": 0})
        es = [dict(M.DEFAULT_EDGE) for _ in edges]
        for k in range(m):
            ns.append({"f": "base", "r": 9, "l": str(mins[k]), "ring": 0})
        for v in settled:
            p = parent[v]
            if p is not None:
                k = eid[frozenset((p, v))]
                for j in (2 * k, 2 * k + 1):
                    es[j] = {"k": "reach", "w": 3.0}
                ns[n + k] = {"f": "reach", "r": 9, "l": str(mins[k]), "ring": 0}
        for k in hot_ties:
            for j in (2 * k, 2 * k + 1):
                es[j] = {"k": "hot", "w": 3.8}
            ns[n + k] = {"f": "hot", "r": 9, "l": str(mins[k]), "ring": 0}
        states.append((ns, es, [waiting_line], text))

    def line(waiting, settled_order):
        w = "  ".join(f"{NAMES[v]} {d}" for d, v in waiting) or "(nobody)"
        s = " ".join(NAMES[v] for v in settled_order)
        return f"Waiting: {w}      Settled: {s}"

    paint(set(), {0: 0}, None, [], "Ana starts with a guess of 0 minutes. Everyone else has no guess yet. The number on each small dot is the minutes that tie takes.", line([(0, 0)], []))
    settled_order = []
    for st in steps:
        u, d = st["settle"], st["dist"]
        settled_order.append(u)
        settled = set(settled_order)
        tentative = {v: dd for dd, v in st["waiting"]}
        hot = [eid[frozenset((u, v))] for v, old, new in st["changes"]]
        if u == 0:
            who = K.join([f"{NAMES[v]} {new}" for v, old, new in st["changes"]])
            text = f"Ana is settled at 0. Each friend gets a first guess from the tie to Ana: {who}."
        else:
            better = [(v, old, new) for v, old, new in st["changes"] if old != float("inf")]
            first = [(v, old, new) for v, old, new in st["changes"] if old == float("inf")]
            bits = []
            if first:
                bits.append("first guesses: " + K.join([f"{NAMES[v]} {new}" for v, _, new in first]))
            if better:
                bits.append("better guesses: " + K.join([f"{NAMES[v]} from {old} to {new}" for v, old, new in better]))
            tail = f" Their ties give {'; '.join(bits)}." if bits else " Nobody's guess improves."
            text = f"{NAMES[u]} has the smallest guess, {d} minutes, so that is final.{tail}"
        paint(settled, tentative, u, hot, text, line(st["waiting"], settled_order))
    route = []
    v = 9
    while v is not None:
        route.append(v)
        v = parent[v]
    route = route[::-1]
    ties = [eid[frozenset(e)] for e in zip(route, route[1:])]
    ns_last = None
    paint(set(range(n)), {}, None, ties,
          f"Everyone is settled. The cheapest way to Jo is {K.join([NAMES[v] for v in route])}, {best[9]} minutes.",
          line([], settled_order))
    scene = {"id": "dijkstra-queue", "w": 640, "h": 380, "ms": 1500, "nodes": nodes, "edges": edges, "book": BOOK,
             "panel": {"kind": "text", "x": 24, "y": 344}, "states": states, "still": [0, 2, 5, len(states) - 1]}
    labels = ["Start", "Cleo settled", "Fay settled", "Done"]
    still = M.filmstrip(scene, labels, "Dijkstra's algorithm on the travel-time network",
                        "Four copies of the ten-person network with minutes on every tie, showing Dijkstra's algorithm from Ana.",
                        show=lambda i, m: NAMES[i] if i < n else "")
    return scene, still


def bidirectional_meet():
    import make_anim as M
    _roles(M)
    raw = M.load("bidirectional-meet", BOOK)["grid"]
    w, h = raw["w"], raw["h"]
    assert (w, h) == (9, 5) and raw["edges"] == [list(e) for e in K.grid_edges(w, h)], "the engine ran on a different grid"
    edges = [list(e) for e in raw["edges"]]
    adj = K.adjacency(w * h, [tuple(e) for e in edges])
    s, t = raw["source"], raw["target"]
    cell = 64
    nodes = []
    for v in range(w * h):
        r, c = divmod(v, w)
        nodes.append(("Home" if v == s else "Cafe" if v == t else "", 44 + c * cell, 48 + r * 58))
    eid = {frozenset(e): i for i, e in enumerate(edges)}
    # reference: one whole level at a time from the end with the smaller frontier (forward end on a tie)
    da, db = {s: 0}, {t: 0}
    fa, fb = [s], [t]
    rounds, meet = [], None
    while meet is None:
        grow_a = len(fa) <= len(fb)
        front, mine, other = (fa, da, db) if grow_a else (fb, db, da)
        nxt, new, hit = [], [], None
        for u in front:
            for v in adj[u]:
                if v in other and hit is None:
                    hit = (u, v)
                if v not in mine:
                    mine[v] = mine[u] + 1
                    nxt.append(v)
                    new.append((u, v))
        if grow_a:
            fa = nxt
        else:
            fb = nxt
        rounds.append(("a" if grow_a else "b", new, dict(da), dict(db)))
        if hit:
            meet = hit
    u, v = meet
    length = (da[u] if u in da else db[u]) + 1 + (db[v] if v in db and u in da else da[v])
    assert float(raw["length"]) == length, "engine route length differs from the reference"
    path = raw["path"]
    assert path[0] == s and path[-1] == t and len(path) == length + 1
    assert all(frozenset(e) in eid for e in zip(path, path[1:])), "the engine's route leaves the grid"
    one_ref, _ = K.bfs_ball(adj, s, t)
    popped_ref = one_ref.index(t) + 1 if False else None
    # reference one-sided search: nodes taken off the line up to and including the target
    from collections import deque
    seen, q, popped = {s}, deque([s]), 0
    while q:
        x = q.popleft()
        popped += 1
        if x == t:
            break
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                q.append(y)
    assert popped == len(raw["one_sided_order"]), "engine one-sided search settled a different number of places"
    states = []

    def paint(rnd, text, final=False):
        side, new, ca, cb = rnd if rnd else (None, [], {s: 0}, {t: 0})
        ns = [dict(M.DEFAULT_NODE, r=13) for _ in range(w * h)]
        es = [dict(M.DEFAULT_EDGE) for _ in edges]
        for x in ca:
            ns[x] = {"f": "reach", "r": 13, "l": "", "ring": 0}
        for x in cb:
            ns[x] = {"f": "c", "r": 13, "l": "", "ring": 0}
        ns[s] = {"f": "src", "r": 16, "l": "", "ring": 0}
        ns[t] = {"f": "hot", "r": 16, "l": "", "ring": 0}
        for dd, f, role in ((ca, s, "reach"), (cb, t, "c")):
            for x, d in dd.items():
                if d:
                    for y in adj[x]:
                        if dd.get(y) == d - 1:
                            es[eid[frozenset((x, y))]] = {"k": role, "w": 2.4}
                            break
        if final:
            for a, b in zip(path, path[1:]):
                es[eid[frozenset((a, b))]] = {"k": "hot", "w": 4.2}
            for x in path:
                ns[x] = {"f": "hot", "r": 15, "l": "", "ring": 0}
            ns[s] = {"f": "src", "r": 17, "l": "", "ring": 0}
        states.append((ns, es, [f"Places found:   from Home {len(ca)}    from Cafe {len(cb)}    together {len(ca) + len(cb)}"], text))

    paint(None, "Two searches start together: one from Home (orange) and one from Cafe (red). Each is an ordinary breadth-first search.")
    for k, rnd in enumerate(rounds):
        side, new, ca, cb = rnd
        who = "Home" if side == "a" else "Cafe"
        d = (max(ca.values()) if side == "a" else max(cb.values()))
        last = k == len(rounds) - 1
        if last:
            text = f"The {who} side steps out to distance {d} and bumps into a place the other side already found. The two searches have met."
        else:
            text = f"The {who} side has fewer people on its frontier, so it steps out one more level, to distance {d}: {len(new)} new places."
        paint(rnd, text)
    last = rounds[-1]
    paint(last, f"Join the two halves: a route of {length} blocks. Together the searches looked at {len(last[2]) + len(last[3])} places; one search from Home alone settled {popped} before it reached Cafe.", final=True)
    k_mid = len(states) // 2
    scene = {"id": "bidirectional-meet", "w": 640, "h": 340, "ms": 1400, "nodes": nodes, "edges": edges, "book": BOOK,
             "panel": {"kind": "text", "x": 24, "y": 306}, "states": states, "still": [0, 3, len(states) - 2, len(states) - 1]}
    labels = ["Both searches start", "After three steps", "They meet", "The route"]
    still = M.filmstrip(scene, labels, "Searching from both ends",
                        "Four copies of a nine by five grid of streets showing two searches growing toward each other and meeting in the middle.",
                        show=lambda i, m: nodes[i][0])
    return scene, still


BUILDERS = {"dijkstra-queue": dijkstra_queue, "bidirectional-meet": bidirectional_meet}

"""Many breadth-first searches sharing one pass, one bit per search (algorithms book, chapter 19).

The frames are the engine's own report (bitset::MultiBfs: at each step, who was newly reached and by which searches).
The scene checks that every search's distances match a plain single search and that the harmonic sums built from the
levels match the engine's harmonic centrality."""

BOOK = "algorithms"


def _adj(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    return adj


def _bfs(adj, s):
    dist = [-1] * len(adj)
    dist[s] = 0
    queue = [s]
    for u in queue:
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


def _trace(raw, n):
    """Per search, the distance to every person, rebuilt from the engine's steps, and checked."""
    lanes, edges = raw["lanes"], raw["edges"]
    dist = [[-1] * n for _ in range(lanes)]
    for lane in range(lanes):
        dist[lane][lane] = 0
    for level, node, bits in raw["steps"]:
        for lane in range(lanes):
            if bits >> lane & 1:
                assert dist[lane][node] < 0
                dist[lane][node] = level
    adj = _adj(n, edges)
    for lane in range(lanes):
        assert dist[lane] == _bfs(adj, lane), "the shared pass disagrees with a single search"
        h = sum(1 / d for d in dist[lane] if d > 0)
        assert abs(h - raw["harmonic"][lane]) < 1e-12, "harmonic sums disagree with the engine"
    return dist


def _frames(M, n, edges, dist, lanes, names, big):
    top = max(max(d) for d in dist)
    states = []
    for k in range(top + 1):
        reached = [sum(1 for l in range(lanes) if 0 <= dist[l][i] <= k) for i in range(n)]
        new = [sum(1 for l in range(lanes) if dist[l][i] == k) for i in range(n)]
        ns = []
        for i in range(n):
            if k == 0 and i < lanes:
                ns.append({"f": "src", "r": 10 if big else 16, "l": "" if big else "1", "ring": 0})
            elif new[i] and k > 0:
                ns.append({"f": "hot", "r": 11 if big else 19, "l": "" if big else str(reached[i]), "ring": 1})
            elif reached[i] == lanes:
                ns.append({"f": "reach", "r": 9 if big else 16, "l": "" if big else str(reached[i]), "ring": 0})
            elif reached[i]:
                ns.append({"f": "reach" if not big else "base", "r": 9 if big else 16, "l": "" if big else str(reached[i]), "ring": 0})
            else:
                ns.append({"f": "base", "r": 8 if big else 16, "l": "", "ring": 0})
        es = []
        for a, b in edges:
            used = k > 0 and any((dist[l][a] == k - 1 and dist[l][b] == k) or (dist[l][b] == k - 1 and dist[l][a] == k)
                                 for l in range(lanes))
            es.append({"k": "hot", "w": 2.6 if not big else 1.8} if used else {"k": "base", "w": 1.6 if not big else 1.0})
        per_lane = [sum(1 for d in dist[l] if 0 <= d <= k) for l in range(lanes)]
        pairs = sum(new) if k > 0 else lanes
        if k == 0:
            text = (f"{lanes} searches start at once, one bit each, from {M.join(names[:lanes])}." if not big else
                    f"{lanes} searches start at once, one bit each, from members 1 to {lanes} (orange).")
        else:
            hot = sum(1 for i in range(n) if new[i])
            text = (f"Step {k}: one pass over the friend lists. {pairs} search-and-person pairs are new, spread over {hot} "
                    f"{'person' if hot == 1 else 'people'} (red)." + ("" if big or k > 1 else " The number in a dot is how many searches have reached that person."))
            if k == top:
                text += f" Every search has now reached all {n} people."
        states.append((ns, es, per_lane, text))
    return states, top


def kite():
    import make_anim as M

    raw = M.load("msbfs-kite", BOOK)
    names, edges, lanes = raw["names"], raw["edges"], raw["lanes"]
    n = len(names)
    dist = _trace(raw, n)
    states, top = _frames(M, n, edges, dist, lanes, names, big=False)
    h = raw["harmonic"]
    states.append((states[-1][0], [dict(M.DEFAULT_EDGE) for _ in edges], states[-1][2],
                   f"{top} passes did the work of {lanes} separate searches. The harmonic sums match the engine's: Ana {h[0]:.2f}, Dev {h[3]:.2f}, Hana {h[7]:.2f}."))
    scene = {"id": "msbfs-kite", "book": BOOK, "w": 640, "h": 360, "ms": 1700, "nodes": M.layout(names, edges), "edges": edges,
             "panel": {"kind": "bars", "x": 452, "y": 56, "w": 172, "h": 268, "labels": [f"from {x}" for x in names[:lanes]],
                       "max": n, "title": "People each search has reached"},
             "states": states, "still": [0, 1, 2, top]}
    still = M.filmstrip(scene, ["Start: 8 searches", "Step 1", "Step 2", f"Step {top}: done"],
                        "Eight searches sharing one pass",
                        "Four copies of the ten-person network as eight searches spread together; the number in each dot counts the searches that have reached that person.")
    return scene, still


def karate():
    import make_anim as M
    from anim_scenes import compact

    raw = M.load("msbfs-karate", BOOK)
    n, edges, lanes = raw["n"], raw["edges"], raw["lanes"]
    dist = _trace(raw, n)
    names = [f"member {i + 1}" for i in range(n)]
    states, top = _frames(M, n, edges, dist, lanes, names, big=True)
    nodes0 = [("", x, y) for _, x, y in M.layout([str(i) for i in range(n)], edges)]
    scene = {"id": "msbfs-karate", "book": BOOK, "w": 640, "h": 360, "ms": 1700, "compact": True, "nodes": nodes0, "edges": edges,
             "panel": {"kind": "bars", "x": 452, "y": 40, "w": 172, "h": 300, "labels": [str(i + 1) for i in range(lanes)],
                       "max": n, "title": "Reached, by search"},
             "states": states, "still": [0, 1, 2, top]}
    still = compact.filmstrip(M, scene, ["Start: 16 searches", "Step 1", "Step 2", f"Step {top}: done"],
                              "Sixteen searches sharing one pass on the karate club",
                              "Four copies of the karate club as sixteen searches spread together; newly reached members are red.")
    return scene, still


BUILDERS = {"msbfs-kite": kite, "msbfs-karate": karate}

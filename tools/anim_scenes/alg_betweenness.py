"""Brandes' two passes from Ana, and betweenness from a growing sample of starting people (algorithms book, ch. 18).

The forward and backward traces follow the textbook rule level by level; each scene checks that its last frame equals
the engine's own answer (route counts from bitset::RowPaths, credit from compute_betweenness_from_sources), so the
pictures cannot drift from the engine. The sampling scene shows the engine's partial sums directly."""

BOOK = "algorithms"


def _levels(dist):
    by = {}
    for i, d in enumerate(dist):
        by.setdefault(d, []).append(i)
    return by


def _positions(dist):
    """Columns by distance from the source, like the chapter's still figures."""
    pos = {}
    for d, ids in _levels(dist).items():
        for k, i in enumerate(ids):
            pos[i] = (40 + d * 92, 60 + 250 * (k + 0.5) / len(ids))
    return pos


def _num(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def _run(raw, source):
    return next(r for r in raw["runs"] if r["source"] == source)


def forward():
    import make_anim as M

    raw = M.load("brandes-steps", BOOK)
    names, edges = raw["names"], raw["edges"]
    run = _run(raw, 0)
    dist, sigma = run["distances"], [int(round(s)) for s in run["sigma"]]
    n = len(names)
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    # the textbook rule: a person's count is the sum of the counts of their neighbors one step closer
    ref = [0] * n
    ref[0] = 1
    for d in range(1, max(dist) + 1):
        for v in range(n):
            if dist[v] == d:
                ref[v] = sum(ref[u] for u in adj[v] if dist[u] == d - 1)
    assert ref == sigma, "the forward rule disagrees with the engine's route counts"
    pos = _positions(dist)
    nodes0 = [(names[i], *pos[i]) for i in range(n)]
    top = max(dist)
    states = []
    for k in range(top + 2):
        kk = min(k, top)
        ns, es = [], []
        for i in range(n):
            if i == 0:
                ns.append({"f": "src", "r": 18, "l": "1", "ring": 0})
            elif dist[i] <= kk:
                now = dist[i] == kk and k <= top
                ns.append({"f": "reach", "r": 19 if now else 16, "l": str(sigma[i]), "ring": 1 if now else 0})
            else:
                ns.append(dict(M.DEFAULT_NODE))
        for a, b in edges:
            lo, hi = min(dist[a], dist[b]), max(dist[a], dist[b])
            if hi - lo == 1 and hi <= kk:
                now = hi == kk and k <= top
                es.append({"k": "hot" if now else "reach", "w": 3.2 if now else 2.2})
            else:
                es.append(dict(M.DEFAULT_EDGE))
        bars = [sigma[i] if dist[i] <= kk else 0 for i in range(n)]
        if k == 0:
            text = "Ana starts with 1 route to herself. Every count after this is a sum of the counts one step closer."
        elif k <= top:
            who = [i for i in range(n) if dist[i] == k]
            big = max(who, key=lambda i: (sigma[i], -i))
            parents = [names[u] for u in adj[big] if dist[u] == k - 1]
            if sigma[big] > 1:
                text = (f"Distance {k}: {M.join(names[i] for i in who)}. {names[big]} is reached from {M.join(parents)}, "
                        f"so {names[big]} has {' + '.join(str(sigma[adj_u]) for adj_u in adj[big] if dist[adj_u] == k - 1)} = {sigma[big]} shortest routes.")
            else:
                text = (f"Distance {k}: {M.join(names[i] for i in who)}, " +
                        ("each reached by a single shortest route." if len(who) > 1 else "reached by a single shortest route."))
        else:
            text = (f"Done in one sweep. Gus has {sigma[6]} shortest routes from Ana, Eli has {sigma[4]}, everyone else 1. "
                    "These are the engine's own counts.")
        states.append((ns, es, bars, text))
    scene = {"id": "brandes-forward", "book": BOOK, "w": 640, "h": 360, "ms": 1500, "nodes": nodes0, "edges": edges,
             "panel": {"kind": "bars", "x": 452, "y": 56, "w": 172, "h": 268, "labels": names, "max": max(sigma) + 1,
                       "title": "Shortest routes from Ana"},
             "states": states, "still": [0, 1, 2, top + 1]}
    still = M.filmstrip(scene, ["Start", "Distance 1", "Distance 2", "Every count"], "Counting shortest routes from Ana",
                        "Four copies of the ten-person network in columns by distance from Ana, filling in each person's number of shortest routes.")
    return scene, still


def backward():
    import make_anim as M

    raw = M.load("brandes-steps", BOOK)
    names, edges = raw["names"], raw["edges"]
    run = _run(raw, 0)
    dist, sigma, contrib = run["distances"], run["sigma"], run["contrib"]
    n = len(names)
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    pos = _positions(dist)
    nodes0 = [(names[i], *pos[i]) for i in range(n)]
    top = max(dist)
    delta = [0.0] * n
    done = set()
    states = []

    def picture(active, text):
        ns, es = [], []
        for i in range(n):
            if i == 0:
                ns.append({"f": "src", "r": 18, "l": "", "ring": 0})
            elif i in active:
                ns.append({"f": "hot", "r": 19, "l": _num(delta[i]), "ring": 1})
            elif i in done:
                ns.append({"f": "reach", "r": 16, "l": _num(delta[i]), "ring": 0})
            else:
                ns.append({"f": "base", "r": 16, "l": _num(delta[i]) if delta[i] else "", "ring": 0})
        for a, b in edges:
            far, near = (a, b) if dist[a] > dist[b] else (b, a)
            on = dist[far] - dist[near] == 1
            es.append({"k": "hot", "w": 3.2} if on and far in active else ({"k": "reach", "w": 2.2} if on and far in done else dict(M.DEFAULT_EDGE)))
        states.append((ns, es, [round(delta[i], 3) for i in range(n)], text))

    picture(set(), "Now walk back from the far end. Everyone starts with no credit. Each person will pass on 1 for themselves plus whatever credit they have collected.")
    for d in range(top, 0, -1):
        layer = [w for w in range(n) if dist[w] == d]
        for w in layer:
            for v in adj[w]:
                if dist[v] == d - 1 and v != 0:
                    delta[v] += sigma[v] / sigma[w] * (1 + delta[w])
        done.update(layer)
        w = max(layer, key=lambda i: (delta[i], i))
        ups = [v for v in adj[w] if dist[v] == d - 1]
        if len(ups) == 1:
            text = (f"Distance {d}: {M.join(names[i] for i in layer)} {'pass' if len(layer) > 1 else 'passes'} back. {names[w]} hands 1 + {_num(delta[w])} = "
                    f"{_num(1 + delta[w])} to {names[ups[0]]}" + (" (Ana is the start, so hers is not counted)." if ups[0] == 0 else "."))
        else:
            text = (f"Distance {d}: {M.join(names[i] for i in layer)} {'pass' if len(layer) > 1 else 'passes'} back. {names[w]} splits 1 + {_num(delta[w])} among "
                    f"{M.join(names[v] for v in ups)} by their route counts.")
        picture(set(layer), text)
    done.add(0)
    # the engine halves each source's credit (every pair is seen from both ends), so its value times 2 is the rule's
    assert all(abs(delta[i] - 2 * contrib[i]) < 1e-9 for i in range(n)), "the backward rule disagrees with the engine"
    picture(set(), f"Ana's routes give Fay {_num(delta[5])}, Hana {_num(delta[7])}, Ivo {_num(delta[8])}, Ben and Dev {_num(delta[1])}. "
                   "The engine reports the same numbers, halved because each pair is seen from both ends.")
    last = len(states) - 1
    scene = {"id": "brandes-backward", "book": BOOK, "w": 640, "h": 360, "ms": 1700, "nodes": nodes0, "edges": edges,
             "panel": {"kind": "bars", "x": 452, "y": 56, "w": 172, "h": 268, "labels": names,
                       "max": int(max(delta)) + 1, "title": "Credit from Ana's routes"},
             "states": states, "still": [1, 3, 4, last]}
    still = M.filmstrip(scene, ["Jo passes back", "Distance 2 passes back", "Distance 1 passes back", "All credit"],
                        "Passing credit back toward Ana",
                        "Four copies of the ten-person network in columns by distance from Ana, with credit flowing back from the far end, one column at a time.")
    return scene, still


def sampling():
    import make_anim as M
    from anim_scenes import compact

    raw = M.load("betweenness-sampling", BOOK)
    n, edges, order, rows, exact = raw["n"], raw["edges"], raw["order"], raw["samples"], raw["exact"]
    nodes0 = [("", x, y) for _, x, y in M.layout([str(i) for i in range(n)], edges)]
    top = sorted(range(n), key=lambda i: -exact[i])[:5]
    peak = max(exact)
    states = []

    def size(v):
        return M.r1(5 + 13 * min(v, 1.3 * peak) / peak)
    for r in rows:
        k = r["k"]
        est = [n / k * p for p in r["partial"]]
        picked = set(order[:k])
        ns = [{"f": "src" if i in picked else ("reach" if i in top else "base"), "r": size(est[i]), "l": "", "ring": 1 if i in top else 0}
              for i in range(n)]
        es = [{"k": "base", "w": 1.0} for _ in edges]
        worst = max(range(n), key=lambda i: abs(est[i] - exact[i]))
        if k == n:
            assert all(abs(a - b) < 1e-9 for a, b in zip(est, exact)), "the full sample must equal the exact scores"
            text = f"All {n} members as starting people: the estimate is the exact betweenness. Member {top[0] + 1} scores {exact[top[0]]:.0f}."
        else:
            text = (f"{k} starting {'person' if k == 1 else 'people'} (orange), scaled up by {n} / {k}. Member {top[0] + 1} is estimated at "
                    f"{est[top[0]]:.0f} against an exact {exact[top[0]]:.0f}; the worst miss is member {worst + 1}, off by {abs(est[worst] - exact[worst]):.0f}.")
        states.append((ns, es, [round(est[i], 1) for i in top], text))
    states.insert(0, ([{"f": "reach" if i in top else "base", "r": size(exact[i]), "l": "", "ring": 1 if i in top else 0} for i in range(n)],
                      [{"k": "base", "w": 1.0} for _ in edges], [round(exact[i], 1) for i in top],
                      f"The karate club, dots sized by exact betweenness. The five ringed members score highest. Now estimate it from a few starting people instead of all {n}."))
    scene = {"id": "betweenness-sampling", "book": BOOK, "w": 640, "h": 360, "ms": 1800, "compact": True, "nodes": nodes0,
             "edges": edges,
             "panel": {"kind": "bars", "x": 452, "y": 56, "w": 172, "h": 268, "labels": [f"member {i + 1}" for i in top],
                       "max": int(1.3 * peak) + 1, "title": "Estimated betweenness"},
             "states": states, "still": [0, 2, 6, len(states) - 1]}
    ks = [r["k"] for r in rows]
    still = compact.filmstrip(M, scene, ["Exact", f"{ks[1]} sampled", f"{ks[5]} sampled", f"All {n}"],
                              "Betweenness estimated from sampled starting people",
                              "Four copies of the karate club with dots sized by estimated betweenness from a growing sample of starting people, ending at the exact scores.")
    return scene, still


BUILDERS = {"brandes-forward": forward, "brandes-backward": backward, "betweenness-sampling": sampling}

"""The ten-person network joined tie by tie with union-find (algorithms book, chapter 3).
The scene replays the engine's rule (the smaller root is kept, path halving) and asserts every step against the
engine's recorded unions and leaders."""
ROLES = ["src", "reach", "d", "c", "a", "e"]  # light fills first, so the leader number stays readable


def _find(p, x):
    while p[x] != x:
        p[x] = p[p[x]]
        x = p[x]
    return x


def build():
    import make_anim as M
    from anim_scenes import community_levels

    community_levels._common()  # registers the extra colors
    raw = M.load("union-find", "algorithms")
    names, steps = raw["names"], raw["steps"]
    n = len(names)
    edges = [tuple(s["tie"]) for s in steps]
    parent = list(range(n))
    color = {}
    states = [([dict(M.DEFAULT_NODE, r=16) for _ in range(n)], [dict(M.DEFAULT_EDGE) for _ in edges],
               [f"{n} groups.", "Leaders:", " ".join(map(str, range(n)))],
               "Ten people, no ties yet: ten groups of one. Each ties is a clue that two people belong together.")]
    merged_edge = {}
    used = 0
    for k, s in enumerate(steps):
        a, b = s["tie"]
        got = None
        ra, rb = _find(parent, a), _find(parent, b)
        if ra != rb:
            kept, absorbed = min(ra, rb), max(ra, rb)
            parent[absorbed] = kept
            got = [kept, absorbed]
        copy = list(parent)
        roots = [_find(copy, i) for i in range(n)]
        assert got == s["merged"], f"step {k}: the engine's union disagrees with the replay"
        assert roots == s["roots"], f"step {k}: leaders disagree with the engine"
        if got:
            kept, absorbed = got
            if kept not in color:
                color[kept] = next((r for r in ROLES if r not in color.values()), None)
                assert color[kept], "more groups than colors"
            if absorbed in color:
                del color[absorbed]
            merged_edge[k] = True
        groups = sorted(set(roots))
        ns = []
        for i in range(n):
            r = roots[i]
            ns.append({"f": color.get(r, "base"), "r": 16, "l": str(r), "ring": 1 if i == r and color.get(r) else 0})
        es = []
        for j, e in enumerate(edges):
            if j == k:
                es.append({"k": "hot", "w": 3.4})
            elif j < k and merged_edge.get(j):
                es.append({"k": color.get(roots[e[0]], "base"), "w": 2.6})
            elif j < k:
                es.append({"k": "base", "w": 1.0})
            else:
                es.append(dict(M.DEFAULT_EDGE))
        if got:
            text = (f"{names[a]} and {names[b]}: different leaders ({ra} and {rb}), so join the groups. "
                    f"{kept} stays leader and {absorbed}'s group moves under it.")
        else:
            used += 1
            text = f"{names[a]} and {names[b]} already have the same leader ({ra}), so nothing changes."
        states.append((ns, es, [f"{len(groups)} groups.", "Leaders:", " ".join(map(str, roots))], text))
    # final frame: all ties processed
    ns, es, m, _ = states[-1]
    es = [{"k": e["k"] if e["k"] != "hot" else "base", "w": e["w"] if e["w"] < 3 else 1.0} for e in es]
    states.append((ns, es, m, f"All 18 ties are read. {used} of them told us nothing new. "
                              f"Everyone has leader {steps[-1]['roots'][0]}: the network is one connected piece."))
    last = len(states) - 1
    scene = {"id": "union-find", "book": "algorithms", "w": 640, "h": 360, "ms": 1300, "nodes": [(nm, x, y) for nm, x, y in M.layout(names, [list(e) for e in edges])],
             "edges": [list(e) for e in edges], "panel": {"kind": "text", "x": 24, "y": 8, "title": ""}, "states": states,
             "still": [0, 4, 11, last]}
    labels = ["Start", "After 4 ties", "After 11 ties", "Done"]
    still = M.filmstrip(scene, labels, "Union-find on the ten-person network",
                        "Four copies of the ten-person network colored by group as ties are read one at a time.")
    return scene, still


BUILDERS = {"union-find": build}

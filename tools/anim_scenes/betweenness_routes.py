"""Betweenness counted source by source on the ten-person friendship network (chapter 6)."""


def build():
    import make_anim as M
    from anim_scenes import compact

    raw = M.load("betweenness-routes")
    names, edges, rows, total = raw["names"], raw["edges"], raw["sources"], raw["total"]
    n = len(names)
    top = max(total)
    nodes0 = M.layout(names, edges)
    # the engine's per-source scores must add up to its full betweenness (the generator asserts it too)
    assert all(abs(sum(r["contrib"][i] for r in rows) - total[i]) < 1e-9 for i in range(n))

    def size(v):
        return M.r1(10 + 14 * v / top)

    def g(x):
        return f"{x:.1f}".rstrip("0").rstrip(".")

    cum = [0.0] * n
    states = [([{"f": "base", "r": size(0), "l": "", "ring": 0} for _ in range(n)],
               [dict(M.DEFAULT_EDGE) for _ in edges], [0.0] * n,
               "Betweenness counts how often a person sits on other people's shortest routes. We add them up one starting person at a time, and every route is seen from both ends, so each end counts half. Everyone starts at zero.")]
    for r in rows:
        s, c, d = r["source"], r["contrib"], r["distances"]
        cum = [a + b for a, b in zip(cum, c)]
        ns = []
        for i in range(n):
            if i == s:
                ns.append({"f": "src", "r": 18, "l": "", "ring": 1})
            elif c[i] > 1e-9:
                ns.append({"f": "reach", "r": max(13, size(cum[i])), "l": "+" + g(c[i]), "ring": 0})
            else:
                ns.append({"f": "base", "r": size(cum[i]), "l": "", "ring": 0})
        es = []
        for a, b in edges:
            on = abs(d[a] - d[b]) == 1
            es.append({"k": "hot" if on else "base", "w": 3.2 if on else 1.6})
        gain = max(range(n), key=lambda i: (c[i], -i))
        if c[gain] < 1e-9:
            text = f"Shortest routes starting at {names[s]}. Nobody sits in the middle of them, so no one gains anything."
        else:
            text = (f"Shortest routes starting at {names[s]}. {names[gain]} sits on the most of them and gains {g(c[gain])}; "
                    f"the number inside a dot is what that person gains from this source.")
        states.append((ns, es, [round(x, 1) for x in cum], text))
    last = len(states) - 1
    ns = [{"f": "src" if total[i] == top else "base", "r": size(total[i]), "l": "", "ring": 0} for i in range(n)]
    order = sorted(range(n), key=lambda i: -total[i])
    zeros = sum(1 for v in total if v < 1e-9)
    states.append((ns, [dict(M.DEFAULT_EDGE) for _ in edges], [round(x, 1) for x in total],
                   f"All ten sources counted. {names[order[0]]} is on top with {g(total[order[0]])} routes through them, "
                   f"then {names[order[1]]} with {g(total[order[1]])}; {zeros} people score zero."))
    scene = {"id": "betweenness-routes", "w": 640, "h": 360, "ms": 1300, "nodes": nodes0, "edges": edges,
             "panel": {"kind": "bars", "x": 452, "y": 56, "w": 172, "h": 268, "labels": names,
                       "max": int(top) + 1, "title": "Routes through each person"},
             "states": states, "still": [0, 1, 5, last + 1]}
    labels = ["Start", f"Source: {names[0]}", f"Source: {names[4]}", "All ten sources"]

    def show(i, m):
        return f"{names[i]} {g(m[i])}"

    still = compact.filmstrip(M, scene, labels, "Betweenness counted one source at a time",
                              "Four copies of the ten-person friendship network showing shortest routes from one person at a time and the running scores.",
                              tag=show)
    return scene, still


BUILDERS = {"betweenness-routes": build}

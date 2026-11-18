"""Louvain and Leiden merging communities level by level on the karate club (chapter 10)."""
ROLES = ["a", "src", "c", "d", "reach", "hot"]  # six colors that look different on paper


def _common():
    import make_anim as M
    from figs import BLUE, GREEN, ORANGE, PURPLE, SKY
    for role, fill, stroke in (("a", BLUE, "#004f7c"), ("c", GREEN, "#00694c"), ("d", PURPLE, "#8f4a73"),
                               ("b", ORANGE, "#b87f00"), ("e", SKY, "#2f7fae")):
        M.NODE.setdefault(role, (fill, stroke))
    return M


def _groups(membership):
    out = {}
    for i, g in enumerate(membership):
        out.setdefault(g, []).append(i)
    return list(out.values())


def _connected(members, adj):
    seen, todo = {members[0]}, [members[0]]
    while todo:
        for j in adj[todo.pop()]:
            if j in members and j not in seen:
                seen.add(j)
                todo.append(j)
    return len(seen) == len(members)


def _colors(groups, prev_colors, adj):
    """One role per group of two or more people; touching groups differ; a group keeps the color of the earlier
    group it mostly came from when that is free."""
    where = {i: gi for gi, g in enumerate(groups) for i in g}
    touch = [set() for _ in groups]
    for i, js in enumerate(adj):
        for j in js:
            if where[i] != where[j]:
                touch[where[i]].add(where[j])
    out = {}
    for gi in sorted((g for g, m in enumerate(groups) if len(m) > 1), key=lambda g: -len(groups[g])):
        taken = {out[t] for t in touch[gi] if t in out}
        votes = {}
        for i in groups[gi]:
            c = prev_colors.get(i)
            if c:
                votes[c] = votes.get(c, 0) + 1
        pref = [c for c, _ in sorted(votes.items(), key=lambda kv: -kv[1])] + ROLES
        pick = next((c for c in pref if c not in taken), None)
        assert pick, "more touching groups than colors"
        out[gi] = pick
    return {i: out[where[i]] for i in where if where[i] in out}, where


def _scene(aid, title, strip_title, strip_alt, lead, texts, labels, ms):
    M = _common()
    raw = M.load(aid)
    n, edges, levels = raw["n"], raw["edges"], raw["levels"]
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    # drop a final level that repeats the one before it (the method stopped changing the partition)
    keep = [levels[0]]
    for lv in levels[1:]:
        if _groups(lv["membership"]) != _groups(keep[-1]["membership"]):
            keep.append(lv)
    levels = keep
    nodes0 = [("", x, y) for _, x, y in M.layout([str(i) for i in range(n)], edges)]
    states, prev = [], {}
    q0 = 0.0
    start_ns = [dict(M.DEFAULT_NODE, r=13) for _ in range(n)]
    states.append((start_ns, [dict(M.DEFAULT_EDGE) for _ in edges], [f"{n} groups,", "modularity below zero"], lead))
    for k, lv in enumerate(levels, start=1):
        groups = _groups(lv["membership"])
        assert all(_connected(g, adj) for g in groups), "a reported group falls apart"
        color, where = _colors(groups, prev, adj)
        prev = color
        ns = [{"f": color.get(i, "base"), "r": 13, "l": "", "ring": 0} for i in range(n)]
        es = []
        for a, b in edges:
            same = where[a] == where[b] and a in color
            es.append({"k": color[a] if same else "base", "w": 2.6 if same else 1.0})
        sizes = sorted((len(g) for g in groups), reverse=True)
        states.append((ns, es, [f"{len(groups)} groups,", f"modularity {lv['modularity']:.3f}"], texts[min(k - 1, len(texts) - 1)](len(groups), lv["modularity"], sizes, k == len(levels))))
    scene = {"id": aid, "w": 640, "h": 360, "ms": ms, "nodes": nodes0, "edges": edges,
             "panel": {"kind": "text", "x": 24, "y": 8, "title": ""}, "states": states, "still": list(range(len(states)))[:4]}
    from anim_scenes import compact
    labels = [lab if i == 0 else f"{lab}: {st[2][0]} {st[2][1]}" for i, (lab, st) in enumerate(zip(labels, states))]
    still = compact.filmstrip(M, scene, labels, strip_title, strip_alt)
    return scene, still, len(levels)


def louvain():
    texts = [
        lambda g, q, s, end: f"First pass: each person, one at a time, moves to the neighboring group that raises modularity most. The 34 people settle into {g} groups, modularity {q:.3f}.",
        lambda g, q, s, end: f"Second pass: every group shrinks to one dot and the same moving starts over on the groups. They merge into {g} communities, modularity {q:.3f}, and one more pass changes nothing.",
    ]
    scene, still, k = _scene("louvain-levels", "", "Louvain on the karate club, level by level",
                             "The karate club network colored by community after each Louvain level.",
                             "Everyone starts as a group of one. Louvain will build communities by moving people, then merging groups.",
                             texts, ["Start", "After level 1", "After level 2", "After level 3"], 1800)
    assert k == 2, f"the Louvain run now has {k} levels: update the captions"
    return scene, still


def leiden():
    texts = [
        lambda g, q, s, end: f"First pass: people move to better groups, and each group is split into well-connected pieces before it merges. {g} small groups form, modularity {q:.3f}.",
        lambda g, q, s, end: f"Second pass: the pieces become the dots and move again. They merge into {g} groups, modularity {q:.3f}.",
        lambda g, q, s, end: f"Third pass: {g} groups, modularity {q:.3f}. Another pass changes nothing, and every group is connected: each member can reach the others without leaving it.",
    ]
    scene, still, k = _scene("leiden-levels", "", "Leiden on the karate club, level by level",
                             "The karate club network colored by community after each Leiden level.",
                             "Everyone starts as a group of one. Leiden adds a refinement step each time before it merges groups.",
                             texts, ["Start", "After level 1", "After level 2", "After level 3"], 1800)
    assert k == 3, f"the Leiden run now has {k} levels: update the captions"
    return scene, still


BUILDERS = {"louvain-levels": louvain, "leiden-levels": leiden}

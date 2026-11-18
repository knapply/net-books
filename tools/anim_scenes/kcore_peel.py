"""Peeling the karate club down to its cores (chapter 10). The peel rounds are derived from the network and checked
against the engine's coreness: a person who leaves while the bar is k has core number k - 1."""


def build():
    import make_anim as M
    from anim_scenes import compact

    raw = M.load("kcore-peel")
    edges, core, n = raw["edges"], raw["coreness"], raw["n"]
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    top = max(core)
    alive, k, rounds, when = set(range(n)), 1, [], {}
    while k <= top:  # the next bar would remove the top core itself, so the peel stops here
        while True:
            out = sorted(i for i in alive if len(adj[i] & alive) < k)
            if not out:
                break
            rounds.append((k, out))
            for i in out:
                when[i] = len(rounds)
            alive -= set(out)
        k += 1
    # every person who left, left at the bar their core number says; everyone left has the top core number
    assert all(core[i] == rounds[when[i] - 1][0] - 1 for i in when), "peel rounds disagree with the engine's coreness"
    assert sorted(alive) == sorted(i for i in range(n) if core[i] == top)
    ids = range(n)
    nodes0 = [("", x, y) for _, x, y in M.layout([str(i) for i in ids], edges)]

    def state(r, text, mark=True):
        """Picture after r rounds have finished, with round r + 1's leavers marked (r = len(rounds): the end)."""
        gone = {i for i in when if when[i] <= r}
        cur = {i for i in when if when[i] == r + 1} if mark else set()
        ns, es = [], []
        for i in ids:
            if i in cur:
                ns.append({"f": "hot", "r": 13, "l": str(core[i]), "ring": 0})
            elif i in gone:
                ns.append({"f": "dim", "r": 11, "l": str(core[i]), "ring": 0})
            elif r == len(rounds):
                ns.append({"f": "reach", "r": 14, "l": str(core[i]), "ring": 1})
            else:
                ns.append({"f": "base", "r": 13, "l": str(len(adj[i] - gone)), "ring": 0})
        for a, b in edges:
            if a in gone or b in gone:
                es.append({"k": "base", "w": 0.5})
            elif a in cur or b in cur:
                es.append({"k": "hot", "w": 2.4})
            elif r == len(rounds):
                es.append({"k": "reach", "w": 2.4})
            else:
                es.append({"k": "base", "w": 1.6})
        shown = r + 1 if r < len(rounds) else r
        done = [sum(1 for i in when if when[i] <= shown and core[i] == c) for c in range(1, top + 1)]
        return ns, es, done, text

    states = [state(0, "Zachary's karate club. The number in each dot is how many friends that person has. "
                       "Peeling means removing everyone with too few friends, over and over, and seeing who is left.", mark=False)]
    for r, (kk, out) in enumerate(rounds, start=1):
        fresh = r == 1 or rounds[r - 2][0] != kk
        who = f"{len(out)} {'person' if len(out) == 1 else 'people'}"
        if kk == 1:
            raise AssertionError("the karate club has nobody with core number 0")
        if fresh:
            text = f"Bar at {kk}: {who} with fewer than {kk} friends leave. Their core number is {kk - 1}."
        else:
            text = (f"Same bar, {kk}. Losing friends who left has pushed {who} below it too. "
                    f"Their core number is {kk - 1} as well.")
        states.append(state(r - 1, text))
    left = sum(1 for i in ids if i not in when)
    states.append(state(len(rounds), f"Nobody else falls below {top}. What is left is the {top}-core: {left} people who each keep "
                                     f"at least {top} friends inside the group. Gray dots show the core number of each person who left."))
    last = len(states) - 1
    cnt = [sum(1 for v in core if v == c) for c in range(1, top + 1)]
    scene = {"id": "kcore-peel", "w": 640, "h": 360, "ms": 1700, "nodes": nodes0, "edges": edges,
             "panel": {"kind": "bars", "x": 470, "y": 74, "w": 156, "h": 150,
                       "labels": [f"Core {c}" for c in range(1, top + 1)], "max": max(cnt), "title": "People peeled off"},
             "states": states, "still": [0, 2, 3, last]}
    labels = ["Start", "Bar at 3", "Bar at 4", f"The {top}-core"]
    still = compact.filmstrip(M, scene, labels, "Peeling the karate club",
                              "Four copies of the karate club network showing people leaving as the bar rises, and the dense core that stays.")
    return scene, still


BUILDERS = {"kcore-peel": build}

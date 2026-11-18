"""PageRank scores settling over rounds on the ten-person friendship network (chapter 6)."""


def build():
    import make_anim as M
    from anim_scenes import compact

    raw = M.load("pagerank-settle")
    names, edges, rounds, settled = raw["names"], raw["edges"], raw["rounds"], raw["settled"]
    n = len(names)
    deg = [sum(1 for e in edges if i in e) for i in range(n)]
    nodes0 = M.layout(names, edges)
    top = max(settled)
    # the last round and the engine's own answer must agree to the shown precision
    assert max(abs(a - b) for a, b in zip(rounds[-1], settled)) < 0.0005, "rounds have not settled"
    moved = [0.0] + [max(abs(a - b) for a, b in zip(rounds[k], rounds[k - 1])) for k in range(1, len(rounds))]
    calm = next(k for k in range(1, len(rounds)) if all(m < 0.0005 for m in moved[k:]))
    seq = [rounds[k] for k in range(calm + 1)] + [settled]
    states = []
    for k, v in enumerate(seq):
        last = k == len(seq) - 1
        lead = max(range(n), key=lambda i: v[i])
        ns = [{"f": "src" if (k > 0 and i == lead) else "base", "r": M.r1(7 + 15 * v[i] / top), "l": "", "ring": 0} for i in range(n)]
        es = [dict(M.DEFAULT_EDGE) for _ in edges]
        order = sorted(range(n), key=lambda i: -v[i])
        if k == 0:
            text = "Everyone starts with the same share of the attention: one tenth each."
        elif k == 1:
            text = (f"Round 1: everyone passes 85% of their score to their friends, split equally, and 15% is shared out evenly. "
                    f"{names[order[0]]}, with {deg[order[0]]} friends, jumps ahead.")
        elif last:
            text = (f"Where it settles, the engine's own answer: {names[order[0]]} holds {v[order[0]]:.2f} and "
                    f"{names[order[-1]]} {v[order[-1]]:.2f}. The scores add up to 1.")
        elif k == calm:
            text = f"Round {k}: from here on no score moves by more than 0.0005. The ranking has settled."
        else:
            mover = max(range(n), key=lambda i: abs(v[i] - seq[k - 1][i]))
            text = f"Round {k}: the biggest change is {moved[k]:.3f}, for {names[mover]}. Changes keep shrinking."
        states.append((ns, es, [round(x, 4) for x in v], text))
    last = len(states) - 1
    scene = {"id": "pagerank-settle", "w": 640, "h": 360, "ms": 1000, "nodes": nodes0, "edges": edges,
             "panel": {"kind": "bars", "x": 452, "y": 56, "w": 172, "h": 268, "labels": names, "max": 0.16, "title": "PageRank"},
             "states": states, "still": [0, 1, 4, last]}
    labels = ["Start: everyone equal", "Round 1", "Round 4", "Settled"]

    def show(i, m):
        return f"{names[i]} {m[i]:.2f}"

    still = compact.filmstrip(M, scene, labels, "PageRank settling, ten people",
                              "Four copies of the ten-person friendship network with dots sized by PageRank at the start, rounds 1 and 4, and settled.",
                              tag=show)
    return scene, still


BUILDERS = {"pagerank-settle": build}

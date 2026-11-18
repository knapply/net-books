"""A ring lattice rewired with a growing probability (chapter 9)."""
import math


def build():
    import make_anim as M
    from anim_scenes import compact

    raw = M.load("small-world-rewiring")
    n, k, draws = raw["n"], raw["k"], raw["draws"]
    allties = sorted({tuple(t) for d in draws for t in d["ties"]})
    index = {t: i for i, t in enumerate(allties)}

    def lattice(t):
        d = (t[1] - t[0]) % n
        return min(d, n - d) <= k // 2

    assert {tuple(t) for t in draws[0]["ties"]} == {t for t in allties if lattice(t)}, "p = 0 should be the plain ring"
    c0, l0 = draws[0]["clustering"], draws[0]["mean_distance"]
    r = 140.0
    nodes0 = [("", 225 + r * math.sin(2 * math.pi * i / n), 190 - r * math.cos(2 * math.pi * i / n)) for i in range(n)]
    states = []
    for j, d in enumerate(draws):
        present = {tuple(t) for t in d["ties"]}
        es = []
        for t in allties:
            if t not in present:
                es.append({"k": "base", "w": 0})
            elif lattice(t):
                es.append({"k": "base", "w": 1.6})
            else:
                es.append({"k": "hot", "w": 2.6})
        moved = sum(1 for t in present if not lattice(t))
        c, l = d["clustering"] / c0, d["mean_distance"] / l0
        p = d["p"]
        if j == 0:
            text = (f"{n} people on a ring, each tied to the 2 nearest on each side: {len(present)} ties, no rewiring. "
                    f"Everyone is {l0:.1f} steps from everyone else on average. Each later picture is a new draw with a bigger rewiring chance.")
        elif j == len(draws) - 1:
            text = (f"Chance {p:g}: every tie is up for rewiring and almost nothing of the ring is left. Clustering has fallen to {c:.2f} of the ring's "
                    f"and distance to {l:.2f}.")
        else:
            text = (f"Chance {p:g}: {moved} of the {len(present)} ties now jump to someone far away (orange). "
                    f"Distance is down to {l:.2f} of the ring's, clustering is {c:.2f}.")
        states.append(([{"f": "base", "r": 9, "l": "", "ring": 0} for _ in range(n)], es, [round(c, 3), round(l, 3)], text))
    still_idx = [0, 2, 4, len(draws) - 1]
    scene = {"id": "small-world-rewiring", "w": 640, "h": 360, "ms": 1500, "nodes": nodes0,
             "edges": [list(t) for t in allties], "panel": {"kind": "bars", "x": 452, "y": 120, "w": 172, "h": 90,
                                                            "labels": ["Clustering", "Distance"], "max": 1,
                                                            "title": "Compared with the ring"},
             "states": states, "still": still_idx}
    labels = [f"Chance of rewiring {draws[i]['p']:g}" for i in still_idx]
    still = compact.filmstrip(M, scene, labels, "A ring of 30 people, rewired",
                              "Four rings of 30 people with more and more ties rewired to far-away people.")
    return scene, still


BUILDERS = {"small-world-rewiring": build}

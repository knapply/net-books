"""Chapter 6: a random walk wandering the ten-person friendship network, with visit counts growing.

One walker, one fixed seed. Frame k is the engine's walk (metrics::walks::sample_walk_visits) after k steps
(data/anim/walk-visits.frames.json). The walker's place at step k is the node whose count rose between the runs of k - 1 and
k steps.
"""
import math


from ._strip import lean_filmstrip  # noqa: E402


def build():
    import make_anim as M
    raw = M.load("walk-visits")
    names, edges, start = raw["names"], raw["edges"], raw["start"]
    frames = [f for f in raw["frames"] if f["steps"] <= 120]  # longer runs stay in the data; 120 keeps the bars readable
    n = len(names)
    deg = [sum(1 for e in edges if i in e) for i in range(n)]
    nodes = M.layout(names, edges)
    eidx = {frozenset(e): i for i, e in enumerate(edges)}
    top_max = max(max(f["visits"]) for f in frames)
    states, here, prev_step = [], start, None
    for k, f in enumerate(frames):
        v, steps = f["visits"], f["steps"]
        hot = None
        if steps == 0:
            assert v[start] == 1 and sum(v) == 1
        else:
            rose = [i for i in range(n) if v[i] != f["before"][i]]
            assert len(rose) == 1 and sum(v) == steps + 1, "the walker's place is not determined by the counts"
            new = rose[0]
            if prev_step is not None and steps == prev_step + 1:
                assert frozenset((here, new)) in eidx, "the walker jumped across a tie that does not exist"
                hot = eidx[frozenset((here, new))]
            else:
                hot = None
            came, here = here, new
        prev_step = steps
        ns = [{"f": "src" if i == here else "reach" if v[i] else "base",
               "r": round(11 + 3.2 * math.sqrt(v[i]), 1) if v[i] else 13, "l": str(v[i]) if v[i] else "",
               "ring": 1 if i == here else 0} for i in range(n)]
        es = [{"k": "hot" if hot == j else "base", "w": 3.4 if hot == j else 1.6} for j in range(len(edges))]
        if steps == 0:
            text = f"{names[start]} starts here, at the far end of the chain. Each number is how many times the walker has stood on that person."
        elif steps <= 9:
            text = f"Step {steps}: from {names[came]}, one friend is picked at random: {names[here]}."
        elif k == len(frames) - 1:
            order = sorted(range(n), key=lambda i: -v[i])
            hi, lo = order[0], order[-1]
            many = lambda d: f"{d} friends" if d > 1 else "1 friend"
            text = (f"After {steps} steps: {names[hi]}, with {many(deg[hi])}, has been visited {v[hi]} times, and "
                    f"{names[lo]}, with {many(deg[lo])}, {v[lo]}. More friends, more visits.")
        else:
            text = f"Skipping ahead to step {steps}: the walker is at {names[here]}, and the counts keep climbing."
        states.append((ns, es, list(v), text))
    cap = int(math.ceil(top_max / 5.0) * 5)
    scene = {"id": "walk-visits", "w": 640, "h": 360, "ms": 900, "nodes": nodes, "edges": edges,
             "panel": {"kind": "bars", "x": 452, "y": 56, "w": 172, "h": 268, "labels": names, "max": cap,
                       "title": "Times visited"},
             "states": states, "still": [0, 4, 13, len(frames) - 1]}
    labels = ["Start", "After 4 steps", "After 20 steps", "After 120 steps"]
    still = lean_filmstrip(scene, labels, "A random walk on the friendship network",
                        "Four copies of the ten-person friendship network with a walker and visit counts.",
                        show=lambda i, m: f"{names[i]} {m[i]}")
    return scene, still


BUILDERS = {"walk-visits": build}

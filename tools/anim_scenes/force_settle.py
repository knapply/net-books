"""Chapter 5: a force-directed layout settling, and the stress layout doing the same (karate club).

Frames are complete engine runs with a growing budget (data/anim/force-settle.frames.json, stress-settle.frames.json).
Two things are done to the engine's coordinates, and nothing else: each run is turned (rotation or reflection) and
shifted to sit over the last run, because the engine orients every layout on its own; and all runs are scaled by one
common factor to fit the picture. The stress number in the side panel is the chapter's scale-free stress of each frame.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

FACTION = Path(__file__).resolve().parent.parent.parent / "books" / "sna" / "data" / "karate" / "nodes.csv"


def procrustes(P, Q):
    """Rotate or reflect, and shift, the points P to sit as close as possible to Q (no scaling)."""
    n = len(P)
    pc = (sum(p[0] for p in P) / n, sum(p[1] for p in P) / n)
    qc = (sum(q[0] for q in Q) / n, sum(q[1] for q in Q) / n)
    best = None
    for flip in (1, -1):
        A = [((p[0] - pc[0]) * flip, p[1] - pc[1]) for p in P]
        B = [(q[0] - qc[0], q[1] - qc[1]) for q in Q]
        c = sum(a[0] * b[0] + a[1] * b[1] for a, b in zip(A, B))
        s = sum(a[0] * b[1] - a[1] * b[0] for a, b in zip(A, B))
        th = math.atan2(s, c)
        ct, st = math.cos(th), math.sin(th)
        R = [(a[0] * ct - a[1] * st + qc[0], a[0] * st + a[1] * ct + qc[1]) for a in A]
        err = sum((r[0] - q[0]) ** 2 + (r[1] - q[1]) ** 2 for r, q in zip(R, Q))
        if best is None or err < best[0]:
            best = (err, R)
    return best[1]


def scale_free_stress(pts, dist):
    """The chapter's score: mean of ((s* p - d) / d)^2 over pairs, s* the best common factor."""
    n = len(pts)
    ratios, pairs = [], []
    for i in range(n):
        for j in range(i + 1, n):
            p = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            ratios.append(p / dist[i][j])
            pairs.append((p, dist[i][j]))
    s = sum(ratios) / sum(r * r for r in ratios)
    return sum(((s * p - d) / d) ** 2 for p, d in pairs) / len(pairs)


def factions():
    rows = FACTION.read_text().strip().splitlines()[1:]
    return [r.split(",")[1] for r in rows]


from ._strip import lean_filmstrip  # noqa: E402


def build_layout(aid, budget_key, words):
    import make_anim as M
    from fig_layout import distances, fit
    M.NODE.setdefault("a", ("#0072B2", "#004f7c"))
    M.NODE.setdefault("b", ("#E69F00", "#b87f00"))
    raw = M.load(aid)
    n, edges = raw["n"], raw["edges"]
    dist = distances(n, [tuple(e) for e in edges])
    runs = [list(zip(f["x"], f["y"])) for f in raw["frames"]]
    final = runs[-1]
    aligned = [procrustes(r, final) for r in runs]
    # one common scale and offset for every frame: fit the union of all points into the picture box
    allp = [p for r in aligned for p in r]
    fitted = fit(allp, 24, 40, 400, 300)
    pos = [fitted[k * n:(k + 1) * n] for k in range(len(aligned))]
    stress = [scale_free_stress(r, dist) for r in runs]
    side = ["a" if f == "Mr. Hi" else "b" for f in factions()]
    budgets = [f[budget_key] for f in raw["frames"]]
    last = len(budgets) - 1
    states = []
    for k, b in enumerate(budgets):
        ns = [{"f": side[i], "r": 8, "l": "", "ring": 0} for i in range(n)]
        es = [{"k": "base", "w": 1.0} for _ in edges]
        states.append((ns, es, [round(stress[k], 3)], words(k, b, stress, last), pos[k]))
    scene = {"id": aid, "w": 640, "h": 360, "ms": 1000, "nodes": [("", x, y) for x, y in pos[-1]], "edges": edges,
             "panel": {"kind": "bars", "x": 450, "y": 120, "w": 175, "h": 24, "labels": ["Stress"], "max": 0.3,
                       "title": "Scale-free stress"},
             "states": states, "still": [0, 3, 6, last]}
    return scene, raw, stress


def strip(scene, stress, labels, title, desc):
    import make_anim as M
    return lean_filmstrip(scene, labels, title, desc, show=lambda i, m: "")


def build_force():
    def words(k, b, stress, last):
        s = f"{stress[k]:.2f}"
        if k == 0:
            return f"One round of pushing and pulling from the random start. Hardly anyone has moved, and the stress is {s}."
        if k == last:
            return (f"{b} rounds, the setting behind the stored force layout. Stress {s}. "
                    f"The number stopped improving long ago, at around 70 rounds.")
        if k < 5:
            return f"{b} rounds. Friends are drifting together while everyone pushes everyone else away. Stress {s}."
        if k < 9:
            return f"{b} rounds. The tangle is loosening. Stress {s}."
        return f"{b} rounds. Only small adjustments now. Stress {s}."
    scene, raw, stress = build_layout("force-settle", "iterations", words)
    assert abs(stress[-1] - 0.089) < 0.001, "the final force layout should score what the chapter's table says"
    still = strip(scene, stress, ["1 round", "6 rounds", "16 rounds", "500 rounds"], "A force layout settling",
                  "Four copies of the karate club drawn by a force layout run for 1, 6, 16 and 500 rounds, blue circles for Mr. Hi's members and orange for the officer's.")
    return scene, still


BUILDERS = {"force-settle": build_force}

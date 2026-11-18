"""Chapter 21: one simulation chain on the karate club, one accepted tie change at a time."""
import json

ID = "ergm-steps"


def build(M):
    M.NODE.setdefault("a", (M.BLUE, "#004f7c"))
    M.NODE.setdefault("b", (M.ORANGE, "#b87f00"))
    raw = json.loads((M.DATA / f"{ID}.frames.json").read_text())
    obs, side, steps = [tuple(e) for e in raw["edges"]], raw["side"], raw["steps"]
    n = len(side)
    ever = sorted(set(obs) | {(t[0], t[1]) for t in (s["toggle"] for s in steps) if t})
    idx = {e: i for i, e in enumerate(ever)}
    base = M.layout([""] * n, [list(e) for e in obs])
    base[0] = ("Mr. Hi",) + base[0][1:]
    base[33] = ("Officer",) + base[33][1:]
    present = set(obs)
    states = []
    for k, s in enumerate(steps):
        t = s["toggle"]
        edge_now = None
        if t:
            edge_now = (t[0], t[1])
            (present.add if t[2] == "added" else present.discard)(edge_now)
        es = []
        for e in ever:
            if e == edge_now:
                es.append({"k": "hot" if t[2] == "added" else "reach", "w": 3.6})
            elif e in present:
                es.append({"k": "base", "w": 1.4})
            else:
                es.append({"k": "dim", "w": 1.0})
        ns = [{"f": "a" if side[i] == 0 else "b", "r": 7, "l": "", "ring": 1 if edge_now and i in edge_now else 0}
              for i in range(n)]
        edges_n, same, _, tri = s["stats"]
        assert len(present) == edges_n, "tie count disagrees with the engine's running statistic"
        prev = steps[k - 1]["stats"] if k else None
        if k == 0:
            text = (f"The real club: {edges_n:.0f} ties and {tri:.0f} triangles. Blue dots took Mr. Hi's side, orange dots the "
                    "officer's. The model now proposes changing one pair at a time, and accepts some proposals and refuses others.")
        else:
            what = (f"the tie between members {t[0] + 1} and {t[1] + 1} appears" if t[2] == "added"
                    else f"the tie between members {t[0] + 1} and {t[1] + 1} disappears")
            skipped = s["proposals"] - steps[k - 1]["proposals"] - 1
            tail = "" if not skipped else f" ({skipped} proposal{'s' if skipped > 1 else ''} before it " + ("was" if skipped == 1 else "were") + " refused)"
            d = int(tri - prev[3])
            tri_txt = "triangles unchanged" if d == 0 else f"triangles {'up' if d > 0 else 'down'} by {abs(d)}"
            text = f"Proposal {s['proposals']} is accepted: {what}{tail}. Ties {edges_n:.0f}, triangles {tri:.0f}{'' if d == 0 else ' (' + tri_txt.replace('triangles ', '') + ')'}."
        states.append((ns, es, [edges_n, same, tri], text))
    last = len(steps) - 1
    scene = {"id": ID, "w": 640, "h": 360, "ms": 900, "nodes": base, "edges": [list(e) for e in ever], "compact": True,
             "panel": {"kind": "bars", "x": 452, "y": 74, "w": 172, "h": 130, "labels": ["Ties", "Same side", "Triangles"],
                       "max": 100, "title": "Running counts"},
             "states": states, "still": [0, last // 3, 2 * last // 3, last]}
    pick = scene["still"]
    st = lambda i: f"{states[i][2][0]:.0f} ties, {states[i][2][2]:.0f} triangles"  # noqa: E731
    labels = [f"Start: the real club, {st(0)}"] + [f"After {i} changes: {st(i)}" for i in pick[1:]]
    still = M.filmstrip(
        scene, labels, "A simulated chain starting at the karate club",
        "Four copies of the karate club network, blue dots for one side and orange for the other, as ties come and go.",
        show=lambda i, m: scene["nodes"][i][0])
    return scene, still


def _builder():
    import make_anim
    return build(make_anim)


BUILDERS = {ID: _builder}

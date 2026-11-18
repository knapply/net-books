"""Chapter 23: one period of the actor-oriented model on the ten-person office, one change opportunity at a time."""
import json

ID = "saom-steps"


def build(M):
    raw = json.loads((M.DATA / f"{ID}.frames.json").read_text())
    names, steps = raw["names"], raw["steps"]
    n = len(names)
    arcs = [{tuple(e) for e in s["edges"]} for s in steps]
    start = {tuple(e) for e in raw["edges"]}
    assert arcs[0] == start and steps[0]["ministeps"] == 0, "row 0 must be the real network"
    ever = sorted(set().union(*arcs))
    last = len(steps) - 1
    total = steps[-1]["ministeps"]
    und = [list(e) for e in ever]
    pts = M.fit(M.stress_layout(n, [tuple(e) for e in und], seed=3), 24, 30, 400, 255)
    base = [(nm, p[0], p[1]) for nm, p in zip(names, pts)]
    states = []
    for k, s in enumerate(steps):
        cur, prev = arcs[k], arcs[max(k - 1, 0)]
        gone, new = sorted(prev - cur), sorted(cur - prev)
        count = s["ministeps"]
        gap = count - steps[k - 1]["ministeps"] if k else 0
        actor = None
        if gap == 1 and len(gone) + len(new) == 1:
            actor = (gone or new)[0][0]
        es = []
        for e in ever:
            if e not in cur:
                es.append({"k": "reach" if e in gone else "dim", "w": 3.4 if e in gone else 1.0})
            else:
                es.append({"k": "hot" if e in new else "base", "w": 3.4 if e in new else 2.0})
        ns = [{"f": "src" if i == actor else "base", "r": 19 if i == actor else 16, "l": "", "ring": 1 if i == actor else 0}
              for i in range(n)]
        mutual = int(s["reciprocity"]) // 2
        if k == 0:
            text = ("The office before the period starts: an arrow from A to B means A asks B for advice. "
                    "Each step is one chance for someone to change one of their own ties.")
        elif gap == 1 and actor is not None:
            a, b = (gone or new)[0]
            verb = f"drops the tie to {names[b]}" if gone else f"starts asking {names[b]}"
            text = f"Chance {count}: {names[a]} {verb}."
        elif gap == 1:
            text = f"Chance {count}: somebody had a chance and kept everything as it was."
        else:
            text = f"Chances {count - gap + 1} to {count}: {len(gone)} ties dropped and {len(new)} started."
        if k == last:
            text += f" That is the end of the period: {s['ties']:.0f} ties are left, {int(s['changed'])} of them different from the start."
        m = [f"Chance {count} of {total} ·", f"Ties {s['ties']:.0f} ·", f"Mutual pairs {mutual}"]
        states.append((ns, es, m, text))
    scene = {"id": ID, "w": 640, "h": 360, "ms": 800, "nodes": base, "edges": [list(e) for e in ever], "dir": True,
             "panel": {"kind": "text", "x": 24, "y": 330}, "states": states,
             "still": [0, last // 3, 2 * last // 3, last]}
    pick = scene["still"]
    labels = ["Start", f"After {steps[pick[1]]['ministeps']} chances", f"After {steps[pick[2]]['ministeps']} chances",
              f"End: {steps[pick[3]]['ministeps']} chances"]
    still = M.filmstrip(
        scene, labels, "One period of the office advice network",
        "Four copies of the ten-person office advice network, with arrows drawn from the person who asks to the person asked.")
    return scene, still


def _builder():
    import make_anim
    return build(make_anim)


BUILDERS = {ID: _builder}

"""Chapter 22: the karate club's latent-space map settling while it is fitted."""
import json
import math

ID = "latent-settle"


def align(pts, ref):
    """Turn (and flip, if that fits better) pts to sit on ref. Distances do not change, only the picture's orientation."""
    cx = lambda p: (sum(x for x, _ in p) / len(p), sum(y for _, y in p) / len(p))  # noqa: E731
    (px, py), (rx, ry) = cx(pts), cx(ref)
    best = None
    for flip in (1, -1):
        p = [(x - px, flip * (y - py)) for x, y in pts]
        r = [(x - rx, y - ry) for x, y in ref]
        a = sum(u[0] * v[0] + u[1] * v[1] for u, v in zip(p, r))
        b = sum(u[0] * v[1] - u[1] * v[0] for u, v in zip(p, r))
        th = math.atan2(b, a)
        c, s = math.cos(th), math.sin(th)
        q = [(x * c - y * s, x * s + y * c) for x, y in p]
        err = sum((u[0] - v[0]) ** 2 + (u[1] - v[1]) ** 2 for u, v in zip(q, r))
        if best is None or err < best[0]:
            best = (err, q)
    return best[1]


def build(M):
    M.NODE.setdefault("a", (M.BLUE, "#004f7c"))
    M.NODE.setdefault("b", (M.ORANGE, "#b87f00"))
    raw = json.loads((M.DATA / f"{ID}.frames.json").read_text())
    edges, side, steps = raw["edges"], raw["side"], raw["steps"]
    n = len(side)
    pos = [[(s["positions"][2 * i], s["positions"][2 * i + 1]) for i in range(n)] for s in steps]
    final = steps[-1]
    assert final["converged"], "the last call should be the converged fit"
    pos = [align(p, pos[-1]) for p in pos]
    xs = [x for p in pos for x, _ in p]
    ys = [y for p in pos for _, y in p]
    sc = min(400 / (max(xs) - min(xs)), 255 / (max(ys) - min(ys)))
    place = [[(24 + (x - min(xs)) * sc, 30 + (y - min(ys)) * sc) for x, y in p] for p in pos]
    tied = {tuple(e) for e in edges}
    far = lambda p, want: (lambda v: sum(v) / len(v))([  # noqa: E731
        math.dist(p[a], p[b]) for a in range(n) for b in range(a + 1, n) if ((a, b) in tied) == want])
    base = [("Mr. Hi" if i == 0 else "Officer" if i == 33 else "",) + place[0][i] for i in range(n)]
    states = []
    for k, s in enumerate(steps):
        ns = [{"f": "a" if side[i] == 0 else "b", "r": 7, "l": "", "ring": 0} for i in range(n)]
        es = [{"k": "base", "w": 1.0} for _ in edges]
        dt, dn = far(pos[k], True), far(pos[k], False)
        it = s["iterations"]
        score = s["loglik"]
        if k == 0:
            text = (f"Before any fitting: members are placed by how many steps apart they are in the club. "
                    f"The score is {score:.1f}; closer to zero is better. Friends average {dt:.1f} apart, everyone else {dn:.1f}.")
        elif k == len(steps) - 1:
            text = (f"Settled after {it} steps: the score stops improving at {score:.2f}. Friends average {dt:.1f} apart, "
                    f"everyone else {dn:.1f}. The two sides sit at opposite ends.")
        else:
            text = f"After {it} step{'s' if it > 1 else ''}: score {score:.1f}. Friends average {dt:.1f} apart, everyone else {dn:.1f}."
        states.append((ns, es, [f"Step {it} ·", f"score {score:.1f}"], text, place[k]))
    scene = {"id": ID, "w": 640, "h": 360, "ms": 900, "nodes": base, "edges": edges, "compact": True,
             "panel": {"kind": "text", "x": 24, "y": 330}, "states": states, "still": [0, 5, 9, len(steps) - 1]}
    pick = scene["still"]
    labels = ["Start: path distances"] + [f"After {steps[i]['iterations']} steps" for i in pick[1:3]] + ["Settled"]
    still = M.filmstrip(
        scene, labels, "A map of the karate club settling",
        "Four copies of the karate club, blue dots for one side and orange for the other, drawn at four stages of the fit.",
        show=lambda i, m: scene["nodes"][i][0])
    return scene, still


def _builder():
    import make_anim
    return build(make_anim)


BUILDERS = {ID: _builder}

"""Chapter 14: a two-mode projection forming, one event at a time (southern women).

Frame k is the engine's projection onto the women (bipartite::project) of the attendance with only the first k events kept
(data/anim/projection-forms.frames.json).
"""
import math

SHORT = ["Evelyn", "Laura", "Theresa", "Brenda", "Charlotte", "Frances", "Eleanor", "Pearl", "Ruth",
         "Verne", "Myra", "Katherine", "Sylvia", "Nora", "Helen", "Dorothy", "Olive", "Flora"]


from ._strip import lean_filmstrip  # noqa: E402


def build():
    import make_anim as M
    raw = M.load("projection-forms")
    n = 18
    frames = raw["frames"]
    pairs_of = lambda f: {(a, b): w for a, b, w in zip(f["from"], f["to"], f["weights"])}
    maps = [pairs_of(f) for f in frames]
    # the engine's projection must agree with a plain count of shared events
    attend = {k: set() for k in range(14)}
    for w, e in raw["attend"]:
        attend[e].add(w)
    for k, f in enumerate(frames, start=1):
        want = {}
        for e in range(k):
            for a in attend[e]:
                for b in attend[e]:
                    if a < b:
                        want[(a, b)] = want.get((a, b), 0) + 1
        assert want == maps[k - 1], f"projection after {k} events disagrees with a direct count"
    final = sorted(maps[-1])
    index = {p: i for i, p in enumerate(final)}
    cx, cy, rad = 215, 190, 135
    nodes = []
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * i / n
        nodes.append((SHORT[i], cx + rad * math.cos(a), cy + rad * math.sin(a)))
    states = [([dict(M.DEFAULT_NODE, r=11) for _ in range(n)], [{"k": "base", "w": 0} for _ in final], [0],
               "Eighteen women and nothing between them yet. We tie two women whenever they were at the same event, "
               "and we add the events one at a time.")]
    prev = {}
    for k, cur in enumerate(maps, start=1):
        here = sorted(attend[k - 1])
        a = len(here)
        ns = [{"f": "src" if i in here else "base", "r": 14 if i in here else 11, "l": "", "ring": 0} for i in range(n)]
        es = []
        for p in final:
            if p in cur and p not in prev:
                es.append({"k": "hot", "w": 2.2})
            elif p in cur:
                es.append({"k": "reach", "w": 0.9})
            else:
                es.append({"k": "base", "w": 0})
        new = len(cur) - len(prev)
        pairs = a * (a - 1) // 2
        if new == pairs:
            text = f"Event {k}: {a} women were there, so {pairs} pairs of women get tied."
        elif new == 0:
            text = f"Event {k}: {a} women were there, but every one of their {pairs} pairs was tied already. Nothing new."
        else:
            text = f"Event {k}: {a} women were there, which is {pairs} pairs. {new} are tied for the first time; the other {pairs - new} already shared an earlier event."
        if k == 8:
            text = f"Event 8, the biggest: {a} women, so {pairs} pairs, and {new} of them are new ties. The picture fills in fast."
        if k == 14:
            text = (f"Event {k}: {a} women, nothing new. In the end {len(cur)} of the 153 possible pairs are tied, "
                    f"just from turning up at the same events.")
        states.append((ns, es, [len(cur)], text))
        prev = cur
    scene = {"id": "projection-forms", "w": 640, "h": 380, "ms": 1100, "nodes": nodes, "edges": [list(p) for p in final],
             "panel": {"kind": "bars", "x": 450, "y": 130, "w": 175, "h": 24, "labels": ["Tied"], "max": 153,
                       "title": "Pairs tied so far (of 153)"},
             "states": states, "still": [0, 3, 8, 14]}
    labels = ["Before any event", "After event 3", "After event 8", "After all 14"]
    still = lean_filmstrip(scene, labels, "A projection forming, one event at a time",
                        "Four copies of the ring of 18 southern women, showing ties appearing as events are added.",
                        show=lambda i, m: "")
    return scene, still


BUILDERS = {"projection-forms": build}

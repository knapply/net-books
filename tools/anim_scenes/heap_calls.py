"""A heap of ten people keyed by their distance from Jo, filled and emptied (algorithms book, chapter 3).
The keys are the engine's breadth-first distances; the scene builds a heap by the textbook rule and asserts that
taking the smallest ten times gives exactly the sorted engine distances."""
LEVEL_Y = 80
DY = 72


def _slot_xy(i, x0=40, w=560):
    lvl = (i + 1).bit_length() - 1
    j = i + 1 - 2 ** lvl
    return x0 + (j + 0.5) / 2 ** lvl * w, LEVEL_Y + lvl * DY


def build():
    import make_anim as M

    raw = M.load("heap-calls", "algorithms")
    names, dist = raw["names"], raw["distances"]
    n = len(names)
    assert n == 10
    heap = []  # (key, person)
    nodes0 = [(str(i), *_slot_xy(i)) for i in range(n)]
    edges = [[(i - 1) // 2, i] for i in range(1, n)]
    states = []

    def snap(marks, text, tail=None):
        k = len(heap)
        ns, es = [], []
        for i in range(n):
            if i < k:
                role = marks.get(i, "base")
                ns.append({"f": role, "r": 17, "l": str(heap[i][0]), "ring": 1 if role in ("src", "hot") else 0})
            else:
                ns.append({"f": "dim", "r": 5, "l": "", "ring": 0})
        for e, (p, c) in zip(range(len(edges)), edges):
            if c >= k:
                es.append({"k": "dim", "w": 0.4})
            elif marks.get(c) in ("hot", "src") and marks.get(p) in ("reach", "hot"):
                es.append({"k": "hot", "w": 3.4})
            else:
                es.append({"k": "base", "w": 1.8})
        keys = " ".join(str(h[0]) for h in heap) if heap else "(empty)"
        states.append((ns, es, ["List in memory:", keys] + ([" " + tail] if tail else []), text))

    snap({}, "An empty heap. The number in each circle is a person's distance from Jo. We will add people one at a time, closest-first wins the top.")
    for p in range(n):
        key = dist[p]
        heap.append((key, p))
        i = len(heap) - 1
        snap({i: "src"}, f"{names[p]} (distance {key}) joins at the bottom, in the next free slot.")
        while i > 0 and heap[(i - 1) // 2][0] > heap[i][0]:
            par = (i - 1) // 2
            heap[par], heap[i] = heap[i], heap[par]
            snap({par: "hot", i: "reach"}, f"{names[heap[par][1]]} ({heap[par][0]}) is smaller than the one above, so they swap.")
            i = par
    assert all(heap[(i - 1) // 2][0] <= heap[i][0] for i in range(1, n)), "not a heap"
    snap({0: "src"}, f"All ten are in. The smallest, {names[heap[0][1]]} at {heap[0][0]}, is on top without any searching.")
    popped = []
    detailed = 4
    for t in range(n):
        top = heap[0]
        popped.append(top[0])
        if t < detailed:
            snap({0: "src"}, f"Take the top: {names[top[1]]} ({top[0]}) leaves first.")
        last = heap.pop()
        if heap:
            heap[0] = last
            if t < detailed:
                snap({0: "hot"}, f"The last person, {names[last[1]]} ({last[0]}), moves to the top to fill the hole.")
            i = 0
            while True:
                kids = [c for c in (2 * i + 1, 2 * i + 2) if c < len(heap)]
                if not kids:
                    break
                c = min(kids, key=lambda j: heap[j][0])
                if heap[c][0] >= heap[i][0]:
                    break
                heap[i], heap[c] = heap[c], heap[i]
                if t < detailed:
                    snap({i: "reach", c: "hot"}, f"{names[heap[i][1]]} ({heap[i][0]}) is the smaller child, so it moves up and {names[heap[c][1]]} sinks.")
                i = c
            if t < detailed:
                snap({}, f"The rule holds again, and the new smallest ({heap[0][0]}) is on top.")
    assert popped == sorted(dist), "taking the smallest ten times must give the sorted engine distances"
    heap.clear()
    snap({}, "The same repair happens for every person. Taken one by one, they come out in order of distance: " + ", ".join(map(str, popped)) + ".",
         tail="Out: " + " ".join(map(str, popped)))
    scene = {"id": "heap-calls", "book": "algorithms", "w": 640, "h": 360, "ms": 1200, "nodes": nodes0, "edges": edges,
             "panel": {"kind": "text", "x": 24, "y": 8, "title": ""}, "states": states, "still": []}
    first_pop = next(i for i, s in enumerate(states) if "leaves first" in s[3])
    full = next(i for i, s in enumerate(states) if "All ten are in" in s[3])
    scene["still"] = [1, 5, full, first_pop + 3]
    labels = ["First person joins", "Floating up", "All ten in", "Taking the smallest"]
    still = M.filmstrip(scene, labels, "A heap of ten people", "Four copies of a ten-slot tree showing a person joining, floating up, the full heap and the repair after the top leaves.")
    return scene, still


BUILDERS = {"heap-calls": build}

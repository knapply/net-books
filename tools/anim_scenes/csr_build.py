"""Five people stored as compressed sparse rows, built in three passes (algorithms book, chapter 1).
The passes are the textbook rule (count, add up, fill); the scene asserts the result equals the engine's own rows."""
FIVE_POS = [(0, 70), (95, 70), (175, 10), (175, 130), (270, 130)]


def build():
    import make_anim as M

    raw = M.load("csr-build", "algorithms")
    names, ties, off_e, tgt_e, deg_e = raw["names"], [tuple(e) for e in raw["edges"]], raw["offsets"], raw["targets"], raw["degrees"]
    n = len(names)
    adj = [[] for _ in range(n)]
    for a, b in ties:
        adj[a].append(b)
        adj[b].append(a)
    adj = [sorted(x) for x in adj]
    # pass 1: count, tie by tie
    counts_seq, c = [], [0] * n
    for a, b in ties:
        c[a] += 1
        c[b] += 1
        counts_seq.append(list(c))
    # pass 2: running totals
    offsets = [0]
    for i in range(n):
        offsets.append(offsets[-1] + c[i])
    # pass 3: fill person by person
    targets, fill_seq = [], []
    for i in range(n):
        targets += adj[i]
        fill_seq.append(list(targets))
    assert c == deg_e, "counted degrees disagree with the engine"
    assert offsets == off_e, "offsets disagree with the engine's rows"
    assert targets == tgt_e, "targets disagree with the engine's rows"
    nodes0 = [(names[i], 90 + FIVE_POS[i][0] * 1.7, 110 + FIVE_POS[i][1] * 1.5) for i in range(n)]
    E = lambda hot=(): [{"k": "hot" if k in hot else "base", "w": 3.4 if k in hot else 1.8} for k in range(len(ties))]
    states = []
    states.append(([dict(M.DEFAULT_NODE, r=18) for _ in range(n)], E(), ["The five ties as pairs:", "0-1  1-2  1-3  2-3  3-4"],
                   "Five people and five ties. We will store them in two flat lists. First pass: count each person's friends."))
    for k, (a, b) in enumerate(ties):
        ns = [{"f": "src" if i in (a, b) else "base", "r": 18, "l": str(counts_seq[k][i]), "ring": 0} for i in range(n)]
        states.append((ns, E({k}), ["Friends counted:", " ".join(map(str, counts_seq[k]))],
                       f"{names[a]} and {names[b]} are tied: add 1 to each of their counts."))
    ns = [{"f": "reach", "r": 18, "l": str(c[i]), "ring": 0} for i in range(n)]
    states.append((ns, E(), ["Counts:", " ".join(map(str, c)), " Running totals (offsets):", " ".join(map(str, offsets))],
                   "Second pass: add the counts up as you go. Each running total says where that person's block of friends begins."))
    for i in range(n):
        ns = [{"f": "src" if j == i else "reach" if j in adj[i] else "base", "r": 18, "l": str(offsets[j]), "ring": 0} for j in range(n)]
        hot = {k for k, (a, b) in enumerate(ties) if i in (a, b)}
        filled = fill_seq[i] + ["_"] * (len(tgt_e) - len(fill_seq[i]))
        who = ", ".join(names[j] for j in adj[i])
        states.append((ns, E(hot), ["targets:", " ".join(map(str, filled))],
                       f"Third pass: write {names[i]}'s friends ({who}) into slots {offsets[i]} to {offsets[i + 1] - 1}."))
    d = 3
    ns = [{"f": "src" if j == d else "reach" if j in adj[d] else "base", "r": 18, "l": str(offsets[j]), "ring": 1 if j == d else 0} for j in range(n)]
    states.append((ns, E(), ["offsets:", " ".join(map(str, offsets)), " targets:", " ".join(map(str, targets))],
                   f"Done. To find {names[d]}'s friends, read targets from slot {offsets[d]} up to {offsets[d + 1] - 1}: that's {len(adj[d])} friends, no searching."))
    last = len(states) - 1
    scene = {"id": "csr-build", "book": "algorithms", "w": 640, "h": 360, "ms": 1500, "nodes": nodes0, "edges": [list(e) for e in ties],
             "panel": {"kind": "text", "x": 24, "y": 8, "title": ""}, "states": states, "still": [0, 3, 7, last]}
    labels = ["Start", "Pass 1: counting", "Pass 3: filling", "Done"]
    still = M.filmstrip(scene, labels, "Building CSR for five people",
                        "Four copies of the five-person network showing the counting pass, the filling pass and the finished rows.")
    return scene, still


BUILDERS = {"csr-build": build}

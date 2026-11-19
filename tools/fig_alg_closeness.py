"""Figures for the algorithms book, chapter 19 (closeness and harmonic centrality on millions of ties).

Standard library only. Every number drawn is computed here from the small networks below by plain breadth-first
search, so the pictures cannot drift from the chapter.
"""
from fig_alg_betweenness import EDGES, NAMES, PALE, adjacency
from fig_layout import fit, stress_layout
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, PURPLE, RED, SKY, Canvas

GRAY = "#9ca3af"
LEVEL = [ORANGE, SKY, BLUE, PURPLE, GREEN]


def bfs(adj, s):
    dist = [-1] * len(adj)
    dist[s] = 0
    queue = [s]
    for u in queue:
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


def kite_pos(x0, y0, w, h):
    return fit(stress_layout(10, EDGES, seed=3), x0, y0, w, h)


def level_counts(dist):
    out = [0] * (max(dist) + 1)
    for d in dist:
        if d > 0:
            out[d] += 1
    return out


# ---------------------------------------------------------------- 1. one search per person walks the same ties again
def repeat_searches():
    adj = adjacency(10, EDGES)
    c = Canvas(760, 430, "One search per person",
               "Four copies of the ten-person network, each colored by distance from a different starting person.")
    c.text(380, 28, "Four of the ten searches: every one walks every tie", size=15, weight="700")
    data = {}
    for k, s in enumerate([0, 3, 7, 9]):
        ox, oy = 20 + (k % 2) * 370, 50 + (k // 2) * 190
        c.rect(ox, oy, 350, 175, fill="none", stroke=FAINT, sw=1, rx=8)
        dist = bfs(adj, s)
        data[NAMES[s]] = dist
        pos = kite_pos(ox + 30, oy + 30, 220, 130)
        for a, b in EDGES:
            c.edge(pos[a], pos[b], ra=0, rb=0, color=ORANGE if abs(dist[a] - dist[b]) == 1 else GRAY, width=1.6)
        for i in range(10):
            col = LEVEL[min(dist[i], 4)]
            c.node(*pos[i], str(dist[i]), r=11, fill=col if i == s else PAPER, stroke=col, size=10, sw=2.2)
        c.text(ox + 300, oy + 28, f"from {NAMES[s]}", size=13, weight="700")
        c.text(ox + 300, oy + 48, f"sum {sum(dist)}", size=12, fill=MUTED)
    meta = dict(book="algorithms", chapter=19,
                caption="Closeness needs every person's distances to everyone, and the plain way runs one full search per person. Each search here (from Ana, Dev, Hana and Jo) touches all ten people and all eighteen ties; ten people means ten such sweeps, a million people a million.",
                alt=("Four small copies of the ten-person network in a two by two grid. In each, the numbers in the dots are distances from one starting person: Ana, Dev, Hana and Jo. "
                     f"The distance sums are {sum(data['Ana'])}, {sum(data['Dev'])}, {sum(data['Hana'])} and {sum(data['Jo'])}. Orange ties lead one step farther from the start."),
                data={"distances": data})
    return c, meta


# ---------------------------------------------------------------- 2. a word of lights, one per search
def bits_row(c, x, y, bits, label, color, cell=34):
    c.text(x - 12, y + cell / 2 + 5, label, size=13, anchor="end", weight="600")
    for i, b in enumerate(bits):
        c.rect(x + i * cell, y, cell - 4, cell - 4, fill=color if b else PAPER, stroke=color if b else FAINT, sw=1.5, rx=4)
        c.text(x + i * cell + (cell - 4) / 2, y + cell / 2 + 3, str(b), size=13, weight="700", fill=PAPER if b else MUTED)


def word_lights():
    adj = adjacency(10, EDGES)
    dists = [bfs(adj, s) for s in range(8)]  # searches from Ana to Hana, one bit each
    gus, level = 6, 2
    arrived = [1 if dists[s][gus] <= level and any(dists[s][u] == level - 1 for u in adj[gus]) else 0 for s in range(8)]
    seen = [1 if dists[s][gus] <= level - 1 else 0 for s in range(8)]
    new = [a & (1 - b) for a, b in zip(arrived, seen)]
    assert new == [1 if dists[s][gus] == level else 0 for s in range(8)]
    c = Canvas(760, 380, "Eight searches in one word",
               "Three rows of eight boxes for Gus at step two: who arrived, who had already been there, and who is new.")
    c.text(380, 30, "Gus's word at step 2: one box per search", size=15, weight="700")
    x0 = 230
    for i in range(8):
        c.text(x0 + i * 34 + 15, 64, NAMES[i], size=11, fill=MUTED)
    bits_row(c, x0, 76, arrived, "came from a neighbor", SKY)
    bits_row(c, x0, 136, seen, "already reached", GRAY)
    c.text(x0 + 4 * 34, 128, "and not", size=12, fill=MUTED, italic=True)
    bits_row(c, x0, 196, new, "new at step 2", ORANGE)
    c.text(x0 + 4 * 34, 188, "gives", size=12, fill=MUTED, italic=True)
    c.lines(40, 268, [
        "Each box is one bit of a machine word, one bit per search.",
        "Top row: OR of the words of Gus's neighbors that were on the edge of a search at step 1.",
        "Middle row: the searches that had already reached Gus.  Bottom row: top AND NOT middle.",
        "Two word operations update all eight searches at once.",
    ], size=13, gap=1.5, fill=INK)
    meta = dict(book="algorithms", chapter=19,
                caption="Eight searches share one word. Each box is one bit; bit k says something about the search from person k. Two quick operations on whole words, an OR to collect arrivals and an AND NOT to drop repeats, do the work of eight separate searches at once.",
                alt=("Three rows of eight boxes labelled Ana to Hana. Top row, came from a neighbor: " + " ".join(map(str, arrived)) +
                     ". Middle row, already reached: " + " ".join(map(str, seen)) + ". Bottom row, new at step 2: " + " ".join(map(str, new)) +
                     ". Shaded boxes are ones, white boxes zeros."),
                data={"person": "Gus", "step": level, "arrived": arrived, "already": seen, "new": new, "searches": NAMES[:8]})
    return c, meta


# ---------------------------------------------------------------- 3. look-alike people collapse
def twins():
    c = Canvas(760, 340, "Collapsing look-alike people",
               "Before and after: two interns with exactly the same contacts become one dot that counts twice.")
    left = {"Kai": (80, 110), "Lea": (80, 230), "Ana": (260, 70), "Ben": (260, 170), "Cleo": (260, 270), "Dev": (360, 170)}
    ties = [("Kai", "Ana"), ("Kai", "Ben"), ("Kai", "Cleo"), ("Lea", "Ana"), ("Lea", "Ben"), ("Lea", "Cleo"),
            ("Ana", "Dev"), ("Ben", "Dev"), ("Cleo", "Dev")]
    c.text(200, 30, "Before: Kai and Lea know the same people", size=14, weight="700")
    for a, b in ties:
        c.edge(left[a], left[b], ra=20, rb=20, color=GRAY, width=1.8)
    for k, p in left.items():
        tw = k in ("Kai", "Lea")
        c.node(*p, k, r=20, fill="#fff4dc" if tw else PALE, stroke=ORANGE if tw else BLUE, size=11)
    c.arrow((420, 170), (470, 170), color=MUTED, width=2.5)
    right = {"Kai+Lea": (540, 170), "Ana": (650, 70), "Ben": (650, 170), "Cleo": (650, 270), "Dev": (730, 170)}
    c.text(620, 30, "After: one dot, weight 2", size=14, weight="700")
    for a, b in [("Kai+Lea", "Ana"), ("Kai+Lea", "Ben"), ("Kai+Lea", "Cleo"), ("Ana", "Dev"), ("Ben", "Dev"), ("Cleo", "Dev")]:
        c.edge(right[a], right[b], ra=24 if a == "Kai+Lea" else 18, rb=18, color=GRAY, width=1.8)
    for k, p in right.items():
        tw = k == "Kai+Lea"
        c.node(*p, "x2" if tw else k, r=24 if tw else 18, fill="#fff4dc" if tw else PALE, stroke=ORANGE if tw else BLUE, size=12 if tw else 10)
    c.text(540, 214, "Kai + Lea", size=12, fill=MUTED)
    c.text(380, 325, "Same distances to everyone else, and two steps to each other: one search does for both.", size=12.5, fill=MUTED)
    meta = dict(book="algorithms", chapter=19,
                caption="Look-alike people (same contacts, not tied to each other) are always the same distance from everyone else, and two steps from each other. Fold them into one dot with a weight of 2: one search answers for both, and anyone reaching the dot counts it twice.",
                alt="Left: six dots. Kai and Lea, in orange, are each tied to Ana, Ben and Cleo, who are all tied to Dev. Right: Kai and Lea have become one larger orange dot marked x2, tied to Ana, Ben and Cleo; the rest is unchanged.",
                data={"twins": ["Kai", "Lea"], "shared_contacts": ["Ana", "Ben", "Cleo"]})
    return c, meta


# ---------------------------------------------------------------- 4. dangling leaves fold onto their parent
def leaf_fold():
    adj = adjacency(10, EDGES)
    ivo, jo = bfs(adj, 8), bfs(adj, 9)
    lp, ll = level_counts(ivo), level_counts(jo)
    rebuilt = [0, 1, lp[1] - 1] + lp[2:]
    assert rebuilt == ll, (rebuilt, ll)
    c = Canvas(760, 360, "A leaf is its parent, one step farther",
               "Two rows of level counts, for Ivo and for Jo, with arrows showing Jo's row is Ivo's shifted right by one.")
    c.text(380, 30, "People at each distance: Ivo, and Jo who hangs off Ivo", size=15, weight="700")
    cell, x0 = 76, 210
    for d in range(1, 5):
        c.text(x0 + (d - 1) * cell + cell / 2, 70, f"distance {d}", size=12, fill=MUTED)
    rows = [("Ivo (parent)", lp, BLUE, 86), ("Jo (leaf)", ll, ORANGE, 196)]
    for name, counts, col, y in rows:
        c.text(x0 - 14, y + 34, name, size=13, anchor="end", weight="700")
        for d in range(1, 5):
            v = counts[d] if d < len(counts) else 0
            c.rect(x0 + (d - 1) * cell, y, cell - 8, 52, fill=col + "22", stroke=col, sw=1.5, rx=6)
            c.text(x0 + (d - 1) * cell + (cell - 8) / 2, y + 33, str(v), size=18, weight="700")
    for d in range(1, 4):
        c.arrow((x0 + (d - 1) * cell + 34, 142), (x0 + d * cell + 34, 192), color=MUTED, width=1.6)
    c.lines(560, 110, ["Jo's row from Ivo's:", "distance 1: 1 (Ivo himself)", f"distance 2: {lp[1]} - 1 = {ll[2]}",
                        "  (Ivo's friends, minus Jo)", "distance d + 1: Ivo's distance d"], size=12.5, gap=1.6)
    c.text(380, 300, f"Sum of distances, Ivo: {sum(ivo)}.  Jo: {sum(jo)}, with no search from Jo at all.", size=13, weight="600")
    c.text(380, 330, "Every leaf is folded away the same way, and its parent counts it at one level deeper.", size=12, fill=MUTED)
    meta = dict(book="algorithms", chapter=19,
                caption="A person with a single tie (a leaf) is exactly one step farther than their only friend from everybody else. So we never search from Jo: Jo's counts are Ivo's slid one place to the right, with Jo removed from Ivo's first count and Ivo put in Jo's.",
                alt=(f"Two rows of four boxes. Ivo's row holds the number of people at distances 1 to 4: {', '.join(str(lp[d]) if d < len(lp) else '0' for d in range(1, 5))}. "
                     f"Jo's row holds {', '.join(str(ll[d]) for d in range(1, 5))}. Diagonal arrows show each of Ivo's counts moving one box to the right in Jo's row. "
                     f"The sums of distances are {sum(ivo)} for Ivo and {sum(jo)} for Jo."),
                data={"ivo_levels": lp, "jo_levels": ll})
    return c, meta


# ---------------------------------------------------------------- 5. counters kept as bit planes
def planes(counts, k=3):
    return [[(v >> b) & 1 for v in counts] for b in range(k)]


def bit_planes():
    before = [2, 0, 3, 1, 5, 0, 1, 4]
    mask = [1, 1, 1, 0, 1, 0, 0, 1]
    after = [a + m for a, m in zip(before, mask)]
    pb, pa = planes(before), planes(after)
    # ripple add: carry into plane b is the AND of the mask carried so far and plane b
    carry, steps = mask[:], []
    for b in range(3):
        newp = [p ^ cc for p, cc in zip(pb[b], carry)]
        steps.append(carry[:])
        carry = [p & cc for p, cc in zip(pb[b], carry)]
        assert newp == pa[b]
    assert not any(carry)
    c = Canvas(760, 470, "Counters stored as bit planes",
               "Eight counters, one per search, stored as three rows of bits; adding a word of new arrivals updates all eight with a few word operations.")
    c.text(380, 28, "Eight counters, one per search, stored sideways", size=15, weight="700")
    cell, x0 = 34, 250
    for i in range(8):
        c.text(x0 + i * cell + 15, 60, NAMES[i], size=11, fill=MUTED)
    c.text(x0 + 8 * cell + 30, 60, "", size=11)

    def block(y, title, pl, counts, col):
        c.text(40, y + 14, title, size=13, anchor="start", weight="700")
        for b in range(3):
            bits_row(c, x0, y + 24 + b * 36, pl[b], f"plane {b} (counts {2 ** b}s)", col)
        for i, v in enumerate(counts):
            c.text(x0 + i * cell + 15, y + 24 + 3 * 36 + 16, str(v), size=13, weight="700", fill=INK)
        c.text(x0 - 12, y + 24 + 3 * 36 + 16, "count", size=12, anchor="end", fill=MUTED)
    block(70, "Before", pb, before, BLUE)
    bits_row(c, x0, 222, mask, "add: new this level", ORANGE)
    block(262, "After", pa, after, BLUE)
    c.text(380, 452, "Add plane by plane: new bit = bit XOR carry, next carry = bit AND carry. Three planes count to 7.", size=12, fill=MUTED)
    meta = dict(book="algorithms", chapter=19,
                caption="Instead of eight separate counters, keep the ones digits of all eight in one word, the twos digits in another and the fours in a third. Adding a word of new arrivals is schoolbook addition with carries, done for all eight searches at once.",
                alt=("Two blocks of three rows of eight bits, before and after, with an orange row of bits being added between them. "
                     f"Read down each column, the counts before are {', '.join(map(str, before))}; the orange row adds {', '.join(map(str, mask))}; "
                     f"the counts after are {', '.join(map(str, after))}."),
                data={"before": before, "add": mask, "after": after, "carries_into_plane": steps})
    return c, meta


# ---------------------------------------------------------------- 6. compressing a list of friends
def varint_len(v):
    n = 1
    while v >= 128:
        v >>= 7
        n += 1
    return n


def gap_varint():
    friends = [12, 15, 16, 40, 41, 300, 1_250, 70_000]
    gaps = [friends[0]] + [b - a for a, b in zip(friends, friends[1:])]
    sizes = [varint_len(g) for g in gaps]
    c = Canvas(760, 360, "Storing a friend list as gaps",
               "A sorted list of friend numbers, the gaps between them, and how many bytes each gap needs.")
    c.text(380, 28, "One person's friends, by id", size=15, weight="700")
    cell, x0 = 78, 150
    for row, (title, vals, col) in enumerate([("friend id", friends, BLUE), ("gap", gaps, ORANGE),
                                              ("bytes", sizes, GREEN)]):
        y = 60 + row * 70
        c.text(x0 - 14, y + 30, title, size=13, anchor="end", weight="700")
        for i, v in enumerate(vals):
            c.rect(x0 + i * cell, y, cell - 8, 46, fill=col + "1f", stroke=col, sw=1.4, rx=6)
            c.text(x0 + i * cell + (cell - 8) / 2, y + 29, f"{v:,}", size=14, weight="600")
    c.text(380, 290, f"Plain list: {len(friends)} x 4 = {4 * len(friends)} bytes.  Gaps: {sum(sizes)} bytes.", size=14, weight="700")
    c.text(380, 318, "Small gaps fit in one byte (up to 127), medium ones in two (up to 16,383), and so on.", size=12, fill=MUTED)
    meta = dict(book="algorithms", chapter=19,
                caption="Friend lists are kept sorted, so the gaps between neighbours' ids are mostly small. Writing each gap with as few bytes as it needs (7 bits of value per byte) shrinks this list from 32 bytes to " + str(sum(sizes)) + ".",
                alt=(f"Three rows of eight boxes. Friend ids: {', '.join(f'{v:,}' for v in friends)}. Gaps: {', '.join(f'{v:,}' for v in gaps)}. "
                     f"Bytes per gap: {', '.join(map(str, sizes))}, {sum(sizes)} in all, against 32 for the plain list."),
                data={"friends": friends, "gaps": gaps, "bytes": sizes})
    return c, meta


# ---------------------------------------------------------------- 7. how much reading the shared pass saves
def shared_work():
    adj = adjacency(10, EDGES)
    dists = [bfs(adj, s) for s in range(8)]
    alone = sum(sum(len(adj[u]) for u in range(10) if d[u] >= 0) for d in dists)  # each search reads every list once
    shared, top = 0, max(max(d) for d in dists)
    per_level = []
    for lvl in range(top + 1):
        frontier = [u for u in range(10) if any(d[u] == lvl for d in dists)]
        reads = sum(len(adj[u]) for u in frontier)
        per_level.append(reads)
        shared += reads
    c = Canvas(760, 300, "Friend lists read: separate searches versus one shared pass",
               "Two bars comparing how many friend-list entries are read by eight separate searches and by one shared pass.")
    c.text(380, 30, "Friend-list entries read, eight searches on the ten-person network", size=15, weight="700")
    x0, w = 200, 500
    for k, (lab, v, col) in enumerate([("eight separate searches", alone, RED), ("one shared pass", shared, BLUE)]):
        y = 70 + k * 70
        c.text(x0 - 12, y + 26, lab, size=13, anchor="end", weight="600")
        c.rect(x0, y, w * v / alone, 40, fill=col, stroke=col, sw=0)
        c.text(x0 + w * v / alone + 8, y + 26, f"{v}", size=14, anchor="start", weight="700")
    c.text(380, 240, "Shared pass, entries read at each step: " + ", ".join(map(str, per_level)), size=13)
    c.text(380, 268, "A person's list is read once per step in which any of the eight searches is passing through.", size=12, fill=MUTED)
    meta = dict(book="algorithms", chapter=19,
                caption=f"Eight separate searches read {alone} friend-list entries between them; one shared pass reads {shared}. The saving grows with the number of searches in a word and with how much their paths overlap.",
                alt=f"Two horizontal bars. Eight separate searches: {alone} entries read. One shared pass: {shared}. Below, the shared pass's reads per step: {', '.join(map(str, per_level))}.",
                data={"separate": alone, "shared": shared, "shared_per_step": per_level})
    return c, meta


FIGURES = {"alg-cl-repeat-searches": repeat_searches, "alg-cl-word-lights": word_lights, "alg-cl-twins": twins,
           "alg-cl-leaf-fold": leaf_fold, "alg-cl-bit-planes": bit_planes, "alg-cl-gap-varint": gap_varint,
           "alg-cl-shared-work": shared_work}

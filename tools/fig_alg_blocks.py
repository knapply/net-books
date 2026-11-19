"""Figures for the building-blocks chapter of the algorithms book (chapter 3). Standard library only.

The heap, union-find, hash map, bitset and radix-sort pictures are produced by small reference routines in this
file that do the textbook steps and record every state, so the drawing is the trace and not a hand copy.
"""
from alg_draw import (FIVE, LIGHT, PALE_GREEN, PALE_ORANGE, PALE_PURPLE, PALE_RED, cells, pill)
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, PURPLE, RED, SKY, Canvas

CH = 3
TASKS = [("Ana", 2), ("Ben", 5), ("Cleo", 3), ("Dev", 9), ("Eli", 6), ("Fay", 4), ("Gus", 8)]


# ----------------------------------------------------------------- reference routines
def sift_up_trace(arr, key):
    """Insert key at the end of a min-heap array; return every state and the index that just moved."""
    a = list(arr) + [key]
    states = [(list(a), len(a) - 1, None)]
    i = len(a) - 1
    while i > 0 and a[(i - 1) // 2] > a[i]:
        p = (i - 1) // 2
        a[p], a[i] = a[i], a[p]
        states.append((list(a), p, i))
        i = p
    return states


def pop_trace(arr):
    """Remove the smallest of a min-heap array; return (smallest, states of the repair)."""
    a = list(arr)
    top = a[0]
    a[0] = a.pop()
    states = [(list(a), 0, None)]
    i = 0
    while True:
        kids = [k for k in (2 * i + 1, 2 * i + 2) if k < len(a)]
        if not kids:
            break
        k = min(kids, key=lambda j: a[j])
        if a[k] >= a[i]:
            break
        a[i], a[k] = a[k], a[i]
        states.append((list(a), k, i))
        i = k
    return top, states


def is_min_heap(a):
    return all(a[(i - 1) // 2] <= a[i] for i in range(1, len(a)))


def tree_pos(i, x0, y0, w, dy):
    lvl = (i + 1).bit_length() - 1
    j = i + 1 - 2 ** lvl
    return x0 + (j + 0.5) / 2 ** lvl * w, y0 + lvl * dy


def heap_panel(c, x, y, arr, title, mark=None, other=None, w=300, label=None, r=15, arr_cells=True):
    c.rect(x, y, w + 40, 262, fill="none", stroke=FAINT, sw=1, rx=8)
    c.text(x + 14, y + 24, title, size=13, anchor="start", weight="700")
    tx, ty = x + 20, y + 50
    for i in range(1, len(arr)):
        c.edge(tree_pos((i - 1) // 2, tx, ty, w, 46), tree_pos(i, tx, ty, w, 46), ra=r, rb=r, color=MUTED, width=1.6)
    for i, v in enumerate(arr):
        px, py = tree_pos(i, tx, ty, w, 46)
        hot = i == mark
        sec = i == other
        c.node(px, py, str(v), r=r, fill=PALE_ORANGE if hot else PALE_PURPLE if sec else LIGHT,
               stroke=ORANGE if hot else PURPLE if sec else BLUE, size=13)
    if arr_cells:
        cw = min(34, (w + 20) / max(len(arr), 1))
        cells(c, x + 20, y + 205, arr, w=cw, h=26, size=12, fills={mark: PALE_ORANGE} if mark is not None else None,
              idx=False)
    if label:
        c.text(x + 14, y + 253, label, size=12, anchor="start", fill=MUTED)


# ----------------------------------------------------------------- figures
def queue_stack():
    c = Canvas(900, 330, "Queue and stack", "A cafe line and a stack of plates.")
    c.text(30, 32, "Queue: first in, first out.   Stack: last in, first out.", size=16, weight="700", anchor="start")
    c.text(60, 70, "Queue (the cafe line)", size=14, weight="700", anchor="start", fill=BLUE)
    for k, n in enumerate(FIVE):
        x = 90 + k * 80
        c.node(x, 130, str(k), r=20, fill=LIGHT, stroke=BLUE)
        c.text(x, 172, n, size=12, fill=MUTED)
    c.text(60, 130, "", size=1)
    c.arrow((70, 130), (24, 130), color=GREEN, width=2.6)
    c.text(40, 200, "OUT: Ana, the longest waiter", size=12, anchor="start", fill=GREEN, weight="700")
    c.arrow((520, 130), (440, 130), color=ORANGE, width=2.6)
    c.text(380, 200, "IN: Eli joined last", size=12, anchor="start", fill=ORANGE, weight="700")
    c.text(60, 250, "Used for: breadth-first search (visit people in the order they were found).", size=13, anchor="start", fill=MUTED)
    c.text(620, 70, "Stack (plates)", size=14, weight="700", anchor="start", fill=PURPLE)
    for k, n in enumerate(FIVE):
        y = 240 - k * 28
        c.rect(650, y, 120, 22, fill=LIGHT if k < 4 else PALE_PURPLE, stroke=PURPLE if k == 4 else BLUE, sw=1.8, rx=6)
        c.text(710, y + 16, f"{k}  {n}", size=12, weight="600")
    c.arrow((800, 80), (774, 100), color=ORANGE, width=2.6)
    c.text(800, 70, "IN and OUT", size=12, anchor="middle", fill=PURPLE, weight="700")
    c.text(620, 275, "Eli is on top, so Eli comes off first.", size=13, anchor="start", fill=MUTED)
    c.text(620, 295, "Used for: depth-first search, undo.", size=13, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Same five people, two rules. In a queue the first to arrive is served first; in a stack the last to arrive is served first.",
                   alt="Left, five numbered people in a line labeled queue, with an arrow marking Ana at the front as OUT and an arrow at the back marking Eli as IN. Right, five plates stacked with Eli on top, labeled stack, with a single arrow at the top for both IN and OUT.")


def heap_tree():
    arr = [v for _, v in TASKS]
    assert is_min_heap(arr)
    c = Canvas(900, 330, "A heap", "A heap drawn as a tree and stored as a list.")
    c.text(30, 32, "A heap: a tree on paper, a plain list in memory. The smallest is always on top.", size=16, weight="700", anchor="start")
    tx, ty, w = 60, 70, 380
    for i in range(1, 7):
        c.edge(tree_pos((i - 1) // 2, tx, ty, w, 62), tree_pos(i, tx, ty, w, 62), ra=19, rb=19, color=MUTED, width=1.8)
    for i, (n, v) in enumerate(TASKS):
        px, py = tree_pos(i, tx, ty, w, 62)
        c.node(px, py, str(v), r=19, fill=PALE_ORANGE if i == 0 else LIGHT, stroke=ORANGE if i == 0 else BLUE, size=14)
        c.text(px, py + 33, n, size=11, fill=MUTED)
    c.text(520, 80, "The same heap as a list:", size=14, anchor="start", weight="700")
    cells(c, 520, 96, arr, w=44, h=34, size=15, bold=True, fills={0: PALE_ORANGE}, idx_label="slot")
    c.text(520, 170, "The rule: every parent is no bigger than its children.", size=13, anchor="start")
    c.text(520, 196, "Where is the family? Just arithmetic on the slot number i:", size=13, anchor="start", fill=MUTED)
    c.text(534, 220, "children of slot i: slots 2i+1 and 2i+2", size=13, anchor="start", mono=True)
    c.text(534, 242, "parent of slot i: slot (i-1) // 2", size=13, anchor="start", mono=True)
    c.text(520, 262, "(// means divide, then drop the remainder.)", size=12, anchor="start", fill=MUTED)
    c.text(520, 290, "Example: slot 1 (Ben, 5) has children in slots 3 and 4: 9 and 6.", size=13, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="A heap of seven tasks. The picture is a tree, the storage is a plain list, and the family tree is slot arithmetic. The smallest number is always in slot 0.",
                   alt="Left, a tree of seven circles: 2 at the top, then 5 and 3, then 9, 6, 4 and 8, with names Ana, Ben, Cleo, Dev, Eli, Fay and Gus underneath. Right, the same seven numbers as a row of seven boxes numbered 0 to 6, and the slot rules: children of slot i are slots 2i plus 1 and 2i plus 2; the parent is slot (i minus 1) over 2 rounded down.",
                   data={"array": arr})


def heap_insert():
    arr = [v for _, v in TASKS]
    states = sift_up_trace(arr, 1)
    assert is_min_heap(states[-1][0])
    c = Canvas(960, 620, "Inserting into a heap", "Add a 1 at the bottom and let it float up.")
    c.text(30, 30, "Insert a new task with number 1: put it at the bottom, swap upward while it is smaller than its parent", size=15, weight="700", anchor="start")
    notes = ["Put 1 in the next free slot, at the bottom.", "1 is smaller than its parent 9: swap.",
             "1 is smaller than its new parent 5: swap.", "1 is smaller than the old top, 2: swap. Done."]
    for k, (a, mark, other) in enumerate(states[:4]):
        x, y = 20 + (k % 2) * 470, 50 + (k // 2) * 280
        heap_panel(c, x, y, a, f"Step {k + 1}", mark=mark, other=other, w=290, label=notes[k])
    c.text(30, 610, f"{len(states) - 1} swaps for a heap of eight. Doubling the heap adds one more level, so at most one more swap.", size=13, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Inserting 1 into the heap. It starts in the last slot and floats up, swapping with each bigger parent, until it reaches the top. Only the nodes on one path from bottom to top are touched.",
                   alt="Four small heaps in a two by two grid, each a tree above a row of boxes. Step 1 places a 1 at the bottom, under 9. Step 2 swaps it with 9. Step 3 swaps it with 5. Step 4 swaps it with 2, leaving 1 at the top. Each panel has a one-line note.",
                   data={"states": [s[0] for s in states]})


def heap_pop():
    arr = sift_up_trace([v for _, v in TASKS], 1)[-1][0]
    top, states = pop_trace(arr)
    assert top == 1 and is_min_heap(states[-1][0])
    c = Canvas(960, 620, "Removing from a heap", "Take the top, move the last one up, sink it.")
    c.text(30, 30, "Take the smallest: remove the top, move the last task to the top, swap it downward with its smaller child", size=15, weight="700", anchor="start")
    notes = ["The smallest, 1, is on top. We take it, which leaves a hole.", f"The last task ({arr[-1]}) fills the hole at the top.",
             "Its children are 3 and 2. Swap with the smaller one, 2.", "Its children are now 5 and 6. Swap with 5. Done: the rule holds."]
    shown = [(arr, 0, None)] + states
    assert len(shown) == 4
    for k in range(4):
        a, mark, other = shown[k]
        x, y = 20 + (k % 2) * 470, 50 + (k // 2) * 280
        heap_panel(c, x, y, a, f"Step {k + 1}", mark=mark, other=other, w=290, label=notes[k])
    c.text(30, 610, f"The new smallest is {states[-1][0][0]}. The repair walked down one path, so it costs about one swap per level.", size=13, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Removing the smallest. The last task jumps into the empty top slot and sinks, each time swapping with the smaller of its two children, until the rule holds again.",
                   alt="Four small heaps of seven tasks in a two by two grid. Step 1 shows the last task moved into the top. Steps 2 and 3 show it swapping downward with the smaller child. Step 4 shows the finished heap with the new smallest number on top.",
                   data={"popped": top, "states": [s[0] for s in states]})


def uf_forest(c, x, y, parent, title, hi=None, note=""):
    c.rect(x, y, 225, 250, fill="none", stroke=FAINT, sw=1, rx=8)
    c.text(x + 12, y + 24, title, size=12, anchor="start", weight="700")
    n = len(parent)
    depth = [0] * n
    for i in range(n):
        d, j = 0, i
        while parent[j] != j:
            j = parent[j]
            d += 1
        depth[i] = d
    roots = [i for i in range(n) if parent[i] == i]
    kids = {i: [] for i in range(n)}
    for i in range(n):
        if parent[i] != i:
            kids[parent[i]].append(i)
    pos = {}
    slot = [0]

    def place(i, d):
        if not kids[i]:
            pos[i] = (slot[0], d)
            slot[0] += 1
        else:
            for k in kids[i]:
                place(k, d + 1)
            xs = [pos[k][0] for k in kids[i]]
            pos[i] = (sum(xs) / len(xs), d)
    for r in roots:
        place(r, 0)
        slot[0] += 0.5
    total = max(slot[0], 1)
    px = lambda v: x + 28 + v / max(total, 4) * 170
    py = lambda d: y + 60 + d * 42
    for i in range(n):
        if parent[i] != i:
            c.arrow((px(pos[i][0]), py(pos[i][1])), (px(pos[parent[i]][0]), py(pos[parent[i]][1])), color=MUTED, width=1.6)
    for i in range(n):
        isroot = parent[i] == i
        c.node(px(pos[i][0]), py(pos[i][1]), FIVE[i][0], r=15, fill=PALE_ORANGE if isroot else LIGHT, stroke=ORANGE if isroot else BLUE, size=13)
    cells(c, x + 12, y + 195, parent, w=30, h=26, size=12, idx=False, fills={i: PALE_ORANGE for i in range(n) if parent[i] == i})
    c.text(x + 12, y + 240, note, size=10, anchor="start", fill=MUTED)


def unionfind():
    def find(p, i):
        while p[i] != i:
            i = p[i]
        return i
    p0 = list(range(5))
    p1 = list(p0)
    p1[1] = 0
    p1[4] = 3
    p2 = list(p1)
    ra, rb = find(p2, 1), find(p2, 3)
    p2[rb] = ra
    p3 = list(p2)
    r = find(p3, 4)
    p3[4] = r
    c = Canvas(960, 330, "Union-find", "Joining groups with a forest of parent pointers.")
    c.text(30, 30, "Union-find: every group is a little tree, and the root is the group's name", size=16, weight="700", anchor="start")
    uf_forest(c, 10, 46, p0, "Start: five groups of one", note="everyone is their own parent")
    uf_forest(c, 245, 46, p1, "Two small joins", note="Ben under Ana; Eli under Dev")
    uf_forest(c, 480, 46, p2, "Ben-Dev: join the roots", note="Dev now hangs under Ana")
    uf_forest(c, 715, 46, p3, "Ask about Eli: shortcut", note="Eli points straight at Ana")
    c.text(30, 320, "Orange circles are roots. The row of boxes under each picture is the actual storage: slot i holds the parent of person i.", size=12, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Union-find on five people. Joining two groups means hanging one root under the other, a single change. When we later ask who Eli's group leader is, we point Eli straight at the leader so the next question is faster.",
                   alt="Four panels, each a small forest of circles holding the initials A, B, C, D and E, with a row of five boxes of parent numbers below. Panel 1: five separate roots. Panel 2: Ben hangs under Ana and Eli under Dev. Panel 3: Dev's tree is hung under Ana, so Ana is the root of Ana, Ben, Dev and Eli, with Cleo alone. Panel 4: Eli points directly at Ana.",
                   data={"parents": [p0, p1, p2, p3]})


def hashmap():
    names = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus"]
    place = lambda s: sum(ord(ch.lower()) - 96 for ch in s)
    h = lambda s: place(s) % 7
    buckets = {b: [] for b in range(7)}
    for n in names:
        buckets[h(n)].append(n)
    assert any(len(v) > 1 for v in buckets.values()), "the example should show a collision"
    c = Canvas(900, 420, "A hash map", "Names to buckets by a scrambling rule.")
    c.text(30, 32, "Hash map: a scrambling rule sends each name to a bucket, so we do not search", size=16, weight="700", anchor="start")
    c.text(40, 64, "The rule here: add up each letter's place in the alphabet (a = 1, b = 2, ...), keep the remainder after dividing by 7.", size=13, anchor="start", fill=MUTED)
    for i, n in enumerate(names):
        y = 90 + i * 44
        c.rect(40, y, 90, 30, fill=PAPER, stroke=INK, sw=1.4, rx=4)
        c.text(85, y + 20, n, size=13, weight="600")
        c.text(142, y + 20, f"{place(n)} mod 7 = {h(n)}", size=12, anchor="start", fill=MUTED)
        shared = len(buckets[h(n)]) > 1
        c.add(f'<line x1="250" y1="{y + 15}" x2="400" y2="{90 + h(n) * 44 + 15}" stroke="{ORANGE if shared else MUTED}" stroke-width="1.6"/>')
    for b in range(7):
        y = 90 + b * 44
        c.rect(400, y, 70, 30, fill=LIGHT, stroke=BLUE, sw=1.6, rx=4)
        c.text(435, y + 20, f"bucket {b}", size=11, weight="600")
        x = 490
        for n in buckets[b]:
            sh = len(buckets[b]) > 1
            c.rect(x, y, 70, 30, fill=PALE_ORANGE if sh else PAPER, stroke=ORANGE if sh else INK, sw=1.6, rx=4)
            c.text(x + 35, y + 20, n, size=13, weight="600")
            x += 78
    c.text(680, 150, "Look up Dev: do the sum (31),", size=13, anchor="start")
    c.text(680, 170, "go to bucket 3, read what is there.", size=13, anchor="start")
    c.text(680, 214, "Ben and Cleo share bucket 0: a", size=13, anchor="start", fill=ORANGE, weight="700")
    c.text(680, 234, "collision. We check just those two.", size=13, anchor="start", fill=ORANGE, weight="700")
    c.text(680, 278, "A good rule spreads names evenly,", size=13, anchor="start", fill=MUTED)
    c.text(680, 298, "so buckets stay short.", size=13, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="A hash map sends each key through a scrambling rule to a bucket, then looks only in that bucket. Two keys can land in the same bucket (orange), which is why we still check names inside it.",
                   alt="Seven names on the left, each with its alphabet-place sum and remainder after dividing by 7, joined by lines to seven buckets in the middle. Ben and Cleo share bucket 0 and Eli and Gus share bucket 5, drawn in orange. Notes on the right explain the lookup and collisions.",
                   data={str(b): v for b, v in buckets.items()})


def bitset():
    A = {0, 2, 3, 6}
    B = {2, 3, 5, 6, 7}
    def bits(s):
        return [1 if i in s else 0 for i in range(8)]
    c = Canvas(900, 360, "A bitset", "People as bits in a row.")
    c.text(30, 32, "Bitset: a set of people stored as one row of on/off switches", size=16, weight="700", anchor="start")
    rows = [("Ana's friends", A, BLUE), ("Dev's friends", B, PURPLE), ("both (AND)", A & B, ORANGE), ("either (OR)", A | B, GREEN)]
    c.text(210, 66, "person:", size=11, anchor="end", fill=MUTED, italic=True)
    for j in range(8):
        c.text(222 + j * 36 + 18, 66, str(j), size=11, fill=MUTED)
    for k, (lab, s, col) in enumerate(rows):
        y = 78 + k * 52
        c.text(206, y + 26, lab, size=13, anchor="end", weight="700", fill=col)
        for j, b in enumerate(bits(s)):
            c.rect(222 + j * 36, y, 36, 36, fill=(col + "33") if b else PAPER, stroke=col, sw=1.6)
            c.text(222 + j * 36 + 18, y + 24, str(b), size=15, weight="700" if b else "400", fill=INK if b else MUTED)
        c.text(222 + 8 * 36 + 16, y + 24, f"{len(s)} people", size=13, anchor="start", fill=MUTED)
    c.text(30, 306, "Each AND or OR works on 64 people at a time, in a single step of the processor.", size=13, anchor="start")
    c.text(30, 330, "Counting the ones is also a single instruction, called popcount: here 4, 5, 3 and 6.", size=13, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="A bitset holds a group of people as one row of switches. AND finds who is in both groups, OR finds who is in either, and a count of the ones tells the group's size.",
                   alt="Four rows of eight boxes, each 0 or 1, for people 0 to 7. Ana's friends have ones at 0, 2, 3 and 6; Dev's friends at 2, 3, 5, 6 and 7. The AND row has ones at 2, 3 and 6, three people; the OR row has ones at 0, 2, 3, 5, 6 and 7, six people.",
                   data={"A": sorted(A), "B": sorted(B)})


def sorting():
    nums = [329, 457, 657, 839, 436, 720, 355]
    passes = [("Start", list(nums))]
    cur = list(nums)
    for d, nm in ((0, "ones digit"), (1, "tens digit"), (2, "hundreds digit")):
        buckets = [[] for _ in range(10)]
        for v in cur:
            buckets[(v // 10 ** d) % 10].append(v)
        cur = [v for b in buckets for v in b]
        passes.append((f"After sorting by the {nm}", list(cur)))
    assert cur == sorted(nums), "radix sort must end sorted"
    c = Canvas(900, 330, "Radix sort", "Sorting numbers one digit at a time.")
    c.text(30, 32, "Radix sort: sort by the last digit, then the middle, then the first", size=16, weight="700", anchor="start")
    for k, (title, arr) in enumerate(passes):
        x = 30 + k * 215
        c.text(x, 66, title, size=12, anchor="start", weight="700")
        for i, v in enumerate(arr):
            y = 80 + i * 32
            d = k - 1
            s = f"{v:03d}"
            c.rect(x, y, 90, 26, fill=PAPER, stroke=INK, sw=1.3, rx=3)
            for pos, ch in enumerate(s):
                hot = k > 0 and pos == 3 - k
                c.text(x + 18 + pos * 27, y + 19, ch, size=15, weight="700" if hot else "400", fill=ORANGE if hot else INK, mono=True)
    c.text(30, 318, "Each pass drops numbers into ten buckets by one digit and reads them back in order, keeping earlier order for ties. Three passes, no comparisons.", size=12, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Radix sort on seven numbers. Each pass looks at one digit (orange) and files the numbers into ten buckets, then reads them back out. After three passes, the list is in order.",
                   alt="Four columns of the same seven three-digit numbers: the start (329, 457, 657, 839, 436, 720, 355), then after sorting by the ones digit, the tens digit and the hundreds digit. The digit used in each pass is orange. The last column reads 329, 355, 436, 457, 657, 720, 839.",
                   data={"passes": passes})


def costs():
    c = Canvas(900, 430, "Building blocks at a glance", "What each block costs.")
    c.text(30, 32, "At a glance: what each building block costs", size=16, weight="700", anchor="start")
    cols = ["Block", "Add", "Take or find", "Good for"]
    rows = [("Queue", "1 step", "1 step (oldest)", "breadth-first search", GREEN),
            ("Stack", "1 step", "1 step (newest)", "depth-first search, undo", GREEN),
            ("Heap", "log n steps", "1 step to peek, log n to take", "shortest paths, top few", BLUE),
            ("Union-find", "1 step", "about 1 step (nearly)", "who is connected to whom", GREEN),
            ("Hash map", "about 1 step", "about 1 step", "names to ids, counting", GREEN),
            ("Bitset", "1 step", "1 step; groups: n / 64 steps", "sets of people, common friends", GREEN),
            ("Sort (comparing)", "n log n steps", "all at once", "ordering anything", BLUE),
            ("Radix sort", "k passes over n", "all at once", "integer ids, in bulk", BLUE)]
    xs = [40, 220, 400, 640]
    for j, h in enumerate(cols):
        c.text(xs[j], 72, h, size=13, anchor="start", weight="700", fill=MUTED)
    for i, (n, a, t, g, col) in enumerate(rows):
        y = 84 + i * 40
        c.rect(30, y, 840, 34, fill=LIGHT if i % 2 == 0 else PAPER, stroke=FAINT, sw=1, rx=4)
        for j, v in enumerate((n, a, t, g)):
            c.text(xs[j], y + 22, v, size=13, anchor="start", weight="700" if j == 0 else "400", fill=col if j == 0 else INK)
    c.text(30, 424, "n is the number of items held. 'About 1 step' means 1 on average, or nearly constant over a whole run.", size=12, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="The building blocks side by side. Most do their basic job in one step or a handful; the heap and sorts pay a logarithm for keeping order.",
                   alt="A table with eight rows and four columns: block, cost to add, cost to take or find, and what it is good for. Queue, stack, union-find, hash map and bitset are one step or close to it. The heap costs log n steps to add and to take. A comparing sort costs n log n and radix sort k passes over n.")


FIGURES = {
    "blocks-queue-stack": queue_stack, "blocks-heap-tree": heap_tree, "blocks-heap-insert": heap_insert,
    "blocks-heap-pop": heap_pop, "blocks-unionfind": unionfind, "blocks-hashmap": hashmap,
    "blocks-bitset": bitset, "blocks-sorting": sorting, "blocks-costs": costs,
}

#!/usr/bin/env python3
"""Draw every figure for the books. Standard library only.

Usage:
  python3 tools/make_figures.py            write books/sna/figures/*.svg and figures.json
  python3 tools/make_figures.py --snippets print the Markdown to paste into chapters

Each figure is a function returning (canvas, meta). meta holds the chapter, a
caption, alt text (a real description, not a restatement of the caption) and, for
network figures, the data drawn, so the pictures are also available as data.
"""
import json
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figs import (BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, PURPLE, RED, SKY,  # noqa: E402
                  Canvas, bfs_mean_distance, ring)

OUT = Path(__file__).resolve().parent.parent / "books" / "sna" / "figures"
NAMES = ["Ana", "Ben", "Chloe", "Dev", "Eli"]
LIGHT = "#eef6fb"


def net(c, pos, edges, r=24, **kw):
    for a, b in edges:
        c.edge(pos[a], pos[b], ra=r, rb=r, **kw)


# ---------------------------------------------------------------- chapter 1
def two_teams():
    c = Canvas(780, 330, "Two five-person teams with the same people",
               "Left: five people all tied to each other. Right: Ana in the middle tied to four others who are not tied to each other.")
    left = dict(zip(NAMES, ring(200, 160, 95, 5)))
    right = {"Ana": (580, 160)}
    right.update(dict(zip(NAMES[1:], ring(580, 160, 100, 4, start=-45))))
    c.caption(200, 28, "Everyone talks to everyone")
    c.caption(580, 28, "Ana is the hub")
    net(c, left, list(combinations(NAMES, 2)), width=2, color=MUTED)
    star = [("Ana", n) for n in NAMES[1:]]
    net(c, right, star, width=2, color=MUTED)
    for n in NAMES:
        c.node(*left[n], n, r=24, fill=LIGHT, stroke=BLUE, size=12)
        hub = n == "Ana"
        c.node(*right[n], n, r=24, fill=ORANGE if hub else LIGHT, stroke=ORANGE if hub else BLUE, size=12)
    c.text(200, 300, "Everyone has 4 ties", size=14, fill=MUTED)
    c.text(580, 300, "Ana has 4 ties; everyone else has 1", size=14, fill=MUTED)
    meta = dict(chapter=1, caption="The same five people in two different teams. The attribute table is identical; the pattern of ties is not, and neither is what happens when Ana has a bad week.",
                alt="Two network diagrams of the same five people. On the left every person is connected to every other person. On the right, Ana is in the center connected to the four others, who are not connected to each other.",
                data={"left": {"nodes": NAMES, "edges": list(map(list, combinations(NAMES, 2)))},
                      "right": {"nodes": NAMES, "edges": [list(e) for e in star]}})
    return c, meta


def habit():
    c = Canvas(800, 240, "The five-step habit",
               "Five boxes in a row: idea, data, compute, interpret, doubt, with an arrow looping from doubt back to idea.")
    steps = [("1. Idea", "what social claim?"), ("2. Data", "what is a tie?"),
             ("3. Compute", "by hand, then code"), ("4. Interpret", "tie back to the idea"),
             ("5. Doubt", "other conventions?")]
    xs = [16 + i * 154 for i in range(5)]
    for i, (t, s) in enumerate(steps):
        c.rect(xs[i], 46, 140, 66, fill=LIGHT, stroke=BLUE, sw=2, rx=10)
        c.text(xs[i] + 70, 76, t, size=16, weight="700")
        c.text(xs[i] + 70, 98, s, size=12, fill=MUTED)
        if i < 4:
            c.arrow((xs[i] + 142, 79), (xs[i + 1] - 2, 79), color=BLUE)
    mk = c.marker(BLUE)
    c.add(f'<path d="M{xs[4] + 70},114 V170 H{xs[0] + 70} V116" fill="none" stroke="{BLUE}" '
          f'stroke-width="2" stroke-dasharray="6 4" marker-end="url(#{mk})"/>')
    c.text(400, 192, "revise the question, the data, or the claim, and go round again", size=13,
           fill=MUTED, italic=True)
    meta = dict(chapter=1, caption="The rhythm of every measure in the book: start from the idea, be clear about the data, compute, interpret, doubt, and loop back.",
                alt="A left-to-right flow of five labeled boxes: Idea, Data, Compute, Interpret, Doubt. A dashed arrow runs from the last box back to the first.",
                data={"steps": [s[0] for s in steps]})
    return c, meta


# ---------------------------------------------------------------- chapter 2
def dyad_triad():
    c = Canvas(780, 260, "From two people to three",
               "Three small diagrams: a pair of connected people, a triangle of three connected people, and a person in the middle linking two others who have no direct tie.")
    # dyad
    a, b = (80, 110), (180, 110)
    c.edge(a, b, width=2.5, color=MUTED)
    c.node(*a, "A", fill=LIGHT, stroke=BLUE)
    c.node(*b, "B", fill=LIGHT, stroke=BLUE)
    c.caption(130, 205, "A dyad")
    c.text(130, 227, "If either leaves, the pair is over", size=12, fill=MUTED)
    # triad
    t = {"A": (390, 62), "B": (335, 150), "C": (445, 150)}
    net(c, t, [("A", "B"), ("B", "C"), ("A", "C")], r=18, width=2.5, color=MUTED)
    for k, p in t.items():
        c.node(*p, k, fill=LIGHT, stroke=BLUE)
    c.caption(390, 205, "A triad")
    c.text(390, 227, "A third person changes the structure", size=12, fill=MUTED)
    # broker
    p = {"A": (590, 150), "B": (650, 62), "C": (710, 150)}
    net(c, p, [("A", "B"), ("B", "C")], r=18, width=2.5, color=MUTED)
    c.edge(p["A"], p["C"], ra=18, rb=18, width=2, color=FAINT, dash="6 5")
    c.text(650, 170, "no direct tie", size=11, fill=MUTED, italic=True)
    c.node(*p["A"], "A", fill=LIGHT, stroke=BLUE)
    c.node(*p["C"], "C", fill=LIGHT, stroke=BLUE)
    c.node(*p["B"], "B", fill=ORANGE, stroke=ORANGE)
    c.caption(650, 205, "A go-between")
    c.text(650, 227, "B can mediate, or be bypassed", size=12, fill=MUTED)
    meta = dict(chapter=2, caption="Simmel's contrast. A pair depends on both members. Add a third person and new roles appear, such as the one in the middle.",
                alt="Left: two nodes joined by a line. Middle: three nodes joined in a triangle. Right: three nodes where the middle node is joined to both others, and a dashed line shows no direct tie between those two.",
                data={})
    return c, meta


BAL = [("+", "+", "+"), ("+", "-", "-"), ("+", "+", "-"), ("-", "-", "-")]
GLOSS = ["everyone gets along", "two friends, one shared enemy", "A is torn between two friends",
         "no one likes anyone"]


def balance_triads():
    c = Canvas(860, 350, "Balanced and unbalanced triangles",
               "Four triangles of three people with positive or negative ties. Triangles with all positive ties, or with exactly one positive tie, are balanced. Triangles with two positive ties and one negative, or all negative, are unbalanced.")
    data = []
    for i, (ab, bc, ac) in enumerate(BAL):
        cx = 110 + i * 214
        pos = {"A": (cx, 58), "B": (cx - 58, 146), "C": (cx + 58, 146)}
        for (u, v), s in [(("A", "B"), ab), (("B", "C"), bc), (("A", "C"), ac)]:
            c.edge(pos[u], pos[v], ra=17, rb=17, width=2.6, color=BLUE if s == "+" else RED,
                   dash=None if s == "+" else "7 5", sign=s)
        for k, p in pos.items():
            c.node(*p, k, r=17, fill=LIGHT, stroke=INK)
        prod = [1 if s == "+" else -1 for s in (ab, bc, ac)]
        result = prod[0] * prod[1] * prod[2]
        sym = {"+": "(+)", "-": "(−)"}
        c.text(cx, 206, f"{sym[ab]}{sym[bc]}{sym[ac]} = {'+' if result > 0 else chr(0x2212)}", size=15,
               weight="600")
        ok = result > 0
        c.text(cx, 232, ("✓ Balanced" if ok else "✗ Unbalanced"), size=15, weight="700",
               fill=GREEN if ok else RED)
        c.text(cx, 254, GLOSS[i], size=12, fill=MUTED)
        data.append({"signs": {"AB": ab, "BC": bc, "AC": ac}, "balanced": ok})
    c.edge((200, 306), (240, 306), ra=0, rb=0, width=2.6, color=BLUE)
    c.text(248, 311, "positive tie (like)", size=13, anchor="start", fill=MUTED)
    c.edge((430, 306), (470, 306), ra=0, rb=0, width=2.6, color=RED, dash="7 5")
    c.text(478, 311, "negative tie (dislike)", size=13, anchor="start", fill=MUTED)
    c.text(430, 332, "Multiply the signs: a positive product means balanced.", size=13, anchor="start", fill=MUTED)
    meta = dict(chapter=2, caption="Heider's balance rule on four triangles. Multiply the three signs: a positive product is balanced. Line style and symbol repeat the colors, so the figure reads in greyscale.",
                alt="Four triangles with signed ties. Plus, plus, plus: balanced. One plus and two minus: balanced. Two plus and one minus: unbalanced. Three minus: unbalanced.",
                data={"triangles": data})
    return c, meta


def two_camps():
    c = Canvas(620, 330, "A balanced network splits into two camps",
               "Five people in two groups. Inside each group all ties are positive; between the groups all ties are negative.")
    pos = {"A": (115, 125), "B": (115, 235), "C": (235, 180), "D": (445, 125), "E": (445, 235)}
    c.halo(70, 88, 205, 190, BLUE, "Camp 1")
    c.halo(395, 88, 100, 190, ORANGE, "Camp 2")
    plus = [("A", "B"), ("B", "C"), ("A", "C"), ("D", "E")]
    minus = [("A", "D"), ("C", "D"), ("B", "E")]
    for u, v in plus:
        c.edge(pos[u], pos[v], width=2.6, color=BLUE, sign="+")
    for u, v in minus:
        c.edge(pos[u], pos[v], width=2.4, color=RED, dash="7 5", sign="-")
    for k, p in pos.items():
        camp1 = k in "ABC"
        c.node(*p, k, fill=LIGHT if camp1 else "#fdf3dc", stroke=BLUE if camp1 else ORANGE,
               shape="circle" if camp1 else "square")
    c.text(310, 312, "Positive ties stay inside the camps; negative ties run between them.", size=13, fill=MUTED)
    meta = dict(chapter=2, caption="Cartwright and Harary's result: a signed network is balanced exactly when it can be split into two camps, friendly inside and hostile between.",
                alt="Five nodes in two outlined groups. The three nodes of Camp 1 are joined by positive ties, the two nodes of Camp 2 by one positive tie, and three negative dashed ties cross between the camps.",
                data={"camps": [["A", "B", "C"], ["D", "E"]], "positive": [list(e) for e in plus],
                      "negative": [list(e) for e in minus]})
    return c, meta


def weak_ties():
    c = Canvas(780, 330, "A weak tie as a bridge",
               "Two tightly connected circles of four people each. One dashed weak tie joins one person in each circle and is the only connection between the circles.")
    L = [(90, 110), (190, 70), (190, 200), (90, 200)]
    R = [(590, 70), (690, 110), (690, 200), (590, 200)]
    c.halo(50, 40, 180, 195, BLUE, "Circle 1")
    c.halo(550, 40, 180, 195, BLUE, "Circle 2")
    for grp in (L, R):
        for a, b in combinations(grp, 2):
            c.edge(a, b, ra=15, rb=15, width=3, color=MUTED)
    c.edge(L[1], R[0], ra=15, rb=15, width=3, color=ORANGE, dash="9 6")
    c.text(390, 56, "weak tie: the only bridge", size=14, weight="600", fill=ORANGE)
    for i, p in enumerate(L + R):
        bridge = p in (L[1], R[0])
        c.node(*p, "", r=15, fill=ORANGE if bridge else LIGHT, stroke=ORANGE if bridge else BLUE)
    c.text(390, 282, "Close friends know each other, so they tend to know the same things.", size=13, fill=MUTED)
    c.text(390, 303, "The weak tie is how news gets from one circle to the other.", size=13, fill=MUTED)
    meta = dict(chapter=2, caption="Granovetter's bridge. Within each circle everyone is tied to everyone, so information circulates but is mostly redundant; the single weak tie is the route for new information.",
                alt="Two outlined clusters, each with four fully connected nodes drawn with thick gray lines. A single dashed orange line links one orange node in the left cluster to one orange node in the right cluster.",
                data={"circle1": 4, "circle2": 4, "bridge": "one weak tie"})
    return c, meta


def structural_hole():
    c = Canvas(800, 360, "Redundant contacts and a structural hole",
               "Left: a person with four contacts who all know each other. Right: the same person with four contacts split into two pairs, the pairs not connected to each other.")
    off = [(-75, -75), (75, -75), (-75, 75), (75, 75)]
    for panel, cx in enumerate((210, 590)):
        ego = (cx, 180)
        pos = [(cx + dx, 180 + dy) for dx, dy in off]
        if panel == 0:
            for a, b in combinations(range(4), 2):
                c.edge(pos[a], pos[b], ra=16, rb=16, width=1.8, color=SKY)
        else:
            for a, b in ((0, 2), (1, 3)):
                c.edge(pos[a], pos[b], ra=16, rb=16, width=1.8, color=SKY)
            c.edge(pos[0], pos[1], ra=16, rb=16, width=1.4, color=FAINT, dash="5 5")
            c.edge(pos[2], pos[3], ra=16, rb=16, width=1.4, color=FAINT, dash="5 5")
            c.text(cx, 96, "no ties", size=11, fill=MUTED, italic=True)
        for p in pos:
            c.edge(ego, p, ra=20, rb=16, width=2.4, color=INK)
        for p in pos:
            c.node(*p, "", r=16, fill=LIGHT, stroke=BLUE)
        c.node(*ego, "Ego", r=22, fill=ORANGE, stroke=ORANGE, size=12)
    c.caption(210, 36, "Closed: the contacts all know each other")
    c.caption(590, 36, "Open: two groups that don't know each other")
    c.text(210, 318, "Redundant: everyone hears the same things.", size=13, fill=MUTED)
    c.text(210, 338, "Good for trust and enforcement (Coleman).", size=13, fill=MUTED)
    c.text(590, 318, "Ego spans a structural hole: new, non-redundant", size=13, fill=MUTED)
    c.text(590, 338, "information and control (Burt).", size=13, fill=MUTED)
    meta = dict(chapter=2, caption="Both egos have four contacts. On the left the contacts are all tied to each other (closure). On the right ego is the only link between two groups (a structural hole).",
                alt="Two diagrams of an orange node with four contacts. On the left the four contacts are connected to each other. On the right the contacts form two separate pairs with no ties between the pairs.",
                data={"left": "ego with 4 mutually tied contacts", "right": "ego with 2 pairs of contacts, no tie between pairs"})
    return c, meta


def homophily():
    c = Canvas(840, 360, "Homophily: ties follow group",
               "Two layouts of the same ten people in two groups. On the left most ties cross between groups; on the right nearly all ties stay within a group.")
    A = [(70, 100), (150, 75), (120, 165), (70, 230), (150, 255)]
    B = [(250, 100), (330, 75), (300, 165), (250, 230), (330, 255)]
    mixed = [("A0", "B0"), ("A1", "B1"), ("A2", "B2"), ("A0", "A2"), ("A3", "B3"), ("A3", "B4"),
             ("A4", "B4"), ("B0", "B2"), ("A1", "B2")]
    homo = [("A0", "A1"), ("A0", "A2"), ("A1", "A2"), ("A2", "A3"), ("A3", "A4"), ("A2", "A4"),
            ("B0", "B1"), ("B0", "B2"), ("B1", "B2"), ("B2", "B3"), ("B3", "B4"), ("B2", "B4"),
            ("A2", "B2")]
    counts = []
    for panel, (x0, edges, title) in enumerate(((20, mixed, "Ties ignore group"),
                                                (440, homo, "Ties follow group"))):
        pos = {f"A{i}": (x0 + p[0], p[1]) for i, p in enumerate(A)}
        pos.update({f"B{i}": (x0 + p[0], p[1]) for i, p in enumerate(B)})
        cross = sum(1 for a, b in edges if a[0] != b[0])
        counts.append((cross, len(edges)))
        for a, b in edges:
            crosses = a[0] != b[0]
            c.edge(pos[a], pos[b], ra=14, rb=14, width=2.2, color=RED if crosses else MUTED,
                   dash="6 4" if crosses else None)
        for k, p in pos.items():
            if k[0] == "A":
                c.node(*p, "", r=14, fill=LIGHT, stroke=BLUE)
            else:
                c.node(*p, "", r=14, fill="#fdf3dc", stroke=ORANGE, shape="square")
        c.caption(x0 + 190, 34, title)
        c.text(x0 + 190, 300, f"{cross} of {len(edges)} ties cross between groups", size=14, fill=MUTED)
    c.node(300, 338, "", r=8, fill=LIGHT, stroke=BLUE)
    c.text(316, 343, "Group 1", size=12, anchor="start", fill=MUTED)
    c.node(420, 338, "", r=8, fill="#fdf3dc", stroke=ORANGE, shape="square")
    c.text(436, 343, "Group 2", size=12, anchor="start", fill=MUTED)
    c.edge((520, 338), (556, 338), ra=0, rb=0, width=2.2, color=RED, dash="6 4")
    c.text(564, 343, "tie between groups", size=12, anchor="start", fill=MUTED)
    meta = dict(chapter=2, caption="Homophily in one picture. The same ten people and the same two groups; what changes is where the ties go. To claim a preference, compare against what group sizes alone would produce.",
                alt="Two network diagrams of ten people, five circles and five squares. In the left diagram seven of nine ties cross between the shapes. In the right diagram only one of thirteen ties crosses.",
                data={"mixed": {"cross": counts[0][0], "total": counts[0][1]},
                      "homophilous": {"cross": counts[1][0], "total": counts[1][1]}})
    return c, meta


def small_world():
    n = 16
    ring_edges = sorted({tuple(sorted((i, (i + d) % n))) for i in range(n) for d in (1, 2)})
    shortcuts = [(0, 8), (4, 12), (2, 6)]
    sw_edges = ring_edges + shortcuts
    d0, d1 = bfs_mean_distance(n, ring_edges), bfs_mean_distance(n, sw_edges)
    c = Canvas(780, 400, "A ring of neighbors, with and without shortcuts",
               f"Two rings of sixteen nodes, each tied to its four nearest neighbors. The second has three long-range shortcuts. Average distance falls from {d0:.2f} to {d1:.2f} steps.")
    for cx, extra, title, d in ((200, [], "A ring of neighbors", d0),
                                (580, shortcuts, "The same ring plus three shortcuts", d1)):
        pts = ring(cx, 190, 120, n)
        for a, b in ring_edges:
            c.edge(pts[a], pts[b], ra=5, rb=5, width=1.6, color=MUTED)
        for a, b in extra:
            c.edge(pts[a], pts[b], ra=5, rb=5, width=2.8, color=ORANGE)
        for p in pts:
            c.node(*p, "", r=5.5, fill=LIGHT, stroke=BLUE, sw=1.6)
        c.caption(cx, 30, title)
        c.text(cx, 352, f"average distance: {d:.2f} steps", size=14, fill=MUTED)
    c.text(390, 382, "Clustering stays high; three shortcuts are enough to shrink the distances (Watts and Strogatz).",
           size=13, fill=MUTED)
    meta = dict(chapter=2, caption="The small-world effect. Both rings are equally clustered; adding three long-range shortcuts cuts the average distance between people noticeably.",
                alt="Two circular networks of sixteen nodes. The right one has three extra straight orange lines crossing the circle. Captions give the average distance in each.",
                data={"nodes": n, "ring_edges": [list(e) for e in ring_edges],
                      "shortcuts": [list(e) for e in shortcuts],
                      "average_distance": {"ring": round(d0, 3), "with_shortcuts": round(d1, 3)}})
    return c, meta


# ---------------------------------------------------------------- chapter 3
ADVICE = [("Ana", "Ben"), ("Ana", "Chloe"), ("Ben", "Chloe"), ("Chloe", "Ana"), ("Dev", "Ana"),
          ("Dev", "Chloe"), ("Eli", "Chloe")]


def three_formats():
    c = Canvas(900, 580, "One network, three ways of writing it down",
               "A directed advice network of five people drawn as a picture, as a five by five adjacency matrix, as an edge list with seven rows, and as an adjacency list.")
    pos = {"Ana": (70, 100), "Ben": (290, 100), "Chloe": (180, 190), "Dev": (70, 290), "Eli": (290, 290)}
    c.caption(180, 30, "As a picture")
    for a, b in ADVICE:
        mutual = (b, a) in ADVICE
        c.edge(pos[a], pos[b], ra=24, rb=24, directed=True, width=2, color=MUTED, curve=14 if mutual else 0)
    for k, p in pos.items():
        c.node(*p, k, r=24, fill=LIGHT, stroke=BLUE, size=12)
    # matrix
    x0, y0, cell = 520, 80, 46
    c.caption(640, 30, "As an adjacency matrix")
    c.text(640, 50, "row = who goes to; column = who is asked", size=12, fill=MUTED)
    short = ["Ana", "Ben", "Chl", "Dev", "Eli"]
    for i, n in enumerate(NAMES):
        c.text(x0 - 8, y0 + i * cell + cell / 2 + 5, short[i], size=12, anchor="end", fill=MUTED)
        c.text(x0 + i * cell + cell / 2, y0 - 8, short[i], size=12, fill=MUTED)
        for j, m in enumerate(NAMES):
            on = (n, m) in ADVICE
            c.rect(x0 + j * cell, y0 + i * cell, cell, cell, fill=BLUE if on else PAPER, stroke=FAINT, sw=1)
            c.text(x0 + j * cell + cell / 2, y0 + i * cell + cell / 2 + 5, "1" if on else "0", size=14,
                   weight="700" if on else "400", fill=PAPER if on else MUTED)
    # edge list
    c.caption(130, 352, "As an edge list")
    c.text(60, 380, "from", size=13, anchor="start", mono=True, weight="700")
    c.text(150, 380, "to", size=13, anchor="start", mono=True, weight="700")
    for i, (a, b) in enumerate(ADVICE):
        c.text(60, 402 + i * 20, a, size=13, anchor="start", mono=True)
        c.text(150, 402 + i * 20, b, size=13, anchor="start", mono=True)
    # adjacency list
    c.caption(640, 352, "As an adjacency list")
    for i, n in enumerate(NAMES):
        outs = ", ".join(b for a, b in ADVICE if a == n)
        c.text(520, 380 + i * 22, f"{n}:", size=13, anchor="start", mono=True, weight="700")
        c.text(590, 380 + i * 22, outs, size=13, anchor="start", mono=True)
    meta = dict(chapter=3, caption="The same five-person advice network in the three standard formats. They hold the same information; they differ in what they are good at.",
                alt="A directed network of five people shown as a picture, with the same ties as a five by five matrix of ones and zeros, as a seven-row edge list, and as a list of who each person goes to.",
                data={"nodes": NAMES, "edges": [list(e) for e in ADVICE]})
    return c, meta


def two_mode():
    events = {"P1": ["E1", "E2"], "P2": ["E1"], "P3": ["E2", "E3"], "P4": ["E3"]}
    c = Canvas(900, 380, "A two-mode network and its one-mode projection",
               "Left: four people linked to the three events they attended. Right: the four people linked to each other when they attended an event together, each tie labeled with the shared event.")
    ppos = {f"P{i + 1}": (80, 90 + i * 70) for i in range(4)}
    epos = {f"E{i + 1}": (290, 125 + i * 70) for i in range(3)}
    c.caption(185, 30, "Two kinds of nodes")
    for p, evs in events.items():
        for e in evs:
            c.edge(ppos[p], epos[e], ra=17, rb=17, width=2, color=MUTED)
    for k, p in ppos.items():
        c.node(*p, k, r=17, fill=LIGHT, stroke=BLUE)
    for k, p in epos.items():
        c.node(*p, k, r=17, fill="#fdf3dc", stroke=ORANGE, shape="square")
    c.text(80, 355, "people", size=12, fill=BLUE, weight="600")
    c.text(290, 355, "events", size=12, fill=ORANGE, weight="600")
    c.arrow((380, 195), (460, 195), color=MUTED, width=2.5)
    c.text(420, 176, "project", size=13, fill=MUTED)
    q = {"P2": (540, 270), "P1": (620, 130), "P3": (770, 130), "P4": (850, 270)}
    shared = []
    for a, b in combinations(events, 2):
        both = sorted(set(events[a]) & set(events[b]))
        if both:
            shared.append((a, b, both[0]))
    c.caption(700, 30, "People linked by shared events")
    for a, b, e in shared:
        c.edge(q[a], q[b], ra=17, rb=17, width=2.4, color=MUTED, label=e)
    for k, p in q.items():
        c.node(*p, k, r=17, fill=LIGHT, stroke=BLUE)
    c.text(700, 322, "Who was together is kept;", size=13, fill=MUTED)
    c.text(700, 342, "which event is mostly lost.", size=13, fill=MUTED)
    meta = dict(chapter=3, caption="Two-mode data (people and events) and its one-mode projection (people tied by shared events), after the idea of the duality of persons and groups.",
                alt="Left: people P1 to P4 each linked to events E1 to E3. Right: a chain of people P2, P1, P3, P4 where each neighboring pair is tied and the tie is labeled with the event they share.",
                data={"attendance": events, "projection": [list(s) for s in shared]})
    return c, meta


def boundary():
    c = Canvas(780, 380, "Where we draw the boundary",
               "A network with a dashed rectangle around most of it. Two nodes just inside the boundary have ties that cross it to nodes outside, which are not in the data.")
    inside = {"X1": (130, 130), "X2": (230, 100), "X3": (220, 200), "X4": (120, 235),
              "Y1": (350, 140), "Y2": (350, 235)}
    outside = {"Z1": (540, 110), "Z2": (630, 190), "Z3": (540, 270)}
    c.halo(60, 60, 340, 245, BLUE, "What we collected", dash="9 6")
    for a, b in [("X1", "X2"), ("X1", "X3"), ("X2", "X3"), ("X1", "X4"), ("X3", "X4"), ("X3", "Y1"),
                 ("X3", "Y2"), ("Y1", "Y2")]:
        c.edge(inside[a], inside[b], ra=15, rb=15, width=2.4, color=MUTED)
    for a, b in [("Z1", "Z2"), ("Z2", "Z3"), ("Z1", "Z3")]:
        c.edge(outside[a], outside[b], ra=15, rb=15, width=2, color=FAINT)
    for a, b in [("Y1", "Z1"), ("Y2", "Z3"), ("Y1", "Z2")]:
        pa = inside[a]
        pb = outside[b]
        c.edge(pa, pb, ra=15, rb=15, width=2.2, color=RED, dash="6 5")
    for k, p in inside.items():
        near = k.startswith("Y")
        c.node(*p, "", r=15, fill=ORANGE if near else LIGHT, stroke=ORANGE if near else BLUE)
    for k, p in outside.items():
        c.node(*p, "", r=15, fill=PAPER, stroke=MUTED, sw=2)
    c.text(600, 70, "outside the boundary:", size=13, fill=MUTED, weight="600")
    c.text(600, 90, "not in the data", size=13, fill=MUTED)
    c.text(450, 330, "Ties that cross the line are lost", size=13, fill=RED, weight="600")
    c.text(390, 358, "The orange nodes look less connected than they are, and every measure of them inherits that.",
           size=13, fill=MUTED)
    meta = dict(chapter=3, caption="Boundary choices change results. Nodes near the cut lose ties to people outside the data, so their measures understate how connected they are.",
                alt="A network inside a dashed outline. Two orange nodes on its right edge have dashed red ties leading out to three gray nodes outside the outline, which are not part of the data.",
                data={"inside": list(inside), "outside": list(outside),
                      "cut_ties": [["Y1", "Z1"], ["Y2", "Z3"], ["Y1", "Z2"]]})
    return c, meta


def levels():
    c = Canvas(900, 270, "Five levels of analysis",
               "The same small network shown five times, with a different part highlighted each time: one node, one pair, one triangle, one cluster, and the whole network.")
    base = [(30, 40), (80, 20), (120, 60), (75, 80), (30, 110), (110, 115), (145, 100)]
    edges = [(0, 1), (1, 2), (1, 3), (0, 3), (2, 3), (0, 4), (3, 4), (3, 5), (5, 6), (2, 6)]
    titles = [("Node", "how many ties does it have?"), ("Dyad", "is the tie mutual?"),
              ("Triad", "do friends of friends connect?"), ("Group", "which cluster is this?"),
              ("Whole network", "how dense is it overall?")]
    hl_nodes = [{3}, {3, 5}, {0, 1, 3}, {0, 1, 2, 3, 4}, set(range(7))]
    hl_edges = [set(), {(3, 5)}, {(0, 1), (1, 3), (0, 3)}, {e for e in edges if e[0] <= 4 and e[1] <= 4},
                set(edges)]
    for i in range(5):
        x0, y0 = 28 + i * 176, 60
        pos = [(x0 + x, y0 + y) for x, y in base]
        if i in (2, 3):
            pts = [pos[k] for k in sorted(hl_nodes[i])]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            c.halo(min(xs) - 22, min(ys) - 22, max(xs) - min(xs) + 44, max(ys) - min(ys) + 44, ORANGE, dash="5 4")
        for e in edges:
            on = e in hl_edges[i]
            c.edge(pos[e[0]], pos[e[1]], ra=9, rb=9, width=3.4 if on else 1.8,
                   color=ORANGE if on and i != 4 else (BLUE if on else FAINT))
        for k, p in enumerate(pos):
            on = k in hl_nodes[i]
            col = BLUE if i == 4 else ORANGE
            c.node(*p, "", r=9, fill=col if on else PAPER, stroke=col if on else MUTED, sw=1.8)
        c.caption(x0 + 70, 215, titles[i][0])
        c.text(x0 + 70, 236, titles[i][1], size=11.5, fill=MUTED)
    meta = dict(chapter=3, caption="Levels of analysis on one network. Each question lives at one level; a statement about a node is not a statement about the whole network.",
                alt="Five copies of the same seven-node network. Each highlights something different in orange: a single node, a pair of tied nodes, a triangle, a five-node cluster, and finally the whole network in blue.",
                data={"nodes": 7, "edges": [list(e) for e in edges], "levels": [t[0] for t in titles]})
    return c, meta


FIGURES = {
    "two-teams": two_teams, "habit": habit, "dyad-triad": dyad_triad,
    "balance-triads": balance_triads, "two-camps": two_camps, "weak-ties": weak_ties,
    "structural-hole": structural_hole, "homophily": homophily, "small-world": small_world,
    "three-formats": three_formats, "two-mode": two_mode, "boundary": boundary, "levels": levels,
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    registry = []
    for fid, fn in FIGURES.items():
        canvas, meta = fn()
        (OUT / f"{fid}.svg").write_text(canvas.svg())
        registry.append({"id": f"fig-{fid}", "file": f"figures/{fid}.svg", "width": canvas.w,
                         "height": canvas.h, **meta})
    (OUT / "figures.json").write_text(json.dumps({"schema": "net-books/figures/1", "figures": registry},
                                                 indent=2, ensure_ascii=False) + "\n")
    if "--snippets" in sys.argv:
        for f in registry:
            print(f"ch{f['chapter']}: ![{f['caption']}](../{f['file']}){{#{f['id']} fig-alt=\"{f['alt']}\"}}\n")
    print(f"wrote {len(registry)} figures to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

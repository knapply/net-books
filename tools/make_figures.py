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
import math
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fig_layout import community_graph, crossings, distances, fit, stress_layout  # noqa: E402
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


# ---------------------------------------------------------------- chapter 5
GROUP_STYLE = [(BLUE, "circle"), (ORANGE, "square"), (PURPLE, "diamond")]


def _shuffled_ring(n, cx, cy, r, seed):
    import random
    order = list(range(n))
    random.Random(seed).shuffle(order)
    pts = ring(cx, cy, r, n)
    pos = [None] * n
    for slot, node in enumerate(order):
        pos[node] = pts[slot]
    return pos


def _draw_graph(c, pos, edges, groups, r=8, width=1.4, color="#9ca3af"):
    for a, b in edges:
        c.edge(pos[a], pos[b], ra=r, rb=r, width=width, color=color)
    for i, p in enumerate(pos):
        col, shape = GROUP_STYLE[groups[i]]
        c.node(*p, "", r=r, fill=col + "33", stroke=col, shape=shape, sw=2)


def layout_matters():
    import random
    n, edges, groups = community_graph([6, 6, 6], 0.7, 0.04, 3)
    c = Canvas(900, 330, "One network, three layouts",
               "The same eighteen-person network drawn with random positions, with people placed around a circle in the order they appear in the data, and with a stress layout.")
    w = 260
    rnd = random.Random(5)
    pos_r = fit([(rnd.uniform(0, 1), rnd.uniform(0, 1)) for _ in range(n)], 20, 60, w, 220)
    pos_c = _shuffled_ring(n, 20 + w / 2 + 300, 170, 105, 2)
    pos_s = fit(stress_layout(n, edges), 20 + 2 * 300, 60, w, 220)
    panels = [("Random positions", pos_r), ("Around a circle", pos_c), ("Stress layout", pos_s)]
    counts = []
    for k, (title, pos) in enumerate(panels):
        x0 = 20 + k * 300
        if title == "Around a circle":
            pass
        c.caption(x0 + w / 2, 30, title)
        _draw_graph(c, pos, edges, groups)
        cr = crossings(pos, edges)
        counts.append(cr)
        c.text(x0 + w / 2, 304, f"{cr} edge crossings", size=13, fill=MUTED)
    meta = dict(chapter=5,
                caption="One network, three pictures. Nothing about the data changed; only the positions did. Only the last layout lets the three groups show.",
                alt="Three drawings of the same eighteen nodes, which belong to three groups drawn as circles, squares and diamonds. In the first, positions are random and ties form a tangle. In the second, nodes sit on a circle and many ties cross the middle. In the third, each group forms its own tight cluster with a few ties between the clusters.",
                data={"nodes": n, "edges": [list(e) for e in edges], "groups": groups, "crossings": counts})
    return c, meta


def distance_lies():
    n, edges, groups = community_graph([6, 6, 6], 0.7, 0.04, 3)
    d = distances(n, edges)
    pos_c = _shuffled_ring(n, 150, 175, 105, 2)
    import math
    best = None
    for i in range(n):
        for j in range(i + 1, n):
            gap = d[i][j] - 0
            near = math.dist(pos_c[i], pos_c[j])
            if d[i][j] >= 3 and (best is None or near < best[0]):
                best = (near, i, j)
    _, a, b = best
    c = Canvas(780, 340, "Close on the page is not close in the network",
               "Two drawings of the same network, each with one pair of people highlighted.")
    c.caption(150, 30, "Around a circle")
    _draw_graph(c, pos_c, edges, groups)
    for k in (a, b):
        c.node(*pos_c[k], "", r=11, fill="none", stroke=RED, sw=3)
    c.edge(pos_c[a], pos_c[b], ra=11, rb=11, width=2.4, color=RED, dash="5 4")
    c.text(150, 306, "neighbors on the page,", size=13, fill=MUTED)
    c.text(150, 324, f"{int(d[a][b])} steps apart in the network", size=13, fill=MUTED)
    pos_s = fit(stress_layout(n, edges), 420, 60, 330, 220)
    c.caption(585, 30, "Stress layout")
    _draw_graph(c, pos_s, edges, groups)
    for k in (a, b):
        c.node(*pos_s[k], "", r=11, fill="none", stroke=RED, sw=3)
    c.edge(pos_s[a], pos_s[b], ra=11, rb=11, width=2.4, color=RED, dash="5 4")
    c.text(585, 306, "the same pair, now drawn far apart,", size=13, fill=MUTED)
    c.text(585, 324, "which is how far apart they are", size=13, fill=MUTED)
    meta = dict(chapter=5,
                caption="Distance on the page can mislead. A stress layout tries to make distance on the page match steps in the network; a circle ignores it.",
                alt="Left: a circular drawing of an eighteen-node network with two nodes ringed in red that sit next to each other on the circle, joined by a dashed red line. Right: a stress-layout drawing of the same network with the same two nodes ringed in red, now far apart.",
                data={"pair": [a, b], "graph_distance": int(d[a][b])})
    return c, meta


def hairball_matrix():
    n, edges, groups = community_graph([8, 8, 8], 0.65, 0.04, 11)
    c = Canvas(900, 400, "A hairball and the same network as a matrix",
               "A twenty-four person network as a node-link drawing on a circle and as a sorted adjacency matrix.")
    pos = _shuffled_ring(n, 220, 205, 150, 4)
    c.caption(220, 30, "As a node-link drawing")
    _draw_graph(c, pos, edges, groups, r=7, width=1.1)
    c.text(220, 385, f"{len(edges)} ties, and the groups are hard to see", size=13, fill=MUTED)
    cell, x0, y0 = 12.5, 530, 60
    c.caption(x0 + cell * n / 2, 30, "As a matrix, sorted by group")
    es = {tuple(sorted(e)) for e in edges}
    order = sorted(range(n), key=lambda i: (groups[i], i))
    for ri, i in enumerate(order):
        for ci, j in enumerate(order):
            on = (min(i, j), max(i, j)) in es and i != j
            col = GROUP_STYLE[groups[i]][0] if (on and groups[i] == groups[j]) else (INK if on else None)
            c.rect(x0 + ci * cell, y0 + ri * cell, cell, cell, fill=(col or "#ffffff"), stroke="#e5e7eb", sw=0.6)
    start = 0
    for g in range(3):
        size = groups.count(g)
        c.rect(x0 + start * cell, y0 + start * cell, size * cell, size * cell, stroke=INK, sw=1.6)
        start += size
    c.text(x0 + cell * n / 2, 385, "colored blocks: ties inside groups. dark squares: ties between groups", size=13, fill=MUTED)
    meta = dict(chapter=5,
                caption="The same network twice. When a node-link drawing turns into a hairball, a matrix with rows sorted by group shows the block structure immediately.",
                alt="Left: a tangled circular drawing of twenty-four nodes in three groups. Right: a twenty-four by twenty-four grid of squares, with three dense blocks along the diagonal outlined in black and very few filled squares outside them.",
                data={"nodes": n, "edges": [list(e) for e in edges], "groups": groups})
    return c, meta


def encodings():
    n, edges, groups = community_graph([5, 5], 0.8, 0.08, 6)
    deg = [sum(1 for e in edges if i in e) for i in range(n)]
    c = Canvas(900, 360, "Four ways to show what a node or tie is like",
               "A ten-node network where node size shows number of ties, shape and color show group, and line thickness shows tie strength. Callouts name each channel.")
    pos = fit(stress_layout(n, edges), 30, 40, 520, 270)
    import random
    rnd = random.Random(2)
    strength = {e: rnd.choice([1, 1, 2, 4]) for e in edges}
    for e in edges:
        c.edge(pos[e[0]], pos[e[1]], ra=10, rb=10, width=1 + strength[e] * 1.3, color="#9ca3af")
    for i, p in enumerate(pos):
        col, shape = GROUP_STYLE[groups[i]]
        c.node(*p, "", r=7 + deg[i] * 2.2, fill=col + "33", stroke=col, shape=shape, sw=2)
    rows = [("Size", "number of ties", "bigger node, more ties"),
            ("Shape and color", "group", "both, so it reads in greyscale"),
            ("Thickness", "tie strength", "thicker line, stronger tie"),
            ("Position", "closeness in the network", "set by the layout, not by you")]
    y = 70
    for head, what, note in rows:
        c.text(600, y, head, size=15, anchor="start", weight="700")
        c.text(600, y + 20, what, size=13, anchor="start", fill=INK)
        c.text(600, y + 38, note, size=12, anchor="start", fill=MUTED)
        y += 72
    meta = dict(chapter=5,
                caption="Four visual channels and what each can carry. Pick one idea per channel and say what it is in a legend.",
                alt="A ten-node network drawn in two clusters. Larger nodes have more ties. Circles and squares in different colors mark the two groups. Thicker lines mark stronger ties. A list on the right names each channel and what it encodes.",
                data={"nodes": n, "edges": [list(e) for e in edges], "groups": groups, "degree": deg,
                      "strength": [strength[e] for e in edges]})
    return c, meta


# ---------------------------------------------------------------- chapter 6
KITE_NAMES = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jo"]
KITE_EDGES = [(0, 1), (0, 2), (0, 3), (0, 5), (1, 3), (1, 4), (1, 6), (2, 3), (2, 5), (3, 4),
              (3, 5), (3, 6), (4, 6), (5, 6), (5, 7), (6, 7), (7, 8), (8, 9)]


def _kite_measures():
    n = len(KITE_NAMES)
    d = distances(n, KITE_EDGES)
    adj = {i: set() for i in range(n)}
    for a, b in KITE_EDGES:
        adj[a].add(b)
        adj[b].add(a)
    degree = [len(adj[i]) for i in range(n)]
    close = [(n - 1) / sum(d[i]) for i in range(n)]
    sigma = []
    for s_ in range(n):
        cnt = {s_: 1}
        for u in sorted(range(n), key=lambda x: d[s_][x]):
            if u != s_:
                cnt[u] = sum(cnt[v] for v in adj[u] if d[s_][v] == d[s_][u] - 1)
        sigma.append(cnt)
    between = [0.0] * n
    for a in range(n):
        for b in range(a + 1, n):
            for v in range(n):
                if v not in (a, b) and d[a][v] + d[v][b] == d[a][b]:
                    between[v] += sigma[a][v] * sigma[v][b] / sigma[a][b]
    x = [1.0] * n
    for _ in range(500):
        y = [sum(x[j] for j in adj[i]) for i in range(n)]
        m = max(y)
        x = [v / m for v in y]
    return degree, close, between, x


def four_centralities():
    degree, close, between, eigen = _kite_measures()
    n = len(KITE_NAMES)
    c = Canvas(920, 300, "Four answers to who is central",
               "The same ten-person network drawn four times. In each, node size shows one measure and the largest node is highlighted.")
    panels = [("Degree", degree), ("Closeness", close), ("Betweenness", between), ("Eigenvector", eigen)]
    base = fit(stress_layout(n, KITE_EDGES, seed=3), 0, 0, 190, 170)
    tops = []
    for k, (title, vals) in enumerate(panels):
        x0, y0 = 15 + k * 225, 60
        pos = [(x0 + p[0], y0 + p[1]) for p in base]
        lo, hi = min(vals), max(vals)
        top = max(range(n), key=lambda i: vals[i])
        tied = [i for i in range(n) if abs(vals[i] - vals[top]) < 1e-9]
        tops.append([KITE_NAMES[i] for i in tied])
        c.caption(x0 + 95, 30, title)
        for a, b in KITE_EDGES:
            c.edge(pos[a], pos[b], ra=6, rb=6, width=1.4, color="#9ca3af")
        for i, p in enumerate(pos):
            r = 5 + 12 * (vals[i] - lo) / ((hi - lo) or 1)
            on = i in tied
            c.node(*p, "", r=r, fill=ORANGE if on else "#cfe5f3", stroke=ORANGE if on else BLUE, sw=2)
        c.text(x0 + 95, 268, "most central: " + " and ".join(KITE_NAMES[i] for i in tied), size=13, fill=MUTED)
    meta = dict(chapter=6,
                caption="One network, four rankings. Each measure answers a different question, so each picks a different person as most central.",
                alt="Four copies of the same ten-node network. In the degree and eigenvector panels the node Dev, near the middle of the left cluster, is the largest. In the closeness panel two nodes, Fay and Gus, are largest and equal. In the betweenness panel Hana, on the narrow link leading out to two more people, is largest.",
                data={"names": KITE_NAMES, "edges": [list(e) for e in KITE_EDGES], "degree": degree,
                      "closeness": [round(v, 4) for v in close], "betweenness": [round(v, 2) for v in between],
                      "eigenvector": [round(v, 4) for v in eigen], "most_central": tops})
    return c, meta


def betweenness_paths():
    n = len(KITE_NAMES)
    d = distances(n, KITE_EDGES)
    src = 9  # Jo
    on_path = set()
    for a, b in KITE_EDGES:
        for u, v in ((a, b), (b, a)):
            if d[src][v] == d[src][u] + 1:
                on_path.add((min(a, b), max(a, b)))
    pos = fit(stress_layout(n, KITE_EDGES, seed=3), 20, 40, 520, 250)
    c = Canvas(900, 340, "Shortest routes from Jo",
               "The ten-person network with the shortest routes from Jo to everyone else drawn thick and orange, all passing through Ivo and Hana.")
    for a, b in KITE_EDGES:
        on = (a, b) in on_path
        c.edge(pos[a], pos[b], ra=14, rb=14, width=4 if on else 1.4, color=ORANGE if on else "#c7ccd4")
    for i, p in enumerate(pos):
        key = i in (9, 8, 7)
        c.node(*p, KITE_NAMES[i][:2], r=15, fill=ORANGE + "33" if key else PAPER,
               stroke=ORANGE if key else MUTED, sw=2, size=11)
    c.text(600, 90, "Jo can reach everyone,", size=15, anchor="start", weight="700")
    c.text(600, 112, "but every route starts", size=15, anchor="start", weight="700")
    c.text(600, 134, "with Ivo and then Hana.", size=15, anchor="start", weight="700")
    c.lines(600, 175, ["Remove Ivo or Hana and Jo", "is cut off from the rest.", "", "That is what high betweenness",
                       "means: not many friends, but a", "position everyone else's routes", "depend on."],
            size=13, fill=MUTED)
    meta = dict(chapter=6,
                caption="Betweenness is about routes. Every shortest route from Jo to anyone else passes through Ivo and Hana, so they sit in between even though neither has many ties.",
                alt="A ten-node network. Thick orange lines mark the shortest routes starting at the node Jo: Jo to Ivo, Ivo to Hana, then Hana to the two nodes Fay and Gus, and on from them to the rest. Thin gray lines mark ties not on those routes.",
                data={"source": KITE_NAMES[src], "edges_on_shortest_routes": [list(e) for e in sorted(on_path)]})
    return c, meta


def centralization():
    c = Canvas(900, 330, "Centralization: how unevenly ties are spread",
               "Three ten-person networks: a star, the kite network, and a ring, labeled with their degree centralization.")
    n = 10
    graphs = []
    graphs.append(("A star", [(0, i) for i in range(1, n)], ring(0, 0, 1, n - 1), "star"))
    graphs.append(("The friendship network", KITE_EDGES, None, "kite"))
    graphs.append(("A ring", [(i, (i + 1) % n) for i in range(n)], ring(0, 0, 1, n), "ring"))
    data = []
    for k, (title, edges, _, kind) in enumerate(graphs):
        x0 = 15 + k * 295
        if kind == "star":
            pts = [(0, 0)] + ring(0, 0, 1, n - 1)
        elif kind == "ring":
            pts = ring(0, 0, 1, n)
        else:
            pts = stress_layout(n, edges, seed=3)
        pos = fit(pts, x0, 50, 250, 200)
        deg = [sum(1 for e in edges if i in e) for i in range(n)]
        cen = sum(max(deg) - x for x in deg) / ((n - 1) * (n - 2))
        data.append({"graph": title, "centralization": round(cen, 3)})
        c.caption(x0 + 125, 30, title)
        for a, b in edges:
            c.edge(pos[a], pos[b], ra=8, rb=8, width=1.5, color="#9ca3af")
        for i, p in enumerate(pos):
            hub = deg[i] == max(deg) and kind != "ring"
            c.node(*p, "", r=8 + 1.2 * deg[i] if kind != "ring" else 9, fill=ORANGE if hub else "#cfe5f3",
                   stroke=ORANGE if hub else BLUE, sw=2)
        c.text(x0 + 125, 285, f"degree centralization {cen:.2f}", size=14, weight="600")
    c.text(450, 316, "0 means ties are spread evenly; 1 means one person holds them all.", size=13, fill=MUTED)
    meta = dict(chapter=6,
                caption="Centralization summarizes a whole network: how far the most central person stands above everyone else, compared with the most extreme case.",
                alt="Three ten-node networks side by side. A star with one hub joined to nine others is labeled 1.00. The friendship network with one slightly larger hub is labeled 0.33. A ring in which everyone has two ties is labeled 0.00.",
                data=data)
    return c, meta


def in_out_bars():
    names = ["Ana", "Ben", "Chloe", "Dev", "Eli"]
    out = [2, 1, 1, 2, 1]
    inn = [2, 1, 4, 0, 0]
    c = Canvas(780, 330, "Going to and being gone to",
               "A bar chart of out-degree and in-degree for the five-person advice network.")
    x0, y0, h = 90, 40, 220
    unit = h / 4.5
    c.text(24, y0 + h / 2, "ties", size=13, anchor="middle", fill=MUTED)
    for t in range(0, 5):
        y = y0 + h - t * unit
        c.edge((x0 - 10, y), (740, y), ra=0, rb=0, width=1, color="#e5e7eb")
        c.text(x0 - 18, y + 4, str(t), size=12, anchor="end", fill=MUTED)
    for i, nm in enumerate(names):
        gx = x0 + 20 + i * 130
        for j, (vals, col, lab) in enumerate([(out, BLUE, "goes to"), (inn, ORANGE, "comes to them")]):
            bh = vals[i] * unit
            c.rect(gx + j * 44, y0 + h - bh, 38, bh, fill=col + ("cc" if j == 0 else "ff"), stroke=col, sw=1.6,
                   dash=None if j == 0 else "4 3")
            c.text(gx + j * 44 + 19, y0 + h - bh - 6, str(vals[i]), size=13, weight="600")
        c.text(gx + 41, y0 + h + 22, nm, size=14, weight="600")
    c.rect(300, 305, 14, 14, fill=BLUE + "cc", stroke=BLUE)
    c.text(320, 317, "goes to others (out-degree)", size=12, anchor="start", fill=MUTED)
    c.rect(520, 305, 14, 14, fill=ORANGE, stroke=ORANGE, dash="3 2")
    c.text(540, 317, "others come to them (in-degree)", size=12, anchor="start", fill=MUTED)
    meta = dict(chapter=6,
                caption="In a directed network, activity (going to others) and prestige (being gone to) are different things. Chloe is sought out by everyone and seeks out one person; Dev and Eli seek out others but nobody seeks them.",
                alt="A grouped bar chart for Ana, Ben, Chloe, Dev and Eli. Out-degree bars are solid blue: 2, 1, 1, 2, 1. In-degree bars are dashed orange: 2, 1, 4, 0, 0. Chloe's in-degree bar is the tallest.",
                data={"names": names, "out_degree": out, "in_degree": inn})
    return c, meta


# ---------------------------------------------------------------- chapter 7
def walks_paths():
    c = Canvas(900, 300, "Walks, paths and shortest paths",
               "The same five-person network shown three times with a different route from Ana to Eli highlighted: a walk that doubles back, a path that never repeats a person, and a shortest path.")
    pts = {"A": (30, 100), "B": (110, 100), "C": (170, 40), "D": (170, 160), "E": (250, 100)}
    edges = [("A", "B"), ("B", "C"), ("C", "D"), ("B", "D"), ("D", "E")]
    routes = [("A walk", ["A", "B", "C", "B", "D", "E"], "anything goes: B is visited twice", "5 steps"),
              ("A path", ["A", "B", "C", "D", "E"], "no person repeats", "4 steps"),
              ("A shortest path", ["A", "B", "D", "E"], "the fewest steps possible", "3 steps")]
    for k, (title, route, note, steps) in enumerate(routes):
        x0, y0 = 20 + k * 295, 50
        pos = {n: (x0 + x, y0 + y) for n, (x, y) in pts.items()}
        for a, b in edges:
            c.edge(pos[a], pos[b], ra=15, rb=15, width=1.6, color="#c7ccd4")
        for i in range(len(route) - 1):
            a, b = route[i], route[i + 1]
            curve = 0
            if title == "A walk" and (i, route[i], route[i + 1]) in ((1, "B", "C"), (2, "C", "B")):
                curve = 17
            c.edge(pos[a], pos[b], ra=15, rb=15, directed=True, width=3.2, color=ORANGE if title != "A shortest path" else BLUE,
                   curve=curve)
            mx, my = (pos[a][0] + pos[b][0]) / 2, (pos[a][1] + pos[b][1]) / 2
        for n, p in pos.items():
            on = n in route
            col = (BLUE if title == "A shortest path" else ORANGE) if on else MUTED
            c.node(*p, {"A": "Ana", "B": "Ben", "C": "Cleo", "D": "Dev", "E": "Eli"}[n][:2], r=15,
                   fill=PAPER, stroke=col, sw=2.2, size=11)
        c.caption(x0 + 140, 255, title)
        c.text(x0 + 140, 276, note + " (" + steps + ")", size=12, fill=MUTED)
    meta = dict(chapter=7,
                caption="Three kinds of route from Ana to Eli. A walk may repeat anything; a path never repeats a person; a shortest path (a geodesic) uses the fewest steps. Distance is the length of a shortest path.",
                alt="Three drawings of a five-person network in which Ben, Cleo and Dev form a triangle, Ana hangs off Ben and Eli hangs off Dev. Left: a walk from Ana to Eli that goes to Cleo and back to Ben, five steps. Middle: a path through Ben, Cleo and Dev, four steps. Right: a shortest path through Ben and Dev, three steps.",
                data={"edges": [list(e) for e in edges], "routes": {t: r for t, r, _, _ in routes}})
    return c, meta


def distance_matrix():
    n = len(KITE_NAMES)
    d = distances(n, KITE_EDGES)
    ecc = [max(r) for r in d]
    c = Canvas(820, 420, "Who is how far from whom",
               "A ten by ten table of the number of steps between every pair of people in the friendship network, shaded from light (near) to dark (far).")
    cell, x0, y0 = 34, 90, 50
    shades = ["#ffffff", "#e6f1f9", "#b5d5ea", "#6aa9d2", "#1f6fa8"]
    for j, nm in enumerate(KITE_NAMES):
        c.text(x0 + j * cell + cell / 2, y0 - 10, nm, size=11)
        c.text(x0 - 10, y0 + j * cell + cell / 2 + 4, nm, size=11, anchor="end")
    for i in range(n):
        for j in range(n):
            v = d[i][j]
            c.rect(x0 + j * cell, y0 + i * cell, cell, cell, fill=shades[v], stroke="#e5e7eb", sw=0.8)
            c.text(x0 + j * cell + cell / 2, y0 + i * cell + cell / 2 + 4, str(v), size=12,
                   fill=PAPER if v >= 3 else INK, weight="600" if v == max(ecc) else "400")
    c.text(x0 + n * cell + 48, y0 - 10, "furthest", size=11, fill=MUTED)
    for i in range(n):
        c.text(x0 + n * cell + 48, y0 + i * cell + cell / 2 + 4, str(ecc[i]), size=12, weight="600",
               fill=ORANGE if ecc[i] == max(ecc) else INK)
    avg = sum(sum(r) for r in d) / (n * (n - 1))
    c.text(410, 408, f"Largest entry (the diameter): {max(ecc)}.  Average over all pairs: {avg:.2f} steps.", size=13, fill=MUTED)
    meta = dict(chapter=7,
                caption="The distance table for the friendship network. Its largest entry is the diameter; its average over pairs is the mean distance; each row's largest entry is that person's eccentricity.",
                alt="A ten by ten grid of numbers. The diagonal is zero. Most entries are 1, 2 or 3. The darkest entries, 4, appear between Jo and each of the first five people in the list. A column at the right gives each person's largest distance.",
                data={"names": KITE_NAMES, "distances": d, "eccentricity": ecc, "mean_distance": round(avg, 3)})
    return c, meta


def density_dice():
    c = Canvas(900, 295, "Density: how many of the possible ties exist",
               "The same six people with five ties, nine ties and all fifteen ties, labeled with their density.")
    n = 6
    allp = list(combinations(range(n), 2))
    sets = [("A path", [(i, i + 1) for i in range(5)]),
            ("Some shortcuts", [(i, (i + 1) % 6) for i in range(6)] + [(0, 3), (1, 4), (2, 5)]),
            ("Everyone ties to everyone", allp)]
    data = []
    for k, (title, edges) in enumerate(sets):
        x0 = 20 + k * 295
        pos = ring(x0 + 130, 148, 85, n)
        for a, b in edges:
            c.edge(pos[a], pos[b], ra=11, rb=11, width=1.8, color="#9ca3af")
        for p in pos:
            c.node(*p, "", r=11, fill="#cfe5f3", stroke=BLUE, sw=2)
        c.caption(x0 + 130, 30, title)
        dens = len(edges) / len(allp)
        data.append({"graph": title, "ties": len(edges), "possible": len(allp), "density": round(dens, 3)})
        c.text(x0 + 130, 268, f"{len(edges)} of {len(allp)} possible = {dens:.2f}", size=14, weight="600")
    meta = dict(chapter=7,
                caption="Density is the share of possible ties that are present. With six people there are 15 possible ties.",
                alt="Three drawings of six people on a circle. A path of five ties has density 0.33. A ring with three crossing ties, nine in all, has density 0.60. All fifteen ties give density 1.00.",
                data=data)
    return c, meta


def clustering_idea():
    c = Canvas(900, 300, "Do my friends know each other?",
               "Three views of one person and their four friends: none of the friends know each other, two pairs do, and all pairs do.")
    cases = [("No friends of friends", []), ("Some friends know each other", [(0, 1), (2, 3)]),
             ("All friends know each other", list(combinations(range(4), 2)))]
    data = []
    for k, (title, links) in enumerate(cases):
        x0 = 20 + k * 295
        ctr = (x0 + 130, 135)
        pts = ring(ctr[0], ctr[1], 80, 4, start=-135)
        for p in pts:
            c.edge(ctr, p, ra=14, rb=11, width=1.8, color="#9ca3af")
        for a, b in links:
            c.edge(pts[a], pts[b], ra=11, rb=11, width=3, color=ORANGE)
        for p in pts:
            c.node(*p, "", r=11, fill="#cfe5f3", stroke=BLUE, sw=2)
        c.node(*ctr, "", r=14, fill=ORANGE, stroke=ORANGE, sw=2)
        c.caption(x0 + 130, 30, title)
        val = len(links) / 6
        data.append({"links_among_friends": len(links), "possible": 6, "clustering": round(val, 3)})
        c.text(x0 + 130, 262, f"{len(links)} of 6 pairs are tied = {val:.2f}", size=14, weight="600")
    meta = dict(chapter=7,
                caption="Local clustering for the person in the middle: of all pairs of their friends, what share are friends with each other?",
                alt="Three drawings of a person in the middle tied to four friends. In the first no two friends are tied, giving 0 of 6, clustering 0.00. In the second two pairs of friends are tied, 2 of 6, clustering 0.33. In the third all pairs are tied, 6 of 6, clustering 1.00.",
                data=data)
    return c, meta


def components_fig():
    c = Canvas(900, 320, "Components: pieces that do not connect",
               "Left: an undirected network in two separate pieces. Right: a directed network that is one piece if arrows are ignored, but two strong components when arrows are followed.")
    c.caption(215, 30, "Two separate pieces")
    A = [(40, 100), (110, 70), (110, 140), (180, 100)]
    B = [(300, 90), (360, 140), (395, 70)]
    for a, b in [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]:
        c.edge((A[a][0] + 20, A[a][1] + 60), (A[b][0] + 20, A[b][1] + 60), ra=12, rb=12, width=2, color="#9ca3af")
    for a, b in [(0, 1), (1, 2), (0, 2)]:
        c.edge((B[a][0] - 30, B[a][1] + 60), (B[b][0] - 30, B[b][1] + 60), ra=12, rb=12, width=2, color="#9ca3af")
    for p in A:
        c.node(p[0] + 20, p[1] + 60, "", r=12, fill="#cfe5f3", stroke=BLUE, sw=2)
    for p in B:
        c.node(p[0] - 30, p[1] + 60, "", r=12, fill="#fbe7c2", stroke=ORANGE, sw=2, shape="square")
    c.text(215, 270, "2 components, of sizes 4 and 3", size=14, weight="600")
    c.caption(680, 30, "Weak and strong")
    cyc = [(570, 110), (630, 70), (640, 150)]
    mut = [(740, 100), (810, 150)]
    for a, b in [(0, 1), (1, 2), (2, 0)]:
        c.edge((cyc[a][0], cyc[a][1] + 40), (cyc[b][0], cyc[b][1] + 40), ra=13, rb=13, directed=True, width=2,
               color=BLUE, curve=0)
    for a, b in [(0, 1), (1, 0)]:
        c.edge((mut[a][0], mut[a][1] + 40), (mut[b][0], mut[b][1] + 40), ra=13, rb=13, directed=True, width=2,
               color=ORANGE, curve=10)
    c.edge((cyc[2][0], cyc[2][1] + 40), (mut[0][0], mut[0][1] + 40), ra=13, rb=13, directed=True, width=2, color="#9ca3af", dash="5 4")
    for p in cyc:
        c.node(p[0], p[1] + 40, "", r=13, fill="#cfe5f3", stroke=BLUE, sw=2)
    for p in mut:
        c.node(p[0], p[1] + 40, "", r=13, fill="#fbe7c2", stroke=ORANGE, sw=2, shape="square")
    c.text(680, 270, "1 weak component, 2 strong components", size=14, weight="600")
    c.text(680, 292, "the dashed arrow only goes one way", size=12, fill=MUTED)
    meta = dict(chapter=7,
                caption="Components. In an undirected network a component is a piece in which everyone can reach everyone. In a directed network we distinguish weak components (ignore arrow direction) from strong ones (follow the arrows both ways).",
                alt="Left: a four-person cluster and a separate three-person triangle, with no tie between them. Right: three people joined in a one-way cycle and two people who point at each other, with one dashed arrow from the cycle to the pair.",
                data={"undirected_component_sizes": [4, 3], "strong_components": [3, 2], "weak_components": 1})
    return c, meta


def cores_fig():
    n = len(KITE_NAMES)
    core = [3, 3, 3, 3, 3, 3, 3, 2, 1, 1]
    pos = fit(stress_layout(n, KITE_EDGES, seed=3), 20, 40, 520, 250)
    c = Canvas(900, 330, "Cores: peeling a network from the outside in",
               "The friendship network with each person marked by core number: seven people in the 3-core, one in the 2-core, and two in the 1-core.")
    styles = {3: (BLUE, "circle"), 2: (ORANGE, "square"), 1: (PURPLE, "diamond")}
    for a, b in KITE_EDGES:
        c.edge(pos[a], pos[b], ra=14, rb=14, width=1.6, color="#9ca3af")
    for i, p in enumerate(pos):
        col, shape = styles[core[i]]
        c.node(*p, KITE_NAMES[i][:2], r=14, fill=col + "33", stroke=col, shape=shape, sw=2.2, size=10.5)
    y = 90
    for k, txt in [(3, "core 3: 3+ friends inside the group"),
                   (2, "core 2: joins the group with 2 ties"),
                   (1, "core 1: a thread hanging off the rest")]:
        col, shape = styles[k]
        c.node(590, y, "", r=9, fill=col + "33", stroke=col, shape=shape, sw=2)
        c.text(612, y + 4, txt, size=13, anchor="start")
        y += 38
    c.lines(580, 230, ["Peel off anyone with fewer than 3", "friends, and repeat until no one can", "be peeled. What is left is the 3-core."],
            size=12.5, fill=MUTED)
    meta = dict(chapter=7,
                caption="k-cores. A person's core number is the largest k for which they belong to a group where everyone has at least k ties inside the group. Seven people are in the 3-core.",
                alt="The ten-person friendship network. Seven nodes drawn as blue circles form the dense cluster. Hana, drawn as an orange square, hangs off it. Ivo and Jo, drawn as purple diamonds, trail off at the far end.",
                data={"names": KITE_NAMES, "coreness": core})
    return c, meta


TRIAD_16 = [
    # code, plain gloss, arcs on nodes 0 (top), 1 (bottom left), 2 (bottom right); checked against the engine
    ("003", "no ties", []),
    ("012", "one tie", [(0, 1)]),
    ("102", "one mutual pair", [(0, 1), (1, 0)]),
    ("021D", "one sends to two", [(0, 1), (0, 2)]),
    ("021U", "two send to one", [(1, 0), (2, 0)]),
    ("021C", "a chain", [(1, 0), (0, 2)]),
    ("111D", "mutual pair, and one more points at it", [(0, 1), (1, 0), (2, 0)]),
    ("111U", "mutual pair, and it points at one more", [(0, 1), (1, 0), (0, 2)]),
    ("030T", "transitive: a pecking order", [(0, 1), (0, 2), (1, 2)]),
    ("030C", "a cycle, no top", [(0, 1), (2, 0), (1, 2)]),
    ("201", "two mutual pairs", [(0, 1), (1, 0), (0, 2), (2, 0)]),
    ("120D", "mutual pair, one sends to both", [(1, 0), (0, 2), (2, 0), (1, 2)]),
    ("120U", "mutual pair, both send to one", [(0, 1), (1, 0), (0, 2), (1, 2)]),
    ("120C", "mutual pair, with a chain", [(0, 1), (1, 0), (2, 0), (1, 2)]),
    ("210", "two mutual pairs and one more", [(0, 1), (1, 0), (0, 2), (2, 0), (1, 2)]),
    ("300", "everyone mutual", [(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)]),
]


def triad_types():
    c = Canvas(900, 800, "All sixteen triad types",
               "The sixteen ways three people can be connected once direction is tracked, each labeled with its census code and a plain description.")
    w, h = 225, 195
    for k, (code, gloss, arcs) in enumerate(TRIAD_16):
        x0, y0 = (k % 4) * w, (k // 4) * h + 10
        cx = x0 + w / 2
        pts = [(cx, y0 + 28), (cx - 48, y0 + 108), (cx + 48, y0 + 108)]
        have = set(arcs)
        for a, b in arcs:
            curve = 9 if (b, a) in have else 0
            c.edge(pts[a], pts[b], ra=11, rb=11, directed=True, width=2.2, color=BLUE, curve=curve)
        for i, p in enumerate(pts):
            c.node(*p, "", r=11, fill=PAPER, stroke=INK, sw=2)
        c.text(cx, y0 + 150, code, size=15, weight="700")
        c.text(cx, y0 + 169, gloss if len(gloss) < 30 else gloss[:gloss.rfind(" ", 0, 30)], size=11.5, fill=MUTED)
        if len(gloss) >= 30:
            c.text(cx, y0 + 183, gloss[gloss.rfind(" ", 0, 30) + 1:], size=11.5, fill=MUTED)
    meta = dict(chapter=7,
                caption="All sixteen triad types. In each triangle the same three people appear in the same places; only the ties differ. The code reads as the number of mutual pairs, asymmetric pairs and empty pairs, with a letter for the finer shape.",
                alt="A four by four grid of sixteen small directed triangles, each with its code and description. Row one: 003 no ties, 012 one tie, 102 one mutual pair, 021D one person sends to two. Row two: 021U two send to one, 021C a chain, 111D a mutual pair with one more pointing at it, 111U a mutual pair that points at one more. Row three: 030T a transitive pecking order, 030C a cycle, 201 two mutual pairs, 120D a mutual pair where one sends to both. Row four: 120U a mutual pair where both send to one, 120C a mutual pair with a chain, 210 two mutual pairs and one more tie, 300 everyone mutual.",
                data={"types": [t[0] for t in TRIAD_16]})
    return c, meta


# ---------------------------------------------------------------- chapter 8
KARATE_EDGES = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 10), (0, 11), (0, 12), (0, 13),
                (0, 17), (0, 19), (0, 21), (0, 31), (1, 2), (1, 3), (1, 7), (1, 13), (1, 17), (1, 19), (1, 21),
                (1, 30), (2, 3), (2, 7), (2, 8), (2, 9), (2, 13), (2, 27), (2, 28), (2, 32), (3, 7), (3, 12),
                (3, 13), (4, 6), (4, 10), (5, 6), (5, 10), (5, 16), (6, 16), (8, 30), (8, 32), (8, 33), (9, 33),
                (13, 33), (14, 32), (14, 33), (15, 32), (15, 33), (18, 32), (18, 33), (19, 33), (20, 32),
                (20, 33), (22, 32), (22, 33), (23, 25), (23, 27), (23, 29), (23, 32), (23, 33), (24, 25),
                (24, 27), (24, 31), (25, 31), (26, 29), (26, 33), (27, 33), (28, 31), (28, 33), (29, 32),
                (29, 33), (30, 32), (30, 33), (31, 32), (31, 33), (32, 33)]
# Which side each member took when the club split (0 = Mr. Hi, 1 = the officer), and the communities
# found by Louvain with resolution 1 and seed 1 (the numbers printed by the chapter's Rust example).
KARATE_SIDES = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
KARATE_LOUVAIN = [0, 0, 0, 0, 1, 1, 1, 0, 2, 0, 1, 0, 0, 0, 2, 2, 1, 0, 2, 0, 2, 0, 2, 3, 3, 3, 2, 3, 3, 2, 2, 3, 2, 2]
RESOLUTION_SWEEP = [(0.5, 2, 0.372), (1.0, 4, 0.419), (1.5, 5, 0.381), (2.0, 8, 0.325), (3.0, 12, 0.226)]
COMM_COLORS = [BLUE, ORANGE, GREEN, PURPLE]


def karate_communities():
    n = 34
    pos = fit(stress_layout(n, KARATE_EDGES, seed=2), 20, 30, 560, 380)
    c = Canvas(900, 440, "The karate club, two ways",
               "The karate club network with each member's shape showing which side they took when the club split and each member's color showing the community found by Louvain.")
    for a, b in KARATE_EDGES:
        c.edge(pos[a], pos[b], ra=9, rb=9, width=1.3, color="#b6bcc6")
    for i, p in enumerate(pos):
        col = COMM_COLORS[KARATE_LOUVAIN[i]]
        c.node(*p, "", r=9, fill=col + "55", stroke=col, shape="circle" if KARATE_SIDES[i] == 0 else "square", sw=2.2)
    c.text(620, 80, "Shape: the side each member took", size=14, anchor="start", weight="700")
    c.node(634, 108, "", r=8, fill="#e5e7eb", stroke=INK, sw=2)
    c.text(652, 113, "stayed with Mr. Hi, the instructor", size=13, anchor="start")
    c.node(634, 138, "", r=8, fill="#e5e7eb", stroke=INK, shape="square", sw=2)
    c.text(652, 143, "followed the officer, the administrator", size=13, anchor="start")
    c.text(620, 195, "Color: community found by Louvain", size=14, anchor="start", weight="700")
    names = ["community 1", "community 2", "community 3", "community 4"]
    for k in range(4):
        c.node(634, 223 + 28 * k, "", r=8, fill=COMM_COLORS[k] + "55", stroke=COMM_COLORS[k], sw=2)
        c.text(652, 228 + 28 * k, names[k], size=13, anchor="start")
    c.lines(620, 350, ["Four communities, but they nest", "inside the two real sides, apart", "from two members who sit between."],
            size=12.5, fill=MUTED)
    meta = dict(chapter=8,
                caption="Zachary's karate club. Shape shows who sided with whom when the club split; color shows the four communities found by Louvain. The communities refine the split rather than contradicting it.",
                alt="A network of 34 people. Circles are members who stayed with the instructor and squares followed the administrator. Four colors mark communities: two colors cover almost only circles, two cover almost only squares, with one circle among the squares' communities and one square among the circles' communities.",
                data={"edges": [list(e) for e in KARATE_EDGES], "sides": KARATE_SIDES, "louvain": KARATE_LOUVAIN})
    return c, meta


def modularity_bars():
    n, m = 34, len(KARATE_EDGES)
    comm = KARATE_LOUVAIN
    deg = [sum(1 for e in KARATE_EDGES if i in e) for i in range(n)]
    obs, exp = [], []
    for k in range(4):
        nodes = [i for i in range(n) if comm[i] == k]
        inside = sum(1 for a, b in KARATE_EDGES if comm[a] == k and comm[b] == k)
        obs.append(inside / m)
        exp.append((sum(deg[i] for i in nodes) / (2 * m)) ** 2)
    q = sum(o - e for o, e in zip(obs, exp))
    c = Canvas(780, 330, "Modularity: more ties inside groups than chance predicts",
               "For each of four communities, a bar for the share of all ties inside it and a bar for the share expected if ties were rewired at random keeping everyone's degree.")
    x0, y0, h = 80, 40, 220
    unit = h / 0.35
    for t in (0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35):
        y = y0 + h - t * unit
        c.edge((x0 - 8, y), (730, y), ra=0, rb=0, width=1, color="#e5e7eb")
        c.text(x0 - 14, y + 4, f"{t:.2f}", size=11, anchor="end", fill=MUTED)
    for k in range(4):
        gx = x0 + 30 + k * 155
        for j, (v, col, dash) in enumerate([(obs[k], COMM_COLORS[k], None), (exp[k], "#9ca3af", "4 3")]):
            bh = v * unit
            c.rect(gx + j * 52, y0 + h - bh, 46, bh, fill=col + ("dd" if j == 0 else "55"), stroke=col if j == 0 else "#6b7280", sw=1.6, dash=dash)
            c.text(gx + j * 52 + 23, y0 + h - bh - 6, f"{v:.3f}", size=12, weight="600")
        c.text(gx + 49, y0 + h + 22, f"community {k + 1}", size=13, weight="600")
    c.rect(250, 305, 14, 14, fill=BLUE + "dd", stroke=BLUE)
    c.text(270, 317, "share of all ties inside the community", size=12, anchor="start", fill=MUTED)
    c.rect(520, 305, 14, 14, fill="#9ca3af55", stroke="#6b7280", dash="3 2")
    c.text(540, 317, "share expected by chance", size=12, anchor="start", fill=MUTED)
    c.text(700, 28, f"Q = {q:.3f}", size=15, anchor="end", weight="700")
    meta = dict(chapter=8,
                caption="Modularity adds up, over communities, how much more of the network's ties fall inside the community than random rewiring would put there. Here the four communities sum to Q = 0.419.",
                alt="A grouped bar chart with four pairs of bars, one pair per community. In every pair the solid bar, the observed share of ties inside the community, is taller than the dashed bar, the share expected by chance.",
                data={"observed": [round(o, 4) for o in obs], "expected": [round(e, 4) for e in exp], "Q": round(q, 4)})
    return c, meta


def resolution_sweep():
    c = Canvas(780, 330, "More communities is not better communities",
               "A chart of how many communities Louvain finds, and the modularity of the result, as the resolution setting rises from 0.5 to 3.")
    x0, y0, w, h = 80, 40, 620, 220
    xs = [x0 + 40 + i * (w - 80) / (len(RESOLUTION_SWEEP) - 1) for i in range(len(RESOLUTION_SWEEP))]
    for t in range(0, 13, 3):
        y = y0 + h - t * h / 12
        c.edge((x0, y), (x0 + w, y), ra=0, rb=0, width=1, color="#e5e7eb")
        c.text(x0 - 10, y + 4, str(t), size=11, anchor="end", fill=MUTED)
    for i, (r, g, q) in enumerate(RESOLUTION_SWEEP):
        bh = g * h / 12
        best = abs(q - max(v[2] for v in RESOLUTION_SWEEP)) < 1e-9
        c.rect(xs[i] - 26, y0 + h - bh, 52, bh, fill=(ORANGE if best else BLUE) + "99", stroke=ORANGE if best else BLUE, sw=1.8)
        c.text(xs[i], y0 + h - bh - 8, str(g), size=13, weight="700")
        c.text(xs[i], y0 + h + 22, f"resolution {r:g}", size=12)
        c.text(xs[i], y0 + h + 42, f"Q = {q:.3f}", size=12, weight="600" if best else "400", fill=ORANGE if best else MUTED)
    c.text(x0, 26, "number of communities found", size=12, anchor="start", fill=MUTED)
    meta = dict(chapter=8,
                caption="The resolution setting controls how fine the communities are. The setting with the highest modularity is not necessarily the one that matches your question.",
                alt="A bar chart with five bars for resolution settings 0.5, 1, 1.5, 2 and 3, showing 2, 4, 5, 8 and 12 communities. The bar for resolution 1, four communities, is highlighted because it has the highest modularity, 0.419.",
                data=[{"resolution": r, "communities": g, "modularity_at_1": q} for r, g, q in RESOLUTION_SWEEP])
    return c, meta


def group_ladder():
    c = Canvas(900, 300, "Three kinds of tight group",
               "A clique where everyone is tied to everyone, a near-clique where everyone is missing at most one tie, and a community that is dense inside and sparse to the outside.")
    c.caption(150, 30, "Clique")
    pts = ring(150, 135, 70, 5)
    for a, b in combinations(range(5), 2):
        c.edge(pts[a], pts[b], ra=12, rb=12, width=1.8, color="#9ca3af")
    for p in pts:
        c.node(*p, "", r=12, fill="#cfe5f3", stroke=BLUE, sw=2)
    c.text(150, 245, "every pair is tied", size=13, fill=MUTED)
    c.caption(450, 30, "Near-clique")
    pts = ring(450, 135, 70, 5)
    missing = {(0, 2), (1, 3)}
    for a, b in combinations(range(5), 2):
        if (a, b) in missing:
            c.edge(pts[a], pts[b], ra=12, rb=12, width=1.6, color=RED, dash="4 4", opacity=0.7)
        else:
            c.edge(pts[a], pts[b], ra=12, rb=12, width=1.8, color="#9ca3af")
    for p in pts:
        c.node(*p, "", r=12, fill="#cfe5f3", stroke=BLUE, sw=2)
    c.text(450, 245, "everyone misses at most one tie", size=13, fill=MUTED)
    c.caption(750, 30, "Community")
    left = [(690, 110), (720, 150), (680, 170), (730, 100)]
    right = [(790, 130), (820, 90), (830, 160), (780, 180)]
    for grp, col in ((left, BLUE), (right, ORANGE)):
        for a, b in combinations(range(4), 2):
            c.edge(grp[a], grp[b], ra=10, rb=10, width=1.6, color="#9ca3af")
    c.edge(left[1], right[3], ra=10, rb=10, width=1.6, color="#9ca3af")
    for p in left:
        c.node(*p, "", r=10, fill="#cfe5f3", stroke=BLUE, sw=2)
    for p in right:
        c.node(*p, "", r=10, fill="#fbe7c2", stroke=ORANGE, sw=2, shape="square")
    c.text(750, 245, "dense inside, sparse between", size=13, fill=MUTED)
    meta = dict(chapter=8,
                caption="Subgroup definitions run from strict to loose. A clique allows no missing ties; a near-clique allows a few; a community only asks for more ties inside than you would expect by chance.",
                alt="Left: five people on a circle with every pair tied. Middle: five people on a circle with two dashed red lines marking the two missing ties, so each person is missing at most one. Right: two small clusters of four, blue circles and orange squares, joined by a single tie.",
                data={"clique": 5, "near_clique_missing": [list(e) for e in sorted(missing)]})
    return c, meta


# ---------------------------------------------------------------- chapter 9
OFFICE_NAMES = ["Ada", "Ben", "Cy", "Dee", "Eve", "Flo", "Gus", "Hal", "Ivy", "Jay"]
OFFICE_FROM = [0, 1, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9]
OFFICE_TO = [1, 0, 0, 1, 0, 1, 0, 1, 2, 2, 3, 4, 4]
OFFICE_POSITION = [0, 0, 1, 1, 1, 2, 2, 2, 2, 2]
POS_STYLE = [(PURPLE, "diamond", "Leaders"), (ORANGE, "square", "Managers"), (BLUE, "circle", "Staff")]
OFFICE_XY = [(380, 62), (520, 62), (250, 190), (450, 190), (650, 190),
             (190, 322), (310, 322), (450, 322), (610, 322), (710, 322)]


def office_network():
    c = Canvas(900, 400, "An office where advice flows upward",
               "Ten people in an office, drawn in three rows: two leaders, three managers and five staff, with arrows from the person asking to the person asked.")
    for (col, shape, label), y in zip(POS_STYLE, (62, 190, 322)):
        c.text(24, y + 5, label, size=14, anchor="start", weight="700", fill=col)
    for a, b in zip(OFFICE_FROM, OFFICE_TO):
        mutual = OFFICE_POSITION[a] == 0 and OFFICE_POSITION[b] == 0
        c.edge(OFFICE_XY[a], OFFICE_XY[b], ra=20, rb=20, directed=True, width=1.8, color="#7b8494",
               curve=10 if mutual else 0)
    for i, (x, y) in enumerate(OFFICE_XY):
        col, shape, _ = POS_STYLE[OFFICE_POSITION[i]]
        c.node(x, y, OFFICE_NAMES[i][:2], r=19, fill="#ffffff", stroke=col, shape=shape, sw=2.6, size=12)
    c.text(450, 385, "An arrow means: goes to this person for advice.", size=13, fill=MUTED)
    meta = dict(chapter=9,
                caption="An office advice network. Shape and color mark the position: leaders (diamonds), managers (squares) and staff (circles). Nobody in the bottom row asks anybody else in the bottom row, and yet they have a lot in common.",
                alt="Ten people in three rows. Two leaders at the top, Ada and Ben, point at each other. Three managers in the middle each point at both leaders. Five staff at the bottom each point at one manager: Flo and Gus at Cy, Hal at Dee, and Ivy and Jay at Eve.",
                data={"names": OFFICE_NAMES, "from": OFFICE_FROM, "to": OFFICE_TO, "position": OFFICE_POSITION})
    return c, meta


def equivalence_kinds():
    c = Canvas(900, 360, "Two ways of being alike",
               "Two small panels. On the left, two staff members tied to the same manager are structurally equivalent. On the right, two staff members tied to different managers are only regularly equivalent.")
    for k, (title, pair) in enumerate([("Structurally equivalent", ("Flo", "Gus")), ("Regularly equivalent", ("Flo", "Hal"))]):
        x0 = 20 + k * 450
        c.caption(x0 + 215, 28, title)
        top = (x0 + 215, 78)
        mgr = {"Cy": (x0 + 130, 170), "Dee": (x0 + 300, 170)}
        stf = {"Flo": (x0 + 75, 270), "Gus": (x0 + 185, 270), "Hal": (x0 + 300, 270)}
        c.node(*top, "Ada", r=20, fill="#fff", stroke=PURPLE, shape="diamond", sw=2.4, size=11)
        for nm, p in mgr.items():
            c.edge(p, top, ra=19, rb=22, directed=True, width=1.8, color="#7b8494")
        for nm, p in stf.items():
            tgt = mgr["Cy"] if nm in ("Flo", "Gus") else mgr["Dee"]
            c.edge(p, tgt, ra=19, rb=19, directed=True, width=1.8, color="#7b8494")
        for nm, p in mgr.items():
            c.node(*p, nm[:2], r=19, fill="#fff", stroke=ORANGE, shape="square", sw=2.4, size=12)
        for nm, p in stf.items():
            hit = nm in pair
            c.node(*p, nm[:2], r=19, fill="#cfe5f3" if hit else "#fff", stroke=BLUE, sw=3 if hit else 2, size=12)
        note = ["Same ties to the same people:", "both go to Cy and nobody else."] if k == 0 else \
            ["Different people, same kind of tie:", "each goes to one manager."]
        c.lines(x0 + 215, 322, note, size=12.5, fill=MUTED, anchor="middle")
    meta = dict(chapter=9,
                caption="Structural equivalence asks for the same ties to the same people. Regular equivalence asks only for the same kinds of ties to people who are themselves alike. Flo and Gus are both; Flo and Hal are only the second.",
                alt="Two small drawings. In each, Ada at the top receives from two managers, Cy and Dee, and three staff members each point at a manager. On the left, Flo and Gus are highlighted and both point at Cy. On the right, Flo and Hal are highlighted: Flo points at Cy and Hal points at Dee.",
                data={"left": ["Flo", "Gus"], "right": ["Flo", "Hal"]})
    return c, meta


def blockmodel_matrix():
    n = 10
    arcs = set(zip(OFFICE_FROM, OFFICE_TO))
    c = Canvas(900, 500, "The advice network as a matrix, and its blockmodel",
               "On the left, the ten by ten table of who goes to whom, with people grouped by position. On the right, the three by three table of block densities and the image matrix that results.")
    cell, x0, y0 = 30, 90, 70
    c.caption(x0 + n * cell / 2, 28, "Who goes to whom")
    for j in range(n):
        c.text(x0 + j * cell + cell / 2, y0 - 8, OFFICE_NAMES[j][:2], size=11)
        c.text(x0 - 8, y0 + j * cell + cell / 2 + 4, OFFICE_NAMES[j], size=11, anchor="end")
    for i in range(n):
        for j in range(n):
            tie = (i, j) in arcs
            c.rect(x0 + j * cell, y0 + i * cell, cell, cell, fill=BLUE if tie else ("#f3f4f6" if i == j else "#ffffff"),
                   stroke="#e5e7eb", sw=0.8)
    for b in (2, 5):
        c.add(f'<line x1="{x0 + b * cell}" y1="{y0 - 4}" x2="{x0 + b * cell}" y2="{y0 + n * cell + 4}" stroke="{INK}" stroke-width="2"/>')
        c.add(f'<line x1="{x0 - 4}" y1="{y0 + b * cell}" x2="{x0 + n * cell + 4}" y2="{y0 + b * cell}" stroke="{INK}" stroke-width="2"/>')
    c.text(x0 + n * cell / 2, y0 + n * cell + 32, "rows: who asks    columns: who is asked", size=12, fill=MUTED)
    # densities and image
    labels = ["Leaders", "Managers", "Staff"]
    sizes = [2, 3, 5]
    dens = []
    for r in range(3):
        row = []
        for s in range(3):
            tot = sum(1 for (a, b) in arcs if OFFICE_POSITION[a] == r and OFFICE_POSITION[b] == s)
            pairs = sizes[r] * sizes[s] - (sizes[r] if r == s else 0)
            row.append(tot / pairs)
        dens.append(row)
    overall = len(arcs) / (n * (n - 1))
    for panel, (title, ytop) in enumerate([("Block densities", 70), ("Image: 1 where density is at least %.3f" % overall, 290)]):
        bx = 560
        c.text(bx + 90, ytop - 38, title, size=14, weight="700")
        for j, lb in enumerate(labels):
            c.text(bx + j * 60 + 30, ytop - 8, lb, size=11)
            c.text(bx - 8, ytop + j * 52 + 31, lb, size=11, anchor="end")
        for r in range(3):
            for s in range(3):
                d = dens[r][s]
                one = d >= overall
                if panel == 0:
                    shade = "#cfe5f3" if d > 0 else "#ffffff"
                    txt = f"{d:.2f}"
                else:
                    shade = BLUE if one else "#ffffff"
                    txt = "1" if one else "0"
                c.rect(bx + s * 60, ytop + r * 52, 60, 52, fill=shade, stroke="#9ca3af", sw=1)
                c.text(bx + s * 60 + 30, ytop + r * 52 + 31, txt, size=15, weight="600",
                       fill=PAPER if (panel == 1 and one) else INK)
    c.text(660, 482, "Advice flows up: staff to managers, managers to leaders.", size=13, fill=MUTED)
    meta = dict(chapter=9,
                caption="A blockmodel squeezes the matrix of who goes to whom into one number per pair of positions (the density of that block) and then into a 1 or a 0 (the image). Here three positions and three ones tell the whole story.",
                alt="On the left, a ten by ten grid with blue cells where a person asks another for advice, separated by heavy lines into leaders, managers and staff. Blue cells fill the leaders' own block and the managers-to-leaders block, and a scatter in the staff-to-managers block. On the right, a three by three table of block densities with values 1.00 for leaders to leaders and managers to leaders, 0.33 for staff to managers and 0 elsewhere, and below it the image matrix with ones in those three places.",
                data={"positions": labels, "density": [[round(x, 3) for x in r] for r in dens], "cutoff": round(overall, 3)})
    return c, meta


CP_CORE = [0, 1, 3, 5, 6]


def core_periphery():
    n = len(KITE_NAMES)
    pos = fit(stress_layout(n, KITE_EDGES, seed=3), 20, 40, 470, 250)
    c = Canvas(900, 400, "A core and a periphery",
               "Left: the friendship network with five core members drawn as blue circles and five periphery members as orange squares. Right: the ideal pattern the fit compares against.")
    for a, b in KITE_EDGES:
        c.edge(pos[a], pos[b], ra=14, rb=14, width=1.6, color="#9ca3af")
    for i, p in enumerate(pos):
        core = i in CP_CORE
        col, shape = (BLUE, "circle") if core else (ORANGE, "square")
        c.node(*p, KITE_NAMES[i][:2], r=14, fill=col + "33", stroke=col, shape=shape, sw=2.2, size=10.5)
    order = CP_CORE + [i for i in range(n) if i not in CP_CORE]
    cell, x0, y0 = 22, 600, 60
    c.caption(x0 + n * cell / 2, 30, "The ideal pattern")
    for a in range(n):
        for b in range(n):
            ca, cb = a < 5, b < 5
            if a == b:
                fillc = "#f3f4f6"
            elif ca and cb:
                fillc = BLUE
            elif not ca and not cb:
                fillc = "#ffffff"
            else:
                fillc = "#e5e7eb"
            c.rect(x0 + b * cell, y0 + a * cell, cell, cell, fill=fillc, stroke="#e5e7eb", sw=0.8)
    c.add(f'<line x1="{x0 + 5 * cell}" y1="{y0 - 4}" x2="{x0 + 5 * cell}" y2="{y0 + n * cell + 4}" stroke="{INK}" stroke-width="2"/>')
    c.add(f'<line x1="{x0 - 4}" y1="{y0 + 5 * cell}" x2="{x0 + n * cell + 4}" y2="{y0 + 5 * cell}" stroke="{INK}" stroke-width="2"/>')
    c.node(x0 + 6, y0 + n * cell + 34, "", r=7, fill=BLUE, stroke=BLUE)
    c.text(x0 + 20, y0 + n * cell + 38, "core to core: expect a tie", size=12, anchor="start")
    c.node(x0 + 6, y0 + n * cell + 58, "", r=7, fill="#ffffff", stroke="#9ca3af")
    c.text(x0 + 20, y0 + n * cell + 62, "periphery to periphery: expect none", size=12, anchor="start")
    c.node(x0 + 6, y0 + n * cell + 82, "", r=7, fill="#e5e7eb", stroke="#9ca3af")
    c.text(x0 + 20, y0 + n * cell + 86, "core to periphery: not scored", size=12, anchor="start")
    meta = dict(chapter=9,
                caption="The discrete core-periphery model. Split people into a core and a periphery and compare the network with an ideal pattern: the core is tied to itself, the periphery is not, and core-to-periphery pairs are left out. The best split is the one whose pattern fits the real ties best.",
                alt="On the left, the ten-person friendship network with five people drawn as blue circles in the dense middle and five drawn as orange squares around the edge. On the right, a ten by ten grid ordered core first: the upper-left five by five block is blue, the lower-right block is white, and the two off-diagonal blocks are gray.",
                data={"core": [KITE_NAMES[i] for i in CP_CORE]})
    return c, meta


# ---------------------------------------------------------------- chapter 10
def _nbrs(edges, n):
    nb = [set() for _ in range(n)]
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    return nb


def _burt(edges, n):
    nb = _nbrs(edges, n)
    eff, con = [], []
    for i in range(n):
        p = lambda a, b: (1 / len(nb[a])) if b in nb[a] else 0.0  # noqa: E731
        es = sum(1 - sum(p(i, q) * (1.0 if q in nb[j] else 0.0) for q in nb[i] if q != j) for j in nb[i])
        cs = sum((p(i, j) + sum(p(i, q) * p(q, j) for q in nb[i] if q != j)) ** 2 for j in nb[i])
        eff.append(es)
        con.append(cs)
    return eff, con


def ego_networks():
    c = Canvas(900, 400, "Two people, two ego networks",
               "The ego networks of Dev and Hana in the friendship network: each person at the center, their contacts around them, and the ties among those contacts.")
    cases = [("Dev", 3, ["Ana", "Cleo", "Fay", "Gus", "Eli", "Ben"], "6 contacts, 8 ties among them", "density 0.53: a tight circle"),
             ("Hana", 7, ["Fay", "Gus", "Ivo"], "3 contacts, 1 tie among them", "density 0.33: two separate pieces")]
    data = {}
    for k, (ego, ei, alters, line1, line2) in enumerate(cases):
        cx, cy = 230 + k * 440, 185
        ids = [KITE_NAMES.index(a) for a in alters]
        pts = dict(zip(ids, ring(cx, cy, 120 if k == 0 else 105, len(ids), start=-90 if k == 0 else -150)))
        c.caption(cx, 28, ego + "'s ego network")
        for a, b in KITE_EDGES:
            if a in ids and b in ids:
                c.edge(pts[a], pts[b], ra=19, rb=19, width=2.4, color=BLUE)
        for a in ids:
            c.edge((cx, cy), pts[a], ra=22, rb=19, width=1.4, color="#b6bcc6")
        for a in ids:
            c.node(*pts[a], KITE_NAMES[a][:3], r=19, fill="#cfe5f3", stroke=BLUE, sw=2, size=11.5)
        c.node(cx, cy, ego[:3], r=22, fill=ORANGE + "33", stroke=ORANGE, shape="square", sw=2.6, size=12.5)
        c.text(cx, 340, line1, size=13.5, weight="600")
        c.text(cx, 360, line2, size=13, fill=MUTED)
        data[ego] = alters
    meta = dict(chapter=10,
                caption="An ego network is a person, their contacts, and the ties among those contacts. Dev's contacts mostly know each other. Hana's mostly do not, so Hana links people who would otherwise be apart.",
                alt="Two drawings. On the left, Dev, an orange square in the middle, with six contacts in a hexagon around them, joined in a ring by blue ties with two extra blue ties across the ring. On the right, Hana, an orange square, with three contacts: Fay and Gus are joined to each other by a blue tie, and Ivo is not tied to either.",
                data=data)
    return c, meta


def holes_idea():
    c = Canvas(900, 360, "Redundant contacts and structural holes",
               "Two ego networks with three contacts each. On the left the contacts all know each other. On the right none do.")
    for k, (title, ties, es) in enumerate([("Contacts who all know each other", [(0, 1), (1, 2), (2, 0)], 1),
                                           ("Contacts who do not know each other", [], 3)]):
        cx, cy = 230 + k * 440, 175
        pts = ring(cx, cy, 100, 3, start=-90)
        c.caption(cx, 28, title)
        for a, b in ties:
            c.edge(pts[a], pts[b], ra=17, rb=17, width=2.4, color=BLUE)
        for p_ in pts:
            c.edge((cx, cy), p_, ra=21, rb=17, width=1.4, color="#b6bcc6")
        for p_ in pts:
            c.node(*p_, "", r=17, fill="#cfe5f3", stroke=BLUE, sw=2)
        c.node(cx, cy, "ego", r=21, fill=ORANGE + "33", stroke=ORANGE, shape="square", sw=2.6, size=11)
        c.text(cx, 312, f"effective size {es}", size=14, weight="700")
        c.text(cx, 333, "one contact's worth of news" if es == 1 else "three separate worlds, three contacts' worth", size=12.5, fill=MUTED)
    meta = dict(chapter=10,
                caption="Effective size counts a person's contacts, minus the redundancy among them. Three contacts who all know each other add up to one contact's worth of access. Three who do not add up to three.",
                alt="Two drawings of a person at the center with three contacts around them. On the left the three contacts are joined to one another by blue ties, a triangle, and the effective size is 1. On the right the three contacts have no ties among themselves and the effective size is 3.",
                data={"redundant": 1, "open": 3})
    return c, meta


def effective_size_bars():
    n = len(KITE_NAMES)
    eff, con = _burt(KITE_EDGES, n)
    c = Canvas(900, 455, "Who spans structural holes in the friendship network",
               "Two bar charts for the ten people: effective size on the left and constraint on the right, with Hana highlighted.")
    for panel, (title, vals, top, fmt) in enumerate([("Effective size (higher: more non-redundant contacts)", eff, 3.6, "{:.2f}"),
                                                     ("Constraint (lower: more freedom)", con, 1.1, "{:.2f}")]):
        x0 = 100 + panel * 440
        c.text(x0 + 140, 30, title, size=13.5, weight="700")
        for i in range(n):
            y = 60 + i * 34
            w = 250 * vals[i] / top
            hana = KITE_NAMES[i] == "Hana"
            col = ORANGE if hana else BLUE
            c.text(x0 - 8, y + 16, KITE_NAMES[i], size=12.5, anchor="end", weight="700" if hana else "400")
            c.rect(x0, y + 3, w, 22, fill=col + "55", stroke=col, sw=1.6)
            c.text(x0 + w + 8, y + 19, fmt.format(vals[i]), size=12.5, anchor="start")
    c.text(450, 437, "Jo has one contact, so effective size is 1 and constraint is 1, the most any person can have.", size=12.5, fill=MUTED)
    meta = dict(chapter=10,
                caption="Effective size and constraint for the friendship network. Dev has the largest effective size, but Hana has the lowest constraint: she is the only person whose contacts live in different parts of the network.",
                alt="Two horizontal bar charts with the same ten names. Effective size: Dev 3.33, Fay and Gus 3.00, Hana 2.33, Ana and Ben 2.00, Ivo 2.00, Cleo, Eli and Jo 1.00. Constraint: Hana is lowest at 0.43, then Fay and Gus at 0.45, Dev 0.47, Ivo 0.50, Ana and Ben 0.54, Cleo and Eli 0.66, Jo 1.00. Hana's bars are highlighted in orange.",
                data={"names": KITE_NAMES, "effective_size": [round(x, 3) for x in eff], "constraint": [round(x, 3) for x in con]})
    return c, meta


def brokerage_roles():
    c = Canvas(900, 280, "The five brokerage roles",
               "Five small drawings of a person in the middle of a chain of two arrows, with shape and color showing the groups of the three people.")
    A_, B_, C_ = ((BLUE, "circle"), (ORANGE, "square"), (PURPLE, "diamond"))
    roles = [("coordinator", "links two members of the same group", (A_, A_, A_)),
             ("itinerant", "an outsider linking two members of one group", (A_, B_, A_)),
             ("representative", "passes ties from own group outward", (A_, A_, B_)),
             ("gatekeeper", "controls entry into own group", (A_, B_, B_)),
             ("liaison", "links three different groups", (A_, B_, C_))]
    for k, (name, gloss, (gi, gj, gk)) in enumerate(roles):
        x0 = 20 + k * 175
        pts = [(x0 + 25, 120), (x0 + 87, 120), (x0 + 149, 120)]
        c.edge(pts[0], pts[1], ra=17, rb=17, directed=True, width=2.2, color="#7b8494")
        c.edge(pts[1], pts[2], ra=17, rb=17, directed=True, width=2.2, color="#7b8494")
        for (col, shape), p_, lab in zip((gi, gj, gk), pts, "ijk"):
            c.node(*p_, lab, r=14, fill="#ffffff", stroke=col, shape=shape, sw=3 if lab == "j" else 2, size=12)
        c.text(x0 + 87, 60, name, size=14, weight="700")
        words = gloss.split()
        half = len(words) // 2 + (len(words) % 2)
        c.text(x0 + 87, 180, " ".join(words[:half]), size=11.5, fill=MUTED)
        c.text(x0 + 87, 196, " ".join(words[half:]), size=11.5, fill=MUTED)
    c.text(450, 255, "In every drawing j brokers: i goes to j, j goes to k, and i does not go to k directly.", size=13, fill=MUTED)
    meta = dict(chapter=10,
                caption="Gould and Fernandez's five brokerage roles. The same chain of two arrows, i to j to k, is a different role depending on which groups the three people belong to. Person j is the broker.",
                alt="Five panels, each showing three people i, j and k in a row joined by two arrows. Coordinator: all three are blue circles. Itinerant: i and k are blue circles and j is an orange square. Representative: i and j are blue circles and k is an orange square. Gatekeeper: i is a blue circle, j and k are orange squares. Liaison: i is a blue circle, j an orange square and k a purple diamond.",
                data={"roles": [r[0] for r in roles]})
    return c, meta


EI_GROUP = [0] * 5 + [1] * 5


def ei_index():
    n = len(KITE_NAMES)
    nb = _nbrs(KITE_EDGES, n)
    c = Canvas(900, 430, "Inside ties and outside ties",
               "For each person in the friendship network, a bar split into ties to their own group and ties to the other group, with their E-I index at the right.")
    c.text(120, 30, "Each person's ties", size=13.5, weight="700", anchor="start")
    c.node(600, 26, "", r=7, fill=BLUE + "55", stroke=BLUE)
    c.text(614, 31, "same group (I)", size=12, anchor="start")
    c.node(730, 26, "", r=7, fill=ORANGE + "55", stroke=ORANGE)
    c.text(744, 31, "other group (E)", size=12, anchor="start")
    for i in range(n):
        y = 56 + i * 34
        ext = sum(1 for j in nb[i] if EI_GROUP[j] != EI_GROUP[i])
        inn = len(nb[i]) - ext
        c.node(30, y + 14, "", r=8, fill="#e5e7eb", stroke=INK, shape="circle" if EI_GROUP[i] == 0 else "square", sw=1.8)
        c.text(50, y + 19, KITE_NAMES[i], size=12.5, anchor="start")
        x = 130
        for cnt, col in ((inn, BLUE), (ext, ORANGE)):
            for _ in range(cnt):
                c.rect(x, y + 3, 44, 22, fill=col + "55", stroke=col, sw=1.6)
                x += 46
        ei = (ext - inn) / (ext + inn)
        c.text(640, y + 19, f"E-I {ei:+.2f}", size=12.5, anchor="start", weight="600", fill=ORANGE if ei > 0 else INK)
    c.text(450, 412, "Circles are the first five people, squares the other five. Each block is one tie.", size=12.5, fill=MUTED)
    meta = dict(chapter=10,
                caption="The E-I index for each person is (external ties minus internal ties) divided by all their ties. It runs from -1 (all ties inside the group) to +1 (all ties outside it). Here the groups are the first five people and the other five.",
                alt="Ten horizontal bars, one per person, each made of blocks: blue blocks for ties to their own group and orange blocks for ties to the other group. Fay and Gus have three orange blocks and two blue, giving E-I of plus 0.20. Hana, Ivo and Jo have only blue blocks, giving minus 1.00. Ana and Ben have one orange block and three blue, giving minus 0.50.",
                data={"names": KITE_NAMES, "group": EI_GROUP})
    return c, meta


# ---------------------------------------------------------------- chapter 11
def _pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / (sxx * syy) ** 0.5


def qap_null():
    import math
    import random
    n = len(KITE_NAMES)
    adj = [[0] * n for _ in range(n)]
    for a, b in KITE_EDGES:
        adj[a][b] = adj[b][a] = 1
    floor = [0] * 5 + [1] * 5
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    x = [adj[i][j] for i, j in pairs]
    obs = _pearson(x, [1 if floor[i] == floor[j] else 0 for i, j in pairs])
    rng = random.Random(1)
    draws = []
    for _ in range(10000):
        perm = list(range(n))
        rng.shuffle(perm)
        draws.append(_pearson(x, [1 if floor[perm[i]] == floor[perm[j]] else 0 for i, j in pairs]))
    # The correlation takes only a few values (it depends on how many friend pairs land on
    # the same floor), so draw one bar per possible value.
    vals = sorted({round(d, 6) for d in draws})
    gap = min(b2 - a2 for a2, b2 in zip(vals, vals[1:]))
    counts = {v: 0 for v in vals}
    for d in draws:
        counts[round(d, 6)] += 1
    lo, span = -0.55, 1.1
    c = Canvas(900, 440, "What no relationship looks like",
               "A bar chart of the correlations between friendship and sharing a floor after relabeling the people 10,000 times, with the observed correlation marked.")
    x0, y0, w, h = 90, 60, 720, 270
    top = max(counts.values()) * 1.12
    for v, cnt in counts.items():
        bx = x0 + (v - gap / 2 - lo) / span * w
        bh = h * cnt / top
        right = v >= obs - 1e-6
        col = ORANGE if right else BLUE
        c.rect(bx + 1, y0 + h - bh, gap / span * w - 2, bh, fill=col + "66", stroke=col, sw=1.2)
    sd = 1 / math.sqrt(44)
    pts = []
    for t in range(0, 221):
        xv = lo + t * span / 220
        yv = len(draws) * gap * math.exp(-xv * xv / (2 * sd * sd)) / (sd * math.sqrt(2 * math.pi))
        pts.append(f"{x0 + (xv - lo) / span * w:.1f},{y0 + h - h * yv / top:.1f}")
    c.add(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="6 4"/>')
    ox = x0 + (obs - lo) / span * w
    c.add(f'<line x1="{ox:.1f}" y1="{y0 - 6}" x2="{ox:.1f}" y2="{y0 + h}" stroke="{INK}" stroke-width="2.5"/>')
    c.text(ox + 8, y0 + 8, f"observed {obs:.3f}", size=13, anchor="start", weight="700")
    c.add(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{INK}" stroke-width="1.5"/>')
    for v in (-0.5, -0.25, 0, 0.25, 0.5):
        vx = x0 + (v - lo) / span * w
        c.text(vx, y0 + h + 20, f"{v:g}", size=12)
    c.text(x0 + w / 2, y0 + h + 44, "correlation after relabeling the people", size=13, fill=MUTED)
    c.text(x0, 412, "Orange bars: relabelings at least as high as the observed value. Dashed curve: the spread an ordinary test assumes.", size=12.5, fill=MUTED, anchor="start")
    share = sum(1 for d in draws if d >= obs - 1e-9) / len(draws)
    meta = dict(chapter=11,
                caption="The QAP reference distribution: the correlation between friendship and sharing a floor after relabeling the people 10,000 times, with the observed value marked. Relabeled correlations center near zero, and the observed value sits in the right tail.",
                alt="A bar chart of 10,000 relabeled correlations, which take only a handful of distinct values, centered near zero and spread from about minus 0.3 to plus 0.4. A vertical black line marks the observed correlation, 0.365, in the right tail, where the bars are drawn in orange. A dashed gray curve shows the normal spread an ordinary test would assume.",
                data={"observed": round(obs, 3), "share_at_least_observed": round(share, 4), "values": [[v, counts[v]] for v in vals]})
    return c, meta


# ---------------------------------------------------------------- chapter 12
def ergm_terms():
    c = Canvas(900, 440, "Common ERGM statistics",
               "Six panels, each showing one pattern that an exponential random graph model can count.")

    def dot(x, y, shape="circle", fill="#cfe5f3", stroke=BLUE):
        c.node(x, y, "", r=12, fill=fill, stroke=stroke, shape=shape, sw=2)

    def tie(a, b, **kw):
        c.edge(a, b, ra=12, rb=12, width=kw.pop("width", 2.4), color=kw.pop("color", INK), **kw)

    panels = [("Edges", "every tie counts one"), ("Same side", "ties between alike people"),
              ("Two-star", "one person, two ties"), ("Triangle", "three mutual ties"),
              ("Shared partners", "friends in common, with diminishing returns"), ("Hub", "one person with many ties")]
    for k, (title, note) in enumerate(panels):
        x0, y0 = (k % 3) * 300, (k // 3) * 220
        cx = x0 + 150
        c.caption(cx, y0 + 28, title)
        c.text(cx, y0 + 205, note, size=12.5, fill=MUTED)
        if k == 0:
            a, b = (cx - 45, y0 + 100), (cx + 45, y0 + 100)
            tie(a, b, color=BLUE); dot(*a); dot(*b)
        elif k == 1:
            a, b, d = (cx - 80, y0 + 90), (cx - 20, y0 + 90), (cx + 50, y0 + 90)
            e = (cx + 110, y0 + 90)
            tie(a, b, color=BLUE); dot(*a); dot(*b)
            tie(d, e, color="#9ca3af", dash="5 4"); dot(*d); dot(*e, shape="square", fill=ORANGE + "33", stroke=ORANGE)
            c.text((a[0] + b[0]) / 2, y0 + 135, "counts", size=12, fill=BLUE)
            c.text((d[0] + e[0]) / 2, y0 + 135, "does not", size=12, fill=MUTED)
        elif k == 2:
            m, a, b = (cx, y0 + 80), (cx - 55, y0 + 135), (cx + 55, y0 + 135)
            tie(m, a, color=BLUE); tie(m, b, color=BLUE); dot(*m, fill=ORANGE + "33", stroke=ORANGE); dot(*a); dot(*b)
        elif k == 3:
            a, b, d = (cx, y0 + 70), (cx - 55, y0 + 145), (cx + 55, y0 + 145)
            tie(a, b, color=BLUE); tie(b, d, color=BLUE); tie(d, a, color=BLUE); dot(*a); dot(*b); dot(*d)
        elif k == 4:
            a, b = (cx - 55, y0 + 100), (cx + 55, y0 + 100)
            mids = [(cx, y0 + 55), (cx, y0 + 100), (cx, y0 + 145)]
            for m in mids:
                tie(a, m, color="#9ca3af", width=1.6); tie(m, b, color="#9ca3af", width=1.6)
            tie(a, b, color=BLUE, curve=0)
            for m in mids:
                dot(*m)
            dot(*a, fill=ORANGE + "33", stroke=ORANGE); dot(*b, fill=ORANGE + "33", stroke=ORANGE)
        else:
            h = (cx, y0 + 100)
            for ang in range(0, 360, 60):
                x = cx + 62 * math.cos(math.radians(ang))
                y = y0 + 100 + 62 * math.sin(math.radians(ang))
                tie(h, (x, y), color=BLUE, width=1.8); dot(x, y)
            dot(*h, fill=ORANGE + "33", stroke=ORANGE)
    meta = dict(chapter=12,
                caption="Common ERGM statistics. Each panel shows the pattern that is counted. Shared partners are the people two tied nodes both know.",
                alt="Six small drawings of network patterns. Edges: two nodes joined by a line. Same side: two circles joined by a line, which counts, and a circle and a square joined by a dashed line, which does not. Two-star: one node joined to two others. Triangle: three nodes all joined. Shared partners: two tied nodes, drawn in orange, with three common neighbors between them, and a note that each extra shared partner counts less. Hub: one node joined to six others.",
                data={"terms": [p_[0] for p_ in panels]})
    return c, meta


GOF_ROWS = [("Triangles", 45.0, 21.8, 42.1), ("Two-stars", 528.0, 340.7, 389.3), ("Three-stars", 1764.0, 472.6, 668.8)]


def ergm_gof():
    c = Canvas(900, 330, "Does the model reproduce the karate club?",
               "A dot chart of simulated averages as a percent of the real counts for triangles, two-stars and three-stars, under two models.")
    x0, w = 170, 640
    scale = lambda pct: x0 + w * pct / 120  # noqa: E731
    for pct in (0, 25, 50, 75, 100):
        c.add(f'<line x1="{scale(pct)}" y1="70" x2="{scale(pct)}" y2="250" stroke="{"#9ca3af" if pct == 100 else "#e5e7eb"}" stroke-width="{2 if pct == 100 else 1}"/>')
        c.text(scale(pct), 272, f"{pct}%", size=12, fill=MUTED)
    c.text(scale(100), 60, "real network", size=12.5, weight="700")
    for k, (name, real, simple, closure) in enumerate(GOF_ROWS):
        y = 105 + k * 60
        c.text(x0 - 14, y + 5, name, size=14, anchor="end")
        for val, col, shape, dy in ((simple, ORANGE, "square", -9), (closure, BLUE, "circle", 9)):
            pct = 100 * val / real
            c.node(scale(pct), y + dy, "", r=8, fill=col + "55", stroke=col, shape=shape, sw=2)
            c.text(scale(pct) + 16, y + dy + 4, f"{pct:.0f}%", size=12, anchor="start", fill=col)
    c.node(x0 + 20, 305, "", r=7, fill=ORANGE + "55", stroke=ORANGE, shape="square")
    c.text(x0 + 36, 309, "edges + same side", size=12.5, anchor="start")
    c.node(x0 + 230, 305, "", r=7, fill=BLUE + "55", stroke=BLUE)
    c.text(x0 + 246, 309, "edges + same side + shared partners", size=12.5, anchor="start")
    meta = dict(chapter=12,
                caption="How well each model reproduces features of the karate club it was not fit to. Each dot is the average over simulated networks as a percent of the real count, so 100 means a perfect match.",
                alt="A dot chart with three rows: triangles, two-stars and three-stars. For triangles, the edges-and-side model is at 48 percent and the model with shared partners at 94 percent. For two-stars, the dots are at 65 and 74 percent. For three-stars, they are at 27 and 38 percent. A vertical line marks 100 percent.",
                data={"rows": [{"statistic": r[0], "real": r[1], "edges_side": r[2], "plus_shared_partners": r[3]} for r in GOF_ROWS]})
    return c, meta


FIGURES = {
    "two-teams": two_teams, "habit": habit, "dyad-triad": dyad_triad,
    "balance-triads": balance_triads, "two-camps": two_camps, "weak-ties": weak_ties,
    "structural-hole": structural_hole, "homophily": homophily, "small-world": small_world,
    "three-formats": three_formats, "two-mode": two_mode, "boundary": boundary, "levels": levels,
    "layout-matters": layout_matters, "distance-lies": distance_lies,
    "hairball-matrix": hairball_matrix, "encodings": encodings,
    "four-centralities": four_centralities, "betweenness-paths": betweenness_paths,
    "centralization": centralization, "in-out-bars": in_out_bars,
    "walks-paths": walks_paths, "distance-matrix": distance_matrix, "density-dice": density_dice,
    "clustering-idea": clustering_idea, "components": components_fig, "cores": cores_fig,
    "triad-types": triad_types,
    "office-network": office_network, "equivalence-kinds": equivalence_kinds,
    "blockmodel-matrix": blockmodel_matrix, "core-periphery": core_periphery,
    "ego-networks": ego_networks, "holes-idea": holes_idea, "effective-size-bars": effective_size_bars,
    "brokerage-roles": brokerage_roles, "ei-index": ei_index, "qap-null": qap_null,
    "ergm-terms": ergm_terms, "ergm-gof": ergm_gof,
    "karate-communities": karate_communities, "modularity-bars": modularity_bars,
    "resolution-sweep": resolution_sweep, "group-ladder": group_ladder,
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

"""Figures for the collecting-data chapter (chapter 26). Standard library only.

The karate club comes from books/sna/data/karate. Counts in the captions are computed here
and must match what the chapter's code prints (checked by the asserts).
"""
from collections import deque

from fig_case_karate import N, load, positions
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, RED, Canvas

GRAY = "#9ca3af"


def neighbours(ties):
    nb = [[] for _ in range(N)]
    for a, b, _ in ties:
        nb[a].append(b)
        nb[b].append(a)
    return nb


def boundary_cut():
    ties, side = load()
    inside = [s == 0 for s in side]
    kept = [(a, b) for a, b, _ in ties if inside[a] and inside[b]]
    cut = [(a, b) for a, b, _ in ties if inside[a] != inside[b]]
    assert len(kept) == 35 and len(cut) == 11
    w, h = 760, 560
    c = Canvas(w, h, "A boundary drawn through the karate club",
               "The karate club with Mr. Hi's side in blue, the officer's side faded, and the ties that cross the boundary dashed.")
    pos = positions(ties, 40, 40, w - 80, h - 110)
    for a, b, _ in ties:
        if inside[a] and inside[b]:
            c.edge(pos[a], pos[b], ra=10, rb=10, width=1.6, color=INK)
        elif not inside[a] and not inside[b]:
            c.edge(pos[a], pos[b], ra=10, rb=10, width=1.0, color=FAINT)
        else:
            c.edge(pos[a], pos[b], ra=10, rb=10, width=1.6, color=RED, dash="5 4")
    for i in range(N):
        c.node(pos[i][0], pos[i][1], str(i + 1), r=11, fill=(BLUE + "cc") if inside[i] else (GRAY + "55"),
               stroke=INK if inside[i] else GRAY, size=9.5, sw=1.3)
    c.text(w / 2, h - 22, "Solid: the 35 ties kept. Dashed: the 11 ties the boundary cuts. Faded: the 17 members left out.", size=13, fill=MUTED)
    meta = dict(chapter=26,
                caption="Studying only Mr. Hi's side of the karate club keeps 17 members and 35 ties and cuts 11 ties to members outside the boundary.",
                alt="A network of 34 numbered members. Seventeen members on Mr. Hi's side are blue circles joined by 35 solid black ties. Seventeen members on the officer's side are faded gray circles joined by faint gray ties. Eleven red dashed ties cross between the two sides.",
                data={"kept_ties": len(kept), "cut_ties": len(cut)})
    return c, meta


def snowball_panels():
    ties, side = load()
    nb = neighbours(ties)

    def waves(seed):
        dist = {seed: 0}
        queue = deque([seed])
        while queue:
            u = queue.popleft()
            for v in nb[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        return dist

    w, h = 900, 520
    c = Canvas(w, h, "Two snowball samples of the karate club",
               "Two drawings of the karate club after a two-wave snowball sample, one started from member 12 and one from member 1.")
    shown = {}
    colors = {0: ORANGE, 1: BLUE, 2: GREEN}
    for k, seed in enumerate((11, 0)):
        dist = waves(seed)
        reached = {v for v, d in dist.items() if d <= 2}
        asked = {v for v, d in dist.items() if d <= 1}
        seen = [(a, b) for a, b, _ in ties if a in asked or b in asked]
        px = 20 + k * 445
        pos = positions(ties, px + 25, 55, 385, 380)
        c.caption(px + 210, 28, f"Seed: member {seed + 1}", size=15)
        for a, b, _ in ties:
            on = (a, b) in seen
            c.edge(pos[a], pos[b], ra=10, rb=10, width=1.6 if on else 0.8, color=INK if on else FAINT)
        for i in range(N):
            if i in reached:
                c.node(pos[i][0], pos[i][1], str(i + 1), r=11, fill=colors[dist[i]] + "cc", size=9.5, sw=1.3)
            else:
                c.node(pos[i][0], pos[i][1], str(i + 1), r=11, fill=GRAY + "33", stroke=GRAY, size=9.5, sw=1.0)
        c.text(px + 210, 470, f"{len(reached)} members named, {len(asked)} interviewed, {len(seen)} ties seen", size=13, fill=MUTED)
        shown[f"member {seed + 1}"] = {"named": len(reached), "interviewed": len(asked), "ties_seen": len(seen)}
    assert shown["member 12"] == {"named": 17, "interviewed": 2, "ties_seen": 16}
    assert shown["member 1"] == {"named": 26, "interviewed": 17, "ties_seen": 51}
    c.text(w / 2, h - 16, "Orange: the seed. Blue: named by the seed. Green: named by those. Bold ties: seen. Faded: never reached.", size=13, fill=MUTED)
    meta = dict(chapter=26,
                caption="A two-wave snowball sample from member 12 names 17 members and sees 16 ties. From member 1 it names 26 members and sees 51 ties.",
                alt="Two drawings of the 34-member karate club. On the left the sample starts at member 12: 17 members are colored, 2 were interviewed, and 16 ties are drawn bold. On the right it starts at member 1: 26 members are colored, 17 were interviewed, and 51 ties are drawn bold. Members never reached are faded gray.",
                data=shown)
    return c, meta


FIGURES = {"boundary-cut": boundary_cut, "snowball-seeds": snowball_panels}

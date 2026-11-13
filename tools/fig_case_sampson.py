"""Figures for the case study of Sampson's monastery.

Standard library only. The waves are computed from books/sna/data/sampson/edges.csv and the
groups from books/sna/data/sampson_groups/nodes.csv. The communities used for the agreement
picture are the ones the Rust tab of the chapter prints (Louvain, resolution 1, seed 1, on the
graph where either direction counts as a tie); the agreement numbers are computed here.
"""
import csv
from collections import Counter
from math import comb
from pathlib import Path

from fig_layout import fit, stress_layout
from figs import BLUE, GREEN, INK, MUTED, ORANGE, PAPER, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"
LOOK = {"Turks": ("circle", BLUE), "Loyal": ("square", ORANGE), "Outcasts": ("diamond", RED), "Waverers": ("triangle", GREEN)}

# Communities printed by the Rust tab of chapter 30 (members by name).
COMMUNITIES = {
    1: [["Romuald", "Bonaventure", "Ambrose", "Boniface", "Albert", "Amand"],
        ["Berthold", "Peter", "Louis", "Winfrid", "John Bosco", "Gregory", "Hugh", "Basil"],
        ["Victor", "Mark", "Elias", "Simplicius"]],
    2: [["Romuald", "Bonaventure", "Victor", "Boniface", "Albert", "Amand", "Basil"],
        ["Ambrose", "Elias", "Simplicius"],
        ["Berthold", "Peter", "Louis", "Winfrid", "John Bosco", "Gregory", "Hugh", "Mark"]],
    3: [["Romuald", "Bonaventure", "Victor", "Boniface", "Albert", "Amand", "Basil"],
        ["Ambrose", "Mark", "Elias", "Simplicius"],
        ["Berthold", "Peter", "Louis", "Winfrid", "John Bosco", "Gregory", "Hugh"]],
}


def load():
    names = [r["name"] for r in csv.DictReader(open(DATA / "sampson" / "nodes.csv", newline=""))]
    group = {r["name"]: r["group"] for r in csv.DictReader(open(DATA / "sampson_groups" / "nodes.csv", newline=""))}
    ix = {n: i for i, n in enumerate(names)}
    rows = [r for r in csv.DictReader(open(DATA / "sampson" / "edges.csv", newline="")) if r["relation"] == "liking"]
    waves = {k: sorted({(ix[r["from"]], ix[r["to"]]) for r in rows if int(r["time"]) == k}) for k in (1, 2, 3)}
    return names, [group[n] for n in names], waves


def ari(a, b):
    n = len(a)
    joint, ra, rb = Counter(zip(a, b)), Counter(a), Counter(b)
    index = sum(comb(v, 2) for v in joint.values())
    sa, sb = sum(comb(v, 2) for v in ra.values()), sum(comb(v, 2) for v in rb.values())
    expected = sa * sb / comb(n, 2)
    return (index - expected) / ((sa + sb) / 2 - expected)


def shape(c, x, y, kind, r, fill, stroke, sw=1.8):
    if kind == "triangle":
        pts = f"{x:.1f},{y - r * 1.25:.1f} {x + r * 1.2:.1f},{y + r * 0.95:.1f} {x - r * 1.2:.1f},{y + r * 0.95:.1f}"
        c.add(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    else:
        c.node(x, y, "", r=r, fill=fill, stroke=stroke, shape=kind, sw=sw)


def waves_by_group():
    names, group, waves = load()
    n = len(names)
    union = sorted({tuple(sorted(e)) for es in waves.values() for e in es})
    base = fit(stress_layout(n, union, seed=3), 0, 0, 250, 240)
    c = Canvas(900, 400, "Sampson's novices at three times, by group",
               "Three copies of the same eighteen novices, drawn in the same places, with liking choices at times 1, 2 and 3. Shape and colour show Sampson's group.")
    tops = {}
    mutual_counts = {}
    for k in (1, 2, 3):
        x0, y0 = 25 + (k - 1) * 295, 55
        pos = [(x0 + p[0] + 10, y0 + p[1]) for p in base]
        es = set(waves[k])
        indeg = [sum(1 for _, b in es if b == i) for i in range(n)]
        top = sorted(range(n), key=lambda i: (-indeg[i], i))[:3]
        tops[k] = [names[i] for i in top]
        mutual = sorted((a, b) for a, b in es if a < b and (b, a) in es)
        mutual_counts[k] = len(mutual)
        c.caption(x0 + 135, 30, f"Time {k}: {len(es)} choices, {len(mutual)} mutual pairs", size=13)
        for a, b in sorted(es):
            if (b, a) in es:
                if a < b:
                    c.edge(pos[a], pos[b], ra=9, rb=9, width=2.2, color=INK, opacity=0.65)
            else:
                c.edge(pos[a], pos[b], ra=9, rb=9, directed=True, width=0.9, color=MUTED, opacity=0.6)
        for i, p in enumerate(pos):
            kind, colour = LOOK[group[i]]
            shape(c, p[0], p[1], kind, 8.5, colour if i in top else PAPER, colour)
        for i in top:
            c.text(pos[i][0], pos[i][1] - 15, names[i], size=11.5, weight="600")
    lx = 150
    for g, (kind, colour) in LOOK.items():
        shape(c, lx, 352, kind, 7, PAPER, colour)
        c.text(lx + 14, 357, g, size=12.5, anchor="start")
        lx += 150
    c.text(450, 385, "Dark lines join mutual pairs; grey arrows are one-way choices. Filled marks are the three most chosen.",
           size=12, fill=MUTED)
    meta = dict(chapter=30,
                caption="Sampson's liking choices at times 1, 2 and 3, drawn in the same places each time. Shape and colour give Sampson's group; filled marks are the three most chosen novices that time; dark lines join mutual pairs and grey arrows are one-way choices.",
                alt=f"Three copies of the same 18 marks, one per time, joined by lines and arrows. The marks are circles for the Turks, squares for the Loyal, diamonds for the Outcasts and triangles for the Waverers. Time 1 shows 55 choices with {mutual_counts[1]} mutual pairs, time 2 shows 57 with {mutual_counts[2]}, time 3 shows 56 with {mutual_counts[3]}. Filled marks are the three most chosen: {', '.join(tops[1])} at time 1, {', '.join(tops[2])} at time 2 and {', '.join(tops[3])} at time 3.",
                data={"top3": tops, "mutual_pairs": {str(k): v for k, v in mutual_counts.items()}})
    return c, meta


def agreement():
    names, group, _ = load()
    labs = {}
    for k, comms in COMMUNITIES.items():
        label = [None] * len(names)
        for j, members in enumerate(comms):
            for m in members:
                label[names.index(m)] = j
        assert None not in label
        labs[f"Liking, time {k}"] = label
    labs["Sampson's groups"] = group
    keys = list(labs)
    m = [[ari(labs[a], labs[b]) for b in keys] for a in keys]
    # The numbers the chapter prints for the Rust tab.
    assert [round(m[i][3], 3) for i in range(3)] == [0.037, 0.170, 0.077], m
    cell, left, top = 118, 170, 70
    c = Canvas(left + cell * 4 + 40, top + cell * 4 + 80, "Agreement between partitions of the novices",
               "A four by four grid of adjusted Rand index values between the Louvain communities of liking at times 1, 2 and 3 and Sampson's groups.")
    c.caption(left + cell * 2, 30, "Adjusted Rand index between partitions")
    for j, k in enumerate(keys):
        c.text(left + cell * (j + 0.5), top - 12, k, size=12.5)
        c.text(left - 12, top + cell * (j + 0.5) + 4, k, size=12.5, anchor="end")
    for i in range(4):
        for j in range(4):
            v = m[i][j]
            shade = max(v, 0)
            r, g_, b = (int(255 - shade * 255), int(255 - shade * (255 - 0x72)), int(255 - shade * (255 - 0xB2)))
            c.rect(left + cell * j, top + cell * i, cell, cell, fill=f"#{r:02x}{g_:02x}{b:02x}", stroke=PAPER, sw=2)
            c.text(left + cell * (j + 0.5), top + cell * (i + 0.5) + 6, f"{v:.2f}", size=17, weight="600",
                   fill=PAPER if shade > 0.6 else INK)
    c.rect(left + cell * 3, top, cell, cell * 3, fill="none", stroke=ORANGE, sw=3)
    c.text(left + cell * 2, top + cell * 4 + 26, "0 is no more agreement than chance; 1 is the same partition.", size=12, fill=MUTED)
    c.text(left + cell * 2, top + cell * 4 + 46, "The orange frame is the question of the chapter.", size=12, fill=MUTED)
    last = [m[i][3] for i in range(3)]
    meta = dict(chapter=30,
                caption="How well the communities of liking at each time (Louvain, seed 1) and Sampson's groups agree, as the adjusted Rand index. The communities of one wave resemble those of the next; none of them resembles Sampson's groups much. The orange frame marks the comparison with the groups.",
                alt=f"A four by four grid of numbers with rows and columns Liking time 1, Liking time 2, Liking time 3 and Sampson's groups. The diagonal is 1.00. Liking time 1 and time 2 score {m[0][1]:.2f}, time 2 and time 3 score {m[1][2]:.2f}, and time 1 and time 3 score {m[0][2]:.2f}. Against Sampson's groups the three times score {last[0]:.2f}, {last[1]:.2f} and {last[2]:.2f}. Cells with higher values are darker blue.",
                data={"keys": keys, "ari": [[round(v, 3) for v in row] for row in m]})
    return c, meta


FIGURES = {"sampson-case-waves": waves_by_group, "sampson-agreement": agreement}

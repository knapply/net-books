"""Figures for the networks-as-data chapter (chapter 3). Standard library only.

Counts drawn here are computed from books/sna/data and asserted to match the numbers the
chapter's code prints.
"""
import csv
from pathlib import Path

from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, RED, Canvas, ring

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"
GRAY = "#9ca3af"


def read(name):
    with open(DATA / name) as f:
        return list(csv.DictReader(f))


def dyad_counts(relation):
    arcs = {(int(r["from"]), int(r["to"])) for r in read("krackhardt/edges.csv") if r["relation"] == relation}
    mutual = sum(1 for a, b in arcs if a < b and (b, a) in arcs)
    asym = len(arcs) - 2 * mutual
    return mutual, asym, 210 - mutual - asym


def dyads_krackhardt():
    rows = [(rel, dyad_counts(key)) for rel, key in
            [("Advice", "advice"), ("Friendship", "friendship"), ("Reports to", "reports_to")]]
    assert [r[1] for r in rows] == [(45, 100, 65), (23, 56, 131), (0, 20, 190)]
    w, h = 820, 360
    c = Canvas(w, h, "Dyads in the three Krackhardt relations",
               "Horizontal bars split the 210 pairs of managers into mutual, one-sided and no-tie pairs for advice, friendship and reporting.")
    x0, scale = 130, 640 / 210
    c.text(w / 2, 26, "Each bar is the 210 pairs of managers", size=15, weight="600")
    for k, (label, (m, a, n)) in enumerate(rows):
        y = 70 + k * 78
        c.text(x0 - 12, y + 25, label, size=15, anchor="end", weight="600")
        x = x0
        for count, fill, stroke, tcol in [(m, BLUE + "cc", BLUE, PAPER), (a, ORANGE + "cc", ORANGE, INK), (n, "#f3f4f6", GRAY, MUTED)]:
            if count:
                c.rect(x, y, count * scale, 38, fill=fill, stroke=stroke, sw=1.2)
                if count * scale > 28:
                    c.text(x + count * scale / 2, y + 25, str(count), size=14, weight="600", fill=tcol)
            x += count * scale
        # what each rule for undirected data keeps
        c.add(f'<line x1="{x0 + (m + a) * scale:.1f}" y1="{y - 6}" x2="{x0 + (m + a) * scale:.1f}" y2="{y + 44}" '
              f'stroke="{INK}" stroke-width="1.6" stroke-dasharray="4 3"/>')
        c.add(f'<line x1="{x0 + m * scale:.1f}" y1="{y + 44}" x2="{x0 + m * scale:.1f}" y2="{y + 50}" stroke="{INK}" stroke-width="1.6"/>')
    ly = h - 54
    for i, (fill, stroke, text) in enumerate([(BLUE + "cc", BLUE, "mutual"), (ORANGE + "cc", ORANGE, "one-sided"), ("#f3f4f6", GRAY, "no tie")]):
        c.rect(150 + i * 130, ly - 12, 16, 16, fill=fill, stroke=stroke, sw=1.2)
        c.text(172 + i * 130, ly + 1, text, size=13, anchor="start", fill=MUTED)
    c.text(150, ly + 28, "Dashed line: where \"either\" stops counting. \"Both\" counts only the blue segment (tick below the bar).", size=12.5, anchor="start", fill=MUTED)
    meta = dict(chapter=3,
                caption="The three Krackhardt relations by what each pair of managers did. Mutual pairs are returned ties; one-sided pairs are asymmetric. The rule you choose for undirected data (either or both) keeps everything up to the dashed marks, or only the first segment.",
                alt="Three horizontal bars, one each for advice, friendship and reporting, each split into mutual, one-sided and no-tie pairs out of 210. Advice: 45 mutual, 100 one-sided, 65 none. Friendship: 23, 56, 131. Reporting: 0, 20, 190.",
                data={rel: dict(zip(("mutual", "one_sided", "none"), v)) for rel, v in rows})
    return c, meta


def karate_thresholds_data():
    ties = [(int(r["source"]), int(r["target"]), int(r["contexts"])) for r in read("karate/edges.csv")]
    out = []
    for k in range(1, 7):
        kept = [(a, b) for a, b, v in ties if v >= k]
        parent = list(range(35))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for a, b in kept:
            parent[find(a)] = find(b)
        sizes = {}
        for i in range(1, 35):
            sizes[find(i)] = sizes.get(find(i), 0) + 1
        out.append((k, len(kept), len(sizes), max(sizes.values())))
    assert out == [(1, 78, 1, 34), (2, 72, 1, 34), (3, 48, 7, 28), (4, 21, 19, 15), (5, 9, 25, 5), (6, 2, 32, 2)]
    w, h = 820, 410
    c = Canvas(w, h, "Thresholding the karate club's valued ties",
               "Two small charts of ties kept and pieces against the threshold on the number of shared settings.")
    panels = [("Ties kept", 1, 78, 70), ("Separate pieces", 2, 32, 440)]
    for title, col, top, px in panels:
        pw, ph, py = 310, 220, 70
        c.text(px + pw / 2, 42, title, size=15, weight="600")
        c.add(f'<line x1="{px}" y1="{py + ph}" x2="{px + pw}" y2="{py + ph}" stroke="{INK}" stroke-width="1.4"/>')
        c.add(f'<line x1="{px}" y1="{py}" x2="{px}" y2="{py + ph}" stroke="{INK}" stroke-width="1.4"/>')
        pts = []
        for k, *vals in out:
            vals = {1: vals[0], 2: vals[1]}
            x = px + (k - 1) / 5 * pw
            y = py + ph - vals[col] / top * ph
            pts.append((x, y, vals[col], k))
            c.text(x, py + ph + 22, str(k), size=13, fill=MUTED)
        c.add('<polyline fill="none" stroke="%s" stroke-width="2.2" points="%s"/>' % (BLUE if col == 1 else RED, " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in pts)))
        for x, y, v, k in pts:
            c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{BLUE if col == 1 else RED}" stroke="{PAPER}" stroke-width="1.5"/>')
            c.text(x + (14 if (col == 2 and k == 1) else 0), y - 10, str(v), size=12, fill=INK)
        c.text(px + pw / 2, py + ph + 50, "ties must be in at least this many settings", size=12.5, fill=MUTED)
    c.text(w / 2, h - 18, "Between 2 and 3 the club goes from one piece to seven: 28 members stay in the largest.", size=13, fill=MUTED)
    meta = dict(chapter=3,
                caption="Thresholding the karate club's valued ties. Each step up in the number of shared settings removes ties, and between 2 and 3 the club breaks from one piece into seven.",
                alt="Two line charts with the threshold, from 1 to 6 shared settings, across the bottom. The first shows ties kept, falling from 78 to 72, 48, 21, 9 and 2. The second shows separate pieces: 1, 1, 7, 19, 25 and 32, with the steepest rise between thresholds 2 and 3.",
                data={"threshold": [r[0] for r in out], "ties": [r[1] for r in out], "pieces": [r[2] for r in out]})
    return c, meta


def id_phantoms():
    w, h = 820, 400
    c = Canvas(w, h, "Phantom nodes from spelling",
               "A network of seven names that is really five people: 'ana' and 'Chloe ' (with a trailing space) are extra nodes.")
    people = ["Ana", "Ben", "Chloe", "Dev", "Eli"]
    pos = dict(zip(people, ring(250, 200, 120, 5)))
    pos["ana"] = (95, 70)
    pos["Chloe "] = (95, 330)
    rows = [("Ana", "Ben"), ("ana", "Chloe"), ("Ben", "Chloe"), ("Chloe ", "Ana"), ("Dev", "Ana"), ("Dev", "Chloe"), ("Eli", "Chloe")]
    for a, b in rows:
        bad = a not in people or b not in people
        c.edge(pos[a], pos[b], ra=24, rb=24, directed=True, color=RED if bad else INK, width=2.2 if bad else 1.8, dash="6 4" if bad else None)
    for name in people:
        c.node(*pos[name], name, r=24, fill=BLUE + "33", size=13)
    for name in ("ana", "Chloe "):
        c.node(*pos[name], name.replace(" ", "␣"), r=24, fill="#fde8d8", stroke=RED, size=12)
    c.text(560, 80, "What the file says", size=15, anchor="start", weight="600")
    c.lines(560, 108, ["Ana,Ben", "ana,Chloe", "Ben,Chloe", "Chloe␣,Ana", "Dev,Ana", "Dev,Chloe", "Eli,Chloe"], size=14, mono=True)
    c.text(560, 262, "7 different strings", size=14, anchor="start", weight="600", fill=RED)
    c.text(560, 286, "5 people on the roster", size=14, anchor="start", weight="600", fill=BLUE)
    c.text(560, 318, "Compare every id with the roster.", size=13, anchor="start", fill=MUTED)
    c.text(560, 338, "Whatever is left over is a typo, not a person.", size=13, anchor="start", fill=MUTED)
    meta = dict(chapter=3,
                caption="A file with one lower-case name and one trailing space has seven names for five people. The two phantom nodes (outlined in red) carry the ties that belong to Ana and Chloe.",
                alt="A drawing with five blue people, Ana, Ben, Chloe, Dev and Eli, around a ring, plus two orange nodes outside it, labeled ana and Chloe with a space mark. Two dashed red arrows run from the orange nodes: ana to Chloe and Chloe-space to Ana. To the right, the seven lines of the file and a note that there are seven different strings but five people on the roster.",
                data={"strings": 7, "people": 5})
    return c, meta


def tidy_tables():
    w, h = 820, 360
    c = Canvas(w, h, "Two tidy tables and their views",
               "A node table and an edge table are the data; the adjacency matrix and adjacency list are views of the edge table.")
    names = ["Ana", "Ben", "Chloe", "Dev", "Eli"]
    ties = [("Ana", "Ben"), ("Ana", "Chloe"), ("Ben", "Chloe"), ("Chloe", "Ana"), ("Dev", "Ana"), ("Dev", "Chloe"), ("Eli", "Chloe")]
    # node table
    c.text(20, 36, "nodes: one row per person", size=14, weight="600", anchor="start")
    for i, (hdr, vals) in enumerate([("id", names), ("team", ["north", "north", "south", "south", "south"])]):
        x = 20 + i * 90
        c.rect(x, 52, 90, 26, fill="#e5e7eb", stroke=GRAY, sw=1)
        c.text(x + 45, 70, hdr, size=13, weight="600")
        for r, v in enumerate(vals):
            c.rect(x, 78 + r * 26, 90, 26, fill=PAPER, stroke=GRAY, sw=1)
            c.text(x + 45, 96 + r * 26, v, size=13)
    # edge table
    c.text(250, 36, "ties: one row per tie", size=14, weight="600", anchor="start")
    for i, hdr in enumerate(["source", "target", "relation"]):
        x = 250 + i * 90
        c.rect(x, 52, 90, 26, fill="#e5e7eb", stroke=GRAY, sw=1)
        c.text(x + 45, 70, hdr, size=13, weight="600")
        for r, t in enumerate(ties):
            v = t[i] if i < 2 else "advice"
            c.rect(x, 78 + r * 26, 90, 26, fill=PAPER, stroke=GRAY, sw=1)
            c.text(x + 45, 96 + r * 26, v, size=13)
    # views
    c.text(690, 36, "views (not the data)", size=14, weight="600", fill=MUTED)
    cell = 26
    for i in range(5):
        for j in range(5):
            on = (names[i], names[j]) in ties
            c.rect(600 + j * cell, 52 + i * cell, cell, cell, fill=(BLUE + "55") if on else PAPER, stroke=GRAY, sw=1)
            c.text(600 + j * cell + cell / 2, 52 + i * cell + 18, "1" if on else "0", size=12, fill=INK if on else GRAY)
    c.text(665, 205, "adjacency matrix", size=13, fill=MUTED)
    c.lines(600, 235, ["Ana: Ben, Chloe", "Ben: Chloe", "Chloe: Ana", "Dev: Ana, Chloe", "Eli: Chloe"], size=13, mono=True, fill=MUTED)
    c.text(665, 345, "adjacency list", size=13, fill=MUTED)
    c.add(f'<line x1="530" y1="140" x2="593" y2="140" stroke="{GRAY}" stroke-width="2" marker-end="url(#{c.marker(GRAY)})"/>')
    meta = dict(chapter=3,
                caption="The tidy form of network data is two tables, one row per node and one row per tie. The adjacency matrix and the adjacency list are views of the tie table.",
                alt="Left, a table of five people with a team column. Middle, a table of seven ties with source, target and relation columns. Right, an arrow to a five by five matrix of ones and zeros and a list of who each person goes to, labeled as views, not the data.",
                data={"nodes": 5, "ties": 7})
    return c, meta


FIGURES = {"dyads-krackhardt": dyads_krackhardt, "karate-thresholds-data": karate_thresholds_data,
           "id-phantoms": id_phantoms, "tidy-tables": tidy_tables}

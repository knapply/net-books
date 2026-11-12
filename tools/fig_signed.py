"""Figures for the chapter on signed and valued networks.

Standard library only. The four triangle types are spelled out; the Sampson picture is
computed from books/sna/data/sampson/edges.csv (liking and disliking at time 3, keeping a pair
only when every choice about it has the same sign) and the karate panels from
books/sna/data/karate/edges.csv.
"""
import csv
import math
from itertools import combinations
from pathlib import Path

from fig_layout import fit, stress_layout
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, RED, Canvas, ring

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"
POS, NEG = BLUE, RED


def signed_pairs():
    """Sampson's signed ties among 18 novices: (names, [(a, b, sign)])."""
    rows = [r for r in csv.DictReader(open(DATA / "sampson" / "edges.csv", newline=""))
            if r["time"] == "3" and r["relation"] in ("liking", "disliking")]
    names = sorted({r["from"] for r in csv.DictReader(open(DATA / "sampson" / "edges.csv", newline=""))}
                   | {r["to"] for r in csv.DictReader(open(DATA / "sampson" / "edges.csv", newline=""))})
    ix = {n: i for i, n in enumerate(names)}
    seen = {}
    for r in rows:
        key = tuple(sorted((ix[r["from"]], ix[r["to"]])))
        seen.setdefault(key, set()).add(int(r["sign"]))
    return names, sorted((a, b, next(iter(s))) for (a, b), s in seen.items() if len(s) == 1)


def best_split(n, ties):
    """Camps (list of +1/-1, node 0 is +1) with the fewest disagreeing ties, and that fewest."""
    best, arg = None, None
    for mask in range(2 ** (n - 1)):
        camp = [1] + [1 - 2 * ((mask >> k) & 1) for k in range(n - 1)]
        bad = sum(1 for a, b, s in ties if camp[a] * camp[b] != s)
        if best is None or bad < best:
            best, arg = bad, camp
    return best, arg


def triad_types():
    c = Canvas(900, 270, "The four kinds of triangle in a signed network",
               "Four triangles with the signs of their three ties.")
    kinds = [("+ + +", [1, 1, 1], "balanced", "three friends"),
             ("+ + −", [1, 1, -1], "unbalanced", "two friends, and one of them dislikes the third"),
             ("+ − −", [1, -1, -1], "balanced", "two friends with a shared enemy"),
             ("− − −", [-1, -1, -1], "unbalanced", "three people who dislike each other")]
    for k, (label, signs, verdict, story) in enumerate(kinds):
        cx = 120 + k * 225
        pts = [(cx, 52), (cx - 62, 150), (cx + 62, 150)]
        for (i, j), s in zip([(0, 1), (0, 2), (1, 2)], signs):
            c.edge(pts[i], pts[j], ra=13, rb=13, color=POS if s > 0 else NEG, width=2.6,
                   dash=None if s > 0 else "7 5", sign="+" if s > 0 else "-")
        for p in pts:
            c.node(p[0], p[1], "", r=12, fill=PAPER, stroke=INK)
        good = verdict == "balanced"
        c.text(cx, 192, label, size=15, weight="700", mono=True)
        c.text(cx, 214, verdict, size=14, weight="700", fill=GREEN if good else ORANGE)
        words, rows = story.split(), [""]
        for w in words:
            if len(rows[-1]) + len(w) > 30:
                rows.append("")
            rows[-1] = (rows[-1] + " " + w).strip()
        c.lines(cx, 234, rows, size=11.5, anchor="middle", fill=MUTED)
    meta = dict(chapter=16,
                caption="The four triangles a signed network can contain. Balanced triangles have an even number of negative ties (none or two); unbalanced ones have an odd number (one or three). Solid blue lines are positive ties and dashed red lines are negative ones.",
                alt="Four triangles side by side. The first has three positive ties and is labeled balanced. The second has two positive ties and one negative tie and is labeled unbalanced. The third has one positive tie and two negative ties and is labeled balanced. The fourth has three negative ties and is labeled unbalanced.",
                data={"types": ["+++", "++-", "+--", "---"], "balanced": [True, False, True, False]})
    return c, meta


def sampson_signed():
    names, ties = signed_pairs()
    n = len(names)
    bad, camp = best_split(n, ties)
    frustrated = [(a, b, s) for a, b, s in ties if camp[a] * camp[b] != s]
    c = Canvas(880, 600, "Sampson's novices: liking and disliking",
               "The novices joined by positive and negative ties, split into the two camps that disagree with the fewest ties.")
    left = [i for i in range(n) if camp[i] == 1]
    right = [i for i in range(n) if camp[i] == -1]
    pos = [None] * n
    for i, p in zip(left, ring(270, 300, 170, len(left))):
        pos[i] = p
    for i, p in zip(right, ring(680, 300, 120, len(right))):
        pos[i] = p
    for a, b, s in ties:
        wrong = camp[a] * camp[b] != s
        c.edge(pos[a], pos[b], ra=11, rb=11, color=POS if s > 0 else NEG,
               width=3.4 if wrong else 1.6, dash=None if s > 0 else "6 4", opacity=1.0 if wrong else 0.55)
    for i, p in enumerate(pos):
        c.node(p[0], p[1], "", r=10, fill=PAPER if camp[i] == 1 else INK, stroke=INK, sw=2,
               shape="circle" if camp[i] == 1 else "square")
    for i, p in enumerate(pos):
        cx0 = 270 if camp[i] == 1 else 680
        dx, dy = p[0] - cx0, p[1] - 300
        d = math.hypot(dx, dy) or 1
        c.text(p[0] + dx / d * 30, p[1] + dy / d * 24 + 4, names[i], size=11.5, weight="600",
               anchor="end" if dx < -20 else ("start" if dx > 20 else "middle"))
    c.text(440, 28, "55 signed ties among 18 novices", size=16, weight="700")
    c.text(440, 580, "Open circles: one camp. Filled squares: the other. Thick lines: the ties that disagree with the split.", size=12.5, fill=MUTED)
    npos = sum(1 for _, _, s in ties if s > 0)
    camp_a = [names[i] for i in range(n) if camp[i] == 1]
    camp_b = [names[i] for i in range(n) if camp[i] == -1]
    meta = dict(chapter=16,
                caption="Sampson's novices at time 3: positive ties (liking, solid blue) and negative ties (disliking, dashed red), drawn only where every choice about the pair had the same sign. The novices are split into the two camps that leave the fewest ties disagreeing; those ties are drawn thick.",
                alt=f"A network of 18 named novices joined by {len(ties)} ties, {npos} positive and {len(ties) - npos} negative. Eleven novices are drawn as open circles and seven as filled squares. {len(frustrated)} ties disagree with that split: {sum(1 for *_, s in frustrated if s < 0)} negative ties inside a camp and {sum(1 for *_, s in frustrated if s > 0)} positive ties between the camps.",
                data={"camp_open": camp_a, "camp_filled": camp_b, "frustrated": len(frustrated)})
    assert len(camp_a) == 11 and len(camp_b) == 7 and len(ties) == 55, (len(camp_a), len(camp_b), len(ties))
    return c, meta


def karate_thresholds():
    rows = list(csv.DictReader(open(DATA / "karate" / "edges.csv", newline="")))
    edges = [(int(r["source"]) - 1, int(r["target"]) - 1, int(r["contexts"])) for r in rows]
    n = 34
    base = fit(stress_layout(n, [(a, b) for a, b, _ in edges], seed=2), 0, 0, 250, 270)
    c = Canvas(900, 390, "Karate club ties, kept only above a threshold",
               "Three drawings of the same 34 members with ties kept only if seen in at least 1, 3 or 5 contexts.")
    summary = []
    for k, t in enumerate((1, 3, 5)):
        keep = [(a, b) for a, b, w in edges if w >= t]
        deg = [0] * n
        for a, b in keep:
            deg[a] += 1
            deg[b] += 1
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for a, b in keep:
            parent[find(a)] = find(b)
        pieces = len({find(i) for i in range(n)})
        x0, y0 = 20 + k * 295, 60
        pos = [(x0 + p[0] + 10, y0 + p[1]) for p in base]
        c.text(x0 + 135, 30, f"at least {t} context{'s' if t > 1 else ''}", size=15, weight="700")
        for a, b in keep:
            c.edge(pos[a], pos[b], ra=3, rb=3, color=BLUE, width=0.9 + 0.35 * dict(((x, y), w) for x, y, w in edges)[(a, b)], opacity=0.7)
        top = max(deg)
        for i, p in enumerate(pos):
            c.node(p[0], p[1], "", r=2.6 + 0.55 * deg[i], fill=ORANGE if deg[i] == top else (PAPER if deg[i] else FAINT),
                   stroke=ORANGE if deg[i] == top else (BLUE if deg[i] else MUTED), sw=1.6)
        c.text(x0 + 135, 352, f"{len(keep)} ties, {pieces} piece{"s" if pieces > 1 else ""}", size=13, fill=MUTED)
        c.text(x0 + 135, 372, "most ties: " + ", ".join(str(i + 1) for i in range(n) if deg[i] == top), size=12, fill=MUTED)
        summary.append({"threshold": t, "ties": len(keep), "pieces": pieces,
                        "most_ties": [i + 1 for i in range(n) if deg[i] == top]})
    s = summary
    meta = dict(chapter=16,
                caption="The same 34 karate club members with ties kept only if Zachary saw the pair in at least 1, 3 or 5 kinds of situation. Line thickness shows how many. Filled orange dots have the most ties left; grey dots have none.",
                alt=f"Three drawings of the same 34 dots. With every tie kept there are {s[0]['ties']} ties in {s[0]['pieces']} piece. Keeping ties seen in at least 3 contexts leaves {s[1]['ties']} ties in {s[1]['pieces']} pieces. Keeping at least 5 leaves {s[2]['ties']} ties in {s[2]['pieces']} pieces, most dots with no tie at all.",
                data={"thresholds": summary})
    return c, meta


FIGURES = {"signed-triads": triad_types, "sampson-signed": sampson_signed, "karate-thresholds": karate_thresholds}

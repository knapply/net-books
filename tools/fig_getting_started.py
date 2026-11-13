"""Figures for the getting-started chapter (chapter 4). Standard library only.

The managers' advice network comes from books/sna/data/krackhardt. Counts drawn here are
asserted to match what the chapter's code prints.
"""
import csv
import math
from pathlib import Path

from fig_layout import fit, stress_layout
from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"
GRAY = "#9ca3af"


def advice_ties():
    with open(DATA / "krackhardt" / "edges.csv") as f:
        return [(int(r["from"]) - 1, int(r["to"]) - 1) for r in csv.DictReader(f) if r["relation"] == "advice"]


def managers_advice():
    arcs = advice_ties()
    assert len(arcs) == 190
    indeg = [sum(1 for _, b in arcs if b == i) for i in range(21)]
    assert indeg[1] == 18 and indeg[17] == 15 and indeg[20] == 15 and max(indeg) == 18
    w, h = 760, 600
    c = Canvas(w, h, "Krackhardt's advice network",
               "The 21 managers drawn with a stress layout, circle area proportional to the number of managers who come to each one for advice.")
    undirected = sorted({(min(a, b), max(a, b)) for a, b in arcs})
    pos = fit(stress_layout(21, undirected, seed=3), 60, 50, w - 120, h - 120)
    for a, b in undirected:
        c.add(f'<line x1="{pos[a][0]:.1f}" y1="{pos[a][1]:.1f}" x2="{pos[b][0]:.1f}" y2="{pos[b][1]:.1f}" '
              f'stroke="{GRAY}" stroke-width="0.9" opacity="0.45"/>')
    top = {1, 17, 20}
    for i in range(21):
        r = 3.2 * math.sqrt(indeg[i]) + 2
        c.node(pos[i][0], pos[i][1], str(i + 1), r=r, fill=(ORANGE + "dd") if i in top else (BLUE + "88"),
               stroke=INK, size=10 if r < 16 else 12, sw=1.2)
    c.text(w / 2, h - 36, "Circle area: number of managers who come to this manager for advice (4 to 18).", size=13, fill=MUTED)
    c.text(w / 2, h - 16, "Orange: the three most asked (managers 2, 18 and 21). Lines: the 145 pairs with at least one tie; direction is not drawn.", size=13, fill=MUTED)
    assert len(undirected) == 145
    meta = dict(chapter=4,
                caption="Krackhardt's advice network. Circle area is the number of managers who come to each manager for advice (in-degree); the three orange circles are the most asked. Lines join the 145 pairs with at least one tie; direction is not drawn.",
                alt="A network of 21 numbered managers drawn as circles joined by thin gray lines, 145 lines in all. Circle area grows with the number of managers who ask each one for advice. Managers 2, 18 and 21, the three most asked, are orange and the largest; the rest are blue.",
                data={"in_degree": {str(i + 1): d for i, d in enumerate(indeg)}, "pairs": len(undirected)})
    return c, meta


def first_analysis_loop():
    w, h = 820, 250
    c = Canvas(w, h, "The first-analysis loop",
               "Five steps, each with a question: load, describe, compute, stress-test, write.")
    steps = [("Load", "Is every person\nand tie in?"), ("Describe", "Do the counts match\nwhat I know?"),
             ("Compute", "Can I say what it\nmeans in a sentence?"), ("Stress-test", "Does it survive\nlosing some ties?"),
             ("Write", "What does it\nnot show?")]
    bw, gap, x0, y0 = 128, 28, 22, 70
    for i, (name, q) in enumerate(steps):
        x = x0 + i * (bw + gap)
        c.rect(x, y0, bw, 64, fill=BLUE + "22", stroke=BLUE, sw=1.8, rx=8)
        c.text(x + bw / 2, y0 + 28, f"{i + 1}. {name}", size=16, weight="700")
        for k, line in enumerate(q.split("\n")):
            c.text(x + bw / 2, y0 + 92 + k * 18, line, size=13, fill=MUTED)
        if i < len(steps) - 1:
            c.add(f'<line x1="{x + bw + 3}" y1="{y0 + 32}" x2="{x + bw + gap - 3}" y2="{y0 + 32}" stroke="{INK}" '
                  f'stroke-width="2" marker-end="url(#{c.marker(INK)})"/>')
    last = x0 + 4 * (bw + gap) + bw / 2
    c.add(f'<path d="M{last:.0f},{y0 + 126} C{last:.0f},{h - 4} {x0 + bw / 2:.0f},{h - 4} {x0 + bw / 2:.0f},{y0 + 126}" '
          f'fill="none" stroke="{ORANGE}" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#{c.marker(ORANGE)})"/>')
    c.text(w / 2, 26, "A first analysis, and every one after it", size=15, weight="600")
    meta = dict(chapter=4,
                caption="The first-analysis loop. Each step has a check; the loop closes when you can say what the numbers do and do not show.",
                alt="Five boxes in a row labeled load, describe, compute, stress-test and write, joined by arrows. Under each is a short question. A dashed arrow runs from the last box back to the first.",
                data={"steps": [s[0] for s in steps]})
    return c, meta


FIGURES = {"managers-advice": managers_advice, "first-analysis-loop": first_analysis_loop}

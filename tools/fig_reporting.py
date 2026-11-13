"""Figures for the reporting chapter (chapter 28).

Standard library only. The stability figure is computed here from the Krackhardt CSV in
books/sna/data with the recipe the chapter's code uses: in replicate r, tie i (counting
from 1) gets the key frac(sin(12.9898 i + 78.233 r) * 43758.5453) and the 19 ties with the
smallest keys are dropped, for r = 1 to 200.
"""
import csv
from collections import deque
from math import floor, sin
from pathlib import Path

from figs import BLUE, FAINT, INK, MUTED, ORANGE, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"
N, DROP, RUNS = 21, 19, 200


def advice_ties():
    with open(DATA / "krackhardt" / "edges.csv", newline="") as f:
        return [(int(r["from"]) - 1, int(r["to"]) - 1) for r in csv.DictReader(f) if r["relation"] == "advice"]


def key(i, r):
    x = sin(i * 12.9898 + r * 78.233) * 43758.5453
    return x - floor(x)


def betweenness(ties):
    """Brandes' algorithm for a directed network on N nodes; each ordered pair counts once."""
    out = [[] for _ in range(N)]
    for a, b in ties:
        out[a].append(b)
    score = [0.0] * N
    for s in range(N):
        dist, sigma, order, preds = [-1] * N, [0.0] * N, [], [[] for _ in range(N)]
        dist[s], sigma[s] = 0, 1.0
        queue = deque([s])
        while queue:
            v = queue.popleft()
            order.append(v)
            for w in out[v]:
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    preds[w].append(v)
        delta = [0.0] * N
        for w in reversed(order):
            for v in preds[w]:
                delta[v] += sigma[v] / sigma[w] * (1 + delta[w])
            if w != s:
                score[w] += delta[w]
    return score


def percentile(values, p):
    v = sorted(values)
    pos = p / 100 * (len(v) - 1)
    lo, hi = floor(pos), min(floor(pos) + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


def runs():
    ties = advice_ties()
    original = ([sum(1 for _, b in ties if b == v) for v in range(N)], betweenness(ties))
    out = []
    for r in range(1, RUNS + 1):
        dropped = set(sorted(range(len(ties)), key=lambda i: key(i + 1, r))[:DROP])
        kept = [t for i, t in enumerate(ties) if i not in dropped]
        out.append(([sum(1 for _, b in kept if b == v) for v in range(N)], betweenness(kept)))
    return original, out


def tie_drop_stability():
    original, out = runs()
    c = Canvas(900, 400, "Rank stability when 10 percent of the advice ties are dropped",
               "Two dot-and-whisker panels for the six managers with the highest score in the full advice network, over 200 random drops of 19 of the 190 ties.")
    top, step = 66, 46
    panels = [(190, 280, 0, 120, 1, "Betweenness (dot: all ties, bar: 5th to 95th percentile)"),
              (590, 250, 0, 20, 0, "Asked for advice (dot: all ties, bar: 5th to 95th percentile)")]
    data = {}
    for x0, w, lo, hi, j, title in panels:
        name = ["asked", "betweenness"][j]
        c.text(x0 + w / 2 - 30, 34, title, size=12.5, weight="600")
        leaders = sorted(range(N), key=lambda v: (-original[j][v], v))[:6]
        for t in range(lo, hi + 1, 20 if j else 4):
            x = x0 + (t - lo) / (hi - lo) * w
            c.add(f'<line x1="{x:.1f}" y1="{top - 14}" x2="{x:.1f}" y2="{top + 6 * step - 24}" stroke="{FAINT}" stroke-width="1"/>')
            c.text(x, top + 6 * step - 2, str(t), size=12, fill=MUTED)
        data[name] = {}
        for row, v in enumerate(leaders):
            y = top + row * step
            vals = [run[j][v] for run in out]
            p5, p95 = percentile(vals, 5), percentile(vals, 95)
            data[name][v + 1] = [round(original[j][v], 1), round(p5, 1), round(p95, 1)]
            x1, x2 = x0 + (p5 - lo) / (hi - lo) * w, x0 + (p95 - lo) / (hi - lo) * w
            c.add(f'<line x1="{x1:.1f}" y1="{y}" x2="{x2:.1f}" y2="{y}" stroke="{INK}" stroke-width="2"/>')
            c.text(x0 - 14, y + 5, f"manager {v + 1}", size=13, anchor="end")
            c.node(x0 + (original[j][v] - lo) / (hi - lo) * w, y, r=6.5, fill=ORANGE if row == 0 else BLUE, stroke=INK, sw=1.5)
    c.text(450, 386, "Orange: the leader in the full network. The bars overlap for the managers just behind the leader.",
           size=12.5, fill=MUTED)
    b, a = data["betweenness"], data["asked"]
    first_b = min(b, key=lambda v: -b[v][0])
    first_a = min(a, key=lambda v: -a[v][0])
    meta = dict(
        chapter=28,
        caption="Dropping a random tenth of the advice ties 200 times. Each dot is a manager's score in the full network and each bar spans the middle 90 percent of the scores across the 200 drops.",
        alt=("Two panels, each listing six managers. Left, betweenness: manager %d has the highest dot at %.1f with a bar from %.1f to %.1f; "
             "the next dot, manager %d, is at %.1f with a bar from %.1f to %.1f. Right, number of people who asked each manager for advice: "
             "manager %d has the highest dot at %d with a bar from %.1f to %.1f." % (
                 first_b, b[first_b][0], b[first_b][1], b[first_b][2],
                 sorted(b, key=lambda v: -b[v][0])[1], sorted(b.values(), key=lambda t: -t[0])[1][0],
                 sorted(b.values(), key=lambda t: -t[0])[1][1], sorted(b.values(), key=lambda t: -t[0])[1][2],
                 first_a, a[first_a][0], a[first_a][1], a[first_a][2])),
        data={"drops": RUNS, "ties_dropped": DROP, "scores": data})
    return c, meta


FIGURES = {"tie-drop-stability-krackhardt": tie_drop_stability}

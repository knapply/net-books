"""Figures for the chapter on networks in time.

Standard library only. The small six-person contact log is spelled out here, and
everything drawn from it (who reaches whom, wave contents) is computed from it. The
Sampson panels are computed from books/sna/data/sampson/edges.csv.
"""
import csv
from pathlib import Path

from fig_layout import fit, stress_layout
from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"
PEOPLE = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay"]
# (time, person, person): who met whom, and when
LOG = [(1, 0, 1), (2, 2, 3), (3, 1, 2), (4, 3, 4), (5, 0, 1), (6, 4, 5)]
ZIGZAG = [(0, 0), (1, 1), (2, 0), (3, 1), (4, 0), (5, 1)]  # the six people along a zigzag chain


def earliest_arrival(root, contacts, directed=False):
    """People a message from root can reach by following contacts forward in time."""
    arrive = {root: float("-inf")}
    for t, a, b in sorted(contacts):
        for u, v in ([(a, b)] if directed else [(a, b), (b, a)]):
            if u in arrive and arrive[u] <= t and t < arrive.get(v, float("inf")):
                arrive[v] = t
    return arrive


def mini(c, x0, y0, width, pairs, title, weights=None, gap=33):
    """The six people on a zigzag, with the given pairs drawn as ties."""
    pos = [(x0 + (width - 5 * gap) / 2 + gx * gap, y0 + 22 + gy * 34) for gx, gy in ZIGZAG]
    for k, (a, b) in enumerate(pairs):
        w = 2 + 2.4 * ((weights[k] - 1) if weights else 0)
        c.edge(pos[a], pos[b], ra=11, rb=11, width=w, color=BLUE)
    for i, p in enumerate(pos):
        c.node(p[0], p[1], PEOPLE[i][0], r=11, size=11, sw=1.8)
    c.text(x0 + width / 2, y0 - 6, title, size=12.5, fill=MUTED)


def four_ways():
    c = Canvas(900, 590, "One small network held four ways",
               "Four panels showing the same six contacts as snapshots, as aggregated pictures, as an event stream and as intervals.")
    heads = [(30, 30, "1. Snapshots (waves)"), (470, 30, "2. Aggregation"),
             (30, 300, "3. Event stream"), (470, 300, "4. Intervals")]
    for x, y, h in heads:
        c.text(x, y, h, size=16, weight="700", anchor="start")
        c.add(f'<line x1="{x}" y1="{y + 10}" x2="{x + 400}" y2="{y + 10}" stroke="{FAINT}" stroke-width="1.5"/>')
    # 1. two waves: times 1-3 and 4-6
    for k, (lo, hi) in enumerate([(1, 3), (4, 6)]):
        pairs = [(a, b) for t, a, b in LOG if lo <= t <= hi]
        mini(c, 30 + k * 205, 82, 195, pairs, f"wave {k + 1}: times {lo} to {hi}")
    c.lines(30, 180, ["Two photographs. Inside a wave, the order of", "contacts is gone."],
            size=12.5, fill=MUTED)
    # 2. cumulative to time 6, and a sliding window of width 3 ending at 5
    every = {}
    for t, a, b in LOG:
        every[(a, b)] = every.get((a, b), 0) + 1
    mini(c, 470, 82, 195, list(every), "everything up to time 6", weights=list(every.values()))
    inwin = [(a, b) for t, a, b in LOG if 3 <= t <= 5]
    mini(c, 675, 82, 195, inwin, "sliding window: times 3 to 5")
    c.lines(470, 180, ["Piling contacts up (thick = met twice) or", "looking through a moving window."],
            size=12.5, fill=MUTED)
    # 3. event stream
    left, right = 70, 400
    tx = lambda t: left + (t - 0.5) * (right - left) / 6  # noqa: E731
    y = 392
    c.add(f'<line x1="{left - 20}" y1="{y}" x2="{right + 20}" y2="{y}" stroke="{FAINT}" stroke-width="2"/>')
    for t, a, b in LOG:
        c.add(f'<line x1="{tx(t):.1f}" y1="{y - 12}" x2="{tx(t):.1f}" y2="{y + 12}" stroke="{ORANGE}" stroke-width="3"/>')
        c.text(tx(t), y - 22, f"{PEOPLE[a][0]}-{PEOPLE[b][0]}", size=12.5, weight="600")
        c.text(tx(t), y + 32, f"t={t}", size=12, fill=MUTED)
    c.lines(30, 525, ["A list of who met whom, and when. Order is kept;", "nothing is merged."],
            size=12.5, fill=MUTED)
    # 4. intervals: invented, each meeting lasts half a time unit
    rows = list(every)
    left, right = 530, 860
    tx2 = lambda t: left + (t - 0.5) * (right - left) / 7  # noqa: E731
    for r, (a, b) in enumerate(rows):
        ry = 345 + r * 30
        c.text(left - 10, ry + 4, f"{PEOPLE[a][0]}-{PEOPLE[b][0]}", size=12.5, anchor="end", weight="600")
        c.add(f'<line x1="{left}" y1="{ry}" x2="{right}" y2="{ry}" stroke="#eef0f3" stroke-width="1.5"/>')
        for t, p, q in LOG:
            if (p, q) == (a, b):
                x1, x2 = tx2(t), tx2(t + 0.5)
                c.rect(round(x1, 1), ry - 7, round(x2 - x1, 1), 14, fill=RED + "cc", stroke=RED, sw=1, rx=2)
    for t in range(1, 7):
        c.text(tx2(t), 345 + len(rows) * 30 + 4, f"{t}", size=12, fill=MUTED)
    c.lines(470, 530, ["Each contact now has a start and an end. Here every", "meeting lasted half a time unit (invented)."],
            size=12.5, fill=MUTED)
    c.text(450, 578, "Same six contacts in all four panels. Each way of holding them answers some questions and loses others.",
           size=12.5, fill=MUTED)
    meta = dict(chapter=13,
                caption="One small network held four ways. Snapshots keep two photographs and lose the order inside each. Aggregation piles contacts into one picture, or looks through a moving window. An event stream keeps every contact and its time. Intervals give each contact a start and an end.",
                alt="Four panels, each showing the same six contacts among Ana, Ben, Cleo, Dev, Eli and Fay. Panel 1 shows two small networks, times 1 to 3 with three ties and times 4 to 6 with three ties. Panel 2 shows one network of everything up to time 6 with five ties, the Ana-Ben tie drawn thick because they met twice, and a sliding window of times 3 to 5 with three ties. Panel 3 is a timeline with six ticks labeled A-B at 1, C-D at 2, B-C at 3, D-E at 4, A-B at 5 and E-F at 6. Panel 4 shows five rows of pairs with a short bar for each meeting, A-B twice, at times 1 and 5.",
                data={"contacts": [{"time": t, "a": PEOPLE[a], "b": PEOPLE[b]} for t, a, b in LOG]})
    return c, meta


def reach_matrices():
    n = len(PEOPLE)
    timed = []
    for p in range(n):
        timed.append(set(earliest_arrival(p, LOG)) - {p})
    c = Canvas(900, 400, "Who can reach whom: one picture without time, and with time",
               "Two six by six grids of who can reach whom, one for the contacts piled into one picture and one for contacts respecting their order.")
    cell = 40
    panels = [("Piled into one picture", [set(range(n)) - {p} for p in range(n)], BLUE, 60),
              ("Respecting the clock", timed, ORANGE, 490)]
    for title, reach, col, x0 in panels:
        top = 90
        c.text(x0 + 3 * cell + 40, 36, title, size=15, weight="700")
        c.text(x0 + 3 * cell + 40, 56, f"{sum(len(r) for r in reach)} of {n * (n - 1)} pairs", size=13, fill=MUTED)
        for k, name in enumerate(PEOPLE):
            c.text(x0 + 40 + k * cell + cell / 2, top - 8, name[:3], size=11.5, fill=MUTED)
            c.text(x0 + 32, top + k * cell + cell / 2 + 4, name, size=12.5, anchor="end")
        for a in range(n):
            for b in range(n):
                x, y = x0 + 40 + b * cell, top + a * cell
                if a == b:
                    c.rect(x, y, cell, cell, fill="#f3f4f6", stroke=PAPER, sw=2)
                elif b in reach[a]:
                    c.rect(x, y, cell, cell, fill=col, stroke=PAPER, sw=2)
                else:
                    c.rect(x, y, cell, cell, fill=PAPER, stroke=FAINT, sw=1.2)
        c.text(x0 + 40 + 3 * cell, top + 6 * cell + 24, "can reach (columns)", size=12, fill=MUTED)
    c.text(450, 385, "Rows are where the message starts. The right grid is not symmetric: Dev reaches Ana, but Ana does not reach Dev.",
           size=12.5, fill=MUTED)
    counts = [len(r) for r in timed]
    meta = dict(chapter=13,
                caption="Who can reach whom. Left: the six contacts piled into one picture, where everyone is connected to everyone. Right: the same contacts when a message can only move forward in time. Rows are where a message starts, columns where it can arrive.",
                alt="Two six by six grids with people in rows and columns. The left grid has every off-diagonal cell filled, 30 of 30 pairs. The right grid has 17 of 30 cells filled. Ana's row has Ben and Cleo filled, Ben's row has Ana and Cleo, Cleo's and Dev's rows have all five others, Eli's row has Dev and Fay, and Fay's row has only Eli.",
                data={"reach_counts": counts, "pairs_with_time": sum(counts), "pairs_without_time": n * (n - 1)})
    return c, meta


def sampson_waves():
    rows = [r for r in csv.DictReader(open(DATA / "sampson" / "edges.csv", newline="")) if r["relation"] == "liking"]
    names = sorted({r["from"] for r in rows} | {r["to"] for r in rows})
    ix = {nm: i for i, nm in enumerate(names)}
    n = len(names)
    waves = {k: [(ix[r["from"]], ix[r["to"]]) for r in rows if int(r["time"]) == k] for k in (1, 2, 3)}
    union = sorted({tuple(sorted(e)) for es in waves.values() for e in es})
    base = fit(stress_layout(n, union, seed=3), 0, 0, 260, 250)
    c = Canvas(900, 370, "Sampson's novices: who they like, at three times",
               "Three copies of the same eighteen novices, drawn in the same places, showing the liking choices at time 1, 2 and 3.")
    tops = {}
    for k in (1, 2, 3):
        x0, y0 = 20 + (k - 1) * 295, 60
        pos = [(x0 + p[0] + 10, y0 + p[1]) for p in base]
        indeg = [0] * n
        for a, b in waves[k]:
            indeg[b] += 1
        order = sorted(range(n), key=lambda i: (-indeg[i], names[i]))
        top = order[:3]
        tops[k] = [names[i] for i in top]
        c.caption(x0 + 140, 30, f"Time {k}: {len(waves[k])} choices")
        for a, b in waves[k]:
            c.edge(pos[a], pos[b], ra=3 + 1.1 * indeg[a], rb=3 + 1.1 * indeg[b], directed=True, width=0.9,
                   color=BLUE, opacity=0.5)
        for i, p in enumerate(pos):
            c.node(p[0], p[1], "", r=3 + 1.1 * indeg[i], fill=ORANGE if i in top else PAPER,
                   stroke=ORANGE if i in top else BLUE, sw=1.8)
        for i in top:
            c.text(pos[i][0], pos[i][1] - 6 - 1.1 * indeg[i], names[i], size=11.5, weight="600")
        c.text(x0 + 140, 338, f"most chosen: {', '.join(names[i] for i in top)}", size=12, fill=MUTED)
    meta = dict(chapter=13,
                caption="Sampson's liking choices among 18 novices at times 1, 2 and 3, drawn in the same places each time. Dot size shows how many novices chose that person at that time. The three most chosen at each time are filled and named.",
                alt=f"Three copies of the same 18 dots joined by arrows, with 55 arrows at time 1, 57 at time 2 and 56 at time 3. Filled dots mark the three most chosen novices. At time 1 they are {', '.join(tops[1])}. At time 2 they are {', '.join(tops[2])}. At time 3 they are {', '.join(tops[3])}.",
                data={"top3": tops, "ties": {str(k): len(v) for k, v in waves.items()}})
    return c, meta



# The eighty invented messages of the chapter: hour sent, sender and receiver (people numbered 0 to 7).
MSG_TIMES = [
    0.3, 0.8, 3.3, 4.8, 6.8, 25.4, 28.4, 33.4, 35.2, 36.8,
    37.0, 38.0, 43.6, 44.5, 46.3, 46.6, 48.2, 49.0, 49.3, 50.1,
    50.4, 50.7, 52.4, 52.7, 53.3, 55.0, 56.0, 56.9, 57.8, 58.6,
    58.8, 63.3, 64.5, 64.6, 65.6, 77.9, 78.0, 85.1, 98.6, 99.4,
    99.7, 102.9, 105.4, 106.1, 107.1, 107.2, 108.0, 128.2, 128.6, 128.8,
    129.2, 130.8, 134.5, 135.2, 148.1, 149.0, 149.3, 176.8, 182.2, 182.4,
    182.6, 182.8, 183.1, 183.6, 184.6, 185.9, 193.0, 195.1, 196.2, 202.8,
    203.2, 204.4, 204.7, 205.8, 206.1, 208.4, 208.5, 214.4, 215.2, 217.3,
]
MSG_SENDER = [
    6, 2, 5, 7, 4, 4, 6, 5, 3, 4,
    6, 0, 5, 6, 2, 3, 1, 5, 7, 2,
    3, 7, 4, 3, 5, 0, 1, 7, 1, 0,
    7, 5, 7, 5, 6, 2, 5, 1, 6, 5,
    2, 1, 1, 6, 4, 2, 4, 5, 5, 7,
    6, 3, 0, 2, 0, 6, 6, 2, 7, 3,
    3, 4, 7, 7, 1, 6, 1, 6, 4, 1,
    0, 7, 0, 1, 7, 4, 3, 3, 4, 3,
]
MSG_RECEIVER = [
    4, 7, 4, 0, 7, 5, 1, 6, 6, 6,
    3, 4, 2, 1, 5, 7, 6, 3, 5, 3,
    5, 2, 2, 2, 3, 3, 3, 1, 5, 3,
    3, 4, 4, 2, 7, 7, 6, 6, 5, 3,
    0, 7, 6, 2, 6, 6, 7, 2, 1, 6,
    4, 1, 4, 4, 7, 1, 1, 4, 3, 0,
    5, 0, 6, 0, 2, 7, 6, 2, 5, 3,
    4, 2, 1, 4, 4, 2, 7, 1, 0, 0,
]


def reach_ratio(log, n=8, start=0.0, end=float("inf")):
    """Share of ordered pairs joined by a time-respecting path (same-time contacts may chain)."""
    total = 0
    for root in range(n):
        have = {root}
        for t in sorted({c[0] for c in log if start <= c[0] <= end}):
            moved = True
            while moved:
                moved = False
                for when, a, b in log:
                    if when == t and a in have and b not in have:
                        have.add(b)
                        moved = True
        total += len(have) - 1
    return total / (n * (n - 1)), total


def shift_null():
    """Reach over the first 48 hours when the timestamps are shifted around a circle (79 shifts)."""
    log = sorted(zip(MSG_TIMES, MSG_SENDER, MSG_RECEIVER))
    observed = reach_ratio(log, end=48)[1]
    counts = []
    for s in range(1, 80):
        shifted = [(MSG_TIMES[(i + s) % 80], MSG_SENDER[i], MSG_RECEIVER[i]) for i in range(80)]
        counts.append(reach_ratio(shifted, end=48)[1])
    lo, hi = min(counts + [observed]), max(counts + [observed])
    freq = {k: counts.count(k) for k in range(lo, hi + 1)}
    c = Canvas(900, 380, "Reach over the first 48 hours: observed against shifted timestamps",
               "A bar chart of how many of 79 shifted-time versions of the message log reach each number of the 56 ordered pairs, with the real log marked.")
    x0, x1, base, top = 70, 850, 300, 70
    step = (x1 - x0) / (hi - lo + 1)
    tall = max(freq.values())
    c.text(450, 30, "Pairs able to reach each other in the first 48 hours, 79 shifted versions of the log", size=15, weight="700")
    for k in range(lo, hi + 1):
        h = freq[k] / tall * (base - top)
        mine = k == observed
        c.rect(x0 + (k - lo) * step + 3, base - h, step - 6, h, fill=ORANGE if mine else BLUE, stroke=PAPER, sw=1)
        if freq[k]:
            c.text(x0 + (k - lo) * step + step / 2, base - h - 6, str(freq[k]), size=11, fill=MUTED)
        if (k - lo) % 2 == 0 or mine or k == hi:
            c.text(x0 + (k - lo) * step + step / 2, base + 20, str(k), size=11.5, fill=MUTED)
    c.text(450, base + 46, "pairs (out of 56) that can reach each other; the real log is the orange bar", size=12.5, fill=MUTED)
    c.text(450, base + 68, "Bars count shifts; each shift keeps who wrote to whom and changes only when.", size=12.5, fill=MUTED)
    at_least = sum(1 for v in counts if v >= observed)
    meta = dict(chapter=17,
                caption="How many of the 56 ordered pairs of coworkers can reach each other within the first 48 hours, for the real log (orange) and for 79 versions in which the same timestamps are dealt out to the pairs from a different starting point. The real log sits inside the spread.",
                alt=f"A bar chart. The horizontal axis is the number of the 56 ordered pairs that can reach each other, from {lo} to {hi}. Bar heights count how many of 79 shifted logs give that number, with the tallest bar for {tall} shifts. The real log, at {observed} pairs, is drawn in orange; {at_least} of the 79 shifted logs reach {observed} pairs or more.",
                data={"observed_pairs": observed, "shifted_counts": freq, "shifts_at_least_as_high": at_least})
    return c, meta


FIGURES = {"time-four-ways": four_ways, "reach-static-vs-time": reach_matrices, "sampson-waves": sampson_waves, "reach-shift-null": shift_null}

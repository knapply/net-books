"""Figures for the chapter on longitudinal and temporal networks.

Standard library only. The Sampson panel is computed from books/sna/data/sampson;
the event-model panel refits the chapter's eighty invented messages here, by Newton's
method on the log partial likelihood, so the numbers drawn are computed, not typed.
"""
import csv
import math
from pathlib import Path

from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data" / "sampson"

# The eighty invented messages of the chapter: sender and receiver (0 to 7).
SENDER = [6, 2, 5, 7, 4, 4, 6, 5, 3, 4, 6, 0, 5, 6, 2, 3, 1, 5, 7, 2,
          3, 7, 4, 3, 5, 0, 1, 7, 1, 0, 7, 5, 7, 5, 6, 2, 5, 1, 6, 5,
          2, 1, 1, 6, 4, 2, 4, 5, 5, 7, 6, 3, 0, 2, 0, 6, 6, 2, 7, 3,
          3, 4, 7, 7, 1, 6, 1, 6, 4, 1, 0, 7, 0, 1, 7, 4, 3, 3, 4, 3]
RECEIVER = [4, 7, 4, 0, 7, 5, 1, 6, 6, 6, 3, 4, 2, 1, 5, 7, 6, 3, 5, 3,
            5, 2, 2, 2, 3, 3, 3, 1, 5, 3, 3, 4, 4, 2, 7, 7, 6, 6, 5, 3,
            0, 7, 6, 2, 6, 6, 7, 2, 1, 6, 4, 1, 4, 4, 7, 1, 1, 4, 3, 0,
            5, 0, 6, 0, 2, 7, 6, 2, 5, 3, 4, 2, 1, 4, 4, 2, 7, 1, 0, 0]



def sampson_waves():
    with open(DATA / "nodes.csv") as f:
        number = {r["name"]: int(r["number"]) - 1 for r in csv.DictReader(f)}
    waves = [[[0] * 18 for _ in range(18)] for _ in range(3)]
    with open(DATA / "edges.csv") as f:
        for r in csv.DictReader(f):
            if r["relation"] == "liking":
                waves[int(r["time"]) - 1][number[r["from"]]][number[r["to"]]] = 1
    return waves


def turnover():
    waves = sampson_waves()
    steps = []
    for w in range(2):
        x, y = waves[w], waves[w + 1]
        cells = [(x[i][j], y[i][j]) for i in range(18) for j in range(18)]
        steps.append((sum(a * b for a, b in cells), sum(a * (1 - b) for a, b in cells),
                      sum((1 - a) * b for a, b in cells)))
    groups = {(1, 1): [0, 0], (1, 0): [0, 0], (0, 1): [0, 0], (0, 0): [0, 0]}
    for w in range(2):
        x, y = waves[w], waves[w + 1]
        for i in range(18):
            for j in range(18):
                if i != j:
                    key = (x[i][j], x[j][i])
                    groups[key][0] += 1
                    groups[key][1] += y[i][j]
    c = Canvas(900, 400, "How much of Sampson's liking network changed between waves",
               "Left: ties kept, dropped and new between waves. Right: the share of novice pairs with a tie at the next wave, by whether a tie existed and was returned.")
    c.text(225, 30, "Ties between consecutive waves", size=15, weight="700")
    c.text(725, 30, "Share with a tie at the next wave", size=15, weight="700")
    base, scale = 320, 6.4
    colors = [("kept", BLUE), ("dropped", ORANGE), ("new", GREEN)]
    for s, (kept, dropped, new) in enumerate(steps):
        for k, v in enumerate((kept, dropped, new)):
            x = 70 + s * 200 + k * 58
            c.rect(x, base - v * scale, 48, v * scale, fill=colors[k][1] + "55", stroke=colors[k][1], sw=2)
            c.text(x + 24, base - v * scale - 8, str(v), size=13, weight="600", fill=colors[k][1])
            c.text(x + 24, base + 18, colors[k][0], size=11.5, fill=MUTED)
        c.text(70 + s * 200 + 82, base + 44, f"wave {s + 1} to {s + 2}", size=13, weight="600")
    c.add(f'<line x1="55" y1="{base}" x2="425" y2="{base}" stroke="{MUTED}" stroke-width="1.5"/>')
    rows = [("tie, returned", (1, 1), BLUE), ("tie, not returned", (1, 0), SKY_OR(BLUE)),
            ("no tie, reverse tie", (0, 1), ORANGE), ("no tie, neither way", (0, 0), MUTED)]
    shares = []
    for k, (label, key, color) in enumerate(rows):
        n, later = groups[key]
        share = later / n
        shares.append((label, n, later, share))
        y = 70 + k * 62
        c.text(600, y + 22, label, size=12.5, anchor="end")
        c.rect(610, y, 230 * share, 32, fill=color + "55", stroke=color, sw=2)
        c.text(610 + 230 * share + 8, y + 22, f"{share:.2f} ({later} of {n})", size=12.5, anchor="start", fill=INK)
    meta = dict(chapter=23,
                caption="Sampson's novices, liking at three times. Left: between consecutive waves most ties were kept, but many were dropped and many new ones appeared, although the totals barely moved. Right: pooling both steps, the share of ordered pairs of novices that have a tie at the next wave, by whether the tie existed and whether it was returned.",
                alt=(f"Two panels. On the left, bars for the two steps between waves. From wave 1 to 2: {steps[0][0]} ties kept, {steps[0][1]} dropped and {steps[0][2]} new. From wave 2 to 3: {steps[1][0]} kept, {steps[1][1]} dropped and {steps[1][2]} new. "
                     f"On the right, horizontal bars for the share of ordered pairs with a tie at the next wave: {shares[0][3]:.2f} ({shares[0][2]} of {shares[0][1]}) for pairs with a returned tie, {shares[1][3]:.2f} ({shares[1][2]} of {shares[1][1]}) for a tie that was not returned, {shares[2][3]:.2f} ({shares[2][2]} of {shares[2][1]}) for no tie where the other novice names him, and {shares[3][3]:.2f} ({shares[3][2]} of {shares[3][1]}) for no tie either way."),
                data={"steps": steps, "shares": {r[0]: r[3] for r in shares}})
    return c, meta


def SKY_OR(color):
    return "#56B4E9"


def solve(a, b):
    """Solve a x = b by Gaussian elimination (small systems); also return the inverse's diagonal."""
    n = len(a)
    m = [row[:] + [1.0 if i == k else 0.0 for k in range(n)] for i, row in enumerate(a)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        m[col], m[piv] = m[piv], m[col]
        m[col] = [v / m[col][col] for v in m[col]]
        for r in range(n):
            if r != col:
                f = m[r][col]
                m[r] = [v - f * w for v, w in zip(m[r], m[col])]
    inverse = [row[n:] for row in m]
    return [sum(inverse[i][k] * b[k] for k in range(n)) for i in range(n)], [inverse[i][i] for i in range(n)]


def fit_events(sender, receiver, p, n=8):
    """Newton's method on the log partial likelihood. p = 2: inertia and reply;
    p = 4 adds sender activity and receiver popularity."""
    pairs = [(a, b) for a in range(n) for b in range(n) if a != b]
    rows = []
    for k in range(len(sender)):
        count = {}
        for e in range(k):
            count[(sender[e], receiver[e])] = count.get((sender[e], receiver[e]), 0) + 1
        sent = [sum(v for (a, _), v in count.items() if a == i) for i in range(n)]
        got = [sum(v for (_, b), v in count.items() if b == i) for i in range(n)]
        xs = [(count.get((a, b), 0), count.get((b, a), 0), sent[a], got[b])[:p] for a, b in pairs]
        rows.append((xs, pairs.index((sender[k], receiver[k]))))
    beta = [0.0] * p
    for _ in range(60):
        grad, info = [0.0] * p, [[0.0] * p for _ in range(p)]
        for xs, chosen in rows:
            w = [math.exp(sum(b * v for b, v in zip(beta, x))) for x in xs]
            total = sum(w)
            m = [sum(wi * x[d] for wi, x in zip(w, xs)) / total for d in range(p)]
            grad = [grad[d] + xs[chosen][d] - m[d] for d in range(p)]
            for d in range(p):
                for e in range(p):
                    info[d][e] += sum(wi * x[d] * x[e] for wi, x in zip(w, xs)) / total - m[d] * m[e]
        step, diag = solve(info, grad)
        beta = [b + s for b, s in zip(beta, step)]
        if max(abs(s) for s in step) < 1e-10:
            break
    return beta, [math.sqrt(v) for v in diag]


def rem_stability():
    variants = [("all 80 messages", slice(0, 80), 2), ("first 40", slice(0, 40), 2),
                ("last 40", slice(40, 80), 2), ("all 80, plus activity and popularity", slice(0, 80), 4)]
    fits = [(name,) + fit_events(SENDER[s], RECEIVER[s], p) for name, s, p in variants]
    c = Canvas(900, 300, "How the event-model coefficients move with the data and the model",
               "Two panels of estimates with two standard errors either side, one row per variant: all eighty messages, each half of the log, and the model with sender activity and receiver popularity added.")
    panels = [("Repeating a pair (inertia)", 0, BLUE, 300), ("Replying to a pair (reciprocity)", 1, ORANGE, 650)]
    lo, hi = -1.6, 1.6
    width = 200

    def px(x0, v):
        return x0 + (v - lo) / (hi - lo) * width

    for title, d, color, x0 in panels:
        c.text(x0 + width / 2, 30, title, size=14, weight="700")
        c.add(f'<line x1="{px(x0, 0):.1f}" y1="50" x2="{px(x0, 0):.1f}" y2="{50 + 40 * len(fits)}" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="5 4"/>')
        for v in (-1, 0, 1):
            c.text(px(x0, v), 50 + 40 * len(fits) + 18, str(v), size=11.5, fill=MUTED)
        for k, (name, beta, se) in enumerate(fits):
            y = 70 + k * 40
            if d == 0:
                c.text(x0 - 20, y + 4, name, size=12.5, anchor="end")
            c.add(f'<line x1="{px(x0, beta[d] - 2 * se[d]):.1f}" y1="{y}" x2="{px(x0, beta[d] + 2 * se[d]):.1f}" y2="{y}" stroke="{color}" stroke-width="2.4"/>')
            c.add(f'<circle cx="{px(x0, beta[d]):.1f}" cy="{y}" r="5.5" fill="{color}"/>')
    c.text(450, 290, "coefficient (log multiplier of the rate); dashed line is no effect", size=12, fill=MUTED)
    parts = "; ".join(f"{n}: inertia {b[0]:+.2f}, reply {b[1]:+.2f}" for n, b, s in fits)
    meta = dict(chapter=23,
                caption="The two event-model coefficients for the eighty invented messages, refitted on each half of the log and with two more effects in the model. Dots are estimates, bars reach two standard errors either side. The halves agree in sign and size, but each half alone is only about two standard errors from zero.",
                alt=(f"Two panels with four rows each, estimates as dots with bars of two standard errors either side and a dashed line at zero. {parts}. "
                     f"In every row the inertia estimate is below zero and the reply estimate is above zero; in the two half-log rows the inertia bars extend slightly past zero and the reply bars begin just above it."),
                data={n: {"inertia": b[0], "reply": b[1], "se": s} for n, b, s in fits})
    return c, meta


FIGURES = {"sampson-turnover": turnover, "rem-stability": rem_stability}

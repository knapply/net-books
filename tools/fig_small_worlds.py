"""Figures for the chapter on random graphs, small worlds and degree distributions.

Standard library only. The karate pictures are computed from books/sna/data/karate/edges.csv.
The other three read the small CSV files in books/sna/data/small_worlds, which hold the numbers
the chapter's Rust code prints (see the README there), so the pictures and the text come from the
same runs.
"""
import csv
import math
from pathlib import Path

from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"


def rows(path):
    with open(DATA / path, newline="") as f:
        return list(csv.DictReader(f))


def karate_degrees():
    ties = [(int(r["source"]), int(r["target"])) for r in rows("karate/edges.csv")]
    deg = {}
    for a, b in ties:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    return sorted(deg.values())


def ccdf(degrees):
    """(k, share of people with degree at least k) at each degree from 1 up that occurs.
    Degree 0 is left out because log axes cannot show it; its CCDF value is 1."""
    n = len(degrees)
    return [(k, sum(d >= k for d in degrees) / n) for k in sorted(set(degrees)) if k >= 1]


class Axes:
    """A plot area with linear or log10 axes, ticks and light grid lines."""

    def __init__(self, c, x, y, w, h, xr, yr, xlog=False, ylog=False):
        self.c, self.x, self.y, self.w, self.h = c, x, y, w, h
        self.xr, self.yr, self.xlog, self.ylog = xr, yr, xlog, ylog

    def px(self, v):
        lo, hi = self.xr
        t = (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) if self.xlog else (v - lo) / (hi - lo)
        return self.x + t * self.w

    def py(self, v):
        lo, hi = self.yr
        t = (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) if self.ylog else (v - lo) / (hi - lo)
        return self.y + self.h - t * self.h

    def frame(self, xticks, yticks, xlabel, ylabel, xfmt=str, yfmt=str):
        c = self.c
        for v in yticks:
            c.add(f'<line x1="{self.x}" y1="{self.py(v):.1f}" x2="{self.x + self.w}" y2="{self.py(v):.1f}" stroke="{FAINT}" stroke-width="1"/>')
            c.text(self.x - 8, self.py(v) + 4, yfmt(v), size=11.5, anchor="end", fill=MUTED)
        for v in xticks:
            c.add(f'<line x1="{self.px(v):.1f}" y1="{self.y}" x2="{self.px(v):.1f}" y2="{self.y + self.h}" stroke="{FAINT}" stroke-width="1"/>')
            c.text(self.px(v), self.y + self.h + 18, xfmt(v), size=11.5, fill=MUTED)
        c.rect(self.x, self.y, self.w, self.h, stroke=MUTED, sw=1.2)
        c.text(self.x + self.w / 2, self.y + self.h + 38, xlabel, size=12.5, fill=INK)
        c.add(f'<text x="{self.x - 46}" y="{self.y + self.h / 2}" font-size="12.5" text-anchor="middle" fill="{INK}" '
              f'transform="rotate(-90 {self.x - 46} {self.y + self.h / 2})">{ylabel}</text>')

    def line(self, pts, color, width=2.2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        path = " ".join(f"{'M' if i == 0 else 'L'}{self.px(x):.1f},{self.py(y):.1f}" for i, (x, y) in enumerate(pts))
        self.c.add(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{width}"{d}/>')

    def dots(self, pts, color, r=3.6, shape="circle"):
        for x, y in pts:
            px, py = self.px(x), self.py(y)
            if shape == "square":
                self.c.add(f'<rect x="{px - r:.1f}" y="{py - r:.1f}" width="{2 * r}" height="{2 * r}" fill="{color}"/>')
            else:
                self.c.add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r}" fill="{color}"/>')


def degree_karate():
    deg = karate_degrees()
    n = len(deg)
    counts = {k: deg.count(k) for k in range(1, max(deg) + 1)}
    c = Canvas(900, 340, "Degrees in the karate club",
               "Left: a bar chart of how many members have each number of ties. Right: the share of members with at least k ties.")
    left = Axes(c, 70, 40, 340, 230, (0.5, 17.5), (0, 12))
    left.frame([1, 5, 10, 15], [0, 4, 8, 12], "ties (degree)", "members")
    for k, v in counts.items():
        if v:
            c.rect(left.px(k - 0.4), left.py(v), left.px(k + 0.4) - left.px(k - 0.4), left.y + left.h - left.py(v), fill=BLUE, stroke=BLUE, sw=0.5)
    c.text(left.x + left.w / 2, 24, "How many members have k ties", size=14, weight="700")
    right = Axes(c, 520, 40, 340, 230, (1, 20), (0.02, 1), xlog=True, ylog=True)
    right.frame([1, 2, 5, 10, 20], [0.03, 0.1, 0.3, 1], "ties (degree), log scale", "share with at least k ties, log scale",
                yfmt=lambda v: f"{v:g}")
    pts = ccdf(deg)
    right.dots(pts, BLUE)
    c.text(right.x + right.w / 2, 24, "Share of members with at least k ties", size=14, weight="700")
    meta = dict(chapter=9,
                caption="The 34 members of the karate club. Left: most members have few ties and a handful have many. Right: the same distribution as a complementary cumulative distribution on log axes, the form used to look at tails.",
                alt=f"Two charts of karate club degrees. The bar chart shows {counts[2]} members with 2 ties, {counts[3]} with 3, {counts[4]} with 4, one with 1 tie, and single members with 9, 10, 12, 16 and 17 ties. The log-log chart plots the share of members with at least k ties; it starts at 1 for k = 1 and falls to {1 / n:.3f} at k = 17.",
                data={"degree_counts": counts})
    return c, meta


def degree_models():
    r = rows("small_worlds/degrees.csv")
    random = [int(x["random"]) for x in r]
    grown = [int(x["grown"]) for x in r]
    c = Canvas(560, 400, "Degree distributions of a random and a grown network",
               "Log-log plot of the share of people with at least k ties for two networks of 2000 people.")
    a = Axes(c, 80, 40, 440, 280, (1, 300), (0.0004, 1), xlog=True, ylog=True)
    a.frame([1, 3, 10, 30, 100, 300], [0.001, 0.01, 0.1, 1], "ties (degree), log scale", "share with at least k ties, log scale",
            yfmt=lambda v: f"{v:g}")
    a.dots(ccdf(random), ORANGE, shape="square")
    a.dots(ccdf(grown), BLUE)
    c.add(f'<rect x="300" y="52" width="9" height="9" fill="{ORANGE}"/>')
    c.text(316, 61, "ties placed at random", size=12.5, anchor="start")
    c.add(f'<circle cx="305" cy="80" r="4.5" fill="{BLUE}"/>')
    c.text(316, 84, "grown by preferential attachment", size=12.5, anchor="start")
    c.text(300, 24, "Two networks of 2,000 people, about 4 ties each", size=14, weight="700")
    meta = dict(chapter=9,
                caption="Complementary cumulative degree distributions of two networks of 2,000 people with the same average degree. The random network's tail falls away steeply after about ten ties; the grown network's tail stretches to well over a hundred.",
                alt=f"A log-log plot with two clouds of dots. The orange squares, a network with ties placed at random, run from share 1 at degree 1 and drop sharply, ending at degree {max(random)}. The blue circles, a network grown by preferential attachment, fall in a nearly straight slope and end at degree {max(grown)}.",
                data={"max_random": max(random), "max_grown": max(grown)})
    return c, meta


def ws_curve():
    r = rows("small_worlds/ws_sweep.csv")
    pts_c = [(float(x["p"]), float(x["c_ratio"])) for x in r]
    pts_l = [(float(x["p"]), float(x["l_ratio"])) for x in r]
    c = Canvas(640, 400, "Rewiring a ring lattice",
               "Clustering and mean distance, each relative to the ring with no rewiring, against the rewiring probability.")
    a = Axes(c, 80, 40, 520, 280, (0.0001, 1), (0, 1.05), xlog=True)
    a.frame([0.0001, 0.001, 0.01, 0.1, 1], [0, 0.25, 0.5, 0.75, 1], "share of ties rewired, p (log scale)",
            "relative to the ring (p = 0)", xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}")
    a.line(pts_c, BLUE)
    a.dots(pts_c, BLUE)
    a.line(pts_l, ORANGE, dash="7 4")
    a.dots(pts_l, ORANGE, shape="square", r=3.4)
    c.add(f'<line x1="215" y1="140" x2="245" y2="140" stroke="{BLUE}" stroke-width="2.2"/>')
    c.text(251, 144, "clustering, C(p) / C(0)", size=12.5, anchor="start")
    c.add(f'<line x1="215" y1="161" x2="245" y2="161" stroke="{ORANGE}" stroke-width="2.2" stroke-dasharray="7 4"/>')
    c.text(251, 165, "mean distance, L(p) / L(0)", size=12.5, anchor="start")
    c.text(320, 24, "1,000 people, each tied to the 10 nearest on a ring", size=14, weight="700")
    mid = min(r, key=lambda x: abs(float(x["p"]) - 0.01))
    meta = dict(chapter=9,
                caption="Rewiring a ring lattice. A few rewired ties collapse the mean distance while clustering barely moves; clustering falls only when a large share of ties has been rewired. The small-world range is the stretch in between.",
                alt=f"A line chart with a log horizontal axis from 0.0001 to 1. The solid blue line, clustering relative to the ring, stays near 1 until about p = 0.03 and then falls to {pts_c[-1][1]:.2f} at p = 1. The dashed orange line, mean distance relative to the ring, drops early: it is {float(mid['l_ratio']):.2f} at p = 0.01, while clustering there is still {float(mid['c_ratio']):.2f}, and it ends at {pts_l[-1][1]:.2f}.",
                data={"p": [x[0] for x in pts_c], "c_ratio": [x[1] for x in pts_c], "l_ratio": [x[1] for x in pts_l]})
    return c, meta


def baselines():
    r = rows("small_worlds/baselines.csv")
    nets = ["karate", "florentine", "managers"]
    c = Canvas(820, 360, "Three networks against two random baselines",
               "For each of three networks, transitivity and mean distance in the observed network, in random networks with the same number of ties, and in random networks with the same degrees.")
    for panel, (measure, title, top, ticks) in enumerate([("transitivity", "Transitivity", 0.8, [0, 0.2, 0.4, 0.6, 0.8]), ("mean distance", "Mean distance", 3.0, [0, 1, 2, 3])]):
        x0 = 70 + panel * 400
        a = Axes(c, x0, 50, 320, 230, (0, 3), (0, top))
        a.frame([], ticks, "", "", yfmt=lambda v: f"{v:g}")
        c.text(x0 + 160, 30, title, size=14, weight="700")
        for i, net in enumerate(nets):
            row = next(x for x in r if x["network"] == net and x["measure"] == measure)
            cx = a.px(i + 0.5)
            c.text(cx, 50 + 230 + 20, net, size=12.5, fill=INK)
            for dx, key, col, shape in [(-26, "observed", INK, "circle"), (0, "random", ORANGE, "square"), (26, "same_degrees", BLUE, "circle")]:
                y = a.py(float(row[key]))
                if shape == "square":
                    c.add(f'<rect x="{cx + dx - 5:.1f}" y="{y - 5:.1f}" width="10" height="10" fill="{col}"/>')
                else:
                    c.add(f'<circle cx="{cx + dx:.1f}" cy="{y:.1f}" r="5.5" fill="{col}"/>')
    c.add(f'<circle cx="190" cy="326" r="5.5" fill="{INK}"/>')
    c.text(200, 330, "observed", size=12.5, anchor="start")
    c.add(f'<rect x="300" y="321" width="10" height="10" fill="{ORANGE}"/>')
    c.text(316, 330, "same number of ties, placed at random", size=12.5, anchor="start")
    c.add(f'<circle cx="565" cy="326" r="5.5" fill="{BLUE}"/>')
    c.text(575, 330, "same degrees", size=12.5, anchor="start")
    vals = {(x["network"], x["measure"]): x for x in r}
    meta = dict(chapter=9,
                caption="Each network against two random baselines. The left panel is how clustered the network is; the right is how far apart people are. Keeping every person's degree (blue) usually moves the random baseline toward the observed network, so it is the harder one to beat.",
                alt="Two panels with three groups of three dots each, one group per network: karate, florentine and managers. Each group shows the observed value in black, the random-ties baseline in orange and the same-degrees baseline in blue. " +
                    " ".join(f"{n} {m}: observed {float(vals[(n, m)]['observed']):.2f}, random {float(vals[(n, m)]['random']):.2f}, same degrees {float(vals[(n, m)]['same_degrees']):.2f}." for m in ("transitivity", "mean distance") for n in nets),
                data={f"{n}|{m}": {k: float(vals[(n, m)][k]) for k in ("observed", "random", "same_degrees")} for m in ("transitivity", "mean distance") for n in nets})
    return c, meta


FIGURES = {
    "sw-degree-karate": degree_karate,
    "sw-degree-models": degree_models,
    "sw-ws-curve": ws_curve,
    "sw-baselines": baselines,
}

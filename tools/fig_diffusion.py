"""Figures for the diffusion chapter (chapter 24).

Standard library only. The contact network is the karate club (books/sna/data/karate) or a
60-person ring written here; the outbreaks are simulated by the small functions below, which
follow the chapter's code. The pictures use their own random numbers, so their curves differ
slightly from the numbers in the code blocks.
"""
import csv
import math
import random
from pathlib import Path

from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"


def karate():
    with open(DATA / "karate" / "edges.csv", newline="") as f:
        ties = [(int(r["source"]) - 1, int(r["target"]) - 1) for r in csv.DictReader(f)]
    nb = [[] for _ in range(34)]
    for a, b in ties:
        nb[a].append(b)
        nb[b].append(a)
    return nb


def ring(n, k, p, rng):
    m = [[False] * n for _ in range(n)]
    for a in range(n):
        for step in range(1, k + 1):
            b = (a + step) % n
            if rng.random() < p:
                b = rng.randrange(n)
            if a != b:
                m[a][b] = m[b][a] = True
    return [[j for j in range(n) if m[i][j]] for i in range(n)]


def spread(nb, seeds, beta, gamma, steps, rng, thr=0):
    """States 0 susceptible, 1 infected, 2 recovered. Returns the list of states after each step."""
    s = [0] * len(nb)
    for i in seeds:
        s[i] = 1
    out = [s]
    for _ in range(steps):
        nxt = s[:]
        for i, row in enumerate(nb):
            k = sum(1 for j in row if s[j] == 1)
            if s[i] == 0:
                if (k >= thr) if thr else (rng.random() < 1 - (1 - beta) ** k):
                    nxt[i] = 1
            elif s[i] == 1 and rng.random() < gamma:
                nxt[i] = 2
        s = nxt
        out.append(s)
    return out


def quantile(v, p):
    v = sorted(v)
    h = p * (len(v) - 1)
    lo, hi = math.floor(h), math.ceil(h)
    return v[lo] + (h - lo) * (v[hi] - v[lo])


class Plot:
    """A plain linear plot area with faint grid lines."""

    def __init__(self, c, x, y, w, h, xr, yr, xticks, yticks, xlabel, ylabel=None, yfmt="{:.1f}"):
        self.c, self.x, self.y, self.w, self.h, self.xr, self.yr = c, x, y, w, h, xr, yr
        for v in yticks:
            py = self.py(v)
            c.add(f'<line x1="{x}" y1="{py:.1f}" x2="{x + w}" y2="{py:.1f}" stroke="{FAINT}" stroke-width="0.8"/>')
            c.text(x - 8, py + 4, yfmt.format(v), size=12, anchor="end")
        c.add(f'<line x1="{x}" y1="{y + h}" x2="{x + w}" y2="{y + h}" stroke="{INK}" stroke-width="1.5"/>')
        c.add(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + h}" stroke="{INK}" stroke-width="1.5"/>')
        for v in xticks:
            c.text(self.px(v), y + h + 18, f"{v:g}", size=12)
        c.text(x + w / 2, y + h + 40, xlabel, size=13, fill=MUTED)
        if ylabel:
            c.text(x, y - 12, ylabel, size=13, fill=MUTED, anchor="start")

    def px(self, v):
        return self.x + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def py(self, v):
        return self.y + self.h - (v - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def line(self, xs, ys, color, dash=None, width=3):
        pts = " ".join(f"{self.px(a):.1f},{self.py(b):.1f}" for a, b in zip(xs, ys))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.c.add(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}"{d}/>')

    def band(self, xs, lo, hi, color):
        pts = [(self.px(a), self.py(b)) for a, b in zip(xs, hi)] + [(self.px(a), self.py(b)) for a, b in zip(reversed(xs), reversed(lo))]
        self.c.add(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{color}" fill-opacity="0.15"/>')

    def key(self, x, y, color, dash, label):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.c.add(f'<line x1="{x}" y1="{y}" x2="{x + 34}" y2="{y}" stroke="{color}" stroke-width="3"{d}/>')
        self.c.text(x + 42, y + 4, label, size=13, anchor="start")


# ---------------------------------------------------------------- spread curves by seed rule
def seed_curves():
    nb = karate()
    deg = [len(v) for v in nb]
    hub, periphery = deg.index(max(deg)), deg.index(min(deg))
    rng = random.Random(24)
    steps, runs = 16, 1500
    rules = [("seeded at the best-connected member (17 ties)", lambda: hub, BLUE, None),
             ("seeded at a random member", lambda: rng.randrange(34), ORANGE, "7 5"),
             ("seeded at the member with one tie", lambda: periphery, RED, "2 5")]
    c = Canvas(900, 440, "Spread curves by seed rule", "Average number of infected members of the karate club over time for three seed rules.")
    pl = Plot(c, 80, 50, 760, 280, (0, steps), (0, 34), range(0, steps + 1, 2), (0, 8.5, 17, 25.5, 34),
              "steps since the first infection", "members infected (out of 34)", yfmt="{:g}")
    facts = []
    for k, (label, pick, col, dash) in enumerate(rules):
        curves = []
        for _ in range(runs):
            h = spread(nb, [pick()], 0.2, 0, steps, rng)
            curves.append([sum(s) for s in h])
        xs = list(range(steps + 1))
        mean = [sum(cv[t] for cv in curves) / runs for t in xs]
        pl.band(xs, [quantile([cv[t] for cv in curves], .025) for t in xs], [quantile([cv[t] for cv in curves], .975) for t in xs], col)
        pl.line(xs, mean, col, dash)
        pl.key(100, 76 + k * 24, col, dash, label)
        half = next(t for t, v in enumerate(mean) if v >= 17)
        width = max(quantile([cv[t] for cv in curves], .975) - quantile([cv[t] for cv in curves], .025) for t in xs)
        facts.append((label, half, mean[4], mean[-1], width))
    pl.c.add(f'<line x1="{pl.x}" y1="{pl.py(17):.1f}" x2="{pl.x + pl.w}" y2="{pl.py(17):.1f}" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="3 4"/>')
    meta = dict(chapter=24,
                caption="Simple contagion (SI, infection chance 0.2 per tie per step) on the karate club, 1,500 simulated outbreaks per seed rule. Lines are the average number of members infected; shaded bands hold the middle 95 percent of runs. The dotted line marks half the club. The outbreak is simulated; only the ties are observed.",
                alt=("Three rising curves of the number of karate club members infected over 16 steps, each starting at 1. "
                     f"By step 16 the average is {facts[0][3]:.1f}, {facts[1][3]:.1f} and {facts[2][3]:.1f} for the best-connected, random and one-tie seeds. The average passes half the club (17) at step {facts[0][1]} for the best-connected seed, step {facts[1][1]} for the random seed and step {facts[2][1]} for the one-tie seed. "
                     f"Shaded bands around each line show the middle 95 percent of runs; the widest band is {max(facts, key=lambda f: f[4])[4]:.0f} members tall, for the seed '{max(facts, key=lambda f: f[4])[0]}'."),
                data={"average_infected_at_step_4": {f[0]: round(f[2], 2) for f in facts}, "steps_to_half_by_average": {f[0]: f[1] for f in facts}})
    return c, meta


# ---------------------------------------------------------------- attack rate against transmissibility
def attack_curve():
    nb = karate()
    deg = [len(v) for v in nb]
    n = len(nb)
    mean_k = sum(deg) / n
    t_c = mean_k / (sum(d * d for d in deg) / n - mean_k)
    rng = random.Random(25)
    ts = [i / 40 for i in range(1, 25)]
    mean, lo, hi = [], [], []
    for t in ts:
        r = []
        for _ in range(1000):
            h = spread(nb, [rng.randrange(n)], t, 1.0, 40, rng)
            r.append(sum(1 for v in h[-1] if v) / n)
        mean.append(sum(r) / len(r))
        lo.append(quantile(r, .025))
        hi.append(quantile(r, .975))
    c = Canvas(900, 420, "Final size against transmissibility", "Average share of the karate club ever infected against the chance an infected member passes it to a given contact.")
    pl = Plot(c, 80, 40, 760, 280, (0, 0.6), (0, 1), [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], (0, 0.25, 0.5, 0.75, 1),
              "transmissibility T, the chance an infected member passes it to one contact", "share of the club ever infected", yfmt="{:.2f}")
    pl.band(ts, lo, hi, BLUE)
    pl.line(ts, mean, BLUE)
    tx = pl.px(t_c)
    c.add(f'<line x1="{tx:.1f}" y1="{pl.y}" x2="{tx:.1f}" y2="{pl.y + pl.h}" stroke="{RED}" stroke-width="2.2" stroke-dasharray="7 5"/>')
    c.text(tx + 8, pl.y + 16, f"T_c = {t_c:.3f}", size=13, anchor="start", fill=RED, weight="700")
    at = lambda t: mean[ts.index(t)]
    meta = dict(chapter=24,
                caption="Average share of the karate club that ends up infected after one random seed, against the transmissibility T (SIR, 1,000 simulated outbreaks per value). The shaded band holds the middle 95 percent of runs. The dashed line is the degree-moment threshold. With 34 people the curve bends gradually; it does not jump at the threshold.",
                alt=(f"A curve rising from about {mean[0]:.2f} at T = 0.025 to about {mean[-1]:.2f} at T = 0.6, with a dashed vertical line at T = {t_c:.3f}. "
                     f"The average share infected is {at(0.25):.2f} at T = 0.25 and {at(0.5):.2f} at T = 0.5. The lower edge of the shaded band stays at one person out of 34 (the seed alone) for every T up to {max(t for t, v in zip(ts, lo) if v <= 1 / 34 + 1e-9):.3f}, because some outbreaks die at once."),
                data={"t_c": round(t_c, 4), "T": ts, "mean": [round(v, 4) for v in mean]})
    return c, meta


# ---------------------------------------------------------------- simple and complex on ring and rewired
def complex_curves():
    rng = random.Random(26)
    n, steps, runs = 60, 30, 500
    panels = [("Simple contagion (0.15 per infected tie)", dict(beta=0.15, gamma=0)),
              ("Complex contagion (needs 2 adopting ties)", dict(beta=0, gamma=0, thr=2))]
    c = Canvas(960, 430, "Simple and complex contagion on a ring and a rewired network",
               "Two panels of average share adopted over time on a clustered ring and a rewired random network.")
    facts = {}
    for q, (title, kw) in enumerate(panels):
        x0 = 70 + q * 460
        pl = Plot(c, x0, 60, 380, 250, (0, steps), (0, 1), range(0, steps + 1, 5), (0, 0.5, 1), "steps", None, yfmt="{:.1f}")
        c.text(x0 + 190, 38, title, size=14, weight="600")
        for label, p, col, dash in (("clustered ring (clustering 0.6)", 0, BLUE, None), ("rewired (clustering about 0.08)", 1, ORANGE, "7 5")):
            curves = []
            for _ in range(runs):
                nb = ring(n, 3, p, rng)
                s = rng.randrange(n)
                seeds = [s] + rng.sample(nb[s], min(2, len(nb[s])))
                h = spread(nb, seeds, steps=steps, rng=rng, **kw)
                curves.append([sum(1 for v in st if v == 1) / n for st in h])
            xs = list(range(steps + 1))
            mean = [sum(cv[t] for cv in curves) / runs for t in xs]
            pl.line(xs, mean, col, dash)
            pl.key(x0 + 130, 250 + (0 if p == 0 else 22), col, dash, label)
            facts[(q, p)] = mean[-1]
            facts[(q, p, 8)] = mean[8]
    meta = dict(chapter=24,
                caption="Share of a 60-person network that has adopted, by step, averaged over 500 simulated runs per line, from one random member plus two of their contacts. Left: each contact passes it on with chance 0.15 per step. Right: a person adopts once two of their contacts have. The clustered ring is a 60-person ring where each person is tied to the three people on either side; the rewired network re-draws every tie's far end at random.",
                alt=(f"Two panels of rising curves. On the left, simple contagion has reached {facts[(0, 0)]:.2f} of the clustered ring (solid) and {facts[(0, 1)]:.2f} of the rewired network (dashed) by step 30; at step 8 the figures are {facts[(0, 0, 8)]:.2f} and {facts[(0, 1, 8)]:.2f}. "
                     f"On the right, complex contagion has reached {facts[(1, 0)]:.2f} of the clustered ring by step 30 and {facts[(1, 1)]:.2f} of the rewired network."),
                data={"share_at_step_8": {"simple_ring": round(facts[(0, 0, 8)], 3), "simple_rewired": round(facts[(0, 1, 8)], 3)},
                      "final_share": {"simple_ring": round(facts[(0, 0)], 3), "simple_rewired": round(facts[(0, 1)], 3),
                                      "complex_ring": round(facts[(1, 0)], 3), "complex_rewired": round(facts[(1, 1)], 3)}})
    return c, meta


FIGURES = {
    "diffusion-seeds": seed_curves,
    "diffusion-attack": attack_curve,
    "diffusion-complex": complex_curves,
}

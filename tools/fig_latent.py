"""Figures for the latent space and block model chapter (chapter 22).

Standard library only. Every number drawn is read from the CSV files in
books/sna/data/latent, which tools/latent_data.py writes by running the chapter's own
Python code (40 posterior draws of the map; 200 simulated networks per model).
"""
import csv
import math
from pathlib import Path

from figs import BLUE, FAINT, INK, MUTED, ORANGE, PURPLE, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data" / "latent"
SIDE_STYLE = {0: (BLUE, "circle"), 1: (ORANGE, "square")}


def read(name):
    with open(DATA / name, newline="") as f:
        return list(csv.DictReader(f))


def posterior_cloud():
    fit = {int(r["member"]): (float(r["x"]), float(r["y"]), int(r["side"])) for r in read("fit.csv")}
    draws = {}
    for r in read("draws.csv"):
        draws.setdefault(int(r["member"]), []).append((float(r["x"]), float(r["y"])))
    n_draws = len(draws[0])
    spread = {i: math.sqrt(sum((x - fit[i][0]) ** 2 + (y - fit[i][1]) ** 2 for x, y in pts) / len(pts)) for i, pts in draws.items()}
    xs = [x for pts in draws.values() for x, _ in pts] + [v[0] for v in fit.values()]
    ys = [y for pts in draws.values() for _, y in pts] + [v[1] for v in fit.values()]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h, pad = 900, 580, 50
    scale = min((w - 2 * pad) / (x1 - x0), (h - 2 * pad - 30) / (y1 - y0))
    px = lambda x: pad + (x - x0) * scale  # noqa: E731
    py = lambda y: h - pad - 20 - (y - y0) * scale  # noqa: E731
    c = Canvas(w, h, "How far the map could move", "The fitted map of the karate club with 40 posterior draws of every member's position drawn as small dots around it.")
    for i, pts in draws.items():
        col, _ = SIDE_STYLE[fit[i][2]]
        for x, y in pts:
            c.add(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="2.3" fill="{col}" fill-opacity="0.35"/>')
    for i, (x, y, side) in fit.items():
        col, shape = SIDE_STYLE[side]
        c.node(px(x), py(y), "", r=6, fill="#ffffff", stroke=col, shape=shape, sw=2)
    for i, name in ((0, "Mr. Hi"), (2, "member 2"), (33, "the officer")):
        x, y, _ = fit[i]
        c.text(px(x) + 12, py(y) - 10, name, size=13, weight="700", anchor="start")
    c.node(300, h - 22, "", r=6, fill="#ffffff", stroke=BLUE)
    c.text(314, h - 18, "Mr. Hi's side", size=12.5, anchor="start")
    c.node(450, h - 22, "", r=6, fill="#ffffff", stroke=ORANGE, shape="square")
    c.text(464, h - 18, "the officer's side", size=12.5, anchor="start")
    c.text(w / 2, 24, "Large markers: the fitted map. Small dots: where each member sat in 40 posterior draws", size=13, fill=MUTED)
    lo, hi = min(spread, key=spread.get), max(spread, key=spread.get)
    # Spread against number of friends, from the club's own ties.
    degree = {}
    with open(DATA.parent / "karate" / "edges.csv", newline="") as f:
        for r in csv.DictReader(f):
            for end in (int(r["source"]) - 1, int(r["target"]) - 1):
                degree[end] = degree.get(end, 0) + 1
    few = [spread[i] for i in spread if degree[i] <= 2]
    many = [spread[i] for i in spread if degree[i] >= 10]
    meta = dict(chapter=22,
                caption="The fitted map of the karate club (large markers) with 40 posterior draws of every member's position (small dots). Each draw was turned and mirrored to match the fitted map, because a map is only defined up to such moves. The cloud around a member shows how far the data let that member's place move.",
                alt=f"A scatter of 34 large hollow markers, blue circles for Mr. Hi's side and orange squares for the officer's side, each surrounded by {n_draws} small dots of the same color. The dots lie a root-mean-square {spread[lo]:.1f} map units from the fitted position for member {lo}, the tightest cloud, and {spread[hi]:.1f} units for member {hi}, the widest. The {len(few)} members with at most two friends average {sum(few) / len(few):.1f} units, and the {len(many)} members with ten or more friends average {sum(many) / len(many):.1f}.",
                data={"rms_spread": {str(i): round(v, 3) for i, v in spread.items()}})
    return c, meta


def gof_intervals():
    rows = read("gof.csv")
    stats = list(dict.fromkeys(r["statistic"] for r in rows))
    models = list(dict.fromkeys(r["model"] for r in rows))
    colors = {models[0]: MUTED, models[1]: BLUE, models[2]: ORANGE}
    c = Canvas(900, 560, "Does the model reproduce the club?", "Four panels, one per summary of the karate club, each showing for three fitted models the middle 95 percent of 200 simulated networks and the club's own value.")
    facts = []
    for k, stat in enumerate(stats):
        gx, gy = 40 + (k % 2) * 440, 60 + (k // 2) * 250
        sub = [r for r in rows if r["statistic"] == stat]
        lo = min(min(float(r["low"]) for r in sub), float(sub[0]["club"]))
        hi = max(max(float(r["high"]) for r in sub), float(sub[0]["club"]))
        span = hi - lo
        lo, hi = lo - 0.08 * span, hi + 0.08 * span
        left, width = gx + 150, 250
        sx = lambda v, lo=lo, hi=hi, left=left, width=width: left + (v - lo) / (hi - lo) * width  # noqa: E731
        c.text(gx, gy - 14, stat, size=14, weight="700", anchor="start")
        club = float(sub[0]["club"])
        c.add(f'<line x1="{sx(club):.1f}" y1="{gy}" x2="{sx(club):.1f}" y2="{gy + 3 * 52 - 10}" stroke="{INK}" stroke-width="2" stroke-dasharray="5 4"/>')
        c.text(sx(club), gy + 3 * 52 + 6, f"club {club:g}", size=12, fill=INK)
        inside = []
        for j, r in enumerate(sub):
            y = gy + 20 + j * 52
            col = colors[r["model"]]
            c.text(gx + 138, y + 4, r["model"], size=12, anchor="end")
            c.add(f'<line x1="{sx(float(r["low"])):.1f}" y1="{y}" x2="{sx(float(r["high"])):.1f}" y2="{y}" stroke="{col}" stroke-width="5" stroke-linecap="round"/>')
            c.node(sx(float(r["median"])), y, "", r=5, fill="#ffffff", stroke=col, sw=2)
            if float(r["low"]) <= club <= float(r["high"]):
                inside.append(r["model"])
        facts.append((stat, club, inside))
    parts = []
    for stat, club, inside in facts:
        parts.append(f"{stat}: the club's {club:g} lies inside the interval of " + (", ".join(inside) if inside else "no model") )
    meta = dict(chapter=22,
                caption="Goodness of fit by simulation. For each of three fitted models, 200 networks were simulated and four summaries computed. Bars show the middle 95 percent, dots the median, and the dashed line the karate club's own value. A model fits a summary when the line falls inside its bar.",
                alt="Four small panels with three horizontal bars each, for the models with the same chance for every pair, the latent space map and hubs and the rest, with a dashed vertical line at the club's value. " + "; ".join(parts) + ".",
                data={"rows": rows})
    return c, meta


FIGURES = {"latent-posterior": posterior_cloud, "latent-gof": gof_intervals}

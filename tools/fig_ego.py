"""Figures for the ego-networks chapter (chapter 13).

Standard library only. Every number drawn is computed here, from the CSV files in
books/sna/data (krackhardt, florentine), with constraint written out from its definition.
"""
import csv
from pathlib import Path

from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"


def read(name, file):
    with open(DATA / name / file, newline="") as f:
        return list(csv.DictReader(f))


def managers():
    """Krackhardt's friendship relation, a tie if either manager names the other."""
    adj = {i: set() for i in range(1, 22)}
    for r in read("krackhardt", "edges.csv"):
        if r["relation"] == "friendship":
            a, b = int(r["from"]), int(r["to"])
            adj[a].add(b)
            adj[b].add(a)
    return adj


def families():
    adj = {}
    for r in read("florentine", "edges.csv"):
        adj.setdefault(r["source"], set()).add(r["target"])
        adj.setdefault(r["target"], set()).add(r["source"])
    return adj


def constraint(adj, i, inside=None):
    """Burt's constraint of i for binary ties; if inside is given, every contact's degree counts only ties inside it."""
    def deg(q):
        return len(adj[q] if inside is None else adj[q] & inside)
    total = 0.0
    for j in adj[i]:
        indirect = sum((1 / len(adj[i])) * (1 / deg(q)) for q in adj[i] if q != j and j in adj[q])
        total += (1 / len(adj[i]) + indirect) ** 2
    return total


def ego_only(adj):
    return {i: constraint(adj, i, inside=adj[i] | {i}) for i in adj}


def whole(adj):
    return {i: constraint(adj, i) for i in adj}


def without(adj, gone):
    return {i: adj[i] - {gone} for i in adj if i != gone}


def ego_vs_whole():
    panels = [("Krackhardt's managers, friendship", managers()), ("Florentine families, marriage", families())]
    c = Canvas(760, 400, "Constraint from an ego network alone, against constraint from the whole network",
               "Two scatter plots of constraint computed from each person's ego network alone against constraint computed from the whole network, with the diagonal drawn.")
    stats = []
    for k, (title, adj) in enumerate(panels):
        w, e = whole(adj), ego_only(adj)
        x0, y0, size, top_v = 60 + k * 380, 60, 290, 1.2
        c.text(x0 + size / 2, 28, title, size=14, weight="600")
        c.add(f'<rect x="{x0}" y="{y0}" width="{size}" height="{size}" fill="none" stroke="{INK}" stroke-width="1.5"/>')
        c.add(f'<line x1="{x0}" y1="{y0 + size}" x2="{x0 + size}" y2="{y0}" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="6 4"/>')
        for v in (0, 0.4, 0.8, 1.2):
            px, py = x0 + v / top_v * size, y0 + size - v / top_v * size
            c.text(px, y0 + size + 18, f"{v:g}", size=12)
            c.text(x0 - 8, py + 4, f"{v:g}", size=12, anchor="end")
        c.text(x0 + size / 2, y0 + size + 40, "constraint, whole network", size=13, fill=MUTED)
        c.add(f'<text x="{x0 - 42}" y="{y0 + size / 2}" font-size="13" text-anchor="middle" fill="{MUTED}" '
              f'transform="rotate(-90 {x0 - 42} {y0 + size / 2})">constraint, ego network alone</text>')
        for i in adj:
            c.add(f'<circle cx="{x0 + w[i] / top_v * size:.1f}" cy="{y0 + size - e[i] / top_v * size:.1f}" r="4.5" fill="{BLUE}" fill-opacity="0.55" stroke="{BLUE}"/>')
        on = sum(abs(e[i] - w[i]) < 1e-9 for i in adj)
        stats.append((len(adj), min(w.values()), max(w.values()), min(e.values()), max(e.values()), on,
                      sum(e[i] < w[i] - 1e-9 for i in adj)))
    (n1, wl1, wh1, el1, eh1, on1, bad1), (n2, wl2, wh2, el2, eh2, on2, bad2) = stats
    assert bad1 == 0 and bad2 == 0
    meta = dict(chapter=13,
                caption="Constraint computed from each person's ego network alone, against constraint computed from the whole network. The dashed line is where the two agree. No point lies below it.",
                alt=(f"Two scatter plots, each with a dashed diagonal. Left, the {n1} managers of Krackhardt's firm: whole-network constraint runs from {wl1:.2f} to {wh1:.2f} "
                     f"and ego-network constraint from {el1:.2f} to {eh1:.2f}, and {on1} of the {n1} points lie on the diagonal. Right, the {n2} Florentine families: whole-network constraint runs from "
                     f"{wl2:.2f} to {wh2:.2f} and ego-network constraint from {el2:.2f} to {eh2:.2f}, and {on2} of the {n2} points lie on the diagonal. In both plots every other point lies above the diagonal."),
                data={"krackhardt": {str(i): [round(whole(managers())[i], 4), round(ego_only(managers())[i], 4)] for i in managers()},
                      "florentine": {i: [round(whole(families())[i], 4), round(ego_only(families())[i], 4)] for i in families()}})
    return c, meta


def medici_stress():
    adj = families()
    base = whole(adj)
    rows = [("nobody removed", adj)] + [(f"{a} removed", without(adj, a)) for a in sorted(adj["Medici"])]
    c = Canvas(720, 370, "The Medici's constraint when one marriage partner is left out",
               "For each scenario, the Medici's constraint and the lowest constraint among the other families.")
    x0, w = 190, 480
    lo, hi = 0.15, 0.40
    xs = lambda v: x0 + (v - lo) / (hi - lo) * w
    top = 70
    gap = 34
    c.add(f'<line x1="{x0}" y1="{top - 22}" x2="{x0}" y2="{top + gap * (len(rows) - 1) + 22}" stroke="{FAINT}"/>')
    for v in (0.15, 0.20, 0.25, 0.30, 0.35, 0.40):
        c.add(f'<line x1="{xs(v):.1f}" y1="{top - 22}" x2="{xs(v):.1f}" y2="{top + gap * (len(rows) - 1) + 22}" stroke="{FAINT}"/>')
        c.text(xs(v), top + gap * (len(rows) - 1) + 44, f"{v:.2f}", size=12)
    c.text(x0 + w / 2, top + gap * (len(rows) - 1) + 68, "constraint (lower means fewer redundant contacts)", size=13, fill=MUTED)
    results = []
    for k, (label, g) in enumerate(rows):
        con = whole(g)
        # a family left with no partner has no constraint, so it cannot be the least constrained
        others = {f: v for f, v in con.items() if f != "Medici" and g[f]}
        other, other_v = min(others.items(), key=lambda kv: (kv[1], kv[0]))
        m = con["Medici"]
        y = top + k * gap
        c.text(x0 - 14, y + 4, label, size=13, anchor="end")
        c.add(f'<circle cx="{xs(other_v):.1f}" cy="{y}" r="7" fill="{PAPER}" stroke="{BLUE}" stroke-width="2.5"/>')
        c.add(f'<rect x="{xs(m) - 6:.1f}" y="{y - 6}" width="12" height="12" fill="{ORANGE}" stroke="{INK}"/>')
        results.append((label, m, other, other_v))
    c.text(x0, 24, "orange square: the Medici", size=13, weight="600", fill=ORANGE, anchor="start")
    c.text(x0 + 220, 24, "blue circle: lowest of the other families", size=13, weight="600", fill=BLUE, anchor="start")
    first = results[0]
    lead = [r for r in results[1:] if r[1] <= r[3]]
    alt_rows = "; ".join(f"{r[0]}: Medici {r[1]:.3f}, {r[2]} {r[3]:.3f}" for r in results)
    meta = dict(chapter=13,
                caption="The Medici's constraint (orange square) against the lowest constraint among the other families (blue circle), first with the full data and then with each of the Medici's six marriage partners left out in turn.",
                alt=f"Seven rows, each with an orange square for the Medici and a blue circle for the family with the lowest constraint among the others. {alt_rows}. The Medici have the lowest constraint in {len(lead) + 1} of the 7 rows.",
                data={"scenarios": [{"scenario": r[0], "medici": round(r[1], 4), "lowest_other": r[2], "lowest_other_value": round(r[3], 4)} for r in results]})
    return c, meta


FIGURES = {"ego-vs-whole": ego_vs_whole, "medici-stress": medici_stress}

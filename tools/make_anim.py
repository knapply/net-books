#!/usr/bin/env python3
"""Build the book's animations from knappnet results. Standard library only, deterministic.

Usage: python3 tools/make_anim.py          (runs alongside tools/make_figures.py; neither calls the other)

For every animation it reads books/sna/data/anim/<id>.frames.json (raw engine results written by
tools/anim_data) and writes books/sna/figures/anim/<id>.json (the player data, schema v1) and
books/sna/figures/anim/<id>-still.svg (the filmstrip that print, PDF, EPUB and no-JavaScript readers see).
See docs/ANIMATION.md.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fig_layout import distances, fit, stress_layout  # noqa: E402
from figs import BLUE, FAINT, INK, MUTED, ORANGE, RED, SKY, Canvas  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "books" / "sna" / "data" / "anim"
OUT = ROOT / "books" / "sna" / "figures" / "anim"
GRAY = "#9ca3af"

# The palette the player knows (shared/js/netanim.js): role -> (node fill, node stroke). Edge color = fill, base = gray.
NODE = {"base": ("#eef6fb", BLUE), "src": (ORANGE, "#b87f00"), "reach": (SKY, BLUE), "hot": (RED, "#9a4300"),
        "dim": ("#e5e7eb", GRAY)}
DEFAULT_NODE = {"f": "base", "r": 16, "l": "", "ring": 0}
DEFAULT_EDGE = {"k": "base", "w": 1.6}


def edge_color(role):
    return GRAY if role == "base" else NODE[role][0]


def r1(x):
    return round(x + 0.0, 1)


def encode(scene):
    """scene: dict with w, h, id, ms, nodes[(name,x,y)], edges, panel, states [(nodes, edges, m, text)], still."""
    prev_n = [dict(DEFAULT_NODE) for _ in scene["nodes"]]
    prev_e = [dict(DEFAULT_EDGE) for _ in scene["edges"]]
    prev_p = [(r1(x), r1(y)) for _, x, y in scene["nodes"]]
    frames = []
    for st in scene["states"]:
        nodes, edges, m, text = st[:4]
        f = {"t": text}
        if len(st) > 4 and st[4] is not None:  # optional fifth element: a position (x, y) for every node
            now = [(r1(x), r1(y)) for x, y in st[4]]
            dp = {str(i): list(q) for i, (q, p) in enumerate(zip(now, prev_p)) if q != p}
            if dp:
                f["p"] = dp
            prev_p = now
        dn = {str(i): {k: v for k, v in s.items() if p.get(k) != v} for i, (s, p) in enumerate(zip(nodes, prev_n))}
        dn = {i: d for i, d in dn.items() if d}
        de = {str(i): {k: v for k, v in s.items() if p.get(k) != v} for i, (s, p) in enumerate(zip(edges, prev_e))}
        de = {i: d for i, d in de.items() if d}
        if dn:
            f["n"] = dn
        if de:
            f["e"] = de
        if m is not None:
            f["m"] = m
        frames.append(f)
        prev_n, prev_e = nodes, edges
    doc = {"v": 1, "id": scene["id"], "w": scene["w"], "h": scene["h"], "ms": scene["ms"],
           "nodes": [{"id": n, "x": r1(x), "y": r1(y)} for n, x, y in scene["nodes"]],
           "edges": [list(e) for e in scene["edges"]], "dir": bool(scene.get("dir")), "panel": scene["panel"],
           "frames": frames, "still": scene["still"]}
    return json.dumps(doc, separators=(",", ":"), ensure_ascii=False) + "\n"


def filmstrip(scene, labels, title, desc, show=None):
    """A 2 by 2 grid of the key frames, drawn with the same colors the player uses."""
    pw, ph, scale = 470, 300, 0.8
    idx = scene["still"]
    c = Canvas(960, 30 + 310 * ((len(idx) + 1) // 2), title, desc)
    pos = [(x, y) for _, x, y in scene["nodes"]]
    allp = [q for st in scene["states"] if len(st) > 4 and st[4] is not None for q in st[4]] or pos
    xs, ys = [p[0] for p in allp], [p[1] for p in allp]
    gx, gy = min(xs), min(ys)
    for k, fi in enumerate(idx):
        ox, oy = 20 + (k % 2) * pw, 20 + (k // 2) * 310
        nodes, edges, m, _ = scene["states"][fi][:4]
        if len(scene["states"][fi]) > 4 and scene["states"][fi][4] is not None:
            pos = list(scene["states"][fi][4])  # this frame's own positions (layouts that move)
        c.rect(ox, oy, pw - 20, ph, fill="none", stroke=FAINT, sw=1, rx=8)
        c.text(ox + 14, oy + 24, labels[k], size=14, anchor="start", weight="700")
        mp = [(ox + 40 + (x - gx) * scale, oy + 54 + (y - gy) * scale) for x, y in pos]
        if scene.get("compact"):  # big networks: edges and dots grouped by style so the picture stays small
            paths, dots, rings = {}, {}, []
            for (a, b), e in zip(scene["edges"], edges):
                if e["k"] != "dim":
                    paths.setdefault((edge_color(e["k"]), round(e["w"] * 0.9, 1)), []).append(
                        f"M{mp[a][0]:.0f} {mp[a][1]:.0f}L{mp[b][0]:.0f} {mp[b][1]:.0f}")
            for (col, w), d in paths.items():
                c.add(f'<path d="{"".join(d)}" fill="none" stroke="{col}" stroke-width="{w}"/>')
            for i, nd in enumerate(nodes):
                dots.setdefault((nd["f"], round(nd["r"] * scale, 1)), []).append(i)
                if nd["ring"]:
                    rings.append(i)
            for (role, r), ids in dots.items():
                fill, stroke = NODE[role]
                c.add(f'<g fill="{fill}" stroke="{stroke}" stroke-width="1.6">'
                      + "".join(f'<circle cx="{mp[i][0]:.0f}" cy="{mp[i][1]:.0f}" r="{r}"/>' for i in ids) + "</g>")
            if rings:
                c.add(f'<g fill="none" stroke="{RED}" stroke-width="2">'
                      + "".join(f'<circle cx="{mp[i][0]:.0f}" cy="{mp[i][1]:.0f}" r="{nodes[i]["r"] * scale + 4:.1f}"/>' for i in rings) + "</g>")
            for i, nd in enumerate(nodes):
                tag = scene["nodes"][i][0] if not show else show(i, m)
                if tag:
                    c.text(mp[i][0], mp[i][1] + nd["r"] * scale + 13, tag, size=11, fill=MUTED)
            continue
        for (a, b), e in zip(scene["edges"], edges):
            c.edge(mp[a], mp[b], ra=0, rb=nodes[b]["r"] * scale if scene.get("dir") else 0, directed=bool(scene.get("dir")), width=e["w"] * (0.9 if e["w"] < 2 else 1), color=edge_color(e["k"]))
        for i, nd in enumerate(nodes):
            fill, stroke = NODE[nd["f"]]
            r = nd["r"] * scale
            if nd["ring"]:
                c.add(f'<circle cx="{mp[i][0]:.1f}" cy="{mp[i][1]:.1f}" r="{r + 5:.1f}" fill="none" stroke="{RED}" stroke-width="2"/>')
            c.node(mp[i][0], mp[i][1], nd["l"], r=r, fill=fill, stroke=stroke, size=11)
            tag = scene["nodes"][i][0] if not show else show(i, m)
            c.text(mp[i][0], mp[i][1] + r + 13, tag, size=11, fill=MUTED)
    return c.svg()


def layout(names, edges):
    """The book's usual picture of the friendship network: stress layout, seed 3."""
    pos = fit(stress_layout(len(names), [tuple(e) for e in edges], seed=3), 24, 56, 400, 270)
    return [(n, p[0], p[1]) for n, p in zip(names, pos)]


def load(aid, book="sna"):
    return json.loads((ROOT / "books" / book / "data" / "anim" / f"{aid}.frames.json").read_text())


def join(words):
    words = list(words)
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]


# ------------------------------------------------------------------ breadth-first search
def bfs():
    raw = load("bfs-expansion")
    names, edges, src, dist = raw["names"], raw["edges"], raw["source"], raw["distances"]
    n = len(names)
    # the engine's answer must agree with a plain search (a check, not the source of the frames)
    check = distances(n, [tuple(e) for e in edges])[src]
    assert [int(d) for d in check] == dist, "engine BFS levels disagree with the reference search"
    top = max(dist)
    nodes0 = layout(names, edges)
    states = []
    for k in range(top + 2):
        kk = min(k, top)
        ns, es = [], []
        for i in range(n):
            if i == src:
                ns.append({"f": "src", "r": 18, "l": "0", "ring": 0})
            elif dist[i] <= kk:
                ns.append({"f": "reach", "r": 20 if dist[i] == kk and k <= top else 16, "l": str(dist[i]),
                           "ring": 1 if dist[i] == kk and k <= top else 0})
            else:
                ns.append(dict(DEFAULT_NODE))
        for a, b in edges:
            reached = max(dist[a], dist[b]) <= kk
            fwd = abs(dist[a] - dist[b]) == 1 and reached
            now = fwd and max(dist[a], dist[b]) == kk and k <= top
            es.append({"k": "hot" if now else "reach" if fwd else "base", "w": 3.2 if now else 2.4 if fwd else 1.6})
        counts = [sum(1 for i in range(n) if dist[i] == j and j <= kk) for j in range(top + 1)]
        if k == 0:
            text = f"We start at {names[src]}. Everyone else is still waiting to be found."
        elif k <= top:
            who = [names[i] for i in range(n) if dist[i] == k]
            if k == 1:
                text = f"Everyone one step from {names[src]} lights up: that's distance 1 ({join(who)})."
            else:
                text = f"Now the friends of those people, not yet found: {join(who)}. That's distance {k}."
        else:
            text = f"Nobody is left to find. The farthest anyone is from {names[src]} is {top} steps."
        states.append((ns, es, counts, text))
    labels_panel = ["Jo itself"] + [f"{j} step{'s' if j > 1 else ''}" for j in range(1, top + 1)]
    labels_panel[0] = f"{names[src]} (0)"
    scene = {"id": "bfs-expansion", "w": 640, "h": 360, "ms": 1400, "nodes": nodes0, "edges": edges,
             "panel": {"kind": "bars", "x": 452, "y": 74, "w": 172, "h": 200, "labels": labels_panel,
                       "max": max(sum(1 for d in dist if d == j) for j in range(top + 1)) + 1,
                       "title": "People found"},
             "states": states, "still": [0, 1, 3, 4]}
    strip_labels = ["Start", "One step out", "Three steps out", "Four steps out"]
    still = filmstrip(scene, strip_labels, "Breadth-first search from Jo",
                      "Four copies of the ten-person friendship network showing a search spreading from Jo, one step at a time.")
    return scene, still


# ------------------------------------------------------------------ eigenvector centrality
def eigen():
    raw = load("eigen-converge")
    names, edges, rounds, settled = raw["names"], raw["edges"], raw["rounds"], raw["settled"]
    n = len(names)
    scaled = [[v / max(r) for v in r] for r in rounds] + [[v / max(settled) for v in settled]]
    nodes0 = layout(names, edges)
    # the last round and the engine's settled answer must agree to the shown precision
    assert max(abs(a - b) for a, b in zip(scaled[-2], scaled[-1])) < 0.005, "rounds have not settled"
    states, last = [], len(scaled) - 1
    moved = [0.0] + [max(abs(a - b) for a, b in zip(scaled[k], scaled[k - 1])) for k in range(1, len(scaled))]
    calm = next(k for k in range(1, last) if all(m < 0.005 for m in moved[k:last]))
    for k, v in enumerate(scaled):
        top = max(v)
        ns = [{"f": "src" if (k > 0 and v[i] == top) else "base", "r": r1(7 + 15 * v[i]), "l": "", "ring": 0} for i in range(n)]
        es = [dict(DEFAULT_EDGE) for _ in edges]
        deg = [sum(1 for e in edges if i in e) for i in range(n)]
        order = sorted(range(n), key=lambda i: -v[i])
        if k == 0:
            text = "Everyone starts with a score of 1, so nobody is ahead yet."
        elif k == 1:
            text = (f"Round 1: each score becomes the sum of friends' scores, then everything is rescaled so the top is 1. "
                    f"That is just friend counts: {names[order[0]]} has {deg[order[0]]}, {names[order[-1]]} has {deg[order[-1]]}.")
        elif k == 2:
            text = "Round 2: now it matters who your friends are. Scores shift toward people whose friends are well connected."
        elif k < last:
            mover = max(range(n), key=lambda i: abs(scaled[k][i] - scaled[k - 1][i]))
            if k == calm:
                text = f"Round {k}: from here on, no score moves by more than 0.005. The ranking has settled."
            elif k > calm:
                text = f"Round {k}: the scores look the same as before, to two decimals."
            else:
                text = f"Round {k}: the biggest change is {moved[k]:.2f}, for {names[mover]}. Changes are shrinking."
        else:
            text = (f"Where it settles, the engine's own answer: {names[order[0]]} is 1.00, "
                    f"{names[order[-1]]} is {v[order[-1]]:.2f}. The {last - 1} rounds above landed in the same place.")
        states.append((ns, es, [round(x, 3) for x in v], text))
    scene = {"id": "eigen-converge", "w": 640, "h": 360, "ms": 1100, "nodes": nodes0, "edges": edges,
             "panel": {"kind": "bars", "x": 452, "y": 56, "w": 172, "h": 268, "labels": names, "max": 1,
                       "title": "Score"},
             "states": states, "still": [0, 1, 3, last]}
    labels = ["Start: everyone at 1", "Round 1", "Round 3", "Settled"]

    def show(i, m):
        return f"{names[i]} {m[i]:.2f}"

    still = filmstrip(scene, labels, "Scores passing along, ten people",
                      "Four copies of the ten-person friendship network with dots sized by score at the start, rounds 1 and 3, and settled.",
                      show=show)
    return scene, still


BUILDERS = {"bfs-expansion": bfs, "eigen-converge": eigen}
sys.modules.setdefault("make_anim", sys.modules[__name__]); from anim_scenes import discover; BUILDERS.update(discover())  # noqa: E402


def main() -> int:
    for aid, fn in BUILDERS.items():
        scene, still = fn()
        out = ROOT / "books" / scene.get("book", "sna") / "figures" / "anim"  # a scene may set "book" (default sna)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{aid}.json").write_text(encode(scene))
        (out / f"{aid}-still.svg").write_text(still)
        print(f"{aid}: {(out / (aid + '.json')).stat().st_size} B json, {(out / (aid + '-still.svg')).stat().st_size} B still")
    return 0


if __name__ == "__main__":
    sys.exit(main())

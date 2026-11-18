"""A smaller filmstrip for scenes with many dots and ties (the generic one in make_anim.py draws every tie as its own
element and would blow the 25 KB budget). Same layout, colors and look; ties of one color and width share one path.
Holds no scene: BUILDERS is empty so discover() has nothing to register."""

BUILDERS = {}


def filmstrip(M, scene, labels, title, desc, size=10, tag=None):
    from figs import FAINT, INK, MUTED, RED, Canvas

    pw, ph, scale = 470, 300, 0.8
    idx = scene["still"]
    c = Canvas(960, 30 + 310 * ((len(idx) + 1) // 2), title, desc)
    pos = [(x, y) for _, x, y in scene["nodes"]]
    gx, gy = min(p[0] for p in pos), min(p[1] for p in pos)
    bw, bh = max(p[0] for p in pos) - gx or 1, max(p[1] for p in pos) - gy or 1
    fit = min(400 / bw, 218 / bh)  # fill the frame, keeping the shape
    dx = (400 - bw * fit) / 2
    for k, fi in enumerate(idx):
        ox, oy = 20 + (k % 2) * pw, 20 + (k // 2) * 310
        nodes, edges, m, _ = scene["states"][fi]
        c.rect(ox, oy, pw - 20, ph, fill="none", stroke=FAINT, sw=1, rx=8)
        c.text(ox + 14, oy + 24, labels[k], size=14, anchor="start", weight="700")
        mp = [(round(ox + 25 + dx + (x - gx) * fit), round(oy + 56 + (y - gy) * fit)) for x, y in pos]
        groups = {}
        for (a, b), e in zip(scene["edges"], edges):
            if e["w"] <= 0:
                continue
            groups.setdefault((M.edge_color(e["k"]), round(e["w"] * (0.9 if e["w"] < 2 else 1), 1)), []).append(
                f"M{mp[a][0]} {mp[a][1]}L{mp[b][0]} {mp[b][1]}")
        for (col, w), segs in sorted(groups.items(), key=lambda kv: kv[0][1]):
            c.add(f'<path d="{"".join(segs)}" fill="none" stroke="{col}" stroke-width="{w:g}"/>')
        dots, rings, texts, tags = [], [], [], []
        for i, nd in enumerate(nodes):
            fill, stroke = M.NODE[nd["f"]]
            r = round(nd["r"] * scale)
            x, y = mp[i]
            if nd["ring"]:
                rings.append(f'<circle cx="{x}" cy="{y}" r="{r + 4}"/>')
            dots.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}"/>')
            if tag:
                tags.append(f'<text x="{x}" y="{y + r + 12}">{tag(i, m)}</text>')
            if nd["l"]:
                texts.append(f'<text x="{x}" y="{y + 3}">{nd["l"]}</text>')
        if rings:
            c.add(f'<g fill="none" stroke="{RED}" stroke-width="2">{"".join(rings)}</g>')
        c.add(f'<g stroke-width="2">{"".join(dots)}</g>')
        if tags:
            c.add(f'<g font-size="10" text-anchor="middle" fill="{MUTED}">{"".join(tags)}</g>')
        if texts:
            c.add(f'<g font-size="{size}" font-weight="600" text-anchor="middle" fill="{INK}">{"".join(texts)}</g>')
    return c.svg()

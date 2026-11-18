"""A lean filmstrip for scenes with many ties: all ties of one style go into a single path, so a 34-node, 78-tie picture
stays far under the 25 KB budget for a still. Same layout, colors and fonts as make_anim.filmstrip."""
from figs import FAINT, MUTED, RED, Canvas


def lean_filmstrip(scene, labels, title, desc, show=None):
    import make_anim as M
    pw, ph, scale = 470, 300, 0.8
    idx = scene["still"]
    c = Canvas(960, 30 + 310 * ((len(idx) + 1) // 2), title, desc)
    base = [(x, y) for _, x, y in scene["nodes"]]
    gx, gy = min(p[0] for p in base), min(p[1] for p in base)
    for k, fi in enumerate(idx):
        st = scene["states"][fi]
        nodes, edges, m = st[0], st[1], st[2]
        pos = list(st[4]) if len(st) > 4 and st[4] is not None else base
        ox, oy = 20 + (k % 2) * pw, 20 + (k // 2) * 310
        c.rect(ox, oy, pw - 20, ph, fill="none", stroke=FAINT, sw=1, rx=8)
        c.text(ox + 14, oy + 24, labels[k], size=14, anchor="start", weight="700")
        mp = [(ox + 40 + (x - gx) * scale, oy + 54 + (y - gy) * scale) for x, y in pos]
        groups = {}
        for (a, b), e in zip(scene["edges"], edges):
            if e["w"] <= 0:
                continue
            key = (M.edge_color(e["k"]), round(e["w"] * (0.9 if e["w"] < 2 else 1), 1))
            groups.setdefault(key, []).append(f"M{mp[a][0]:.0f} {mp[a][1]:.0f}L{mp[b][0]:.0f} {mp[b][1]:.0f}")
        for (col, w), segs in sorted(groups.items(), key=lambda kv: kv[0][1]):
            c.add(f'<path d="{"".join(segs)}" fill="none" stroke="{col}" stroke-width="{w}"/>')
        for i, nd in enumerate(nodes):
            fill, stroke = M.NODE[nd["f"]]
            r = nd["r"] * scale
            x, y = mp[i]
            if nd["ring"]:
                c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r + 5:.1f}" fill="none" stroke="{RED}" stroke-width="2"/>')
            c.node(x, y, nd["l"], r=round(r, 1), fill=fill, stroke=stroke, size=11)
            tag = show(i, m) if show else ""
            if tag:
                c.text(x, y + r + 13, tag, size=11, fill=MUTED)
    return c.svg()

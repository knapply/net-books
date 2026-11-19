"""Shared drawing helpers for the algorithms-book figure modules (fig_alg_*.py). Standard library only."""
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, PURPLE, RED, SKY, Canvas

LIGHT = "#eef6fb"
PALE_ORANGE = "#fdf1d6"
PALE_RED = "#fbe3d6"
PALE_GREEN = "#d8f0e8"
PALE_PURPLE = "#f6e3ee"
FIVE = ["Ana", "Ben", "Cleo", "Dev", "Eli"]
FIVE_TIES = [(0, 1), (1, 2), (1, 3), (2, 3), (3, 4)]
FIVE_ADJ = {0: [1], 1: [0, 2, 3], 2: [1, 3], 3: [1, 2, 4], 4: [3]}
# Where the five people sit, in a box about 280 wide and 140 tall.
FIVE_POS = [(0, 70), (95, 70), (175, 10), (175, 130), (270, 130)]


def csr_of(adj, n):
    offsets, targets = [0], []
    for i in range(n):
        targets += sorted(adj[i])
        offsets.append(len(targets))
    return offsets, targets


def net5(c, ox, oy, s=1.0, ids=True, names=True, r=18, hi_nodes=(), hi_edges=(), fills=None, size=13):
    """The five people at (ox, oy). The number inside each dot is the id; the name sits underneath."""
    pos = [(ox + x * s, oy + y * s) for x, y in FIVE_POS]
    for k, (a, b) in enumerate(FIVE_TIES):
        hot = (a, b) in hi_edges or (b, a) in hi_edges
        c.edge(pos[a], pos[b], ra=r, rb=r, color=ORANGE if hot else INK, width=3.4 if hot else 2)
    for i, (x, y) in enumerate(pos):
        fill = (fills or {}).get(i, PALE_ORANGE if i in hi_nodes else LIGHT)
        c.node(x, y, str(i) if ids else "", r=r, fill=fill, stroke=ORANGE if i in hi_nodes else BLUE, size=size)
        if names:
            c.text(x, y - r - 8 if i == 2 else y + r + 16, FIVE[i], size=12, fill=MUTED)
    return pos


def cells(c, x, y, vals, w=40, h=34, fills=None, strokes=None, idx=True, idx_label=None, size=14, bold=False, gap=0):
    """A row of boxes holding vals, with the position number underneath. Returns the box centers."""
    out = []
    for k, v in enumerate(vals):
        cx = x + k * (w + gap)
        fill = (fills or {}).get(k, PAPER)
        stroke = (strokes or {}).get(k, INK)
        c.rect(cx, y, w, h, fill=fill, stroke=stroke, sw=1.6)
        c.text(cx + w / 2, y + h / 2 + size * 0.36, str(v), size=size, weight="700" if bold else "500")
        if idx:
            c.text(cx + w / 2, y + h + 14, str(k), size=11, fill=MUTED)
        out.append((cx + w / 2, y + h / 2))
    if idx_label:
        c.text(x - 8, y + h + 14, idx_label, size=11, anchor="end", fill=MUTED, italic=True)
    return out


def legend_dot(c, x, y, color, label, size=12):
    c.rect(x, y - 10, 14, 14, fill=color + "33", stroke=color, sw=1.6, rx=3)
    c.text(x + 22, y + 2, label, size=size, anchor="start")


def pill(c, x, y, w, h, text, fill, stroke, size=12, weight="600"):
    c.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=h / 2)
    c.text(x + w / 2, y + h / 2 + size * 0.36, text, size=size, weight=weight)


def human_bytes(b):
    for unit, f in (("TB", 1e12), ("GB", 1e9), ("MB", 1e6), ("KB", 1e3)):
        if b >= f:
            v = b / f
            return f"{v:.0f} {unit}" if v >= 10 else f"{v:.1f} {unit}"
    return f"{b:.0f} B"

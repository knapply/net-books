"""Tiny SVG drawing helpers for the book's figures. Standard library only.

House style (see docs/FIGURES.md): colour-blind-safe palette, shape and line style
repeat what colour says (so figures survive greyscale printing), text is real
text, every figure has a title and a description for assistive technology.
"""
import html
import math

INK = "#1f2937"
MUTED = "#6b7280"
FAINT = "#d1d5db"
PAPER = "#ffffff"
BLUE = "#0072B2"
ORANGE = "#E69F00"
RED = "#D55E00"
GREEN = "#009E73"
PURPLE = "#CC79A7"
SKY = "#56B4E9"
FONT = 'system-ui, "Helvetica Neue", Arial, sans-serif'
MONO = 'ui-monospace, "SF Mono", Menlo, Consolas, monospace'


def esc(s) -> str:
    return html.escape(str(s), quote=True)


class Canvas:
    def __init__(self, width, height, title, desc):
        self.w, self.h, self.title, self.desc = width, height, title, desc
        self.parts: list[str] = []
        self.markers: dict[str, str] = {}

    # -- plumbing -------------------------------------------------------
    def add(self, s: str):
        self.parts.append(s)

    def marker(self, color: str) -> str:
        mid = "arrow-" + color.lstrip("#")
        if mid not in self.markers:
            self.markers[mid] = (
                f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
                f'fill="{color}"/></marker>')
        return mid

    def svg(self) -> str:
        defs = "".join(self.markers.values())
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}" role="img" font-family=\'{FONT}\'>\n'
            f'<title>{esc(self.title)}</title>\n<desc>{esc(self.desc)}</desc>\n'
            f'<defs>{defs}</defs>\n'
            f'<rect width="{self.w}" height="{self.h}" fill="{PAPER}"/>\n'
            + "\n".join(self.parts) + "\n</svg>\n")

    # -- primitives -----------------------------------------------------
    def text(self, x, y, s, size=14, anchor="middle", weight="400", fill=INK,
             mono=False, italic=False):
        fam = f' font-family=\'{MONO}\'' if mono else ""
        st = ' font-style="italic"' if italic else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
                 f'font-weight="{weight}" fill="{fill}"{fam}{st}>{esc(s)}</text>')

    def lines(self, x, y, rows, size=14, anchor="start", gap=1.45, **kw):
        for i, r in enumerate(rows):
            self.text(x, y + i * size * gap, r, size=size, anchor=anchor, **kw)

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=1.5, rx=0, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def halo(self, x, y, w, h, color, label=None, dash="6 4"):
        self.rect(x, y, w, h, fill=color + "14", stroke=color, sw=1.6, rx=min(w, h) / 2.6, dash=dash)
        if label:
            self.text(x + w / 2, y - 7, label, size=13, weight="600", fill=color)

    def node(self, x, y, label="", r=18, fill=PAPER, stroke=INK, shape="circle",
             size=13, sw=2, label_fill=INK):
        if shape == "circle":
            self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        elif shape == "square":
            self.add(f'<rect x="{x - r}" y="{y - r}" width="{2 * r}" height="{2 * r}" rx="3" '
                     f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        elif shape == "diamond":
            pts = f"{x},{y - r * 1.2} {x + r * 1.2},{y} {x},{y + r * 1.2} {x - r * 1.2},{y}"
            self.add(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        if label:
            self.text(x, y + size * 0.36, label, size=size, weight="600", fill=label_fill)

    def edge(self, a, b, ra=18, rb=18, directed=False, color=INK, width=2, dash=None,
             curve=0, sign=None, label=None, opacity=1.0):
        (x1, y1), (x2, y2) = a, b
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1
        ux, uy = dx / d, dy / d
        # perpendicular for curves
        px, py = -uy, ux
        sx, sy = x1 + ux * (ra + 1), y1 + uy * (ra + 1)
        gap = rb + (4 if directed else 1)
        ex, ey = x2 - ux * gap, y2 - uy * gap
        dashattr = f' stroke-dasharray="{dash}"' if dash else ""
        mk = f' marker-end="url(#{self.marker(color)})"' if directed else ""
        op = f' opacity="{opacity}"' if opacity != 1 else ""
        if curve:
            cx, cy = (sx + ex) / 2 + px * curve, (sy + ey) / 2 + py * curve
            self.add(f'<path d="M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}" fill="none" '
                     f'stroke="{color}" stroke-width="{width}"{dashattr}{mk}{op}/>')
            mx, my = (sx + 2 * cx + ex) / 4, (sy + 2 * cy + ey) / 4
        else:
            self.add(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" '
                     f'stroke-width="{width}"{dashattr}{mk}{op}/>')
            mx, my = (sx + ex) / 2, (sy + ey) / 2
        if sign:
            col = BLUE if sign == "+" else RED
            self.add(f'<circle cx="{mx - px * 11:.1f}" cy="{my - py * 11:.1f}" r="9" fill="{PAPER}" '
                     f'stroke="{col}" stroke-width="1.5"/>')
            self.text(mx - px * 11, my - py * 11 + 5, "+" if sign == "+" else "−", size=15,
                      weight="700", fill=col)
        if label:
            self.text(mx - px * 12, my - py * 12 + 4, label, size=12, fill=MUTED)

    def arrow(self, a, b, color=MUTED, width=2, curve=0):
        self.edge(a, b, ra=0, rb=0, directed=True, color=color, width=width, curve=curve)

    def caption(self, x, y, s, size=14, weight="600", fill=INK):
        self.text(x, y, s, size=size, weight=weight, fill=fill)


def ring(cx, cy, r, n, start=-90):
    return [(cx + r * math.cos(math.radians(start + 360 * i / n)),
             cy + r * math.sin(math.radians(start + 360 * i / n))) for i in range(n)]


def bfs_mean_distance(n, edges):
    adj = {i: set() for i in range(n)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    total = count = 0
    for s in range(n):
        dist = {s: 0}
        queue = [s]
        for u in queue:
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        for t, d in dist.items():
            if t != s:
                total += d
                count += 1
    return total / count

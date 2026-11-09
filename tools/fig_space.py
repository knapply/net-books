"""Figures for the chapter on networks in space.

Standard library only. Every number drawn is computed here from the CSV files in
books/sna/data/space, so the pictures cannot drift from the data. Maps use the
equirectangular projection: longitude and latitude are used directly as x and y.
"""
import csv
import math
import re
from pathlib import Path

from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data" / "space" / "borders"
EARTH_KM = 6371.0088
BIN_KM = 500
LAST_BIN = 6  # bins 0..5 are 500 km wide; bin 6 is 3000 km and more
GRAY = "#9ca3af"


def read(name):
    with open(DATA / name, newline="") as f:
        return list(csv.DictReader(f))


def haversine(lon1, lat1, lon2, lat2, radius=EARTH_KM):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(min(1.0, max(0.0, h))))


def load():
    nodes = read("nodes.csv")
    index = {n["id"]: i for i, n in enumerate(nodes)}
    lon = [float(n["longitude"]) for n in nodes]
    lat = [float(n["latitude"]) for n in nodes]
    ties = [(index[e["source"]], index[e["target"]]) for e in read("edges.csv")]
    return nodes, index, lon, lat, ties


def all_pairs(lon, lat):
    n = len(lon)
    return [(i, j, haversine(lon[i], lat[i], lon[j], lat[j])) for i in range(n) for j in range(i + 1, n)]


def bin_of(d):
    return min(int(d // BIN_KM), LAST_BIN)


class Map:
    """An equirectangular map panel: lon -180..180 and lat -58..84 mapped to a box."""

    LAT0, LAT1 = -58.0, 84.0

    def __init__(self, canvas, x, y, width):
        self.c, self.x, self.y, self.w = canvas, x, y, width
        self.h = width * (self.LAT1 - self.LAT0) / 360.0

    def xy(self, lon, lat):
        return (self.x + (lon + 180.0) / 360.0 * self.w,
                self.y + (self.LAT1 - lat) / (self.LAT1 - self.LAT0) * self.h)

    def frame(self):
        self.c.rect(self.x, self.y, self.w, self.h, fill="#f8fafc", stroke=FAINT, sw=1)

    def inside(self, lat):
        return self.LAT0 <= lat <= self.LAT1


def wkt_parts(wkt):
    parts = []
    for body in re.findall(r"\(([^()]+)\)", wkt):
        pts = [tuple(map(float, p.split())) for p in body.split(",")]
        parts.append(pts)
    return parts


def border_map():
    nodes, index, lon, lat, ties = load()
    geometry = read("geometry.csv")
    c = Canvas(960, 520, "Country land borders as a spatial network",
               "A world map with a dot for each country unit and a line for each shared land border.")
    m = Map(c, 10, 14, 940)
    m.frame()
    for g in geometry:
        for part in wkt_parts(g["geometry"]):
            d = " ".join(f"{'M' if k == 0 else 'L'}{m.xy(px, py)[0]:.1f},{m.xy(px, py)[1]:.1f}"
                         for k, (px, py) in enumerate(part))
            c.add(f'<path d="{d}" fill="none" stroke="{GRAY}" stroke-width="1.1"/>')
    fra, bra, sur = index["FRA"], index["BRA"], index["SUR"]
    odd = {(min(fra, bra), max(fra, bra)), (min(fra, sur), max(fra, sur))}
    for a, b in ties:
        key = (min(a, b), max(a, b))
        if key in odd or not (m.inside(lat[a]) and m.inside(lat[b])):
            continue
        (x1, y1), (x2, y2) = m.xy(lon[a], lat[a]), m.xy(lon[b], lat[b])
        c.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{BLUE}" '
              f'stroke-width="1.3" opacity="0.55"/>')
    for a, b in sorted(odd):
        (x1, y1), (x2, y2) = m.xy(lon[a], lat[a]), m.xy(lon[b], lat[b])
        c.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ORANGE}" '
              f'stroke-width="2.2" stroke-dasharray="7 4"/>')
    degree = [0] * len(nodes)
    for a, b in ties:
        degree[a] += 1
        degree[b] += 1
    shown = 0
    for i in range(len(nodes)):
        if not m.inside(lat[i]):
            continue
        shown += 1
        x, y = m.xy(lon[i], lat[i])
        if degree[i] == 0:
            c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#ffffff" stroke="{MUTED}" stroke-width="1.2"/>')
        else:
            c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{BLUE}" stroke="#ffffff" stroke-width="0.8"/>')
    px, py = m.xy(lon[fra], lat[fra])
    c.add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.5" fill="{ORANGE}" stroke="{INK}" stroke-width="1.2"/>')
    c.text(px - 90, py - 46, "France: the dot is at Paris, but the unit", size=11.5, anchor="end", fill=INK)
    c.text(px - 90, py - 33, "also holds French Guiana", size=11.5, anchor="end", fill=INK)
    bx, by = m.xy(lon[bra], lat[bra])
    c.text(bx + 8, by - 16, "Brazil", size=11.5, anchor="start", fill=INK)
    notes = ["Equirectangular projection: longitude and latitude are used as x and y, so high latitudes are stretched.",
             "Blue lines join the dots of countries that share a border; they are straight on the page, not great circles.",
             "Grey lines are the shared borders. Hollow dots border no one (islands). Antarctica, south of the frame, is left out.",
             "Dashed orange: the two ties that exist only because the French unit includes French Guiana."]
    for k, line in enumerate(notes):
        c.text(12, 22 + m.h + 14 + 15 * k, line, size=11.5, anchor="start", fill=MUTED)
    c.h = int(22 + m.h + 14 + 15 * len(notes) + 2)
    n_ties = len(ties)
    meta = dict(chapter=14,
                caption="The 177 country units of Natural Earth as a spatial network. A dot is a unit's label point and a line is a shared land border; the longest lines are the two orange dashed ones, which come from French Guiana.",
                alt=f"A flat world map. Blue dots mark countries and blue lines join neighbouring countries, forming a connected web across Europe, Africa, Asia and South America, with a looser set of ties in North and Central America. Hollow dots are islands with no land border. Two orange dashed lines run from the dot for France, at Paris, across the Atlantic to the dots for Brazil and Suriname.",
                data={"nodes": len(nodes), "ties": n_ties, "dots_shown": shown})
    return c, meta


def decay_bars():
    nodes, index, lon, lat, ties = load()
    pairs = all_pairs(lon, lat)
    tie_set = {(min(a, b), max(a, b)) for a, b in ties}
    total = [0] * (LAST_BIN + 1)
    tied = [0] * (LAST_BIN + 1)
    for i, j, d in pairs:
        b = bin_of(d)
        total[b] += 1
        tied[b] += (i, j) in tie_set
    share = [t / n for t, n in zip(tied, total)]
    labels = [f"{b * BIN_KM}-{(b + 1) * BIN_KM}" for b in range(LAST_BIN)] + ["3000+"]
    c = Canvas(780, 380, "Distance decay of ties",
               "Bar chart of the share of country pairs that share a border, by distance between their label points.")
    left, base, top = 70, 300, 50
    width = 680
    step = width / (LAST_BIN + 1)
    c.add(f'<line x1="{left}" y1="{base}" x2="{left + width}" y2="{base}" stroke="{INK}" stroke-width="1.5"/>')
    ymax = 0.7
    for tick in (0, 0.2, 0.4, 0.6):
        y = base - tick / ymax * (base - top)
        c.add(f'<line x1="{left}" y1="{y:.1f}" x2="{left + width}" y2="{y:.1f}" stroke="{FAINT}" stroke-width="1"/>')
        c.text(left - 8, y + 4, f"{int(tick * 100)}%", size=12, anchor="end", fill=MUTED)
    for b in range(LAST_BIN + 1):
        h = share[b] / ymax * (base - top)
        x = left + b * step + step * 0.15
        c.rect(round(x, 1), round(base - h, 1), round(step * 0.7, 1), round(h, 1), fill=BLUE, stroke=BLUE, sw=1)
        c.text(x + step * 0.35, base - h - 8, f"{share[b] * 100:.1f}%", size=12, weight="600")
        c.text(x + step * 0.35, base + 18, labels[b], size=12, fill=MUTED)
        c.text(x + step * 0.35, base + 34, f"{tied[b]} of {total[b]}", size=11, fill=MUTED)
    c.text(left + width / 2, base + 56, "Distance between label points (km); beneath: tied pairs of all pairs in the bin",
           size=12.5, fill=MUTED)
    c.text(left - 52, top - 22, "Share of pairs with a shared border", size=12.5, anchor="start", fill=MUTED)
    meta = dict(chapter=14,
                caption="Share of country pairs that share a land border, by the distance between their label points. Ties are common among close pairs and rare among distant ones, but the 3000 km and beyond bin is not zero.",
                alt="A bar chart with seven bars. The share of pairs with a shared border is " +
                    ", ".join(f"{s * 100:.1f} percent" for s in share[:-1]) + f", and {share[-1] * 100:.1f} percent for the bins 0 to 500, 500 to 1000, 1000 to 1500, 1500 to 2000, 2000 to 2500, 2500 to 3000 and 3000 kilometres and more. The bars fall steeply from left to right, then flatten near zero.",
                data={"bins_km": labels, "pairs": total, "tied": tied, "share": share})
    return c, meta


def threshold_panels():
    nodes, index, lon, lat, ties = load()
    pairs = all_pairs(lon, lat)
    tie_set = {(min(a, b), max(a, b)) for a, b in ties}
    radii = [500, 1000, 2000]
    c = Canvas(980, 330, "Proximity networks at three radii",
               "Three world maps. Each joins every pair of countries whose label points are within a radius.")
    pw = 300
    gap = 20
    rows = []
    for k, r in enumerate(radii):
        m = Map(c, 12 + k * (pw + gap), 40, pw)
        m.frame()
        near = [(i, j) for i, j, d in pairs if d <= r]
        hit = sum((i, j) in tie_set for i, j in near)
        rows.append((r, len(near), hit))
        for i, j in near:
            if not (m.inside(lat[i]) and m.inside(lat[j])):
                continue
            (x1, y1), (x2, y2) = m.xy(lon[i], lat[i]), m.xy(lon[j], lat[j])
            real = (i, j) in tie_set
            col = BLUE if real else GRAY
            c.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" '
                  f'stroke-width="{1.6 if real else 0.7}" opacity="{0.9 if real else 0.5}"/>')
        for i in range(len(nodes)):
            if m.inside(lat[i]):
                x, y = m.xy(lon[i], lat[i])
                c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.3" fill="{INK}"/>')
        c.text(m.x + pw / 2, 24, f"Within {r} km", size=14, weight="700")
        c.text(m.x + pw / 2, 40 + m.h + 18, f"{len(near)} pairs, {hit} are real borders", size=12, fill=MUTED)
    c.text(12, 40 + m.h + 42, "Blue: the pair really shares a border. Grey: the pair is near but there is no shared border. "
           "Equirectangular projection; lines are straight on the page.", size=11.5, anchor="start", fill=MUTED)
    c.h = int(40 + m.h + 54)
    meta = dict(chapter=14,
                caption="The same 177 label points joined by distance alone, at three radii. A small radius misses most real borders and leaves most units alone; a large one joins whole regions into one dense knot.",
                alt="Three side-by-side world maps with dots at the country label points. The first, within 500 kilometres, has " +
                    f"{rows[0][1]} lines of which {rows[0][2]} are real borders. The second, within 1000 kilometres, has {rows[1][1]} lines of which {rows[1][2]} are real borders. The third, within 2000 kilometres, has {rows[2][1]} lines of which {rows[2][2]} are real borders. Real borders are drawn in blue and the rest in grey; the third map has many grey lines, most of all in Europe.",
                data={"radii_km": radii, "pairs": [r[1] for r in rows], "real_borders": [r[2] for r in rows]})
    return c, meta


FIGURES = {
    "space-border-map": border_map,
    "space-decay": decay_bars,
    "space-thresholds": threshold_panels,
}

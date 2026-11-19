"""Figures for the all-pairs chapter of the algorithms book (chapter 7).

Standard library only. Every number drawn is computed here from the tiny networks defined below, so the
pictures cannot drift from the arithmetic in the text. Also holds a few drawing helpers that the other
algorithm-book figure modules import.
"""
import math

from fig_layout import fit, stress_layout
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, PURPLE, RED, SKY, Canvas

LIGHT = "#eef6fb"
GRAY = "#9ca3af"
INF = math.inf

NAMES10 = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jo"]
KITE = [(0, 1), (0, 2), (0, 3), (0, 5), (1, 3), (1, 4), (1, 6), (2, 3), (2, 5), (3, 4),
        (3, 5), (3, 6), (4, 6), (5, 6), (5, 7), (6, 7), (7, 8), (8, 9)]


# ------------------------------------------------------------------ small helpers (shared by the other modules)
def adjacency(n, edges, directed=False):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        if not directed:
            adj[b].append(a)
    return adj


def bfs_dist(n, edges, s, directed=False):
    adj = adjacency(n, edges, directed)
    d = [INF] * n
    d[s] = 0
    q = [s]
    for u in q:
        for v in adj[u]:
            if d[v] == INF:
                d[v] = d[u] + 1
                q.append(v)
    return d


def all_bfs(n, edges, directed=False):
    return [bfs_dist(n, edges, s, directed) for s in range(n)]


def kite_pos(x0=30, y0=30, w=520, h=300):
    return fit(stress_layout(10, KITE, seed=3), x0, y0, w, h)


def draw_graph(c, pos, edges, labels, r=20, fills=None, strokes=None, ecolor=None, ewidth=None, edash=None,
               directed=False, size=12, shapes=None, curves=None, elabels=None, lab_fill=INK):
    """Draw ties then dots. fills/strokes: per node; ecolor/ewidth/edash: per tie (dict by index or list)."""
    for k, (a, b) in enumerate(edges):
        col = (ecolor or {}).get(k, GRAY) if isinstance(ecolor, dict) else (ecolor[k] if ecolor else GRAY)
        wid = (ewidth or {}).get(k, 2) if isinstance(ewidth, dict) else (ewidth[k] if ewidth else 2)
        dsh = (edash or {}).get(k) if isinstance(edash, dict) else (edash[k] if edash else None)
        cv = (curves or {}).get(k, 0)
        lab = (elabels or {}).get(k) if elabels else None
        c.edge(pos[a], pos[b], ra=r, rb=r, directed=directed, color=col, width=wid, dash=dsh, curve=cv, label=lab)
    for i, p in enumerate(pos):
        c.node(p[0], p[1], labels[i], r=r, fill=(fills[i] if fills else LIGHT),
               stroke=(strokes[i] if strokes else BLUE), size=size, shape=(shapes[i] if shapes else "circle"),
               label_fill=lab_fill)


def table(c, x, y, cell, rows, header_rows, header_cols, fills=None, bolds=None, size=13, hsize=12,
          corner="", colfill=None):
    """A grid of text cells. rows: list of lists of strings. fills: dict (i, j) -> color."""
    nr, nc = len(rows), len(rows[0])
    for j, h in enumerate(header_cols):
        c.text(x + (j + 1) * cell + cell / 2, y + cell * 0.62, h, size=hsize, weight="600", fill=MUTED)
    for i, h in enumerate(header_rows):
        c.text(x + cell * 0.9, y + (i + 1) * cell + cell * 0.62, h, size=hsize, weight="600", fill=MUTED, anchor="end")
    if corner:
        c.text(x + cell * 0.9, y + cell * 0.62, corner, size=hsize - 1, fill=MUTED, anchor="end")
    for i in range(nr):
        for j in range(nc):
            cx, cy = x + (j + 1) * cell, y + (i + 1) * cell
            fill = (fills or {}).get((i, j), PAPER)
            c.rect(cx, cy, cell, cell, fill=fill, stroke=FAINT, sw=1)
            bold = (bolds or {}).get((i, j), False)
            c.text(cx + cell / 2, cy + cell * 0.64, rows[i][j], size=size, weight="700" if bold else "400")


def fmt(v):
    return "∞" if v == INF else (str(int(v)) if float(v).is_integer() else f"{v:.1f}")


# ------------------------------------------------------------------ the small examples
FIVE = ["Ana", "Ben", "Cleo", "Dev", "Eli"]
FIVE_EDGES = [(0, 1), (1, 2), (1, 3), (2, 3), (3, 4)]
FIVE_POS = [(70, 150), (190, 150), (290, 80), (290, 220), (410, 150)]

# travel minutes between five meeting places (used for Floyd-Warshall by hand)
RIDE = [(0, 1, 9), (0, 2, 2), (2, 3, 3), (3, 1, 1), (3, 4, 6), (1, 4, 8)]


def floyd_warshall(n, wedges, directed=False):
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for a, b, w in wedges:
        d[a][b] = min(d[a][b], w)
        if not directed:
            d[b][a] = min(d[b][a], w)
    tables = [[row[:] for row in d]]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
        tables.append([row[:] for row in d])
    return tables


def bellman_ford_all(n, wedges, directed=True):
    """Reference: single-source distances by Bellman-Ford from each person (used as a check)."""
    out = []
    for s in range(n):
        d = [INF] * n
        d[s] = 0
        for _ in range(n):
            for a, b, w in wedges:
                if d[a] + w < d[b]:
                    d[b] = d[a] + w
                if not directed and d[b] + w < d[a]:
                    d[a] = d[b] + w
        out.append(d)
    return out


# ------------------------------------------------------------------ figures
def all_pairs_table():
    n = 10
    D = all_bfs(n, KITE)
    ecc = [max(r) for r in D]
    diam, rad = max(ecc), min(ecc)
    pairs = [D[i][j] for i in range(n) for j in range(n) if i != j]
    mean = sum(pairs) / len(pairs)
    c = Canvas(760, 470, "The distance table for the ten-person friendship network",
               "A ten by ten grid of distances with each person's largest distance in a column on the right.")
    cell = 38
    rows = [[str(int(v)) for v in r] + [str(int(e))] for r, e in zip(D, ecc)]
    fills = {}
    bolds = {}
    shade = {0: PAPER, 1: "#e4f1f9", 2: "#c6e2f3", 3: "#9fd0ec", 4: "#f6c28a"}
    for i in range(n):
        for j in range(n):
            fills[(i, j)] = shade[int(D[i][j])]
            if D[i][j] == diam:
                bolds[(i, j)] = True
        fills[(i, n)] = ORANGE + "55" if ecc[i] == diam else (GREEN + "44" if ecc[i] == rad else PAPER)
        bolds[(i, n)] = True
    table(c, 30, 20, cell, rows, NAMES10, NAMES10 + ["Ecc."], fills=fills, bolds=bolds, size=14, hsize=11.5)
    c.text(30 + 12 * cell + 14, 20 + cell * 1.6, "Diameter", size=13, anchor="start", weight="700", fill=ORANGE)
    c.text(30 + 12 * cell + 14, 20 + cell * 1.6 + 18, f"= biggest entry = {diam}", size=12, anchor="start", fill=MUTED)
    c.text(30 + 12 * cell + 14, 20 + cell * 4.0, "Radius", size=13, anchor="start", weight="700", fill=GREEN)
    c.text(30 + 12 * cell + 14, 20 + cell * 4.0 + 18, f"= smallest Ecc. = {rad}", size=12, anchor="start", fill=MUTED)
    c.text(30 + 12 * cell + 14, 20 + cell * 6.4, "Mean distance", size=13, anchor="start", weight="700", fill=BLUE)
    c.text(30 + 12 * cell + 14, 20 + cell * 6.4 + 18, f"= average of all", size=12, anchor="start", fill=MUTED)
    c.text(30 + 12 * cell + 14, 20 + cell * 6.4 + 34, f"90 off-diagonal = {mean:.3f}", size=12, anchor="start", fill=MUTED)
    meta = dict(chapter=7,
                caption=f"Every distance at once. The darkest entries (orange) are the diameter, {diam}. The right-hand column is each person's eccentricity: their distance to whoever is farthest. The mean of the 90 off-diagonal entries is {mean:.3f}.",
                alt=f"A ten by ten table of distances between the ten friends. The diagonal is zero, and every entry is between 1 and {diam}. The entries equal to {diam} are shaded orange and sit in the rows and columns of Jo and of Ana, Ben, Cleo, Dev and Eli. A right-hand column lists each person's largest distance.",
                data={"names": NAMES10, "distances": D, "eccentricity": ecc, "mean": round(mean, 4)})
    return c, meta


def repeated_search():
    n = 5
    D = all_bfs(n, FIVE_EDGES)
    cols = [ORANGE, SKY, GREEN, PURPLE, RED]
    c = Canvas(920, 520, "Repeated search fills the table one row at a time",
               "Five small copies of a five-person network, each with a search from a different person, above the table those searches fill.")
    for s in range(n):
        ox = 20 + s * 178
        pos = [(ox + 14 + (x - 70) * 0.34, 70 + (y - 150) * 0.42) for x, y in FIVE_POS]
        c.rect(ox - 4, 18, 168, 134, fill=cols[s] + "12", stroke=cols[s], sw=1.4, rx=8)
        c.text(ox + 80, 38, f"Search {s + 1}: start at {FIVE[s]}", size=12.5, weight="700", fill=INK)
        fills = [cols[s] + "88" if i == s else LIGHT for i in range(n)]
        draw_graph(c, [(x + 6, y + 28) for x, y in pos], FIVE_EDGES, [str(int(D[s][i])) for i in range(n)], r=13,
                   fills=fills, strokes=[cols[s]] * n, size=11)
    cell = 52
    rows = [[str(int(v)) for v in r] for r in D]
    fills = {(i, j): cols[i] + "44" for i in range(n) for j in range(n)}
    table(c, 170, 180, cell, rows, [f"{FIVE[i]} (search {i + 1})" for i in range(n)], FIVE, fills=fills, size=16, hsize=12.5)
    c.lines(600, 300, ["Each search costs about one", "look at every person and tie.", "", "Do it from everyone and the", "work is that, times n."], size=14, fill=MUTED)
    meta = dict(chapter=7,
                caption="Repeated search. One breadth-first search from each person gives one row of the table. Five people, five searches, five rows.",
                alt="Five small copies of the five-person network. In each, a different person is the starting point and every dot shows its distance from that person. Below, a five by five table whose rows are colored to match the five searches that produced them.",
                data={"distances": D})
    return c, meta


def fw_rule():
    c = Canvas(820, 330, "The Floyd-Warshall question: is the detour shorter?",
               "Three stops, Ana, Cleo and Ben, with a direct ride of 9 minutes and a detour through Cleo of 2 plus 3 minutes.")
    a, k, b = (150, 190), (410, 80), (670, 190)
    c.edge(a, b, ra=24, rb=24, color=GRAY, width=3.5, label=None)
    c.text(410, 238, "direct ride: 9 minutes", size=15, weight="600", fill=MUTED)
    c.edge(a, k, ra=24, rb=24, color=ORANGE, width=3.5)
    c.edge(k, b, ra=24, rb=24, color=ORANGE, width=3.5)
    c.text(250, 110, "2 minutes", size=15, weight="600", fill=ORANGE, anchor="middle")
    c.text(570, 110, "3 minutes", size=15, weight="600", fill=ORANGE, anchor="middle")
    for (x, y), name, fl in [(a, "Ana", LIGHT), (k, "Cleo", ORANGE + "55"), (b, "Ben", LIGHT)]:
        c.node(x, y, name, r=24, fill=fl, stroke=BLUE if fl == LIGHT else ORANGE, size=12)
    c.text(410, 40, "Allow Cleo as a stopover", size=16, weight="700")
    c.text(410, 282, "2 + 3 = 5 is less than 9, so Ana to Ben becomes 5.", size=15, weight="700", fill=INK)
    c.text(410, 308, "The rule: new d(i, j) = the smaller of d(i, j) and d(i, k) + d(k, j).", size=13.5, fill=MUTED)
    meta = dict(chapter=7,
                caption="The one move that Floyd-Warshall repeats. For a pair of people and one allowed stopover, keep whichever is shorter: the best known ride, or the two rides joined at the stopover.",
                alt="Three dots in a triangle: Ana at the left, Ben at the right and Cleo above between them. A gray line from Ana to Ben is labeled 9 minutes. Two orange lines, Ana to Cleo at 2 minutes and Cleo to Ben at 3 minutes, are the detour. The text says 2 plus 3 is 5, which beats 9.",
                data={"direct": 9, "detour": [2, 3]})
    return c, meta


def fw_stopovers():
    n = 5
    T = floyd_warshall(n, RIDE)
    ref = bellman_ford_all(n, RIDE, directed=False)
    assert T[-1] == ref, "Floyd-Warshall disagrees with the reference"
    c = Canvas(960, 640, "Floyd-Warshall, allowing one more stopover at a time",
               "Six small distance tables for five people: no stopovers, then Ana, Ben, Cleo, Dev and Eli allowed one at a time, with changed cells highlighted.")
    # the little map
    pos = [(60, 60), (200, 90), (80, 150), (200, 150), (140, 210)]
    cell = 34
    titles = ["No stopovers: only direct rides"] + [f"Stopover {FIVE[k]} allowed" for k in range(n)]
    allowed = ["nobody"] + ["Ana", "Ana, Ben", "Ana, Ben, Cleo", "Ana, Ben, Cleo, Dev", "everyone"]
    for t in range(6):
        ox, oy = 20 + (t % 3) * 315, 20 + (t // 3) * 305
        c.rect(ox, oy, 300, 290, fill="none", stroke=FAINT, sw=1, rx=8)
        c.text(ox + 12, oy + 24, titles[t], size=13.5, weight="700", anchor="start")
        c.text(ox + 12, oy + 42, f"may stop at: {allowed[t]}", size=11.5, anchor="start", fill=MUTED)
        rows = [[fmt(v) for v in r] for r in T[t]]
        fills, bolds = {}, {}
        if t > 0:
            for i in range(n):
                for j in range(n):
                    if T[t][i][j] != T[t - 1][i][j]:
                        fills[(i, j)] = ORANGE + "88"
                        bolds[(i, j)] = True
            kk = t - 1
            for j in range(n):
                fills.setdefault((kk, j), SKY + "44")
                fills.setdefault((j, kk), SKY + "44")
        table(c, ox + 22, oy + 50, cell, rows, FIVE, FIVE, fills=fills, bolds=bolds, size=13, hsize=10.5)
        changed = sum(1 for i in range(n) for j in range(n) if t and T[t][i][j] != T[t - 1][i][j])
        c.text(ox + 12, oy + 282, "start: the ties as written" if t == 0 else f"{changed} cells improved this step", size=11.5, anchor="start", fill=MUTED)
    meta = dict(chapter=7,
                caption="Floyd-Warshall on five places and travel minutes. Each step allows one more person as a stopover and rewrites any cell that the new stopover improves (orange). The blue row and column belong to the stopover being added. After the fifth step the table is final.",
                alt="Six five by five tables of travel minutes. The first holds only the direct rides, with infinity where there is no direct ride. Each next table allows one more stopover, in the order Ana, Ben, Cleo, Dev, Eli, and highlights cells that got smaller. The last table has no infinity left and every entry is a shortest travel time.",
                data={"ride_edges": [list(e) for e in RIDE], "tables": [[[None if v == INF else v for v in r] for r in t] for t in T]})
    return c, meta


def johnson_reweight():
    names = ["Ana", "Ben", "Cleo", "Dev"]
    arcs = [(0, 1, 4), (0, 2, 5), (1, 2, -2), (2, 3, 3), (1, 3, 6)]
    n = 4
    h = [0.0] * n  # distances from a helper person tied to everyone at cost 0
    for _ in range(n + 1):
        for a, b, w in arcs:
            if h[a] + w < h[b]:
                h[b] = h[a] + w
    new = [(a, b, w + h[a] - h[b]) for a, b, w in arcs]
    assert all(w >= 0 for _, _, w in new)
    pos = [(70, 140), (200, 70), (200, 210), (330, 140)]
    c = Canvas(860, 330, "Johnson's trick: make every cost non-negative",
               "The same four-person network twice. Left: ties with one negative cost. Right: every cost shifted by the people's scores so none is negative.")
    for side, (ox, ws, ttl) in enumerate([(10, [w for _, _, w in arcs], "Before: one negative cost"),
                                          (440, [w for _, _, w in new], "After: costs shifted, none negative")]):
        c.text(ox + 190, 28, ttl, size=15, weight="700")
        p = [(x + ox, y + 20) for x, y in pos]
        for k, (a, b, _) in enumerate(arcs):
            bad = ws[k] < 0
            col = RED if bad else GRAY
            cv = 0
            c.edge(p[a], p[b], ra=20, rb=20, directed=True, color=col, width=2.6, curve=cv)
            mx, my = (p[a][0] + p[b][0]) / 2, (p[a][1] + p[b][1]) / 2
            off = -14 if k in (0,) else 16
            dx = 16 if k == 2 else 0
            c.text(mx + dx, my + (5 if k == 2 else off), fmt(ws[k]), size=14, weight="700", fill=RED if bad else INK)
        for i in range(n):
            c.node(p[i][0], p[i][1], names[i], r=20, fill=LIGHT, stroke=BLUE, size=11)
            if side == 1:
                c.text(p[i][0] + (48 if i == 1 else 0), p[i][1] + (4 if i == 1 else 38), f"score {fmt(h[i])}", size=11.5, fill=MUTED)
    c.text(430, 316, "new cost = old cost + score of where it starts − score of where it ends; every route between two people shifts by the same amount.", size=12, fill=MUTED)
    meta = dict(chapter=7,
                caption="Johnson's reweighting. Each person gets a score (the cheapest way to reach them from a helper tied to everyone at cost 0). Adding the starting score and subtracting the ending score to each cost removes the negative cost, and every route between the same two people shifts by the same amount.",
                alt="Two copies of a four-person directed network. On the left the tie from Ben to Cleo costs minus 2 and is drawn in red. On the right every cost has been adjusted using scores of 0, 0, minus 2 and 0 for Ana, Ben, Cleo and Dev, so all costs are zero or more.",
                data={"arcs": [list(a) for a in arcs], "scores": h, "new_costs": [w for _, _, w in new]})
    return c, meta


def apsp_costs():
    cases = [("1,000 people, 5,000 ties", 1000, 5000), ("1,000 people, 100,000 ties", 1000, 100000),
             ("10,000 people, 50,000 ties", 10000, 50000), ("100,000 people, 500,000 ties", 100000, 500000)]
    methods = [("Repeated search (no weights)", BLUE, lambda n, m: n * (n + m)),
               ("Johnson (weights, even negative)", GREEN, lambda n, m: n * m + n * (m + n * math.log2(n))),
               ("Floyd-Warshall", ORANGE, lambda n, m: n ** 3)]
    c = Canvas(900, 520, "Rough work for filling the whole table",
               "Horizontal bars on a log scale for three methods across four network sizes.")
    x0, w = 270, 570
    lo, hi = 6, 16.5
    sx = lambda v: x0 + (math.log10(v) - lo) / (hi - lo) * w
    top = 34
    for ci, (name, n, m) in enumerate(cases):
        y = top + ci * 118
        c.text(x0 - 14, y + 44, name, size=13, anchor="end", weight="600")
        for mi, (mname, col, fn) in enumerate(methods):
            v = fn(n, m)
            yy = y + mi * 30
            c.rect(x0, yy + 4, sx(v) - x0, 22, fill=col + "55", stroke=col, sw=1.2)
            c.text(sx(v) + 8, yy + 20, f"{v:.0e}".replace("e+0", "e").replace("e+", "e") + " steps", size=11.5, anchor="start", fill=INK)
    for e in range(6, 17, 2):
        c.text(sx(10 ** e), 506, f"10^{e}", size=11, fill=MUTED)
    for mi, (mname, col, _) in enumerate(methods):
        c.rect(x0 + mi * 200 - 70, 8, 14, 14, fill=col + "55", stroke=col, sw=1.2)
        c.text(x0 + mi * 200 - 52, 20, mname.split(" (")[0], size=12, anchor="start", fill=INK)
    meta = dict(chapter=7,
                caption="Rough counts of basic steps (not seconds) to fill the whole table. Floyd-Warshall pays for every triple of people no matter how few ties there are. Repeated search and Johnson pay in proportion to the ties.",
                alt="Four groups of three horizontal bars on a log scale, one group per network size. In every group the Floyd-Warshall bar is longest. For the sparse networks the other two bars are two to three powers of ten shorter. For the 1,000 person network with 100,000 ties the three bars are closer together.",
                data={"cases": [[a, b, c2] for a, b, c2 in cases]})
    return c, meta


def apsp_memory():
    ns = [1000, 10000, 100000, 1000000]
    unit = ["MB", "GB", "TB", "TB"]
    byts = [n * n * 4 for n in ns]
    labels = ["1,000 people", "10,000 people", "100,000 people", "1,000,000 people"]
    texts = ["4 megabytes: a photo", "400 megabytes: a laptop copes", "40 gigabytes: a big server", "4 terabytes: a data center"]
    c = Canvas(860, 330, "The table itself is the problem at scale",
               "Horizontal bars on a log scale: memory for a full distance table at four network sizes.")
    x0, w = 200, 560
    lo, hi = 6, 13
    sx = lambda v: x0 + (math.log10(v) - lo) / (hi - lo) * w
    for i, (b, lab, t) in enumerate(zip(byts, labels, texts)):
        y = 30 + i * 62
        c.text(x0 - 12, y + 24, lab, size=13, anchor="end", weight="600")
        col = BLUE if b < 1e10 else RED
        c.rect(x0, y + 6, sx(b) - x0, 28, fill=col + "55", stroke=col, sw=1.2)
        c.text(sx(b) + 8, y + 25, t, size=12.5, anchor="start")
    for e in (6, 8, 10, 12):
        c.text(sx(10 ** e), 300, f"10^{e} bytes", size=11, fill=MUTED)
    meta = dict(chapter=7,
                caption="Memory for a full distance table at 4 bytes per entry. Ten times more people means a hundred times more table, which is why very large networks answer distance questions without ever writing the whole table down.",
                alt="Four horizontal bars on a log scale. Each is a hundred times longer than the one above: 4 megabytes for a thousand people, 400 megabytes for ten thousand, 40 gigabytes for a hundred thousand and 4 terabytes for a million. The last two are drawn in red.",
                data={"people": ns, "bytes": byts})
    return c, meta


def eccentricity_center():
    n = 10
    D = all_bfs(n, KITE)
    ecc = [max(r) for r in D]
    rad, diam = min(ecc), max(ecc)
    pos = kite_pos(20, 60, 470, 280)
    col = {rad: GREEN, diam: ORANGE}
    fills = [col.get(e, SKY) + "66" for e in ecc]
    strokes = [col.get(e, BLUE) for e in ecc]
    shapes = ["square" if e == rad else "circle" for e in ecc]
    c = Canvas(900, 380, "Center and edge of the friendship network",
               "The ten-person network with people colored by eccentricity, next to a bar for each person's eccentricity.")
    draw_graph(c, pos, KITE, [f"{NAMES10[i]}" for i in range(n)], r=19, fills=fills, strokes=strokes, shapes=shapes, size=10.5)
    c.text(255, 24, "Green squares: the center. Orange circles: the far edge.", size=13, weight="600")
    order = sorted(range(n), key=lambda i: (ecc[i], NAMES10[i]))
    for k, i in enumerate(order):
        y = 60 + k * 29
        c.text(620, y + 17, NAMES10[i], size=12.5, anchor="end")
        cc = col.get(ecc[i], BLUE)
        c.rect(630, y + 3, ecc[i] * 50, 20, fill=cc + "55", stroke=cc, sw=1.2)
        c.text(630 + ecc[i] * 50 + 8, y + 18, str(ecc[i]), size=12, anchor="start", fill=MUTED)
    c.text(730, 46, "Eccentricity", size=12.5, weight="700", fill=INK)
    meta = dict(chapter=7,
                caption=f"Eccentricity is a person's distance to whoever is farthest from them. The people with the smallest value (radius {rad}) form the center; those with the largest (diameter {diam}) sit on the edge.",
                alt=f"On the left, the ten-person network. Hana, with eccentricity {rad}, is the one green square. Ana, Ben, Cleo, Dev, Eli and Jo, with eccentricity {diam}, are orange circles; Fay, Gus and Ivo, at 3, are blue circles. On the right, ten horizontal bars sorted by eccentricity.",
                data={"eccentricity": dict(zip(NAMES10, ecc)), "radius": rad, "diameter": diam})
    return c, meta


def unreachable_trap():
    names = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay"]
    edges = [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5)]
    n = 6
    D = all_bfs(n, edges)
    reach = [(i, j) for i in range(n) for j in range(n) if i != j and D[i][j] != INF]
    mean_reach = sum(D[i][j] for i, j in reach) / len(reach)
    harm = sum(1 / D[i][j] for i in range(n) for j in range(n) if i != j and D[i][j] != INF) / (n * (n - 1))
    pos = [(70, 80), (170, 40), (170, 130), (300, 80), (400, 40), (400, 130)]
    pos = [(x, y + 40) for x, y in pos]
    c = Canvas(900, 330, "When some people cannot reach each other",
               "Two separate groups of three, the distance table with infinity between groups, and three ways to summarize it.")
    draw_graph(c, pos, edges, names, r=19, size=11)
    c.text(235, 30, "Two groups, no tie between them", size=14, weight="700")
    rows = [[fmt(v) for v in r] for r in D]
    fills = {(i, j): ORANGE + "44" for i in range(n) for j in range(n) if D[i][j] == INF}
    table(c, 490, 8, 34, rows, names, names, fills=fills, size=13, hsize=10.5)
    c.text(40, 262, f"Average over pairs that can reach each other: {mean_reach:.2f}", size=13.5, anchor="start", weight="600")
    c.text(40, 284, "Looks like a tight network. It leaves out 18 of 30 pairs.", size=12.5, anchor="start", fill=MUTED)
    c.text(40, 310, f"Average of 1 over distance, counting unreachable as 0: {harm:.2f}  (the efficiency)", size=13.5, anchor="start", weight="600")
    meta = dict(chapter=7,
                caption="A network in two pieces. Averaging only the pairs that can reach each other gives a small, friendly number and hides that 18 of the 30 ordered pairs cannot reach each other at all. Report how many pairs are cut off, or use a measure that counts them.",
                alt="Two groups of three people each, tied within the group and not between groups. Beside them, a six by six table of distances: the two three by three blocks along the diagonal hold 0, 1 and 2, and the rest is infinity, shaded orange. Below, two averages: 1.17 over reachable pairs, and 0.37 when unreachable pairs count as zero efficiency.",
                data={"mean_reachable": round(mean_reach, 4), "efficiency": round(harm, 4), "unreachable_pairs": 18})
    return c, meta


FIGURES = {
    "all-pairs-table": all_pairs_table, "repeated-search": repeated_search, "fw-rule": fw_rule,
    "fw-stopovers": fw_stopovers, "johnson-reweight": johnson_reweight, "apsp-costs": apsp_costs,
    "apsp-memory": apsp_memory, "eccentricity-center": eccentricity_center, "unreachable-trap": unreachable_trap,
}

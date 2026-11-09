"""Figures for the two-mode chapter (chapter 11).

Standard library only. Every number drawn is computed here from the southern women CSV
in books/sna/data, or from the small invented table at the top of the town-hall figure.
"""
import csv
import math
from pathlib import Path

from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, Canvas, ring

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"
WOMEN = ["Evelyn", "Laura", "Theresa", "Brenda", "Charlotte", "Frances", "Eleanor", "Pearl", "Ruth",
         "Verne", "Myra", "Katherine", "Sylvia", "Nora", "Helen", "Dorothy", "Olive", "Flora"]
GRAY = "#9ca3af"

# An invented table, used only to show how one big event reshapes a projection.
TOWN_PEOPLE = ["Ana", "Ben", "Cleo", "Dev", "Esi", "Finn", "Gus", "Hana"]
TOWN_EVENTS = {"Choir": ["Ana", "Ben", "Cleo"], "Chess": ["Cleo", "Dev"], "Quiz": ["Esi", "Finn", "Gus"],
               "Garden": ["Gus", "Hana"], "Town hall": TOWN_PEOPLE}


def _mix(hex_color, t):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(round(255 + (v - 255) * t) for v in (r, g, b))


def attendance():
    with open(DATA / "southern_women" / "edges.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    labels = list(dict.fromkeys(r["woman"] for r in rows))
    attended = [set() for _ in labels]
    for r in rows:
        attended[labels.index(r["woman"])].add(int(r["event"][1:]) - 1)
    return attended


def shared_counts(attended):
    n = len(attended)
    return {(i, j): len(attended[i] & attended[j]) for i in range(n) for j in range(i + 1, n)
            if attended[i] & attended[j]}


def southern_bipartite():
    att = attendance()
    sizes = [sum(e in a for a in att) for e in range(14)]
    c = Canvas(760, 600, "The southern women as a two-mode network",
               "Eighteen women in a left column and fourteen events in a right column, with a line for each of the 89 attendances. The lines of the biggest event, event 8, are drawn in orange.")
    xl, xr, top, step_w, step_e = 150, 610, 60, 28, 36
    wy = [top + i * step_w for i in range(18)]
    ey = [top + 5 + i * step_e for i in range(14)]
    for i, a in enumerate(att):
        for e in sorted(a):
            if e != 7:
                c.add(f'<line x1="{xl + 8}" y1="{wy[i]}" x2="{xr - 12}" y2="{ey[e]}" stroke="{GRAY}" stroke-width="1.1" opacity="0.7"/>')
    for i, a in enumerate(att):
        if 7 in a:
            c.add(f'<line x1="{xl + 8}" y1="{wy[i]}" x2="{xr - 12}" y2="{ey[7]}" stroke="{ORANGE}" stroke-width="2"/>')
    for i, name in enumerate(WOMEN):
        c.add(f'<circle cx="{xl}" cy="{wy[i]}" r="7" fill="#cfe5f3" stroke="{BLUE}" stroke-width="2"/>')
        c.text(xl - 14, wy[i] + 4, name, size=12, anchor="end")
    for e in range(14):
        col = ORANGE if e == 7 else BLUE
        c.add(f'<rect x="{xr - 8}" y="{ey[e] - 8}" width="16" height="16" rx="2" fill="{"#fdf3dc" if e == 7 else "#cfe5f3"}" stroke="{col}" stroke-width="2"/>')
        c.text(xr + 16, ey[e] + 4, f"Event {e + 1} ({sizes[e]})", size=12, anchor="start", weight="700" if e == 7 else "400")
    c.text(xl, 30, "Women (circles)", size=13, weight="700", fill=BLUE)
    c.text(xr, 30, "Events (squares), with attendance", size=13, weight="700", fill=BLUE)
    c.text(380, 580, "No line joins two women or two events. Event 8 (orange) drew 14 of the 18 women.", size=12.5, fill=MUTED)
    meta = dict(chapter=11,
                caption="The southern women as a two-mode network: 18 women on the left, 14 events on the right, one line for each of the 89 attendances. Every line runs between the two columns, never within one. The lines of event 8, the biggest, are orange.",
                alt="Eighteen women in a left column and fourteen events in a right column, joined by 89 lines. Event 8 has 14 lines, drawn in orange, and event 9 has 12. The first women connect mostly to events 1 to 9 and the last women mostly to events 7 to 14. No line joins two women or two events.",
                data={"attended": [sorted(a) for a in att], "event_sizes": sizes})
    return c, meta


def incidence_heatmap():
    att = attendance()
    n, m, cell = 18, 14, 22
    x0, y0 = 120, 70
    c = Canvas(720, 540, "The incidence matrix of the southern women",
               "A grid with a row for each of 18 women and a column for each of 14 events. A blue cell means she attended. Totals for each row and column are printed on the margins.")
    for j in range(m):
        c.text(x0 + j * cell + cell / 2, y0 - 8, str(j + 1), size=11, fill=MUTED)
    for i in range(n):
        c.text(x0 - 8, y0 + i * cell + 15, WOMEN[i], size=11.5, anchor="end")
        for j in range(m):
            on = j in att[i]
            c.rect(x0 + j * cell, y0 + i * cell, cell, cell, fill=BLUE if on else PAPER, stroke="#e5e7eb", sw=0.8)
        c.text(x0 + m * cell + 14, y0 + i * cell + 15, str(len(att[i])), size=12, weight="700", anchor="middle")
    sizes = [sum(e in a for a in att) for e in range(m)]
    for j in range(m):
        big = sizes[j] >= 12
        c.text(x0 + j * cell + cell / 2, y0 + n * cell + 18, str(sizes[j]), size=12, weight="700", fill=ORANGE if big else INK)
    c.text(x0 + m * cell + 16, y0 - 8, "total", size=11.5, fill=MUTED)
    c.text(x0 - 8, y0 + n * cell + 18, "women at event", size=11.5, anchor="end", fill=MUTED)
    c.text(x0 + m * cell / 2, y0 - 36, "Event number", size=12.5, weight="600")
    c.text(360, 520, "Row totals are the women's degrees (2 to 8). Column totals are the events' degrees (3 to 14).", size=12.5, fill=MUTED)
    meta = dict(chapter=11,
                caption="The incidence matrix as a picture. A blue cell means the woman (row) attended the event (column). The numbers on the right are row totals, the number of events each woman attended; the numbers underneath are column totals, the number of women at each event.",
                alt="A grid of 18 rows, one for each woman, and 14 columns, one for each event, with 89 blue cells. Row totals on the right run from 2 to 8. Column totals underneath are 3, 3, 6, 4, 8, 8, 10, 14, 12, 5, 4, 6, 3, 3, with the 14 and the 12 for events 8 and 9 in orange. Blue cells run in a band from the upper left to the lower right.",
                data={"row_totals": [len(a) for a in att], "column_totals": sizes})
    return c, meta


def projection_network():
    att = attendance()
    shared = shared_counts(att)
    c = Canvas(900, 470, "Projecting the women: every tie, and only the strong ones",
               "Two rings of the same 18 women. On the left, a line for every pair that shared at least one event. On the right, only the pairs that shared four or more.")
    for k, (cx, title, cut) in enumerate([(230, "All pairs that shared an event", 1), (670, "Only pairs that shared 4 or more", 4)]):
        pos = ring(cx, 250, 150, 18)
        c.text(cx, 36, title, size=14, weight="700")
        for (i, j), w in sorted(shared.items(), key=lambda kv: kv[1]):
            if w >= cut:
                c.edge(pos[i], pos[j], ra=6, rb=6, width=0.6 + 0.55 * w if k else 0.5 + 0.2 * w,
                       color=BLUE if k else GRAY, opacity=0.9 if k else 0.45)
        for i, p in enumerate(pos):
            col = BLUE if i < 9 else ORANGE
            c.add(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="6" fill="{"#cfe5f3" if i < 9 else "#fdf3dc"}" stroke="{col}" stroke-width="2"/>')
            ang = math.radians(-90 + 360 * i / 18)
            lx, ly = cx + 168 * math.cos(ang), 250 + 168 * math.sin(ang)
            anchor = "start" if math.cos(ang) > 0.2 else ("end" if math.cos(ang) < -0.2 else "middle")
            c.text(lx, ly + 4, WOMEN[i], size=11, anchor=anchor)
    all_n = len(shared)
    strong = sum(w >= 4 for w in shared.values())
    c.text(230, 450, f"{all_n} ties (91% of the 153 possible pairs)", size=12.5, fill=MUTED)
    c.text(670, 450, f"{strong} ties; line width grows with the count", size=12.5, fill=MUTED)
    meta = dict(chapter=11,
                caption=f"The projection onto the women, drawn two ways. Left: every pair that shared at least one event, {all_n} of the 153 possible pairs, a hairball. Right: only the {strong} pairs that shared four or more events, where two groups of women (the first nine listed, in blue, and the last nine, in orange) become visible: none of the strong ties crosses between them.",
                alt=f"Two rings of the same 18 women, with the first nine in blue and the last nine in orange. The left ring has {all_n} gray lines, so many that individual ties cannot be told apart. The right ring has {strong} blue lines, thicker for pairs that shared more events, and every one of them joins two women of the same color. Four women, Dorothy, Olive, Flora and Pearl, have no line.",
                data={"all_ties": all_n, "strong_ties": strong})
    return c, meta


def weight_compare():
    att = attendance()
    sizes = [sum(e in a for a in att) for e in range(14)]
    pts = []
    for (i, j), w in shared_counts(att).items():
        newman = sum(1 / (sizes[e] - 1) for e in att[i] & att[j])
        pts.append((w, newman, i, j))
    c = Canvas(720, 490, "Two weightings of the same 139 pairs",
               "A scatter plot of plain shared-event counts against Newman weights for the 139 pairs of women who share at least one event.")
    x0, y0, w, h = 90, 390, 580, 300
    xmax, ymax = 7.5, 2.0
    for t in range(0, 8):
        x = x0 + t / xmax * w
        c.add(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y0 - h}" stroke="#eef0f3" stroke-width="1"/>')
        c.text(x, y0 + 20, str(t), size=12, fill=MUTED)
    for t in (0, 0.5, 1.0, 1.5, 2.0):
        y = y0 - t / ymax * h
        c.add(f'<line x1="{x0}" y1="{y}" x2="{x0 + w}" y2="{y}" stroke="#eef0f3" stroke-width="1"/>')
        c.text(x0 - 10, y + 4, f"{t:.1f}", size=12, fill=MUTED, anchor="end")
    c.text(x0 + w / 2, y0 + 42, "Shared events (plain count)", size=13, weight="600")
    c.add(f'<text transform="translate(26 {y0 - h / 2}) rotate(-90)" text-anchor="middle" font-size="13" font-weight="600" fill="{INK}">Newman weight</text>')
    lo3 = min(p[1] for p in pts if p[0] == 3)
    hi3 = max(p[1] for p in pts if p[0] == 3)
    top_count = max(pts)
    top_newman = max(pts, key=lambda p: p[1])
    for wcount, nw, i, j in pts:
        x, y = x0 + wcount / xmax * w, y0 - nw / ymax * h
        hi = (wcount, nw, i, j) in (top_count, top_newman)
        c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5.5 if hi else 4}" fill="{ORANGE if hi else BLUE}" fill-opacity="{0.9 if hi else 0.35}" stroke="{ORANGE if hi else BLUE}" stroke-width="1.2"/>')
    for p, dx, dy, anchor in [(top_count, 0, -14, "middle"), (top_newman, -12, -4, "end")]:
        x, y = x0 + p[0] / xmax * w, y0 - p[1] / ymax * h
        c.text(x + dx, y + dy, f"{WOMEN[p[2]]} and {WOMEN[p[3]]}", size=12, anchor=anchor, weight="700", fill=ORANGE)
    c.text(360, 478, "More shared events tends to mean a higher Newman weight, but not in lockstep.", size=12.5, fill=MUTED)
    meta = dict(chapter=11,
                caption=f"Each dot is one of the {len(pts)} pairs of women who shared at least one event, plotted by plain count (across) and Newman weight (up). Pairs with the same count can have very different Newman weights, because small events count for more. The strongest pair under each weighting is orange.",
                alt=f"A scatter plot of {len(pts)} dots. The horizontal axis is shared events from 0 to 7 and the vertical axis is Newman weight from 0 to 2. Dots with the same count are spread vertically: pairs with 3 shared events have Newman weights from {lo3:.2f} to {hi3:.2f}. Two dots are orange and labeled: {WOMEN[top_count[2]]} and {WOMEN[top_count[3]]} at 7 shared events, and {WOMEN[top_newman[2]]} and {WOMEN[top_newman[3]]} with the highest Newman weight.",
                data={"pairs": [[p[0], round(p[1], 4), p[2], p[3]] for p in pts]})
    return c, meta


def town_hall():
    names = TOWN_PEOPLE
    ix = {n: i for i, n in enumerate(names)}

    def ties(skip):
        out = set()
        for ev, members in TOWN_EVENTS.items():
            if ev == skip:
                continue
            for a in members:
                for b in members:
                    if ix[a] < ix[b]:
                        out.add((ix[a], ix[b]))
        return out

    full, without = ties(None), ties("Town hall")
    c = Canvas(820, 400, "One big event makes a hairball (an invented example)",
               "The same eight invented people, projected twice. With the town hall that everyone attended, every pair is tied. Without it, two clusters of four appear.")
    for cx, title, edges in [(210, "With the town hall", full), (610, "Without the town hall", without)]:
        pos = ring(cx, 215, 105, 8)
        c.text(cx, 40, title, size=14, weight="700")
        for a, b in sorted(edges):
            c.edge(pos[a], pos[b], ra=14, rb=14, width=2, color=BLUE if (a, b) in without else GRAY, opacity=0.9 if (a, b) in without else 0.5)
        for i, p in enumerate(pos):
            c.node(p[0], p[1], names[i][:2], r=14, fill="#cfe5f3" if i < 4 else "#fdf3dc", stroke=BLUE if i < 4 else ORANGE, size=11)
        c.text(cx, 360, f"{len(edges)} of 28 possible pairs tied", size=13, fill=MUTED)
    c.text(410, 388, "Invented data, for illustration only.", size=12, fill=MUTED)
    meta = dict(chapter=11,
                caption="An invented example of a hairball. Eight people share four small events (choir, chess, quiz, garden) and one town hall that all of them attended. With the town hall, every one of the 28 pairs is tied. Without it, eight pairs remain, in two clusters.",
                alt=f"Two rings of the same eight people, Ana to Hana, invented for illustration. The left ring has {len(full)} lines, one for every pair. The right ring has {len(without)} blue lines forming two separate clusters: Ana, Ben, Cleo and Dev in one, Esi, Finn, Gus and Hana in the other.",
                data={"with": len(full), "without": len(without)})
    return c, meta


FIGURES = {"southern-bipartite": southern_bipartite, "incidence-heatmap": incidence_heatmap,
           "projection-network": projection_network, "weight-compare": weight_compare, "town-hall": town_hall}

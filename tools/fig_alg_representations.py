"""Figures for the representations chapter of the algorithms book (chapter 1). Standard library only.

Everything drawn is computed here from the five-person network in alg_draw.py (the arrays), so the pictures cannot
drift from the text. The CSR arrays are also what the engine returns for the same graph (data/anim/csr-build).
"""
import math

from alg_draw import (FIVE, FIVE_ADJ, FIVE_TIES, LIGHT, PALE_GREEN, PALE_ORANGE, PALE_PURPLE, PALE_RED, cells,
                      csr_of, human_bytes, net5, pill)
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, PURPLE, RED, SKY, Canvas

CH = 1


def network():
    c = Canvas(900, 270, "Five people, five ties", "The five-person network with ids and names.")
    c.text(30, 34, "Five people and the ties between them", size=16, weight="700", anchor="start")
    net5(c, 60, 70, 1.15, r=20)
    c.text(450, 70, "Computers count from zero:", size=14, anchor="start", weight="600")
    for i, n in enumerate(FIVE):
        x = 450 + i * 82
        c.node(x + 20, 112, str(i), r=18, fill=LIGHT, stroke=BLUE)
        c.text(x + 20, 150, n, size=13, fill=MUTED)
    c.text(450, 190, "The number inside each dot is the person's id. The name is a label.", size=13, anchor="start", fill=MUTED)
    c.text(450, 210, "Ties: Ana-Ben, Ben-Cleo, Ben-Dev, Cleo-Dev, Dev-Eli.", size=13, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Five people, numbered from zero. The numbers are what the computer stores; the names are for us.",
                   alt="A five-person network. Ana (0) is tied to Ben (1). Ben is tied to Cleo (2) and Dev (3), who are tied to each other, and Dev is tied to Eli (4). To the right, the five ids 0 to 4 sit above the names Ana, Ben, Cleo, Dev and Eli.",
                   data={"ties": [[FIVE[a], FIVE[b]] for a, b in FIVE_TIES]})


def ids_labels():
    c = Canvas(900, 300, "Badge numbers become positions", "A lookup table from messy ids to 0 to 4.")
    c.text(30, 34, "Real data has messy ids. We swap them for 0, 1, 2... once, at the door.", size=16, weight="700", anchor="start")
    badges = [4017, 52, 9, 3180, 77]
    c.text(120, 80, "In the file", size=13, weight="600", fill=MUTED)
    c.text(450, 80, "Lookup table (a hash map)", size=13, weight="600", fill=MUTED)
    c.text(780, 80, "In the engine", size=13, weight="600", fill=MUTED)
    for i, (b, n) in enumerate(zip(badges, FIVE)):
        y = 100 + i * 36
        c.rect(40, y, 160, 30, fill=PAPER, stroke=INK, sw=1.4, rx=4)
        c.text(120, y + 20, f"badge {b} ({n})", size=13)
        c.rect(360, y, 180, 30, fill=LIGHT, stroke=BLUE, sw=1.4, rx=4)
        c.text(450, y + 20, f"{b}  ->  {i}", size=14, weight="600")
        c.arrow((204, y + 15), (356, y + 15), color=MUTED)
        c.arrow((544, y + 15), (720, y + 15), color=MUTED)
        c.node(745, y + 15, str(i), r=13, fill=LIGHT, stroke=BLUE, size=12)
        c.text(775, y + 20, "id", size=12, anchor="start", fill=MUTED)
    c.text(450, 292, "To print results, go back the other way: position 3 means badge 3180, Dev.", size=13, fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Ids versus labels. The file may use badge numbers or usernames; the engine wants 0 to n minus 1, so a lookup table translates once on the way in and back on the way out.",
                   alt="Three columns. On the left, five badge numbers from a file: 4017 for Ana, 52 for Ben, 9 for Cleo, 3180 for Dev and 77 for Eli. In the middle, a lookup table pairing each badge number with a position 0 to 4. On the right, the five positions as numbered dots. Arrows run left to right.")


def edge_list():
    c = Canvas(900, 300, "The edge list", "Five ties written as five rows.")
    c.text(30, 34, "1. Edge list: one row per tie", size=16, weight="700", anchor="start")
    net5(c, 40, 90, 1.0, r=17, hi_edges={(1, 3)}, hi_nodes={1, 3}, size=12)
    x0, y0 = 480, 70
    c.text(x0 + 45, y0 - 6, "from", size=13, weight="600", fill=MUTED)
    c.text(x0 + 135, y0 - 6, "to", size=13, weight="600", fill=MUTED)
    for k, (a, b) in enumerate(FIVE_TIES):
        y = y0 + k * 34
        hot = (a, b) == (1, 3)
        c.rect(x0, y, 90, 30, fill=PALE_ORANGE if hot else PAPER, stroke=ORANGE if hot else INK, sw=1.6)
        c.rect(x0 + 90, y, 90, 30, fill=PALE_ORANGE if hot else PAPER, stroke=ORANGE if hot else INK, sw=1.6)
        c.text(x0 + 45, y + 21, str(a), size=15, weight="600")
        c.text(x0 + 135, y + 21, str(b), size=15, weight="600")
        c.text(x0 - 14, y + 21, f"row {k}", size=11, anchor="end", fill=MUTED)
    c.text(x0 + 200, y0 + 21 + 2 * 34, "<- Ben-Dev", size=13, anchor="start", fill=ORANGE, weight="700")
    c.text(x0, y0 + 190, "An undirected tie is written once. Order inside a row does not matter.", size=13, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="The edge list: the network as a plain list of pairs. It is the format files arrive in, and the easiest to add to.",
                   alt="The five-person network on the left with the Ben-Dev tie highlighted. On the right, a two-column table of five rows: 0 and 1, 1 and 2, 1 and 3, 2 and 3, 3 and 4. The row 1 and 3 is highlighted and labeled Ben-Dev.")


def adjacency_list():
    c = Canvas(900, 330, "The adjacency list", "A short list of neighbors for each person.")
    c.text(30, 34, "2. Adjacency list: each person keeps a list of their friends", size=16, weight="700", anchor="start")
    for i in range(5):
        y = 62 + i * 52
        c.node(70, y + 20, str(i), r=18, fill=LIGHT, stroke=BLUE)
        c.text(110, y + 25, FIVE[i], size=13, anchor="start", fill=MUTED)
        x = 220
        for j in FIVE_ADJ[i]:
            c.rect(x, y + 4, 64, 32, fill=PAPER, stroke=INK, sw=1.6, rx=4)
            c.text(x + 32, y + 25, str(j), size=15, weight="600")
            c.text(x + 32, y + 52 - 2, "", size=1)
            x += 64
            c.add(f'<line x1="{x}" y1="{y + 20}" x2="{x + 24}" y2="{y + 20}" stroke="{MUTED}" stroke-width="1.6" stroke-dasharray="4 3"/>')
            x += 24
        c.text(x - 10, y + 25, "end", size=11, anchor="start", fill=MUTED, italic=True)
        c.arrow((140, y + 20), (216, y + 20), color=MUTED)
    c.text(600, 120, "Each list lives in its own", size=13, anchor="start", fill=MUTED)
    c.text(600, 140, "little spot in memory.", size=13, anchor="start", fill=MUTED)
    c.text(600, 170, "Ben's friends: 0, 2, 3.", size=13, anchor="start", fill=INK, weight="600")
    c.text(600, 190, "Counting them means walking the list,", size=13, anchor="start", fill=MUTED)
    c.text(600, 210, "unless we also keep the length.", size=13, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="The adjacency list: every person points to a short list of their neighbors. Asking who Ben knows is now one step to Ben's list.",
                   alt="Five rows, one per person, each with a numbered dot and a name. An arrow leads from each person to a chain of boxes holding the neighbor ids: Ana 1; Ben 0, 2, 3; Cleo 1, 3; Dev 1, 2, 4; Eli 3. Each chain ends with the word end. A note on the right says each list lives in its own spot in memory.")


def csr():
    off, tgt = csr_of(FIVE_ADJ, 5)
    c = Canvas(900, 410, "Compressed sparse rows", "Two flat arrays hold the whole network.")
    c.text(30, 34, "3. Compressed sparse rows (CSR): two flat arrays", size=16, weight="700", anchor="start")
    cols = [BLUE, ORANGE, GREEN, PURPLE, RED]
    pales = [LIGHT, PALE_ORANGE, PALE_GREEN, PALE_PURPLE, PALE_RED]
    w = 48
    xo, yo = 160, 80
    c.text(xo - 14, yo + 22, "offsets", size=14, anchor="end", weight="700")
    cells(c, xo, yo, off, w=w, fills={k: pales[k] if k < 5 else PAPER for k in range(6)}, idx_label="person", size=15, bold=True)
    xt, yt = 160, 230
    c.text(xt - 14, yt + 22, "targets", size=14, anchor="end", weight="700")
    fills = {}
    for p in range(5):
        for k in range(off[p], off[p + 1]):
            fills[k] = pales[p]
    cells(c, xt, yt, tgt, w=w, fills=fills, idx_label="slot", size=15, bold=True)
    # Dev's slice: offsets[3] to offsets[4]
    d = 3
    a, b = off[d], off[d + 1]
    c.add(f'<path d="M{xt + a * w:.0f},{yt - 8} L{xt + a * w:.0f},{yt - 26} L{xt + b * w:.0f},{yt - 26} L{xt + b * w:.0f},{yt - 8}" fill="none" stroke="{PURPLE}" stroke-width="2.4"/>')
    c.add(f'<line x1="{xo + d * w + w / 2}" y1="{yo + 52}" x2="{xt + a * w}" y2="{yt - 26}" stroke="{PURPLE}" stroke-width="1.8" stroke-dasharray="4 3"/>')
    c.add(f'<line x1="{xo + (d + 1) * w + w / 2}" y1="{yo + 52}" x2="{xt + b * w}" y2="{yt - 26}" stroke="{PURPLE}" stroke-width="1.8" stroke-dasharray="4 3"/>')
    c.text(xt + a * w + (b - a) * w / 2, yt + 70, f"Dev's friends: slots {a}, {a + 1} and {b - 1}", size=13, weight="700", fill=PURPLE)
    c.text(30, 340, "Read it like this. To find Dev's (3) friends, look at offsets[3] = 6 and offsets[4] = 9.", size=14, anchor="start")
    c.text(30, 364, "Dev's friends are the slots 6, 7 and 8 of targets: 1, 2 and 4 (Ben, Cleo and Eli).", size=14, anchor="start")
    c.text(30, 388, "Dev's number of friends is 9 - 6 = 3. No searching, no counting.", size=14, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="CSR keeps the whole network in two flat lists. The first says where each person's friends start; the second holds everyone's friends one after another.",
                   alt="Two rows of numbered boxes. The top row, offsets, holds 0, 1, 4, 6, 9, 10, one box for each person plus a last one. The bottom row, targets, holds 1, 0, 2, 3, 1, 3, 1, 2, 4, 3, shaded in five colors, one color for each person's block of friends. A bracket over slots 6, 7 and 8 is labeled Dev's friends and arrows lead to it from offsets 6 and 9.",
                   data={"offsets": off, "targets": tgt})


def matrix():
    c = Canvas(900, 370, "The adjacency matrix", "A grid with a 1 where two people are tied.")
    c.text(30, 34, "4. Adjacency matrix: a grid, one cell for every pair", size=16, weight="700", anchor="start")
    x0, y0, s = 150, 90, 46
    for j in range(5):
        c.text(x0 + j * s + s / 2, y0 - 10, FIVE[j], size=12, fill=MUTED)
    for i in range(5):
        c.text(x0 - 10, y0 + i * s + s / 2 + 5, FIVE[i], size=12, anchor="end", fill=MUTED)
        for j in range(5):
            on = j in FIVE_ADJ[i]
            hot = i == 1
            c.rect(x0 + j * s, y0 + i * s, s, s, fill=(PALE_ORANGE if hot else LIGHT) if on else (PALE_ORANGE if hot else "#eceff3" if i == j else PAPER),
                   stroke=FAINT if not hot else ORANGE, sw=1.2 if not hot else 1.8)
            c.text(x0 + j * s + s / 2, y0 + i * s + s / 2 + 6, "1" if on else "0", size=16, weight="700" if on else "400",
                   fill=INK if on else MUTED)
    c.text(x0 + 5 * s + 20, y0 + 20, "Ben's row (orange)", size=13, anchor="start", fill=ORANGE, weight="700")
    c.text(x0 + 5 * s + 20, y0 + 40, "says who Ben knows:", size=13, anchor="start", fill=MUTED)
    c.text(x0 + 5 * s + 20, y0 + 60, "Ana, Cleo and Dev.", size=13, anchor="start", fill=MUTED)
    c.text(x0 + 5 * s + 20, y0 + 110, "Undirected: the grid is a mirror", size=13, anchor="start", fill=MUTED)
    c.text(x0 + 5 * s + 20, y0 + 130, "image of itself across the gray", size=13, anchor="start", fill=MUTED)
    c.text(x0 + 5 * s + 20, y0 + 150, "diagonal (Ana-Ben and Ben-Ana).", size=13, anchor="start", fill=MUTED)
    c.text(x0 + 5 * s + 20, y0 + 190, "25 cells for 5 people; 10 ones.", size=13, anchor="start", fill=INK, weight="600")
    return c, dict(chapter=CH,
                   caption="The adjacency matrix: one cell for every possible pair, with a 1 where a tie exists. Checking one pair is instant; the price is that nearly all the cells are empty in a big network.",
                   alt="A five by five grid with the people's names along the top and left. Ones mark the ties; the grid is a mirror image across the diagonal. Ben's row, shaded orange, has ones under Ana, Cleo and Dev. A note counts 25 cells and 10 ones.",
                   data={"rows": [[1 if j in FIVE_ADJ[i] else 0 for j in range(5)] for i in range(5)]})


def bitrows():
    c = Canvas(900, 360, "Bit rows", "Each row of the matrix packed into one number.")
    c.text(30, 34, "5. Bit rows: each matrix row packed into one machine word", size=16, weight="700", anchor="start")
    rows = [[1 if j in FIVE_ADJ[i] else 0 for j in range(5)] for i in range(5)]
    words = [sum(b << j for j, b in enumerate(r)) for r in rows]
    x0, y0, s = 150, 66, 34
    c.text(x0 - 10, y0 - 10, "column", size=11, anchor="end", fill=MUTED, italic=True)
    for j in range(5):
        c.text(x0 + j * s + s / 2, y0 - 10, str(j), size=11, fill=MUTED)
    for i in range(5):
        y = y0 + i * 38
        c.text(x0 - 10, y + 22, FIVE[i], size=12, anchor="end", fill=MUTED)
        for j in range(5):
            on = rows[i][j]
            c.rect(x0 + j * s, y, s, 32, fill=LIGHT if on else PAPER, stroke=INK, sw=1.3)
            c.text(x0 + j * s + s / 2, y + 22, str(on), size=15, weight="700" if on else "400", fill=INK if on else MUTED)
        c.text(x0 + 5 * s + 16, y + 22, f"as one number: {words[i]}", size=13, anchor="start", fill=MUTED)
    ya = 290
    c.text(30, ya - 18, "Who do Ben and Dev both know? One AND of two words:", size=14, anchor="start", weight="600")
    a, b = rows[1], rows[3]
    both = [x & y for x, y in zip(a, b)]
    for k, (lab, r, col, xs) in enumerate((("Ben", a, BLUE, 130), ("Dev", b, PURPLE, 350), ("both", both, ORANGE, 590))):
        c.text(xs - 8, ya + 22, lab, size=13, anchor="end", fill=col, weight="700")
        for j in range(5):
            c.rect(xs + j * 26, ya, 26, 30, fill=(PALE_ORANGE if k == 2 and r[j] else PAPER), stroke=col, sw=1.5)
            c.text(xs + j * 26 + 13, ya + 21, str(r[j]), size=14, weight="700" if r[j] else "400", fill=INK if r[j] else MUTED)
    c.text(290, ya + 22, "AND", size=12, fill=MUTED, weight="700")
    c.text(528, ya + 24, "=", size=18, fill=MUTED, weight="700")
    c.text(590, ya + 56, "Only column 2 is left: Cleo.", size=13, anchor="start", fill=ORANGE, weight="700")
    return c, dict(chapter=CH,
                   caption="Bit rows pack each row of the matrix into a few machine words. One AND of two rows answers a question about 64 people at once; here it finds that Ben and Dev both know Cleo.",
                   alt="A five by five grid of zeros and ones, one row per person, with each row also shown as a single number: 2, 13, 10, 22 and 8. Underneath, the rows for Ben and Dev are placed side by side with the word AND between them and a result row that has a single one, in column 2, which is Cleo.",
                   data={"words": words})


def directed_weighted():
    c = Canvas(900, 400, "Directed and weighted", "Arrows and weights stored beside the targets.")
    c.text(30, 34, "Directed ties and weights: same two arrays, plus a third", size=16, weight="700", anchor="start")
    arcs = [(0, 1, 3), (1, 2, 5), (1, 3, 2), (3, 2, 4), (3, 4, 1), (4, 3, 6)]
    from alg_draw import FIVE_POS
    ox, oy, s = 50, 110, 1.0
    pos = [(ox + x * 1.2, oy + y * s) for x, y in FIVE_POS]
    for a, b, w in arcs:
        mutual = (b, a, None) in [(x, y, None) for x, y, _ in arcs]
        c.edge(pos[a], pos[b], ra=18, rb=18, directed=True, color=INK, width=2, curve=26 if mutual else 0,
               label=None if mutual else str(w))
    for i, (x, y) in enumerate(pos):
        c.node(x, y, str(i), r=18, fill=LIGHT, stroke=BLUE)
        c.text(x, y - 28 if i == 2 else y + 34, FIVE[i], size=12, fill=MUTED)
    c.text(50, 300, "Arrows: who follows whom. Numbers: messages sent.", size=13, anchor="start", fill=MUTED)
    c.text(50, 320, "Dev and Eli follow each other (Dev to Eli: 1, Eli to Dev: 6);", size=13, anchor="start", fill=MUTED)
    c.text(50, 340, "Ana follows Ben, not the reverse.", size=13, anchor="start", fill=MUTED)
    by = {i: [] for i in range(5)}
    for a, b, w in arcs:
        by[a].append((b, w))
    off, tgt, wts = [0], [], []
    for i in range(5):
        for b, w in sorted(by[i]):
            tgt.append(b)
            wts.append(w)
        off.append(len(tgt))
    xa = 470
    c.text(xa - 6, 92, "offsets", size=13, anchor="end", weight="700")
    cells(c, xa, 70, off, w=40, h=30, size=14, bold=True, idx=False)
    c.text(xa - 6, 172, "targets", size=13, anchor="end", weight="700")
    cells(c, xa, 150, tgt, w=40, h=30, size=14, bold=True, fills={k: LIGHT for k in range(len(tgt))}, idx_label="slot")
    c.text(xa - 6, 252, "weights", size=13, anchor="end", weight="700")
    cells(c, xa, 230, wts, w=40, h=30, size=14, bold=True, fills={k: PALE_ORANGE for k in range(len(wts))}, idx=False)
    c.text(xa, 310, "Slot k of weights belongs to slot k of targets.", size=13, anchor="start", fill=MUTED)
    c.text(xa, 332, "Each person lists only who they follow.", size=13, anchor="start", fill=MUTED)
    c.text(xa, 354, "'Who follows Dev?' needs a second, reversed copy.", size=13, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Directed and weighted: arrows mean each person lists only the people they point to, and weights ride along in a third array that lines up slot for slot with the targets.",
                   alt="On the left, the five-person network with arrows and a number on each: Ana to Ben 3, Ben to Cleo 5, Ben to Dev 2, Dev to Cleo 4, Dev and Eli pointing at each other with 1 and 6. On the right, three rows of boxes: offsets 0, 1, 3, 3, 5, 6; targets 1, 2, 3, 2, 4, 3; weights 3, 5, 2, 4, 1, 6. Notes explain that each weight lines up with the target in the same slot.",
                   data={"offsets": off, "targets": tgt, "weights": wts})


def memory():
    c = Canvas(900, 520, "Memory by size", "How much memory each layout needs as the network grows.")
    c.text(30, 32, "Memory needed as the network grows (each person knows about 10 others)", size=16, weight="700", anchor="start")
    x0, y0, w, h = 110, 60, 600, 380
    ns = [10 ** (k / 4) for k in range(8, 25)]  # 100 to 1,000,000
    lo, hi = 3, 13  # log10 bytes
    lx = lambda n: x0 + (math.log10(n) - 2) / 4 * w
    ly = lambda b: y0 + h - (math.log10(b) - lo) / (hi - lo) * h
    for e in range(lo, hi + 1, 3):
        y = ly(10 ** e)
        c.add(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 + w}" y2="{y:.1f}" stroke="#e5e7eb" stroke-width="1"/>')
        c.text(x0 - 8, y + 4, human_bytes(10 ** e) if e > 0 else "1 B", size=11, anchor="end", fill=MUTED)
    for e in range(2, 7):
        x = lx(10 ** e)
        c.text(x, y0 + h + 18, f"{10 ** e:,}", size=11, fill=MUTED)
    c.text(x0 + w / 2, y0 + h + 40, "number of people", size=12, fill=MUTED)
    series = [("Edge list", lambda n: 40 * n, SKY, None),
              ("Adjacency list", lambda n: 64 * n, GREEN, "6 3"),
              ("CSR", lambda n: 44 * n, BLUE, None),
              ("Matrix, 1 byte a cell", lambda n: n * n, RED, None),
              ("Bit rows", lambda n: n * n / 8, ORANGE, "6 3")]
    meta = {}
    for name, f, col, dash in series:
        pts = " ".join(f"{lx(n):.1f},{ly(f(n)):.1f}" for n in ns)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        c.add(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"{d}/>')
        meta[name] = {"100": f(100), "10000": f(10 ** 4), "1000000": f(10 ** 6)}
    y16 = ly(16e9)
    c.add(f'<line x1="{x0}" y1="{y16:.1f}" x2="{x0 + w}" y2="{y16:.1f}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="2 4"/>')
    c.text(x0 + 8, y16 - 6, "a laptop's memory (16 GB)", size=12, anchor="start", fill=INK, weight="600")
    lab = [("Matrix, 1 byte a cell", RED, ly(1e12), "Matrix: 1 TB at a million people"),
           ("Bit rows", ORANGE, ly(1.25e11), "Bit rows: 125 GB"),
           ("Adjacency list", GREEN, ly(64e6) - 14, "Adjacency list: 64 MB"),
           ("CSR", BLUE, ly(44e6) + 2, "CSR: 44 MB"),
           ("Edge list", SKY, ly(40e6) + 22, "Edge list: 40 MB")]
    for _, col, y, t in lab:
        c.text(x0 + w + 12, y + 4, t, size=12, anchor="start", fill=col, weight="700")
    return c, dict(chapter=CH,
                   caption="Memory against network size on a log scale (each gridline is a thousand times more). The three list layouts grow in step with the people; the matrix grows with the square of them and passes a laptop's memory around 100,000 people.",
                   alt="A chart on logarithmic axes, number of people from 100 to 1,000,000 across and memory from 1 kilobyte to 10 terabytes up. Three nearly parallel straight lines for the edge list, adjacency list and CSR end near 40 to 64 megabytes at a million people. Two steeper lines for the matrix and bit rows end at 1 terabyte and 125 gigabytes, crossing a dashed line at 16 gigabytes, a laptop's memory, before a million people.",
                   data=meta)


def questions():
    c = Canvas(900, 400, "Which layout answers what", "A grid of layouts against questions.")
    c.text(30, 32, "Which layout answers which question quickly?", size=16, weight="700", anchor="start")
    qs = ["Are Ana and\nDev tied?", "List Ben's\nfriends", "How many\nfriends has Ben?", "Visit every\ntie", "Who do Ben and\nDev both know?"]
    rows = [("Edge list", ["slow", "slow", "slow", "fast", "slow"]),
            ("Adjacency list", ["ok", "fast", "fast", "fast", "ok"]),
            ("CSR", ["ok", "fast", "fast", "fast", "ok"]),
            ("Matrix", ["fast", "ok", "ok", "slow", "ok"]),
            ("Bit rows", ["fast", "ok", "fast", "ok", "fast"])]
    x0, y0, cw, rh = 170, 100, 130, 46
    for j, q in enumerate(qs):
        for k, line in enumerate(q.split("\n")):
            c.text(x0 + j * cw + cw / 2, y0 - 34 + k * 16, line, size=12, weight="600")
    style = {"fast": (PALE_GREEN, GREEN, "fast"), "ok": (PALE_ORANGE, ORANGE, "so-so"), "slow": (PALE_RED, RED, "slow")}
    for i, (name, vals) in enumerate(rows):
        y = y0 + i * rh
        c.text(x0 - 12, y + 28, name, size=13, anchor="end", weight="600")
        for j, v in enumerate(vals):
            fill, stroke, word = style[v]
            c.rect(x0 + j * cw + 6, y + 4, cw - 12, rh - 8, fill=fill, stroke=stroke, sw=1.6, rx=6)
            shape = {"fast": "check", "ok": "dash", "slow": "cross"}[v]
            c.text(x0 + j * cw + cw / 2, y + 29, {"check": "✓ ", "dash": "~ ", "cross": "✗ "}[shape] + word, size=13, weight="700", fill=INK)
    c.text(30, 360, "fast = one or a few steps; so-so = look through one person's list or one row; slow = look at everything.", size=12, anchor="start", fill=MUTED)
    c.text(30, 380, "CSR with sorted friend lists can check a tie by binary search; the bit row wins when you compare two people.", size=12, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="No layout wins everywhere. Lists are quick at who knows whom; the matrix is quick at whether two people are tied; bit rows are quick at comparing two people.",
                   alt="A grid with five rows for the layouts and five columns for questions. Each cell reads fast, so-so or slow with a tick, tilde or cross. The edge list is fast only at visiting every tie. Adjacency list and CSR are fast at listing and counting a person's friends and visiting every tie. The matrix is fast at checking one pair only. Bit rows are fast at checking a pair, counting friends and finding common friends.")


FIGURES = {
    "rep-network": network, "rep-ids-labels": ids_labels, "rep-edge-list": edge_list,
    "rep-adjacency-list": adjacency_list, "rep-csr": csr, "rep-matrix": matrix, "rep-bitrows": bitrows,
    "rep-directed-weighted": directed_weighted, "rep-memory": memory, "rep-questions": questions,
}

"""Figures for the cost chapter of the algorithms book (chapter 2). Standard library only.

Every number drawn is computed here: step counts from the five-person edge list, growth tables from the formulas,
the speedup curves from Amdahl's formula, and the floating-point sums from Python's own floats.
"""
import math
import random

from alg_draw import (FIVE, FIVE_ADJ, FIVE_TIES, LIGHT, PALE_GREEN, PALE_ORANGE, PALE_PURPLE, PALE_RED, cells,
                      pill)
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, PURPLE, RED, SKY, Canvas

CH = 2


def human_time(sec):
    if sec < 1e-6:
        return "under a microsecond"
    for unit, f in (("years", 3.156e7), ("days", 86400), ("hours", 3600), ("minutes", 60), ("seconds", 1),
                    ("milliseconds", 1e-3), ("microseconds", 1e-6)):
        if sec >= f:
            v = sec / f
            if unit == "years" and v > 1.4e10:
                return "older than the universe"
            return f"{v:,.0f} {unit}" if v >= 9.5 else f"{v:.1f} {unit}"
    return f"{sec:.2g} s"


def count_steps():
    c = Canvas(900, 330, "Counting steps by hand", "Is Ana tied to Dev, in an edge list and in an adjacency list.")
    c.text(30, 32, "Is Ana tied to Dev? Count the steps.", size=16, weight="700", anchor="start")
    c.text(30, 66, "Edge list: look at every row", size=14, weight="700", anchor="start", fill=BLUE)
    for k, (a, b) in enumerate(FIVE_TIES):
        y = 80 + k * 34
        c.rect(70, y, 70, 28, fill=PALE_ORANGE, stroke=ORANGE, sw=1.6)
        c.rect(140, y, 70, 28, fill=PALE_ORANGE, stroke=ORANGE, sw=1.6)
        c.text(105, y + 20, str(a), size=14, weight="600")
        c.text(175, y + 20, str(b), size=14, weight="600")
        c.node(44, y + 14, str(k + 1), r=12, fill=PAPER, stroke=ORANGE, size=12)
        c.text(232, y + 20, "not (0, 3)", size=12, anchor="start", fill=MUTED)
    c.text(70, 266, "5 rows looked at, then we can say no.", size=13, anchor="start", weight="600")
    c.text(70, 286, "Ten times the ties would mean 50 looks.", size=13, anchor="start", fill=MUTED)
    c.text(500, 66, "Adjacency list: go straight to Ana", size=14, weight="700", anchor="start", fill=GREEN)
    c.node(530, 110, "0", r=18, fill=LIGHT, stroke=BLUE)
    c.text(560, 115, "Ana", size=13, anchor="start", fill=MUTED)
    c.arrow((600, 110), (650, 110), color=MUTED)
    c.rect(654, 94, 64, 32, fill=PALE_GREEN, stroke=GREEN, sw=1.6, rx=4)
    c.text(686, 115, "1", size=15, weight="600")
    c.node(500, 170, "1", r=12, fill=PAPER, stroke=GREEN, size=12)
    c.text(522, 175, "jump to Ana's list", size=13, anchor="start")
    c.node(500, 205, "2", r=12, fill=PAPER, stroke=GREEN, size=12)
    c.text(522, 210, "look at its one entry: Ben, not Dev", size=13, anchor="start")
    c.text(500, 266, "2 steps, then we can say no.", size=13, anchor="start", weight="600")
    c.text(500, 286, "Ten times the ties: still about 2 steps for Ana.", size=13, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Counting by hand. To be sure Ana and Dev are not tied, the edge list makes us read all five rows. The adjacency list takes us to Ana's own list, and her list has one entry.",
                   alt="Left, the five-row edge list with each row numbered 1 to 5 in order, labeled as five rows looked at. Right, a single arrow from Ana to her list holding just Ben's id, labeled as two steps: jump to Ana's list and look at its one entry.")


def growth():
    c = Canvas(900, 482, "Growth curves", "How the steps grow with the number of people.")
    c.text(30, 32, "How fast the work grows when the network does", size=16, weight="700", anchor="start")
    x0, y0, w, h = 90, 60, 560, 340
    nmax, ymax = 20, 400
    lx = lambda n: x0 + n / nmax * w
    ly = lambda v: y0 + h - min(v, ymax * 1.02) / ymax * h
    for v in range(0, ymax + 1, 100):
        c.add(f'<line x1="{x0}" y1="{ly(v):.1f}" x2="{x0 + w}" y2="{ly(v):.1f}" stroke="#e5e7eb"/>')
        c.text(x0 - 8, ly(v) + 4, str(v), size=11, anchor="end", fill=MUTED)
    for n in range(0, nmax + 1, 5):
        c.text(lx(n), y0 + h + 18, str(n), size=11, fill=MUTED)
    c.text(x0 + w / 2, y0 + h + 40, "number of people, n", size=12, fill=MUTED)
    c.text(x0 - 60, y0 + h / 2, "steps", size=12, fill=MUTED)
    series = [("n (one pass)", lambda n: n, GREEN, None), ("n log n (sort)", lambda n: n * math.log2(max(n, 1)), BLUE, None),
              ("n squared (all pairs)", lambda n: n * n, ORANGE, None), ("2 to the n (try everything)", lambda n: 2 ** n, RED, None)]
    for name, f, col, _ in series:
        pts = []
        for k in range(0, nmax * 4 + 1):
            n = k / 4
            v = f(n)
            pts.append(f"{lx(n):.1f},{ly(v):.1f}")
            if v > ymax * 1.02:
                break
        c.add(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="3.2"/>')
    ly0 = y0 + 10
    for k, (name, f, col, _) in enumerate(series):
        c.add(f'<line x1="{x0 + w + 20}" y1="{ly0 + k * 28}" x2="{x0 + w + 48}" y2="{ly0 + k * 28}" stroke="{col}" stroke-width="3.2"/>')
        c.text(x0 + w + 56, ly0 + k * 28 + 4, name, size=12, anchor="start")
    c.text(x0 + w + 20, ly0 + 140, "At n = 20:", size=12, anchor="start", weight="700")
    for k, (name, f, col, _) in enumerate(series):
        c.text(x0 + w + 20, ly0 + 160 + k * 20, f"{f(20):,.0f}", size=12, anchor="start", fill=col, weight="600")
    c.text(30, 466, "Lines leave the picture when they pass 400 steps. The red line leaves at n = 9.", size=12, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Four growth rates drawn on one chart. For a small number of people they all look harmless; by 20 people the red line is above a million steps and the chart cannot hold it.",
                   alt="A line chart of steps against the number of people from 0 to 20. A green straight line reaches 20. A blue line that bends slightly upward reaches about 86. An orange curve reaches 400 at 20 people. A red curve shoots off the top of the chart at about 9 people. A legend lists the four rates and the step counts at 20 people: 20, 86, 400 and 1,048,576.")


def doubling():
    c = Canvas(900, 330, "Doubling the network", "How much longer the job takes when the input doubles.")
    c.text(30, 32, "Double the network. How much longer does the job take?", size=16, weight="700", anchor="start")
    n = 1000
    rows = [("one pass over everything", 2.0, GREEN), ("sorting (n log n)", (2 * n * math.log2(2 * n)) / (n * math.log2(n)), BLUE),
            ("every pair (n squared)", 4.0, ORANGE), ("every triple (n cubed)", 8.0, PURPLE),
            ("try every subset (2 to the n)", None, RED)]
    x0, y0, bw = 270, 70, 520
    for k, (name, f, col) in enumerate(rows):
        y = y0 + k * 46
        c.text(x0 - 12, y + 24, name, size=13, anchor="end")
        if f is None:
            c.rect(x0, y + 4, bw, 30, fill=col + "33", stroke=col, sw=1.8)
            c.text(x0 + bw / 2, y + 25, "squared: 2 to the 2,000 instead of 2 to the 1,000", size=13, weight="700")
            c.text(x0 + bw + 8, y + 25, ">", size=18, anchor="start", fill=col, weight="700")
        else:
            wd = bw * f / 8.5
            c.rect(x0, y + 4, wd, 30, fill=col + "33", stroke=col, sw=1.8)
            c.text(x0 + wd + 10, y + 25, f"about {f:.1f} times", size=13, anchor="start", weight="700", fill=col)
    c.text(x0, y0 + 5 * 46 + 18, "Computed for a network of 1,000 people growing to 2,000.", size=12, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="What doubling does. A single pass takes twice as long, a sort a little more than twice, every pair four times, every triple eight times. Trying every subset does not just multiply the work, it squares it.",
                   alt="Five horizontal bars. One pass over everything is a bar for 2 times. Sorting is slightly longer, about 2.2 times. Every pair is 4 times and every triple 8 times. The last bar, try every subset, runs off the end of the chart with the note that 2 to the 1,000 becomes 2 to the 2,000.")


def times():
    c = Canvas(900, 330, "How long it really takes", "Time for each growth rate at a billion steps a second.")
    c.text(30, 32, "How long, at a billion steps a second?", size=16, weight="700", anchor="start")
    ns = [1000, 1_000_000, 1_000_000_000]
    classes = [("n", lambda n: n), ("n log n", lambda n: n * math.log2(n)), ("n squared", lambda n: n * n),
               ("n cubed", lambda n: n ** 3)]
    x0, y0, cw, rh = 150, 90, 240, 46
    for j, n in enumerate(ns):
        c.text(x0 + j * cw + cw / 2, y0 - 16, f"{n:,} people", size=13, weight="700")
    data = {}
    for i, (name, f) in enumerate(classes):
        y = y0 + i * rh
        c.text(x0 - 12, y + 29, name, size=13, anchor="end", weight="600")
        for j, n in enumerate(ns):
            sec = f(n) / 1e9
            data[f"{name} at {n}"] = sec
            col = GREEN if sec < 1 else BLUE if sec < 3600 else ORANGE if sec < 3.156e7 else RED
            pale = {GREEN: PALE_GREEN, BLUE: LIGHT, ORANGE: PALE_ORANGE, RED: PALE_RED}[col]
            c.rect(x0 + j * cw + 6, y + 4, cw - 12, rh - 8, fill=pale, stroke=col, sw=1.6, rx=6)
            c.text(x0 + j * cw + cw / 2, y + 29, human_time(sec), size=13, weight="700")
    c.text(30, y0 + 4 * rh + 24, "2 to the n is off the table: at just 100 people it needs about 40 trillion years.", size=13, anchor="start")
    c.text(30, y0 + 4 * rh + 46, "Green: instant. Blue: a coffee break. Orange: the project deadline. Red: a career or longer.", size=12, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Wall-clock time for a computer doing a billion simple steps a second. A single pass is fine at any size; every pair is fine at a thousand people and hopeless at a billion.",
                   alt="A grid of four growth rates by three network sizes (1,000; 1,000,000; 1,000,000,000 people). One pass takes a microsecond, a millisecond and one second. Sorting takes 10 microseconds, 20 milliseconds and 30 seconds. Every pair takes one millisecond, 17 minutes and about 32 years. Every triple takes one second, about 32 years and longer than the universe has existed.",
                   data=data)


def cache_story():
    c = Canvas(900, 330, "A cache analogy", "Desk, shelf and archive.")
    c.text(30, 32, "Why memory has levels: the desk, the shelf and the archive", size=16, weight="700", anchor="start")
    # scale: 1 nanosecond = 1 second. Rough typical latencies: cache 1 ns, main memory 80 ns, solid-state drive 100 microseconds.
    cols = [(60, "Your desk", "the processor's cache", "about 1 second", "1 ns", GREEN, PALE_GREEN),
            (340, "The shelf across the room", "main memory", "about a minute and a half", "80 ns", BLUE, LIGHT),
            (620, "The archive across town", "a solid-state drive", "more than a day", "100 microseconds", RED, PALE_RED)]
    for x, name, real, scaled, actual, col, pale in cols:
        c.rect(x, 60, 230, 190, fill=pale, stroke=col, sw=2, rx=10)
        c.text(x + 115, 90, name, size=15, weight="700")
        c.text(x + 115, 112, f"= {real}", size=12, fill=MUTED)
    # desk drawing
    c.rect(100, 150, 150, 14, fill=PAPER, stroke=INK, sw=1.6)
    c.rect(115, 125, 30, 25, fill=PALE_ORANGE, stroke=ORANGE, sw=1.4)
    c.rect(160, 130, 24, 20, fill=PALE_ORANGE, stroke=ORANGE, sw=1.4)
    c.text(175, 190, "a few notes, at arm's reach", size=12, fill=MUTED)
    # shelf drawing
    for k in range(3):
        c.rect(370, 128 + k * 18, 170, 12, fill=PAPER, stroke=INK, sw=1.2)
        for m in range(6):
            c.rect(374 + m * 28, 120 + k * 18 + 2, 20, 8, fill=[SKY, LIGHT, PALE_ORANGE][m % 3], stroke=BLUE, sw=1)
    c.text(455, 198, "many binders, a short walk", size=12, fill=MUTED)
    # archive drawing
    for k in range(4):
        c.rect(650 + k * 42, 125, 36, 56, fill=PAPER, stroke=INK, sw=1.4)
        c.text(668 + k * 42, 158, "A" if k == 0 else "B" if k == 1 else "C" if k == 2 else "D", size=14, weight="700", fill=MUTED)
    c.text(735, 198, "a whole building, a car ride", size=12, fill=MUTED)
    for (x, name, real, scaled, actual, col, pale) in cols:
        c.text(x + 115, 228, scaled, size=14, weight="700", fill=col)
        c.text(x + 115, 244, f"(really {actual})", size=11, fill=MUTED)
    c.text(30, 280, "Stretch one nanosecond to one second and these are the waits for one fetch. The numbers are rough, typical ones.", size=13, anchor="start", fill=MUTED)
    c.text(30, 304, "A fast program works like a good clerk: grab a whole armful at once, and use it all before going back.", size=13, anchor="start")
    return c, dict(chapter=CH,
                   caption="The memory story. If one nanosecond lasted a second, your desk (the cache) would answer in a second, the shelf (main memory) in about a minute and a half, and the archive (a drive) in more than a day.",
                   alt="Three boxes side by side. Left, a desk with a few notes, labeled the processor's cache, about 1 second. Middle, a shelf of binders across the room, labeled main memory, about a minute and a half. Right, a building of filing cabinets across town, labeled a solid-state drive, more than a day.")


def cache_lines():
    c = Canvas(900, 400, "Cache lines", "Reading neighbors in a row versus jumping around.")
    c.text(30, 32, "Memory is fetched in armfuls (cache lines), not one number at a time", size=16, weight="700", anchor="start")
    def grid(x0, y0, hits, title, fetched):
        c.text(x0, y0 - 14, title, size=14, weight="700", anchor="start")
        lines = set()
        for k in range(40):
            row, col = divmod(k, 8)
            hit = k in hits
            if hit:
                lines.add(row)
            c.rect(x0 + col * 38, y0 + row * 44, 38, 36, fill=PALE_ORANGE if hit else PAPER, stroke=INK, sw=1.2)
            c.text(x0 + col * 38 + 19, y0 + row * 44 + 23, str(k), size=12, fill=INK if hit else MUTED, weight="700" if hit else "400")
        for row in range(5):
            fetchedrow = row in lines
            c.rect(x0 - 5, y0 + row * 44 - 3, 8 * 38 + 10, 42, fill="none", stroke=RED if fetchedrow else FAINT, sw=2.4 if fetchedrow else 1, rx=4, dash=None if fetchedrow else "3 3")
        c.text(x0, y0 + 5 * 44 + 18, fetched.format(len(lines)), size=14, weight="700", anchor="start", fill=RED if len(lines) > 2 else GREEN)
        return len(lines)
    a = grid(60, 80, {6, 7, 8, 9, 10}, "Walk down one person's friends (slots 6 to 10, side by side)", "{} armfuls fetched")
    b = grid(480, 80, {1, 12, 19, 27, 36}, "Hop to five friends stored far apart", "{} armfuls fetched")
    c.text(60, 372, "Each framed row is one armful (one cache line). Highlighted slots are the ones we wanted.", size=12, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="A cache line is an armful of neighbors fetched together. Reading five numbers that sit side by side costs about two armfuls; reading five scattered numbers costs five.",
                   alt="Two grids of 40 numbered slots, five rows of eight, each row framed as one cache line. On the left, slots 6 to 10 are highlighted and sit in two rows, so two lines are fetched. On the right, slots 1, 12, 19, 27 and 36 are highlighted, one in each row, so five lines are fetched.",
                   data={"side_by_side": a, "scattered": b})


def amdahl():
    c = Canvas(900, 470, "Parallel speedup", "Speedup against number of workers.")
    c.text(30, 32, "More workers do not help the part that cannot be shared", size=16, weight="700", anchor="start")
    x0, y0, w, h = 90, 60, 580, 320
    cmax, smax = 64, 64
    lx = lambda k: x0 + (math.log2(k)) / 6 * w
    ly = lambda s: y0 + h - s / smax * h
    for s in (0, 16, 32, 48, 64):
        c.add(f'<line x1="{x0}" y1="{ly(s)}" x2="{x0 + w}" y2="{ly(s)}" stroke="#e5e7eb"/>')
        c.text(x0 - 8, ly(s) + 4, f"{s}x", size=11, anchor="end", fill=MUTED)
    for e in range(0, 7):
        c.text(lx(2 ** e), y0 + h + 18, str(2 ** e), size=11, fill=MUTED)
    c.text(x0 + w / 2, y0 + h + 40, "workers (cores)", size=12, fill=MUTED)
    c.add(f'<polyline points="{" ".join(f"{lx(2 ** e):.1f},{ly(2 ** e):.1f}" for e in range(7))}" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="6 4"/>')
    c.text(lx(32) - 20, ly(40) - 6, "perfect", size=12, anchor="end", fill=MUTED)
    data = {}
    for p, col in ((0.5, RED), (0.9, ORANGE), (0.99, BLUE)):
        pts = []
        for e in range(0, 61):
            k = 2 ** (e / 10)
            s = 1 / ((1 - p) + p / k)
            pts.append(f"{lx(k):.1f},{ly(s):.1f}")
        c.add(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="3.2"/>')
        s64 = 1 / ((1 - p) + p / 64)
        data[str(p)] = round(s64, 2)
        c.text(x0 + w + 12, ly(s64) + 4, f"{int(p * 100)}% shareable: {s64:.1f}x at 64", size=12, anchor="start", fill=col, weight="700")
    c.text(30, 458, "Speedup = 1 / ((1 - p) + p / k), with p the shareable fraction and k the number of workers.", size=12, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Speedup from extra workers when only part of the job can be shared. If half is shareable you never beat 2 times, however many workers you hire; at 99 percent, 64 workers give about 39 times.",
                   alt="A line chart of speedup against number of workers from 1 to 64 on a log axis. A dashed diagonal shows perfect speedup. Three curves bend away below it: 50 percent shareable flattens at about 2 times, 90 percent reaches about 8.8 times at 64 workers, and 99 percent reaches about 39 times.",
                   data=data)


def float_order():
    nums = [1e16, 1.0, -1e16, 1.0]
    def total(order):
        s = 0.0
        for k in order:
            s += nums[k]
        return s
    orders = [("as listed", [0, 1, 2, 3]), ("big ones cancel first", [0, 2, 1, 3]), ("big one, then both 1s", [0, 1, 3, 2])]
    results = [total(o) for _, o in orders]
    assert len(set(results)) > 1, "the example should give different sums"
    c = Canvas(900, 330, "Floating-point order", "The same four numbers added in three orders.")
    c.text(30, 32, "Same four numbers, three orders, three answers", size=16, weight="700", anchor="start")
    names = ["10,000,000,000,000,000", "1", "-10,000,000,000,000,000", "1"]
    for k, (lab, order) in enumerate(orders):
        y = 66 + k * 70
        c.text(40, y + 28, lab, size=13, anchor="start", weight="700")
        x = 220
        for step, i in enumerate(order):
            c.rect(x, y + 6, 100, 34, fill=LIGHT if abs(nums[i]) > 1 else PAPER, stroke=BLUE if abs(nums[i]) > 1 else INK, sw=1.5, rx=4)
            c.text(x + 50, y + 28, "1e16" if nums[i] == 1e16 else "-1e16" if nums[i] == -1e16 else "1", size=14, weight="600")
            if step < 3:
                c.text(x + 114, y + 28, "+", size=16, fill=MUTED)
            x += 128
        c.text(x - 4, y + 28, "=", size=18, anchor="start", fill=MUTED)
        c.text(x + 24, y + 30, f"{results[k]:.0f}", size=22, anchor="start", weight="700", fill=RED if results[k] != 2 else GREEN)
    c.text(40, 292, "The true sum is 2. Adding 1 to ten quadrillion changes nothing the computer can store, so that 1 vanishes.", size=13, anchor="start")
    c.text(40, 314, "Computers keep about 16 significant digits. Where the small numbers land in the order decides what survives.", size=12, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Floating-point addition is not associative. Ten quadrillion plus 1 rounds back to ten quadrillion, so the order of the additions decides whether the 1s survive.",
                   alt=f"Three rows, each adding the same four numbers (1e16, 1, minus 1e16 and 1) in a different order. As listed gives {results[0]:.0f}, letting the big ones cancel first gives {results[1]:.0f}, and adding the big one and both 1s before the other big one gives {results[2]:.0f}. A note says the true sum is 2.",
                   data={lab: r for (lab, _), r in zip(orders, results)})


def determinism():
    rng = random.Random(11)
    parts = [10 ** rng.uniform(-6, 6) * rng.choice([1, -1]) for _ in range(8)]
    def run(order):
        s = 0.0
        for k in order:
            s += parts[k]
        return s
    base = list(range(8))
    found = None
    for seed in range(1, 200):
        a, b = list(base), list(base)
        random.Random(seed).shuffle(a)
        random.Random(seed + 1000).shuffle(b)
        if run(a) != run(b):
            found = (a, b)
            break
    a, b = found
    ra, rb = run(a), run(b)
    c = Canvas(900, 360, "Determinism", "Two runs of the same parallel sum.")
    c.text(30, 32, "Same input, two runs: the workers finish in a different order", size=16, weight="700", anchor="start")
    for r, (order, res, title) in enumerate(((a, ra, "Run 1"), (b, rb, "Run 2"))):
        y = 70 + r * 110
        c.text(40, y + 26, title, size=14, anchor="start", weight="700")
        for step, i in enumerate(order):
            x = 120 + step * 68
            c.node(x + 20, y + 20, f"W{i + 1}", r=19, fill=LIGHT, stroke=BLUE, size=12)
            c.text(x + 20, y + 58, f"{parts[i]:.3g}", size=10, fill=MUTED)
            if step < 7:
                c.arrow((x + 42, y + 20), (x + 52, y + 20), color=MUTED, width=1.6)
        c.text(120 + 8 * 68 + 4, y + 25, "=", size=18, anchor="start", fill=MUTED)
        c.text(120 + 8 * 68 + 24, y + 26, f"{res:.17g}", size=13, anchor="start", mono=True, weight="700", fill=RED)
    c.text(40, 300, f"Exact answer (summed with care): {math.fsum(parts):.17g}", size=13, anchor="start", mono=True, fill=GREEN)
    c.text(40, 328, "The runs agree to about 15 digits and differ after that. A deterministic program fixes the order.", size=13, anchor="start", fill=MUTED)
    return c, dict(chapter=CH,
                   caption="Each worker adds up its own share; the total depends on the order in which the shares are combined. If that order changes from run to run, so do the last digits.",
                   alt=f"Two rows of eight numbered workers joined by arrows in two different orders, the same eight numbers in each. Run 1 ends at {ra:.17g} and run 2 at {rb:.17g}; underneath, the exact sum is {math.fsum(parts):.17g}.",
                   data={"run1": ra, "run2": rb, "exact": math.fsum(parts)})


FIGURES = {
    "cost-count": count_steps, "cost-growth": growth, "cost-doubling": doubling, "cost-times": times,
    "cost-cache-story": cache_story, "cost-cache-lines": cache_lines, "cost-amdahl": amdahl,
    "cost-float-order": float_order, "cost-determinism": determinism,
}

"""Figures for the algorithms book, chapter 33 (case study: exact closeness on big graphs).

Standard library only. The timings are the measured numbers from the standalone closeness lab described in the
chapter (512 lanes, 2 threads, a 2-core AVX-512 workspace), typed here once in LAB so every figure and the chapter
draw on the same table. Arithmetic (speedups, byte counts) is computed from it. The exactness picture is computed
by plain search on the ten-person network.
"""
import math

from fig_alg_betweenness import EDGES, NAMES, adjacency
from fig_alg_closeness import bfs
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, PURPLE, RED, SKY, Canvas

# Measured in the lab. Seconds. None = not measured. A on the two big graphs was estimated from a sample of sources.
LAB = [
    {"graph": "Chung-Lu", "n": 50_000, "m": 192_000, "A": 51.3, "B": 36.8, "C": 1.86, "D": 0.87},
    {"graph": "R-MAT", "n": 2 ** 16, "m": 478_000, "A": 53.4, "B": 30.2, "C": 1.51, "D": 0.56},
    {"graph": "Barabasi-Albert", "n": 50_000, "m": 200_000, "A": 53.8, "D": 2.2},
    {"graph": "Chung-Lu", "n": 500_000, "m": 1_950_000, "A": 2.3 * 3600, "V": 143.0, "rss_mb": 317, "sampled": True},
    {"graph": "R-MAT", "n": 2 ** 19, "m": 3_980_000, "A": 82 * 60, "V": 38.0, "rss_mb": 262, "sampled": True, "reported": {"V": 130}},
]
COLORS = {"B": SKY, "C": BLUE, "D": ORANGE, "V": RED}
WORDS = {"B": "B: shrunk graph", "C": "C: 512 per pass",
         "D": "D: shrunk + shared", "V": "V: D, compressed lists"}


def tag(row):
    n = f"{row['n'] // 1000}k" if row["n"] % 1000 == 0 else f"2^{int(math.log2(row['n']))}"
    m = f"{row['m'] / 1e6:.2f}M" if row["m"] >= 1e6 else f"{row['m'] // 1000}k"
    return f"{row['graph']} n={n}", f"m={m}"


# ---------------------------------------------------------------- 1. the speedups, as bars
def speedup_bars():
    c = Canvas(760, 400, "Speedups over one search per person",
               "Grouped bars on a log scale: how many times faster each method was than the baseline, on five test graphs.")
    c.text(380, 28, "Times faster than the baseline (A), log scale", size=15, weight="700")
    x0, w, y = 230, 470, 60

    def px(v):
        return x0 + w * math.log10(v) / math.log10(200)
    for t in [1, 2, 5, 10, 20, 50, 100, 200]:
        c.add(f'<line x1="{px(t):.1f}" y1="50" x2="{px(t):.1f}" y2="335" stroke="{FAINT}"/>')
        c.text(px(t), 350, f"{t}x", size=11, fill=MUTED)
    data = []
    for row in LAB:
        keys = [k for k in ("B", "C", "D", "V") if k in row]
        a, b = tag(row)
        c.text(x0 - 12, y + 9 * len(keys), a, size=12.5, anchor="end", weight="600")
        c.text(x0 - 12, y + 9 * len(keys) + 16, b + (", A estimated" if row.get("sampled") else ""), size=11, anchor="end", fill=MUTED)
        for k in keys:
            s = row.get("reported", {}).get(k, row["A"] / row[k])
            c.rect(x0, y, max(px(s) - x0, 1), 15, fill=COLORS[k], stroke=COLORS[k], sw=0)
            c.text(px(s) + 5, y + 12, f"{s:.0f}x ({k})" if s >= 10 else f"{s:.1f}x ({k})", size=11, anchor="start")
            data.append({"graph": a + " " + b, "method": k, "speedup": round(s, 2)})
            y += 18
        y += 22
    lx = 60
    for k in ("B", "C", "D", "V"):
        c.rect(lx, 374, 12, 12, fill=COLORS[k], stroke=COLORS[k], sw=0)
        c.text(lx + 18, 385, WORDS[k], size=11.5, anchor="start")
        lx += 180
    meta = dict(book="algorithms", chapter=33,
                caption="The whole story in one picture. Shrinking the graph alone (B) gains less than 2x; sharing passes 512 searches at a time (C) gains about 30x; doing both (D, V) gains 24x to 130x. Every bar is one lab measurement on one graph; on the two big graphs the baseline time is an estimate from sampled sources.",
                alt=("Horizontal bars on a logarithmic scale from 1x to 200x, grouped by graph. "
                     + "; ".join(f"{d['graph']}, method {d['method']}: {d['speedup']:.1f}x" for d in data) + "."),
                data={"rows": data})
    return c, meta


# ---------------------------------------------------------------- 2. one graph, step by step
def ladder():
    row = LAB[0]
    steps = [("A: one search per person", row["A"], GRAY), ("B: same, on the shrunk graph", row["B"], SKY),
             ("C, counting each bit one by one", 3.75, PURPLE), ("C: 512 per pass, bit-plane counters", row["C"], BLUE),
             ("D: shrunk graph + shared pass", row["D"], ORANGE)]
    c = Canvas(760, 330, "Chung-Lu, 50,000 people, step by step",
               "Horizontal bars of seconds on a log scale for five versions of the computation on one graph.")
    c.text(380, 28, "Seconds for every person's exact closeness: Chung-Lu, n = 50,000, m = 192,000", size=14, weight="700")
    x0, w = 290, 400

    def px(v):
        return x0 + w * (math.log10(v) + 0.3) / (math.log10(100) + 0.3)
    for t in [0.5, 1, 2, 5, 10, 20, 50, 100]:
        c.add(f'<line x1="{px(t):.1f}" y1="48" x2="{px(t):.1f}" y2="282" stroke="{FAINT}"/>')
        c.text(px(t), 298, f"{t:g} s", size=11, fill=MUTED)
    for k, (lab, sec, col) in enumerate(steps):
        y = 56 + k * 46
        c.text(x0 - 12, y + 20, lab, size=12.5, anchor="end", weight="600")
        c.rect(x0, y, px(sec) - x0, 28, fill=col, stroke=col, sw=0)
        c.text(px(sec) + 6, y + 19, f"{sec:g} s", size=12.5, anchor="start", weight="700")
    c.text(380, 320, "Lab: 512 lanes, 2 threads, 2-core AVX-512 workspace. The 3.75 s bar is C before the bit-plane counters.", size=11.5, fill=MUTED)
    meta = dict(book="algorithms", chapter=33,
                caption="One graph, five versions. The shared pass is the big step (from 51.3 to 3.75 seconds), the bit-plane counters halve it again (1.86), and folding twins and leaves into a weighted graph halves it once more (0.87): 59 times faster than the baseline, with the same answers.",
                alt="Five horizontal bars on a logarithmic seconds axis: A, one search per person, 51.3 seconds; B, the same on the shrunk graph, 36.8; C counting bits one by one, 3.75; C with bit-plane counters, 1.86; D, shrunk graph plus shared pass, 0.87.",
                data={"graph": "Chung-Lu n=50000 m=192000", "seconds": {lab: sec for lab, sec, _ in steps}})
    return c, meta


GRAY = "#9ca3af"


# ---------------------------------------------------------------- 3. the two big graphs, in minutes
def big_graphs():
    rows = [r for r in LAB if r.get("sampled")]
    c = Canvas(760, 300, "The two big graphs, in minutes",
               "Paired bars in minutes: the estimated baseline and the measured fastest method on two graphs with millions of ties.")
    c.text(380, 28, "Minutes for exact closeness of everyone (baseline estimated from sampled sources)", size=14, weight="700")
    x0, w = 230, 440
    top = max(r["A"] for r in rows) / 60
    for k, r in enumerate(rows):
        a, b = tag(r)
        y = 60 + k * 110
        c.text(x0 - 12, y + 26, a, size=12.5, anchor="end", weight="600")
        c.text(x0 - 12, y + 44, b, size=11, anchor="end", fill=MUTED)
        for j, (lab, sec, col) in enumerate([("A, estimated", r["A"], GRAY), ("V, measured", r["V"], RED)]):
            mins = sec / 60
            c.rect(x0, y + j * 34, max(w * mins / top, 2), 26, fill=col, stroke=col, sw=0)
            c.text(x0 + max(w * mins / top, 2) + 6, y + j * 34 + 18, f"{mins:.0f} min ({lab})" if mins >= 10 else f"{mins:.1f} min ({lab})", size=12, anchor="start")
    c.text(380, 288, "V: shrunk graph, 512 searches per pass, bit-plane counters, compressed friend lists. 2 threads.", size=11.5, fill=MUTED)
    meta = dict(book="algorithms", chapter=33,
                caption="On a Chung-Lu graph with half a million people and on an R-MAT graph with four million ties, the baseline would need over two hours and over an hour; the fastest version took two and a half minutes and under a minute.",
                alt="Two pairs of horizontal bars in minutes. Chung-Lu with 500,000 people and 1.95 million ties: baseline about 138 minutes (estimated), fastest version 2.4 minutes. R-MAT with 2 to the 19 people and 3.98 million ties: baseline about 82 minutes (estimated), fastest version 0.6 minutes.",
                data={"rows": [{"graph": " ".join(tag(r)), "A_seconds_estimated": r["A"], "V_seconds": r["V"]} for r in rows]})
    return c, meta


# ---------------------------------------------------------------- 4. the pipeline
def pipeline():
    steps = [("A", "one search per person", "the textbook way", GRAY),
             ("B", "shrink the graph first", "fold twins and leaves", SKY),
             ("C", "share the passes", "512 searches per pass,\nbit-plane counters", BLUE),
             ("D", "both together", "weighted shared pass,\nbatched in search order", ORANGE),
             ("V", "squeeze the lists", "gap-coded friend lists", RED)]
    c = Canvas(760, 250, "Five versions of one computation",
               "Five boxes in a row, A to V, each naming what changes from the one before.")
    c.text(380, 28, "Same answer every time; only the route to it changes", size=15, weight="700")
    for k, (key, head, sub, col) in enumerate(steps):
        x = 20 + k * 148
        c.rect(x, 60, 128, 140, fill=col + "1a", stroke=col, sw=2, rx=10)
        c.text(x + 64, 96, key, size=28, weight="800", fill=col)
        c.text(x + 64, 128, head, size=12, weight="700")
        for i, line in enumerate(sub.split("\n")):
            c.text(x + 64, 150 + i * 16, line, size=11, fill=MUTED)
        if k:
            c.arrow((x - 18, 130), (x - 2, 130), color=MUTED, width=2)
    c.text(380, 232, "Every version must produce the same integers: distance sums, people reached, and the harmonic sum.", size=12, fill=MUTED)
    meta = dict(book="algorithms", chapter=33,
                caption="The five versions compared in this chapter. Each changes one thing about how the work is done, never what is computed, so every version is checked against the plain baseline.",
                alt="Five rounded boxes left to right with arrows between them: A, one search per person; B, shrink the graph first; C, share the passes, 512 searches per pass with bit-plane counters; D, both together; V, squeeze the lists with gap-coded friend lists.",
                data={"steps": [s[0] for s in steps]})
    return c, meta


# ---------------------------------------------------------------- 5. memory: where the bytes go
def memory():
    big = LAB[3]
    n, m = big["n"], big["m"]
    state = 3 * n * 64 * 2 / 1e6  # three arrays of 64 bytes (512 bits) per person, per thread, two threads
    plain = 2 * m * 4 / 1e6
    comp_lo, comp_hi = 2 * m * 1.3 / 1e6, 2 * m * 2.2 / 1e6
    bars = [("peak memory, measured", big["rss_mb"], RED, "measured"),
            ("search state, 2 threads (upper bound)", state, ORANGE, "arithmetic"),
            ("friend lists, plain 4 bytes", plain, BLUE, "arithmetic"),
            ("friend lists, gap-coded", comp_hi, SKY, "arithmetic")]
    c = Canvas(760, 330, "Where the memory goes",
               "Horizontal bars in megabytes for the half-million-person Chung-Lu run: measured peak, and the arithmetic sizes of its parts.")
    c.text(380, 28, "Chung-Lu, n = 500,000, m = 1.95M: megabytes", size=15, weight="700")
    x0, w, top = 300, 380, 330
    for k, (lab, mb, col, kind) in enumerate(bars):
        y = 56 + k * 52
        c.text(x0 - 12, y + 18, lab, size=12.5, anchor="end", weight="600")
        c.text(x0 - 12, y + 34, kind, size=11, anchor="end", fill=MUTED, italic=kind != "measured")
        c.rect(x0, y, w * mb / top, 28, fill=col, stroke=col, sw=0, dash="5 3" if kind != "measured" else None)
        label = f"{mb:.0f} MB" if k != 3 else f"{comp_lo:.0f} to {comp_hi:.0f} MB"
        c.text(x0 + w * mb / top + 6, y + 19, label, size=12.5, anchor="start", weight="700")
    c.text(380, 284, "Search state: 3 arrays x 64 bytes per person (512 bits), per thread, for all n people;", size=11.5, fill=MUTED)
    c.text(380, 302, "the shrunk graph has fewer people, so the real figure is lower. Friend lists: 2m entries.", size=11.5, fill=MUTED)
    meta = dict(book="algorithms", chapter=33,
                caption="The friend lists are not where the memory goes. The run's measured peak was 317 MB; the per-thread search state (three 512-bit words per person) can account for most of it, while the friend lists take 16 MB plain and 5 to 9 MB gap-coded. Only the peak was measured; the other bars are arithmetic.",
                alt=f"Four horizontal bars in megabytes. Peak memory, measured: 317. Search state for two threads, upper bound by arithmetic: {state:.0f}. Friend lists at 4 bytes per entry: {plain:.1f}. Friend lists gap-coded: {comp_lo:.1f} to {comp_hi:.1f}.",
                data={"peak_rss_mb": 317, "state_mb_upper": state, "lists_plain_mb": plain, "lists_gap_mb": [comp_lo, comp_hi]})
    return c, meta


# ---------------------------------------------------------------- 6. exact means the same integers
def exactness():
    adj = adjacency(10, EDGES)
    rows = []
    for s in range(10):
        d = bfs(adj, s)
        lv = [0] * (max(d) + 1)
        for x in d:
            if x > 0:
                lv[x] += 1
        farness = sum(d)
        reach = sum(1 for x in d if x > 0)
        harm = 0.0
        for L in range(1, len(lv)):
            harm += lv[L] / L
        rows.append((NAMES[s], lv[1:], farness, reach, harm))
    c = Canvas(760, 420, "What gets compared",
               "A table for the ten-person network: each person's counts per distance, distance sum, number reached and harmonic sum.")
    c.text(380, 28, "The check: every version must give these numbers exactly", size=15, weight="700")
    cols = ["person", "people at distance 1, 2, 3, 4", "distance sum", "reached", "harmonic sum"]
    xs = [70, 250, 450, 550, 660]
    for x, h in zip(xs, cols):
        c.text(x, 62, h, size=12, weight="700")
    for k, (nm, lv, far, reach, harm) in enumerate(rows):
        y = 88 + k * 28
        if k % 2 == 0:
            c.rect(20, y - 18, 720, 26, fill="#f3f4f6", stroke="none", sw=0)
        c.text(xs[0], y, nm, size=12)
        c.text(xs[1], y, "  ".join(str(v) for v in lv), size=12, mono=True)
        c.text(xs[2], y, str(far), size=12, mono=True)
        c.text(xs[3], y, str(reach), size=12, mono=True)
        c.text(xs[4], y, f"{harm:.4f}", size=12, mono=True)
    c.text(380, 380, "Sums are whole numbers, compared exactly. The harmonic sum is added in level order", size=11.5, fill=MUTED)
    c.text(380, 398, "(count at distance 1 / 1, then count at 2 / 2, ...), so every version rounds the same way.", size=11.5, fill=MUTED)
    meta = dict(book="algorithms", chapter=33,
                caption="Exact means identical. For each person every version must produce the same people-per-distance counts, the same whole-number distance sum and reach, and the same harmonic sum to the last bit, which holds because every version adds the same counts in the same order.",
                alt="A ten-row table, one row per person in the ten-person network, with columns for people at each distance, distance sum, number reached and harmonic sum. "
                    + " ".join(f"{nm}: {' '.join(map(str, lv))}, sum {far}, reached {reach}, harmonic {harm:.4f}." for nm, lv, far, reach, harm in rows),
                data={"rows": [{"person": nm, "levels": lv, "farness": far, "reached": reach, "harmonic": harm} for nm, lv, far, reach, harm in rows]})
    return c, meta


FIGURES = {"alg-cc-speedup-bars": speedup_bars, "alg-cc-ladder": ladder, "alg-cc-big-graphs": big_graphs,
           "alg-cc-pipeline": pipeline, "alg-cc-memory": memory, "alg-cc-exactness": exactness}

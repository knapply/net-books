"""Figures for chapter 4 of the algorithms book (trusting an implementation). Standard library only.

Every number drawn is computed here from small reference routines, so the pictures cannot drift from the arithmetic.
"""
import math
import random

import algkit as K
from figs import BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PAPER, PURPLE, RED, SKY, Canvas

CH = 4
GRAY, PALE = K.GRAY, K.PALE


def _dist_from(adj, s):
    d = {s: 0}
    q = [s]
    for u in q:
        for v in adj[u]:
            if v not in d:
                d[v] = d[u] + 1
                q.append(v)
    return d


# the two-island network of the "same question, two answers" figure: a path of four, and a pair apart
TWO = (["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay"], [(0, 1), (1, 2), (2, 3), (4, 5)])


def closeness_variants(adj, v, n):
    d = _dist_from(adj, v)
    r = len(d) - 1
    total = sum(d.values())
    a = r / total if total else 0.0
    b = a * r / (n - 1)
    c = 0.0 if r < n - 1 else a
    h = sum(1 / x for x in d.values() if x) / (n - 1)
    return [a, b, c, h]


# ------------------------------------------------------------------ 1. same question, two answers
def two_answers():
    names, edges = TWO
    n = len(names)
    adj = K.adjacency(n, edges)
    ben, eli = closeness_variants(adj, 1, n), closeness_variants(adj, 4, n)
    labels = ["Divide by the\npeople reached", "...and scale by the\nshare reached", "Unreached means\ninfinite: zero", "Add up 1 over\neach distance"]
    c = Canvas(920, 470, "Same question, four answers", "A network of two islands, and four closeness scores for Ben and Eli under four conventions.")
    pos = [(60, 90), (150, 60), (240, 90), (330, 60), (80, 220), (200, 220)]
    K.draw_graph(c, pos, edges, node=lambda i: {"fill": ORANGE + "88" if i in (1, 4) else PALE, "stroke": INK if i in (1, 4) else BLUE, "label": names[i][0]},
                 r=19, size=13, names=names)
    c.text(195, 30, "How central are Ben and Eli?", size=15, weight="700")
    c.text(195, 300, "Ben can reach 3 of the 5 others (distances 1, 1, 2).", size=12.5, fill=MUTED)
    c.text(195, 320, "Eli can reach only 1 of the 5 (distance 1).", size=12.5, fill=MUTED)
    x0, y0, w, h = 470, 70, 430, 250
    c.add(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{INK}" stroke-width="1.5"/>')
    for v in (0, 0.5, 1.0):
        yy = y0 + h - v * h
        c.add(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x0 + w}" y2="{yy:.1f}" stroke="{FAINT}" stroke-width="0.8"/>')
        c.text(x0 - 8, yy + 4, f"{v:.1f}", size=11.5, anchor="end")
    gw = w / 4
    for k in range(4):
        bx = x0 + k * gw + gw * 0.14
        for j, (val, col) in enumerate(((ben[k], ORANGE), (eli[k], PURPLE))):
            bh = val * h
            c.rect(bx + j * gw * 0.36, y0 + h - bh, gw * 0.32, bh, fill=col + "77", stroke=col, sw=1.3)
            c.text(bx + j * gw * 0.36 + gw * 0.16, y0 + h - bh - 5, f"{val:.2f}", size=11.5, weight="700", fill=INK)
        for li, line in enumerate(labels[k].split("\n")):
            c.text(x0 + k * gw + gw / 2, y0 + h + 20 + li * 16, line, size=11.5)
    c.rect(x0 + 40, 36, 14, 12, fill=ORANGE + "77", stroke=ORANGE)
    c.text(x0 + 60, 47, "Ben", size=12.5, anchor="start")
    c.rect(x0 + 120, 36, 14, 12, fill=PURPLE + "77", stroke=PURPLE)
    c.text(x0 + 140, 47, "Eli", size=12.5, anchor="start")
    c.text(460, 424, f"First convention: Eli ({eli[0]:.2f}) looks more central than Ben ({ben[0]:.2f}). The other three: Ben is ahead.", size=13.5, weight="600")
    c.text(460, 448, "Nothing is buggy. Each tool made an honest choice about people it cannot reach.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="One question (how close is each person to everyone else?) on a network with two islands, answered four ways. Two honest tools can print different numbers, and even rank Ben and Eli in a different order, without either having a bug.",
                alt=f"On the left, a path of four people (Ana, Ben, Cleo, Dev) and a separate pair (Eli, Fay). On the right, a bar chart with four groups of two bars, for Ben and Eli. First group, Ben {ben[0]:.2f} and Eli {eli[0]:.2f}. Second group, Ben {ben[1]:.2f} and Eli {eli[1]:.2f}. Third group, both 0.00. Fourth group, Ben {ben[3]:.2f} and Eli {eli[3]:.2f}.",
                data={"ben": ben, "eli": eli, "conventions": labels})
    return c, meta


# ------------------------------------------------------------------ 2. the checking recipe
def recipe():
    c = Canvas(920, 330, "How a check works", "A diagram: the same input goes to your routine and to a trusted reference, and the two answers are compared within a tolerance.")
    def box(x, y, w, h, text, col, sub=None):
        c.rect(x, y, w, h, fill=col + "18", stroke=col, sw=2, rx=12)
        c.text(x + w / 2, y + h / 2 + (0 if not sub else -6), text, size=15, weight="700")
        if sub:
            c.text(x + w / 2, y + h / 2 + 16, sub, size=12, fill=MUTED)
    box(30, 125, 150, 80, "Same input", BLUE, "a small network")
    box(300, 50, 190, 80, "Your routine", ORANGE, "the thing being tested")
    box(300, 200, 190, 80, "Reference", PURPLE, "a tool you trust, or a hand answer")
    c.arrow((180, 150), (298, 92), color=MUTED, width=2.5)
    c.arrow((180, 180), (298, 238), color=MUTED, width=2.5)
    box(610, 125, 150, 80, "Compare", GREEN, "within a tolerance")
    c.arrow((490, 92), (608, 150), color=MUTED, width=2.5)
    c.arrow((490, 238), (608, 180), color=MUTED, width=2.5)
    c.arrow((760, 165), (800, 165), color=MUTED, width=2.5)
    c.text(860, 150, "agree:", size=13.5, weight="700", fill=GREEN)
    c.text(860, 168, "carry on", size=13, fill=GREEN)
    c.text(860, 205, "differ:", size=13.5, weight="700", fill=RED)
    c.text(860, 223, "find out why", size=13, fill=RED)
    c.text(460, 312, "A difference is a question, not a verdict. Either side, or the input, or the convention, can be the one that is off.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="The basic move of testing: give two independent sources the same question, compare the answers, and treat any difference as something to explain.",
                alt="Four boxes joined by arrows. A blue box, Same input, sends arrows to an orange box, Your routine, and a purple box, Reference. Both of those send arrows to a green box, Compare, which leads to two outcomes: agree, carry on; differ, find out why.",
                data={})
    return c, meta


# ------------------------------------------------------------------ 3. the hand check
def hand_check():
    names = ["Ana", "Ben", "Cleo", "Dev", "Eli"]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
    adj = K.adjacency(5, edges)
    deg = [len(a) for a in adj]
    da = _dist_from(adj, 0)
    pos = [(60, 150), (180, 70), (180, 230), (310, 150), (430, 150)]
    c = Canvas(920, 400, "A case you can check on paper", "A five-person network with its degrees and the distances from Ana worked out by hand.")
    K.draw_graph(c, pos, edges, node=lambda i: {"fill": ORANGE + "88" if i == 0 else PALE, "stroke": INK if i == 0 else BLUE, "label": names[i][0]}, r=21, size=14, names=names)
    c.text(250, 40, "Five people, five ties", size=15, weight="700")
    rows = [[names[i], str(deg[i]), str(da[i]), "1" if i != 2 else "1", ""] for i in range(5)]
    # shortest routes from Ana: count by hand = counts of equal-length ways
    cnt = {0: 1}
    for v in sorted(da, key=lambda x: da[x]):
        if v != 0:
            cnt[v] = sum(cnt[u] for u in adj[v] if da[u] == da[v] - 1)
    rows = [[names[i], str(deg[i]), str(da[i]), str(cnt[i])] for i in range(5)]
    K.table(c, 500, 60, ["Person", "Ties", "Steps from Ana", "Shortest routes"], rows, [80, 60, 130, 140], row_h=32, size=13)
    c.lines(500, 285, [f"Ties add up to {sum(deg)}, which is 2 x {len(edges)}: each tie is", "counted at both ends.", "Dev is 2 steps away by two routes (through Ben or", "Cleo), and Eli is 3 steps away by the same two."], size=12.5, fill=MUTED, gap=1.4)
    c.text(460, 372, "With five people you can check every number with a pencil. Do that once, then ask the routine for the same numbers.", size=13.5, weight="600")
    meta = dict(chapter=CH,
                caption="A tiny case with answers worked out by hand. If a routine cannot get these right, nothing larger is worth running.",
                alt=f"A five-person network: Ana is tied to Ben and to Cleo; Ben and Cleo are each tied to Dev; Dev is tied to Eli. A table lists each person's number of ties ({', '.join(str(d) for d in deg)}), the steps from Ana ({', '.join(str(da[i]) for i in range(5))}) and the number of shortest routes from Ana ({', '.join(str(cnt[i]) for i in range(5))}).",
                data={"degrees": deg, "distance_from_ana": [da[i] for i in range(5)], "route_counts": [cnt[i] for i in range(5)]})
    return c, meta


# ------------------------------------------------------------------ 4. properties that must always hold
def properties():
    kite_adj = K.adjacency(10, K.EDGES)
    n = 10
    d = [_dist_from(kite_adj, s) for s in range(n)]
    sym = all(d[a][b] == d[b][a] for a in range(n) for b in range(n))
    tri = all(d[a][c] <= d[a][b] + d[b][c] for a in range(n) for b in range(n) for c in range(n))
    deg_sum = sum(len(a) for a in kite_adj)
    # relabel: rotate names, recompute, compare
    perm = [(i * 3 + 1) % n for i in range(n)]
    edges2 = [(perm[a], perm[b]) for a, b in K.EDGES]
    adj2 = K.adjacency(n, edges2)
    d2 = [_dist_from(adj2, s) for s in range(n)]
    relabel = all(d[a][b] == d2[perm[a]][perm[b]] for a in range(n) for b in range(n))
    # adding a tie never lengthens a distance
    edges3 = K.EDGES + [(0, 9)]
    adj3 = K.adjacency(n, edges3)
    d3 = [_dist_from(adj3, s) for s in range(n)]
    mono = all(d3[a][b] <= d[a][b] for a in range(n) for b in range(n))
    assert sym and tri and relabel and mono and deg_sum == 2 * len(K.EDGES)
    cards = [("Relabeling changes nothing", "Rename everybody and every distance is the same, just filed under the new names.", f"checked on the friendship network: {n * n} distances, all match", BLUE),
             ("Distances are symmetric", "In an undirected network, the way from A to B is as long as from B to A.", "checked: all 100 pairs", GREEN),
             ("No shortcuts through a third person", "The distance from A to C never exceeds the distance from A to B plus B to C.", "checked: all 1,000 triples", ORANGE),
             ("A new tie never hurts", "Add one tie and no distance gets longer.", "added Ana-Jo: 100 distances, none longer; Ana to Jo fell from 4 to 1", PURPLE),
             ("Degrees add up to twice the ties", "Every tie has two ends, so the degrees sum to twice the number of ties.", f"checked: degrees sum to {deg_sum}, ties are {len(K.EDGES)}", RED),
             ("Same input, same output", "Run it twice, or on four threads, and the answer is identical.", "a property of the routine, not of the data", SKY)]
    c = Canvas(920, 440, "Things that must always be true", "Six cards, each a property a correct graph routine must satisfy for any network.")
    for i, (head, body, check, col) in enumerate(cards):
        x, y = 20 + (i % 3) * 300, 20 + (i // 3) * 210
        c.rect(x, y, 280, 190, fill=col + "14", stroke=col, sw=2, rx=12)
        c.text(x + 14, y + 30, head, size=14.5, weight="700", anchor="start")
        words, line, lines = body.split(), "", []
        for wd in words:
            if len(line) + len(wd) > 36:
                lines.append(line)
                line = wd
            else:
                line = (line + " " + wd).strip()
        lines.append(line)
        c.lines(x + 14, y + 62, lines, size=12.5, fill=INK)
        words, line, lines = check.split(), "", []
        for wd in words:
            if len(line) + len(wd) > 38:
                lines.append(line)
                line = wd
            else:
                line = (line + " " + wd).strip()
        lines.append(line)
        c.lines(x + 14, y + 138, lines, size=12, fill=col, weight="700")
    meta = dict(chapter=CH,
                caption="Property tests check rules that hold for every network, so they need no hand-worked answer. The notes under each card are checks actually run on the friendship network.",
                alt="Six cards in two rows. Relabeling changes nothing; distances are symmetric; no shortcuts through a third person; a new tie never hurts; degrees add up to twice the ties; same input gives the same output. Each carries a note on a check made on the ten-person friendship network.",
                data={"checks": [c_[0] for c_ in cards]})
    return c, meta


# ------------------------------------------------------------------ 5. tolerance
def tolerance():
    a, b = 0.1 + 0.2, 0.3
    diff = abs(a - b)
    c = Canvas(920, 420, "Why 'equal' needs a tolerance", "A number line showing that 0.1 plus 0.2 differs from 0.3 by a tiny amount, which is far smaller than a real discrepancy.")
    c.text(460, 34, "Computers keep numbers in binary, so 0.1 + 0.2 is not exactly 0.3", size=15, weight="700")
    c.text(460, 74, f"0.1 + 0.2  prints as  {a!r}", size=15, mono=True)
    c.text(460, 102, f"0.3        prints as  {b!r}", size=15, mono=True)
    c.text(460, 130, f"difference: {diff:.3e}", size=14, fill=MUTED)
    y = 230
    x0, x1 = 120, 800
    c.add(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{INK}" stroke-width="2"/>')
    ticks = [(1e-17, "0.00000000000000001"), (1e-12, ""), (1e-8, "1e-8"), (1e-4, ""), (1e-2, "0.01"), (1, "1")]
    def X(v):
        return x0 + (math.log10(v) + 17) / 17 * (x1 - x0)
    for e in range(-17, 1, 2):
        c.add(f'<line x1="{X(10 ** e):.1f}" y1="{y - 6}" x2="{X(10 ** e):.1f}" y2="{y + 6}" stroke="{INK}" stroke-width="1.2"/>')
        c.text(X(10 ** e), y + 26, f"1e{e}", size=11.5)
    c.text(460, y + 56, "size of the difference between two answers (log scale)", size=12.5, fill=MUTED)
    tol = 1e-9
    c.rect(x0, y - 44, X(tol) - x0, 34, fill=GREEN + "22", stroke=GREEN, sw=1.6, rx=4)
    c.text((x0 + X(tol)) / 2, y - 22, "rounding noise: accept", size=12.5, fill=GREEN, weight="700")
    c.rect(X(tol), y - 44, x1 - X(tol), 34, fill=RED + "18", stroke=RED, sw=1.6, rx=4)
    c.text((X(tol) + x1) / 2, y - 22, "too big to be rounding: investigate", size=12.5, fill=RED, weight="700")
    c.add(f'<circle cx="{X(diff):.1f}" cy="{y}" r="8" fill="{GREEN}" stroke="{INK}" stroke-width="1.6"/>')
    c.text(X(diff), y + 90 - 20, "0.1 + 0.2 vs 0.3", size=12, weight="700")
    c.add(f'<circle cx="{X(0.01):.1f}" cy="{y}" r="8" fill="{RED}" stroke="{INK}" stroke-width="1.6"/>')
    c.text(X(0.01), y + 70, "a wrong closeness", size=12, weight="700")
    c.text(460, 394, "Typical rule: two answers agree if they differ by less than about a billionth of their size, relative to the larger one.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption=f"The difference between 0.1 + 0.2 and 0.3 is about {diff:.1e}, which is rounding, not error. A tolerance draws the line between that and a real discrepancy such as a score that is off in the second decimal place.",
                alt="A horizontal line from 1e-17 to 1 on a log scale. A green zone on the left, up to a billionth, is labeled rounding noise: accept. A red zone on the right is labeled too big to be rounding. A green dot sits far left for 0.1 plus 0.2 versus 0.3; a red dot sits at 0.01 for a wrong closeness score.",
                data={"sum": a, "target": b, "difference": diff, "tolerance": tol})
    return c, meta


# ------------------------------------------------------------------ 6. fuzzing reaches the odd corners
def fuzz():
    rng = random.Random(3)
    N = 4000
    cats = {"no ties at all": 0, "someone with no friends": 0, "two or more islands": 0, "a person tied to themselves": 0, "the same tie listed twice": 0, "all of those at once": 0}
    forced = dict.fromkeys(cats, 0)

    def random_graph(force):
        n = rng.randint(1, 8)
        pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
        es = rng.sample(pairs, rng.randint(0, len(pairs))) if pairs else []  # a typical random generator: distinct pairs only
        if force:
            if rng.random() < 0.5 and n >= 2:
                es.append((0, 0))
            if es and rng.random() < 0.5:
                es.append(es[0])
            if n >= 3:
                es = [e for e in es if e[0] != n - 1 and e[1] != n - 1] or es  # isolate the last person
        return n, es

    def tally(n, es, into):
        simple = {frozenset(e) for e in es if e[0] != e[1]}
        deg = [0] * n
        for e in simple:
            for v in e:
                deg[v] += 1
        adj = [set() for _ in range(n)]
        for e in simple:
            a, b = tuple(e)
            adj[a].add(b)
            adj[b].add(a)
        seen, comps = set(), 0
        for s in range(n):
            if s not in seen:
                comps += 1
                st = [s]
                seen.add(s)
                while st:
                    u = st.pop()
                    for v in adj[u]:
                        if v not in seen:
                            seen.add(v)
                            st.append(v)
        flags = {"no ties at all": not es, "someone with no friends": any(d == 0 for d in deg),
                 "two or more islands": comps > 1, "a person tied to themselves": any(a == b for a, b in es),
                 "the same tie listed twice": len({tuple(sorted(e)) for e in es}) < len(es)}
        flags["all of those at once"] = all(flags[k] for k in ("someone with no friends", "a person tied to themselves", "the same tie listed twice"))
        for k, v in flags.items():
            into[k] += bool(v)
    for _ in range(N):
        tally(*random_graph(False), cats)
        tally(*random_graph(True), forced)
    c = Canvas(920, 420, "A typical random generator misses the odd corners", "Bars showing how many of 4,000 random tiny networks contain each awkward feature, for plain random generation and for generation that deliberately adds odd features.")
    x0, y0, w = 330, 60, 520
    c.text(460, 30, "Share of 4,000 tiny networks containing each feature", size=15, weight="700")
    for i, (k, v) in enumerate(cats.items()):
        yy = y0 + i * 50
        c.text(x0 - 12, yy + 22, k, size=13, anchor="end")
        for j, (val, col) in enumerate(((v, BLUE), (forced[k], ORANGE))):
            bw = w * val / N
            c.rect(x0, yy + j * 20, max(bw, 1), 17, fill=col + "77", stroke=col, sw=1.2)
            c.text(x0 + bw + 8, yy + j * 20 + 13, f"{100 * val / N:.1f}%", size=12, anchor="start")
    c.rect(x0, 372, 14, 12, fill=BLUE + "77", stroke=BLUE)
    c.text(x0 + 20, 383, "typical random generator", size=12.5, anchor="start")
    c.rect(x0 + 230, 372, 14, 12, fill=ORANGE + "77", stroke=ORANGE)
    c.text(x0 + 250, 383, "random plus deliberate odd features", size=12.5, anchor="start")
    c.text(460, 410, "A fuzzer is only as good as the corners it can reach. Say what odd inputs it should add.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="Fuzzing means testing with many random inputs. Blue bars: how often tiny networks from a typical random generator (distinct pairs only) contain each awkward feature. Orange bars: the same when the generator is told to add self-ties, repeats and a lonely person on purpose.",
                alt=f"Six pairs of horizontal bars, one pair per feature: no ties at all, someone with no friends, two or more islands, a person tied to themselves, the same tie listed twice, and all of those at once. The blue bars for the typical generator are empty for self-ties, repeated ties and all of those at once ({100 * cats['a person tied to themselves'] / N:.0f} percent each), and the orange bars for deliberate generation are long.",
                data={"plain": cats, "deliberate": forced, "networks": N})
    return c, meta


# ------------------------------------------------------------------ 7. the ladder
def ladder():
    c = Canvas(920, 420, "Layers of checking", "Five stacked bands, from hand-checked cases at the bottom to regression tests at the top, with what each one catches.")
    rungs = [("Regression tests", "a past bug never comes back", PURPLE),
             ("Fuzzing", "crashes and odd inputs nobody thought of", ORANGE),
             ("Reference tools", "wrong answers on realistic networks", GREEN),
             ("Property tests", "broken rules, on many networks at once", BLUE),
             ("Hand-checked tiny cases", "plain mistakes, and misunderstanding the question", RED)]
    for i, (name, what, col) in enumerate(rungs):
        y = 30 + i * 74
        inset = i * 24
        c.rect(70 + inset, y, 780 - 2 * inset, 62, fill=col + "18", stroke=col, sw=2, rx=10)
        c.text(90 + inset, y + 28, name, size=16, weight="700", anchor="start")
        c.text(90 + inset, y + 50, "catches: " + what, size=13, anchor="start", fill=MUTED)
    c.text(460, 410, "Start at the bottom. Each layer is cheap to add and catches something the layer below cannot.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="No single check is enough. Together they cover plain mistakes, broken rules, disagreement with other tools, strange inputs and old bugs coming back.",
                alt="Five horizontal bands stacked like a pyramid, widest at the bottom. From the bottom: hand-checked tiny cases, property tests, reference tools, fuzzing, and regression tests at the top. Each band names what it catches.",
                data={"layers": [r[0] for r in rungs]})
    return c, meta


# ------------------------------------------------------------------ 8. where careful tools differ
def conventions():
    adj = K.adjacency(5, [(0, 1), (1, 2), (2, 3), (3, 4)])
    d = _dist_from(adj, 2)
    raw_b = 4  # middle of a path of 5: 2 x 2 pairs
    norm_b = raw_b / ((5 - 1) * (5 - 2) / 2)
    rows = [["A person tied to themselves", "degree counts it once: 1", "counts it twice: 2", "a loop has two ends"],
            ["Closeness with an unreachable person", "ignore them", "score 0, or add 1/distance", "no distance exists"],
            ["Clustering of someone with 1 friend", "0", "not defined (empty)", "no pair of friends to test"],
            ["Betweenness of the middle of 5 in a row", f"raw count: {raw_b}", f"scaled to 0 to 1: {norm_b:.2f}", "same routes, different units"],
            ["Which shortest route to list", "first in alphabetical order", "first in the order typed", "ties need a rule"],
            ["Two ties between the same pair", "count as one", "count as two", "multigraph or not"]]
    c = Canvas(960, 420, "Places where careful tools differ", "A table of six common conventions with the two answers each tool might give.")
    K.table(c, 20, 44, ["Question", "One tool says", "Another says", "Why they can differ"], rows, [270, 230, 230, 210], row_h=46, size=12.5)
    c.text(480, 30, "Six places where two correct tools can print different numbers", size=15, weight="700")
    c.text(480, 396, "Before comparing two tools, line up the conventions. After, any difference left is worth chasing.", size=13, fill=MUTED)
    meta = dict(chapter=CH,
                caption="Disagreement is not always a bug. These six questions have more than one defensible answer, so a careful comparison fixes the convention first.",
                alt="A table with six rows and four columns: the question, what one tool says, what another says, and why they can differ. Rows cover self-ties, closeness with unreachable people, clustering for a person with one friend, betweenness raw or scaled, the choice among tied shortest routes, and repeated ties between a pair.",
                data={"rows": rows, "path5_middle_betweenness": [raw_b, norm_b]})
    return c, meta


FIGURES = {
    "alg-trust-two-answers": two_answers,
    "alg-trust-recipe": recipe,
    "alg-trust-hand-check": hand_check,
    "alg-trust-properties": properties,
    "alg-trust-tolerance": tolerance,
    "alg-trust-fuzz": fuzz,
    "alg-trust-ladder": ladder,
    "alg-trust-conventions": conventions,
}

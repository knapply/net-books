"""Figures for the link prediction chapter (chapter 25).

Standard library only. Every number drawn is computed here from the CSV files in
books/sna/data/karate with the same splits, scores and tie rules the chapter's code uses
(the fixed scramble `hide_key`, 20 percent of the ties hidden, seeds 1 to 100).
"""
import csv
import math
from pathlib import Path

from figs import BLUE, FAINT, INK, MUTED, ORANGE, PAPER, RED, Canvas

DATA = Path(__file__).resolve().parent.parent / "books" / "sna" / "data"
N = 34
SCORES = ["CN", "Jaccard", "AA", "RA", "PA", "Katz", "Path", "Block", "Embed2", "Embed3", "Embed6"]


def read(name, file):
    with open(DATA / name / file, newline="") as f:
        return list(csv.DictReader(f))


def karate_ties():
    return [tuple(sorted((int(r["source"]), int(r["target"])))) for r in read("karate", "edges.csv")]


def adjacency(pairs, n=N):
    a = [[0.0] * n for _ in range(n)]
    for u, v in pairs:
        a[u - 1][v - 1] = a[v - 1][u - 1] = 1.0
    return a


def matmul(a, b):
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def jacobi(a, sweeps=60):
    """Eigenvalues and eigenvectors (as columns) of a symmetric matrix, by cyclic Jacobi rotations."""
    n = len(a)
    a = [row[:] for row in a]
    v = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for _ in range(sweeps):
        off = sum(a[i][j] ** 2 for i in range(n) for j in range(i + 1, n))
        if off < 1e-22:
            break
        for p in range(n - 1):
            for q in range(p + 1, n):
                if abs(a[p][q]) < 1e-300:
                    continue
                theta = (a[q][q] - a[p][p]) / (2 * a[p][q])
                t = (1 if theta >= 0 else -1) / (abs(theta) + math.sqrt(theta * theta + 1))
                c = 1 / math.sqrt(t * t + 1)
                s = t * c
                for k in range(n):
                    akp, akq = a[k][p], a[k][q]
                    a[k][p], a[k][q] = c * akp - s * akq, s * akp + c * akq
                for k in range(n):
                    apk, aqk = a[p][k], a[q][k]
                    a[p][k], a[q][k] = c * apk - s * aqk, s * apk + c * aqk
                for k in range(n):
                    vkp, vkq = v[k][p], v[k][q]
                    v[k][p], v[k][q] = c * vkp - s * vkq, s * vkp + c * vkq
    return [a[i][i] for i in range(n)], v


def inverse(m):
    n = len(m)
    w = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(w[r][c]))
        w[c], w[piv] = w[piv], w[c]
        d = w[c][c]
        w[c] = [x / d for x in w[c]]
        for r in range(n):
            if r != c and w[r][c] != 0:
                f = w[r][c]
                w[r] = [x - f * y for x, y in zip(w[r], w[c])]
    return [row[n:] for row in w]


def hops(a):
    n = len(a)
    nbrs = [[j for j in range(n) if a[i][j] > 0] for i in range(n)]
    out = []
    for s in range(n):
        dist = {s: 0}
        queue = [s]
        for u in queue:
            for w in nbrs[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    queue.append(w)
        out.append([dist.get(t, n) for t in range(n)])
    return out


def all_scores(a, beta=0.05):
    n = len(a)
    deg = [sum(r) for r in a]
    common = matmul(a, a)
    aa = matmul([[a[i][w] / math.log(max(deg[w], 2)) for w in range(n)] for i in range(n)], a)
    ra = matmul([[a[i][w] / max(deg[w], 1) for w in range(n)] for i in range(n)], a)
    inv = inverse([[(1.0 if i == j else 0.0) - beta * a[i][j] for j in range(n)] for i in range(n)])
    d = hops(a)
    vals, vecs = jacobi(a)
    by_size = sorted(range(n), key=lambda i: -abs(vals[i]))

    def low_rank(k):
        top = by_size[:k]
        return [[sum(vecs[i][t] * vals[t] * vecs[j][t] for t in top) for j in range(n)] for i in range(n)]

    second = sorted(range(n), key=lambda i: vals[i])[-2]
    vec = [vecs[i][second] for i in range(n)]
    lead = max(range(n), key=lambda i: abs(vec[i]))
    flip = 1 if vec[lead] > 0 else -1
    z = [1 if flip * x > 1e-8 else 0 for x in vec]
    size = [z.count(0), z.count(1)]
    tie = [[sum(a[i][j] for i in range(n) for j in range(n) if z[i] == p and z[j] == q) for q in (0, 1)] for p in (0, 1)]
    dens = [[tie[p][q] / max(size[p] * size[q] - (size[p] if p == q else 0), 1) for q in (0, 1)] for p in (0, 1)]
    return {
        "CN": common,
        "Jaccard": [[common[i][j] / (deg[i] + deg[j] - common[i][j]) if deg[i] + deg[j] - common[i][j] > 0 else 0.0
                     for j in range(n)] for i in range(n)],
        "AA": aa, "RA": ra,
        "PA": [[deg[i] * deg[j] for j in range(n)] for i in range(n)],
        "Katz": [[inv[i][j] - (1.0 if i == j else 0.0) for j in range(n)] for i in range(n)],
        "Path": [[-d[i][j] for j in range(n)] for i in range(n)],
        "Block": [[dens[z[i]][z[j]] for j in range(n)] for i in range(n)],
        "Embed2": low_rank(2), "Embed3": low_rank(3), "Embed6": low_rank(6),
    }


def hide_key(u, v, seed):
    x = (u * 7919 + v * 6841 + seed * 104729 + 12345) % 1000003
    x = (x * x + 12345) % 1000003
    x = (x * x + 777) % 1000003
    return (x * 48271) % 1000003


def hidden(pairs, seed, frac):
    order = sorted(range(len(pairs)), key=lambda i: (hide_key(pairs[i][0], pairs[i][1], seed), i))
    return set(order[:round(frac * len(pairs))])


def auc_and_precision(score, hit):
    s = [round(x, 10) for x in score]
    pos = [x for x, h in zip(s, hit) if h]
    neg = [x for x, h in zip(s, hit) if not h]
    won = sum(1.0 if p > q else 0.5 if p == q else 0.0 for p in pos for q in neg) / (len(pos) * len(neg))
    k = len(pos)
    cut = sorted(s, reverse=True)[k - 1]
    above = sum(1 for x in s if x > cut)
    tied = sum(1 for x in s if x == cut)
    hits_above = sum(1 for x, h in zip(s, hit) if h and x > cut)
    hits_tied = sum(1 for x, h in zip(s, hit) if h and x == cut)
    return won, (hits_above + hits_tied * (k - above) / tied) / k, k / len(s)


def evaluate(seeds=range(1, 101), frac=0.2):
    pairs = karate_ties()
    truth = adjacency(pairs)
    runs = {name: [] for name in SCORES}
    chance = []
    for seed in seeds:
        hid = hidden(pairs, seed, frac)
        train = adjacency([p for i, p in enumerate(pairs) if i not in hid])
        sc = all_scores(train)
        cells = [(i, j) for i in range(N) for j in range(i + 1, N) if train[i][j] == 0]
        hit = [truth[i][j] > 0 for i, j in cells]
        for name in SCORES:
            a, p, base = auc_and_precision([sc[name][i][j] for i, j in cells], hit)
            runs[name].append((a, p))
        chance.append(base)
    return runs, sum(chance) / len(chance)


def stats(xs):
    m = sum(xs) / len(xs)
    return m, math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def score_panels():
    runs, chance_p = evaluate()
    labels = {"CN": "common neighbours", "Jaccard": "Jaccard", "AA": "Adamic-Adar", "RA": "resource allocation",
              "PA": "degree product", "Katz": "Katz", "Path": "shortest path", "Block": "two-block model",
              "Embed2": "embedding, 2 dims", "Embed3": "embedding, 3 dims", "Embed6": "embedding, 6 dims"}
    c = Canvas(900, 470, "Link prediction scores on the karate club",
               "Two dot-and-whisker panels for eleven scores over 100 random splits of the karate club with 20 percent of the ties hidden. Left: mean area under the curve with one standard deviation. Right: mean precision at k, with the chance level marked.")
    top, step = 70, 31
    height = step * len(SCORES)
    data = {}
    panels = [(280, 270, 0.4, 0.9, 0, "Area under the curve (chance = 0.5)", 0.5),
              (640, 220, 0.0, 0.4, 1, "Precision at k (chance = %.3f)" % chance_p, chance_p)]
    for x0, w, lo, hi, idx, title, chance in panels:
        c.text(x0 + w / 2, 38, title, size=14, weight="600")
        for t in range(int(round(lo * 10)), int(round(hi * 10)) + 1):
            v = t / 10
            x = x0 + (v - lo) / (hi - lo) * w
            c.add(f'<line x1="{x:.1f}" y1="{top - 12}" x2="{x:.1f}" y2="{top + height - 14}" stroke="{FAINT}" stroke-width="1"/>')
            c.text(x, top + height + 6, f"{v:.1f}", size=12, fill=MUTED)
        cx = x0 + (chance - lo) / (hi - lo) * w
        c.add(f'<line x1="{cx:.1f}" y1="{top - 12}" x2="{cx:.1f}" y2="{top + height - 14}" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/>')
        for r, name in enumerate(SCORES):
            y = top + r * step
            m, sd = stats([run[idx] for run in runs[name]])
            data.setdefault(name, {})["auc" if idx == 0 else "p_at_k"] = round(m, 3)
            if idx == 0:
                data[name]["sd"] = round(sd, 3)
                x1, x2 = x0 + (m - sd - lo) / (hi - lo) * w, x0 + (m + sd - lo) / (hi - lo) * w
                c.add(f'<line x1="{x1:.1f}" y1="{y}" x2="{x2:.1f}" y2="{y}" stroke="{INK}" stroke-width="2"/>')
                c.text(x0 - 12, y + 5, labels[name], size=13, anchor="end")
            model = name in ("Block", "Embed2", "Embed3", "Embed6")
            c.node(x0 + (m - lo) / (hi - lo) * w, y, r=6.5, fill=ORANGE if model else BLUE, stroke=INK,
                   shape="square" if model else "circle", sw=1.5)
    c.text(450, 452, "Circles: scores from neighbourhoods and paths. Squares: scores from a model or an embedding fitted to the training ties.",
           size=12.5, fill=MUTED)
    best = max(SCORES, key=lambda s: data[s]["auc"])
    under = [labels[s] for s in SCORES if data[s]["p_at_k"] < chance_p]
    below = ("all to the right of the dashed chance line at %.3f" % chance_p if not under else
             "all to the right of the dashed chance line at %.3f except %s, which lies to its left" % (chance_p, " and ".join(under)))
    meta = dict(
        chapter=25,
        caption="Mean area under the ROC curve (with one standard deviation across splits) and mean precision at k for eleven scores on 100 splits of the karate club, 20 percent of the ties hidden each time. The dashed line is chance.",
        alt="Two panels listing eleven scores from common neighbours down to a six-dimension embedding. In the left panel the dots for the mean area under the curve lie between %.2f and %.2f, every one to the right of the dashed chance line at 0.5, and each has a horizontal bar about 0.05 to 0.08 long on either side. The highest dot is the %s at %.3f. In the right panel the dots for precision at k lie between %.2f and %.2f, %s." % (
            min(d["auc"] for d in data.values()), max(d["auc"] for d in data.values()), labels[best], data[best]["auc"],
            min(d["p_at_k"] for d in data.values()), max(d["p_at_k"] for d in data.values()), below),
        data={"splits": 100, "hidden_fraction": 0.2, "chance_precision": round(chance_p, 4), "scores": data})
    return c, meta


def laplacian_embedding():
    rows = read("karate", "nodes.csv")
    side = [0 if r["faction"] == "Mr. Hi" else 1 for r in rows]
    a = adjacency(karate_ties())
    deg = [sum(r) for r in a]
    lap = [[(1.0 if i == j else 0.0) - a[i][j] / math.sqrt(deg[i] * deg[j]) for j in range(N)] for i in range(N)]
    vals, vecs = jacobi(lap)
    order = sorted(range(N), key=lambda i: vals[i])
    f2 = [vecs[i][order[1]] / math.sqrt(deg[i]) for i in range(N)]
    f3 = [vecs[i][order[2]] / math.sqrt(deg[i]) for i in range(N)]
    if sum(1 for i in range(N) if (f2[i] > 0) == (side[i] == 1)) < 17:
        f2 = [-x for x in f2]
    return side, f2, f3, vals, order


def embedding_scatter():
    side, f2, f3, vals, order = laplacian_embedding()
    c = Canvas(780, 520, "Karate club in two spectral coordinates",
               "A scatter plot of the 34 karate club members placed by the second and third eigenvectors of the normalised Laplacian, coloured by the side each took when the club split.")
    x0, y0, w, h = 70, 56, 660, 410
    lx, hx = min(f2) - 0.02, max(f2) + 0.02
    ly, hy = min(f3) - 0.02, max(f3) + 0.02

    def px(v):
        return x0 + (v - lx) / (hx - lx) * w

    def py(v):
        return y0 + h - (v - ly) / (hy - ly) * h

    c.rect(x0, y0, w, h, fill=PAPER, stroke=FAINT, sw=1.2)
    zx = px(0)
    c.add(f'<line x1="{zx:.1f}" y1="{y0}" x2="{zx:.1f}" y2="{y0 + h}" stroke="{FAINT}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    wrong = [i + 1 for i in range(N) if (f2[i] > 0) != (side[i] == 1)]
    for i in range(N):
        c.node(px(f2[i]), py(f3[i]), r=8, fill=BLUE if side[i] == 0 else ORANGE, stroke=INK,
               shape="circle" if side[i] == 0 else "square", sw=1.4)
    for i, (dx, dy) in {0: (12, -8), 33: (-4, 24), 32: (4, -14), 2: (12, 4), 8: (12, -6)}.items():
        c.text(px(f2[i]) + dx, py(f3[i]) + dy, str(i + 1), size=12, anchor="start", weight="600")
    c.text(x0 + w / 2, y0 + h + 28, "second eigenvector (Fiedler vector), divided by the square root of the degree; third eigenvector up the side",
           size=13, fill=MUTED)
    c.text(x0, y0 - 18, "Mr. Hi's side: circles", size=13, anchor="start", fill=BLUE, weight="600")
    c.text(x0 + w, y0 - 18, "the officer's side: squares", size=13, anchor="end", fill=ORANGE, weight="600")
    c.text(x0 + w / 2, 508, "The dashed line is where the second coordinate is zero. Members %s land on the other side." % " and ".join(str(x) for x in wrong),
           size=12.5, fill=MUTED)
    meta = dict(
        chapter=25,
        caption="The karate club placed by two eigenvectors of its normalised Laplacian, coloured by the side each member took. One coordinate nearly separates the two sides.",
        alt="A scatter plot of 34 points. Blue circles for the 17 members on Mr. Hi's side and orange squares for the 17 members on the officer's side, separated by a dashed vertical line, with the circles mostly on one side of it and the squares on the other. %d points lie on the wrong side of the line: members %s." % (
            len(wrong), ", ".join(str(x) for x in wrong)),
        data={"second_eigenvalue": round(vals[order[1]], 4), "third_eigenvalue": round(vals[order[2]], 4),
              "wrong_side": wrong,
              "points": [[i + 1, round(f2[i], 4), round(f3[i], 4), side[i]] for i in range(N)]})
    return c, meta


FIGURES = {
    "prediction-scores": score_panels,
    "prediction-embedding": embedding_scatter,
}

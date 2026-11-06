"""Small layout helpers for the figures. Standard library only, deterministic."""
import math
import random


def community_graph(sizes, p_in, p_out, seed):
    rng = random.Random(seed)
    groups, n = [], 0
    for g, s in enumerate(sizes):
        groups += [g] * s
        n += s
    edges = []
    for a in range(n):
        for b in range(a + 1, n):
            if rng.random() < (p_in if groups[a] == groups[b] else p_out):
                edges.append((a, b))
    return n, edges, groups


def distances(n, edges):
    adj = {i: [] for i in range(n)}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    d = [[math.inf] * n for _ in range(n)]
    for s in range(n):
        d[s][s] = 0
        queue = [s]
        for u in queue:
            for v in adj[u]:
                if d[s][v] == math.inf:
                    d[s][v] = d[s][u] + 1
                    queue.append(v)
    return d


def stress_layout(n, edges, seed=1, iters=300):
    """Stress majorization (SMACOF) on graph distances. Disconnected pairs get the
    largest finite distance plus one."""
    d = distances(n, edges)
    big = max(x for row in d for x in row if x != math.inf) + 1
    d = [[x if x != math.inf else big for x in row] for row in d]
    rng = random.Random(seed)
    x = [[rng.uniform(-1, 1), rng.uniform(-1, 1)] for _ in range(n)]
    w = [[(1 / d[i][j] ** 2) if i != j else 0 for j in range(n)] for i in range(n)]
    for _ in range(iters):
        new = []
        for i in range(n):
            sw = sum(w[i])
            sx = sy = 0.0
            for j in range(n):
                if i == j:
                    continue
                dx, dy = x[i][0] - x[j][0], x[i][1] - x[j][1]
                dist = math.hypot(dx, dy) or 1e-9
                sx += w[i][j] * (x[j][0] + d[i][j] * dx / dist)
                sy += w[i][j] * (x[j][1] + d[i][j] * dy / dist)
            new.append([sx / sw, sy / sw])
        x = new
    return [tuple(p) for p in x]


def fit(points, x0, y0, w, h):
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    sx = (max(xs) - min(xs)) or 1
    sy = (max(ys) - min(ys)) or 1
    s = min(w / sx, h / sy)
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    return [(x0 + w / 2 + (p[0] - cx) * s, y0 + h / 2 + (p[1] - cy) * s) for p in points]


def crossings(pos, edges):
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])

    count = 0
    for i, (a, b) in enumerate(edges):
        for c, d in edges[i + 1:]:
            if len({a, b, c, d}) < 4:
                continue
            if (ccw(pos[a], pos[b], pos[c]) > 0) != (ccw(pos[a], pos[b], pos[d]) > 0) and \
               (ccw(pos[c], pos[d], pos[a]) > 0) != (ccw(pos[c], pos[d], pos[b]) > 0):
                count += 1
    return count

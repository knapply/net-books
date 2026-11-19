"""Chapter 5 of the algorithms book: breadth-first search with its queue, depth-first search with its stack, and the two
side by side, all on the ten-person friendship network from Ana.

The step-by-step trace is the textbook rule (tools/algkit.py: neighbours in index order). Each scene asserts that the
engine's answer for the same network and start (data/anim/traversal-orders.frames.json: traversal::list_bfs_edges,
compute_bfs_levels and list_dfs_events) is exactly what the trace ends with.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import algkit as K  # noqa: E402
from fig_layout import fit, stress_layout  # noqa: E402

BOOK = "algorithms"
NAMES = K.NAMES
EDGES = [list(e) for e in K.EDGES]


def _raw():
    import make_anim as M
    raw = M.load("traversal-orders", BOOK)
    assert raw["names"] == NAMES and raw["edges"] == EDGES, "the engine ran on a different network"
    run = next(r for r in raw["runs"] if r["start"] == 0)
    adj = K.adjacency(10, K.EDGES)
    steps, order, dist, tree = K.bfs_trace(adj, 0)
    assert [tuple(e) for e in run["bfs_edges"]] == tree, "engine breadth-first tree differs from the trace"
    assert run["distances"] == dist, "engine distances differ from the trace"
    events, dorder, dtree = K.dfs_trace(adj, 0)
    eng = [(a, b, k) for a, b, k in run["dfs_events"] if k in (0, 2)]
    mine = [(0, 0, 0)] + [(a, b, 0) if kind == "go" else (b, a, 2) for kind, a, b, _ in events] + [(0, 0, 2)]
    assert eng == mine, "engine depth-first events differ from the trace"
    return M, adj, (steps, order, dist, tree), (events, dorder, dtree)


def _nodes(M):
    return [dict(M.DEFAULT_NODE) for _ in range(10)]


def _eidx():
    return {frozenset(e): i for i, e in enumerate(K.EDGES)}


def _line(prefix, people):
    return f"{prefix} {' '.join(NAMES[p] for p in people) if people else '(empty)'}"


def _scene(M, aid, nodes, states, panel_y, h=380, still=None):
    return {"id": aid, "w": 640, "h": h, "ms": 1500, "nodes": nodes, "edges": EDGES, "book": BOOK,
            "panel": {"kind": "text", "x": 24, "y": panel_y}, "states": states, "still": still}


def _show_from(states):
    def show(i, m):
        k = next(j for j, s in enumerate(states) if s[2] is m)
        return NAMES[i]
    return show


# ------------------------------------------------------------------------ breadth-first search
def bfs_queue():
    M, adj, (steps, order, dist, tree), _ = _raw()
    n = 10
    nodes0 = M.layout(NAMES, EDGES)
    ei = _eidx()
    num = {v: i + 1 for i, v in enumerate(order)}
    states = []

    def make(met, queue, cur, newedge_set, done, text):
        ns = _nodes(M)
        for v in met:
            role = "reach" if v in done else "src"
            ns[v] = {"f": role, "r": 18, "l": str(num[v]), "ring": 0}
        if cur is not None:
            ns[cur] = {"f": "hot", "r": 20, "l": str(num[cur]), "ring": 1}
        es = [dict(M.DEFAULT_EDGE) for _ in EDGES]
        for a, b in tree:
            if a in met and b in met:
                es[ei[frozenset((a, b))]] = {"k": "reach", "w": 2.6}
        for a, b in newedge_set:
            es[ei[frozenset((a, b))]] = {"k": "hot", "w": 3.6}
        line = [_line("Waiting line:", queue)] + ["   |   " + _line("Finished:", [p for p in order if p in done])]
        states.append((ns, es, line, text))

    make({0}, [0], None, [], set(), "Ana is the first person in line. Nobody else has been met yet.")
    met, done = {0}, set()
    for k, st in enumerate(steps):
        u, new = st["take"], st["new"]
        met |= set(new)
        newedges = [(u, v) for v in new]
        if new:
            text = f"Take {NAMES[u]} off the front of the line. {K.join([NAMES[v] for v in new])} are met for the first time and join the back."
            if len(new) == 1:
                text = f"Take {NAMES[u]} off the front of the line. {NAMES[new[0]]} is met for the first time and joins the back."
        else:
            text = f"Take {NAMES[u]} off the front of the line. Nobody new, so nobody joins the back."
        make(met, st["queue"], u, newedges, set(done), text)
        done.add(u)
    make(met, [], None, [], done,
         f"The line is empty, so everyone Ana can reach has been met, in this order: {K.join([NAMES[v] for v in order])}.")
    scene = _scene(M, "bfs-queue", nodes0, states, 346, still=[0, 1, 4, len(states) - 1])
    labels = ["Ana starts the line", "Ana's friends join", "Four people served", "Line empty"]
    still = M.filmstrip(scene, labels, "Breadth-first search with its waiting line",
                        "Four copies of the ten-person friendship network showing a breadth-first search from Ana.",
                        show=_show_from(states))
    return scene, still


# ------------------------------------------------------------------------ depth-first search
def dfs_stack():
    M, adj, _, (events, dorder, dtree) = _raw()
    nodes0 = M.layout(NAMES, EDGES)
    ei = _eidx()
    num = {v: i + 1 for i, v in enumerate(dorder)}
    states = []

    def make(met, trail, cur, finished, walked, text, edge_now=None):
        ns = _nodes(M)
        for v in met:
            ns[v] = {"f": "reach" if v in finished else "src", "r": 18, "l": str(num[v]), "ring": 0}
        if cur is not None:
            ns[cur] = {"f": "hot", "r": 20, "l": str(num[cur]), "ring": 1}
        es = [dict(M.DEFAULT_EDGE) for _ in EDGES]
        for a, b in walked:
            es[ei[frozenset((a, b))]] = {"k": "reach", "w": 2.6}
        for a, b in zip(trail, trail[1:]):
            es[ei[frozenset((a, b))]] = {"k": "src", "w": 3.4}
        if edge_now:
            es[ei[frozenset(edge_now)]] = {"k": "hot", "w": 3.8}
        states.append((ns, es, [_line("Stack (top last):", trail)], text))

    make({0}, [0], 0, set(), [], "Ana goes on the stack. The stack is the trail of people from Ana to wherever we are now.")
    met, finished, walked = {0}, set(), []
    for kind, a, b, trail in events:
        if kind == "go":
            met.add(b)
            walked.append((a, b))
            text = f"From {NAMES[a]}, walk on to {NAMES[b]}, the first friend not yet met. {NAMES[b]} goes on top of the stack."
            make(met, trail, b, set(finished), walked, text, edge_now=(a, b))
        else:
            finished.add(a)
            text = f"{NAMES[a]} has no unmet friends left, so take {NAMES[a]} off the stack and step back to {NAMES[b]}."
            make(met, trail, b, set(finished), walked, text, edge_now=(a, b))
    make(met, [], None, set(range(10)), walked,
         f"The stack is empty: everyone has been met, in this order: {K.join([NAMES[v] for v in dorder])}.")
    k_dead = next(k for k, s in enumerate(states) if "has no unmet" in s[3])
    scene = _scene(M, "dfs-stack", nodes0, states, 346, still=[0, 4, k_dead, len(states) - 1])
    labels = ["Ana starts the trail", "Four people deep", "First dead end", "Stack empty"]
    still = M.filmstrip(scene, labels, "Depth-first search with its stack",
                        "Four copies of the ten-person friendship network showing a depth-first search from Ana.",
                        show=_show_from(states))
    return scene, still


# ------------------------------------------------------------------------ side by side
def bfs_dfs_side():
    M, adj, (steps, border, bdist, btree), (events, dorder, dtree) = _raw()
    pts = stress_layout(10, K.EDGES, seed=3)
    left = fit(pts, 24, 46, 270, 236)
    right = fit(pts, 346, 46, 270, 236)
    nodes = [(f"{NAMES[i]}", x, y) for i, (x, y) in enumerate(left)] + [(f"{NAMES[i]}", x, y) for i, (x, y) in enumerate(right)]
    edges = [list(e) for e in K.EDGES] + [[a + 10, b + 10] for a, b in K.EDGES]
    ei = _eidx()
    states = []

    def role_nodes(order, k, r=15):
        out = []
        for v in range(10):
            if v in order[:k]:
                last = v == order[k - 1]
                out.append({"f": "hot" if last and k > 1 else ("src" if v == order[0] else "reach"), "r": r + (3 if last else 0),
                            "l": str(order.index(v) + 1), "ring": 1 if last and k > 1 else 0})
            else:
                out.append({"f": "base", "r": r, "l": "", "ring": 0})
        return out

    def role_edges(tree, order, k):
        met = set(order[:k])
        es = []
        for e in K.EDGES:
            es.append({"k": "base", "w": 1.6})
        for a, b in tree:
            if b in met:
                es[ei[frozenset((a, b))]] = {"k": "hot" if b == order[k - 1] and k > 1 else "reach", "w": 3.4 if b == order[k - 1] and k > 1 else 2.4}
        return es

    for k in range(1, 11):
        nb, nd = role_nodes(border, k), role_nodes(dorder, k)
        eb, ed = role_edges(btree, border, k), role_edges(dtree, dorder, k)
        if k == 1:
            text = "Both searches start at Ana. She is person number 1 in each picture."
        elif k == 10:
            text = "Both searches have met all ten people, but in different orders. Breadth-first left Jo until last because Jo is farthest; depth-first got there in a long dive."
        else:
            b, d = NAMES[border[k - 1]], NAMES[dorder[k - 1]]
            if b == d:
                text = f"Person number {k}: both searches meet {b} at this moment."
            else:
                text = f"Person number {k}: breadth-first meets {b}, depth-first meets {d}."
        states.append((nb + nd, eb + ed, ["Left: breadth-first, a queue.      Right: depth-first, a stack."], text))
    scene = {"id": "bfs-dfs-side", "w": 640, "h": 340, "ms": 1400, "nodes": nodes, "edges": edges, "book": BOOK,
             "panel": {"kind": "text", "x": 24, "y": 306}, "states": states, "still": [0, 3, 6, 9]}
    labels = ["Person 1", "Person 4", "Person 7", "Person 10"]
    still = _side_strip(M, scene, labels)
    return scene, still


def _side_strip(M, scene, labels):
    """Four small pairs of networks, drawn with the same colors the player uses."""
    from figs import FAINT, MUTED, RED, Canvas
    idx = scene["still"]
    c = Canvas(960, 20 + 266 * ((len(idx) + 1) // 2), "Breadth-first and depth-first side by side",
               "Four pairs of ten-person networks, breadth-first on the left of each pair and depth-first on the right.")
    pos = [(x, y) for _, x, y in scene["nodes"]]
    sc = 0.74
    for k, fi in enumerate(idx):
        ox, oy = 12 + (k % 2) * 474, 12 + (k // 2) * 266
        nodes, edges = scene["states"][fi][0], scene["states"][fi][1]
        c.rect(ox, oy, 456, 250, fill="none", stroke=FAINT, sw=1, rx=8)
        c.text(ox + 12, oy + 22, labels[k], size=14, anchor="start", weight="700")
        mp = [(ox + 8 + (x - 14) * sc, oy + 40 + (y - 40) * sc) for x, y in pos]
        for (a, b), e in zip(scene["edges"], edges):
            c.edge(mp[a], mp[b], ra=0, rb=0, width=e["w"] * 0.9, color=M.edge_color(e["k"]))
        for i, nd in enumerate(nodes):
            fill, stroke = M.NODE[nd["f"]]
            r = nd["r"] * sc
            if nd["ring"]:
                c.add(f'<circle cx="{mp[i][0]:.1f}" cy="{mp[i][1]:.1f}" r="{r + 4:.1f}" fill="none" stroke="{RED}" stroke-width="2"/>')
            c.node(mp[i][0], mp[i][1], nd["l"], r=r, fill=fill, stroke=stroke, size=10)
            c.text(mp[i][0], mp[i][1] + r + 11, scene["nodes"][i][0], size=9.5, fill=MUTED)
    return c.svg()


BUILDERS = {"bfs-queue": bfs_queue, "dfs-stack": dfs_stack, "bfs-dfs-side": bfs_dfs_side}

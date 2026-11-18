"""Chapter 17: a temporal network changing over time, and who a piece of news can reach (six contacts).

Per time step t the engine gave the contacts active at t (find_contacts_at) and the earliest arrival from Ana and from Dev
using only contacts up to t (find_temporal_paths, window ending at t) in data/anim/temporal-reach.frames.json.
"""

from ._strip import lean_filmstrip  # noqa: E402


def build():
    import make_anim as M
    raw = M.load("temporal-reach")
    names, a, b, when = raw["names"], raw["a"], raw["b"], raw["when"]
    n, roots, frames = len(names), raw["roots"], raw["frames"]
    pairs = []
    for x, y in zip(a, b):
        p = (min(x, y), max(x, y))
        if p not in pairs:
            pairs.append(p)
    contact_edge = [pairs.index((min(x, y), max(x, y))) for x, y in zip(a, b)]
    pos = [("%s" % names[i], 50 + 78 * i, 130 + (i % 2) * 90) for i in range(n)]

    def reached(ri, fi):
        row = frames[fi]["arrival"][ri * n:(ri + 1) * n]
        return {i: v for i, v in enumerate(row) if v is not None and i != roots[ri]}

    states = []
    for ri, root in enumerate(roots):
        who = names[root]
        for fi in range(-1, len(frames)):
            t = fi + 1
            got = reached(ri, fi) if fi >= 0 else {}
            before = reached(ri, fi - 1) if fi >= 1 else {}
            active = frames[fi]["active"] if fi >= 0 else []
            for c in active:  # sanity: an active contact is one the data says starts at t
                assert when[c] == t
            ns, es = [], []
            for i in range(n):
                if i == root:
                    ns.append({"f": "src", "r": 20, "l": "", "ring": 0})
                elif i in got:
                    new = i not in before
                    ns.append({"f": "reach", "r": 20, "l": f"{got[i]:g}", "ring": 1 if new else 0})
                else:
                    ns.append({"f": "base", "r": 16, "l": "", "ring": 0})
            carried = set()
            for i, v in got.items():
                for c in active:
                    if i in (a[c], b[c]) and v == t:
                        carried.add(contact_edge[c])
            old = {contact_edge[c] for c in range(len(a)) if when[c] < t and (a[c] in got or b[c] in got or root in (a[c], b[c]))
                   and (got.get(a[c], 99) <= when[c] or a[c] == root or got.get(b[c], 99) <= when[c] or b[c] == root)}
            on = {contact_edge[c] for c in active}
            for e in range(len(pairs)):
                if e in on:
                    es.append({"k": "hot", "w": 4})
                elif e in old:
                    es.append({"k": "reach", "w": 2.4})
                else:
                    es.append({"k": "dim", "w": 1.6})
            if fi < 0:
                text = (f"Same six meetings, but {who} has the news. Each gray line is a pair that meets at some point; "
                        f"watch which ones are lit and when.")
            else:
                c = active[0]
                pa, pb = names[a[c]], names[b[c]]
                gained = sorted(got[i] for i in got if i not in before)
                gnames = [names[i] for i in got if i not in before]
                if gnames:
                    text = f"Time {t}: {pa} and {pb} meet, and {gnames[0]} hears the news from {names[[x for x in (a[c], b[c]) if x != [i for i in got if i not in before][0]][0]]}."
                else:
                    text = f"Time {t}: {pa} and {pb} meet. Neither knows the news yet, so nothing is passed on." \
                        if not ({a[c], b[c]} & ({root} | set(got))) else \
                        f"Time {t}: {pa} and {pb} meet, but both already have the news, so nothing changes."
            if fi == len(frames) - 1:
                if got and max(got) in got and len(got) < n - 1:
                    text += (f" The news went from {names[root]} to " + " to ".join(names[i] for i in sorted(got, key=got.get))
                             + " and stopped: Cleo's meeting with Dev was over before she heard.")
                else:
                    text += f" {who}'s news reached all {len(got)} others, in the order of the meetings."
            states.append((ns, es, [len(got)], text))
    scene = {"id": "temporal-reach", "w": 640, "h": 320, "ms": 1300, "nodes": pos, "edges": [list(p) for p in pairs],
             "panel": {"kind": "bars", "x": 450, "y": 150, "w": 175, "h": 24, "labels": ["Heard"], "max": 5,
                       "title": "People who heard it"},
             "states": states, "still": [3, 6, 10, 13]}
    labels = [f"{names[roots[0]]}'s news, time 3", f"{names[roots[0]]}'s news, time 6",
              f"{names[roots[1]]}'s news, time 3", f"{names[roots[1]]}'s news, time 6"]
    still = lean_filmstrip(scene, labels, "Six meetings in time, and who hears the news",
                           "Four copies of a chain of six people showing who has heard news that starts with Ana or with Dev.",
                           show=lambda i, m: names[i])
    return scene, still


BUILDERS = {"temporal-reach": build}

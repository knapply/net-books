"""Chapter 19: a degree-preserving swap chain on the Florentine marriages, one accepted swap at a time."""
import json

ID = "swap-chain"


def build(M):
    raw = json.loads((M.DATA / f"{ID}.frames.json").read_text())
    names, orig, steps = raw["names"], [tuple(e) for e in raw["edges"]], raw["steps"]
    n = len(names)
    deg0 = steps[0]["degrees"]
    sets = [{tuple(e) for e in s["edges"]} for s in steps]
    assert sets[0] == set(orig), "swap 0 must be the real network"
    for s in steps:
        assert s["degrees"] == deg0, "a swap changed a degree"
    for k in range(1, 11):  # single swaps: exactly two ties out and two in
        assert len(sets[k] - sets[k - 1]) == 2 and len(sets[k - 1] - sets[k]) == 2, f"step {k} is not one swap"
    ever = sorted(set().union(*sets))
    idx = {e: i for i, e in enumerate(ever)}
    base = M.layout(names, [list(e) for e in orig])
    label = lambda e: f"{names[e[0]]}-{names[e[1]]}"  # noqa: E731
    states = []
    for k, s in enumerate(steps):
        cur, prev = sets[k], sets[max(k - 1, 0)]
        single = k >= 1 and steps[k]["swaps"] - steps[k - 1]["swaps"] == 1
        touched = {v for e in (cur ^ prev) for v in e} if single else set()
        ns = [{"f": "base", "r": 6 + 2.2 * deg0[i], "l": "", "ring": 1 if i in touched else 0} for i in range(n)]
        es = []
        for e in ever:
            if e not in cur:
                es.append({"k": "dim", "w": 1.0})
            elif single and e not in prev:
                es.append({"k": "hot", "w": 4.0})
            else:
                es.append({"k": "reach" if e in set(orig) else "src", "w": 2.6})
        kept = len(cur & set(orig))
        swaps = s["swaps"]
        if k == 0:
            text = ("The real network: 15 families and 20 marriages. Each dot's size, and each bar, is the family's number "
                    "of ties.")
        elif single:
            out, new = sorted(prev - cur), sorted(cur - prev)
            text = (f"Swap {swaps}: {label(out[0])} and {label(out[1])} are replaced by {label(new[0])} and "
                    f"{label(new[1])}. {kept} of the 20 original ties are left.")
        else:
            text = f"After {swaps} swaps, {kept} of the 20 original ties are left. Every family has the same number of ties."
        states.append((ns, es, list(s["degrees"]), text))
    scene = {"id": ID, "w": 640, "h": 360, "ms": 900, "nodes": base, "edges": [list(e) for e in ever], "compact": True,
             "panel": {"kind": "bars", "x": 468, "y": 56, "w": 164, "h": 268, "labels": names,
                       "max": max(deg0) + 1, "title": "Ties per family"},
             "states": states, "still": [0, 3, 10, 13]}
    swaps_of = [s["swaps"] for s in steps]
    labels = ["Start", "After 3 swaps", "After 10 swaps", f"After {swaps_of[13]} swaps"]
    still = M.filmstrip(
        scene, labels, "Swapping ties in the Florentine marriages",
        "Four copies of the Florentine marriage network, with ties drawn in blue when they are original and orange when "
        "they came from a swap.", show=lambda i, m: names[i])
    return scene, still


def _builder():
    import make_anim
    return build(make_anim)


BUILDERS = {ID: _builder}

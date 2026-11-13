#!/usr/bin/env python3
"""Write the two small tables behind the latent-space figures.

Runs the Python tabs of the latent-space chapter as one script (like check_lang.py does),
then saves what they computed: the 40 posterior draws of the map (aligned to the fitted
map, because positions are only defined up to turns, mirror images and shifts) and the
simulation summaries of the goodness-of-fit check. Needs numpy, scipy, pandas, networkx.

Note: the Python tabs of the chapter are stubs now (no hand-written fitter), so this script
cannot run until knappnet exposes net_latent_fit() and net_latent_sample(). The CSVs it wrote
earlier are kept in books/sna/data/latent/.

Usage: python3 tools/latent_data.py      (writes books/sna/data/latent/*.csv)
"""
import csv
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tabs import tabs_of, tabsets  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CHAPTER = ROOT / "books" / "sna" / "chapters" / "22-latent-space.qmd"
OUT = ROOT / "books" / "sna" / "data" / "latent"

TAIL = '''
import csv as _csv
def _align(z, target):
    z0, t0 = z - z.mean(axis=0), target - target.mean(axis=0)
    u, _, vt = np.linalg.svd(z0.T @ t0)
    return z0 @ (u @ vt) + target.mean(axis=0)
with open(r"%(draws)s", "w", newline="") as f:
    w = _csv.writer(f)
    w.writerow(["draw", "member", "x", "y", "side"])
    for d, (z, _a) in enumerate(draws):
        for i, (x, y) in enumerate(_align(z, positions)):
            w.writerow([d, i, round(float(x), 4), round(float(y), 4), int(side[i])])
with open(r"%(fit)s", "w", newline="") as f:
    w = _csv.writer(f)
    w.writerow(["member", "x", "y", "side"])
    for i, (x, y) in enumerate(positions):
        w.writerow([i, round(float(x), 4), round(float(y), 4), int(side[i])])
with open(r"%(gof)s", "w", newline="") as f:
    w = _csv.writer(f)
    w.writerow(["model", "statistic", "club", "median", "low", "high"])
    for name in models:
        for k, stat in enumerate(["degree spread (sd)", "busiest member", "triangles", "pairs two steps apart"]):
            low, mid, high = np.quantile(runs[name][:, k], [0.025, 0.5, 0.975])
            w.writerow([name, stat, round(float(seen[k]), 2), round(float(mid), 2), round(float(low), 2), round(float(high), 2)])
'''


def main():
    import subprocess
    lines = CHAPTER.read_text().split("\n")
    cells = []
    for s, e in tabsets(lines):
        t = tabs_of(lines, s, e).get("Python")
        if t and t["code"] and not t["code"][2].lstrip().startswith("# TODO"):
            cells.append(t["code"][2])
    OUT.mkdir(parents=True, exist_ok=True)
    script = "\n\n".join(cells) + TAIL % {"draws": OUT / "draws.csv", "fit": OUT / "fit.csv", "gof": OUT / "gof.csv"}
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "data").symlink_to(ROOT / "books" / "sna" / "data")
        (Path(tmp) / "script.py").write_text(script)
        proc = subprocess.run(["python3", "-I", "script.py"], cwd=tmp, capture_output=True, text=True)
    if proc.returncode:
        print(proc.stderr)
        return 1
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("*.csv"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())

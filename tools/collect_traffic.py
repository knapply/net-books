#!/usr/bin/env python3
"""Keep GitHub's repository traffic past its 14-day window.

GitHub reports views, clones, top referrers and popular paths for the last 14
days only, and only to people with push access. This script reads them with a
token, merges the daily counts into stats/traffic.json (keyed by day, so reruns
never double count), and writes the small JSON files that the README badges
read. Everything is aggregate: GitHub does not report who the visitors are.

Usage: GH_TOKEN=... python3 tools/collect_traffic.py owner/repo OUT_DIR
"""
import json
import os
import sys
import urllib.request
from pathlib import Path


def get(repo: str, what: str):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/traffic/{what}",
        headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}",
                 "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def badge(label: str, value) -> dict:
    return {"schemaVersion": 1, "label": label, "message": f"{value:,}", "color": "0072B2"}


def main(repo: str, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    path = out / "traffic.json"
    store = json.loads(path.read_text()) if path.exists() else {"views": {}, "clones": {}}
    for kind in ("views", "clones"):
        for day in get(repo, kind)[kind]:
            store[kind][day["timestamp"][:10]] = {"count": day["count"], "uniques": day["uniques"]}
    store["referrers"] = get(repo, "popular/referrers")
    store["paths"] = get(repo, "popular/paths")
    path.write_text(json.dumps(store, indent=1, sort_keys=True) + "\n")
    total = lambda k, f: sum(d[f] for d in store[k].values())
    for name, label, value in [
        ("views", "page views", total("views", "count")),
        ("visitors", "visitors (daily, summed)", total("views", "uniques")),
        ("clones", "clones", total("clones", "count")),
    ]:
        (out / f"badge-{name}.json").write_text(json.dumps(badge(label, value)) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], Path(sys.argv[2]))

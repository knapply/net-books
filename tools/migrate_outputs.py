#!/usr/bin/env python3
"""One-off: move each tabset's shared output block into its tabs (each tab owns its output)."""
from pathlib import Path
from tabs import tabsets, tabs_of, set_output

ROOT = Path(__file__).resolve().parent.parent
for qmd in sorted(list((ROOT / "books").glob("*/chapters/*.qmd")) + list((ROOT / "books").glob("*/appendices/*.qmd"))):
    lines = qmd.read_text().split("\n")
    for s, e in reversed(list(tabsets(lines))):
        a = e + 1
        while a < len(lines) and not lines[a].strip():
            a += 1
        if a >= len(lines) or not lines[a].startswith("::: {.code-output}"):
            continue
        z = a + 1
        while lines[z].strip() != ":::":
            z += 1
        inner = lines[a + 1:z]
        if inner and inner[0].startswith("```"):
            inner = inner[1:]
            if inner and inner[-1].startswith("```"):
                inner = inner[:-1]
        shared = "\n".join(inner)
        lines = lines[:e + 1] + lines[z + 1:]
        tabs = tabs_of(lines, s, e)
        for name in reversed(list(tabs)):
            if tabs[name]["code"]:
                lines = set_output(lines, tabs[name], shared)
    qmd.write_text("\n".join(lines))
    print("migrated", qmd.name)

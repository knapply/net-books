#!/usr/bin/env python3
"""Structure checks for every book under books/.

For each book with an outline.toml it checks that
- every chapter and appendix in the outline has a file,
- every _quarto.yml chapter path exists,
- every chapter has a prerequisites box, exercises, a summary,
- every code tabset has R, Python and Rust tabs, in that order,
- section anchors (#sec-...) are unique across the book,
- every @key citation exists in shared/bib/references.bib.

Standard library only. Exit status 1 on any problem.
"""
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABS = ["R", "Python", "Rust"]
problems: list[str] = []


def bib_keys() -> set[str]:
    text = (ROOT / "shared" / "bib" / "references.bib").read_text()
    return set(re.findall(r"^@\w+\{([^,\s]+),", text, flags=re.M))


def check_book(book: Path, keys: set[str]) -> int:
    outline = tomllib.loads((book / "outline.toml").read_text())
    files: list[Path] = []
    number = 0
    for part in outline["part"]:
        for chapter in part["chapter"]:
            number += 1
            files.append(book / "chapters" / f"{number:02d}-{chapter['slug']}.qmd")
    for appendix in outline.get("appendix", []):
        files.append(book / "appendices" / f"{appendix['slug']}.qmd")

    config = (book / "_quarto.yml").read_text()
    for rel in re.findall(r"^\s+- ((?:chapters|appendices)/\S+\.qmd)", config, flags=re.M):
        if not (book / rel).exists():
            problems.append(f"{book.name}: _quarto.yml lists missing file {rel}")

    anchors: dict[str, Path] = {}
    for path in files:
        if not path.exists():
            problems.append(f"{book.name}: missing {path.relative_to(book)}")
            continue
        text = path.read_text()
        name = f"{book.name}/{path.relative_to(book)}"
        for needle, label in [("Prerequisites", "prerequisites box"),
                              ("## Exercises", "exercises"),
                              ("## Summary", "summary")]:
            if needle not in text:
                problems.append(f"{name}: no {label}")
        for anchor in re.findall(r"\{#(sec-[\w-]+)\}", text):
            if anchor in anchors:
                problems.append(f"{name}: anchor {anchor} also in {anchors[anchor].name}")
            anchors[anchor] = path
        for tabset in re.findall(r"panel-tabset[^\n]*\n(.*?)\n:::", text, flags=re.S):
            tabs = re.findall(r"^## (.+)$", tabset, flags=re.M)
            if tabs != TABS:
                problems.append(f"{name}: tabset tabs {tabs}, expected {TABS}")
        for m in re.finditer(r"panel-tabset[^\n]*\n.*?\n:::\n", text, flags=re.S):
            if not text[m.end():].lstrip().startswith("::: {.code-output}"):
                problems.append(f"{name}: a code tabset has no code-output block after it")
        for key in re.findall(r"(?<![\w`])@([A-Za-z][\w:.-]*\d\w*)", text):
            if key not in keys and not key.startswith(("sec-", "fig-", "tbl-", "eq-")):
                problems.append(f"{name}: citation @{key} not in references.bib")
        for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)(\{[^}]*\})?", text):
            target = (path.parent / m.group(1)).resolve()
            if not target.exists():
                problems.append(f"{name}: figure {m.group(1)} not found")
            if 'fig-alt="' not in (m.group(2) or "") or 'fig-alt=""' in (m.group(2) or ""):
                problems.append(f"{name}: figure {m.group(1)} needs fig-alt text")
    return len(files)


def main() -> int:
    keys = bib_keys()
    total = 0
    for outline in sorted((ROOT / "books").glob("*/outline.toml")):
        total += check_book(outline.parent, keys)
    for problem in problems:
        print("FAIL", problem)
    print(f"{total} chapter files checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

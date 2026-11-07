#!/usr/bin/env python3
"""Run the R or Python tab of every example and compare what it prints with the
output block shown after the tabset (the same block the Rust tab is checked against).

The tabs of one chapter form one script, like cells in a notebook: later tabs may
use what earlier ones defined. Tabs whose first line is a `# TODO` comment are
skipped. Data files are read from `data/<name>/...`, relative to the working
directory (the checker links books/sna/data there).

Two allowances, both for output that cannot match by design:
- The network description that Rust prints (`Undirected network: ...` and its
  indented lines) is removed from the expected text; R and Python tabs do not
  reproduce it.
- A line `# CHECK: stop` in a tab ends the comparison there: the code still runs, but
  output printed after that line is not compared. Use it only for layouts and for
  results that depend on random draws, which differ between languages; say so in a
  comment (and in the prose).

Usage:
  python3 tools/check_lang.py --lang python [--diff] [chapter-name-part ...]
  python3 tools/check_lang.py --lang r      [--diff] [chapter-name-part ...]

Needs python3 with networkx, numpy (and whatever a chapter imports), or Rscript
with the packages a chapter loads (on btower: knappnet installed from r/).
Exit status is 1 if any example fails to run or prints something different.
"""
import difflib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABSET = re.compile(r'::: \{\.panel-tabset group="language"\}\n(.*?)\n:::\n\n::: \{\.code-output\}\n(.*?)\n:::', re.S)
TAB = re.compile(r"^## (R|Python|Rust)\n\n```(?:r|python|rust)\n(.*?)```", re.S | re.M)
MARK = "@@FRAGMENT "
LANG = {"python": ("Python", ["python3", "-I"], "script.py", 'print("%s%d")'),
        "r": ("R", ["Rscript", "--vanilla"], "script.R", 'cat("%s%d\\n")')}


def todo(code: str) -> bool:
    first = code.lstrip().split("\n", 1)[0]
    return first.startswith("# TODO") or first.startswith("// TODO")


def strip_description(text: str) -> str:
    out, skipping = [], False
    for line in text.splitlines():
        if re.match(r"(Directed|Undirected) network: ", line):
            skipping = True
            continue
        if skipping and not line.strip():
            skipping = False  # a blank line ends the description; the next lines are real output
            continue
        if skipping and line.startswith("  "):
            continue
        skipping = False
        out.append(line)
    return "\n".join(out)


STOP = "@@STOP"


def with_stop(code: str, lang: str) -> str:
    emit = 'print("%s")' if lang == "python" else 'cat("%s\\n")'
    out = []
    for line in code.split("\n"):
        if re.match(r"\s*#\s*CHECK:\s*(stop|skip)\b", line):
            out.append(emit % STOP)
        out.append(line)
    return "\n".join(out)


def norm(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def check_chapter(lang: str, qmd: Path, show_diff: bool) -> int:
    tab_name, cmd, fname, marker = LANG[lang]
    text = qmd.read_text()
    cells = []  # (index, code, expected)
    for i, m in enumerate(TABSET.finditer(text)):
        tabs = {name: code for name, code in TAB.findall(m.group(1))}
        code = tabs.get(tab_name)
        shown = re.search(r"```text\n(.*?)```", m.group(2), re.S)
        if code is None or todo(code) or not shown:
            continue
        cells.append((i, code, strip_description(shown.group(1))))
    if not cells:
        print(f"skip {qmd.name} (no {tab_name} examples yet)")
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "data").symlink_to(ROOT / "books" / "sna" / "data")
        body = "".join((marker % (MARK, i)) + "\n" + with_stop(code, lang).rstrip("\n") + "\n" for i, code, _ in cells)
        (Path(tmp) / fname).write_text(body)
        run = subprocess.run(cmd + [fname], cwd=tmp, capture_output=True, text=True)
    if run.returncode != 0:
        print(f"FAIL {qmd.name}: the {tab_name} examples do not run\n{run.stderr[-3000:]}")
        got = run.stdout
    else:
        got = run.stdout
    parts = {}
    for chunk in got.split(MARK)[1:]:
        idx, _, rest = chunk.partition("\n")
        parts[int(idx.strip())] = rest
    failures = 0 if run.returncode == 0 else 1
    codes = {i: c for i, c, _ in cells}
    for i, _, expected in cells:
        code = codes[i]
        if i not in parts:
            if run.returncode == 0:
                failures += 1
                print(f"DIFF {qmd.name}: {tab_name} example {i + 1} printed nothing")
            continue
        actual = parts[i]
        if STOP in actual:
            actual = actual.split(STOP)[0]
            expected = "\n".join(expected.splitlines()[:len(actual.strip().splitlines())])
        if norm(actual) != norm(expected):
            failures += 1
            print(f"DIFF {qmd.name}: {tab_name} example {i + 1} printed something other than its output block")
            if show_diff:
                d = difflib.unified_diff(norm(expected).splitlines(), norm(actual).splitlines(),
                                         "expected (output block)", f"{tab_name} printed", lineterm="", n=1)
                print("\n".join(list(d)[:30]))
    if not failures:
        print(f"ok   {qmd.name} ({len(cells)} {tab_name} example{'s' if len(cells) != 1 else ''})")
    return 1 if failures else 0


def main() -> int:
    args = sys.argv[1:]
    if "--lang" not in args:
        print(__doc__)
        return 2
    lang = args[args.index("--lang") + 1]
    if lang not in LANG:
        print("--lang must be python or r")
        return 2
    only = [a for a in args if not a.startswith("--") and a != lang]
    chapters = sorted(list((ROOT / "books").glob("*/chapters/*.qmd")) + list((ROOT / "books").glob("*/appendices/*.qmd")))
    if only:
        chapters = [q for q in chapters if any(o in q.name for o in only)]
    return 1 if sum(check_chapter(lang, q, "--diff" in args) for q in chapters) else 0


if __name__ == "__main__":
    sys.exit(main())

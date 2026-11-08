#!/usr/bin/env python3
"""Run the R or Python tab of every example and keep its output block honest.

Every tab owns the output it printed (the `.code-output` block right after its code),
so R and Python show what R and Python really print; they do not have to match
Rust or each other character for character. The tabs of one chapter form one
script, like cells in a notebook. Tabs whose first line is a `# TODO` comment
are skipped. Data files are read from `data/<name>/...`.

Usage:
  python3 tools/check_lang.py --lang python|r [--diff] [--agree] [chapter-part ...]
        check that each stored output equals what the tab prints now
  python3 tools/check_lang.py --lang python --write [chapter-part ...]
        run the tabs and store what they print in the output blocks
  python3 tools/check_lang.py --lang r --emit FILE [chapter-part ...]
        run the tabs and save what they print as JSON (for runs elsewhere)
  python3 tools/check_lang.py --lang r --apply FILE [chapter-part ...]
        store a saved run in the output blocks
  --agree  also list numbers a tab prints that Rust does not print (advisory only;
           different libraries may print different things)

Exit status is 1 if a tab fails to run or a stored output is stale.
"""
import difflib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tabs import set_output, tabs_of, tabsets  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MARK = "@@FRAGMENT "
LANG = {"python": ("Python", ["python3", "-I"], "script.py", 'print("%s%d")'),
        "r": ("R", ["Rscript", "--vanilla"], "script.R", 'cat("%s%d\\n")')}
NUMBER = re.compile(r"-?\d+(?:\.\d+)?")


def todo(code):
    first = code.lstrip().split("\n", 1)[0]
    return first.startswith(("# TODO", "// TODO"))


def norm(text):
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def cells(lang, lines):
    """(tabset index, code, stored output or None, rust output or None) per runnable tab."""
    tab_name = LANG[lang][0]
    found = []
    for i, (s, e) in enumerate(tabsets(lines)):
        tabs = tabs_of(lines, s, e)
        t = tabs.get(tab_name)
        if not t or not t["code"] or todo(t["code"][2]):
            continue
        rust = tabs.get("Rust")
        found.append((i, t["code"][2], t["out"][2] if t["out"] else None,
                      rust["out"][2] if rust and rust["out"] else None))
    return found


def run(lang, cs):
    _, cmd, fname, marker = LANG[lang]
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "data").symlink_to(ROOT / "books" / "sna" / "data")
        body = "".join((marker % (MARK, i)) + "\n" + code.rstrip("\n") + "\n" for i, code, _, _ in cs)
        (Path(tmp) / fname).write_text(body)
        proc = subprocess.run(cmd + [fname], cwd=tmp, capture_output=True, text=True)
    parts = {}
    for chunk in proc.stdout.split(MARK)[1:]:
        idx, _, rest = chunk.partition("\n")
        parts[int(idx.strip())] = rest
    return proc, parts


def numbers(text):
    text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
    text = re.sub(r"^\s*\[\d+\]", "", text, flags=re.M)
    return [t for t in NUMBER.findall(text)]


def unmatched(actual, rust):
    ref = [(float(t), len(t.split(".")[1]) if "." in t else 0) for t in numbers(rust)]
    out = []
    for t in numbers(actual):
        v, d = float(t), (len(t.split(".")[1]) if "." in t else 0)
        if not any(abs(v - r) <= 0.51 * 10 ** -min(d, rd) for r, rd in ref):
            out.append(t)
    return out


def chapters(only):
    files = sorted(list((ROOT / "books").glob("*/chapters/*.qmd")) + list((ROOT / "books").glob("*/appendices/*.qmd")))
    return [q for q in files if not only or any(o in q.name for o in only)]


def main():
    args = sys.argv[1:]
    if "--lang" not in args:
        print(__doc__)
        return 2
    lang = args[args.index("--lang") + 1]
    tab_name = LANG[lang][0]
    flags = {"--diff", "--agree", "--write"}
    value_flags = {"--lang", "--emit", "--apply"}
    values = {f: args[args.index(f) + 1] for f in value_flags if f in args}
    only = [a for a in args if a not in flags and a not in value_flags and a not in values.values()]
    saved = json.load(open(values["--apply"])) if "--apply" in values else {}
    dump, bad = {}, 0
    for qmd in chapters(only):
        lines = qmd.read_text().split("\n")
        cs = cells(lang, lines)
        if not cs:
            continue
        if "--apply" in values:
            actual, proc = {int(k): v for k, v in saved.get(qmd.name, {}).items()}, None
        else:
            proc, actual = run(lang, cs)
            if proc.returncode != 0:
                bad += 1
                print(f"FAIL {qmd.name}: the {tab_name} examples do not run\n{proc.stderr[-3000:]}")
                continue
        dump[qmd.name] = {str(k): v for k, v in actual.items()}
        stale = 0
        for i, code, stored, rust in cs:
            if i not in actual:
                continue
            if "--agree" in args and rust:
                extra = unmatched(actual[i], rust)
                if extra:
                    print(f"note {qmd.name}: {tab_name} example {i + 1} prints numbers Rust does not: {' '.join(extra[:8])}")
            if stored is not None and norm(stored) == norm(actual[i]):
                continue
            stale += 1
            if "--write" in args or "--apply" in values:
                continue
            print(f"DIFF {qmd.name}: {tab_name} example {i + 1}: stored output is {'missing' if stored is None else 'stale'}")
            if "--diff" in args and stored is not None:
                d = difflib.unified_diff(norm(stored).splitlines(), norm(actual[i]).splitlines(),
                                         "stored", "printed now", lineterm="", n=1)
                print("\n".join(list(d)[:30]))
        if stale and ("--write" in args or "--apply" in values):
            for i, code, stored, rust in sorted(cs, reverse=True):
                if i in actual and (stored is None or norm(stored) != norm(actual[i])):
                    s, e = list(tabsets(lines))[i]
                    lines = set_output(lines, tabs_of(lines, s, e)[tab_name], actual[i])
            qmd.write_text("\n".join(lines))
            print(f"wrote {qmd.name} ({stale} output{'s' if stale != 1 else ''})")
        elif not stale:
            print(f"ok   {qmd.name} ({len(cs)} {tab_name} example{'s' if len(cs) != 1 else ''})")
        bad += 1 if stale and not ("--write" in args or "--apply" in values) else 0
    if "--emit" in values:
        json.dump(dump, open(values["--emit"], "w"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

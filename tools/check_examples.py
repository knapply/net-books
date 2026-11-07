#!/usr/bin/env python3
"""Compile and run the real Rust examples in each chapter and compare what they
print with the output block shown after each one.

How a chapter's Rust blocks fit together:
- If the chapter has one Rust block and it contains `fn main`, that block is a
  whole program.
- Otherwise the blocks are fragments of one script, in order, like cells in a
  notebook. Each fragment may use what earlier ones defined, and may start with
  its own `use` lines. The checker wraps them all in one `main`, runs it, and
  compares each fragment's printed text with the output block that follows it.
- A block whose first line is a `// TODO` comment is a placeholder and is skipped.

Needs the engine source and a Rust toolchain; skips quietly without them.

Usage:
  KNAPPNET_PATH=/path/to/crates/engine python3 tools/check_examples.py [--update] [chapter-name-part ...]

With --update, the output blocks in the chapters are rewritten from what the
code actually printed. Review the diff, and check new numbers independently.
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAIR = re.compile(r"(```rust\n)(.*?)(```\n\n:::\n\n::: \{\.code-output\}\n)(.*?)(\n:::)", re.S)
MARK = "@@FRAGMENT "


def run_program(engine: str, program: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "src").mkdir()
        (Path(tmp) / "Cargo.toml").write_text(
            f'[package]\nname = "ex"\nversion = "0.0.0"\nedition = "2021"\n'
            f'[dependencies]\nknappnet = {{ path = "{engine}" }}\n')
        (Path(tmp) / "src" / "main.rs").write_text(program)
        (Path(tmp) / "data").symlink_to(ROOT / "books" / "sna" / "data")
        return subprocess.run(["cargo", "run", "-q", "--offline"], cwd=tmp, capture_output=True, text=True)


def check_chapter(engine: str, qmd: Path, update: bool) -> int:
    text = qmd.read_text()
    pairs = [m for m in PAIR.finditer(text) if not m.group(2).lstrip().startswith("// TODO")]
    if not pairs:
        return 0
    codes = [m.group(2) for m in pairs]
    whole = len(codes) == 1 and "fn main" in codes[0]
    if whole:
        program = codes[0]
    else:
        body = "".join(f'println!("{MARK}{i}");\n{code}\n' for i, code in enumerate(codes))
        program = "fn main() -> Result<(), knappnet::Error> {\n" + body + "Ok(())\n}\n"
    run = run_program(engine, program)
    if run.returncode != 0:
        print(f"FAIL {qmd.name}: the examples do not run\n{run.stderr}")
        return 1
    if whole:
        printed = [run.stdout]
    else:
        parts = run.stdout.split(MARK)[1:]
        printed = [p.split("\n", 1)[1] if "\n" in p else "" for p in parts]
    if len(printed) != len(codes):
        print(f"FAIL {qmd.name}: expected {len(codes)} fragments of output, got {len(printed)}")
        return 1
    failures = 0
    for i, (m, out) in enumerate(zip(pairs, printed)):
        shown = re.search(r"```text\n(.*?)```", m.group(4), re.S)
        if not shown or shown.group(1).strip() != out.strip():
            failures += 1
            print(f"DIFF {qmd.name}: example {i + 1} printed something other than its output block")
    if update and failures:
        out_iter = iter(printed)

        def rep(m: re.Match) -> str:
            if m.group(2).lstrip().startswith("// TODO"):
                return m.group(0)
            out = next(out_iter).rstrip("\n") + "\n"
            return m.group(1) + m.group(2) + m.group(3) + "```text\n" + out + "```" + m.group(5)

        qmd.write_text(PAIR.sub(rep, text))
        print(f"updated {qmd.name}")
        return 0
    if not failures:
        print(f"ok   {qmd.name} ({len(codes)} example{'s' if len(codes) != 1 else ''})")
    return 1 if failures else 0


def main() -> int:
    engine = os.environ.get("KNAPPNET_PATH")
    if not engine or not Path(engine).exists():
        print("KNAPPNET_PATH not set; skipping example checks")
        return 0
    update = "--update" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    chapters = sorted(list((ROOT / "books").glob("*/chapters/*.qmd")) + list((ROOT / "books").glob("*/appendices/*.qmd")))
    if only:
        chapters = [q for q in chapters if any(o in q.name for o in only)]
    return 1 if sum(check_chapter(engine, q, update) for q in chapters) else 0


if __name__ == "__main__":
    sys.exit(main())

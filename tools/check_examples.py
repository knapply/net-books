#!/usr/bin/env python3
"""Compile and run every real Rust example in the chapters and compare what it
prints with the output block shown after it.

Needs the engine source and a Rust toolchain; skips quietly without them.
Usage: KNAPPNET_PATH=/path/to/crates/engine python3 tools/check_examples.py
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    engine = os.environ.get("KNAPPNET_PATH")
    if not engine or not Path(engine).exists():
        print("KNAPPNET_PATH not set; skipping example checks")
        return 0
    failures = 0
    for qmd in sorted((ROOT / "books").glob("*/chapters/*.qmd")):
        text = qmd.read_text()
        for m in re.finditer(r"```rust\n(.*?)```\n\n:::\n\n::: \{\.code-output\}\n(.*?)\n:::", text, re.S):
            code, shown = m.group(1), m.group(2)
            if code.lstrip().startswith("//"):
                continue  # placeholder
            expected = re.search(r"```text\n(.*?)```", shown, re.S)
            with tempfile.TemporaryDirectory() as tmp:
                (Path(tmp) / "src").mkdir()
                (Path(tmp) / "Cargo.toml").write_text(
                    f'[package]\nname = "ex"\nversion = "0.0.0"\nedition = "2021"\n'
                    f'[dependencies]\nknappnet = {{ path = "{engine}" }}\n')
                (Path(tmp) / "src" / "main.rs").write_text(code)
                run = subprocess.run(["cargo", "run", "-q", "--offline"], cwd=tmp, capture_output=True, text=True)
            if run.returncode != 0:
                print(f"FAIL {qmd.name}: example does not run\n{run.stderr}")
                failures += 1
            elif expected and run.stdout.strip() != expected.group(1).strip():
                print(f"FAIL {qmd.name}: printed output differs from the output block")
                failures += 1
            else:
                print(f"ok   {qmd.name}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

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
from pathlib import Path as _P
sys.path.insert(0, str(_P(__file__).resolve().parent))
from tabs import tabs_of, tabsets
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABS = ["R", "Python", "Rust"]
problems: list[str] = []


def bib_keys() -> set[str]:
    text = (ROOT / "shared" / "bib" / "references.bib").read_text()
    return set(re.findall(r"^@\w+\{([^,\s]+),", text, flags=re.M))


CARD_FIELDS = {"id": str, "title": str, "kind": str, "chapter": str, "summary": str, "answers": str,
               "data_requirements": list, "assumptions": list, "readings": list, "pitfalls": list,
               "checks": list, "do_not_claim": list, "report_template": str, "related": list,
               "sources": list, "knappnet": dict}


def check_cards(book: Path, outline: dict, keys: set[str]) -> None:
    slugs = {c["slug"] for p in outline["part"] for c in p["chapter"]}
    ids = set()
    for path in sorted((book / "cards").glob("*.toml")):
        name = f"{book.name}/cards/{path.name}"
        card = tomllib.loads(path.read_text())
        for field, kind in CARD_FIELDS.items():
            if field not in card:
                problems.append(f"{name}: missing field {field}")
            elif not isinstance(card[field], kind):
                problems.append(f"{name}: field {field} should be {kind.__name__}")
            elif kind is list and not card[field]:
                problems.append(f"{name}: field {field} is empty")
        if card.get("id") != path.stem:
            problems.append(f"{name}: id {card.get('id')} does not match the file name")
        if card.get("kind") not in ("measure", "model", "procedure"):
            problems.append(f"{name}: kind must be measure, model or procedure")
        if card.get("chapter") not in slugs:
            problems.append(f"{name}: chapter {card.get('chapter')} is not in the outline")
        for r in card.get("readings", []):
            if not {"context", "high", "low"} <= set(r):
                problems.append(f"{name}: each reading needs context, high and low")
        for key in card.get("sources", []):
            if key not in keys:
                problems.append(f"{name}: source {key} not in references.bib")
        for lang in ("rust", "r", "python"):
            if lang not in card.get("knappnet", {}):
                problems.append(f"{name}: knappnet table needs {lang}")
        for placeholder in re.findall(r"\{(\w+)\}", card.get("report_template", "")):
            pass
        ids.add(path.stem)


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

    check_cards(book, outline, keys)
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
        lines = text.split("\n")
        for start, end in tabsets(lines):
            tabs = tabs_of(lines, start, end)
            if list(tabs) != TABS:
                problems.append(f"{name}: tabset tabs {list(tabs)}, expected {TABS}")
            for tab, info in tabs.items():
                code = info["code"]
                if code and not code[2].lstrip().startswith(("# TODO", "// TODO")) and not info["out"]:
                    problems.append(f"{name}: a {tab} example has no output block")
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

ANIM_JS_BUDGET, ANIM_JSON_BUDGET, ANIM_STILL_BUDGET = 6 * 1024, 40 * 1024, 100 * 1024
ANIM_STILL_GZIP_BUDGET = 8 * 1024  # stills are repetitive SVG; what readers download is the gzip size
FILL_ROLES = {"base", "src", "reach", "hot", "dim", "a", "b", "c", "d", "e"}
BANNED = re.compile(r"\b(generated|AI|artificial intelligence|Claude|model-made)\b", re.I)


def anim_texts(doc: dict):
    for fr in doc.get("frames", []):
        yield fr.get("t", "")
    for k in ("title",):
        yield (doc.get("panel") or {}).get(k, "")


def check_anim(book: Path) -> int:
    """Animations: every still-frame figure has a player JSON that follows schema v1 and the size budgets."""
    count = 0
    js = ROOT / "shared" / "js" / "netanim.js"
    if js.exists() and js.stat().st_size > ANIM_JS_BUDGET:
        problems.append(f"shared/js/netanim.js is {js.stat().st_size} bytes, budget {ANIM_JS_BUDGET}")
    for path in sorted((book / "chapters").glob("*.qmd")) + sorted((book / "appendices").glob("*.qmd")):
        text = path.read_text()
        name = f"{book.name}/{path.relative_to(book)}"
        for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+-still\.svg)\)(\{[^}]*\})?", text):
            count += 1
            caption, rel, attrs = m.group(1), m.group(2), m.group(3) or ""
            still = (path.parent / rel).resolve()
            data = still.with_name(still.name[: -len("-still.svg")] + ".json")
            if not still.exists():
                problems.append(f"{name}: still {rel} not found")
                continue
            if still.stat().st_size > ANIM_STILL_BUDGET:
                problems.append(f"{name}: {rel} is {still.stat().st_size} bytes, budget {ANIM_STILL_BUDGET}")
            else:
                import gzip
                zipped = len(gzip.compress(still.read_bytes(), 9))
                if zipped > ANIM_STILL_GZIP_BUDGET:
                    problems.append(f"{name}: {rel} is {zipped} bytes gzipped, budget {ANIM_STILL_GZIP_BUDGET}")
            if not data.exists():
                problems.append(f"{name}: {rel} has no matching {data.name}")
                continue
            if "#fig-" not in attrs:
                problems.append(f"{name}: animation {rel} needs a #fig- label")
            for label, s in (("caption", caption), ("fig-alt", attrs)):
                if "\u2014" in s or BANNED.search(s):
                    problems.append(f"{name}: animation {rel} {label} has an em dash or a banned word")
            check_anim_json(f"{book.name}/{data.relative_to(book)}", data)
    root = book / "figures" / "anim"
    if root.exists() and js.exists():
        squash = lambda t: "\n".join(line.strip() for line in t.splitlines())  # noqa: E731
        config = squash((book / "_quarto.yml").read_text())
        if squash(js.read_text()) not in config or "figures/anim/*.json" not in config:
            problems.append(f"{book.name}/_quarto.yml does not carry the current player or the anim resources; "
                            "run python3 tools/new_chapters.py books/" + book.name)
    if root.exists():
        for j in sorted(root.glob("*.json")):
            if not (root / f"{j.stem}-still.svg").exists():
                problems.append(f"{book.name}/figures/anim/{j.name}: no {j.stem}-still.svg beside it")
    return count


def check_anim_json(name: str, path: Path) -> None:
    import json
    raw = path.read_text()
    if len(raw.encode()) > ANIM_JSON_BUDGET:
        problems.append(f"{name}: {len(raw.encode())} bytes, budget {ANIM_JSON_BUDGET}")
    try:
        d = json.loads(raw)
    except ValueError as err:
        problems.append(f"{name}: not JSON ({err})")
        return

    def bad(msg):
        problems.append(f"{name}: {msg}")

    if d.get("v") != 1:
        bad("v must be 1")
    if d.get("id") != path.stem:
        bad("id must match the file name")
    for k in ("w", "h", "ms"):
        if not isinstance(d.get(k), (int, float)) or d[k] <= 0:
            bad(f"{k} must be a positive number")
    nodes, edges, frames = d.get("nodes"), d.get("edges"), d.get("frames")
    if not isinstance(nodes, list) or not nodes or not all({"id", "x", "y"} <= set(n) for n in nodes):
        bad("nodes need id, x and y")
        return
    if not isinstance(edges, list) or not all(isinstance(e, list) and len(e) == 2 and all(isinstance(i, int) and 0 <= i < len(nodes) for i in e) for e in edges):
        bad("edges must be index pairs into nodes")
        return
    if not isinstance(frames, list) or len(frames) < 2:
        bad("frames needs at least 2 entries")
        return
    panel = d.get("panel")
    if panel is not None and panel.get("kind") not in ("bars", "line", "text", None):
        bad("panel.kind must be bars, line, text or null")
    for k, fr in enumerate(frames):
        if not isinstance(fr.get("t"), str) or not fr["t"].strip():
            bad(f"frame {k} needs caption text t")
        for i, ch in (fr.get("n") or {}).items():
            if not i.isdigit() or int(i) >= len(nodes):
                bad(f"frame {k}: node index {i} out of range")
            if "f" in ch and ch["f"] not in FILL_ROLES:
                bad(f"frame {k}: unknown fill role {ch['f']}")
        for i, ch in (fr.get("e") or {}).items():
            if not i.isdigit() or int(i) >= len(edges):
                bad(f"frame {k}: edge index {i} out of range")
            if "k" in ch and ch["k"] not in FILL_ROLES:
                bad(f"frame {k}: unknown edge role {ch['k']}")
        for i in (fr.get("p") or {}):
            if not i.isdigit() or int(i) >= len(nodes):
                bad(f"frame {k}: position index {i} out of range")
    if not all(isinstance(i, int) and 0 <= i < len(frames) for i in d.get("still", [])) or not 3 <= len(d.get("still", [])) <= 4:
        bad("still must list 3 or 4 valid frame indexes")
    for t in anim_texts(d):
        if "\u2014" in t or BANNED.search(t):
            bad(f"text {t!r} has an em dash or a banned word")


def main() -> int:
    keys = bib_keys()
    total = 0
    animations = 0
    for outline in sorted((ROOT / "books").glob("*/outline.toml")):
        total += check_book(outline.parent, keys)
        animations += check_anim(outline.parent)
    for problem in problems:
        print("FAIL", problem)
    print(f"{total} chapter files checked, {animations} animations checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

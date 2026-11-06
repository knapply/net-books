#!/usr/bin/env python3
"""Export a structured, plain-text copy of every book.

Usage: python3 tools/export_machine.py [OUTDIR]      (default: _machine)

For each book it writes, under OUTDIR/<book>/machine/:
  book.json       title, author, license, language, parts, and per chapter: id,
                  number, title, purpose, prerequisites, sections, code
                  languages, source path, html path, text path, status
  book.md         the whole book as one plain Markdown file
  chapters/*.md   one plain Markdown file per chapter

and OUTDIR/index.json listing the books.

"Plain" means no Quarto syntax: tabsets become labelled code blocks, callouts
become block quotes, heading attributes are removed. The structured fields come
from outline.toml, the single source of truth, so nothing is parsed out of prose.
Standard library only.
"""
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://knapply.github.io/net-books"
REPO = "https://github.com/knapply/net-books"
LICENSE = {"name": "CC BY-NC-ND 4.0",
           "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/"}
LANGUAGES = ["R", "Python", "Rust"]


def plain(md: str) -> str:
    """Quarto Markdown to plain Markdown."""
    def tabset(match: re.Match) -> str:
        body = re.sub(r"^## (.+)$", r"**\1**", match.group(1), flags=re.M)
        return body.strip("\n") + "\n"

    def callout(match: re.Match) -> str:
        body = match.group(2).strip("\n")
        body = re.sub(r"^## (.+)$", r"**\1.**", body, count=1, flags=re.M)
        return "\n".join("> " + line if line else ">" for line in body.splitlines()) + "\n"

    md = re.sub(r"^::: \{\.panel-tabset[^\n]*\}\n(.*?)^:::[ \t]*$", tabset, md,
                flags=re.S | re.M)
    md = re.sub(r"^::: \{\.callout-(\w+)[^\n]*\}\n(.*?)^:::[ \t]*$", callout, md,
                flags=re.S | re.M)
    md = re.sub(r"^(#{1,6} .*?)\s*\{[#.][^}]*\}\s*$", r"\1", md, flags=re.M)
    md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)\{[^}]*fig-alt=\"([^\"]*)\"[^}]*\}",
                lambda m: f"*Figure: {m.group(3)}* {m.group(1)}", md)
    md = re.sub(r"^```\{\.(\w+)\}", r"```\1", md, flags=re.M)
    md = re.sub(r"^(#{1,6} .*)\n(?!\n)", r"\1\n\n", md, flags=re.M)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def status(source: str) -> str:
    """placeholder: prose still to write; text-complete: prose done, code
    examples pending; complete: nothing pending."""
    if re.search(r"TODO\((prose|exercise|summary|refs)", source):
        return "placeholder"
    return "text-complete" if "TODO(code" in source else "complete"


def sections(md: str) -> list[str]:
    return re.findall(r"^## (.+)$", md, flags=re.M)


def export_book(book: Path, out_root: Path) -> dict:
    outline = tomllib.loads((book / "outline.toml").read_text())
    meta = outline["book"]
    out = out_root / book.name / "machine"
    (out / "chapters").mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    parts: list[dict] = []
    number = 0
    parts_of = []

    def add(kind: str, rel: str, item: dict, part: str | None, num: int | None):
        text_source = (book / rel).read_text()
        text = plain(text_source)
        stem = Path(rel).stem
        entry = {
            "id": item["slug"],
            "kind": kind,
            "number": num,
            "title": item["title"],
            "part": part,
            "purpose": item["purpose"],
            "prerequisites": item["prerequisites"],
            "sections": sections(text),
            "code_languages": LANGUAGES,
            "source": f"books/{book.name}/{rel}",
            "source_url": f"{REPO}/blob/main/books/{book.name}/{rel}",
            "html": f"{SITE}/{book.name}/{rel[:-4]}.html",
            "text": f"{SITE}/{book.name}/machine/chapters/{stem}.md",
            "status": status(text_source),
        }
        (out / "chapters" / f"{stem}.md").write_text(text)
        entries.append(entry)
        return entry

    for part in outline["part"]:
        ids = []
        for chapter in part["chapter"]:
            number += 1
            rel = f"chapters/{number:02d}-{chapter['slug']}.qmd"
            ids.append(add("chapter", rel, chapter, part["title"], number)["id"])
        parts.append({"title": part["title"], "chapters": ids})
    for appendix in outline.get("appendix", []):
        add("appendix", f"appendices/{appendix['slug']}.qmd", appendix, None, None)

    document = {
        "schema": "net-books/1",
        "id": book.name,
        "title": meta["title"],
        "subtitle": meta["subtitle"],
        "author": meta["author"],
        "language": "en",
        "license": LICENSE,
        "site": f"{SITE}/{book.name}/",
        "source_repository": REPO,
        "code_languages": LANGUAGES,
        "parts": parts,
        "chapters": entries,
    }
    (out / "book.json").write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n")

    whole = [f"# {meta['title']}: {meta['subtitle']}\n\nBy {meta['author']}. "
             f"License: {LICENSE['name']}.\n"]
    index = book / "index.qmd"
    if index.exists():
        whole.append(plain(index.read_text()))
    for entry in entries:
        whole.append(plain((ROOT / entry["source"]).read_text()))
    (out / "book.md").write_text("\n\n".join(whole))
    return {"id": book.name, "title": meta["title"], "author": meta["author"],
            "metadata": f"{SITE}/{book.name}/machine/book.json",
            "text": f"{SITE}/{book.name}/machine/book.md",
            "site": f"{SITE}/{book.name}/"}


def main() -> int:
    out_root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_machine"
    books = [export_book(path.parent, out_root)
             for path in sorted((ROOT / "books").glob("*/outline.toml"))]
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "index.json").write_text(
        json.dumps({"schema": "net-books/1", "books": books}, indent=2) + "\n")
    print(f"exported {len(books)} book(s) to {out_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

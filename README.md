# net-books

[![site](https://github.com/knapply/net-books/actions/workflows/pages.yml/badge.svg)](https://github.com/knapply/net-books/actions/workflows/pages.yml)
[![license](https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-lightgrey)](LICENSE.md)
[![stars](https://img.shields.io/github/stars/knapply/net-books?style=flat)](https://github.com/knapply/net-books/stargazers)
[![forks](https://img.shields.io/github/forks/knapply/net-books?style=flat)](https://github.com/knapply/net-books/forks)
[![watchers](https://img.shields.io/github/watchers/knapply/net-books?style=flat)](https://github.com/knapply/net-books/watchers)
[![issues](https://img.shields.io/github/issues/knapply/net-books)](https://github.com/knapply/net-books/issues)
[![last commit](https://img.shields.io/github/last-commit/knapply/net-books)](https://github.com/knapply/net-books/commits/main)
[![commit activity](https://img.shields.io/github/commit-activity/m/knapply/net-books)](https://github.com/knapply/net-books/graphs/commit-activity)
[![repo size](https://img.shields.io/github/repo-size/knapply/net-books)](https://github.com/knapply/net-books)
[![page views](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fknapply%2Fnet-books%2Fstats%2Fbadge-views.json)](https://github.com/knapply/net-books/graphs/traffic)
[![visitors](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fknapply%2Fnet-books%2Fstats%2Fbadge-visitors.json)](https://github.com/knapply/net-books/graphs/traffic)
[![clones](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fknapply%2Fnet-books%2Fstats%2Fbadge-clones.json)](https://github.com/knapply/net-books/graphs/traffic)

Open books on network analysis. One repository, one book per folder under
`books/`, shared build tooling and print settings under `shared/`. The website
is built from this repository and published with GitHub Pages.

| Book | Folder | Status |
| --- | --- | --- |
| Social Network Analysis (R, Python, Rust) | `books/sna/` | skeleton |

Author: Brendan Knapp. License: CC BY-NC-ND 4.0 (see `LICENSE.md`).

## Design

- Voice: fun, empathetic, plain-spoken, built to make technical ideas
  accessible. See `docs/VOICE.md`.
- Plain-text sources (`.qmd`: Markdown plus code chunks), one file per chapter,
  in the style of R for Data Science and bookdown books: short chapters, a
  prerequisites box, runnable examples, exercises, a summary.
- Every code example has three tabs, R, Python and Rust (JavaScript and other languages
  come later). In the HTML book the
  reader picks a language once and every example follows. In print each example
  shows the versions one after another (see `shared/tex/`).
- One source, three outputs: HTML (website), PDF (print, via LaTeX) and EPUB.
  `docs/PUBLISHING.md` covers trim sizes, soft and hard cover, and what a
  printer asks for.
- Rust examples run against the engine and are compiled before they go in. R and
  Python tabs stay placeholders until their packages are ready; each placeholder
  says what it will do. No example is written against an API that does not exist.
- Later: a GUI edition. Once the graphical interface exists, each example gains
  a fourth way to follow along (the same steps by pointing and clicking), either
  as a fourth tab or as a separate edition built from the same chapters. Keep
  prose tool-neutral so both work.

## Layout

```
books/<book>/
  _quarto.yml        book config, generated; extends shared/quarto-common.yml
  outline.toml       parts, chapters, one-line purpose of each
  index.qmd          preface
  chapters/*.qmd     generated from outline.toml, then written by hand
  appendices/*.qmd
  references.qmd
  data/              small datasets used in examples
shared/
  quarto-common.yml  formats shared by every book (html, pdf, epub)
  css/book.css       web styling
  tex/               print preamble (trim size, fonts, code blocks)
  bib/references.bib one bibliography for all books
  templates/         chapter template with the language tabset
tools/
  new_chapters.py    stamp chapter files from a book's outline.toml
  export_machine.py  plain-text and JSON export of every book (published with the site)
  check_books.py     structure checks (tabs present, ids unique, citations resolve)
  build.sh           render a book to html, pdf or epub
.github/workflows/
  pages.yml          build the site and publish it with GitHub Pages
docs/PUBLISHING.md   print and distribution notes
docs/VOICE.md        how the prose should sound (read before writing)
```

## Readable by people and programs

- Sources are plain Markdown, one file per chapter, readable on GitHub as is.
- Structure lives in data, not in prose: `outline.toml` is the single source of
  truth for parts, chapters, purposes and prerequisites.
- Every deployed book also publishes, under `/<book>/machine/`: `book.json`
  (outline, ids, sections, status, links), `book.md` (the whole book as plain
  Markdown) and `chapters/*.md`. `/index.json` lists the books. Built by
  `tools/export_machine.py`.
- Each page carries schema.org `Book` metadata and links to those files; pages
  have source and issue links, search, and a sitemap.

## Add a chapter

1. Add it to `books/<book>/outline.toml`.
2. `python3 tools/new_chapters.py books/<book>` (creates missing files only,
   never overwrites).
3. `python3 tools/check_books.py`.

## Build

```
tools/build.sh sna html
tools/build.sh sna pdf
tools/build.sh sna epub
```

Needs Quarto (which brings Pandoc), a TeX distribution with XeLaTeX for PDF, and
R and Python only for executing chunks. Chunks are not executed while they are
placeholders (`execute: eval: false` in the shared config).

## Publishing the website

Every push to `main` runs `.github/workflows/pages.yml`, which renders each book
to HTML and deploys it. One-time setting: repository Settings, Pages, Source:
GitHub Actions. The site lands at `https://knapply.github.io/net-books/`, with
each book under its own folder.

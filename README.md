# knappnet books

Source for the books that go with knappnet. One repository, one book per folder
under `books/`, shared build tooling and print settings under `shared/`.

| Book | Folder | Status |
| --- | --- | --- |
| Social Network Analysis (R, Python, JavaScript) | `books/sna/` | skeleton |
| Cyber networks | `books/cyber/` | outline only |

Author: Brendan Knapp.

## Design

- Plain-text sources (`.qmd`: Markdown plus code chunks), one file per chapter,
  in the style of R for Data Science and bookdown books: short chapters, a
  prerequisites box, runnable examples, exercises, a summary.
- Every code example has three tabs: R, Python, JavaScript. In the HTML book the
  reader picks a language once and every example follows. In print each example
  shows the three versions one after another (see `shared/tex/`).
- One source, three outputs: HTML (website), PDF (print, via LaTeX) and EPUB.
  `docs/PUBLISHING.md` covers trim sizes, soft and hard cover, and what a
  printer asks for.
- Code is placeholder only until the knappnet measure registry lands; each
  placeholder says which measure it will call. No example is written against an
  API that does not exist yet.

## Layout

```
books/<book>/
  _quarto.yml        book config; extends shared/quarto-common.yml
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
  templates/         chapter template with the three-language tabset
tools/
  new_chapters.py    stamp chapter files from a book's outline.toml
  check_books.py     structure checks (tabs present, ids unique, links resolve)
  build.sh           render a book to html, pdf or epub
docs/PUBLISHING.md   print and distribution notes
```

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

Needs Quarto (which brings Pandoc), a TeX distribution with XeLaTeX or LuaLaTeX
for PDF, R and Python for executing chunks. Chunks are not executed while they
are placeholders (`execute: eval: false` in the shared config).

All rights reserved.

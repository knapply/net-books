#!/usr/bin/env bash
# Render one book. Usage: tools/build.sh BOOK [html|pdf|epub|all]
# Output lands in books/BOOK/_book/ (git-ignored).
set -euo pipefail
cd "$(dirname "$0")/.."

book="${1:?usage: tools/build.sh BOOK [html|pdf|epub|all]}"
format="${2:-html}"

command -v quarto >/dev/null || { echo "quarto is not installed (https://quarto.org)"; exit 1; }
[ -d "books/$book" ] || { echo "no such book: books/$book"; exit 1; }

python3 tools/new_chapters.py "books/$book"
python3 tools/check_books.py

if [ "$format" = "all" ]; then
  quarto render "books/$book"
else
  quarto render "books/$book" --to "$format"
fi

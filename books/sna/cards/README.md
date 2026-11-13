# Interpretation cards

One TOML file per measure or model. A card is the short, checked guidance that sits
next to a number: what it measures, when it is valid, how to read it in different
settings, what you may and may not claim, and how to report it. Cards are written
for people and for programs that interpret results for people (for example an MCP
server that runs knappnet and then explains the output). They are exported with the
book (`python3 tools/export_machine.py`) as `cards.json`.

Required fields (see tools/check_books.py):

| field | meaning |
| --- | --- |
| id, title, kind | `kind` is `measure`, `model` or `procedure` (a repeatable analysis step or checklist, such as a permutation test or the reporting checklist) |
| chapter | slug of the chapter that teaches it |
| summary | one sentence |
| answers | the question it answers, in plain words |
| data_requirements | list: what the network must look like |
| assumptions | list: what must hold for the number to mean what it seems to |
| readings | list of `{context, high, low}`: how to read it in different settings |
| pitfalls | list: common mistakes |
| checks | list: how to stress-test the result before reporting it |
| do_not_claim | list: conclusions the number cannot support |
| report_template | text with `{placeholders}`: a defensible way to state the result |
| related | list of card ids |
| sources | list of bibliography keys (must exist in references.bib) |
| knappnet | table with `rust`, `r`, `python`: the call that computes it |

Keep each line a plain sentence. No claim without a reason; no reason without a source
or a check that can be run.

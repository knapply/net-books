# Authoring rules: Graph and Network Algorithms

House rules for `books/algorithms/`. They sit on top of `docs/VOICE.md` (read it first, especially
"Friendly for everyone" and "Animations") and `docs/ANIMATION.md`.

## Who it is for

Someone with no computer science degree: an analyst, a social scientist, a curious engineer. Nothing
may assume they know Big-O, recursion, pseudocode or what a "data structure" is. Every idea earns its
place with a story, a picture and a tiny example before any notation.

## Shape of a chapter

1. **The short version** (3 to 5 sentences, no symbols) and **Why you might care**.
2. **A story first.** An everyday picture of the problem: a queue at a cafe, passing notes down a row,
   planning errands, water through pipes.
3. **The tiny example, by hand.** Five to ten people, drawn. Work it step by step in words and numbers.
4. **The idea in steps.** A short numbered list in ordinary words. If pseudocode helps, keep it under
   fifteen lines, annotated line by line, and follow it with an "In plain words" callout.
5. **What it costs, in plain words.** "Double the network and the work doubles" before any O(...).
   Then the formal statement, then an "In plain words" callout that plugs in real numbers.
6. **At a glance** table: what it answers, time, memory, when to use it, when not to.
7. **Where it goes wrong.** Common mistakes, edge cases, what to check.
8. **If you like proofs** (optional callout): a short, friendly argument for why it works. Never
   required to follow the chapter.
9. **Code** (stubs, see below), exercises (3 to 6, mix of by-hand, think-it-through and coding) with
   short worked answers at the end, a summary, further reading.

Target length: 600 to 1,100 lines of source per chapter, a 30 to 40 minute read. Short beats complete;
depth lives in the further reading and the proof boxes.

## Pictures and motion

- Every idea gets a picture. At least six figures per chapter, drawn with the figure tools
  (`tools/fig_*.py`; one new module per chapter, for example `tools/fig_alg_traversal.py`, registered
  with one line in `tools/make_figures.py`). Match the look of the SNA book figures.
- Use animation wherever motion explains better than a still: a search spreading, a queue changing, a
  heap reshuffling, flow filling pipes, labels merging. See `docs/ANIMATION.md`. Aim for two to four per
  chapter where they help; none where they do not.
- Frames come from knappnet results where the engine exposes the algorithm. When the step-by-step trace
  is fully determined by the textbook rule (queue order, heap contents), the scene may compute it with a
  short reference routine, but the scene must also assert that its final answer equals the engine's
  result for the same graph, run on btower and committed as raw data. If the engine cannot give that
  answer, leave `<!-- TODO(animation): needs ... -->` and move on.
- Captions and alt text in the book's voice. Every frame caption is a plain sentence.

## Code is stubs for now

Keep the standard three-tab block (R, Python, Rust) with `TODO(code, <language>): <what it will do>`
inside each tab and `TODO(output)` in the output block. Write the stub line so it says exactly what
the code will compute and print, in one sentence, so it can be implemented later without guessing.
Write no code beyond that. `python3 tools/pending.py` lists every stub.

## Rules carried over

- No em dashes. Contractions. Short paragraphs.
- Name people in examples (Ana, Ben, Chloe...) and use the same tiny networks across chapters where
  you can, so readers see old friends.
- Define every term the first time. No symbol without a name.
- Formulas stay, each with an "In plain words" callout right after.
- Cite with `@key` from `shared/bib/references.bib`. Only add entries you are sure of (authors, title,
  year, venue); leave out fields you cannot confirm. Check that braces balance and keys are unique.
- The SNA book is at https://knapply.github.io/net-books/sna/ . Mention it by name and link, not with
  `@sec-` cross-references (those do not work across books).
- Run `python3 tools/check_books.py` before every push. Commit as knapply with plain messages.

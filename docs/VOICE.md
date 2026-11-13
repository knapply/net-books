# Voice and style

How the books sound, so every chapter reads like the same person talking. The
goal: a friendly guide who has been where the reader is and wants them to get it.

## Tone

- Fun, warm, a little playful. The humor comes from the material and from being
  honest about how confusing network analysis can be.
- Empathetic. Name the moment a reader is likely to feel lost, then get them
  through it. Never call something obvious or easy.
- Speak to "you". Use "we" when working through something together. Use "I" for
  the author's own experience and opinions.
- Plain and confident. If something is subtle, say so and explain it.

## Explaining technical ideas

In this order, stopping as soon as the reader has it:

1. The question the idea answers, in plain words.
2. A tiny example you can check by hand (five nodes, not five thousand).
3. The idea in words, with an analogy only when it really fits.
4. The formula, once the reader knows what it says. Say what each symbol means.
5. The code, in the language tab block.
6. What the result means, and what it doesn't.

## Habits

- Define a term the first time it appears, in a sentence.
- One new idea per paragraph. Short paragraphs, varied sentence length.
- Concrete over abstract: a named group of real people or things beats "a set of
  actors".
- Say why before how. Readers push through hard parts when they know the payoff.
- Be honest about limits, disagreements between methods, and common mistakes.
- Ordinary words over formal ones: "use", "show", "start".
- Contractions, the way you'd say it out loud.
- Read it aloud. If you wouldn't say it across a table, rewrite it.

## The target register

> Start with the simplest question you can ask about someone in a network: how
> many people are they connected to? That count is their degree. It's crude, and
> it's still the first thing worth checking, because a surprising number of
> bigger ideas turn out to be degree wearing a costume.

## Before a chapter is done

- Could a motivated reader with no network background follow it?
- Is there at least one example they can verify by hand?
- Does each hard idea get a moment of reassurance and a payoff?
- Does it sound like the other chapters?

## Friendly for everyone (standing rule, 13 November 2026)

The book keeps its formulas and formal definitions, and every one of them must
come wrapped in friendly explanation, so a reader with no math or coding
background can follow the whole text.

- Every displayed formula or formal definition gets, right after it, a callout
  or paragraph starting "In plain words", that says what it computes, reads the
  symbols out loud one by one, and gives a number from a tiny example.
- Before a formula, say what question it answers in one ordinary sentence.
- No symbol without a name the first time: "the sum over all ties" before the
  sigma, "the number of people, which we call n".
- Every chapter opens with "The short version" (3 to 5 sentences, no symbols,
  no code) and a plain-language "Why you might care", so a reader can stop there.
- Jargon gets a one-sentence definition at first use; tool names and package
  names are never needed to understand an idea.
- Every code tabset is introduced by one sentence saying what it does and what to
  look for in the output, and followed by one sentence reading the result.
- Prefer a real, named example and an everyday analogy before the abstraction.
- Reassure: say when a part is the hard one, that it can be skimmed on a first
  read, and what the reader will still have if they skip it.
- Math stays correct and complete. Friendly means more explanation, not less
  rigor; never delete a formula to make a page easier.

## Code rules (standing, 13 November 2026)

- **Only show what the tool really does.** R and Python tabs call functions the knappnet
  packages actually expose today. If the package lacks a function, the tab is a stub:
  a short comment naming the missing function, no hand-written replacement, and an
  empty output block:

  ```r
  # TODO(code, R): needs <what knappnet would expose, e.g. net_swap_edges()>
  ```
  ```text
  TODO(output)
  ```

  Rust tabs stay as they are. `python3 tools/pending.py` lists every stub so we can
  see what is still missing.
- **R stays simple.** Base R, plus `library(knappnet)` and nothing else unless there is
  no sensible alternative. No tidyverse (dplyr, purrr, tidyr, tibble), no pipes
  chains of verbs. Read results the way a student would: name the vector or list
  (`setNames()`, `names<-`), or build a plain `data.frame` or `table`, and let R print it.
  Output does not have to look like the Python or Rust output; it has to be easy to read.
  Native pipe `|>` is fine for one or two steps; no loops written out for show, no `print()`
  or `cat()`.

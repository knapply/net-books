"""Read and rewrite the language tabsets in the books' .qmd files.

A tabset looks like

    ::: {.panel-tabset group="language"}
    ## R
    ```r ... ```
    ::: {.code-output}
    ```text ... ```
    :::
    ## Python
    ...
    :::

Each tab owns the output it printed. Standard library only.
"""
import re

OPEN = re.compile(r'^::: \{\.panel-tabset group="language"\}\s*$')
DIV_OPEN = re.compile(r"^:::+ *(\{.*\}|\w+)\s*$")
DIV_CLOSE = re.compile(r"^:::+\s*$")
FENCE = re.compile(r"^```(\w+)\s*$")


def tabsets(lines):
    """Yield (start, end) line indexes of each language tabset (end = closing ':::')."""
    i = 0
    while i < len(lines):
        if OPEN.match(lines[i]):
            depth, j = 1, i + 1
            while j < len(lines) and depth:
                if DIV_CLOSE.match(lines[j]):
                    depth -= 1
                elif DIV_OPEN.match(lines[j]):
                    depth += 1
                j += 1
            yield i, j - 1
            i = j
        else:
            i += 1


def tabs_of(lines, start, end):
    """Return {name: dict(head, code, out)} for one tabset. code/out are (first, last, text)
    where first/last are line indexes of the fence lines; out may be None."""
    heads = [(k, lines[k][3:].strip()) for k in range(start + 1, end) if lines[k].startswith("## ")]
    result = {}
    for n, (h, name) in enumerate(heads):
        stop = heads[n + 1][0] if n + 1 < len(heads) else end
        code = out = None
        k = h + 1
        while k < stop:
            m = FENCE.match(lines[k])
            if m and code is None and m.group(1) != "text":
                e = k + 1
                while not lines[e].startswith("```"):
                    e += 1
                code = (k, e, "\n".join(lines[k + 1:e]))
                k = e
            elif lines[k].startswith("::: {.code-output}"):
                f = k + 1
                while not FENCE.match(lines[f]):
                    f += 1
                e = f + 1
                while not lines[e].startswith("```"):
                    e += 1
                out = (k, e + 1, "\n".join(lines[f + 1:e]))  # k = div open, e+1 = div close
                k = e + 1
            k += 1
        result[name] = dict(head=h, stop=stop, code=code, out=out)
    return result


def set_output(lines, tab, text):
    """Return new lines with the tab's output block replaced (or added after its code)."""
    block = ["::: {.code-output}", "```text", *text.rstrip("\n").split("\n"), "```", ":::"]
    if tab["out"]:
        k, close, _ = tab["out"]
        return lines[:k] + block + lines[close + 1:]
    e = tab["code"][1]
    return lines[:e + 1] + [""] + block + lines[e + 1:]

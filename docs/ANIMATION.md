# Animations

Short, looping pictures for ideas that motion explains better than a still. An animation is an ordinary Quarto figure
that a small script upgrades in the browser. Everything else (print, PDF, EPUB, search engines, readers with no
JavaScript) sees a still picture, so nothing is lost without the script.

## Add one

1. **Get the numbers from knappnet.** Add a block to `tools/anim_data/src/main.rs` that calls the engine and writes
   `books/sna/data/anim/<id>.frames.json`. "Stepwise" means honest repeated calls (same graph and seed, growing budget) or a
   view fully determined by a result (BFS levels from distances, peel rounds from coreness). Never type numbers in. If the
   engine cannot give them, leave a stub (below) and do not draw the figure.
2. **Run it on btower**, bench runner, from the engine checkout (see the knappnet-btower notes): `tools/btower.sh -r bench ...`,
   then fetch the output branch and commit the `.frames.json` files and `PROVENANCE.txt`.
3. **Describe the scene** in `tools/make_anim.py`: add a builder that turns the raw frames into `states` (one per frame:
   node roles, edge roles, panel values, caption) and add it to `BUILDERS`. Run `python3 tools/make_anim.py`; it writes
   `figures/anim/<id>.json` and `figures/anim/<id>-still.svg`. Output is deterministic.
4. **Put the figure in the chapter**, one sentence before it saying what to watch:

       ![Human-sounding caption.](../figures/anim/<id>-still.svg){#fig-<name>-anim fig-alt="What the still shows and how it changes."}

5. `python3 tools/check_books.py` and `python3 tools/test_anim.py` (needs Playwright and a Chromium).

The convention: `figures/anim/<id>-still.svg` is the picture, `figures/anim/<id>.json` is the player data. The script finds
every `img[src$="-still.svg"]`, and when one is within 400 px of the screen it fetches the JSON next to it, builds one SVG
and puts it after the image. The image stays in the page, hidden on screen and shown (with the player hidden) when printing.
If the JSON cannot be fetched the image just stays.

Scenes added after the pilot live one per module in `tools/anim_scenes/<name>.py` and their engine runs in
`tools/anim_data/src/bin/<id>.rs`, so two people adding scenes never edit the same file. A module defines
`BUILDERS = {id: builder}`; `anim_scenes.discover()` (called once from `make_anim.py`) collects every module whose name does not
start with an underscore. A builder imports `make_anim` inside the function to reuse `encode`, `load`, `layout`, `filmstrip` and the
palette, and returns `(scene, still_svg)`. Optional scene keys: `"dir": True` (arrows) and `"compact": True` (a smaller still for
networks of 30 or more people). A state is `(nodes, edges, panel_values, caption)`; add a fifth element, a position `(x, y)` for
every node, when the layout moves between frames (the player moves the dots, and the still draws each frame where it was).
`anim_scenes/_strip.py` has `lean_filmstrip`, a variant of the still that puts all ties of one style into one path, for pictures
with a hundred or more ties. `anim_scenes/compact.py` is a similar strip that also takes `tag=` (a function giving the text under each
dot) and fits the picture to the frame; the betweenness, PageRank, k-core, community and rewiring scenes use it. It holds no scene.

## Where the script lives

`shared/js/netanim.js` is the one source (vanilla, no libraries, 6 KB budget). `tools/new_chapters.py` inlines it into every page
head of a book that has a `figures/anim` folder, and writes `resources: figures/anim/*.json` under `project:` so Quarto publishes
the data files (it only copies files it can see referenced). Inlining is chosen because the book folder cannot reference a file
outside itself and a static page cannot rely on a path that depends on where the site is hosted. After editing the script, run
`python3 tools/new_chapters.py books/sna`; `check_books.py` fails if `_quarto.yml` is out of date.

## Player behavior

- Controls under the picture: Back, Play or Pause, Next, Restart, a range slider and "Step n of N". Space toggles play and Left or
  Right step while the player has focus.
- A caption line shows the frame's text. It is `aria-live="polite"` only while paused or stepping, never while playing.
- Autoplay when at least half the player is on screen; pauses when it leaves the screen or the tab is hidden. Loops with a 1.5 s
  hold on the last frame. 1.2 s per frame unless the JSON says `ms`. Pressing Pause or any step control stops autoplay for good
  until Play is pressed.
- `prefers-reduced-motion`: no autoplay and instant changes.
- Motion is CSS transitions on transform, fill and stroke; the script draws no frames itself.
- Colors come from the book's figure palette, so animations and figures look alike. The player draws its own white paper
  background, like the figures, so dark mode needs nothing.

## JSON schema (version 1)

    {"v":1, "id":"bfs-expansion", "w":640, "h":360, "ms":1200,
     "nodes":[{"id":"Jo","x":120,"y":80}],      // id is drawn under the dot; canvas units
     "edges":[[0,1]], "dir":false,               // index pairs; dir:true adds arrowheads
     "panel":{"kind":"bars","x":452,"y":74,"w":172,"h":200,"labels":[...],"max":5,"title":"..."},
     "frames":[{"t":"Caption.", "n":{"0":{"f":"src","r":22,"l":"0","ring":1}}, "e":{"3":{"k":"hot","w":3}},
                "p":{"0":[x,y]}, "m":[0.4,0.7]}],
     "still":[0,2,5]}                            // 3 or 4 frames for the filmstrip

Frames are delta encoded: a frame lists only what changed since the one before it (the first frame starts from defaults:
node `f` base, `r` 16, `l` empty, `ring` 0; edge `k` base, `w` 1.6). `f` and `k` are role names: base, src, reach, hot, dim,
a, b, c, d, e. `r` is the dot radius, `l` the text inside it, `ring` 1 draws a halo. `m` is the panel's values for the frame.
Panel kinds the player draws today: `bars` (one horizontal bar per label, `max` is the full width) and `text` (the `m`
strings joined on one line). `line` is reserved in the schema and not drawn yet. A panel is optional; `null` omits it.

## Budgets

Script 6 KB. Each JSON 40 KB. Each still 25 KB. `check_books.py` enforces these, that every still has `fig-alt`, a matching JSON
that follows the schema, no em dashes, and none of the words generated or AI in captions or frame text.

## Stubs

If the engine does not expose what an animation needs, do not write the numbers by hand. Put one line where the figure
would go:

    <!-- TODO(animation): needs <what knappnet would expose> -->

`python3 tools/pending.py` lists these beside the code stubs.

## Stills

The still is a 2 by 2 filmstrip of the frames named in `still`, drawn with `tools/figs.py` in the figures' style. Its alt
text (`fig-alt`) says what the filmstrip shows and how the picture changes from the first frame to the last.

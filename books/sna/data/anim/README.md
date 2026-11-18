# Raw engine results for the animations

`<id>.frames.json` is what the knappnet engine returned for one animation, step by step. `tools/make_anim.py` turns it
into the player data and the still picture in `figures/anim/`. Nothing here is typed in by hand except the ten-person
friendship network (the book's usual edge list).

| file | engine call | what a step is |
| --- | --- | --- |
| bfs-expansion.frames.json | `traversal::frontier::compute_bfs_levels` from Jo (index 9) | the distance of every person; step k shows everyone within k steps |
| eigen-converge.frames.json | `metrics::nx_power::compute_katz` with alpha 1, beta 0, unscaled, `max_iter` 1, started from the previous round | round k of the passing game, one call per round (unscaled, so these are walk counts; the animation rescales each round so the top is 1) |
| eigen-converge.frames.json (`settled`) | `metrics::eigenvector::compute_eigenvector_centrality`, default options | the scores the rounds settle on |

The engine's eigenvector function converges in one call, so the rounds are asked for one at a time: with alpha 1 and beta 0
the NetworkX-compatible Katz iteration computes exactly "new score = sum of the friends' scores", and a huge tolerance makes
each call stop after a single step. `make_anim.py` checks that the last round and the engine's answer agree.

## Regenerating

`tools/anim_data` is a small crate that depends on the engine. It is not part of any workspace. Run it from a place where
`../../../knappnet` (relative to `tools/anim_data`) is a knappnet checkout, or edit the path in its `Cargo.toml`:

    cd tools/anim_data && cargo run --release -- ../../books/sna/data/anim
    cd ../.. && python3 tools/make_anim.py

The committed files were made on the btower bench runner (knappnet commit recorded in `PROVENANCE.txt` beside them).

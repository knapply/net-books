# Raw engine results for the animations

`<id>.frames.json` is what the knappnet engine returned for one animation, step by step. `tools/make_anim.py` turns it
into the player data and the still picture in `figures/anim/`. Nothing here is typed in by hand except the ten-person
friendship network (the book's usual edge list).

| file | engine call | what a step is |
| --- | --- | --- |
| bfs-expansion.frames.json | `traversal::frontier::compute_bfs_levels` from Jo (index 9) | the distance of every person; step k shows everyone within k steps |
| eigen-converge.frames.json | `metrics::nx_power::compute_katz` with alpha 1, beta 0, unscaled, `max_iter` 1, started from the previous round | round k of the passing game, one call per round (unscaled, so these are walk counts; the animation rescales each round so the top is 1) |
| eigen-converge.frames.json (`settled`) | `metrics::eigenvector::compute_eigenvector_centrality`, default options | the scores the rounds settle on |
| swap-chain.frames.json | `metrics::rewiring::run_double_edge_swap` on the Florentine marriages, seed 1, k = 0 to 10 one at a time, then 12 to 60; degrees from `compute_degree` | k accepted swaps, one call per k (same seed, so each result extends the last) |
| ergm-steps.frames.json | `ergm::Chain::step` on the karate club from the real network, seed 1, coefficients from `fit_mcmle`; statistics from `Chain::statistics` | one accepted Metropolis-Hastings change (the engine reports accepted or refused for every proposal) |
| saom-steps.frames.json | `saom::simulate_period`, office network, outdegree -2, reciprocity 1.5, seed 1, one run, rate swept from 0 to 3 in steps of 0.002 | one change opportunity: the engine draws the same sequence for a seed at any rate, so a larger rate gives a longer prefix, and `ministeps` says how many opportunities it holds. The engine does not say who acted when nothing changed |
| latent-settle.frames.json | `latent_space::fit`, dim 2, `max_iter` = 0, 1, 2, 3, 5, ... 400, then to convergence (807 steps) | the k-th ascent step; the fit is deterministic, so one call per k |

The four newer files come from one run of `tools/anim_data/src/bin/*.rs` (`cargo run --release --bin swap-chain -- OUT`, and so on).
Diffusion and contagion (chapter 24) has no file: the engine has no SI, SIR, threshold or cascade model.

The engine's eigenvector function converges in one call, so the rounds are asked for one at a time: with alpha 1 and beta 0
the NetworkX-compatible Katz iteration computes exactly "new score = sum of the friends' scores", and a huge tolerance makes
each call stop after a single step. `make_anim.py` checks that the last round and the engine's answer agree.

## Regenerating

`tools/anim_data` is a small crate that depends on the engine. It is not part of any workspace. Run it from a place where
`../../../knappnet` (relative to `tools/anim_data`) is a knappnet checkout, or edit the path in its `Cargo.toml`:

    cd tools/anim_data && cargo run --release -- ../../books/sna/data/anim
    cd ../.. && python3 tools/make_anim.py

The committed files were made on the btower bench runner (knappnet commit recorded in `PROVENANCE.txt` beside them).

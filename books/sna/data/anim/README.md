# Raw engine results for the animations

`<id>.frames.json` is what the knappnet engine returned for one animation, step by step. `tools/make_anim.py` turns it
into the player data and the still picture in `figures/anim/`. Nothing here is typed in by hand except the ten-person
friendship network (the book's usual edge list).

| file | engine call | what a step is |
| --- | --- | --- |
| bfs-expansion.frames.json | `traversal::frontier::compute_bfs_levels` from Jo (index 9) | the distance of every person; step k shows everyone within k steps |
| eigen-converge.frames.json | `metrics::nx_power::compute_katz` with alpha 1, beta 0, unscaled, `max_iter` 1, started from the previous round | round k of the passing game, one call per round (unscaled, so these are walk counts; the animation rescales each round so the top is 1) |
| eigen-converge.frames.json (`settled`) | `metrics::eigenvector::compute_eigenvector_centrality`, default options | the scores the rounds settle on |
| betweenness-routes.frames.json | `metrics::betweenness::compute_betweenness_from_sources` with one source per call (unnormalized, pairs counted once), distances from `compute_bfs_levels`; the sum over sources is checked against `compute_betweenness` | one starting person: what their shortest routes add to everyone's score |
| pagerank-settle.frames.json | `metrics::nx_power::compute_pagerank` (damping 0.85), `max_iter` 1 and a tolerance too large to fail, started from the previous round; settled: `metrics::spectral::compute_pagerank` | round k of the passing game, one call per round |
| kcore-peel.frames.json | `metrics::cores::compute_coreness` on the karate club (`data/karate/edges.csv`) | nothing is stepped by the engine: `make_anim.py` replays the peel (remove everyone below the bar, repeat) and asserts that every person leaves at the bar their engine core number says |
| louvain-levels.frames.json, leiden-levels.frames.json | `metrics::louvain_nx::find_louvain_communities` and `metrics::leiden_nx::find_leiden_communities` (the engine's ports that return every level), resolution 1, Python-style generator seeded with 1; modularity of each level from `metrics::community::compute_modularity` | one level: the partition after that pass (the last Leiden level repeats, so the animation drops it) |
| small-world-rewiring.frames.json | `generate::sample_small_world(30, 4, p, 1, seed 1)` for p = 0, 0.05, 0.1, 0.2, 0.4, 0.7, 1; `compute_average_clustering` and `compute_mean_distance` | one value of p. The generator makes a fresh draw for each p, so a later picture is not the earlier one plus more rewiring |
| swap-chain.frames.json | `metrics::rewiring::run_double_edge_swap` on the Florentine marriages, seed 1, k = 0 to 10 one at a time, then 12 to 60; degrees from `compute_degree` | k accepted swaps, one call per k (same seed, so each result extends the last) |
| ergm-steps.frames.json | `ergm::Chain::step` on the karate club from the real network, seed 1, coefficients from `fit_mcmle`; statistics from `Chain::statistics` | one accepted Metropolis-Hastings change (the engine reports accepted or refused for every proposal) |
| saom-steps.frames.json | `saom::simulate_period`, office network, outdegree -2, reciprocity 1.5, seed 1, one run, rate swept from 0 to 3 in steps of 0.002 | one change opportunity: the engine draws the same sequence for a seed at any rate, so a larger rate gives a longer prefix, and `ministeps` says how many opportunities it holds. The engine does not say who acted when nothing changed |
| latent-settle.frames.json | `latent_space::fit`, dim 2, `max_iter` = 0, 1, 2, 3, 5, ... 400, then to convergence (807 steps) | the k-th ascent step; the fit is deterministic, so one call per k |
| force-settle.frames.json | `layout::layout_fruchterman_reingold`, karate club, seed 1, `iterations` = 1, 2, 3, 4, 6, 8, 12, 16, 24, 40, 70, 120, 500 | a complete run with that many rounds (the cooling schedule depends on the budget, so a frame is not a prefix of the next). `make_anim` turns each run to sit over the last (the engine orients every layout on its own) and fits all runs into one box; it scores each frame with the chapter's scale-free stress and checks the last against the chapter's table |
| stress-settle.frames.json | `layout::layout_stress_majorization`, karate club, seed 1, `max_iter` = 1, 2, 3, 4, 5, 6, 8, 10, 14, 20, 30, 60, 500 | a complete run capped at that many sweeps; the engine starts from a rough picture built from the distances and tries up to four restarts, so frames are close to each other from the first |
| projection-forms.frames.json | `metrics::bipartite::project` (onto the women, Count weights) on the southern women with only events 1 to k kept, k = 1 to 14 | the projection after k events; `make_anim` checks every frame against a direct count of shared events |
| temporal-reach.frames.json | `temporal::find_contacts_at` for t = 1 to 6, `temporal::find_temporal_paths` (earliest arrival, out) from Ana and from Dev with the window ending at t, and `temporal::count_temporal_reach` | the meetings happening at time t, and who a message has reached using meetings up to t |
| walk-visits.frames.json | `metrics::walks::sample_walk_visits`, ten-person network, start Jo, restart 0, seed 7, `steps` = 0 to 10, 12, 15, 20, 30, 50, 80, 120, 300, 1000 (the animation uses up to 120) | visit counts after k steps. The walk is one stream used in step order, so k steps are the first k of a longer run; the walker's place is the node whose count rose between k - 1 and k steps (`make_anim` checks that it moved along a tie) |

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

The Louvain and Leiden programs need the 625 integers of `random.Random(1).getstate()[1]` (the engine ports draw from a
Python-style generator): `python3 -c "import random,json;print(json.dumps(random.Random(1).getstate()[1]))" > mt1.json`, then
`community-levels OUT_DIR mt1.json`, run from the book root so it can read `books/sna/data/karate/edges.csv`.
`PROVENANCE-centrality-communities.txt` records the btower run that made these six files.

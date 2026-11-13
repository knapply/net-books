# Stored layouts of the karate club

Used by the visualization chapter (`chapters/05-visualization.qmd`) so that every language scores the same
coordinates. The network is `data/karate` (34 members, 78 ties); node `i` here is member `i`.

## karate_layouts.csv

Columns `layout,node,x,y`, one row per member per layout, coordinates to six decimals.

| layout | how it was made |
| --- | --- |
| random | Park and Miller's generator (`state * 48271 mod 2147483647`, seed 1): member `i` gets the draws `2i-1` and `2i`, each divided by 2147483647 |
| circle | the engine's `layout_circle` (members in file order) |
| force | the engine's `layout_fruchterman_reingold` with `FrOptions { seed: 1, ..Default::default() }` |
| stress | the engine's `layout_stress_majorization` with `StressOptions { seed: 1, ..Default::default() }` |
| spectral | the eigenvectors of the second- and third-smallest eigenvalues of the Laplacian, from the engine's `symmetric_eigen` (columns 1 and 2) |
| mds | the engine's `compute_classical_mds` on the table of graph distances, two dimensions |

The signs of the spectral and classical scaling coordinates are whatever the eigen solver returned; the picture is the same
up to reflection.

## fr_seeds.csv

Columns `seed,x,y`: the engine's force layout with seeds 1 to 20, 34 rows per seed in member order.

## Regenerating

`tools/layout_data.rs` is the program. Make a crate whose `main.rs` is that file and whose `Cargo.toml` depends on the engine,
then run it from `books/sna`. The R and Rust tabs of the visualization chapter check that the engine still makes the force and stress layouts
and the circle from seed 1.

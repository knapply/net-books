# Numbers behind the small-worlds figures

These three small files hold the results that the chapter on random graphs, small worlds
and degree distributions prints, so that its figures are drawn from the same runs as its text.
They are generated, not collected: nothing here is a real network.

| file | what it holds | how it was made |
|---|---|---|
| `degrees.csv` | the degree of each of 2,000 people in two networks, `random` (2,000 people, 4,000 ties placed at random) and `grown` (preferential attachment, 2 ties per newcomer) | the Rust code in the chapter's heavy-tail block, `sample_gnm(2000, 4000, ..., seed 1)` and `sample_preferential(2000, 2, seed 1)`, first draw of each |
| `ws_sweep.csv` | clustering and mean distance of Watts-Strogatz networks (1,000 people, each tied to the 10 nearest) relative to the unrewired ring, for each rewiring probability `p`; mean of 10 draws | the Rust code in the chapter's rewiring block, `sample_small_world(1000, 10, p, 10, seed 1)` |
| `baselines.csv` | transitivity and mean distance of the karate club, the Florentine marriages and Krackhardt's friendship network (directions ignored), observed and in two random baselines | the Rust code in the chapter's baseline block, 500 random networks per cell |

The values are printed to three decimals, as in the chapter.

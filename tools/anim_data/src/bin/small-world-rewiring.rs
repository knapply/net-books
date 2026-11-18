// A small ring lattice rewired with a growing probability (chapter 9).
//   cargo run --release --bin small-world-rewiring -- OUT_DIR
// Thirty people on a ring, each tied to the 2 nearest on each side (k = 4), and the engine's seeded Watts-Strogatz
// generator sample_small_world(30, 4, p, 1, seed 1, ...) for each p. Same seed every time; the generator draws a
// fresh set of rewirings for each p (it does not keep the earlier ones), so the ties in two pictures can differ more
// than the step in p suggests. Clustering and mean distance of each draw come from the engine.
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::generate::sample_small_world;
use knappnet::metrics::descriptive::{compute_average_clustering, compute_mean_distance, ClusteringOptions, PathOptions};
use knappnet::Graph;

const N: usize = 30;
const PS: [f64; 7] = [0.0, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0];

fn main() -> Result<(), knappnet::Error> {
    let out = out_dir();
    let mut rows = Vec::new();
    for &p in &PS {
        let d = &sample_small_world(N, 4, p, 1, 1, 1)?[0];
        let f: Vec<i64> = d.from.iter().map(|&x| x as i64).collect();
        let u: Vec<i64> = d.to.iter().map(|&x| x as i64).collect();
        let g = Graph::from_edges(d.n, &f, &u, None, false)?;
        let c = compute_average_clustering(&g, ClusteringOptions::default())?;
        let l = compute_mean_distance(&g, PathOptions::default(), true)?;
        let ties: Vec<(i64, i64)> = f.iter().zip(&u).map(|(&a, &b)| (a.min(b), a.max(b))).collect();
        rows.push(format!("{{\"p\":{:?},\"ties\":{},\"clustering\":{:?},\"mean_distance\":{:?}}}", p, pairs(&ties), c, l));
    }
    let text = format!(
        "{{\"v\":1,\"id\":\"small-world-rewiring\",\"n\":{N},\"k\":4,\"seed\":1,\"engine\":\"generate::sample_small_world (one draw per p, seed 1); metrics::descriptive::compute_average_clustering and compute_mean_distance (unconnected pairs skipped)\",\"draws\":[{}]}}\n",
        rows.join(","));
    std::fs::write(format!("{out}/small-world-rewiring.frames.json"), text).unwrap();
    println!("wrote small-world-rewiring to {out}");
    Ok(())
}

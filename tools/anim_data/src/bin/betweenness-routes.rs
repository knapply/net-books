// Betweenness one source at a time on the ten-person friendship network (chapter 6).
//   cargo run --release --bin betweenness-routes -- OUT_DIR
// For every person s, the engine's compute_betweenness_from_sources with sources = [s] gives what s's shortest routes
// add to everyone's score; compute_bfs_levels from s gives the distances that say which ties lie on those routes.
// The sum over all sources is checked against compute_betweenness. The scores are the plain counts of routes through
// a person, each pair counted once (undirected), not normalized.
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::metrics::betweenness::{compute_betweenness, compute_betweenness_from_sources, BetweennessOptions};
use knappnet::traversal::frontier::{compute_bfs_levels, Direction};
use knappnet::DegreeMode;

fn main() -> Result<(), knappnet::Error> {
    let out = out_dir();
    let g = kite();
    let opts = BetweennessOptions { threads: 1, ..BetweennessOptions::default() };
    let mut rows = Vec::new();
    let mut sum = vec![0.0f64; 10];
    for s in 0..10u32 {
        let part = compute_betweenness_from_sources(&g, &[s], opts)?;
        let (dist, _) = compute_bfs_levels(&g, s, DegreeMode::All, Direction::Auto)?;
        for (a, b) in sum.iter_mut().zip(&part) {
            *a += b;
        }
        rows.push(format!("{{\"source\":{s},\"contrib\":{},\"distances\":{}}}", floats(&part), ints(&dist)));
    }
    let total = compute_betweenness(&g, opts)?;
    for (a, b) in sum.iter().zip(&total) {
        assert!((a - b).abs() < 1e-9, "the per-source scores do not add up to the full betweenness");
    }
    let text = format!(
        "{{\"v\":1,{},\"engine\":\"metrics::betweenness::compute_betweenness_from_sources (one source per call, unnormalized, undirected pairs counted once); distances: traversal::frontier::compute_bfs_levels; full: compute_betweenness\",\"sources\":[{}],\"total\":{}}}\n",
        kite_header("betweenness-routes"), rows.join(","), floats(&total));
    std::fs::write(format!("{out}/betweenness-routes.frames.json"), text).unwrap();
    println!("wrote betweenness-routes to {out}");
    Ok(())
}

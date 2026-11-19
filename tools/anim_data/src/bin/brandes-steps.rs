// Brandes' two passes from one starting person on the ten-person friendship network (algorithms book, chapter 18).
//   cargo run --release --bin brandes-steps -- OUT_DIR
// Forward pass: distances from traversal::frontier::compute_bfs_levels and shortest-route counts (sigma) from
// bitset::RowPaths on the network's bit rows. Backward pass: what the source's routes add to everyone, from
// metrics::betweenness::compute_betweenness_from_sources with sources = [s] (undirected pairs counted once, so the
// dependency of the textbook rule is twice this value). The full betweenness is written too, for the last caption.
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::bitset::{BitMatrix, RowPaths};
use knappnet::metrics::betweenness::{compute_betweenness, compute_betweenness_from_sources, BetweennessOptions};
use knappnet::traversal::frontier::{compute_bfs_levels, Direction};
use knappnet::DegreeMode;

fn main() -> Result<(), knappnet::Error> {
    let out = out_dir();
    let g = kite();
    let opts = BetweennessOptions { threads: 1, ..BetweennessOptions::default() };
    let mut rows = BitMatrix::new(10);
    for &(a, b) in EDGES.iter() {
        rows.set(a as usize, b as usize);
        rows.set(b as usize, a as usize);
    }
    let mut parts = Vec::new();
    for s in [0u32, 9u32] {
        let (dist, _) = compute_bfs_levels(&g, s, DegreeMode::All, Direction::Auto)?;
        let mut paths = RowPaths::new();
        paths.run(&rows, &rows, 10, s as usize, u32::MAX);
        for v in 0..10 {
            assert_eq!(paths.level(v), dist[v], "bit-row levels disagree with the breadth-first levels");
        }
        let sigma: Vec<f64> = (0..10).map(|v| paths.sigma(v)).collect();
        let contrib = compute_betweenness_from_sources(&g, &[s], opts)?;
        parts.push(format!("{{\"source\":{s},\"distances\":{},\"sigma\":{},\"contrib\":{}}}", ints(&dist), floats(&sigma), floats(&contrib)));
    }
    let total = compute_betweenness(&g, opts)?;
    let text = format!(
        "{{\"v\":1,{},\"engine\":\"distances: traversal::frontier::compute_bfs_levels; route counts: bitset::RowPaths::run; per-source contribution: metrics::betweenness::compute_betweenness_from_sources (one source, unnormalized, undirected pairs counted once); full: compute_betweenness\",\"runs\":[{}],\"total\":{}}}\n",
        kite_header("brandes-steps"), parts.join(","), floats(&total));
    std::fs::write(format!("{out}/brandes-steps.frames.json"), text).unwrap();
    println!("wrote brandes-steps to {out}");
    Ok(())
}

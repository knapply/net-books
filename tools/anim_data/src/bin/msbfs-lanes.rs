// Many breadth-first searches sharing one pass, one bit per search (algorithms book, chapter 19).
//   cargo run --release --bin msbfs-lanes -- OUT_DIR      (run from the net-books root, for the karate club file)
// bitset::MultiBfs::run reports, level by level, every person newly reached and the searches (bits) that reached
// them. Two runs: the ten-person friendship network with 8 searches (Ana to Hana) and the karate club with 16
// (people 1 to 16). Every search's distances are checked against traversal::frontier::compute_bfs_levels, and the
// harmonic sums built from the levels against metrics::closeness::compute_harmonic_centrality (unnormalized).
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::bitset::{MultiBfs, Step, View};
use knappnet::metrics::closeness::{compute_harmonic_centrality, ClosenessOptions};
use knappnet::traversal::frontier::{compute_bfs_levels, Direction};
use knappnet::{DegreeMode, Graph};

fn run(g: &Graph, n: usize, lanes: usize) -> Result<String, knappnet::Error> {
    let sources: Vec<u32> = (0..lanes as u32).collect();
    let mut steps: Vec<String> = Vec::new();
    let mut dist = vec![vec![u32::MAX; n]; lanes];
    for (lane, &s) in sources.iter().enumerate() {
        dist[lane][s as usize] = 0;
    }
    let mut bfs = MultiBfs::new(n);
    bfs.run(View::new(g, DegreeMode::All), &sources, u32::MAX, |step| {
        if let Step::Reached { level, node, sources: bits } = step {
            steps.push(format!("[{level},{node},{bits}]"));
            for lane in 0..lanes {
                if bits >> lane & 1 == 1 {
                    assert_eq!(dist[lane][node as usize], u32::MAX, "a search reached a person twice");
                    dist[lane][node as usize] = level;
                }
            }
        }
    });
    let opts = ClosenessOptions { threads: 1, ..ClosenessOptions::default() };
    let harmonic = compute_harmonic_centrality(g, opts)?;
    for (lane, &s) in sources.iter().enumerate() {
        let (want, _) = compute_bfs_levels(g, s, DegreeMode::All, Direction::Auto)?;
        assert_eq!(dist[lane], want, "the shared search disagrees with a single search");
        let h: f64 = dist[lane].iter().filter(|&&d| d > 0 && d != u32::MAX).map(|&d| 1.0 / d as f64).sum();
        assert!((h - harmonic[s as usize]).abs() < 1e-12, "harmonic sums disagree");
    }
    Ok(format!("\"lanes\":{lanes},\"steps\":[{}],\"harmonic\":{}", steps.join(","), floats(&harmonic)))
}

fn main() -> Result<(), knappnet::Error> {
    let out = out_dir();
    let kite_part = run(&kite(), 10, 8)?;
    let (k, ties) = karate();
    let karate_part = run(&k, 34, 16)?;
    let engine = "\"engine\":\"bitset::MultiBfs::run (one bit per search; Step::Reached gives level, person and the searches' bits); checked against traversal::frontier::compute_bfs_levels and metrics::closeness::compute_harmonic_centrality\"";
    std::fs::write(format!("{out}/msbfs-kite.frames.json"),
        format!("{{\"v\":1,{},{engine},{kite_part}}}\n", kite_header("msbfs-kite"))).unwrap();
    std::fs::write(format!("{out}/msbfs-karate.frames.json"),
        format!("{{\"v\":1,\"id\":\"msbfs-karate\",\"n\":34,\"edges\":{},{engine},{karate_part}}}\n", pairs(&ties))).unwrap();
    println!("wrote msbfs-kite and msbfs-karate to {out}");
    Ok(())
}

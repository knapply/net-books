// PageRank as a passing game on the ten-person friendship network (chapter 6).
//   cargo run --release --bin pagerank-settle -- OUT_DIR
// Round k is one call of the engine's NetworkX-compatible PageRank (metrics::nx_power::compute_pagerank, damping 0.85)
// with max_iter = 1, started from round k-1 (nstart); a tolerance too large to ever fail makes each call stop after one
// step. Where it settles: metrics::spectral::compute_pagerank with default options.
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::metrics::nx_power::compute_pagerank as pagerank_steps;
use knappnet::metrics::spectral::{compute_pagerank, PagerankOptions};

const ROUNDS: usize = 30;

fn main() -> Result<(), knappnet::Error> {
    let out = out_dir();
    let g = kite();
    let mut x = vec![0.1f64; 10];
    let mut rounds = vec![x.clone()];
    for _ in 0..ROUNDS {
        x = pagerank_steps(&g, false, 0.85, None, Some(&x), None, 1, 1e30, 1)?
            .expect("one step always 'converges' with this tolerance");
        rounds.push(x.clone());
    }
    let settled = compute_pagerank(&g, &PagerankOptions { threads: 1, ..PagerankOptions::default() })?;
    let rows: Vec<String> = rounds.iter().map(|r| floats(r)).collect();
    let text = format!(
        "{{\"v\":1,{},\"engine\":\"metrics::nx_power::compute_pagerank (damping 0.85, max_iter 1, tol 1e30, nstart = previous round); settled: metrics::spectral::compute_pagerank (default options)\",\"rounds\":[{}],\"settled\":{}}}\n",
        kite_header("pagerank-settle"), rows.join(","), floats(&settled));
    std::fs::write(format!("{out}/pagerank-settle.frames.json"), text).unwrap();
    println!("wrote pagerank-settle to {out}");
    Ok(())
}

// Betweenness estimated from a growing sample of starting people on Zachary's karate club (algorithms book, ch. 18).
//   cargo run --release --bin betweenness-sampling -- OUT_DIR      (run from the net-books root)
// The sample order is a fixed shuffle of the 34 people (splitmix64, seed 2026, written out below so it can be checked).
// For each k, metrics::betweenness::compute_betweenness_from_sources with the first k people of that order; the
// estimate is that sum times 34 / k. The exact scores come from compute_betweenness. Unnormalized, pairs counted once.
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::metrics::betweenness::{compute_betweenness, compute_betweenness_from_sources, BetweennessOptions};

fn splitmix(state: &mut u64) -> u64 {
    *state = state.wrapping_add(0x9E37_79B9_7F4A_7C15);
    let mut z = *state;
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^ (z >> 31)
}

fn main() -> Result<(), knappnet::Error> {
    let out = out_dir();
    let (g, ties) = karate();
    let n = 34usize;
    let opts = BetweennessOptions { threads: 1, ..BetweennessOptions::default() };
    let mut order: Vec<u32> = (0..n as u32).collect();
    let mut state = 2026u64;
    for i in (1..n).rev() {
        let j = (splitmix(&mut state) % (i as u64 + 1)) as usize;
        order.swap(i, j);
    }
    let exact = compute_betweenness(&g, opts)?;
    let mut rows = Vec::new();
    for k in [1usize, 2, 3, 4, 6, 8, 12, 17, 24, 34] {
        let part = compute_betweenness_from_sources(&g, &order[..k], opts)?;
        rows.push(format!("{{\"k\":{k},\"partial\":{}}}", floats(&part)));
    }
    let text = format!(
        "{{\"v\":1,\"id\":\"betweenness-sampling\",\"n\":{n},\"edges\":{},\"engine\":\"metrics::betweenness::compute_betweenness_from_sources on the first k people of the order (unnormalized, pairs counted once); exact: compute_betweenness\",\"order\":{},\"samples\":[{}],\"exact\":{}}}\n",
        pairs(&ties), ints(&order), rows.join(","), floats(&exact));
    std::fs::write(format!("{out}/betweenness-sampling.frames.json"), text).unwrap();
    println!("wrote betweenness-sampling to {out}");
    Ok(())
}

// Zachary's karate club and its core numbers (chapter 10).
//   cargo run --release --bin kcore-peel -- OUT_DIR      (run from the net-books root: reads data/karate/edges.csv)
// The engine's compute_coreness is the only result; tools/make_anim.py derives the peel rounds from the network and
// checks every person's removal level against it.
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::metrics::cores::compute_coreness;
use knappnet::DegreeMode;

fn main() -> Result<(), knappnet::Error> {
    let out = out_dir();
    let (g, ties) = karate();
    let core = compute_coreness(&g, DegreeMode::All);
    let text = format!(
        "{{\"v\":1,\"id\":\"kcore-peel\",\"n\":34,\"edges\":{},\"engine\":\"metrics::cores::compute_coreness (DegreeMode::All)\",\"coreness\":{}}}\n",
        pairs(&ties), ints(&core));
    std::fs::write(format!("{out}/kcore-peel.frames.json"), text).unwrap();
    println!("wrote kcore-peel to {out}");
    Ok(())
}

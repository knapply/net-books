// Distances from Jo, the keys of the priority queue in the heap animation (algorithms book, chapter 3).
//   cargo run --release --bin heap-order -- OUT_DIR
// The engine's breadth-first levels are the only result. tools/anim_scenes/heap_calls.py builds a heap out of
// them and asserts that taking the smallest one at a time gives exactly the sorted engine distances.
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::traversal::frontier::{compute_bfs_levels, Direction};
use knappnet::DegreeMode;

fn main() -> Result<(), knappnet::Error> {
    let out = out_dir();
    let g = kite();
    let jo = 9u32;
    let (dist, _steps) = compute_bfs_levels(&g, jo, DegreeMode::All, Direction::Auto)?;
    let text = format!(
        "{{\"v\":1,{},\"engine\":\"traversal::frontier::compute_bfs_levels (DegreeMode::All, Direction::Auto)\",\"source\":{jo},\"distances\":{}}}\n",
        kite_header("heap-calls"), ints(&dist));
    std::fs::write(format!("{out}/heap-calls.frames.json"), text).unwrap();
    println!("wrote heap-calls to {out}");
    Ok(())
}

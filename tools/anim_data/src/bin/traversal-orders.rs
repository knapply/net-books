// Raw engine results for the traversal animations (chapter 5 of the algorithms book): breadth-first and depth-first
// search on the ten-person friendship network, neighbours visited in index order (alphabetical, here).
//   cargo run --release --bin traversal-orders -- OUT_DIR   (default OUT_DIR: books/algorithms/data/anim)
// Writes <OUT_DIR>/traversal-orders.frames.json: the engine's breadth-first tree edges in discovery order
// (traversal::list_bfs_edges), its distances (traversal::frontier::compute_bfs_levels) and its depth-first events
// (traversal::list_dfs_events), for two starting people.
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::order::{build_rows, Direction, NeighborOrder};
use knappnet::traversal::frontier::{compute_bfs_levels, Direction as Push};
use knappnet::traversal::{list_bfs_edges, list_dfs_events};
use knappnet::DegreeMode;

fn main() -> Result<(), knappnet::Error> {
    let out = std::env::args().nth(1).unwrap_or_else(|| "books/algorithms/data/anim".into());
    std::fs::create_dir_all(&out).unwrap();
    let g = kite();
    let rows = build_rows(&g, Direction::Both, NeighborOrder::Sorted, true, true);
    let mut runs = Vec::new();
    for &start in &[0u32, 9u32] {
        let bfs = list_bfs_edges(&rows, start, usize::MAX)?;
        let (dist, _) = compute_bfs_levels(&g, start, DegreeMode::All, Push::Auto)?;
        let dfs = list_dfs_events(&rows, Some(&[start]), usize::MAX)?;
        let bfs_txt: Vec<String> = bfs.iter().map(|(a, b)| format!("[{a},{b}]")).collect();
        let dfs_txt: Vec<String> = dfs.iter().map(|(a, b, k)| format!("[{a},{b},{}]", *k as i32)).collect();
        runs.push(format!(
            "{{\"start\":{start},\"bfs_edges\":[{}],\"distances\":{},\"dfs_events\":[{}]}}",
            bfs_txt.join(","), ints(&dist), dfs_txt.join(",")));
    }
    let names: Vec<String> = NAMES.iter().map(|n| format!("\"{n}\"")).collect();
    let edges: Vec<String> = EDGES.iter().map(|(a, b)| format!("[{a},{b}]")).collect();
    let text = format!(
        "{{\"v\":1,\"id\":\"traversal-orders\",\"engine\":\"traversal::list_bfs_edges, traversal::frontier::compute_bfs_levels (DegreeMode::All, Direction::Auto), traversal::list_dfs_events; rows from order::build_rows (Both, sorted, no loops, deduplicated)\",\"names\":[{}],\"edges\":[{}],\"runs\":[{}]}}\n",
        names.join(","), edges.join(","), runs.join(","));
    std::fs::write(format!("{out}/traversal-orders.frames.json"), text).unwrap();
    println!("wrote traversal-orders.frames.json to {out}");
    Ok(())
}

// Raw engine results for the search-from-both-ends animation and the A* figure (chapter 6 of the algorithms book): a grid
// of streets, searched from one corner of town to the other.
//   cargo run --release --bin bidirectional-meet -- OUT_DIR   (default OUT_DIR: books/algorithms/data/anim)
// Writes <OUT_DIR>/bidirectional-meet.frames.json. The grids are the example's own data; the engine supplies the shortest
// route found by bidirectional search (paths::bidirectional::find_bidirectional_path), the one-sided breadth-first
// search with a target (paths::search::Searcher, its settling order), and the A* route with a Manhattan-distance
// heuristic (paths::astar::find_astar_path) on a grid with a wall.
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::paths::astar::find_astar_path;
use knappnet::paths::bidirectional::find_bidirectional_path;
use knappnet::paths::search::{SearchOptions, Searcher};
use knappnet::paths::{PathGraph, PathGraphOptions};
use knappnet::Graph;

fn grid(w: usize, h: usize, wall: &dyn Fn(usize, usize, usize, usize) -> bool) -> (Graph, Vec<(i64, i64)>) {
    let mut e = Vec::new();
    for r in 0..h {
        for c in 0..w {
            let v = (r * w + c) as i64;
            if c + 1 < w && !wall(r, c, r, c + 1) {
                e.push((v, v + 1));
            }
            if r + 1 < h && !wall(r, c, r + 1, c) {
                e.push((v, v + w as i64));
            }
        }
    }
    let from: Vec<i64> = e.iter().map(|x| x.0).collect();
    let to: Vec<i64> = e.iter().map(|x| x.1).collect();
    (Graph::from_edges(w * h, &from, &to, None, false).unwrap(), e)
}

fn main() -> Result<(), knappnet::Error> {
    let out = std::env::args().nth(1).unwrap_or_else(|| "books/algorithms/data/anim".into());
    std::fs::create_dir_all(&out).unwrap();
    // 1. A plain 9 by 5 grid, from the middle of the left side to the middle of the right side.
    let (w, h) = (9usize, 5usize);
    let (g, edges) = grid(w, h, &|_, _, _, _| false);
    let pg = PathGraph::new(&g, PathGraphOptions::default())?;
    let (s, t) = ((2 * w) as u32, (2 * w + w - 1) as u32);
    let (len, path) = find_bidirectional_path(&pg, s, t)?.expect("connected");
    let mut one = Searcher::new(w * h);
    one.run(&pg, &[s], SearchOptions { target: Some(t), ..Default::default() })?;
    // 2. A 9 by 7 grid with a wall between columns 3 and 4 (rows 1 to 6 closed, the gap is in row 0).
    let (w2, h2) = (9usize, 7usize);
    let (g2, edges2) = grid(w2, h2, &|r, c, _, c2| c == 3 && c2 == 4 && r >= 1);
    let pg2 = PathGraph::new(&g2, PathGraphOptions::default())?;
    let (s2, t2) = ((5 * w2 + 1) as u32, (5 * w2 + 7) as u32);
    let heur: Vec<f64> = (0..w2 * h2)
        .map(|v| {
            let (r, c) = ((v / w2) as f64, (v % w2) as f64);
            let (tr, tc) = ((t2 as usize / w2) as f64, (t2 as usize % w2) as f64);
            (r - tr).abs() + (c - tc).abs()
        })
        .collect();
    let (alen, apath) = find_astar_path(&pg2, s2, t2, &heur, f64::INFINITY)?.expect("connected");
    let mut one2 = Searcher::new(w2 * h2);
    one2.run(&pg2, &[s2], SearchOptions { target: Some(t2), ..Default::default() })?;
    let text = format!(
        "{{\"v\":1,\"id\":\"bidirectional-meet\",\"engine\":\"paths::bidirectional::find_bidirectional_path, paths::search::Searcher (breadth-first, with a target), paths::astar::find_astar_path\",\"grid\":{{\"w\":{w},\"h\":{h},\"edges\":{},\"source\":{s},\"target\":{t},\"length\":{len:?},\"path\":{},\"one_sided_order\":{}}},\"wall\":{{\"w\":{w2},\"h\":{h2},\"edges\":{},\"source\":{s2},\"target\":{t2},\"astar_length\":{alen:?},\"astar_path\":{},\"one_sided_order\":{}}}}}\n",
        pairs(&edges), ints(&path), ints(one.order()), pairs(&edges2), ints(&apath), ints(one2.order()));
    std::fs::write(format!("{out}/bidirectional-meet.frames.json"), text).unwrap();
    println!("wrote bidirectional-meet.frames.json to {out}");
    Ok(())
}

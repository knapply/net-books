// Raw engine results for the shortest-path animations (chapter 6 of the algorithms book): Dijkstra's algorithm on the
// ten-person friendship network with travel times, from Ana.
//   cargo run --release --bin dijkstra-queue -- OUT_DIR   (default OUT_DIR: books/algorithms/data/anim)
// Writes <OUT_DIR>/dijkstra-queue.frames.json. Nothing is typed in except the travel times of the ten-person network (the
// example's own data). From the engine: Dijkstra's distances, parents and settling order (paths::search::Searcher),
// Bellman-Ford's distances on the same network (paths::negative::run_bellman_ford), and two tiny directed networks for the
// negative-weight figure: one with a negative arc (Bellman-Ford finds the paths) and one with a negative cycle (it reports it).
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::paths::negative::{run_bellman_ford, Outcome};
use knappnet::paths::search::{SearchOptions, Searcher};
use knappnet::paths::{ArcLengths, PathGraph, PathGraphOptions};
use knappnet::weights::WeightKind;
use knappnet::Graph;

/// Minutes between friends, in the order of `EDGES`.
const MINUTES: [f64; 18] = [4.0, 2.0, 9.0, 7.0, 3.0, 6.0, 10.0, 5.0, 8.0, 2.0, 4.0, 7.0, 3.0, 6.0, 5.0, 2.0, 4.0, 3.0];
const SOURCE: u32 = 0; // Ana

fn tree_json(pg: &PathGraph, source: u32) -> Result<String, knappnet::Error> {
    let mut s = Searcher::new(pg.node_count());
    s.run(pg, &[source], SearchOptions::default())?;
    let n = pg.node_count();
    let dist: Vec<f64> = (0..n).map(|v| s.dist(v)).collect();
    let parent: Vec<i64> = (0..n).map(|v| if s.parent(v) == u32::MAX { -1 } else { s.parent(v) as i64 }).collect();
    Ok(format!("{{\"dist\":{},\"parent\":{},\"order\":{}}}", floats(&dist), ints(&parent), ints(s.order())))
}

fn directed(n: usize, arcs: &[(i64, i64, f64)]) -> Result<PathGraph, knappnet::Error> {
    let from: Vec<i64> = arcs.iter().map(|a| a.0).collect();
    let to: Vec<i64> = arcs.iter().map(|a| a.1).collect();
    let w: Vec<f64> = arcs.iter().map(|a| a.2).collect();
    let g = Graph::from_edges(n, &from, &to, Some(&w), true)?;
    PathGraph::new(&g, PathGraphOptions { lengths: ArcLengths::Weights(WeightKind::Distance), ..Default::default() })
}

fn main() -> Result<(), knappnet::Error> {
    let out = std::env::args().nth(1).unwrap_or_else(|| "books/algorithms/data/anim".into());
    std::fs::create_dir_all(&out).unwrap();
    let from: Vec<i64> = EDGES.iter().map(|e| e.0).collect();
    let to: Vec<i64> = EDGES.iter().map(|e| e.1).collect();
    let g = Graph::from_edges(10, &from, &to, Some(&MINUTES), false)?;
    let pg = PathGraph::new(&g, PathGraphOptions { lengths: ArcLengths::Weights(WeightKind::Distance), ..Default::default() })?;
    let dijkstra = tree_json(&pg, SOURCE)?;
    let bf = match run_bellman_ford(&pg, &[SOURCE])? {
        Outcome::Tree(t) => format!("{{\"dist\":{},\"order\":{}}}", floats(&t.dist), ints(&t.order)),
        Outcome::NegativeCycle(c) => panic!("unexpected negative cycle {c:?}"),
    };
    // Negative weights. Nodes 0..4 are s, a, b, c, d. One negative arc: Dijkstra's rule would settle a too early.
    let neg_arcs = [(0, 1, 2.0), (0, 2, 5.0), (2, 1, -4.0), (1, 3, 3.0), (2, 3, 6.0), (3, 4, 1.0)];
    let neg = directed(5, &neg_arcs)?;
    let neg_bf = match run_bellman_ford(&neg, &[0])? {
        Outcome::Tree(t) => format!("{{\"dist\":{},\"parent\":{},\"order\":{}}}", floats(&t.dist),
            ints(&t.parent.iter().map(|&p| if p == u32::MAX { -1 } else { p as i64 }).collect::<Vec<_>>()), ints(&t.order)),
        Outcome::NegativeCycle(c) => panic!("unexpected negative cycle {c:?}"),
    };
    let mut ds = Searcher::new(5);
    let neg_dijkstra_error = match ds.run(&neg, &[0], SearchOptions::default()) {
        Ok(()) => "none".to_string(),
        Err(e) => format!("{e}"),
    };
    // A negative cycle: b to a is now -6, so going around a, c, b, a keeps getting cheaper.
    let cyc_arcs = [(0, 1, 2.0), (1, 3, 3.0), (3, 2, 2.0), (2, 1, -6.0), (3, 4, 1.0)];
    let cyc = directed(5, &cyc_arcs)?;
    let cyc_found = match run_bellman_ford(&cyc, &[0])? {
        Outcome::Tree(_) => "[]".to_string(),
        Outcome::NegativeCycle(c) => ints(&c),
    };
    let arcs_txt = |a: &[(i64, i64, f64)]| format!("[{}]", a.iter().map(|x| format!("[{},{},{:?}]", x.0, x.1, x.2)).collect::<Vec<_>>().join(","));
    let names: Vec<String> = NAMES.iter().map(|n| format!("\"{n}\"")).collect();
    let text = format!(
        "{{\"v\":1,\"id\":\"dijkstra-queue\",\"engine\":\"paths::search::Searcher (Dijkstra), paths::negative::run_bellman_ford\",\"names\":[{}],\"edges\":{},\"minutes\":{},\"source\":{SOURCE},\"dijkstra\":{dijkstra},\"bellman_ford\":{bf},\"negative\":{{\"arcs\":{},\"bellman_ford\":{neg_bf},\"dijkstra_error\":{:?}}},\"cycle\":{{\"arcs\":{},\"found\":{cyc_found}}}}}\n",
        names.join(","), pairs(&EDGES), floats(&MINUTES), arcs_txt(&neg_arcs), neg_dijkstra_error, arcs_txt(&cyc_arcs));
    std::fs::write(format!("{out}/dijkstra-queue.frames.json"), text).unwrap();
    println!("wrote dijkstra-queue.frames.json to {out}");
    Ok(())
}

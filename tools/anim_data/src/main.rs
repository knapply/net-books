// Raw engine results for the book's animations.
//   cargo run --release -- OUT_DIR      (default OUT_DIR: books/sna/data/anim)
// One file per animation: <id>.frames.json. tools/make_anim.py turns them into the player data.
// Every number is returned by a knappnet function; nothing here is typed in by hand except the ten-person network
// (the book's friendship network, the same edge list as tools/make_figures.py KITE_EDGES).
use knappnet::metrics::eigenvector::{compute_eigenvector_centrality, EigenvectorOptions};
use knappnet::metrics::nx_power::compute_katz;
use knappnet::traversal::frontier::{compute_bfs_levels, Direction};
use knappnet::{DegreeMode, Graph};

const NAMES: [&str; 10] = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jo"];
const EDGES: [(i64, i64); 18] = [
    (0, 1), (0, 2), (0, 3), (0, 5), (1, 3), (1, 4), (1, 6), (2, 3), (2, 5), (3, 4),
    (3, 5), (3, 6), (4, 6), (5, 6), (5, 7), (6, 7), (7, 8), (8, 9),
];
/// Rounds of the passing game shown (round 0 is the start, everyone at 1).
const ROUNDS: usize = 8;

fn floats(v: &[f64]) -> String {
    let s: Vec<String> = v.iter().map(|x| format!("{:?}", x)).collect();
    format!("[{}]", s.join(","))
}

fn header(id: &str) -> String {
    let names: Vec<String> = NAMES.iter().map(|n| format!("\"{n}\"")).collect();
    let edges: Vec<String> = EDGES.iter().map(|(a, b)| format!("[{a},{b}]")).collect();
    format!("\"id\":\"{id}\",\"names\":[{}],\"edges\":[{}]", names.join(","), edges.join(","))
}

fn main() -> Result<(), knappnet::Error> {
    let out = std::env::args().nth(1).unwrap_or_else(|| "books/sna/data/anim".into());
    std::fs::create_dir_all(&out).unwrap();
    let from: Vec<i64> = EDGES.iter().map(|e| e.0).collect();
    let to: Vec<i64> = EDGES.iter().map(|e| e.1).collect();
    let g = Graph::from_edges(10, &from, &to, None, false)?;
    let n = NAMES.len();

    // 1. Breadth-first search from Jo: the engine's BFS levels. The frames are "everyone within k steps".
    let jo = 9u32;
    let (dist, _steps) = compute_bfs_levels(&g, jo, DegreeMode::All, Direction::Auto)?;
    let dist_txt: Vec<String> = dist.iter().map(|d| d.to_string()).collect();
    let text = format!(
        "{{\"v\":1,{},\"engine\":\"traversal::frontier::compute_bfs_levels (DegreeMode::All, Direction::Auto)\",\"source\":{jo},\"distances\":[{}]}}\n",
        header("bfs-expansion"), dist_txt.join(","));
    std::fs::write(format!("{out}/bfs-expansion.frames.json"), text).unwrap();

    // 2. Eigenvector centrality as a passing game: one more round per call, same graph, start from the last round.
    // The engine's NetworkX-compatible Katz iteration with alpha = 1, beta = 0 and no scaling is exactly
    // x <- A x; a tolerance too large to ever fail makes each call stop after one step (max_iter = 1).
    let mut x = vec![1.0f64; n];
    let mut rounds = vec![x.clone()];
    for _ in 0..ROUNDS {
        x = compute_katz(&g, false, false, 1.0, &[0.0], Some(&x), 1, 1e30, false, 1)?
            .expect("one step always 'converges' with this tolerance");
        rounds.push(x.clone());
    }
    // Where it settles: the engine's eigenvector centrality (largest score 1).
    let eig = compute_eigenvector_centrality(&g, EigenvectorOptions::default())?;
    let rows: Vec<String> = rounds.iter().map(|r| floats(r)).collect();
    let text = format!(
        "{{\"v\":1,{},\"engine\":\"metrics::nx_power::compute_katz (alpha 1, beta 0, unscaled, max_iter 1, started from the previous round); settled: metrics::eigenvector::compute_eigenvector_centrality (scale Max)\",\"rounds\":[{}],\"settled\":{}}}\n",
        header("eigen-converge"), rows.join(","), floats(&eig.values));
    std::fs::write(format!("{out}/eigen-converge.frames.json"), text).unwrap();
    println!("wrote 2 files to {out}");
    Ok(())
}

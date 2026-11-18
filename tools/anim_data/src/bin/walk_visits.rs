// Raw engine results for the random-walk animation (chapter 6): one walker on the ten-person friendship network, one
// fixed seed, rerun with a growing number of steps. The walk is one stream consumed in step order, so a run of k steps is
// the first k steps of any longer run. For each frame we keep the visit counts after k steps and after k - 1, so the
// walker's place at step k is the node whose count went up.
//   cargo run --release --bin walk_visits -- OUT_DIR      (default OUT_DIR: books/sna/data/anim)
use knappnet::exec::Exec;
use knappnet::metrics::walks::{sample_walk_visits, WalkOptions, WalkSampleOptions, WalkTables};
use knappnet::Graph;

const NAMES: [&str; 10] = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jo"];
const EDGES: [(i64, i64); 18] = [
    (0, 1), (0, 2), (0, 3), (0, 5), (1, 3), (1, 4), (1, 6), (2, 3), (2, 5), (3, 4),
    (3, 5), (3, 6), (4, 6), (5, 6), (5, 7), (6, 7), (7, 8), (8, 9),
];
const SEED: u64 = 7;
const START: usize = 9; // Jo
const STEPS: [usize; 20] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30, 50, 80, 120, 300, 1000];

fn ints(v: &[u64]) -> String {
    format!("[{}]", v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","))
}

fn main() -> Result<(), knappnet::Error> {
    let out = std::env::args().nth(1).unwrap_or_else(|| "books/sna/data/anim".into());
    std::fs::create_dir_all(&out).unwrap();
    let from: Vec<i64> = EDGES.iter().map(|e| e.0).collect();
    let to: Vec<i64> = EDGES.iter().map(|e| e.1).collect();
    let g = Graph::from_edges(10, &from, &to, None, false)?;
    let tables = WalkTables::new(&g, WalkOptions { seed: SEED, ..Default::default() })?;
    let run = |steps: usize| -> Result<Vec<u64>, knappnet::Error> {
        let o = WalkSampleOptions { start: START, steps, burn_in: 0, restart: 0.0, size: 0, seed: SEED };
        Ok(sample_walk_visits(&g, &tables, &o, &Exec::default())?.visits)
    };
    let mut frames = Vec::new();
    for &k in &STEPS {
        let now = run(k)?;
        let before = if k == 0 { vec![0; 10] } else { run(k - 1)? };
        frames.push(format!("{{\"steps\":{k},\"visits\":{},\"before\":{}}}", ints(&now), ints(&before)));
    }
    let names: Vec<String> = NAMES.iter().map(|n| format!("\"{n}\"")).collect();
    let edges: Vec<String> = EDGES.iter().map(|(a, b)| format!("[{a},{b}]")).collect();
    let text = format!(
        "{{\"v\":1,\"id\":\"walk-visits\",\"engine\":\"metrics::walks::sample_walk_visits (restart 0, burn_in 0, seed {SEED}, steps = k)\",\"names\":[{}],\"edges\":[{}],\"start\":{START},\"frames\":[{}]}}\n",
        names.join(","), edges.join(","), frames.join(","));
    std::fs::write(format!("{out}/walk-visits.frames.json"), text).unwrap();
    println!("wrote walk-visits.frames.json to {out}");
    Ok(())
}

// Degree-preserving swap chain on the Florentine marriages (chapter 19).
//   cargo run --release --bin swap-chain -- OUT_DIR      (default OUT_DIR: books/sna/data/anim)
// Writes <OUT_DIR>/swap-chain.frames.json. Every step is an honest repeated call of the engine's double edge swap
// with the same graph and seed and a growing number of accepted swaps; the degrees of each step come from
// compute_degree on that step's network. Nothing is typed in; the marriages are read from data/florentine/edges.csv.
use knappnet::metrics::rewiring::run_double_edge_swap;
use knappnet::{compute_degree, DegreeMode, Graph};

const SEED: u64 = 1;
const STEPS: [u64; 17] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30, 40, 60];

fn main() -> Result<(), knappnet::Error> {
    let out = std::env::args().nth(1).unwrap_or_else(|| "books/sna/data/anim".into());
    std::fs::create_dir_all(&out).unwrap();
    let text = std::fs::read_to_string(format!("{out}/../florentine/edges.csv")).expect("florentine edges");
    let rows: Vec<(&str, &str)> = text.lines().skip(1).map(|l| l.split_once(',').unwrap()).collect();
    let mut names: Vec<&str> = Vec::new();
    for &(a, b) in &rows {
        for f in [a, b] {
            if !names.contains(&f) {
                names.push(f);
            }
        }
    }
    let at = |f: &str| names.iter().position(|n| *n == f).unwrap() as i64;
    let from: Vec<i64> = rows.iter().map(|r| at(r.0)).collect();
    let to: Vec<i64> = rows.iter().map(|r| at(r.1)).collect();
    let g = Graph::from_edges(names.len(), &from, &to, None, false)?;

    let pairs = |v: &[(u32, u32)]| {
        let mut s: Vec<String> = v.iter().map(|&(a, b)| format!("[{},{}]", a.min(b), a.max(b))).collect();
        s.sort();
        s.join(",")
    };
    let mut steps = Vec::new();
    for &k in &STEPS {
        let edges = run_double_edge_swap(&g, k, 1_000_000, SEED)?;
        let from2: Vec<i64> = edges.iter().map(|e| e.0 as i64).collect();
        let to2: Vec<i64> = edges.iter().map(|e| e.1 as i64).collect();
        let g2 = Graph::from_edges(names.len(), &from2, &to2, None, false)?;
        let deg: Vec<String> = compute_degree(&g2, DegreeMode::All, true).iter().map(|d| format!("{}", *d as u64)).collect();
        steps.push(format!("{{\"swaps\":{k},\"edges\":[{}],\"degrees\":[{}]}}", pairs(&edges), deg.join(",")));
    }
    let nm: Vec<String> = names.iter().map(|n| format!("\"{n}\"")).collect();
    let orig: Vec<(u32, u32)> = from.iter().zip(&to).map(|(&a, &b)| (a as u32, b as u32)).collect();
    let text = format!(
        "{{\"v\":1,\"id\":\"swap-chain\",\"names\":[{}],\"edges\":[{}],\"engine\":\"metrics::rewiring::run_double_edge_swap(graph, k, 1000000, seed {SEED}), one call per k; degrees: compute_degree on each result\",\"seed\":{SEED},\"steps\":[{}]}}\n",
        nm.join(","), pairs(&orig), steps.join(","));
    std::fs::write(format!("{out}/swap-chain.frames.json"), text).unwrap();
    println!("wrote swap-chain.frames.json ({} steps)", STEPS.len());
    Ok(())
}

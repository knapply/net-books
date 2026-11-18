// Raw engine results for the force-layout animation (chapter 5): the karate club, the engine's Fruchterman and
// Reingold layout rerun with a growing number of iterations from one seed.
//   cargo run --release --bin force_settle -- OUT_DIR      (default OUT_DIR: books/sna/data/anim)
// Each frame is a complete run with `iterations` iterations (the cooling schedule depends on the budget, so a frame is
// not a prefix of the next). Writes <id>.frames.json for force-settle.
use knappnet::layout::{layout_fruchterman_reingold, FrOptions};
use knappnet::Graph;

const SEED: u64 = 1;
const STEPS: [usize; 13] = [1, 2, 3, 4, 6, 8, 12, 16, 24, 40, 70, 120, 500];

fn floats(v: &[f64]) -> String {
    let s: Vec<String> = v.iter().map(|x| format!("{:?}", x)).collect();
    format!("[{}]", s.join(","))
}

fn main() -> Result<(), knappnet::Error> {
    let out = std::env::args().nth(1).unwrap_or_else(|| "books/sna/data/anim".into());
    std::fs::create_dir_all(&out).unwrap();
    let text = std::fs::read_to_string(format!("{out}/../karate/edges.csv")).unwrap();
    let rows: Vec<Vec<i64>> = text.lines().skip(1).map(|l| l.split(',').take(2).map(|x| x.parse().unwrap()).collect()).collect();
    let from: Vec<i64> = rows.iter().map(|r| r[0] - 1).collect();
    let to: Vec<i64> = rows.iter().map(|r| r[1] - 1).collect();
    let g = Graph::from_edges(34, &from, &to, None, false)?;
    let mut frames = Vec::new();
    for &k in &STEPS {
        let l = layout_fruchterman_reingold(&g, &FrOptions { seed: SEED, iterations: k, ..Default::default() })?;
        frames.push(format!("{{\"iterations\":{k},\"x\":{},\"y\":{}}}", floats(&l.x), floats(&l.y)));
    }
    let edges: Vec<String> = from.iter().zip(&to).map(|(a, b)| format!("[{a},{b}]")).collect();
    let text = format!(
        "{{\"v\":1,\"id\":\"force-settle\",\"engine\":\"layout::layout_fruchterman_reingold (FrOptions seed {SEED}, iterations = k)\",\"n\":34,\"edges\":[{}],\"frames\":[{}]}}\n",
        edges.join(","), frames.join(","));
    std::fs::write(format!("{out}/force-settle.frames.json"), text).unwrap();
    println!("wrote force-settle.frames.json to {out}");
    Ok(())
}

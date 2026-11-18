// Raw engine results for the stress-layout animation (chapter 5): the karate club, the engine's stress majorization
// rerun with a growing iteration cap from one seed.
//   cargo run --release --bin stress_settle -- OUT_DIR      (default OUT_DIR: books/sna/data/anim)
use knappnet::layout::{layout_stress_majorization, StressOptions};
use knappnet::Graph;

const SEED: u64 = 1;
const STEPS: [usize; 13] = [1, 2, 3, 4, 5, 6, 8, 10, 14, 20, 30, 60, 500];

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
        let l = layout_stress_majorization(&g, &StressOptions { seed: SEED, max_iter: k, ..Default::default() })?;
        frames.push(format!("{{\"max_iter\":{k},\"x\":{},\"y\":{}}}", floats(&l.x), floats(&l.y)));
    }
    let edges: Vec<String> = from.iter().zip(&to).map(|(a, b)| format!("[{a},{b}]")).collect();
    let text = format!(
        "{{\"v\":1,\"id\":\"stress-settle\",\"engine\":\"layout::layout_stress_majorization (StressOptions seed {SEED}, max_iter = k)\",\"n\":34,\"edges\":[{}],\"frames\":[{}]}}\n",
        edges.join(","), frames.join(","));
    std::fs::write(format!("{out}/stress-settle.frames.json"), text).unwrap();
    println!("wrote stress-settle.frames.json to {out}");
    Ok(())
}

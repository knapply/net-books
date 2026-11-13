// Writes books/sna/data/layouts/karate_layouts.csv and fr_seeds.csv.
// Run from books/sna (so data/karate/edges.csv is found) as the main.rs of a small crate that
// depends on the engine: knappnet = { path = "<knappnet>/crates/engine" }. See data/layouts/README.md.
use knappnet::layout::{layout_circle, layout_fruchterman_reingold, layout_stress_majorization, FrOptions, StressOptions};
use knappnet::linalg::symmetric_eigen;
use knappnet::matrix::Dense;
use knappnet::metrics::descriptive::{compute_distances, PathOptions};
use knappnet::metrics::scaling::compute_classical_mds;
use knappnet::Graph;

fn main() -> Result<(), knappnet::Error> {
    let text = std::fs::read_to_string("data/karate/edges.csv").unwrap();
    let rows: Vec<Vec<i64>> = text.lines().skip(1).map(|l| l.split(',').map(|x| x.parse().unwrap()).collect()).collect();
    let from: Vec<i64> = rows.iter().map(|r| r[0] - 1).collect();
    let to: Vec<i64> = rows.iter().map(|r| r[1] - 1).collect();
    let g = Graph::from_edges(34, &from, &to, None, false)?;
    let d = compute_distances(&g, None, PathOptions::default())?;
    let mut out = String::from("layout,node,x,y\n");
    let mut put = |name: &str, x: &[f64], y: &[f64]| {
        for i in 0..34 { out.push_str(&format!("{name},{},{:.6},{:.6}\n", i + 1, x[i], y[i])); }
    };
    // random: shared generator
    let mut state: u64 = 1;
    let mut u = Vec::new();
    for _ in 0..68 { state = state * 48271 % 2147483647; u.push(state as f64 / 2147483647.0); }
    let rx: Vec<f64> = (0..34).map(|i| u[2 * i]).collect();
    let ry: Vec<f64> = (0..34).map(|i| u[2 * i + 1]).collect();
    put("random", &rx, &ry);
    let c = layout_circle(&g);
    put("circle", &c.x, &c.y);
    let f = layout_fruchterman_reingold(&g, &FrOptions { seed: 1, ..Default::default() })?;
    put("force", &f.x, &f.y);
    let s = layout_stress_majorization(&g, &StressOptions { seed: 1, ..Default::default() })?;
    put("stress", &s.x, &s.y);
    // spectral
    let mut lap = vec![0.0; 34 * 34];
    for (a, b) in from.iter().zip(&to) {
        let (a, b) = (*a as usize, *b as usize);
        lap[a * 34 + b] -= 1.0; lap[b * 34 + a] -= 1.0; lap[a * 34 + a] += 1.0; lap[b * 34 + b] += 1.0;
    }
    let (_, vecs) = symmetric_eigen(&Dense::from_row_major(34, 34, lap)?)?;
    let sx: Vec<f64> = (0..34).map(|i| vecs.get(i, 1)).collect();
    let sy: Vec<f64> = (0..34).map(|i| vecs.get(i, 2)).collect();
    put("spectral", &sx, &sy);
    let mds = compute_classical_mds(&d, 2)?;
    let mx: Vec<f64> = (0..34).map(|i| mds.points.get(i, 0)).collect();
    let my: Vec<f64> = (0..34).map(|i| mds.points.get(i, 1)).collect();
    put("mds", &mx, &my);
    std::fs::write("karate_layouts.csv", &out).unwrap();
    // seeds
    let mut seeds = String::from("seed,x,y\n");
    for seed in 1..=20u64 {
        let f = layout_fruchterman_reingold(&g, &FrOptions { seed, ..Default::default() })?;
        for i in 0..34 { seeds.push_str(&format!("{seed},{:.6},{:.6}\n", f.x[i], f.y[i])); }
    }
    std::fs::write("fr_seeds.csv", &seeds).unwrap();
    Ok(())
}

// A period of the actor-oriented model on the ten-person office, one change opportunity at a time (chapter 23).
//   cargo run --release --bin saom-steps -- OUT_DIR      (default OUT_DIR: books/sna/data/anim)
// Writes <OUT_DIR>/saom-steps.frames.json. simulate_period has no step budget: it runs the opportunities that fit in
// one period, a number set by the rate. The engine draws the same sequence of opportunities for a given seed whatever
// the rate (the rate only rescales the clock), so a growing rate with one seed gives a growing prefix of one run. We sweep
// the rate finely and keep, for each number of opportunities the engine reports (`ministeps`), the network it returns.
use knappnet::ergm::ToggleGraph;
use knappnet::saom::{simulate_period, Effect, SaomModel, SaomOptions};
use knappnet::Graph;

fn main() -> Result<(), knappnet::Error> {
    let out = std::env::args().nth(1).unwrap_or_else(|| "books/sna/data/anim".into());
    std::fs::create_dir_all(&out).unwrap();
    // The ten-person office from chapter 23: who asks whom for advice. Positions 0 to 9 are Ada to Jay.
    let names = ["Ada", "Ben", "Cy", "Dee", "Eve", "Flo", "Gus", "Hal", "Ivy", "Jay"];
    let asks = [0, 1, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9];
    let is_asked = [1, 0, 0, 1, 0, 1, 0, 1, 2, 2, 3, 4, 4];
    let office = Graph::from_edges(10, &asks, &is_asked, None, true)?;
    let start = ToggleGraph::from_graph(&office)?;
    let model = SaomModel::new(vec![Effect::Outdegree, Effect::Reciprocity], vec![], 10)?;
    let beta = [-2.0, 1.5];
    let seed = 1u64;

    let ties = |g: &ToggleGraph| -> String {
        let mut v: Vec<(usize, usize)> = (0..g.edge_count()).map(|i| g.edge(i)).collect();
        v.sort();
        v.iter().map(|(a, b)| format!("[{a},{b}]")).collect::<Vec<_>>().join(",")
    };
    let mut rows: Vec<String> = Vec::new();
    let mut seen_max: i64 = -1;
    for j in 0..=1500u32 {
        let rate = j as f64 * 0.002;
        let sim = simulate_period(&model, &beta, &start, &SaomOptions { rate, runs: 1, seed, threads: 1 })?;
        let steps = sim.ministeps[0] as i64;
        if steps > seen_max {
            seen_max = steps;
            // stats: outdegree (ties), reciprocity (counted from both ends), ties that differ from the start
            rows.push(format!(
                "{{\"ministeps\":{steps},\"rate\":{rate:.3},\"ties\":{},\"reciprocity\":{},\"changed\":{},\"edges\":[{}]}}",
                sim.stats[0], sim.stats[1], sim.stats[2], ties(&sim.networks[0])));
        }
    }
    let nm: Vec<String> = names.iter().map(|n| format!("\"{n}\"")).collect();
    let text = format!(
        "{{\"v\":1,\"id\":\"saom-steps\",\"names\":[{}],\"edges\":[{}],\"engine\":\"saom::simulate_period (outdegree -2, reciprocity 1.5, seed {seed}, runs 1), rate swept from 0 to 3 in steps of 0.002; one row per new number of opportunities\",\"seed\":{seed},\"start\":{{\"ties\":{},\"reciprocity\":{}}},\"steps\":[{}]}}\n",
        nm.join(","), ties(&start), model.compute_statistics(&start)?[0], model.compute_statistics(&start)?[1], rows.join(","));
    std::fs::write(format!("{out}/saom-steps.frames.json"), text).unwrap();
    println!("wrote saom-steps.frames.json ({} rows, up to {} opportunities)", rows.len(), seen_max);
    Ok(())
}

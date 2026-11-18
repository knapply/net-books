// Louvain and Leiden, level by level, on Zachary's karate club (chapter 10).
//   cargo run --release --bin community-levels -- OUT_DIR MT_STATE.json     (from the net-books root)
// The engine's NetworkX-compatible ports (metrics::louvain_nx::find_louvain_communities and metrics::leiden_nx::
// find_leiden_communities) return the partition after every level. They draw from a Python-style Mersenne Twister, so
// MT_STATE.json is `random.Random(1).getstate()[1]` (625 integers), dumped with Python in the same job.
// Every level's modularity is scored with metrics::community::compute_modularity.
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::metrics::community::compute_modularity;
use knappnet::metrics::leiden_nx::{find_leiden_communities, LeidenMetric, LeidenOptions};
use knappnet::metrics::louvain_nx::{find_louvain_communities, LouvainOptions, NxWeighted};
use knappnet::metrics::pyrandom::PyRandom;

fn levels_json(g: &knappnet::Graph, levels: &[Vec<Vec<u32>>]) -> String {
    let rows: Vec<String> = levels.iter().map(|lv| {
        let mut label = vec![0i64; 34];
        for (c, members) in lv.iter().enumerate() {
            for &m in members {
                label[m as usize] = c as i64;
            }
        }
        let q = compute_modularity(g, &label, 1.0, false).expect("modularity");
        format!("{{\"membership\":{},\"modularity\":{:?}}}", ints(&label), q)
    }).collect();
    format!("[{}]", rows.join(","))
}

fn main() -> Result<(), knappnet::Error> {
    let out = out_dir();
    let state_path = std::env::args().nth(2).expect("second argument: MT_STATE.json");
    let text = std::fs::read_to_string(state_path).unwrap();
    let words: Vec<i64> = text.split(|c: char| !(c.is_ascii_digit() || c == '-')).filter(|s| !s.is_empty())
        .map(|s| s.parse().unwrap()).collect();
    let rng0 = PyRandom::from_state(&words).expect("625 integers");
    let (g, ties) = karate();
    let mut nx = NxWeighted::new(34, false);
    for &(a, b) in &ties {
        nx.add_edge(a as u32, b as u32, 1.0);
    }
    let hashes: Vec<i64> = (0..34).collect();

    let mut rng = rng0.clone();
    let lv = find_louvain_communities(&nx, &hashes, &mut rng,
        &LouvainOptions { resolution: 1.0, threshold: 1e-7, max_level: None, new_style: true, compensated: true });
    let lou = format!(
        "{{\"v\":1,\"id\":\"louvain-levels\",\"n\":34,\"edges\":{},\"engine\":\"metrics::louvain_nx::find_louvain_communities (resolution 1, threshold 1e-7, Python-style generator seeded with 1); modularity: metrics::community::compute_modularity\",\"levels\":{}}}\n",
        pairs(&ties), levels_json(&g, &lv));
    std::fs::write(format!("{out}/louvain-levels.frames.json"), lou).unwrap();

    let mut rng = rng0.clone();
    let lv = find_leiden_communities(&nx, &hashes, &mut rng,
        &LeidenOptions { metric: LeidenMetric::Modularity, resolution: 1.0, theta: 0.01, max_level: None, compensated: true })
        .expect("leiden");
    let lei = format!(
        "{{\"v\":1,\"id\":\"leiden-levels\",\"n\":34,\"edges\":{},\"engine\":\"metrics::leiden_nx::find_leiden_communities (modularity, resolution 1, theta 0.01, Python-style generator seeded with 1); modularity: metrics::community::compute_modularity\",\"levels\":{}}}\n",
        pairs(&ties), levels_json(&g, &lv));
    std::fs::write(format!("{out}/leiden-levels.frames.json"), lei).unwrap();
    println!("wrote louvain-levels and leiden-levels to {out}");
    Ok(())
}

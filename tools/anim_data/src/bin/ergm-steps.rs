// One chain of ERGM simulation, one accepted tie change at a time, on the karate club (chapter 21).
//   cargo run --release --bin ergm-steps -- OUT_DIR      (default OUT_DIR: books/sna/data/anim)
// Writes <OUT_DIR>/ergm-steps.frames.json. The model is the chapter's (edges, same side, shared partners 0.5), fitted
// the way the chapter fits it; a triangle count rides along with coefficient 0. The engine's Chain steps one
// Metropolis-Hastings proposal at a time and says whether it was accepted, so the trace is the engine's own: we start
// at the observed club, take steps until TOGGLES proposals have been accepted, and after each accepted one record
// the changed pair and the running statistics (Chain::statistics).
use knappnet::ergm::{fit_mcmle, Chain, McmleOptions, Model, Term, ToggleGraph};
use knappnet::Graph;

const TOGGLES: usize = 24;
const SEED: u64 = 1;

fn main() -> Result<(), knappnet::Error> {
    let out = std::env::args().nth(1).unwrap_or_else(|| "books/sna/data/anim".into());
    std::fs::create_dir_all(&out).unwrap();
    let from = [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3,
        4, 4, 5, 5, 5, 6, 8, 8, 8, 9, 13, 14, 14, 15, 15, 18, 18, 19, 20, 20, 22, 22, 23, 23, 23, 23, 23, 24, 24,
        24, 25, 26, 26, 27, 28, 28, 29, 29, 30, 30, 31, 31, 32,
    ];
    let to = [
        1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 17, 19, 21, 31, 2, 3, 7, 13, 17, 19, 21, 30, 3, 7, 8, 9, 13, 27, 28,
        32, 7, 12, 13, 6, 10, 6, 10, 16, 16, 30, 32, 33, 33, 33, 32, 33, 32, 33, 32, 33, 33, 32, 33, 32, 33, 25, 27,
        29, 32, 33, 25, 27, 31, 31, 29, 33, 33, 31, 33, 32, 33, 32, 33, 32, 33, 33,
    ];
    let side: [f64; 34] = [
        0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 1., 0., 0., 1., 0., 1., 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,
    ];
    let club = Graph::from_edges(34, &from, &to, None, false)?;
    let observed = ToggleGraph::from_graph(&club)?;

    // The chapter's fit.
    let fitted = Model::new(vec![Term::Edges, Term::NodeMatch(0), Term::Gwesp(0.5)], vec![side.to_vec()], 34, false)?;
    let fit = fit_mcmle(&fitted, &observed, &McmleOptions::default())?;
    // The same model plus a triangle count that is counted but not used (coefficient 0).
    let monitor = Model::new(
        vec![Term::Edges, Term::NodeMatch(0), Term::Gwesp(0.5), Term::Triangle],
        vec![side.to_vec()], 34, false)?;
    let theta = [fit.coef[0], fit.coef[1], fit.coef[2], 0.0];

    let edges_of = |g: &ToggleGraph| -> Vec<(usize, usize)> {
        let mut v: Vec<(usize, usize)> = (0..g.edge_count()).map(|i| { let (a, b) = g.edge(i); (a.min(b), a.max(b)) }).collect();
        v.sort();
        v
    };
    let stat = |s: &[f64]| format!("[{},{},{:?},{}]", s[0], s[1], s[2], s[3]);
    let mut chain = Chain::new(&monitor, &theta, &observed, SEED, 0)?;
    let mut before = edges_of(chain.graph());
    let mut rows = vec![format!("{{\"proposals\":0,\"toggle\":null,\"stats\":{}}}", stat(chain.statistics()))];
    let mut proposals = 0u64;
    while rows.len() <= TOGGLES {
        proposals += 1;
        if chain.step() {
            let after = edges_of(chain.graph());
            let added: Vec<_> = after.iter().filter(|e| !before.contains(e)).collect();
            let removed: Vec<_> = before.iter().filter(|e| !after.contains(e)).collect();
            assert_eq!(added.len() + removed.len(), 1, "one accepted step changes exactly one pair");
            let (kind, e) = if let Some(e) = added.first() { ("added", **e) } else { ("removed", *removed[0]) };
            rows.push(format!("{{\"proposals\":{proposals},\"toggle\":[{},{},\"{kind}\"],\"stats\":{}}}", e.0, e.1, stat(chain.statistics())));
            before = after;
        }
        assert!(proposals < 100_000, "chain never accepted enough proposals");
    }
    let text = format!(
        "{{\"v\":1,\"id\":\"ergm-steps\",\"engine\":\"ergm::Chain (step, graph, statistics), started at the observed club, seed {SEED}; coefficients from ergm::fit_mcmle with default options\",\"theta\":[{:?},{:?},{:?}],\"stat_names\":[\"edges\",\"same side\",\"shared partners\",\"triangles\"],\"edges\":[{}],\"side\":[{}],\"steps\":[{}]}}\n",
        fit.coef[0], fit.coef[1], fit.coef[2],
        edges_of(&observed).iter().map(|e| format!("[{},{}]", e.0, e.1)).collect::<Vec<_>>().join(","),
        side.iter().map(|s| format!("{}", *s as u8)).collect::<Vec<_>>().join(","),
        rows.join(","));
    std::fs::write(format!("{out}/ergm-steps.frames.json"), text).unwrap();
    println!("wrote ergm-steps.frames.json ({} accepted changes in {} proposals)", TOGGLES, proposals);
    Ok(())
}

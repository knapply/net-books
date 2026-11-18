// Raw engine results for the projection animation (chapter 14): the southern women, projected onto the women with
// only the first k events kept, k = 1 to 14.
//   cargo run --release --bin projection_forms -- OUT_DIR      (default OUT_DIR: books/sna/data/anim)
use knappnet::metrics::bipartite::{project, ProjectionOptions, ProjectionWeight};
use knappnet::Graph;

fn main() -> Result<(), knappnet::Error> {
    let out = std::env::args().nth(1).unwrap_or_else(|| "books/sna/data/anim".into());
    std::fs::create_dir_all(&out).unwrap();
    let text = std::fs::read_to_string(format!("{out}/../southern_women/edges.csv")).unwrap();
    let mut women: Vec<String> = Vec::new();
    let mut pairs: Vec<(usize, usize)> = Vec::new(); // (woman index, event 0-based)
    for line in text.lines().skip(1) {
        let (w, e) = line.split_once(',').unwrap();
        let wi = match women.iter().position(|x| x == w) {
            Some(i) => i,
            None => { women.push(w.to_string()); women.len() - 1 }
        };
        pairs.push((wi, e.trim_start_matches('E').parse::<usize>().unwrap() - 1));
    }
    assert_eq!(women.len(), 18);
    let is_event: Vec<bool> = (0..32).map(|i| i >= 18).collect();
    let mut frames = Vec::new();
    for k in 1..=14usize {
        let kept: Vec<&(usize, usize)> = pairs.iter().filter(|p| p.1 < k).collect();
        let from: Vec<i64> = kept.iter().map(|p| p.0 as i64).collect();
        let to: Vec<i64> = kept.iter().map(|p| (18 + p.1) as i64).collect();
        let g = Graph::from_edges(32, &from, &to, None, false)?;
        let pr = project(&g, &is_event, ProjectionOptions { second: false, weight: ProjectionWeight::Count, ..Default::default() })?;
        let list = |v: &[u32]| v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",");
        let w: Vec<String> = pr.weights.iter().map(|x| format!("{:?}", x)).collect();
        frames.push(format!("{{\"events\":{k},\"from\":[{}],\"to\":[{}],\"weights\":[{}]}}", list(&pr.from), list(&pr.to), w.join(",")));
    }
    let att: Vec<String> = pairs.iter().map(|p| format!("[{},{}]", p.0, p.1)).collect();
    let names: Vec<String> = women.iter().map(|w| format!("\"{w}\"")).collect();
    let text = format!(
        "{{\"v\":1,\"id\":\"projection-forms\",\"engine\":\"metrics::bipartite::project (second = false, Count weights) on the attendance with only events 1..k kept\",\"women\":[{}],\"attend\":[{}],\"frames\":[{}]}}\n",
        names.join(","), att.join(","), frames.join(","));
    std::fs::write(format!("{out}/projection-forms.frames.json"), text).unwrap();
    println!("wrote projection-forms.frames.json to {out}");
    Ok(())
}

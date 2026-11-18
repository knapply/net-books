// Raw engine results for the temporal-network animation (chapter 17): the chapter's six contacts. For every time step t:
// the contacts active at t (find_contacts_at), and earliest arrival from Ana and from Dev when only contacts up to
// time t may be used (find_temporal_paths with the window ending at t).
//   cargo run --release --bin temporal_reach -- OUT_DIR      (default OUT_DIR: books/sna/data/anim)
use knappnet::temporal::{count_temporal_reach, find_contacts_at, find_temporal_paths, Criterion, Direction, PathOptions, TemporalNetwork};

fn num(x: f64) -> String {
    if x.is_finite() { format!("{:?}", x) } else { "null".into() }
}

fn main() -> Result<(), knappnet::Error> {
    let out = std::env::args().nth(1).unwrap_or_else(|| "books/sna/data/anim".into());
    std::fs::create_dir_all(&out).unwrap();
    let names = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay"];
    let person_a = [0i64, 2, 1, 3, 0, 4];
    let person_b = [1i64, 3, 2, 4, 1, 5];
    let when = [1.0f64, 2.0, 3.0, 4.0, 5.0, 6.0];
    let net = TemporalNetwork::new(6, &person_a, &person_b, &when, None, false)?;
    let roots = [0usize, 3];
    let mut frames = Vec::new();
    for t in 1..=6 {
        let tf = t as f64;
        let active = find_contacts_at(&net, tf)?;
        let opts = PathOptions { end: Some(tf), ..PathOptions::default() };
        let arr = find_temporal_paths(&net, Criterion::EarliestArrival, Direction::Out, &roots, &opts)?;
        let act: Vec<String> = active.iter().map(|x| x.to_string()).collect();
        let a: Vec<String> = arr.iter().map(|x| num(*x)).collect();
        frames.push(format!("{{\"t\":{t},\"active\":[{}],\"arrival\":[{}]}}", act.join(","), a.join(",")));
    }
    let reach = count_temporal_reach(&net, Direction::Out, &PathOptions::default())?;
    let r: Vec<String> = reach.iter().map(|x| num(*x)).collect();
    let q = |v: &[&str]| v.iter().map(|s| format!("\"{s}\"")).collect::<Vec<_>>().join(",");
    let ints = |v: &[i64]| v.iter().map(|s| s.to_string()).collect::<Vec<_>>().join(",");
    let text = format!(
        "{{\"v\":1,\"id\":\"temporal-reach\",\"engine\":\"temporal::find_contacts_at; temporal::find_temporal_paths (EarliestArrival, Out, window ending at t); temporal::count_temporal_reach\",\"names\":[{}],\"a\":[{}],\"b\":[{}],\"when\":[1,2,3,4,5,6],\"roots\":[0,3],\"reach_full\":[{}],\"frames\":[{}]}}\n",
        q(&names), ints(&person_a), ints(&person_b), r.join(","), frames.join(","));
    std::fs::write(format!("{out}/temporal-reach.frames.json"), text).unwrap();
    println!("wrote temporal-reach.frames.json to {out}");
    Ok(())
}

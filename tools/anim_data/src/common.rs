// Shared by the programs in src/bin (each includes this file with #[path]).
// Nothing here is a result: the ten-person friendship network (the book's usual edge list, the same as
// tools/make_figures.py KITE_EDGES) and small printing helpers.
#![allow(dead_code)]
use knappnet::Graph;

pub const NAMES: [&str; 10] = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jo"];
pub const EDGES: [(i64, i64); 18] = [
    (0, 1), (0, 2), (0, 3), (0, 5), (1, 3), (1, 4), (1, 6), (2, 3), (2, 5), (3, 4),
    (3, 5), (3, 6), (4, 6), (5, 6), (5, 7), (6, 7), (7, 8), (8, 9),
];

pub fn out_dir() -> String {
    let out = std::env::args().nth(1).unwrap_or_else(|| "books/sna/data/anim".into());
    std::fs::create_dir_all(&out).unwrap();
    out
}

pub fn kite() -> Graph {
    let from: Vec<i64> = EDGES.iter().map(|e| e.0).collect();
    let to: Vec<i64> = EDGES.iter().map(|e| e.1).collect();
    Graph::from_edges(10, &from, &to, None, false).expect("kite")
}

pub fn floats(v: &[f64]) -> String {
    let s: Vec<String> = v.iter().map(|x| format!("{:?}", x)).collect();
    format!("[{}]", s.join(","))
}

pub fn ints<T: std::fmt::Display>(v: &[T]) -> String {
    let s: Vec<String> = v.iter().map(|x| x.to_string()).collect();
    format!("[{}]", s.join(","))
}

pub fn pairs(v: &[(i64, i64)]) -> String {
    let s: Vec<String> = v.iter().map(|(a, b)| format!("[{a},{b}]")).collect();
    format!("[{}]", s.join(","))
}

pub fn kite_header(id: &str) -> String {
    let names: Vec<String> = NAMES.iter().map(|n| format!("\"{n}\"")).collect();
    format!("\"id\":\"{id}\",\"names\":[{}],\"edges\":{}", names.join(","), pairs(&EDGES))
}

/// Zachary's karate club from the book's data file (columns source, target, 1-based); returns 0-based ties.
pub fn karate_ties() -> Vec<(i64, i64)> {
    let text = std::fs::read_to_string("books/sna/data/karate/edges.csv").expect("run from the net-books root");
    text.lines().skip(1).filter(|l| !l.trim().is_empty()).map(|l| {
        let mut f = l.split(',');
        let a: i64 = f.next().unwrap().trim().parse().unwrap();
        let b: i64 = f.next().unwrap().trim().parse().unwrap();
        (a - 1, b - 1)
    }).collect()
}

pub fn karate() -> (Graph, Vec<(i64, i64)>) {
    let ties = karate_ties();
    let from: Vec<i64> = ties.iter().map(|e| e.0).collect();
    let to: Vec<i64> = ties.iter().map(|e| e.1).collect();
    (Graph::from_edges(34, &from, &to, None, false).expect("karate"), ties)
}

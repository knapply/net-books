// Five people stored as compressed sparse rows (algorithms book, chapter 1).
//   cargo run --release --bin csr-build -- OUT_DIR
// The engine's own rows (offsets, targets), degrees and bit rows are the results; tools/anim_scenes/csr_build.py
// replays "count the ties, add up the counts, fill the slots" and asserts it ends on exactly these arrays.
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::bitset::BitMatrix;
use knappnet::Graph;

const FIVE: [&str; 5] = ["Ana", "Ben", "Cleo", "Dev", "Eli"];
const TIES: [(i64, i64); 5] = [(0, 1), (1, 2), (1, 3), (2, 3), (3, 4)];

fn main() -> Result<(), knappnet::Error> {
    let out = out_dir();
    let from: Vec<i64> = TIES.iter().map(|e| e.0).collect();
    let to: Vec<i64> = TIES.iter().map(|e| e.1).collect();
    let g = Graph::from_edges(5, &from, &to, None, false)?;
    let csr = g.out();
    let mut offsets: Vec<usize> = (0..5).map(|i| csr.arc_range(i).start).collect();
    offsets.push(csr.arc_count());
    let mut targets: Vec<u32> = Vec::new();
    let mut degrees: Vec<usize> = Vec::new();
    for i in 0..5 {
        targets.extend_from_slice(csr.neighbors(i));
        degrees.push(csr.degree(i));
    }
    let mut bits = BitMatrix::new(5);
    for i in 0..5 {
        for &j in csr.neighbors(i) {
            bits.set(i, j as usize);
        }
    }
    let rows: Vec<u64> = (0..5).map(|i| bits.row(i)[0]).collect();
    let names: Vec<String> = FIVE.iter().map(|n| format!("\"{n}\"")).collect();
    let text = format!(
        "{{\"v\":1,\"id\":\"csr-build\",\"names\":[{}],\"edges\":{},\"engine\":\"Graph::out (Csr::arc_range, neighbors, degree, arc_count) and bitset::BitMatrix\",\"offsets\":{},\"targets\":{},\"degrees\":{},\"bit_rows\":{}}}\n",
        names.join(","), pairs(&TIES), ints(&offsets), ints(&targets), ints(&degrees), ints(&rows));
    std::fs::write(format!("{out}/csr-build.frames.json"), text).unwrap();
    println!("wrote csr-build to {out}");
    Ok(())
}

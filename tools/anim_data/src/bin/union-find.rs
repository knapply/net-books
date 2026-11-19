// The ten-person friendship network joined tie by tie with the engine's union-find (algorithms book, chapter 3).
//   cargo run --release --bin union-find -- OUT_DIR
// One engine call per tie: union(a, b) returns (kept, absorbed) or None when the two were already together; the
// representative of every person is read from a copy (reading from the real one would compress paths and change
// what the next union sees). tools/anim_scenes/union_find.py replays the same rule and asserts every step.
#[path = "../common.rs"]
mod common;
use common::*;
use knappnet::union_find::UnionFind;

fn main() {
    let out = out_dir();
    let mut uf = UnionFind::new(10);
    let mut steps: Vec<String> = Vec::new();
    for &(a, b) in EDGES.iter() {
        let res = uf.union(a as usize, b as usize);
        let mut copy = uf.clone();
        let roots = copy.find_roots();
        let r = match res {
            Some((k, x)) => format!("[{k},{x}]"),
            None => "null".to_string(),
        };
        steps.push(format!("{{\"tie\":[{a},{b}],\"merged\":{r},\"roots\":{}}}", ints(&roots)));
    }
    let text = format!(
        "{{\"v\":1,{},\"engine\":\"union_find::UnionFind (new, union, find_roots on a copy)\",\"steps\":[{}]}}\n",
        kite_header("union-find"), steps.join(","));
    std::fs::write(format!("{out}/union-find.frames.json"), text).unwrap();
    println!("wrote union-find to {out}");
}

// The latent-space map of the karate club settling while it is fitted (chapter 22).
//   cargo run --release --bin latent-settle -- OUT_DIR      (default OUT_DIR: books/sna/data/anim)
// Writes <OUT_DIR>/latent-settle.frames.json. The fit is deterministic, so asking for max_iter = k ascent steps gives
// exactly the k-th iterate of the full fit: one honest call per k, same graph and options as the chapter.
use knappnet::latent_space::{fit, LatentOptions};
use knappnet::Graph;

const ITERS: [usize; 14] = [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 100, 200, 400, 5000];

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
    let side: [u32; 34] = [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    ];
    let club = Graph::from_edges(34, &from, &to, None, false)?;
    let fl = |v: &[f64]| v.iter().map(|x| format!("{:?}", x)).collect::<Vec<_>>().join(",");
    let mut rows = Vec::new();
    for &k in &ITERS {
        let m = fit(&club, &LatentOptions { dim: 2, max_iter: k, ..Default::default() })?;
        rows.push(format!(
            "{{\"max_iter\":{k},\"iterations\":{},\"converged\":{},\"alpha\":{:?},\"loglik\":{:?},\"positions\":[{}]}}",
            m.iterations, m.converged, m.alpha, m.loglik_exact, fl(&m.positions)));
    }
    let text = format!(
        "{{\"v\":1,\"id\":\"latent-settle\",\"engine\":\"latent_space::fit, dim 2, default options except max_iter = k (one call per k); loglik is the exact log-likelihood\",\"edges\":[{}],\"side\":[{}],\"steps\":[{}]}}\n",
        from.iter().zip(&to).map(|(a, b)| format!("[{a},{b}]")).collect::<Vec<_>>().join(","),
        side.iter().map(|s| s.to_string()).collect::<Vec<_>>().join(","),
        rows.join(","));
    std::fs::write(format!("{out}/latent-settle.frames.json"), text).unwrap();
    println!("wrote latent-settle.frames.json");
    Ok(())
}

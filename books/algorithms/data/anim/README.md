# Raw engine results for the algorithms book animations

`<id>.frames.json` is what the knappnet engine returned for one animation. `tools/make_anim.py` turns it into the player
data and the still picture in `books/algorithms/figures/anim/`. The scenes live in `tools/anim_scenes/` and the engine
programs in `tools/anim_data/src/bin/`. Nothing here is typed in by hand except the two small networks (the five people and
the ten-person friendship network, the books' usual edge lists).

| file | engine call | what a step is |
| --- | --- | --- |
| csr-build.frames.json | `Graph::out` (`Csr::arc_range`, `neighbors`, `degree`, `arc_count`) and `bitset::BitMatrix` on the five people | the engine's own offsets, targets, degrees and bit rows. `tools/anim_scenes/csr_build.py` replays the three passes (count, add up, fill) and asserts it ends on exactly these arrays |
| union-find.frames.json | `union_find::UnionFind` (`new`, `union`, `find_roots` on a copy) on the ten-person network, one call per tie in the book's order | one tie: what `union` returned (`[kept, absorbed]` or `null`) and every person's leader afterwards. `tools/anim_scenes/union_find.py` replays the rule (smaller root kept, path halving) and asserts every step against the engine |
| heap-calls.frames.json | `traversal::frontier::compute_bfs_levels` from Jo (index 9) | the distance of every person, used as the heap keys. The engine has no public heap, so `tools/anim_scenes/heap_calls.py` builds one by the textbook rule and asserts that taking the smallest ten times gives the sorted engine distances |

## Regenerating

    cd tools/anim_data && cargo run --release --bin csr-build -- ../../books/algorithms/data/anim
    (and the same for union-find and heap-order, which writes heap-calls.frames.json)
    cd ../.. && python3 tools/make_anim.py

`tools/anim_data` depends on a knappnet checkout at `../../../knappnet` (edit the path in its `Cargo.toml` if yours is elsewhere).

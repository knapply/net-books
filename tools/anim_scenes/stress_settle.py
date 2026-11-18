"""Chapter 5: the stress layout settling (karate club), the companion of the force layout. See force_settle.py."""
from . import force_settle as F


def build_stress():
    def words(k, b, stress, last):
        s = f"{stress[k]:.3f}"
        if k == 0:
            return f"One sweep from the starting positions. Stress {s}."
        if k == last:
            return f"{b} sweeps, the most we tried. Stress {s}. Past the first ten or so, more sweeps barely help."
        if k < 4:
            return f"{b} sweeps. Every pair is nudged toward the page distance that matches the steps between them. Stress {s}."
        return f"{b} sweeps. Stress {s}, changing only in the third decimal now."
    scene, raw, stress = F.build_layout("stress-settle", "max_iter", words)
    assert abs(stress[-1] - 0.068) < 0.001, "the final stress layout should score what the chapter's table says"
    still = F.strip(scene, stress, ["1 sweep", "4 sweeps", "10 sweeps", "500 sweeps"], "A stress layout settling",
                    "Four copies of the karate club drawn by a stress layout after 1, 4, 10 and 500 sweeps.")
    return scene, still


BUILDERS = {"stress-settle": build_stress}

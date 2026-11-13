"""Figures for the chapter on exponential random graph models.

Standard library only. The weights drawn are computed here from the GWESP formula.
"""
import math

from fig_small_worlds import Axes
from figs import BLUE, GREEN, INK, MUTED, ORANGE, RED, Canvas

DECAYS = [(0.25, BLUE), (0.5, GREEN), (1.0, ORANGE), (2.0, RED)]


def weight(decay, k):
    """What a tie with k shared partners adds to GWESP at this decay."""
    return 0.0 if k == 0 else math.exp(decay) * (1 - (1 - math.exp(-decay)) ** k)


def gwesp_weights():
    c = Canvas(760, 380, "What a tie is worth as its shared partners pile up",
               "Lines for four decay settings of the weight a tie adds to the GWESP statistic, against its number of shared partners, with the raw count as a dashed line.")
    ax = Axes(c, 80, 50, 560, 270, (0, 10), (0, 8))
    ax.frame([0, 2, 4, 6, 8, 10], [0, 2, 4, 6, 8], "shared partners of the tie (k)", "weight added to GWESP")
    ax.line([(k, k) for k in range(0, 11)], MUTED, width=1.6, dash="6 4")
    c.text(ax.px(8.9), ax.py(8.0) + 14, "raw count", size=12, fill=MUTED)
    for decay, color in DECAYS:
        ax.line([(k, weight(decay, k)) for k in range(0, 11)], color)
        c.text(ax.px(10) + 10, ax.py(weight(decay, 10)) + 4, f"decay {decay:g}", size=12, anchor="start", fill=color)
    c.text(380, 28, "Each extra shared partner counts for less", size=14, weight="700")
    ten = {d: round(weight(d, 10), 2) for d, _ in DECAYS}
    limits = {d: round(math.exp(d), 2) for d, _ in DECAYS}
    meta = dict(chapter=21,
                caption="The weight a tie adds to the GWESP statistic as a function of its number of shared partners, for four decay settings. A tie with no shared partner adds 0 and with one adds exactly 1 whatever the decay. After that each further partner adds less, and the weight levels off at $e^{\\alpha}$. The dashed line is the raw count of shared partners.",
                alt=(f"A line chart with shared partners from 0 to 10 on the horizontal axis and the weight added to GWESP on the vertical axis. Every line starts at 0 for no shared partners and passes through 1 for one shared partner. At 10 shared partners the lines for decay 0.25, 0.5, 1 and 2 reach {ten[0.25]}, {ten[0.5]}, {ten[1.0]} and {ten[2.0]}, and they level off at {limits[0.25]}, {limits[0.5]}, {limits[1.0]} and {limits[2.0]}. A dashed straight line shows the raw count, which reaches the top of the chart at 8 shared partners."),
                data={"weights_at_10": ten, "limits": limits})
    return c, meta


FIGURES = {"gwesp-weights": gwesp_weights}

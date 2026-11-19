#!/usr/bin/env python3
"""Headless-browser test of shared/js/netanim.js (not published). Needs Playwright for Python and a Chromium.

Usage: python3 tools/test_anim.py [--shots DIR] [--browser /path/to/chromium]
Serves the repository over HTTP on a free port, opens a static harness page with a still figure for every
animation in books/sna/figures/anim, and checks the swap, the controls, reduced motion and print.
"""
import functools
import http.server
import shutil
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ANIM = [ROOT / "books" / b / "figures" / "anim" for b in ("sna", "algorithms")]
fails: list[str] = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def page_html(stills):
    figs = "\n".join(
        f'<figure><img src="/{s}" alt="Alt text for {s}" width="960" height="640"></figure>'
        for s in stills)
    return ('<!doctype html><meta charset="utf-8"><title>harness</title><link rel="icon" href="data:,"><body style="margin:0;padding:8px;max-width:900px">'
            f'{figs}<script src="/shared/js/netanim.js" defer></script></body>')


def main() -> int:
    shots = Path(sys.argv[sys.argv.index("--shots") + 1]) if "--shots" in sys.argv else None
    exe = sys.argv[sys.argv.index("--browser") + 1] if "--browser" in sys.argv else shutil.which("chromium") or shutil.which("google-chrome")
    stills = sorted(str(p.relative_to(ROOT)) for d in ANIM for p in d.glob("*-still.svg"))
    harness = ROOT / "tools" / "_anim_harness.html"
    harness.write_text(page_html(stills))
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(Quiet, directory=str(ROOT))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_port}/tools/_anim_harness.html"
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=exe, args=["--no-sandbox"])
            run(b, url, stills, shots)
            b.close()
    finally:
        srv.shutdown()
        harness.unlink(missing_ok=True)
    print(f"{len(fails)} failures")
    return 1 if fails else 0


def run(b, url, stills, shots):
    ctx = b.new_context(viewport={"width": 1000, "height": 700 * max(2, len(stills))})
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.goto(url)
    pg.wait_for_selector(".na", timeout=5000)
    check(pg.locator(".na").count() == len(stills), f"every still is swapped for a player ({len(stills)})")
    check(all(pg.locator("img.na-off").nth(i).evaluate("e => getComputedStyle(e).display") == "none" for i in range(len(stills))),
          "the still stays in the DOM but is hidden on screen")
    check(pg.locator("img").count() == len(stills), "the img elements are kept")
    box = pg.locator(".na").first
    cap = box.locator(".na-c")
    rg = box.locator("input[type=range]")
    play = box.get_by_role("button", name="Play").or_(box.get_by_role("button", name="Pause"))
    n = int(rg.get_attribute("max")) + 1
    check(n >= 5, f"slider covers {n} steps")
    # autoplay starts: the figure is visible
    pg.wait_for_timeout(300)
    check(play.inner_text() == "Pause", "autoplays when at least half visible (button reads Pause)")
    check(cap.get_attribute("aria-live") == "off", "caption is not live while autoplaying")
    first = cap.inner_text()
    pg.wait_for_timeout(2300)
    check(cap.inner_text() != first, "autoplay advances the caption")
    play.click()
    check(play.inner_text() == "Play" and cap.get_attribute("aria-live") == "polite", "Pause stops it and makes the caption live")
    v = rg.input_value()
    pg.wait_for_timeout(2000)
    check(rg.input_value() == v, "paused stays paused")
    box.get_by_role("button", name="Restart").click()
    check(rg.input_value() == "0" and box.locator(".na-r span").inner_text() == f"Step 1 of {n}", "Restart goes to step 1")
    box.get_by_role("button", name="Next").click()
    check(rg.input_value() == "1" and box.locator(".na-r span").inner_text() == f"Step 2 of {n}", "Next steps forward")
    c1 = cap.inner_text()
    box.get_by_role("button", name="Back").click()
    check(rg.input_value() == "0" and cap.inner_text() != c1, "Back steps back and the caption follows")
    rg.fill("3")
    check(rg.input_value() == "3" and "Step 4 of" in box.locator(".na-r span").inner_text(), "the slider jumps to a step")
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
        pg.wait_for_timeout(900)
        box.screenshot(path=str(shots / "frame-step4.png"))
    box.focus()
    pg.keyboard.press("ArrowRight")
    check(rg.input_value() == "4", "keyboard: Right steps forward")
    pg.keyboard.press("ArrowLeft")
    check(rg.input_value() == "3", "keyboard: Left steps back")
    pg.keyboard.press("Space")
    pg.wait_for_timeout(200)
    check(play.inner_text() == "Pause", "keyboard: Space toggles play")
    pg.keyboard.press("Space")
    check(play.inner_text() == "Play", "keyboard: Space toggles pause")
    # the tab being hidden pauses (simulated through the visibility API)
    pg.evaluate("Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'))")
    check(play.inner_text() == "Play", "hidden tab does not play")
    pg.evaluate("Object.defineProperty(document,'hidden',{value:false,configurable:true})")
    # the filled-in last step
    rg.fill(str(n - 1))
    if shots:
        pg.wait_for_timeout(900)
        box.screenshot(path=str(shots / "frame-last.png"))
    # print media
    pg.emulate_media(media="print")
    check(pg.locator("img.na-off").first.evaluate("e => getComputedStyle(e).display") != "none", "print: the still is shown")
    check(pg.locator(".na").first.evaluate("e => getComputedStyle(e).display") == "none", "print: the player is hidden")
    check(not errors, "no console errors" + (f": {errors}" if errors else ""))
    ctx.close()

    # reduced motion: no autoplay, instant changes
    ctx = b.new_context(viewport={"width": 1000, "height": 700 * max(2, len(stills))}, reduced_motion="reduce")
    pg = ctx.new_page()
    pg.goto(url)
    pg.wait_for_selector(".na", timeout=5000)
    box = pg.locator(".na").first
    pg.wait_for_timeout(2800)
    check(box.locator("input[type=range]").input_value() == "0", "reduced motion: no autoplay")
    check(box.get_by_role("button", name="Play").count() == 1, "reduced motion: the button offers Play")
    box.get_by_role("button", name="Next").click()
    check(box.locator("input[type=range]").input_value() == "1", "reduced motion: stepping works")
    check(box.evaluate("e => getComputedStyle(e.querySelector('circle')).transitionDuration") in ("0s", "0.0s"),
          "reduced motion: transitions are instant")
    ctx.close()

    # no JSON: the image stays
    ctx = b.new_context(viewport={"width": 1000, "height": 800})
    pg = ctx.new_page()
    pg.route("**/*.json", lambda r: r.fulfill(status=404, body="nope"))
    pg.goto(url)
    pg.wait_for_timeout(1000)
    check(pg.locator(".na").count() == 0 and pg.locator("img.na-off").count() == 0, "no JSON: the still stays as it is")
    ctx.close()


if __name__ == "__main__":
    raise SystemExit(main())

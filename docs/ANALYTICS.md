# Visit statistics

What is measured, and how to turn it on.

## Without any setup
GitHub reports stars, forks, watchers, issues and commit activity, and the README
badges read them directly.

## GitHub traffic (views, unique visitors, clones, referrers, popular pages)
GitHub keeps these for 14 days and shows them only to people with push access.
`.github/workflows/traffic.yml` copies them every day to the `stats` branch, so
history builds up, and writes the badge files the README reads.

One step needs you: create a fine-grained personal access token for this
repository with the "Administration: read" permission, and save it as a
repository secret named `TRAFFIC_TOKEN` (Settings, Secrets and variables, Actions).
Then run the `traffic` workflow once from the Actions tab.

## On the website
`books/sna/outline.toml` has an `[analytics]` table. Fill in the values for the
tools you have an account with and regenerate (`python3 tools/new_chapters.py
books/sna`); empty values add nothing. Supported: GoatCounter, Plausible and
Umami. All three count visits in aggregate without cookies: pages, referrers,
countries, devices and browsers. When any is on, the page footer says so.

## What is left out, on purpose
Fingerprinting, session recording and ad-network trackers. They identify
individual readers, they need consent banners in many places, and this book
spends a whole chapter asking researchers to protect the people in their data.
Aggregate counts answer the questions that matter: how many people read it,
which chapters, and where they came from.

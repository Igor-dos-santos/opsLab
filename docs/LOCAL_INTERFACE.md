# Local staffing explorer

## Setup

Download the repository ZIP from GitHub, extract it, and open a terminal in the
folder containing README.md. Python 3.10+ is required. No third-party packages,
accounts, database, API keys or paid services are needed.

```sh
python -m opslab.web
```

Open http://127.0.0.1:8000 in your browser. If `python` is unavailable, use `python3`
on macOS/Linux or `py` on Windows. For an occupied port use
`python -m opslab.web --port 8001`, then open http://127.0.0.1:8001.
Stop the process with Ctrl+C. Restarting resets the form defaults; there is no storage.

## First comparison

Leave cases at 100, workers at `2 3 4`, seed at `42`, arrival gap at 2 minutes,
and processing time at 5 minutes. Select **Compare staffing**.
Average waits displayed are 11.123, 0.951 and 0.202 minutes respectively.
Waiting means time before work begins, not processing duration.

Change seeds to `40 41 42` and compare again. Average trial means become
34.171, 7.775 and 1.138 minutes. The table reports lowest and highest trial means,
not the longest individual case wait and not confidence bounds.

Download summary CSV for one row per staffing choice or raw trials CSV for each
seed/staffing pair. Downloads rerun the same deterministic settings and retain
unrounded numbers. The page shows the settings used. Preserve them alongside CSV
when sharing results because the existing CSV schemas do not include all generator
parameters. Browser download location and duplicate filename handling depend on
browser settings. No files are written by the server.

## How it works

The browser submits a GET form to the local Python server. The server validates
inputs, calls the existing paired-trial engine and summary functions, then renders
HTML with a CSS bar chart. CSV endpoints use the existing serializers. Everything
finishes before response bytes are sent. There is no JavaScript or external asset.
All staffing choices receive the identical workload within each seed.

## Limits and privacy

The interface allows 1-10,000 cases, 1-20 unique seeds, 1-8 unique worker counts,
1-100 workers per count and durations between 0.001 and 10,000 minutes. A request
may simulate at most 100,000 case-runs. These conservative limits include heap size
and are not performance guarantees. CLI budgets remain unchanged.

The server binds only to 127.0.0.1 and checks Host, escapes reflected values and
sets content restrictions. It serves only fixed application routes, not filesystem
paths. It is a single-user local teaching server, not a hardened production service.
Do not expose it through a public proxy. Query parameters can appear in browser
history; use synthetic numeric settings only. No employer or customer data is used.
Errors preserve bounded known inputs and return no partial results or CSV.

The model omits shifts, breaks, skills, abandonment, AI, quality and costs. Results
are not real staffing recommendations. Developed with AI assistance.

## Verification and remaining work

`python -m unittest discover -s tests -v` includes engine-equivalence, malformed
inputs, work limits, output escaping, error atomicity, zero-wait charts, HTTP CSV
headers and Host rejection. Browser visual QA used a generated results page through
the managed preview, not the live Python form. Full browser interaction and a timed
five-minute walkthrough remain release tasks. No online demo or release exists yet.

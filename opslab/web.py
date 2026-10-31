"""Local-only, server-rendered staffing explorer. No external assets or data."""
import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
import math
from urllib.parse import parse_qs, urlencode, urlsplit

from .export import summary_results_to_csv, trial_results_to_csv
from .scenarios import run_paired_trials, summarize_mean_wait

DEFAULTS = dict(cases="100", seeds="42", workers="2 3 4", arrival="2", service="5")
MAX_CASE_RUNS = 100_000
STYLE = """
:root{color-scheme:light;font-family:system-ui,sans-serif;color:#162c3d;background:#f1f5f7}
*{box-sizing:border-box}body{margin:0}main{max-width:1100px;margin:auto;padding:40px 22px}
header{margin-bottom:30px}.eyebrow{color:#086c6b;font-weight:750;letter-spacing:.12em;font-size:.8rem}
h1{font-size:clamp(2rem,5vw,3.4rem);margin:10px 0}h2{margin-top:0;font-size:1.3rem}
p{line-height:1.6}.layout{display:grid;grid-template-columns:300px 1fr;gap:24px}
section,form{background:white;border:1px solid #d6e1e6;border-radius:16px;padding:24px}
label{display:block;font-weight:650;margin-top:16px}input{width:100%;padding:11px;border:1px solid #8ba4b3;border-radius:7px;font:inherit;margin:6px 0}
small,.muted{color:#4b6271}button,.button{display:inline-block;background:#086c6b;color:white;border:0;border-radius:8px;padding:12px 16px;font:inherit;text-decoration:none;cursor:pointer}
button{width:100%;margin-top:20px}a{color:#086c6b}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #d79512;outline-offset:3px}
.notice{background:#fff5de;border-left:4px solid #d79512;padding:12px 16px;border-radius:4px}
.error{background:#fff0ec;color:#8b2615;padding:16px;border-radius:8px}
.bar-row{margin:16px 0}.bar-label{display:flex;justify-content:space-between;gap:12px;margin-bottom:7px}.track{background:#eef3f5;height:18px;border-radius:5px;overflow:hidden}.bar{background:#168684;height:100%}
.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;margin:22px 0}th,td{text-align:right;padding:12px 9px;border-bottom:1px solid #d6e1e6}th:first-child,td:first-child{text-align:left}caption{text-align:left;font-weight:700;margin-bottom:8px}
.downloads{display:flex;flex-wrap:wrap;gap:16px}footer{margin-top:26px;font-size:.9rem}
@media(max-width:760px){.layout{grid-template-columns:1fr}main{padding:24px 14px}section,form{padding:20px}}
"""


def parse_inputs(query):
    """Bound all work before invoking the engine, including worker heap size."""
    if len(query) > 2048:
        raise ValueError("Input is too long. Use up to 20 seeds and 8 worker counts.")
    params = parse_qs(query, keep_blank_values=True, max_num_fields=8)
    if set(params) - set(DEFAULTS) or any(len(v) != 1 for v in params.values()):
        raise ValueError("Unknown or repeated input field.")
    fields = {key: params.get(key, [value])[0] for key, value in DEFAULTS.items()}
    try:
        cases = int(fields["cases"])
        seeds = [int(x) for x in fields["seeds"].replace(",", " ").split()]
        workers = [int(x) for x in fields["workers"].replace(",", " ").split()]
        arrival, service = float(fields["arrival"]), float(fields["service"])
    except ValueError:
        raise ValueError("Use whole numbers for cases, seeds and workers; numbers for durations.") from None
    if not 1 <= cases <= 10000:
        raise ValueError("Cases must be between 1 and 10000.")
    if not 1 <= len(seeds) <= 20 or len(set(seeds)) != len(seeds):
        raise ValueError("Use 1 to 20 distinct seeds.")
    if any(abs(seed) > 2**31 - 1 for seed in seeds):
        raise ValueError("Seeds must be between -2147483647 and 2147483647.")
    if not 1 <= len(workers) <= 8 or len(set(workers)) != len(workers):
        raise ValueError("Use 1 to 8 distinct worker counts.")
    if any(not 1 <= worker <= 100 for worker in workers):
        raise ValueError("Each worker count must be between 1 and 100.")
    if any(not math.isfinite(v) or not 0.001 <= v <= 10000 for v in (arrival, service)):
        raise ValueError("Both durations must be between 0.001 and 10000 minutes.")
    if cases * len(seeds) * len(workers) > MAX_CASE_RUNS:
        raise ValueError("This local interface allows at most 100000 case-runs (cases x seeds x worker counts).")
    return fields, dict(seeds=seeds, agent_counts=workers, case_count=cases,
                        mean_interarrival=arrival, mean_service=service)


def render_page(fields, summaries=None, error=None):
    controls = ""
    for key, label, hint in (
        ("cases", "Cases per workload", "1 to 10,000 fictional cases"),
        ("workers", "Worker counts to compare", "Separate with spaces, for example: 2 3 4"),
        ("seeds", "Workload seeds", "Repeatable workloads, for example: 40 41 42"),
        ("arrival", "Average arrival gap (minutes)", "A smaller gap means a busier queue"),
        ("service", "Average processing time (minutes)", "Time spent working on each case"),
    ):
        controls += (f'<label for="{key}">{label}</label><input id="{key}" name="{key}" '
                     f'value="{escape(fields[key], quote=True)}" required maxlength="220" '
                     f'aria-describedby="{key}-hint"><small id="{key}-hint">{hint}</small>')
    results = '<p>Choose your assumptions and select Compare staffing to see results.</p>'
    if error:
        results = f'<p class="error" role="alert">{escape(str(error))}</p><p>No partial results were returned. Adjust your inputs and try again.</p>'
    elif summaries:
        maximum = max(row.average_mean_wait_minutes for row in summaries)
        bars, table = "", ""
        for row in summaries:
            mean = row.average_mean_wait_minutes
            width = 0 if maximum == 0 else 100 * mean / maximum
            bars += (f'<div class="bar-row"><div class="bar-label"><span>{row.agents} workers</span>'
                     f'<strong>{mean:.3f} min</strong></div><div class="track" aria-hidden="true">'
                     f'<div class="bar" style="width:{width:.4f}%"></div></div></div>')
            table += (f'<tr><th scope="row">{row.agents}</th><td>{row.trials}</td><td>{mean:.3f}</td>'
                      f'<td>{row.minimum_mean_wait_minutes:.3f}</td><td>{row.maximum_mean_wait_minutes:.3f}</td></tr>')
        query = escape(urlencode(fields), quote=True)
        results = (f'<p class="muted">{escape(fields["cases"])} cases per workload. Seeds: {escape(fields["seeds"])}. '
                   f'Arrival gap: {escape(fields["arrival"])} min. Processing: {escape(fields["service"])} min.</p>'
                   '<h3>Average wait before work starts</h3><p>Lower means less waiting. All staffing choices receive the same cases within each seed.</p>'
                   f'{bars}<div class="table-wrap"><table><caption>Wait comparison, in minutes</caption>'
                   '<thead><tr><th scope="col">Workers</th><th scope="col">Trials</th><th scope="col">Average</th>'
                   '<th scope="col">Lowest trial</th><th scope="col">Highest trial</th></tr></thead>'
                   f'<tbody>{table}</tbody></table></div><p class="muted">The range describes observed trial means, not individual case waits or a confidence interval. Display rounded to 3 decimals; CSV retains precision.</p>'
                   f'<div class="downloads"><a href="/summary.csv?{query}">Download summary CSV</a>'
                   f'<a href="/trials.csv?{query}">Download raw trials CSV</a></div>')
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>OpsLab | Staffing explorer</title><style>{STYLE}</style></head><body><main><header>'
            '<div class="eyebrow">OPSLAB / SYNTHETIC STAFFING EXPLORER</div><h1>See what changes when your team grows.</h1>'
            '<p>Compare fictional workloads and explore how staffing affects waiting time.</p>'
            '<p class="notice">Learning simulation only. These results are not real-world staffing recommendations. No AI model, cost or quality calculation is included.</p></header>'
            f'<div class="layout"><form action="/compare" method="get"><h2>Set up a comparison</h2>{controls}'
            '<button type="submit">Compare staffing</button><p><a href="/">Reset to example</a></p></form>'
            f'<section aria-labelledby="results"><h2 id="results">Your comparison</h2>{results}</section></div>'
            '<footer>Runs on your computer. No uploads or external services. Workers are simulated people. '
            'Developed with AI assistance. Stop the server with Ctrl+C.</footer></main></body></html>')


def response_for(target):
    """Compute an entire response before sending headers or bytes."""
    path = urlsplit(target)
    if path.path not in ("/", "/compare", "/summary.csv", "/trials.csv"):
        return 404, "text/plain; charset=utf-8", "Not found", None
    if path.path == "/" and not path.query:
        return 200, "text/html; charset=utf-8", render_page(DEFAULTS), None
    try:
        fields, settings = parse_inputs(path.query)
        rows = run_paired_trials(**settings)
        summaries = summarize_mean_wait(rows)
        if path.path.endswith(".csv"):
            csv = summary_results_to_csv(summaries) if path.path == "/summary.csv" else trial_results_to_csv(rows)
            return 200, "text/csv; charset=utf-8", csv, path.path[1:]
        return 200, "text/html; charset=utf-8", render_page(fields, summaries), None
    except ValueError as error:
        # Preserve only known, bounded fields so mistakes can be corrected safely.
        fields = dict(DEFAULTS)
        if len(path.query) <= 2048:
            try:
                params = parse_qs(path.query, keep_blank_values=True, max_num_fields=8)
                fields.update({k: v[0][:220] for k, v in params.items() if k in fields})
            except ValueError:
                pass
        if path.path.endswith(".csv"):
            return 400, "text/plain; charset=utf-8", str(error), None
        return 400, "text/html; charset=utf-8", render_page(fields, error=error), None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        allowed_hosts = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        if self.headers.get("Host") not in allowed_hosts:
            self.send_error(403, "Use the local server address")
            return
        status, kind, content, filename = response_for(self.path)
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # Avoid logging query values.


def main():
    parser = argparse.ArgumentParser(description="Open the local OpsLab staffing explorer")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    try:
        with HTTPServer(("127.0.0.1", args.port), Handler) as server:
            server.timeout = 5
            print(f"Open http://127.0.0.1:{args.port} in your browser. Stop with Ctrl+C.", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    except OSError as error:
        parser.exit(1, f"Could not start local server: {error}\n")


if __name__ == "__main__":
    main()

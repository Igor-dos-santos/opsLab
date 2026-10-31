import csv
from http.client import HTTPConnection
from http.server import HTTPServer
from io import StringIO
import threading
import unittest
from unittest.mock import patch
from urllib.parse import urlencode

from opslab.export import summary_results_to_csv, trial_results_to_csv
from opslab.scenarios import run_paired_trials, summarize_mean_wait
from opslab.web import DEFAULTS, Handler, parse_inputs, render_page, response_for


class WebTests(unittest.TestCase):
    def test_initial_page_does_not_run_simulation(self):
        with patch('opslab.web.run_paired_trials') as engine:
            status, kind, body, filename = response_for('/')
        self.assertEqual(status, 200)
        self.assertIn('Compare staffing', body)
        self.assertIn('name="viewport"', body)
        engine.assert_not_called()

    def test_table_and_downloads_match_engine(self):
        fields = dict(DEFAULTS, seeds='40 41', workers='4 2', arrival='3', service='6')
        query = urlencode(fields)
        rows = run_paired_trials([40, 41], [4, 2], case_count=100, mean_interarrival=3, mean_service=6)
        summary = summarize_mean_wait(rows)
        body = response_for('/compare?' + query)[2]
        self.assertIn(f'{summary[0].average_mean_wait_minutes:.3f}', body)
        self.assertLess(body.index('4 workers'), body.index('2 workers'))
        self.assertEqual(response_for('/summary.csv?' + query)[2], summary_results_to_csv(summary))
        self.assertEqual(response_for('/trials.csv?' + query)[2], trial_results_to_csv(rows))
        self.assertEqual(len(list(csv.DictReader(StringIO(response_for('/trials.csv?' + query)[2])))), 4)

    def test_invalid_and_oversize_inputs_never_invoke_engine(self):
        invalid = [dict(cases='0'), dict(cases='10001'), dict(seeds='1 1'),
                   dict(workers='2 2'), dict(workers='10000000'), dict(arrival='nan'),
                   dict(service='inf'), dict(service='0'), dict(seeds=''),
                   dict(cases='10000', seeds='1 2 3 4', workers='2 3 4')]
        for values in invalid:
            with self.subTest(values=values), patch('opslab.web.run_paired_trials') as engine:
                result = response_for('/compare?' + urlencode(dict(DEFAULTS, **values)))
                self.assertEqual(result[0], 400)
                self.assertIn('No partial results', result[2])
                engine.assert_not_called()

    def test_query_shape_limits(self):
        for query in ['cases=1&cases=2', 'unknown=3', 'x=' + 'a' * 2049, '&'.join('x=1' for _ in range(9))]:
            with self.subTest(query=query[:40]), patch('opslab.web.run_paired_trials') as engine:
                self.assertEqual(response_for('/compare?' + query)[0], 400)
                engine.assert_not_called()

    def test_exact_budget_and_comma_lists(self):
        fields, settings = parse_inputs(urlencode(dict(DEFAULTS, cases='10000', seeds='1,2,3,4,5', workers='2,4')))
        self.assertEqual(settings['agent_counts'], [2, 4])
        self.assertEqual(settings['case_count'] * len(settings['seeds']) * 2, 100000)

    def test_error_reflection_is_escaped(self):
        attack = '"><script>alert(1)</script>'
        body = response_for('/compare?' + urlencode(dict(DEFAULTS, cases=attack)))[2]
        self.assertNotIn('<script>', body)
        self.assertIn('&lt;script&gt;', body)

    def test_late_failure_does_not_emit_csv(self):
        with patch('opslab.web.run_paired_trials', side_effect=ValueError('simulation failed')):
            status, kind, body, filename = response_for('/trials.csv?' + urlencode(DEFAULTS))
        self.assertEqual((status, filename), (400, None))
        self.assertEqual(body, 'simulation failed')
        self.assertNotIn('text/csv', kind)

    def test_zero_wait_chart_is_finite(self):
        rows = run_paired_trials([42], [2, 3], case_count=1)
        body = render_page(DEFAULTS, summarize_mean_wait(rows))
        self.assertIn('width:0.0000%', body)
        self.assertNotIn('width:nan', body)

    def test_unknown_path(self):
        self.assertEqual(response_for('/../../etc/passwd')[0], 404)

    def test_real_http_headers_csv_and_host_guard(self):
        with HTTPServer(('127.0.0.1', 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                connection = HTTPConnection('127.0.0.1', server.server_port, timeout=5)
                connection.request('GET', '/summary.csv?' + urlencode(DEFAULTS))
                reply = connection.getresponse()
                self.assertEqual(reply.status, 200)
                self.assertEqual(reply.getheader('Content-Disposition'), 'attachment; filename="summary.csv"')
                self.assertEqual(reply.getheader('X-Content-Type-Options'), 'nosniff')
                self.assertIn("frame-ancestors 'none'", reply.getheader('Content-Security-Policy'))
                self.assertIn(b'average_mean_wait_minutes', reply.read())
                connection.close()
                connection = HTTPConnection('127.0.0.1', server.server_port, timeout=5)
                connection.request('GET', '/', headers={'Host': 'untrusted.example'})
                reply = connection.getresponse()
                self.assertEqual(reply.status, 403)
                reply.read()
                connection.close()
            finally:
                server.shutdown()
                thread.join()

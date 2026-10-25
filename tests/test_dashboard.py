"""Dashboard backend: settings, statuses, quota display, job control and HTTP safety."""
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from solsync import dashboard
from solsync.config import ConfigError, load_config, manila_day, save_daily_limit
from solsync.ledger import Ledger
from solsync.models import Candidate

BASE_CONFIG = {
    "uploads_enabled": False,
    "repos": {
        "hackerrank": {"path": "../hr", "remote_url": "https://github.com/me/HR.git"},
        "exercism": {"path": "../ex", "remote_url": "https://github.com/me/EX.git",
                     "language_dirs": {"python": "Python"}},
    },
}


class ProjectTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tmp.name) / "proj"
        self.root.mkdir()
        self.config = self.root / "config.json"
        self.config.write_text(json.dumps(BASE_CONFIG))

    def tearDown(self):
        self.tmp.cleanup()

    def cfg(self):
        return load_config(root=self.root)


class SettingsTests(ProjectTestCase):
    def test_1_fresh_install_defaults_to_4(self):
        self.assertEqual(self.cfg().daily_limit, 4)

    def test_2_saved_limit_survives_restart_and_is_what_the_engine_reads(self):
        save_daily_limit(6, self.config)
        self.assertEqual(self.cfg().daily_limit, 6)       # a new process reads the file again
        self.assertEqual(json.loads(self.config.read_text())["daily_limit"], 6)
        save_daily_limit(1, self.config)
        self.assertEqual(self.cfg().daily_limit, 1)
        save_daily_limit(0, self.config)
        self.assertEqual(self.cfg().daily_limit, 0)

    def test_4_invalid_values_rejected_and_file_unchanged(self):
        save_daily_limit(4, self.config)
        before = self.config.read_text()
        for bad in (-1, 1.5, "3", True, None, 21, 10**9):
            with self.subTest(bad=bad), self.assertRaises(ConfigError):
                save_daily_limit(bad, self.config)
        self.assertEqual(self.config.read_text(), before)

    def test_max_is_configurable(self):
        self.config.write_text(json.dumps({**BASE_CONFIG, "max_daily_limit": 50}))
        self.assertEqual(save_daily_limit(30, self.config), 30)
        self.assertEqual(self.cfg().daily_limit, 30)

    def test_failed_save_keeps_previous_value(self):
        save_daily_limit(5, self.config)
        with mock.patch("solsync.config.os.replace", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                save_daily_limit(7, self.config)
        self.assertEqual(self.cfg().daily_limit, 5)


class StatusTests(unittest.TestCase):
    def test_11_unreachable_github_is_never_reported_missing(self):
        failed_check = {"repo_ok": False, "problems": ["cannot reach GitHub"]}
        for engine_status in ("eligible", "deferred_quota", "already_present", "needs_source"):
            self.assertEqual(dashboard.github_status(engine_status, False, failed_check), dashboard.UNVERIFIED)
            self.assertEqual(dashboard.github_status(engine_status, False, None), dashboard.UNVERIFIED)

    def test_status_mapping_with_successful_check(self):
        ok = {"repo_ok": True}
        self.assertEqual(dashboard.github_status("already_present", False, ok), dashboard.PUBLISHED)
        self.assertEqual(dashboard.github_status("uploaded_verified", False, ok), dashboard.PUBLISHED)
        self.assertEqual(dashboard.github_status("eligible", False, ok), dashboard.MISSING)
        self.assertEqual(dashboard.github_status("upload_failed", False, ok), dashboard.FAILED)
        self.assertEqual(dashboard.github_status("eligible", True, ok), dashboard.PENDING)

    def test_next_reset_is_manila_midnight(self):
        from datetime import datetime, timezone
        now = datetime(2026, 10, 25, 15, 59, tzinfo=timezone.utc)   # 23:59 Manila
        self.assertEqual(dashboard.next_reset(now), "2026-10-26T00:00:00+08:00")


class QuotaTests(ProjectTestCase):
    def test_9_concurrent_reservations_cannot_exceed_limit(self):
        db = self.root / "state" / "solsync.db"
        Ledger(db).close()
        results = []

        def worker(i):
            led = Ledger(db)
            results.append(led.reserve("2026-10-25", 4, "x", f"k{i}", [(f"p{i}", "h")]))
            led.close()

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(12)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(sum(r is not None for r in results), 4)
        led = Ledger(db)
        self.assertEqual(led.used_on("2026-10-25"), 4)
        led.close()

    def test_5_lowering_limit_keeps_uploads_and_blocks_more(self):
        led = Ledger(self.root / "state" / "solsync.db")
        day = manila_day()
        for i in range(3):
            b = led.reserve(day, 4, "hackerrank", f"k{i}", [(f"p{i}", "h")])
            led.set_batch(b, "verified", commit_sha="abc")
        self.assertIsNone(led.reserve(day, 1, "exercism", "k9", [("p9", "h")]))  # limit lowered to 1
        self.assertEqual(led.verified_on(day), 3)   # nothing undone
        led.close()


class JobTests(unittest.TestCase):
    def test_12_repeated_clicks_start_only_one_job(self):
        gate = threading.Event()
        calls = []

        def slow_run(*a, **k):
            calls.append(a)
            gate.wait(5)
            return mock.Mock(stdout="done", stderr="", returncode=0)

        jobs = dashboard.JobRunner(Path("."), python="python")
        with mock.patch.object(dashboard.subprocess, "run", side_effect=slow_run):
            self.assertTrue(jobs.start("sync")[0])
            self.assertFalse(jobs.start("sync")[0])
            self.assertFalse(jobs.start("scan")[0])
            gate.set()
            for _ in range(50):
                if jobs.job["state"] == "finished":
                    break
                threading.Event().wait(0.05)
        self.assertEqual(len(calls), 1)
        self.assertEqual(jobs.job["exit_code"], 0)

    def test_sync_job_runs_the_engine_command(self):
        self.assertEqual(dashboard.JobRunner.COMMANDS["sync"], ["run"])
        self.assertEqual(dashboard.JobRunner.COMMANDS["scan"], ["run", "--dry-run"])


class HttpTests(ProjectTestCase):
    def setUp(self):
        super().setUp()
        led = Ledger(self.root / "state" / "solsync.db")
        for i, status in enumerate(["already_present", "eligible", "upload_failed"]):
            led.save_item(Candidate(platform="hackerrank", item_id=f"c{i}:python", title=f"Challenge {i}",
                                    language="python3", url="", method="t", evidence="t",
                                    status=status, dest_paths=[f"Python/Challenge {i}/1.py"]))
        led.set_meta("check:hackerrank", json.dumps({"repo_ok": True, "time": "2026-10-25T10:00:00+08:00"}))
        b = led.reserve(manila_day(), 4, "hackerrank", "hackerrank:c0:python", [("Python/Challenge 0/1.py", "h")])
        led.set_batch(b, "verified", commit_sha="abc")
        led.close()
        self.jobs = dashboard.JobRunner(self.root)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), None)
        self.port = self.server.server_address[1]
        self.server.RequestHandlerClass = dashboard.make_handler(self.root, self.jobs, self.port)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.task = mock.patch.object(dashboard, "task_info", return_value={"configured": True, "state": "Ready"})
        self.task.start()

    def tearDown(self):
        self.task.stop()
        self.server.shutdown()
        self.server.server_close()
        super().tearDown()

    def call(self, path, body=None, headers=None):
        h = {"X-SolSync": "1", **({"Content-Type": "application/json"} if body is not None else {})}
        h.update(headers or {})
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", headers=h,
                                     data=None if body is None else json.dumps(body).encode())
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    def test_13_overview_shows_real_data(self):
        code, o = self.call("/api/overview")
        self.assertEqual(code, 200)
        self.assertEqual(o["total"], 3)
        self.assertEqual(o["counts"]["Published"], 1)
        self.assertEqual(o["counts"]["Missing"], 1)
        self.assertEqual(o["counts"]["Failed"], 1)
        self.assertEqual(o["quota"], {**o["quota"], "limit": 4, "uploaded_today": 1, "remaining": 3})
        code, rows = self.call("/api/solutions")
        published = next(r for r in rows if r["github_status"] == "Published")
        self.assertEqual(published["github_url"], "https://github.com/me/HR/blob/main/Python/Challenge%200/1.py")
        self.assertIsNone(next(r for r in rows if r["github_status"] == "Missing")["github_url"])

    def test_6_settings_saved_through_ui_are_what_the_engine_reads(self):
        code, r = self.call("/api/settings", {"daily_limit": 6})
        self.assertEqual((code, r["ok"]), (200, True))
        self.assertEqual(load_config(root=self.root).daily_limit, 6)
        code, o = self.call("/api/overview")
        self.assertEqual(o["quota"]["limit"], 6)
        events = self.call("/api/events")[1]
        self.assertIn("changed from 4 to 6", events[0]["message"])

    def test_invalid_and_high_values_through_ui(self):
        for bad in (-1, 2.5, "x"):
            code, r = self.call("/api/settings", {"daily_limit": bad})
            self.assertEqual(code, 400, bad)
            self.assertFalse(r["ok"])
        code, r = self.call("/api/settings", {"daily_limit": 12})
        self.assertEqual(code, 409)
        self.assertTrue(r["needs_confirm"])
        self.assertEqual(load_config(root=self.root).daily_limit, 4)   # not saved yet
        code, r = self.call("/api/settings", {"daily_limit": 12, "confirm": True})
        self.assertEqual(code, 200)
        self.assertEqual(load_config(root=self.root).daily_limit, 12)

    def test_requests_without_header_or_from_other_hosts_are_refused(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/overview")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req, timeout=10)
        self.assertEqual(ctx.exception.code, 403)
        code, _ = self.call("/api/overview", headers={"Host": f"evil.example:{self.port}"})
        self.assertEqual(code, 403)
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/settings", method="POST",
                                     data=b'{"daily_limit": 9}', headers={"X-SolSync": "1",
                                                                          "Content-Type": "text/plain"})
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req, timeout=10)
        self.assertEqual(ctx.exception.code, 403)
        self.assertEqual(load_config(root=self.root).daily_limit, 4)

    def test_duplicate_job_request_is_refused(self):
        with mock.patch.object(self.jobs, "_run", side_effect=lambda job: None):
            self.assertEqual(self.call("/api/jobs", {"kind": "scan"})[0], 202)
            code, r = self.call("/api/jobs", {"kind": "sync"})
        self.assertEqual(code, 409)
        self.assertIn("already running", r["message"])


if __name__ == "__main__":
    unittest.main()

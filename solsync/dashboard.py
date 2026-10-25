"""Local dashboard: a small web server on 127.0.0.1 plus one HTML page.

The dashboard never uploads or counts anything itself. Every action runs the same
`python -m solsync ...` command the scheduled task runs, so the daily limit, the run
lock and every Git safety check stay in one place (the engine).

    python -m solsync dashboard            # opens http://127.0.0.1:8765
"""
from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .config import (MANILA, PROJECT_ROOT, ConfigError, load_config, manila_day,
                     manila_now, save_daily_limit)
from .ledger import Ledger

TASK_NAME = "SolutionSync Daily"
HIGH_LIMIT_WARNING = 8   # saving more than this asks for confirmation first
PAGE = Path(__file__).with_name("dashboard.html")

PUBLISHED, MISSING, PENDING, FAILED, UNVERIFIED = (
    "Published", "Missing", "Pending", "Failed", "Unable to Verify")
FAILED_STATES = {"upload_failed", "retrieval_failed", "missing_source"}
PUBLISHED_STATES = {"already_present", "uploaded_verified"}


# ---------------------------------------------------------------- data
def github_status(item_status: str, pending: bool, check: dict | None) -> str:
    """Publication status for one solution. Never "Missing" without a successful remote check."""
    if pending:
        return PENDING
    if item_status in FAILED_STATES:
        return FAILED
    if not check or not check.get("repo_ok"):
        return UNVERIFIED  # GitHub unreachable, auth failed, or never checked
    return PUBLISHED if item_status in PUBLISHED_STATES else MISSING


def next_reset(now: datetime | None = None) -> str:
    now = (now or manila_now()).astimezone(MANILA)
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.isoformat(timespec="seconds")


def _pid_alive(pid: int) -> bool:
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)  # QUERY_LIMITED_INFORMATION
    if not handle:
        return False
    code = ctypes.c_ulong()
    ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
    ctypes.windll.kernel32.CloseHandle(handle)
    return code.value == 259  # STILL_ACTIVE


def current_run(state_dir: Path) -> dict | None:
    """The engine run in progress (scheduled or manual), if any."""
    try:
        info = json.loads((state_dir / "current_run.json").read_text())
    except (OSError, ValueError):
        return None
    return info if _pid_alive(int(info.get("pid", 0))) else None


_task_cache: dict = {"at": 0.0, "info": None}


def task_info() -> dict:
    """Windows Task Scheduler state of the daily task (cached for 15 s)."""
    if time.time() - _task_cache["at"] < 15 and _task_cache["info"]:
        return _task_cache["info"]
    ps = (f"$t = Get-ScheduledTask -TaskName '{TASK_NAME}' -ErrorAction SilentlyContinue; "
          "if (-not $t) { '{\"configured\": false}'; exit }; $i = $t | Get-ScheduledTaskInfo; "
          "[pscustomobject]@{configured=$true; state=[string]$t.State; "
          "next=$(if ($i.NextRunTime) { $i.NextRunTime.ToString('s') } else { $null }); "
          "last=$(if ($i.LastRunTime) { $i.LastRunTime.ToString('s') } else { $null }); "
          "result=$i.LastTaskResult} | ConvertTo-Json -Compress")
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True,
                             text=True, timeout=30, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        info = json.loads(out.stdout.strip() or '{"configured": false}')
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        info = {"configured": None, "error": f"could not read Task Scheduler: {exc}"}
    _task_cache.update(at=time.time(), info=info)
    return info


def set_automation(paused: bool) -> tuple[bool, str]:
    verb = "Disable" if paused else "Enable"
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          f"{verb}-ScheduledTask -TaskName '{TASK_NAME}' | Out-Null"],
                         capture_output=True, text=True, timeout=60,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    _task_cache["at"] = 0.0
    if out.returncode != 0:
        return False, (out.stderr.strip().splitlines() or ["Task Scheduler refused the change"])[-1]
    return True, "Automation paused" if paused else "Automation resumed"


def solutions(cfg, ledger: Ledger) -> list[dict]:
    pending = {b["item_key"] for p in cfg.repos for b in ledger.open_batches(p)}
    checks = {p: json.loads(ledger.get_meta(f"check:{p}", "null")) for p in cfg.repos}
    rows = []
    for r in ledger.db.execute("SELECT * FROM items ORDER BY platform, title"):
        repo = cfg.repos.get(r["platform"])
        if not repo:
            continue
        status = github_status(r["status"] or "", r["item_key"] in pending, checks.get(r["platform"]))
        dests = [d for d in (r["dest"] or "").split(";") if d]
        local = [repo.path / d for d in dests]
        remote = repo.remote_url.removesuffix(".git").rstrip("/")
        link = None
        if status == PUBLISHED and dests:
            kind = "tree" if local[0].is_dir() else "blob"
            link = f"{remote}/{kind}/{repo.branch}/{urllib.parse.quote(dests[0])}"
        rows.append({
            "key": r["item_key"], "platform": r["platform"], "title": r["title"],
            "language": r["language"], "github_status": status, "engine_status": r["status"],
            "local_status": ("Present" if local and all(p.exists() for p in local)
                             else "Not in local copy" if dests else "Unknown"),
            "local_paths": [str(p) for p in local], "remote_paths": dests,
            "repository": remote, "github_url": link, "last_checked": r["last_seen"],
            "note": r["note"] or "", "source_url": r["url"] or "", "evidence": r["evidence"] or "",
        })
    return rows


def overview(cfg, ledger: Ledger, rows: list[dict]) -> dict:
    today = manila_day()
    used = ledger.used_on(today)
    verified = ledger.verified_on(today)
    counts = {s: sum(r["github_status"] == s for r in rows)
              for s in (PUBLISHED, MISSING, PENDING, FAILED, UNVERIFIED)}
    task = task_info()
    run = current_run(cfg.state_dir)
    if run:
        state = "Running now"
    elif not task.get("configured"):
        state = "Not scheduled"
    elif task.get("state") == "Disabled":
        state = "Paused"
    else:
        state = "Enabled"
    return {
        "total": len(rows), "counts": counts,
        "quota": {"limit": cfg.daily_limit, "max": cfg.max_daily_limit,
                  "high_warning": HIGH_LIMIT_WARNING, "uploaded_today": verified,
                  "in_progress_today": used - verified, "used_today": used,
                  "remaining": max(0, cfg.daily_limit - used), "day": today,
                  "next_reset": next_reset()},
        "last_scan": ledger.get_meta("last_scan", ""),
        "last_upload": ledger.get_meta("last_success", ""),
        "automation": {"state": state, "task": task, "running": run,
                       "uploads_enabled": cfg.uploads_enabled},
        "checks": {p: json.loads(ledger.get_meta(f"check:{p}", "null")) for p in cfg.repos},
    }


# ---------------------------------------------------------------- jobs
class JobRunner:
    """Runs one engine command at a time; repeated clicks cannot start a second one."""

    COMMANDS = {"scan": ["run", "--dry-run"], "refresh": ["run", "--dry-run"], "sync": ["run"]}

    def __init__(self, root: Path = PROJECT_ROOT, python: str = sys.executable):
        self.root, self.python = root, python
        self.lock = threading.Lock()
        self.job: dict | None = None

    def start(self, kind: str) -> tuple[bool, str]:
        if kind not in self.COMMANDS:
            return False, f"unknown job '{kind}'"
        with self.lock:
            if self.job and self.job["state"] == "running":
                return False, f"a {self.job['kind']} is already running"
            self.job = {"kind": kind, "state": "running", "started": manila_now().isoformat(
                timespec="seconds"), "output": "", "exit_code": None}
        threading.Thread(target=self._run, args=(self.job,), daemon=True).start()
        return True, f"{kind} started"

    def _run(self, job: dict) -> None:
        try:
            out = subprocess.run([self.python, "-m", "solsync", *self.COMMANDS[job["kind"]]],
                                 cwd=self.root, capture_output=True, text=True, timeout=3600,
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            job["output"] = (out.stdout + out.stderr)[-6000:]
            job["exit_code"] = out.returncode
        except Exception as exc:  # timeout, cannot start Python...
            job["output"], job["exit_code"] = str(exc), -1
        job["finished"] = manila_now().isoformat(timespec="seconds")
        job["state"] = "finished"


# ---------------------------------------------------------------- HTTP
def make_handler(root: Path, jobs: JobRunner, port: int):
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep the console quiet
            pass

        def _send(self, code: int, body, ctype: str = "application/json") -> None:
            data = body if isinstance(body, bytes) else json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(data)

        def _allowed(self) -> bool:
            # Host check blocks DNS-rebinding; the custom header blocks other websites,
            # because browsers cannot send it cross-site without a preflight we never answer.
            if self.headers.get("Host") not in allowed_hosts:
                return False
            return not self.path.startswith("/api/") or self.headers.get("X-SolSync") == "1"

        def _data(self):
            cfg = load_config(root=root)
            ledger = Ledger(cfg.state_dir / "solsync.db")
            return cfg, ledger

        def do_GET(self) -> None:
            if not self._allowed():
                return self._send(403, {"error": "forbidden"})
            path = urllib.parse.urlsplit(self.path).path
            if path == "/":
                return self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            try:
                cfg, ledger = self._data()
            except ConfigError as exc:
                return self._send(500, {"error": f"config.json problem: {exc}"})
            try:
                if path == "/api/overview":
                    rows = solutions(cfg, ledger)
                    return self._send(200, {**overview(cfg, ledger, rows), "job": jobs.job})
                if path == "/api/solutions":
                    return self._send(200, solutions(cfg, ledger))
                if path == "/api/events":
                    return self._send(200, ledger.events(500))
                return self._send(404, {"error": "not found"})
            finally:
                ledger.close()

        def do_POST(self) -> None:
            if not self._allowed() or self.headers.get("Content-Type") != "application/json":
                return self._send(403, {"error": "forbidden"})
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or 2))
            except ValueError:
                return self._send(400, {"error": "invalid JSON"})
            path = urllib.parse.urlsplit(self.path).path
            if path == "/api/jobs":
                ok, msg = jobs.start(str(body.get("kind")))
                return self._send(202 if ok else 409, {"ok": ok, "message": msg, "job": jobs.job})
            if path == "/api/settings":
                return self._settings(body)
            if path == "/api/automation":
                ok, msg = set_automation(body.get("action") == "pause")
                cfg, ledger = self._data()
                ledger.event("automation", "success" if ok else "error", msg)
                ledger.close()
                return self._send(200 if ok else 500, {"ok": ok, "message": msg})
            return self._send(404, {"error": "not found"})

        def _settings(self, body: dict) -> None:
            cfg, ledger = self._data()
            try:
                value = body.get("daily_limit")
                if isinstance(value, int) and not isinstance(value, bool) \
                        and value > HIGH_LIMIT_WARNING and not body.get("confirm"):
                    return self._send(409, {"ok": False, "needs_confirm": True, "message":
                                            f"{value} files per day is unusually high. Confirm to save."})
                try:
                    new = save_daily_limit(value, root / "config.json")
                except ConfigError as exc:
                    return self._send(400, {"ok": False, "message": str(exc)})
                except (OSError, ValueError) as exc:
                    return self._send(500, {"ok": False, "message": f"could not save settings: {exc}; "
                                            f"the previous limit ({cfg.daily_limit}) is still in use"})
                ledger.event("settings", "success",
                             f"Daily upload limit changed from {cfg.daily_limit} to {new}")
                return self._send(200, {"ok": True, "daily_limit": new})
            finally:
                ledger.close()

    return Handler


def serve(port: int = 8765, open_browser: bool = True, root: Path = PROJECT_ROOT) -> None:
    jobs = JobRunner(root)
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(root, jobs, port))
    url = f"http://127.0.0.1:{port}/"
    print(f"SolutionSync dashboard: {url}\nPress Ctrl+C in this window to stop it.")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("Dashboard stopped.")

"""SolutionSync desktop app: the same dashboard and engine, in its own window.

    SolutionSync.exe                      open the app
    SolutionSync.exe --data <folder>      use an existing SolutionSync data folder (remembered)
    SolutionSync.exe run [--dry-run]      run the engine without a window (for Task Scheduler)

The window shows the existing web dashboard (Edge WebView2 via pywebview). The app
serves it from an in-process server on 127.0.0.1, or reuses a SolutionSync dashboard
that is already running for the same data folder. Nothing here re-implements the
dashboard or the sync logic.
"""
from __future__ import annotations

import ctypes
import json
import os
import shutil
import socket
import sys
import threading
import time
import urllib.request
from pathlib import Path

from .config import ConfigError, data_root, load_config, location_file

APP = "SolutionSync"
PORT = 8765
CLI_COMMANDS = {"run", "status", "check", "reset-item", "inspect-export"}


def message(text: str, error: bool = True) -> None:
    """A plain Windows message box: works even when the window could not open."""
    ctypes.windll.user32.MessageBoxW(None, text, APP, 0x10 if error else 0x40)


def bundled(name: str) -> Path:
    """A file shipped next to the app (PyInstaller unpacks data under sys._MEIPASS)."""
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)) / name


def probe(port: int) -> dict | None:
    """The SolutionSync server on this port, or None (free port or an unrelated service)."""
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/ping", headers={"X-SolSync": "1"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            info = json.load(resp)
        return info if info.get("app") == APP else None
    except Exception:
        return None


def port_free(port: int) -> bool:
    with socket.socket() as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def first_instance() -> bool:
    """One desktop window at a time (a named mutex that Windows frees when we exit)."""
    first_instance.handle = ctypes.windll.kernel32.CreateMutexW(None, False, "Local\\SolutionSyncDesktop")
    return ctypes.windll.kernel32.GetLastError() != 183  # ERROR_ALREADY_EXISTS


def remember_data_folder(folder: str) -> str | None:
    path = Path(folder).expanduser().resolve()
    if not (path / "config.json").is_file():
        return f"{path} has no config.json, so it is not a SolutionSync data folder."
    location_file().parent.mkdir(parents=True, exist_ok=True)
    location_file().write_text(str(path), encoding="utf-8")
    return None


def prepare_data(root: Path) -> str | None:
    """Make sure the data folder is usable; returns a message to show if not."""
    cfg = root / "config.json"
    if not cfg.exists():
        root.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(bundled("config.example.json"), cfg)
        os.startfile(root)  # show the user where it is
        return (f"Welcome to SolutionSync.\n\nA starter settings file was created:\n{cfg}\n\n"
                "Edit it with your repository folders and GitHub URLs (see the README), then open "
                "SolutionSync again.\n\nAlready use SolutionSync from source? Run once:\n"
                "SolutionSync.exe --data \"<your SolutionSync folder>\"")
    try:
        load_config(root=root)
    except ConfigError as exc:
        return f"SolutionSync could not start because config.json has a problem:\n\n{exc}\n\nFile: {cfg}"
    return None


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--data"]:
        if len(argv) < 2:
            message("Usage: SolutionSync.exe --data <folder>")
            return 2
        problem = remember_data_folder(argv[1])
        if problem:
            message(problem)
            return 2
        argv = argv[2:]
    if argv[:1] and argv[0] in CLI_COMMANDS:  # headless engine, e.g. for the scheduled task
        from .__main__ import main as cli
        return cli(argv)

    if not first_instance():
        message("SolutionSync is already open.", error=False)
        return 0
    root = data_root()
    problem = prepare_data(root)
    if problem:
        message(problem, error="Welcome" not in problem)
        return 0 if "Welcome" in problem else 2

    from .__main__ import setup_logging
    from .dashboard import make_server
    setup_logging(root / "logs")

    # Reuse a dashboard already serving this data folder (not ours to stop); otherwise
    # start our own, on 8765 if free or any free port if something else holds it.
    server = jobs = None
    info = probe(PORT)
    if info and Path(info.get("data_root", "")).resolve() == root.resolve():
        url = f"http://127.0.0.1:{PORT}/"
    else:
        try:
            server, jobs = make_server(root, PORT if port_free(PORT) else 0)
        except OSError as exc:
            message(f"SolutionSync could not start its local dashboard server:\n\n{exc}")
            return 2
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{server.server_address[1]}/"

    try:
        import webview
        window = webview.create_window(APP, url, width=1360, height=900, min_size=(380, 560),
                                       background_color="#0e3442")

        def on_closing():
            # Never cut an upload short: hide the window and quit once the job is done.
            if jobs and jobs.running():
                window.hide()
                threading.Thread(target=finish_then_close, daemon=True).start()
                return False
            return True

        def finish_then_close():
            while jobs.running():
                time.sleep(1)
            window.destroy()

        window.events.closing += on_closing
        webview.start()
    except Exception as exc:
        message("SolutionSync could not open its window.\n\n"
                f"{exc}\n\nThe Microsoft Edge WebView2 Runtime may be missing: install it from "
                "https://go.microsoft.com/fwlink/p/?LinkId=2124703 and try again. Until then, "
                "the browser dashboard still works: py -m solsync dashboard")
        return 2
    finally:
        if server:
            server.shutdown()
            server.server_close()
    return 0

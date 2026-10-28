# Architecture

```
SolutionSyncAutomation/
  config.json              settings (no secrets): repo paths, remotes, quota, folder mapping
  solsync/
    __main__.py            command line: run, status, check, reset-item, inspect-export
    runner.py              one run: reconcile -> discover -> match -> select -> upload -> summary
    config.py              loads config.json; Manila date helper
    ledger.py              SQLite state: quota ledger, item history, rotation pointer
    lock.py                single-run lock (released by Windows if the process dies)
    exercism_source.py     Exercism API (same endpoints as the official CLI)
    hackerrank_source.py   reads the official HackerRank account export
    credentials.py         reads the Exercism token from Windows Credential Manager
    matching.py            already-uploaded detection, safe names, static validation
    gitsync.py             every Git command the tool runs (and nothing destructive)
  scripts/                 install/uninstall the scheduled task
  tests/                   unit + end-to-end tests on throwaway Git repos
  state/  logs/  inbox/    private runtime data (git-ignored)
```

## Key decisions

- **SQLite instead of JSON for state.** It gives transactions: `BEGIN IMMEDIATE` makes "check
  remaining quota, then reserve it" a single step no other process can interleave with. A crash
  never leaves a half-written file.
- **Quota is reserved before writing anything.** Each file is a row in `uploads`. It counts
  while `reserved`, `committed` or `verified`. If nothing reached GitHub, it becomes `failed` and
  frees its slot. This is why crashes and retries can never push the day above the daily limit.
- **Commits use `git commit --only -- <new files>`.** Anything you staged yourself stays staged
  and out of the commit. The commit is then checked to contain exactly the new files (all
  "added").
- **Truth comes from GitHub, not the ledger.** "Uploaded" means `git ls-remote` shows a
  commit that contains ours. On restart, unfinished batches are checked against GitHub before
  anything is retried, which covers "pushed, but crashed before saving".
- **Dry runs never fetch.** They read GitHub's file list with `git ls-remote`, using
  `git ls-tree` on a commit already present locally or the public GitHub API otherwise, so the
  local repo isn't modified at all.
- **Matching by content first.** Git's blob hash of the candidate (also tried with LF line
  endings) is compared with every file on GitHub, so renamed or moved copies count as present.
  Next comes the folder name, normalized by lowercasing and removing punctuation and spaces. A
  different file in the same folder is treated as a revision you made, not a missing
  solution.
- **No third-party dependencies in the engine.** (Only the desktop build adds PyInstaller and
  pywebview; see `requirements-desktop.txt`.) urllib, sqlite3, zipfile, ctypes and unittest cover
  everything. `Asia/Manila` falls back to a fixed UTC+8 offset when Windows Python lacks tz data.
  That's exact, because the Philippines hasn't used daylight saving since 1978.

## Desktop app

```
desktop_app.py             entry point PyInstaller packages (SolutionSync.exe)
solsync/desktop.py         window (pywebview / Edge WebView2), local server, lifecycle
SolutionSync.spec          PyInstaller recipe (one folder, windowed, bundles Python)
installer/SolutionSync.iss Inno Setup per-user installer
scripts/build_desktop.ps1  build: private venv -> PyInstaller -> zip -> installer
.github/workflows/desktop.yml  CI build; a v* tag publishes a GitHub Release
```

- **No second dashboard.** The window shows `dashboard.html` served by the same
  `dashboard.make_server`; the packaged app runs scan/sync jobs in-process through the same
  `runner.run`, because it has no separate Python to call.
- **One data folder for every interface.** `config.data_root()` resolves `SOLSYNC_HOME`, then
  `%APPDATA%\SolutionSync\data-location.txt`, then the source folder (or `%APPDATA%\SolutionSync`
  when packaged). Web, desktop and the scheduled task therefore share one config, one ledger
  and one quota; the run lock and SQLite transactions keep them from overlapping.
- **Lifecycle.** On start the app asks `/api/ping` on port 8765: a SolutionSync server for the
  same data folder is reused; anything else makes it serve on a free port. A named mutex allows
  one window. On close it stops only its own server, and waits for its own running job.

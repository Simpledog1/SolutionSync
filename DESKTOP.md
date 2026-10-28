# SolutionSync desktop app

The desktop app is the **same dashboard and the same engine** as the web version, packaged
as a normal Windows program: it opens in its own window, needs no Python and no command,
and includes its own copy of Python. It does not replace the web dashboard;
`py -m solsync dashboard` keeps working exactly as before.

| | Web dashboard | Desktop app |
|---|---|---|
| Open it | `py -m solsync dashboard` | Start menu → **SolutionSync** |
| Window | your browser | its own window (Microsoft Edge WebView2) |
| Python needed | yes | no |
| Settings, theme, upload history, daily limit | shared | shared |

**Still required on the PC:** [Git for Windows](https://git-scm.com/download/win) (the app
commits and pushes with it), and the Microsoft Edge WebView2 Runtime, which Windows 10 and 11
already include. If it is missing, the app says so and links to it.

---

## Install

### From a release

Download one of these from the **[latest release](https://github.com/Simpledog1/SolutionSync/releases/latest)**:

- **`SolutionSync-<version>-setup.exe`**: the installer. Installs for your user only (no
  admin rights) into `%LOCALAPPDATA%\Programs\SolutionSync`, with a Start-menu entry and an
  optional desktop shortcut. Uninstall from **Settings → Apps**.
- **`SolutionSync-<version>-win64-portable.zip`**: no installer. Unzip anywhere and run
  `SolutionSync\SolutionSync.exe`.

The app is not code-signed yet, so on first run Windows SmartScreen may say "Windows protected
your PC". Click **More info → Run anyway**.

### Build it yourself

From the SolutionSync source folder in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_desktop.ps1
```

This creates a private build environment (`.venv-build`; nothing is installed into your normal
Python), then writes:

| File | What it is |
|---|---|
| `dist\SolutionSync\SolutionSync.exe` | the app (keep the whole `SolutionSync` folder together) |
| `dist\SolutionSync-<version>-win64-portable.zip` | that folder, zipped |
| `dist\SolutionSync-<version>-setup.exe` | the installer, only when [Inno Setup 6](https://jrsoftware.org/isinfo.php) is installed |

The **Desktop app** GitHub Actions workflow (`.github/workflows/desktop.yml`) builds both the
installer and the zip on GitHub's Windows machines, on demand or when the app changes.

---

## First launch: where your data lives

The web dashboard, the desktop app and the scheduled task all use **one data folder**,
holding `config.json`, `state\` (the upload history and quota database), `logs\` and
`inbox\`. They find it in this order:

1. the `SOLSYNC_HOME` environment variable, if set;
2. the folder remembered in `%APPDATA%\SolutionSync\data-location.txt`;
3. otherwise: the source folder (web dashboard and Python) or `%APPDATA%\SolutionSync`
   (desktop app).

**Already using SolutionSync from source?** Point the desktop app at your existing folder
once, so it uses the same settings and upload history (nothing is copied or reset):

```powershell
& "$env:LOCALAPPDATA\Programs\SolutionSync\SolutionSync.exe" --data "G:\DAILY\SolutionSyncAutomation"
```

It remembers this in `data-location.txt`. Delete that file to undo it.

**New user?** The first launch creates a starter `config.json` in `%APPDATA%\SolutionSync`
and opens that folder. Fill it in as described in the README's
[Configure](README.md#3-configure) step, then open the app again. Your Exercism token goes
into Windows Credential Manager exactly as in the README; no password or token is stored in
the app or its files.

---

## Using web and desktop together, safely

- **Same data, one quota.** Both read the same `config.json` and database, so a limit saved in
  one is the limit everywhere, and uploads from either count toward the same daily total.
- **No double jobs.** Inside one app the buttons refuse a second job; across apps (web,
  desktop, scheduled task) the engine's run lock lets only one scan or sync run at a time.
  The other is reported as "skipped: another run is already in progress".
- **Opening the desktop app while the web dashboard is running** reuses that dashboard instead
  of starting a second server. If another, unrelated program holds port 8765, the app quietly
  uses a different port.
- **Only one desktop window**: opening it again says "SolutionSync is already open".
- **Closing the desktop app** stops only what it started. It never stops the web dashboard or
  the scheduled task. If a scan or sync is running, the window hides and the app exits once the
  job finishes, so an upload is never cut off.

## Scheduled automation

The daily task keeps working whether or not the desktop app is open; closing the app does
not pause it. Pause and resume it from the app's **Pause automation** button, as before.

- **If you have Python** (the source setup), nothing changes: the task runs
  `pythonw -m solsync run`.
- **Desktop-only users without Python** can have the task run the app's built-in engine
  instead:

  ```powershell
  $app = "$env:LOCALAPPDATA\Programs\SolutionSync"
  powershell -ExecutionPolicy Bypass -File "$app\_internal\scripts\install_task.ps1" -Exe "$app\SolutionSync.exe"
  ```

  (`SolutionSync.exe run` runs the engine without a window. The script ships inside the app;
  for the portable zip, set `$app` to wherever you unzipped the `SolutionSync` folder.)

## Updating

Install the new `setup.exe` over the old one, or replace the portable folder. Your data folder
is never inside the install folder, so settings, upload history and the daily quota are kept.
If the task runs the app (`-Exe`) and you moved the app, re-run the `install_task.ps1` line.

## Releasing a new version (maintainers)

1. Raise `__version__` in `solsync/__init__.py`.
2. Commit and push, then tag: `git tag v1.2.3` and `git push origin v1.2.3`.
3. The **Desktop app** workflow builds, tests and publishes a GitHub Release with the installer
   and the portable zip.

## Troubleshooting

| Problem | What to do |
|---|---|
| "could not open its window … WebView2" | Install the Evergreen WebView2 Runtime from Microsoft (link in the message), then open the app again. Meanwhile `py -m solsync dashboard` works in a browser. |
| "config.json has a problem" | The message names the file and the problem. Fix it in Notepad; files saved with or without a BOM both work. |
| Statuses say **Unable to Verify** / "Git was not found" | Install Git for Windows and check that `git` works in a new terminal. |
| "No Exercism token" / "rejected the token" | Store or replace the token with `cmdkey`, as in [TROUBLESHOOTING.md](TROUBLESHOOTING.md). |
| The desktop app shows different data than the web dashboard | They are using different data folders. Run `SolutionSync.exe --data "<your folder>"` once. |
| Nothing happens when opening it | It may already be open in the background finishing a sync. Wait a minute, or check Task Manager for `SolutionSync.exe`. |

Logs: `<data folder>\logs\solsync.log`.

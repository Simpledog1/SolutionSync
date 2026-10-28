# SolutionSync

**Automatically back up your solved HackerRank and Exercism problems to your own GitHub
repositories, a few files per day.**

You solve problems on HackerRank and Exercism. SolutionSync finds the ones you have
*completed*, checks which of them are not on GitHub yet, and uploads them to two GitHub
repositories you own, at most a few new files each day. Your GitHub then shows steady
progress instead of one giant dump. Once set up, it runs by itself every day through
Windows Task Scheduler.

> **Windows 10 and 11 only.** SolutionSync uses Windows Task Scheduler and Windows
> Credential Manager, so it does not run on macOS or Linux.

> **Use it responsibly.** Only use your own HackerRank, Exercism and GitHub accounts, and
> repositories you are allowed to push to. Follow each website's terms of service.
> SolutionSync does not log in to websites for you, bypass logins or CAPTCHAs, or scrape
> pages. It uses Exercism's API with your own token and a data export that HackerRank
> lets you download yourself.

---

## Contents

- [Quick start](#quick-start)
- [1. What SolutionSync does](#1-what-solutionsync-does)
- [2. What you need](#2-what-you-need)
- [3. Install](#3-install)
- [4. Configure](#4-configure)
- [5. Your first run, safely](#5-your-first-run-safely)
- [6. Ways to use it](#6-ways-to-use-it)
- [7. Daily use and the daily limit](#7-daily-use-and-the-daily-limit)
- [8. Settings reference](#8-settings-reference)
- [9. Where files go in your repositories](#9-where-files-go-in-your-repositories)
- [10. Troubleshooting](#10-troubleshooting)
- [11. Your data, privacy and security](#11-your-data-privacy-and-security)
- [12. Updating and uninstalling](#12-updating-and-uninstalling)
- [13. FAQ](#13-faq)

---

## Quick start

For people who already have Python, Git and two GitHub repositories for their solutions.
Every step is explained in detail further down.

```powershell
cd C:\Code
git clone https://github.com/Simpledog1/SolutionSync.git
cd SolutionSync
Copy-Item config.example.json config.json
notepad config.json
```

In Notepad, set your two repository folders and GitHub URLs ([step 4](#4-configure)).
Then store your Exercism token, check everything and do a dry run:

```powershell
cmdkey /generic:SolutionSync-Exercism /user:exercism /pass
py -m solsync check
py -m solsync run --dry-run
```

When the dry run looks right, set `"uploads_enabled": true` in `config.json`, then schedule
the daily run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_task.ps1 -Time 06:00
```

---

## 1. What SolutionSync does

**Who it is for:** anyone who practises on HackerRank or Exercism and wants their solved
problems kept on GitHub, without copying files by hand.

**How it works:**

1. **Finds your completed solutions.**
   - **Exercism:** solutions you marked complete, read through Exercism's official API
     using your personal API token.
   - **HackerRank:** challenges you solved with full marks, read from the data export you
     download from HackerRank. HackerRank has no API for your submitted code, so this
     export is the only supported source.
2. **Checks GitHub.** It compares each solution with what is already in your solution
   repository, by file content and by folder name, so renamed or moved copies still count
   as present.
3. **Uploads what is missing.** It copies your submitted code (never changed) into the
   right folder of your local copy of the repository, commits it with your Git identity
   and pushes it to GitHub. It uploads at most the **daily limit** of new files per day:
   4 by default, HackerRank and Exercism combined.

**Three different actions:**

| Action | What happens | Changes anything? |
|---|---|---|
| **Scan** (dry run) | Finds your solutions and shows what is missing on GitHub and what *would* be uploaded. | No. Nothing is committed or pushed, and no quota is used. |
| **Sync** (run) | Does a scan, then uploads up to the remaining daily limit. | Yes: commits and pushes new files to your solution repositories. |
| **View progress** | The dashboard, or `py -m solsync status`, shows what is published, missing or needs attention. | No. |

**What is automatic and what is not:**

| Automatic (after setup) | You do it |
|---|---|
| A daily run (sync) at the time you choose, plus a catch-up run after you sign in | Download a fresh HackerRank export when you have solved new HackerRank problems |
| Finding new Exercism solutions | Keep your Exercism token valid |
| Retrying failed uploads safely | Fix anything listed as needing your attention |

**Features**

- Uploads only **completed** solutions, using your **real submitted code**. It never writes
  or changes solutions.
- **Never overwrites or duplicates** anything already in your repositories.
- **Daily limit** (default 4 files per Philippine day), changeable from the dashboard.
- **Dashboard** in your browser or as a desktop app: progress, every solution's GitHub
  status, activity log and settings.
- **Safe dry runs** that change nothing.
- Free: plain Python with **no packages to install**, no paid services, no AI.

---

## 2. What you need

All of these are required unless marked optional.

| What | Why | Get it |
|---|---|---|
| **Windows 10 or 11** | Task Scheduler and Credential Manager are Windows features. | |
| **Python 3.10 or newer** (tested with 3.13 and 3.15) | SolutionSync is a Python program. Not needed if you only use the [desktop app](#64-desktop-app). | [python.org/downloads/windows](https://www.python.org/downloads/windows/) |
| **Git for Windows** | SolutionSync commits and pushes with Git. It includes Git Credential Manager, which remembers your GitHub login. Needed for the desktop app too. | [git-scm.com/download/win](https://git-scm.com/download/win) |
| **A GitHub account** | Your solutions are uploaded to your repositories. | [github.com/signup](https://github.com/signup) |
| **Two GitHub repositories**, one for HackerRank and one for Exercism solutions | For example `HackerRank-Problems` and `Exercism-Problems`. They can be new, but each needs at least one commit (for example a README). | [Creating a new repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository) |
| **An Exercism account** (if you use Exercism) | For your solutions and API token. | [exercism.org](https://exercism.org) |
| **A HackerRank account** (if you use HackerRank) | For your data export. | [hackerrank.com](https://www.hackerrank.com) |
| **Internet access** | To reach GitHub and Exercism. | |

You do **not** need a virtual environment, `pip install`, a browser extension, browser
automation or admin rights.

### Open PowerShell

All commands in this guide are typed into **PowerShell**:

1. Press the **Windows key**, type `PowerShell` and press **Enter**.
2. A window opens with a line starting with `PS C:\Users\<you>>`. That is where you type.
3. To paste a command, copy it from this page and right-click in the window (or press
   **Ctrl + V**), then press **Enter**.

### Check Python and Git

```powershell
py --version
git --version
```

You should see something like `Python 3.13.1` and `git version 2.47.0.windows.1`.

- **`py` is not recognized:** Python is missing, or was installed without the `py`
  launcher. Install it from [python.org](https://www.python.org/downloads/windows/), then
  close and reopen PowerShell.
- **`git` is not recognized:** install Git for Windows (default options are fine), then
  close and reopen PowerShell.

> **Use `py`, not `python`.** This guide always uses `py`, the Python launcher for Windows.
> On many PCs, typing `python` opens the Microsoft Store or says "Python was not found",
> even though Python is installed. That is a Windows shortcut (an "app execution alias")
> getting in the way. `py` always finds your real Python.

---

## 3. Install

### Step 1: Choose a folder

This guide uses `C:\Code`. Create it and go there:

```powershell
New-Item -ItemType Directory -Force C:\Code
cd C:\Code
```

### Step 2: Download SolutionSync

```powershell
git clone https://github.com/Simpledog1/SolutionSync.git
cd SolutionSync
```

This copies SolutionSync into `C:\Code\SolutionSync` and moves you into that folder.
**Run every `py -m solsync ...` command from this folder.**

### Step 3: Download your two solution repositories

Use your own GitHub username and repository names. Keep them **outside** the SolutionSync
folder, which is why the first line goes back up to `C:\Code`:

```powershell
cd C:\Code
git clone https://github.com/YOUR-USERNAME/HackerRank-Problems.git
git clone https://github.com/YOUR-USERNAME/Exercism-Problems.git
```

### Step 4: Tell Git who you are (once per PC)

Uploads are commits made in your name. If you have never used Git on this PC, set your name
and the email address of your GitHub account:

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Check with `git config --global user.name`. It should print your name.

### Step 5: Let Git sign in to GitHub

This asks GitHub for permission to push, without sending anything:

```powershell
git -C C:\Code\HackerRank-Problems push --dry-run
git -C C:\Code\Exercism-Problems push --dry-run
```

The first time, a GitHub sign-in window appears. Sign in in your browser; Git Credential
Manager remembers it. Success looks like `Everything up-to-date`. If you see
`Permission denied` or `403`, the repository is not yours or you lack write access.

If a repository is completely empty, add a first commit on github.com (for example
**Add a README**), then run `git -C C:\Code\HackerRank-Problems pull`.

### Step 6: Nothing to install

SolutionSync uses only Python's standard library, so there is no `pip install` step and no
virtual environment. Check that it starts:

```powershell
cd C:\Code\SolutionSync
py -m solsync --help
```

You should see `usage: py -m solsync [-h] {run,status,check,reset-item,inspect-export,dashboard}`.
Installation is done; next, configure it.

---

## 4. Configure

### Required: create your config.json

`config.json` in the SolutionSync folder holds your settings. **It contains no passwords
or tokens.** It isn't part of the download, and Git ignores it, so your settings are never
committed or overwritten by updates. Create it from the template and open it:

```powershell
cd C:\Code\SolutionSync
Copy-Item config.example.json config.json
notepad config.json
```

Change the values marked here, then save (**Ctrl + S**):

```json
{
  "daily_limit": 4,
  "uploads_enabled": false,
  "max_downloads_per_run": 10,
  "repos": {
    "hackerrank": {
      "path": "C:/Code/HackerRank-Problems",
      "remote_url": "https://github.com/YOUR-USERNAME/HackerRank-Problems.git",
      "branch": "main"
    },
    "exercism": {
      "path": "C:/Code/Exercism-Problems",
      "remote_url": "https://github.com/YOUR-USERNAME/Exercism-Problems.git",
      "branch": "main",
      "language_dirs": {"python": "Python", "dart": "Dart"}
    }
  },
  "exercism": {
    "api_base": "https://api.exercism.org",
    "credential_target": "SolutionSync-Exercism"
  },
  "hackerrank": {
    "inbox": "inbox/hackerrank"
  }
}
```

- **`path`**: where you cloned each repository in [step 3](#step-3-download-your-two-solution-repositories).
  Use forward slashes `/` (a single `\` breaks the file).
- **`remote_url`**: the repository's GitHub URL, exactly as you cloned it. SolutionSync
  refuses to push anywhere else.
- **`branch`**: usually `main`.
- **`language_dirs`** (Exercism): one entry per Exercism track you use, mapping the track
  name as it appears in Exercism URLs to the top folder in your repository, for example
  `"javascript": "JavaScript"`. Tracks not listed are not uploaded; they are shown for review.
- Leave **`"uploads_enabled": false`** for now. While it is `false`, every run is a dry run.

All settings are explained in the [settings reference](#8-settings-reference).

**Only using one platform?** Still fill in both repositories (both are checked at startup),
and skip the other platform's connection step below. Runs then report the unused platform
as a problem (`No Exercism token` or `no export file`) and finish as "partial" (exit code 1).
Uploads for the platform you use work normally.

### Required for Exercism: store your API token

SolutionSync reads your Exercism solutions with your personal API token. It is kept in
**Windows Credential Manager**, never in a file.

1. Sign in at [exercism.org/settings/api_cli](https://exercism.org/settings/api_cli) and
   copy your **API token**.
2. Run this command. At the `Password:` prompt, paste the token (nothing appears while
   you paste) and press **Enter**:

   ```powershell
   cmdkey /generic:SolutionSync-Exercism /user:exercism /pass
   ```

   Success: `CMDKEY: Credential added successfully.`

> Never paste your token into a chat, an issue, a file or a commit. If you ever do,
> generate a new token on Exercism (the old one stops working) and store it again with the
> same command.

### Required for HackerRank: download your data export

1. On hackerrank.com, click your profile picture → **Settings** → **Export Data** →
   **Create new archive**.
2. When it is ready, click **Download**. HackerRank allows one new archive every 24 hours.
3. Create the inbox folder and open it:

   ```powershell
   New-Item -ItemType Directory -Force C:\Code\SolutionSync\inbox\hackerrank
   explorer C:\Code\SolutionSync\inbox\hackerrank
   ```

4. Move the downloaded file (`.json` or `.zip`) into that folder. If there are several
   files, the newest one is used.
5. Check that it was understood:

   ```powershell
   py -m solsync inspect-export
   ```

   This shows only the *structure* of the file, never your code. The last line should look
   like `Reader result: 231 submission records, 137 accepted solutions`.

A HackerRank solution counts as completed when it scored full marks. Supported sections:
**Python**, **Java**, **Problem Solving** (Algorithms, Data Structures) and **30 Days of
Code**, in Python or Java. Others are listed for review, not uploaded.

**Repeat this whenever you solve new HackerRank problems.** The export does not update
itself, and SolutionSync never logs in to HackerRank.

### Check everything

```powershell
py -m solsync check
```

This checks both repositories and both platforms without changing anything. Success looks
like:

```
[hackerrank] repo: OK
[exercism] repo: OK
[hackerrank] platform: ok (export my_data.json) (137 completed found)
[exercism] platform: ok (token accepted) (58 completed found)
```

Any other message names the problem; see [Troubleshooting](#10-troubleshooting).

---

## 5. Your first run, safely

### 1. Do a dry run

```powershell
py -m solsync run --dry-run
```

A dry run is a real scan that changes nothing: it does not commit, push or use the daily
limit. It can take a minute or two. It lists every solution it found and what it would do:

```
[hackerrank] access: ok (export my_data.json)
  repo ok: True
  records seen: 231  completed found: 137
   - eligible                 Plus Minus -> Problem Solving (Python)/Plus Minus/1.py
   - deferred_quota           Text Wrap -> Python/Text Wrap/1.py  (daily quota reached; ...)

Counts: completed_found=195, already_present=98, new_candidates=86, ...
Quota: 0/4 used today, 4 remaining
  would upload: hackerrank:plus-minus:python -> Problem Solving (Python)/Plus Minus/1.py
```

### 2. Review it

- **`already_present=`** counts solutions already in your repositories. They are not listed
  one by one and are never uploaded again.
- **`eligible`** and **`would upload`** show exactly which files would go where. Check the
  folder and file names; [section 9](#9-where-files-go-in-your-repositories) explains the layout.
- **`deferred_quota`** items wait for a later day because of the daily limit.
- Anything else (`needs_review`, `conflict`, ...) is explained in the
  [status table](#status-names).

Each Exercism run downloads at most 10 solutions (`max_downloads_per_run`), so on a first
run some show `needs_source`. They are fetched on later runs.

### 3. Allow uploads

Open `config.json` (`notepad config.json`), change `"uploads_enabled": false` to
`"uploads_enabled": true` and save. **This is the switch that lets SolutionSync push.**

To start extra carefully, also set `"daily_limit": 1` so the first run uploads only one
file. Set it back later from the dashboard.

### 4. Do one real run

```powershell
py -m solsync run
```

Success: the first line says `mode=live  status=success`, and the end lists
`uploaded_verified: ...` for each uploaded file. The file is counted only after GitHub
confirms it.

### 5. Check on GitHub and in SolutionSync

1. Open your repository on github.com. The newest commit adds the file(s) shown in the
   run's output, in the folder it listed.
2. Run `py -m solsync status`. The first line shows today's count, for example
   `Manila day 2026-10-28: 1/4 files used`, and `Last successful upload:` shows the time.

### 6. Schedule the daily run

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_task.ps1 -Time 06:00
```

This creates the Windows task **SolutionSync Daily**. Choose any time with `-Time`. The
script prints a summary ending with the next run time. Running it again just updates the
task.

---

## 6. Ways to use it

### 6.1 Web dashboard

```powershell
cd C:\Code\SolutionSync
py -m solsync dashboard
```

Your browser opens **http://127.0.0.1:8765**. If it doesn't, open that address yourself.

- **To stop it:** press **Ctrl + C** in the PowerShell window, or close the window.
- **Options:** `--port 8766` uses another port; `--no-browser` doesn't open the browser.
- Only your own PC can reach the dashboard, and other websites cannot press its buttons.
- **Port already in use:** if PowerShell shows an error ending in `WinError 10013` or
  `WinError 10048`, another program (perhaps a SolutionSync window that is already open)
  uses port 8765. Use the open one, or run `py -m solsync dashboard --port 8766`.

| Page | What you can do |
|---|---|
| **Overview** | A status banner (**Fair** = all good, **Caution** = needs a look, **Storm** = something failed), today's uploads against your limit, each repository's progress, totals, the last 14 days and recent activity. Buttons: **Scan solutions** and **Refresh GitHub status** (dry runs: check everything, upload nothing), **Run sync** (upload within today's limit; asks first), **Pause / Resume automation** (turns the scheduled task off and on). |
| **Solutions** | Every solution with its GitHub status: **Published**, **Missing**, **Pending**, **Failed** or **Unable to Verify** (GitHub could not be checked). Filter by platform and status, search by name, and click a row for its file paths, GitHub link and last error. |
| **Activity logs** | Scans, uploads, limit changes, pauses and errors, grouped by day, with filters. |
| **Settings** | Change the **daily upload limit**. |

**Run sync** respects `uploads_enabled`: while it is `false`, it does a dry run.

### 6.2 Command line

Run these from the SolutionSync folder. Show the built-in help with `py -m solsync --help`.

| Command | What it does | Changes anything? |
|---|---|---|
| `py -m solsync check` | Checks both repositories and both platform connections. | No |
| `py -m solsync run --dry-run` | Full scan; shows what would be uploaded. | No (it only refreshes SolutionSync's own records) |
| `py -m solsync run` | Scan and upload up to today's remaining limit. A dry run while `uploads_enabled` is `false`. | **Yes**: commits and pushes to your repositories |
| `py -m solsync status` | Today's count, unfinished uploads and every item that is not done yet. | No |
| `py -m solsync inspect-export` | Shows the structure of your HackerRank export (no code). | No |
| `py -m solsync reset-item KEY` | Lets an item that stopped retrying be retried on the next run, e.g. `py -m solsync reset-item exercism:python/bob`. | Only SolutionSync's records |
| `py -m solsync dashboard` | Starts the web dashboard. | Only through its buttons |

For a short summary, use `py -m solsync status | Select-Object -First 4`.

**Exit codes** (also shown by Task Scheduler as "Last Run Result"): `0` success, `1` partly
done or something needs attention, `2` failed (for example a broken `config.json`), `3`
skipped because another run was already in progress.

### 6.3 Scheduled automation

The task **SolutionSync Daily** (created in [step 5.6](#6-schedule-the-daily-run)) runs
`py -m solsync run` without opening a window:

- every day at the time you chose, **using your PC's clock**; and
- 5 minutes after you sign in to Windows or unlock the PC, to catch up on a run that was
  missed because the PC was off or asleep. Once the day's limit is used, these extra
  runs finish immediately.

It runs **as you, only while you are signed in**, because that is how it can use your saved
GitHub login and Exercism token. It does not wake the PC from sleep, needs no admin rights,
and stores no password. It works whether or not the dashboard is open. Without internet,
a run fails safely and the next one tries again.

| To... | Do this |
|---|---|
| See its state and last result | `Get-ScheduledTaskInfo -TaskName "SolutionSync Daily"` (`LastTaskResult` uses the exit codes above), or the dashboard sidebar |
| Pause it | Dashboard → **Pause automation**, or `Disable-ScheduledTask -TaskName "SolutionSync Daily"` |
| Resume it | Dashboard → **Resume automation**, or `Enable-ScheduledTask -TaskName "SolutionSync Daily"` |
| Change the time | Run `install_task.ps1` again with a new `-Time` |
| Remove it | `powershell -ExecutionPolicy Bypass -File scripts\uninstall_task.ps1` |

**Did a scheduled run work?** `py -m solsync status` ends with a line such as
`last_run.json: 2026-10-28T06:01:12+08:00 status=success exit=0`. The Activity logs page
and `logs\solsync.log` show the details.

### 6.4 Desktop app

There is also a Windows desktop app: the same dashboard in its own window, with Python
included. It shares settings, history and the daily limit with everything above.
**[Download it from the latest release](https://github.com/Simpledog1/SolutionSync/releases/latest)**:
`SolutionSync-<version>-setup.exe` (installer) or the portable `.zip`. It still needs Git
for Windows.

The app is not code-signed yet, so Windows SmartScreen may warn on first run; click
**More info → Run anyway**. Installing, pointing it at an existing SolutionSync folder,
scheduling and building it yourself are covered in **[DESKTOP.md](DESKTOP.md)**.

---

## 7. Daily use and the daily limit

### A normal day

You don't need to do anything: the scheduled task uploads up to the daily limit. When you
want to look:

1. Open the dashboard (`py -m solsync dashboard`, or the desktop app).
2. Read the **Overview** banner. **Fair** means nothing needs you.
3. Click **Scan solutions** to pick up solutions you just finished. It uploads nothing.
4. Use **Solutions** to search or filter, for example to see everything still **Missing**.
5. Check **Activity logs** for what happened recently.
6. Solved new HackerRank problems? Download a fresh export into `inbox\hackerrank`
   ([how](#required-for-hackerrank-download-your-data-export)). New Exercism solutions are
   found automatically.

### How the daily limit works

- **Default: 4 new files per day**, HackerRank and Exercism combined (`"daily_limit": 4`).
- **"Day" means the Philippine calendar day** (Asia/Manila time, UTC+8, midnight to
  midnight). The count resets at midnight Manila time, whatever your PC's time zone.
- **What counts:** a file counts once it is committed for upload. If it never reaches
  GitHub, the slot is freed again. Dry runs, scans and solutions already on GitHub never
  count.
- **When the limit is reached:** remaining solutions show as `deferred_quota` and wait for
  the next day. An exercise with several files is never split across days. When both
  platforms have work, they take turns.
- **Failed uploads:** the commit stays in your local repository and is retried
  automatically on the next run, after checking GitHub first, so it is never uploaded
  twice. On a later day it needs a free slot of that day.
- **Failed downloads (Exercism):** retried later with growing waits, at most 5 times. Then
  `py -m solsync reset-item KEY` allows a fresh try.

### Change the limit

- **Dashboard → Settings → Daily upload limit.** Saved to `config.json`, so the scheduled
  task uses it too. Values above 8 ask for confirmation.
- Or edit `"daily_limit"` in `config.json`.

Allowed values: whole numbers from **0** (no new uploads) to the safety maximum, **20** by
default (`max_daily_limit`). Changing the limit does not reset today's count and never
re-uploads anything. Lowering it below what you already uploaded today simply stops
uploads for the rest of the day.

---

## 8. Settings reference

All settings live in `config.json`. Every run and every dashboard refresh reads the file
again, so **no restart is needed** after a change.

| Setting | What it controls | Default | Allowed values | Where to change |
|---|---|---|---|---|
| `daily_limit` | Most new files uploaded per Manila day, both platforms combined | `4` | Whole number, 0 to `max_daily_limit` | Dashboard → Settings, or `config.json` |
| `max_daily_limit` | Safety maximum for `daily_limit` (not in the template; add it to change it) | `20` | Whole number, 1 to 100 | `config.json` |
| `uploads_enabled` | `false`: every run is a dry run. `true`: runs may commit and push | `false` in the template | `true` / `false` | `config.json` |
| `max_downloads_per_run` | How many Exercism solutions are downloaded per run (keeps requests polite) | `10` | Whole number | `config.json` |
| `repos.<platform>.path` | Folder of your local solution repository; must be outside the SolutionSync folder | none (required) | A folder path with `/` | `config.json` |
| `repos.<platform>.remote_url` | The only GitHub URL SolutionSync will push to | none (required) | Your repository's URL | `config.json` |
| `repos.<platform>.branch` | Branch to upload to | `main` | An existing branch | `config.json` |
| `repos.exercism.language_dirs` | Exercism track → top folder in your repository | `{"python": "Python", "dart": "Dart"}` in the template | Track names as in Exercism URLs | `config.json` |
| `exercism.credential_target` | Name of the Credential Manager entry holding your token | `SolutionSync-Exercism` | Any name you stored with `cmdkey` | `config.json` |
| `exercism.api_base` | Exercism API address; leave as is | `https://api.exercism.org` | | `config.json` |
| `hackerrank.inbox` | Folder for your HackerRank export (relative to the SolutionSync folder, or a full path) | `inbox/hackerrank` | A folder path | `config.json` |

Advanced: the environment variable `SOLSYNC_HOME` makes SolutionSync use a different folder
for `config.json`, `state`, `logs` and `inbox` (see [DESKTOP.md](DESKTOP.md#first-launch-where-your-data-lives)).
Most people never need it.

---

## 9. Where files go in your repositories

SolutionSync follows a fixed folder layout and never moves or renames existing files.

**Exercism:** `<Track folder>/<Exercise title>/<your solution file>`

```
Exercism-Problems/
  Python/
    Bob/bob.py
    Grains/grains.py
  Dart/
    Hello World/hello_world.dart
```

The track folder comes from `language_dirs`. Only the files Exercism marks as *your
solution* are copied, never tests or READMEs.

**HackerRank:** `<Section (Language)>/<Challenge name>/<file>`. The language is left out
when it matches the section name. Python solutions are saved as `1.py`, Java as
`Solution.java`.

| HackerRank section | Python | Java |
|---|---|---|
| Python | `Python/<name>/1.py` | n/a |
| Java | n/a | `Java/<name>/Solution.java` |
| Problem Solving (Algorithms, Data Structures) | `Problem Solving (Python)/<name>/1.py` | `Problem Solving (Java)/<name>/Solution.java` |
| 30 Days of Code | `30 Days of Code (Python)/<name>/1.py` | `30 Days of Code (Java)/<name>/Solution.java` |

HackerRank's export doesn't say which section a challenge belongs to, so SolutionSync looks
it up in `solsync\hackerrank_sections.json`. If HackerRank adds challenges, refresh it with
`py scripts\build_hackerrank_sections.py`.

**Solutions you uploaded yourself** are recognised if the same code is anywhere in the
repository, or a folder with the same exercise name exists (ignoring case and punctuation),
and are never uploaded again.

### Status names

| Status | Meaning |
|---|---|
| `eligible` | Missing from GitHub and ready to upload. |
| `deferred_quota` | Ready, but today's limit is used up. It goes on a later day. |
| `uploaded_verified` | Uploaded, and GitHub confirmed it. |
| `already_present` | Already in your repository. Nothing to do. |
| `needs_source` | Exercism solution not downloaded yet (a few are fetched each run). |
| `needs_review` | Not uploaded: unsupported section or language, or a failed check (for example a syntax error or something that looks like a password). |
| `conflict` / `ambiguous_match` | Something already sits at that path, or several folders could match. Not touched; you decide. |
| `upload_failed` | Commit or push failed. Kept and retried safely on the next run. |
| `retrieval_failed` / `missing_source` | Couldn't fetch the code. Retried later with growing waits. |

---

## 10. Troubleshooting

**Start here.** These show what went wrong without changing anything:

```powershell
cd C:\Code\SolutionSync
py -m solsync status
Get-Content logs\solsync.log -Tail 50
```

Git-specific problems (unpushed commits, diverged histories, failed pulls) are covered in
**[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**, and desktop-app problems in
[DESKTOP.md](DESKTOP.md#troubleshooting).

#### `py` is not recognized
- **Cause:** Python isn't installed, or was installed without the `py` launcher.
- **Check:** `py --version`.
- **Fix:** install Python from [python.org](https://www.python.org/downloads/windows/),
  then close and reopen PowerShell. Don't switch to `python`; see [the note](#check-python-and-git).
- **Verify:** `py --version` prints a version of 3.10 or newer.

#### `git` is not recognized, or statuses say "Git was not found"
- **Cause:** Git for Windows is missing, or PowerShell was opened before installing it.
- **Fix:** install [Git for Windows](https://git-scm.com/download/win), then open a new
  PowerShell window.
- **Verify:** `git --version`, then `py -m solsync check`.

#### `No module named solsync`
- **Cause:** you are not in the SolutionSync folder.
- **Fix:** `cd C:\Code\SolutionSync` (or wherever you cloned it), then run the command again.
- **Verify:** `py -m solsync --help` shows the command list.

#### `Config error: Cannot read ...config.json` or a JSON error
- **Cause:** `config.json` is missing or has a typo, such as a missing comma or quote, or a
  single `\` in a path.
- **Check:** the message names the line and column.
- **Fix:** correct it in Notepad (use `/` in paths), or start again from the template with
  `Copy-Item config.example.json config.json -Force` (this replaces your settings).
- **Verify:** `py -m solsync check`.

#### `Solution repos must live outside the automation project`
- **Cause:** a `path` points inside the SolutionSync folder.
- **Fix:** clone the repository next to it (for example `C:\Code\HackerRank-Problems`) and
  update `path`.
- **Verify:** `py -m solsync check` shows `repo: OK`.

#### `repo:` shows `is not a Git repository`, `origin is ..., expected ...` or `current branch is ...`
- **Cause:** `path` points to the wrong folder, `remote_url` differs from the repository's
  real URL, or the repository is on a different branch than `branch`.
- **Check:** `git -C C:\Code\HackerRank-Problems remote -v` shows the real URL;
  `git -C C:\Code\HackerRank-Problems status` shows the current branch.
- **Fix:** correct `path`, `remote_url` or `branch` in `config.json`, or switch the
  repository back with `git -C C:\Code\HackerRank-Problems switch main`.
- **Verify:** `py -m solsync check` shows `repo: OK`.

#### GitHub sign-in fails, `cannot reach GitHub`, `Permission denied` or `403`
- **Cause:** Git is not signed in to GitHub, the saved login expired, your account has no
  write access, or there is no internet.
- **Check:** `git -C C:\Code\HackerRank-Problems push --dry-run`.
- **Fix:** sign in when the window appears. If you have no write access, use a repository
  you own. If an old login is stuck, open **Credential Manager** (Start menu) →
  **Windows Credentials**, remove the `git:https://github.com` entry, and run the
  `push --dry-run` command again to sign in fresh. Removing it only makes Git ask you to
  sign in again.
- **Verify:** the command prints `Everything up-to-date`.

#### Exercism: `No Exercism token` or `Exercism rejected the token (HTTP 401/403)`
- **Cause:** the token was never stored, or it was regenerated or revoked.
- **Fix:** copy your current token from
  [exercism.org/settings/api_cli](https://exercism.org/settings/api_cli) and store it again
  (this replaces the old one):

  ```powershell
  cmdkey /generic:SolutionSync-Exercism /user:exercism /pass
  ```

- **Verify:** `py -m solsync check` shows `[exercism] platform: ok (token accepted)`.

After an authentication error, SolutionSync stops calling Exercism for the rest of that
run, so a bad token never floods the site.

#### HackerRank: `no export file`, `export unreadable` or `0 accepted solutions`
- **Cause:** no export in `inbox\hackerrank`, or the file isn't a HackerRank export.
- **Check:** `py -m solsync inspect-export`.
- **Fix:** download a fresh export ([how](#required-for-hackerrank-download-your-data-export))
  and put it in `inbox\hackerrank`. If HackerRank changed its export format, see
  [TROUBLESHOOTING.md](TROUBLESHOOTING.md#hackerrank-export-problems).
- **Verify:** the last line of `inspect-export` reports accepted solutions.

#### Browser sessions or logins "expiring"
SolutionSync never uses a browser session. It uses only your Exercism token, your saved
GitHub login (Git Credential Manager) and your HackerRank export file. If one of them stops
working, see the matching entry above.

#### A solution shows as missing, but it is on GitHub (or the reverse)
- **Cause:** your copy is in a different folder with different code, or GitHub could not be
  reached (then it shows **Unable to Verify**, never Missing).
- **Check:** in the dashboard, open the solution on the **Solutions** page to see the exact
  paths compared. In PowerShell, run `git -C <repo folder> pull` so your local copy is
  current.
- **Fix:** if it is a different version of your solution, either leave it (it is reported,
  not overwritten) or move or rename it yourself. SolutionSync never moves files.
- **Verify:** click **Refresh GitHub status**.

#### An upload failed (`upload_failed`)
- **Cause:** usually no internet or a GitHub sign-in problem during the push.
- **Fix:** nothing, usually. The next run checks GitHub first, then retries. Fix the
  sign-in if needed (see above). `py -m solsync status` lists it under "Unfinished upload".
- **Verify:** after the next run it shows `uploaded_verified`.

#### Nothing uploads: `daily quota reached`
- **Cause:** today's limit is used up (this is normal), or `daily_limit` is `0`.
- **Check:** `py -m solsync status | Select-Object -First 1` shows `4/4 files used`.
- **Fix:** wait for midnight Manila time, or raise the limit (Dashboard → Settings).
- **Verify:** the next run uploads again.

#### Nothing uploads, and the run says `dry-run (uploads_enabled is false)`
- **Fix:** set `"uploads_enabled": true` in `config.json`.

#### The dashboard doesn't open, or the port is in use
- **Cause:** the browser didn't open by itself, the PowerShell window was closed (which
  stops the dashboard), or another program uses port 8765.
- **Fix:** open **http://127.0.0.1:8765** yourself. If PowerShell showed `WinError 10013`
  or `WinError 10048`, use the dashboard that is already open (for example the desktop app),
  or run `py -m solsync dashboard --port 8766`.
- **Verify:** the Overview page loads.

#### The dashboard is slow
Scans and GitHub refreshes take a while (the page says "usually under two minutes") and
run in the background. The page stays usable meanwhile. A second scan can't start until
the first finishes.

#### The scheduled task didn't run
- **Check:** `Get-ScheduledTaskInfo -TaskName "SolutionSync Daily"` and
  `Get-ScheduledTask -TaskName "SolutionSync Daily"` (State `Disabled` means paused).
- **Causes:** you weren't signed in to Windows, the PC was off or asleep (it catches up 5
  minutes after you sign in or unlock), automation is paused, or the task was never
  created.
- **Fix:** resume it (dashboard or `Enable-ScheduledTask -TaskName "SolutionSync Daily"`),
  or create it again with `install_task.ps1`. If you moved the SolutionSync folder or
  reinstalled Python, run `install_task.ps1` again.
- **Verify:** `LastTaskResult` is `0` after the next run, or check `py -m solsync status`.

#### Exit code `3` / "Another sync run is already in progress"
Two runs tried to start at the same moment (for example the task and a dashboard button).
Only one runs, by design. Nothing to fix.

---

## 11. Your data, privacy and security

**Where your data is stored.** In the SolutionSync folder (or the folder set by
`SOLSYNC_HOME`):

| File or folder | Contains |
|---|---|
| `config.json` | Your settings. No secrets. |
| `state\solsync.db` | Upload history, daily counts, and each solution's status. |
| `state\last_run.json`, `state\last_dry_run.json` | Summary of the last real run and the last dry run. |
| `logs\solsync.log` | Activity log, kept to about 6 files of 1 MB each. |
| `inbox\hackerrank\` | Your HackerRank export (personal data). |

All of it stays after you close the dashboard or restart the PC. `config.json`, `state`,
`logs` and `inbox` are excluded from Git by `.gitignore`, so they cannot be committed by
accident.

**Credentials.** Your Exercism token is stored in Windows Credential Manager under
`SolutionSync-Exercism`, tied to your Windows account. Your GitHub login is stored by Git
Credential Manager. Neither is written to any SolutionSync file or log, and the scheduled
task stores no password.

**What is sent where.**
- **Exercism:** your token, plus requests for your list of solutions and your solution files.
- **GitHub:** the new solution files, pushed by Git under your Git name and email. Dry runs
  may also read your repository's public file list through GitHub's API.
- **HackerRank:** nothing. SolutionSync only reads the export file on your PC.
- Nothing else: no analytics, no other services.

**Keeping secrets out of Git.** Never put tokens or passwords in `config.json`. Uploaded
files are checked for anything that looks like a password or key; matches are held back
as `needs_review`. `.gitignore` also excludes `.env`, `*.token` and `*.secret` files.

**Backup.** Close the dashboard and make sure no run is active, then copy `config.json` and
the `state` folder somewhere safe. **Restore** by copying them back into the SolutionSync
folder. Your solutions themselves are safe on GitHub.

---

## 12. Updating and uninstalling

### Update

1. Close the dashboard (Ctrl + C) and make sure no run is active (`py -m solsync status`).
2. Get the new version:

   ```powershell
   cd C:\Code\SolutionSync
   git pull
   ```

Your settings and history are kept: `config.json`, `state`, `logs` and `inbox` are never
touched by Git. There are no dependencies to update.

**Downloaded SolutionSync before 28 October 2026?** Back then `config.json` was part of the
download, and the next `git pull` removes that copy. Save your settings first, then put
them back after the update:

```powershell
Copy-Item config.json config.mine.json
git restore config.json
git pull
Copy-Item config.mine.json config.json -Force
```

The first line saves your settings, the second undoes your edits to the old downloaded
copy so the update can go ahead, and the last line restores your settings. You only need
this once.

If you moved the folder or reinstalled Python, run `install_task.ps1` again so the task
points to the right place.

### Uninstall

Removing the program does **not** touch your solution repositories, on GitHub or on your PC.

1. Remove the scheduled task:

   ```powershell
   cd C:\Code\SolutionSync
   powershell -ExecutionPolicy Bypass -File scripts\uninstall_task.ps1
   ```

2. Remove the stored Exercism token (optional; also stops SolutionSync from using it):

   ```powershell
   cmdkey /delete:SolutionSync-Exercism
   ```

3. Back up `state\` if you want to keep your upload history, then delete the
   `C:\Code\SolutionSync` folder. **This deletes your settings, history, logs and
   HackerRank export.** Make sure you are deleting the SolutionSync folder, not
   `HackerRank-Problems` or `Exercism-Problems`.

Desktop app: uninstall it from **Settings → Apps** (see [DESKTOP.md](DESKTOP.md)).

---

## 13. FAQ

**Does it solve coding problems for me?**
No. It only uploads solutions you already solved and submitted.

**Will it upload all my existing solutions at once?**
No. At most the daily limit per day (default 4). With many solutions it takes several days.

**Can it overwrite a solution already in my repository?**
No. If something already exists at the destination, the item is skipped and reported.

**Do I need to keep the dashboard open?**
No. The scheduled task works whether the dashboard is open or closed. Your PC must be on
and you must be signed in to Windows.

**Can I change the daily limit?**
Yes: Dashboard → Settings, or `daily_limit` in `config.json` (0 to 20 by default).

**What happens when an upload fails?**
It is kept and retried on the next run, after checking GitHub so it is never uploaded twice.

**Can I use my own repositories and folder names?**
Yes, any GitHub repositories you can push to. The folder layout inside them is fixed
([section 9](#9-where-files-go-in-your-repositories)), except the Exercism track folders,
set by `language_dirs`.

**What if my login expires?**
Exercism: store a new token ([how](#exercism-no-exercism-token-or-exercism-rejected-the-token-http-401403)).
GitHub: Git asks you to sign in again; do it with `git push --dry-run` in a repository.
HackerRank: there is no login. Just download a fresh export.

**Can I use a time zone other than the Philippines?**
Not through a setting. The daily count always uses Asia/Manila time. The scheduled time
uses your PC's clock.

**Does it work on macOS or Linux?**
No. It relies on Windows Credential Manager and Task Scheduler.

**Does it use AI or send my code anywhere else?**
No. Your code goes only to your own GitHub repositories.

---

More: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (Git problems) ·
[DESKTOP.md](DESKTOP.md) (desktop app) · [ARCHITECTURE.md](ARCHITECTURE.md) (how it works inside)

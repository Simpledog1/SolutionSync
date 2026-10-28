"""Load and validate config.json, and handle Philippine (Asia/Manila) time."""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    MANILA = ZoneInfo("Asia/Manila")
except Exception:
    # Windows Python often ships without tz data. Manila is UTC+8 with no daylight
    # saving since 1978, so a fixed offset gives the same calendar day.
    MANILA = timezone(timedelta(hours=8), "Asia/Manila")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FROZEN = bool(getattr(sys, "frozen", False))  # running as the packaged desktop app


def location_file() -> Path:
    """Where the desktop app remembers which data folder to use (one line: a path)."""
    return Path(os.environ.get("APPDATA") or Path.home()) / "SolutionSync" / "data-location.txt"


def data_root() -> Path:
    """The one folder holding config.json, state/, logs/ and inbox/.

    The web dashboard, the desktop app and the scheduled task all resolve it the same
    way, so they share one config, one upload ledger and one daily quota:
    SOLSYNC_HOME, else the saved data-location.txt, else the source folder
    (or %APPDATA%\\SolutionSync for the packaged app, whose install folder is read-only).
    """
    env = os.environ.get("SOLSYNC_HOME", "").strip()
    if env:
        return Path(env)
    try:
        saved = location_file().read_text(encoding="utf-8-sig").strip()
        if saved:
            return Path(saved)
    except OSError:
        pass
    return location_file().parent if FROZEN else PROJECT_ROOT


def manila_now() -> datetime:
    return datetime.now(MANILA)


def manila_day(moment: datetime | None = None) -> str:
    """Philippine calendar date as 'YYYY-MM-DD'. Used for the daily quota."""
    moment = moment or manila_now()
    return moment.astimezone(MANILA).strftime("%Y-%m-%d")


@dataclass
class RepoConfig:
    platform: str
    path: Path
    remote_url: str
    branch: str
    # Maps a language (HackerRank language or Exercism track slug) to the repo's top folder.
    language_dirs: dict[str, str]


@dataclass
class Config:
    root: Path
    daily_limit: int
    uploads_enabled: bool
    repos: dict[str, RepoConfig]
    exercism_api_base: str
    exercism_credential_target: str
    hackerrank_inbox: Path
    max_downloads_per_run: int = 10
    max_daily_limit: int = 20
    state_dir: Path = field(init=False)
    log_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        self.state_dir = self.root / "state"
        self.log_dir = self.root / "logs"


class ConfigError(Exception):
    pass


DEFAULT_LIMIT = 4        # files per Manila day, both platforms combined
DEFAULT_MAX_LIMIT = 20   # safety cap; change "max_daily_limit" in config.json to move it


def validate_limit(value, max_limit: int) -> int:
    """Accept only a whole number from 0 to max_limit (0 = no new uploads)."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError("Daily upload limit must be a whole number (no decimals or text).")
    if value < 0:
        raise ConfigError("Daily upload limit cannot be negative.")
    if value > max_limit:
        raise ConfigError(f"Daily upload limit cannot be more than {max_limit} "
                          "(the safety maximum, 'max_daily_limit' in config.json).")
    return value


def save_daily_limit(value, path: Path | None = None) -> int:
    """Validate and store a new daily limit in config.json, atomically.

    On any error the file is left exactly as it was.
    """
    path = path or data_root() / "config.json"
    raw = json.loads(path.read_text(encoding="utf-8-sig"))  # tolerate Notepad's BOM
    limit = validate_limit(value, raw.get("max_daily_limit", DEFAULT_MAX_LIMIT))
    raw["daily_limit"] = limit
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)  # all-or-nothing: readers see the old file or the new one
    return limit


def load_config(path: Path | None = None, root: Path | None = None) -> Config:
    root = root or data_root()
    path = path or root / "config.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))  # tolerate Notepad's BOM
    except (OSError, ValueError) as exc:
        raise ConfigError(f"Cannot read {path}: {exc}") from exc

    max_limit = raw.get("max_daily_limit", DEFAULT_MAX_LIMIT)
    if not isinstance(max_limit, int) or isinstance(max_limit, bool) or not 1 <= max_limit <= 100:
        raise ConfigError("max_daily_limit must be a whole number from 1 to 100")
    limit = validate_limit(raw.get("daily_limit", DEFAULT_LIMIT), max_limit)

    repos = {}
    for platform in ("hackerrank", "exercism"):
        r = raw.get("repos", {}).get(platform)
        if not r:
            raise ConfigError(f"repos.{platform} is missing")
        repo_path = Path(r["path"])
        if not repo_path.is_absolute():
            repo_path = root / repo_path
        if repo_path.resolve() == root.resolve() or root.resolve() in repo_path.resolve().parents:
            raise ConfigError("Solution repos must live outside the automation project")
        repos[platform] = RepoConfig(
            platform=platform,
            path=repo_path,
            remote_url=r["remote_url"],
            branch=r.get("branch", "main"),
            language_dirs=dict(r.get("language_dirs", {})),
        )

    ex = raw.get("exercism", {})
    hr = raw.get("hackerrank", {})
    inbox = Path(hr.get("inbox", "inbox/hackerrank"))
    return Config(
        root=root,
        daily_limit=limit,
        max_daily_limit=max_limit,
        uploads_enabled=bool(raw.get("uploads_enabled", False)),
        repos=repos,
        exercism_api_base=ex.get("api_base", "https://api.exercism.org").rstrip("/"),
        exercism_credential_target=ex.get("credential_target", "SolutionSync-Exercism"),
        hackerrank_inbox=inbox if inbox.is_absolute() else root / inbox,
        max_downloads_per_run=int(raw.get("max_downloads_per_run", 10)),
    )

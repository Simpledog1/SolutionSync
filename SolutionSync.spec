# PyInstaller recipe for the desktop app. Build with scripts\build_desktop.ps1.
# One folder (not one-file) so it starts fast and antivirus tools don't flag a self-extractor.
from solsync import __version__

a = Analysis(
    ["desktop_app.py"],
    datas=[
        ("solsync/dashboard.html", "solsync"),
        ("solsync/hackerrank_sections.json", "solsync"),
        ("config.example.json", "."),
        ("scripts/install_task.ps1", "scripts"),   # lets desktop-only users schedule the app
    ],
    hiddenimports=["webview.platforms.edgechromium", "webview.platforms.winforms"],
    excludes=["tkinter", "unittest", "pydoc"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="SolutionSync",
    icon="assets/solsync.ico",
    console=False,            # a normal windowed app: no console window
    version_info=None,
)
coll = COLLECT(exe, a.binaries, a.datas, name="SolutionSync")

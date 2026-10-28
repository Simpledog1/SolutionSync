"""Entry point for the packaged desktop app (see scripts/build_desktop.ps1)."""
import sys

from solsync.desktop import main

if __name__ == "__main__":
    sys.exit(main())

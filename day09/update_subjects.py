"""Safe updater for `day09/subjects.txt`.

This script downloads a raw `subjects.txt` from a remote URL and replaces the
local `day09/subjects.txt`. It makes a timestamped backup before overwriting.

By default the script only updates the local file. Use `--commit` to create a
git commit for the change (push is not performed automatically).

Usage examples:
  # update local file only
  python -m day09.update_subjects

  # specify a different source URL and commit the change
  python -m day09.update_subjects \
      --url https://raw.githubusercontent.com/Code-Maven/wis-python-course-2025-10/main/day09/subjects.txt \
      --commit --commit-message "Update subjects.txt from upstream"
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from urllib.request import urlopen


DEFAULT_URL = (
    "https://raw.githubusercontent.com/Code-Maven/wis-python-course-2025-10/"
    "main/day09/subjects.txt"
)


def download(url: str, timeout: int = 15) -> bytes:
    """Download bytes from URL. Try urllib first; if that fails, fall back to
    calling `curl` if available (helps on systems with SSL cert issues).
    """
    try:
        with urlopen(url, timeout=timeout) as r:
            return r.read()
    except Exception:
        # If curl is available, fallback to it
        try:
            out = subprocess.run(["curl", "-sS", "-L", url], capture_output=True, check=True)
            return out.stdout
        except Exception:
            # re-raise the original urllib exception for clarity
            raise


def safe_write(path: str, data: bytes) -> None:
    # write to a temp file then atomically move
    dirn = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=dirn)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        shutil.move(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def backup_file(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    bak = f"{path}.bak.{ts}"
    shutil.copy2(path, bak)
    return bak


def git_commit(path: str, message: str) -> bool:
    try:
        subprocess.run(["git", "add", path], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        return True
    except subprocess.CalledProcessError as exc:
        print("Git commit failed:", exc, file=sys.stderr)
        return False


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Update day09/subjects.txt from remote source")
    p.add_argument("--url", default=DEFAULT_URL, help="Raw URL to download subjects.txt from")
    p.add_argument("--output", default=os.path.join(os.path.dirname(__file__), "subjects.txt"),
                   help="Local output path")
    p.add_argument("--commit", action="store_true", help="Create a git commit for the updated file")
    p.add_argument("--commit-message", default="Update day09/subjects.txt from upstream",
                   help="Commit message when --commit is used")
    p.add_argument("--no-backup", action="store_true", help="Don't create a timestamped backup of the old file")
    args = p.parse_args(argv)

    print(f"Downloading {args.url} ...")
    try:
        data = download(args.url)
    except Exception as exc:
        print("Download failed:", exc, file=sys.stderr)
        return 2

    out = args.output
    # create backup
    if not args.no_backup:
        bak = backup_file(out)
        if bak:
            print(f"Backed up existing file to: {bak}")

    try:
        safe_write(out, data)
        print(f"Wrote {len(data)} bytes to {out}")
    except Exception as exc:
        print("Failed to write output file:", exc, file=sys.stderr)
        return 3

    if args.commit:
        ok = git_commit(out, args.commit_message)
        if ok:
            print("Committed updated file (local commit created).")
        else:
            print("Commit failed. See errors above.")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())

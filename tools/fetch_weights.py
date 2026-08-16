#!/usr/bin/env python3
"""Download the DRLCE network weights.

``AlphaZeroNet_20x256.pt`` is 93 MB. Model weights are build artifacts, not
source, so they are published as a GitHub Release asset rather than committed —
which keeps a clone of this repository under 60 MB.

Usage::

    python tools/fetch_weights.py            # download if missing
    python tools/fetch_weights.py --force    # re-download

Only the standard library is used, so this runs before any dependencies are
installed.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = "Momad-Y/Magnus-Hikaru-Chess-Robots"
TAG = "assets-v1"
FILENAME = "AlphaZeroNet_20x256.pt"
EXPECTED_BYTES = 97_233_326

DEST = Path(__file__).resolve().parent.parent / "hikaru-v2" / "DRLCE" / "weights" / FILENAME
URL = f"https://github.com/{REPO}/releases/download/{TAG}/{FILENAME}"


def _human(n: int) -> str:
    return f"{n / 1_000_000:.1f} MB"


def _progress(done: int, total: int) -> None:
    if not total:
        return
    pct = done * 100 // total
    bar = "#" * (pct // 3)
    sys.stdout.write(f"\r  [{bar:<33}] {pct:3d}%  {_human(done)}/{_human(total)}")
    sys.stdout.flush()


def download() -> int:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    print(f"Fetching {FILENAME} ({_human(EXPECTED_BYTES)})")
    print(f"  from {URL}")
    tmp = DEST.with_suffix(".part")
    try:
        with urllib.request.urlopen(URL) as resp, open(tmp, "wb") as fh:
            total = int(resp.headers.get("Content-Length") or EXPECTED_BYTES)
            done = 0
            while chunk := resp.read(1 << 20):
                fh.write(chunk)
                done += len(chunk)
                _progress(done, total)
        print()
    except urllib.error.HTTPError as exc:
        tmp.unlink(missing_ok=True)
        print(f"\nDownload failed: HTTP {exc.code}", file=sys.stderr)
        print(
            "\nThe release asset may not have been uploaded yet. You can also place\n"
            f"the file manually at:\n  {DEST}",
            file=sys.stderr,
        )
        return 1
    except urllib.error.URLError as exc:
        tmp.unlink(missing_ok=True)
        print(f"\nDownload failed: {exc.reason}", file=sys.stderr)
        return 1

    tmp.replace(DEST)
    size = DEST.stat().st_size
    digest = hashlib.sha256(DEST.read_bytes()).hexdigest()[:16]
    print(f"Saved {DEST}  ({_human(size)}, sha256:{digest}…)")
    if size != EXPECTED_BYTES:
        print(
            f"Warning: expected {EXPECTED_BYTES} bytes but got {size}.",
            file=sys.stderr,
        )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="re-download even if present")
    args = ap.parse_args()

    if DEST.exists() and not args.force:
        print(f"Already present: {DEST} ({_human(DEST.stat().st_size)})")
        print("Use --force to re-download.")
        return 0
    return download()


if __name__ == "__main__":
    raise SystemExit(main())

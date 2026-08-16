"""Locate a Stockfish binary on any platform.

The original projects hardcoded a Windows ``.exe`` path, which made them
unrunnable anywhere else. This resolves the engine at runtime instead.

Resolution order:

1. ``$STOCKFISH_PATH``           explicit override, wins over everything
2. ``stockfish.txt`` next to this file  a local, git-ignored override
3. ``shutil.which("stockfish")`` a system install, the normal case
4. a bundled ``engine/`` directory     for a self-contained checkout

Raises ``EngineNotFound`` with per-OS install instructions if all fail.

This helper is intentionally duplicated in ``hikaru-v2/`` so each version
stays runnable on its own. They are archived projects, not a shared library.
"""

from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path

_HERE = Path(__file__).resolve().parent

_INSTALL_HINT = """\
Stockfish was not found. Install it, or set STOCKFISH_PATH.

  Linux (Debian/Ubuntu)  sudo apt install stockfish
  Linux (Arch)           sudo pacman -S stockfish
  macOS                  brew install stockfish
  Windows                winget install Stockfish.Stockfish
  Any platform           download from https://stockfishchess.org/download/
                         then:  export STOCKFISH_PATH=/full/path/to/stockfish

This project was originally developed against Stockfish 15.1; any recent
release speaks the same UCI protocol and will work.
"""


class EngineNotFound(RuntimeError):
    """Raised when no usable Stockfish binary can be located."""


def _usable(path: Path) -> bool:
    if not path.is_file():
        return False
    return bool(path.stat().st_mode & stat.S_IXUSR) or os.name == "nt"


def find_stockfish() -> str:
    """Return an absolute path to a Stockfish binary, or raise EngineNotFound."""
    override = os.environ.get("STOCKFISH_PATH")
    if override:
        candidate = Path(override).expanduser()
        if _usable(candidate):
            return str(candidate)
        raise EngineNotFound(
            f"STOCKFISH_PATH is set to {override!r} but that is not an "
            f"executable file.\n\n{_INSTALL_HINT}"
        )

    pointer = _HERE / "stockfish.txt"
    if pointer.is_file():
        candidate = Path(pointer.read_text(encoding="utf-8").strip()).expanduser()
        if _usable(candidate):
            return str(candidate)

    on_path = shutil.which("stockfish")
    if on_path:
        return on_path

    # Check both this file's directory and its parent, so the layout works
    # whether the helper sits at the project root (hikaru-v2/) or inside a
    # source directory (magnus-v1/src/, with engine/ at magnus-v1/).
    for base in (_HERE, _HERE.parent):
        for name in ("stockfish", "stockfish.exe"):
            candidate = base / "engine" / name
            if _usable(candidate):
                return str(candidate)

    raise EngineNotFound(_INSTALL_HINT)

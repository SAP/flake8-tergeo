"""Test utility for paths."""

from __future__ import annotations

from pathlib import Path


def mkdir(parent: Path, name: str) -> Path:
    """Create a directory and return it."""
    path = parent / name
    path.mkdir()
    return path


def mkfile(parent: Path, name: str) -> Path:
    """Create a file, touch it and return it."""
    path = parent / name
    path.touch()
    return path

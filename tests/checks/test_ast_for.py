"""Tests for _flake8_tergeo.checks.ast_for."""

from __future__ import annotations

from functools import partial

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture

FTP029 = partial(
    Issue,
    issue_number="FTP029",
    message=(
        "If the index variable in an enumerate loop is not needed, "
        "use a classical for loop instead."
    ),
)


def test_ftp029(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp029.txt", issue_number="FTP029")
    assert results == [FTP029(line=27, column=5)]

"""Tests for _flake8_tergeo.checks.ast_bin_op"""

from __future__ import annotations

from functools import partial

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture

FTP060 = partial(
    Issue,
    issue_number="FTP060",
    message="String literal formatting using percent operator.",
)


def test_ftp060(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp060.txt", issue_number="FTP060")
    assert results == [
        FTP060(line=6, column=1),
        FTP060(line=7, column=1),
        FTP060(line=8, column=1),
    ]

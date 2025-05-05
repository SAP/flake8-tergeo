"""Tests for _flake8_tergeo.checks.ast_except_handler"""

from __future__ import annotations

from functools import partial

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture

FTP046 = partial(
    Issue,
    issue_number="FTP046",
    message="Catching an exception with a direct reraise can be removed.",
)


def test_ftp046(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp046.txt", issue_number="FTP046")
    assert results == [FTP046(line=49, column=1)]

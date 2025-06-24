"""Tests for _flake8_tergeo.ast_assert."""

from __future__ import annotations

from functools import partial

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture

FTP116 = partial(
    Issue,
    issue_number="FTP116",
    message="Found named expression (:=) in assert statement.",
)


def test_ftp116(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp116.txt", issue_number="FTP116")
    assert results == [FTP116(line=9, column=28), FTP116(line=10, column=9)]

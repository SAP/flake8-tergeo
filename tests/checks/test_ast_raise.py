"""Tests for _flake8_tergeo.checks.ast_raise"""

from __future__ import annotations

from functools import partial

from _flake8_tergeo import Issue
from tests.conftest import Flake8Runner

FTP044 = partial(
    Issue, issue_number="FTP044", message="Found exception raised from itself."
)
_FTP047 = partial(
    Issue,
    issue_number="FTP047",
    message=(
        "Raising {exc} is too generic and should be replaced with a more concrete subclass."
    ),
)


def FTP047(*, line: int, column: int, exc: str) -> Issue:  # pylint:disable=invalid-name
    issue = _FTP047(column=column, line=line)
    return issue._replace(message=issue.message.format(exc=exc))


def test_ftp047(runner: Flake8Runner) -> None:
    results = runner(filename="ftp047.txt", issue_number="FTP047")
    assert results == [
        FTP047(line=5, column=1, exc="Exception"),
        FTP047(line=6, column=1, exc="BaseException"),
        FTP047(line=7, column=1, exc="BaseException"),
        FTP047(line=8, column=1, exc="BaseException"),
    ]


def test_ftp044(runner: Flake8Runner) -> None:
    results = runner(filename="ftp044.txt", issue_number="FTP044")
    assert results == [FTP044(line=11, column=1), FTP044(line=12, column=1)]

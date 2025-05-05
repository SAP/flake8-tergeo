"""Tests for _flake8_tergeo.file_tokens"""

from __future__ import annotations

from functools import partial

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture

FTP028 = partial(Issue, issue_number="FTP028", message="Found empty doc comment.")
FTP072 = partial(
    Issue, issue_number="FTP072", message="Found unnecessary string unicode prefix."
)
FTP078 = partial(
    Issue,
    issue_number="FTP078",
    message="Use type annotations instead of type comments.",
)
FTP080 = partial(
    Issue, issue_number="FTP080", message="Implicitly concatenated string literals."
)
FTP091 = partial(
    Issue,
    issue_number="FTP091",
    message="Found backslash that is used for line breaking.",
)


def test_ftp028(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp028.txt", issue_number="FTP028")
    assert results == [FTP028(line=4, column=9), FTP028(line=5, column=1)]


def test_ftp072(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp072.txt", issue_number="FTP072")
    assert results == [
        FTP072(line=7, column=1),
        FTP072(line=8, column=1),
        FTP072(line=10, column=1),
        FTP072(line=11, column=1),
        FTP072(line=13, column=1),
        FTP072(line=14, column=1),
        FTP072(line=16, column=1),
        FTP072(line=17, column=1),
    ]


def test_ftp078(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp078.txt", issue_number="FTP078")
    assert results == [
        FTP078(line=9, column=8),
        FTP078(line=10, column=8),
        FTP078(line=11, column=8),
    ]


def test_ftp080(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp080.txt", issue_number="FTP080")
    assert results == [
        FTP080(line=12, column=9),
        FTP080(line=13, column=9),
    ]


def test_ftp091(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp091.txt", issue_number="FTP091")
    assert results == [
        FTP091(line=41, column=1),
        FTP091(line=45, column=1),
        FTP091(line=47, column=1),
        FTP091(line=51, column=1),
        FTP091(line=52, column=5),
        FTP091(line=56, column=1),
    ]

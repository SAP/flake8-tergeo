"""Tests for _flake8_tergeo.ast_str"""

from __future__ import annotations

from functools import partial

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture

FTP021 = partial(
    Issue,
    issue_number="FTP021",
    message="Found string value which can be replaced with string.ascii_letters",
)
FTP022 = partial(
    Issue,
    issue_number="FTP022",
    message="Found string value which can be replaced with string.ascii_lowercase",
)
FTP023 = partial(
    Issue,
    issue_number="FTP023",
    message="Found string value which can be replaced with string.ascii_uppercase",
)
FTP024 = partial(
    Issue,
    issue_number="FTP024",
    message="Found string value which can be replaced with string.digits",
)


def test_ftp021(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp021.txt", issue_number="FTP021")
    assert results == [FTP021(line=7, column=5), FTP021(line=8, column=5)]


def test_ftp022(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp022.txt", issue_number="FTP022")
    assert results == [FTP022(line=6, column=5), FTP022(line=7, column=5)]


def test_ftp023(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp023.txt", issue_number="FTP023")
    assert results == [FTP023(line=6, column=5), FTP023(line=7, column=5)]


def test_ftp024(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp024.txt", issue_number="FTP024")
    assert results == [FTP024(line=7, column=5), FTP024(line=8, column=5)]

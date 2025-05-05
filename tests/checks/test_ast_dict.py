"""Tests for _flake8_tergeo.checks.ast_dict"""

from __future__ import annotations

from functools import partial

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture

FTP048 = partial(Issue, issue_number="FTP048", message="Found float used as key.")
FTP095 = partial(
    Issue,
    issue_number="FTP095",
    message="Instead of declaring a dictionary and directly unpacking it, "
    "specify the keys and values in the outer dictionary.",
)
FTP101 = partial(
    Issue,
    issue_number="FTP101",
    message="Instead of using the unpack operator for the first/last element in a dict, "
    "use the union operator ('|') instead",
)


def test_ftp048(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp048.txt", issue_number="FTP048")
    assert results == [
        FTP048(line=7, column=6),
        FTP048(line=8, column=12),
        FTP048(line=9, column=6),
        FTP048(line=10, column=6),
        FTP048(line=11, column=6),
    ]


def test_ftp095(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp095.txt", issue_number="FTP095")
    assert results == [
        FTP095(line=8, column=1),
        FTP095(line=9, column=1),
        FTP095(line=10, column=1),
        FTP095(line=11, column=1),
        FTP095(line=12, column=1),
    ]


class TestFTP101:

    def test_python38(self, runner: Flake8RunnerFixture) -> None:
        assert not runner(
            filename="ftp101.txt",
            issue_number="FTP101",
            args=("--ftp-python-version", "3.8.0"),
        )

    def test(self, runner: Flake8RunnerFixture) -> None:
        results = runner(
            filename="ftp101.txt",
            issue_number="FTP101",
            args=("--ftp-python-version", "3.11.0"),
        )
        assert results == [
            FTP101(line=9, column=5),
            FTP101(line=10, column=5),
            FTP101(line=11, column=5),
            FTP101(line=12, column=5),
        ]

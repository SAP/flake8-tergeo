"""Tests for _flake8_tergeo.checks.ast_subscript."""

from __future__ import annotations

from functools import partial

import pytest

from _flake8_tergeo import Issue
from tests.conftest import Flake8RunnerFixture

FTP048 = partial(Issue, issue_number="FTP048", message="Found float used as key.")
FTP106 = partial(
    Issue, issue_number="FTP106", message="Found union with only one element."
)
FTP123 = partial(
    Issue,
    issue_number="FTP123",
    message="The 2nd/3rd argument of a Generator annotation can be omitted if they are None.",
)


def test_ftp048(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp048.txt", issue_number="FTP048")
    assert results == [
        FTP048(line=9, column=1),
        FTP048(line=10, column=1),
        FTP048(line=11, column=1),
        FTP048(line=12, column=1),
    ]


class TestFTP106:
    @pytest.mark.parametrize(
        "imp,union",
        [
            ("import foo", "foo.Union"),
            ("from foo import Union", "Union"),
            ("from foo import typing", "typing.Union"),
        ],
    )
    def test_ignore(self, runner: Flake8RunnerFixture, imp: str, union: str) -> None:
        assert not runner(
            filename="ftp106.txt", issue_number="FTP106", imp=imp, union=union
        )

    @pytest.mark.parametrize(
        "imp,union",
        [
            ("from typing import Union", "Union"),
            ("import typing", "typing.Union"),
        ],
    )
    def test(self, runner: Flake8RunnerFixture, imp: str, union: str) -> None:
        results = runner(
            filename="ftp106.txt", issue_number="FTP106", imp=imp, union=union
        )
        assert results == [FTP106(line=8, column=4), FTP106(line=9, column=4)]


@pytest.mark.parametrize(
    "future,find_by_future",
    [
        ("from __future__ import annotations", True),
        ("from foo import annotations", False),
    ],
)
@pytest.mark.parametrize(
    "imp,find_by_imp,name",
    [
        ("from typing import Generator", True, "Generator"),
        ("import typing", True, "typing.Generator"),
        ("import foo", False, "foo.Generator"),
        ("from foo import Generator", False, "Generator"),
        ("from foo import typing", False, "typing.Generator"),
        ("from collections.abc import Generator", True, "Generator"),
        ("import collections.abc", True, "collections.abc.Generator"),
        ("from collections.other import Generator", False, "Generator"),
    ],
)
@pytest.mark.parametrize(
    "version,find_by_version", [("3.7.0", False), ("3.13.0", True)]
)
def test_ftp123(
    runner: Flake8RunnerFixture,
    future: str,
    find_by_future: bool,
    imp: str,
    find_by_imp: bool,
    name: str,
    version: str,
    find_by_version: bool,
) -> None:
    results = runner(
        filename="ftp123.txt",
        issue_number="FTP123",
        future=future,
        imp=imp,
        name=name,
        args=("--ftp-python-version", version),
    )
    if find_by_imp and (find_by_future or find_by_version):
        assert results == [
            FTP123(line=12, column=8),
            FTP123(line=13, column=9),
            FTP123(line=15, column=4),
            FTP123(line=16, column=4),
            FTP123(line=17, column=14),
        ] + ([FTP123(line=19, column=5)] if find_by_version else [])
    elif find_by_imp:
        assert results == [FTP123(line=12, column=8), FTP123(line=13, column=9)]
    else:
        assert not results

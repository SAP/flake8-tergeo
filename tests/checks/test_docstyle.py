"""Tests for _flake8_tergeo.checks.docstyle."""

from __future__ import annotations

from functools import partial
from pathlib import Path

import pytest

from _flake8_tergeo.flake8_types import Issue
from tests.conftest import Flake8RunnerFixture
from tests.path_util import mkdir, mkfile

FTP300 = partial(
    Issue, issue_number="FTP300", message="Missing docstring in public package."
)
FTP301 = partial(
    Issue, issue_number="FTP301", message="Missing docstring in public class."
)
FTP302 = partial(
    Issue, issue_number="FTP302", message="Missing docstring in public method."
)
FTP303 = partial(
    Issue, issue_number="FTP303", message="Missing docstring in public function."
)
FTP304 = partial(
    Issue, issue_number="FTP304", message="Missing docstring in magic method."
)
FTP305 = partial(Issue, issue_number="FTP305", message="Missing docstring in __init__.")
FTP306 = partial(
    Issue, issue_number="FTP306", message="Missing docstring in overridden method."
)
FTP307 = partial(
    Issue, issue_number="FTP307", message="Missing docstring in public module."
)
FTP308 = partial(Issue, issue_number="FTP308", message="Empty docstring.")
FTP309 = partial(
    Issue,
    issue_number="FTP309",
    message="The summary should be placed in the first line.",
)
FTP310 = partial(
    Issue,
    issue_number="FTP310",
    message="There should be an empty line after the summary.",
)
FTP311 = partial(
    Issue, issue_number="FTP311", message="The summary should end with a period."
)
FTP312 = partial(
    Issue,
    issue_number="FTP312",
    message="Functions decorated with @overload should not have a docstring.",
)
FTP313 = partial(
    Issue, issue_number="FTP313", message="Missing docstring in magic function."
)
FTP314 = partial(
    Issue,
    issue_number="FTP314",
    message="A function/method docstring should not be followed by a newline.",
)
FTP315 = partial(
    Issue,
    issue_number="FTP315",
    message="A multiline docstring should end with a line break.",
)
FTP316 = partial(
    Issue,
    issue_number="FTP316",
    message="The summary should start with an uppercase letter or number.",
)
FTP317 = partial(
    Issue,
    issue_number="FTP317",
    message="A docstring should use triple quotes.",
)


class TestFTP300:

    @pytest.mark.parametrize(
        "is_public,has_docstring",
        [
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        ],
    )
    def test(
        self,
        runner: Flake8RunnerFixture,
        tmp_path: Path,
        is_public: bool,
        has_docstring: bool,
    ) -> None:
        package_name = "package" if is_public else "_package"
        package = mkdir(tmp_path, package_name)
        file = mkfile(package, "__init__.py")
        if has_docstring:
            file.write_text('"""This is a docstring."""\n')

        results = runner(filename=str(file), issue_number="FTP300")
        if is_public and not has_docstring:
            assert results == [FTP300(line=1, column=1)]
        else:
            assert not results

    def test_non_init_file_is_ignored(
        self, runner: Flake8RunnerFixture, tmp_path: Path
    ) -> None:
        file = mkfile(tmp_path, "non_init_file.py")
        results = runner(filename=str(file), issue_number="FTP300")
        assert not results


def test_ftp301(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp301.txt", issue_number="FTP301")
    assert results == [
        FTP301(line=15, column=1),
        FTP301(line=18, column=1),
        FTP301(line=19, column=5),
        FTP301(line=23, column=5),
    ]


def test_ftp302(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp302.txt", issue_number="FTP302")
    assert results == [FTP302(line=21, column=5)]


def test_ftp303(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp303.txt", issue_number="FTP303")
    assert results == [FTP303(line=21, column=1), FTP303(line=25, column=5)]


def test_ftp304(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp304.txt", issue_number="FTP304")
    assert results == [FTP304(line=20, column=5)]


def test_ftp305(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp305.txt", issue_number="FTP305")
    assert results == [FTP305(line=17, column=5)]


@pytest.mark.parametrize(
    "imp,decorator,found",
    [
        ("import typing", "typing.override", True),
        ("from typing import override", "override", True),
        ("import typing", "override", False),
        ("from typing2 import override", "override", False),
    ],
)
def test_ftp306(
    runner: Flake8RunnerFixture, imp: str, decorator: str, found: bool
) -> None:
    results = runner(
        filename="ftp306.txt", issue_number="FTP306", imp=imp, decorator=decorator
    )
    if found:
        assert results == [FTP306(line=19, column=5)]
    else:
        assert not results


@pytest.mark.parametrize("has_docstring", [True, False])
def test_ftp307(
    runner: Flake8RunnerFixture, tmp_path: Path, has_docstring: bool
) -> None:
    file = mkfile(tmp_path, "dummy.py")
    if has_docstring:
        file.write_text('"""This is a docstring."""\n')
    results = runner(filename=str(file), issue_number="FTP307")
    if has_docstring:
        assert not results
    else:
        assert results == [FTP307(line=1, column=1)]


def test_ftp308(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp308.txt", issue_number="FTP308")
    assert results == [FTP308(line=9, column=5), FTP308(line=12, column=5)]


def test_ftp309(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp309.txt", issue_number="FTP309")
    assert results == [FTP309(line=13, column=5), FTP309(line=18, column=5)]


def test_ftp310(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp310.txt", issue_number="FTP310")
    assert results == [FTP310(line=14, column=1)]


def test_ftp311(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp311.txt", issue_number="FTP311")
    assert results == [
        FTP311(line=9, column=5),
        FTP311(line=12, column=5),
        FTP311(line=15, column=5),
    ]


@pytest.mark.parametrize(
    "imp,decorator,found",
    [
        ("import typing", "typing.overload", True),
        ("from typing import overload", "overload", True),
        ("import typing", "overload", False),
        ("from typing2 import overload", "overload", False),
    ],
)
def test_ftp312(
    runner: Flake8RunnerFixture, imp: str, decorator: str, found: bool
) -> None:
    results = runner(
        filename="ftp312.txt", issue_number="FTP312", imp=imp, decorator=decorator
    )
    if found:
        assert results == [FTP312(line=13, column=5)]
    else:
        assert not results


def test_ftp313(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp313.txt", issue_number="FTP313")
    assert results == [FTP313(line=8, column=1)]


def test_ftp314(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp314.txt", issue_number="FTP314")
    assert results == [
        FTP314(line=45, column=1),
        FTP314(line=50, column=1),
        FTP314(line=59, column=1),
    ]


def test_ftp315(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp315.txt", issue_number="FTP315")
    assert results == [FTP315(line=21, column=21)]


@pytest.mark.parametrize(
    "ignores,expected",
    [
        (["e.g."], []),
        ([], [FTP316(line=26, column=5)]),
    ],
)
def test_ftp316(
    runner: Flake8RunnerFixture, ignores: list[str], expected: list[Issue]
) -> None:
    results = runner(
        filename="ftp316.txt",
        issue_number="FTP316",
        args=(f"--ftp-docstyle-lowercase-words={','.join(ignores)}",),
    )
    assert results == [FTP316(line=18, column=5), FTP316(line=22, column=5), *expected]


def test_ftp317(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp317.txt", issue_number="FTP317")
    assert results == [
        FTP317(line=15, column=5),
        FTP317(line=17, column=5),
        FTP317(line=19, column=5),
    ]

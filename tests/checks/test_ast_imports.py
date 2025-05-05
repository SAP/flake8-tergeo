"""Tests for _flake8_tergeo.checks.ast_imports"""

from __future__ import annotations

import ast
from functools import partial
from typing import cast

from _flake8_tergeo import Issue
from _flake8_tergeo.checks import ast_import
from tests.conftest import Flake8RunnerFixture

FTP057 = partial(
    Issue, issue_number="FTP057", message="Replace relative imports with absolute ones."
)
FTP058 = partial(
    Issue, issue_number="FTP058", message="Found unnecessary import alias."
)
FTP087 = partial(
    Issue,
    issue_number="FTP087",
    message="Found import of deprecated module xml.etree.cElementTree.",
)
_FTP026 = partial(
    Issue, issue_number="FTP026", message="Found import of easteregg module {module}"
)
_FTP089 = partial(
    Issue,
    issue_number="FTP089",
    message="Found OSError alias {module}.error; use OSError instead.",
)
_FTP030 = partial(
    Issue, issue_number="FTP030", message="Found unnecessary future import {future}."
)
_FTP027 = partial(
    Issue, issue_number="FTP027", message="Found easteregg future import {future}."
)
_FTP001 = partial(
    Issue, issue_number="FTP001", message="Found debugging module {module}."
)
FTP015 = partial(
    Issue,
    issue_number="FTP015",
    message=(
        "Found import of pkg_resources "
        "which should be replaced with a proper alternative of importlib.*"
    ),
)


def FTP001(  # pylint:disable=invalid-name
    *, line: int, column: int, module: str
) -> Issue:
    issue = _FTP001(line=line, column=column)
    return issue._replace(message=issue.message.format(module=module))


def FTP026(  # pylint:disable=invalid-name
    *, line: int, column: int, module: str
) -> Issue:
    issue = _FTP026(line=line, column=column)
    return issue._replace(message=issue.message.format(module=module))


def FTP089(  # pylint:disable=invalid-name
    *, line: int, column: int, module: str
) -> Issue:
    issue = _FTP089(line=line, column=column)
    return issue._replace(message=issue.message.format(module=module))


def FTP027(  # pylint:disable=invalid-name
    *, line: int, column: int, future: str, issue_number: str = "FTP027"
) -> Issue:
    issue = _FTP027(line=line, column=column, issue_number=issue_number)
    return issue._replace(message=issue.message.format(future=future))


def FTP030(  # pylint:disable=invalid-name
    *, line: int, column: int, future: str
) -> Issue:
    issue = _FTP030(line=line, column=column)
    return issue._replace(message=issue.message.format(future=future))


def test_ftp001(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp001.txt", issue_number="FTP001")
    assert results == [
        FTP001(line=11, column=1, module="pdb"),
        FTP001(line=12, column=1, module="ipdb"),
        FTP001(line=13, column=1, module="pudb"),
        FTP001(line=14, column=1, module="debug"),
        FTP001(line=15, column=1, module="pdbpp"),
        FTP001(line=16, column=1, module="wdb"),
        FTP001(line=17, column=1, module="pdb"),
        FTP001(line=18, column=1, module="pdb"),
    ]


def test_ftp015(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp015.txt", issue_number="FTP015")
    assert results == [FTP015(line=8, column=1), FTP015(line=9, column=1)]


def test_ftp030(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp030.txt", issue_number="FTP030")
    assert results == [
        FTP030(line=2, column=1, future="nested_scopes"),
        FTP030(line=3, column=1, future="generators"),
        FTP030(line=4, column=1, future="division"),
        FTP030(line=5, column=1, future="absolute_import"),
        FTP030(line=6, column=1, future="with_statement"),
        FTP030(line=7, column=1, future="print_function"),
        FTP030(line=8, column=1, future="unicode_literals"),
        FTP030(line=9, column=1, future="generator_stop"),
    ]


def test_ftp087(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp087.txt", issue_number="FTP087")
    assert results == [
        FTP087(line=11, column=1),
        FTP087(line=12, column=1),
    ]


class TestFTP027:
    def test_ftp027(self, runner: Flake8RunnerFixture) -> None:
        results = runner(filename="ftp027.txt", issue_number="FTP027")
        assert results == [FTP027(line=2, column=1, future="barry_as_FLUFL")]

    def test_ftp027_braces(self) -> None:
        # since braces leads to a syntax error and we have pydocstring running
        # the test would fail if we would use the Flake8RunnerFixture
        tree = ast.parse("from __future__ import braces")
        import_ = cast(ast.ImportFrom, tree.body[0])
        results = list(ast_import.check_imports(import_))
        assert results == [
            FTP027(line=1, column=0, future="braces", issue_number="027")
        ]


def test_ftp026(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp026.txt", issue_number="FTP026")
    assert results == [
        FTP026(line=20, column=1, module="this"),
        FTP026(line=21, column=1, module="antigravity"),
        FTP026(line=22, column=1, module="__hello__"),
        FTP026(line=23, column=1, module="__phello__"),
    ]


def test_ftp089(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp089.txt", issue_number="FTP089")
    assert results == [
        FTP089(line=6, column=1, module="socket"),
        FTP089(line=7, column=1, module="select"),
    ]


def test_ftp057(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp057.txt", issue_number="FTP057")
    assert results == [FTP057(line=7, column=1), FTP057(line=8, column=1)]


def test_ftp058(runner: Flake8RunnerFixture) -> None:
    results = runner(filename="ftp058.txt", issue_number="FTP058")
    assert results == [
        FTP058(line=8, column=1),
        FTP058(line=9, column=1),
        FTP058(line=10, column=1),
        FTP058(line=11, column=1),
    ]

"""Tests for _flake8_tergeo.checks.ast_imports"""

from __future__ import annotations

import sys
from functools import partial

import pytest

from _flake8_tergeo import Issue
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
_FTP133 = partial(
    Issue,
    issue_number="FTP133",
    message=(
        "Using the compression namespace is recommended. "
        "Replace the imported module with compression.{module}"
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


def FTP133(  # pylint:disable=invalid-name
    *, line: int, column: int, module: str
) -> Issue:
    issue = _FTP133(line=line, column=column)
    return issue._replace(message=issue.message.format(module=module))


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


@pytest.mark.parametrize(
    "version,find_annotations", [("3.7.0", False), ("3.14.1", True)]
)
def test_ftp030(
    runner: Flake8RunnerFixture, version: str, find_annotations: bool
) -> None:
    results = runner(
        filename="ftp030.txt",
        issue_number="FTP030",
        args=("--ftp-python-version", version),
    )
    assert results == [
        FTP030(line=2, column=1, future="nested_scopes"),
        FTP030(line=3, column=1, future="generators"),
        FTP030(line=4, column=1, future="division"),
        FTP030(line=5, column=1, future="absolute_import"),
        FTP030(line=6, column=1, future="with_statement"),
        FTP030(line=7, column=1, future="print_function"),
        FTP030(line=8, column=1, future="unicode_literals"),
        FTP030(line=9, column=1, future="generator_stop"),
        *(
            [FTP030(line=12, column=1, future="annotations")]
            if find_annotations
            else []
        ),
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

    @pytest.mark.skipif(
        sys.version_info >= (3, 14), reason="AST parsing now throws a SyntaxError"
    )
    def test_ftp027_braces(self, runner: Flake8RunnerFixture) -> None:
        results = runner(filename="ftp027_braces.txt", issue_number="FTP027")
        assert results == [FTP027(line=1, column=1, future="braces")]


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


@pytest.mark.parametrize(
    "python_version,find_by_version", [("3.7.1", False), ("3.14.1", True)]
)
@pytest.mark.parametrize(
    "imp,find_by_imp,module",
    [
        ("import bz2", True, "bz2"),
        ("import gzip", True, "gzip"),
        ("import lzma", True, "lzma"),
        ("import zlib", True, "zlib"),
        ("from zlib import some", True, "zlib"),
        ("import zlib2", False, None),
        ("from compression.gzip import some", False, None),
        ("import compression.lzma", False, None),
    ],
)
def test_ftp133(
    runner: Flake8RunnerFixture,
    python_version: str,
    find_by_version: bool,
    imp: str,
    find_by_imp: bool,
    module: str,
) -> None:
    results = runner(
        filename="ftp133.txt",
        issue_number="FTP133",
        imp=imp,
        args=("--ftp-python-version", python_version),
    )
    if find_by_version and find_by_imp:
        assert results == [FTP133(line=1, column=1, module=module)]
    else:
        assert not results

"""Fixtures used by flake8 tests."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import tokenize
from pathlib import Path
from typing import Any, Iterable

import pytest
from pytest_fixture_classes import fixture_class
from pytest_mock import MockerFixture
from typing_extensions import override

from _flake8_tergeo import BaseWrapperChecker, Flake8TergeoPlugin, base, registry
from _flake8_tergeo.flake8_types import Issue, IssueGenerator, OptionManager
from _flake8_tergeo.interfaces import AbstractChecker
from tests.util import LenientIssue


@pytest.fixture(autouse=True)
def auto_patch_constants(mocker: MockerFixture) -> None:
    mocker.patch.object(base, "_PLUGIN", None)
    mocker.patch.object(Flake8TergeoPlugin, "_parse_options_option_manager", None)
    mocker.patch.object(Flake8TergeoPlugin, "_parse_options_options", None)
    mocker.patch.object(Flake8TergeoPlugin, "_parse_options_args", None)
    mocker.patch.object(Flake8TergeoPlugin, "_setup_performed", False)


@pytest.fixture(autouse=True)
def auto_patch_registry(mocker: MockerFixture) -> None:
    mocker.patch.dict(registry.AST_REGISTRY, clear=True)
    mocker.patch.object(registry, "TOKEN_REGISTRY", [])
    mocker.patch.object(registry, "ADD_OPTIONS_REGISTRY", [])
    mocker.patch.object(registry, "PARSE_OPTIONS_REGISTRY", [])


def create_plugin(mocker: MockerFixture) -> Flake8TergeoPlugin:
    return Flake8TergeoPlugin(
        tree=ast.parse(""),
        filename="foo",
        max_line_length=100,
        file_tokens=[mocker.Mock(spec=tokenize.TokenInfo)],
        lines=["line1", "line2"],
    )


@pytest.fixture
def plugin(mocker: MockerFixture) -> Flake8TergeoPlugin:
    return create_plugin(mocker)


class _BasicChecker(AbstractChecker):
    prefix = "X"
    args = None
    parse_options_args: list[Any] = []

    def __init__(self, tree: ast.AST) -> None:
        pass

    @override
    def check(self) -> IssueGenerator:
        yield Issue(1, 2, "002", "Dummy")


@pytest.fixture
def basic_checker(mocker: MockerFixture) -> type[AbstractChecker]:
    class _Checker(_BasicChecker):
        pass

    mocker.patch.object(base, "_get_concrete_classes", return_value=[_Checker])
    return _Checker


@pytest.fixture
def checker_with_options(mocker: MockerFixture) -> None:
    class _CheckerWithOptions(AbstractChecker):

        @staticmethod
        def add_options(option_manager: OptionManager) -> None:
            option_manager.extend_default_ignore(["1", "2"])

    mocker.patch.object(
        base, "_get_concrete_classes", return_value=[_CheckerWithOptions]
    )


@pytest.fixture
def checker_with_parse(mocker: MockerFixture) -> type[AbstractChecker]:
    class _Checker(_BasicChecker):
        @classmethod
        def parse_options(cls, options: argparse.Namespace) -> None:
            cls.parse_options_args = [options]

    mocker.patch.object(base, "_get_concrete_classes", return_value=[_Checker])
    return _Checker


@pytest.fixture
def checker_with_complex_parse(mocker: MockerFixture) -> type[AbstractChecker]:
    class _Checker(_BasicChecker):
        @classmethod
        def parse_options(
            cls,
            option_manager: OptionManager,
            options: argparse.Namespace,
            args: list[str],
        ) -> None:
            cls.parse_options_args = [option_manager, options, args]

    mocker.patch.object(base, "_get_concrete_classes", return_value=[_Checker])
    return _Checker


@pytest.fixture
def invalid_checker(mocker: MockerFixture) -> None:
    class _Checker(AbstractChecker):
        def __init__(self, invalid: Any) -> None:
            pytest.fail("Should not be called")

        @override
        def check(self) -> IssueGenerator:
            pytest.fail("Should not be called")

    mocker.patch.object(base, "_get_concrete_classes", return_value=[_Checker])


@pytest.fixture
def checker_wrapper_with_options(mocker: MockerFixture) -> None:
    class _PluginWithOptions:

        @staticmethod
        def add_options(option_manager: OptionManager) -> None:
            option_manager.extend_default_ignore(["OLD01", "OLD06"])

    class _WrapperChecker(BaseWrapperChecker):
        checker_class = _PluginWithOptions
        old_prefix = "OLD"
        prefix = "N"

    mocker.patch.object(base, "_get_concrete_classes", return_value=[_WrapperChecker])


@pytest.fixture
def checker_with_disable(mocker: MockerFixture) -> None:
    class _Checker(AbstractChecker):
        disabled = ["001"]
        prefix = "F"

        @override
        def check(self) -> IssueGenerator:
            yield Issue(1, 2, "001", "Dummy")
            yield Issue(1, 2, "002", "Dummy")

    mocker.patch.object(base, "_get_concrete_classes", return_value=[_Checker])


@fixture_class(name="runner")
class Flake8RunnerFixture:
    datadir: Path
    tmp_path: Path

    def __call__(
        self,
        filename: str,
        issue_number: str,
        args: tuple[str, ...] = (),
        **kwargs: str,
    ) -> Iterable[Issue | LenientIssue]:
        content = (self.datadir / filename).read_text(encoding="utf-8")
        if kwargs:
            content = content.format(**kwargs)

        file = self.tmp_path / filename
        file = file.with_suffix(".py")
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")
        return run_tests(path=file, issue_number=issue_number, args=args)


def run_tests(path: Path, issue_number: str, args: tuple[str, ...]) -> list[Issue]:
    process = subprocess.run(  # pylint: disable=subprocess-run-check
        [
            "python",
            "-m",
            "flake8",
            "--isolated",
            "--enable-extensions",
            "FT",
            "--format",
            "json",
            "--select",
            # E999 reports syntax errors and should always be reported
            f"{issue_number},E999",
            str(path),
            *args,
        ],
        capture_output=True,
        text=True,
    )
    try:
        result = json.loads(process.stdout)
    except json.JSONDecodeError:
        print(process.stdout, process.stderr)  # noqa: FTP050
        pytest.fail("Failed to parse flake8 json")
    return [
        Issue(
            column=issue["column_number"],
            line=issue["line_number"],
            issue_number=issue["code"],
            message=issue["text"],
        )
        for issue in result[str(path)]
    ]

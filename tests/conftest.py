"""Fixtures used by flake8 tests."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import tokenize
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture
from typing_extensions import Protocol, override

from _flake8_tergeo import BaseWrapperChecker, Flake8TergeoPlugin, base, registry
from _flake8_tergeo.flake8_types import Issue, IssueGenerator, OptionManager
from _flake8_tergeo.interfaces import AbstractChecker


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


@pytest.fixture
def no_checker(mocker: MockerFixture) -> None:
    mocker.patch.object(base, "_get_concrete_classes", return_value=[])


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
        def __init__(self) -> None:
            pass

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
            pass

        @override
        def check(self) -> IssueGenerator:
            yield from []

    mocker.patch.object(base, "_get_concrete_classes", return_value=[_Checker])


@pytest.fixture
def checker_wrapper_with_options(mocker: MockerFixture) -> None:
    class _PluginWithOptions:
        @staticmethod
        def run() -> Iterator[None]:
            yield None

        @staticmethod
        def add_options(option_manager: OptionManager) -> None:
            option_manager.extend_default_ignore(["OLD01", "OLD06"])

    class _WrapperChecker(BaseWrapperChecker):
        checker_class = _PluginWithOptions
        old_prefix = "OLD"
        prefix = "N"

        def __init__(self) -> None:
            super().__init__(_PluginWithOptions())

        @override
        def check(self) -> IssueGenerator:
            yield from super().check()

    mocker.patch.object(base, "_get_concrete_classes", return_value=[_WrapperChecker])


@pytest.fixture
def checker_with_disable(mocker: MockerFixture) -> None:
    class _Checker(AbstractChecker):
        disabled = ["001"]
        prefix = "F"

        def __init__(self) -> None:
            pass

        @override
        def check(self) -> IssueGenerator:
            yield Issue(1, 2, "001", "Dummy")
            yield Issue(1, 2, "002", "Dummy")

    mocker.patch.object(base, "_get_concrete_classes", return_value=[_Checker])


class Flake8Runner(Protocol):
    def __call__(
        self,
        filename: str,
        issue_number: str,
        args: tuple[str, ...] = ...,
        **kwargs: str,
    ) -> list[Issue]: ...


@pytest.fixture
def runner(datadir: Path, tmp_path: Path) -> Flake8Runner:
    def _inner(
        filename: str, issue_number: str, args: tuple[str, ...] = (), **kwargs: str
    ) -> list[Issue]:
        content = (datadir / filename).read_text(encoding="utf-8")
        if kwargs:
            content = content.format(**kwargs)

        file = tmp_path / filename
        file = file.with_suffix(".py")
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")
        return run_tests(path=file, issue_number=issue_number, args=args)

    return _inner


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

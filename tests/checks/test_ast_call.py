"""Tests for _flake8_tergeo.checks.ast_call"""

from __future__ import annotations

from functools import partial

import pytest

from _flake8_tergeo import Issue, ast_call
from tests.conftest import Flake8Runner

FTP081 = partial(
    Issue, issue_number="FTP081", message="Missing onerror keyword in os.walk call."
)
FTP014 = partial(
    Issue,
    issue_number="FTP014",
    message="Call of urlparse should be replaced with urlsplit.",
)
FTP098 = partial(
    Issue,
    issue_number="FTP098",
    message="Found usage of multiprocessing.set_start_method. "
    "Use a multiprocessing Context instead.",
)
FTP065 = partial(
    Issue,
    issue_number="FTP065",
    message="Use typing.NamedTuple instead of collections.namedtuple.",
)
FTP068 = partial(
    Issue,
    issue_number="FTP068",
    message="Replace 'stdout=PIPE and stderr=PIPE' with 'capture_output=True'.",
)
FTP075 = partial(
    Issue,
    issue_number="FTP075",
    message="Replace 'universal_newlines' with 'text'.",
)
FTP017 = partial(
    Issue,
    issue_number="FTP017",
    message="Extend typing.Namedtuple instead of calling it.",
)
FTP018 = partial(
    Issue,
    issue_number="FTP018",
    message="Extend typing.TypedDict instead of calling it.",
)
FTP003 = partial(
    Issue,
    issue_number="FTP003",
    message=(
        "Found usage/import of datetime.utcnow. Consider to use datetime.now(tz=)."
    ),
)
FTP092 = partial(
    Issue,
    issue_number="FTP092",
    message="Remove 0 as starting point in range(), as it starts at 0 by default.",
)
FTP007 = partial(
    Issue,
    issue_number="FTP007",
    message=(
        "Found usage/import of datetime.utcfromtimestamp. "
        "Consider to use datetime.fromtimestamp(tz=)."
    ),
)
_FTP073 = partial(Issue, issue_number="FTP073")
FTP061 = partial(
    Issue,
    issue_number="FTP061",
    message="String literal formatting using format method.",
)
FTP062 = partial(
    Issue, issue_number="FTP062", message="String formatting with str.format."
)
_FTP045 = partial(Issue, issue_number="FTP045", message="Found bad call to {func}.")
FTP002 = partial(
    Issue, issue_number="FTP002", message="Found debugging builtin breakpoint."
)
FTP038 = partial(
    Issue, issue_number="FTP038", message="Instead of float('NaN') use math.nan."
)
FTP025 = partial(
    Issue,
    issue_number="FTP025",
    message=(
        "Calling isinstance with a one-element tuple can be simplified. "
        "Instead of a tuple, just use the element directly."
    ),
)
FTP063 = partial(
    Issue,
    issue_number="FTP063",
    message=(
        "Found usage/import of contextlib.wraps. This is a not a re-exported import. "
        "Use the original functools.wraps instead."
    ),
)
FTP070 = partial(
    Issue,
    issue_number="FTP070",
    message="Use `super()` instead of `super(__class__, self)`.",
)
FTP083 = partial(
    Issue, issue_number="FTP083", message="Found unnecessary use of str() on a constant"
)
FTP084 = partial(
    Issue, issue_number="FTP084", message="Found unnecessary use of int() on a constant"
)
FTP085 = partial(
    Issue,
    issue_number="FTP085",
    message="Found unnecessary use of float() on a constant",
)
FTP086 = partial(
    Issue,
    issue_number="FTP086",
    message="Found unnecessary use of bool() on a constant",
)
FTP088 = partial(
    Issue,
    issue_number="FTP088",
    message="Found unnecessary use of io.open; use open instead.",
)
FTP050 = partial(Issue, issue_number="FTP050", message="Found print statement.")
FTP051 = partial(
    Issue,
    issue_number="FTP051",
    message="Found pprint.pprint statement which prints on stdout.",
)
FTP052 = partial(
    Issue,
    issue_number="FTP052",
    message="Found pprint.pp statement which prints on stdout.",
)
FTP053 = partial(
    Issue,
    issue_number="FTP053",
    message="Found pprint.PrettyPrinter statement which prints on stdout.",
)
FTP200 = partial(
    Issue,
    issue_number="FTP200",
    message="Instead of using abort raise the appropriate exception directly.",
)
FTP059 = partial(
    Issue,
    issue_number="FTP059",
    message=(
        "Using starred expression on a constant structure is pointless. "
        "Rewrite the code to be flat."
    ),
)
FTP100 = partial(
    Issue,
    issue_number="FTP100",
    message="Calling print with an empty string can be simplified to 'print()'.",
)
FTP102 = partial(
    Issue,
    issue_number="FTP102",
    message="Calling the path constructor with '.' can be simplified to 'Path()'.",
)
FTP109 = partial(
    Issue,
    issue_number="FTP109",
    message="Found unnecessary use of bytes() on a constant",
)
FTP110 = partial(
    Issue,
    issue_number="FTP110",
    message='Replace str() with the constant <""> directly.',
)
FTP111 = partial(
    Issue,
    issue_number="FTP111",
    message="Replace int() with the constant <0> directly.",
)
FTP112 = partial(
    Issue,
    issue_number="FTP112",
    message="Replace float() with the constant <0.0> directly.",
)
FTP113 = partial(
    Issue,
    issue_number="FTP113",
    message="Replace bool() with the constant <False> directly.",
)
FTP114 = partial(
    Issue,
    issue_number="FTP114",
    message='Replace bytes() with the constant <b""> directly.',
)
FTP117 = partial(
    Issue,
    issue_number="FTP117",
    message="The outer function is already decorated with 'deprecated'. "
    "Remove the warnings.warn call to avoid duplicate warnings.",
)
FTP118 = partial(
    Issue,
    issue_number="FTP118",
    message="Consider using the 'deprecated' decorator instead of warnings.warn.",
)
_FTP121 = partial(
    Issue,
    issue_number="FTP121",
    message="Function {func} should be replaced with function of the subprocess module.",
)
FTP127 = partial(
    Issue,
    issue_number="FTP127",
    message="Use the new generic syntax instead of TypeVar.",
)


def FTP073(  # pylint:disable=invalid-name
    *, line: int, column: int, message: str
) -> Issue:
    return _FTP073(line=line, column=column, message=message)


def FTP045(  # pylint:disable=invalid-name
    *, line: int, column: int, func: str
) -> Issue:
    issue = _FTP045(line=line, column=column)
    return issue._replace(message=issue.message.format(func=func))


def FTP121(  # pylint:disable=invalid-name
    *, line: int, column: int, func: str
) -> Issue:
    issue = _FTP121(line=line, column=column)
    return issue._replace(message=issue.message.format(func=func))


class TestFTP081:
    def test_ftp081_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp081_ignore.txt", issue_number="FTP081")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("import os", "os.walk"),
            ("from os import walk", "walk"),
        ],
    )
    def test_ftp081(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp081.txt", issue_number="FTP081", imp=imp, func=func
        )
        assert results == [FTP081(line=4, column=1)]


class TestFTP014:
    def test_ftp014_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp014_ignore.txt", issue_number="FTP014")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("import urllib.parse", "urllib.parse.urlparse"),
            ("import urllib", "urllib.parse.urlparse"),
            ("from urllib import parse", "parse.urlparse"),
            ("from urllib.parse import urlparse", "urlparse"),
        ],
    )
    def test_ftp014(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp014.txt", issue_number="FTP014", imp=imp, func=func
        )
        assert results == [FTP014(line=3, column=1)]


class TestFTP098:
    def test_ftp098_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp098_ignore.txt", issue_number="FTP098")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("from multiprocessing import set_start_method", "set_start_method"),
            ("import multiprocessing", "multiprocessing.set_start_method"),
        ],
    )
    def test_ftp098(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp098.txt", issue_number="FTP098", imp=imp, func=func
        )
        assert results == [FTP098(line=3, column=1)]


class TestFTP065:
    def test_ftp065_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp065_ignore.txt", issue_number="FTP065")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("from collections import namedtuple", "namedtuple"),
            ("import collections", "collections.namedtuple"),
        ],
    )
    def test_ftp065(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp065.txt", issue_number="FTP065", imp=imp, func=func
        )
        assert results == [FTP065(line=3, column=7)]


class TestFTP068:
    @pytest.mark.parametrize("filename", ["ftp068_ignore1.txt", "ftp068_ignore2.txt"])
    def test_ftp068_ignore(self, runner: Flake8Runner, filename: str) -> None:
        assert not runner(filename=filename, issue_number="FTP068")

    @pytest.mark.parametrize(
        "imp,func,pipe",
        [
            ("from subprocess import run, PIPE", "run", "PIPE"),
            ("import subprocess", "subprocess.run", "subprocess.PIPE"),
        ],
    )
    def test_ftp068(self, runner: Flake8Runner, imp: str, func: str, pipe: str) -> None:
        results = runner(
            filename="ftp068.txt", issue_number="FTP068", imp=imp, func=func, pipe=pipe
        )
        assert results == [FTP068(line=8, column=1)]


class TestFTP003:
    def test_ftp003_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp003_ignore.txt", issue_number="FTP003")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("from datetime import datetime", "datetime.utcnow()"),
            ("import datetime", "datetime.datetime.utcnow()"),
            ("from datetime.datetime import utcnow", "utcnow()"),
        ],
    )
    def test_ftp003(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp003.txt", issue_number="FTP003", imp=imp, func=func
        )
        assert results == [FTP003(line=3, column=1)]


class TestFTP007:
    def test_ftp007_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp007_ignore.txt", issue_number="FTP007")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("from datetime import datetime", "datetime.utcfromtimestamp()"),
            ("import datetime", "datetime.datetime.utcfromtimestamp()"),
            ("from datetime.datetime import utcfromtimestamp", "utcfromtimestamp()"),
        ],
    )
    def test_ftp007(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp007.txt", issue_number="FTP007", imp=imp, func=func
        )
        assert results == [FTP007(line=3, column=1)]


class TestFTP073:
    def test_ftp073_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp073.txt", issue_number="FTP073")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("import functools", "functools.lru_cache"),
            ("from functools import lru_cache", "lru_cache"),
        ],
    )
    def test_ftp073(self, imp: str, func: str, runner: Flake8Runner) -> None:
        results = runner(
            filename="ftp073.txt",
            issue_number="FTP073",
            imp=imp,
            func=func,
        )
        assert results == [
            FTP073(line=13, column=1, message="Use functools.cache instead."),
            FTP073(line=14, column=1, message="Use functools.cache instead."),
        ]


class TestFTP063:
    def test_ftp063_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp063_ignore.txt", issue_number="FTP063")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("import contextlib", "contextlib.wraps"),
            ("from contextlib import wraps", "wraps"),
        ],
    )
    def test_ftp063(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp063.txt", issue_number="FTP063", imp=imp, func=func
        )
        assert results == [FTP063(line=3, column=1)]


def test_ftp061(runner: Flake8Runner) -> None:
    assert runner(filename="ftp061.txt", issue_number="FTP061") == [
        FTP061(line=7, column=1),
        FTP061(line=8, column=1),
    ]


def test_ftp062(runner: Flake8Runner) -> None:
    assert runner(filename="ftp062.txt", issue_number="FTP062") == [
        FTP062(line=7, column=1),
        FTP062(line=8, column=1),
    ]


@pytest.mark.parametrize("func", ast_call.BAD_CALLS)
def test_ftp045(runner: Flake8Runner, func: str) -> None:
    assert runner(filename="ftp045.txt", issue_number="FTP045", func=func) == [
        FTP045(line=6, column=1, func=func)
    ]


def test_ftp002(runner: Flake8Runner) -> None:
    assert runner(filename="ftp002.txt", issue_number="FTP002") == [
        FTP002(line=6, column=1)
    ]


def test_ftp038(runner: Flake8Runner) -> None:
    assert runner(filename="ftp038.txt", issue_number="FTP038") == [
        FTP038(line=10, column=1),
        FTP038(line=11, column=1),
        FTP038(line=12, column=1),
    ]


def test_ftp025(runner: Flake8Runner) -> None:
    assert runner(filename="ftp025.txt", issue_number="FTP025") == [
        FTP025(line=9, column=1)
    ]


class TestFTP088:
    def test_ftp088_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp088_ignore.txt", issue_number="FTP088")

    @pytest.mark.parametrize(
        "imp,func",
        [("import io", "io.open"), ("from io import open", "open")],
    )
    def test_ftp088(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp088.txt", issue_number="FTP088", imp=imp, func=func
        )
        assert results == [FTP088(line=3, column=1)]


def test_ftp050(runner: Flake8Runner) -> None:
    assert runner(filename="ftp050.txt", issue_number="FTP050") == [
        FTP050(line=5, column=1),
        FTP050(line=6, column=1),
    ]


class TestFTP051:
    def test_ftp051_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp051_ignore.txt", issue_number="FTP051")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("import pprint", "pprint.pprint"),
            ("from pprint import pprint", "pprint"),
        ],
    )
    def test_ftp051(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp051.txt", issue_number="FTP051", imp=imp, func=func
        )
        assert results == [FTP051(line=7, column=1)]


class TestFTP052:
    def test_ftp052_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp052_ignore.txt", issue_number="FTP052")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("import pprint", "pprint.pp"),
            ("from pprint import pp", "pp"),
        ],
    )
    def test_ftp052(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp052.txt", issue_number="FTP052", imp=imp, func=func
        )
        assert results == [FTP052(line=7, column=1)]


class TestFTP053:
    def test_ftp053_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp053_ignore.txt", issue_number="FTP053")

    @pytest.mark.parametrize(
        "imp,cls",
        [
            ("import pprint", "pprint.PrettyPrinter"),
            ("from pprint import PrettyPrinter", "PrettyPrinter"),
        ],
    )
    def test_ftp053(self, runner: Flake8Runner, imp: str, cls: str) -> None:
        results = runner(filename="ftp053.txt", issue_number="FTP053", imp=imp, cls=cls)
        assert results == [FTP053(line=7, column=1)]


def test_ftp092(runner: Flake8Runner) -> None:
    assert runner(filename="ftp092.txt", issue_number="FTP092") == [
        FTP092(line=11, column=1),
        FTP092(line=12, column=1),
        FTP092(line=13, column=1),
    ]


def test_ftp070(runner: Flake8Runner) -> None:
    assert runner(filename="ftp070.txt", issue_number="FTP070") == [
        FTP070(line=6, column=1)
    ]


def test_ftp083(runner: Flake8Runner) -> None:
    assert runner(filename="ftp083.txt", issue_number="FTP083") == [
        FTP083(line=10, column=1),
        FTP083(line=11, column=1),
        FTP083(line=12, column=1),
        FTP083(line=13, column=1),
        FTP083(line=14, column=1),
    ]


def test_ftp084(runner: Flake8Runner) -> None:
    assert runner(filename="ftp084.txt", issue_number="FTP084") == [
        FTP084(line=13, column=1),
        FTP084(line=14, column=1),
        FTP084(line=15, column=1),
        FTP084(line=16, column=1),
    ]


def test_ftp085(runner: Flake8Runner) -> None:
    assert runner(filename="ftp085.txt", issue_number="FTP085") == [
        FTP085(line=12, column=1),
        FTP085(line=13, column=1),
        FTP085(line=14, column=1),
    ]


def test_ftp086(runner: Flake8Runner) -> None:
    assert runner(filename="ftp086.txt", issue_number="FTP086") == [
        FTP086(line=10, column=1),
        FTP086(line=11, column=1),
    ]


class TestFTP075:
    def test_ftp075_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp075_ignore.txt", issue_number="FTP075")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("import subprocess", "subprocess.run"),
            ("from subprocess import run", "run"),
            ("import subprocess", "subprocess.Popen"),
            ("from subprocess import Popen", "Popen"),
        ],
    )
    def test_ftp075(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp075.txt", issue_number="FTP075", imp=imp, func=func
        )
        assert results == [FTP075(line=7, column=1), FTP075(line=8, column=1)]


class TestFTP017:
    def test_ftp017_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp017_ignore.txt", issue_number="FTP017")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("import typing", "typing.NamedTuple"),
            ("from typing import NamedTuple", "NamedTuple"),
        ],
    )
    def test_ftp017(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp017.txt", issue_number="FTP017", imp=imp, func=func
        )
        assert results == [FTP017(line=7, column=1)]


class TestFTP018:
    def test_ftp018_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp018_ignore.txt", issue_number="FTP018")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("import typing", "typing.TypedDict"),
            ("from typing import TypedDict", "TypedDict"),
        ],
    )
    def test_ftp018(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp018.txt", issue_number="FTP018", imp=imp, func=func
        )
        assert results == [FTP018(line=7, column=1)]


class TestFTP200:
    def test_ftp200_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp200_ignore.txt", issue_number="FTP200")

    @pytest.mark.parametrize(
        "imp,func",
        [
            ("import flask", "flask.abort"),
            ("from flask import abort", "abort"),
            ("import werkzeug", "werkzeug.exceptions.abort"),
            ("from werkzeug import exceptions", "exceptions.abort"),
            ("from werkzeug.exceptions import abort", "abort"),
        ],
    )
    def test_ftp200(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp200.txt", issue_number="FTP200", imp=imp, func=func
        )
        assert results == [FTP200(line=3, column=1)]


def test_ftp059(runner: Flake8Runner) -> None:
    assert runner(filename="ftp059.txt", issue_number="FTP059") == [
        FTP059(line=14, column=7),
        FTP059(line=15, column=7),
        FTP059(line=16, column=7),
        FTP059(line=17, column=7),
        FTP059(line=18, column=1),
        FTP059(line=19, column=7),
        FTP059(line=20, column=7),
        FTP059(line=21, column=1),
        FTP059(line=21, column=11),
    ]


def test_ftp100(runner: Flake8Runner) -> None:
    assert runner(filename="ftp100.txt", issue_number="FTP100") == [
        FTP100(line=10, column=1)
    ]


class TestFTP102:
    def test_ignore(self, runner: Flake8Runner) -> None:
        assert not runner(filename="ftp102_ignore.txt", issue_number="FTP102")

    @pytest.mark.parametrize(
        "imp,func",
        [("import pathlib", "pathlib.Path"), ("from pathlib import Path", "Path")],
    )
    def test(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp102.txt", issue_number="FTP102", imp=imp, func=func
        )
        assert results == [FTP102(line=12, column=1)]


def test_ftp109(runner: Flake8Runner) -> None:
    assert runner(filename="ftp109.txt", issue_number="FTP109") == [
        FTP109(line=10, column=1),
        FTP109(line=11, column=1),
        FTP109(line=12, column=1),
    ]


@pytest.mark.parametrize(
    "func,issue,issue_number",
    [
        ("str", FTP110, "FTP110"),
        ("int", FTP111, "FTP111"),
        ("float", FTP112, "FTP112"),
        ("bool", FTP113, "FTP113"),
        ("bytes", FTP114, "FTP114"),
    ],
)
def test_ftp110_114(
    runner: Flake8Runner, func: str, issue: partial[Issue], issue_number: str
) -> None:
    assert runner(filename="ftp110_114.txt", issue_number=issue_number, func=func) == [
        issue(line=8, column=1)
    ]


class TestFTP117_118:  # pylint:disable=invalid-name

    @pytest.mark.parametrize("warnings_imp,warn", [("from foo import warn", "warn")])
    @pytest.mark.parametrize("issue_number", ["FTP117", "FTP118"])
    def test_ignore_invalid_warning_import(
        self,
        runner: Flake8Runner,
        warnings_imp: str,
        warn: str,
        issue_number: str,
    ) -> None:
        assert not runner(
            filename="ftp117_118.txt",
            issue_number=issue_number,
            deprecated_imp="from warnings import deprecated",
            deprecated="deprecated",
            warnings_imp=warnings_imp,
            warn=warn,
        )

    @pytest.mark.parametrize(
        "deprecated_imp,deprecated", [("from foo import deprecated", "deprecated")]
    )
    def test_ignore_invalid_deprecated_import(
        self,
        runner: Flake8Runner,
        deprecated_imp: str,
        deprecated: str,
    ) -> None:
        assert not runner(
            filename="ftp117_118.txt",
            issue_number="FTP117",
            deprecated_imp=deprecated_imp,
            deprecated=deprecated,
            warnings_imp="from warnings import warn",
            warn="warn",
        )

    @pytest.mark.parametrize(
        "deprecated_imp,deprecated",
        [
            ("from typing_extensions import deprecated", "deprecated"),
            ("import typing_extensions", "typing_extensions.deprecated"),
            ("from warnings import deprecated", "deprecated"),
            ("import warnings", "warnings.deprecated"),
        ],
    )
    @pytest.mark.parametrize("issue_cls,line", [(FTP117, 28), (FTP118, 33)])
    def test(
        self,
        runner: Flake8Runner,
        deprecated_imp: str,
        deprecated: str,
        issue_cls: partial[Issue],
        line: int,
    ) -> None:
        issue = issue_cls(line=line, column=5)
        results = runner(
            filename="ftp117_118.txt",
            issue_number=issue.issue_number,
            deprecated_imp=deprecated_imp,
            deprecated=deprecated,
            warnings_imp="import warnings",
            warn="warnings.warn",
        )
        assert results == [issue]


class TestFTP121:

    @pytest.mark.parametrize(
        "imp,func",
        [
            *[
                ("import foo", f"foo.{func}")
                for func in ast_call.BAD_SUBPROCESS_ALIASES
            ],
            ("import os", "os.open"),
        ],
    )
    def test_ignore_invalid_import(
        self, runner: Flake8Runner, imp: str, func: str
    ) -> None:
        assert not runner(
            filename="ftp121.txt", issue_number="FTP121", imp=imp, func=func
        )

    @pytest.mark.parametrize(
        "imp,func",
        [
            *[("import os", f"os.{func}") for func in ast_call.BAD_SUBPROCESS_ALIASES],
            *[
                (f"from os import {func}", func)
                for func in ast_call.BAD_SUBPROCESS_ALIASES
            ],
        ],
    )
    def test(self, runner: Flake8Runner, imp: str, func: str) -> None:
        results = runner(
            filename="ftp121.txt", issue_number="FTP121", imp=imp, func=func
        )
        assert results == [FTP121(line=9, column=1, func=func)]


@pytest.mark.parametrize(
    "imp,find_by_imp,type_var",
    [
        ("from typing import TypeVar", True, "TypeVar"),
        ("import typing", True, "typing.TypeVar"),
        ("import foo", False, "foo.TypeVar"),
        ("from foo import TypeVar", False, "TypeVar"),
        ("from foo import typing", False, "typing.TypeVar"),
    ],
)
@pytest.mark.parametrize(
    "version,find_by_version", [("3.7.0", False), ("3.12.0", True)]
)
def test_ftp127(
    runner: Flake8Runner,
    imp: str,
    find_by_imp: bool,
    type_var: str,
    version: str,
    find_by_version: bool,
) -> None:
    results = runner(
        filename="ftp127.txt",
        issue_number="FTP127",
        imp=imp,
        type_var=type_var,
        args=("--ftp-python-version", version),
    )
    if find_by_imp and find_by_version:
        assert results == [FTP127(line=9, column=5)]
    else:
        assert not results

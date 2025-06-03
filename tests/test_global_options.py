"""Tests for _flake8_tergeo.global_options."""

from __future__ import annotations

import platform

import pytest
from packaging.version import InvalidVersion
from pytest_mock import MockerFixture

from _flake8_tergeo import global_options


def test_register_global_options(mocker: MockerFixture) -> None:
    option_manager = mocker.Mock()
    global_options.register_global_options(option_manager)

    assert option_manager.add_option.call_args_list == [
        mocker.call(
            "--python-version",
            parse_from_config=True,
            default=platform.python_version(),
        ),
        mocker.call(
            "--auto-manage-options", parse_from_config=True, action="store_true"
        ),
    ]


@pytest.mark.parametrize(
    "version,parsed_version",
    [("3.8.0", (3, 8, 0)), ("3.10.6", (3, 10, 6)), ("3.14.0b1", (3, 14, 0))],
)
def test_parse_global_options(
    mocker: MockerFixture, version: str, parsed_version: tuple[int, int, int]
) -> None:
    options = mocker.Mock()
    options.python_version = version

    global_options.parse_global_options(options)
    assert options.python_version == parsed_version  # type:ignore[comparison-overlap]


@pytest.mark.parametrize("version", ["a.b.c", "3.x.a"])
def test_parse_global_options_invalid_not_int(
    mocker: MockerFixture, version: str
) -> None:
    options = mocker.Mock()
    options.python_version = version

    with pytest.raises(InvalidVersion):
        global_options.parse_global_options(options)


def test_get_python_version(mocker: MockerFixture) -> None:
    plugin = mocker.patch.object(global_options, "get_plugin")
    plugin().get_options().python_version = (3, 8, 1)
    assert global_options.get_python_version() == (3, 8, 1)

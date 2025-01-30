"""Tests for _flake8_tergeo.base_wrapper."""

from __future__ import annotations

import argparse
import inspect
from typing import Any

import pytest
from pytest_mock import MockerFixture

from _flake8_tergeo import BaseWrapperChecker
from _flake8_tergeo.flake8_types import OptionManager


class TestBaseWrapperChecker:
    @pytest.mark.parametrize(
        "add_options_callable,value", [(True, None), (False, None), (False, 22)]
    )
    def test_add_options(
        self, mocker: MockerFixture, add_options_callable: bool, value: Any | None
    ) -> None:
        checker_class = mocker.patch.object(
            BaseWrapperChecker, "checker_class", create=True
        )
        mocker.patch.object(BaseWrapperChecker, "old_prefix", create=True)
        mocker.patch.object(BaseWrapperChecker, "prefix", create=True)

        if not add_options_callable:
            checker_class.add_options = value

        manager = mocker.Mock(spec=OptionManager)
        BaseWrapperChecker.add_options(manager)

        if add_options_callable:
            checker_class.add_options.assert_called_once()
        else:
            assert checker_class.add_options == value

    @pytest.mark.parametrize(
        "parse_options_callable,parse_options_value,is_complex",
        [
            (True, None, False),
            (True, None, True),
            (False, None, False),
            (False, 22, False),
        ],
    )
    def test_parse_options(
        self,
        mocker: MockerFixture,
        parse_options_callable: bool,
        parse_options_value: Any | None,
        is_complex: bool,
    ) -> None:
        checker_class = mocker.patch.object(
            BaseWrapperChecker, "checker_class", create=True
        )

        if not parse_options_callable:
            checker_class.parse_options = parse_options_value
        if is_complex:
            getfullargspec = mocker.patch.object(inspect, "getfullargspec")
            getfullargspec().args = [mocker.ANY, mocker.ANY, mocker.ANY]

        manager = mocker.Mock(spec=OptionManager)
        options = mocker.Mock(spec=argparse.Namespace)
        args = ["foo"]
        BaseWrapperChecker.parse_options(manager, options, args)

        if parse_options_callable and is_complex:
            checker_class.parse_options.assert_called_once_with(manager, options, args)
        elif parse_options_callable and not is_complex:
            checker_class.parse_options.assert_called_once_with(options)
        else:
            assert checker_class.parse_options == parse_options_value

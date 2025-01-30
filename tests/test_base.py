"""Tests for _flake8_tergeo.base."""

from __future__ import annotations

import argparse
from typing import Any

import pytest
from pytest_mock import MockerFixture

from _flake8_tergeo import base
from _flake8_tergeo.base import (
    BaseNamespace,
    BaseOptionManager,
    DefaultWrapper,
    Flake8TergeoPlugin,
)
from _flake8_tergeo.flake8_types import OptionManager
from _flake8_tergeo.interfaces import AbstractChecker
from tests import conftest


class TestFlake8TergeoPlugin:
    def test_metadata(self) -> None:
        assert Flake8TergeoPlugin.off_by_default
        assert Flake8TergeoPlugin.name
        assert Flake8TergeoPlugin.version

    @pytest.mark.usefixtures("basic_checker")
    def test_run(self, plugin: Flake8TergeoPlugin, mocker: MockerFixture) -> None:
        mocker.patch.object(Flake8TergeoPlugin, "_parse_options_options")

        findings = list(plugin.run())
        assert len(findings) == 1
        assert findings[0][0] == 1
        assert findings[0][1] == 2
        assert findings[0][2] == "FTX002 Dummy"
        assert findings[0][3] == type(plugin)

    @pytest.mark.usefixtures("basic_checker")
    def test_setup_once_prevents_multiple_calls(
        self, plugin: Flake8TergeoPlugin, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(Flake8TergeoPlugin, "_parse_options_options")
        setup_once = mocker.spy(Flake8TergeoPlugin, "_setup_once")
        run_parse_options = mocker.spy(Flake8TergeoPlugin, "_run_parse_options")

        list(plugin.run())
        assert setup_once.call_count == 1
        assert run_parse_options.call_count == 1

        list(plugin.run())
        assert setup_once.call_count == 2
        assert run_parse_options.call_count == 1

    @pytest.mark.usefixtures("invalid_checker")
    def test_invalid_arg_for_checker(
        self, plugin: Flake8TergeoPlugin, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(Flake8TergeoPlugin, "_parse_options_options")
        with pytest.raises(RuntimeError):
            list(plugin.run())

    @pytest.mark.usefixtures("basic_checker")
    def test_module_not_found(
        self, mocker: MockerFixture, plugin: Flake8TergeoPlugin
    ) -> None:
        mocker.patch.object(
            Flake8TergeoPlugin, "module_load_error", ImportError("import error")
        )
        assert list(plugin.run()) == [
            (-1, -1, "FTP000 Cannot load plugin due 'import error'", type(plugin))
        ]

    def test_parse_options_on_checker(
        self,
        mocker: MockerFixture,
        plugin: Flake8TergeoPlugin,
        checker_with_parse: type[AbstractChecker],
    ) -> None:
        options = mocker.patch.object(Flake8TergeoPlugin, "_parse_options_options")
        spy = mocker.spy(checker_with_parse, "parse_options")
        list(plugin.run())
        spy.assert_called_once_with(options)

    def test_pre_parse_options_not_called(
        self,
        mocker: MockerFixture,
        plugin: Flake8TergeoPlugin,
        basic_checker: type[AbstractChecker],
    ) -> None:
        options = mocker.patch.object(Flake8TergeoPlugin, "_parse_options_options")
        options.auto_manage_options = False
        spy = mocker.spy(basic_checker, "pre_parse_options")
        list(plugin.run())
        spy.assert_not_called()

    def test_pre_parse_options_called(
        self,
        mocker: MockerFixture,
        plugin: Flake8TergeoPlugin,
        basic_checker: type[AbstractChecker],
    ) -> None:
        options = mocker.patch.object(Flake8TergeoPlugin, "_parse_options_options")
        options.auto_manage_options = True
        spy = mocker.spy(basic_checker, "pre_parse_options")
        list(plugin.run())
        spy.assert_called_once_with(options)

    def test_complex_parse_options_on_checker(
        self,
        mocker: MockerFixture,
        plugin: Flake8TergeoPlugin,
        checker_with_complex_parse: type[Any],
    ) -> None:
        option_manager = mocker.patch.object(
            Flake8TergeoPlugin, "_parse_options_option_manager"
        )
        options = mocker.patch.object(Flake8TergeoPlugin, "_parse_options_options")
        options_args = mocker.patch.object(Flake8TergeoPlugin, "_parse_options_args")

        list(plugin.run())
        assert checker_with_complex_parse.parse_options_args == [
            option_manager,
            options,
            options_args,
        ]

    def test_parse_options(self, mocker: MockerFixture) -> None:
        options_args = mocker.Mock()

        Flake8TergeoPlugin.parse_options(mocker.Mock(), mocker.Mock(), options_args)
        assert isinstance(
            Flake8TergeoPlugin._parse_options_option_manager,
            BaseOptionManager,
        )
        assert isinstance(Flake8TergeoPlugin._parse_options_options, BaseNamespace)
        assert Flake8TergeoPlugin._parse_options_args == options_args

    @pytest.mark.usefixtures("basic_checker")
    def test_add_options_no_configured(self, mocker: MockerFixture) -> None:
        option_manager = mocker.Mock()
        Flake8TergeoPlugin.add_options(option_manager)
        assert not option_manager.mock_calls

    @pytest.mark.usefixtures("checker_with_options")
    def test_add_options(self, mocker: MockerFixture) -> None:
        option_manager = mocker.Mock()
        Flake8TergeoPlugin.add_options(option_manager)

        expected = ["FT1", "FT2"]
        option_manager.extend_default_ignore.assert_called_once_with(expected)

    @pytest.mark.usefixtures("checker_wrapper_with_options")
    def test_add_option_with_wrapper(self, mocker: MockerFixture) -> None:
        option_manager = mocker.Mock()
        Flake8TergeoPlugin.add_options(option_manager)

        expected = ["FTN01", "FTN06"]
        option_manager.extend_default_ignore.assert_called_once_with(expected)

    @pytest.mark.usefixtures("checker_with_disable")
    def test_checker_disable(
        self, plugin: Flake8TergeoPlugin, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(Flake8TergeoPlugin, "_parse_options_options")

        findings = list(plugin.run())
        assert findings == [(1, 2, "FTF002 Dummy", type(plugin))]

    def test_get_options_not_set(self, plugin: Flake8TergeoPlugin) -> None:
        with pytest.raises(AssertionError):
            plugin.get_options()

    def test_get_options(
        self, mocker: MockerFixture, plugin: Flake8TergeoPlugin
    ) -> None:
        options = mocker.Mock()
        Flake8TergeoPlugin.parse_options(mocker.Mock(), options, mocker.Mock())
        assert plugin.get_options()._args == options


class TestBaseNamespace:
    def test_get(self) -> None:
        args = argparse.Namespace(ftp_arg=22)
        wrapper = BaseNamespace(args)
        assert wrapper.arg == 22

    def test_with_flake8_config(self) -> None:
        args = argparse.Namespace(ignore="dummy")
        wrapper = BaseNamespace(args)
        assert wrapper.ignore == "dummy"
        assert not hasattr(wrapper, "ftp_ignore")

    def test_set(self) -> None:
        args = argparse.Namespace(ftp_arg=22)
        wrapper = BaseNamespace(args)
        wrapper.arg = 42

        assert wrapper.arg == 42
        assert args.ftp_arg == 42

    def test_get_with_default_wrapper(self) -> None:
        args = argparse.Namespace(ftp_arg=DefaultWrapper(22))
        wrapper = BaseNamespace(args)
        assert wrapper.arg == 22

    def test_ftp_is_default(self) -> None:
        args = argparse.Namespace(ftp_arg=DefaultWrapper(22), ftp_other="some")
        wrapper = BaseNamespace(args)
        assert wrapper.ftp_is_default("arg")
        assert not wrapper.ftp_is_default("other")


class TestBaseOptionManager:
    def test_add_option(self, mocker: MockerFixture) -> None:
        manager = mocker.Mock(spec=OptionManager)
        wrapper = BaseOptionManager(manager)
        wrapper.add_option("--dummy")
        manager.add_option.assert_called_once_with("--ftp-dummy")

    def test_add_option_default(self, mocker: MockerFixture) -> None:
        manager = mocker.Mock(spec=OptionManager)
        wrapper = BaseOptionManager(manager)
        wrapper.add_option("--dummy", default="some")
        manager.add_option.assert_called_once_with(
            "--ftp-dummy", default=DefaultWrapper("some")
        )

    def test_add_invalid_option(self, mocker: MockerFixture) -> None:
        wrapper = BaseOptionManager(mocker.Mock())
        with pytest.raises(ValueError, match="Unable to handle first argument"):
            wrapper.add_option("dummy")


def test_get_plugin(mocker: MockerFixture) -> None:
    with pytest.raises(AssertionError):
        base.get_plugin()
    plugin = conftest.create_plugin(mocker)
    assert base.get_plugin() == plugin


class TestDefaultWrapper:

    def test(self) -> None:
        wrapper = DefaultWrapper(42)
        assert wrapper.default == 42

    def test_eq(self) -> None:
        wrapper = DefaultWrapper(42)
        assert wrapper == DefaultWrapper(42)
        assert wrapper != DefaultWrapper(43)
        assert wrapper != 42

    def test_hash(self) -> None:
        wrapper = DefaultWrapper(42)
        assert hash(wrapper) == hash(wrapper)
        assert hash(wrapper) == hash(DefaultWrapper(42))
        assert hash(wrapper) != hash(DefaultWrapper(44))

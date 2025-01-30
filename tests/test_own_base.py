"""Tests for _flake8_tergeo.own_base."""

from __future__ import annotations

import ast
import tokenize
from collections.abc import Sequence

from pytest_mock import MockerFixture

from _flake8_tergeo import registry
from _flake8_tergeo.flake8_types import Issue, IssueGenerator, OptionManager
from _flake8_tergeo.own_base import ASTChecker, OwnOptionManager, TokenChecker


class TestOwnOptionManager:
    def test_add_option(self, mocker: MockerFixture) -> None:
        manager = mocker.Mock(spec=OptionManager)
        wrapper = OwnOptionManager(manager)
        wrapper.add_option("--dummy")
        manager.add_option.assert_called_once_with("--dummy")

    def test_extend_default_ignore(self, mocker: MockerFixture) -> None:
        manager = mocker.Mock(spec=OptionManager)
        wrapper = OwnOptionManager(manager)
        wrapper.extend_default_ignore(["F1", "B2"])
        manager.extend_default_ignore.assert_called_once_with(["PF1", "PB2"])


class TestASTChecker:
    def _check_import(self, _: ast.Import) -> IssueGenerator:
        yield Issue(1, 2, "001", "Dummy")
        yield Issue(1, 2, "002", "Dummy")

    def test(self, mocker: MockerFixture) -> None:
        new_map = {ast.Import: [self._check_import]}
        mocker.patch.dict(registry.AST_REGISTRY, new_map, clear=True)
        checker = ASTChecker(tree=ast.parse("import foo"))

        assert len(list(checker.check())) == 2


class TestTokenChecker:
    @staticmethod
    def _check_tokens(tokens: Sequence[tokenize.TokenInfo]) -> IssueGenerator:
        assert len(tokens) == 2
        yield Issue(1, 2, "001", "Dummy")
        yield Issue(1, 2, "002", "Dummy")

    def test(self, mocker: MockerFixture) -> None:
        mocker.patch.object(registry, "TOKEN_REGISTRY", [self._check_tokens])

        token = mocker.Mock(spec=tokenize.TokenInfo)
        checker = TokenChecker(file_tokens=[token, token])

        assert len(list(checker.check())) == 2

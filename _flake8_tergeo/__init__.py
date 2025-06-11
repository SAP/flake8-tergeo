"""Flake8 plugin."""

from __future__ import annotations

from _flake8_tergeo import global_options
from _flake8_tergeo.base import Flake8TergeoPlugin
from _flake8_tergeo.flake8_types import Issue
from _flake8_tergeo.hacks import add_python314_removed_ast_nodes
from _flake8_tergeo.own_base import ASTChecker, OwnChecker, TokenChecker
from _flake8_tergeo.wrapper_base import BaseWrapperChecker

add_python314_removed_ast_nodes()

try:
    from _flake8_tergeo.checks import (
        ast_assert,
        ast_assign,
        ast_bin_op,
        ast_call,
        ast_class_def,
        ast_dict,
        ast_except_handler,
        ast_for,
        ast_func_def,
        ast_import,
        ast_lambda,
        ast_name_or_attribute,
        ast_raise,
        ast_str,
        ast_subscript,
        dev_comments,
        file_tokens,
        log_lint,
        parens,
        requirements,
    )
    from _flake8_tergeo.checks.filename import FileNameChecker
    from _flake8_tergeo.checks.lines import LineChecker
    from _flake8_tergeo.checks.wrappers import (
        BugBearChecker,
        BuiltinsChecker,
        ComprehensionsChecker,
        PytestStyleChecker,
        SimplifyChecker,
        TypingImportChecker,
    )
except ImportError as err:  # pragma: no cover
    Flake8TergeoPlugin.module_load_error = err

__all__ = (
    "ASTChecker",
    "BaseWrapperChecker",
    "BugBearChecker",
    "BuiltinsChecker",
    "ComprehensionsChecker",
    "FileNameChecker",
    "Flake8TergeoPlugin",
    "Issue",
    "LineChecker",
    "OwnChecker",
    "PytestStyleChecker",
    "SimplifyChecker",
    "TokenChecker",
    "TypingImportChecker",
    "ast_assert",
    "ast_assign",
    "ast_bin_op",
    "ast_call",
    "ast_class_def",
    "ast_dict",
    "ast_except_handler",
    "ast_for",
    "ast_func_def",
    "ast_import",
    "ast_lambda",
    "ast_name_or_attribute",
    "ast_raise",
    "ast_str",
    "ast_subscript",
    "dev_comments",
    "file_tokens",
    "global_options",
    "log_lint",
    "parens",
    "registry",
    "requirements",
)

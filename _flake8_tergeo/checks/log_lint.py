"""logging checks."""

from __future__ import annotations

import ast
from typing import cast

from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.registry import register

LOGGING_FUNCTIONS = {
    "log",
    "debug",
    "critical",
    "error",
    "exception",
    "info",
    "warn",
    "warning",
}
RESERVED_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}


@register(ast.Call)
def check_call(node: ast.Call) -> IssueGenerator:
    """Visit a call statement."""
    if not isinstance(node.func, ast.Attribute):
        return
    if isinstance(node.func.value, ast.Name) and node.func.value.id in {
        "warnings",
        "_warnings",
    }:
        return
    if node.func.attr not in LOGGING_FUNCTIONS:
        return
    if not node.args:
        return
    if node.func.attr == "log" and len(node.args) < 2:
        return

    message_arg = node.args[1] if node.func.attr == "log" else node.args[0]
    yield from _check_for_percentage_formatting(node, message_arg)
    yield from _check_for_f_string(node, message_arg)
    yield from _check_for_str_format(node, message_arg)

    yield from _check_exec_info_in_exception(node)
    yield from _check_warn_call(node)
    yield from _check_error_exc_info(node)
    yield from _check_extra_arg(node)


def _check_for_percentage_formatting(
    node: ast.Call, message: ast.AST
) -> IssueGenerator:
    if isinstance(message, ast.BinOp) and isinstance(message.op, ast.Mod):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="031",
            message="percentage formatting should be replaced with printf-style formatting.",
        )


def _check_for_f_string(node: ast.Call, message: ast.AST) -> IssueGenerator:
    if isinstance(message, ast.JoinedStr):
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="032",
            message="f-string should be replaced with printf-style formatting.",
        )


def _check_for_str_format(node: ast.Call, message: ast.AST) -> IssueGenerator:
    if not isinstance(message, ast.Call):
        return
    if not isinstance(message.func, ast.Attribute):
        return
    if message.func.attr != "format":
        return
    yield Issue(
        line=node.lineno,
        column=node.col_offset,
        issue_number="033",
        message="str.format should be replaced with printf-style formatting.",
    )


def _check_exec_info_in_exception(node: ast.Call) -> IssueGenerator:
    if cast(ast.Attribute, node.func).attr != "exception":
        return
    for keyword in node.keywords:
        if (
            keyword.arg == "exc_info"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value is True
        ):
            yield Issue(
                line=node.lineno,
                column=node.col_offset,
                issue_number="034",
                message="Using exec_info=True in exception() is redundant.",
            )


def _check_warn_call(node: ast.Call) -> IssueGenerator:
    if cast(ast.Attribute, node.func).attr == "warn":
        yield Issue(
            line=node.lineno,
            column=node.col_offset,
            issue_number="035",
            message="warn() is deprecated. Use warning() instead.",
        )


def _check_error_exc_info(node: ast.Call) -> IssueGenerator:
    if cast(ast.Attribute, node.func).attr != "error":
        return
    for keyword in node.keywords:
        if (
            keyword.arg == "exc_info"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value is True
        ):
            yield Issue(
                line=node.lineno,
                column=node.col_offset,
                issue_number="036",
                message="Using exec_info=True in error() can be simplified to exception().",
            )


def _check_extra_arg(node: ast.Call) -> IssueGenerator:
    for keyword in node.keywords:
        if keyword.arg != "extra":
            return
        if not isinstance(keyword.value, ast.Dict):
            return

        for key in keyword.value.keys:
            if not isinstance(key, ast.Constant):
                continue
            if key.value not in RESERVED_ATTRS:
                continue
            yield Issue(
                line=key.lineno,
                column=key.col_offset,
                issue_number="037",
                message=f"The extra key '{key.value}' clashes with existing log record fields.",
            )

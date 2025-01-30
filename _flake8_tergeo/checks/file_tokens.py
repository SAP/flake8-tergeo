"""Checks using file tokens."""

from __future__ import annotations

import re
import tokenize
from collections.abc import Sequence

from _flake8_tergeo.flake8_types import Issue, IssueGenerator
from _flake8_tergeo.registry import register_token_checker

_INVALID_LINE_BREAK = re.compile(r"(?<!\\)\\$", re.M)
_INVALID_MULTILINE_BACKSLASH = re.compile(r"(?<![\']{3}|[\"]{3})\\$", re.M)
_WHITESPACE = re.compile(r"\s+")
_TYPE_COMMENT_PATTERN = re.compile("^.*(#type:)((?!(ignore)).)*$")
_STRING_PATTERN = re.compile("^([^'\"]*)(.*)$", re.DOTALL)


@register_token_checker
def check_tokens(file_tokens: Sequence[tokenize.TokenInfo]) -> IssueGenerator:
    """Checks based on file tokens."""
    yield from _check_broken_line(file_tokens)
    yield from _check_type_comment(file_tokens)
    yield from _check_unicode_prefix(file_tokens)
    yield from _check_implicit_concat(file_tokens)
    yield from _check_empty_doc_comment(file_tokens)


def _check_broken_line(file_tokens: Sequence[tokenize.TokenInfo]) -> IssueGenerator:
    checked_lines: list[int] = []
    for token in file_tokens:
        if token.exact_type in (
            tokenize.STRING,
            tokenize.COMMENT,
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.ENDMARKER,
        ):
            continue
        if token.start[0] in checked_lines:
            continue
        if _INVALID_LINE_BREAK.search(
            token.line
        ) and _INVALID_MULTILINE_BACKSLASH.search(token.line):
            yield Issue(
                line=token.start[0],
                column=token.start[1],
                issue_number="091",
                message="Found backslash that is used for line breaking.",
            )
            checked_lines.append(token.start[0])


def _check_type_comment(file_tokens: Sequence[tokenize.TokenInfo]) -> IssueGenerator:
    for token in file_tokens:
        if token.type != tokenize.COMMENT:
            continue
        text = _WHITESPACE.sub("", token.string)
        if _TYPE_COMMENT_PATTERN.match(text):
            yield Issue(
                line=token.start[0],
                column=token.start[1],
                issue_number="078",
                message="Use type annotations instead of type comments.",
            )


def _check_implicit_concat(file_tokens: Sequence[tokenize.TokenInfo]) -> IssueGenerator:
    previous_token = file_tokens[0]
    for token in file_tokens[1:]:
        if (
            previous_token.type == token.type == tokenize.STRING
            and previous_token.line == token.line
        ):
            yield Issue(
                line=token.start[0],
                column=token.start[1],
                issue_number="080",
                message="Implicitly concatenated string literals.",
            )
        previous_token = token


def _check_unicode_prefix(file_tokens: Sequence[tokenize.TokenInfo]) -> IssueGenerator:
    for token in file_tokens:
        if token.type != tokenize.STRING:
            continue
        match = _STRING_PATTERN.match(token.string)
        if not match:  # pragma: no cover
            continue
        if match.group(1).lower() == "u":
            yield Issue(
                line=token.start[0],
                column=token.start[1],
                issue_number="072",
                message="Found unnecessary string unicode prefix.",
            )


def _check_empty_doc_comment(
    file_tokens: Sequence[tokenize.TokenInfo],
) -> IssueGenerator:
    for token in file_tokens:
        if token.type != tokenize.COMMENT:
            continue
        if token.string != "#:":
            continue
        yield Issue(
            line=token.start[0],
            column=token.start[1],
            issue_number="028",
            message="Found empty doc comment.",
        )

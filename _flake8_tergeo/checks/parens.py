"""Unnecessary parenthesis checks."""

from __future__ import annotations

import tokenize
from collections.abc import Sequence

from _flake8_tergeo.base import get_plugin
from _flake8_tergeo.flake8_types import Issue, IssueGenerator, OptionManager
from _flake8_tergeo.registry import register_add_options, register_token_checker

NON_CODING_TOKENS = frozenset((tokenize.NL, tokenize.COMMENT))
OPENING = frozenset(("(", "[", "{"))
CLOSING = frozenset((")", "]", "}"))

CODING_TOKENS = (tokenize.NAME, tokenize.OP, tokenize.NUMBER)

Tokens = Sequence[tokenize.TokenInfo]


@register_token_checker
def check_tokens(tokens: Tokens) -> IssueGenerator:
    """Checks for unnecessary parenthesis."""
    yield from _find_parens_in_statements(tokens)
    yield from _find_parens_in_return(tokens)


def _find_parens_in_statements(tokens: Tokens) -> IssueGenerator:
    # find all opening parens tokens
    start_indexes = _find_first_opening(tokens)
    # find all opening parens tokens followed by another opening parens tokens
    indexes = _find_second_opening(tokens, start_indexes)
    for index in indexes:
        yield from _check_iteration(tokens, index)


def _find_first_opening(
    tokens: Tokens,
) -> list[int]:
    return [index for index, token in enumerate(tokens) if token.string == "("]


def _find_second_opening(tokens: Tokens, indexes: list[int]) -> list[int]:
    found = []
    for index in indexes:
        index += 1
        while tokens[index].type in NON_CODING_TOKENS:
            index += 1
        if tokens[index].string == "(":
            found.append(index)
    return found


def _check_iteration(tokens: Tokens, index: int) -> IssueGenerator:
    start = index
    depth = 1

    while depth:
        index += 1
        # found comma or yield at depth 1: this is a tuple / coroutine
        if depth == 1 and tokens[index].string in {",", "yield"}:
            return
        if tokens[index].string in OPENING:
            depth += 1
        elif tokens[index].string in CLOSING:
            depth -= 1

    # empty tuple
    if all(t.type in NON_CODING_TOKENS for t in tokens[start + 1 : index]):
        return

    # search forward for the next non-coding token
    index += 1
    while tokens[index].type in NON_CODING_TOKENS:
        index += 1

    if tokens[index].string == ")":
        yield _create_issue(tokens, start)


def _find_parens_in_return(tokens: Tokens) -> IssueGenerator:
    for index, token in enumerate(tokens):
        if token.string == "(" and tokens[index - 1].string == "return":
            yield from _find_in_return_statement(tokens, index)


def _find_in_return_statement(tokens: Tokens, index: int) -> IssueGenerator:
    start = index
    depth = 1
    num_comma = 0

    if tokens[index + 1].string == ")":
        return

    while depth:
        index += 1
        if tokens[index].type not in CODING_TOKENS:
            return
        if tokens[index].type == tokenize.NAME and tokens[index].string == "for":
            # most likely a generator expression
            return
        if (
            tokens[index].type == tokenize.OP
            and tokens[index].string == ","
            and depth == 1
        ):
            num_comma += 1
        if tokens[index].string in OPENING:
            depth += 1
        elif tokens[index].string in CLOSING:
            depth -= 1

    if tokens[index + 1].type in CODING_TOKENS:
        return

    disallow_single_tuple = (
        get_plugin().get_options().disallow_parens_in_return_single_element_tuple
    )
    if (
        not disallow_single_tuple
        and num_comma == 1
        and tokens[index - 1].type == tokenize.OP
        and tokens[index - 1].string == ","
    ):
        # ignore single element tuples
        return
    yield _create_issue(tokens, start)


def _create_issue(tokens: Tokens, index: int) -> Issue:
    return Issue(
        line=tokens[index].start[0],
        column=tokens[index].start[1],
        issue_number="008",
        message="Found unnecessary parenthesis.",
    )


@register_add_options
def add_options(option_manager: OptionManager) -> None:
    """Add options for this checker."""
    option_manager.add_option(
        "--disallow-parens-in-return-single-element-tuple",
        parse_from_config=True,
        action="store_true",
    )

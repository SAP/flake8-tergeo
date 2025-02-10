"""Development comment checks."""

from __future__ import annotations

import re
import tokenize
from argparse import Namespace
from collections.abc import Sequence

from typing_extensions import Protocol

from _flake8_tergeo import base
from _flake8_tergeo.flake8_types import Issue, IssueGenerator, OptionManager
from _flake8_tergeo.registry import (
    register_add_options,
    register_parse_options,
    register_token_checker,
)

_WHITESPACE = re.compile(r" +")


class _ParseOptions(Protocol):
    dev_comments_disallowed_synonyms: list[str]
    dev_comments_enforce_description: bool
    dev_comments_tracking_regex: re.Pattern[str] | None
    dev_comments_allowed_synonyms: list[str]


@register_token_checker
def check(file_tokens: Sequence[tokenize.TokenInfo]) -> IssueGenerator:
    """Check the provided AST."""
    for token in file_tokens:
        if token.type == tokenize.COMMENT:
            issue = _check_comment(token)
            if issue:
                yield issue


def _check_comment(token: tokenize.TokenInfo) -> Issue | None:
    parts = _parse_comment(token.string)
    options: _ParseOptions = base.get_plugin().get_options()
    tracking_regex = options.dev_comments_tracking_regex

    if parts[0] in options.dev_comments_disallowed_synonyms:
        return Issue(
            line=token.start[0],
            column=token.start[1],
            issue_number="010",
            message=f"Usage of disallowed dev comment identifier '{parts[0]}'.",
        )

    if parts[0] in options.dev_comments_allowed_synonyms:
        parts = parts[1:]
        if not parts and tracking_regex:
            return Issue(
                line=token.start[0],
                column=token.start[1],
                issue_number="011",
                message="Missing tracking id in dev comment.",
            )

        if tracking_regex and not tracking_regex.fullmatch(parts[0]):
            return Issue(
                line=token.start[0],
                column=token.start[1],
                issue_number="012",
                message=f"Invalid tracking id '{parts[0]}' in dev comment.",
            )

        if tracking_regex:
            parts = parts[1:]  # if a project id exists, strip it

        if not parts and options.dev_comments_enforce_description:
            return Issue(
                line=token.start[0],
                column=token.start[1],
                issue_number="013",
                message="Missing description in dev comment.",
            )
    return None


def _parse_comment(text: str) -> list[str]:
    text = text.strip().upper()[1:].strip()
    text = _WHITESPACE.sub(" ", text)
    return text.split(" ")


@register_add_options
def add_options(option_manager: OptionManager) -> None:
    """Add options for this checker."""
    option_manager.add_option(
        "--dev-comments-tracking-project-ids",
        parse_from_config=True,
        comma_separated_list=True,
        default=[],
    )
    option_manager.add_option(
        "--dev-comments-allowed-synonyms",
        parse_from_config=True,
        comma_separated_list=True,
        default=["TODO"],
    )
    option_manager.add_option(
        "--dev-comments-disallowed-synonyms",
        parse_from_config=True,
        comma_separated_list=True,
        default=["FIXME"],
    )
    option_manager.add_option(
        "--dev-comments-enforce-description",
        parse_from_config=True,
        action="store_true",
    )


@register_parse_options
def parse_options(options: Namespace) -> None:
    """Parse options for this checker."""
    options.dev_comments_tracking_regex = _build_tracking_id_regex(
        options.dev_comments_tracking_project_ids
    )
    options.dev_comments_allowed_synonyms = [
        option.upper() for option in options.dev_comments_allowed_synonyms
    ]
    options.dev_comments_disallowed_synonyms = [
        option.upper() for option in options.dev_comments_disallowed_synonyms
    ]


def _build_tracking_id_regex(project_ids: list[str]) -> re.Pattern[str] | None:
    if not project_ids:
        return None

    parts = [rf"({project_id.upper()}-[0-9]+)" for project_id in project_ids]
    return re.compile("|".join(parts))

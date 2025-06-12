"""Global flake8 options."""

from __future__ import annotations

import platform
from argparse import Namespace

from packaging.version import Version

from _flake8_tergeo.base import get_plugin
from _flake8_tergeo.flake8_types import OptionManager
from _flake8_tergeo.registry import register_add_options, register_parse_options


@register_add_options
def register_global_options(option_manager: OptionManager) -> None:
    """Add global options."""
    option_manager.add_option(
        "--python-version", parse_from_config=True, default=platform.python_version()
    )
    option_manager.add_option(
        "--auto-manage-options", parse_from_config=True, action="store_true"
    )
    option_manager.add_option(
        "--pyproject-toml-file", parse_from_config=True, default=None
    )


@register_parse_options
def parse_global_options(options: Namespace) -> None:
    """Parse the global options."""
    version = Version(options.python_version)
    options.python_version = (version.major, version.minor, version.micro)


def get_python_version() -> tuple[int, int, int]:
    """Return the python version used for checks."""
    return get_plugin().get_options().python_version

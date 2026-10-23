# ----------------------------------------------------------------------
# Load config from environment
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

"""Environment-based configuration backend.

This module implements configuration loading from operating system
environment variables.

The backend URL format is::

    env:///<prefix>

Configuration keys are converted to environment variable names by replacing
dots with underscores and converting characters to upper case.

Example:
    ``config.database.host`` with prefix ``NOC`` maps to
    ``NOC_DATABASE_HOST``.
"""

# Python modules
from __future__ import annotations
from functools import cached_property
import os
from dataclasses import dataclass
from urllib.parse import urlparse

# NOC modules
from noc.core.typing import SENTINEL
from .base import BaseConfigBackend


@dataclass
class EnvParams:
    """Environment backend parameters.

    Args:
        prefix: Environment variable name prefix.
    """

    prefix: str

    @classmethod
    def from_url(cls, url: str) -> EnvParams:
        """Parse environment backend parameters from URL.

        Args:
            url: Environment backend URL.

        Returns:
            Parsed environment backend parameters.
        """
        parsed = urlparse(url)
        return EnvParams(prefix=parsed.path.lstrip("/"))


class EnvBackend(BaseConfigBackend):
    """Configuration backend backed by environment variables.

    URL format::

        env:///<prefix>

    Configuration keys are mapped to environment variables:

    ``config.my.variable`` -> ``<prefix>_MY_VARIABLE``.
    """

    @cached_property
    def params(self) -> EnvParams:
        """Return parsed backend parameters.

        Returns:
            Environment backend parameters.
        """
        return EnvParams.from_url(self.url)

    def get(self, key: str, default: object) -> object:
        """Get configuration value from environment variable.

        Args:
            key: Dot-separated configuration key.
            default: Value returned when environment variable is missing.

        Returns:
            Environment variable value or default value.
        """
        params = self.params
        name = key.replace(".", "_").upper()
        env_name = f"{params.prefix}_{name}"
        v = os.environ.get(env_name, SENTINEL)
        return default if v is SENTINEL else v

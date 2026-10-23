# ----------------------------------------------------------------------
# Load config from YAML
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""YAML-based configuration backend.

This module implements configuration loading from YAML files.

The backend URL format is::

    yaml:///<path>

The loaded YAML document must contain a mapping at the top level. Nested
values can be accessed using dot-separated configuration keys.
"""

# Python modules
from __future__ import annotations
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from urllib.parse import urlparse
from typing import cast

# Third-party modules
import yaml

# NOC modules
from .base import DataConfigBackend


@dataclass
class YAMLParams:
    """YAML backend parameters.

    Args:
        path: Path to the YAML configuration file.
    """

    path: Path

    @classmethod
    def from_url(cls, url: str) -> YAMLParams:
        """Parse YAML backend parameters from URL.

        Args:
            url: YAML backend URL.

        Returns:
            Parsed YAML backend parameters.
        """
        parsed = urlparse(url)
        return YAMLParams(path=Path(parsed.path))


class YAMLBackend(DataConfigBackend):
    """Configuration backend backed by a YAML file.

    URL format::

        yaml:///<path>

    The YAML document root must be a mapping. Configuration values are
    accessed using dot-separated keys.
    """

    @cached_property
    def params(self) -> YAMLParams:
        """Return parsed backend parameters.

        Returns:
            YAML backend parameters.
        """
        return YAMLParams.from_url(self.url)

    def get_data(self) -> dict[str, object] | None:
        """Load configuration data from YAML file.

        Returns:
            Parsed configuration mapping or None when the file does not exist
            or does not contain a mapping at the root level.
        """
        params = self.params
        if not params.path.exists():
            return None
        with open(params.path) as fp:
            data = yaml.safe_load(fp)
        if not isinstance(data, dict):
            return None
        return cast(dict[str, object], data)

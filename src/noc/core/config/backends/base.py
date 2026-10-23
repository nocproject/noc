# ----------------------------------------------------------------------
# Base config backend class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

"""Configuration backend base classes.

This module provides the base classes for configuration backends and the
factory function used to create configuration backend instances from URLs.

Configuration backends provide a unified interface for accessing
configuration values regardless of the underlying storage backend.
"""

# Python modules
from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property

# Third-party modules
from gufo.loader import Loader

# NOC modules
from noc.core.typing import SENTINEL


class BaseConfigBackend(ABC):
    """Base class for configuration backend implementations.

    A configuration backend maps hierarchical configuration keys to values
    from a specific backend, such as environment variables, files, or
    external key-value stores.

    Args:
        url: Backend URL used to initialize the backend.
    """

    def __init__(self, url: str) -> None:
        self.url = url

    @abstractmethod
    def get(self, key: str, default: object) -> object:
        """Get configuration value by key.

        Args:
            key: Dot-separated configuration key.
            default: Value returned when the key does not exist.

        Returns:
            Configuration value or default value.
        """


class DataConfigBackend(BaseConfigBackend):
    """Base class for backends providing hierarchical data.

    This class implements configuration lookup for backends which return the
    complete configuration tree as a dictionary.

    The loaded data is cached after the first access.
    """

    @abstractmethod
    def get_data(self) -> dict[str, object] | None:
        """Load configuration data from the backend.

        Returns:
            Configuration data tree or None when data is unavailable.
        """

    @cached_property
    def _data(self) -> dict[str, object] | None:
        return self.get_data()

    def get(self, key: str, default: object) -> object:
        """Get value from hierarchical configuration data.

        The key is interpreted as a dot-separated path. For example,
        ``database.host`` is resolved as ``data["database"]["host"]``.

        Args:
            key: Dot-separated configuration key.
            default: Value returned when the key does not exist.

        Returns:
            Configuration value or default value.
        """
        data = self._data
        if not data:
            return default
        value: object = data
        for part in key.split("."):
            if not isinstance(value, dict):
                return default
            value = value.get(part, SENTINEL)
            if value is SENTINEL:
                return default

        return value


def from_url(url: str) -> BaseConfigBackend:
    """Create configuration backend instance from URL.

    The backend scheme is used to locate the corresponding implementation.
    For example, ``yaml://...`` creates an instance of the YAML configuration
    backend.

    Args:
        url: Configuration backend URL.

    Returns:
        Initialized configuration backend instance.

    Raises:
        ValueError: If the backend scheme is not registered.
    """
    name = url.split(":", 1)[0]
    try:
        kls = loader[name]
    except KeyError as e:
        msg = f"invalid backend: {name}"
        raise ValueError(msg) from e
    return kls(url)


loader = Loader[type[BaseConfigBackend]](base="noc.core.config.backends", exclude=["base"])

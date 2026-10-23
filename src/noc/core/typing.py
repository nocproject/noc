# ----------------------------------------------------------------------
# typing definitions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
Attributes:
    SENTINEL: A unique sentinel object used to distinguish missing values
        from values explicitly stored as None or other valid values.
"""

# Python modules
from typing import Any, Protocol

# Third-party modules
from bson import ObjectId


class _Sentinel:
    """Sentinel object implementation."""

    def __repr__(self) -> str:
        """Return the sentinel representation.

        Returns:
            String representation of the sentinel object.
        """
        return "SENTINEL"


SENTINEL = _Sentinel()


class SupportsGetById(Protocol):
    """
    Defines get_by_id method
    """

    @classmethod
    def get_by_id(cls, id: int | ObjectId | str) -> Any:  # -> Self
        ...


class AsResource(Protocol):
    """
    Defines as_resource method, which convert
    an instance or its part to a resource reference.
    """

    def as_resource(self, path: str | None = None) -> str: ...


class SupportsStr(Protocol):
    """
    Defines `__str__` function and supports `str()`
    """

    def __str__(self) -> str: ...

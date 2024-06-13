# ----------------------------------------------------------------------
# typing definitions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Union, Protocol, Optional

# Third-party modules
from bson import ObjectId


class SupportsGetById(Protocol):
    """
    Defines get_by_id method
    """

    @classmethod
    def get_by_id(cls, id: Union[int, ObjectId, str]) -> Any:  # -> Self
        ...


class AsResource(Protocol):
    """
    Defines as_resource method, which convert
    an instance or its part to a resource reference.
    """

    def as_resource(self, path: Optional[str] = None) -> str: ...

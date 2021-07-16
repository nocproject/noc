# ----------------------------------------------------------------------
# typing definitions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Union, Protocol

# Third-party modules
from bson import ObjectId


class SupportsGetById(Protocol):
    @classmethod
    def get_by_id(self, id: Union[int, ObjectId, str]) -> Any:  # -> Self
        ...

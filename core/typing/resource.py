# ----------------------------------------------------------------------
# AsResource protocol
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Protocol, Optional


class AsResource(Protocol):
    """
    Defines as_resource method, which convert
    an instance or its part to a resource reference.
    """

    def as_resource(self, path: Optional[str] = None) -> str: ...

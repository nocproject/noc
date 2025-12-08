# ----------------------------------------------------------------------
# GetCssClass protocol
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 Gufo Labs
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Protocol, Optional, runtime_checkable


@runtime_checkable
class GetCssClass(Protocol):
    """
    Get styling info.

    - get_css_class() - Get item style's css class name.
    """

    def get_css_class(self) -> Optional[str]: ...

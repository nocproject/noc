# ----------------------------------------------------------------------
# BaseCollator class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any

# NOC modules
from noc.core.profile.base import BaseProfile
from .typing import PortItem


class BaseCollator:
    def __init__(self, profile: BaseProfile | None) -> None:
        self.profile = profile

    def collate(self, physical_port: PortItem, interfaces: dict[str, Any]) -> str | None:
        raise NotImplementedError

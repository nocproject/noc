# ----------------------------------------------------------------------
# BaseCollator class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Optional, Any

# NOC modules
from noc.core.profile.base import BaseProfile
from .typing import PortItem


class BaseCollator(object):
    def __init__(self, profile: Optional[BaseProfile]):
        self.profile = profile

    def collate(self, physical_port: PortItem, interfaces: Dict[str, Any]) -> Optional[str]:
        raise NotImplementedError

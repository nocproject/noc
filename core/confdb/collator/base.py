# ----------------------------------------------------------------------
# BaseCollator class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from typing import Dict, Optional

# NOC modules
from noc.inv.models.interface import Interface
from noc.core.profile.base import BaseProfile


class BaseCollator(object):
    def __init__(self, profile: Optional[BaseProfile]):
        self.profile = profile

    def collate(self, physical_path: str, interfaces: Dict[str, Interface]) -> Optional[str]:
        raise NotImplementedError

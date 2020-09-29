# ----------------------------------------------------------------------
# IfPathCollator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.core.confdb.collator.base import BaseCollator

logger = logging.getLogger(__name__)


class HuaweiMgmgIfCollator(BaseCollator):
    def collate(self, physical_path, interfaces):
        logger.debug("Collate Management interface: %s", physical_path)
        if physical_path[-1].connection.name == "MEth0/0/1":
            return "M-Ethernet0/0/1"

# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Caps check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import ujson
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck


class CapsCheck(DiscoveryCheck):
    """
    Version discovery
    """
    name = "caps"
    required_script = "get_capabilities"

    def handler(self):
        self.logger.info("Checking capabilities")
        result = self.object.scripts.get_capabilities()
        self.logger.debug("Received capabilities: \n%s",
                          ujson.dumps(result, indent=4))
        self.update_caps(result, source="caps")

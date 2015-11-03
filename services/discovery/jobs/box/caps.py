# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Caps check
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
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
        self.logger.info("Received capabilities: %s", result)
        self.object.update_caps(result)

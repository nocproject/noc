# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Config check
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck


class ConfigCheck(DiscoveryCheck):
    """
    Version discovery
    """
    name = "caps"
    required_script = "get_config"

    def handler(self):
        self.logger.info("Checking config")
        result = self.object.scripts.get_config()
        self.object.save_config(result)

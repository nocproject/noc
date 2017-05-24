# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HouseKeeping check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.handler import get_handler


class HouseKeepingCheck(DiscoveryCheck):
    """
    Housekeeping
    """
    name = "hk"

    def handler(self):
        if self.object.object_profile.hk_handler:
            handler = get_handler(self.object.object_profile.hk_handler)
            if handler:
                self.logger.info("Running housekeeping")
                handler(self)
            else:
                self.logger.info("Invalid handler: %s", self.object.object_profile.hk_handler)
        else:
            self.logger.info("No housekeeping handler, ignoring")

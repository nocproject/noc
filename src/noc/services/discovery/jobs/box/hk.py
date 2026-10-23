# ---------------------------------------------------------------------
# HouseKeeping check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck


class HouseKeepingCheck(DiscoveryCheck):
    """
    Housekeeping
    """

    name = "hk"

    def handler(self):
        if self.object.object_profile.hk_handler:
            if self.object.object_profile.hk_handler.allow_housekeeping:
                handler = self.object.object_profile.hk_handler.get_handler()
                self.logger.info("Running housekeeping")
                handler(self)
            else:
                self.logger.info("Invalid handler: %s", self.object.object_profile.hk_handler)
        else:
            self.logger.info("No housekeeping handler, ignoring")

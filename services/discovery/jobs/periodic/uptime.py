# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Uptime check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.fm.models.uptime import Uptime
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck


class UptimeCheck(DiscoveryCheck):
    """
    Uptime discovery
    """
    name = "uptime"
    required_script = "get_uptime"

    def handler(self):
        self.logger.debug("Checking uptime")
        uptime = self.object.scripts.get_uptime()
        self.logger.debug("Received uptime: %s", uptime)
        if uptime:
            r = Uptime.register(self.object, uptime)
            if not r:
                self.set_artefact("reboot", True)

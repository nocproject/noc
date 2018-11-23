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
        sections = self.object.object_profile.caps_profile.get_sections(
            self.object.object_profile,
            self.object.segment.profile
        )
        self.logger.info("Checking capabilities: %s", ", ".join(sections))
        result = self.object.scripts.get_capabilities(only=sections)
        self.logger.debug("Received capabilities: \n%s",
                          ujson.dumps(result, indent=4))
        self.update_caps(result, source="caps")

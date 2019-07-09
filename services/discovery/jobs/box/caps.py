# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Caps check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import ujson

# NOC modules
from noc.services.discovery.jobs.base import PolicyDiscoveryCheck


class CapsCheck(PolicyDiscoveryCheck):
    """
    Version discovery
    """

    name = "caps"
    required_script = "get_capabilities"

    LLDP_QUERY = "Match('system', 'protocols', 'lldp', 'interface')"
    CDP_QUERY = "Match('system', 'protocols', 'cdp', 'interface')"
    UDLD_QUERY = "Match('system', 'protocols', 'udld', 'interface')"

    def handler(self):
        self.sections = self.object.object_profile.caps_profile.get_sections(
            self.object.object_profile, self.object.segment.profile
        )
        self.logger.info("Checking capabilities: %s", ", ".join(self.sections))
        result = self.get_data()
        if result is None:
            self.logger.error("Failed to get capabilities")
            return
        self.logger.debug("Received capabilities: \n%s", ujson.dumps(result, indent=4))
        self.update_caps(result, source="caps")

    def get_policy(self):
        return self.object.get_caps_discovery_policy()

    def get_data_from_script(self):
        return self.object.scripts.get_capabilities(only=self.sections)

    def get_data_from_confdb(self):
        caps = {}
        if self.is_requested("lldp") and self.confdb_has_lldp():
            caps["Network | LLDP"] = True
        if self.is_requested("cdp") and self.confdb_has_cdp():
            caps["Network | CDP"] = True
        if self.is_requested("udld") and self.confdb_has_udld():
            caps["Network | UDLD"] = True
        return caps

    def is_requested(self, section):
        """
        Check if section is requested
        :param section:
        :return:
        """
        if self.sections:
            return section in self.sections
        return True

    def confdb_has_lldp(self):
        return any(self.confdb.query(self.LLDP_QUERY))

    def confdb_has_cdp(self):
        return any(self.confdb.query(self.CDP_QUERY))

    def confdb_has_udld(self):
        return any(self.confdb.query(self.UDLD_QUERY))

# ---------------------------------------------------------------------
# Caps check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import orjson

# NOC modules
from noc.services.discovery.jobs.base import PolicyDiscoveryCheck
from noc.core.comp import DEFAULT_ENCODING


class CapsCheck(PolicyDiscoveryCheck):
    """
    Version discovery
    """

    name = "caps"
    required_script = "get_capabilities"

    LLDP_QUERY = "Match('protocols', 'lldp', 'interface', X)"
    CDP_QUERY = "Match('protocols', 'cdp', 'interface', X)"
    UDLD_QUERY = "Match('protocols', 'udld', 'interface', X)"
    STP_QUERY = "Match('protocols', 'stp', 'interface', X)"
    LACP_QUERY = "Match('protocols', 'lacp', 'interface', X)"
    LDP_QUERY = """Match('virtual-router', VR, 'forwarding-instance', FI, 'protocols', 'ldp', 'interface', X)"""
    OSPF_QUERY = """Match('virtual-router', VR, 'forwarding-instance', FI, 'protocols', 'ospf', 'interface', X)"""

    #
    ATTR_CAPS = {
        "Serial Number": "Chassis | Serial Number",
        "Boot PROM": "Chassis | Boot PROM",
        "HW version": "Chassis | HW Version",
        "Build": "Software | Build Version",
        "Patch Version": "Software | Patch Version",
    }

    def handler(self):
        self.sections = self.object.object_profile.caps_profile.get_sections(
            self.object.object_profile, self.object.segment.profile
        )
        self.logger.info("Checking capabilities: %s", ", ".join(self.sections))
        result = self.get_data()
        if result is None:
            self.logger.error("Failed to get capabilities")
        else:
            self.logger.debug(
                "Received capabilities: \n%s",
                orjson.dumps(result, option=orjson.OPT_INDENT_2).decode(DEFAULT_ENCODING),
            )
            self.update_caps(result, source="discovery")
        object_attrs = self.get_artefact("object_attributes")
        if object_attrs is None:
            return
        object_caps = {}
        for k, v in object_attrs.items():
            if k in self.ATTR_CAPS:
                caps = self.ATTR_CAPS[k]
            else:
                # Custom Attributes
                caps = f"Custom | Attribute | {k}"
                self.logger.info("Custom attribute: %s, Use caps: %s", k, caps)
            object_caps[caps] = v
        self.update_caps(object_caps, source="database")

    def get_policy(self):
        return self.object.get_caps_discovery_policy()

    def get_data_from_script(self):
        return self.object.scripts.get_capabilities(only=self.sections)

    def get_data_from_confdb(self):
        self.logger.debug("Filling capabilities from ConfDB")
        caps = {}
        if self.is_requested("lldp") and self.confdb_has_lldp():
            caps["Network | LLDP"] = True
        if self.is_requested("cdp") and self.confdb_has_cdp():
            caps["Network | CDP"] = True
        if self.is_requested("stp") and self.confdb_has_stp():
            caps["Network | STP"] = True
        if self.is_requested("udld") and self.confdb_has_udld():
            caps["Network | UDLD"] = True
        if self.is_requested("lacp") and self.confdb_has_lacp():
            caps["Network | LACP"] = True
        if self.is_requested("ldp") and self.confdb_has_ldp():
            caps["Network | LDP"] = True
        if self.is_requested("ospf") and self.confdb_has_ospf():
            caps["Network | OSFP | v2"] = True
        if self.object.get_caps_discovery_policy() in {"C", "S"} and set(
            self.sections
        ).intersection({"snmp", "snmp_v1", "snmp_v2c"}):
            # Filling SNMP caps.
            self.logger.debug("Filling SNMP capabilities from script")
            r = self.object.scripts.get_capabilities(
                only=list(set(self.sections).intersection({"snmp", "snmp_v1", "snmp_v2c"}))
            )
            if r is not None:
                self.logger.error("Failed to get SNMP capabilities")
                caps.update(r)
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

    def confdb_has_stp(self):
        return any(self.confdb.query(self.STP_QUERY))

    def confdb_has_udld(self):
        return any(self.confdb.query(self.UDLD_QUERY))

    def confdb_has_lacp(self):
        return any(self.confdb.query(self.LACP_QUERY))

    def confdb_has_ldp(self):
        return any(self.confdb.query(self.LDP_QUERY))

    def confdb_has_ospf(self):
        return any(self.confdb.query(self.OSPF_QUERY))

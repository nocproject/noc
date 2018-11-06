# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC
from noc.core.mib import mib


class Script(BaseScript):
    name = "Generic.get_chassis_id"
    cache = True
    interface = IGetChassisID
    # OIDS to get MACs via SNMP GET
    # capability -> [oid, ...]
    SNMP_GET_OIDS = {
        "SNMP": [
            mib["BRIDGE-MIB::dot1dBaseBridgeAddress", 0]
        ],
        "Network | LLDP": [
            mib["LLDP-MIB::lldpLocChassisId", 0]
        ]
    }
    # OIDS to get MACs via SNMP GETNEXT request
    # capability -> [oid, ...]
    SNMP_GETNEXT_OIDS = {}
    #
    IGNORED_MACS = {
        "00:00:00:00:00:00",  # Empty MAC
        "FF:FF:FF:FF:FF:FF"  # Broadcast
    }

    def execute_snmp(self):
        macs = set()
        # Process SNMP GET
        oids = self.get_snmp_get_oids()
        if oids:
            r = self.snmp.get(dict(zip(oids, oids)))
            for k in r:
                v = r[k]
                if v:
                    try:
                        macs.add(MAC(v))
                    except ValueError:
                        pass
        # Process SNMP GETNEXT requests
        oids = self.get_snmp_getnext_oids()
        for oid in oids:
            for k, v in self.snmp.getnext(oid):
                if v:
                    try:
                        macs.add(MAC(v))
                    except ValueError:
                        pass
        # Filter and convert macs
        return [{
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        } for mac in sorted(macs) if not self.is_ignored_mac(mac)]

    def get_oids_by_caps(self, oids_map):
        """
        Process caps -> [oid, ...] mappings
        :param oids_map:
        :return:
        """
        oids = set()
        for cap in oids_map:
            if cap in self.capabilities:
                oids.update(oids_map[cap])
        return list(oids)

    def get_snmp_get_oids(self):
        """
        Get list of SNMP GET oids to request MAC addresses.
        Can be overriden
        :return:
        """
        return self.get_oids_by_caps(self.SNMP_GET_OIDS)

    def get_snmp_getnext_oids(self):
        """
        Get list of SNMP GET oids to request MAC addresses.
        Can be overriden
        :return:
        """
        return self.get_oids_by_caps(self.SNMP_GETNEXT_OIDS)

    def is_ignored_mac(self, mac):
        """
        Check if MAC address should be ignored
        :param mac: Normalized MAC address
        :return: True if MAC should be ignored
        """
        if mac in self.IGNORED_MACS:
            return True
        # Multicast addresses has 0-bit of first octet set to 1
        if int(mac.split(":", 1)[0]) & 0x1:
            return True
        # Address is allowed
        return False

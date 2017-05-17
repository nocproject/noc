# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Suggest SNMP check check
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.service.client import open_sync_rpc, RPCError
from noc.lib.mib import mib


class SuggestSNMPCheck(DiscoveryCheck):
    """
    Version discovery
    """
    name = "suggest_snmp"

    CHECK_OIDS = [
        mib["SNMPv2-MIB::sysObjectID.0"],
        mib["SNMPv2-MIB::sysUpTime.0"],
        mib["SNMPv2-MIB::sysDescr.0"]
    ]

    def handler(self):
        if not self.object.auth_profile or not self.object.auth_profile.enable_suggest:
            return
        self.object._suggest_snmp = None
        for oid in self.CHECK_OIDS:
            for ro, rw in self.object.auth_profile.iter_snmp():
                if self.check_oid(oid, ro):
                    self.logger.info("Guessed community: %s", ro)
                    self.object._suggest_snmp = (ro, rw)
                    return
        self.logger.info("Failed to guess SNMP community")
        self.set_problem("Failed to guess SNMP community")

    def check_oid(self, oid, community):
        """
        Perform SNMP v2c GET. Param is OID or symbolic name
        """
        self.logger.info("Trying community '%s': %s", community, oid)
        try:
            r = open_sync_rpc(
                "activator",
                pool=self.object.pool.name,
                calling_service="discovery"
            ).snmp_v2c_get(
                self.object.address,
                community,
                oid
            )
            self.logger.info("Result: %s", r)
            return r is not None
        except RPCError as e:
            self.logger.debug("RPC Error: %s", e)
            return False

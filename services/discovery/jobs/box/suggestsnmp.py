# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Suggest SNMP check check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.service.client import open_sync_rpc, RPCError
from noc.core.snmp.version import SNMP_v1, SNMP_v2c
from noc.core.mib import mib


class SuggestSNMPCheck(DiscoveryCheck):
    """
    Version discovery
    """
    name = "suggest_snmp"

    # %fixme have to be configured ?

    CHECK_OIDS = [
        mib["SNMPv2-MIB::sysObjectID.0"],
        mib["SNMPv2-MIB::sysUpTime.0"],
        mib["SNMPv2-MIB::sysDescr.0"]
    ]

    CHECK_VERSION = {SNMP_v1: "snmp_v2c_get",
                     SNMP_v2c: "snmp_v1_get"}

    def handler(self):
        if not self.object.auth_profile or not self.object.auth_profile.enable_suggest:
            return
        self.object._suggest_snmp = None
        for oid in self.CHECK_OIDS:
            for ro, rw in self.object.auth_profile.iter_snmp():
                for ver in sorted(self.CHECK_VERSION):
                    if self.check_oid(oid, ro, self.CHECK_VERSION[ver]):
                        self.logger.info("Guessed community: %s, version: %d", ro, ver)
                        self.object._suggest_snmp = (ro, rw, self.CHECK_VERSION[ver])
                        self.set_credentials(
                            snmp_ro=ro,
                            snmp_rw=rw
                        )
                        return
        self.logger.info("Failed to guess SNMP community")
        self.set_problem(
            alarm_class="Discovery | Guess | SNMP Community",
            message="Failed to guess SNMP community",
            fatal=True
        )

    def check_oid(self, oid, community, version="snmp_v2c_get"):
        """
        Perform SNMP v2c GET. Param is OID or symbolic name
        """
        self.logger.info("Trying community '%s': %s, version: %s", community, oid, version)
        try:
            r = open_sync_rpc(
                "activator",
                pool=self.object.pool.name,
                calling_service="discovery"
            ).__getattr__(version)(
                self.object.address,
                community,
                oid
            )
            self.logger.info("Result: %s", r)
            return r is not None
        except RPCError as e:
            self.logger.debug("RPC Error: %s", e)
            return False

    def set_credentials(self, snmp_ro, snmp_rw):
        self.logger.info("Setting credentials")
        self.object.snmp_ro = snmp_ro
        self.object.snmp_rw = snmp_rw
        # Reset auth profile to continue operations with new credentials
        self.object.auth_profile = None
        self.object.save()
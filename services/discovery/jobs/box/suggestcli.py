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


class SuggestCLICheck(DiscoveryCheck):
    """
    Version discovery
    """
    name = "suggest_cli"
    required_script = "login"

    def handler(self):
        if not self.object.auth_profile or not self.object.auth_profile.enable_suggest:
            return
        if self.object.profile_name == "Generic.Host":
            self.logger.info("Profile is not detected properly. Skipping")
            return
        for user, password, super_password in self.object.auth_profile.iter_cli():
            if self.check_login(user, password, super_password):
                if self.object._suggest_snmp:
                    ro, rw = self.object._suggest_snmp
                else:
                    ro, rw = None, None
                self.set_credentials(
                    user=user,
                    password=password,
                    super_password=super_password,
                    snmp_ro=ro,
                    snmp_rw=rw
                )
                return
        self.logger.info("Failed to guess CLI credentials")
        self.set_problem("Failed to guess CLI credentials")

    def check_login(self, user, password, super_password):
        self.logger.info("Checking %s/%s/%s", user, password, super_password)
        try:
            r = open_sync_rpc(
                "activator",
                pool=self.object.pool.name,
                calling_service="discovery"
            ).script(
                "%s.login" % self.object.profile_name,
                {
                    "cli_protocol": "ssh" if self.object.scheme == 2 else "telnet",
                    "address": self.object.address,
                    "user": user,
                    "password": password,
                    "super_password": super_password,
                    "path": None
                }
            )
            self.logger.info("Result: %s", r)
            return bool(r)  # bool(False) == bool(None)
        except RPCError as e:
            self.logger.debug("RPC Error: %s", e)
            return False

    def set_credentials(self, user, password, super_password,
                        snmp_ro, snmp_rw):
        self.logger.info("Setting credentials")
        self.object.user = user
        self.object.password = password
        self.object.super_password = super_password
        self.object.snmp_ro = snmp_ro
        self.object.snmp_rw = snmp_rw
        # Reset auth profile to continue operations with new credentials
        self.object.auth_profile = None
        self.object.save()

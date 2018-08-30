# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Resolver check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck


class ResolverCheck(DiscoveryCheck):
    """
    Version discovery
    """
    name = "resolver"

    def handler(self):
        fqdn = self.object.get_full_fqdn()
        self.logger.info("Resolving %s", fqdn)
        address = self.object.resolve_fqdn()
        if not address:
            self.logger.info("Failed to resolve")
            self.set_problem(
                alarm_class="Discovery | Error | Unhandled Exception",
                message="Failed to resolve fqdn %s" % fqdn,
                fatal=True
            )
            return
        if address == self.object.address:
            self.logger.info("Confirmed address %s", address)
            # If policy set once and address == self.object.address, check is not disabled
            return
        policy = self.object.get_address_resolution_policy()
        self.logger.info("Changing address to %s", address)
        self.object.address = address
        if policy == "O":  # Once
            self.object.address_resolution_policy = "D"  # Disable
        self.object.save()

    def is_enabled(self):
        if not super(ResolverCheck, self).is_enabled():
            return False
        if not self.object.fqdn:
            self.logger.info("FQDN field is empty")
            return False
        return self.object.get_address_resolution_policy() in ("E", "O")

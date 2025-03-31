# ---------------------------------------------------------------------
# Resolver check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.wf.diagnostic import RESOLVER_DIAG, DiagnosticState


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
                message=f"Failed to resolve fqdn {fqdn}",
                fatal=True,
                diagnostic=RESOLVER_DIAG,
            )
        if address == self.object.address:
            self.logger.info("Confirmed address %s", address)
            # If policy set once and address == self.object.address, check is not disabled
            return
        policy = self.object.get_address_resolution_policy()
        self.logger.info("Changing address to %s", address)
        self.object.address = address
        if address and policy == "O":  # Once
            self.object.address_resolution_policy = "D"  # Disable
        self.object.save()

    def is_enabled(self):
        if not super().is_enabled():
            return False
        if not self.object.fqdn:
            self.logger.info("FQDN field is empty")
            return False
        return self.object.diagnostic[RESOLVER_DIAG].state != DiagnosticState.blocked

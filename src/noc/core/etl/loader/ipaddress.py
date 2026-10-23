# ----------------------------------------------------------------------
# IP Address Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.ipaddress import IPAddress
from noc.ip.models.address import Address


class IPAddressLoader(BaseLoader):
    """
    IP Address loader
    """

    name = "ipaddress"
    model = Address
    data_model = IPAddress
    ignore_unique = {"bi_id", "ipv6_transition"}
    unique_index = ("vrf", "afi", "address")

    workflow_delete_event = "remove"
    workflow_state_sync = True

    def purge(self):
        """
        Perform pending deletes
        """
        for r_id, msg in reversed(self.pending_deletes):
            self.logger.debug("Deactivating: %s", msg)
            self.c_delete += 1
            try:
                obj = self.model.objects.get(pk=self.mappings[r_id])
                obj.fire_event("expired")
            except self.model.DoesNotExist:
                pass  # Already deleted
        self.pending_deletes = []

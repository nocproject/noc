# ----------------------------------------------------------------------
# IP VRF Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db.models.query_utils import Q

# NOC modules
from .base import BaseLoader
from ..models.ipprefix import IPPrefix
from noc.ip.models.prefix import Prefix


class IPPrefixLoader(BaseLoader):
    """
    IP Prefix Loader
    """

    name = "ipprefix"
    model = Prefix
    data_model = IPPrefix
    ignore_unique = {"bi_id", "ipv6_transition"}

    workflow_delete_event = "remove"
    workflow_state_sync = True
    unique_index = ("vrf", "afi", "prefix")

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

# ---------------------------------------------------------------------
# UDLD check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.discoveryid import DiscoveryID


class UDLDCheck(TopologyDiscoveryCheck):
    """
    UDLD Topology discovery
    """

    name = "udld"
    required_script = "get_udld_neighbors"
    required_capabilities = ["Network | UDLD"]

    def iter_neighbors(self, mo):
        result = mo.scripts.get_udld_neighbors()
        d = DiscoveryID.objects.filter(object=self.object.id).first()
        local_id = d.udld_id if d and d.udld_id else None
        for n in result:
            if local_id != n["local_device"]:
                DiscoveryID.update_udld_id(self.object, n["local_device"])
                local_id = n["local_device"]
            yield (n["local_interface"], n["remote_device"], n["remote_interface"])

    def get_neighbor(self, device_id):
        r = DiscoveryID.get_by_udld_id(device_id)
        if r:
            return ManagedObject.get_by_id(r["object"])
        return None

# ---------------------------------------------------------------------
# CDP check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck
from noc.inv.models.interface import Interface
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.validators import is_ipv4, is_mac


class CDPCheck(TopologyDiscoveryCheck):
    """
    CDP Topology discovery
    """

    name = "cdp"
    required_script = "get_cdp_neighbors"
    required_capabilities = ["Network | CDP"]

    RESERVED_NAMES = {"Switch", "Router", "MikroTik"}

    def iter_neighbors(self, mo):
        result = mo.scripts.get_cdp_neighbors()
        for n in result["neighbors"]:
            device_id = n["device_id"]
            if device_id in self.RESERVED_NAMES and n.get("remote_ip"):
                device_id = n["remote_ip"]
            yield n["local_interface"], device_id, n["remote_interface"]

    def get_remote_interface(self, remote_object, port_id: str):
        # Try interface name
        try:
            n_port = remote_object.get_profile().convert_interface_name(port_id)
            i = (
                Interface.objects.filter(managed_object=remote_object.id, name=n_port)
                .read_preference(ReadPreference.SECONDARY_PREFERRED)
                .first()
            )
            if i:
                return i.name
            for p in remote_object.get_profile().get_interface_names(n_port):
                i = (
                    Interface.objects.filter(managed_object=remote_object.id, name=p)
                    .read_preference(ReadPreference.SECONDARY_PREFERRED)
                    .first()
                )
                if i:
                    return i.name
        except InterfaceTypeError:
            pass
        # Unable to decode
        self.logger.info("Unable to decode local subtype port id %s at %s", port_id, remote_object)
        return None

    def get_neighbor(self, n):
        nn = self.get_neighbor_by_hostname(n)
        if nn:
            return nn
        if is_ipv4(n):
            return self.get_neighbor_by_ip(n)
        if is_mac(n):
            return self.get_neighbor_by_mac(n)
        return None

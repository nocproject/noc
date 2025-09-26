# ----------------------------------------------------------------------
# NRI Topology check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck
from noc.inv.models.extnrilink import ExtNRILink
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface


class NRICheck(TopologyDiscoveryCheck):
    """
    Network Resource Inventory Topology Discovery
    Maps NRI port name to local interface
    """

    name = "nri"
    aliased_names_only = True

    def handler(self):
        self.logger.info("NRI Topology")
        if not self.object.remote_system:
            self.logger.info("Created directly. No NRI integration. Skipping check")
            return None
        # Bulk interface aliasing
        self.seen_neighbors = set()
        # Actual discovery
        return super().handler()

    def iter_neighbors(self, mo):
        self.set_nri_aliases(mo)
        for d in (
            ExtNRILink._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .find({"$or": [{"src_mo": mo.id}, {"dst_mo": mo.id}]})
        ):
            if d.get("ignored"):
                continue
            if d["src_mo"] == mo.id:
                yield d["src_interface"], d["dst_mo"], d["dst_interface"]
            elif d["dst_mo"] == mo.id:
                yield d["dst_interface"], d["src_mo"], d["src_interface"]

    def get_neighbor(self, n):
        return ManagedObject.get_by_id(n)

    def get_remote_interface(self, remote_object, remote_interface):
        """
        Real values are set by set_interface alias
        :param remote_object:
        :param remote_interface:
        :return:
        """
        return remote_interface

    def set_nri_aliases(self, mo):
        """
        Fill interface alias cache with nri names
        :param mo:
        :return:
        """
        if mo in self.seen_neighbors:
            return
        seen = False
        for d in (
            Interface._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .find(
                {"managed_object": mo.id, "nri_name": {"$exists": True}},
                {"_id": 0, "name": 1, "nri_name": 1},
            )
        ):
            self.set_interface_alias(mo, d["name"], d["nri_name"])
            seen = True
        self.seen_neighbors.add(mo)
        if not seen:
            self.logger.info(
                "[%s] Object has no nri interface name. Topology may be incomplete", mo.name
            )

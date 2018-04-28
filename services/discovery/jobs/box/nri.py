# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NRI Portmapper check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

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

    def handler(self):
        self.logger.info("NRI Topology")
        if not self.object.remote_system:
            self.logger.info("Created directly. No NRI integration. Skipping check")
            return
        # Check object has interfaces
        if self.has_capability("DB | Interfaces"):
            self.logger.info(
                "No interfaces discovered. "
                "Skipping interface status check"
            )
            return
        # managed object -> nri_name -> name
        self.remote_interfaces = {}
        return super(NRICheck, self).handler()

    def iter_neighbors(self, mo):
        for d in ExtNRILink._get_collection().find({
            "$or": [
                {"src_mo": mo.id},
                {"dst_mo": mo.id}
            ]
        }):
            if d.get("ignored"):
                continue
            if d["src_mo"] == mo.id:
                yield d["src_iface"], d["dst_mo"], d["dst_iface"]
            elif d["dst_mo"] == mo.id:
                yield d["dst_iface"], d["src_mo"], d["src_iface"]

    def get_neighbor(self, n):
        return ManagedObject.get_by_id(n)

    def get_remote_interface(self, remote_object, remote_interface):
        """
        Return normalized remote interface name
        May return aliases name which can be finally resolved
        during clean interface
        """
        if remote_object not in self.remote_interfaces:
            self.remote_interfaces[remote_object] = dict(
                (d["nri_name"], d["name"])
                for d in Interface._get_collection().find({
                    "managed_object": remote_object.id,
                    "nri_name": {
                        "$exists": True
                    }
                })
            )
        return self.remote_interfaces[remote_object].get(remote_interface)

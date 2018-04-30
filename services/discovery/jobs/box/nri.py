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
        if not self.has_capability("DB | Interfaces"):
            self.logger.info(
                "No interfaces discovered. "
                "Skipping interface status check"
            )
            return
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
                iface = Interface.objects.filter(managed_object=mo, nri_name=d["src_interface"]).first()
                self.set_interface_alias(mo, iface.name, d["src_interface"])
                yield d["src_interface"], d["dst_mo"], d["dst_interface"]
            elif d["dst_mo"] == mo.id:
                iface = Interface.objects.filter(managed_object=mo, nri_name=d["dst_interface"]).first()
                self.set_interface_alias(mo, iface.name, d["dst_interface"])
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

# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NRI Portmapper check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.etl.portmapper.loader import loader as portmapper_loader
from noc.inv.models.interface import Interface


class NRIPortmapperCheck(DiscoveryCheck):
    """
    Network Resource Inventory pormapper
    Maps NRI port name to local interface
    """
    name = "nri_portmap"

    def handler(self):
        self.logger.info("NRI Portmapper")
        if not self.object.remote_system:
            self.logger.info("Created directly. No NRI integration. Skipping check")
            return
        nri = self.object.remote_system.name
        # Check object has interfaces
        if self.has_capability("DB | Interfaces"):
            self.logger.info(
                "No interfaces discovered. "
                "Skipping interface status check"
            )
            return
        # Get portmapper instance
        portmapper = portmapper_loader(self.object.remote_system.name)
        if not portmapper:
            self.logger.info("[%s] No portmapper for NRI. Skipping checks", nri)
            return
        # Process interfaces
        bulk = []
        icol = Interface._get_collection()
        for d in icol.find({
            "managed_object": self.object.id,
            "type": "physical"
        }, {
            "_id": 1,
            "name": 1,
            "nri_name": 1
        }):
            nri_name = portmapper.to_remote(d["name"])
            self.logger.debug("[%s] Port mapping %s <-> %s", nri, d["name"], nri_name)
            if not nri_name:
                self.logger.info("[%s] Cannot map port name '%s'", nri, d["name"])
            elif d.get("nri_name") != nri_name:
                self.logger.info("[%s] Mapping '%s' to '%s'", nri, nri_name, d["name"])
                bulk += [UpdateOne({
                    "_id": d["_id"]
                }, {
                    "$set": {
                        "nri_name": nri_name
                    }
                })]
        if bulk:
            self.logger.info("Sending %d updates", len(bulk))
            icol.bulk_write(bulk)

# ----------------------------------------------------------------------
# NRI Portmapper check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne
from collections import namedtuple

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.etl.portmapper.loader import loader as portmapper_loader
from noc.inv.models.interface import Interface

IFHint = namedtuple("IFHint", ("name", "ifindex"))


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
        if not self.has_capability("DB | Interfaces"):
            self.logger.info("No interfaces discovered. " "Skipping interface status check")
            return
        # Get portmapper instance
        pm_cls = portmapper_loader[self.object.remote_system.name]
        if not pm_cls:
            self.logger.info("[%s] No portmapper for NRI. Skipping checks", nri)
            return
        portmapper = pm_cls(self.object)
        # Process interfaces
        bulk = []
        icol = Interface._get_collection()
        ifaces_hints = tuple(
            IFHint(name=iface["name"], ifindex=iface.get("ifindex"))
            for iface in icol.find(
                {"managed_object": self.object.id, "type": {"$in": ["physical", "virtual"]}},
                {"_id": 1, "name": 1, "ifindex": 1},
            )
        )
        for d in icol.find(
            {"managed_object": self.object.id, "type": {"$in": ["physical", "virtual"]}},
            {"_id": 1, "name": 1, "nri_name": 1},
        ):
            try:
                nri_name = portmapper.to_remote(d["name"], iface_hints=ifaces_hints)
            except Exception as e:
                self.logger.error(
                    "[%s] Unhandled exception on portmapper handler '%s'. Skipping checks.", nri, e
                )
                break
            self.logger.debug("[%s] Port mapping %s <-> %s", nri, d["name"], nri_name)
            if not nri_name:
                self.logger.info("[%s] Cannot map port name '%s'", nri, d["name"])
                if d.get("nri_name"):
                    bulk += [UpdateOne({"_id": d["_id"]}, {"$unset": {"nri_name": 1}})]
            elif d.get("nri_name") != nri_name:
                self.logger.info("[%s] Mapping '%s' to '%s'", nri, nri_name, d["name"])
                bulk += [UpdateOne({"_id": d["_id"]}, {"$set": {"nri_name": nri_name}})]
        if bulk:
            self.logger.info("Sending %d updates", len(bulk))
            icol.bulk_write(bulk)

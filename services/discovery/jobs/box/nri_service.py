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
from noc.sa.models.serviceprofile import ServiceProfile
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.sa.models.service import Service
from noc.inv.models.interface import Interface


class NRIServiceCheck(DiscoveryCheck):
    """
    Network Resource Inventory service mapper
    Maps NRI service to local interface
    """

    name = "nri_service"

    def handler(self):
        self.logger.info("NRI Service Mapper")
        if not self.object.remote_system:
            self.logger.info("Created directly. No NRI integration. Skipping check")
            return
        if not self.object.remote_system.enable_link:
            self.logger.info(
                "NRI does not provide link information. Skipping check", self.object.remote_system
            )
            return
        # Check object has interfaces
        if not self.has_capability("DB | Interfaces"):
            self.logger.info("No interfaces discovered. " "Skipping interface status check")
            return
        # Get services related to Managed object
        scol = Service._get_collection()
        slist = [
            s
            for s in scol.find(
                {"managed_object": self.object.id, "nri_port": {"$exists": True}},
                {"_id": 1, "nri_port": 1, "profile": 1},
            )
        ]
        # nri_port -> service_id
        smap = dict((s["nri_port"], s["_id"]) for s in slist)
        # service id -> service profile
        prof_map = dict((s["_id"], ServiceProfile.get_by_id(s["profile"])) for s in slist)
        icol = Interface._get_collection()
        nmap = {}
        bulk = []
        for i in icol.find({"managed_object": self.object.id, "nri_name": {"$exists": True}}):
            if not i.get("nri_name"):
                continue
            if i["nri_name"] in smap:
                svc = smap[i["nri_name"]]
                p = prof_map.get(svc)
                if svc != i.get("service"):
                    self.logger.info("Binding service %s to interface %s", svc, i["name"])
                    op = {"service": svc}
                    if p and p.interface_profile:
                        op["profile"] = p.interface_profile.id
                    bulk += [UpdateOne({"_id": i["_id"]}, {"$set": op})]
                elif p and p.interface_profile and p.interface_profile.id != i["profile"]:
                    self.logger.info(
                        "Replace profile to %s on intertace %s", p.interface_profile, i["name"]
                    )
                    bulk += [
                        UpdateOne({"_id": i["_id"]}, {"$set": {"profile": p.interface_profile.id}})
                    ]
                del smap[i["nri_name"]]
            elif i.get("service"):
                self.logger.info("Removing service %s from interface %s", i["service"], i["name"])
                op = {"$unset": {"service": ""}}
                if i["service"] in prof_map:
                    op["$set"] = {"profile": InterfaceProfile.get_default_profile().id}
                bulk += [UpdateOne({"_id": i["_id"]}, op)]
            nmap[i["nri_name"]] = i
        # Report hanging interfaces
        for n in smap:
            svc = smap[n]
            if n not in nmap:
                self.logger.info("Cannot bind service %s. Cannot find NRI interface %s", svc, n)
                continue
            i = nmap[n]
            self.logger.info("Binding service %s to interface %s", svc, i["name"])
            op = {"service": svc}
            p = prof_map.get(svc)
            if p:
                op["profile"] = p.interface_profile.id
            bulk += [UpdateOne({"_id": i["_id"]}, {"$set": op})]
        if bulk:
            self.logger.info("Sending %d updates", len(bulk))
            icol.bulk_write(bulk)

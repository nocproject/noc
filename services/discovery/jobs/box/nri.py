# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NRI check
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.interface import Interface
from noc.inv.models.extnrilink import ExtNRILink
from noc.sa.models.service import Service
from noc.core.etl.portmapper.loader import loader as portmapper_loader


class NRICheck(DiscoveryCheck):
    """
    Network Resource Inventory integration
    """
    name = "nri"

    def handler(self):
        self.logger.info("NRI integration")
        # Check object has interfaces
        has_interfaces = "DB | Interfaces" in self.object.get_caps()
        if not has_interfaces:
            self.logger.info(
                "No interfaces discovered. "
                "Skipping interface status check"
            )
            return
        # Get NRI portmapper
        src_tags = [t[4:] for t in self.object.tags
                    if t.startswith("src:")]
        if len(src_tags) == 0:
            self.logger.info("Created directly. No NRI integration")
            return
        elif len(src_tags) > 1:
            self.logger.info(
                "Ambiguous NRI information (%s). Skipping checks",
                ", ".join(src_tags)
            )
            return
        self.nri = src_tags[0]
        pm = portmapper_loader.get_loader(self.nri)
        if not pm:
            self.logger.info("No portmapper for %s. Skipping checks",
                             src_tags[0])
            return
        self.portmapper = pm(self.object)
        # Process tasks
        self.process_interfaces()
        self.process_links()
        self.process_services()

    def process_interfaces(self):
        """
        Fill Interface.nri_name
        """
        self.logger.info("Setting NRI names (%s)", self.nri)
        bulk = Interface._get_collection().initialize_unordered_bulk_op()
        n = 0
        for i in Interface._get_collection().find({
                "managed_object": self.object.id,
                "type": "physical",
                "nri_name": {
                    "$exists": False
                }
            },
            {
                "_id": 1,
                "name": 1
            }):
            nri_name = self.portmapper.to_remote(i["name"])
            if not nri_name:
                self.logger.info(
                    "Cannot map interface name '%s' to NRI '%s' (%s)",
                    i["name"], self.object.platform
                )
                continue
            self.logger.info("Mapping %s to %s", i["name"], nri_name)
            bulk.find({"_id": i["_id"]}).update({"$set": {"nri_name": nri_name}})
            n += 1
        if n:
            bulk.execute()

    def process_links(self):
        pass

    def process_services(self):
        """
        Bind services to interfaces
        """
        smap = dict(
            (s["nri_port"], s["_id"])
            for s in Service._get_collection().find({
                "managed_object": self.object.id,
                "nri_name": {
                    "$exists": True
                }
            }, {
                "_id": 1,
                "nri_port": 1
            }))

        nmap = {}
        bulk = Interface._get_collection().initialize_unordered_bulk_op()
        n = 0
        for i in Interface._get_collection().find({
            "managed_object": self.object.id,
            "type": "physical",
            "nri_name": {
                "$exists": True
            }
        }, {
            "_id": 1,
            "name": 1,
            "nri_name": 1,
            "service": 1
        }):
            if i["nri_name"] in smap:
                svc = smap[i["nri_name"]]
                if svc != i["service"]:
                    self.logger.info(
                        "Binding service %s to interface %s",
                        svc, i["name"]
                    )
                    bulk.find({"_id": i["_id"]}).update({
                        "$set": {
                            "service": svc
                        }
                    })
                    n += 1
                del smap[i["nri_name"]]
            else:
                self.logger.info(
                    "Removing service %s from interface %s",
                    i["service"], i["name"]
                )
                bulk.find({"_id": i["_id"]}).update({
                    "$unset": {
                        "service": ""
                    }
                })
                n += 1
            nmap[i["nri_name"]] = i
        for n in smap:
            svc = smap[n]
            if n not in nmap:
                self.logger.info(
                    "Cannot bind service %s. "
                    "Cannot find NRI interface %s",
                    svc, n
                )
                continue
            i = nmap[n]
            self.logger.info(
                "Binding service %s to interface %s",
                svc, i["name"]
            )
            bulk.find({"_id": i["_id"]}).update({
                "$set": {
                    "service": svc
                }
            })
            n += 1
        if n:
            bulk.execute()

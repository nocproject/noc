# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Interface Status check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import threading
# Third-party modules
from pymongo import ReadPreference
from pymongo.errors import BulkWriteError
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile

ips_lock = threading.RLock()


class InterfaceStatusCheck(DiscoveryCheck):
    """
    Interface status discovery
    """
    name = "interfacestatus"
    required_script = "get_interface_status_ex"
    required_capabilities = ["DB | Interfaces"]

    def get_interface_ifindexes(self):
        """
        Populate metrics list with interface metrics
        :return:
        """
        ifindexes = []
        for i in Interface._get_collection().with_options(
                read_preference=ReadPreference.SECONDARY_PREFERRED).find(
                    {"managed_object": self.object.id, "type": "physical", "profile":
                     {"$in": InterfaceProfile.get_with_status_discovery()}},
                    {"_id": 1, "name": 1, "ifindex": 1, "profile": 1}):
            ifindexes += [{"interface": i.get("name"), "ifindex": (i.get("ifindex"))}]
        if not ifindexes:
            self.logger.info("Interface are not configured. Skipping")
            return None
        return ifindexes

    def handler(self):
        def get_interface(name):
            if_name = interfaces.get(name)
            if if_name:
                return if_name
            for iname in self.object.get_profile().get_interface_names(i["interface"]):
                if_name = interfaces.get(iname)
                if if_name:
                    return if_name

            return None

        self.logger.info("Checking interface statuses")
        interfaces = dict(
            (i.name, i) for i in Interface.objects.filter(
                managed_object=self.object.id,
                type="physical",
                profile__in=self.InterfaceProfile.get_with_status_discovery(),
                read_preference=ReadPreference.SECONDARY_PREFERRED
            )
        )
        if not interfaces:
            self.logger.info("No interfaces with status discovery enabled. Skipping")
            return

        ifaces = self.get_interface_ifindexes()
        if ifaces:
            result = self.object.scripts.get_interface_status_ex(interfaces=ifaces)
        else:
            result = self.object.scripts.get_interface_status_ex()
        collection = Interface._get_collection()
        bulk = []
        for i in result:
            iface = get_interface(i["interface"])
            if not iface:
                continue
            kwargs = {
                "admin_status": i.get("admin_status"),
                "full_duplex": i.get("full_duplex"),
                "in_speed": i.get("in_speed"),
                "out_speed": i.get("out_speed"),
                "bandwidth": i.get("bandwidth")
            }
            changes = self.update_if_changed(iface, kwargs, ignore_empty=kwargs.keys(), bulk=bulk)
            self.log_changes("Interface %s status has been changed" % i["interface"], changes)
            ostatus = i.get("oper_status")
            if iface.oper_status != ostatus and ostatus is not None:
                self.logger.info("[%s] set oper status to %s", i["interface"], ostatus)
                iface.set_oper_status(ostatus)
        if bulk:
            self.logger.info("Commiting changes to database")
            try:
                collection.bulk_write(bulk, ordered=False)
                # 1 bulk operations complete in 0ms: inserted=0, updated=1, removed=0
                self.logger.info("Database has been synced")
            except BulkWriteError as e:
                self.logger.error("Bulk write error: '%s'", e.details)

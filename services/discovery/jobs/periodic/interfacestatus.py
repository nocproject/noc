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

    def __init__(self, *args, **kwargs):
        super(InterfaceStatusCheck, self).__init__(*args, **kwargs)
        # self.metrics_artefact = {}  # name -> {name: , admin_status:, oper_status:, duplex_status:, speed:}

    def get_interface_ifindexes(self):
        """
        Populate metrics list with interface metrics
        :return:
        """
        ifindexes = []
        ifnames = {}
        for i in Interface.objects.filter(
                managed_object=self.object.id,
                type="physical",
                ifindex__exists=True,
                profile__in=InterfaceProfile.get_with_status_discovery(),
                read_preference=ReadPreference.SECONDARY_PREFERRED):
            ifindexes += [{"interface": i.name, "ifindex": i.ifindex}]
            ifnames[i.name] = i
        if not ifindexes:
            self.logger.info("No interfaces with status discovery enabled. Skipping")
            return None, ifnames
        return ifindexes, ifnames

    def handler(self):
        def get_interface(name):
            if_name = names.get(name)
            if if_name:
                return if_name
            for iname in self.object.get_profile().get_interface_names(i["interface"]):
                if_name = names.get(iname)
                if if_name:
                    return if_name
            return None

        self.logger.info("Checking interface statuses")
        interfaces, names = self.get_interface_ifindexes()
        if interfaces:
            result = self.object.scripts.get_interface_status_ex(interfaces=interfaces)
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
            changes = self.update_if_changed(
                iface, kwargs, ignore_empty=kwargs.keys(), bulk=bulk)
            self.log_changes(
                "Interface %s status has been changed" % i["interface"],
                changes)
            ostatus = i.get("oper_status")
            if iface.oper_status != ostatus and ostatus is not None:
                self.logger.info("[%s] set oper status to %s", i["interface"],
                                 ostatus)
                iface.set_oper_status(ostatus)
        if bulk:
            self.logger.info("Commiting changes to database")
            try:
                collection.bulk_write(bulk, ordered=False)
                # 1 bulk operations complete in 0ms: inserted=0, updated=1, removed=0
                self.logger.info("Database has been synced")
            except BulkWriteError as e:
                self.logger.error("Bulk write error: '%s'", e.details)

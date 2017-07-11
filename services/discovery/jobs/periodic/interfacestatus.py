# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Interface Status check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import threading
import operator
# Third-party modules
import cachetools
from pymongo import ReadPreference
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

    _ips_cache = cachetools.TTLCache(maxsize=10, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_ips_cache"), lock=lambda _: ips_lock)
    def get_profiles(cls, x):
        return list(InterfaceProfile.objects.filter(status_discovery=True))

    def handler(self):
        def get_interface(name):
            if_name = interfaces.get(name)
            if if_name:
                return if_name
            for iname in self.object.profile().get_interface_names(i["interface"]):
                if_name = interfaces.get(iname)
                if if_name:
                    return if_name
            return None

        has_interfaces = "DB | Interfaces" in self.object.get_caps()
        if not has_interfaces:
            self.logger.info(
                "No interfaces discovered. "
                "Skipping interface status check"
            )
            return
        self.logger.info(
            "Checking interface statuses"
        )
        interfaces = dict(
            (i.name, i)
            for i in Interface.objects.filter(
                managed_object=self.object.id,
                type="physical",
                profile__in=self.get_profiles(None),
                read_preference=ReadPreference.SECONDARY_PREFERRED
            )
        )
        if not interfaces:
            self.logger.info("No interfaces with status discovery enabled. Skipping")
            return
        result = self.object.scripts.get_interface_status_ex()
        bulk = Interface._get_collection().initialize_unordered_bulk_op()
        nb = 0
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
                iface, kwargs,
                ignore_empty=kwargs.keys(),
                bulk=bulk
            )
            self.log_changes(
                "Interface %s status has been changed" % i["interface"],
                changes
            )
            if changes:
                nb += 1
            ostatus = i.get("oper_status")
            if iface.oper_status != ostatus and ostatus is not None:
                self.logger.info("[%s] set oper status to %s",
                                 i["interface"], ostatus)
                iface.set_oper_status(ostatus)
        if nb:
            bulk.execute()

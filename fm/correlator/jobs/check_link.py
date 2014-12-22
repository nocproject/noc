# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Correlator job:
## Check link is up
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import AlarmJob
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile


class CheckLinkJob(AlarmJob):
    name = "check_link"
    map_task = "get_interface_status"

    def get_map_task_params(self):
        return {
            "interface": self.data["interface"]
        }

    def handler(self, object, result):
        """
        Process result like
        <object>, [{'interface': 'Gi 1/0', 'status': True}]
        :param object:
        :param result:
        :return:
        """
        if len(result) == 1:
            r = result[0]
            if (r["status"] and
                r["interface"] == self.data["interface"]):
                self.clear_alarm("Interface '%s' is up" % (
                    self.data["interface"]))
        return True

    def get_effective_intervals(self):
        def parse(x):
            x = x.strip()
            if not x:
                return []
            parts = [p.strip() for p in x.split(",")]
            if not parts:
                return []
            if len(parts) % 2:
                self.error("Invalid interval description '%s': Must be even size" % x)
                return []
            try:
                parts = [int(p) if p else None for p in parts]
            except ValueError, why:
                self.error("Invalid interval description '%s': %s" % (x, why))
                return []
            if parts[-2] is not None:
                self.error("Invalid interval description '%s': Next to last element must be empty")
                return []
            # @todo: Check times are in ascending order
            # @todo: Check for additional Nones
            return parts

        mo = self.get_managed_object()
        ifname = mo.profile.convert_interface_name(self.data["interface"])
        iface = Interface.objects.get(managed_object=mo.id, name=ifname).first()
        # Check interface profile first
        if iface and iface.profile:
            if iface.profile.check_link_interval:
                return parse(iface.profile.check_link_interval)
        # Check Managed object's profile
        if mo.object_profile.check_link_interval:
            return parse(iface.profile.check_link_interval)
        # Fallback to default interface profile
        # when interface profile doesn't set
        if iface and not iface.profile:
            dp = InterfaceProfile.get_default_profile()
            if dp and dp.check_link_interval:
                return parse(dp.check_link_interval)
        # Job disabled
        return []

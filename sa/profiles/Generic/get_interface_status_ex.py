# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.mib import mib


class Script(BaseScript):
    name = "Generic.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []
    HIGH_SPEED = 4294967295
    DEFAULT_MAX_REPETITIONS = 40

    def get_max_repetitions(self):
        """
        Calculate bulk max_repetitions according to platform
        :return:
        """
        return self.DEFAULT_MAX_REPETITIONS

    def get_iftable(self, oid):
        if "::" in oid:
            oid = mib[oid]
        for oid, v in self.snmp.getnext(oid, max_repetitions=self.get_max_repetitions()):
            yield int(oid.rsplit(".", 1)[-1]), v

    def apply_table(self, r, mib, name, f=None):
        if not f:
            def f(x):
                return x
        for ifindex, v in self.get_iftable(mib):
            s = r.get(ifindex)
            if s:
                s[name] = f(v)

    def get_data(self):
        # ifIndex -> ifName mapping
        r = {}  # ifindex -> data
        unknown_interfaces = []
        for ifindex, name in self.get_iftable("IF-MIB::ifName"):
            try:
                v = self.profile.convert_interface_name(name)
            except InterfaceTypeError as e:
                self.logger.debug(
                    "Ignoring unknown interface %s: %s",
                    name, e
                )
                unknown_interfaces += [name]
                continue
            r[ifindex] = {
                "interface": v
            }
        # Apply ifAdminStatus
        self.apply_table(r, "IF-MIB::ifAdminStatus", "admin_status", lambda x: x == 1)
        # Apply ifOperStatus
        self.apply_table(r, "IF-MIB::ifOperStatus", "oper_status", lambda x: x == 1)
        # Apply ifSpeed
        highspeed = set()
        for ifindex, s in self.get_iftable("IF-MIB::ifSpeed"):
            ri = r.get(ifindex)
            if ri:
                s = int(s)
                if self.is_high_speed(ri, s):
                    highspeed.add(ifindex)
                elif s:
                    ri["in_speed"] = s // 1000
                    ri["out_speed"] = s // 1000
        # Refer to ifHighSpeed if necessary
        if highspeed:
            for ifindex, s in self.get_iftable("IF-MIB::ifHighSpeed"):
                if ifindex in highspeed:
                    s = int(s)
                    if s:
                        r[ifindex]["in_speed"] = s * 1000
                        r[ifindex]["out_speed"] = s * 1000
        # Log unknown interfaces
        if unknown_interfaces:
            self.logger.info("%d unknown interfaces has been ignored",
                             len(unknown_interfaces))
        return r.values()

    def is_high_speed(self, data, speed):
        """
        Detect should we check ifHighSpeed
        :param data: dict with
        :param speed:
        :return:
        """
        return speed == self.HIGH_SPEED

    def execute(self):
        r = []
        if self.has_snmp():
            try:
                r = self.get_data()
            except self.snmp.TimeOutError:
                pass
        return r

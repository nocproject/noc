# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.DSLAM.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
import six
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.DSLAM.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []

    HIGH_SPEED = 4294967295

    def get_iftable(self, oid):
        if "::" in oid:
            oid = mib[oid]
        r = {}
        for oid, v in self.snmp.getnext(oid, max_repetitions=15):
            if oid.endswith(".0"):
                ifindex = int(oid.split(".")[-2])
            else:
                ifindex = int(oid.split(".")[-1])
            r[ifindex] = v
        return r

    def apply_table(self, r, oid, name, f=None):
        if not f:
            def f(x):
                return x
        for ifindex, v in six.iteritems(self.get_iftable(oid)):
            s = r.get(ifindex)
            if s:
                s[name] = f(v)

    def get_data(self):
        # ifIndex -> ifName mapping
        r = {}  # ifindex -> data
        unknown_interfaces = []
        for ifindex, name in six.iteritems(self.get_iftable("IF-MIB::ifName")):
            if " " in name:
                name = name.split()[2]
            if name.startswith("p"):
                name = "s%s" % name
            r[ifindex] = {
                "interface": name
            }
        # Apply ifAdminStatus
        self.apply_table(r, "IF-MIB::ifAdminStatus", "admin_status", lambda x: x == 1)
        # Apply ifOperStatus
        self.apply_table(r, "IF-MIB::ifOperStatus", "oper_status", lambda x: x == 1)
        # Apply dot3StatsDuplexStatus
        self.apply_table(r, "EtherLike-MIB::dot3StatsDuplexStatus", "full_duplex", lambda x: x != 2)
        # Apply ifSpeed
        highspeed = set()
        for ifindex, s in six.iteritems(self.get_iftable("IF-MIB::ifSpeed")):
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
            for ifindex, s in six.iteritems(self.get_iftable("IF-MIB::ifHighSpeed")):
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

    def get_data_sw(self):
        # ifIndex -> ifName mapping
        o = self.snmp.get(mib["SNMPv2-MIB::sysObjectID", 0])
        sw_oid = "%s.15.2.1.2" % o
        r = {}  # ifindex -> data
        unknown_interfaces = []
        for ifindex, name in six.iteritems(self.get_iftable(sw_oid)):
            if " " in name:
                name = name.split()[2]
            if name.startswith("p"):
                name = "s%s" % name
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
        self.apply_table(r, "%s.15.2.1.3" % o, "admin_status", lambda x: x == "UP" or "1")
        # Apply ifOperStatus
        self.apply_table(r, "%s.15.2.1.3" % o, "oper_status", lambda x: x == "UP" or "1")
        # Apply ifSpeed
        for ifindex, s in six.iteritems(self.get_iftable("%s.15.2.1.4" % o)):
            ri = r.get(ifindex)
            if isinstance(s, int):
                s = s
            elif " " in str(s):
                s = s.split()[0]
            else:
                s = 0
            if ri:
                s = int(s)
                ri["in_speed"] = s * 1000
                ri["out_speed"] = s * 1000
        # Log unknown interfaces
        if unknown_interfaces:
            self.logger.info("%d unknown interfaces has been ignored",
                             len(unknown_interfaces))
        return r.values()

    def get_data_adsl(self):
        # ifIndex -> ifName mapping
        o = self.snmp.get(mib["SNMPv2-MIB::sysObjectID", 0])
        if self.match_version(platform="MXA64"):
            o = o.replace("28", "33")
        if (self.match_version(platform="MXA32") or self.match_version(platform="MXA64")):
            s_oid = "%s.10.2.1.5" % o
        else:
            s_oid = "%s.10.2.1.7" % o
        adsl_oid = "%s.10.2.1.2" % o
        r = {}  # ifindex -> data
        unknown_interfaces = []
        for ifindex, name in six.iteritems(self.get_iftable(adsl_oid)):
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
        self.apply_table(r, "%s.10.2.1.3" % o, "admin_status", lambda x: x == "up" or x == 1)
        # Apply ifOperStatus
        self.apply_table(r, "%s.10.2.1.3" % o, "oper_status", lambda x: x == "up" or x == 1)
        # Apply ifSpeed
        for ifindex, s in six.iteritems(self.get_iftable(s_oid)):
            ri = r.get(ifindex)
            if ri:
                s = int(s)
                ri["in_speed"] = s
                ri["out_speed"] = s

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

    def execute_snmp(self):
        if self.match_version(platform="MXA24"):
            r = self.get_data_sw()
            r += self.get_data_adsl()
        else:
            r = self.get_data()
            r += self.get_data_adsl()
        return r

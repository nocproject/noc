# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
import re


class Script(BaseScript):
    name = "OS.FreeBSD.get_portchannel"
    interface = IGetPortchannel
    cache = True
    rx_if_name = re.compile(
        r"^(?P<ifname>\S+): flags=[0-9a-f]+<(?P<flags>\S+)>( metric \d+)?"
        r" mtu (?P<mtu>\d+)$")
    rx_if_lagg = re.compile(r"^\tgroups:.+?bridge.*?$")
    rx_if_lagg_p = re.compile(r"^\tlaggproto lacp")
    rx_if_lagg_m = re.compile(
        r"^\tlaggport: (?P<ifname>\S+) flags=[0-9a-f]+<.*>")

    def execute(self):
        self.interfaces = []
        self.iface = {}
        for s in self.cli("ifconfig -v", cached=True).splitlines():
            match = self.rx_if_name.search(s)
            if match:
                if ("members" in self.iface):
                    if not "type" in self.iface:
                        self.iface["type"] = "S"
                    self.interfaces += [self.iface]
                    self.iface = {}
                self.iface["interface"] = match.group("ifname")
            match = self.rx_if_lagg_p.search(s)
            if match:
                self.iface["type"] = "L"
            match = self.rx_if_lagg_m.search(s)
            if match:
                ifname = match.group("ifname")
                if "members" in self.iface:
                    self.iface["members"] += [ifname]
                else:
                    self.iface["members"] = [ifname]
                continue
        if "members" in self.iface:
            if not "type" in self.iface:
                self.iface["type"] = "S"
            self.interfaces += [self.iface]
        return self.interfaces

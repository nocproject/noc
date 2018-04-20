# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Cisco.IOS.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
from noc.lib.text import parse_table
import re


class Script(BaseScript):
    name = "Cisco.IOS.get_portchannel"
    interface = IGetPortchannel

    rx_iface = re.compile("^(\S+)\(", re.MULTILINE)

    def extract_iface(self, i):
        match = self.rx_iface.search(i)
        return match.group(1)
=======
##----------------------------------------------------------------------
## Cisco.IOS.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetPortchannel
import re


class Script(noc.sa.script.Script):
    name = "Cisco.IOS.get_portchannel"
    implements = [IGetPortchannel]

    # Member 0 : GigabitEthernet0/2 , Full-duplex, 1000Mb/s
    rx_po2_members = re.compile(
        r"^\s+Member\s+\d+\s+:\s+(?P<interface>.+?)\s+.*$")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        r = []
        try:
<<<<<<< HEAD
            s = self.cli("show etherchannel summary")
        except self.CLISyntaxError:
            # Some ASR100X do not have this command
            # raise self.NotSupportedError
            return []
        for i in parse_table(s, allow_wrap=True):
            iface = {
                "interface": self.extract_iface(i[1]),
                "members": []
            }
            if (len(i) == 4) and (i[2] == "LACP"):
                iface["type"] = "L"
            else:
                iface["type"] = "S"
            for ifname in i[len(i)-1].split():
                iface["members"] += [self.extract_iface(ifname)]
            r += [iface]
=======
            s = self.cli("show interfaces status | i ^Po[0-9]+")
        except self.CLISyntaxError:
            # one more try
            try:
                s = self.cli("show interfaces description | i ^Po[0-9]+_")
            except self.CLISyntaxError:
                return []
            for l in s.splitlines():
                pc, rest = l.split(" ", 1)
                pc = pc[2:]
                v = self.cli("show interfaces port-channel {0} | i Member_[0-9]+".format(pc))
                out_if = {
                    "interface": "Po %s" % pc,
                    "members": [],
                    "type": "S",  # <!> TODO: port-channel type detection
                }
                for line in v.splitlines():
                    match = self.rx_po2_members.match(line)
                    if match:
                        out_if["members"].append(match.group('interface'))
                r += [out_if]
                return r
        for l in s.splitlines():
            pc, rest = l.split(" ", 1)
            pc = pc[2:]
            v = self.cli("show interfaces port-channel %s | i Members in this channel" % pc).strip()
            if not v:
                continue
            if v.startswith("Members in this channel"):
                x, y = v.split(":", 1)
                r += [{
                    "interface": "Po %s" % pc,
                    "members": y.strip().split(),
                    "type": "L",  # <!> TODO: port-channel type detection
                }]
            else:
                r += [{
                    "interface": "Po %s" % pc,
                    "members": [],
                    "type": "L",  # <!> TODO: port-channel type detection
                }]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return r

# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.lib.validators import is_mac
from noc.lib.text import parse_table
from noc.core.mib import mib
from noc.sa.interfaces.base import MACAddressParameter
import re


class Script(BaseScript):
    name = "DLink.DxS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(
        r"^MAC [Aa]ddress\s+:\s*(?P<id>\S+)", re.MULTILINE)
    rx_line = re.compile(
        r"^\s*\d+\s+(?:\S+\s+)?"
        r"([0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-"
        r"[0-9A-F]{2}-[0-9A-F]{2})\s+CPU\s+Self\s*(?:\S*\s*)?$",
        re.MULTILINE)

    # Do not use noc.sa.profiles.Generic.get_chassis_id
    def execute_snmp(self):
        macs = []
        for oid, v in self.snmp.getnext(mib["IF-MIB::ifPhysAddress"]):
            mac = MACAddressParameter().clean(v)
            if mac == "00:00:00:00:00:00" or mac in macs:
                continue
            macs += [mac]
        macs.sort()
        return [{
            "first_chassis_mac": f,
            "last_chassis_mac": t
        } for f, t in self.macs_to_ranges(macs)]

    def execute_cli(self):
        match = self.rx_mac.search(self.scripts.get_switch())
        mac = match.group("id")
        macs = []
        try:
            v = self.cli("show fdb static", cached=True)
            macs = self.rx_line.findall(v)
            if macs:
                found = False
                for m in macs:
                    if m == mac:
                        found = True
                        break
                if not found:
                    macs += [mac]
        except self.CLISyntaxError:
            pass
        try:
            v = self.cli("show stack_information", cached=True)
            for i in parse_table(v):
                if not i[5] or not is_mac(i[5]):
                    continue
                found = False
                for m in macs:
                    if m == i[5]:
                        found = True
                        break
                if not found:
                    macs += [i[5]]
        except self.CLISyntaxError:
            pass
        if macs:
            macs.sort()
            return [{
                "first_chassis_mac": f,
                "last_chassis_mac": t
            } for f, t in self.macs_to_ranges(macs)]

        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }

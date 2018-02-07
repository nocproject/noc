# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# TFortis.PSW.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "TFortis.PSW.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_ecfg = re.compile(
        r"""
        Port\s(?P<name>\d+)\n
        Port\sState:\s+(?P<admin_status>\w+)\n
        Port\sSpeed/Duplex:\s+(?P<speed>.*)\n
        Port\sLink:\s+(?P<oper_status>.*)\n
        (?:Port\sPoE:\s+(?P<poe>.*))?
        """,
        re.MULTILINE | re.VERBOSE
    )
    rx_vlans = re.compile(
        r"""
        VID:\s*(?P<vlan_id>\d+)\n
        VLAN\sName:\s*(?P<vlan_name>.*)\n
        VLAN\sType:\s*(?P<vlan_type>.*)\n
        Tagged\sPorts:\s*(?P<tagged_ports>.*)\n
        Untagged\sPorts:(:?\s*(?P<untagged_ports>.*))?
        """,
        re.MULTILINE | re.VERBOSE
    )

    def parse_section(self, section):
        """
        ------------------------------
        Port 1
        Port State:             enable
        Port Speed/Duplex:      100M Full Duplex
        Port Link:              Up
        Port PoE:               On
        """
        r = {}
        name = None
        match = self.rx_ecfg.search(section)
        if match:
            name = match.group("name")
            r['admin_status'] = "enable" in match.group('admin_status').lower()
            r['oper_status'] = "up" in match.group('oper_status').lower()
            r['enabled_protocols'] = ""

        return name, r

    def parse_vlans(self, section):
        r = {}
        match = self.rx_vlans.search(section)
        if match:
            r = match.groupdict()
        return r

    def execute(self):
        v = self.cli("show vlans")
        vlans = []
        for section in v.split("\n\n"):
            if not section:
                continue
            vlans.append(self.parse_vlans(section))

        v = self.cli("show ports")
        ifaces = []
        for section in v.split("------------------------------"):
            if not section:
                continue
            name, cfg = self.parse_section(section)
            untag = ""
            tagged = []
            for i in vlans:
                if name in i["untagged_ports"]:
                    untag = int(i["vlan_id"])
                if name in i["untagged_ports"]:
                    tagged.append(int(i["vlan_id"]))
            i = {
                "name": name,
                "type": "physical",
                "admin_status": cfg["admin_status"],
                "oper_status": cfg["oper_status"],
                "subinterfaces": [{
                    "name": name,
                    "enabled_afi": ["BRIDGE"],
                    "tagged_vlans": tagged,
                    "untagged_vlan": untag,
                }]
            }
            ifaces += [i]
        # @todo: show vlan
        return [{"interfaces": ifaces}]

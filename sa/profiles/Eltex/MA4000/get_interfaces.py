# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.lib.text import list_to_ranges
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Eltex.MA4000.get_interfaces"
    interface = IGetInterfaces

    rx_mgmt = re.compile(
        r"^\s+ip\s+(?P<ip>\S+)\s*\n"
        r"^\s+mask\s+(?P<mask>\S+)\s*\n"
        r"^\s+gateway.+\n"
        r"^\s+vlan\s+(?P<vlan_id>\d+)\s*\n",
        re.MULTILINE
    )
    rx_mac = re.compile(
        r"^\s*\*\d\s+\S+\s+MASTER\s+\d+\s+(?P<mac>\S+)",
        re.MULTILINE
    )

    def create_iface(self, i, iftype):
        ifname = " ".join(i[0].split())
        if not ifname.startswith(iftype):
            return None
        pvid = i[1]
        if i[4] not in ["none", "N/S"]:
            tagged = self.expand_rangelist(i[4])
        else:
            tagged = []
        untagged = i[5]
        if untagged in ["none", "N/S"]:
            untagged = pvid
        iface = {
            "name": ifname,
            "type": "physical",
            "subinterfaces": [{
                "name": ifname,
                "enabled_afi": ["BRIDGE"]
            }]
        }
        if untagged != "N/S":
            iface["subinterfaces"][0]["untagged_vlan"] = int(untagged)
        if tagged:
            iface["subinterfaces"][0]["tagged_vlans"] = tagged
        return iface

    def execute(self):
        interfaces = []

        lldp = []
        c = self.cli("show lldp configuration")
        if "LLDP state: Enabled" in c:
            c = self.cli("show lldp local")
            t = parse_table(c, allow_wrap=True, footer="dummy footer")
            for i in t:
                ifname = " ".join(i[0].split())
                lldp += [ifname]

        c = self.cli("show interface front-port all vlans")
        t = parse_table(
            c, allow_wrap=True, footer="N/A - interface doesn't exist")
        for i in t:
            iface = self.create_iface(i, "front-port")
            if iface is not None:
                if iface["name"] in lldp:
                    iface["enabled_protocols"] = ["LLDP"]
                interfaces += [iface]

        c = self.cli("show management")
        match = self.rx_mgmt.search(c)
        ip_address = "%s/%s" % (
            match.group("ip"), IPv4.netmask_to_len(match.group("mask"))
        )
        iface = {
            "name": "management",
            "type": "SVI",
            "subinterfaces": [{
                "name": "management",
                "enabled_afi": ["IPv4"],
                "ipv4_addresses": [ip_address],
                "vlan_ids": int(match.group("vlan_id"))
            }]
        }
        c = self.cli("show stack")
        match = self.rx_mac.search(c)
        iface["mac"] = match.group("mac")
        iface["subinterfaces"][0]["mac"] = match.group("mac")
        interfaces += [iface]

        return [{"interfaces": interfaces}]

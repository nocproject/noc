# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport


class Script(BaseScript):
    name = "Qtech.QSW2800.get_switchport"
    interface = IGetSwitchport

    rx_descr = re.compile(r"^\s+(?P<interface>\S+\d+(?:/\d+)?) is layer \d+ "
                          r"port, alias name is (?P<description>.+?), "
                          r"index is \d+$",
                          re.MULTILINE)
    rx_switchport = re.compile(r"(?P<interface>\S+\d+(/\d+)?)\n"
                               r"Type :(?P<type>Universal|"
                               r"Aggregation(?: member)?)\n"
                               r"(?:Mac addr num: No limit\n)?"
                               r"Mode :\S+\s*\nPort VID :(?P<pvid>\d+)\n"
                               r"((?:Hybrid tag|Trunk) allowed Vlan:"
                               r"\s+(?P<tags>\S+))?",
                               re.MULTILINE)
    rx_qinq_port = re.compile(r"^Interface (?P<interface>\S+):\n"
                              r"\s+dot1q-tunnel is enable",
                              re.MULTILINE)

    def execute(self):
        # Get portchannels
        pc_members = []
        portchannels = self.scripts.get_portchannel()
        for pch in portchannels:
            pc_members += pch["members"]

        qinq_ports = []
        cmd = self.cli("show dot1q-tunnel")
        for match in self.rx_qinq_port.finditer(cmd):
            qinq_ports += [match.group("interface")]

        # Get interfaces' status
        int_status = {}
        for istat in self.scripts.get_interface_status():
            int_status[istat["interface"]] = istat["status"]

        # Get tags
        # Get vlans
        vlans = [vlan["vlan_id"] for vlan in self.scripts.get_vlans()]

        # Get descriptions
        descr = {}
        cmd = self.cli("show interface | i alias")
        for match in self.rx_descr.finditer(cmd):
            if match.group("description") != "(null)":
                descr[match.group("interface")] = match.group("description")
        result = []
        cmd = self.cli("show switchport interface")
        for match in self.rx_switchport.finditer(cmd):
            ifname = match.group("interface")
            # skip portchannels members
            if ifname in pc_members:
                continue
            pvid = int(match.group("pvid"))
            # initial data
            swp = {
                "interface": ifname,
                "status": int_status.get(ifname, False),
                "tagged": [],
                "untagged": pvid,
                "members": [],
                "802.1ad Tunnel": False
            }
            # description
            if ifname in descr:
                swp["description"] = descr[ifname]
            # port-channel members
            if match.group("type") == "Aggregation":
                for pch in portchannels:
                    if pch["interface"] == ifname:
                        swp["members"] = pch["members"]
                        for mmbr in swp["members"]:  # if PC member is QinQ
                            if mmbr in qinq_ports:   # PC is QinQ too
                                swp["802.1ad Tunnel"] = True
                                break
                        break
            # tags
            if match.group("tags"):
                for tag in self.expand_rangelist(
                        match.group("tags").replace(";", ",")):
                    if tag in vlans and tag != pvid:
                        swp["tagged"] += [tag]
            # 802.1q and QinQ
            if ifname in qinq_ports:
                swp["802.1ad Tunnel"] = True
            if len(swp["tagged"]) > 0:
                swp["802.1Q Enabled"] = True
            result += [swp]
        return result

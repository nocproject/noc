# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Qtech.QSW.get_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
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
=======
##----------------------------------------------------------------------
## Qtech.QSW.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "Qtech.QSW2800.get_switchport"
    implements = [IGetSwitchport]

    rx_interface = re.compile(r"^(?P<interface>\d+/\d+)\s+\S+\s+\S+\s+\S+\s+"
                    r"(?P<vlan>\S+)\s+\S+\s+(?P<description>.*)", re.MULTILINE)
    rx_switchport = re.compile(r"(?P<interface>\S+\d+/\d+).Type :\S+."
                    r"(?:Mac addr num: No limit.)?Mode :\S+\s*.Port VID :\d+."
                    r"(?:Hybrid tag|Trunk) allowed Vlan:"
                    r"\s+(?P<tags>\S+)", re.MULTILINE | re.DOTALL)
    rx_qinq_port = re.compile(r"^Interface (?P<interface>\S+):.\s+dot1q-tunnel"
                    r" is enable", re.MULTILINE | re.DOTALL)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        # Get portchannels
        pc_members = []
        portchannels = self.scripts.get_portchannel()
<<<<<<< HEAD
        for pch in portchannels:
            pc_members += pch["members"]

=======
        for p in portchannels:
            pc_members += p["members"]

        # Get 802.1ad (QinQ) tunnels
        # @todo: doesn't work for port-channels,
        #        waiting for a bugfix from qtech
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        qinq_ports = []
        cmd = self.cli("show dot1q-tunnel")
        for match in self.rx_qinq_port.finditer(cmd):
            qinq_ports += [match.group("interface")]

<<<<<<< HEAD
        # Get interfaces' status
        int_status = {}
        for istat in self.scripts.get_interface_status():
            int_status[istat["interface"]] = istat["oper_status"]

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
                ma_group = match.group("tags").replace(";", ",")
                if "showOneSwitchPort" in ma_group:
                    continue
                for tag in self.expand_rangelist(ma_group):
                    if tag in vlans and tag != pvid:
                        swp["tagged"] += [tag]
            # 802.1q and QinQ
            if ifname in qinq_ports:
                swp["802.1ad Tunnel"] = True
            if len(swp["tagged"]) > 0:
                swp["802.1Q Enabled"] = True
            result += [swp]
        return result
=======
        # Get interafces' status
        int_status = {}
        for s in self.scripts.get_interface_status():
            int_status[s["interface"]] = s["status"]

        # Get tags
        tags = {}
        vlans = [v["vlan_id"] for v in self.scripts.get_vlans()]
        cmd = self.cli("show switchport interface")
        for match in self.rx_switchport.finditer(cmd):
            tags[match.group("interface")] = \
                self.expand_rangelist(match.group("tags").replace(";",","))

        # Get the rest of data
        r = []
        cmd = self.cli("show interface ethernet status")
        for l in cmd.splitlines():
            match = self.rx_interface.match(l)
            if match:
                # fill in initial data
                ifname = "Ethernet%s" % match.group("interface")
                if ifname not in pc_members:
                    swp = {
                        "interface": ifname,
                        "members": [],
                        "tagged": []
                    }
                else:
                    for p in portchannels:
                        if ifname in p["members"]:
                            swp["interface"] = p["interface"]
                            swp["members"] = p["members"]
                            swp["tagged"] = []
                            portchannels.remove(p)
                            break
                # get status
                swp["status"] = int_status.get(swp["interface"], False)
                # get description
                if match.group("description") != "":
                    swp["description"] = match.group("description")
                # get tagged vlans
                try:
                    for t in tags[swp["interface"]]:
                        if t in vlans:
                            swp["tagged"] += [t]
                except KeyError:
                    pass
                # get untagged vlan
                try:
                    swp["untagged"] = int(match.group("vlan"))
                except ValueError:
                    pass
                # get qinq and dot1q status
                if swp["interface"] in qinq_ports:
                    swp["802.1ad Tunnel"] = True
                    swp["802.1Q Enabled"] = True
                if len(swp["tagged"]) > 0:
                    swp["802.1Q Enabled"] = True
                r += [swp]
        return r
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

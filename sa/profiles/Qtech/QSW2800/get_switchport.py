# -*- coding: utf-8 -*-
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

    def execute(self):
        # Get portchannels
        pc_members = []
        portchannels = self.scripts.get_portchannel()
        for p in portchannels:
            pc_members += p["members"]

        # Get 802.1ad (QinQ) tunnels
        # @todo: doesn't work for port-channels,
        #        waiting for a bugfix from qtech
        qinq_ports = []
        cmd = self.cli("show dot1q-tunnel")
        for match in self.rx_qinq_port.finditer(cmd):
            qinq_ports += [match.group("interface")]

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

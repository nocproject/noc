# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_mpls_vpn
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetmplsvpn import IGetMPLSVPN


class Script(NOCScript):
    name = "Cisco.IOS.get_mpls_vpn"
    implements = [IGetMPLSVPN]

    rx_line = re.compile(r"^\s+(?P<vrf>.+?)\s+"
                         r"(?P<rd>\S+:\S+|<not set>)\s+"
                         "(?P<iface>.*?)\s*$", re.IGNORECASE)
    rx_cont = re.compile("^\s{6,}(?P<iface>.+?)\s*$")
    rx_portchannel = re.compile(r"^Po\s*\d+(?:A|B)?$")

    portchannel_members = {}

    def _get_portchannel_members(self, iface):
        iface = self.profile.convert_interface_name(iface)
        if not self.portchannel_members:
            for pc in self.scripts.get_portchannel():
                i = pc["interface"]
                self.portchannel_members[i] = pc["members"]
        if iface in self.portchannel_members:
            return self.portchannel_members[iface]
        else:
            return []

    def execute(self, **kwargs):
        vpns = []
        v = self.cli("show ip vrf")
        for l in v.splitlines():
            match = self.rx_line.match(l)
            if match:
                iface = match.group("iface").strip()
                if iface:
                    interfaces = [iface]
                    po_match = self.rx_portchannel.match(iface)
                    if po_match:
                        members = self._get_portchannel_members(iface)
                        interfaces += members
                else:
                    interfaces = []
                vpn = {
                    "type": "VRF",
                    "status": True,
                    "name": match.group("vrf"),
                    "interfaces": interfaces
                }
                rd = match.group("rd")
                if ":" in rd:
                    vpn["rd"] = rd
                vpns += [vpn]
            elif vpns:
                match = self.rx_cont.match(l)
                if match:
                    iface = match.group("iface")
                    interfaces = [iface]
                    po_match = self.rx_portchannel.match(iface)
                    if po_match:
                        members = self._get_portchannel_members(iface)
                        interfaces += members
                    vpns[-1]["interfaces"] += interfaces
        return vpns

# ---------------------------------------------------------------------
# HP.Comware.get_mpls_vpn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_mpls_vpn import Script as BaseScript
from noc.sa.interfaces.igetmplsvpn import IGetMPLSVPN


class Script(BaseScript):
    name = "HP.Comware.get_mpls_vpn"
    interface = IGetMPLSVPN

    rx_line = re.compile(r"^\s+(?P<vrf>\S+)\s+(?P<rd>\S+:\S+|<not set>)\s+", re.MULTILINE)
    rx_if = re.compile(r"^\s+Interfaces : (?P<ifaces>.+)", re.MULTILINE | re.DOTALL)

    def execute_cli(self):
        vpns = []
        try:
            v = self.cli("display ip vpn-instance")
        except self.CLISyntaxError:
            return []
        for ll in v.splitlines():
            match = self.rx_line.match(ll)
            if match:
                vrf = match.group("vrf")
                v1 = self.cli("display ip vpn-instance instance-name %s" % vrf)
                match1 = self.rx_if.search(v1)
                if match1:
                    interfaces = match1.group("ifaces").replace("\n", "")
                    interfaces = interfaces.replace(" ", "").split(",")
                vpn = {
                    "type": "VRF",
                    "status": True,
                    "name": vrf,
                    "rd": match.group("rd"),
                    "interfaces": interfaces,
                }
                vpns += [vpn]
        return vpns

# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Cisco.IOSXR.get_mpls_vpn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmplsvpn import IGetMPLSVPN


class Script(BaseScript):
    name = "Cisco.IOSXR.get_mpls_vpn"
    interface = IGetMPLSVPN
=======
##----------------------------------------------------------------------
## Cisco.IOSXR.get_mpls_vpn
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMPLSVPN


class Script(NOCScript):
    name = "Cisco.IOSXR.get_mpls_vpn"
    implements = [IGetMPLSVPN]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_vrf = re.compile(r"^VRF\s+(?P<name>[^;]+);\s+RD\s+(?P<rd>[^;]+);.+$")

    def is_not_set(self, s):
        if isinstance(s, basestring):
            return s.strip().lower() == "not set"
        return False

    def execute(self, **kwargs):
        vpns = []
        v = self.cli("show vrf all detail")
        current = None
        in_interfaces = False
        for l in v.splitlines():
            # Look for new VRF
            match = self.rx_vrf.match(l)
            if match:
                if current:
                    # Write existing VRF
                    vpns += [current]
                # Create new VRF
                current = {
                    "name": match.group("name"),
                    "type": "VRF",
                    "status": True,
                    "interfaces": []
                }
                # Add RD when exists
                rd = match.group("rd")
                if not self.is_not_set(rd):
                    current["rd"] = rd
                #
                in_interfaces = False
                continue
            if not current:
                continue
            # Look for description
            if l.startswith("Description "):
                description = l[12:].strip()
                if not self.is_not_set(description):
                    current["description"] = description
                continue
            # Look for interfaces
            if l.startswith("Interfaces:"):
                in_interfaces = True
                continue
            if in_interfaces:
                if l.startswith(" "):
                    current["interfaces"] += [l.strip()]
                else:
                    in_interfaces = False
        if current:
            vpns += [current]
        return vpns

# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.base import IntParameter
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "Juniper.JUNOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
    #
    # EX Series
    #
    rx_localport = re.compile(
        r"^(\S+?)\s+?(\d+?)\s+?\S+?\s+?Up.+?$",
        re.MULTILINE | re.DOTALL)
    rx_neigh = re.compile(
        r"^(?P<local_if>.e-\S+?|me\d|fxp0)\s.*?$",
        re.MULTILINE)
    # If <p_type>=='Interface alias', then <p_id> will match 'Port description'
    # else it will match 'Port ID'
    rx_detail = re.compile(
        r"Chassis type\s+:\s+(?P<ch_type>.+)\n"
        r"Chassis ID\s+:\s(?P<id>\S+)\n"
        r"Port type\s+:\s(?P<p_type>.+)\n"
        r"Port ID\s+:\s(?P<p_id>.+)\n"
        r"(Port description\s+:\s(?P<p_descr>.+)\n)?"
        r"(System name\s+:\s(?P<name>.+)\n)?",
        re.MULTILINE
    )
    rx_caps = re.compile(
        r"System capabilities\s*\n"
        r"\s*Supported\s*:\s(?P<capability>.+)\n",
        re.MULTILINE
    )
    CHASSIS_TYPE = {
        "Mac address": 4,
        "Network address": 5
    }
    PORT_TYPE = {
        "Interface alias": 1,
        "Port component": 2,
        "Mac address": 3,
        "Interface name": 5,
        "Locally assigned": 7
    }

    def execute_cli(self):
        if self.is_has_lldp:
            return self.execute_switch()
        else:
            return self.execute_other()

    # Match mx, ex, qfx, acx
    def execute_switch(self):
=======
##----------------------------------------------------------------------
## Juniper.JUNOS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import (IGetLLDPNeighbors, IntParameter,
                               MACAddressParameter, InterfaceTypeError)


class Script(NOCScript):
    name = "Juniper.JUNOS.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]
    ##
    ## EX Series
    ##
    rx_localport = re.compile(r"^(\S+?)\s+?(\d+?)\s+?\S+?\s+?Up.+?$",
        re.MULTILINE | re.DOTALL)
    rx_neigh = re.compile(r"(?P<local_if>.e-\S+?)\s.*?$",
        re.MULTILINE | re.IGNORECASE)
    # If <p_type>=='Interface alias', then <p_id> will match 'Port description'
    # else it will match 'Port ID'
    rx_detail = [
         r"Chassis ID\s+:\s(?P<id>\S+)",
         r"Port type\s+:\s(?P<p_type>.+)",
         r"Port \S+\s+:\s(?P<p_id>.+)",
         r"System name\s+:\s(?P<name>\S+)",
         r"System capabilities",
         r"Supported\s*:\s(?P<capability>.+)"
    ]

    @NOCScript.match(platform__regex="[em]x")
    def execute_ex(self):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        r = []
        # Collect data
        local_port_ids = {}  # name -> id
        v = self.cli("show lldp local-information")
        for port, local_id in self.rx_localport.findall(v):
            local_port_ids[port] = IntParameter().clean(local_id)
        v = self.cli("show lldp neighbors")
        ifs = [{
            "local_interface": match.group("local_if"),
            "neighbors": [],
        } for match in self.rx_neigh.finditer(v)]
        for i in ifs:
            if i["local_interface"] in local_port_ids:
                i["local_interface_id"] = local_port_ids[i["local_interface"]]
<<<<<<< HEAD
            v = self.cli(
                "show lldp neighbors interface %s" % i["local_interface"]
            )
            n = {}
            match = self.rx_detail.search(v)
            n["remote_chassis_id_subtype"] = self.CHASSIS_TYPE[
                match.group("ch_type")
            ]
            n["remote_chassis_id"] = match.group("id")
            n["remote_port_subtype"] = self.PORT_TYPE[match.group("p_type")]
            n["remote_port"] = match.group("p_id")
            if match.group("p_descr"):
                n["remote_port_description"] = match.group("p_descr")
            if match.group("name"):
                n["remote_system_name"] = match.group("name")
            # Get capability
            cap = 0
            match = self.rx_caps.search(v)
            if match:
                s = match.group("capability")
                # WLAN Access Point
                s = s.replace(" Access Point", "")
                # Station Only
                s = s.replace(" Only", "")
                for c in s.strip().split(" "):
                    cap |= {
                        "Other": 1, "Repeater": 2, "Bridge": 4,
                        "WLAN": 8, "Router": 16, "Telephone": 32,
                        "Cable": 64, "Station": 128
                    }[c]
                n["remote_capabilities"] = cap
            i["neighbors"] += [n]
            r += [i]
        for q in r:
            if q['local_interface'].endswith(".0"):
                q['local_interface'] = q['local_interface'][:-2]
        return r

    #
    # No lldp on M/T
    #
=======
            v = self.cli("show lldp neighbors interface %s" % i["local_interface"])
            match = self.match_lines(self.rx_detail, v)
            n = {"remote_chassis_id_subtype": 4}
            if match:
                n["remote_port_subtype"] = {
                    "Mac address": 3,
                    "Interface alias": 1,
                    "Interface name": 5,
                    "Locally assigned": 7
                }[match.get("p_type")]
                if n["remote_port_subtype"] == 3:
                    remote_port = MACAddressParameter().clean(match.get("p_id"))
                elif n["remote_port_subtype"] == 7:
                    p_id = match.get("p_id")
                    try:
                        remote_port = IntParameter().clean(p_id)
                    except InterfaceTypeError:
                        remote_port = p_id
                else:
                    remote_port = match.get("p_id")
                n["remote_chassis_id"] = match.get("id")
                n["remote_system_name"] = match.get("name")
                n["remote_port"] = remote_port
                # Get capability
                cap = 0
                if match.get("capability"):
                    for c in match.get("capability").strip().split(" "):
                            cap |= {
                            "Other": 1, "Repeater": 2, "Bridge": 4,
                            "WLAN": 8, "Router": 16, "Telephone": 32,
                            "Cable": 64, "Station": 128
                            }[c]
                n["remote_capabilities"] = cap
            i["neighbors"] += [n]
            r += [i]
        return r

    ##
    ## No lldp on M/T
    ##
    @NOCScript.match()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute_other(self):
        raise self.NotSupportedError()

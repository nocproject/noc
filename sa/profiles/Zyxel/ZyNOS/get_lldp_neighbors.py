# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

#NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors
from noc.lib.validators import is_int, is_ipv4
#Python standard modules
import re


class Script(NOCScript):
    name = "Zyxel.ZyNOS.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    rx_summary_split = re.compile(r"^LocalPort.+?\n",
                                    re.MULTILINE | re.IGNORECASE)
    rx_s_line = re.compile(r"(?P<local_if>\d+)\s+[0-9a-f:]+\s+.+?$")

    rx_remote_port = re.compile("^\s+Port id:\s*(?P<remote_if>.+?)\s*$",
        re.MULTILINE | re.IGNORECASE)

    rx_remote_port_desc = re.compile("^Port Description:\s*(?P<remote_if_desc>.+?)\s*$",
        re.MULTILINE | re.IGNORECASE)

    rx_remote_port_subtype = re.compile("^Port id subtype:\s*(?P<remote_if_subtype>.+?)\s*$",
        re.MULTILINE | re.IGNORECASE)

    rx_chassis_id = re.compile(r"^\s+Chassis id:\s*(?P<id>\S+)",
        re.MULTILINE | re.IGNORECASE)

    rx_enabled_caps = re.compile("^System Capabilities Enabled:\s*(?P<caps>((other|repeater|bridge|router|wlan-access-point|telephone|docsis-cable-device|station-only)\s+)+)\s*$",
        re.MULTILINE | re.IGNORECASE)

    rx_system = re.compile(r"^\s+System Name:\s*(?P<name>\S+)",
                           re.MULTILINE | re.IGNORECASE)

    rx_mac = re.compile(r"^[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}$")

    def execute(self):
        r=[]
        try:
            v = self.cli("sh lldp info remote")
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        v = self.rx_summary_split.split(v)[1]
        lldp_interfaces = []

        #Get lldp interfaces
        for l in v.splitlines():
            l = l.strip()
            if not l:
                break
            match = self.rx_s_line.match(l)
            if not match:
                continue
            lldp_interfaces += [match.group('local_if')]

        #Get lldp neighbors
        for local_if in lldp_interfaces:
            i = {
                "local_interface": local_if,
                "neighbors": []
            }

            #Get neighbor details
            try:
                v = self.cli("sh lldp info remote interface port-channel %s" % local_if)
            except self.CLISyntaxError:
                raise self.NotSupportedError()

            #Get remote port
            match = self.re_search(self.rx_remote_port, v)
            remote_port = match.group("remote_if")

            match = self.re_search(self.rx_remote_port_subtype, v)
            remote_port_subtype_str = match.group('remote_if_subtype')

            #Get remote port subtype from "Port ID Subtype" field
            if remote_port_subtype_str == 'local-assigned':
                remote_port_subtype = 7 #Local
            else:
                remote_port_subtype = 5
                if self.rx_mac.match(remote_port):
                    # Actually macAddress(3)
                    remote_port_subtype = 3
                elif is_ipv4(remote_port):
                    # Actually networkAddress(4)
                    remote_port_subtype = 4
                elif is_int(remote_port):
                    # Actually local(7)
                    remote_port_subtype = 7
            n = {
                "remote_port": remote_port,
                "remote_port_subtype": remote_port_subtype,
                "remote_chassis_id_subtype": 4
            }

            #Get Chassis ID
            match = self.rx_chassis_id.search(v)
            if not match:
                continue
            n["remote_chassis_id"] = match.group("id")

            #Get capabilities
            cap = 0
            match = self.rx_enabled_caps.search(v)
            if match:
                for c in match.group("caps").split():
                    c = c.strip()
                    if c:
                        cap |= {
                            "other": 1, "repeater": 2, "bridge": 4,
                            "wlan-access-point": 8, "router": 16, "telephone": 32,
                            "docsis-cable-device": 64, "station-only": 128
                        }[c]
            n["remote_capabilities"] = cap

            #Get system name
            match = self.rx_system.search(v)
            if match:
                n["remote_system_name"] = match.group("name")
            i["neighbors"] += [n]
            r += [i]
        return r

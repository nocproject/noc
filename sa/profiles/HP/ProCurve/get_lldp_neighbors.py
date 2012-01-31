# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors
from noc.lib.text import parse_table


class Script(NOCScript):
    name = "HP.ProCurve.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    rx_localport = re.compile(r"^\s*(\S+)\s*\|\s*local\s+(\d+)\s+.+?$", re.MULTILINE)
    rx_split = re.compile(r"^\s*----.+?\n", re.MULTILINE | re.DOTALL)
    rx_line = re.compile(r"^\s*(?P<port>\S+)\s*|", re.MULTILINE | re.DOTALL)
    #rx_chassis_id=re.compile(r"^\s*ChassisId\s*:\s*(.{17})",re.MULTILINE|re.DOTALL|re.IGNORECASE)
    rx_chassis_id = re.compile(r"ChassisType\s*:\s*(\S+).+?ChassisId\s*:\s*([a-zA-Z0-9\.\- ]+)", re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_port_id = re.compile(r"^\s*PortId\s*:\s*(.+?)\s*$", re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_sys_name = re.compile(r"^\s*SysName\s*:\s*(.+?)\s*$", re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_cap = re.compile(r"^\s*System Capabilities Enabled\s*:(.*?)$", re.MULTILINE | re.IGNORECASE)

    def execute(self):
        r = []
        # HP.ProCurve advertises local(7) port sub-type, so local_interface_id parameter required
        # Collect data
        local_port_ids = {}  # name -> id
        for port, local_id in self.rx_localport.findall(self.cli("show lldp info local-device")):
            local_port_ids[port] = int(local_id)
        # Get neighbors
        v = self.cli("show lldp info remote-device")
        for l in self.rx_split.split(v)[1].splitlines():
            l = l.strip()
            if not l:
                continue
            match = self.rx_line.search(l)
            if not match:
                continue
            local_interface = match.group("port")
            i = {"local_interface": local_interface, "neighbors": []}
            # Add locally assigned port id, if exists
            if local_interface in local_port_ids:
                i["local_interface_id"] = local_port_ids[local_interface]
            v = self.cli("show lldp info remote-device %s" % local_interface)
            # Get chassis id
            match = self.rx_chassis_id.search(v)
            if not match:
                continue
            remote_chassis_id_subtype = {
                "mac-address": 4,
                "local": 7,  # @todo: check
            }[match.group(1)]
            remote_chassis_id = match.group(2).strip().replace(" ", "")
            if remote_chassis_id_subtype == 4:
                remote_chassis_id = "%s-%s" % (remote_chassis_id[:6], remote_chassis_id[6:])  # Convert to HP-style mac
            else:
                remote_chassis_id = remote_chassis_id.strip()
            n = {
                "remote_chassis_id": remote_chassis_id,
                "remote_port_subtype": 5,
                 "remote_chassis_id_subtype": remote_chassis_id_subtype
            }
            # Get remote port
            match = self.rx_port_id.search(v)
            if not match:
                continue
            n["remote_port"] = match.group(1)
            # Get remote system name
            match = self.rx_sys_name.search(v)
            if match:
                n["remote_system_name"] = match.group(1)
            # Get capabilities
            caps = 0
            match = self.rx_cap.search(v)
            if match:
                for c in match.group(1).strip().split(", "):
                    if not c:
                        continue
                    caps |= {
                        "other": 1, "repeater": 2, "bridge": 4,
                        "wlanaccesspoint": 8, "router": 16, "telephone": 32,
                        "docsis": 64, "station": 128
                    }[c.lower()]
            n["remote_capabilities"] = caps
            i["neighbors"] += [n]
            r += [i]
        return r

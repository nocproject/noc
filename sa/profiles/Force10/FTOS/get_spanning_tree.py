# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_spanning_tree
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetSpanningTree
from noc.lib.text import parse_table
import re


class Script(noc.sa.script.Script):
    name = "Force10.FTOS.get_spanning_tree"
    implements = [IGetSpanningTree]
    ##
    ## MSTP Mode parsing
    ##
    rx_mstp_instance_list = re.compile(r"^\s*(\d+)", re.MULTILINE)
    rx_mstp_region = re.compile(r"MST Region Name:\s+(?P<region>\S+).*Revision:\s+(?P<revision>\d+)", re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_mstp_vlans = re.compile(
        r"^MSTI \d VLANs mapped\s+(?P<vlans>.+?)$", re.MULTILINE)
    rx_mstp_root = re.compile(r"^Root\s+ID\s+Priority\s+(?P<root_priority>\d+),\s+Address\s+(?P<root_id>\S+)", re.MULTILINE)
    rx_mstp_bridge = re.compile(r"^Bridge\s+ID\s+Priority\s+(?P<bridge_priority>\d+),\s+Address\s+(?P<bridge_id>\S+)", re.MULTILINE)

    def process_mstp(self):
        # Get Instances List
        v = self.cli("show spanning-tree mst configuration")
        match = self.rx_mstp_region.search(v)
        r = {
            "mode": "MSTP",
            "instances": [],
            "configuration": {
                "MSTP": {
                    "region": match.group("region"),
                    "revision": match.group("revision"),
                }
            }
        }
        for instance_id in ["0"] + self.rx_mstp_instance_list.findall(v):
            # Get instance data
            ri = {"id": int(instance_id), "interfaces": []}
            v = self.cli("show spanning-tree msti %s brief" % instance_id)
            # Get VLAN mapping
            match = self.rx_mstp_vlans.search(v)
            ri["vlans"] = match.group(1)
            # Get Root ID and priority
            match = self.rx_mstp_root.search(v)
            ri["root_id"] = match.group("root_id")
            ri["root_priority"] = match.group("root_priority")
            # Get Bridge ID and priority
            match = self.rx_mstp_bridge.search(v)
            ri["bridge_id"] = match.group("bridge_id")
            ri["bridge_priority"] = match.group("bridge_priority")
            # Process interfaces
            s1, s2, s3 = v.split("\n\nInterface")
            for interface, port_id, priority, _, state, _, desg_bridge, desg_port_id in parse_table(s2):
                desg_bridge_priority, desg_bridge_id = desg_bridge.split()
                i = {
                    "interface": interface,
                    "port_id": port_id,
                    "state": {
                        "dis": "disabled",
                        "blk": "discarding",
                        "??": "learning",
                        "fwd": "forwarding"
                    }[state.lower()],  # @todo: refine states
                    "priority": priority,
                    "designated_bridge_id": desg_bridge_id,
                    "designated_bridge_priority": desg_bridge_priority,
                    "designated_port_id": desg_port_id,
                }
                ri["interfaces"] += [i]
            for i, s in zip(ri["interfaces"], parse_table(s3)):
                interface, role, port_id, priority, cost, status, cost2, link_type, edge, boundary = s
                i["role"] = {
                    "dis": "disabled",
                    "?": "alternate",
                    "backup": "backup",
                    "root": "root",
                    "desg": "designated",
                    "???": "master",
                    "????": "nonstp",
                    "_": "unknown"}[role.lower()]  # @todo: refine roles
                i["point_to_point"] = "P2P" in link_type.upper()
                i["edge"] = True if edge.lower().startswith("y") else False
            # Append instance to result
            r["instances"] += [ri]
        return r

    def execute(self):
        # Check if is MSTP
        v = self.cli("show spanning-tree mst configuration")
        if v and not v.startswith("%"):
            return self.process_mstp()
        raise self.NotSupportedError()

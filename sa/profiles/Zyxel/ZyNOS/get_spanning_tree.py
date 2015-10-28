# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_spanning_tree
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_spanning_tree"
    interface = IGetSpanningTree

    rx_config = re.compile(r"Configuration Name:\s+(?P<region>\S+)$\s+"
            r"Reve?ision Number:\s+(?P<revision>\d+)",
            re.MULTILINE)
    rx_inst_vlans = re.compile(r"^\s+(?P<id>\d+)\s+(?P<vlans>\S+)",
            re.MULTILINE)
    rx_bridge = re.compile(r"\(a\)BridgeID:\s+(?P<bridge_priority>[0-9a-f]+)"
            r"-(?P<bridge_id>\S+)")
    rx_root = re.compile(r"\(e\)DesignatedRoot:\s+(?P<root_priority>\S+)"
            r"-(?P<root_id>\S+)")
    rx_port = re.compile(r"Port \[(?P<iface>\d+)\] Info:."
            r"(?:\s+\(\S\)MSTID:\s+\d+.)?"
            r"\s+\(\S\)Uptime:\s+\d+\s+\(seconds\)."
            r"\s+\(\S\)State:\s+(?P<state>\S+)."
            r"\s+\(\S\)PortID:\s+(?P<port_id>\S+)."
            r"\s+\(\S\)PathCost:\s+\d+.\s+\(\S\)DesignatedRoot:\s+\S+."
            r"\s+\(\S\)DesignatedCost:\s+\d+.\s+\(\S\)"
            r"DesignatedBridge:\s+(?P<ds_br_pr>[0-9a-f]+)-(?P<ds_br_id>\S+)."
            r"\s+\(\S\)DesignatedPort:\s+(?P<ds_port_id>\S+)"
            r"(?:\s+\(\S\)TopoChangeAck:\s+\S+.\s+\(\S\)adminEdgePort:\s+\S+."
            r"\s+\(\S\)operEdgePort:\s+(?P<edge>\S+)."
            r"\s+\(\S\)MAC_Operational:\s+\S+."
            r"\s+\(\S\)adminPointToPointMAC:\s+\S+."
            r"\s+\(\S\)operPointToPointMAC:\s+(?P<p2p>\S+))?",
            re.DOTALL)

    @classmethod
    def hex_to_portid(cls, v):
        """
        Convert hexadecimal port id to commonly used dot notation
        0x8001 -> 128.1
        """
        i = int(v, 16)
        prio = (i >> 12) * 16
        port = i & 0xFFF
        return "%d.%d" % (prio, port)

    def process_mstp(self):
        """
        Get MSTP configuration
        """
        # some default values
        config = {"MSTP": {}}
        instances = []
        edge = False
        p2p = True
        # get MSTP global config
        cmd = self.cli("show mstp")
        match = self.rx_config.search(cmd)
        if match:
            config["MSTP"]["region"] = match.group("region")
            config["MSTP"]["revision"] = match.group("revision")
        # get instances and their vlans
        for match in self.rx_inst_vlans.finditer(cmd):
            instances += [{
                "id": match.group("id"),
                "vlans": match.group("vlans").rstrip(",")
            }]
        # get instances' config and status
        for i in instances:
            cmd = self.cli("show mstp instance %s" % i["id"])
            # get bridge id and priority
            match = self.rx_bridge.search(cmd)
            if match:
                i["bridge_id"] = match.group("bridge_id")
                i["bridge_priority"] = int(match.group("bridge_priority"), 16)
            # get root id and priority
            match = self.rx_root.search(cmd)
            if match:
                i["root_id"] = match.group("root_id")
                i["root_priority"] = int(match.group("root_priority"), 16)
            # get interfaces
            ifaces = []
            for match in self.rx_port.finditer(cmd):
                port_id = self.hex_to_portid(match.group("port_id"))
                ds_port_id = self.hex_to_portid(match.group("ds_port_id"))
                # Interface state
                state = {
                        "FORWARDING": "forwarding",
                        "DISCARDING": "discarding",
                        # etc
                }[match.group("state")]
                # get edge and p2p properties from instance 0
                if i["id"] == 0:
                    edge = match.group("edge")
                    p2p = match.group("p2p")
                # detect port role
                if match.group("ds_br_id") == i["bridge_id"]:
                    role = "designated"
                elif state == "forwarding":
                    role = "root"
                elif state == "discarding":
                    role = "alternate"
                else:
                    role = "unknown"
                ifaces += [{
                    "interface": int(match.group("iface")),
                    "port_id": port_id,
                    "state": state,
                    "role": role,
                    "priority": int(port_id.split(".")[0]),
                    "designated_bridge_id": match.group("ds_br_id"),
                    "designated_bridge_priority": int(ds_port_id.split(".")[0]),
                    "designated_port_id": ds_port_id
                }]
            # Edge and p2p properties from instance 0
            for ifc in ifaces:
                ifc["edge"] = edge
                ifc["point_to_point"] = p2p
            i["interfaces"] = ifaces

        return {
            "mode": "MSTP",
            "configuration": config,
            "instances": instances
        }

    def process_rstp(self):
        """
        Get RSTP configuration
        """
        cmd = self.cli("show spanning-tree config")
        # get bridge id and priority
        match = self.rx_bridge.search(cmd)
        if match:
            bridge_id = match.group("bridge_id")
            bridge_priority = int(match.group("bridge_priority"), 16)
        else:
            return {
                "mode": "None",
                "instances": []
            }
        # get root id and priority
        match = self.rx_root.search(cmd)
        if match:
            root_id = match.group("root_id")
            root_priority = int(match.group("root_priority"), 16)
        else:
            return {
                "mode": "None",
                "instances": []
            }
        # get interfaces
        ifaces = []
        for match in self.rx_port.finditer(cmd):
            port_id = self.hex_to_portid(match.group("port_id"))
            ds_port_id = self.hex_to_portid(match.group("ds_port_id"))
            state = {
                    "FORWARDING": "forwarding",
                    "DISCARDING": "discarding",
                    # etc
            }[match.group("state")]
            # detect port role
            if match.group("ds_br_id") == bridge_id:
                role = "designated"
            elif state == "forwarding":
                role = "root"
            elif state == "discarding":
                role = "alternate"
            else:
                role = "unknown"
            ifaces += [{
                "interface": int(match.group("iface")),
                "port_id": port_id,
                "state": state,
                "role": role,
                "priority": int(port_id.split(".")[0]),
                "designated_bridge_id": match.group("ds_br_id"),
                "designated_bridge_priority": int(match.group("ds_br_pr"), 16),
                "designated_port_id": ds_port_id,
                "edge": match.group("edge"),
                "point_to_point": match.group("p2p")
            }]

        return {
            "mode": "RSTP",
            "instances": [{
                "id": 0,
                "vlans": "1-4095",
                "bridge_id": bridge_id,
                "bridge_priority": bridge_priority,
                "root_id": root_id,
                "root_priority": root_priority,
                "interfaces": ifaces

            }]
        }

    def execute(self):
        cmd = self.cli("show mstp", cached=True)
        if "MSTP Disabled" not in cmd:
            r = self.process_mstp()
        else:
            cmd = self.cli("show spanning-tree config", cached=True)
            if "RSTP Disabled" not in cmd:
                r = self.process_rstp()
            else:
                r = {
                    "mode": "None",
                    "instances": []
                }
        return r

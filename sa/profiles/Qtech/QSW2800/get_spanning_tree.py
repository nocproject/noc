# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW2800.get_spanning_tree
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree


class Script(BaseScript):
    name = "Qtech.QSW2800.get_spanning_tree"
    interface = IGetSpanningTree

    rx_mode = re.compile(r"^Standard\s+:\s+IEEE (?P<mode>\S+)",
                        re.MULTILINE)
    rx_inst_id = re.compile(r"^#+ Instance (?P<inst_id>\d+) #+")
    rx_vlans = re.compile(r"^vlans mapped\s+: (?P<vlans>\S+)$")
    rx_root = re.compile(r"^(?:Region )?Root Id\s+:\s+"
                        r"(?P<root>\d*\.?\S+\s?\S*)")
    rx_bridge = re.compile(r"Self Bridge Id\s+:\s+(?P<priority>\d+)\."
                        r"(?P<id>\S+)")
    rx_interface = re.compile(r"^\s+(?P<ifname>\S+)\s+(?P<port>\d+\.\d+)\s+"
                        r"(?:\d+\s+)?\d+\s+(?P<state>\S+)\s+(?P<role>\S+)\s+"
                        r"(?P<dsg_bridge>\d+\.\S+)\s+(?P<dsg_port>\d+\.\d+)")
    rx_edge = re.compile(r"^Edge port\s+: (?P<edge>\S+)$",
                        re.MULTILINE)
    rx_p2p = re.compile(r"^Link type\s+: (?P<p2p>.+)$",
                        re.MULTILINE)
    rx_mst_conf = re.compile("Name\s+(?P<name>\S+)\n"
                        r"Revision\s+(?P<rev>\d+)")

    def execute(self):
        # defaults
        r = {
            "mode": "None",
            "instances": []
        }
        inst_id = 0
        # detect STP mode
        cmd = self.cli("show spanning-tree")
        if "Global MSTP is disabled" in cmd:
            return r
        match = self.rx_mode.search(cmd)
        if match:
            r["mode"] = {
                "802.1d": "STP",
                "802.1w": "RSTP",
                "802.1s": "MSTP"
            }[match.group("mode")]
        # get instances
        cmd = self.cli("show spanning-tree mst")
        for inst in cmd.split("\n#"):
            if "does not exist!" in inst:
                continue
            for l in inst.splitlines():
                # get instance id
                match = self.rx_inst_id.match(l)
                if match:
                    inst_id = match.group("inst_id")
                    continue
                # get vlans
                match = self.rx_vlans.match(l)
                if match:
                    vlans = match.group("vlans")
                    continue
                # get bridge id and priority
                match = self.rx_bridge.match(l)
                if match:
                    bridge_id = match.group("id")
                    bridge_priority = match.group("priority")
                    ifaces = []
                    continue
                # get root id and priority
                match = self.rx_root.match(l)
                if match:
                    root = match.group("root")
                    if root == "this switch":
                        root_id = bridge_id
                        root_priority = bridge_priority
                    else:
                        root_id = root.split(".")[1]
                        root_priority = root.split(".")[0]
                    continue
                # get interfaces
                match = self.rx_interface.match(l)
                if match:
                    port = match.group("port").split(".")
                    dsg_bridge = match.group("dsg_bridge").split(".")
                    dsg_port = match.group("dsg_port").split(".")
                    iface = match.group("ifname")
                    # get interface details
                    if_details = self.cli("show spanning-tree interface %s detail" % iface)
                    e_match = self.rx_edge.search(if_details)
                    if e_match:
                        edge = (e_match.group("edge") == "Yes")
                    else:
                        edge = False
                    p2p_match = self.rx_p2p.search(if_details)
                    if p2p_match:
                        p2p = "point-to-point" in p2p_match.group("p2p")
                    else:
                        p2p = False
                    ifaces += [{
                        "interface": iface,
                        "port_id": int(port[1]),
                        "priority": port[0],
                        "state": {
                            "FWD": "forwarding",
                            "LRN": "learning",
                            "BLK": "discarding"
                        }[match.group("state")],
                        "role": {
                            "ROOT": "root",
                            "DSGN": "designated",
                        }[match.group("role")],
                        "designated_bridge_id": dsg_bridge[1],
                        "designated_bridge_priority": dsg_bridge[0],
                        "designated_port_id": int(dsg_port[1]),
                        "point_to_point": p2p,
                        "edge": edge
                    }]
                    continue

            r["instances"] += [{
                "id": inst_id,
                "bridge_id": bridge_id,
                "bridge_priority": bridge_priority,
                "root_id": root_id,
                "root_priority": root_priority,
                "interfaces": ifaces,
                "vlans": vlans.replace(";", ",")
            }]
        cmd = self.cli("show spanning-tree mst config")
        match = self.rx_mst_conf.search(cmd)
        if match:
            r["configuration"] = {
                "MSTP": {
                    "region": match.group("name"),
                    "revision": match.group("rev")
                }
            }

        return r

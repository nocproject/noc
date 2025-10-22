# ---------------------------------------------------------------------
# Qtech.QSW2800.get_spanning_tree
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree


class Script(BaseScript):
    name = "Qtech.QSW2800.get_spanning_tree"
    interface = IGetSpanningTree

    rx_mode = re.compile(r"^Standard\s+:\s+IEEE (?P<mode>\S+)", re.MULTILINE)
    rx_inst_id = re.compile(r"^#+ Instance (?P<inst_id>\d+) #+", re.MULTILINE)
    rx_vlans = re.compile(r"^vlans mapped\s+: (?P<vlans>\S+)$")
    rx_root = re.compile(r"^(?:Region )?Root Id\s+:\s+(?P<root>\d*\.?\S+\s?\S*)")
    rx_bridge = re.compile(r"Self Bridge Id\s+:\s+(?P<priority>\d+)\.(?P<id>\S+)")
    rx_interface = re.compile(
        r"^\s*(?P<ifname>\S+)\s+(?P<port>\d+\.\d+)\s+"
        r"(?:\d+\s+)?\d+\s+(?P<state>\S+)\s+(?P<role>\S+)\s+"
        r"(?P<dsg_bridge>\d+\.\S+)\s+(?P<dsg_port>\d+\.\d+)"
    )
    rx_edge = re.compile(r"^Edge port\s+: (?P<edge>\S+)$", re.MULTILINE)
    rx_p2p = re.compile(r"^Link type\s+: (?P<p2p>.+)$", re.MULTILINE)
    rx_mst_conf = re.compile(r"Name\s+(?P<name>\S+)\nRevision\s+(?P<rev>\d+)")

    def execute(self):
        def q_port(s):
            if "." in s:
                x, y = [int(k) for k in s.split(".")]
                return "%d.%d" % (x, y)
            return s

        def port_priority(s):
            return int(s.split(".")[0])

        # defaults
        r = {"mode": "None", "instances": []}
        inst_id = 0
        # detect STP mode
        cmd = self.cli("show spanning-tree")
        if "Global MSTP is disabled" in cmd:
            return r
        match = self.rx_mode.search(cmd)
        if match:
            r["mode"] = {"802.1d": "STP", "802.1w": "RSTP", "802.1s": "MSTP"}[match.group("mode")]
        vlans = "1-4095"
        # get instances
        if r["mode"] == "MSTP":
            instances = self.rx_inst_id.findall(cmd)
        else:
            instances = ["0"]
        for i in instances:
            inst = self.cli("show spanning-tree mst %s" % i)
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
                    port = q_port(match.group("port"))
                    dsg_bridge = match.group("dsg_bridge").split(".")
                    dsg_port = q_port(match.group("dsg_port"))
                    iface = match.group("ifname")
                    # get interface details
                    if_details = self.cli("show spanning-tree interface %s detail" % iface)
                    e_match = self.rx_edge.search(if_details)
                    if e_match:
                        edge = e_match.group("edge") == "Yes"
                    else:
                        edge = False
                    p2p_match = self.rx_p2p.search(if_details)
                    if p2p_match:
                        p2p = "point-to-point" in p2p_match.group("p2p")
                    else:
                        p2p = False
                    ifaces += [
                        {
                            "interface": iface,
                            "port_id": port,
                            "priority": port_priority(port),
                            "state": {"FWD": "forwarding", "LRN": "learning", "BLK": "discarding"}[
                                match.group("state")
                            ],
                            "role": {
                                "ROOT": "root",
                                "DSGN": "designated",
                                "ALTR": "alternate",
                                "BKUP": "backup",
                                "MSTR": "master",
                            }[match.group("role")],
                            "designated_bridge_id": dsg_bridge[1],
                            "designated_bridge_priority": dsg_bridge[0],
                            "designated_port_id": dsg_port,
                            "point_to_point": p2p,
                            "edge": edge,
                        }
                    ]
                    continue

            r["instances"] += [
                {
                    "id": inst_id,
                    "bridge_id": bridge_id,
                    "bridge_priority": bridge_priority,
                    "root_id": root_id,
                    "root_priority": root_priority,
                    "interfaces": ifaces,
                    "vlans": vlans.replace(";", ","),
                }
            ]
        cmd = self.cli("show spanning-tree mst config")
        match = self.rx_mst_conf.search(cmd)
        if match:
            r["configuration"] = {
                "MSTP": {"region": match.group("name"), "revision": match.group("rev")}
            }

        return r

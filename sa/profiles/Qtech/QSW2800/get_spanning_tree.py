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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSpanningTree


class Script(NOCScript):
    name = "Qtech.QSW2800.get_spanning_tree"
    implements = [IGetSpanningTree]

    rx_mode = re.compile(r"^Standard\s+:\s+IEEE (?P<mode>\S+)")
    rx_inst_id = re.compile(r"^#+ Instance (?P<inst_id>\d+) #+")
    rx_root = re.compile(r"^(?:Region )?Root Id\s+:\s+"
                        r"(?P<root>\d*\.?\S+\s?\S*)")
    rx_bridge = re.compile(r"Self Bridge Id\s+:\s+(?P<priority>\d+)\."
                        r"(?P<id>\S+)")
    rx_interface = re.compile(r"^\s+(?P<ifname>\S+)\s+(?P<port>\d+\.\d+)\s+"
                        r"(?:\d+\s+)?\d+\s+(?P<state>\S+)\s+(?P<role>\S+)\s+"
                        r"(?P<dsg_bridge>\d+\.\S+)\s+(?P<dsg_port>\d+\.\d+)")

    def execute(self):

        cmd = self.cli("show spanning-tree")
        # default result
        r = {
            "mode": "None",
            "instances": []
        }
        # STP is disabled
        if "Global MSTP is disabled" in cmd:
            return r

        for l in cmd.splitlines():
            # detect STP mode
            match = self.rx_mode.match(l)
            if match:
                r["mode"] = {
                    "802.1d": "STP",
                    "802.1w": "RSTP",
                    "802.1s": "MSTP"
                }[match.group("mode")]
                continue
            # get instance id
            match = self.rx_inst_id.match(l)
            if match:
                inst_id = match.group("inst_id")
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
                ifaces += [{
                    "interface": match.group("ifname"),
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
                    "point_to_point": True, # temp
                    "edge": False # temp
                }]
                continue

            r["instances"] += [{
                "id": inst_id if r["mode"] == "MSTP" else 0,
                "bridge_id": bridge_id,
                "bridge_priority": bridge_priority,
                "root_id": root_id,
                "root_priority": root_priority,
                "interfaces": ifaces,
                "vlans": "1-4095"
            }]

        return r

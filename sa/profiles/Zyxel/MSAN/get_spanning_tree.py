# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.MSAN.get_spanning_tree
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree


class Script(BaseScript):
    name = "Zyxel.MSAN.get_spanning_tree"
    interface = IGetSpanningTree

    rx_status = re.compile(r"^status\s+: (?P<status>enable|disable)d?\s*\n", re.MULTILINE)
    rx_config = re.compile(
        r"^config name\s+: (?P<region>\S+)\s*\n"
        r"^revision level\s+: (?P<revision>\S+)\s*\n"
        r"^status\s+: (?P<status>\S+)\s*\n"
        r"^priority\s+: (?P<priority>\d+)\s*\n"
        r"^.+\n"
        r"^.+\n"
        r"^.+\n"
        r"^force version\s+: (?P<version>rstp|mstp)\s*\n",
        re.MULTILINE,
    )
    rx_mstid = re.compile(r"^\s*(?P<id>\d+) (?P<vlans>[0-9\-\,]+)\s*\n", re.MULTILINE)
    rx_bridge = re.compile(
        r"(?:BridgeID|bridge id)\s+:\s+(?P<bridge_priority>[0-9a-fx]+)-(?P<bridge_id>\S+)"
    )
    rx_root = re.compile(
        r"(?:ExtRootID|designated root)\s+:\s+(?P<root_priority>[0-9a-fx]+)-(?P<root_id>\S+)"
    )
    rx_port = re.compile(
        r"^Port \[\s*(?P<iface>\S+)\] info\s*\n"
        r"^Uptime\s+:.+\n"
        r"^State\s+:\s+(?P<state>\S+)\s*\n"
        r"^PortID\s+:\s+(?P<port_id>\S+)\s*\n"
        r"^DsgBridgeID\s+:\s+(?P<ds_br_pr>[0-9a-fx]+)-(?P<ds_br_id>\S+)\s*\n"
        r"^DsgPortID\s+:\s+(?P<dsg_port_id>\S+)\s*\n"
        r"^ExtPortPathCost\s+:\s+\d+\s*\n"
        r"^ExtRootID\s+:\s+(?P<root_pr>[0-9a-fx]+)-(?P<root_id>\S+)\s*\n"
        r"^ExtRootPathCost\s+:\s+\d+\s*\n"
        r"^AdminEdgePort\s+:\s+\S+\s*\n"
        r"^OperEdgePort\s+:\s+(?P<edge>\S+)\s*\n"
        r"^MACOperational\s+:\s+\S+\s*\n"
        r"^AdminP2PLink\s+:\s+\S+\s*\n"
        r"^OperP2PLink\s+:\s+(?P<p2p>\S+)\s*\n",
        re.MULTILINE,
    )

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

    def get_inst(self, inst_id):
        if inst_id == 0:
            vlans = "1-4095"
        else:
            vlans = ""
        inst = {"id": inst_id, "vlans": vlans, "interfaces": []}
        try:
            v = self.cli("show mstp %s" % inst_id)
        except self.CLISyntaxError:
            v = self.cli("statistics rstp")
        match = self.rx_root.search(v)
        inst["root_priority"] = int(match.group("root_priority"), 16)
        inst["root_id"] = match.group("root_id")
        match = self.rx_bridge.search(v)
        inst["bridge_priority"] = int(match.group("bridge_priority"), 16)
        inst["bridge_id"] = match.group("bridge_id")
        for match in self.rx_port.finditer(v):
            state = match.group("state")
            if match.group("ds_br_id") == inst["bridge_id"]:
                role = "designated"
            elif state == "forwarding":
                role = "root"
            elif state == "discarding":
                role = "alternate"
            else:
                role = "unknown"
            iface = {
                "interface": match.group("iface"),
                "port_id": self.hex_to_portid(match.group("port_id")),
                "state": state,
                "role": role,
                "priority": int(match.group("port_id"), 16),
                "designated_bridge_id": match.group("ds_br_id"),
                "designated_bridge_priority": int(match.group("ds_br_pr"), 16),
                "designated_port_id": self.hex_to_portid(match.group("dsg_port_id")),
                "edge": match.group("edge") == "true",
                "point_to_point": match.group("p2p") == "true",
            }
            inst["interfaces"] += [iface]
        return inst

    def process_rstp(self):
        return self.get_inst(0)

    def process_mstp(self, inst, vlans):
        i = self.get_inst(inst)
        i["vlans"] = vlans
        return i

    def execute(self):
        try:
            v = self.cli("switch mstp show", cached=True)
            mode = "mstp"
        except self.CLISyntaxError:
            v = self.cli("switch rstp show", cached=True)
            mode = "rstp"
        match = self.rx_status.search(v)
        if match.group("status") != "enable":
            return {"mode": "None", "instances": []}
        if mode == "rstp":
            r = {"mode": "RSTP", "instances": [self.process_rstp()]}
        else:
            match = self.rx_config.search(v)
            r = {
                "mode": "MSTP",
                "configuration": {
                    "MSTP": {
                        "region": match.group("region"),
                        "revision": int(match.group("revision")),
                    }
                },
                "instances": [],
            }
            for match1 in self.rx_mstid.finditer(v):
                r["instances"] += [self.process_mstp(match1.group("id"), match1.group("vlans"))]
        return r

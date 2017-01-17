# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_spanning_tree
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import itertools
import time
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "DLink.DxS.get_spanning_tree"
    interface = IGetSpanningTree

    rx_stp = re.compile(
        r"^\s*STP Bridge Global Settings\n"
        r"^\s*\-+\n"
        r"^\s*STP Status\s+: (?P<status>Enabled|Disabled)\s*"
        r"^\s*STP Version\s+: (?P<mode>STP|RSTP)\s*", re.MULTILINE)
    rx_ins = re.compile(
        r"^\s*STP Instance Settings\n"
        r"^\s*\-+\n"
        r"^\s*Instance Type\s+: (?P<inst_type>\S+)\s*\n"
        r"^\s*Instance Status\s+: Enabled \n"
        r"^\s*Instance Priority\s+: .+\n"
        r"^\s*\n"
        r"^\s*STP Instance Operational Status\n"
        r"^\s*\-+\n"
        r"^\s*Designated Root Bridge\s+: (?P<root_priority>\d+)\s*/(?P<root_id>\S+)\s*\n"
        r"^\s*External Root Cost\s+: (?P<ext_root_cost>\d+)\s*\n"
        r"^\s*Regional Root Bridge\s+: (?P<rbridge_priority>\d+)\s*/(?P<rbridge_id>\S+)\s*\n"
        r"^\s*Internal Root Cost\s+: (?P<int_root_cost>\d+)\s*\n"
        r"^\s*Designated Bridge\s+: (?P<bridge_priority>\d+)\s*/(?P<bridge_id>\S+)\s*\n"
        r"^\s*Root Port\s+: (?P<root_port>\S+)\s*\n", re.MULTILINE)
    rx_ins1 = re.compile(
        r"^\s*Designated Root Bridge\s+(?P<root_id>\S+)\s+Priority\s+(?P<root_priority>\d+)\s*\n"
        r"(^\s*.*\n)?"
        r"^\s*Port (?P<root_port>\d+)\s+,\s+path cost (?P<ext_root_cost>\d+)\s*\n"
        r"^\s*Regional Root Bridge\s+(?P<rbridge_id>\S+)\s+Priority\s+(?P<rbridge_priority>\d+)\s*\n"
        r"^\s*Path cost (?P<int_root_cost>\d+)\s*\n"
        r"^\s*Designated Bridge\s+(?P<bridge_id>\S+)\s+Priority\s+(?P<bridge_priority>\d+)\s*\n",
        re.MULTILINE)
    rx_ins2 = re.compile(
        r"^\s*Bridge\s+Address (?P<bridge_id>\S+)\s+Priority\s+(?P<bridge_priority>\d+)\s*\n"
        r"^\s*Root\s+Address (?P<root_id>\S+)\s+Priority\s+(?P<root_priority>\d+)\s*\n",
        re.MULTILINE)
    rx_iface_role = re.compile(
        r"^\s*(?P<iface>\d+)\s+(P<role>\S+)\s+(P<status>\S+)\s+\d+(?P<prio_n>\S+)\s+(?P<type>.+)\n",
        re.MULTILINE)
    rx_iface = re.compile(
        r"^\s*Port Index\s+: (?P<iface>\d+)\s+,.+\n"
        r"(^\s*.*\n)?"
        r"^\s*External PathCost : \S+\s+, Edge Port : \S+\s*/(?P<edge>Yes|No) , P2P : \S+\s*/(?P<p2p>Yes|No)\s*\n"
        r"(^\s*.*\n)?"
        r"^\s*Port Forward BPDU : (?:Enabled|Disabled)\s*\n"
        r"^\s*MSTI   Designated Bridge   Internal PathCost  Prio  Status      Role\n"
        r"^\s*-----  ------------------  -----------------  ----  ----------  ----------\n"
        r"^\s*0\s+(?P<d_bridge>\S+)\s+(?P<patch_cost>\d+)\s+(?P<priority>\d+)\s+(?P<status>\S+)\s+(?P<role>\S+)\s*\n",
        re.MULTILINE)
    rx_iface1 = re.compile(
        r"^\s*Port Index:\s*(?P<iface>\d+).+\n"
        r"^\s*External PathCost : \S+\s+,\s+Edge Port:.+\n"
        r"(^\s*.*\n)?"
        r"^\s*Port Priority:\s*(?P<p_priority>\d+) ,\s+Port Forward BPDU:\s*(?:Enabled|Disabled).+\n"
        r"^\s*MSTI Designated Bridge        Internal PathCost  Prio  Status      Role\n"
        r"^\s*---- ------------------       -----------------  ----  ----------  ----------\n"
        r"^\s*0\s+(?P<d_bridge>\S+)\s+(?P<patch_cost>\d+)\s+(?P<priority>\d+)\s+(?P<status>\S+)\s+(?P<role>\S+)\s*\n",
        re.MULTILINE)
    """
    rx_mst = re.compile(
        r" Current MST Configuration Identification\n"
        r" ----------------------------------------\n"
        r"\n"
        r" Configuration Name : (?P<name>\S+)\s+Revision Level :0\n"
        r" MSTI ID           VID List\n"
        r" -------           -------------------------------------------------------------\n"
        r"    CIST           (?P<vlans>\S+)\n", re.MULTILINE)
    rx_mst1 = re.compile(
        r"Name            \[(?P<name>\S+)\]\s*\n"
        r"Revision        0\n"
        r"Instance        Vlans mapped\n"
        r" --------      ------------------------------------------\n"
        r"  0              (?P<vlans>\S+)\n"
        r" -------------------------------------------------------\n",
        re.MULTILINE)
    """
    PORT_STATE = {
        "Broken": "broken",
        "Disabled": "disabled",
        "Discarding": "discarding",
        "Forwarding": "forwarding",
        "Loopback": "loopback",
        "Learning": "learning",
        "Listen": "listen"
    }
    PORT_ROLE = {
        "Alternate": "alternate",
        "Backup": "backup",
        "Designated": "designated",
        "Disabled": "disabled",
        "Master": "master",
        "Root": "root",
        "NonStp": "nonstp",
    }
    designated_bridge = ""

    def parse_stp(self, s):
        match = self.rx_iface.search(s)
        if match:
            d_bridge = match.group("d_bridge")
            if d_bridge != "N/A":
                desg_priority, desg_id = d_bridge.split("/")
                desg_priority = int(desg_priority, 16)
            else:
                desg_priority, desg_id = 128, self.designated_bridge
            iface = {
                "interface": match.group("iface"),
                "port_id": "%d.%d" % (int(match.group("priority")), int(match.group("iface"))),
                "state": self.PORT_STATE[match.group("status")],
                "role": self.PORT_ROLE[match.group("role")],
                "priority": match.group("priority"),
                "designated_bridge_id": desg_id,
                "designated_bridge_priority": desg_priority,
                "designated_port_id": "%d.%d" % (int(match.group("priority")), int(match.group("iface"))),
                "point_to_point": match.group("p2p") == "Yes",
                "edge": match.group("edge") == "Yes"
            }
        else:
            match = self.rx_iface1.search(s)
            if match:
                d_bridge = match.group("d_bridge")
                if d_bridge != "N/A":
                    desg_id = d_bridge[6:]
                    desg_priority = d_bridge[:6].replace(":", "")
                    desg_priority = int(desg_priority, 16)
                else:
                    desg_priority, desg_id = 128, self.designated_bridge
                edge = False
                p2p = False
                iface = match.group("iface")
                if int(iface) in iface_role:
                    p2p = iface_role[int(iface)]["type"] == "Point to point"
                iface = {
                    "interface": match.group("iface"),
                    "port_id": "%d.%d" % (int(match.group("p_priority")), int(match.group("iface"))),
                    "state": self.PORT_STATE[match.group("status")],
                    "role": self.PORT_ROLE[match.group("role")],
                    "priority": match.group("p_priority"),
                    "designated_bridge_id": desg_id,
                    "designated_bridge_priority": desg_priority,
                    "designated_port_id": "%d.%d" % (int(match.group("priority")), int(match.group("iface"))),
                    "point_to_point": p2p,
                    "edge": False
                }
        if match:
            key = match.group("iface")
            return key, iface, s[match.end():]
        else:
            return None

    def execute(self):
        try:
            c = self.cli("show stp")
        except self.CLISyntaxError:
            return {"mode": "None", "instances": []}
        match = self.rx_stp.search(c)
        if (not match) or (not match.group("mode")):
            return {"mode": "None", "instances": []}
        stp = {
            "mode": match.group("mode"),
            "instances": []
        }
        c = self.cli("show stp instance\nq", ignore_errors=True)
        match = self.rx_ins.search(c)
        if not match:
            match = self.rx_ins1.search(c)
            if not match:
                match = self.rx_ins2.search(c)
                if not match:
                    return {"mode": "None", "instances": []}
            iface_role = []
            for match_r in self.rx_iface_role.finditer(c):
                iface_role[int(match_r.group("iface"))] = {
                    "role": match_r.group("role"),
                    "state": match_r.group("status"),
                    "prio_n": match_r.group("prio_n"),
                    "type": match_r.group("type").strip()
                }
        inst = {
            "id": 0,
            "vlans": "1-4095",
            "root_id": match.group("root_id"),
            "root_priority": int(match.group("root_priority")),
            "bridge_id": match.group("bridge_id"),
            "bridge_priority": int(match.group("bridge_priority")),
            "interfaces": []
        }
        self.designated_bridge = match.group("bridge_id")
        c = self.cli(
            "show stp ports", obj_parser=self.parse_stp,
            cmd_next="n", cmd_stop="q"
        )
        for i in c:
            inst["interfaces"] += [i]
        stp["instances"] += [inst]
        return stp

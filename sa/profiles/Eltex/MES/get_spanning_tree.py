# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_spanning_tree
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree
from noc.lib.text import parse_table


class Script(NOCScript):
    name = "Eltex.MES.get_spanning_tree"
    implements = [IGetSpanningTree]

    TIMEOUT = 240

    rx_ins = re.compile(
        r"^(?P<instance>\d+)\s+Vlans Mapped:\s+(?P<vlans>\S+)$",
        re.MULTILINE)

    PORT_STATE = {
        "bkn": "broken",
        "dsbl": "disabled",
        "dscr": "discarding",
        "frw": "forwarding",
        "lbk": "loopback",
        "lrn": "learning",
        "lis": "listen",
        "??": "learning",
    }

    PORT_ROLE = {
        "altn": "alternate",
        "back": "backup",
        "boun": "master",
        "desg": "designated",
        "dsbl": "disabled",
        "mstr": "master",
        "root": "root",
        "????": "nonstp",
        "_": "unknown"
    }

    def get_ports_attrs(self, cli_stp, sep):
        """
        Get port attributes (Link type and edge status)
        :param cli_stp:
        :return: hash of port -> {link_type: , edge, role, status}
        """
        ports = {}  # instance -> port -> attributes
        instance_id = 0
        for instance in cli_stp.split(sep):
            match = self.rx_ins.search(instance)
            if match:
                instance_id = int(match.group("instance"))
            ports[instance_id] = {}
            for I in parse_table(instance):
                interface = I[0]
                priority = I[2].split('.')[0]
                ports[instance_id][interface] = {
                    "status": I[1].lower() == 'enabled',
                    "priority": priority,
                    "port_id": I[2],
                    "cost": I[3],
                    "state": self.PORT_STATE[I[4].lower()],
                    "role": self.PORT_ROLE[I[5].lower()],
                    "point_to_point": "p2p" in I[7].lower(
                    ).split(' '),
                }
        return ports

    #
    # STP/RSTP Parsing
    #
    rx_pvst_root = re.compile(
        r"^\s+Root ID\s+Priority\s+(?P<root_priority>\d+).\s+"
        r"Address\s+(?P<root_id>\S+)",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    rx_pvst_bridge = re.compile(
        r"^\s+Bridge ID\s+Priority\s+(?P<bridge_priority>\d+).\s+"
        r"Address\s+(?P<bridge_id>\S+)",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    rx_pvst_interfaces = re.compile(
        r"Port\s+(?P<interface>\S+)\s+(?P<status>(enabled|disabled))\s*."
        r"State:\s+\S+\s+Role:\s+\S+\s*."
        r"Port id:\s+(?P<port_id>\d+\.\d+)\s+Port cost:\s+(?P<cost>\d+)\s*."
        r"Type:\s+\S+\s+\(configured:\S+\s+(\S+\s+|)\)\s+(\S+\s+|)"
        r"Port Fast:\s+\S+\s+\(configured:\S+\)\s*."
        r"Designated bridge Priority\s*:\s+"
        r"(?P<designated_bridge_priority>\d+)\s+"
        r"Address:\s+(?P<designated_bridge_id>\S+)\s*."
        r"Designated port id:\s+(?P<designated_port_id>\d+\.\d+)",
        re.DOTALL | re.IGNORECASE | re.MULTILINE)

    def process_pvst(self, cli_stp, proto, sep):
        # Save port attributes
        ports = self.get_ports_attrs(cli_stp, sep)
        r = {
            "mode": proto,
            "instances": []
        }
        interfaces = {}
        instance_id = 0
        interfaces[instance_id] = []
        for I in self.cli("show spanning-tree detail").split(
                "BPDU: sent"):
            match_r = self.rx_pvst_root.search(I)
            match_b = self.rx_pvst_bridge.search(I)
            if match_b:
                r["instances"] += [{
                    "id": instance_id,
                    "vlans": "",
                    "root_id": match_r.group("root_id"),
                    "root_priority": match_r.group("root_priority"),
                    "bridge_id": match_b.group("bridge_id"),
                    "bridge_priority": match_b.group("bridge_priority"),
                }]
            elif match_r:
                r["instances"] += [{
                    "id": instance_id,
                    "vlans": "",
                    "root_id": match_r.group("root_id"),
                    "root_priority": match_r.group("root_priority"),
                    "bridge_id": match_r.group("root_id"),
                    "bridge_priority": match_r.group("root_priority"),
                }]

            match = self.rx_pvst_interfaces.search(I)
            if match:
                interface = match.group("interface")
                port_attrs = ports[instance_id][interface]
                interfaces[instance_id] += [{
                    "interface": interface,
                    "port_id": match.group("port_id"),
                    "state": port_attrs["state"],
                    "role": port_attrs["role"],
                    "priority": port_attrs["priority"],
                    "designated_bridge_id": match.group(
                        "designated_bridge_id"),
                    "designated_bridge_priority": match.group(
                        "designated_bridge_priority"),
                    "designated_port_id": match.group(
                        "designated_port_id"),
                    "point_to_point": port_attrs["point_to_point"],
                    "edge": port_attrs["status"],
                }]
            for I in r["instances"]:
                I["interfaces"] = interfaces[I["id"]]
        return r

    #
    # MSTP Parsing
    #

    rx_mstp_rev = re.compile(
        r"^Name: (?P<region>\S+).Revision: (?P<revision>\d+)",
        re.DOTALL | re.MULTILINE)

    rx_mstp_ins = re.compile(
        r"^\s*(?P<instance>\d+)\s+Vlans Mapped:\s+(?P<vlans>\S+)\s*$",
        re.MULTILINE)

    rx_mstp_root = re.compile(
        r"^(CST |)Root ID\s+Priority\s+(?P<root_priority>\d+).\s+"
        r"Address\s+(?P<root_id>\S+)",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    rx_mstp_bridge = re.compile(
        r"^Bridge ID\s+Priority\s+(?P<bridge_priority>\d+).\s+"
        r"Address\s+(?P<bridge_id>\S+)",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    rx_mstp_interfaces = re.compile(
        r"Port\s+(?P<interface>\S+)\s+(?P<status>(enabled|disabled))\s*."
        r"State:\s+\S+\s+Role:\s+\S+\s*."
        r"Port id:\s+(?P<port_id>\d+\.\d+)\s+Port cost:\s+(?P<cost>\d+)\s*."
        r"Type:\s+\S+\s+\(configured:\S+\s+(\S+\s*|)\)\s+"
        r"(\S+\s+\S+\s+|\S+\s+|)"
        r"Port Fast:\s+\S+\s+\(configured:\s*\S+\)\s*."
        r"Designated bridge Priority\s*:\s+"
        r"(?P<designated_bridge_priority>\d+)\s+"
        r"Address:\s+(?P<designated_bridge_id>\S+)\s*."
        r"Designated port id:\s+(?P<designated_port_id>\d+.\d+)",
        re.DOTALL | re.IGNORECASE | re.MULTILINE)

    def process_mstp(self, cli_stp, sep):
        # Save port attributes
        ports = self.get_ports_attrs(cli_stp, sep)

        v = self.cli("show spanning-tree mst-configuration")
        match = self.rx_mstp_rev.search(v)
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

        interfaces = {}
        v = self.cli("show spanning-tree detail")
        instance_id = 0
        vlans = ""
        for instance in v.split(sep):
            match = self.rx_mstp_ins.search(instance)
            if match:
                instance_id = int(match.group("instance"))
                vlans = match.group("vlans")
            interfaces[instance_id] = []
            for I in instance.split("BPDU: sent"):
                match_r = self.rx_mstp_root.search(I)
                match_b = self.rx_mstp_bridge.search(I)
                if match_b:
                    r["instances"] += [{
                        "id": instance_id,
                        "vlans": vlans,
                        "root_id": match_r.group("root_id"),
                        "root_priority": match_r.group("root_priority"),
                        "bridge_id": match_b.group("bridge_id"),
                        "bridge_priority": match_b.group(
                            "bridge_priority"),
                    }]
                elif match_r:
                    r["instances"] += [{
                        "id": instance_id,
                        "vlans": vlans,
                        "root_id": match_r.group("root_id"),
                        "root_priority": match_r.group("root_priority"),
                        "bridge_id": match_r.group("root_id"),
                        "bridge_priority": match_r.group(
                            "root_priority"),
                    }]

                match = self.rx_mstp_interfaces.search(I)
                if match:
                    interface = match.group("interface")
                    port_attrs = ports[instance_id][interface]
                    interfaces[instance_id] += [{
                        "interface": interface,
                        "port_id": match.group("port_id"),
                        "state": port_attrs["state"],
                        "role": port_attrs["role"],
                        "priority": port_attrs["priority"],
                        "designated_bridge_id": match.group(
                            "designated_bridge_id"),
                        "designated_bridge_priority": match.group(
                            "designated_bridge_priority"),
                        "designated_port_id": match.group(
                            "designated_port_id").replace(' ', '.'),
                        "point_to_point": port_attrs["point_to_point"],
                        "edge": port_attrs["status"],
                    }]
        for I in r["instances"]:
            I["interfaces"] = interfaces[I["id"]]
        return r

    def execute(self):
        v = self.cli("show spanning-tree")
        if "Spanning tree enabled mode STP" in v:
            return self.process_pvst(v, proto="STP", sep="###### STP ")
        elif "Spanning tree enabled mode RSTP" in v:
            return self.process_pvst(v, proto="RSTP", sep="###### RST ")
        elif "Spanning tree enabled mode MSTP" in v:
            return self.process_mstp(v, sep="###### MST ")
        else:
            return {"mode": "None", "instances": []}

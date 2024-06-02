# ----------------------------------------------------------------------
# Cisco.SMB.get_spanning_tree
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Cisco.SMB.get_spanning_tree"
    interface = IGetSpanningTree

    def get_ports_attrs(self, cli_stp, instance_sep):
        """
        Get port attributes (Link type and edge status)
        :param cli_stp:
        :param instance_sep:
        :return: hash of instance_id -> port -> {link_type: , edge, role,
            status}
        """
        ports = {}  # instance -> port -> attributes
        for I in cli_stp.split(instance_sep)[1:]:
            instance_id = I.split(" ", 1)[0]
            if not instance_id:  # STP/RSTP
                instance_id = 0
            instance_id = int(instance_id)
            ports[instance_id] = {}
            for R in parse_table(I):
                interface = self.profile.convert_interface_name(R[0])
                settings = R[6]
                ports[instance_id][interface] = {
                    "point_to_point": "p2p" in " ".join(R).lower(),
                    "edge": "yes" in settings.lower(),
                    "role": {
                        "boun": "designated",
                        "dsbl": "disabled",
                        "altn": "alternate",
                        "back": "backup",
                        "root": "root",
                        "desg": "designated",
                        "mstr": "master",
                        "????": "nonstp",
                        "-": "unknown",
                        "_": "unknown",
                    }[
                        R[5].lower()
                    ],  # @todo: refine roles
                    "state": {
                        "dsbl": "disabled",
                        "dis": "disabled",
                        "blk": "discarding",
                        "bkn": "broken",
                        "lrn": "learning",
                        "??": "learning",
                        "frw": "forwarding",
                        "fwd": "forwarding",
                        "lis": "listen",
                        "lst": "listen",
                        "_": "unknown",
                        "-": "unknown",
                        "lbk": "loopback",
                    }[
                        R[4].lower()
                    ],  # @todo: refine states
                }
        return ports

    #
    # PVST+/rapid-PVST+ Parsing
    #
    rx_pvst_bridge = re.compile(
        r"(CST )?Root ID\s+Priority\s+(?P<root_priority>\d+).+Address\s+(?P<root_id>\S+).+(Bridge ID\s+Priority\s+(?P<bridge_priority>\d+).+Address\s+(?P<bridge_id>\S+))?",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_pvst_interfaces = re.compile(
        r"^Port\s+(?P<interface>\S+)\s+enabled.+?"
        r"State:\s+(?P<status>\S+)\s+Role:\s+(?P<role>\S+).+?"
        r"Port\s+id:\s+(?P<port_id>\S+)\s+Port\s+cost:\s+(?P<cost>\d+).+?"
        r"Designated\s+bridge\s+Priority\s+:\s+(?P<designated_bridge_priority>\d+)\s+Address:\s+(?P<designated_bridge_id>\S+).+?"
        r"Designated\s+port\s+id:\s+(?P<designated_port_id>\S+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    def process_pvst(self, cli_stp, proto):
        # Save port attributes
        ports = self.get_ports_attrs(cli_stp, "Name")
        #
        reply = {"mode": proto, "instances": []}
        interfaces = {}
        spanning_tree_detail = self.cli("show spanning-tree detail")
        instance_id = 0
        interfaces[instance_id] = []
        match = self.rx_pvst_bridge.search(spanning_tree_detail)
        reply["instances"] += [
            {
                "id": instance_id,
                "vlans": "1-4095",
                "root_id": match.group("root_id"),
                "root_priority": match.group("root_priority"),
                "bridge_id": (
                    match.group("bridge_id") if match.group("bridge_id") else match.group("root_id")
                ),
                "bridge_priority": (
                    match.group("bridge_priority")
                    if match.group("bridge_priority")
                    else match.group("root_priority")
                ),
            }
        ]
        for match in self.rx_pvst_interfaces.finditer(spanning_tree_detail):
            interface = self.profile.convert_interface_name(match.group("interface"))
            port_attrs = ports[instance_id][interface]
            interfaces[instance_id] += [
                {
                    "interface": interface,
                    "port_id": match.group("port_id"),
                    "state": port_attrs["state"],
                    "role": port_attrs["role"],
                    "priority": match.group("port_id").split(".", 1)[0],
                    "designated_bridge_id": match.group("designated_bridge_id"),
                    "designated_bridge_priority": match.group("designated_bridge_priority"),
                    "designated_port_id": match.group("designated_port_id"),
                    "point_to_point": port_attrs["point_to_point"],
                    "edge": port_attrs["edge"],
                }
            ]
        for INST in reply["instances"]:
            INST["interfaces"] = interfaces[INST["id"]]
        return reply

    #
    # MSTP Parsing
    #
    rx_mstp_region = re.compile(
        r"Name:\s+(?P<region>\S+).+Revision:\s+(?P<revision>\d+)",
        re.DOTALL | re.MULTILINE | re.IGNORECASE,
    )
    rx_mstp_instance = re.compile(r"^\s*(\d+)\s+(\S+)", re.MULTILINE)
    rx_mstp_bridge = re.compile(
        r"(CST )?Root ID\s+Priority\s+(?P<root_priority>\d+).+Address\s+(?P<root_id>\S+).+(Bridge ID\s+Priority\s+(?P<bridge_priority>\d+).+Address\s+(?P<bridge_id>\S+))?",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_mstp_interfaces = re.compile(
        r"^Port\s+(?P<interface>\S+)\s+enabled.+?"
        r"State:\s+(?P<status>\S+)\s+Role:\s+(?P<role>\S+).+?"
        r"Port\s+id:\s+(?P<port_id>\S+)\s+Port\s+cost:\s+(?P<cost>\d+).+?"
        r"Designated\s+bridge\s+Priority\s+:\s+(?P<designated_bridge_priority>\d+)\s+Address:\s+(?P<designated_bridge_id>\S+).+?"
        r"Designated\s+port\s+id:\s+(?P<designated_port_id>\S+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    def process_mstp(self, cli_stp):
        instance_sep = "\n###### MST "
        # Save port attributes
        ports = self.get_ports_attrs(cli_stp, instance_sep)
        #
        spanning_tree_mst_configuration = self.cli("show spanning-tree mst-configuration")
        match = self.rx_mstp_region.search(spanning_tree_mst_configuration)
        reply = {
            "mode": "MSTP",
            "instances": [],
            "configuration": {
                "MSTP": {"region": match.group("region"), "revision": match.group("revision")}
            },
        }
        iv = {}  # instance -> vlans
        for instance, vlans in self.rx_mstp_instance.findall(spanning_tree_mst_configuration):
            iv[int(instance)] = vlans
        #
        interfaces = {}
        for INS in self.cli("show spanning-tree detail").split(instance_sep)[1:]:
            instance_id = int(INS.split(" ", 1)[0])
            if instance_id not in interfaces:
                interfaces[instance_id] = []
            match = self.rx_mstp_bridge.search(INS)
            root_id = match.group("root_id")
            root_priority = match.group("root_priority")
            bridge_id = match.group("bridge_id")
            bridge_priority = match.group("bridge_priority")
            # we are the root bridge for instance
            if not bridge_id and not bridge_priority:
                bridge_id = root_id
                bridge_priority = root_priority
            reply["instances"] += [
                {
                    "id": instance_id,
                    "vlans": iv[instance_id],
                    "root_id": root_id,
                    "root_priority": root_priority,
                    "bridge_id": bridge_id,
                    "bridge_priority": bridge_priority,
                }
            ]
            for match in self.rx_mstp_interfaces.finditer(INS):
                interface = self.profile.convert_interface_name(match.group("interface"))
                port_attrs = ports[instance_id][interface]
                port_id = match.group("port_id")
                priority = port_id.split(".", 1)[0]
                interfaces[instance_id] += [
                    {
                        "interface": interface,
                        "port_id": port_id,
                        "state": port_attrs["state"],
                        "role": port_attrs["role"],
                        "priority": priority,
                        "designated_bridge_id": match.group("designated_bridge_id"),
                        "designated_bridge_priority": match.group("designated_bridge_priority"),
                        "designated_port_id": match.group("designated_port_id"),
                        "point_to_point": port_attrs["point_to_point"],
                        "edge": port_attrs["edge"],
                    }
                ]
        for INST in reply["instances"]:
            INST["interfaces"] = interfaces[INST["id"]]
        return reply

    def execute_cli(self):
        v = self.cli("show spanning-tree")
        if "Spanning tree enabled mode STP" in v:
            return self.process_pvst(v, proto="STP")
        elif "Spanning tree enabled mode RSTP" in v:
            return self.process_pvst(v, proto="RSTP")
        elif "Spanning tree enabled mode MSTP" in v:
            return self.process_mstp(v)
        # elif "No spanning tree instance exists" in v \
        # or "No spanning tree instances exist" in v:
        else:
            return {"mode": "None", "instances": []}

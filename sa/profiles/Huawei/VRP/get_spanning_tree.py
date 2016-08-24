# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_spanning_tree
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Huawei.VRP.get_spanning_tree"
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
        # for I in cli_stp.split(instance_sep)[1:]:
        # instance_id, _ = I.split("\n", 1)
        # instance_id = int(instance_id)
        ports[0] = {}
        for R in cli_stp.splitlines()[1:]:
            if not R.strip():
                columns = []
                continue
            # R = R.strip()
            R = R.split()
                    # Skip empty first line on 3750
            #I.replace("---\n\n", "---\n")):
            interface = self.profile.convert_interface_name(R[1])
            settings = R[-1]
            ports[int(R[0])][interface] = {
                "point_to_point": True,  # @todo: detect P2P properly
                "edge": "edge" in settings.lower(),
                "role": {
                    "dis": "disabled",
                    "altn": "alternate",
                    "back": "backup",
                    "root": "root",
                    "desi": "designated",
                    "mstr": "master",
                    "????": "nonstp",
                    "_": "unknown"
                }[R[2].lower()],  # @todo: refine roles
                "state": {
                    "dis": "disabled",
                    "blk": "discarding",
                    "bkn": "broken",
                    "lrn": "learning",
                    "??": "learning",
                    "forwarding": "forwarding",
                    "listening": "listen",
                    "lbk": "loopback"
                }[R[3].lower()],  # @todo: refine states
            }
        return ports

    ##
    ## MSTP Parsing
    ##
    rx_mstp_region = re.compile(
        # r"Name\s+\[(?P<region>[^\]]*?)\].+Revision\s+(?P<revision>\d+)",
        r"Region name\s+:(?P<region>\S+).+Revision level\s+:(?P<revision>\d+)",
        re.DOTALL | re.MULTILINE | re.IGNORECASE)
    rx_mstp_instance = re.compile(r"^\s*(\d+)\s+(\S+)", re.MULTILINE)
    rx_mstp_bridge = re.compile(
        # "Bridge\s+address\s+(?P<bridge_id>\S+)\s+priority\s+(?P<bridge_priority>\d+).+?Root\s+address\s+(?P<root_id>\S+)\s+priority\s+(?P<root_priority>\d+)",
        r"CIST\sBridge\s+:(?P<bridge_priority>\d+)\.(?P<bridge_id>\S+).+?"
        r"CIST\sRoot/ERPC\s+:(?P<root_priority>\d+)\.(?P<root_id>\S+)\s",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_mstp_interfaces = re.compile(
        # r"^(?P<interface>\S+)\s+of\s+MST(?P<instance_id>\d+)\s+is\s+(?P<role>\S+)\s+(?P<status>\S+).+?"
        # r"Port\s+info\s+port\s+id\s+(?P<port_id>\S+)\s+priority\s+(?P<priority>\d+)\s+cost\s+(?P<cost>\d+).+?"
        # r"Designated\s+bridge\s+address\s+(?P<designated_bridge_id>\S+)\s+priority\s+(?P<designated_bridge_priority>\d+)\s+port\s+id\s+(?P<designated_port_id>\S+)",
        #r"^----\[(?P<port_id>\S+)\((?P<interface>\S+)\)\]\[(?P<state>\S+)\].+?"
        r"^----\[Port(?P<port_id>\d+)\((?P<interface>\S+)\)\]\[(?P<state>\S+)\].+?"
        r"Port\sProtocol\s+:(?P<status>\S+).+?"
        r"Port\sRole\s+:(?P<role>[\S\s]+?$).+?"
        r"Port\sPriority\s+:(?P<priority>\d+).+?"
        r"Port\sCost\(Dot1T \)\s+:.+?Active=(?P<cost>\d+).+?"
        r"Desg\.\sBridge/Port\s+:(?P<designated_bridge_priority>\d+)\.(?P<designated_bridge_id>\S+)\s/\s(?P<designated_port_id>\S+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def process_mstp(self, cli_stp):
        # Save port attributes
        ports = self.get_ports_attrs(cli_stp, "\nMST")
        #
        v = self.cli("display stp region-configuration")
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
        iv = {}  # instance -> vlans
        for instance, vlans in self.rx_mstp_instance.findall(v):
            if vlans == "none":
                vlans = ""
            iv[instance] = vlans
        #
        interfaces = {}
        for I in self.cli("display stp").split("-------\[")[0:]:
            # instance_id, _ = I.split(" ", 1)
            instance_id = "0"
            match = self.rx_mstp_bridge.search(I)
            r["instances"] += [{
                "id": int(instance_id),
                "vlans": iv[instance_id],
                "root_id": match.group("root_id"),
                "root_priority": match.group("root_priority"),
                "bridge_id": match.group("bridge_id"),
                "bridge_priority": match.group("bridge_priority"),
                }]
            v2 = self.rx_mstp_interfaces.finditer(I)
            v3 = self.rx_mstp_interfaces.findall(I)
            for match in v2:
                # instance_id = int(match.group("instance_id"))
                instance_id = 0
                if instance_id not in interfaces:
                    interfaces[instance_id] = []
                interface = self.profile.convert_interface_name(
                    match.group("interface"))
                if interface not in ports[instance_id]:
                    continue
                port_attrs = ports[instance_id][interface]
                interfaces[instance_id] += [{
                    "interface": interface,
                    "port_id": "%s.%s" % (match.group("priority"), match.group("port_id")),
                    "state": port_attrs["state"],
                    "role": port_attrs["role"],
                    "priority": match.group("priority"),
                    "designated_bridge_id": match.group("designated_bridge_id"),
                    "designated_bridge_priority": match.group(
                        "designated_bridge_priority"),
                    "designated_port_id": match.group("designated_port_id"),
                    "point_to_point": port_attrs["point_to_point"],
                    "edge": port_attrs["edge"],
                    }]
        for I in r["instances"]:
            I["interfaces"] = interfaces[I["id"]]
        return r

    def execute(self):
        v = self.cli("display stp brief")
        # if "Spanning tree enabled protocol ieee" in v:
        #    return self.process_pvst(v, proto="PVST+")
        # elif "Spanning tree enabled protocol rstp" in v:
        #    return self.process_pvst(v, proto="rapid-PVST+")
        # if "Spanning tree enabled protocol mstp" in v:
        # if "Mode MSTP" in v:
        return self.process_mstp(v)
        #elif "No spanning tree instance exists" in v \
        #or "No spanning tree instances exist" in v:
        #else:
        #    return {"mode": "None", "instances": []}

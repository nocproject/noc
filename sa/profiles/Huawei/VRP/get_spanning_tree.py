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


class Script(BaseScript):
    name = "Huawei.VRP.get_spanning_tree"
    interface = IGetSpanningTree

    def get_ports_attrs(self):
        """
        Get port attributes (Link type and edge status)
        :param cli_stp:
        :param instance_sep:
        :return: hash of instance_id -> port -> {link_type: , edge, role,
            status}
        """
        cli_stp = self.cli("display stp brief")
        ports = {}  # instance -> port -> attributes
        for R in cli_stp.splitlines()[1:]:
            if not R.strip():
                continue
            R = R.split()
            interface = self.profile.convert_interface_name(R[1])
            protection = R[-1]
            instance_id = int(R[0])
            if instance_id not in ports:
                ports[instance_id] = {}
            ports[instance_id][interface] = {
                "role": {
                    "dis": "disabled",
                    "alte": "alternate",
                    "back": "backup",
                    "root": "root",
                    "desi": "designated",
                    "mast": "master",
                    "????": "nonstp",
                    "_": "unknown"
                }[R[2].lower()],  # @todo: refine roles
                "state": {
                    "dis": "disabled",
                    "discarding": "discarding",
                    "bkn": "broken",
                    "learning": "learning",
                    "??": "learning",
                    "forwarding": "forwarding",
                    "listening": "listen",
                    "lbk": "loopback"
                }[R[3].lower()]  # @todo: refine states
            }
        return ports

    rx_stp_disabled = re.compile(
        "Protocol Status\s+:\s*Disabled", re.MULTILINE)

    rx_mstp_region = re.compile(
        r"Region name\s+:(?P<region>\S+).+Revision level\s+:(?P<revision>\d+)",
        re.DOTALL | re.MULTILINE | re.IGNORECASE)

    rx_mstp_instance = re.compile(r"^\s*(\d+)\s+(.+)?", re.MULTILINE)

    rx_mstp0_bridge = re.compile(
        r"CIST\sBridge\s+:(?P<bridge_priority>\d+)\.(?P<bridge_id>\S+).+?"
        r"CIST\sRoot/ERPC\s+:(?P<root_priority>\d+)\.(?P<root_id>\S+)\s",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

    rx_mstp_bridge = re.compile(
        r"MSTI\sBridge\sID\s+:(?P<bridge_priority>\d+)\.(?P<bridge_id>\S+).+?"
        r"MSTI\sRegRoot/[IE]RPC\s+:(?P<root_priority>\d+)\.(?P<root_id>\S+)\s",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

    rx_mstp0_interfaces = re.compile(
        r"^----\[Port(?P<port_id>\d+)\((?P<interface>\S+)\)\]\[(?P<state>\S+)\].+?"
        r"\s+Port\sProtocol\s+:(?P<status>\S+).+?"
        r"\s+Port\sRole\s+:(?P<role>\S+).+?"
        r"\s+Port\sPriority\s+:(?P<priority>\d+).+?"
        r"\s+Port\sCost\((?:Dot1T |Legacy)\)\s+:.+?Active=(?P<cost>\d+).+?"
        r"\s+(Desg\.|Designated)\sBridge/Port\s+:(?P<designated_bridge_priority>\d+)\."
        r"(?P<designated_bridge_id>\S+)\s/\s(?P<designated_port_id>\S+).+?"
        r"\s+Port\sEdged\s+:Config=(?P<edge_config>\S+)\s/\sActive=(?P<edge_status>\S+).+?"
        r"\s+Point-to-point\s+:Config=(?P<ptop_config>\S+)\s/\sActive=(?P<ptop_status>\S+)",
        re.MULTILINE | re.IGNORECASE)

    rx_mstp_interfaces = re.compile(
        r"----\[Port(?P<port_id>\d+)\((?P<interface>\S+)\)\]\[(?P<state>\S+)\].+?"
        r"\s+Port\sRole\s+:(?P<role>\S+).+?"
        r"\s+Port\sPriority\s+:(?P<priority>\d+).+?"
        r"\s+Port\sCost\(Dot1T \)\s+:.+?Active=(?P<cost>\d+).+?"
        r"\s+(Desg\.|Designated)\sBridge/Port\s+:(?P<designated_bridge_priority>\d+)\."
        r"(?P<designated_bridge_id>\S+)\s/\s(?P<designated_port_id>\S+).+?",
        re.MULTILINE | re.IGNORECASE)

    def process_mstp(self):
        check_d = re.compile("\s*\d+\s*")
        # Save port attributes
        ports = self.get_ports_attrs()
        #
        v = self.cli("display stp region-configuration")
        match = self.rx_mstp_region.search(v)
        r = {
            "mode": "MSTP",
            "instances": [],
            "configuration": {
                "MSTP": {
                    "region": match.group("region"),
                    "revision": int(match.group("revision")),
                    }
            }
        }
        iv = {}  # instance -> vlans
        instance_table = v.splitlines()[6:]

        vlans = ""
        for row in instance_table:
            s = row[0:13]
            if check_d.match(row[0:13]):
                instance = int(row[0:13].strip())
                vlans = row[14:]
                iv[int(instance)] = vlans
            else:
                iv[int(instance)] += row[14:]
        iv[int(instance)] = vlans
        for x in iv:
            iv[x] = iv[x].replace(" to ", "-")

        #
        interfaces = {}
        for instance_id in iv:
            for I in self.cli("display stp instance %s" % instance_id).split("-------\[")[0:]:
                # instance_id = int(instance_id)
                if instance_id == 0:
                    match = self.rx_mstp0_bridge.search(I)
                    v2 = self.rx_mstp0_interfaces.finditer(I)
                else:
                    match = self.rx_mstp_bridge.search(I)
                    v2 = self.rx_mstp_interfaces.finditer(I)
                r["instances"] += [{
                    "id": int(instance_id),
                    "vlans": iv[instance_id],
                    "root_id": match.group("root_id"),
                    "root_priority": match.group("root_priority"),
                    "bridge_id": match.group("bridge_id"),
                    "bridge_priority": match.group("bridge_priority"),
                    }]
                if instance_id not in interfaces:
                    interfaces[instance_id] = []
                for match in v2:
                    interface = self.profile.convert_interface_name(
                        match.group("interface"))
                    if interface not in ports[instance_id]:
                        continue
                    ptop = False
                    edge = False
                    if instance_id == 0:
                        ptop = match.group("ptop_status") == "true"
                        edge = match.group("edge_status") == "true"
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
                        "point_to_point": ptop,
                        "edge": edge
                        }]
        for st in r["instances"]:
            st["interfaces"] = interfaces[st["id"]]
        return r

    def execute(self):
        cli_stp = self.cli("display stp brief")
        if self.rx_stp_disabled.search(cli_stp):
            return {"mode": None, "instances": []}

        return self.process_mstp()

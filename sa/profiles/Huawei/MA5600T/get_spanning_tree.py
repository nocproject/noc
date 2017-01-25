# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.MA5600T.get_spanning_tree
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree


class Script(BaseScript):
    name = "Huawei.MA5600T.get_spanning_tree"
    interface = IGetSpanningTree

    rx_region = re.compile("region-name\s+(?P<region>\S+)")
    rx_vlans = re.compile(
        "^\s+instance\s+(?P<inst>\d+)\s+vlan\s+(?P<vlans>\d+.+)",
        re.MULTILINE)
    rx_inst_split = re.compile("^\s+=+ Instance\s+", re.MULTILINE)
    rx_inst_id = re.compile("^\s*(?P<id>\d+)", re.MULTILINE)
    rx_inst = re.compile(
        r"^\s+Bridge\s+Priority\s*:\s*(?P<bridge_priority>\d+)\s+"
        r"MAC Address\s*:\s*(?P<bridge_id>\S+)\s*\n", re.MULTILINE)
    rx_ist_root = re.compile(
        r"^\s+IST Root\s+Priority\s*:\s*(?P<root_priority>\d+)\s+"
        r"MAC Address\s*:\s*(?P<root_id>\S+)\s*\n", re.MULTILINE)
    rx_cst_root = re.compile(
        r"^\s+CST Root\s+Priority\s*:\s*(?P<root_priority>\d+)\s+"
        r"MAC Address\s*:\s*(?P<root_id>\S+)\s*\n", re.MULTILINE)
    rx_port = re.compile(
        r"^\s*\d+\s+(?P<port>\d+/\s*\d+/\s*\d+)\s+\d+", re.MULTILINE)
    rx_port_id_state = re.compile(
        r"\-+\[Port(?P<port_id>\d+)\((?P<state>\S+)\)\]\-+")
    rx_port_role_pri = re.compile(
        r"^\s*Port Role\s+:(?P<role>.+)\n"
        r"^\s*Port Priority\s+:(?P<priority>\d+)\n", re.MULTILINE)
    rx_designated = re.compile(
        r"^\s*Desg. Bridge/Port\s+:(?P<designated_bridge_priority>\d+)\."
        r"(?P<designated_bridge_id>\S+)\s+/\s+"
        r"(?P<designated_port_id>\S+)\s*\n", re.MULTILINE)
    rx_edge = re.compile(r"Port Edged\(Admin\)\s*:\s*(?P<edge>\S+)")
    rx_p2p = re.compile(
        r"Point-to-point\s*:\s*Config=\S+\s+/\s+ Active=(?P<p2p>\S+)")

    PORT_STATE = {
        "Discarding": "discarding",
        "Down": "disabled",
        "Forwarding": "forwarding"
    }
    PORT_ROLE = {
        "Alternate Port": "alternate",
        "Designated Port": "designated",
        "Disabled Port": "disabled",
        "Root Port": "root",
        "Master Port": "master"
    }

    def execute(self):
        r = {"mode": "None", "instances": []}
        try:
            c = self.cli("display current-configuration section config\r\n")
        except self.CLISyntaxError:
            return r
        if "stp enable" not in c:
            return r

        v = self.cli("display stp\r\n")
        if "IEEE Multiple Spanning Tree Protocol":
            r["mode"] = "MSTP"
            match = self.rx_region.search(c)
            if match:
                r["configuration"] = {
                    "MSTP": {
                        "region": match.group("region"),
                        "revision": 0
                    }
                }
            for inst in self.rx_inst_split.split(v):
                instance = {
                    "interfaces": []
                }
                match = self.rx_inst_id.search(inst)
                if not match:
                    continue
                instance["id"] = int(match.group("id"))
                match = self.rx_inst.search(inst)
                instance.update(match.groupdict())
                if instance["id"] == 0:
                    match = self.rx_ist_root.search(inst)
                    instance.update(match.groupdict())
                else:
                    match = self.rx_cst_root.search(inst)
                    if not match:
                        match = self.rx_ist_root.search(inst)
                    instance.update(match.groupdict())
                vlans = ""
                for i in c.split("\n"):
                    match = self.rx_vlans.search(c)
                    if match:
                        if int(match.group("inst")) == instance["id"]:
                            vlans = match.group("vlans").strip()
                            # 90   to   91
                            vlans = re.sub('\s+to\s+', '-', vlans)
                            # 90  100
                            vlans = re.sub('\s{2,}', ' ', vlans)
                            vlans = vlans.replace(" ", ",")
                            break
                if vlans == "":
                    vlans = "1-4095"
                instance["vlans"] = vlans
                for p in self.rx_port.finditer(inst):
                    ifname = p.group("port").replace(" ", "")
                    p1 = self.cli("display stp instance %d port %s" %
                                  (instance["id"], ifname))
                    iface = {"interface": ifname}
                    match = self.rx_port_id_state.search(p1)
                    iface["port_id"] = match.group("port_id")
                    iface["state"] = self.PORT_STATE[match.group("state")]
                    match = self.rx_port_role_pri.search(p1)
                    iface["role"] = self.PORT_ROLE[
                        match.group("role").replace("CIST ", "")]
                    iface["priority"] = match.group("priority")
                    match = self.rx_designated.search(p1)
                    iface.update(match.groupdict())
                    match = self.rx_edge.search(p1)
                    if match:
                        iface["edge"] = match.group("edge") != "disabled"
                    else:
                        iface["edge"] = False
                    match = self.rx_p2p.search(p1)
                    if match:
                        iface["point_to_point"] = match.group("p2p") == "true"
                    else:
                        iface["point_to_point"] = False
                    instance["interfaces"] += [iface]

                r["instances"] += [instance]

        return r

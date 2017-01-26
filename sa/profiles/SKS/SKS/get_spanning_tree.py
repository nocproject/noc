# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SKS.SKS.get_spanning_tree
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree
from noc.sa.interfaces.base import MACAddressParameter


class Script(BaseScript):
    name = "SKS.SKS.get_spanning_tree"
    interface = IGetSpanningTree

    rx_mode = re.compile(
        r"^\s*Spanning tree enabled mode (?P<mode>\S+)")
    rx_mstp = re.compile(
        r"^\s*Name: (?P<region>\S+)\s*\n"
        r"^\s*Revision: (?P<revision>\d+)", re.MULTILINE)
    rx_inst = re.compile(
        "MST (?P<id>\d+) Vlans Mapped: (?P<vlans>.+?)\n"
        "^\s*CST Root ID\s+ Priority\s+(?P<root_priority>\d+)\s*\n"
        "^\s*Address\s+(?P<root_id>\S+)\s*\n"
        "^\s*Path Cost\s+\d+\s*\n"
        "^\s*Root Port\s+\S+\s*\n"
        "^\s*.+\n"
        "(^\s*.+\n)?"
        "^\s*Bridge ID\s+Priority\s+(?P<bridge_priority>\d+)\s*\n"
        "^\s*Address\s+(?P<bridge_id>\S+)\s*\n", re.MULTILINE)
    rx_inst1 = re.compile(
        "^\s*Root ID\s+ Priority\s+(?P<root_priority>\d+)\s*\n"
        "^\s*Address\s+(?P<root_id>\S+)\s*\n"
        "^\s*Cost\s+\d+\s*\n"
        "^\s*Port\s+\S+\s*\n"
        "^\s*.+\n"
        "^\s*Bridge ID\s+ Priority\s+(?P<bridge_priority>\d+)\s*\n"
        "^\s*Address\s+(?P<bridge_id>\S+)\s*\n", re.MULTILINE)
    rx_inst2 = re.compile(
        "^\s*Root ID\s+ Priority\s+(?P<root_priority>\d+)\s*\n"
        "^\s*Address\s+(?P<root_id>\S+)\s*\n"
        "^\s*This switch is the root\s*\n", re.MULTILINE)
    rx_vlans = re.compile("^0\s+(?P<vlans>\S+)\s+enabled", re.MULTILINE)
    rx_port = re.compile(
        "^\s*Port (?P<interface>\S+) (?:enabled|disabled)\s*\n"
        "^\s*State: (?P<state>\S+)\s+Role: (?P<role>\S+)\s*\n"
        "^\s*Port id: (?P<port_id>\S+)\s+Port cost: (?P<priority>\d+)\s*\n"
        "^\s*.+\n"
        "^\s*Designated bridge Priority\s*: "
        "(?P<designated_bridge_priority>\S+)\s+Address: "
        "(?P<designated_bridge_id>\S+)\s*\n"
        "^\s*Designated port id: (?P<designated_port_id>\S+)\s+"
        "Designated path cost: \d+\s*\n",
        re.MULTILINE)

    def execute(self):
        try:
            v = self.cli("show spanning-tree detail")
        except self.CLISyntaxError:
            return {"mode": "None", "instances": []}
        match = self.rx_mode.search(v)
        mode = match.group("mode")
        stp = {"mode": mode, "instances": []}
        if mode == "MSTP":
            try:
                c = self.cli("show spanning-tree mst-configuration")
                match = self.rx_mstp.search(c)
                stp["configuration"] = {}
                stp["configuration"]["MSTP"] = match.groupdict()
            except self.CLISyntaxError:
                pass
            for instanses in v.split("######"):
                match = self.rx_inst.search(instanses)
                if match:
                    inst = match.groupdict()
                    inst["interfaces"] = []
                    for port in instanses.split("\n\n"):
                        match = self.rx_port.search(port)
                        if match:
                            iface = match.groupdict()
                            iface["point_to_point"] = "Type: P2P" in port
                            iface["priority"] = \
                                match.group("port_id").split(".")[0]
                            iface["edge"] = False
                            inst["interfaces"] += [iface]
                    stp["instances"] += [inst]
        else:
            match = self.rx_inst.search(v)
            if match:
                inst = match.groupdict()
            else:
                match = self.rx_inst1.search(v)
                if match:
                    inst = match.groupdict()
                    inst["id"] = 0
                    inst["interfaces"] = []
                    inst["vlans"] = "1-4095"
                else:
                    match = self.rx_inst2.search(v)
                    inst = match.groupdict()
                    inst["id"] = 0
                    inst["bridge_priority"] = inst["root_priority"]
                    inst["bridge_id"] = inst["root_id"]
                    inst["interfaces"] = []
                    try:
                        c = self.cli("show spanning-tree mst-configuration")
                        match = self.rx_vlans.search(c)
                        inst["vlans"] = match.group("vlans")
                    except:
                        inst["vlans"] = "1-4095"
            for port in v.split("\n\n"):
                match = self.rx_port.search(port)
                if match:
                    iface = match.groupdict()
                    iface["point_to_point"] = "Type: P2P" in port
                    iface["priority"] = \
                        match.group("port_id").split(".")[0]
                    iface["edge"] = False
                    inst["interfaces"] += [iface]
            stp["instances"] = [inst]
        return stp

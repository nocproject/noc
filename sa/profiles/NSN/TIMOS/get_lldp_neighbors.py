# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NSN.TIMOS.get_lldp_neighbors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "NSN.TIMOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_some = re.compile(r"^(?P<port>\w/\w/\w+)\s+")
    rx_local_lldp = re.compile(r"\s+?:\s(?P<local_interface_id>.+?)\s")
    rx_remote_info = re.compile(
        r"^Supported Caps\s+:\s(?P<remote_capabilities>.+?)\n"
        r"^Enabled Caps\s+:.*\n"
        r"^Chassis Id Subtype\s+:\s(?P<remote_chassis_id_subtype>\d)\s.*\n"
        r"^Chassis Id\s+:\s(?P<remote_chassis_id>\S+)\s*\n"
        r"^PortId Subtype\s+:\s(?P<remote_port_subtype>\d)\s.*\n"
        r"^Port\sId\s+:\s(?P<remote_port>(.+\n?){1,3}?)\n"  # Port Id : 70:6F:72:74:20:32:37\n"port 27"
        r"^Port\sDescription\s+:\s(?P<remote_port_description>.+\n?.+?)\n"
        r"^System\sName\s+:\s(?P<remote_system_name>\S+)\n",
        re.MULTILINE,
    )
    rx_port_descr = re.compile(
        r"(?P<remote_port_name>\S+),"
        r"\s*(?P<remote_port_type>.+),\n?"
        r"\s*\"(?P<remote_port_description>.+)"
    )
    rx_port_id = re.compile(r"^\s*(?P<remote_port>.+)\s+\"(?P<port_name>.+)\"", re.DOTALL)

    CAPS_MAP = {
        "other": 1,
        "repeater": 2,
        "bridge": 4,
        "wlanaccesspoint": 8,
        "router": 16,
        "telephone": 32,
        "docsis": 64,
        "station": 128,
        "cvlan": 0,
    }

    NOT_SPECIFIED = "(not specified)"

    @classmethod
    def fixcaps(cls, caps):
        caps = caps.lower().strip()
        fixedcaps = 0
        if caps == cls.NOT_SPECIFIED:
            return fixedcaps
        for c in caps.split():
            if c.startswith("(not"):
                continue
            fixedcaps |= cls.CAPS_MAP[c]
        return fixedcaps

    def get_port_info(self, port):
        try:
            v = self.cli("show port %s ethernet lldp remote-info" % port)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        else:
            match_obj = self.rx_remote_info.search(v)
            pri = match_obj.groupdict()
            pri["remote_capabilities"] = self.fixcaps(pri["remote_capabilities"])
            if "n/a" in pri["remote_system_name"]:
                del pri["remote_system_name"]
            # print("Match Port Description", self.rx_port_descr.match(pri["remote_port_description"]))
            if self.rx_port_descr.match(pri["remote_port_description"]):
                pri["remote_port_description"] = (
                    self.rx_port_descr.match(pri["remote_port_description"])
                    .group("remote_port_description")
                    .strip(' "')
                )
            elif "n/a" in pri["remote_port"]:
                del pri["remote_port_description"]
            if self.rx_port_id.match(pri["remote_port"]):
                pri["remote_port"] = self.rx_port_id.match(pri["remote_port"]).group("port_name")
            return pri

    def execute_cli(self):
        r = []
        try:
            v = self.cli("show system lldp neighbor")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for line in v.splitlines():
            match = self.rx_some.search(line)
            if not match:
                continue
            port = match.group("port")
            local_lldp = self.cli("show port %s ethernet detail | match IfIndex" % port)
            lldp_match = self.rx_local_lldp.search(local_lldp)
            if not lldp_match:
                continue
            local_interface_id = str(lldp_match.group("local_interface_id"))
            pri = self.get_port_info(port)
            r += [
                {
                    "local_interface": port,
                    "local_interface_id": local_interface_id,
                    "neighbors": [pri],
                }
            ]
        return r

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
        r"^Port\sId\s+:\s(?P<remote_port>.+?)\n"
        r"^Port\sDescription\s+:\s(?P<remote_port_description>.+?)\n"
        r"^System\sName\s+:\s(?P<remote_system_name>\S+)\n",
        re.MULTILINE )

    CAPS_MAP = {
        "other": 1,
        "repeater": 2,
        "bridge": 4,
        "wlanaccesspoint": 8,
        "router": 16,
        "telephone": 32,
        "docsis": 64,
        "station": 128,
        "cvlan": 0
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
            if 'n/a' in pri['remote_system_name']:
                del pri['remote_system_name']
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
            port = match.group('port')
            local_lldp = self.cli('show port %s ethernet detail | match IfIndex' % port)
            lldp_match = self.rx_local_lldp.search(local_lldp)
            if not lldp_match:
                continue
            local_interface_id = str(lldp_match.group('local_interface_id'))
            pri = self.get_port_info(port)
            r += [{
                "local_interface": port,
                "local_interface_id": local_interface_id,
                "neighbors": [pri]
            }]
        return r

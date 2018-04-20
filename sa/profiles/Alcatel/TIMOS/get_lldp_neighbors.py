# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Alcatel.TIMOS.get_lldp_neighbors
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
    name = "Alcatel.TIMOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_some = re.compile(r"^(?P<port>\w/\w/\w+)\s+")
    rx_local_lldp = re.compile(r"""\s+?:\s(?P<local_interface_id>.+?)\s""")
    rx_remote_info = re.compile(r"""
        Supported\sCaps\s+:\s(?P<remote_capabilities>.+?)\n
        .*?
        Chassis\sId\sSubtype\s+:\s(?P<remote_chassis_id_subtype>\d)\s
        .*?
        Chassis\sId\s+:\s(?P<remote_chassis_id>\S+)\n
        .*?
        PortId\sSubtype\s+:\s(?P<remote_port_subtype>.)\s
        .*?
        Port\sId\s+:\s(?P<remote_port>.+?)("|Port)
        .*?
        System\sName\s+:\s(?P<remote_system_name>\S+).+
        """, re.MULTILINE | re.DOTALL | re.VERBOSE)

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

    @staticmethod
    def fixport(port, port_type):
        # fix alcatel encode port like hex string
=======
##----------------------------------------------------------------------
## Alcatel.TIMOS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
__author__ = 'shirokih'
"""
"""

from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors
import re


class Script(NOCScript):
    name = "Alcatel.TIMOS.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]
    rx_some = re.compile(r"^(?P<port>\w/\w/\w+)\s+")

    def fixcaps(self, caps):
        fixedcaps = 0
        if caps.lower() == '(not specified)':
            return fixedcaps
        for c in caps.split():
            if c.lower() == '(not': 
                continue
            fixedcaps |= {
                "other": 1, "repeater": 2, "bridge": 4,
                "wlanaccesspoint": 8, "router": 16,
                "telephone": 32, "docsis": 64, "station": 128,
                "cvlan": 0
            }[c.lower()]
        return fixedcaps

    def fixport(self, port, port_type):
        #fix alcatel encode port like hex string
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        remote_port = "u"
        if port_type == '5' and "\n " in port:
            remote_port = port.replace("\n                        ", "")
            remote_port = remote_port.replace(":", "").replace("\n", "")
            remote_port = remote_port.decode("hex")
        elif port_type == '5' and "\n" in port:
            remote_port = port.replace("\n", "")
            remote_port = remote_port.replace(":", "").replace("\n", "")
            remote_port = remote_port.decode("hex")
        elif port_type == '5' and "\n " not in port:
            remote_port = remote_port.replace(":", "").replace("\n", "")
            remote_port = remote_port.decode("hex")
<<<<<<< HEAD
        elif port_type == '7':
            return port.replace("\n", "")
        return remote_port

    def get_port_info(self, port):
=======
        return remote_port

    def get_port_info(self, port):
        remote_info = re.compile(r"""
            Supported\sCaps\s+:\s(?P<remote_capabilities>.+?)\n
            .*?
            Chassis\sId\sSubtype\s+:\s(?P<remote_chassis_id_subtype>\d)\s
            .*?
            Chassis\sId\s+:\s(?P<remote_chassis_id>\S+)\n
            .*?
            PortId\sSubtype\s+:\s(?P<remote_port_subtype>.)\s
            .*?
            Port\sId\s+:\s(?P<remote_port>.+?)("|Port)
            .*?
            System\sName\s+:\s(?P<remote_system_name>\S+).+
            """, re.MULTILINE | re.DOTALL | re.VERBOSE)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        try:
            v = self.cli("show port %s ethernet lldp remote-info" % port)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        else:
<<<<<<< HEAD
            match_obj = self.rx_remote_info.search(v)
=======
            match_obj = re.search(remote_info, v)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            pri = match_obj.groupdict()
            pri["remote_capabilities"] = self.fixcaps(pri["remote_capabilities"])
            pri["remote_port"] = self.fixport(pri["remote_port"],
                                              pri["remote_port_subtype"])
<<<<<<< HEAD
            if 'n/a' in pri['remote_system_name']:
                del pri['remote_system_name']
            return pri

    def execute(self):
        r = []
=======
            return pri

    def execute(self):
        my_dict = []
        re_local_lldp =re.compile(r"""\s+?:\s(?P<local_interface_id>.+?)\s""")

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        try:
            v = self.cli("show system lldp neighbor")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for line in v.splitlines():
            match = self.rx_some.search(line)
<<<<<<< HEAD
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
=======

            if match:
                port = match.group('port')
                local_lldp = self.cli('show port %s ethernet detail | match IfIndex' % port)
                lldp_match = re.search(re_local_lldp, local_lldp)
                local_interface_id = str(lldp_match.group('local_interface_id'))
                pri = self.get_port_info(port)
                port_info = {
                    "local_interface": port,
                    "local_interface_id": local_interface_id,
                    "neighbors": [pri]
                }
                my_dict.append(port_info)
        return my_dict
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.TIMOS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors
import re



class Script(NOCScript):
    name = "Alcatel.TIMOS.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]
    rx_some = re.compile(r"^(?P<port>\w/\w/\w)\s+")

    def fixcaps(self, caps):
        fixedcaps = 0
        for c in caps.split():
            fixedcaps |= {
                "other": 1, "repeater": 2, "bridge": 4,
                "wlanaccesspoint": 8, "router": 16,
                "telephone": 32, "docsis": 64, "station": 128,
                "cVlan": 0, "(Not Specified)": 0
            }[c.lower()]
        return fixedcaps

    def fixport(self, port, port_type):
        """
        fix Alcatel encode port like hex string
        """
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
            Port\sId\s+:\s(?P<remote_port>.+?)Port
            .*?
            System\sName\s+:\s(?P<remote_system_name>\S+).+
            """, re.MULTILINE | re.DOTALL | re.VERBOSE)
        try:
            v = self.cli("show port %s ethernet lldp remote-info" % port)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        else:
            match_obj = re.search(remote_info, v)
            pri = match_obj.groupdict()
            pri["remote_capabilities"] = self.fixcaps(pri["remote_capabilities"])
            pri["remote_port"] = self.fixport(pri["remote_port"], pri["remote_port_subtype"])
        return pri

    def execute(self):
        my_dict = []
        re_local_lldp =re.compile(r"""\s+?:\s(?P<local_interface_id>.+?)\s""")

        try:
            v = self.cli("show system lldp neighbor")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for line in v.splitlines():
            match = self.rx_some.search(line)

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

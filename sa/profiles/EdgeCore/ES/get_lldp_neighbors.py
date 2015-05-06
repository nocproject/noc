# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
import binascii
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors, MACAddressParameter


class Script(NOCScript):
    name = "EdgeCore.ES.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    ##
    ## No lldp on 46xx
    ##
    @NOCScript.match(platform__contains="46")
    def execute_46(self):
        raise self.NotSupportedError()

    ##
    ## 35xx
    ##


    rx_localport = re.compile(r"^\s*Eth(| )(.+?)\s*(\|)MAC Address\s+(\S+).+?$", re.MULTILINE | re.DOTALL)
    rx_neigh = re.compile(r"(?P<local_if>Eth\s\S+)\s+(\||)\s+(?P<id>\S+).*?(?P<name>\S+)$", re.MULTILINE | re.IGNORECASE)
    rx_detail = re.compile(r".*Chassis I(d|D)\s+:\s(?P<id>\S+).*?Port(|\s+)ID Type\s+:\s(?P<p_type>[^\n]+).*?Port(|\s+)ID\s+:\s(?P<p_id>[^\n]+).*?Sys(|tem\s+)Name\s+:\s(?P<name>\S+).*?SystemCapSupported\s+:\s(?P<capability>[^\n]+).*", re.MULTILINE | re.IGNORECASE | re.DOTALL)

    @NOCScript.match()
    def execute_35(self):
        ifs = []
        r = []
        # EdgeCore ES3526 advertises MAC address(3) port sub-type, so local_interface_id parameter required
        # Collect data
        local_port_ids = {}  # name -> id
        for port, local_id in self.rx_localport.findall(self.cli("show lldp info local-device")):
            local_port_ids["Eth " + port] = MACAddressParameter().clean(local_id)
        v = self.cli("show lldp info remote-device")
        for match in self.rx_neigh.finditer(v):
            ifs += [{
                "local_interface": match.group("local_if"),
                "neighbors": [],
            }]
        for i in ifs:
            if i["local_interface"] in local_port_ids:
                i["local_interface_id"] = local_port_ids[i["local_interface"]]
            v = self.cli("show lldp info remote detail %s" % i["local_interface"])
            match = self.re_search(self.rx_detail, v)
            n = {"remote_chassis_id_subtype": 4}
            if match:
                n["remote_port_subtype"] = {"MAC Address": 3, "Interface name": 5, "Inerface alias": 5, "Local": 7}[match.group("p_type")]
                if n["remote_port_subtype"] == 3:
                    remote_port = MACAddressParameter().clean(match.group("p_id"))
                elif n["remote_port_subtype"] == 5:
                    remote_port = match.group("p_id").strip()
                else:
                    # Removing bug
                    remote_port = binascii.unhexlify('' . join(match.group("p_id").split('-')))
                    remote_port = remote_port.rstrip('\x00')
                n["remote_chassis_id"] = match.group("id")
                n["remote_system_name"] = match.group("name")
                n["remote_port"] = remote_port
                # Get capability
                cap = 0
                for c in match.group("capability").strip().split(", "):
                        cap |= {
                        "Other": 1, "Repeater": 2, "Bridge": 4,
                        "WLAN": 8, "Router": 16, "Telephone": 32,
                        "Cable": 64, "Station": 128
                        }[c]
                n["remote_capabilities"] = cap
            i["neighbors"] += [n]
            r += [i]
        return r

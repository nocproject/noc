# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# EdgeCore.ES.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
import binascii
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors, MACAddressParameter


class Script(BaseScript):
    name = "EdgeCore.ES.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    #
    # No lldp on 46xx
    #
    @BaseScript.match(platform__contains="46")
    def execute_46(self):
        raise self.NotSupportedError()

    #
    # 35xx
    #
    rx_localport = re.compile(
        r"^\s*Eth(| )(.+?)\s*(\|)MAC Address\s+(\S+).+?$",
        re.MULTILINE | re.DOTALL)
    rx_neigh = re.compile(
        r"(?P<local_if>Eth\s\S+)\s+(\||)\s+(?P<id>\S+).*?(?P<name>\S+)$",
        re.MULTILINE | re.IGNORECASE)
    rx_detail = re.compile(
        r".*Chassis I(d|D)\s+:\s(?P<id>\S+).*?Port(|\s+)ID Type\s+:\s"
        r"(?P<p_type>[^\n]+).*?Port(|\s+)ID\s+:\s(?P<p_id>[^\n]+).*?"
        r"Sys(|tem\s+)Name\s+:\s(?P<name>\S+).*?"
        r"(SystemCapSupported|System\sCapabilities)\s+:\s"
        r"(?P<capability>[^\n]+).*", re.MULTILINE | re.IGNORECASE | re.DOTALL)
    rx_port_descr = re.compile(
        r"^\s*Port Description\s+:\s+(?P<descr>.+)\n",
        re.MULTILINE
    )
    rx_system_descr = re.compile(
        r"^\s*System Description\s+:\s+(?P<descr>.+)\n",
        re.MULTILINE
    )

    @BaseScript.match()
    def execute_35(self):
        ifs = []
        r = []
        # EdgeCore ES3526 advertises MAC address(3) port sub-type,
        # so local_interface_id parameter required Collect data
        local_port_ids = {}  # name -> id
        for port, local_id in self.rx_localport.findall(
            self.cli("show lldp info local-device")
        ):
            local_port_ids["Eth " + port] = \
                MACAddressParameter().clean(local_id)
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        v = self.cli("show lldp info remote-device")
        for match in self.rx_neigh.finditer(v):
            ifs += [{
                "local_interface": match.group("local_if"),
                "neighbors": [],
            }]
        for i in ifs:
            if i["local_interface"] in local_port_ids:
                i["local_interface_id"] = local_port_ids[i["local_interface"]]
<<<<<<< HEAD
            v = self.cli(
                "show lldp info remote detail %s" %
                i["local_interface"]
            )
            match = self.re_search(self.rx_detail, v)
            n = {"remote_chassis_id_subtype": 4}
            if match:
                n["remote_port_subtype"] = {
                    "MAC Address": 3,
                    "Interface name": 5, "Interface Name": 5,
                    "Inerface Alias": 5, "Inerface alias": 5,
                    "Interface Alias": 5, "Interface alias": 5,
                    "Local": 7, "Locally Assigned": 7, "Locally assigned": 7
                }[match.group("p_type")]
                if n["remote_port_subtype"] == 3:
                    remote_port = \
                        MACAddressParameter().clean(match.group("p_id"))
=======
            v = self.cli("show lldp info remote detail %s" % i["local_interface"])
            match = self.re_search(self.rx_detail, v)
            n = {"remote_chassis_id_subtype": 4}
            if match:
                n["remote_port_subtype"] = {"MAC Address": 3, "Interface name": 5, "Inerface alias": 5, "Local": 7}[match.group("p_type")]
                if n["remote_port_subtype"] == 3:
                    remote_port = MACAddressParameter().clean(match.group("p_id"))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                elif n["remote_port_subtype"] == 5:
                    remote_port = match.group("p_id").strip()
                else:
                    # Removing bug
<<<<<<< HEAD
                    try:
                        remote_port = binascii.unhexlify(
                            '' . join(match.group("p_id").split('-'))
                        )
                    except TypeError:
                        remote_port = str(match.group("p_id"))
=======
                    remote_port = binascii.unhexlify('' . join(match.group("p_id").split('-')))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    remote_port = remote_port.rstrip('\x00')
                n["remote_chassis_id"] = match.group("id")
                n["remote_system_name"] = match.group("name")
                n["remote_port"] = remote_port
                # Get capability
                cap = 0
                for c in match.group("capability").strip().split(", "):
<<<<<<< HEAD
                    cap |= {
                        "Other": 1, "Repeater": 2, "Bridge": 4,
                        "WLAN": 8, "WLAN Access Point": 8, "Router": 16,
                        "Telephone": 32, "Cable": 64, "Station": 128
                    }[c]
                n["remote_capabilities"] = cap
                match = self.rx_system_descr.search(v)
                if match:
                    n["remote_system_description"] = match.group("descr")
                match = self.rx_port_descr.search(v)
                if match:
                    n["remote_port_description"] = match.group("descr")
=======
                        cap |= {
                        "Other": 1, "Repeater": 2, "Bridge": 4,
                        "WLAN": 8, "Router": 16, "Telephone": 32,
                        "Cable": 64, "Station": 128
                        }[c]
                n["remote_capabilities"] = cap
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            i["neighbors"] += [n]
            r += [i]
        return r

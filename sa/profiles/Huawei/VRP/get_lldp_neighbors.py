# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Huawei.VRP.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors, MACAddressParameter
from noc.lib.text import parse_kv


class Script(BaseScript):
    name = "Huawei.VRP.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
=======
##----------------------------------------------------------------------
## Huawei.VRP.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors, MACAddressParameter
from noc.lib.text import parse_kv


class Script(NOCScript):
    name = "Huawei.VRP.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    @NOCScript.match(version__startswith="3.")
    def execute_vrp3(self):
        """
        No LLDP on VRP3
        :return:
        """
        raise self.NotSupportedError()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_iface_sep = re.compile(
        r"^(\S+)\s+has\s+\d+\s+neighbors?", re.MULTILINE
    )
<<<<<<< HEAD
    rx_iface3_sep = re.compile(
        r"^LLDP neighbor-information of port \d+\[(?P<local_iface>\S+)\]:", re.MULTILINE
    )

    rx_neighbor_split = re.compile(
        r"^\s*Neighbor",
=======

    rx_neighbor_split = re.compile(
        r"^Neighbor",
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        re.MULTILINE
    )

    CHASSIS_TYPES = {
<<<<<<< HEAD
        "chassiscomponent": 1,
        "chassis component": 1,
        "portcomponent": 3,
        "port component": 3,
        "macaddress": 4,
        "mac address": 4,
        "networkaddress": 5,
        "network address": 5,
        "interfacename": 6,
        "interface name": 6,
=======
        "macaddress": 4,
        "interfacename": 6,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "local": 7
    }

    PORT_TYPES = {
        "interfacealias": 1,
<<<<<<< HEAD
        "interface alias": 1,
        "portcomponent": 2,
        "port component": 2,
        "macaddress": 3,
        "mac address": 3,
        "interfacename": 5,
        "interface name": 5,
        "local": 7,
        "locally assigned": 7
    }

    CAPS = {
        "na": 0, "other": 1, "repeater": 2, "bridge": 4,
        "wlan": 8, "wlanaccesspoint": 8, "access point": 8,
        "router": 16, "telephone": 32, "cable": 64, "docsiscabledevice": 64,
        "station": 128, "stationonly": 128
    }

    @BaseScript.match()
=======
        "macaddress": 3,
        "interfacename": 5,
        "local": 7
    }

    CAPS = {
        "NA": 0, "other": 1, "repeater": 2, "bridge": 4,
        "WLAN": 8, "router": 16, "telephone": 32,
        "cable": 64, "station": 128
    }

    @NOCScript.match()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute_other(self):
        """
        VRP5 style
        :return:
        """
        r = []
<<<<<<< HEAD
        if self.match_version(version__startswith=r"3."):
            try:
                v = self.cli("display lldp neighbor-information")
            except self.CLISyntaxError:
                raise self.NotSupportedError()
        else:
            try:
                v = self.cli("display lldp neighbor")
            except self.CLISyntaxError:
                raise self.NotSupportedError
        il = self.rx_iface_sep.split(v)[1:]
        if not il:
            il = self.rx_iface3_sep.split(v)[1:]
=======
        try:
            v = self.cli("display lldp neighbor")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        il = self.rx_iface_sep.split(v)[1:]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        for local_iface, data in zip(il[::2], il[1::2]):
            neighbors = []
            for ndata in self.rx_neighbor_split.split(data)[1:]:
                n = parse_kv({
                    "chassis type": "remote_chassis_id_subtype",
                    "chassisidsubtype": "remote_chassis_id_subtype",
                    "chassis id": "remote_chassis_id",
                    "chassisid": "remote_chassis_id",
                    "port id type": "remote_port_subtype",
                    "portidsubtype": "remote_port_subtype",
                    "port id": "remote_port",
                    "portid": "remote_port",
<<<<<<< HEAD
                    "port description": "remote_port_description",
                    "portdesc": "remote_port_description",
                    "system capabilities enabled": "remote_capabilities",
                    "syscapenabled": "remote_capabilities",
                    "system name": "remote_system_name",
                    "sysname": "remote_system_name",
                    "system description": "remote_system_description",
                    "sysdesc": "remote_system_description"
=======
                    "system capabilities enabled": "remote_capabilities",
                    "syscapenabled": "remote_capabilities",
                    "system name": "remote_system_name",
                    "sysname": "remote_system_name"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                }, ndata)
                # Convert chassis id
                n["remote_chassis_id_subtype"] = self.CHASSIS_TYPES[n["remote_chassis_id_subtype"].lower()]
                if n["remote_chassis_id_subtype"] == 3:
                    n["remote_chassis_id"] = MACAddressParameter().clean(n["remote_chassis_id"])
                # Convert port id
                n["remote_port_subtype"] = self.PORT_TYPES[n["remote_port_subtype"].lower()]
                if n["remote_port_subtype"] == 3:
                    n["remote_port"] = MACAddressParameter().clean(n["remote_port"])
<<<<<<< HEAD
                if n["remote_port_description"] in ["NA", "N/A"]:
                    del n["remote_port_description"]
                if n["remote_system_description"] in ["NA", "N/A"]:
                    del n["remote_system_description"]
                if n["remote_system_name"] in ["NA", "N/A"]:
                    del n["remote_system_name"]
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                # Process capabilities
                caps = 0
                cs = n.get("remote_capabilities", "").replace(",", " ")
                for c in cs.split():
<<<<<<< HEAD
                    caps |= self.CAPS[c.lower().strip()]
=======
                    caps |= self.CAPS[c.strip()]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                n["remote_capabilities"] = caps
                neighbors += [n]
            if neighbors:
                r += [{
                    "local_interface": local_iface,
                    "neighbors": neighbors
                }]
        return r

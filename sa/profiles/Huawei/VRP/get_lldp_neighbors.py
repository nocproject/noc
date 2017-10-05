# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_lldp_neighbors
#
# commands for the device open mib tree
#
# snmp-agent mib-view included ALL iso
# snmp-agent community read xxx mib-view ALL 
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
#import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4
#from noc.lib.text import parse_kv

class Script(BaseScript):
    name = "Huawei.VRP.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
    """ #comment for cli
    rx_iface_sep = re.compile(
        r"^(\S+)\s+has\s+\d+\s+neighbors?", re.MULTILINE
    )
    rx_iface3_sep = re.compile(
        r"^LLDP neighbor-information of port \d+\[(?P<local_iface>\S+)\]:", re.MULTILINE
    )

    rx_neighbor_split = re.compile(
        r"^\s*Neighbor",
        re.MULTILINE
    )

    CHASSIS_TYPES = {
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
        "local": 7
    }

    PORT_TYPES = {
        "interfacealias": 1,
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
    """

    def execute(self):
        r = []
        # Try SNMP first
        if self.has_snmp():
            try:
                local_int={}
                for vv in self.snmp.get_tables(
                    ["1.0.8802.1.1.2.1.3.7.1.2","1.0.8802.1.1.2.1.3.7.1.3"
                    ], bulk=True):
                    local_int[vv[0]]=vv[2]
                for v in self.snmp.get_tables(
                    [#"1.0.8802.1.1.2.1.4.1.1.2",
                     "1.0.8802.1.1.2.1.4.1.1.4", "1.0.8802.1.1.2.1.4.1.1.5",
                     "1.0.8802.1.1.2.1.4.1.1.6", "1.0.8802.1.1.2.1.4.1.1.7",
                     "1.0.8802.1.1.2.1.4.1.1.9", "1.0.8802.1.1.2.1.4.1.1.12"
                     ], bulk=True):
                    interf=v[0].split('.')
                    local_interface = local_int[interf[1]]
                    remote_chassis_id_subtype = v[1]
                    remotechassisid = ":".join(["%02x" % ord(c) for c in v[2]])
                    remote_port_subtype = v[3]
                    if remote_port_subtype == '3':
                        remote_port = ":".join(["%02x" % ord(c) for c in v[4]])
                    else:
                        remote_port = v[4]
                    if remote_port_subtype == '7':
                        remote_port_subtype = '5'

                    remote_system_name = v[5]

                    for c in v[6]:
                           bits = bin(ord(c))[2:]
                           bits = '00000000'[len(bits):] + bits

                    bb=bits[::-1]

                    cap = 0

                    for b in bb:
                         cap = cap * 2 + int(b)
                    remote_capabilities = cap

                    i = {"local_interface": local_interface, "neighbors": []}
                    n = {
                        "remote_chassis_id_subtype": remote_chassis_id_subtype,
                        "remote_chassis_id": remotechassisid,
                        "remote_port_subtype": remote_port_subtype,
                        "remote_port": remote_port,
                        "remote_capabilities": remote_capabilities,
                        }
                    if remote_system_name:
                        n["remote_system_name"] = remote_system_name
                    i["neighbors"].append(n)
                    r.append(i)
                return r

            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        raise Exception("Not implemented")
        """
        VRP5 style
        :return:
        """
        """#comment for cli
        r = []
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
                    "port description": "remote_port_description",
                    "portdesc": "remote_port_description",
                    "system capabilities enabled": "remote_capabilities",
                    "syscapenabled": "remote_capabilities",
                    "system name": "remote_system_name",
                    "sysname": "remote_system_name",
                    "system description": "remote_system_description",
                    "sysdesc": "remote_system_description"
                }, ndata)
                # Convert chassis id
                n["remote_chassis_id_subtype"] = self.CHASSIS_TYPES[n["remote_chassis_id_subtype"].lower()]
                if n["remote_chassis_id_subtype"] == 3:
                    n["remote_chassis_id"] = MACAddressParameter().clean(n["remote_chassis_id"])
                # Convert port id
                n["remote_port_subtype"] = self.PORT_TYPES[n["remote_port_subtype"].lower()]
                if n["remote_port_subtype"] == 3:
                    n["remote_port"] = MACAddressParameter().clean(n["remote_port"])
                # Process capabilities
                caps = 0
                cs = n.get("remote_capabilities", "").replace(",", " ")
                for c in cs.split():
                    caps |= self.CAPS[c.lower().strip()]
                n["remote_capabilities"] = caps
                neighbors += [n]
            if neighbors:
                r += [{
                    "local_interface": local_iface,
                    "neighbors": neighbors
                }]
        return r
        """

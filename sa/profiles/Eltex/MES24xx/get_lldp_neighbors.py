# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES24xx.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# Third-party modules
import six

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.mib import mib
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CAP_OTHER,
    LLDP_CAP_REPEATER,
    LLDP_CAP_BRIDGE,
    LLDP_CAP_WLAN_ACCESS_POINT,
    LLDP_CAP_ROUTER,
    LLDP_CAP_TELEPHONE,
    LLDP_CAP_DOCSIS_CABLE_DEVICE,
    LLDP_CAP_STATION_ONLY,
    lldp_caps_to_bits,
)


class Script(BaseScript):
    name = "Eltex.MES24xx.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_detail = re.compile(
        r"^Chassis Id SubType\s+: (?P<chassis_id_subtype>.+?)\n"
        r"^Chassis Id\s+: (?P<chassis_id>.+?)\n"
        r"^Port Id SubType\s+: (?P<port_id_subtype>.+?)\n"
        r"^Port Id\s+: (?P<port_id>.+?)\n"
        r"^Port Description\s+: (?P<port_description>.*?)\n"
        r"^System Name\s+: (?P<system_name>.*?)\n"
        r"^System Desc\s+: (?P<system_description>.*?)\n"
        r"^Local Intf\s+: (?P<local_port>.*?)\n"
        r"^Time Remaining.*?\n"
        r"^System Capabilities Supported\s+:.*?\n"
        r"^System Capabilities Enabled\s+:(?P<caps>.*?)\n",
        re.MULTILINE | re.DOTALL,
    )

    CHASSIS_SUBTYPE = {"Mac Address": LLDP_CHASSIS_SUBTYPE_MAC, "Local": LLDP_CHASSIS_SUBTYPE_LOCAL}
    PORT_SUBTYPE = {
        "Mac Address": LLDP_PORT_SUBTYPE_MAC,
        "Interface Name": LLDP_PORT_SUBTYPE_NAME,
        "Local": LLDP_PORT_SUBTYPE_LOCAL,
    }

    def get_local_iface(self):
        r = {}
        names = {x: y for y, x in six.iteritems(self.scripts.get_ifindexes())}
        # Get LocalPort Table
        for port_num, port_subtype, port_id, port_descr in self.snmp.get_tables(
            [
                mib["LLDP-MIB::lldpLocPortIdSubtype"],
                mib["LLDP-MIB::lldpLocPortId"],
                mib["LLDP-MIB::lldpLocPortDesc"],
            ]
        ):
            if port_subtype == 1:
                # Iface alias
                iface_name = port_id  # BUG. Look in PortID instead PortDesc
            elif port_subtype == 3:
                # Iface MAC address
                raise NotImplementedError()
            elif port_subtype == 7 and port_id.isdigit():
                # Iface local (ifindex)
                iface_name = names[int(port_id)]
            else:
                # Iface local
                iface_name = port_id
            r[port_num] = {"local_interface": iface_name, "local_interface_subtype": port_subtype}
        if not r:
            self.logger.warning(
                "Not getting local LLDP port mappings. Check 1.0.8802.1.1.2.1.3.7 table"
            )
            raise NotImplementedError()
        return r

    def execute_cli(self):
        r = []
        c = self.cli("show lldp neighbors detail")
        for match in self.rx_detail.finditer(c):
            iface = {"local_interface": match.group("local_port").strip(), "neighbors": []}
            cap = lldp_caps_to_bits(
                match.group("caps").strip().split(","),
                {
                    "O": LLDP_CAP_OTHER,
                    "r": LLDP_CAP_REPEATER,
                    "B": LLDP_CAP_BRIDGE,
                    "W": LLDP_CAP_WLAN_ACCESS_POINT,
                    "R": LLDP_CAP_ROUTER,
                    "T": LLDP_CAP_TELEPHONE,
                    "D": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                    "S": LLDP_CAP_STATION_ONLY,
                },
            )
            n = {
                "remote_chassis_id": match.group("chassis_id").strip(),
                "remote_chassis_id_subtype": self.CHASSIS_SUBTYPE[
                    match.group("chassis_id_subtype").strip()
                ],
                "remote_port": match.group("port_id").strip(),
                "remote_port_subtype": self.PORT_SUBTYPE[match.group("port_id_subtype").strip()],
                "remote_capabilities": cap,
            }
            if match.group("system_name").strip():
                n["remote_system_name"] = match.group("system_name").strip()
            if match.group("system_description").strip():
                n["remote_system_description"] = match.group("system_description").strip()
            if match.group("port_description").strip():
                n["remote_port_description"] = match.group("port_description").strip()
            iface["neighbors"] += [n]
            r += [iface]
        return r

# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS_Smart.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from builtins import zip
import re
import six

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.mac import MAC
from noc.core.lldp import LLDP_CHASSIS_SUBTYPE_MAC, LLDP_PORT_SUBTYPE_MAC


class Script(BaseScript):
    name = "DLink.DxS_Smart.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_port = re.compile(
        r"^Port ID : (?P<port>\S+)\s*\n"
        r"^-+\s*\n"
        r"^Remote Entities Count : [1-9]+\s*\n"
        r"(?P<entities>.+?): \d+\s*\n\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_entity = re.compile(
        r"^Entity \d+\s*\n"
        r"^\s+Chassis ID Subtype\s+:(?P<chassis_id_subtype>.+)\s*\n"
        r"^\s+Chassis ID\s+:(?P<chassis_id>.+)\s*\n"
        r"^\s+Port ID Subtype\s+:(?P<port_id_subtype>.+)\s*\n"
        r"^\s+Port ID\s+:(?P<port_id>.+)\s*\n"
        r"^\s*Port Description\s+:(?P<port_description>.*)"
        r"^\s+System Name\s+:(?P<system_name>.*)"
        r"^\s+System Description\s+:(?P<system_description>.*)"
        r"^\s+System Capabilities\s+:(?P<system_capabilities>.+?)\s*\n"
        r"^\s+Management Address Count",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    def execute_snmp(self):
        neighb = (
            "remote_chassis_id_subtype",
            "remote_chassis_id",
            "remote_port_subtype",
            "remote_port",
            "remote_port_description",
            "remote_system_name",
            "remote_system_description",
            "remote_capabilities",
        )
        r = []
        local_ports = {}
        # Get LocalPort Table
        for v in self.snmp.get_tables(
            [
                "1.0.8802.1.1.2.1.3.7.1.2",  # LLDP-MIB::lldpLocPortIdSubtype
                "1.0.8802.1.1.2.1.3.7.1.4",  # LLDP-MIB::lldpLocPortDesc
            ]
        ):
            local_ports[v[0]] = {
                "local_interface": self.profile.convert_interface_name(v[2]),
                "local_interface_subtype": v[1],
            }
        for v in self.snmp.get_tables(
            [
                "1.0.8802.1.1.2.1.4.1.1.4",  # LLDP-MIB::lldpRemChassisIdSubtype
                "1.0.8802.1.1.2.1.4.1.1.5",  # LLDP-MIB::lldpRemChassisId
                "1.0.8802.1.1.2.1.4.1.1.6",  # LLDP-MIB::lldpRemPortIdSubtype
                "1.0.8802.1.1.2.1.4.1.1.7",  # LLDP-MIB::lldpRemPortId
                "1.0.8802.1.1.2.1.4.1.1.8",  # LLDP-MIB::lldpRemPortDesc
                "1.0.8802.1.1.2.1.4.1.1.9",  # LLDP-MIB::lldpRemSysName
                "1.0.8802.1.1.2.1.4.1.1.10",  # LLDP-MIB::lldpRemSysDesc
                "1.0.8802.1.1.2.1.4.1.1.12",  # LLDP-MIB::lldpRemSysCapEnabled
            ]
        ):
            neigh = dict(list(zip(neighb, v[1:])))
            if neigh["remote_chassis_id_subtype"] == LLDP_CHASSIS_SUBTYPE_MAC:
                neigh["remote_chassis_id"] = MAC(neigh["remote_chassis_id"])
            if neigh["remote_port_subtype"] == LLDP_PORT_SUBTYPE_MAC:
                neigh["remote_port"] = MAC(neigh["remote_port"])
            for i in neigh:
                if isinstance(neigh[i], six.string_types):
                    neigh[i] = neigh[i].rstrip("\x00")
            if neigh["remote_capabilities"]:
                neigh["remote_capabilities"] = int(
                    "".join(
                        x
                        for x in reversed(
                            "{0:016b}".format(ord(neigh["remote_capabilities"]) << 8 + 0x0)
                        )
                    ),
                    2,
                )
            else:
                neigh["remote_capabilities"] = 0
            r += [
                {
                    "local_interface": local_ports[v[0].split(".")[1]]["local_interface"],
                    "neighbors": [neigh],
                }
            ]
        return r

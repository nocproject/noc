# ---------------------------------------------------------------------
# NAG.SNR.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import IntParameter, MACAddressParameter, InterfaceTypeError
from noc.core.validators import is_ipv4, is_ipv6, is_mac
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
)


class Script(BaseScript):
    name = "NAG.SNR.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_detail = re.compile(
        r"^Port name : (?P<local_if>\S+)\s*\n"
        r"^Port Remote Counter : (?P<status>\S+)\s*\n"
        r"^TimeMark :\S*\n"
        r"^ChassisIdSubtype :(?P<rem_cid_type>.*)\n"
        r"^ChassisId :(?P<id>.*)\n"
        r"^PortIdSubtype :(?P<p_type>.*)\n"
        r"^PortId :(?P<port_id>.*)",
        re.MULTILINE,
    )
    rx_port = re.compile(
        r"^\s*Interface Ethernet (?P<local_if>\S+)\n"
        r"^\s*Port LLDP:.+\n"
        r"^\s*Total neighbor count: 1\n"
        r"^\s*\n"
        r"^\s*Neighbor \(1\):\n"
        r"^\s*TTL: \d+\(s\)\n"
        r"^\s*Chassis ID: (?P<chassis_id>.+)\n"
        r"^\s*Port ID: (?P<port_id>.+)\n"
        r"^\s*System Name: (?P<sys_name>.*)\n"
        r"^\s*System Description: (?P<sys_descr>.*)\n"
        r"^\s*Port Description: (?P<port_descr>.*)\n",
        re.MULTILINE,
    )

    def get_lldp_foxgatecli(self):
        """
        For FoxGate Like CLI syntax
        :return:
        """
        r = []
        cmd = self.cli("show lldp interface", cached=True)
        for match in self.rx_port.finditer(cmd):
            local_if = match.group("local_if")
            chassis_id = match.group("chassis_id")
            if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(chassis_id):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
            else:
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_LOCAL
            port_id = match.group("port_id")
            if is_ipv4(port_id) or is_ipv6(port_id):
                port_id_subtype = LLDP_PORT_SUBTYPE_NETWORK_ADDRESS
            elif is_mac(port_id):
                port_id_subtype = LLDP_PORT_SUBTYPE_MAC
            else:
                port_id_subtype = LLDP_PORT_SUBTYPE_LOCAL
            neighbor = {
                "remote_chassis_id": chassis_id,
                "remote_chassis_id_subtype": chassis_id_subtype,
                "remote_port": port_id,
                "remote_port_subtype": port_id_subtype,
                "remote_capabilities": 0,
            }
            if match.group("sys_name"):
                neighbor["remote_system_name"] = match.group("sys_name").strip()
            if match.group("sys_descr"):
                neighbor["remote_system_description"] = match.group("sys_descr").strip()
            if match.group("port_descr"):
                neighbor["remote_port_description"] = match.group("port_descr").strip()
            r += [{"local_interface": f"e{local_if}", "neighbors": [neighbor]}]
        return r

    def execute_cli(self, **kwargs):
        r = []
        if self.is_foxgate_cli:
            return self.get_lldp_foxgatecli()
        # Fallback to CLI
        for lldp in self.cli("show lldp neighbors interface").split("\n\n"):
            match = self.rx_detail.search(lldp)
            if match:
                i = {"local_interface": match.group("local_if"), "neighbors": []}
                n = {"remote_chassis_id_subtype": match.group("rem_cid_type")}
                n["remote_port_subtype"] = {
                    "Interface alias": LLDP_PORT_SUBTYPE_ALIAS,
                    # "Port component": 2,
                    "MAC address": LLDP_PORT_SUBTYPE_MAC,
                    "Interface": LLDP_PORT_SUBTYPE_NAME,
                    "Local": LLDP_PORT_SUBTYPE_LOCAL,
                }[match.group("p_type")]
                if n["remote_port_subtype"] == LLDP_PORT_SUBTYPE_MAC:
                    remote_port = MACAddressParameter().clean(match.group("port_id"))
                elif n["remote_port_subtype"] == LLDP_PORT_SUBTYPE_LOCAL:
                    p_id = match.group("port_id")
                    try:
                        remote_port = IntParameter().clean(p_id)
                    except InterfaceTypeError:
                        remote_port = p_id
                else:
                    remote_port = match.group("port_id")
                n["remote_chassis_id"] = match.group("id")
                n["remote_port"] = str(remote_port)
                # Get capability
                cap = 0
                n["remote_capabilities"] = cap
                i["neighbors"] += [n]
                r += [i]

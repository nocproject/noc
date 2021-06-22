# ---------------------------------------------------------------------
# Orion.NOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_COMPONENT,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CAP_OTHER,
    LLDP_CAP_REPEATER,
    LLDP_CAP_BRIDGE,
    LLDP_CAP_ROUTER,
    LLDP_CAP_TELEPHONE,
    LLDP_CAP_STATION_ONLY,
    lldp_caps_to_bits,
)


class Script(BaseScript):
    name = "Orion.NOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    """
    Notes:

    On Alpha-A10E ver.4.15.1205 `show lldp remote detail` do not display
    ChassisId field
    """
    rx_lldp = re.compile(r"^port(?P<port>\d+)\s+(?P<chassis_id>\S+)", re.MULTILINE)
    rx_int = re.compile(
        r"^P(ort\s+port)?(?P<interface>\d+)\s+has\s+1\s+remotes:\s*\n"
        r"(^\s*\n)?"
        r"^Remote\s*1\s*\n"
        r"^-+\s*\n"
        r"^ChassisIdSubtype\s*:\s+(?P<chassis_subtype>\S+)\s*\n"
        r"(^ChassisId\s*:\s+(?P<chassis_id>\S+)\s*\n)?"  # See Notes
        r"^PortIdSubtype\s*:\s+(?P<port_subtype>\S+)\s*\n"
        r"^PortId\s*:\s+(?P<port_id>.+)\n"
        r"^PortDesc\s*:\s+(?P<port_descr>.+)\n"
        r"^SysName\s*:\s+(?P<sys_name>.*)\n"
        r"^SysDesc\s*:\s+(?P<sys_descr>(.+\n)+)"
        r"^SysCapSupported\s*:.*\n"
        r"^SysCapEnabled\s*:\s+(?P<caps>.+)\s*\n",
        re.MULTILINE,
    )
    rx_int_a26 = re.compile(
        r"^Port name\s*:\s*(?P<interface>\S+)\s*\n"
        r"^Port Remote Counter\s*:\s*1\s*\n"
        r"^TimeMark\s*:\s*\d+\s*\n"
        r"^ChassisIdSubtype\s*:\s*(?P<chassis_subtype>\d+)\s*\n"
        r"^ChassisId\s*:\s*(?P<chassis_id>\S+)\s*\n"
        r"^PortIdSubtype\s*:\s*(?P<port_subtype>\S+)\s*\n"
        r"^PortId\s*:\s*(?P<port_id>.+)\n"
        r"^PortDesc\s*:\s*(?P<port_descr>.+)\n"
        r"^SysName\s*:\s*(?P<sys_name>.*)\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        result = []
        if self.is_a26:
            v = self.cli("show lldp neighbors interface")
            for match in self.rx_int_a26.finditer(v):
                neighbor = {
                    "remote_chassis_id_subtype": match.group("chassis_subtype"),
                    "remote_chassis_id": match.group("chassis_id"),
                    "remote_port_subtype": {
                        # Need more examples
                        "Interface": LLDP_PORT_SUBTYPE_NAME,
                    }[match.group("port_subtype")],
                    "remote_port": match.group("port_id"),
                }
                if match.group("port_descr").strip():
                    p = match.group("port_descr").strip()
                    neighbor["remote_port_description"] = p
                if match.group("sys_name").strip():
                    p = match.group("sys_name").strip()
                    neighbor["remote_system_name"] = p
                result += [{"local_interface": match.group("interface"), "neighbors": [neighbor]}]
            return result

        chassis = {}
        v = self.cli("show lldp remote")
        for match in self.rx_lldp.finditer(v):
            chassis[match.group("port")] = match.group("chassis_id")
        v = self.cli("show lldp remote detail")
        for match in self.rx_int.finditer(v):
            neighbor = {
                "remote_chassis_id_subtype": {
                    "macAddress": LLDP_CHASSIS_SUBTYPE_MAC,
                    "networkAddress": LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
                    "ifName": LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
                }[match.group("chassis_subtype")],
                # "remote_chassis_id": match.group("chassis_id"),
                "remote_port_subtype": {
                    "ifAlias": LLDP_PORT_SUBTYPE_ALIAS,
                    "macAddress": LLDP_PORT_SUBTYPE_MAC,
                    "ifName": LLDP_PORT_SUBTYPE_NAME,
                    "portComponent": LLDP_PORT_SUBTYPE_COMPONENT,
                    "local": LLDP_PORT_SUBTYPE_LOCAL,
                }[match.group("port_subtype")],
                "remote_port": match.group("port_id"),
            }
            if match.group("chassis_id"):
                neighbor["remote_chassis_id"] = match.group("chassis_id")
            else:
                neighbor["remote_chassis_id"] = chassis[match.group("interface")]
            if match.group("port_descr").strip():
                p = match.group("port_descr").strip()
                if p != "N/A":
                    neighbor["remote_port_description"] = re.sub(r"\n\s{30}", "", p)
            if match.group("sys_name").strip():
                p = match.group("sys_name").strip()
                if p != "N/A":
                    neighbor["remote_system_name"] = re.sub(r"\n\s{30}", "", p)
            if match.group("sys_descr").strip():
                p = match.group("sys_descr").strip()
                if p != "N/A":
                    neighbor["remote_system_description"] = re.sub(r"\n\s{30}", "", p)
            caps = lldp_caps_to_bits(
                match.group("caps").strip().split(","),
                {
                    "other": LLDP_CAP_OTHER,
                    "repeater/hub": LLDP_CAP_REPEATER,
                    "bridge/switch": LLDP_CAP_BRIDGE,
                    "router": LLDP_CAP_ROUTER,
                    "telephone": LLDP_CAP_TELEPHONE,
                    "station": LLDP_CAP_STATION_ONLY,
                },
            )
            neighbor["remote_capabilities"] = caps
            result += [{"local_interface": match.group("interface"), "neighbors": [neighbor]}]
        return result

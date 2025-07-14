# ---------------------------------------------------------------------
# DLink.DxS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modiles
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.sa.interfaces.base import IPv4Parameter
from noc.core.mac import MAC
from noc.core.comp import smart_text
from noc.core.snmp.render import render_utf8
from noc.core.snmp.render import render_bin
from noc.core.snmp.render import render_mac
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_CHASSIS_COMPONENT,
    LLDP_CHASSIS_SUBTYPE_INTERFACE_ALIAS,
    LLDP_CHASSIS_SUBTYPE_PORT_COMPONENT,
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_COMPONENT,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_AGENT_CIRCUIT_ID,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CAP_OTHER,
    LLDP_CAP_REPEATER,
    LLDP_CAP_BRIDGE,
    LLDP_CAP_WLAN_ACCESS_POINT,
    LLDP_CAP_ROUTER,
    LLDP_CAP_TELEPHONE,
    LLDP_CAP_DOCSIS_CABLE_DEVICE,
    LLDP_CAP_STATION_ONLY,
)


class Script(BaseScript):
    name = "DLink.DxS.get_lldp_neighbors"
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

    rx_ifname_valid = re.compile(r"^\d+((/\d+)|(\:\d+))?$")

    def is_valid_ifname(self, name):
        m = self.rx_ifname_valid.search(name)
        return m is not None

    def get_local_iface(self):
        r = {}
        # Get LocalPort Table
        for port_num, port_subtype, port_id, port_desc in self.snmp.get_tables(
            [
                "1.0.8802.1.1.2.1.3.7.1.2",  # LLDP-MIB::lldpLocPortIdSubtype
                "1.0.8802.1.1.2.1.3.7.1.3",  # LLDP-MIB::lldpLocPortId
                "1.0.8802.1.1.2.1.3.7.1.4",  # LLDP-MIB::lldpLocPortDesc
            ],
            display_hints={"1.0.8802.1.1.2.1.3.7.1.3": render_bin},
        ):
            if port_subtype == LLDP_PORT_SUBTYPE_MAC:
                port_id = render_mac("", port_id)
            else:
                port_id = render_utf8("", port_id)

            local_interface = ""
            ifname_desc = self.profile.convert_interface_name(port_desc)

            # Old behavior
            if self.is_valid_ifname(ifname_desc):
                local_interface = ifname_desc
            elif port_subtype == LLDP_PORT_SUBTYPE_LOCAL:
                # DGS-3120-24SC   - 1/24
                # DGS-3000-28SC   - 1/24
                # DGS1210-12TS/ME - 12
                local_interface = port_id
            elif port_subtype == LLDP_PORT_SUBTYPE_NAME:
                local_interface = port_id
            elif port_subtype == LLDP_PORT_SUBTYPE_MAC:
                # Some old switches or switches with old firmware
                self.logger.debug(
                    "Cannot match local interface by MAC. Use '%s' as local ifname",
                    port_num,
                )
                local_interface = port_num
            else:
                self.logger.debug(
                    "Unknown PortIdSubtype '%s'. Set ifname to PortId '%s'", port_subtype, port_id
                )
                local_interface = port_id

            r[port_num] = {
                "local_interface": local_interface,
                "local_interface_subtype": port_subtype,
            }

        return r

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
        local_ports = self.get_local_iface()

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
            ],
            max_repetitions=15,
            display_hints={
                "1.0.8802.1.1.2.1.4.1.1.7": render_bin,
                "1.0.8802.1.1.2.1.4.1.1.5": render_bin,
            },
        ):
            neigh = dict(zip(neighb, v[1:]))
            if neigh["remote_chassis_id_subtype"] == LLDP_CHASSIS_SUBTYPE_MAC:
                neigh["remote_chassis_id"] = MAC(neigh["remote_chassis_id"])
            if neigh["remote_port_subtype"] == LLDP_PORT_SUBTYPE_MAC:
                neigh["remote_port"] = MAC(neigh["remote_port"])
            else:
                neigh["remote_port"] = smart_text(neigh["remote_port"]).rstrip("\x00")
            for i in neigh:
                if isinstance(neigh[i], str):
                    neigh[i] = neigh[i].rstrip(smart_text("\x00"))
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

    def execute_cli(self):
        r = []
        try:
            v = self.cli("show lldp remote_ports mode normal")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_port.finditer(v):
            i = {"local_interface": match.group("port"), "neighbors": []}
            for m in self.rx_entity.finditer(match.group("entities")):
                n = {}
                remote_chassis_id_subtype = m.group("chassis_id_subtype").replace("_", " ")
                n["remote_chassis_id_subtype"] = {
                    "chassis component": LLDP_CHASSIS_SUBTYPE_CHASSIS_COMPONENT,
                    "interface alias": LLDP_CHASSIS_SUBTYPE_INTERFACE_ALIAS,
                    "port component": LLDP_CHASSIS_SUBTYPE_PORT_COMPONENT,
                    "mac address": LLDP_CHASSIS_SUBTYPE_MAC,
                    "macaddress": LLDP_CHASSIS_SUBTYPE_MAC,
                    "network address": LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
                    "interface name": LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
                    "local": LLDP_CHASSIS_SUBTYPE_LOCAL,
                }[remote_chassis_id_subtype.strip().lower()]
                n["remote_chassis_id"] = m.group("chassis_id").strip()
                remote_port_subtype = m.group("port_id_subtype").replace("_", " ")
                n["remote_port_subtype"] = {
                    "interface alias": LLDP_PORT_SUBTYPE_ALIAS,
                    # DES-3526 6.00 B48, DES-3526 6.00 B49,
                    # DES-3200-28 1.85.B008
                    "nterface alias": LLDP_PORT_SUBTYPE_ALIAS,
                    "port component": LLDP_PORT_SUBTYPE_COMPONENT,
                    "mac address": LLDP_PORT_SUBTYPE_MAC,
                    "macaddress": LLDP_PORT_SUBTYPE_MAC,
                    "network address": LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
                    "interface name": LLDP_PORT_SUBTYPE_NAME,
                    "agent circuit id": LLDP_PORT_SUBTYPE_AGENT_CIRCUIT_ID,
                    "locally assigned": LLDP_PORT_SUBTYPE_LOCAL,
                    "local": LLDP_PORT_SUBTYPE_LOCAL,
                }[remote_port_subtype.strip().lower()]
                n["remote_port"] = m.group("port_id").strip()
                if n["remote_port_subtype"] == LLDP_PORT_SUBTYPE_MAC:
                    try:
                        n["remote_port"] = MACAddressParameter().clean(n["remote_port"])
                    except ValueError:
                        continue
                if n["remote_port_subtype"] == LLDP_PORT_SUBTYPE_NETWORK_ADDRESS:
                    n["remote_port"] = IPv4Parameter().clean(n["remote_port"])

                if m.group("port_description").strip():
                    p = m.group("port_description").strip()
                    n["remote_port_description"] = re.sub(r"\n\s{49}", "", p)
                if m.group("system_name").strip():
                    p = m.group("system_name").strip()
                    n["remote_system_name"] = re.sub(r"\n\s{49}", "", p)
                if m.group("system_description").strip():
                    p = m.group("system_description").strip()
                    n["remote_system_description"] = re.sub(r"\n\s{49}", "", p)
                caps = 0
                for c in m.group("system_capabilities").split(","):
                    c = re.sub(r"\s{49,50}", "", c)
                    c = c.strip()
                    if not c:
                        break
                    caps |= {
                        "Other": LLDP_CAP_OTHER,
                        "Repeater": LLDP_CAP_REPEATER,
                        "Bridge": LLDP_CAP_BRIDGE,
                        "Access Point": LLDP_CAP_WLAN_ACCESS_POINT,
                        "WLAN Access Point": LLDP_CAP_WLAN_ACCESS_POINT,
                        "Router": LLDP_CAP_ROUTER,
                        "Telephone": LLDP_CAP_TELEPHONE,
                        "DOCSIS Cable Device": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                        "Station Only": LLDP_CAP_STATION_ONLY,
                    }[c]
                n["remote_capabilities"] = caps
                i["neighbors"] += [n]
            if i["neighbors"]:
                r += [i]
        return r

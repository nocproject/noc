# ---------------------------------------------------------------------
# DLink.DxS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
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
from noc.core.snmp.render import render_bin
from noc.core.lldp import (
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_UNSPECIFIED,
)

def render_smart_mac(oid: str, value: bytes) -> bytes:
    """
    Try render 6 octets as MAC address. Render UTF-8 string on length mismatch
    :param oid:
    :param value:
    :return:
    """
    if len(value) != 6:
        return smart_text(value, errors="ignore")
    return "%02X:%02X:%02X:%02X:%02X:%02X" % tuple(value)

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

    def get_local_iface(self):
        r = {}
        
        # Get LocalPort Table
        for port_num, port_subtype, port_id, port_desc in self.snmp.get_tables(
            [
                "1.0.8802.1.1.2.1.3.7.1.2",  # LLDP-MIB::lldpLocPortIdSubtype
                "1.0.8802.1.1.2.1.3.7.1.3",  # LLDP-MIB::lldpLocPortId
                "1.0.8802.1.1.2.1.3.7.1.4",  # LLDP-MIB::lldpLocPortDesc
            ],
            display_hints={
                "1.0.8802.1.1.2.1.3.7.1.3": render_smart_mac
            }
        ):
            local_interface = ""
            if port_subtype == LLDP_PORT_SUBTYPE_LOCAL:
                # DGS-3120-24SC   - 1/24
                # DGS-3000-28SC   - 1/24
                # DES3200-28F     - 1/24
                # DGS1210-12TS/ME - 12
                local_interface = port_id
            elif port_subtype == LLDP_PORT_SUBTYPE_NAME:
                # DGS3130-30S - eth1/0/30
                local_interface = port_id
            elif port_subtype == LLDP_PORT_SUBTYPE_MAC:
                self.logger.debug("'%s' We cannot match interface by MAC. Try parse PortDesc '%s'", port_id, port_desc)
                local_interface = self.profile.convert_interface_name(port_desc)
            else:
                self.logger.debug("Unknown PortIdSubtype '%s'. Set ifname to PortId", port_subtype, port_id)
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
            if neigh["remote_chassis_id_subtype"] == 4:
                neigh["remote_chassis_id"] = MAC(neigh["remote_chassis_id"])
            if neigh["remote_port_subtype"] == 3:
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
                    "chassis component": 1,
                    "interface alias": 2,
                    "port component": 3,
                    "mac address": 4,
                    "macaddress": 4,
                    "network address": 5,
                    "interface name": 6,
                    "local": 7,
                }[remote_chassis_id_subtype.strip().lower()]
                n["remote_chassis_id"] = m.group("chassis_id").strip()
                remote_port_subtype = m.group("port_id_subtype").replace("_", " ")
                n["remote_port_subtype"] = {
                    "interface alias": 1,
                    # DES-3526 6.00 B48, DES-3526 6.00 B49,
                    # DES-3200-28 1.85.B008
                    "nterface alias": 1,
                    "port component": 2,
                    "mac address": 3,
                    "macaddress": 3,
                    "network address": 4,
                    "interface name": 5,
                    "agent circuit id": 6,
                    "locally assigned": 7,
                    "local": 7,
                }[remote_port_subtype.strip().lower()]
                n["remote_port"] = m.group("port_id").strip()
                if n["remote_port_subtype"] == 3:
                    try:
                        n["remote_port"] = MACAddressParameter().clean(n["remote_port"])
                    except ValueError:
                        continue
                if n["remote_port_subtype"] == 4:
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
                        "Other": 1,
                        "Repeater": 2,
                        "Bridge": 4,
                        "Access Point": 8,
                        "WLAN Access Point": 8,
                        "Router": 16,
                        "Telephone": 32,
                        "DOCSIS Cable Device": 64,
                        "Station Only": 128,
                    }[c]
                n["remote_capabilities"] = caps
                i["neighbors"] += [n]
            if i["neighbors"]:
                r += [i]
        return r

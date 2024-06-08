# ---------------------------------------------------------------------
# Eltex.LTP16N.get_cpe
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE
from noc.core.text import parse_table, parse_kv


class Script(BaseScript):
    name = "Eltex.LTP16N.get_cpe"
    interface = IGetCPE

    splitter = re.compile(r"\s*-+\n")

    state_map = {
        "OK": "active",
        "OFFLINE": "inactive",
        "CFGINPROGRESS": "provisioning",
        None: "other",
    }
    state_map_snmp = {
        4: "provisioning",
        5: "active",
        6: "provisioning",
        7: "inactive",
        8: "inactive",
    }
    kv_map = {
        "serial number": "serial_number",
        "pon-password": "pon_password",
        "pon-port": "pon_port",
        "ont id": "ont_id",
        "equipment id": "equipment_id",
        "hardware version": "hardware_version",
        "software version": "software_version",
        "equalization delay": "equalization_delay",
        "fec state": "fec_state",
        "alloc ids": "alloc_ids",
        "state": "state",
        "ont distance": "ont_distance",
        "rssi": "rssi",
    }

    def get_active_pon_ports(self):
        pon_ports_active = []
        try:
            v = self.cli("show interface pon-port 1-16 state", cached=True)
            for i in parse_table(v, line_wrapper=None):
                if i[1] == "OK":
                    pon_ports_active += [i[0].split()]
        except self.CLISyntaxError:
            raise NotImplementedError

        return pon_ports_active

    def execute_cli(self, **kwargs):
        r = []
        active_pon_ports = self.get_active_pon_ports()
        for iface in active_pon_ports:
            try:
                res_ont = self.cli(f"show interface ont {iface} state")
            except self.CLISyntaxError:
                raise NotImplementedError
            ports = res_ont.split("\n\n")
            for port in ports:
                if port:
                    parts = self.splitter.split(port)
                    if len(parts) > 1:
                        header = parts[1]
                        cpe_id = header.split("[ONT")[-1].split("]")[0]
                        data = parse_kv(self.kv_map, port)
                        if data:
                            r += [
                                {
                                    "id": cpe_id.lower(),
                                    "global_id": data.get("serial_number"),
                                    "status": self.state_map.get(data.get("state"), "other"),
                                    "type": "ont",
                                    "interface": iface,
                                    "model": data.get("equipment_id"),
                                    "serial": data.get("serial_number"),
                                    "version": data.get("software_version"),
                                    "distance": float(data.get("ont_distance").split()[0]) * 1000,
                                }
                            ]
        return r

    def execute_snmp(self, **kwargs):
        r = []
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.35265.1.209.4.1.1.1.5.1"):
            iface = oid[len("1.3.6.1.4.1.35265.1.209.4.1.1.1.5.1") + 1 :].split(".")[0]
            ont_id = oid[len("1.3.6.1.4.1.35265.1.209.4.1.1.1.5.1") + 1 :].split(".")[1]
            r += [
                {
                    "interface": iface,
                    "id": ont_id,
                    "global_id": self.snmp.get(
                        f"1.3.6.1.4.1.35265.1.209.4.1.1.1.4.1.{iface}.{ont_id}"
                    ),
                    "serial": self.snmp.get(
                        f"1.3.6.1.4.1.35265.1.209.4.1.1.1.4.1.{iface}.{ont_id}"
                    ),
                    "model": self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.1.1.1.8.1.{iface}.{ont_id}"),
                    "version": self.snmp.get(
                        f"1.3.6.1.4.1.35265.1.209.4.1.1.1.7.1.{iface}.{ont_id}"
                    ),
                    "distance": self.snmp.get(
                        f"1.3.6.1.4.1.35265.1.209.4.1.1.1.18.1.{iface}.{ont_id}"
                    ),
                    "type": "ont",
                    "status": self.state_map_snmp.get(v, "other"),
                }
            ]

        return r

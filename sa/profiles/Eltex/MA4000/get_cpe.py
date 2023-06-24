# ---------------------------------------------------------------------
# Eltex.MA4000.get_cpe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "Eltex.MA4000.get_cpe"
    interface = IGetCPE

    splitter = re.compile(r"\s*-+\n")

    kv_map = {
        "serial number": "serial_number",
        "slot": "slot",
        "gpon password": "gpon_password",
        "gpon-port": "gpon_port",
        "ont id": "ont_id",
        "equipment id": "equipment_id",
        "hardware version": "hardware_version",
        "software version": "software_version",
        "equalization delay": "equalization_delay",
        "fec state": "fec_state",
        "omci port": "omci_port",
        "alloc ids": "alloc_ids",
        "hardware state": "hardware_state",
        "state": "state",
        "ont distance": "ont_distance",
        "rssi": "rssi",
    }

    state_map = {"OK": "active", "CFGINPROGRESS": "provisioning", None: "other"}

    def execute_cli(self, **kwargs):
        r = []
        boards = self.profile.get_board(self)
        for slot in boards:
            if slot["status"] != "up":
                continue
            try:
                c = self.cli(f"show interface ont {slot['slot']} state")
            except self.CLISyntaxError:
                raise NotImplementedError
            parts = self.splitter.split(c)[1:]
            while len(parts) > 1:
                (header, body), parts = parts[:2], parts[2:]
                if len(body) > 100:
                    data = parse_kv(self.kv_map, body)
                    cpe_id = header.split("[")[-1].split("]")[0]
                    r += [
                        {
                            "id": cpe_id[3:].lower(),
                            "global_id": data.get("serial_number"),
                            "status": self.state_map.get(data.get("state"), "other"),
                            "type": "ont",
                            "interface": cpe_id[3:].rsplit("/", 1)[0],
                            "model": data.get("equipment_id"),
                            "serial": data.get("serial_number"),
                            "version": data.get("software_version"),
                            "distance": float(data.get("ont_distance").split()[0]) * 1000,
                        }
                    ]
        return r

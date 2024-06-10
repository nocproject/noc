# ---------------------------------------------------------------------
# ECI.HiFOCuS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.text import parse_kv
from noc.core.comp import smart_text, smart_bytes


class Script(BaseScript):
    name = "ECI.HiFOCuS.get_inventory"
    interface = IGetInventory
    always_prefer = "S"  # Stuck CLI periodically

    rx_table_spliter = re.compile(r"(?:\+-*)+\n")

    slot_detail_map = {
        "runswversion": "sw_ver",
        "bootswversion": "boot_sw",
        "hwversion": "hw_version",
        "serialno": "serial",
        "vendorid": "vendor",
        "hwdescription": "hw_descr",
        "catalognumber": "order_num",
        "productrevision": "rev",
    }

    def execute_snmp(self, **kwargs):
        r = []
        for (
            oid,
            serial,
            vendor,
            inv_type,
            part_no,
            hw_descr,
            catalog_num,
            rev,
        ) in self.snmp.get_tables(
            [
                "1.3.6.1.4.1.1286.1.3.3.1.1.7",
                "1.3.6.1.4.1.1286.1.3.3.1.1.8",
                "1.3.6.1.4.1.1286.1.3.3.1.1.10",
                "1.3.6.1.4.1.1286.1.3.3.1.1.15",
                "1.3.6.1.4.1.1286.1.3.3.1.1.17",
                "1.3.6.1.4.1.1286.1.3.3.1.1.29",
                "1.3.6.1.4.1.1286.1.3.3.1.1.30",
            ],
            max_retries=2,
        ):
            serial = smart_text(serial, errors="ignore").strip("\x00")
            if not serial:
                continue
            r += [
                {
                    "type": "LINECARD",
                    "number": "0",
                    "vendor": "ECI",
                    "part_no": [hw_descr, catalog_num],
                    "serial": serial.split(smart_text("\x00"))[0],
                    "revision": rev,
                    "description": "",
                }
            ]
        return r

    def execute_cli(self, **kwargs):
        # "EXISTSH ALL"
        r = []
        # boards = self.profile.get_boards(self)
        try:
            v = self.cli("ginv all", cached=True)
        except self.CLISyntaxError:
            raise NotImplementedError
        for line in self.rx_table_spliter.split(v):
            if not line.startswith("|"):
                continue
            row = [x.strip() for x in line.strip("|\n").split("|")]
            if row[0] == "SH":
                # header
                continue
            shelf, slot, port, mani, _, sw_ver, boot_ver, hw_ver, serial, _, _ = row
            if int(port):
                continue
            detail = self.cli("ginv %s %s %s %s" % (shelf, slot, port, mani))
            if not detail:
                continue
            x = parse_kv(self.slot_detail_map, detail)
            r += [
                {
                    "type": "LINECARD",
                    "number": slot,
                    "vendor": "ECI",
                    "part_no": (
                        [x["hw_descr"], x["order_num"]] if x.get("order_num") else [x["hw_descr"]]
                    ),
                    "serial": serial,
                    "revision": smart_text(smart_bytes(x["rev"]), errors="ignore"),
                    "description": "",
                }
            ]
        return r

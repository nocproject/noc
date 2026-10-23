# ---------------------------------------------------------------------
# MikroTik.SwOS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import codecs

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "MikroTik.SwOS.get_inventory"
    interface = IGetInventory

    def execute_cli(self):
        r = []
        v = self.scripts.get_version()
        serial = self.capabilities.get("Chassis | Serial Number")
        r.append(
            {
                "type": "CHASSIS",
                "vendor": "MikroTik",
                "part_no": [v["platform"]],
                "serial": serial,
            }
        )
        sfps = self.profile.parseBrokenJson(self.http.get("/sfp.b", cached=True, eof_mark=b"}"))
        if sfps.get("vnd"):
            sfp_count = len(sfps["vnd"])
            for i in range(sfp_count):
                vendor = codecs.decode(sfps["vnd"][i], "hex").decode().strip()
                part_no = codecs.decode(sfps["pnr"][i], "hex").decode().strip()
                revision = codecs.decode(sfps["rev"][i], "hex").decode().strip()
                serial = codecs.decode(sfps["ser"][i], "hex").decode().strip()
                date = codecs.decode(sfps["dat"][i], "hex").decode().strip()
                dt = date.split("-")
                year = "20" + dt[0]
                parts = [year, dt[1], dt[2]]
                mfd = "-".join(parts)

                descr = codecs.decode(sfps["typ"][i], "hex").strip()
                r.append(
                    {
                        "type": "XCVR",
                        "vendor": vendor,
                        "serial": serial,
                        "part_no": [part_no],
                        "number": i,
                        "revision": revision,
                        "description": descr,
                        "mfg_date": mfd,
                    }
                )
        elif sfps.get("vndr"):
            vendor = codecs.decode(sfps["vndr"], "hex").decode().strip()
            part_no = codecs.decode(sfps["ptnr"], "hex").decode().strip()
            revision = codecs.decode(sfps["rev"], "hex").decode().strip()
            serial = codecs.decode(sfps["ser"], "hex").decode().strip()
            date = codecs.decode(sfps["date"], "hex").decode().strip()
            dt = date.split("-")
            year = "20" + dt[0]
            parts = [year, dt[1], dt[2]]
            mfd = "-".join(parts)
            r.append(
                {
                    "type": "XCVR",
                    "vendor": vendor,
                    "serial": serial,
                    "part_no": [part_no],
                    "number": 1,
                    "revision": revision,
                    "mfg_date": mfd,
                }
            )
        return r

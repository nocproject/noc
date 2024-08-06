# ---------------------------------------------------------------------
# inv.inv pconf plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import orjson

# NOC modules
from .base import InvPlugin


class PConfPlugin(InvPlugin):
    name = "pconf"
    js = "NOC.inv.inv.plugins.pconf.PConfPanel"

    PATH = "var/adm200/AGG-200.json"

    def get_data(self, request, o):
        # @todo: Temporary
        with open(self.PATH) as fp:
            data = orjson.loads(fp.read())
        # Parse data
        conf = []
        for item in data["RK"][0]["DV"]:
            # Iterate cards
            # >>>
            if item["cls"] != "adm200":
                continue
            # <<<
            pm = item.get("PM")
            if not item:
                continue
            for row in pm:
                name = row.get("nam")
                if not name:
                    continue
                conf.append(
                    {
                        "name": name,
                        "value": row.get("val") or "",
                        "description": row.get("dsc") or "",
                        "units": row.get("unt") or "",
                        "read_only": (row.get("acs") or "") != "W",
                    }
                )
        return {"id": str(o.id), "conf": conf}

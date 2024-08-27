# ---------------------------------------------------------------------
# inv.inv pconf plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import orjson

# NOC modules
from noc.inv.models.object import Object
from noc.sa.interfaces.base import StringParameter
from .base import InvPlugin


class PConfPlugin(InvPlugin):
    name = "pconf"
    js = "NOC.inv.inv.plugins.pconf.PConfPanel"

    PATH = "var/adm200/AGG-200.json"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            f"api_plugin_{self.name}_set",
            self.api_set,
            url=f"^(?P<id>[0-9a-f]{{24}})/plugin/{self.name}/set/$",
            method=["POST"],
            validate={"name": StringParameter(), "value": StringParameter()},
        )

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
                # Determinee type
                options = row.get("EM")
                t = row.get("typ")
                if options:
                    dt = "enum"
                elif t == 32:
                    dt = "string"
                else:
                    dt = "string"
                c = {
                    "name": name,
                    "value": row.get("val") or "",
                    "description": row.get("dsc") or "",
                    "units": row.get("unt") or "",
                    "read_only": (row.get("acs") or "") != "W",
                    "type": dt,
                }
                if options:
                    c["options"] = [{"id": x["val"], "label": x["dsc"]} for x in options]
                conf.append(c)
        return {"id": str(o.id), "conf": conf}

    def api_set(self, request, id:str,,name:str,value:str):
        o = self.app.get_object_or_404(Object, id=id)
        print(f">>> name={name}, value={value}")
        return {
            "status": True
        }

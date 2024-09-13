# ---------------------------------------------------------------------
# inv.inv BoM plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any

# NOC modules
from noc.inv.models.object import Object
from .base import InvPlugin


class BoMPlugin(InvPlugin):
    name = "bom"
    js = "NOC.inv.inv.plugins.bom.BoMPanel"

    def get_data(self, request, obj: Object) -> dict[str, Any]:
        r: list[dict[str, str]] = []
        for o in Object.objects.filter(id__in=obj.get_nested_ids()):
            r.append(
                {
                    "id": str(o.id),
                    "vendor": str(o.model.vendor.name),
                    "model": o.model.name.split("|")[-1].strip(),
                    "location": "???",
                    "serial": o.get_data("asset", "serial") or "",
                    "asset_no": o.get_data("asset", "asset_no") or "",
                }
            )
        return {"data": r}

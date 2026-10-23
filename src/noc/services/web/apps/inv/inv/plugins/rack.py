# ---------------------------------------------------------------------
# inv.inv data plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.inv.models.object import Object
from noc.sa.interfaces.base import ObjectIdParameter, IntParameter
from noc.core.facade.rack import get_svg_for_rack
from noc.core.facade.response import svg_response
from .base import InvPlugin


class RackPlugin(InvPlugin):
    name = "rack"
    js = "NOC.inv.inv.plugins.rack.RackPanel"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            f"api_plugin_{self.name}_set_rackload",
            self.api_set_rack_load,
            url=f"^(?P<id>[0-9a-f]{{24}})/plugin/{self.name}/rackload/$",
            method=["POST"],
            validate={
                "cid": ObjectIdParameter(),
                "position_front": IntParameter(),
                "position_rear": IntParameter(),
                "shift": IntParameter(),
            },
        )
        self.add_view(
            f"api_plugin_{self.name}_facade",
            self.api_facade_svg,
            url=f"^(?P<id>[0-9a-f]{{24}})/plugin/{self.name}/(?P<name>front|rear).svg$",
            method=["GET"],
        )

    def get_data(self, request: HttpRequest, o):
        r = {
            "id": str(o.id),
            "rack": {k: o.get_data("rack", k) for k in ("units", "width", "depth")},
            "load": [],
        }
        r["rack"]["label"] = o.name
        # Fill content
        for c in o.iter_children():
            # Rack position
            units = c.get_data("rackmount", "units")
            pos = c.get_data("rackmount", "position")
            side = c.get_data("rackmount", "side") or "f"
            # Facades
            # Rack content
            r["load"].append(
                {
                    "id": str(c.id),
                    "name": c.name,
                    "model": c.model.name,
                    "units": units,
                    "position_front": pos if units and side == "f" else None,
                    "position_rear": pos if units and side == "r" else None,
                    "shift": c.get_data("rackmount", "shift") or 0,
                }
            )
        return r

    def api_set_rack_load(
        self, request: HttpRequest, id, cid, position_front, position_rear, shift
    ):
        o = self.app.get_object_or_404(Object, id=id)
        co = self.app.get_object_or_404(Object, id=cid)
        if co.parent.id != o.id:
            return self.app.response_not_found()
        if position_front:
            co.set_data("rackmount", "position", position_front)
            co.set_data("rackmount", "side", "f")
            co.save()
            co.log(
                f"Set rack position to front #{int(position_front)}",
                user=request.user.username,
                system="WEB",
                op="CHANGE",
            )
        elif position_rear:
            co.set_data("rackmount", "position", position_rear)
            co.set_data("rackmount", "side", "r")
            co.save()
            co.log(
                f"Set rack position to rear #{int(position_rear)}",
                user=request.user.username,
                system="WEB",
                op="CHANGE",
            )
        else:
            co.reset_data("rackmount", "position")
            co.reset_data("rackmount", "side")
            co.save()
            co.log("Reset rack position", user=request.user.username, system="WEB", op="CHANGE")
        if shift < 0 or shift > 2:
            shift = 0
        if co.get_data("rackmount", "shift") != shift:
            co.set_data("rackmount", "shift", shift)
            co.save()
            co.log(
                f"Set position shift to {int(shift)} holes",
                user=request.user.username,
                system="WEB",
                op="CHANGE",
            )

    def api_facade_svg(self, request: HttpRequest, id: str, name: str):
        obj = self.app.get_object_or_404(Object, id=id)
        # Get SVG
        svg = get_svg_for_rack(obj, name=name)
        svg.enable_highlight()
        return svg_response(svg)

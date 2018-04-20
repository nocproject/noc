# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv data plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import InvPlugin
from noc.inv.models.object import Object
from noc.sa.interfaces.base import ObjectIdParameter, IntParameter


class RackPlugin(InvPlugin):
    name = "rack"
    js = "NOC.inv.inv.plugins.rack.RackPanel"

    def init_plugin(self):
        super(RackPlugin, self).init_plugin()
        self.add_view(
            "api_plugin_%s_set_rackload" % self.name,
            self.api_set_rack_load,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/rackload/$" % self.name,
            method=["POST"],
            validate={
                "cid": ObjectIdParameter(),
                "position_front": IntParameter(),
                "position_rear": IntParameter(),
                "shift": IntParameter()
            }
        )

    def get_data(self, request, o):
        r = {
            "id": str(o.id),
            "rack": dict(
                (k, o.get_data("rack", k))
                for k in ("units", "width", "depth")
            ),
            "content": [],
            "load": []
        }
        r["rack"]["label"] = o.name
        # Fill content
        for c in o.get_content():
            units = c.get_data("rackmount", "units")
            pos = c.get_data("rackmount", "position")
            side = c.get_data("rackmount", "side") or "f"
            r["load"] += [{
                "id": str(c.id),
                "name": c.name,
                "model": c.model.name,
                "units": units,
                "position_front": pos if units and side == "f" else None,
                "position_rear": pos if units and side == "r" else None,
                "shift": c.get_data("rackmount", "shift") or 0
            }]
            if units and pos:
                r["content"] += [{
                    "id": str(c.id),
                    "units": units,
                    "pos": pos,
                    "name": c.name,
                    "side": side,
                    "shift": c.get_data("rackmount", "shift") or 0
                }]
        return r

    def api_set_rack_load(self, request, id, cid,
                          position_front, position_rear, shift):
        o = self.app.get_object_or_404(Object, id=id)
        co = self.app.get_object_or_404(Object, id=cid)
        if co.container != o.id:
            return self.app.response_not_found()
        if position_front:
            co.set_data("rackmount", "position", position_front)
            co.set_data("rackmount", "side", "f")
            co.save()
            co.log(
                "Set rack position to front #%d" % position_front,
                user=request.user.username, system="WEB",
                op="CHANGE"
            )
        elif position_rear:
            co.set_data("rackmount", "position", position_rear)
            co.set_data("rackmount", "side", "r")
            co.save()
            co.log(
                "Set rack position to rear #%d" % position_rear,
                user=request.user.username, system="WEB",
                op="CHANGE"
            )
        else:
            co.reset_data("rackmount", "position")
            co.reset_data("rackmount", "side")
            co.save()
            co.log(
                "Reset rack position",
                user=request.user.username, system="WEB",
                op="CHANGE"
            )
        if shift < 0 or shift > 2:
            shift = 0
        if co.get_data("rackmount", "shift") != shift:
            co.set_data("rackmount", "shift", shift)
            co.save()
            co.log("Set position shift to %d holes" % shift,
                user=request.user.username, system="WEB",
                op="CHANGE")

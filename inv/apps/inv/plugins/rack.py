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
            "api_plugin_%s_rackload" % self.name,
            self.api_rack_load,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/rackload/$" % self.name,
            method=["GET"]
        )
        self.add_view(
            "api_plugin_%s_set_rackload" % self.name,
            self.api_set_rack_load,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/rackload/$" % self.name,
            method=["POST"],
            validate={
                "cid": ObjectIdParameter(),
                "position_front": IntParameter(),
                "position_rear": IntParameter()
            }
        )

    def get_data(self, request, o):
        r = {
            "id": str(o.id),
            "rack": dict(
                (k, o.get_data("rack", k))
                for k in ("units", "width", "depth")
            ),
            "content": []
        }
        for c in o.get_content():
            units = c.get_data("rackmount", "units")
            pos = c.get_data("rackmount", "position")
            side = c.get_data("rackmount", "side") or "f"
            if units and pos:
                r["content"] += [{
                    "units": units,
                    "pos": pos,
                    "name": c.name,
                    "side": side
                }]
        return r

    def api_rack_load(self, request, id):
        o = self.app.get_object_or_404(Object, id=id)
        r = []
        for c in o.get_content():
            x = {
                "id": str(c.id),
                "name": c.name,
                "model": c.model.name,
                "units": c.get_data("rackmount", "units"),
                "position_front": None,
                "position_rear": None
            }
            if x["units"]:
                pos = c.get_data("rackmount", "position")
                if pos:
                    if c.get_data("rackmount", "side") == "r":
                        x["position_rear"] = pos
                    else:
                        x["position_front"] = pos
            r += [x]
        return {
            "units": o.get_data("rack", "units"),
            "content": r
        }

    def api_set_rack_load(self, request, id, cid,
                          position_front, position_rear):
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
            co.log(
                "Reset rack position",
                user=request.user.username, system="WEB",
                op="CHANGE"
            )

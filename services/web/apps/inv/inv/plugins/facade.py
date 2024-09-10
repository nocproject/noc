# ---------------------------------------------------------------------
# inv.inv facade plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import random

# NOC modules
from .base import InvPlugin
from noc.inv.models.object import Object
from noc.core.facade.box import get_svg_for_box
from noc.core.facade.response import svg_response


class FacadePlugin(InvPlugin):
    name = "facade"
    js = "NOC.inv.inv.plugins.facade.FacadePanel"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            "api_plugin_%s_facade" % self.name,
            self.api_facade_svg,
            url="^(?P<id>[0-9a-f]{24})/plugin/facade/(?P<name>front|rear).svg$",
            method=["GET"],
        )

    def get_data(self, request, o: Object):
        r = {"id": str(o.id), "views": []}
        seed = random.randint(0, 0x7FFFFFFF)
        if o.model.front_facade:
            r["views"].append(
                {
                    "name": "Front",
                    "src": f"/inv/inv/{o.id}/plugin/facade/front.svg?_dc={seed}",
                }
            )
        if o.model.rear_facade:
            r["views"].append(
                {
                    "name": "Rear",
                    "src": f"/inv/inv/{o.id}/plugin/facade/rear.svg?_dc={seed}",
                }
            )
        return r

    def api_facade_svg(self, request, id: str, name: str):
        obj = self.app.get_object_or_404(Object, id=id)
        svg = get_svg_for_box(obj, name)
        if svg is None:
            return self.app.response_not_found()
        svg.enable_highlight()
        return svg_response(svg)

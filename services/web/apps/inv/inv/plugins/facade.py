# ---------------------------------------------------------------------
# inv.inv facade plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Dict
import random

# Third-party modules
from bson import ObjectId
from django.http import HttpResponse

# NOC modules
from .base import InvPlugin
from noc.inv.models.facade import Facade
from noc.inv.models.object import Object
from noc.core.svg import SVG
from noc.core.facade.utils import slot_to_id


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
        o = self.app.get_object_or_404(Object, id=id)
        svg = self.get_svg(o, name)
        if svg is None:
            return self.app.response_not_found()
        return HttpResponse(
            svg.to_string(),
            content_type="image/svg+xml",
            status=200,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    def get_svg(
        self, o: Object, name: Optional["str"] = None, cache: Optional[Dict[ObjectId, SVG]] = None
    ) -> Optional["SVG"]:
        def load_svg(facade: Facade) -> SVG:
            svg = cache.get(facade.id)
            if svg:
                return svg
            svg = SVG.from_string(facade.data)
            cache[facade.id] = svg
            return svg

        cache = cache or {}
        # Get facade name
        name = name or "front"
        if name == "front":
            facade = o.model.front_facade
        elif name == "rear":
            facade = o.model.rear_facade
        else:
            msg = f"Invalid facade: {name}"
            raise ValueError(msg)
        if not facade:
            return None
        # Get module facade
        svg = load_svg(facade)
        # Insert nested modules
        for ro in o.iter_children():
            # Always use front facades for nested modules
            mod_svg = self.get_svg(ro, name="front", cache=cache)
            if mod_svg:
                # Embed module
                try:
                    svg.embed(
                        slot_to_id(ro.parent_connection),
                        mod_svg,
                        resource=ro.as_resource(),
                        event="dblclick",
                    )
                except ValueError:
                    pass
        return svg

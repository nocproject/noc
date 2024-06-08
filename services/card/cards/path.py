# ----------------------------------------------------------------------
#  Path
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import orjson
from typing import List

# NOC modules
from .base import BaseCard
from noc.sa.models.managedobject import ManagedObject
from noc.core.topology.path import get_shortest_path
from noc.core.comp import smart_text
from noc.config import config


class PathCard(BaseCard):
    name = "path"
    default_template_name = "path"
    card_css = ["/ui/pkg/leaflet/leaflet.css", "/ui/card/css/path.css"]

    @property
    def card_js(self) -> List[str]:
        res = [
            "/ui/pkg/leaflet/leaflet.js",
        ]

        if config.gis.yandex_supported:
            res += [
                "/ui/pkg/leaflet/yapi.js",
                "/ui/pkg/leaflet/Yandex.js",
            ]

        res += [
            "/ui/common/map_layer_creator.js",
            "/ui/common/settings_loader.js",
            "/ui/card/js/path.js",
        ]

        return res

    def get_data(self):
        mo1, mo2 = self.id.split("-")
        print(self.id)
        mo1 = ManagedObject.get_by_id(int(mo1)) if mo1 else None
        mo2 = ManagedObject.get_by_id(int(mo2)) if mo2 else None
        s_path = [mo1]
        if mo1 and mo2:
            try:
                s_path = get_shortest_path(mo1, mo2)
            except ValueError:
                s_path = [mo1, mo2]

        path = []
        for mo in s_path:
            if not mo.x or not mo.y:
                continue
            if not path or mo.x != path[-1]["x"] or mo.y != path[-1]["y"]:
                path += [{"x": mo.x, "y": mo.y, "objects": [{"id": mo.id, "name": mo.name}]}]
            else:
                path[-1]["objects"] += [{"id": mo.id, "name": mo.name}]
        return {"mo1": mo1, "mo2": mo2, "path": smart_text(orjson.dumps(path))}

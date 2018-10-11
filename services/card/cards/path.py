# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  Path
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
import ujson
# NOC modules
from .base import BaseCard
from noc.sa.models.managedobject import ManagedObject
from noc.core.topology.path import get_shortest_path


class PathCard(BaseCard):
    name = "path"
    default_template_name = "path"
    card_css = [
        "/ui/pkg/leaflet/leaflet.css",
        "/ui/card/css/path.css"
    ]
    card_js = [
        "/ui/pkg/leaflet/leaflet.js",
        "/ui/card/js/path.js"
    ]

    def get_data(self):
        mo1, mo2 = [ManagedObject.get_by_id(int(x)) for x in self.id.split("-")]
        try:
            s_path = get_shortest_path(mo1, mo2)
        except ValueError:
            s_path = [mo1, mo2]

        path = []
        for mo in s_path:
            if not mo.x or not mo.y:
                continue
            if not path or mo.x != path[-1]["x"] or mo.y != path[-1]["y"]:
                path += [{
                    "x": mo.x,
                    "y": mo.y,
                    "objects": [{
                        "id": mo.id,
                        "name": mo.name
                    }]
                }]
            else:
                path[-1]["objects"] += [{
                    "id": mo.id,
                    "name": mo.name
                }]
        return {
            "mo1": mo1,
            "mo2": mo2,
            "path": ujson.dumps(path)
        }

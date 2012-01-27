# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Points overlay -
## Displays points on map
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.gis.overlays.base import *
from noc.lib.nosql import *


class PointsOverlay(OverlayHandler):
    """
    points overlay - display custom points on map

    config:
        collection: collection name
        position: position property name (GeoPointField)
        text: text label property name
    """
    def __init__(self, collection, position, text):
        self.collection = collection
        self.position = position
        self.text = text

    def handle(self, bbox, **kwargs):
        # Get collection
        collection = get_db()[self.collection]
        # Find points
        c = collection.find(
                {self.position: {"$within": {"$box": bbox}}},
                {"_id": 0, self.position: 1, self.text: 1})

        return {
            "type": "GeometryCollection",
            "geometries": [
                {
                    "type": "Point",
                    "coordinates": x[self.position]
                }
                for x in c
            ]
        }

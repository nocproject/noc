# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Gis-related utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from geopy.point import Point as GPoint
from geopy.distance import vincenty, great_circle, ELLIPSOIDS
## NOC settings
from noc.settings import config

# major, minor, flattening=(major-minor)/major
ELLIPSOIDS["Krass"] = (6378.245, 6356.863019, 1 / 298.3000031662238)
ELLIPSOIDS["ПЗ-90"] = (6378.1365, 6356.751758, 1 / 298.2564151)

ELLIPSOID = config.get("gis", "ellipsoid")


def distance(p1, p2, ellipsoid=ELLIPSOID):
    """
    Distnce between two points in meters
    """
    gp1 = GPoint(p1.y, p1.x)
    gp2 = GPoint(p2.y, p2.x)
    return vincenty(gp1, gp2, ellipsoid=ellipsoid).meters


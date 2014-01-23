# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Gis-related utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import math
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
    Distance between two points in meters
    """
    gp1 = GPoint(p1.y, p1.x)
    gp2 = GPoint(p2.y, p2.x)
    return vincenty(gp1, gp2, ellipsoid=ellipsoid).meters


def bearing(p1, p2):
    """
    Bearing from p1 to p2, in degrees, clockwise from north
    """
    sin = math.sin
    cos = math.cos
    lat1 = math.radians(p1.y)
    lat2 = math.radians(p2.y)
    dlon = math.radians(p2.x - p1.x)
    y = sin(dlon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


BEARINGS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
L_BEARINGS = len(BEARINGS)
BS = 360.0 / L_BEARINGS


def bearing_sym(p1, p2):
    """
    Compass-line symbolic bearing
    """
    b = bearing(p1, p2)
    ob = (b + 360 + BS / 2) % 360
    return BEARINGS[int(math.floor(ob / BS))]

# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Geo{graphic,metry} functions
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python module
import math

TS = 256  # Tile size 256x256
MIN_ZOOM = 0
MAX_ZOOM = 18
PI = math.pi

# Precalculated values
Bc = []
Cc = []
zc = []
c = TS
for d in range(0, MAX_ZOOM + 1):
    e = c / 2
    Bc += [c / 360.0]
    Cc += [c / (2 * PI)]
    zc += [(e, e)]
    c <<= 1


def xy_to_ll(zoom, px):
    """
    Convert tile index to EPSG:4326 lon/lat pair
    :param zoom:
    :param px:
    :return:
    """
    e = zc[zoom]
    f = (px[0] * TS - e[0]) / Bc[zoom]
    g = (px[1] * TS - e[1]) / -Cc[zoom]
    h = math.degrees(2 * math.atan(math.exp(g)) - 0.5 * PI)
    return f, h


def ll_to_xy(zoom, ll):
    """
    Convert EPSG:4326 lon/lat pair to tile index
    :param zoom:
    :param ll:
    :return:
    """
    d = zc[zoom]
    e = round(d[0] + ll[0] * Bc[zoom])
    f = min(max(math.sin(math.radians(ll[1])), -0.9999), 0.9999)
    g = round(d[1] + 0.5 * math.log((1 + f) / (1 - f)) * -Cc[zoom])
    return int(e / TS), int(g / TS)

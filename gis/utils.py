# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various GIS helpers
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import xml.dom.minidom


def parse_osm_bounds(tag):
    """
    Parse OSM <bounds> tag
    :param tag: String containing full <bounds ... /> tag
    :return: [minlon, minlat, maxlon, maxlat]
    :rtype: list of float

    >>> parse_osm_bounds('<bounds minlat="56.0756000" minlon="43.4516000" maxlat="56.1294000" maxlon="43.5866000"/>')
    [43.4516000, 56.0756000, 43.5866000, 56.1294000]
    >>> parse_osm_bounds('<bounds minlon="43.4516000" minlat="56.0756000" maxlon="43.5866000" maxlat="56.1294000" origin="http://www.openstreetmap.org/api/0.6"/>')
    [43.4516000, 56.0756000, 43.5866000, 56.1294000]
    """
    doc = xml.dom.minidom.parseString(tag)
    e = doc.getElementsByTagName("bounds")[0]
    return [float(e.getAttribute(n)) for n in ("minlon", "minlat",
                                               "maxlon", "maxlat")]

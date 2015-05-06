# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Geotagging base
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class Geocoder(object):
    name = None

    def forward(self, s):
        """
        Forward geocoding. Find coordinates by name
        :returns: (datum, lon, lat) or None
        """

    def reverse(self, lon, lat):
        """
        Find address by coordinates
        """

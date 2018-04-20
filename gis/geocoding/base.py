# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Geotagging base
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Geotagging base
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


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

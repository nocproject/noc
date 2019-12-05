# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Geocoder Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseGeocoder


class GeocoderLoader(BaseLoader):
    name = "geocoder"
    base_cls = BaseGeocoder
    base_path = ("core", "geocoder")
    ignored_names = {"base", "errors", "loader"}


# Create singleton object
loader = GeocoderLoader()

# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Geocoder Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging
import os

# NOC modules
from noc.core.loader.base import BaseLoader
from noc.core.geocoding.base import BaseGeocoder

logger = logging.getLogger(__name__)
BASE_PREFIX = os.path.join("core", "geocoding")


class GeocoderLoader(BaseLoader):
    name = "geocoder"
    base_cls = BaseGeocoder
    base_path = ("core", "geocoding", "providers")


# Create singleton object
loader = GeocoderLoader()

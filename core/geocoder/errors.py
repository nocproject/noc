# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Geocoding errors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class GeoCoderError(Exception):
    pass


class GeoCoderLimitExceeded(GeoCoderError):
    pass

# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# DataStream loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.loader.base import BaseLoader
from .base import DataStream


class DataStreamLoader(BaseLoader):
    name = "datastream"
    base_cls = DataStream
    base_path = ("services", "datastream", "streams")


# Create singleton object
loader = DataStreamLoader()

# ----------------------------------------------------------------------
# DataStream loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import DataStream


class DataStreamLoader(BaseLoader):
    name = "datastream"
    base_cls = DataStream
    base_path = ("services", "datastream", "streams")


# Create singleton object
loader = DataStreamLoader()

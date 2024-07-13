# ----------------------------------------------------------------------
# Mapper loader class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseMapper


class MapperLoader(BaseLoader):
    name = "mappers"
    base_cls = BaseMapper
    base_path = ("core", "techdomain", "mapper")
    ignored_names = {"loader", "base"}


# Create singleton object
loader = MapperLoader()

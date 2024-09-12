# ----------------------------------------------------------------------
# NRI Port mapper loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.core.loader.base import BaseLoader
from noc.core.etl.portmapper.base import BasePortMapper

logger = logging.getLogger(__name__)


class PortMapperLoader(BaseLoader):
    name = "portmapper"
    base_cls = BasePortMapper
    base_path = ("core", "etl", "portmapper")
    ignored_names = {"loader", "base"}


loader = PortMapperLoader()

# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NRI Port mapper loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import inspect
import logging
# Python modules
import os

from noc.config import config

# NOC modules
from base import BasePortMapper

logger = logging.getLogger(__name__)


class PortMapperLoader(object):
    def __init__(self):
        self.loaders = {}

    def get_loader(self, name):
        loader = self.loaders.get(name)
        custom_name = os.path.basename(config.path.custom_path)
        if not loader:
            logging.info("Loading %s", name)
            mn = "%s.etl.portmappers.%s" % (custom_name, name)
            try:
                sm = __import__(mn, {}, {}, "*")
                for n in dir(sm):
                    o = getattr(sm, n)
                    if (
                        inspect.isclass(o) and
                        issubclass(o, BasePortMapper) and
                        o.__module__ == sm.__name__
                    ):
                        loader = o
                        break
                    logger.error("Loader not found: %s", name)
            except ImportError, why:
                logger.error("Failed to load: %s", why)
                loader = None
            self.loaders[name] = loader
        return loader


loader = PortMapperLoader()

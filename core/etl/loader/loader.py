# ----------------------------------------------------------------------
# Loader loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import inspect
import threading

# NOC modules
from .base import BaseLoader
from noc.config import config

logger = logging.getLogger(__name__)


class LoaderLoader(object):
    def __init__(self):
        self.loaders = {}  # Load loaders
        self.lock = threading.Lock()
        self.all_loaders = set()

    def get_loader(self, name):
        """
        Load loader and return BaseLoader instance.
        Returns None when no loader found or loading error occured
        """
        with self.lock:
            loader = self.loaders.get(name)
            if not loader:
                logger.info("Loading loader %s", name)
                for p in config.get_customized_paths("", prefer_custom=True):
                    base = "noc.custom" if p else "noc.core"
                    module_name = "%s.etl.loader.%s" % (base, name)
                    try:
                        sm = __import__(module_name, {}, {}, "*")
                        for n in dir(sm):
                            o = getattr(sm, n)
                            if (
                                inspect.isclass(o)
                                and issubclass(o, BaseLoader)
                                and o.__module__ == sm.__name__
                            ):
                                loader = o
                                break
                            logger.error("Loader not found: %s", name)
                    except Exception as e:
                        logger.error("Failed to load loader %s: %s", name, e)
                        loader = None
                    if loader:
                        break
                self.loaders[name] = loader
            return loader


# Create singleton object
loader = LoaderLoader()

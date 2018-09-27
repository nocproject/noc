# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NBI API Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging
import inspect
import threading
import os
# NOC modules
from noc.config import config
from .base import NBIAPI

logger = logging.getLogger(__name__)
BASE_PREFIX = os.path.join("services", "nbi", "api")


class NBIAPILoader(object):
    def __init__(self):
        self.apis = {}  # Load API
        self.lock = threading.Lock()
        self.all_apis = set()

    def get_api(self, name):
        """
        Load API and return NBIAPI instance.
        Returns None when no API found or loading error occured
        """
        with self.lock:
            api = self.apis.get(name)
            if not api:
                logger.info("Loading API %s", name)
                if not self.is_valid_name(name):
                    logger.error("Invalid API name")
                    return None
                for path in config.get_customized_paths(BASE_PREFIX, prefer_custom=True):
                    if not os.path.exists(path):
                        continue
                    if path == BASE_PREFIX:
                        base_name = "noc"
                    else:
                        base_name = "noc.custom"
                    mn = "%s.services.nbi.api.%s" % (base_name, name)
                    try:
                        sm = __import__(mn, {}, {}, "*")
                        for n in dir(sm):
                            o = getattr(sm, n)
                            if (
                                inspect.isclass(o) and
                                issubclass(o, NBIAPI) and
                                o.__module__ == sm.__name__
                            ):
                                api = o
                                break
                        if not api:
                            logger.error("API not found: %s", name)
                    except Exception as e:
                        logger.error("Failed to load API %s: %s", name, e)
                        api = None
                self.apis[name] = api
            return api

    def is_valid_name(self, name):
        return ".." not in name

    def iter_apis(self):
        with self.lock:
            if not self.all_apis:
                self.all_apis = self.find_apis()
        for api in sorted(self.all_apis):
            yield api

    def find_apis(self):
        """
        Scan all available API
        """
        names = set()
        for path in config.get_customized_paths(BASE_PREFIX, prefer_custom=True):
            if not os.path.exists(path):
                continue
            for fn in os.listdir(path):
                if fn.startswith("_") or not fn.endswith(".py"):
                    continue
                names.add(fn[:-3])
        return names


# Create singleton object
loader = NBIAPILoader()

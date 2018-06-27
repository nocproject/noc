# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# DataStream loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging
import inspect
import threading
# NOC modules
from .base import DataStream

logger = logging.getLogger(__name__)


class DataStreamLoader(object):
    def __init__(self):
        self.datastreams = {}  # Load datastreams
        self.lock = threading.Lock()

    def get_datastream(self, name):
        """
        Load datastream and return DataStream instance.
        Returns None when no datastream found or loading error occured
        """
        with self.lock:
            datastream = self.datastreams.get(name)
            if not datastream:
                logger.info("Loading datastream %s", name)
                if not self.is_valid_name(name):
                    logger.error("Invalid datastream name")
                    return None
                module_name = "noc.services.datastream.streams.%s" % name
                try:
                    sm = __import__(module_name, {}, {}, "*")
                    for n in dir(sm):
                        o = getattr(sm, n)
                        if (
                            inspect.isclass(o) and
                            issubclass(o, DataStream) and
                            o.__module__ == sm.__name__
                        ):
                            datastream = o
                            break
                    if not datastream:
                        logger.error("DataStream not found: %s", name)
                except Exception as e:
                    logger.error("Failed to load DataStream %s: %s", name, e)
                    datastream = None
                self.datastreams[name] = datastream
            return datastream

    def is_valid_name(self, name):
        return ".." not in name


# Create singleton object
loader = DataStreamLoader()

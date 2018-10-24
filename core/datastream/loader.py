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
import threading
import os
# NOC modules
from noc.config import config
from noc.core.loader.base import BaseLoader
from .base import DataStream

logger = logging.getLogger(__name__)


class DataStreamLoader(BaseLoader):
    def __init__(self):
        super(DataStreamLoader, self).__init__()
        self.datastreams = {}  # Load datastreams
        self.lock = threading.Lock()
        self.all_datastreams = set()

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
                for p in config.get_customized_paths("", prefer_custom=True):
                    path = os.path.join(p, "services", "datastream", "streams", "%s.py" % name)
                    if not os.path.exists(path):
                        continue
                    if p:
                        # Customized datastream
                        base_name = os.path.basename(os.path.dirname(p))
                        module_name = "%s.services.datastream.streams.%s" % (base_name, name)
                    else:
                        # Common datastream
                        module_name = "noc.services.datastream.streams.%s" % name
                    datastream = self.find_class(module_name, DataStream, name)
                    if datastream:
                        break
                if not datastream:
                    logger.error("DataStream not found: %s", name)
                self.datastreams[name] = datastream
            return datastream

    def is_valid_name(self, name):
        return ".." not in name

    def iter_datastreams(self):
        with self.lock:
            if not self.all_datastreams:
                self.all_datastreams = self.find_datastreams()
        for ds in sorted(self.all_datastreams):
            yield ds

    def find_datastreams(self):
        """
        Scan all available datastreams
        """
        names = set()
        for dn in config.get_customized_paths(os.path.join("services", "datastream", "streams")):
            for file in os.listdir(dn):
                if file.startswith("_") or not file.endswith(".py"):
                    continue
                names.add(file[:-3])
        return names


# Create singleton object
loader = DataStreamLoader()

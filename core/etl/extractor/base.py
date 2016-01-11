# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Data Extractor
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import gzip
import os
import csv
import time
## Python modules
from noc.lib.log import PrefixLoggerAdapter

logger = logging.getLogger(__name__)


class BaseExtractor(object):
    """
    Data extractor interface. Subclasses must provide
    *iter_data* method
    """
    name = None
    PREFIX = "var/import"
    REPORT_INTERVAL = 1000
    # List of rows to be used as constant data
    data = []

    def __init__(self, system, config=None):
        self.system = system
        self.config = config or {}
        self.logger = PrefixLoggerAdapter(
            logger, "%s][%s" % (system, self.name)
        )
        self.import_dir = os.path.join(self.PREFIX, system, self.name)

    def get_new_state(self):
        if not os.path.isdir(self.import_dir):
            self.logger.info("Creating directory %s", self.import_dir)
            os.makedirs(self.import_dir)
        path = os.path.join(self.import_dir, "import.csv.gz")
        self.logger.info("Writing to %s", path)
        return gzip.GzipFile(path, "w")

    def iter_data(self):
        for row in self.data:
            yield row

    def clean(self, row):
        return row

    def extract(self):
        def q(s):
            if s == "" or s is None:
                return ""
            elif isinstance(s, unicode):
                return s.encode("utf-8")
            else:
                return str(s)

        self.logger.info("Extracting %s from %s",
                         self.name, self.system)
        t0 = time.time()
        with self.get_new_state() as f:
            writer = csv.writer(f)
            n = 0
            for row in self.iter_data():
                row = self.clean(row)
                writer.writerow([q(x) for x in row])
                n += 1
                if n % self.REPORT_INTERVAL == 0:
                    self.logger.info("   ... %d records", n)
        dt = time.time() - t0
        speed = n / dt
        self.logger.info(
            "%d records downloaded in %.2fs (%d records/s)",
            n, dt, speed
        )

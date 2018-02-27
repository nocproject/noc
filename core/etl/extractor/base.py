# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Data Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import gzip
import os
import csv
import time
import itertools
from collections import namedtuple
# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.config import config

logger = logging.getLogger(__name__)


class BaseExtractor(object):
    """
    Data extractor interface. Subclasses must provide
    *iter_data* method
    """
    Problem = namedtuple("Problem", ["line", "is_rej", "p_class", "message", "row"])
    name = None
    PREFIX = config.path.etl_import
    REPORT_INTERVAL = 1000
    # List of rows to be used as constant data
    data = []
    # Suppress deduplication message
    suppress_deduplication_log = False

    def __init__(self, system):
        self.system = system
        self.config = system.config
        self.logger = PrefixLoggerAdapter(
            logger, "%s][%s" % (system.name, self.name)
        )
        self.import_dir = os.path.join(self.PREFIX, system.name, self.name)
        self.fatal_problems = []
        self.quality_problems = []

    def register_quality_problem(self, line, p_class, message, row):
        self.quality_problems += [self.Problem(line=line + 1, is_rej=False, p_class=p_class, message=message, row=row)]

    def register_fatal_problem(self, line, p_class, message, row):
        self.fatal_problems += [self.Problem(line=line + 1, is_rej=True, p_class=p_class, message=message, row=row)]

    def get_new_state(self):
        if not os.path.isdir(self.import_dir):
            self.logger.info("Creating directory %s", self.import_dir)
            os.makedirs(self.import_dir)
        path = os.path.join(self.import_dir, "import.csv.gz")
        self.logger.info("Writing to %s", path)
        return gzip.GzipFile(path, "w")

    def get_problem_file(self):
        if not os.path.isdir(self.import_dir):
            self.logger.info("Creating directory %s", self.import_dir)
            os.makedirs(self.import_dir)
        path = os.path.join(self.import_dir, "import.csv.rej.gz")
        self.logger.info("Writing to %s", path)
        return gzip.GzipFile(path, "w")

    def iter_data(self):
        for row in self.data:
            yield row

    def filter(self, row):
        return True

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

        # Fetch data
        self.logger.info("Extracting %s from %s",
                         self.name, self.system.name)
        t0 = time.time()
        data = []
        n = 0
        seen = set()
        for row in self.iter_data():
            if not self.filter(row):
                continue
            row = self.clean(row)
            if row[0] in seen:
                if not self.suppress_deduplication_log:
                    self.logger.error("Duplicated row truncated: %r",
                                      row)
                continue
            else:
                seen.add(row[0])
            data += [[q(x) for x in row]]
            n += 1
            if n % self.REPORT_INTERVAL == 0:
                self.logger.info("   ... %d records", n)
        dt = time.time() - t0
        speed = n / dt
        self.logger.info(
            "%d records extracted in %.2fs (%d records/s)",
            n, dt, speed
        )
        # Sort
        data.sort()
        # Write
        f = self.get_new_state()
        writer = csv.writer(f)
        writer.writerows(data)
        f.close()
        if self.fatal_problems or self.quality_problems:
            self.logger.warning("Detect problems on extracting, fatal: %d, quality: %d",
                                len(self.fatal_problems),
                                len(self.quality_problems))
            self.logger.warning("Line num\tType\tProblem string")
            for p in self.fatal_problems:
                self.logger.warning("Fatal problem, line was rejected: %s\t%s\t%s" % (p.line, p.p_class, p.message))
            for p in self.quality_problems:
                self.logger.warning("Data quality problem in line:  %s\t%s\t%s" % (p.line, p.p_class, p.message))
            # Dump problem to file
            try:
                f = self.get_problem_file()
                writer = csv.writer(f, delimiter=";")
                for p in itertools.chain(self.quality_problems, self.fatal_problems):
                    writer.writerow(
                        [c.encode("utf-8") for c in p.row] + ["Fatal problem, line was rejected" if p.is_rej else
                                                              "Data quality problem"] + [p.message.encode("utf-8")])
            except IOError as e:
                self.logger.error("Error when saved problems %s", e)
            finally:
                f.close()
        else:
            self.logger.info("No problems detected")

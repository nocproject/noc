## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Whisper database
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
import whisper
## NOC modules
from base import TimeSeriesDatabase
from noc.settings import config


class WhisperDatabase(TimeSeriesDatabase):
    """
    Whisper database
    Settings:
        data_dir
        sparse_create
        autoflush
        lock_writes
    """
    name = "whisper"

    def __init__(self):
        super(TimeSeriesDatabase, self).__init__()
        sn = "storage_whisper"
        self.data_dir = config.get(sn, "data_dir")
        self.sparse_create = config.getboolean(sn, "sparse_create")
        whisper.AUTOFLUSH = config.getboolean(sn, "autoflush")
        whisper.LOCK = config.getboolean(sn, "lock_writes")

    def get_path(self, metric):
        return os.path.join(self.data_dir, *metric.split(".")) + ".wsp"

    def initialize(self):
        """
        Initialize database
        """
        pass

    def write(self, metric, datapoints):
        """
        Persist datapoints into the database metric
        Datapoints are [(timestamp, value), ....]
        """
        path = self.get_path(metric)
        whisper.update_many(path, datapoints)

    def exists(self, metric):
        """
        Check metric is exists in database
        """
        return os.path.exists(self.get_path(metric))

    def create(self, metric, retentions=None, xfilesfactor=None,
               aggregation_method=None, **kwargs):
        """
        Create database metric using default options
        """
        path = self.get_path(metric)
        self.ensure_path(path)
        whisper.create(
            path,
            retentions,
            xFilesFactor=xfilesfactor,
            aggregationMethod=aggregation_method,
            sparse=self.sparse_create,
            useFallocate=False
        )
        os.chmod(path, 0755)

    def get_metadata(self, metric, key):
        """
        Get metric metadata
        """
        if key != "aggregationMethod":
            raise ValueError("Invalid metadata key: %s" % key)
        path = self.get_path(metric)
        return whisper.info(path)["aggregationMethod"]

    def set_metadata(self, metric, key, value):
        """
        Modify metric metadata
        """
        if key != "aggregationMethod":
            raise ValueError("Invalid metadata key: %s" % key)
        path = self.get_path(metric)
        return whisper.setAggregationMethod(path, value)

    def fetch(self, metric, start, end):
        """
        Returns a all metric's value within range in form
        (start, end, step), [value1, ..., valueN]
        """
        path = self.get_path(metric)
        return whisper.fetch(path, start, end)

    def iter_metrics(self, d, pattern):
        """
        Yield all metrics from given directory
        """
        pattern += ".wsp"
        for f in self.match_entries(os.listdir(d), pattern):
            if os.path.isfile(os.path.join(d, f)):
                yield f[:-4]

    def find(self, path_expr):
        """
        Find all metrics belonging to path expression
        """
        return list(self.find_metrics(self.data_dir, path_expr))

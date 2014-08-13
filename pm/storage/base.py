## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Graphite-compatible storage interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import errno


class TimeSeriesDatabase(object):
    name = None

    def __init__(self):
        pass

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
        raise NotImplementedError()

    def exists(self, metric):
        """
        Check metric is exists in database
        """
        raise NotImplementedError()

    def create(self, metric, **options):
        """
        Create database metric using default options
        """
        raise NotImplementedError()

    def get_metadata(self, metric, key):
        """
        Get metric metadata
        """
        raise NotImplementedError()

    def set_metadata(self, metric, key, value):
        """
        Modify metric metadata
        """
        raise NotImplementedError()

    @classmethod
    def ensure_path(cls, path):
        """
        Create all necessary directories
        """
        d = os.path.dirname(path)
        if not os.path.isdir(d):
            try:
                os.makedirs(d, 0755)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise

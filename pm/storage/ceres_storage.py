## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ceres database
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
import ceres
## NOC modules
from base import TimeSeriesDatabase
from noc.settings import config


class CeresDatabase(TimeSeriesDatabase):
    """
    Ceres database
    """
    name = "ceres"

    def __init__(self):
        super(TimeSeriesDatabase, self).__init__()
        sn = "storage_ceres"
        self.data_dir = config.get(sn, "data_dir")
        if not self.data_dir.endswith(os.path.sep):
            self.data_dir += os.path.sep
        self.ensure_path(self.data_dir)
        self.tree = ceres.CeresTree(self.data_dir)
        # slice_caching = config.get(sn, "slice_caching")
        #if slice_caching:
        #    self.tree.setDefaultSliceCachingBehavior(slice_caching)
        max_slice_gap = config.getint(sn, "max_slice_gap")
        if max_slice_gap:
            ceres.MAX_SLICE_GAP = max_slice_gap

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
        self.tree.store(metric, datapoints)

    def exists(self, metric):
        """
        Check metric is exists in database
        """
        return self.tree.hasNode(metric)

    def create(self, metric, retentions=None, xfilesfactor=None,
               aggregation_method=None, **kwargs):
        """
        Create database metric using default options
        """
        self.tree.createNode(
            metric,
            retentions=retentions,
            timeStep=retentions[0][0],
            xFilesFactor=xfilesfactor,
            aggregationMethod=aggregation_method
        )

    def get_metadata(self, metric, key):
        """
        Get metric metadata
        """
        return self.tree.getNode(metric).readMetadata()[key]

    def set_metadata(self, metric, key, value):
        """
        Modify metric metadata
        """
        node = self.tree.getNode(metric)
        metadata = node.readMetadata()
        metadata[key] = value
        node.writeMetadata(metadata)

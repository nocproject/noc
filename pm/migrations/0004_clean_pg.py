# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# clean pg
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.execute(SP_DROP)
        # Deleting ManyToMany field
        db.delete_table("pm_chart_time_series")
        # Deleting model 'Chart'
        db.delete_table("pm_chart")
        # Deleting model 'TimeSeriesData'
        db.delete_table('pm_timeseriesdata')
        # Deleting model 'TimeSeries'
        db.delete_table('pm_timeseries')

    def backwards(self):
        pass


SP_DROP = "DROP FUNCTION IF EXISTS pm_timeseries_register(CHAR,INTEGER,DOUBLE PRECISION)"

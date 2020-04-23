# ----------------------------------------------------------------------
# clean pg
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute(SP_DROP)
        # Deleting ManyToMany field
        self.db.delete_table("pm_chart_time_series")
        # Deleting model 'Chart'
        self.db.delete_table("pm_chart")
        # Deleting model 'TimeSeriesData'
        self.db.delete_table("pm_timeseriesdata")
        # Deleting model 'TimeSeries'
        self.db.delete_table("pm_timeseries")


SP_DROP = "DROP FUNCTION IF EXISTS pm_timeseries_register(CHAR,INTEGER,DOUBLE PRECISION)"

# ----------------------------------------------------------------------
# initial
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0001_initial")]

    def migrate(self):
        # Adding model 'TimeSeries'
        self.db.create_table(
            "pm_timeseries",
            (
                ("id", models.AutoField(primary_key=True)),
                ("name", models.CharField("Name", unique=True, max_length=128)),
                ("is_enabled", models.BooleanField("Is Enabled?", default=True)),
            ),
        )

        TimeSeries = self.db.mock_model(model_name="TimeSeries", db_table="pm_timeseries")
        # Adding model 'TimeSeriesData'
        self.db.create_table(
            "pm_timeseriesdata",
            (
                ("id", models.AutoField(primary_key=True)),
                (
                    "time_series",
                    models.ForeignKey(
                        TimeSeries, verbose_name="Time Series", on_delete=models.CASCADE
                    ),
                ),
                ("timestamp", models.IntegerField("Timestamp")),
                ("value", models.FloatField("Value", null=True, blank=True)),
            ),
        )
        self.db.create_index("pm_timeseriesdata", ["timestamp"], unique=False)

        self.db.create_table(
            "pm_chart",
            (
                ("id", models.AutoField(primary_key=True)),
                ("name", models.CharField("Name", unique=True, max_length=128)),
            ),
        )

        Chart = self.db.mock_model(model_name="Chart", db_table="pm_chart")
        self.db.create_table(
            "pm_chart_time_series",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("chart", models.ForeignKey(Chart, null=False, on_delete=models.CASCADE)),
                ("timeseries", models.ForeignKey(TimeSeries, null=False, on_delete=models.CASCADE)),
            ),
        )
        self.db.execute(SP_CREATE)


SP_CREATE = """
CREATE OR REPLACE
FUNCTION pm_timeseries_register(CHAR,INTEGER,DOUBLE PRECISION)
RETURNS VOID
AS
$$
DECLARE
    p_ts_name   ALIAS FOR $1;
    p_timestamp ALIAS FOR $2;
    p_value     ALIAS FOR $3;
    ts_id       INTEGER;
BEGIN
    LOOP
        SELECT id
        INTO ts_id
        FROM pm_timeseries
        WHERE name=p_ts_name;

        IF FOUND THEN
            EXIT;
        ELSE
            INSERT INTO pm_timeseries(name)
            VALUES(p_ts_name);
        END IF;
    END LOOP;

    INSERT INTO pm_timeseriesdata(time_series_id,timestamp,value)
    VALUES(ts_id,p_timestamp,p_value);
END;
$$ LANGUAGE plpgsql;
"""

SP_DROP = "DROP FUNCTION pm_timeseries_register(CHAR,INTEGER,DOUBLE PRECISION)"

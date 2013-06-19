# -*- coding: utf-8 -*-

from south.db import db
from django.db import models


class Migration:
    depends_on=(
        ("main","0001_initial"),
    )
    def forwards(self):
        # Adding model 'TimeSeries'
        db.create_table('pm_timeseries', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField("Name", unique=True, max_length=128)),
            ('is_enabled', models.BooleanField("Is Enabled?", default=True)),
        ))
        db.send_create_signal('pm', ['TimeSeries'])
        TimeSeries = db.mock_model(model_name='TimeSeries', db_table='pm_timeseries', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        # Adding model 'TimeSeriesData'
        db.create_table('pm_timeseriesdata', (
            ('id', models.AutoField(primary_key=True)),
            ('time_series', models.ForeignKey(TimeSeries, verbose_name="Time Series")),
            ('timestamp', models.IntegerField("Timestamp")),
            ('value', models.FloatField("Value", null=True, blank=True)),
        ))
        db.create_index('pm_timeseriesdata', ['timestamp'], unique=False, db_tablespace='')
        db.send_create_signal('pm', ['TimeSeriesData'])
        #
        db.create_table('pm_chart', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField("Name", unique=True, max_length=128)),
        ))
        db.send_create_signal('pm', ['Chart'])
        Chart = db.mock_model(model_name='Chart', db_table='pm_chart', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        #
        db.create_table('pm_chart_time_series', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('chart', models.ForeignKey(Chart, null=False)),
            ('timeseries', models.ForeignKey(TimeSeries, null=False))
        ))
        #
        db.execute(SP_CREATE)
    
    def backwards(self):
        db.execute(SP_DROP)
        # Deleting ManyToMany field
        db.delete_table("pm_chart_time_series")
        # Deleting model 'Chart'
        db.delete_table("pm_chart")
        # Deleting model 'TimeSeriesData'
        db.delete_table('pm_timeseriesdata')
        # Deleting model 'TimeSeries'
        db.delete_table('pm_timeseries')

SP_CREATE="""
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

SP_DROP="DROP FUNCTION pm_timeseries_register(CHAR,INTEGER,DOUBLE PRECISION)"
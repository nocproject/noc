# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.db import models
from noc.main.menu import Menu
##
## Time Series
##
class TimeSeries(models.Model):
    class Meta:
        verbose_name="Time Series"
        verbose_name_plural="Time Series"
    name=models.CharField("Name",max_length=128,unique=True)
    is_enabled=models.BooleanField("Is Enabled?",default=True)
    def __unicode__(self):
        return self.name
    ##
    ## Register measurements result
    ## <!> TODO: Cache timeseries lookup
    ##
    @classmethod
    def register(cls,name,timestamp,value=None):
        from django.db import connection
        c=connection.cursor()
        c.execute("SELECT pm_timeseries_register(%s,%s,%s)",[name,timestamp,value])
        c.execute("COMMIT")
##
## Time Series Data
##
class TimeSeriesData(models.Model):
    class Meta:
        verbose_name="Time Series Data"
        verbose_name_plural="Time Series Data"
    time_series=models.ForeignKey(TimeSeries,verbose_name="Time Series")
    timestamp=models.IntegerField("Timestamp",db_index=True)
    value=models.FloatField("Value",null=True,blank=True)
    def __unicode__(self):
        return "%s@%s"%(self.time_series.name,str(self.timestamp))
##
##
##
class Chart(models.Model):
    class Meta:
        verbose_name="Chart"
        verbose_name_plural="Charts"
    name=models.CharField("Name",max_length=128,unique=True)
    time_series=models.ManyToManyField(TimeSeries,verbose_name="Time Series")
    def __unicode__(self):
        return self.name
##
## Application Menu
##
class AppMenu(Menu):
    app="pm"
    title="Performance Management"
    items=[
        ("Charts", "/pm/", "pm.change_chart"),
        ("Setup", [
            ("Time Series", "/admin/pm/timeseries/", "pm.change_timeseries"),
            ("Charts",      "/admin/pm/chart/",      "pm.change_chart"),
        ])
    ]

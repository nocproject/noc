# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.db import models
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
    def as_html(self):
        return '<div id="nocts_%d" style="width: 600px; height: 400px"></div><script>$("#nocts_%d").nocchart({ajaxURL:"/pm/view/ts/%d/data/"});</script>'%(self.id,self.id,self.id)
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
        return u"%s@%s"%(self.time_series.name,str(self.timestamp))
##
## Chart: the group of timeseries
##
class Chart(models.Model):
    class Meta:
        verbose_name="Chart"
        verbose_name_plural="Charts"
    name=models.CharField("Name",max_length=128,unique=True)
    time_series=models.ManyToManyField(TimeSeries,verbose_name="Time Series")
    def __unicode__(self):
        return self.name
    def as_html(self):
        return '<div id="nocchart_%d" style="width: 600px; height: 400px"></div><script>$("#nocchart_%d").nocchart({ajaxURL:"/pm/view/chart/%d/data/"});</script>'%(self.id,self.id,self.id)

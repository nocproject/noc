# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PM Viewer
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.shortcuts import get_object_or_404
from noc.lib.app import Application,HasPerm
from noc.pm.models import Chart,TimeSeries
import time
##
## PM Viewer application
##
class ViewAppplication(Application):
    title="View"
    ##
    ## Chart index
    ##
    def view_index(self,request):
        charts=Chart.objects.order_by("name")
        return self.render(request,"index.html",{"charts":charts})
    view_index.url=r"^$"
    view_index.menu="Charts"
    view_index.access=HasPerm("view")
    ##
    ## Chart Preview
    ##
    def view_chart(self,request,chart_id):
        chart=get_object_or_404(Chart,id=int(chart_id))
        return self.render(request,"view_chart.html",{"chart":chart})
    view_chart.url=r"^chart/(?P<chart_id>\d+)/$"
    view_chart.url_name="chart"
    view_chart.access=HasPerm("view")
    ##
    ## Time Series Preview
    ##
    def view_ts(self,request,ts_id):
        ts=get_object_or_404(TimeSeries,id=int(ts_id))
        return self.render(request,"view_ts.html",{"ts":ts})
    view_ts.url=r"^ts/(?P<ts_id>\d+)/$"
    view_ts.url_name="ts"
    view_ts.access=HasPerm("view")
    ##
    ## JSON-serialized chart data
    ##
    def view_chart_data(self,request,chart_id):
        chart=get_object_or_404(Chart,id=int(chart_id))
        time_series=chart.time_series.all()
        now=int(time.time())
        if request.GET and "t0" in request.GET and "t1" in request.GET:
            t0=int(request.GET["t0"])
            t1=int(request.GET["t1"])
            if t0>t1: # Swap ranges
                v=t1
                t1=t0
                t0=v
            if t1-t0<60: # Do not allow too small window
                t0=t1-60
            range=[t0,t1]
        else:
            range=[now-24*3600,now]
        r={
            "time_series": [ts.name for ts in time_series],
            "points"     : [[(d.timestamp,d.value) for d in ts.timeseriesdata_set.filter(timestamp__range=range).order_by("timestamp")] for ts in time_series],
            "min_ts"     : range[0],
            "max_ts"     : range[1],
        }
        try:
            r["min_v"]=min(0,min([min([x[1] for x in p if x[1] is not None]) for p in r["points"]]))
        except ValueError:
            r["min_v"]=0
        try:
            r["max_v"]=max(0,max([max([x[1] for x in p]) for p in r["points"]]))
        except ValueError:
            r["max_v"]=0
        return self.render_json(r)
    view_chart_data.url=r"chart/(?P<chart_id>\d+)/data/"
    view_chart_data.url_name="chart_data"
    view_chart_data.access=HasPerm("view")
    ##
    ## JSON-serialized time series data
    ##
    def view_ts_data(self,request,ts_id):
        ts=get_object_or_404(TimeSeries,id=int(ts_id))
        now=int(time.time())
        if request.GET and "t0" in request.GET and "t1" in request.GET:
            t0=int(request.GET["t0"])
            t1=int(request.GET["t1"])
            if t0>t1: # Swap ranges
                v=t1
                t1=t0
                t0=v
            if t1-t0<60: # Do not allow too small window
                t0=t1-60
            range=[t0,t1]
        else:
            range=[now-24*60,now]
        r={
            "time_series": [ts.name],
            "points"     : [[(d.timestamp,d.value) for d in ts.timeseriesdata_set.filter(timestamp__range=range).order_by("timestamp")]],
            "min_ts"     : range[0],
            "max_ts"     : range[1],
        }
        try:
            r["min_v"]=min(0,min([min([x[1] for x in p if x[1] is not None]) for p in r["points"]]))
        except ValueError:
            r["min_v"]=0
        try:
            r["max_v"]=max(0,max([max([x[1] for x in p]) for p in r["points"]]))
        except ValueError:
            r["max_v"]=0
        return self.render_json(r)
    view_ts_data.url=r"ts/(?P<ts_id>\d+)/data/"
    view_ts_data.url_name="ts_data"
    view_ts_data.access=HasPerm("view")
    

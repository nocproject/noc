# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django's standard views module
## for Performance Management module
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.shortcuts import get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseForbidden
from django import forms
from noc.pm.models import *
from noc.lib.render import render,render_success,render_failure,render_json
import time
##
##
##
def index(request):
    charts=Chart.objects.order_by("name")
    return render(request,"pm/index.html",{"charts":charts})
##
##
##
def view_chart(request,chart_id):
    chart=get_object_or_404(Chart,id=int(chart_id))
    return render(request,"pm/view_chart.html",{"chart":chart})
##
##
##
def chart_data(request,chart_id):
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
    return render_json(r)
##
##
##
def view_ts(request,ts_id):
    ts=get_object_or_404(TimeSeries,id=int(ts_id))
    return render(request,"pm/view_ts.html",{"ts":ts})
##
##
##
def ts_data(request,ts_id):
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
    return render_json(r)

# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## admin for Performance Management application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django import forms
from models import *
##
class TimeSeriesAdmin(admin.ModelAdmin):
    list_display=["name","is_enabled","view_link"]
    search_fields=["name"]
#
class ChartAdmin(admin.ModelAdmin):
    list_display=["name"]
    search_fields=["name"]
    filter_horizontal=["time_series"]

##
admin.site.register(TimeSeries, TimeSeriesAdmin)
admin.site.register(Chart,      ChartAdmin)

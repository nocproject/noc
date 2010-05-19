# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TimeSeries Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.pm.models import TimeSeries
##
def view_link(o):
    return "<a href='/pm/view/ts/%d/'>View</a>"%o.id
view_link.short_description="View"
view_link.allow_tags=True
##
## TimeSeries admin
##
class TimeSeriesAdmin(admin.ModelAdmin):
    list_display=["name","is_enabled",view_link]
    search_fields=["name"]
##
## TimeSeries application
##
class TimeSeriesApplication(ModelApplication):
    model=TimeSeries
    model_admin=TimeSeriesAdmin
    menu="Setup | Time Series"

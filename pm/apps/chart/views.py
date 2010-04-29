# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Chart Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.pm.models import Chart
##
## Chart admin
##
class ChartAdmin(admin.ModelAdmin):
    list_display=["name"]
    search_fields=["name"]
    filter_horizontal=["time_series"]
##
## Chart application
##
class ChartApplication(ModelApplication):
    model=Chart
    model_admin=ChartAdmin
    menu="Setup | Charts"

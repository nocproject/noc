# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## GroupAccess Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.sa.models import GroupAccess
##
## GroupAccess admin
##
class GroupAccessAdmin(admin.ModelAdmin):
    list_display=["group","selector"]
    list_filter=["group"]
##
## GroupAccess application
##
class GroupAccessApplication(ModelApplication):
    model=GroupAccess
    model_admin=GroupAccessAdmin
    menu="Setup | Group Access"

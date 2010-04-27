# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIBData Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.fm.models import MIBData
##
## MIBData admin
##
class MIBViewAdmin(admin.ModelAdmin):
    list_display=["oid","name"]
    list_filter=["mib"]
    search_fields=["oid","name"]
##
## MIBData application
##
class MIBViewApplication(ModelApplication):
    model=MIBData
    model_admin=MIBViewAdmin
    menu="MIB Viewer"

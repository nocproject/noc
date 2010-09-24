# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ChangesQuarantine Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.main.models import ChangesQuarantine
##
## ChangesQuarantine admin
##
class ChangesQuarantineAdmin(admin.ModelAdmin):
    list_display=["timestamp","changes_type","subject"]
    search_fields=["subject"]
    list_filter=["changes_type"]
##
## ChangesQuarantine application
##
class ChangesQuarantineApplication(ModelApplication):
    model=ChangesQuarantine
    model_admin=ChangesQuarantineAdmin
    menu="Quarantine"

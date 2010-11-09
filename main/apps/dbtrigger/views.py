# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DBTrigger Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC Modules
from noc.lib.app import ModelApplication
from noc.main.models import DBTrigger
##
## DBTrigger admin
##
class DBTriggerAdmin(admin.ModelAdmin):
    list_display=["name","model","is_active","order","description","pre_save_rule","post_save_rule","pre_delete_rule","post_delete_rule"]
    list_filter=["model","is_active"]
    search_fields=["name","model"]

##
## DBTrigger application
##
class DBTriggerApplication(ModelApplication):
    model=DBTrigger
    model_admin=DBTriggerAdmin
    menu="Setup | DB Triggers"

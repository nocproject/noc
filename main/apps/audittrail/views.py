# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AuditTrail Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.main.models import AuditTrail
##
## AuditTrail admin
##
class AuditTrailAdmin(admin.ModelAdmin):
    list_display=["user","timestamp","model","db_table","operation","subject"]
    list_filter=["user"]
    search_fields=["subject","body"]
##
## AuditTrail application
##
class AuditTrailApplication(ModelApplication):
    model=AuditTrail
    model_admin=AuditTrailAdmin
    menu="Audit Trail"

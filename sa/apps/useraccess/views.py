# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UserAccess Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.sa.models import UserAccess
##
## UserAccess admin
##
class UserAccessAdmin(admin.ModelAdmin):
    list_display=["user","administrative_domain","group"]
    list_filter=["user","administrative_domain","group"]
##
## UserAccess application
##
class UserAccessApplication(ModelApplication):
    model=UserAccess
    model_admin=UserAccessAdmin
    menu="Setup | User Access"

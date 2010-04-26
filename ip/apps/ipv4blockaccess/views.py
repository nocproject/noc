# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IPv4BlockAccess Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.ip.models import IPv4BlockAccess
##
## IPv4BlockAccess admin
##
class IPv4BlockAccessAdmin(admin.ModelAdmin):
    list_display=["user","vrf","prefix"]
    list_filter=["user","vrf"]
    search_fields=["user","prefix"]
##
## IPv4BlockAccess application
##
class IPv4BlockAccessApplication(ModelApplication):
    model=IPv4BlockAccess
    model_admin=IPv4BlockAccessAdmin
    menu="Setup | IPv4 Block Access"

# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PrefixAccess Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.ip.models import PrefixAccess
##
## PrefixAccess admin
##
class PrefixAccessAdmin(admin.ModelAdmin):
    list_display=["user","vrf","afi","prefix","can_view","can_change"]
    list_filter=["user","vrf","can_view","can_change"]
    search_fields=["user","prefix"]

##
## PrefixAccess application
##
class PrefixAccessApplication(ModelApplication):
    title="Prefix Access"
    model=PrefixAccess
    model_admin=PrefixAccessAdmin
    menu="Setup | Prefix Access"

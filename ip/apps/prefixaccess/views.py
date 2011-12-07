# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PrefixAccess Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication
from noc.ip.models import PrefixAccess


class PrefixAccessAdmin(admin.ModelAdmin):
    """
    PrefixAccess admin
    """
    list_display = ["user", "vrf", "afi", "prefix", "can_view", "can_change"]
    list_filter = ["user", "vrf", "can_view", "can_change"]
    search_fields = ["user__username", "prefix"]


class PrefixAccessApplication(ModelApplication):
    """
    PrefixAccess application
    """
    title = "Prefix Access"
    model = PrefixAccess
    model_admin = PrefixAccessAdmin
    menu = "Setup | Prefix Access"

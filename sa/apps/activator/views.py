# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Activator Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.sa.models import Activator
##
## Activator admin
##
class ActivatorAdmin(admin.ModelAdmin):
    list_display=["name", "ip", "is_active", "shard"]
    filter_display = ["is_active", "shard"]
##
## Activator application
##
class ActivatorApplication(ModelApplication):
    model=Activator
    model_admin=ActivatorAdmin
    menu="Setup | Activators"

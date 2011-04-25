# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Shard Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication
from noc.main.models import Shard
##
## Shard admin
##
class ShardAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "description"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    
##
## Shard application
##
class ShardApplication(ModelApplication):
    model = Shard
    model_admin = ShardAdmin
    menu = "Setup | Shards"

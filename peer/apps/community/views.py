# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Community Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.peer.models import Community
##
## Community admin
##
class CommunityAdmin(admin.ModelAdmin):
    list_display=["community","type","description"]
    list_filter=["type"]
    search_fields=["community","description"]
##
## Community application
##
class CommunityApplication(ModelApplication):
    model=Community
    model_admin=CommunityAdmin
    menu="Communities"

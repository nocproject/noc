# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CommunityType Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.peer.models import CommunityType
##
## CommunityType admin
##
class CommunityTypeAdmin(admin.ModelAdmin):
    list_display=["name"]
##
## CommunityType application
##
class CommunityTypeApplication(ModelApplication):
    model=CommunityType
    model_admin=CommunityTypeAdmin
    menu="Setup | Community Types"

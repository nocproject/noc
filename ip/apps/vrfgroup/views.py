# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VRFGroup Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.ip.models import VRFGroup
##
## VRFGroup admin
##
class VRFGroupAdmin(admin.ModelAdmin):
    list_display=["name","address_constraint","description"]
    search_fields=["name","description"]
##
## VRFGroup application
##
class VRFGroupApplication(ModelApplication):
    model=VRFGroup
    model_admin=VRFGroupAdmin
    menu="Setup | VRF Groups"

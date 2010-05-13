# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VRF Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.ip.models import VRF
##
## VRF admin
##
class VRFAdmin(admin.ModelAdmin):
    list_display=["rd","name","vrf_group","description"]
    search_fields=["name","rd"]
    list_filter=["vrf_group"]
##
## VRF application
##
class VRFApplication(ModelApplication):
    model=VRF
    model_admin=VRFAdmin
    menu="Setup | VRFs"

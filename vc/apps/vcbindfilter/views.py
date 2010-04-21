# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VCBindFilter Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.vc.models import VCBindFilter
##
## VCBindFilter admin
##
class VCBindFilterAdmin(admin.ModelAdmin):
    list_display=["vc_domain","vrf","prefix","vc_filter"]

##
## VCBindFilter application
##
class VCBindFilterApplication(ModelApplication):
    model=VCBindFilter
    model_admin=VCBindFilterAdmin
    menu="Setup | VC Bind Filters"

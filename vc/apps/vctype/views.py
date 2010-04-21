# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VCType Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.vc.models import VCType
##
## VCType admin
##
class VCTypeAdmin(admin.ModelAdmin):
    list_display=["name","min_labels","label1_min","label1_max","label2_min","label2_max"]
##
## VCType application
##
class VCTypeApplication(ModelApplication):
    model=VCType
    model_admin=VCTypeAdmin
    menu="Setup | VC Types"

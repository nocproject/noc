# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RIR Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.peer.models import RIR
##
## RIR admin
##
class RIRAdmin(admin.ModelAdmin):
    pass
##
## RIR application
##
class RIRApplication(ModelApplication):
    model=RIR
    model_admin=RIRAdmin
    menu="Setup | RIRs"

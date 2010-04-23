# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Organisation Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.peer.models import Organisation
##
## Organisation admin
##
class OrganisationAdmin(admin.ModelAdmin):
    list_display=["organisation","org_name","org_type"]
##
## Organisation application
##
class OrganisationApplication(ModelApplication):
    model=Organisation
    model_admin=OrganisationAdmin
    menu="Setup | Organisations"

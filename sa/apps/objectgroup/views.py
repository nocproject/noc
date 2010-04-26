# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectGroup Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.sa.models import ObjectGroup
##
## ObjectGroup admin
##
class ObjectGroupAdmin(admin.ModelAdmin):
    list_display=["name","description"]
    search_fields=["name","description"]
##
## ObjectGroup application
##
class ObjectGroupApplication(ModelApplication):
    model=ObjectGroup
    model_admin=ObjectGroupAdmin
    menu="Setup | Object Groups"

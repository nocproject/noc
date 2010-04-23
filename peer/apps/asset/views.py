# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ASSet Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.peer.models import ASSet
##
## ASSet admin
##
class ASSetAdmin(admin.ModelAdmin):
    list_display=["name","description","members"]
    search_fields=["name","description","members"]
    actions=["rpsl_for_selected"]
    ##
    ## Generate RPSL for selected objects
    ##
    def rpsl_for_selected(self,request,queryset):
        return self.app.render_plain_text("\n\n".join([o.rpsl for o in queryset]))
    rpsl_for_selected.short_description="RPSL for selected objects"
##
## ASSet application
##
class ASSetApplication(ModelApplication):
    model=ASSet
    model_admin=ASSetAdmin
    menu="AS Sets"

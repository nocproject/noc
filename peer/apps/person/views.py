# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Person Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.peer.models import Person
##
## Person admin
##
class PersonAdmin(admin.ModelAdmin):
    list_display=["nic_hdl","person","rir"]
    list_filter=["rir"]
    search_fields=["nic_hdl","person"]
    actions=["rpsl_for_selected"]
    ##
    ## Generate RPSL for selected objects
    ##
    def rpsl_for_selected(self,request,queryset):
        return self.app.render_plain_text("\n\n".join([o.rpsl for o in queryset]))
    rpsl_for_selected.short_description="RPSL for selected objects"
##
## Person application
##
class PersonApplication(ModelApplication):
    model=Person
    model_admin=PersonAdmin
    menu="Setup | Persons"

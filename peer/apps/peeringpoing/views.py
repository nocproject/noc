# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PeeringPoint Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.peer.models import PeeringPoint
##
## PeeringPoint admin
##
class PeeringPointAdmin(admin.ModelAdmin):
    list_display=["hostname","location","local_as","router_id","profile_name","communities"]
    list_filter=["profile_name"]
    search_fields=["hostname","router_id"]
    actions=["rpsl_for_selected"]
    ##
    ## Generate RPSL for selected objects
    ##
    def rpsl_for_selected(self,request,queryset):
        return self.app.render_plain_text("\n\n".join([o.rpsl for o in queryset]))
    rpsl_for_selected.short_description="RPSL for selected objects"

##
## PeeringPoint application
##
class PeeringPointApplication(ModelApplication):
    model=PeeringPoint
    model_admin=PeeringPointAdmin
    menu="Peering Points"

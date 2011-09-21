# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PeeringPoint Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext as _
## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.peer.models import PeeringPoint


class PeeringPointApplication(ExtModelApplication):
    title = _("Peering Point")
    menu = "Setup | Peering Points"
    model = PeeringPoint

#from django.contrib import admin
#from noc.lib.app import ModelApplication
#from noc.peer.models import PeeringPoint
##
## PeeringPoint admin
##
#class _PeeringPointAdmin(admin.ModelAdmin):
#    list_display=["hostname","location","local_as","router_id","profile_name","communities"]
#    list_filter=["profile_name"]
#    search_fields=["hostname","router_id"]
#    actions=["rpsl_for_selected"]
    ##
    ## Generate RPSL for selected objects
    ##
#    def rpsl_for_selected(self,request,queryset):
#        return self.app.render_plain_text("\n\n".join([o.rpsl for o in queryset]))
#    rpsl_for_selected.short_description="RPSL for selected objects"

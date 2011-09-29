# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PeeringPoint Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication
from noc.peer.models import PeeringPoint


class PeeringPointAdmin(admin.ModelAdmin):
    """
    Peering Point admin
    """
    list_display = ["hostname", "location", "local_as", "router_id",
                  "profile_name", "communities"]
    list_filter = ["profile_name"]
    search_fields = ["hostname", "router_id"]
    actions = ["rpsl_for_selected"]

    def rpsl_for_selected(self, request, queryset):
        """
        Generate RPSL for selected objects
        """
        rpsl = "\n\n".join([o.rpsl for o in queryset])
        return self.app.render_plain_text(rpsl)
    rpsl_for_selected.short_description = "RPSL for selected objects"


class PeeringPointApplication(ModelApplication):
    model = PeeringPoint
    model_admin = PeeringPointAdmin
    menu="Setup | Peering Points"

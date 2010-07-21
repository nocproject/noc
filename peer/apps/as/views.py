# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AS Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.peer.models import AS
##
## AS admin
##
class ASAdmin(admin.ModelAdmin):
    list_display=["asn","as_name","description","organisation"]
    search_fields=["asn","description"]
    filter_horizontal=["administrative_contacts","tech_contacts","maintainers","routes_maintainers"]
    actions=["rpsl_for_selected","update_rir_db_for_selected"]
    ##
    ## Generate RPSL for selected objects
    ##
    def rpsl_for_selected(self,request,queryset):
        return self.app.render_plain_text("\n\n".join([o.rpsl for o in queryset]))
    rpsl_for_selected.short_description="RPSL for selected objects"
    ##
    ## Update RIR database for selected objects
    ##
    def update_rir_db_for_selected(self,request,queryset):
        u=request.user
        if not u or not u.is_superuser:
            self.message_user(request,"Superuser priveleges required")
            return
        r=[]
        for a in queryset:
            r+=["AS%s %s:\n"%(a.asn,a.as_name)+a.update_rir_db()]
        return self.app.render_plain_text("\n\n".join(r))
    update_rir_db_for_selected.short_description="Update RIR DB for selected objects"

##
## AS application
##
class ASApplication(ModelApplication):
    model=AS
    model_admin=ASAdmin
    menu="ASes"

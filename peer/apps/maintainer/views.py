# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Maintainer Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.peer.models import Maintainer
##
## Maintainer admin
##
class MaintainerAdmin(admin.ModelAdmin):
    list_display=["maintainer","description","rir"]
    list_filter=["rir"]
    filter_horizontal=["admins"]
    actions=["rpsl_for_selected"]
    ##
    ## Generate RPSL for selected objects
    ##
    def rpsl_for_selected(self,request,queryset):
        return self.app.render_plain_text("\n\n".join([o.rpsl for o in queryset]))
    rpsl_for_selected.short_description="RPSL for selected objects"
##
## Maintainer application
##
class MaintainerApplication(ModelApplication):
    model=Maintainer
    model_admin=MaintainerAdmin
    menu="Setup | Maintainers"

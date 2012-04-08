# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Style Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication, view
from noc.main.models import Style
##
## Style sample
##
def color_sample(obj):
    return u"<div style='padding: 4px; %s'> Sample text </div>" % obj.style

color_sample.short_description = "Sample"
color_sample.allow_tags = True

##
## Style admin
##
class StyleAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", color_sample, "description"]
    search_fields = ["name"]
    list_filter = ["is_active"]

##
## Style application
##
class StyleApplication(ModelApplication):
    model = Style
    model_admin = StyleAdmin
    menu = "Setup | Styles"

    @view(url=r"^css/$", method=["GET"], access=True)
    def view_css(self, request):
        text = "\n\n".join([s.css for s in Style.objects.all()])
        return self.render_plain_text(text, mimetype="text/css")

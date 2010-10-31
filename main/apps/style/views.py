# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Style Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.main.models import Style
##
## Style sample
##
def color_sample(obj):
    return u"<div style='padding: 4px; %s'> Sample text </div>"%obj.style
color_sample.short_description="Sample"
color_sample.allow_tags=True

##
## Style admin
##
class StyleAdmin(admin.ModelAdmin):
    list_display=["name","is_active",color_sample,"description"]
    search_fields=["name"]
    list_filter=["is_active"]
##
## Style application
##
class StyleApplication(ModelApplication):
    model=Style
    model_admin=StyleAdmin
    menu="Setup | Styles"

# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django's standard admin module
## For VC application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.contrib import admin
from noc.vc.models import VCDomain,VC

##
## Admin form for VCDomain
##
class VCDomainAdmin(admin.ModelAdmin):
    list_display=["name"]
    search_fields=["name"]

class VCAdmin(admin.ModelAdmin):
    list_display=["vc_domain","type","l1","l2","description"]
    search_fields=["l1","l2","description"]
    list_filter=["vc_domain","type"]

admin.site.register(VCDomain,VCDomainAdmin)
admin.site.register(VC,VCAdmin)
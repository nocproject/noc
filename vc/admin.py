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
from noc.vc.models import VCDomain,VC,VCType

##
## Admin form for VCDomain
##
class VCDomainAdmin(admin.ModelAdmin):
    list_display=["name","type","description"]
    search_fields=["name"]
    list_filter=["type"]

class VCAdmin(admin.ModelAdmin):
    list_display=["vc_domain","l1","l2","description"]
    search_fields=["l1","l2","description"]
    list_filter=["vc_domain"]
##
class VCTypeAdmin(admin.ModelAdmin):
    list_display=["name","min_labels","label1_min","label1_max","label2_min","label2_max"]

admin.site.register(VCDomain,VCDomainAdmin)
admin.site.register(VCType,VCTypeAdmin)
admin.site.register(VC,VCAdmin)

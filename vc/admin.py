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
from noc.vc.models import VCDomain,VCFilter,VCBindFilter,VC,VCType,VCDomainProvisioningConfig

##
## Admin form for VCDomain
##
class VCDomainProvisioningConfigAdmin(admin.TabularInline):
    model=VCDomainProvisioningConfig
    extra=3
    
class VCDomainAdmin(admin.ModelAdmin):
    list_display=["name","type","enable_provisioning","enable_vc_bind_filter","description"]
    search_fields=["name"]
    list_filter=["type","enable_provisioning","enable_vc_bind_filter"]
    inlines=[VCDomainProvisioningConfigAdmin]
##
##
##
class VCFilterAdmin(admin.ModelAdmin):
    list_display=["name","expression","test_link"]
    search_fields=["name"]
##
##
##
class VCBindFilterAdmin(admin.ModelAdmin):
    list_display=["vc_domain","vrf","prefix","vc_filter"]
##
##
##
class VCAdmin(admin.ModelAdmin):
    list_display=["vc_domain","name","l1","l2","description","blocks_list"]
    search_fields=["name","l1","l2","description"]
    list_filter=["vc_domain"]
##
class VCTypeAdmin(admin.ModelAdmin):
    list_display=["name","min_labels","label1_min","label1_max","label2_min","label2_max"]

admin.site.register(VCDomain,VCDomainAdmin)
admin.site.register(VCFilter,VCFilterAdmin)
admin.site.register(VCBindFilter,VCBindFilterAdmin)
admin.site.register(VCType,VCTypeAdmin)
admin.site.register(VC,VCAdmin)

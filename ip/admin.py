# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.contrib import admin
from noc.ip.models import VRFGroup,VRF,IPv4BlockAccess,IPv4Block,IPv4Address

class VRFGroupAdmin(admin.ModelAdmin):
    list_display=["name","unique_addresses"]
    search_fields=["name"]
        
class VRFAdmin(admin.ModelAdmin):
    list_display=["rd","name","vrf_group"]
    search_fields=["name","rd"]
    list_filter=["vrf_group"]

class IPv4BlockAccessAdmin(admin.ModelAdmin):
    list_display=["user","vrf","prefix"]
    list_filter=["user","vrf"]
    search_fields=["user","prefix"]

class IPv4BlockAdmin(admin.ModelAdmin):
    list_display=["prefix","vrf","description"]
    list_filter=["vrf","asn"]
    search_fields=["prefix","description"]

class IPv4AddressAdmin(admin.ModelAdmin):
    list_display=["ip","fqdn","vrf","description"]
    list_filter=["vrf"]
    search_fields=["ip","fqdn","description"]

admin.site.register(VRFGroup,VRFGroupAdmin)
admin.site.register(VRF,VRFAdmin)
admin.site.register(IPv4BlockAccess,IPv4BlockAccessAdmin)
admin.site.register(IPv4Block,IPv4BlockAdmin)
admin.site.register(IPv4Address,IPv4AddressAdmin)

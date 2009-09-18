# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## admin.py
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.contrib import admin
from noc.ip.models import VRFGroup,VRF,IPv4BlockAccess,IPv4Block,IPv4Address
from noc.peer.models import AS
##
## Admin for VRFGroup
##
class VRFGroupAdmin(admin.ModelAdmin):
    list_display=["name","unique_addresses","description"]
    search_fields=["name"]
##
## Admin or VRF
##
class VRFAdmin(admin.ModelAdmin):
    list_display=["rd","name","vrf_group","description"]
    search_fields=["name","rd"]
    list_filter=["vrf_group"]
    def save_model(self, request, obj, form, change):
        vrf=form.save()
        # Create 0.0.0.0/0 prefix if not exists
        try:
            IPv4Block.objects.get(vrf=vrf,prefix="0.0.0.0/0")
        except IPv4Block.DoesNotExist:
            IPv4Block(vrf=vrf,prefix="0.0.0.0/0",description="root",asn=AS.default_as(),modified_by=request.user).save()
##
## Admin for IPv4BlockAccess
##
class IPv4BlockAccessAdmin(admin.ModelAdmin):
    list_display=["user","vrf","prefix"]
    list_filter=["user","vrf"]
    search_fields=["user","prefix"]

admin.site.register(VRFGroup,VRFGroupAdmin)
admin.site.register(VRF,VRFAdmin)
admin.site.register(IPv4BlockAccess,IPv4BlockAccessAdmin)

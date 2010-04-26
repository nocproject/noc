# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VRF Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.ip.models import VRF,IPv4Block,AS
##
## VRF admin
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
## VRF application
##
class VRFApplication(ModelApplication):
    model=VRF
    model_admin=VRFAdmin
    menu="Setup | VRFs"

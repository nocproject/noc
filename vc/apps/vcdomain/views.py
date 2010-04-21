# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VCDomain Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.vc.models import VCDomain,VCDomainProvisioningConfig
##
## VCDomain admin
##
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
## VCDomain application
##
class VCDomainApplication(ModelApplication):
    model=VCDomain
    model_admin=VCDomainAdmin
    menu="Setup | VC Domains"

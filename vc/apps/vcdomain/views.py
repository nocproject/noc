# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VCDomain Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication
from noc.vc.models import VCDomain, VCDomainProvisioningConfig


class VCDomainProvisioningConfigAdmin(admin.TabularInline):
    """
    Inline admin for VC Domain
    """
    model = VCDomainProvisioningConfig
    extra = 3


class VCDomainAdmin(admin.ModelAdmin):
    """
    VC Domain Admin
    """
    list_display = ["name", "type", "enable_provisioning",
                    "enable_vc_bind_filter", "selector", "description"]
    search_fields = ["name"]
    list_filter = ["type", "enable_provisioning", "enable_vc_bind_filter"]
    inlines = [VCDomainProvisioningConfigAdmin]


class VCDomainApplication(ModelApplication):
    """
    VC Domain application
    """
    model = VCDomain
    model_admin = VCDomainAdmin
    menu = "Setup | VC Domains"
